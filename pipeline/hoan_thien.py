#!/usr/bin/env python3
"""Ghép cuối một tập: phụ đề song ngữ trong khung kính mờ (kiểu Liquid Glass) + logo góc + âm thanh.

Dùng chung cho render.py (sau khi dựng hình) và cho việc hoàn thiện lại các tập đã dựng từ phần hình "sạch"
(renders/_cache/<MÃ>/video.mp4, chưa có phụ đề, chưa có logo) – không phải dựng lại toàn bộ:

    python3 pipeline/hoan_thien.py data/scripts/L7-B14-04.json renders/v1 [--giu-cau-hoi]

Mặc định khi hoàn thiện lại sẽ thay các cảnh câu hỏi trong hình sạch bằng thẻ "EduHistory hỏi bạn" thiết kế mới
(chuyển cảnh mềm với cảnh trước/sau như lúc dựng).

Khung phụ đề: tiếng Việt dòng trên (đậm, trắng), tiếng Anh dòng dưới (nghiêng, vàng kem), cùng nằm trong một
khung bo tròn; nền khung là chính hình phía sau được làm mờ, phủ lớp kính xanh đêm trong suốt, viền sáng mảnh,
vệt sáng phía trên và bóng đổ mềm. Khung đặt sát mép dưới (ngang: cách đáy 3 %, dọc: 3,5 %).
"""
import os, sys, json, time, subprocess, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
import render, effects  # noqa: E402

FPS = render.FPS
FONT_DIR = render.FONT_DIR
NAVY = np.array([16, 35, 63], np.float32)


# ------------------------------------------------------------------ phụ đề → sự kiện (dùng lại cách chia câu của render)
def su_kien_phu_de(cues, vertical):
    maxlen = 34 if vertical else 58
    ev = []
    for t0, t1, vi, en in cues:
        ml = maxlen
        while True:
            vparts = render.chunk(vi, ml)
            eparts = render.align_en(en or "", vparts)
            if ml <= 22 or all(len(e) <= ml * 1.45 for e in eparts): break
            ml -= 6
        weights = [max(len(v), 1) for v in vparts]; span = t1 - t0; acc = t0
        for v, e, w in zip(vparts, eparts, weights):
            d = span * w / sum(weights)
            ev.append([acc, acc + d, v, e]); acc += d
    ev.sort(key=lambda e: e[0])
    return ev


