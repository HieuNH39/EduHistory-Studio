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

def cau_hoi(W, H, n, q, fps, q_end=3.0, reveal=6.5):
    """Câu hỏi dừng hình: hiện câu hỏi + 3 lựa chọn A/B/C, đếm ngược 3-2-1 sau khi đọc xong câu hỏi, rồi lật đáp án đúng."""
    s = H / 1080
    f_q = ImageFont.truetype(os.path.join(FONT_DIR, "be-vietnam-pro-800-normal.ttf"), int(52 * s))
    f_o = ImageFont.truetype(os.path.join(FONT_DIR, "be-vietnam-pro-600-normal.ttf"), int(42 * s))
    f_c = ImageFont.truetype(os.path.join(FONT_DIR, "be-vietnam-pro-900-normal.ttf"), int(120 * s))
    f_t = ImageFont.truetype(os.path.join(FONT_DIR, "be-vietnam-pro-700-normal.ttf"), int(34 * s))
    def wrap(d, text, font, maxw):
        out, cur = [], ""
        for w in text.split():
            if d.textlength((cur + " " + w).strip(), font=font) > maxw: out.append(cur); cur = w
            else: cur = (cur + " " + w).strip()
        return out + [cur]
    for i in range(n):
        t = i / fps
        img = Image.new("RGB", (W, H), (16, 35, 63)); d = ImageDraw.Draw(img)
        top = .15 if W > H else .12
        d.rounded_rectangle([W * .06, H * top, W * .94, H * (top + .69)], radius=int(30 * s), fill=(250, 244, 230))
        d.text((W * .1, H * (top + .04)), "DỪNG HÌNH – THỬ TÀI", font=f_t, fill=(242, 107, 29))
        y = H * (top + .11)
        for line in wrap(d, q["hoi"], f_q, W * .62):
            d.text((W * .1, y), line, font=f_q, fill=(22, 33, 52)); y += 66 * s
        y += 18 * s
        for k, opt in enumerate(q["lua_chon"]):
            ok = k == q["dung"] and t >= reveal
            dim = t >= reveal and not ok
            box = [W * .1, y, W * .66, y + 78 * s]
            d.rounded_rectangle(box, radius=int(16 * s), fill=(46, 160, 87) if ok else ((225, 220, 210) if dim else (255, 255, 255)), outline=(200, 190, 170), width=3)
            d.text((W * .12, y + 14 * s), f"{'ABC'[k]}.  {opt}", font=f_o, fill=(255, 255, 255) if ok else ((150, 145, 140) if dim else (22, 33, 52)))
            y += 96 * s
        if q_end <= t < reveal:   # đồng hồ đếm ngược
            left = max(1, int(math.ceil(reveal - t))) if reveal - t <= 3.2 else 3
            cx, cy, r = W * .8, H * (top + .36), 120 * s
            frac = (reveal - t) / max(0.1, reveal - q_end)
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(16, 35, 63))
            d.arc([cx - r, cy - r, cx + r, cy + r], start=-90, end=-90 + 360 * frac, fill=(242, 107, 29), width=int(16 * s))
            txt = str(left); tw = d.textlength(txt, font=f_c)
            d.text((cx - tw / 2, cy - 80 * s), txt, font=f_c, fill=(255, 255, 255))
        if t >= reveal:
            d.text((W * .7, H * (top + .32)), "Đáp án đúng!", font=f_q, fill=(46, 160, 87))
        yield np.asarray(img)

def _wrap(d, text, font, maxw):
    out, cur = [], ""
    for w in text.split():
        if cur and d.textlength(cur + " " + w, font=font) > maxw: out.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    return out + ([cur] if cur else [])

