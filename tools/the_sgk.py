#!/usr/bin/env python3
"""Thẻ "Xem ảnh tư liệu trong SGK" cho cảnh tư liệu chưa tìm được ảnh mở (phạm vi công cộng / giấy phép mở).

Không chép lại hình trong sách giáo khoa: thẻ chỉ ghi ảnh đó là gì và chỉ học sinh mở đúng hình, đúng trang.
Dựng bằng code trên nền thương hiệu (xanh đêm + hoa văn trống đồng), quyển sách mở vẽ bằng nét, chừa dải phụ đề.
Ghi vào assets/episodes/<MA>/nguon_tu_lieu.json: {"loai": "the_sgk"} để không nhận nhầm là ảnh có nguồn.

Dùng: python3 tools/the_sgk.py <MA> <so_canh> [--mo-ta "..."]   (mặc định lấy tu_lieu.mo_ta trong kịch bản)
"""
import argparse, json, os, re, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
import effects

GOLD, CREAM, ORANGE = (201, 139, 43), (250, 244, 230), (242, 107, 29)
F = lambda w, z: ImageFont.truetype(os.path.join(ROOT, f"assets/fonts/be-vietnam-pro-{w}-normal.ttf"), int(z))


def tach(mo_ta):
    """→ (nội dung ảnh, chỉ dẫn hình/trang SGK hoặc None)."""
    m = re.search(r"\((?:như\s+)?(Hình\s+[\d.]+)\s*(?:SGK)?[,\s]*(?:tr\.?\s*(\d+))?\s*\)?", mo_ta)
    noi_dung = re.sub(r"\s*\((?:như\s+)?Hình[^)]*\)?\s*$", "", mo_ta).strip()
    noi_dung = re.sub(r"^(Ảnh tư liệu|Ảnh chụp hiện nay|Ảnh)[^:]*:\s*", "", noi_dung).strip()
    noi_dung = noi_dung[:1].upper() + noi_dung[1:]
    noi_dung = re.sub(r"\b(năm|ngày|tháng|thế kỉ) (?=[\dXVI])", "\\1\u00a0", noi_dung)
    if not m: return noi_dung, None
    return noi_dung, (m.group(1), m.group(2))


def wrap(d, s, f, w):
    out, line = [], ""
    for t in s.split(" "):
        if line and d.textlength(line + " " + t, font=f) > w: out.append(line); line = t
        else: line = (line + " " + t).strip()
    if line: out.append(line)
    return out


