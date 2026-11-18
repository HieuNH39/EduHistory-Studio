#!/usr/bin/env python3
"""Hình vẽ minh hoạ dựng bằng code thay cho thẻ "Ảnh tư liệu trong SGK" (thầy yêu cầu 18/11/2026 14:01).

Dùng cho cảnh không tìm được ảnh có giấy phép mở mà nội dung không hợp để AI vẽ (người thật, sự kiện ngoại giao,
tượng thờ, văn bản có chữ). Mỗi hình ghi rõ dòng "Hình vẽ minh hoạ bằng đồ hoạ máy tính – không phải ảnh tư liệu".
Bố cục chừa dải phụ đề phía dưới và góc logo trên phải như các thẻ khác.

Dùng: python3 tools/hinh_ve_thay.py <MA> <so_canh> <kieu>
kieu: le_paria | quan_am | asean_1967 | asean_1999 | vi_xuyen
"""
import json, math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
import effects

GOLD, CREAM, ORANGE, NAVY = (201, 139, 43), (250, 244, 230), (242, 107, 29), (16, 30, 58)
NHAN = "Hình vẽ minh hoạ bằng đồ hoạ máy tính – không\u00a0phải ảnh\u00a0tư\u00a0liệu"


def F(w, z, ho="be-vietnam-pro"):
    return ImageFont.truetype(os.path.join(ROOT, f"assets/fonts/{ho}-{w}-normal.ttf"), int(z))


def chu_giua(d, cx, y, s, f, fill):
    d.text((cx - d.textlength(s, font=f) / 2, y), s, font=f, fill=fill)


def wrap(d, s, f, w):
    out, line = [], ""
    for t in s.split(" "):
        if line and d.textlength(line + " " + t, font=f) > w: out.append(line); line = t
        else: line = (line + " " + t).strip()
    if line: out.append(line)
    return out


def nhan_duoi(d, W, H, y, s):
    f = F(500, 30 * s)
    chu_giua(d, W / 2, y, NHAN, f, (214, 200, 176))


# ------------------------------------------------------------------ Le Paria
def le_paria(W, H, s):
    img = effects._nen_thuong_hieu(W, H).convert("RGB"); d = ImageDraw.Draw(img)
    # tờ báo: giấy ngà, hơi nghiêng, bóng đổ
    ph = int(H * .62); pw = int(ph * .80)
    giay = Image.new("RGB", (pw, ph), (236, 226, 204)); g = ImageDraw.Draw(giay)
    rng = np.random.default_rng(7)
    nhieu = (rng.normal(0, 7, (ph, pw, 1)) * np.ones((1, 1, 3))).astype(np.int16)
    giay = Image.fromarray(np.clip(np.asarray(giay, np.int16) + nhieu, 0, 255).astype(np.uint8)); g = ImageDraw.Draw(giay)
    m = pw * .07; ink = (46, 40, 34)
    fm = F(900, pw * .15, "playfair-display")
    chu_giua(g, pw / 2, ph * .045, "LE PARIA", fm, ink)
    y = ph * .045 + fm.size * 1.12
    g.line([(m, y), (pw - m, y)], fill=ink, width=max(3, int(4 * s))); y += 10 * s
    g.line([(m, y), (pw - m, y)], fill=ink, width=max(1, int(2 * s))); y += 14 * s
    fd = F(400, pw * .028, "playfair-display")
    g.text((m, y), "Paris", font=fd, fill=ink); t = "1922"; g.text((pw - m - g.textlength(t, font=fd), y), t, font=fd, fill=ink)
    y += fd.size * 1.8
    # các cột chữ (chỉ là nét, không phải chữ thật)
    cot = 3; gw = (pw - 2 * m - (cot - 1) * pw * .03) / cot
    rnd = random.Random(3)
    for c in range(cot):
        x0 = m + c * (gw + pw * .03); yy = y
        g.rectangle([x0, yy, x0 + gw, yy + ph * .018], fill=(70, 62, 52)); yy += ph * .04
        while yy < ph * .94:
            if rnd.random() < .07: yy += ph * .02; continue
            L = gw * (rnd.uniform(.55, .95) if rnd.random() < .15 else rnd.uniform(.92, 1.0))
            g.line([(x0, yy), (x0 + L, yy)], fill=(128, 118, 100), width=max(2, int(3 * s))); yy += ph * .0175
        if c < cot - 1: g.line([(x0 + gw + pw * .015, y), (x0 + gw + pw * .015, ph * .94)], fill=(150, 138, 118), width=1)
    giay = giay.rotate(-2.2, expand=True, resample=Image.BICUBIC, fillcolor=(0, 0, 0))
    mask = Image.new("L", (pw, ph), 255).rotate(-2.2, expand=True, resample=Image.BICUBIC)
    x, y0 = int(W * .14), int(H * .085)
    sh = Image.new("L", (W, H), 0); ImageDraw.Draw(sh).bitmap((x + 18, y0 + 22), mask, fill=150)
    img.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(24)))
    img.paste(giay, (x, y0), mask)
    # chú thích bên phải
    cx = W * .70; f1 = F(800, 64 * s); f2 = F(600, 40 * s); f3 = F(400, 36 * s)
    yy = H * .26
    chu_giua(d, cx, yy, "Le Paria", f1, GOLD); yy += f1.size * 1.3
    chu_giua(d, cx, yy, "(Người cùng khổ)", f2, CREAM); yy += f2.size * 2.0
    for ln in wrap(d, "Báo tiếng Pháp ra đời ở Pa-ri năm 1922; Nguyễn Ái Quốc là Chủ nhiệm kiêm chủ bút.", f3, W * .36):
        chu_giua(d, cx, yy, ln, f3, (232, 222, 205)); yy += f3.size * 1.45
    f4 = F(500, 30 * s); yy += 30 * s
    for ln in wrap(d, NHAN, f4, W * .36):
        chu_giua(d, cx, yy, ln, f4, (214, 200, 176)); yy += f4.size * 1.4
    return img


