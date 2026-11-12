"""Bản đồ thế giới động (phép chiếu trụ đều) cho các hành trình: dữ liệu đất liền Natural Earth 1:110m (phạm vi công cộng),
không vẽ biên giới quốc gia. Kinh độ trong hành trình được 'trải phẳng' (đi mãi về phía tây vẫn liên tục), máy quay đi theo tàu.
Khi khu vực Biển Đông hiện trên khung hình, luôn vẽ quần đảo Hoàng Sa, Trường Sa của Việt Nam."""
import json, math, os
import numpy as np, cairo
HERE = os.path.dirname(__file__); ROOT = os.path.dirname(os.path.dirname(HERE))
FONT = "Be Vietnam Pro"
BIEN = (.80, .88, .93); DAT = (.93, .88, .76); BO = (.55, .5, .42); CHU = (.18, .2, .26); NUOC_CHU = (.25, .42, .58)
DO = (.72, .15, .12)
_LAND = None
def land():
    global _LAND
    if _LAND is None:
        g = json.load(open(os.path.join(ROOT, "assets/geo/ne_110m_land.geojson")))
        polys = []
        for f in g["features"]:
            geo = f["geometry"]; cs = geo["coordinates"]
            for poly in (cs if geo["type"] == "MultiPolygon" else [cs]):
                polys.append(np.array(poly[0], float))
        _LAND = polys
    return _LAND

DAO_VN = [("QĐ. Hoàng Sa", 112.0, 16.5), ("QĐ. Trường Sa", 114.0, 9.5)]

