"""Hiệu ứng dựng bằng code: cổng thời gian trống đồng, khung chờ (animatic) khi chưa có hình."""
import os, math, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(ROOT, "pipeline/config.json")))
FONT_DIR = os.path.join(ROOT, "assets/fonts")

def _ease(t):
    t = min(max(t, 0), 1); return t * t * (3 - 2 * t)

def trong_dong(W, H, n, text=""):
    """Cổng thời gian: mặt trống đồng (logo) xoay nhanh, lao về phía máy quay, tia sáng toả, hiện mốc năm, loé sáng chuyển cảnh."""
    icon = Image.open(os.path.join(ROOT, CFG["logo"]["icon"])).convert("RGBA")
    big = ImageFont.truetype(os.path.join(FONT_DIR, "playfair-display-900-normal.ttf"), int(H * 0.17))
    cx, cy = W // 2, H // 2
    rays = Image.new("L", (W, H), 0); d = ImageDraw.Draw(rays)
    for k in range(24):  # tia sáng tĩnh, xoay theo thời gian
        a0 = k * 2 * math.pi / 24; a1 = a0 + 0.06
        R = W
        d.polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)), (cx + R * math.cos(a1), cy + R * math.sin(a1))], fill=255)
    rays = rays.filter(ImageFilter.GaussianBlur(6))
    for i in range(n):
        t = i / max(n - 1, 1)
        bg = Image.new("RGB", (W, H), (12, 26, 48))
        rot = rays.rotate(t * 40, center=(cx, cy))
        glow = Image.new("RGB", (W, H), (201, 139, 43))
        bg = Image.composite(glow, bg, rot.point(lambda p: int(p * 0.35 * _ease(t * 2))))
        s = int(min(W, H) * (0.30 + 1.6 * _ease((t - 0.35) / 0.65) ** 2))
        ic = icon.resize((max(s, 2), max(s, 2)), Image.LANCZOS).rotate(-720 * _ease(t), resample=Image.BICUBIC)
        alpha = ic.split()[3].point(lambda p: int(p * min(1, t * 4)))
        ic.putalpha(alpha)
        bg.paste(ic, (cx - ic.width // 2, cy - ic.height // 2), ic)
        if text:
            kt = _ease((t - 0.15) / 0.3) * (1 - _ease((t - 0.75) / 0.2))
            if kt > 0:
                layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(layer)
                w = dd.textlength(text, font=big)
                dd.text((cx - w / 2 + 4, cy - H * 0.11 + 4), text, font=big, fill=(0, 0, 0, int(160 * kt)))
                dd.text((cx - w / 2, cy - H * 0.11), text, font=big, fill=(255, 236, 200, int(255 * kt)))
                bg.paste(layer, (0, 0), layer)
        arr = np.asarray(bg).astype(np.float32)
        flash = _ease((t - 0.82) / 0.18)
        if flash > 0: arr = arr * (1 - flash) + 255 * flash
        yield arr.astype(np.uint8)

def cho(W, H, n, sc):
    """Khung chờ cho cảnh chưa có hình (bản dựng thử): ghi rõ lớp cảnh và mô tả hình cần tạo."""
    f1 = ImageFont.truetype(os.path.join(FONT_DIR, "be-vietnam-pro-700-normal.ttf"), int(H * 0.04))
    f2 = ImageFont.truetype(os.path.join(FONT_DIR, "be-vietnam-pro-400-normal.ttf"), int(H * 0.03))
    names = {"dan_chuyen": "DẪN CHUYỆN", "du_hanh": "DU HÀNH", "tai_hien": "TÁI HIỆN"}
    img = Image.new("RGB", (W, H), (34, 40, 52)); d = ImageDraw.Draw(img)
    d.text((W * 0.08, H * 0.16), f"[{names.get(sc.get('lop'), 'CẢNH')} – cảnh {sc.get('so', '')}]", font=f1, fill=(242, 160, 90))
    words = (sc.get("hinh") or "").split(); line = ""; y = H * 0.27
    for w in words:
        if d.textlength(line + " " + w, font=f2) > W * 0.84:
            d.text((W * 0.08, y), line, font=f2, fill=(230, 230, 230)); y += H * 0.05; line = w
        else: line = (line + " " + w).strip()
    if line: d.text((W * 0.08, y), line, font=f2, fill=(230, 230, 230))
    arr = np.asarray(img)
    for i in range(n): yield arr