# ------------------------------------------------------------------ Quan Âm nghìn mắt nghìn tay (khung dọc)
def quan_am(W, H, s):
    img = effects._nen_thuong_hieu(W, H).convert("RGB")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    cx, cy = W / 2, H * .285; R = W * .43; lw = max(2, int(3 * s))
    g = (*GOLD, 255); gm = (*GOLD, 60)

    def canh(x, y, a, dai, rong):
        """Bàn tay cách điệu: cánh hình lá (elip dài) hướng ra ngoài, giữa lòng có một con mắt."""
        ca, sa = math.cos(a), math.sin(a)
        pts = []
        for t in np.linspace(0, 2 * math.pi, 40):
            u, v = dai / 2 * math.cos(t), rong / 2 * math.sin(t) * (1 - .25 * math.cos(t))
            pts.append((x + (u + dai / 2) * ca - v * sa, y + (u + dai / 2) * sa + v * ca))
        d.polygon(pts, fill=gm, outline=g, width=lw)
        ex, ey = x + dai * .52 * ca, y + dai * .52 * sa; el, ew = rong * .30, rong * .13
        mat = [(ex + el * math.cos(t) * ca - ew * math.sin(t) * sa, ey + el * math.cos(t) * sa + ew * math.sin(t) * ca) for t in np.linspace(0, 2 * math.pi, 24)]
        d.polygon(mat, outline=g, width=max(1, lw - 1))
        rr = rong * .08; d.ellipse([ex - rr, ey - rr, ex + rr, ey + rr], fill=g)

    for vong, (rr, n, dai, rong) in enumerate([(R * .70, 40, R * .30, R * .085), (R * .52, 30, R * .24, R * .085)]):
        for j in range(n):
            a = -math.pi / 2 + (j + .5 * vong) * 2 * math.pi / n
            canh(cx + rr * math.cos(a), cy + rr * math.sin(a), a, dai, rong)
    d.ellipse([cx - R * .50, cy - R * .50, cx + R * .50, cy + R * .50], outline=g, width=lw)
    # dáng tượng ngồi trên đài sen: đường viền mềm (không vẽ chi tiết khuôn mặt)
    def cong(x0, y0, x1, y1, k=.18, n=24):
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2; nx, ny = -(y1 - y0), (x1 - x0)
        return [((1 - t) ** 2 * x0 + 2 * (1 - t) * t * (mx + nx * k) + t * t * x1, (1 - t) ** 2 * y0 + 2 * (1 - t) * t * (my + ny * k) + t * t * y1)
                for t in np.linspace(0, 1, n)]
    hy = cy - R * .26; hr = R * .085
    vai_t, vai_p = (cx - R * .10, cy - R * .14), (cx + R * .10, cy - R * .14)
    than = (cong(cx - R * .035, hy + hr, *vai_t, k=-.25) + cong(*vai_t, cx - R * .30, cy + R * .30, k=.10)
            + cong(cx - R * .30, cy + R * .30, cx + R * .30, cy + R * .30, k=.06)
            + cong(cx + R * .30, cy + R * .30, *vai_p, k=.10) + cong(*vai_p, cx + R * .035, hy + hr, k=-.25))
    d.polygon(than, fill=(16, 30, 58, 255), outline=g)
    d.line(than + [than[0]], fill=g, width=lw)
    d.ellipse([cx - hr, hy - hr * 1.15, cx + hr, hy + hr * 1.15], fill=(16, 30, 58, 255), outline=g, width=lw)
    for k, (dy, rk) in enumerate([(1.55, .55), (2.45, .45), (3.2, .36)]):     # các tầng đầu nhỏ trên đỉnh
        yk = hy - hr * dy; r0 = hr * rk
        d.ellipse([cx - r0, yk - r0, cx + r0, yk + r0], outline=g, width=lw)
    d.line(cong(cx - R * .12, cy + R * .02, cx, cy - R * .10, k=.10) + cong(cx, cy - R * .10, cx + R * .12, cy + R * .02, k=.10), fill=g, width=lw)
    # đài sen
    for j in range(7):
        x = cx + (j - 3) * R * .11
        d.chord([x - R * .08, cy + R * .24, x + R * .08, cy + R * .48], 180, 360, fill=(16, 30, 58, 255), outline=g, width=lw)
    d.line([(cx - R * .42, cy + R * .36), (cx + R * .42, cy + R * .36)], fill=g, width=lw)
    img.paste(lay, (0, 0), lay); d = ImageDraw.Draw(img)
    f1 = F(800, 64 * s); f2 = F(600, 44 * s); f = F(500, 32 * s)
    y = cy + R + 50 * s
    for ln in wrap(d, "Tượng Phật Bà Quan Âm nghìn mắt, nghìn tay", f1, W * .86):
        chu_giua(d, W / 2, y, ln, f1, CREAM); y += f1.size * 1.3
    chu_giua(d, W / 2, y + 8 * s, "Chùa Bút Tháp, tỉnh Bắc Ninh", f2, GOLD); y += f2.size * 1.6 + 8 * s
    for ln in wrap(d, NHAN, f, W * .86):
        chu_giua(d, W / 2, y + 16 * s, ln, f, (214, 200, 176)); y += f.size * 1.35
    return img


