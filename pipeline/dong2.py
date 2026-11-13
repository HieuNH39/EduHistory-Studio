"""Chuyển động bằng code cho ảnh cảnh 2D (thay Kling ở các tập không dùng clip AI) – phiên bản 2.

Mỗi khung hình được dựng bằng MỘT phép ánh xạ điểm ảnh (cv2.remap) gộp nhiều trường dịch chuyển, rồi phủ lớp vẽ:
  1. Máy quay 2.5D: bản đồ độ sâu (Depth Anything V2 – ONNX) → thị sai khi máy quay trôi + zoom chậm.
  2. Nhân vật (rembg tách người): thở (co giãn dọc quanh chân), lắc nhẹ; đầu gật/nghiêng nhiều hơn khi đang nói.
  3. Khuôn mặt (MediaPipe Face Landmarker, dò theo ô cửa sổ vì mặt nhỏ): khẩu hình theo âm lượng giọng đọc
     (hàm dưới hạ xuống + lòng miệng tối), nháy mắt ngẫu nhiên.
  4. Môi trường theo màu (HSV) hoặc theo khai báo của cảnh: lửa/nến bập bùng, khói bốc, nước lăn tăn, lá cây và cờ lay.
Các bước dò (độ sâu, mặt nạ, khuôn mặt) được lưu đệm theo ảnh."""
import os, hashlib, math, json, subprocess
import numpy as np, cv2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "renders/_cache/dong2"); os.makedirs(CACHE, exist_ok=True)
MODELS = os.environ.get("EDU_MODELS", "/home/claude/models")
NARR = ("Nhật Minh", "Hân Hân")

# ------------------------------------------------------------------ dò tìm (có lưu đệm)
def _key(img, extra=""):
    return hashlib.sha1(img[::9, ::9].tobytes() + extra.encode()).hexdigest()[:16]

def do_sau(img):
    """Độ sâu tương đối 0..1 (1 = gần), cùng kích thước ảnh."""
    p = os.path.join(CACHE, _key(img, "depth") + ".npy")
    if os.path.exists(p): d = np.load(p)
    else:
        import onnxruntime as ort
        s = ort.InferenceSession(os.path.join(MODELS, "depth_anything_v2_small.onnx"), providers=["CPUExecutionProvider"])
        h, w = img.shape[:2]; sc = 518 / min(h, w)
        hh, ww = int(round(h * sc / 14)) * 14, int(round(w * sc / 14)) * 14
        x = cv2.resize(img, (ww, hh), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
        x = (x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
        d = s.run(None, {"pixel_values": x.transpose(2, 0, 1)[None].astype(np.float32)})[0][0]
        d = (d - np.percentile(d, 2)) / max(np.percentile(d, 98) - np.percentile(d, 2), 1e-6)
        d = np.clip(d, 0, 1).astype(np.float32); np.save(p, d)
    return cv2.resize(d, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_LINEAR)

def nguoi(img):
    import song_dong
    return song_dong.mat_na(img)

def khuon_mat(img):
    """Danh sách khuôn mặt: mỗi mặt có 478 điểm (toạ độ ảnh gốc), sắp xếp trái → phải."""
    p = os.path.join(CACHE, _key(img, "faces3") + ".json")
    if os.path.exists(p): return [np.array(f, np.float32) for f in json.load(open(p))]
    import mediapipe as mp
    from mediapipe.tasks import python as mpt
    from mediapipe.tasks.python import vision
    det = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
        base_options=mpt.BaseOptions(model_asset_path=os.path.join(MODELS, "face_landmarker.task")),
        num_faces=4, min_face_detection_confidence=0.35, min_face_presence_confidence=0.35))
    h, w = img.shape[:2]; found = []
    for win in (420, 700, 1100):
        if win > min(h, w): continue
        st = win // 2
        for y0 in list(range(0, h - win + 1, st)) + [h - win]:
            for x0 in list(range(0, w - win + 1, st)) + [w - win]:
                c = np.ascontiguousarray(img[y0:y0 + win, x0:x0 + win])
                for lm in det.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=c)).face_landmarks:
                    pts = np.array([[q.x * win + x0, q.y * win + y0] for q in lm], np.float32)
                    # mặt nằm sát mép ô thì bỏ (thường bị cắt, điểm sai)
                    if pts[:, 0].min() < x0 + 4 or pts[:, 0].max() > x0 + win - 4 or pts[:, 1].min() < y0 + 4 or pts[:, 1].max() > y0 + win - 4: continue
                    found.append(pts)
    det.close()
    keep = []
    for f in sorted(found, key=lambda f: -(f[:, 0].max() - f[:, 0].min())):
        c = f.mean(0); s = f[:, 0].max() - f[:, 0].min()
        if s < 0.02 * w: continue
        if all(np.hypot(*(c - k.mean(0))) > 0.5 * (k[:, 0].max() - k[:, 0].min()) for k in keep): keep.append(f)
    keep.sort(key=lambda f: f[:, 0].mean())
    json.dump([f.round(1).tolist() for f in keep], open(p, "w"))
    return keep