def truc_thoi_gian(W, H, n, items, fps, times=None, title="TRỤC THỜI GIAN"):
    """Sơ đồ trục thời gian (hoạt động SGK 'trình bày diễn biến trên trục thời gian').
    items = [[mốc, nội dung], ...]; times = thời điểm (giây) hiện từng mốc, khớp lời đọc."""
    s = H / 1080; vertical = H > W
    f_t = ImageFont.truetype(os.path.join(FONT_DIR, "be-vietnam-pro-800-normal.ttf"), int(44 * s))
    f_d = ImageFont.truetype(os.path.join(FONT_DIR, "be-vietnam-pro-800-normal.ttf"), int((50 if not vertical else 34) * s))
    f_l = ImageFont.truetype(os.path.join(FONT_DIR, "be-vietnam-pro-500-normal.ttf"), int((36 if not vertical else 27) * s))
    m = len(items); dur_s = n / fps
    if not times or len(times) != m: times = [0.4 + k * (dur_s - 1.5) / max(m, 1) for k in range(m)]
    for i in range(n):
        t = i / fps
        img = Image.new("RGB", (W, H), (16, 35, 63)); d = ImageDraw.Draw(img)
        d.text((W * .06, H * .07), title, font=f_t, fill=(242, 107, 29))
        if not vertical:
            x0, x1, y = W * .05, W * .95, H * .42
            prog = _ease(t / max(times[-1] + .6, .1))
            d.line([x0, y, x0 + (x1 - x0) * prog, y], fill=(201, 139, 43), width=int(8 * s))
            step = (x1 - x0) / m
            for k, (moc, nd) in enumerate(items):
                a = _ease((t - times[k]) / .45)
                if a <= 0: continue
                cx = x0 + step * (k + .5); r = 18 * s * (0.6 + .4 * a)
                d.ellipse([cx - r, y - r, cx + r, y + r], fill=(242, 107, 29), outline=(255, 236, 200), width=int(4 * s))
                col = tuple(int(c * a + 16 * (1 - a)) for c in (255, 214, 140))
                lines = _wrap(d, moc, f_d, step * .94); yy = y - 44 * s - len(lines) * 60 * s
                for ln in lines:
                    d.text((cx - d.textlength(ln, font=f_d) / 2, yy), ln, font=f_d, fill=col); yy += 60 * s
                yy = y + 40 * s; colb = tuple(int(c * a + 30 * (1 - a)) for c in (235, 238, 245))
                for ln in _wrap(d, nd, f_l, step * .92):
                    d.text((cx - d.textlength(ln, font=f_l) / 2, yy), ln, font=f_l, fill=colb); yy += 48 * s
        else:
            x, y0, y1 = W * .16, H * .14, H * .74
            prog = _ease(t / max(times[-1] + .6, .1))
            d.line([x, y0, x, y0 + (y1 - y0) * prog], fill=(201, 139, 43), width=int(8 * s))
            step = (y1 - y0) / m
            for k, (moc, nd) in enumerate(items):
                a = _ease((t - times[k]) / .45)
                if a <= 0: continue
                cy = y0 + step * (k + .3); r = 16 * s
                d.ellipse([x - r, cy - r, x + r, cy + r], fill=(242, 107, 29), outline=(255, 236, 200), width=int(4 * s))
                d.text((x + 40 * s, cy - 24 * s), moc, font=f_d, fill=(255, 214, 140))
                yy = cy + 22 * s
                for ln in _wrap(d, nd, f_l, W * .7):
                    d.text((x + 40 * s, yy), ln, font=f_l, fill=(235, 238, 245)); yy += 36 * s
        yield np.asarray(img)

def ghi_nho(W, H, n, bullets, fps, times=None, title="GHI NHỚ"):
    """Thẻ ghi nhớ kiến thức chốt, từng ý hiện theo lời đọc."""
    s = H / 1080; vertical = H > W
    f_t = ImageFont.truetype(os.path.join(FONT_DIR, "be-vietnam-pro-800-normal.ttf"), int(46 * s))
    f_b = ImageFont.truetype(os.path.join(FONT_DIR, "be-vietnam-pro-600-normal.ttf"), int((46 if not vertical else 36) * s))
    m = len(bullets); dur_s = n / fps
    if not times or len(times) != m: times = [0.5 + k * (dur_s - 1.5) / max(m, 1) for k in range(m)]
    LH = (62 if not vertical else 50) * s
    dd = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    need = 120 * s + sum(LH * len(_wrap(dd, b, f_b, W * .86 - 170 * s)) + 30 * s for b in bullets) + 40 * s
    top = H * (.16 if not vertical else .12); box = [W * .07, top, W * .93, min(H * (.80 if not vertical else .72), top + need)]
    for i in range(n):
        t = i / fps
        img = Image.new("RGB", (W, H), (16, 35, 63)); d = ImageDraw.Draw(img)
        d.rounded_rectangle(box, radius=int(30 * s), fill=(250, 244, 230))
        d.text((box[0] + 50 * s, box[1] + 36 * s), title, font=f_t, fill=(242, 107, 29))
        y = box[1] + 120 * s
        for k, b in enumerate(bullets):
            a = _ease((t - times[k]) / .4)
            lines = _wrap(d, b, f_b, (box[2] - box[0]) - 170 * s)
            if a > 0:
                cx, cy, r = box[0] + 70 * s, y + LH * .45, 24 * s
                d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(46, 160, 87))
                d.line([cx - 10 * s, cy, cx - 2 * s, cy + 9 * s, cx + 12 * s, cy - 9 * s], fill=(255, 255, 255), width=int(5 * s))
                col = tuple(int(c * a + 250 * (1 - a)) for c in (22, 33, 52))
                yy = y
                for ln in lines:
                    d.text((box[0] + 115 * s + 30 * s * (1 - a), yy), ln, font=f_b, fill=col); yy += LH
            y += LH * len(lines) + 30 * s
        yield np.asarray(img)