# ------------------------------------------------------------------ ASEAN 1967: năm nước kí Tuyên bố thành lập
def asean_1967(W, H, s):
    img = effects._nen_thuong_hieu(W, H).convert("RGB"); d = ImageDraw.Draw(img)
    f0 = F(600, 40 * s); f1 = F(800, 72 * s); f1b = F(500, 40 * s)
    chu_giua(d, W / 2, H * .075, "8 – 8 – 1967 · Băng Cốc (Thái Lan)", f0, GOLD)
    chu_giua(d, W / 2, H * .075 + f0.size * 1.45, "Thành lập ASEAN", f1, CREAM)
    chu_giua(d, W / 2, H * .075 + f0.size * 1.45 + f1.size * 1.3, "Hiệp hội các quốc gia Đông Nam Á", f1b, (232, 222, 205))
    cx, cy = W / 2, H * .52; rx, ry = W * .22, H * .14; lw = max(3, int(4 * s))
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(36, 52, 86), outline=GOLD, width=lw)   # bàn họp nhìn từ trên
    # văn bản ở giữa bàn
    tw, th = W * .062, H * .125
    cy -= 18 * s
    d.rectangle([cx - tw / 2, cy - th / 2, cx + tw / 2, cy + th / 2], fill=CREAM)
    for k in range(7):
        yy = cy - th * .30 + k * th * .09
        d.line([(cx - tw * .36, yy), (cx + tw * (.36 if k < 6 else .05), yy)], fill=(150, 140, 120), width=max(2, int(3 * s)))
    d.line([(cx + tw * .05, cy + th * .40), (cx + tw * .38, cy + th * .40)], fill=(40, 40, 60), width=max(2, int(3 * s)))
    fd = F(600, 28 * s)
    chu_giua(d, cx, cy + th / 2 + 8 * s, "Tuyên bố thành lập ASEAN", fd, CREAM)
    nuoc = ["In-đô-nê-xi-a", "Ma-lai-xi-a", "Phi-líp-pin", "Xin-ga-po", "Thái Lan"]
    fn = F(700, 40 * s)
    for i, ten in enumerate(nuoc):
        a = math.radians(-90 + i * 72)
        px, py = cx + (rx + 60 * s) * math.cos(a), cy + (ry + 58 * s) * math.sin(a)
        r = 44 * s
        d.ellipse([px - r, py - r, px + r, py + r], fill=ORANGE)
        chu_giua(d, px, py - fn.size * .62, str(i + 1), fn, (255, 255, 255))
        tx = px - (r + 18 * s) - d.textlength(ten, font=fn) if math.cos(a) < -.2 else px + r + 18 * s
        ty = py - fn.size * .62
        d.text((tx, ty), ten, font=fn, fill=CREAM)
    nhan_duoi(d, W, H, H * .755, s)
    return img