# ------------------------------------------------------------------ chỉ số điểm MediaPipe
MOI_TRONG = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]
MAT_TRAI = [33, 246, 161, 160, 159, 158, 157, 173, 133, 155, 154, 153, 145, 144, 163, 7]
MAT_PHAI = [362, 398, 384, 385, 386, 387, 388, 466, 263, 249, 390, 373, 374, 380, 381, 382]

def _env(wav, fps, n):
    """Biên độ giọng (0..1) theo từng khung hình."""
    if not wav or not os.path.exists(wav): return np.zeros(n, np.float32)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", wav, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    hop = 16000 / fps; e = np.zeros(n, np.float32)
    for i in range(n):
        seg = a[int(i * hop): int((i + 1) * hop)]
        if len(seg): e[i] = np.sqrt((seg ** 2).mean())
    e = e / max(np.percentile(e, 95), 1e-4)
    e = np.clip((e - 0.12) / 0.88, 0, 1)
    k = np.array([.25, .5, .25]); e = np.convolve(e, k, mode="same")
    return e.astype(np.float32)

def _gauss(shape, cx, cy, r):
    h, w = shape; y, x = np.ogrid[:h, :w]
    return np.exp(-(((x - cx) ** 2 + (y - cy) ** 2) / (2 * r * r))).astype(np.float32)