def ve_sach(d, cx, cy, w, h, lw):
    """Quyển sách mở bằng nét vàng đồng."""
    gx = cx
    for side in (-1, 1):
        x_out = cx + side * w / 2
        pts = [(gx, cy - h * .40), (x_out, cy - h * .50), (x_out, cy + h * .42), (gx, cy + h * .50)]
        d.line(pts + [pts[0]], fill=GOLD, width=lw, joint="curve")
        for k in range(4):   # dòng chữ trên trang
            yy = cy - h * .22 + k * h * .17
            x1, x2 = gx + side * w * .10, gx + side * w * (.40 if k < 3 else .28)
            d.line([(x1, yy + (abs(x1 - gx) / (w / 2)) * -h * .06), (x2, yy + (abs(x2 - gx) / (w / 2)) * -h * .06)],
                   fill=(*GOLD, ), width=max(2, lw // 2))
    d.line([(gx, cy - h * .40), (gx, cy + h * .50)], fill=GOLD, width=lw)


def ve_khung_anh(d, cx, cy, w, h, lw):
    """Khung ảnh (núi, mặt trời) bằng nét vàng đồng – dùng khi không có hình trong SGK để chỉ dẫn."""
    x0, y0, x1, y1 = cx - w * .42, cy - h * .46, cx + w * .42, cy + h * .46
    d.rounded_rectangle([x0, y0, x1, y1], radius=int(lw * 3), outline=GOLD, width=lw)
    d.line([(x0 + lw, y1 - h * .18), (cx - w * .12, cy - h * .05), (cx + w * .05, cy + h * .14), (cx + w * .18, cy + h * .02),
            (x1 - lw, y1 - h * .20)], fill=GOLD, width=lw, joint="curve")
    r = h * .11; d.ellipse([cx + w * .16 - r, cy - h * .24 - r, cx + w * .16 + r, cy - h * .24 + r], outline=GOLD, width=lw)


def dung(ma, so, mo_ta, out, noi_dung=None, chi_dan=None, nhan=None):
    sp = json.load(open(os.path.join(ROOT, "data/scripts", ma + ".json")))
    doc = sp.get("huong") == "doc"
    W, H = (1440, 2560) if doc else (2560, 1440)
    s = W / 1080 if doc else H / 1080
    lop = re.match(r"L(\d)", ma).group(1)
    nd0, cd0 = tach(mo_ta)
    noi_dung = noi_dung or nd0
    noi_dung = re.sub(r"\b(năm|ngày|tháng|thế kỉ) (?=[\dXVI])", "\\1\u00a0", noi_dung)
    chi_dan = cd0 if chi_dan is None else (chi_dan or None)
    t = noi_dung.split(" ")   # giữ cụm tên riêng (Niu Oóc, Đồng Lộc) và không để một chữ lẻ ở dòng cuối
    hoa = lambda w: w[:1].isupper()
    ghep = t[0]
    for i in range(1, len(t)):
        noi = (hoa(t[i - 1]) and hoa(t[i]) and not t[i - 1].endswith((",", ")"))) or i == len(t) - 1
        ghep += ("\u00a0" if noi else " ") + t[i]
    noi_dung = ghep
    img = effects._nen_thuong_hieu(W, H).convert("RGB"); d = ImageDraw.Draw(img)
    # vùng nội dung: chừa dải phụ đề dưới và góc logo trên phải; khối nội dung canh giữa theo chiều dọc
    top, bot = (H * .12, H * .68) if doc else (H * .10, H * .76)
    bw, bh = (W * .40, W * .26) if doc else (H * .30, H * .19)
    f_nhan = F(600, (44 if doc else 34) * s); f_nd = F(700, (72 if doc else 52) * s); f_cd = F(600, (46 if doc else 36) * s)
    wmax = W * (.86 if doc else .70)
    lines = wrap(d, noi_dung, f_nd, wmax)
    while len(lines) > (5 if doc else 3) and f_nd.size > 30 * s:
        f_nd = F(700, f_nd.size - 4); lines = wrap(d, noi_dung, f_nd, wmax)
    nhan = nhan or ("Ảnh tư liệu trong sách giáo khoa" if chi_dan else "Tư liệu lịch sử")
    cd = None
    if chi_dan:
        hinh, trang = chi_dan
        bai = re.match(r"L\d-(B|CD)(\d+)", ma)
        bai = (f"Bài {bai.group(2)}" if bai.group(1) == "B" else f"Chủ đề {bai.group(2)}") if bai else ""
        if "." in hinh: bai = ""   # Hình 13.5: số bài đã nằm trong số hình
        cd = f"Mở SGK Lịch sử và Địa lí {lop}, " + (f"{bai}, " if bai else "") + f"xem {hinh}" + (f" (trang {trang})" if trang else "")
        while d.textlength(cd, font=f_cd) > W * .86 and f_cd.size > 24 * s: f_cd = F(600, f_cd.size - 2)
    gap = 34 * s; pad = 26 * s
    h_cd = (f_cd.size * 1.25 + pad + gap * 1.4) if cd else 0
    tong = bh * 1.08 + gap * 1.2 + f_nhan.size * 1.5 + gap * .5 + len(lines) * f_nd.size * 1.3 + h_cd
    y0 = top + max(0, (bot - top - tong) / 2)
    cx = W / 2
    (ve_sach if chi_dan else ve_khung_anh)(d, cx, y0 + bh * .52, bw, bh, max(4, int(5 * s)))
    y = y0 + bh * 1.08 + gap * 1.2
    d.text((cx - d.textlength(nhan, font=f_nhan) / 2, y), nhan, font=f_nhan, fill=GOLD); y += f_nhan.size * 1.5 + gap * .5
    for ln in lines:
        d.text((cx - d.textlength(ln, font=f_nd) / 2, y), ln, font=f_nd, fill=CREAM); y += f_nd.size * 1.3
    if cd:
        y += gap * 1.4
        tw = d.textlength(cd, font=f_cd)
        d.rounded_rectangle([cx - tw / 2 - pad, y - pad * .55, cx + tw / 2 + pad, y + f_cd.size * 1.25 + pad * .45],
                            radius=int(18 * s), fill=ORANGE)
        d.text((cx - tw / 2, y), cd, font=f_cd, fill=(255, 255, 255))
    img.save(out, quality=93)
    return chi_dan


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("ma"); ap.add_argument("so", type=int); ap.add_argument("--mo-ta")
    ap.add_argument("--noi-dung"); ap.add_argument("--hinh", help='vd "Hình 5.3" ; "" = không chỉ dẫn SGK'); ap.add_argument("--trang")
    ap.add_argument("--nhan")
    a = ap.parse_args()
    sp = json.load(open(os.path.join(ROOT, "data/scripts", a.ma + ".json")))
    sc = next(c for c in sp["canh"] if int(c["so"]) == a.so)
    mo_ta = a.mo_ta or (sc.get("tu_lieu") or {}).get("mo_ta") or sc.get("hinh", "")
    dd = os.path.join(ROOT, "assets/episodes", a.ma); os.makedirs(dd, exist_ok=True)
    out = os.path.join(dd, f"canh-{a.so:02d}.jpg")
    cd_tay = None if a.hinh is None else ((a.hinh, a.trang) if a.hinh else "")
    cd = dung(a.ma, a.so, mo_ta, out, noi_dung=a.noi_dung, chi_dan=cd_tay, nhan=a.nhan)
    mp = os.path.join(dd, "nguon_tu_lieu.json")
    meta = json.load(open(mp)) if os.path.exists(mp) else {}
    meta[str(a.so)] = {"loai": "the_sgk" if cd else "the_chu", "mo_ta": mo_ta,
                       "ghi_chu": "Thẻ chỉ dẫn xem hình trong SGK, không chép hình SGK" if cd else "Thẻ chữ thay ảnh tư liệu (chưa tìm được ảnh có giấy phép mở)"}
    json.dump(meta, open(mp, "w"), ensure_ascii=False, indent=1)
    prev = os.path.join(ROOT, "tmp/qa", f"{a.ma}_canh-{a.so:02d}_xem.jpg")
    im = Image.open(out); im.resize((im.width * 3 // 8, im.height * 3 // 8)).save(prev, quality=85)
    print(out, cd)


if __name__ == "__main__":
    main()