# ------------------------------------------------------------------ ASEAN 1999: từ 5 nước đến 10 nước
def asean_1999(W, H, s):
    img = effects._nen_thuong_hieu(W, H).convert("RGB"); d = ImageDraw.Draw(img)
    f0 = F(600, 40 * s); f1 = F(800, 66 * s)
    chu_giua(d, W / 2, H * .085, "Tháng 4 – 1999 · Lễ kết nạp ở Hà Nội", f0, GOLD)
    chu_giua(d, W / 2, H * .085 + f0.size * 1.5, "Cam-pu-chia – thành viên thứ 10 của ASEAN", f1, CREAM)
    moc = [("8 – 1967", "5 nước sáng lập", 5), ("1984", "Bru-nây", 6), ("7 – 1995", "Việt Nam", 7),
           ("7 – 1997", "Lào, Mi-an-ma", 9), ("4 – 1999", "Cam-pu-chia", 10)]
    x0, x1, y = W * .10, W * .90, H * .46; lw = max(4, int(6 * s))
    d.line([(x0, y), (x1, y)], fill=GOLD, width=lw)
    fa = F(800, 44 * s); fb = F(600, 38 * s); fc = F(500, 30 * s)
    for i, (nam, ten, tong) in enumerate(moc):
        x = x0 + (x1 - x0) * (i + .5) / len(moc); cuoi = i == len(moc) - 1
        r = (40 if cuoi else 28) * s
        d.ellipse([x - r, y - r, x + r, y + r], fill=ORANGE if cuoi else GOLD)
        chu_giua(d, x, y - r - fa.size * 1.5, nam, fa, CREAM if not cuoi else (255, 214, 170))
        chu_giua(d, x, y + r + 20 * s, ten, fb, CREAM)
        # chấm đếm số thành viên
        n_hang = 5; cr = 9 * s
        for k in range(tong):
            hx = x + (k % n_hang - 2) * cr * 2.8; hy = y + r + 20 * s + fb.size * 1.9 + (k // n_hang) * cr * 2.8
            d.ellipse([hx - cr, hy - cr, hx + cr, hy + cr], fill=ORANGE if (cuoi and k == 9) else (232, 222, 205))
        chu_giua(d, x, y + r + 20 * s + fb.size * 1.9 + 2 * cr * 2.8 + 6 * s, f"{tong} thành viên", fc, (214, 200, 176))
    nhan_duoi(d, W, H, H * .755, s)
    return img


# ------------------------------------------------------------------ Lời thề Vị Xuyên khắc trên bia đá
def vi_xuyen(W, H, s):
    img = effects._nen_thuong_hieu(W, H).convert("RGB")
    # dãy núi đá mờ phía sau
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    rnd = random.Random(5); pts = [(0, H * .74)]
    for k in range(13): pts.append((W * k / 12, H * rnd.uniform(.40, .60)))
    pts += [(W, H * .74)]
    d.polygon(pts, fill=(28, 44, 70, 220))
    img.paste(lay, (0, 0), lay)
    # bia đá
    bw, bh = W * .40, H * .58; x0, y0 = (W - bw) / 2, H * .10
    rng = np.random.default_rng(11)
    da = (rng.normal(0, 1, (int(bh), int(bw))) * 9 + 92).clip(60, 130).astype(np.uint8)
    da = Image.fromarray(np.stack([da, da, (da.astype(np.int16) + 6).clip(0, 255).astype(np.uint8)], -1)).filter(ImageFilter.GaussianBlur(1.2))
    mask = Image.new("L", da.size, 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, da.size[0] - 1, da.size[1] - 1], radius=int(26 * s), fill=255)
    sh = Image.new("L", (W, H), 0); ImageDraw.Draw(sh).bitmap((int(x0) + 16, int(y0) + 20), mask, fill=170)
    img.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(20)))
    img.paste(da, (int(x0), int(y0)), mask)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x0 + 22 * s, y0 + 22 * s, x0 + bw - 22 * s, y0 + bh - 22 * s], radius=int(18 * s), outline=(196, 160, 96), width=max(2, int(3 * s)))
    f = F(800, 76 * s); khac = (226, 186, 110)
    for i, ln in enumerate(["SỐNG BÁM ĐÁ", "CHẾT HOÁ ĐÁ", "THÀNH BẤT TỬ"]):
        yy = y0 + bh * .20 + i * bh * .23
        chu_giua(d, W / 2 + 3 * s, yy + 3 * s, ln, f, (40, 40, 44))   # bóng chữ khắc
        chu_giua(d, W / 2, yy, ln, f, khac)
    f2 = F(600, 36 * s)
    chu_giua(d, W / 2, y0 + bh + 26 * s, "Lời thề của người lính Vị Xuyên – Điểm cao 468, tỉnh Tuyên Quang", f2, CREAM)
    nhan_duoi(d, W, H, y0 + bh + 26 * s + f2.size * 1.6, s)
    return img


