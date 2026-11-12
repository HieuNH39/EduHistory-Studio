"""Sa bàn động vẽ bằng code (pycairo) cho các trận đánh / diễn biến.
Dữ liệu hình học: pipeline/maps/specs/<ten>.json (vẽ lại theo lược đồ SGK, toạ độ nguồn).
Mỗi 'pha' là một đoạn hoạt cảnh; frames(...) trả về từng khung hình RGB (numpy) để bộ dựng ghép vào video.

Ký hiệu theo SGK: chữ T có mũi tên = quân mai phục; mũi tên mảnh = quân đối phương tiến công;
mũi tên đậm = quân ta tấn công; ô vuông lồng = đại bản doanh."""
import json, math, os
import numpy as np, cairo

HERE = os.path.dirname(__file__)
FONT = "Be Vietnam Pro"
C = {  # bảng màu sa bàn (giấy cũ, nước xanh nhạt)
    "giay": (0.937, 0.905, 0.835), "giay2": (0.902, 0.858, 0.760), "dat": (0.905, 0.870, 0.760),
    "nuoc": (0.612, 0.765, 0.835), "bo": (0.400, 0.575, 0.690), "dao": (0.860, 0.820, 0.640),
    "cay": (0.365, 0.490, 0.300), "chu": (0.235, 0.184, 0.133), "chu_nuoc": (0.180, 0.370, 0.480),
    "ta": (0.722, 0.149, 0.118), "dich": (0.180, 0.243, 0.451), "vang": (0.960, 0.760, 0.250),
}

def ease(t):
    t = min(1, max(0, t)); return t * t * (3 - 2 * t)

def seg(u, a, b):
    """tiến độ 0..1 của một đoạn [a,b] trong trục thời gian u"""
    return ease((u - a) / max(1e-6, b - a))

def catmull(pts, n=16):
    """làm mượt đường gấp khúc → danh sách điểm dày"""
    P = [pts[0]] + list(pts) + [pts[-1]]; out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = map(np.array, (P[i - 1], P[i], P[i + 1], P[i + 2]))
        for k in range(n):
            t = k / n; t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(np.array(pts[-1], float)); return np.array(out)

def cut(path, frac):
    """phần đầu của đường, theo tỉ lệ độ dài"""
    if frac >= 1: return path
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))]
    L = d[-1] * max(0, frac); k = np.searchsorted(d, L)
    if k <= 0: return path[:1]
    a = (L - d[k - 1]) / max(1e-9, d[k] - d[k - 1])
    return np.vstack([path[:k], path[k - 1] + (path[k] - path[k - 1]) * a])