def _ctx(W, H):
    import cairo
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); cr = cairo.Context(surf)
    return surf, cr

def _arr(surf, W, H):
    buf = np.ndarray((H, W, 4), np.uint8, surf.get_data(), 0, (surf.get_stride(), 4, 1))
    return buf[..., [2, 1, 0]].copy()

def _txt(cr, s, x, y, size, color, bold=True, align="c", alpha=1.0):
    import cairo
    cr.select_font_face("Be Vietnam Pro", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    cr.set_font_size(size); e = cr.text_extents(s)
    dx = {"c": -e.width / 2 - e.x_bearing, "l": 0, "r": -e.width}[align]
    cr.move_to(x + dx, y - e.height / 2 - e.y_bearing); cr.set_source_rgba(*color, alpha); cr.show_text(s)

def may_hoi_nuoc(W, H, n, fps, labels=True):
    """Mô phỏng nguyên lí máy hơi nước (minh hoạ đơn giản): lửa đun nồi hơi → hơi nước đẩy pít-tông qua lại
    trong xi-lanh → tay biên làm quay bánh đà → dây cu-roa kéo máy móc. Nhãn hiện dần theo thời gian."""
    s = H / 1080; cx0 = W * .5
    for i in range(n):
        t = i / fps; u = i / max(n - 1, 1)
        surf, cr = _ctx(W, H)
        cr.set_source_rgb(.95, .92, .86); cr.paint()
        _txt(cr, "NGUYÊN LÍ MÁY HƠI NƯỚC (minh hoạ)", W * .06, H * .08, 40 * s, (.95, .42, .11), align="l")
        ang = t * 2.4  # góc quay bánh đà
        # nồi hơi
        bx, by, bw, bh = W * .10, H * .42, W * .20, H * .26
        cr.set_source_rgb(.45, .32, .25); cr.rectangle(bx, by, bw, bh); cr.fill()
        cr.set_source_rgb(.30, .22, .18); cr.rectangle(bx - 10 * s, by - 18 * s, bw + 20 * s, 22 * s); cr.fill()
        for k in range(6):  # lửa
            fx = bx + bw * (k + .5) / 6; fh = (40 + 18 * math.sin(t * 9 + k)) * s
            cr.set_source_rgba(1, .55 + .2 * math.sin(t * 7 + k), .1, .9); cr.move_to(fx - 16 * s, by + bh + 40 * s); cr.line_to(fx, by + bh + 40 * s - fh); cr.line_to(fx + 16 * s, by + bh + 40 * s); cr.close_path(); cr.fill()
        # ống dẫn hơi
        py = H * .40; cyx0, cyx1 = W * .38, W * .60
        cr.set_source_rgb(.55, .55, .58); cr.set_line_width(16 * s); cr.move_to(bx + bw * .7, by - 18 * s); cr.line_to(bx + bw * .7, py - 70 * s); cr.line_to(cyx0 + 20 * s, py - 70 * s); cr.line_to(cyx0 + 20 * s, py - 40 * s); cr.stroke()
        # xi-lanh
        cr.set_source_rgb(.35, .38, .42); cr.rectangle(cyx0, py - 40 * s, cyx1 - cyx0, 80 * s); cr.fill()
        cr.set_source_rgb(.85, .87, .9); cr.rectangle(cyx0 + 8 * s, py - 32 * s, cyx1 - cyx0 - 16 * s, 64 * s); cr.fill()
        # bánh đà + tay biên
        fwx, fwy, R, r = W * .80, py + 20 * s, 150 * s, 70 * s
        crank = (fwx + r * math.cos(ang), fwy + r * math.sin(ang))
        L = 300 * s
        pxp = crank[0] - math.sqrt(max(L * L - (crank[1] - py) ** 2, 1))
        pist = min(max(pxp - 120 * s, cyx0 + 30 * s), cyx1 - 60 * s)
        # hơi nước trong xi-lanh (phía trái pít-tông)
        cr.set_source_rgba(.75, .85, 1, .8); cr.rectangle(cyx0 + 8 * s, py - 32 * s, pist - cyx0 - 8 * s, 64 * s); cr.fill()
        cr.set_source_rgb(.25, .25, .28); cr.rectangle(pist, py - 32 * s, 30 * s, 64 * s); cr.fill()
        cr.set_line_width(12 * s); cr.move_to(pist + 30 * s, py); cr.line_to(pxp, py); cr.stroke()
        cr.set_line_width(10 * s); cr.set_source_rgb(.45, .3, .2); cr.move_to(pxp, py); cr.line_to(*crank); cr.stroke()
        cr.set_source_rgb(.2, .2, .22); cr.set_line_width(18 * s); cr.arc(fwx, fwy, R, 0, 6.2832); cr.stroke()
        for k in range(6):
            a = ang + k * math.pi / 3; cr.set_line_width(8 * s); cr.move_to(fwx, fwy); cr.line_to(fwx + R * math.cos(a), fwy + R * math.sin(a)); cr.stroke()
        cr.arc(*crank, 9 * s, 0, 6.2832); cr.fill()
        # dây cu-roa xuống máy dệt
        mx, my = W * .80, H * .78
        cr.set_source_rgb(.4, .3, .2); cr.set_line_width(5 * s); cr.move_to(fwx - 30 * s, fwy); cr.line_to(mx - 30 * s, my); cr.move_to(fwx + 30 * s, fwy); cr.line_to(mx + 30 * s, my); cr.stroke()
        cr.set_source_rgb(.55, .45, .3); cr.rectangle(mx - 120 * s, my, 240 * s, 60 * s); cr.fill()
        for k in range(5):
            sx = mx - 90 * s + k * 45 * s; cr.set_source_rgb(.95, .95, .9); cr.arc(sx, my - 10 * s, 12 * s, 0, 6.2832); cr.fill()
            cr.set_source_rgb(.3, .3, .3); cr.set_line_width(2); cr.move_to(sx, my - 10 * s); cr.line_to(sx + 10 * s * math.cos(ang * 3 + k), my - 10 * s + 10 * s * math.sin(ang * 3 + k)); cr.stroke()
        # khói/hơi thoát
        for k in range(4):
            ph = (t * .6 + k / 4) % 1; cr.set_source_rgba(1, 1, 1, .5 * (1 - ph)); cr.arc(cyx1 - 30 * s, py - 50 * s - ph * 160 * s, (14 + 30 * ph) * s, 0, 6.2832); cr.fill()
        if labels:
            items = [(.08, "Lửa đun nóng nồi hơi", bx + bw / 2, by + bh + 80 * s), (.25, "Hơi nước", cyx0 - 60 * s, py - 95 * s), (.42, "Pít-tông chuyển động qua lại", (cyx0 + cyx1) / 2, py + 75 * s),
                     (.58, "Bánh đà quay", fwx, fwy - R - 40 * s), (.74, "Máy móc chạy theo", mx, my + 95 * s)]
            for t0, lab, lx, ly in items:
                a = _ease((u - t0) / .06)
                if a > 0: _txt(cr, lab, lx, ly, 30 * s, (.12, .16, .24), alpha=a)
        yield _arr(surf, W, H)

def nha_may(W, H, n, fps):
    """Trước: xưởng dệt phải bám bờ sông chảy xiết (bánh xe nước). Sau: nhà máy dùng máy hơi nước mọc lên ở nhiều nơi thuận lợi."""
    s = H / 1080
    def factory(cr, x, y, k, chimney=True, t=0):
        cr.set_source_rgba(.55, .25, .18, k); cr.rectangle(x - 70 * s, y - 70 * s, 140 * s, 70 * s); cr.fill()
        cr.move_to(x - 70 * s, y - 70 * s)
        for j in range(4): cr.line_to(x - 70 * s + j * 35 * s + 17 * s, y - 95 * s); cr.line_to(x - 70 * s + (j + 1) * 35 * s, y - 70 * s)
        cr.close_path(); cr.fill()
        if chimney:
            cr.rectangle(x + 40 * s, y - 150 * s, 18 * s, 80 * s); cr.fill()
            for q in range(3):
                ph = (t * .5 + q / 3) % 1; cr.set_source_rgba(.4, .4, .42, .45 * k * (1 - ph)); cr.arc(x + 49 * s + ph * 40 * s, y - 160 * s - ph * 90 * s, (10 + 22 * ph) * s, 0, 6.2832); cr.fill()
    for i in range(n):
        t = i / fps; u = i / max(n - 1, 1)
        surf, cr = _ctx(W, H)
        cr.set_source_rgb(.88, .93, .84); cr.paint()
        _txt(cr, "NHÀ MÁY KHÔNG CÒN PHẢI BÁM BỜ SÔNG (minh hoạ)", W * .30, H * .08, 38 * s, (.95, .42, .11), align="l")
        # sông bên trái
        cr.set_source_rgb(.55, .75, .9); cr.move_to(W * .08, 0); cr.curve_to(W * .2, H * .3, W * .05, H * .6, W * .16, H)
        cr.line_to(W * .26, H); cr.curve_to(W * .15, H * .6, W * .3, H * .3, W * .18, 0); cr.close_path(); cr.fill()
        # xưởng ven sông + bánh xe nước
        factory(cr, W * .30, H * .52, 1, chimney=False)
        wx, wy = W * .215, H * .48
        cr.set_source_rgb(.4, .28, .18); cr.set_line_width(6 * s); cr.arc(wx, wy, 50 * s, 0, 6.2832); cr.stroke()
        for k in range(8):
            a = t * 2 + k * math.pi / 4; cr.move_to(wx, wy); cr.line_to(wx + 50 * s * math.cos(a), wy + 50 * s * math.sin(a)); cr.stroke()
        _txt(cr, "1771: xưởng dệt bên sông chảy xiết", W * .36, H * .60, 26 * s, (.12, .16, .24))
        k2 = _ease((u - .35) / .25)
        if k2 > 0:
            for j, (x, y) in enumerate([(.55, .40), (.72, .55), (.86, .38), (.62, .72), (.84, .74)]):
                kk = _ease((u - .35 - j * .06) / .15)
                if kk > 0: factory(cr, W * x, H * y, kk, True, t)
            _txt(cr, "Sau 1784: nhà máy dùng máy hơi nước, xây ở bất cứ nơi nào thuận lợi", W * .66, H * .88, 28 * s, (.12, .16, .24), alpha=k2)
        yield _arr(surf, W, H)

def truc_cong_lich(W, H, n, fps, che_do="co_ban"):
    """Trục Công lịch (theo Hình 3 SGK LSĐL 6, tr. 15). che_do: co_ban | don_vi | khoang_cach."""
    s = H / 1080; y = H * .42; x0, x1 = W * .06, W * .94; xm = W * .5
    def X(year):  # năm âm = TCN; trục co giãn: 3000 TCN .. 3000 CN
        return xm + (x1 - xm) * (year / 3000.0)
    for i in range(n):
        t = i / fps; u = i / max(n - 1, 1)
        surf, cr = _ctx(W, H)
        cr.set_source_rgb(.10, .17, .30); cr.paint()
        _txt(cr, {"co_ban": "TRỤC CÔNG LỊCH", "don_vi": "THẬP KỈ – THẾ KỈ – THIÊN NIÊN KỈ", "khoang_cach": "TÍNH KHOẢNG CÁCH THỜI GIAN"}[che_do], W * .06, H * .08, 40 * s, (.95, .42, .11), align="l")
        k = _ease(u / .15)
        cr.set_source_rgba(.79, .55, .17, 1); cr.set_line_width(8 * s)
        cr.move_to(xm - (xm - x0) * k, y); cr.line_to(xm + (x1 - xm) * k, y); cr.stroke()
        cr.move_to(x1 * 1 + 0 * s, y); cr.line_to(x1 - 24 * s, y - 14 * s); cr.line_to(x1 - 24 * s, y + 14 * s); cr.close_path(); cr.fill()
        for yr in (-2000, -1000, 1000, 2000):
            xx = X(yr); cr.set_line_width(4 * s); cr.move_to(xx, y - 14 * s); cr.line_to(xx, y + 14 * s); cr.stroke()
            _txt(cr, f"{abs(yr)}", xx, y + 48 * s, 30 * s, (.92, .94, .98), bold=False, alpha=k)
        _txt(cr, "Trước Công nguyên (TCN)", (x0 + xm) / 2, y - 60 * s, 34 * s, (.75, .85, 1), alpha=k)
        _txt(cr, "Công nguyên", (xm + x1) / 2, y - 60 * s, 34 * s, (1, .85, .6), alpha=k)
        # mốc năm 1
        a1 = _ease((u - .15) / .1) if che_do == "co_ban" else 1
        if a1 > 0:
            cr.set_source_rgba(.95, .42, .11, a1); cr.arc(xm + 6 * s, y, 12 * s, 0, 6.2832); cr.fill()
            cr.set_source_rgba(.75, .85, 1, a1); cr.arc(xm - 6 * s, y, 9 * s, 0, 6.2832); cr.fill()
            _txt(cr, "Năm 1", xm + 60 * s, y + 48 * s, 30 * s, (1, .85, .6), alpha=a1)
            _txt(cr, "Năm 1 TCN", xm - 90 * s, y + 48 * s, 30 * s, (.75, .85, 1), alpha=a1)
        if che_do == "co_ban":
            a2 = _ease((u - .3) / .1)
            if a2 > 0: _txt(cr, "Năm ra đời của Chúa Giê-su (tương truyền) – năm đầu tiên của Công nguyên", xm, y - 150 * s, 30 * s, (1, 1, 1), bold=False, alpha=a2)
            a3 = _ease((u - .6) / .1)
            if a3 > 0:
                cr.set_source_rgba(.95, .3, .3, a3); cr.set_line_width(5 * s); cr.move_to(xm - 40 * s, y + 90 * s); cr.line_to(xm + 40 * s, y + 150 * s); cr.move_to(xm + 40 * s, y + 90 * s); cr.line_to(xm - 40 * s, y + 150 * s); cr.stroke()
                _txt(cr, "Không có năm 0", xm, y + 190 * s, 34 * s, (.95, .4, .4), alpha=a3)
        elif che_do == "don_vi":
            rows = [(.12, "Thập kỉ = 10 năm", "2021 – 2030"), (.38, "Thế kỉ = 100 năm", "Thế kỉ XXI: 2001 – 2100"), (.64, "Thiên niên kỉ = 1 000 năm", "Thiên niên kỉ III: 2001 – 3000")]
            X2 = lambda yr: W * .34 + (yr - 2000) / 1000.0 * W * .58
            az = _ease((u - .05) / .08)
            if az > 0:
                _txt(cr, "Phóng to đoạn từ năm 2000 đến năm 3000", W * .34, y + 95 * s, 26 * s, (.75, .85, 1), bold=False, align="l", alpha=az)
                cr.set_source_rgba(.79, .55, .17, az); cr.set_line_width(4 * s); cr.move_to(X2(2000), y + 125 * s); cr.line_to(X2(3000), y + 125 * s); cr.stroke()
                for yr in (2000, 2100, 2500, 3000):
                    cr.move_to(X2(yr), y + 115 * s); cr.line_to(X2(yr), y + 135 * s); cr.stroke()
                    _txt(cr, str(yr), X2(yr), y + 152 * s, 22 * s, (.92, .94, .98), bold=False, alpha=az)
            for j, (t0, a, b) in enumerate(rows):
                aa = _ease((u - t0) / .1)
                if aa <= 0: continue
                ya = y + (200 + j * 80) * s
                x_a = X2(2001); x_b = X2({0: 2030, 1: 2100, 2: 3000}[j]); x_b = max(x_b, x_a + 10 * s)
                cr.set_source_rgba(.95, .42, .11, aa); cr.rectangle(x_a, ya - 14 * s, (x_b - x_a) * aa, 28 * s); cr.fill()
                _txt(cr, a, W * .06, ya, 32 * s, (1, 1, 1), align="l", alpha=aa)
                if j < 2: _txt(cr, b, x_b + 20 * s, ya, 28 * s, (1, .85, .6), bold=False, align="l", alpha=aa)
                else: _txt(cr, b, (x_a + x_b) / 2, ya, 28 * s, (1, 1, 1), alpha=aa)
            aa = _ease((u - .85) / .08)
            if aa > 0: _txt(cr, "Tính từ năm đầu tiên của mỗi khoảng thời gian", xm, y - 150 * s, 30 * s, (1, 1, 1), bold=False, alpha=aa)
        else:
            a, b = -208, 2026
            ka = _ease((u - .15) / .2); kb = _ease((u - .4) / .2)
            if ka > 0:
                cr.set_source_rgba(.75, .85, 1, .9); cr.rectangle(X(a), y - 30 * s, (xm - X(a)) * ka, 18 * s); cr.fill()
                _txt(cr, "208 TCN: Thục Phán lập nước Âu Lạc", X(a) - 10 * s, y - 120 * s, 28 * s, (.75, .85, 1), align="r", alpha=ka)
                cr.set_source_rgba(.75, .85, 1, ka); cr.move_to(X(a), y - 100 * s); cr.line_to(X(a), y - 30 * s); cr.set_line_width(3 * s); cr.stroke()
            if kb > 0:
                cr.set_source_rgba(1, .7, .3, .9); cr.rectangle(xm, y - 30 * s, (X(b) - xm) * kb, 18 * s); cr.fill()
                _txt(cr, "Năm 2026", X(b), y - 120 * s, 28 * s, (1, .85, .6), alpha=kb)
                cr.set_source_rgba(1, .85, .6, kb); cr.move_to(X(b), y - 100 * s); cr.line_to(X(b), y - 30 * s); cr.stroke()
            kc = _ease((u - .62) / .12)
            if kc > 0: _txt(cr, "208 + 2026 = 2 234: khoảng 2 234 năm", xm, y + 130 * s, 44 * s, (1, 1, 1), alpha=kc)
            kd = _ease((u - .82) / .1)
            if kd > 0: _txt(cr, "Chính xác: 2 234 − 1 = 2 233 năm (vì không có năm 0)", xm, y + 200 * s, 32 * s, (.95, .6, .5), bold=False, alpha=kd)
        yield _arr(surf, W, H)

def kim_tu_thap(W, H, n, fps):
    """Mô phỏng xây Kim tự tháp Kê-óp: các lớp đá xếp chồng dần (nhìn ngang), số liệu theo SGK LSĐL 6 tr. 33."""
    s = H / 1080; base_y = H * .80; cx = W * .33; half = W * .25; layers = 26; top_y = H * .20
    lh = (base_y - top_y) / layers
    for i in range(n):
        t = i / fps; u = i / max(n - 1, 1)
        surf, cr = _ctx(W, H)
        g = __import__("cairo").LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, .98, .86, .62); g.add_color_stop_rgb(1, .95, .75, .45); cr.set_source(g); cr.paint()
        cr.set_source_rgb(.88, .72, .48); cr.rectangle(0, base_y, W, H - base_y); cr.fill()
        _txt(cr, "KIM TỰ THÁP KÊ-ÓP (minh hoạ)", W * .06, H * .08, 40 * s, (.55, .2, .08), align="l")
        built = min(layers, int(_ease(u / .7) * layers + .0001))
        frac = _ease(u / .7) * layers - built
        for L in range(layers):
            if L > built: break
            w = half * (1 - L / layers); y = base_y - (L + 1) * lh
            k = 1 if L < built else frac
            if k <= 0: continue
            nb = max(1, int(w * 2 / (40 * s)))
            bw = w * 2 / nb
            for b in range(int(nb * k + .999)):
                x = cx - w + b * bw
                shade = .80 + .08 * ((b + L) % 3) / 2
                cr.set_source_rgb(.86 * shade, .70 * shade, .46 * shade); cr.rectangle(x + 1, y + 1, bw - 2, lh - 2); cr.fill()
        # thước đo chiều cao
        a = _ease((u - .72) / .08)
        if a > 0:
            cr.set_source_rgba(.55, .2, .08, a); cr.set_line_width(3 * s)
            hx = cx + half + 40 * s; cr.move_to(hx, base_y); cr.line_to(hx, top_y); cr.stroke()
            for yy in (base_y, top_y): cr.move_to(hx - 14 * s, yy); cr.line_to(hx + 14 * s, yy); cr.stroke()
            _txt(cr, "147 m", hx + 24 * s, (base_y + top_y) / 2, 44 * s, (.55, .2, .08), align="l", alpha=a)
        items = [(.80, "Khoảng 2,3 triệu tảng đá"), (.86, "Mỗi tảng nặng 2,5 – 4 tấn"), (.92, "Xếp chồng, không dùng vật liệu kết dính")]
        for j, (t0, lab) in enumerate(items):
            a = _ease((u - t0) / .05)
            if a > 0: _txt(cr, lab, W * .645, H * (.36 + j * .09), 30 * s, (.2, .15, .1), align="l", alpha=a)
        yield _arr(surf, W, H)

