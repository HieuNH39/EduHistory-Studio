"""Chuyển động 2.5D cho ảnh cảnh (dùng khi chưa có clip Kling, hoặc cho các tập ngoài Đợt 1):
tách nhân vật khỏi nền (rembg), vá nền chỗ nhân vật (inpaint), rồi cho nhân vật thở/nhún/lắc nhẹ quanh chân,
nền và nhân vật trôi với tốc độ khác nhau (thị sai), thêm bụi sáng lơ lửng. Mặt nạ được lưu đệm theo ảnh."""
import os, hashlib, math
import numpy as np, cv2
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "renders/_cache/mat_na"); os.makedirs(CACHE, exist_ok=True)
_SESS = {}

def mat_na(img_rgb, kieu="u2net_human_seg"):
    key = hashlib.sha1(img_rgb[::7, ::7].tobytes() + kieu.encode()).hexdigest()[:16]
    p = os.path.join(CACHE, key + ".png")
    if os.path.exists(p): return cv2.imread(p, cv2.IMREAD_GRAYSCALE)
    from rembg import remove, new_session
    if kieu not in _SESS: _SESS[kieu] = new_session(kieu)
    h, w = img_rgb.shape[:2]; sc = min(1.0, 1280 / max(h, w))
    small = cv2.resize(img_rgb, (int(w * sc), int(h * sc)))
    out = np.array(remove(Image.fromarray(small), session=_SESS[kieu], only_mask=True))
    m = cv2.resize(out, (w, h)); m = (m > 110).astype(np.uint8) * 255
    # bỏ mảnh vụn nhỏ
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    keep = np.zeros_like(m)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] > 0.004 * h * w: keep[lab == i] = 255
    cv2.imwrite(p, keep); return keep

def _cover(img, W, H, z, cx=.5, cy=.5):
    h, w = img.shape[:2]; s = max(W / w, H / h) * z
    M = np.float32([[s, 0, W * cx - w * cx * s], [0, s, H * cy - h * cy * s]])
    return M

def frames(img_rgb, W, H, n, fps=30, huong="vao", seed=0):
    m = mat_na(img_rgb)
    has_fg = m.mean() > 2
    h, w = img_rgb.shape[:2]
    if has_fg:
        dil = cv2.dilate(m, np.ones((15, 15), np.uint8))
        nen = cv2.inpaint(cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR), dil, 7, cv2.INPAINT_TELEA)
        nen = cv2.cvtColor(nen, cv2.COLOR_BGR2RGB)
        alpha = cv2.GaussianBlur(m, (5, 5), 0).astype(np.float32) / 255
        ys, xs = np.nonzero(m); feet_y = ys.max(); cxs = xs.mean()
        # từng cụm nhân vật lắc nhịp riêng
        n_lab, lab = cv2.connectedComponents(m)
    else:
        nen = img_rgb
    rng = np.random.default_rng(seed)
    P = rng.random((40, 4))   # bụi sáng: x, y, tốc độ, pha
    z0, z1 = (1.0, 1.06) if huong != "ra" else (1.06, 1.0)
    for i in range(n):
        t = i / fps; u = i / max(n - 1, 1); e = u * u * (3 - 2 * u)
        z = z0 + (z1 - z0) * e
        Mb = _cover(nen, W, H, z)
        bg = cv2.warpAffine(nen, Mb, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        if has_fg:
            zf = z * (1 + 0.025 * e)                       # thị sai: nhân vật tiến gần hơn nền
            Mf = _cover(img_rgb, W, H, zf)
            # thở / nhún: co giãn dọc quanh chân + lắc nhẹ
            br = 1 + 0.010 * math.sin(2 * math.pi * t / 2.8)
            sway = math.radians(0.7 * math.sin(2 * math.pi * t / 4.1 + 0.6))
            A = np.array([[1, 0, -cxs], [0, 1, -feet_y], [0, 0, 1]], np.float32)
            R = np.array([[math.cos(sway), -math.sin(sway), 0], [math.sin(sway) * 0 + math.sin(sway), math.cos(sway) * br, 0], [0, 0, 1]], np.float32)
            B = np.array([[1, 0, cxs], [0, 1, feet_y], [0, 0, 1]], np.float32)
            Mfull = np.vstack([Mf, [0, 0, 1]]) @ B @ R @ A
            fg = cv2.warpAffine(img_rgb, Mfull[:2], (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
            al = cv2.warpAffine(alpha, Mfull[:2], (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)[..., None]
            fr = (bg * (1 - al) + fg * al).astype(np.float32)
        else:
            fr = bg.astype(np.float32)
        yield np.clip(fr, 0, 255).astype(np.uint8)