def _noise(h, w, scale, seed):
    rng = np.random.default_rng(seed)
    g = rng.standard_normal((max(2, h // scale + 2), max(2, w // scale + 2))).astype(np.float32)
    return cv2.resize(g, (w, h), interpolation=cv2.INTER_CUBIC)

# ------------------------------------------------------------------ dựng khung hình
def frames(img_rgb, W, H, n, fps=30, sc=None, seed=0):
    sc = sc or {}
    cfg = sc.get("dong", {}) if isinstance(sc.get("dong"), dict) else {}
    # ảnh làm việc: phủ kín khung, dư 8% để máy quay di chuyển
    h0, w0 = img_rgb.shape[:2]; M = 1.08
    s = max(W * M / w0, H * M / h0); ww, hh = int(w0 * s), int(h0 * s)
    img = cv2.resize(img_rgb, (ww, hh), interpolation=cv2.INTER_AREA)
    ox, oy = (ww - W) / 2, (hh - H) / 2
    dep = cv2.resize(do_sau(img_rgb), (ww, hh))
    men = cv2.resize(nguoi(img_rgb), (ww, hh)).astype(np.float32) / 255
    men = cv2.GaussianBlur(men, (0, 0), 3)
    faces = [f * s for f in khuon_mat(img_rgb)]
    rng = np.random.default_rng(seed + n)

    # ---- trường cố định
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    D = dep[int(oy):int(oy) + H, int(ox):int(ox) + W]; Dn = D - np.median(D)
    MEN = men[int(oy):int(oy) + H, int(ox):int(ox) + W]
    hsv = cv2.cvtColor(img[int(oy):int(oy) + H, int(ox):int(ox) + W], cv2.COLOR_RGB2HSV).astype(np.float32)
    Hh, S, V = hsv[..., 0], hsv[..., 1] / 255, hsv[..., 2] / 255
    menx = cv2.GaussianBlur(cv2.dilate((MEN > .3).astype(np.uint8), np.ones((31, 31), np.uint8)).astype(np.float32), (0, 0), 8)
    if (MEN > .5).sum() > 500:   # phần gần ngang nhân vật (tay, áo rembg bỏ sót) cũng coi là nhân vật
        dch = np.percentile(D[MEN > .5], 20)
        menx = np.maximum(menx, cv2.GaussianBlur(np.clip((D - dch * .85) / max(dch * .15, 1e-3), 0, 1), (0, 0), 6))
    nonchar = 1 - np.clip(menx, 0, 1)
    fx = lambda: cv2.GaussianBlur
    # lửa/nến: mảng cam – vàng rất sáng, rực, KÍCH THƯỚC NHỎ (tránh nhầm trời/nước hoàng hôn)
    lua0 = ((Hh < 26) & (S > .55) & (V > .86) & (nonchar > .5)).astype(np.uint8)
    nl, labl, stl, _ = cv2.connectedComponentsWithStats(lua0); lua = np.zeros(lua0.shape, np.float32)
    for i in range(1, nl):
        if 30 < stl[i, cv2.CC_STAT_AREA] < 0.012 * W * H: lua[labl == i] = 1
    mo_ta = (sc.get("hinh") or "").lower()
    co_lua = cfg.get("lua", any(k in mo_ta for k in ("lửa", "nến", "đuốc", "cháy", "đèn", "bếp", "lò")))
    if not co_lua: lua[:] = 0
    lua = cv2.GaussianBlur(cv2.dilate(lua, np.ones((9, 9), np.uint8)), (0, 0), 6) if lua.sum() > 50 else None
    la = ((Hh > 30) & (Hh < 90) & (S > .25) & (V > .2)).astype(np.float32) * nonchar
    la = cv2.GaussianBlur(la, (0, 0), 4) * np.clip(1 - D * 1.2, 0.2, 1)   # cây gần ít lay (tránh vỡ hình)
    co = (((Hh < 8) | (Hh > 170)) & (S > .55) & (V > .35)).astype(np.float32) * nonchar
    n_co, lab_co, st_co, _ = cv2.connectedComponentsWithStats((co > 0).astype(np.uint8))
    co = np.zeros_like(co)
    for i in range(1, n_co):
        if 80 < st_co[i, cv2.CC_STAT_AREA] < 0.02 * W * H: co[lab_co == i] = 1   # mảnh đỏ nhỏ (cờ, khăn)
    co = cv2.GaussianBlur(co, (0, 0), 3)
    nuoc = None
    if cfg.get("nuoc", True):
        # vùng nước: phẳng, ít chi tiết, nửa dưới ảnh, không phải lá
        g = cv2.cvtColor(img[int(oy):int(oy) + H, int(ox):int(ox) + W], cv2.COLOR_RGB2GRAY).astype(np.float32)
        tex = cv2.GaussianBlur(np.abs(cv2.Laplacian(g, cv2.CV_32F)), (0, 0), 9)
        cand = (tex < np.percentile(tex, 35)) & (yy > H * .35) & (la < .3) & (nonchar > .9) & (S < .55)
        cand = cv2.morphologyEx(cand.astype(np.uint8), cv2.MORPH_OPEN, np.ones((15, 15), np.uint8))
        nn, labn, stn, _ = cv2.connectedComponentsWithStats(cand)
        big = np.zeros(cand.shape, np.float32)
        for i in range(1, nn):
            if stn[i, cv2.CC_STAT_AREA] > 0.06 * W * H: big[labn == i] = 1
        if big.sum() > 0: nuoc = cv2.GaussianBlur(big, (0, 0), 12) * nonchar
    if cfg.get("nuoc") is False: nuoc = None
    N1 = _noise(H, W, 60, seed + 1); N2 = _noise(H, W, 60, seed + 2); N3 = _noise(H, W, 25, seed + 3)

    # nhân vật: từng cụm người thở/lắc quanh chân
    comps = []
    mb = (MEN > .5).astype(np.uint8)
    nc, labc, stc, _ = cv2.connectedComponentsWithStats(mb)
    for i in range(1, nc):
        if stc[i, cv2.CC_STAT_AREA] < 0.003 * W * H: continue
        x, y, w_, h_ = stc[i, :4]
        wgt = cv2.GaussianBlur((labc == i).astype(np.float32), (0, 0), 6)
        comps.append(dict(x=x + w_ / 2, top=y, feet=y + h_, h=h_, w=wgt, ph=rng.random() * 6.28, per=2.6 + rng.random()))

    # khuôn mặt trong khung + ai đang nói
    fcs = []
    for k, f in enumerate(faces):
        p = f - [ox, oy]
        if p[:, 0].min() < 0 or p[:, 0].max() > W or p[:, 1].min() < 0 or p[:, 1].max() > H: continue
        size = p[:, 0].max() - p[:, 0].min()
        fcs.append(dict(i=k, p=p, size=size, c=p.mean(0), blink=[]))
    for f in fcs:   # lịch nháy mắt
        t = rng.uniform(.4, 2.5)
        while t < n / fps: f["blink"].append(t); t += rng.uniform(2.4, 5.0)
    env = _env(sc.get("wav"), fps, n)
    noi = np.full(n, -1, np.int32)   # chỉ số mặt đang nói tại mỗi khung
    lop = sc.get("lop")
    map_cfg = sc.get("mat_noi", {})
    ten_hien = []
    for (a, b), ln in zip(sc.get("bounds") or [], sc.get("loi") or []):
        ten = ln[0]; idx = None
        if ten in map_cfg: idx = map_cfg[ten]
        elif lop in ("dan_chuyen", "du_hanh") and ten in NARR and len(fcs) >= 2:
            idx = 0 if ten == "Nhật Minh" else 1          # quy ước ảnh: Minh bên trái, Hân bên phải
        elif lop in ("dan_chuyen", "du_hanh") and ten in NARR and len(fcs) == 1:
            idx = 0
        elif ten not in NARR and fcs:
            idx = int(np.argmax([f["size"] for f in fcs]))  # nhân vật lịch sử: mặt lớn nhất
        if idx is not None and idx < len(fcs):
            noi[int(a * fps): int(b * fps)] = idx

    # máy quay
    huong = sc.get("may_quay", "vao")
    par = cfg.get("thi_sai", 14) * H / 1080       # biên độ thị sai (px) cho chênh lệch độ sâu lớn nhất
    for i in range(n):
        t = i / fps; u = i / max(n - 1, 1); e = u * u * (3 - 2 * u)
        dx = np.zeros((H, W), np.float32); dy = np.zeros((H, W), np.float32)
        # 1) máy quay: zoom chậm + trôi ngang, thị sai theo độ sâu
        z = 1 + (0.045 * e if huong != "ra" else 0.045 * (1 - e))
        cam_x = (e - .5) * 2 * par * (1 if seed % 2 == 0 else -1); cam_y = math.sin(math.pi * u) * par * .25
        dx += (xx - W / 2) * (1 / z - 1) - cam_x * Dn
        dy += (yy - H / 2) * (1 / z - 1) - cam_y * Dn
        # 2) nhân vật thở + lắc
        for c in comps:
            br = 0.006 * math.sin(2 * math.pi * t / c["per"] + c["ph"])
            sw = 0.004 * math.sin(2 * math.pi * t / (c["per"] * 1.6) + c["ph"] * 1.3)
            rel = np.clip((c["feet"] - yy) / max(c["h"], 1), 0, 1)
            dy += c["w"] * (rel * c["h"] * br)
            dx += c["w"] * (rel * rel * c["h"] * sw)
        # 3) đầu + hàm theo lời nói
        for k, f in enumerate(fcs):
            sp = noi[i] == k; a = env[i] if sp else 0.0
            r = f["size"] * .75; G = _gauss((H, W), f["c"][0], f["c"][1], r)
            nod = (0.012 + 0.02 * sp) * f["size"] * math.sin(2 * math.pi * t / (1.7 if sp else 3.3) + k)
            tilt = (0.008 + 0.012 * sp) * f["size"] * math.sin(2 * math.pi * t / 2.9 + 2 * k)
            dy -= G * nod; dx -= G * tilt
            # khẩu hình: độ mở mục tiêu theo âm lượng; ảnh vẽ sẵn miệng mở thì khép bớt lúc im lặng
            p = f["p"]; mo = p[MOI_TRONG]; mcx = mo[:, 0].mean(); mw = mo[:, 0].max() - mo[:, 0].min()
            mo0 = max(0.0, p[14][1] - p[13][1])                    # độ mở sẵn có (môi trong trên – dưới)
            want = (a * mw * 0.30) if sp else 0.0                 # độ mở muốn có
            shift = mo0 * (0.85 if not sp else 0.85 * (1 - min(1, a * 1.6))) - (max(0, want - mo0) if mo0 < mw * .12 else 0)
            f["op"] = max(0.0, want - mo0) if mo0 < mw * .12 else 0.0
            if abs(shift) > .3:
                y_top = p[13][1]; chin = p[152]
                Gj = _gauss((H, W), mcx, (p[14][1] + chin[1]) / 2, mw * .6) * np.clip((yy - y_top) / max(mw * .08, 1), 0, 1)
                dy += Gj * shift                  # dương: kéo môi dưới/hàm lên (khép); âm: hạ xuống (mở)
        # 4) môi trường
        if lua is not None:
            dy += lua * (2.5 * np.sin(yy / 9 - t * 9) - 2.0) * (0.6 + 0.4 * N1); dx += lua * 1.5 * np.sin(yy / 13 + t * 7)
        dx += la * (1.6 * np.sin(2 * math.pi * t / 3.1 + N1 * 3) + .6 * np.sin(t * 5.3 + N3 * 4))
        dy += la * .6 * np.sin(2 * math.pi * t / 2.3 + N2 * 3)
        dy += co * 3.0 * np.sin(xx / 14 - t * 8); dx += co * 1.5 * np.sin(yy / 10 - t * 6)
        if nuoc is not None:
            dx += nuoc * 1.1 * np.sin(yy / 7.0 + t * 2.2 + N1 * .8); dy += nuoc * 0.5 * np.sin(xx / 23 - t * 1.6)
        fr = cv2.remap(img, xx + ox + dx, yy + oy + dy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        frf = None
        if lua is not None:   # lửa bập bùng sáng – tối
            fl = 1 + lua[..., None] * (0.10 * np.sin(t * 13 + N3[..., None] * 6) + 0.06 * np.sin(t * 23))
            frf = fr.astype(np.float32) * fl
        if nuoc is not None:  # dải sáng trôi chậm trên mặt nước
            sp_ = 1 + nuoc * 0.035 * np.sin(yy / 11 - t * 1.4 + N1 * .6)
            frf = (fr.astype(np.float32) if frf is None else frf) * sp_[..., None]
        if frf is not None: fr = np.clip(frf, 0, 255).astype(np.uint8)
        # 5) vẽ lòng miệng + nháy mắt (tọa độ đã dịch theo trường chuyển động gần đúng)
        for k, f in enumerate(fcs):
            p = f["p"]
            def warp_pts(q):
                qi = np.clip(q.astype(int), 0, [W - 1, H - 1])
                return q - np.stack([dx[qi[:, 1], qi[:, 0]], dy[qi[:, 1], qi[:, 0]]], 1)
            if f.get("op", 0) > 0.8:
                mo = warp_pts(p[MOI_TRONG].copy()); cy_ = mo[:, 1].mean()
                lo = mo[:, 1] > cy_; mo[lo, 1] += f["op"] * .9; mo[~lo, 1] -= f["op"] * .1
                col = fr[int(np.clip(cy_, 0, H - 1)), int(np.clip(mo[:, 0].mean(), 0, W - 1))].astype(np.float32)
                dark = tuple(int(v) for v in np.clip(col * .28 + [30, 8, 8], 0, 255))
                cv2.fillPoly(fr, [np.round(mo * 4).astype(np.int32)], dark, lineType=cv2.LINE_AA, shift=2)
            for tb in f["blink"]:
                k2 = (t - tb) / 0.16
                if 0 <= k2 <= 1:
                    cl = 1 - abs(2 * k2 - 1)    # 0→1→0
                    for eye in (MAT_TRAI, MAT_PHAI):
                        q = warp_pts(p[eye].copy()); top = q[:, 1].min(); bot = q[:, 1].max(); ccx = q[:, 0].mean()
                        lid = q.copy(); lid[:, 1] = np.minimum(q[:, 1], top + (bot - top) * cl * 1.05)
                        skin = fr[int(np.clip(top - (bot - top) * 1.2, 0, H - 1)), int(np.clip(ccx, 0, W - 1))]
                        cv2.fillPoly(fr, [np.round(np.vstack([q[:9], lid[9:][::-1]]) * 4).astype(np.int32)], tuple(int(v) for v in skin), lineType=cv2.LINE_AA, shift=2)
                        if cl > .6:
                            yl = int(top + (bot - top) * cl * .95)
                            cv2.line(fr, (int(q[:, 0].min()), yl), (int(q[:, 0].max()), yl), (40, 28, 24), max(1, int(f["size"] / 90)), cv2.LINE_AA)
        yield fr