KIEU = {"le_paria": le_paria, "quan_am": quan_am, "asean_1967": asean_1967, "asean_1999": asean_1999, "vi_xuyen": vi_xuyen}


def main():
    ma, so, kieu = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    sp = json.load(open(os.path.join(ROOT, "data/scripts", ma + ".json")))
    doc = sp.get("huong") == "doc"
    W, H = (1440, 2560) if doc else (2560, 1440)
    s = W / 1080 if doc else H / 1080
    img = KIEU[kieu](W, H, s)
    dd = os.path.join(ROOT, "assets/episodes", ma); os.makedirs(dd, exist_ok=True)
    out = os.path.join(dd, f"canh-{so:02d}.jpg"); img.save(out, quality=93)
    mp = os.path.join(dd, "nguon_tu_lieu.json")
    meta = json.load(open(mp)) if os.path.exists(mp) else {}
    meta[str(so)] = {"loai": "minh_hoa_code", "kieu": kieu, "nguon": NHAN,
                     "ghi_chu": "Thay thẻ chỉ dẫn SGK theo yêu cầu GVHD 18/11/2026: không tìm được ảnh có giấy phép mở"}
    json.dump(meta, open(mp, "w"), ensure_ascii=False, indent=1)
    prev = os.path.join(ROOT, "tmp/qa", f"{ma}_canh-{so:02d}_xem.jpg"); os.makedirs(os.path.dirname(prev), exist_ok=True)
    img.resize((img.width * 3 // 8, img.height * 3 // 8)).save(prev, quality=85)
    print(out, prev)


if __name__ == "__main__":
    main()