class KhungKinh:
    """Vẽ khung phụ đề kính mờ lên từng khung hình (numpy RGB)."""

    def __init__(self, W, H, vertical):
        self.W, self.H, self.v = W, H, vertical
        s = W / 1080 if vertical else H / 1080
        self.s = s
        self.f_vi = ImageFont.truetype(os.path.join(FONT_DIR, "be-vietnam-pro-700-normal.ttf"), int((46 if vertical else 42) * s))
        self.f_en_path = os.path.join(FONT_DIR, "be-vietnam-pro-500-italic.ttf")
        self.en_size = int((34 if vertical else 31) * s)
        self.padx, self.pady, self.gap = 36 * s, 16 * s, 6 * s
        self.R = int((30 if vertical else 26) * s)
        self.bottom = H * (1 - (0.035 if vertical else 0.03))   # sát mép dưới (thầy chốt 15/11)
        self.maxw = W - 2 * (48 * s if vertical else W * 0.08)
        self.cache = {}

    def _lop(self, vi, en):
        key = (vi, en)
        if key in self.cache: return self.cache[key]
        d0 = ImageDraw.Draw(Image.new("RGB", (8, 8)))
        f_vi = self.f_vi
        while d0.textlength(vi, font=f_vi) > self.maxw - 2 * self.padx and f_vi.size > 24:
            f_vi = ImageFont.truetype(f_vi.path, f_vi.size - 2)
        sz = self.en_size; f_en = ImageFont.truetype(self.f_en_path, sz)
        while en and d0.textlength(en, font=f_en) > self.maxw - 2 * self.padx and sz > self.en_size * 0.8:
            sz -= 2; f_en = ImageFont.truetype(self.f_en_path, sz)
        en_lines = effects._wrap(d0, en, f_en, self.maxw - 2 * self.padx) if en else []
        lh_vi = f_vi.size * 1.28; lh_en = f_en.size * 1.28
        tw = max([d0.textlength(vi, font=f_vi)] + [d0.textlength(l, font=f_en) for l in en_lines])
        pw = int(min(self.maxw, max(tw + 2 * self.padx, self.W * (0.34 if self.v else 0.30))))
        ph = int(self.pady * 2 + lh_vi + (self.gap + lh_en * len(en_lines) if en_lines else 0))
        x0 = int((self.W - pw) / 2); y1 = int(self.bottom); y0 = y1 - ph
        # mặt nạ bo tròn (khử răng cưa bằng vẽ gấp 4 rồi thu nhỏ)
        m = Image.new("L", (pw * 4, ph * 4), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, pw * 4 - 1, ph * 4 - 1], radius=self.R * 4, fill=255)
        mask = np.asarray(m.resize((pw, ph), Image.LANCZOS)).astype(np.float32)[..., None] / 255.0
        # bóng đổ (vùng lớn hơn khung)
        e = int(28 * self.s)
        sh = Image.new("L", (pw + 2 * e, ph + 2 * e), 0)
        ImageDraw.Draw(sh).rounded_rectangle([e, e + int(8 * self.s), e + pw, e + ph + int(8 * self.s)], radius=self.R, fill=255)
        sh = np.asarray(sh.filter(ImageFilter.GaussianBlur(int(16 * self.s)))).astype(np.float32)[..., None] / 255.0 * 0.38
        # lớp chữ + viền sáng + vệt sáng trên
        L = Image.new("RGBA", (pw, ph), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        hl = Image.new("L", (pw, ph), 0); dh = ImageDraw.Draw(hl)
        for yy in range(int(ph * 0.55)):
            dh.line([0, yy, pw, yy], fill=int(34 * (1 - yy / (ph * 0.55)) ** 1.6))
        hl = Image.fromarray((np.asarray(hl).astype(np.float32) * mask[..., 0]).astype(np.uint8))
        L.paste(Image.new("RGBA", (pw, ph), (255, 255, 255, 255)), (0, 0), hl)
        b = Image.new("RGBA", (pw * 4, ph * 4), (0, 0, 0, 0))
        ImageDraw.Draw(b).rounded_rectangle([2, 2, pw * 4 - 3, ph * 4 - 3], radius=self.R * 4, outline=(255, 255, 255, 120), width=int(5 * self.s))
        b = b.resize((pw, ph), Image.LANCZOS); L = Image.alpha_composite(L, b); d = ImageDraw.Draw(L)
        y = self.pady - f_vi.size * 0.08
        wv = d.textlength(vi, font=f_vi)
        d.text(((pw - wv) / 2 + 2, y + 2), vi, font=f_vi, fill=(0, 0, 0, 110))
        d.text(((pw - wv) / 2, y), vi, font=f_vi, fill=(255, 255, 255, 255))
        y += lh_vi + self.gap
        for ln in en_lines:
            we = d.textlength(ln, font=f_en)
            d.text(((pw - we) / 2 + 1, y + 2), ln, font=f_en, fill=(0, 0, 0, 90))
            d.text(((pw - we) / 2, y), ln, font=f_en, fill=(255, 226, 160, 255)); y += lh_en
        la = np.asarray(L).astype(np.float32)
        lop = dict(x0=x0, y0=y0, pw=pw, ph=ph, mask=mask, sh=sh, e=e, rgb=la[..., :3], a=la[..., 3:] / 255.0)
        self.cache[key] = lop
        return lop

    def ve(self, fr, vi, en, alpha=1.0):
        """fr: mảng HxWx3 uint8 (ghi đè)."""
        if alpha <= 0.01: return fr
        o = self._lop(vi, en); x0, y0, pw, ph, e = o["x0"], o["y0"], o["pw"], o["ph"], o["e"]
        # bóng đổ
        sy0, sx0 = max(0, y0 - e), max(0, x0 - e); sy1, sx1 = min(self.H, y0 + ph + e), min(self.W, x0 + pw + e)
        shm = o["sh"][sy0 - (y0 - e):sy1 - (y0 - e), sx0 - (x0 - e):sx1 - (x0 - e)]
        reg = fr[sy0:sy1, sx0:sx1].astype(np.float32)
        fr[sy0:sy1, sx0:sx1] = (reg * (1 - shm * alpha)).astype(np.uint8)
        # kính: hình phía sau làm mờ + phủ xanh đêm + ánh sáng nhẹ
        crop = fr[y0:y0 + ph, x0:x0 + pw].astype(np.float32)
        sm = cv2.resize(crop, (max(1, pw // 4), max(1, ph // 4)), interpolation=cv2.INTER_AREA)
        sm = cv2.GaussianBlur(sm, (0, 0), 3.2)
        bl = cv2.resize(sm, (pw, ph), interpolation=cv2.INTER_LINEAR)
        lum = bl.mean(axis=2, keepdims=True)
        bl = lum + (bl - lum) * 1.25                       # tăng nhẹ độ bão hoà như kính thật
        glass = bl * 0.42 + NAVY * 0.58 + 8
        m = o["mask"] * alpha
        out = crop * (1 - m) + glass * m
        a = o["a"] * alpha
        out = out * (1 - a) + o["rgb"] * a
        fr[y0:y0 + ph, x0:x0 + pw] = np.clip(out, 0, 255).astype(np.uint8)
        return fr


def _logo(W, H, vertical):
    wm = Image.open(os.path.join(ROOT, render.CFG["logo"]["watermark"])).convert("RGBA")
    ww = int(W * (0.30 if vertical else 0.17)); wm = wm.resize((ww, int(wm.height * ww / wm.width)), Image.LANCZOS)
    a = np.asarray(wm).astype(np.float32); margin = int(W * 0.025)
    return dict(x=W - ww - margin, y=margin, rgb=a[..., :3], a=a[..., 3:] / 255.0 * 0.92)


def _khung_tai(path, idx, W, H):
    """Lấy đúng một khung hình (số thứ tự idx) từ video."""
    p = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", f"{max(idx, 0) / FPS:.4f}", "-i", path, "-frames:v", "1",
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True)
    if len(p.stdout) < W * H * 3: return None
    return np.frombuffer(p.stdout[:W * H * 3], np.uint8).reshape(H, W, 3).astype(np.float32)


def ghep(spec, scenes, starts, total, intro, outro, silent, mix, out, va_cau_hoi=False, log=None):
    """Đọc hình sạch → (thay cảnh câu hỏi) → phụ đề kính + logo → mã hoá cùng âm thanh."""
    vertical = spec.get("huong") == "doc"
    W, H = render.CFG["video"]["portrait"] if vertical else render.CFG["video"]["landscape"]
    cues = []
    for k, s in enumerate(scenes):
        if not s["wav"]: continue
        for (a, b), ln in zip(s["bounds"], s["loi"]):
            cues.append((starts[k] + 0.15 + a, starts[k] + 0.15 + b, ln[1], ln[2] if len(ln) > 2 else ""))
    ev = su_kien_phu_de(cues, vertical)
    kk = KhungKinh(W, H, vertical); lg = _logo(W, H, vertical)
    # các đoạn câu hỏi cần thay
    thay = {}; xf_ = int(render.XFADE * FPS)
    if va_cau_hoi:
        xf = int(render.XFADE * FPS); F = int(intro * FPS)
        for k, s in enumerate(scenes):
            n = int(round(s["length"] * FPS))
            if s.get("lop") == "cau_hoi":
                b = s.get("bounds") or [(0, 3), (6, 8)]
                thay[k] = dict(F=F, n=n, last=(k == len(scenes) - 1),
                               gen=lambda s=s, n=n, b=b: effects.cau_hoi(W, H, n, s["cau_hoi"], FPS, q_end=b[0][1] + 0.15, reveal=b[-1][0] + 0.15),
                               prev=_khung_tai(silent, F - 1, W, H) if F > 0 else None,
                               next=_khung_tai(silent, F + n, W, H))
            F += n - xf
    idx_map = {}
    for k, r in thay.items():
        for i in range(r["n"]): idx_map[r["F"] + i] = (k, i)
    dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", silent, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-i", mix, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
                            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-shortest", out],
                           stdin=subprocess.PIPE)
    fsz = W * H * 3; i = 0; e_i = 0; gens = {}
    while True:
        buf = dec.stdout.read(fsz)
        if len(buf) < fsz: break
        fr = np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy()
        t = i / FPS
        if i in idx_map:
            k, j = idx_map[i]; r = thay[k]
            if k not in gens: gens[k] = iter(r["gen"]())
            c = next(gens[k]).astype(np.float32)
            if j < xf_:
                a = (j + 1) / xf_
                c = (r["prev"] * (1 - a) + c * a) if r["prev"] is not None else c * a
            elif j >= r["n"] - xf_ and not r["last"] and r["next"] is not None:
                bb = (j - (r["n"] - xf_) + 1) / xf_
                c = c * (1 - bb) + r["next"] * bb
            fr = np.clip(c, 0, 255).astype(np.uint8)
        # logo góc (bỏ ở khung mở đầu / kết)
        if intro <= t <= total - outro:
            y, x = lg["y"], lg["x"]; h, w = lg["rgb"].shape[:2]
            reg = fr[y:y + h, x:x + w].astype(np.float32)
            fr[y:y + h, x:x + w] = (reg * (1 - lg["a"]) + lg["rgb"] * lg["a"]).astype(np.uint8)
        # phụ đề
        while e_i < len(ev) and ev[e_i][1] < t: e_i += 1
        if e_i < len(ev) and ev[e_i][0] <= t <= ev[e_i][1]:
            t0, t1, vi, en = ev[e_i]
            prev_end = ev[e_i - 1][1] if e_i > 0 else -9
            next_st = ev[e_i + 1][0] if e_i + 1 < len(ev) else 1e9
            a = 1.0
            if t0 - prev_end > 0.2: a = min(a, (t - t0) / 0.15 + 0.15)
            if next_st - t1 > 0.2: a = min(a, (t1 - t) / 0.15 + 0.15)
            kk.ve(fr, vi, en, max(0.0, min(1.0, a)))
        enc.stdin.write(fr.tobytes()); i += 1
    enc.stdin.close(); enc.wait(); dec.wait()
    return out


def hoan_thien_lai(spec_path, out_dir, va_cau_hoi=True):
    spec = render.load_spec(spec_path)
    work = os.path.join(render.CACHE, spec["id"]); silent = os.path.join(work, "video.mp4")
    assert os.path.exists(silent), "chưa có hình sạch: " + silent
    scenes, starts, total, intro, outro = render.tinh_moc_canh(spec)
    dv = render.dur(silent)
    if abs(dv - total) > 1.0: raise SystemExit(f"{spec['id']}: lệch {dv:.1f}s / {total:.1f}s – kịch bản đã đổi, cần dựng lại hình.")
    log = {"id": spec["id"], "bat_dau": time.time(), "khau": {}, "ghi_chu": "hoàn thiện lại: phụ đề kính mờ + thẻ câu hỏi mới"}
    t0 = time.time()
    mix = os.path.join(work, "mix.wav")
    if not os.path.exists(mix): mix = render.dung_am_thanh(spec, scenes, starts, total, intro, outro, work, log)
    log["khau"]["am_thanh_s"] = round(time.time() - t0, 1)
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"{spec['id']}.mp4"); tmp = out + ".tam.mp4"
    t0 = time.time()
    ghep(spec, scenes, starts, total, intro, outro, silent, mix, tmp, va_cau_hoi=va_cau_hoi)
    os.replace(tmp, out)
    log["khau"]["ghep_cuoi_s"] = round(time.time() - t0, 1); log["thoi_luong_video_s"] = round(total, 1)
    with open(os.path.join(ROOT, "data/logs/san-xuat.jsonl"), "a") as f:
        f.write(json.dumps(log, ensure_ascii=False) + "\n")
    print("→", out, json.dumps(log["khau"], ensure_ascii=False))
    return out


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    hoan_thien_lai(a[0], a[1] if len(a) > 1 else os.path.join(ROOT, "renders/v1"), va_cau_hoi="--giu-cau-hoi" not in sys.argv)
