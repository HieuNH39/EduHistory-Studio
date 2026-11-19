#!/usr/bin/env python3
"""Biểu ngữ (ảnh bìa) kênh YouTube EduHistory Studio – 2560×1440, nội dung chính trong vùng an toàn 1546×423."""
import math
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 2560, 1440
SAFE = (507, 508, 2053, 931)          # vùng hiện trên mọi thiết bị
DESK = (0, 508, 2560, 931)            # dải hiện trên máy tính
NAVY, NAVY2 = (16, 35, 63), (24, 52, 92)
GOLD, GOLD2, ORANGE, WHITE, MUTED = (201, 139, 43), (233, 176, 74), (242, 107, 29), (255, 255, 255), (165, 182, 206)
F = "assets/fonts/be-vietnam-pro-{}-normal.ttf"
font = lambda w, s: ImageFont.truetype(F.format(w), s)
TAG = "Học trọn Lịch sử 6–9 qua video hoạt hình bám sát SGK"
OUT = "/mnt/user-data/outputs/EduHistory_bieu_ngu_YouTube.png"


def nen():
    im = Image.new("RGB", (W, H), NAVY)
    # quầng sáng nhẹ ở giữa dải hiển thị
    g = Image.new("L", (W, H), 0)
    ImageDraw.Draw(g).ellipse((W // 2 - 1300, H // 2 - 520, W // 2 + 1300, H // 2 + 520), fill=255)
    g = g.filter(ImageFilter.GaussianBlur(260))
    im.paste(Image.new("RGB", (W, H), NAVY2), (0, 0), g)
    return im.convert("RGBA")


def trong_dong(r, mau):
    """Mặt trống đồng vẽ bằng code: vòng tròn đồng tâm, vạch, chấm, ngôi sao 14 cánh."""
    S = 2 * r + 8
    lop = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(lop)
    c = S / 2
    col = mau
    for k, w in [(1.0, 10), (0.93, 4), (0.78, 4), (0.70, 3), (0.50, 3), (0.42, 3)]:
        rr = r * k
        d.ellipse((c - rr, c - rr, c + rr, c + rr), outline=col, width=w)
    for i in range(72):                       # chấm giữa hai vòng ngoài
        a = 2 * math.pi * i / 72
        rr = r * 0.965
        d.ellipse((c + rr * math.cos(a) - 7, c + rr * math.sin(a) - 7, c + rr * math.cos(a) + 7, c + rr * math.sin(a) + 7), fill=col)
    for i in range(96):                       # vạch xiên
        a = 2 * math.pi * i / 96
        r1, r2 = r * 0.80, r * 0.90
        d.line((c + r1 * math.cos(a), c + r1 * math.sin(a), c + r2 * math.cos(a + 0.03), c + r2 * math.sin(a + 0.03)), fill=col, width=4)
    for i in range(48):                       # răng cưa vòng trong
        a1, a2 = 2 * math.pi * i / 48, 2 * math.pi * (i + 0.5) / 48
        d.polygon([(c + r * 0.52 * math.cos(a1), c + r * 0.52 * math.sin(a1)),
                   (c + r * 0.68 * math.cos((a1 + a2) / 2), c + r * 0.68 * math.sin((a1 + a2) / 2)),
                   (c + r * 0.52 * math.cos(a2), c + r * 0.52 * math.sin(a2))], outline=col, width=3)
    pts = []                                  # ngôi sao 14 cánh ở tâm
    for i in range(28):
        a = math.pi * i / 14 - math.pi / 2
        rr = r * (0.40 if i % 2 == 0 else 0.17)
        pts.append((c + rr * math.cos(a), c + rr * math.sin(a)))
    d.polygon(pts, fill=col)
    return lop


def diem_hoa_van(d, y, x0, x1, alpha):
    """Dải hoa văn: hàng chấm + đường răng cưa + hàng chấm."""
    col = GOLD + (alpha,)
    d.line((x0, y - 26, x1, y - 26), fill=col, width=3)
    d.line((x0, y + 26, x1, y + 26), fill=col, width=3)
    step = 36
    pts = [(x, y + (-14 if (i % 2 == 0) else 14)) for i, x in enumerate(range(x0, x1 + step, step))]
    d.line(pts, fill=col, width=4, joint="curve")
    for x in range(x0 + step // 2, x1, step):
        d.ellipse((x - 4, y - 44, x + 4, y - 36), fill=col)
        d.ellipse((x - 4, y + 36, x + 4, y + 44), fill=col)


def ve():
    im = nen()
    # hai mặt trống đồng lớn mờ ở hai đầu dải hiển thị trên máy tính
    for cx, r in [(160, 620), (2400, 620)]:
        t = trong_dong(r, (38, 70, 116, 255))
        im.alpha_composite(t, (int(cx - t.width / 2), int(H / 2 - t.height / 2)))
    d = ImageDraw.Draw(im)
    # dải hoa văn trên và dưới (chỉ hiện trên TV; trên máy tính là mép dải)
    diem_hoa_van(d, 450, 0, W, 90)
    diem_hoa_van(d, 990, 0, W, 90)

    # logo trống đồng của dự án
    logo = Image.open("brand/logo/final/eduhistory-icon.png").convert("RGBA")
    L = 330
    logo = logo.resize((L, L), Image.LANCZOS)
    lx, ly = 545, int(H / 2 - L / 2)
    im.alpha_composite(logo, (lx, ly))

    # chữ
    x = lx + L + 52
    t1, t2, t3 = font(800, 116), font(600, 40), font(500, 28)
    d.text((x, 525), "EduHistory Studio", font=t1, fill=WHITE)
    d.text((x, 682), TAG, font=t2, fill=GOLD2)
    # nhãn lịch đăng
    lb = "Video mới mỗi ngày  ·  11:30  ·  17:30  ·  20:00"
    tf = font(700, 34)
    bw = d.textlength(lb, font=tf) + 64
    d.rounded_rectangle((x, 762, x + bw, 762 + 60), radius=30, fill=ORANGE)
    d.text((x + 32, 762 + 30), lb, font=tf, fill=WHITE, anchor="lm")
    d.text((x, 856), "Cùng Nhật Minh & Hân Hân  ·  Đội ChronoVibe – FPT School Bắc Giang", font=t3, fill=MUTED)

    # kiểm tra mọi chữ nằm trong vùng an toàn
    assert x + d.textlength("EduHistory Studio", font=t1) < SAFE[2]
    assert x + d.textlength(TAG, font=t2) < SAFE[2]
    assert x + d.textlength("Cùng Nhật Minh & Hân Hân  ·  Đội ChronoVibe – FPT School Bắc Giang", font=t3) < SAFE[2]
    im.convert("RGB").save(OUT, optimize=True)
    # bản xem trước: khung vùng an toàn và dải máy tính
    pv = im.copy()
    dp = ImageDraw.Draw(pv)
    dp.rectangle(SAFE, outline=(0, 255, 0, 255), width=4)
    dp.rectangle(DESK, outline=(255, 0, 0, 255), width=4)
    pv.convert("RGB").resize((W // 2, H // 2)).save("/tmp/bieu_ngu_xem.jpg", quality=85)


if __name__ == "__main__":
    ve()
    print(OUT)
