"""Sa bàn động – bộ máy tổng quát (phiên bản 2). Mỗi trận/diễn biến là một tệp JSON trong specs/ có "phien_ban": 2.
Hình học vẽ lại theo lược đồ SGK (toạ độ cục bộ của lược đồ). Mỗi 'pha' khai báo các đối tượng hiện sẵn và các bước
xuất hiện theo trục thời gian 0..1 của cảnh, nên một tệp dữ liệu phục vụ nhiều cảnh trong cùng tập.

Loại đối tượng: mui_ten_ta (đậm, đỏ), mui_ten_dich (mảnh, chàm), rut_chay (nét đứt, chàm), sao (nơi thắng lớn),
don_dich / don_ta (đồn), chan_danh (ký hiệu chặn đánh), mai_phuc (chữ T), vung (vùng tô), nhan (nhãn chữ)."""
import json, math, os
import numpy as np, cairo
from saban import C, ease, seg, catmull, cut, FONT

HERE = os.path.dirname(__file__)

class SaBan2:
    def __init__(self, name, W, H):
        self.S = json.load(open(os.path.join(HERE, "specs", name + ".json")))
        self.W, self.H = W, H
        x0, y0, x1, y1 = self.S["khung"]
        self.s = min(W * 0.96 / (x1 - x0), H * 0.80 / (y1 - y0))
        self.ox = (W - (x1 - x0) * self.s) / 2 - x0 * self.s + self.S.get("lech_x", 0) * W
        self.oy = H * 0.02 - y0 * self.s
        self.k = max(1.05, min(1.6, self.s / 0.7))   # hệ số cỡ chữ/nét theo tỉ lệ
        rng = np.random.default_rng(3)
        self.noise = (rng.random((H // 4, W // 4)) * 0.035).astype(np.float32)
        self.base = self._base()

    def P(self, p): return (self.ox + p[0] * self.s, self.oy + p[1] * self.s)
    def PP(self, pts): return np.array([self.P(p) for p in pts], float)

    def text(self, cr, s, x, y, size, color, bold=False, italic=False, angle=0, align="c", alpha=1.0, halo=True):
        cr.save(); cr.translate(x, y); cr.rotate(math.radians(angle))
        cr.select_font_face(FONT, cairo.FONT_SLANT_ITALIC if italic else cairo.FONT_SLANT_NORMAL,
                            cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(size); e = cr.text_extents(s)
        dx = {"c": -e.width / 2 - e.x_bearing, "l": 0, "r": -e.width}[align]
        cr.move_to(dx, -e.height / 2 - e.y_bearing); cr.text_path(s)
        if halo:
            cr.set_source_rgba(*C["giay"], 0.85 * alpha); cr.set_line_width(size * 0.22); cr.set_line_join(cairo.LINE_JOIN_ROUND); cr.stroke_preserve()
        cr.set_source_rgba(*color, alpha); cr.fill(); cr.restore()

    def line(self, cr, pts):
        cr.move_to(*pts[0])
        for p in pts[1:]: cr.line_to(*p)

    def _base(self):
        W, H, S, k = self.W, self.H, self.S, self.k
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); cr = cairo.Context(surf)
        g = cairo.RadialGradient(W * .5, H * .45, H * .2, W * .5, H * .5, W * .75)
        g.add_color_stop_rgb(0, *C["giay"]); g.add_color_stop_rgb(1, *C["giay2"]); cr.set_source(g); cr.paint()
        cr.set_line_cap(cairo.LINE_CAP_ROUND); cr.set_line_join(cairo.LINE_JOIN_ROUND)
        for poly in S.get("vung_nuoc", []):
            self.line(cr, self.PP(catmull(poly + [poly[0]], 8))); cr.close_path()
            cr.set_source_rgb(*C["nuoc"]); cr.fill_preserve(); cr.set_source_rgba(*C["bo"], .9); cr.set_line_width(1.8); cr.stroke()
        for poly in S.get("dat_noi", []):  # đảo, bãi
            self.line(cr, self.PP(catmull(poly + [poly[0]], 8))); cr.close_path()
            cr.set_source_rgb(*C["dao"]); cr.fill_preserve(); cr.set_source_rgba(*C["bo"], .9); cr.set_line_width(1.4); cr.stroke()
        for h in S.get("ho", []):
            if "elip" in h:
                cx, cy, rx, ry, a = h["elip"]; x, y = self.P((cx, cy))
                cr.save(); cr.translate(x, y); cr.rotate(math.radians(a)); cr.scale(rx * self.s, ry * self.s); cr.arc(0, 0, 1, 0, 6.2832); cr.restore()
            else:
                self.line(cr, self.PP(catmull(h["diem"] + [h["diem"][0]], 10))); cr.close_path()
            cr.set_source_rgb(*C["nuoc"]); cr.fill_preserve(); cr.set_source_rgba(*C["bo"], .9); cr.set_line_width(1.6); cr.stroke()
        for r in S.get("song", []):
            pts = self.PP(catmull(r["diem"], 10)); w = r.get("rong", 6) * self.s
            self.line(cr, pts); cr.set_source_rgba(*C["bo"], .9); cr.set_line_width(w + 2.5); cr.stroke()
            self.line(cr, pts); cr.set_source_rgb(*C["nuoc"]); cr.set_line_width(w); cr.stroke()
        for t in S.get("tuong_thanh", []):  # tường thành: đường răng cưa
            pts = cut(self.PP(catmull(t, 12)), 1.0)
            cr.set_source_rgba(*C["chu"], .75); cr.set_line_width(2.2 * k)
            d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]; step = 9 * k
            for L in np.arange(0, d[-1], step * 2):
                i = min(np.searchsorted(d, L), len(pts) - 1); j = min(np.searchsorted(d, L + step), len(pts) - 1)
                a, b = pts[i], pts[j]; v = b - a; n = np.array([-v[1], v[0]]) / (np.linalg.norm(v) + 1e-6) * 5 * k
                cr.move_to(*a); cr.line_to(*(a + n)); cr.line_to(*(b + n)); cr.line_to(*b); cr.stroke()
        for d in S.get("dia_danh", []):
            x, y = self.P(d["vi_tri"])
            if d.get("kieu") == "thanh": self.citadel(cr, x, y)
            elif d.get("kieu") == "diem": cr.arc(x, y, 4 * k, 0, 6.2832); cr.set_source_rgb(*C["chu"]); cr.fill()
            if d.get("ten"):
                nx, ny = self.P(d.get("nhan", d["vi_tri"]))
                self.text(cr, d["ten"], nx, ny, (24 if d.get("lon") else 18) * k, C["chu"], bold=bool(d.get("lon") or d.get("dam")))
        for r in S.get("song", []):
            if r.get("ten"):
                x, y = self.P(r["nhan"]); self.text(cr, r["ten"], x, y, 16 * k, C["chu_nuoc"], italic=True, angle=r.get("goc", 0))
        for h in S.get("ho", []):
            if h.get("ten"):
                x, y = self.P(h["nhan"]); self.text(cr, h["ten"], x, y, 15 * k, C["chu_nuoc"], italic=True)
        n = np.kron(self.noise, np.ones((4, 4), np.float32))[:H, :W]
        a = np.ndarray((H, W, 4), np.uint8, surf.get_data(), 0, (surf.get_stride(), 4, 1)).copy()
        a[..., :3] = np.clip(a[..., :3].astype(np.float32) * (1 - n[..., None]), 0, 255).astype(np.uint8)
        return cairo.ImageSurface.create_for_data(bytearray(a.tobytes()), cairo.FORMAT_ARGB32, W, H, surf.get_stride())

    # ----- ký hiệu
    def citadel(self, cr, x, y, glow=0):
        k = self.k; w = 34 * k
        if glow:
            g = cairo.RadialGradient(x, y, 0, x, y, w * 1.6); g.add_color_stop_rgba(0, *C["vang"], .7 * glow); g.add_color_stop_rgba(1, *C["vang"], 0)
            cr.set_source(g); cr.arc(x, y, w * 1.6, 0, 6.2832); cr.fill()
        cr.set_source_rgb(.33, .30, .27)
        cr.rectangle(x - w / 2, y - w * .1, w, w * .45); cr.fill()
        for i in range(4): cr.rectangle(x - w / 2 + i * w / 3.2, y - w * .22, w / 7, w * .14); cr.fill()
        cr.move_to(x - w * .38, y - w * .25); cr.line_to(x, y - w * .55); cr.line_to(x + w * .38, y - w * .25); cr.close_path(); cr.fill()

    def star(self, cr, x, y, k, color=None):
        if k <= 0: return
        r1 = 15 * self.k * (0.6 + 0.4 * k) * (1 + .3 * math.sin(k * math.pi)); r2 = r1 * .45
        cr.save(); cr.translate(x, y)
        g = cairo.RadialGradient(0, 0, 0, 0, 0, r1 * 2.2); g.add_color_stop_rgba(0, *C["vang"], .6 * k); g.add_color_stop_rgba(1, *C["vang"], 0)
        cr.set_source(g); cr.arc(0, 0, r1 * 2.2, 0, 6.2832); cr.fill()
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5; r = r1 if i % 2 == 0 else r2
            (cr.move_to if i == 0 else cr.line_to)(r * math.cos(a), r * math.sin(a))
        cr.close_path(); cr.set_source_rgba(*(color or C["ta"]), k); cr.fill_preserve(); cr.set_source_rgba(1, .9, .5, k); cr.set_line_width(1.5); cr.stroke(); cr.restore()

    def fort(self, cr, x, y, k, color, gone=0):
        if k <= 0: return
        w = 13 * self.k; cr.set_line_width(2.4)
        cr.set_source_rgba(*color, k * (1 - .6 * gone)); cr.rectangle(x - w, y - w, 2 * w, 2 * w); cr.stroke()
        cr.move_to(x - w * .1, y - w); cr.line_to(x - w * .1, y - w * 2.4); cr.stroke()
        cr.move_to(x - w * .1, y - w * 2.4); cr.line_to(x + w * 1.1, y - w * 2.0); cr.line_to(x - w * .1, y - w * 1.6); cr.close_path(); cr.fill()
        if gone > 0:
            cr.set_source_rgba(*C["ta"], gone); cr.set_line_width(3.5)
            cr.move_to(x - w * 1.3, y - w * 1.3); cr.line_to(x + w * 1.3, y + w * 1.3); cr.move_to(x + w * 1.3, y - w * 1.3); cr.line_to(x - w * 1.3, y + w * 1.3); cr.stroke()

    def block(self, cr, x, y, k, ang=0):
        if k <= 0: return
        cr.save(); cr.translate(x, y); cr.rotate(math.radians(ang)); s = self.k * (0.6 + 0.4 * k)
        cr.scale(s, s); cr.set_source_rgba(*C["ta"], k)
        cr.rectangle(-4, -18, 8, 36); cr.fill(); cr.rectangle(-4, -18, 18, 7); cr.fill(); cr.rectangle(-4, 11, 18, 7); cr.fill(); cr.restore()

    def arrow(self, cr, pts, frac, color, w0, w1, alpha=1.0, dashed=False, screen=False):
        if frac <= 0.01: return
        path = cut(catmull(np.array(pts, float) if screen else self.PP(pts), 12), frac)
        if len(path) < 2: return
        if dashed:
            cr.set_source_rgba(*color, alpha); cr.set_line_width(w0 * self.k); cr.set_dash([12 * self.k, 8 * self.k])
            self.line(cr, path[:-3] if len(path) > 4 else path); cr.stroke(); cr.set_dash([])
            tip = path[-1]; v = path[-1] - path[max(0, len(path) - 4)]; v = v / (np.linalg.norm(v) + 1e-6); n = np.array([-v[1], v[0]])
            hs = w0 * 2.6 * self.k
            cr.move_to(*tip); cr.line_to(*(tip - v * hs * 1.4 + n * hs)); cr.line_to(*(tip - v * hs * 1.4 - n * hs)); cr.close_path(); cr.fill(); return
        d = np.diff(path, axis=0); L = np.linalg.norm(d, axis=1); L[L == 0] = 1e-6
        nrm = np.c_[-d[:, 1] / L, d[:, 0] / L]; nrm = np.vstack([nrm, nrm[-1]])
        t = np.linspace(0, 1, len(path)); w = (w0 + (w1 - w0) * t) * self.k
        head = min(len(path) - 1, max(1, int(len(path) * 0.22)))
        body = path[:-head + 1] if head > 1 else path
        left = body + nrm[:len(body)] * w[:len(body), None] / 2; right = body - nrm[:len(body)] * w[:len(body), None] / 2
        tip = path[-1]; base = body[-1]; bn = nrm[len(body) - 1]; hw = w[len(body) - 1] * 1.9
        cr.set_source_rgba(*color, alpha)
        self.line(cr, np.vstack([left, [base + bn * hw / 2], [tip], [base - bn * hw / 2], right[::-1]])); cr.close_path(); cr.fill()

    def draw_obj(self, cr, o, k, t):
        typ = o["loai"]
        if typ == "mui_ten_ta": self.arrow(cr, o["diem"], k, C["ta"], o.get("w0", 8), o.get("w1", 14), .95)
        elif typ == "mui_ten_dich": self.arrow(cr, o["diem"], k, C["dich"], o.get("w0", 3), o.get("w1", 6), .9)
        elif typ == "rut_chay": self.arrow(cr, o["diem"], k, C["dich"], o.get("w0", 4), 4, .85, dashed=True)
        elif typ == "sao": x, y = self.P(o["vi_tri"]); self.star(cr, x, y, k)
        elif typ == "don_dich": x, y = self.P(o["vi_tri"]); self.fort(cr, x, y, 1 if k > 0 else 0, C["dich"], gone=o.get("_gone", 0))
        elif typ == "don_ta": x, y = self.P(o["vi_tri"]); self.fort(cr, x, y, k, C["ta"])
        elif typ == "chan_danh": x, y = self.P(o["vi_tri"]); self.block(cr, x, y, k, o.get("goc", 0))
        elif typ == "mai_phuc":
            x, y = self.P(o["vi_tri"]); sc = self.k * (0.6 + 0.4 * k) * (1 + .25 * math.sin(k * math.pi))
            cr.save(); cr.translate(x, y); cr.rotate(math.radians(o.get("goc", 0))); cr.scale(sc, sc); cr.set_source_rgba(*C["ta"], k)
            cr.rectangle(-22, -3, 44, 6); cr.fill()
            for dx in (-10, 10):
                cr.move_to(dx - 2, -3); cr.line_to(dx - 2, -11); cr.line_to(dx - 6, -11); cr.line_to(dx, -18); cr.line_to(dx + 6, -11); cr.line_to(dx + 2, -11); cr.line_to(dx + 2, -3); cr.close_path(); cr.fill()
            cr.restore()
        elif typ == "thanh_sang": x, y = self.P(o["vi_tri"]); self.citadel(cr, x, y, glow=k * (0.75 + .25 * math.sin(t * 5)))
        elif typ == "coc":   # bãi cọc ngầm: các cọc nhọn hiện dần khi nước rút
            for i, p in enumerate(o["diem"]):
                kk = max(0, min(1, k * len(o["diem"]) - i * .6))
                if kk <= 0: continue
                x, y = self.P(p); h = 14 * self.k * kk
                cr.set_source_rgba(.36, .25, .15, .95); cr.move_to(x - 3 * self.k, y); cr.line_to(x, y - h); cr.line_to(x + 3 * self.k, y); cr.close_path(); cr.fill()
        elif typ in ("thuyen_dich", "thuyen_ta"):   # đoàn thuyền chạy theo đường, k = tiến độ
            path = catmull(self.PP(o["diem"]), 20); d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))]
            L = d[-1] * (o.get("bat_dau", .15) + (1 - o.get("bat_dau", .15)) * k); col = C["dich"] if typ == "thuyen_dich" else C["ta"]
            for j in range(o.get("so", 6)):
                Lj = L - j * 34 * self.k
                if Lj < 0: break
                q = min(max(np.searchsorted(d, Lj), 1), len(path) - 1); p, v = path[q], path[q] - path[q - 1]
                ang = math.atan2(v[1], v[0]); off = ((j % 3) - 1) * 14 * self.k; pp = p + np.array([-math.sin(ang), math.cos(ang)]) * off
                stuck = o.get("_ket", 0)
                cr.save(); cr.translate(*pp); cr.rotate(ang + stuck * (0.5 if j % 2 else -0.4)); sc = self.k; cr.scale(sc, sc)
                cr.set_source_rgba(*col, 1 - .4 * stuck); cr.move_to(-14, -4); cr.curve_to(-7, -7, 9, -7, 16, 0); cr.curve_to(9, 7, -7, 7, -14, 4); cr.close_path(); cr.fill(); cr.restore()
        elif typ == "lua":
            for i, p in enumerate(o["diem"]):
                kk = max(0, min(1, k * 1.5 - i * .1))
                if kk > 0: x, y = self.P(p); self.fire(cr, x, y, t, kk, 50 + i)
        elif typ == "nhan":
            x, y = self.P(o["vi_tri"]); self.text(cr, o["chu"], x, y, o.get("co", 18) * self.k, C[o.get("mau", "ta")], bold=True, angle=o.get("goc", 0), alpha=k)

    def fire(self, cr, x, y, t, k, seed):
        rng = np.random.default_rng(seed); s = self.k
        for j in range(6):
            ph = rng.random() * 6.28; r = (13 + 9 * rng.random()) * s * k * (0.8 + 0.25 * math.sin(t * 9 + ph))
            dx, dy = rng.normal(0, 7) * s, rng.normal(0, 4) * s - 5 * s * math.sin(t * 5 + ph) ** 2
            g = cairo.RadialGradient(x + dx, y + dy, 0, x + dx, y + dy, r)
            g.add_color_stop_rgba(0, 1, .95, .6, .95 * k); g.add_color_stop_rgba(.45, 1, .55, .1, .7 * k); g.add_color_stop_rgba(1, .7, .1, 0, 0)
            cr.set_source(g); cr.arc(x + dx, y + dy, r, 0, 6.29); cr.fill()
        for j in range(3):
            yy = y - (18 + 36 * ((t * .35 + j / 3) % 1)) * s
            g = cairo.RadialGradient(x, yy, 0, x, yy, 22 * s); g.add_color_stop_rgba(0, .25, .22, .2, .32 * k); g.add_color_stop_rgba(1, .25, .22, .2, 0)
            cr.set_source(g); cr.arc(x, yy, 22 * s, 0, 6.29); cr.fill()

    def card(self, cr, alpha=1.0):
        s = self.k; x, y = 28, 26
        cr.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); cr.set_font_size(30 * s)
        w = max(cr.text_extents(self.S["ten"]).width + 60, 360 * s); h = 92 * s; r = 14
        cr.set_source_rgba(0.12, 0.16, 0.24, .78 * alpha); cr.new_sub_path(); cr.arc(x + w - r, y + r, r, -1.57, 0); cr.arc(x + w - r, y + h - r, r, 0, 1.57)
        cr.arc(x + r, y + h - r, r, 1.57, 3.14); cr.arc(x + r, y + r, r, 3.14, 4.71); cr.close_path(); cr.fill()
        self.text(cr, self.S["ten"], x + 24, y + 34 * s, 30 * s, (1, 1, 1), bold=True, align="l", halo=False, alpha=alpha)
        self.text(cr, self.S.get("phu_de", ""), x + 24, y + 70 * s, 20 * s, (1, .85, .55), align="l", halo=False, alpha=alpha)
        self.text(cr, self.S["nguon"], x + 4, y + h + 18 * s, 13 * s, C["chu"], italic=True, align="l", alpha=.8 * alpha)

    def legend(self, cr, items, alpha=1.0):
        if not items: return
        s = self.k; x = 28; y = 160 * s; rowh = 30 * s; w = 360 * s; h = rowh * len(items) + 16 * s
        cr.set_source_rgba(*C["giay"], .9 * alpha); cr.rectangle(x, y, w, h); cr.fill()
        cr.set_source_rgba(*C["chu"], .45 * alpha); cr.set_line_width(1.2); cr.rectangle(x, y, w, h); cr.stroke()
        for i, (typ, lab) in enumerate(items):
            cy = y + 8 * s + rowh * (i + .5); cx = x + 34 * s
            if typ == "mui_ten_ta": self.arrow(cr, [[cx - 22 * s, cy], [cx + 22 * s, cy]], 1, C["ta"], 6, 9, alpha, screen=True)
            elif typ == "mui_ten_dich": self.arrow(cr, [[cx - 22 * s, cy], [cx + 22 * s, cy]], 1, C["dich"], 3, 5, alpha, screen=True)
            elif typ == "rut_chay": self.arrow(cr, [[cx - 24 * s, cy], [cx + 24 * s, cy]], 1, C["dich"], 3, 3, alpha, dashed=True, screen=True)
            elif typ == "sao": self.star(cr, cx, cy, .8)
            elif typ == "don_dich": self.fort(cr, cx, cy + 5 * s, .9, C["dich"])
            elif typ == "chan_danh": self.block(cr, cx, cy, .8)
            elif typ == "coc":
                for dx in (-10, 0, 10): cr.set_source_rgb(.36, .25, .15); cr.move_to(cx + dx * s - 3, cy + 7); cr.line_to(cx + dx * s, cy - 9); cr.line_to(cx + dx * s + 3, cy + 7); cr.close_path(); cr.fill()
            elif typ == "mai_phuc":
                cr.set_source_rgb(*C["ta"]); cr.rectangle(cx - 18 * s, cy + 2, 36 * s, 5); cr.fill()
                for dx in (-8, 8): cr.move_to(cx + dx * s, cy - 10 * s); cr.line_to(cx + dx * s - 5, cy - 2); cr.line_to(cx + dx * s + 5, cy - 2); cr.close_path(); cr.fill(); cr.rectangle(cx + dx * s - 1.5, cy - 4, 3, 7); cr.fill()
            elif typ == "thanh": cr.save(); cr.translate(cx, cy); cr.scale(.6, .6); self.citadel(cr, 0, 0); cr.restore()
            self.text(cr, lab, cx + 36 * s, cy, 15.5 * s, C["chu"], align="l", halo=False, alpha=alpha)

    def frame(self, phase, u, t):
        W, H, S = self.W, self.H, self.S; ph = S["pha"][phase]
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); cr = cairo.Context(surf)
        z0, z1 = ph.get("zoom", [1.0, 1.04]); fx, fy = self.P(ph.get("tam", S.get("tam", [(S["khung"][0] + S["khung"][2]) / 2, (S["khung"][1] + S["khung"][3]) / 2])))
        z = z0 + (z1 - z0) * ease(u); cr.translate(fx, fy); cr.scale(z, z); cr.translate(-fx, -fy)
        cr.set_source_surface(self.base); cr.paint()
        if ph.get("mo_dau"):
            a = seg(u, 0, .08)
            if a < 1: cr.set_source_rgba(*C["giay"], 1 - a); cr.paint()
        objs = S["doi_tuong"]
        for oid in ph.get("hien", []):
            o = dict(objs[oid]); o["_gone"] = 1 if oid in ph.get("da_mat", []) else 0
            if oid in ph.get("mac_ket", {}): o["_ket"] = seg(u, *ph["mac_ket"][oid])
            self.draw_obj(cr, o, 1, t)
        for st in ph.get("buoc", []):
            k = seg(u, st["tu"], st["den"])
            if k <= 0: continue
            o = dict(objs[st["id"]])
            if st.get("hieu_ung") == "mat": o["_gone"] = k; self.draw_obj(cr, o, 1, t)
            else: self.draw_obj(cr, o, k, t)
        cr.identity_matrix()
        self.card(cr, seg(u, 0, .08) if ph.get("mo_dau") else 1)
        self.legend(cr, [(x["loai"], x["nhan"]) for x in S.get("chu_giai", []) if x["loai"] in ph.get("chu_giai", [c["loai"] for c in S.get("chu_giai", [])])])
        for m in ph.get("moc", []):  # mốc thời gian lớn góc phải
            k = seg(u, m["tu"], m["tu"] + .06) * (1 - seg(u, m.get("den", 1.1) - .05, m.get("den", 1.1)))
            if k > 0:
                s = self.k; tw = 560 * s; x = W - tw - 30; y = H * .14
                cr.set_source_rgba(.55, .1, .08, .85 * k); cr.rectangle(x, y, tw, 64 * s); cr.fill()
                self.text(cr, m["chu"], x + tw / 2, y + 32 * s, 22 * s, (1, .95, .85), bold=True, halo=False, alpha=k)
        if ph.get("bang"):
            b = ph["bang"]; k = seg(u, b["tu"], b["tu"] + .1)
            if k > 0:
                s = self.k; y = H * .40; h = 84 * s; w = W * .66 * (.7 + .3 * k)
                cr.set_source_rgba(*C["ta"], .9 * k); cr.rectangle((W - w) / 2, y - h / 2, w, h); cr.fill()
                cr.set_source_rgba(*C["vang"], k); cr.set_line_width(3); cr.rectangle((W - w) / 2 + 6, y - h / 2 + 6, w - 12, h - 12); cr.stroke()
                self.text(cr, b["chu"], W / 2, y, 36 * s, (1, .96, .85), bold=True, halo=False, alpha=k)
        buf = np.ndarray((H, W, 4), np.uint8, surf.get_data(), 0, (surf.get_stride(), 4, 1))
        return buf[..., [2, 1, 0]].copy()

def frames(name, phase, W, H, n, fps=30):
    sb = SaBan2(name, W, H)
    for i in range(n): yield sb.frame(phase, i / max(1, n - 1), i / fps)

if __name__ == "__main__":
    import sys
    from PIL import Image
    name, phase, u = sys.argv[1], sys.argv[2], float(sys.argv[3])
    Image.fromarray(SaBan2(name, 1920, 1080).frame(phase, u, u * 10)).save(f"/tmp/sb2_{phase}.png"); print("ok")