def _so_ai_cap(cr, sym, x, y, sz):
    """Vẽ kí hiệu chữ số Ai Cập cổ (giản lược): 1 nét gạch, 10 hình vòm, 100 cuộn dây, 1000 hoa sen."""
    cr.set_line_width(sz * .12); cr.set_line_cap(1)
    if sym == 1:
        cr.move_to(x, y - sz * .5); cr.line_to(x, y + sz * .5); cr.stroke()
    elif sym == 10:
        cr.move_to(x - sz * .3, y + sz * .5); cr.line_to(x - sz * .3, y - sz * .05); cr.curve_to(x - sz * .3, y - sz * .55, x + sz * .3, y - sz * .55, x + sz * .3, y - sz * .05); cr.line_to(x + sz * .3, y + sz * .5); cr.stroke()
    elif sym == 100:
        r = sz * .05; a = 0; cr.move_to(x, y)
        while r < sz * .38: a += .3; r += sz * .011; cr.line_to(x + r * math.cos(a), y + r * math.sin(a))
        cr.line_to(x + sz * .2, y - sz * .55); cr.stroke()
    elif sym == 1000:
        cr.move_to(x, y + sz * .5); cr.line_to(x, y - sz * .1); cr.stroke()
        cr.move_to(x, y - sz * .1); cr.curve_to(x - sz * .35, y - sz * .2, x - sz * .25, y - sz * .55, x, y - sz * .5); cr.curve_to(x + sz * .25, y - sz * .55, x + sz * .35, y - sz * .2, x, y - sz * .1); cr.stroke()
        cr.move_to(x - sz * .3, y + sz * .5); cr.line_to(x + sz * .3, y + sz * .5); cr.stroke()