def text(cr, s, x, y, size, color, bold=True, italic=False, align="c", alpha=1.0, halo=True):
    cr.select_font_face(FONT, cairo.FONT_SLANT_ITALIC if italic else cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    cr.set_font_size(size); e = cr.text_extents(s)
    dx = {"c": -e.width / 2 - e.x_bearing, "l": 0, "r": -e.width}[align]
    cr.move_to(x + dx, y - e.height / 2 - e.y_bearing); cr.text_path(s)
    if halo: cr.set_source_rgba(1, 1, 1, .8 * alpha); cr.set_line_width(size * .22); cr.stroke_preserve()
    cr.set_source_rgba(*color, alpha); cr.fill()

class HanhTrinh:
    def __init__(self, name, W, H):
        self.S = json.load(open(os.path.join(HERE, "specs", name + ".json"))); self.W, self.H = W, H
        R = np.array(self.S["duong"], float)   # [[lon_trai_phang, lat], ...]
        d = np.r_[0, np.cumsum(np.hypot(np.diff(R[:, 0]) * np.cos(np.radians(R[:-1, 1])), np.diff(R[:, 1])))]
        self.R, self.d = R, d
    def pos(self, L):   # vị trí theo quãng đường
        L = min(max(L, 0), self.d[-1]); i = min(np.searchsorted(self.d, L), len(self.d) - 1); i = max(i, 1)
        a = (L - self.d[i - 1]) / max(self.d[i] - self.d[i - 1], 1e-9)
        return self.R[i - 1] + (self.R[i] - self.R[i - 1]) * a, self.R[i] - self.R[i - 1]
    def L_at(self, k):  # quãng đường tới điểm mốc thứ k
        return self.d[k]
    def frame(self, phase, u, t):
        W, H, S = self.W, self.H, self.S; ph = S["pha"][phase]; s = H / 1080
        ee = u * u * (3 - 2 * u)
        L0, L1 = self.L_at(ph["tu_moc"]), self.L_at(ph["den_moc"])
        Lcur = L0 + (L1 - L0) * min(1, ee / ph.get("ve_xong", .9))
        ship, v = self.pos(Lcur)
        span = ph.get("tam_nhin", 170.0); ppd = W / span
        if ph.get("camera"):   # máy quay cố định
            clon, clat = ph["camera"]
        else:
            clon = ship[0]
            lo, hi = ph.get("vi_do_khoang", [-30, 30]); clat = min(max(ship[1], lo), hi)
        X = lambda lon: W / 2 + (lon - clon) * ppd
        Y = lambda lat: H * .46 - (lat - clat) * ppd
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); cr = cairo.Context(surf)
        cr.set_source_rgb(*BIEN); cr.paint()
        # lưới kinh vĩ tuyến
        cr.set_source_rgba(1, 1, 1, .45); cr.set_line_width(1)
        lo = clon - span / 2 - 30
        for lon in range(int(math.floor(lo / 30) * 30), int(clon + span / 2 + 30), 30):
            cr.move_to(X(lon), 0); cr.line_to(X(lon), H); cr.stroke()
        for lat in range(-60, 90, 30):
            cr.move_to(0, Y(lat)); cr.line_to(W, Y(lat)); cr.stroke()
        cr.set_source_rgba(.85, .45, .3, .5); cr.set_dash([8, 6]); cr.move_to(0, Y(0)); cr.line_to(W, Y(0)); cr.stroke(); cr.set_dash([])
        # đất liền, lặp theo bội 360°
        for kk in range(int(math.floor((clon - span) / 360)), int(math.ceil((clon + span) / 360)) + 1):
            off = kk * 360
            for P in land():
                xs = P[:, 0] + off
                if xs.max() < clon - span / 2 - 5 or xs.min() > clon + span / 2 + 5: continue
                cr.move_to(X(xs[0]), Y(P[0, 1]))
                for x_, y_ in zip(xs[1:], P[1:, 1]): cr.line_to(X(x_), Y(y_))
                cr.close_path(); cr.set_source_rgb(*DAT); cr.fill_preserve(); cr.set_source_rgba(*BO, .8); cr.set_line_width(1.2); cr.stroke()
            for ten, lon, lat in DAO_VN:
                x, y = X(lon + off), Y(lat)
                if -50 < x < W + 50:
                    for j in range(5): cr.set_source_rgb(*BO); cr.arc(x + (j - 2) * 4 * s, y + ((j % 2) - .5) * 4 * s, 1.8 * s, 0, 6.3); cr.fill()
                    text(cr, ten, x + 10 * s, y - 14 * s, 15 * s, CHU, bold=False, align="l")
            for nh in S.get("nhan", []):
                x, y = X(nh[1] + off), Y(nh[2])
                if -300 < x < W + 300:
                    kind = nh[3] if len(nh) > 3 else "dat"
                    text(cr, nh[0], x, y, (26 if kind == "dat" else 22) * s, CHU if kind == "dat" else NUOC_CHU, bold=kind == "dat", italic=kind != "dat")
        # đường đã đi
        n = int(Lcur / max(self.d[-1], 1) * 2000) + 2
        Ls = np.linspace(0, Lcur, max(n, 2)); pts = [self.pos(L)[0] for L in Ls]
        cr.set_source_rgba(*DO, .9); cr.set_line_width(4.5 * s); cr.set_dash([14 * s, 8 * s])
        cr.move_to(X(pts[0][0]), Y(pts[0][1]))
        for p in pts[1:]: cr.line_to(X(p[0]), Y(p[1]))
        cr.stroke(); cr.set_dash([])
        # điểm mốc đã qua
        for m in S["moc"]:
            if self.L_at(m["chi_so"]) <= Lcur + 1e-6 and m["chi_so"] <= ph["den_moc"] and m["chi_so"] not in ph.get("an_moc", []):
                lon, lat = self.R[m["chi_so"]]; x, y = X(lon), Y(lat)
                cr.set_source_rgb(*DO); cr.arc(x, y, 7 * s, 0, 6.3); cr.fill(); cr.set_source_rgb(1, 1, 1); cr.arc(x, y, 3 * s, 0, 6.3); cr.fill()
                if m["chi_so"] >= ph.get("nhan_tu_moc", 0):
                    text(cr, m["chu"], x + m.get("dx", 0) * s, y + m.get("dy", -26) * s, 22 * s, DO, align=m.get("canh", "c"))
        # con tàu
        x, y = X(ship[0]), Y(ship[1]); ang = math.atan2(-v[1], v[0] * math.cos(math.radians(ship[1])))
        cr.save(); cr.translate(x, y); sc = 1.3 * s; cr.scale(sc, sc)
        cr.set_source_rgb(.35, .2, .1); cr.move_to(-16, 0); cr.line_to(16, 0); cr.line_to(11, 8); cr.line_to(-11, 8); cr.close_path(); cr.fill()
        cr.set_source_rgb(.98, .97, .92); cr.move_to(-2, -2); cr.line_to(-2, -26); cr.line_to(12, -8); cr.close_path(); cr.fill()
        cr.move_to(-6, -2); cr.line_to(-6, -20); cr.line_to(-16, -6); cr.close_path(); cr.fill()
        cr.set_source_rgb(*DO); cr.rectangle(-3, -30, 7, 4); cr.fill(); cr.restore()
        # thẻ tiêu đề + mốc thời gian
        cr.set_source_rgba(.12, .16, .24, .82); cr.rectangle(28, 26, 640 * s, 92 * s); cr.fill()
        text(cr, S["ten"], 52, 26 + 34 * s, 32 * s, (1, 1, 1), align="l", halo=False)
        text(cr, S.get("phu_de", ""), 52, 26 + 72 * s, 20 * s, (1, .85, .55), bold=False, align="l", halo=False)
        text(cr, S["nguon"], 32, 26 + 112 * s, 14 * s, CHU, bold=False, italic=True, align="l")
        if ph.get("moc_chu"):
            k = min(1, u / .06)
            cr.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); cr.set_font_size(24 * s)
            tw = cr.text_extents(ph["moc_chu"]).width + 60 * s; xx = W - tw - 30; yy = H * .165
            cr.set_source_rgba(.55, .1, .08, .85 * k); cr.rectangle(xx, yy, tw, 60 * s); cr.fill()
            text(cr, ph["moc_chu"], xx + tw / 2, yy + 30 * s, 24 * s, (1, .95, .85), alpha=k, halo=False)
        buf = np.ndarray((H, W, 4), np.uint8, surf.get_data(), 0, (surf.get_stride(), 4, 1))
        return buf[..., [2, 1, 0]].copy()

def frames(name, phase, W, H, n, fps=30):
    m = HanhTrinh(name, W, H)
    for i in range(n): yield m.frame(phase, i / max(1, n - 1), i / fps)
