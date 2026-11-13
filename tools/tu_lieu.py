#!/usr/bin/env python3
"""Dựng khung ảnh tư liệu thật (ảnh/phim lịch sử) thành cảnh 16:9 cho video.

- Ảnh gốc giữ nguyên nội dung (không vẽ lại, không tô màu, không AI): chỉ phóng vừa khung, làm nét nhẹ.
- Nền: chính ảnh đó phóng to, làm mờ, tối và ngả nâu nhẹ -> không có dải đen, hợp mọi tỉ lệ ảnh.
- Ảnh đặt trên viền trắng mảnh + bóng đổ, nằm phía trên vùng phụ đề.
- Dòng ghi nguồn nhỏ ngay dưới ảnh (tác giả · năm · nơi lưu · giấy phép) – bắt buộc với ảnh CC BY/CC BY-SA.
Ghi kèm nguồn vào assets/episodes/<MA>/nguon_tu_lieu.json.

Dùng: python3 tools/tu_lieu.py <anh_goc> <MA> <so_canh> --nguon "Ảnh: TTXVN, 1954" --giay-phep "Phạm vi công cộng" \
         --trang https://commons.wikimedia.org/wiki/File:... [--chu-thich "Dân công thồ lương thực ra mặt trận"]
"""
import argparse, json, os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 2560, 1440


def font(size, bold=False):
    for p in (["assets/fonts/be-vietnam-pro-600-normal.ttf"] if bold else
              ["assets/fonts/be-vietnam-pro-400-normal.ttf"]):
        fp = os.path.join(ROOT, p)
        if os.path.exists(fp): return ImageFont.truetype(fp, size)
    for fp in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",):
        if os.path.exists(fp): return ImageFont.truetype(fp, size)
    return ImageFont.load_default()


def dung(src, out, nguon, giay_phep, chu_thich=None):
    im = Image.open(src).convert("RGB")
    # nền: ảnh phóng to phủ kín, mờ, tối, ngả nâu
    s = max(W / im.width, H / im.height)
    bg = im.resize((int(im.width * s) + 2, int(im.height * s) + 2), Image.LANCZOS)
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    bg = bg.filter(ImageFilter.GaussianBlur(38))
    bg = ImageEnhance.Brightness(bg).enhance(0.38)
    tint = Image.new("RGB", (W, H), (58, 40, 24))
    bg = Image.blend(bg, tint, 0.35)
    # vùng đặt ảnh: chừa phụ đề phía dưới (~19%) và nhãn phía trên
    top, bottom = int(H * 0.085), int(H * 0.74)
    maxw, maxh = int(W * 0.84), bottom - top
    k = min(maxw / im.width, maxh / im.height)
    pw, ph = int(im.width * k), int(im.height * k)
    ph_img = im.resize((pw, ph), Image.LANCZOS)
    if k > 1.4:   # ảnh gốc nhỏ: làm nét nhẹ sau khi phóng
        ph_img = ph_img.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
    x, y = (W - pw) // 2, top + (maxh - ph) // 2
    b = max(6, W // 400)
    sh = Image.new("L", (W, H), 0); d = ImageDraw.Draw(sh)
    d.rectangle((x - b + 14, y - b + 18, x + pw + b + 14, y + ph + b + 18), fill=170)
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    bg.paste((0, 0, 0), (0, 0), sh)
    d = ImageDraw.Draw(bg)
    d.rectangle((x - b, y - b, x + pw + b - 1, y + ph + b - 1), fill=(246, 240, 228))
    bg.paste(ph_img, (x, y))
    # ghi nguồn dưới ảnh, canh phải theo mép ảnh
    f = font(30)
    line = " · ".join(t for t in (nguon, giay_phep) if t)
    tw = d.textlength(line, font=f)
    d.text((x + pw - tw, y + ph + b + 10), line, font=f, fill=(232, 222, 205))
    if chu_thich:
        fc = font(34, bold=True)
        d.text((x, y + ph + b + 8), chu_thich, font=fc, fill=(255, 246, 230)) if d.textlength(chu_thich, font=fc) + tw + 60 < pw else None
    bg.save(out, quality=93)
    return (pw, ph, k)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("ma"); ap.add_argument("so", type=int)
    ap.add_argument("--nguon", required=True); ap.add_argument("--giay-phep", default="")
    ap.add_argument("--trang", default=""); ap.add_argument("--tep", default="")
    ap.add_argument("--chu-thich", default=None); ap.add_argument("--mo-ta", default="")
    a = ap.parse_args()
    d = os.path.join(ROOT, "assets/episodes", a.ma); os.makedirs(d, exist_ok=True)
    out = os.path.join(d, f"canh-{a.so:02d}.jpg")
    pw, ph, k = dung(a.src, out, a.nguon, a.giay_phep, a.chu_thich)
    meta_p = os.path.join(d, "nguon_tu_lieu.json")
    meta = json.load(open(meta_p)) if os.path.exists(meta_p) else {}
    meta[str(a.so)] = {"tep": a.tep, "trang": a.trang, "nguon": a.nguon, "giay_phep": a.giay_phep, "mo_ta": a.mo_ta,
                       "kich_thuoc_goc": list(Image.open(a.src).size), "he_so_phong": round(k, 2)}
    json.dump(meta, open(meta_p, "w"), ensure_ascii=False, indent=1)
    prev = os.path.join(ROOT, "tmp/qa", f"{a.ma}_canh-{a.so:02d}_xem.jpg"); os.makedirs(os.path.dirname(prev), exist_ok=True)
    Image.open(out).resize((960, 540)).save(prev, quality=85)
    print(out, f"ảnh {pw}x{ph} (phóng x{k:.2f})")


if __name__ == "__main__":
    main()