def chu_so_ai_cap(W, H, n, fps):
    """Bảng chữ số Ai Cập (1, 10, 100, 1 000) và phép tính 124 + 321 = 445 theo cách viết của họ (bài tập SGK LSĐL 6 tr. 33)."""
    s = H / 1080; sz = 56 * s
    def draw_num(cr, num, x, y, a):
        cr.set_source_rgba(.2, .14, .08, a); xx = x
        for val in (1000, 100, 10, 1):
            for _ in range((num // val) % 10):
                _so_ai_cap(cr, val, xx, y, sz); xx += sz * .8
            if (num // val) % 10: xx += sz * .3
        return xx
    for i in range(n):
        u = i / max(n - 1, 1)
        surf, cr = _ctx(W, H)
        cr.set_source_rgb(.96, .90, .76); cr.paint()
        _txt(cr, "CHỮ SỐ CỦA NGƯỜI AI CẬP CỔ ĐẠI (hệ đếm thập phân)", W * .06, H * .08, 38 * s, (.55, .2, .08), align="l")
        for j, val in enumerate((1, 10, 100, 1000)):
            a = _ease((u - j * .07) / .06)
            if a <= 0: continue
            x = W * (.16 + j * .20); y = H * .26
            cr.set_source_rgba(.2, .14, .08, a); _so_ai_cap(cr, val, x, y, sz * 1.3)
            _txt(cr, f"{val:,}".replace(",", " "), x, y + 80 * s, 34 * s, (.55, .2, .08), alpha=a)
        rows = [(.32, 124, "124"), (.45, 321, "+ 321"), (.62, 445, "= 445")]
        for t0, num, lab in rows:
            a = _ease((u - t0) / .08)
            if a <= 0: continue
            y = H * (.48 + (t0 > .4) * .12 + (t0 > .6) * .14)
            _txt(cr, lab, W * .14, y, 44 * s, (.2, .14, .08), align="r", alpha=a)
            draw_num(cr, num, W * .20, y, a)
        if u > .62:
            cr.set_source_rgba(.55, .2, .08, _ease((u - .62) / .05)); cr.set_line_width(3 * s); cr.move_to(W * .08, H * .665); cr.line_to(W * .62, H * .665); cr.stroke()
        a = _ease((u - .80) / .08)
        if a > 0: _txt(cr, "Gộp các kí hiệu cùng loại: 10 nét gạch đổi thành 1 hình vòm,...", W * .06, H * .86, 28 * s, (.3, .25, .2), bold=False, align="l", alpha=a)
        yield _arr(surf, W, H)