class SaBan:
    def __init__(self, name, W, H):
        self.S = json.load(open(os.path.join(HERE, "specs", name + ".json")))
        self.W, self.H = W, H
        x0, y0, x1, y1 = self.S["khung"]
        usable_h = H * 0.80  # chừa phần dưới cho phụ đề
        self.s = min(W / (x1 - x0), usable_h / (y1 - y0))
        self.ox = (W - (x1 - x0) * self.s) / 2 - x0 * self.s
        self.oy = H * 0.02 - y0 * self.s
        rng = np.random.default_rng(7)
        self.noise = (rng.random((H // 4, W // 4)) * 0.035).astype(np.float32)
        self.trees = self._trees(rng)
        self.base = self._base()

    # ---------- toạ độ
    def P(self, p): return (self.ox + p[0] * self.s, self.oy + p[1] * self.s)
    def PP(self, pts): return np.array([self.P(p) for p in pts])

    # ---------- chữ
    def text(self, cr, s, x, y, size, color, bold=False, italic=False, angle=0, align="c", alpha=1.0, halo=True):
        cr.save(); cr.translate(x, y); cr.rotate(math.radians(angle))
        cr.select_font_face(FONT, cairo.FONT_SLANT_ITALIC if italic else cairo.FONT_SLANT_NORMAL,
                            cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(size); e = cr.text_extents(s)
        dx = {"c": -e.width / 2 - e.x_bearing, "l": 0, "r": -e.width}[align]
        cr.move_to(dx, -e.height / 2 - e.y_bearing); cr.text_path(s)
        if halo:
            cr.set_source_rgba(*C["giay"], 0.85 * alpha); cr.set_line_width(size * 0.22); cr.set_line_join(cairo.LINE_JOIN_ROUND)
            cr.stroke_preserve()
        cr.set_source_rgba(*color, alpha); cr.fill(); cr.restore()

    def polyline(self, cr, pts):
        cr.move_to(*pts[0])
        for p in pts[1:]: cr.line_to(*p)

    # ---------- lớp nền tĩnh
    def _trees(self, rng):
        out = []
        for a, b in self.S.get("cay", []):
            a, b = np.array(a, float), np.array(b, float)
            for _ in range(int(np.linalg.norm(b - a) / 9)):
                t = rng.random(); side = rng.normal(0, 9)
                d = (b - a) / np.linalg.norm(b - a); nrm = np.array([-d[1], d[0]])
                out.append((a + (b - a) * t + nrm * side * (1 if rng.random() > .5 else -1) * 1.6, rng.uniform(3.5, 6.5)))
        return out

    def _base(self):
        W, H = self.W, self.H
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); cr = cairo.Context(surf)
        g = cairo.RadialGradient(W * .5, H * .45, H * .2, W * .5, H * .5, W * .75)
        g.add_color_stop_rgb(0, *C["giay"]); g.add_color_stop_rgb(1, *C["giay2"]); cr.set_source(g); cr.paint()
        # sông
        bank_n = catmull(self.S["song"]["bac"]); bank_s = catmull(self.S["song"]["nam"])
        river = np.vstack([self.PP(bank_n), self.PP(bank_s)])
        self.polyline(cr, river); cr.close_path(); cr.set_source_rgb(*C["nuoc"]); cr.fill_preserve()
        cr.set_source_rgba(*C["bo"], .9); cr.set_line_width(2.2); cr.stroke()
        # đảo, cồn
        for d in self.S["dao"]:
            self._island(cr, d)
        # rạch
        for r in self.S["rach"]:
            pts = self.PP(catmull(r["diem"], 10)); cr.set_line_cap(cairo.LINE_CAP_ROUND); cr.set_line_join(cairo.LINE_JOIN_ROUND)
            self.polyline(cr, pts); cr.set_source_rgba(*C["bo"], .9); cr.set_line_width(r["rong"] * self.s * 0.9 + 2.5); cr.stroke()
            self.polyline(cr, pts); cr.set_source_rgb(*C["nuoc"]); cr.set_line_width(r["rong"] * self.s * 0.9); cr.stroke()
        # cây hai bờ
        for (p, r) in self.trees:
            x, y = self.P(p); cr.arc(x, y, r * self.s * .55, 0, 2 * math.pi); cr.set_source_rgba(*C["cay"], .55); cr.fill()
        # nhãn
        for d in self.S["dia_danh"]:
            x, y = self.P(d["vi_tri"]); self.text(cr, d["ten"], x, y, 21 * self.s / 1.5, C["chu"], bold=True)
        for d in self.S["song_nhan"]:
            x, y = self.P(d["vi_tri"]); self.text(cr, d["ten"], x, y, 19 * self.s / 1.5, C["chu_nuoc"], italic=True, angle=d["goc"])
        for r in self.S["rach"]:
            if r.get("ten"):
                x, y = self.P(r["nhan"]); self.text(cr, r["ten"], x, y, 16 * self.s / 1.5, C["chu_nuoc"], italic=True, angle=r["goc"])
        for d in self.S["dao"]:
            x, y = self.P(d["nhan"]); self.text(cr, d["ten"], x, y, 15.5 * self.s / 1.5, C["chu"], italic=True, angle=d["goc"])
        # hạt giấy
        n = np.kron(self.noise, np.ones((4, 4), np.float32))[:H, :W]
        a = np.ndarray((H, W, 4), np.uint8, surf.get_data(), 0, (surf.get_stride(), 4, 1)).copy()
        a[..., :3] = np.clip(a[..., :3].astype(np.float32) * (1 - n[..., None]), 0, 255).astype(np.uint8)
        out = cairo.ImageSurface.create_for_data(bytearray(a.tobytes()), cairo.FORMAT_ARGB32, W, H, surf.get_stride())
        self._river = river; return out

    def _island(self, cr, d, glow=0.0):
        if "diem" in d:
            self.polyline(cr, self.PP(catmull(d["diem"] + [d["diem"][0]], 10))); cr.close_path()
        else:
            cx, cy, rx, ry, ang = d["elip"]; x, y = self.P((cx, cy))
            cr.save(); cr.translate(x, y); cr.rotate(math.radians(ang)); cr.scale(rx * self.s, ry * self.s)
            cr.arc(0, 0, 1, 0, 2 * math.pi); cr.restore()
        cr.set_source_rgb(*C["dao"]); cr.fill_preserve()
        if glow:
            cr.set_source_rgba(*C["vang"], .55 * glow); cr.fill_preserve()
            cr.set_source_rgba(*C["ta"], .9 * glow); cr.set_line_width(4); cr.stroke_preserve()
        cr.set_source_rgba(*C["bo"], .9); cr.set_line_width(1.8); cr.stroke()

    # ---------- ký hiệu
    def ambush(self, cr, x, y, ang, k, color):
        """chữ T có hai mũi tên (quân mai phục), k: 0..1 xuất hiện"""
        if k <= 0: return
        sc = self.s * (0.6 + 0.4 * k) * (1 + 0.25 * math.sin(k * math.pi))
        cr.save(); cr.translate(x, y); cr.rotate(math.radians(ang)); cr.scale(sc, sc)
        cr.set_source_rgba(*color, k)
        cr.rectangle(-26, -3.5, 52, 7); cr.fill()
        for dx in (-12, 12):
            cr.move_to(dx - 2.5, -3); cr.line_to(dx - 2.5, -13); cr.line_to(dx - 7, -13); cr.line_to(dx, -21)
            cr.line_to(dx + 7, -13); cr.line_to(dx + 2.5, -13); cr.line_to(dx + 2.5, -3); cr.close_path(); cr.fill()
        cr.restore()

    def arrow(self, cr, pts, frac, color, w0, w1, alpha=1.0, screen=False):
        """mũi tên thuôn theo đường cong, vẽ đến tỉ lệ frac (pts: toạ độ nguồn, hoặc toạ độ màn hình nếu screen=True)"""
        if frac <= 0.01: return
        path = cut(catmull(np.array(pts, float) if screen else self.PP(pts), 12), frac)
        if len(path) < 2: return
        d = np.diff(path, axis=0); L = np.linalg.norm(d, axis=1); L[L == 0] = 1e-6
        nrm = np.c_[-d[:, 1] / L, d[:, 0] / L]; nrm = np.vstack([nrm, nrm[-1]])
        t = np.linspace(0, 1, len(path)); w = (w0 + (w1 - w0) * t) * self.s
        head = min(len(path) - 1, max(1, int(len(path) * 0.25)))
        body = path[:-head + 1] if head > 1 else path
        left = body + nrm[:len(body)] * w[:len(body), None] / 2; right = body - nrm[:len(body)] * w[:len(body), None] / 2
        tip = path[-1]; base = body[-1]; bn = nrm[len(body) - 1]; hw = w[len(body) - 1] * 1.9
        cr.set_source_rgba(*color, alpha)
        self.polyline(cr, np.vstack([left, [base + bn * hw / 2], [tip], [base - bn * hw / 2], right[::-1]])); cr.close_path(); cr.fill()

    def boat(self, cr, x, y, ang, color, size=1.0, alpha=1.0):
        cr.save(); cr.translate(x, y); cr.rotate(ang); sc = self.s * size; cr.scale(sc, sc)
        cr.set_source_rgba(*color, alpha)
        cr.move_to(-16, -4); cr.curve_to(-8, -7, 10, -7, 18, 0); cr.curve_to(10, 7, -8, 7, -16, 4); cr.close_path(); cr.fill()
        cr.set_source_rgba(1, 1, 1, .55 * alpha); cr.move_to(-6, 0); cr.line_to(8, 0); cr.set_line_width(1.6); cr.stroke()
        cr.restore()

    def fire(self, cr, x, y, t, k, seed):
        rng = np.random.default_rng(seed)
        for j in range(7):
            ph = rng.random() * 6.28; r = (14 + 10 * rng.random()) * self.s * k * (0.8 + 0.25 * math.sin(t * 9 + ph))
            dx, dy = rng.normal(0, 8) * self.s, rng.normal(0, 5) * self.s - 6 * self.s * math.sin(t * 5 + ph) ** 2
            g = cairo.RadialGradient(x + dx, y + dy, 0, x + dx, y + dy, r)
            g.add_color_stop_rgba(0, 1, .95, .6, .95 * k); g.add_color_stop_rgba(.45, 1, .55, .1, .7 * k); g.add_color_stop_rgba(1, .7, .1, 0, 0)
            cr.set_source(g); cr.arc(x + dx, y + dy, r, 0, 6.29); cr.fill()
        for j in range(4):  # khói
            ph = rng.random() * 6.28; yy = y - (20 + 40 * ((t * .35 + j / 4) % 1)) * self.s
            g = cairo.RadialGradient(x, yy, 0, x, yy, 26 * self.s)
            g.add_color_stop_rgba(0, .25, .22, .2, .35 * k); g.add_color_stop_rgba(1, .25, .22, .2, 0)
            cr.set_source(g); cr.arc(x + 10 * math.sin(ph + t) * self.s, yy, 26 * self.s, 0, 6.29); cr.fill()

    def hq(self, cr, x, y, k):
        sz = 17 * self.s * (1 + .12 * math.sin(k * 12)); cr.set_line_width(3)
        cr.set_source_rgba(1, 1, 1, .9); cr.rectangle(x - sz, y - sz, 2 * sz, 2 * sz); cr.fill()
        cr.set_source_rgb(*C["ta"]); cr.rectangle(x - sz, y - sz, 2 * sz, 2 * sz); cr.stroke()
        cr.rectangle(x - sz * .5, y - sz * .5, sz, sz); cr.fill()

    def card(self, cr, alpha=1.0):
        W, H, s = self.W, self.H, self.s / 1.5
        cr.set_source_rgba(0.12, 0.16, 0.24, .78 * alpha); x, y, w, h = 28, 26, 520 * s, 92 * s
        r = 14; cr.new_sub_path(); cr.arc(x + w - r, y + r, r, -1.57, 0); cr.arc(x + w - r, y + h - r, r, 0, 1.57)
        cr.arc(x + r, y + h - r, r, 1.57, 3.14); cr.arc(x + r, y + r, r, 3.14, 4.71); cr.close_path(); cr.fill()
        self.text(cr, self.S["ten"], x + 24, y + 34 * s, 31 * s, (1, 1, 1), bold=True, align="l", halo=False, alpha=alpha)
        self.text(cr, self.S["phu_de"], x + 24, y + 70 * s, 21 * s, (1, .85, .55), align="l", halo=False, alpha=alpha)
        self.text(cr, self.S["nguon"], x + 4, y + h + 20 * s, 13.5 * s, C["chu"], italic=True, align="l", alpha=.8 * alpha)

    def legend(self, cr, items, alpha=1.0):
        if not items: return
        s = self.s / 1.5; x = 28; y = 158 * s; rowh = 30 * s
        h = rowh * len(items) + 16 * s; w = 330 * s
        cr.set_source_rgba(*C["giay"], .88 * alpha); cr.rectangle(x, y, w, h); cr.fill()
        cr.set_source_rgba(*C["chu"], .45 * alpha); cr.set_line_width(1.2); cr.rectangle(x, y, w, h); cr.stroke()
        for i, it in enumerate(items):
            cy = y + 8 * s + rowh * (i + .5); cx = x + 34 * s
            cr.save(); cr.translate(cx, cy); cr.scale(.62, .62); cr.translate(-cx, -cy)
            if it == "mai_phuc": self.ambush(cr, cx, cy + 8 * s, 0, alpha, C["ta"]); lab = "Quân Tây Sơn mai phục"
            elif it == "dich": self.arrow(cr, [[cx - 34 * s, cy], [cx + 34 * s, cy]], 1, C["dich"], 4, 7, alpha, screen=True); lab = "Quân Xiêm tiến công"
            elif it == "ta": self.arrow(cr, [[cx - 34 * s, cy], [cx + 34 * s, cy]], 1, C["ta"], 9, 14, alpha, screen=True); lab = "Quân Tây Sơn tấn công"
            elif it == "hq": self.hq(cr, cx, cy, 0); lab = "Đại bản doanh quân Tây Sơn"
            cr.restore()
            self.text(cr, lab, cx + 34 * s, cy, 16 * s, C["chu"], align="l", halo=False, alpha=alpha)

    def banner(self, cr, s_, k):
        if k <= 0: return
        W, H = self.W, self.H; sc = self.s / 1.5
        y = H * 0.40; h = 86 * sc; w = W * 0.62 * (0.7 + 0.3 * k)
        cr.set_source_rgba(*C["ta"], .9 * k); cr.rectangle((W - w) / 2, y - h / 2, w, h); cr.fill()
        cr.set_source_rgba(*C["vang"], k); cr.set_line_width(3); cr.rectangle((W - w) / 2 + 6, y - h / 2 + 6, w - 12, h - 12); cr.stroke()
        self.text(cr, s_, W / 2, y, 40 * sc, (1, .96, .85), bold=True, halo=False, alpha=k)

    # ---------- dựng khung hình theo pha
    def frame(self, phase, u, t):
        W, H = self.W, self.H; S = self.S
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); cr = cairo.Context(surf)
        # máy quay: đẩy nhẹ vào trung tâm trận địa
        zoom = {"dia_the": 1 + .03 * u, "mai_phuc": 1.03 + .03 * u, "nhu_dich": 1.06 + .04 * u, "ket_qua": 1.10 + .03 * u}.get(phase, 1)
        fx, fy = self.P((560, 420))
        cr.translate(fx, fy); cr.scale(zoom, zoom); cr.translate(-fx, -fy)
        cr.set_source_surface(self.base); cr.paint()
        appear = seg(u, 0, .08) if phase == "dia_the" else 1
        if phase == "dia_the" and appear < 1:
            cr.set_source_rgba(*C["giay"], 1 - appear); cr.paint()
        legend = []
        if phase == "dia_the":
            # độ dài khúc sông
            k = seg(u, .16, .34)
            if k > 0:
                a, b = np.array(self.P(S["do_dai"]["tu"])), np.array(self.P(S["do_dai"]["den"]))
                d = (b - a) / np.linalg.norm(b - a); n = np.array([d[1], -d[0]]) * 46 * self.s / 1.5
                p0, p1 = a + n, a + n + (b - a) * k
                cr.set_source_rgba(*C["ta"], .95); cr.set_line_width(3.2); cr.set_dash([10, 6]); cr.move_to(*p0); cr.line_to(*p1); cr.stroke(); cr.set_dash([])
                for p in (p0, p1 if k > .98 else None):
                    if p is not None: cr.move_to(*(p - n * .35)); cr.line_to(*(p + n * .35)); cr.stroke()
                if k > .6:
                    m = (a + b) / 2 + n * 1.7; ang = math.degrees(math.atan2(d[1], d[0]))
                    self.text(cr, S["do_dai"]["nhan"], m[0], m[1], 30 * self.s / 1.5, C["ta"], bold=True, angle=ang, alpha=seg(k, .6, 1))
            # bề rộng
            k = seg(u, .36, .5)
            if k > 0:
                a, b = np.array(self.P(S["be_rong"]["tu"])), np.array(self.P(S["be_rong"]["den"]))
                p1 = a + (b - a) * k
                cr.set_source_rgba(*C["dich"], .95); cr.set_line_width(3); cr.move_to(*a); cr.line_to(*p1); cr.stroke()
                for p in (a, p1):
                    cr.move_to(p[0] - 10, p[1]); cr.line_to(p[0] + 10, p[1]); cr.stroke()
                if k > .7: self.text(cr, S["be_rong"]["nhan"], a[0] + 20, (a[1] + b[1]) / 2, 22 * self.s / 1.5, C["dich"], bold=True, align="l", alpha=seg(k, .7, 1))
            # cù lao Thới Sơn sáng lên
            g = seg(u, .5, .58) * (1 - seg(u, .9, 1)) * (0.75 + .25 * math.sin(t * 6))
            if g > 0:
                for d in S["dao"]:
                    if d.get("noi_bat"): self._island(cr, d, glow=g); x, y = self.P(d["nhan"]); self.text(cr, d["ten"], x, y, 18 * self.s / 1.5, C["ta"], bold=True, angle=d["goc"], alpha=g)
            # kênh rạch và cây hai bờ nổi bật
            k = seg(u, .64, .76) * (0.7 + .3 * math.sin(t * 5))
            if k > 0:
                for r in S["rach"]:
                    if r.get("ten"):
                        pts = self.PP(catmull(r["diem"], 10)); self.polyline(cr, pts)
                        cr.set_source_rgba(*C["vang"], .7 * k); cr.set_line_width(r["rong"] * self.s + 8); cr.stroke()
                for (p, r) in self.trees:
                    x, y = self.P(p); cr.arc(x, y, r * self.s * .62, 0, 6.29); cr.set_source_rgba(*C["cay"], .55 * k); cr.fill()
        if phase in ("mai_phuc", "nhu_dich", "ket_qua"):
            legend += ["mai_phuc", "hq"]
            for i, (x, y, ang) in enumerate(S["mai_phuc"]):
                k = seg(u, .08 + i * .07, .2 + i * .07) if phase == "mai_phuc" else 1
                X, Y = self.P((x, y)); self.ambush(cr, X, Y, ang, k, C["ta"])
            X, Y = self.P(S["dai_ban_doanh"]); self.hq(cr, X, Y, t if phase == "mai_phuc" else 0)
        if phase in ("nhu_dich", "ket_qua"):
            legend.append("dich")
            path = catmull(self.PP(S["duong_xiem"]), 20)
            prog = (0.15 + 0.85 * seg(u, .05, .9)) if phase == "nhu_dich" else 1
            for i, a in enumerate(S["xiem"]):
                k = seg(prog, i * .22, i * .22 + .3)
                self.arrow(cr, a, k, C["dich"], 3, 6, .9)
            head = cut(path, prog)[-1]
            d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))]; L = d[-1] * prog
            for j in range(9):  # đoàn thuyền Xiêm
                Lj = L - j * 38 * self.s
                if Lj < 0: break
                k = np.searchsorted(d, Lj); k = min(max(k, 1), len(path) - 1)
                p = path[k]; v = path[k] - path[k - 1]; ang = math.atan2(v[1], v[0])
                off = ((j % 3) - 1) * 16 * self.s
                q = p + np.array([-math.sin(ang), math.cos(ang)]) * off
                burn = seg(u, .25 + j * .03, .5 + j * .03) if phase == "ket_qua" else 0
                self.boat(cr, q[0], q[1], ang, C["dich"], 1.0, 1 - .45 * burn)
                if burn > 0: self.fire(cr, q[0], q[1], t, burn, j)
        if phase == "ket_qua":
            legend.append("ta")
            for i, a in enumerate(S["tay_son"]):
                self.arrow(cr, a, seg(u, .04 + (i % 5) * .03, .3 + (i % 5) * .03), C["ta"], 8, 14, .95)
            for i, p in enumerate(S["dam_chay"]):
                k = seg(u, .3 + i * .04, .5 + i * .04); X, Y = self.P(p)
                if k > 0: self.fire(cr, X, Y, t, k, 100 + i)
        # thẻ tiêu đề, chú giải (không theo máy quay)
        cr.identity_matrix()
        self.card(cr, appear)
        self.legend(cr, legend)
        if phase == "ket_qua": self.banner(cr, "Thắng lợi hoàn toàn chỉ trong một ngày", seg(u, .62, .74))
        buf = np.ndarray((H, W, 4), np.uint8, surf.get_data(), 0, (surf.get_stride(), 4, 1))
        return buf[..., [2, 1, 0]].copy()

def frames(name, phase, W, H, n, fps=30):
    sb = SaBan(name, W, H)
    for i in range(n):
        yield sb.frame(phase, i / max(1, n - 1), i / fps)

if __name__ == "__main__":
    import sys  # kiểm tra nhanh: python saban.py rach-gam-xoai-mut ket_qua 0.8
    name, phase, u = sys.argv[1], sys.argv[2], float(sys.argv[3])
    sb = SaBan(name, 1920, 1080); fr = sb.frame(phase, u, u * 10)
    from PIL import Image; Image.fromarray(fr).save(f"/tmp/saban_{phase}.png"); print("ok")
