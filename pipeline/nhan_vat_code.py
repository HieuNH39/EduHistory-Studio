"""Nhân vật dẫn chuyện vẽ HOÀN TOÀN BẰNG CODE (không dùng ảnh AI): Nhật Minh & Hân Hân.

Hoạt hình 2D vector (pycairo + numpy). Mỗi nhân vật là một bộ khung nhiều bộ phận có điểm xoay:
đầu, tóc (lớp sau / lớp trước), mắt có con ngươi, lông mày, miệng, cổ, thân áo, cánh tay trên / dưới
(IK hai đốt), bàn tay (ngón duỗi – co liên tục), chân, giày, ba lô. Tư thế là một bộ số thực, được
nội suy mượt (ease) giữa các "động tác", nên không có bước nhảy hình.

Bám bảng thiết kế brand/characters/bang-nhan-vat-v5.png và README:
  áo polo cam FPT, viền trắng mảnh ở cổ và cổ tay áo, huy hiệu tròn trắng ngực trái;
  Minh: quần kaki nâu nhạt, tóc đen ngắn gọn; Hân: váy xếp ly kaki trên gối, tóc đen ngang vai,
  kẹp tóc cam bên phải; tất trắng, giày trắng, ba lô xanh đậm. Tỉ lệ ≈ 5,5 đầu (học sinh 15 tuổi).

- Khẩu hình: biên độ giọng từng khung (giống dong2._env) + "độ tròn" của âm (trọng tâm phổ thấp → môi tròn).
  Chỉ người đang nói mới mấp máy môi. Lời đọc trong video bị render.py đặt trễ 0,15 s (adelay) → bù sẵn.
- Động tác tự chọn theo câu (chon_cu_chi): "?" → nghiêng đầu tò mò / chống cằm suy nghĩ;
  "nhé", "!" → mở tay giới thiệu, hai tay hào hứng; "chào", "hẹn gặp" → vẫy tay;
  "Dừng hình", "Thử thách", "các bạn" → chỉ về người xem; "Suỵt" → ngón tay lên môi; "kìa" → chỉ tay.
  Người nghe quay nhìn người nói, thỉnh thoảng gật đầu; khi người nói chỉ tay thì nhìn theo.
- Nền vẽ bằng code, chọn theo từ khoá trong "hinh": bờ sông; thư viện / lớp học; di tích – đình – tượng
  (mái đình chung chung, không phải công trình thật); bản đồ (bản đồ trang trí, đất liền tưởng tượng);
  mặc định: phòng thu nền dịu. Máy quay trôi chậm có thị sai theo lớp. 20% dưới đáy để trơn cho phụ đề,
  góc trên phải để trống cho logo.

API (cùng kiểu các nguồn hình trong render.scene_source):
    frames(sc, W, H, n, fps=30)  → sinh lần lượt n khung RGB (H, W, 3) uint8, không giữ cả cảnh trong RAM.
sc: {"loi": [[người nói, câu Việt, câu Anh], ...], "bounds": [(đầu, cuối), ...], "wav": đường dẫn,
     "lop": "dan_chuyen" | "du_hanh", "hinh": mô tả bối cảnh, tuỳ chọn "nen": loại nền ép buộc,
     "nhan_vat": ["Nhật Minh", "Hân Hân"], "so": số cảnh (làm hạt giống ngẫu nhiên)}.
"""
import os, math, hashlib, subprocess, unicodedata
import numpy as np
import cairo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NARR = ("Nhật Minh", "Hân Hân")
AUDIO_OFFSET = 0.15          # render.py: adelay = mốc cảnh + 150 ms
PI = math.pi
CHIEU_CAO = 1015.0           # chiều cao Nhật Minh trong hệ đơn vị vẽ (đỉnh tóc → đế giày)

# ------------------------------------------------------------------ bảng màu
VIEN = (60, 40, 36)
DA, DA_TOI, DA_SAU = (248, 211, 176), (231, 176, 140), (206, 140, 110)
CAM, CAM_TOI, CAM_SANG = (244, 118, 30), (214, 90, 22), (255, 152, 72)
TRANG = (255, 251, 244)
KAKI, KAKI_TOI, KAKI_SANG = (207, 180, 134), (178, 149, 107), (222, 200, 160)
NAVY, NAVY_TOI = (40, 52, 94), (27, 34, 66)
TOC, TOC_SANG = (33, 29, 38), (84, 88, 116)
GIAY, GIAY_TOI, DE_GIAY = (252, 251, 248), (215, 216, 224), (190, 192, 202)
MONG_MAT, CON_NGUOI = (74, 46, 34), (20, 14, 12)
MIENG, LUOI, MOI = (124, 42, 48), (234, 118, 116), (150, 66, 60)
MA_HONG = (242, 128, 118)
KEP_TOC = (248, 140, 36)


def _c(rgb, a=1.0):
    return (rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0, a)


def _cl(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def _ss(x):
    x = _cl(x)
    return x * x * (3 - 2 * x)


def _lerp(a, b, t):
    return a + (b - a) * t


# ------------------------------------------------------------------ nét vẽ cơ bản
def _capsule(ctx, x0, y0, x1, y1, r0, r1):
    """Hình con nhộng thuôn giữa hai đường tròn (đốt tay, chân, ngón)."""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    ctx.new_sub_path()
    if L < 1e-3 or L <= abs(r0 - r1):
        ctx.arc(x0, y0, max(r0, r1), 0, 2 * PI)
        ctx.close_path()
        return
    a = math.atan2(dy, dx)
    h = PI / 2 - math.asin(_cl((r0 - r1) / L, -1, 1))
    ctx.arc(x1, y1, r1, a - h, a + h)
    ctx.arc(x0, y0, r0, a + h, a + 2 * PI - h)
    ctx.close_path()


def _ellipse(ctx, cx, cy, rx, ry):
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(max(rx, 1e-3), max(ry, 1e-3))
    ctx.new_sub_path()
    ctx.arc(0, 0, 1, 0, 2 * PI)
    ctx.close_path()
    ctx.restore()


def _doi_xung(ctx, start, segs):
    """Vẽ nửa trái (start + các đoạn Bezier), rồi tự lấy đối xứng nửa phải theo trục x = 0."""
    ctx.move_to(*start)
    pts = [start]
    for c1, c2, p in segs:
        ctx.curve_to(c1[0], c1[1], c2[0], c2[1], p[0], p[1])
        pts.append(p)
    for i in range(len(segs) - 1, -1, -1):
        c1, c2, _ = segs[i]
        q = pts[i]
        ctx.curve_to(-c2[0], c2[1], -c1[0], c1[1], -q[0], q[1])
    ctx.close_path()


def _union(ctx, builders, fill, lw, line=VIEN):
    """Viền chung cho nhiều mảnh cùng màu: vẽ nét dày (2*lw) cho tất cả, rồi tô đè → viền ngoài liền mạch."""
    ctx.set_source_rgba(*_c(line))
    ctx.set_line_width(lw * 2)
    for b in builders:
        ctx.new_path(); b(); ctx.stroke()
    ctx.set_source_rgba(*(_c(fill) if len(fill) == 3 else fill))
    for b in builders:
        ctx.new_path(); b(); ctx.fill()


def _fs(ctx, builder, fill, lw, line=VIEN):
    ctx.new_path(); builder()
    ctx.set_source_rgba(*(_c(fill) if len(fill) == 3 else fill))
    ctx.fill_preserve()
    ctx.set_source_rgba(*_c(line)); ctx.set_line_width(lw); ctx.stroke()


def _bong(ctx, clip_b, shade_b, col, a):
    """Đổ bóng mềm: tô hình shade_b trong phạm vi clip_b."""
    ctx.save()
    ctx.new_path(); clip_b(); ctx.clip()
    ctx.new_path(); shade_b()
    ctx.set_source_rgba(*_c(col, a)); ctx.fill()
    ctx.restore()


def _ik(tx, ty, L1, L2, px, py):
    """IK hai đốt từ vai (0,0) tới cổ tay (tx,ty); chọn khuỷu theo hướng ưu tiên (px,py)."""
    d = math.hypot(tx, ty)
    d = min(max(d, abs(L1 - L2) + 1e-2, 1e-2), L1 + L2 - 1e-2)
    a = math.atan2(ty, tx)
    off = math.acos(_cl((L1 * L1 + d * d - L2 * L2) / (2 * L1 * d), -1, 1))
    best = None
    for sg in (1, -1):
        ex, ey = L1 * math.cos(a + sg * off), L1 * math.sin(a + sg * off)
        sc = ex * px + ey * py
        if best is None or sc > best[0]:
            best = (sc, ex, ey)
    return best[1], best[2], math.cos(a) * d, math.sin(a) * d


# ------------------------------------------------------------------ bàn tay (ngón duỗi/co liên tục)
NGON = [  # x gốc, dài, rộng, góc xoè  (ngón cái ở phía +x; trỏ → út)
    (15.0, 37.0, 12.6, 0.30),
    (4.6, 40.0, 12.8, 0.10),
    (-6.0, 37.0, 12.2, -0.10),
    (-16.0, 30.0, 11.2, -0.28),
]


def _ngon_path(ctx, j, idx, oth, spr, fore):
    x, L, w, ang = NGON[j]
    e = idx if j == 0 else oth
    Lc = 9.0 + (L - 9.0) * e
    if j == 0 and fore > 0:
        Lc *= (1 - 0.62 * fore)
    a = ang * spr + (0.0 if j == 0 else -0.05 * (1 - e))
    bx, by = x, 37.0
    _capsule(ctx, bx, by, bx + math.sin(a) * Lc, by + math.cos(a) * Lc, w / 2, w / 2 * 0.9)


def _long_ban_tay(ctx):
    ctx.move_to(-16, -6)
    ctx.line_to(16, -6)
    ctx.curve_to(21, 4, 24, 28, 22.5, 40)
    ctx.curve_to(20, 48, -20, 48, -22.5, 40)
    ctx.curve_to(-24, 28, -21, 4, -16, -6)
    ctx.close_path()


def _ngon_cai(ctx, idx, oth, spr, fore):
    open_ = max(oth, spr)
    a = -0.28 + 0.62 * oth + 0.55 * spr
    L = 20.0 + 9.0 * open_
    bx, by = 16.0, 13.0
    _capsule(ctx, bx, by, bx + math.sin(a) * L, by + math.cos(a) * L, 6.8, 5.8)


# ------------------------------------------------------------------ nhân vật
class NhanVat:
    def __init__(self, ten, huong):
        self.ten = ten
        self.nu = ten == "Hân Hân"
        self.huong = huong                  # +1: bạn diễn ở bên phải màn hình (Minh), -1 (Hân)
        self.k = 0.955 if self.nu else 1.0   # Hân thấp hơn một chút
        self.vai = 88.0 if self.nu else 100.0
        self.L1, self.L2 = (150.0, 140.0) if self.nu else (158.0, 148.0)
        self.lw = 4.4

    # ---------------- hình học tay
    def _tay(self, P, pre, s):
        sx, sy = s * (self.vai - 8), -276.0
        fore, fs = P[pre + "fore"], P[pre + "fs"]
        L1, L2 = self.L1, self.L2
        tx, ty = s * P[pre + "tx"], P[pre + "ty"]
        ex, ey, wx, wy = _ik(tx, ty, L1, L2, s * 0.55, 1.0)
        if fs > 1e-3:
            # cẳng tay chĩa về phía máy quay: khuỷu buông sát người, cẳng tay "ngắn lại" theo phối cảnh
            ad = math.radians(11)
            ex, ey = _lerp(ex, s * L1 * math.sin(ad), fs), _lerp(ey, L1 * math.cos(ad), fs)
            dxw, dyw = tx - ex, ty - ey
            dd = math.hypot(dxw, dyw)
            if dd > L2:
                dxw, dyw = dxw * L2 / dd, dyw * L2 / dd
            wx, wy = _lerp(wx, ex + dxw, fs), _lerp(wy, ey + dyw, fs)
        E, Wr = (sx + ex, sy + ey), (sx + wx, sy + wy)
        phi = math.atan2(Wr[1] - E[1], Wr[0] - E[0]) - s * P[pre + "wr"]
        hx, hy = s * P[pre + "hx"], P[pre + "hy"]
        hn = math.hypot(hx, hy) or 1.0
        fol = P[pre + "fol"]
        dx = fol * math.cos(phi) + (1 - fol) * hx / hn
        dy = fol * math.sin(phi) + (1 - fol) * hy / hn
        if math.hypot(dx, dy) < 1e-3:
            dx, dy = math.cos(phi), math.sin(phi)
        rho = math.atan2(dy, dx) - PI / 2
        # ngón cái hướng vào trong / lên; khi đổi phía thì bàn tay "xoay nghiêng" liên tục (co bề ngang), không giật
        d = (math.cos(rho) * (-s) + math.sin(rho) * (-1.0)) / math.sqrt(2)
        hsx = math.copysign(max(0.38, min(1.0, abs(d) / 0.45)), d)
        return dict(s=s, S=(sx, sy), E=E, W=Wr, ua=math.atan2(ey, ex), rho=rho, hsx=hsx,
                    raised=Wr[1] < E[1] - 6, idx=P[pre + "idx"], oth=P[pre + "oth"], spr=P[pre + "spr"],
                    hs=P[pre + "hs"], fore=fore, hwd=P[pre + "hwd"])

    def _ong_tay_ao(self, ctx, g):
        r0, r1, L = (27.0, 31.0, 80.0) if self.nu else (30.0, 34.0, 86.0)
        ctx.save()
        ctx.translate(*g["S"]); ctx.rotate(g["ua"] - PI / 2)
        ctx.new_sub_path()
        ctx.arc(0, 0, r0, PI, 2 * PI)
        ctx.line_to(r1, L - 4)
        ctx.curve_to(r1 * 0.6, L + 4, -r1 * 0.6, L + 4, -r1, L - 4)
        ctx.close_path()
        ctx.restore()

    def _ban_tay_tf(self, ctx, g):
        ctx.translate(*g["W"]); ctx.rotate(g["rho"])
        k = g["hs"] * (0.94 if self.nu else 1.0)
        ctx.scale(k * g["hwd"] * g["hsx"], k)

    def _ban_tay_paths(self, ctx, g):
        ctx.save(); self._ban_tay_tf(ctx, g)
        _long_ban_tay(ctx)
        for j in range(4):
            _ngon_path(ctx, j, g["idx"], g["oth"], g["spr"], g["fore"])
        _ngon_cai(ctx, g["idx"], g["oth"], g["spr"], g["fore"])
        ctx.restore()

    def _ve_tay(self, ctx, g):
        lw = self.lw
        r_u0, r_u1, r_f1 = (20.5, 18.0, 14.5) if self.nu else (23.5, 20.5, 16.5)
        S, E, Wr = g["S"], g["E"], g["W"]
        up = lambda: _capsule(ctx, S[0], S[1], E[0], E[1], r_u0, r_u1)
        fo = lambda: _capsule(ctx, E[0], E[1], Wr[0], Wr[1], r_u1, r_f1)
        hand = lambda: self._ban_tay_paths(ctx, g)
        # 1) viền chung cánh tay + bàn tay
        ctx.set_source_rgba(*_c(VIEN)); ctx.set_line_width(lw * 2)
        for b in ((up, fo, hand) if not g["raised"] else (up,)):
            ctx.new_path(); b(); ctx.stroke()
        ctx.set_source_rgba(*_c(DA)); ctx.new_path(); up(); ctx.fill()
        # 2) ống tay áo + viền trắng cổ tay áo
        sl = lambda: self._ong_tay_ao(ctx, g)
        ctx.set_source_rgba(*_c(CAM)); ctx.new_path(); sl(); ctx.fill()
        r1, L = (31.0, 80.0) if self.nu else (34.0, 86.0)
        ctx.save()
        ctx.new_path(); sl(); ctx.clip()
        ctx.translate(*S); ctx.rotate(g["ua"] - PI / 2)
        ctx.set_source_rgba(*_c(CAM_TOI, 0.55))   # bóng phía ngoài ống tay
        ctx.rectangle(g["s"] * r1 * 0.35 if g["s"] > 0 else -r1 * 1.4, -40, r1 * 1.05, L + 20); ctx.fill()
        ctx.set_source_rgba(*_c(TRANG)); ctx.set_line_width(4.6)
        ctx.move_to(-r1 - 4, L - 13); ctx.curve_to(-r1 * 0.5, L - 6, r1 * 0.5, L - 6, r1 + 4, L - 13); ctx.stroke()
        ctx.restore()
        ctx.save(); ctx.translate(*S); ctx.rotate(g["ua"] - PI / 2)
        ctx.set_source_rgba(*_c(VIEN)); ctx.set_line_width(lw)
        ctx.move_to(-r1, L - 4); ctx.curve_to(-r1 * 0.6, L + 4, r1 * 0.6, L + 4, r1, L - 4); ctx.stroke()
        ctx.set_line_width(lw * 0.8)
        ctx.move_to(-r1, L - 4); ctx.line_to(-r1 * 0.93, 26); ctx.stroke()
        ctx.move_to(r1, L - 4); ctx.line_to(r1 * 0.93, 26); ctx.stroke()
        ctx.restore()
        # 3) cẳng tay + bàn tay (giơ lên thì vẽ viền riêng, đè lên tay áo)
        if g["raised"]:
            ctx.set_source_rgba(*_c(VIEN)); ctx.set_line_width(lw * 2)
            for b in (fo, hand):
                ctx.new_path(); b(); ctx.stroke()
        ctx.set_source_rgba(*_c(DA))
        for b in (fo, hand):
            ctx.new_path(); b(); ctx.fill()
        self._chi_tiet_tay(ctx, g)

    def _chi_tiet_tay(self, ctx, g):
        lw = self.lw
        ctx.save(); self._ban_tay_tf(ctx, g)
        # bóng nhẹ lòng bàn tay
        ctx.save(); ctx.new_path(); _long_ban_tay(ctx); ctx.clip()
        ctx.set_source_rgba(*_c(DA_TOI, 0.45)); _ellipse(ctx, -14, 26, 14, 26); ctx.fill(); ctx.restore()
        # vạch tách ngón (ngoài lòng bàn tay)
        ctx.save()
        ctx.new_path(); ctx.rectangle(-200, -200, 400, 400); _long_ban_tay(ctx)
        ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD); ctx.clip(); ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
        ctx.set_source_rgba(*_c(VIEN)); ctx.set_line_width(lw * 0.55)
        for j in range(4):
            e = g["idx"] if j == 0 else g["oth"]
            if e > 0.12:
                ctx.new_path(); _ngon_path(ctx, j, g["idx"], g["oth"], g["spr"], g["fore"]); ctx.stroke()
        ctx.restore()
        if g["fore"] > 0.3:   # ngón trỏ chĩa về người xem: móng tay ở đầu ngón
            x, L, w, ang = NGON[0]
            Lc = (9 + (L - 9) * g["idx"]) * (1 - 0.62 * g["fore"])
            ctx.set_source_rgba(*_c((255, 232, 214), g["fore"]))
            _ellipse(ctx, x, 37 + Lc + 1, 4.2, 3.4); ctx.fill()
        # ngón cái: tô lại, nét mảnh phần nằm trên lòng bàn tay
        ctx.new_path(); _ngon_cai(ctx, g["idx"], g["oth"], g["spr"], g["fore"])
        ctx.set_source_rgba(*_c(DA)); ctx.fill()
        ctx.save(); ctx.new_path(); _long_ban_tay(ctx); ctx.clip()
        ctx.new_path(); _ngon_cai(ctx, g["idx"], g["oth"], g["spr"], g["fore"])
        ctx.set_source_rgba(*_c(VIEN)); ctx.set_line_width(lw * 0.6); ctx.stroke()
        ctx.restore()
        ctx.restore()

    # ---------------- thân
    def _than_path(self, ctx, hem):
        v = self.vai
        wst = v - (16 if self.nu else 8)
        _doi_xung(ctx, (-27.0, -328.0), [
            ((-44, -326), (-v + 22, -316), (-v + 2, -302)),
            ((-v - 8, -294), (-v - 6, -252), (-v + 1, -214)),
            ((-wst - 4, -150), (-wst, -90), (-wst + 2, hem)),
            ((-wst * 0.5, hem + 9), (-12, hem + 10), (0, hem + 10)),
        ])

    def _ve_than(self, ctx, P, gL, gR):
        lw, v = self.lw, self.vai
        hem = -46.0 if self.nu else -12.0
        tp = lambda: self._than_path(ctx, hem)
        # viền chung thân + hai ống tay áo, rồi tô thân
        ctx.set_source_rgba(*_c(VIEN)); ctx.set_line_width(lw * 2)
        for b in (tp, lambda: self._ong_tay_ao(ctx, gL), lambda: self._ong_tay_ao(ctx, gR)):
            ctx.new_path(); b(); ctx.stroke()
        ctx.set_source_rgba(*_c(CAM)); ctx.new_path(); tp(); ctx.fill()

        def shade():
            ctx.move_to(v * 0.30, -340)
            ctx.curve_to(v * 0.52, -250, v * 0.40, -120, v * 0.55, hem + 30)
            ctx.line_to(v + 40, hem + 30); ctx.line_to(v + 40, -340); ctx.close_path()
        _bong(ctx, tp, shade, CAM_TOI, 0.42)
        _bong(ctx, tp, lambda: _ellipse(ctx, 0, -282, 58, 20), CAM_TOI, 0.28)
        _bong(ctx, tp, lambda: _ellipse(ctx, -v * 0.45, -250, 26, 60), CAM_SANG, 0.35)
        ctx.set_source_rgba(*_c(CAM_TOI, 0.9)); ctx.set_line_width(2.4)   # nếp áo hai bên hông
        ctx.move_to(-v * 0.78, hem - 6); ctx.curve_to(-v * 0.74, hem - 40, -v * 0.70, hem - 70, -v * 0.72, hem - 96); ctx.stroke()
        ctx.move_to(v * 0.80, hem - 4); ctx.curve_to(v * 0.76, hem - 30, v * 0.74, hem - 52, v * 0.76, hem - 70); ctx.stroke()
        # cổ chữ V lộ da
        ctx.set_source_rgba(*_c(DA)); ctx.move_to(-24, -330); ctx.line_to(24, -330); ctx.line_to(0, -286); ctx.close_path(); ctx.fill()
        ctx.set_source_rgba(*_c(DA_TOI, 0.7)); ctx.move_to(-24, -330); ctx.line_to(24, -330); ctx.line_to(0, -306); ctx.close_path(); ctx.fill()
        # nẹp áo + cúc
        ctx.new_path(); ctx.rectangle(-8.5, -292, 17, 64)
        ctx.set_source_rgba(*_c(CAM)); ctx.fill_preserve(); ctx.set_source_rgba(*_c(VIEN)); ctx.set_line_width(lw * 0.55); ctx.stroke()
        for yb in (-270, -246):
            ctx.new_path(); ctx.arc(0, yb, 4.2, 0, 2 * PI)
            ctx.set_source_rgba(*_c(TRANG)); ctx.fill_preserve(); ctx.set_source_rgba(*_c(VIEN)); ctx.set_line_width(1.6); ctx.stroke()
        # cổ áo hai vạt, viền trắng mảnh
        for s in (-1, 1):
            def flap(s=s):
                ctx.move_to(s * 25, -334)
                ctx.curve_to(s * 40, -326, s * 52, -302, s * 55, -272)
                ctx.curve_to(s * 40, -276, s * 20, -282, s * 5, -289)
                ctx.curve_to(s * 11, -302, s * 17, -320, s * 21, -330)
                ctx.close_path()
            ctx.new_path(); flap(); ctx.set_source_rgba(*_c(CAM)); ctx.fill()
            ctx.save(); ctx.new_path(); flap(); ctx.clip()
            ctx.new_path(); flap(); ctx.set_source_rgba(*_c(TRANG)); ctx.set_line_width(7.0); ctx.stroke()
            ctx.new_path(); flap(); ctx.set_source_rgba(*_c(CAM)); ctx.set_line_width(2.4); ctx.stroke()
            ctx.restore()
            ctx.new_path(); flap(); ctx.set_source_rgba(*_c(VIEN)); ctx.set_line_width(lw * 0.85); ctx.stroke()
        # huy hiệu tròn trắng ngực trái (bên phải màn hình)
        bx, by = v * 0.50, -236
        ctx.new_path(); ctx.arc(bx, by, 12.5, 0, 2 * PI)
        ctx.set_source_rgba(*_c(TRANG)); ctx.fill_preserve(); ctx.set_source_rgba(*_c(VIEN)); ctx.set_line_width(1.8); ctx.stroke()
        ctx.new_path(); ctx.arc(bx, by, 7.5, 0, 2 * PI); ctx.set_source_rgba(*_c(CAM)); ctx.set_line_width(2.4); ctx.stroke()
        ctx.new_path(); ctx.arc(bx, by, 2.6, 0, 2 * PI); ctx.set_source_rgba(*_c(CAM)); ctx.fill()

    def _quai_ba_lo(self, ctx):
        v, lw = self.vai, self.lw
        for s in (-1, 1):
            def strap(s=s):
                ctx.move_to(s * (v * 0.50), -323)
                ctx.curve_to(s * (v * 0.62), -330, s * (v * 0.78), -322, s * (v * 0.80), -304)
                ctx.curve_to(s * (v * 0.84), -250, s * (v * 0.92), -200, s * (v + 4), -150)
                ctx.line_to(s * (v + 4), -112)
                ctx.curve_to(s * (v * 0.84), -160, s * (v * 0.66), -230, s * (v * 0.58), -300)
                ctx.curve_to(s * (v * 0.57), -310, s * (v * 0.54), -316, s * (v * 0.50), -323)
                ctx.close_path()
            _fs(ctx, strap, NAVY, lw * 0.85)
            ctx.new_path(); ctx.rectangle(s * v * 0.75 - 9, -262, 18, 9)
            ctx.set_source_rgba(*_c((120, 130, 150))); ctx.fill_preserve(); ctx.set_source_rgba(*_c(VIEN)); ctx.set_line_width(1.6); ctx.stroke()

    def _than_ba_lo(self, ctx):
        v = self.vai
        b = lambda: (ctx.new_sub_path(), self._rrect(ctx, -v - 16, -300, 2 * v + 32, 250, 34))
        _fs(ctx, b, NAVY, self.lw)
        _bong(ctx, b, lambda: ctx.rectangle(v - 4, -320, 60, 300), NAVY_TOI, 0.8)

    @staticmethod
    def _rrect(ctx, x, y, w, h, r):
        ctx.new_sub_path()
        ctx.arc(x + w - r, y + r, r, -PI / 2, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, PI / 2)
        ctx.arc(x + r, y + h - r, r, PI / 2, PI)
        ctx.arc(x + r, y + r, r, PI, 1.5 * PI)
        ctx.close_path()

    # ---------------- chân, quần, váy, giày
    def _giay(self, ctx, fx, s):
        w, h = (74.0, 50.0) if self.nu else (86.0, 58.0)
        cx = fx + s * 5
        def up():   # giày thể thao nhìn chính diện: mũi rộng, cổ giày hẹp
            ctx.move_to(cx - w / 2, -10)
            ctx.curve_to(cx - w / 2 - 2, -h * 0.55, cx - w * 0.36, -h * 0.92, cx - w * 0.24, -h)
            ctx.line_to(cx + w * 0.24, -h)
            ctx.curve_to(cx + w * 0.38, -h * 0.92, cx + w / 2 + 2, -h * 0.55, cx + w / 2, -10)
            ctx.close_path()
        _fs(ctx, up, GIAY, self.lw * 0.9)
        _bong(ctx, up, lambda: _ellipse(ctx, cx + w * 0.42, -h * 0.35, w * 0.28, h * 0.7), GIAY_TOI, 0.75)
        ctx.set_source_rgba(*_c(DE_GIAY)); ctx.set_line_width(2.4)   # lưỡi gà + dây giày
        ctx.move_to(cx - w * 0.17, -h * 0.98); ctx.curve_to(cx - w * 0.15, -h * 0.55, cx + w * 0.15, -h * 0.55, cx + w * 0.17, -h * 0.98); ctx.stroke()
        for yy in (-h * 0.86, -h * 0.74):
            ctx.move_to(cx - w * 0.13, yy); ctx.line_to(cx + w * 0.13, yy); ctx.stroke()
        ctx.move_to(cx - w * 0.38, -h * 0.30); ctx.curve_to(cx - w * 0.15, -h * 0.40, cx + w * 0.15, -h * 0.40, cx + w * 0.38, -h * 0.30); ctx.stroke()
        sole = lambda: self._rrect(ctx, cx - w / 2 - 3, -14, w + 6, 14, 6)
        _fs(ctx, sole, DE_GIAY, self.lw * 0.9)

    def _ve_chan(self, ctx, P):
        lw = self.lw
        px, py = P["hip"], -490.0 + P["bob"]
        ax = 40.0 if self.nu else 46.0
        if self.nu:
            legs = []
            for s in (-1, 1):
                kx = s * 41 + px * 0.45
                th = lambda s=s, kx=kx: _capsule(ctx, px + s * 42, py + 60, kx, -255, 34, 25)
                sh = lambda s=s, kx=kx: _capsule(ctx, kx, -255, s * ax, -46, 25, 17)
                legs += [th, sh]
            _union(ctx, legs, DA, lw)
            for s in (-1, 1):
                kx = s * 41 + px * 0.45
                sh = lambda s=s, kx=kx: _capsule(ctx, kx, -255, s * ax, -46, 25, 17)
                _bong(ctx, sh, lambda s=s: ctx.rectangle(s * ax + 2, -300, 30, 300), DA_TOI, 0.55)
                # tất trắng cổ cao
                ctx.save(); ctx.new_path(); sh(); ctx.clip()
                ctx.set_source_rgba(*_c(TRANG)); ctx.rectangle(-200, -150, 400, 140); ctx.fill()
                ctx.set_source_rgba(*_c(GIAY_TOI)); ctx.rectangle(s * ax + 4, -150, 30, 140); ctx.fill()
                ctx.set_source_rgba(*_c(VIEN)); ctx.set_line_width(lw * 0.7)
                ctx.move_to(-200, -150); ctx.line_to(200, -150); ctx.stroke()
                ctx.set_source_rgba(*_c(GIAY_TOI)); ctx.set_line_width(1.5)
                ctx.move_to(-200, -141); ctx.line_to(200, -141); ctx.stroke()
                ctx.restore()
            for s in (-1, 1):
                self._giay(ctx, s * ax, s)
            return
        # Minh: giày trước, ống quần phủ lên
        for s in (-1, 1):
            self._giay(ctx, s * ax, s)
        parts = []
        top = lambda: (ctx.move_to(px - 88, py - 66), ctx.line_to(px + 88, py - 66), ctx.line_to(px + 92, py + 22),
                       ctx.line_to(px, py + 70), ctx.line_to(px - 92, py + 22), ctx.close_path())
        parts.append(top)
        for s in (-1, 1):
            def leg(s=s):
                ctx.move_to(px + s * 92, py - 10)
                ctx.curve_to(px + s * 96, py + 150, s * (ax + 34), -230, s * (ax + 30), -34)
                ctx.curve_to(s * (ax + 10), -28, s * (ax - 14), -28, s * (ax - 26), -34)
                ctx.curve_to(s * (ax - 30), -200, px + s * 8, py + 120, px + s * 2, py + 64)
                ctx.close_path()
            parts.append(leg)
        _union(ctx, parts, KAKI, lw)
        for s in (-1, 1):
            leg = parts[1 if s < 0 else 2]
            _bong(ctx, leg, lambda s=s: (ctx.move_to(s * ax + 6, -20), ctx.line_to(px + s * 30 + 14, py),
                                         ctx.line_to(px + s * 120 + 60, py), ctx.line_to(s * ax + 80, -20), ctx.close_path()),
                  KAKI_TOI, 0.55)
            ctx.set_source_rgba(*_c(KAKI_TOI)); ctx.set_line_width(2.2)   # nếp ly quần
            ctx.move_to(px * 0.6 + s * (ax + 4) * 0.98, -300); ctx.line_to(s * (ax + 2), -60); ctx.stroke()
            ctx.set_source_rgba(*_c(VIEN)); ctx.set_line_width(lw * 0.6)
            ctx.move_to(px + s * 2, py + 64); ctx.line_to(px + s * 2, py + 40); ctx.stroke()

    def _ve_vay(self, ctx, P):
        lw = self.lw
        px, py = P["hip"], -490.0 + P["bob"]
        top, hem = py - 62, py + 160
        tw, hw = 84.0, 132.0
        sw = P.get("sway", 0.0)
        N = 8
        def skirt():
            ctx.move_to(px - tw, top)
            ctx.line_to(px + tw, top)
            ctx.curve_to(px + tw + 20, top + 60, px + hw - 6 + sw, hem - 50, px + hw + sw, hem)
            for i in range(N, 0, -1):
                x0 = px - hw + 2 * hw * i / N + sw
                x1 = px - hw + 2 * hw * (i - 1) / N + sw
                ctx.curve_to(x0 - 4, hem + 8, x1 + 4, hem + 8, x1, hem)
            ctx.curve_to(px - hw + 6 + sw, hem - 50, px - tw - 20, top + 60, px - tw, top)
            ctx.close_path()
        _fs(ctx, skirt, KAKI, lw)
        for i in range(N):   # xếp ly: mảng sáng – tối xen kẽ
            if i % 2 == 0:
                continue
            xt0, xt1 = px - tw + 2 * tw * i / N, px - tw + 2 * tw * (i + 1) / N
            xh0, xh1 = px - hw + 2 * hw * i / N + sw, px - hw + 2 * hw * (i + 1) / N + sw
            _bong(ctx, skirt, lambda: (ctx.move_to(xt0, top), ctx.line_to(xt1, top), ctx.line_to(xh1, hem + 12),
                                      ctx.line_to(xh0, hem + 12), ctx.close_path()), KAKI_TOI, 0.32)
        _bong(ctx, skirt, lambda: ctx.rectangle(px + tw * 0.4, top, 200, 260), KAKI_TOI, 0.35)
        ctx.set_source_rgba(*_c(KAKI_TOI)); ctx.set_line_width(2.0)
        for i in range(1, N):
            ctx.move_to(px - tw + 2 * tw * i / N, top + 16); ctx.line_to(px - hw + 2 * hw * i / N + sw, hem + 2); ctx.stroke()
        band = lambda: ctx.rectangle(px - tw - 1, top, 2 * tw + 2, 15)
        _fs(ctx, band, KAKI_SANG, lw * 0.7)

    # ---------------- đầu
    def _mat_path(self, ctx):  # khuôn mặt
        if self.nu:
            _doi_xung(ctx, (0.0, 11.0), [((-22, 11), (-50, -6), (-61, -36)),
                                         ((-69, -60), (-72, -96), (-72, -122)),
                                         ((-71, -166), (-40, -188), (0, -188))])
        else:
            _doi_xung(ctx, (0.0, 14.0), [((-25, 14), (-53, -4), (-63, -36)),
                                         ((-71, -60), (-74, -96), (-73, -122)),
                                         ((-72, -166), (-40, -188), (0, -188))])

    def _toc_sau_han(self, ctx):
        ctx.move_to(0, -206)
        ctx.curve_to(62, -206, 98, -160, 95, -100)
        ctx.curve_to(93, -50, 98, 0, 106, 38)
        ctx.curve_to(100, 46, 94, 50, 86, 52)
        ctx.line_to(80, 40); ctx.curve_to(74, 50, 66, 54, 58, 52); ctx.line_to(52, 28)
        ctx.curve_to(20, 34, -20, 34, -52, 28)
        ctx.line_to(-58, 52); ctx.curve_to(-66, 54, -74, 50, -80, 40); ctx.line_to(-86, 52)
        ctx.curve_to(-94, 50, -100, 46, -106, 38)
        ctx.curve_to(-98, 0, -93, -50, -95, -100)
        ctx.curve_to(-98, -160, -62, -206, 0, -206)
        ctx.close_path()

    def _toc_truoc_minh(self, ctx, o):
        ctx.move_to(-74, -88)
        ctx.curve_to(-82, -118, -86, -158, -70, -182)
        ctx.curve_to(-52, -206, -14, -210, 8 + o, -207)
        ctx.curve_to(50, -205, 84, -186, 82, -148)
        ctx.curve_to(81, -126, 78, -106, 73, -88)
        ctx.line_to(67, -98)
        ctx.curve_to(66, -112, 63, -124, 56 + o, -132)
        # mái gọn, rẽ ngôi lệch, các lọn bo tròn chải sang trái
        V = [(56, -132), (30, -142), (4, -144), (-22, -140)]
        T = [(36, -120), (10, -121), (-16, -119), (-44, -114)]
        for k in range(4):
            vx, vy = V[k][0] + o, V[k][1]
            tx, ty = T[k][0] + o, T[k][1]
            ctx.curve_to(vx - 4, vy + 8, tx + 12, ty + 2, tx, ty)
            if k < 3:
                nx, ny = V[k + 1][0] + o, V[k + 1][1]
                ctx.curve_to(tx - 4, ty - 3, nx + 6, ny + 3, nx, ny)
        ctx.curve_to(-54, -118, -62, -112, -66, -100)
        ctx.close_path()

    def _toc_truoc_han(self, ctx, o):
        ctx.move_to(-78, -92)
        ctx.curve_to(-84, -160, -50, -210, 0 + o, -210)
        ctx.curve_to(54, -210, 86, -160, 78, -92)
        ctx.curve_to(72, -112, 62, -126, 50 + o, -132)
        V = [(50, -132), (27, -142), (4, -144), (-20, -140), (-44, -132)]
        T = [(34, -112), (12, -108), (-12, -111), (-36, -108), (-60, -104)]
        for k in range(5):
            vx, vy = V[k][0] + o, V[k][1]
            tx, ty = T[k][0] + o, T[k][1]
            ctx.curve_to(vx - 5, vy + 8, tx + 9, ty - 12, tx, ty)
            if k < 4:
                nx, ny = V[k + 1][0] + o, V[k + 1][1]
                ctx.curve_to(tx + 2, ty - 12, nx + 8, ny + 2, nx, ny)
        ctx.curve_to(-66, -104, -72, -98, -78, -92)
        ctx.close_path()

    def _toc_mai_han(self, ctx, s, o):   # lọn tóc hai bên má (che tai)
        ctx.move_to(s * 66 + o * 0.3, -132)
        ctx.curve_to(s * 88, -100, s * 90, -40, s * 84, 18)
        ctx.curve_to(s * 80, 26, s * 74, 30, s * 68, 24)
        ctx.line_to(s * 66, 14)
        ctx.curve_to(s * 70, -30, s * 66, -80, s * 60 + o * 0.3, -122)
        ctx.close_path()

    @staticmethod
    def _mat_hinh(ctx, cx, cy, rx, ry, op, side, upper_only=False):
        """Mắt hình hạnh nhân; op = độ mở (mí trên hạ xuống khi nháy)."""
        xi, xo = cx - side * rx, cx + side * rx
        yu = _lerp(cy + ry * 0.62, cy - ry * 1.40, op)
        ctx.move_to(xi, cy + ry * 0.14)
        ctx.curve_to(cx - side * rx * 0.55, yu, cx + side * rx * 0.42, yu, xo, cy - ry * 0.16)
        if upper_only:
            return
        ctx.curve_to(cx + side * rx * 0.48, cy + ry * 0.98, cx - side * rx * 0.5, cy + ry * 0.98, xi, cy + ry * 0.14)
        ctx.close_path()

    def _ve_mat(self, ctx, cx, cy, rx, ry, lx, ly, blink, side):
        lw = self.lw
        op = 1 - _cl(blink)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        if op < 0.18:
            ctx.set_source_rgba(*_c((30, 22, 22))); ctx.set_line_width(lw * 0.95)
            ctx.move_to(cx - rx, cy + ry * 0.2); ctx.curve_to(cx - rx * 0.4, cy + ry * 0.75, cx + rx * 0.4, cy + ry * 0.75, cx + rx, cy + ry * 0.15)
            ctx.stroke()
            return
        ctx.save()
        ctx.new_path(); self._mat_hinh(ctx, cx, cy, rx, ry, op, side); ctx.clip()
        ctx.set_source_rgba(*_c((255, 255, 255))); ctx.paint()
        ir = ry * (0.86 if self.nu else 0.82)
        ix, iy = cx + lx * rx * 0.28, cy + ly * ry * 0.26 + ry * 0.08
        ctx.set_source_rgba(*_c(MONG_MAT)); ctx.new_path(); ctx.arc(ix, iy, ir, 0, 2 * PI); ctx.fill()
        ctx.set_source_rgba(*_c((132, 88, 60), 0.75)); ctx.new_path(); ctx.arc(ix, iy + ir * 0.30, ir * 0.62, 0.15, PI - 0.15); ctx.fill()
        ctx.set_source_rgba(*_c(CON_NGUOI)); ctx.new_path(); ctx.arc(ix, iy, ir * 0.50, 0, 2 * PI); ctx.fill()
        ctx.set_source_rgba(1, 1, 1, 1); ctx.new_path(); ctx.arc(ix - ir * 0.34, iy - ir * 0.34, ir * 0.30, 0, 2 * PI); ctx.fill()
        ctx.new_path(); ctx.arc(ix + ir * 0.36, iy + ir * 0.30, ir * 0.13, 0, 2 * PI); ctx.fill()
        ctx.set_source_rgba(*_c((120, 90, 80), 0.18)); ctx.set_line_width(ry * 0.4)   # bóng mí trên
        ctx.new_path(); self._mat_hinh(ctx, cx, cy, rx, ry, op, side, upper_only=True); ctx.stroke()
        ctx.restore()
        # mí trên đậm; Hân có nét hất mi ở đuôi mắt
        ctx.set_source_rgba(*_c((30, 22, 22)))
        ctx.set_line_width(lw * (1.3 if self.nu else 1.05))
        ctx.new_path(); self._mat_hinh(ctx, cx, cy, rx, ry, op, side, upper_only=True); ctx.stroke()
        if self.nu:
            ox, oy = cx + side * rx, cy - ry * 0.16
            ctx.set_line_width(lw * 0.85)
            ctx.move_to(ox - side * 3, oy - 1); ctx.line_to(ox + side * 6, oy - ry * 0.55 * op); ctx.stroke()
        ctx.set_line_width(1.6); ctx.set_source_rgba(*_c(VIEN, 0.35))
        ctx.move_to(cx + side * rx * 0.55, cy + ry * 0.78); ctx.curve_to(cx + side * rx * 0.2, cy + ry * 0.95, cx - side * rx * 0.2, cy + ry * 0.95, cx - side * rx * 0.5, cy + ry * 0.78)
        ctx.stroke()

    def _ve_mieng(self, ctx, mx, my, P):
        lw = self.lw
        w = 26.0 if self.nu else 30.0
        o, r, sm = _cl(P["mo"]), _cl(P["mr"]), _cl(P["smile"])
        ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        if o < 0.07:
            hw = w / 2 * (1 - 0.35 * r) * (0.8 + 0.25 * sm)
            ctx.set_source_rgba(*_c(MOI)); ctx.set_line_width(lw * 0.78)
            ctx.move_to(mx - hw, my - sm * 3)
            ctx.curve_to(mx - hw * 0.4, my + sm * 6 + 1, mx + hw * 0.4, my + sm * 6 + 1, mx + hw, my - sm * 3)
            ctx.stroke()
            return
        hw = w / 2 * (1 - 0.40 * r) * (0.86 + 0.22 * o)
        h = 3.5 + o * (22.0 if self.nu else 25.0)
        def m():
            ctx.move_to(mx - hw, my - sm * 2)
            ctx.curve_to(mx - hw * 0.45, my - h * 0.40 * r + sm * 1.5, mx + hw * 0.45, my - h * 0.40 * r + sm * 1.5, mx + hw, my - sm * 2)
            ctx.curve_to(mx + hw * (0.95 - 0.2 * r), my + h * 1.25, mx - hw * (0.95 - 0.2 * r), my + h * 1.25, mx - hw, my - sm * 2)
            ctx.close_path()
        ctx.new_path(); m(); ctx.set_source_rgba(*_c(MIENG)); ctx.fill()
        ctx.save(); ctx.new_path(); m(); ctx.clip()
        if o > 0.22:
            ctx.set_source_rgba(*_c((255, 255, 255))); ctx.rectangle(mx - hw, my - h, 2 * hw, h + min(h * 0.26, 5.5)); ctx.fill()
        if o > 0.3:
            ctx.set_source_rgba(*_c(LUOI)); _ellipse(ctx, mx, my + h * 0.98, hw * 0.62, h * 0.42); ctx.fill()
        ctx.restore()
        ctx.new_path(); m(); ctx.set_source_rgba(*_c(VIEN)); ctx.set_line_width(lw * 0.7); ctx.stroke()

    def _ve_dau(self, ctx, P):
        lw = self.lw
        turn, nod = P["turn"], P["nod"]
        fx, fy = turn * 13.0, nod * 5.0
        face = lambda: self._mat_path(ctx)
        if not self.nu:   # tai
            eo = -turn * 5
            for s in (-1, 1):
                sxs = 1 - 0.55 * max(0.0, s * turn)
                ear = lambda s=s, sxs=sxs: _ellipse(ctx, s * 70 + eo, -80 + fy * 0.5, 13 * sxs, 21)
                _fs(ctx, ear, DA, lw)
                ctx.set_source_rgba(*_c(DA_SAU)); ctx.set_line_width(2.4)
                ctx.move_to(s * 70 + eo, -92); ctx.curve_to(s * (70 + 7 * sxs) + eo, -86, s * (70 + 6 * sxs) + eo, -72, s * 69 + eo, -68); ctx.stroke()
        _fs(ctx, face, DA, lw)
        _bong(ctx, face, lambda: _ellipse(ctx, 78 + fx * 0.6, -70, 36, 130), DA_TOI, 0.5)
        _bong(ctx, face, lambda: _ellipse(ctx, fx * 0.4, -134, 80, 20), DA_TOI, 0.45)
        # má hồng
        for s in (-1, 1):
            g = cairo.RadialGradient(s * 45 + fx, -50 + fy, 0, s * 45 + fx, -50 + fy, 17)
            g.add_color_stop_rgba(0, *_c(MA_HONG, 0.42 if self.nu else 0.22)); g.add_color_stop_rgba(1, *_c(MA_HONG, 0))
            ctx.set_source(g); _ellipse(ctx, s * 45 + fx, -50 + fy, 20, 12); ctx.fill()
        # mũi
        nx, ny = fx * 1.35, -58 + fy
        ctx.set_source_rgba(*_c(DA_SAU)); ctx.set_line_width(lw * 0.62); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(nx + 2, ny - 12); ctx.curve_to(nx + 6, ny - 4, nx + 6, ny + 2, nx - 2, ny + 2); ctx.stroke()
        self._ve_mieng(ctx, fx * 1.1, -30 + fy * 0.9, P)
        # mắt
        rx, ry = (17.0, 16.5) if self.nu else (15.5, 14.5)
        ex_, ey_ = (30.0, -82.0) if self.nu else (29.0, -84.0)
        for s in (-1, 1):
            k = 1 - 0.16 * max(0.0, s * turn)
            self._ve_mat(ctx, s * ex_ + fx, ey_ + fy, rx * k, ry, P["lx"], P["ly"], P["blink"], s)
        # lông mày
        br, bq = P["brow"], P["brow_q"]
        ctx.set_source_rgba(*_c(TOC)); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_width(lw * (1.05 if self.nu else 1.45))
        by = (-113.0 if self.nu else -111.0) + fy - br * 6
        for s in (-1, 1):
            inner = by + 2 - bq * 5 * (1 if s * self.huong > 0 else 0.3)
            ctx.move_to(s * 13 + fx, inner)
            ctx.curve_to(s * 24 + fx, by - 7, s * 38 + fx, by - 7, s * 46 + fx, by + 1)
            ctx.stroke()
        # tóc trước
        o = fx * 0.45
        if self.nu:
            for s in (-1, 1):
                _fs(ctx, lambda s=s: self._toc_mai_han(ctx, s, o), TOC, lw)
            hair = lambda: self._toc_truoc_han(ctx, o)
        else:
            hair = lambda: self._toc_truoc_minh(ctx, o)
        _fs(ctx, hair, TOC, lw)
        ctx.save(); ctx.new_path(); hair(); ctx.clip()
        ctx.set_source_rgba(*_c(TOC_SANG, 0.75)); ctx.set_line_width(7)
        ctx.move_to(-46 + o, -184); ctx.curve_to(-26 + o, -198, 2 + o, -200, 24 + o, -194); ctx.stroke()
        ctx.set_line_width(4); ctx.move_to(34 + o, -190); ctx.curve_to(42 + o, -186, 48 + o, -182, 52 + o, -176); ctx.stroke()
        ctx.restore()
        if self.nu:   # kẹp tóc cam bên phải (trái màn hình)
            ctx.save(); ctx.translate(-50 + o, -146); ctx.rotate(-0.55)
            clip_b = lambda: self._rrect(ctx, -19, -6, 38, 12, 6)
            _fs(ctx, clip_b, KEP_TOC, lw * 0.75)
            ctx.set_source_rgba(1, 1, 1, 0.8); ctx.set_line_width(2.2); ctx.move_to(-11, -2); ctx.line_to(6, -2); ctx.stroke()
            ctx.restore()

    # ---------------- vẽ toàn thân
    def draw(self, ctx, P):
        lw = self.lw
        ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        si, so = self.huong, -self.huong
        gi = self._tay(P, "i", si); go = self._tay(P, "o", so)
        gL, gR = (gi, go) if si < 0 else (go, gi)
        px, py = P["hip"], -490.0 + P["bob"]

        def upper():
            ctx.translate(px, py); ctx.rotate(math.radians(P["lean"]))
            ctx.scale(1.0, 1.0 + 0.010 * P["breath"])

        def head_tf():
            ctx.translate(0, -332.0); ctx.rotate(math.radians(P["tilt"])); ctx.translate(0, P["nod"] * 1.5)

        # sau lưng: ba lô, tóc sau
        ctx.save(); upper(); self._than_ba_lo(ctx)
        if self.nu:
            ctx.save(); head_tf(); _fs(ctx, lambda: self._toc_sau_han(ctx), TOC, lw); ctx.restore()
        ctx.restore()
        self._ve_chan(ctx, P)
        ctx.save(); upper()
        # cổ
        neck = lambda: (ctx.move_to(-21, -352), ctx.line_to(21, -352), ctx.line_to(23, -300), ctx.line_to(-23, -300), ctx.close_path())
        _fs(ctx, neck, DA, lw)
        _bong(ctx, neck, lambda: _ellipse(ctx, 0, -336, 30, 16), DA_TOI, 0.9)
        self._ve_than(ctx, P, gL, gR)
        ctx.restore()
        if self.nu:
            self._ve_vay(ctx, P)
        ctx.save(); upper()
        self._quai_ba_lo(ctx)
        ctx.save(); head_tf(); self._ve_dau(ctx, P); ctx.restore()
        # tay nào giơ lên trước mặt thì vẽ sau cùng
        order = sorted((gL, gR), key=lambda g: g["W"][1] < g["E"][1])
        for g in order:
            self._ve_tay(ctx, g)
        ctx.restore()


# ------------------------------------------------------------------ tư thế & động tác
ARM_KEYS = ("tx", "ty", "hx", "hy", "fol", "idx", "oth", "spr", "hs", "fore", "wr", "hwd", "fs")
ARM_NGHI = dict(tx=16.0, ty=300.0, hx=0.0, hy=1.0, fol=1.0, idx=0.6, oth=0.55, spr=0.0, hs=1.0, fore=0.0, wr=0.0, hwd=0.78, fs=0.0)


def _arm(pre, **kw):
    d = dict(ARM_NGHI, hwd=1.0)
    d.update(kw)
    return {pre + k: v for k, v in d.items()}


CU_CHI = {
    # người nói
    "noi":           dict(**_arm("i", tx=78, ty=196, hx=0.8, hy=-0.25, fol=0.0, idx=0.9, oth=0.85, spr=0.3, fs=0.55)),
    "trinh_bay":     dict(**_arm("i", tx=182, ty=150, hx=1.0, hy=-0.3, fol=0.0, idx=1, oth=1, spr=0.35),
                          turn_rel=0.22, lx_rel=0.5, smile=0.85, brow=0.3),
    "hai_tay":       dict(**_arm("i", tx=150, ty=172, hx=1.0, hy=-0.25, fol=0.0, idx=1, oth=1, spr=0.35),
                          **_arm("o", tx=150, ty=172, hx=1.0, hy=-0.25, fol=0.0, idx=1, oth=1, spr=0.35),
                          smile=0.9, brow=0.45, turn=0.0, lx=0.0),
    "hao_hung":      dict(**_arm("i", tx=118, ty=70, hx=0.45, hy=-1.0, fol=0.0, idx=1, oth=1, spr=0.85),
                          **_arm("o", tx=118, ty=70, hx=0.45, hy=-1.0, fol=0.0, idx=1, oth=1, spr=0.85),
                          smile=1.0, brow=0.9, turn=0.0, lx=0.0),
    "chi_ben":       dict(**_arm("i", tx=212, ty=-82, hx=1.0, hy=-0.55, fol=0.0, idx=1, oth=0.0, spr=0.0),
                          turn_rel=0.30, lx_rel=1.0, ly=-0.6, brow=0.55, smile=0.7),
    "chi_nguoi_xem": dict(**_arm("i", tx=34, ty=118, hx=0.15, hy=-1.0, fol=0.0, idx=1, oth=0.0, spr=0.0, fore=1.0, hs=1.18, fs=0.75),
                          turn=0.0, lx=0.0, ly=0.0, brow=0.65, smile=0.75),
    "suy_nghi":      dict(**_arm("i", tx=-80, ty=26, hx=-0.22, hy=-1.0, fol=0.0, idx=0.55, oth=0.15, spr=0.0),
                          tilt_rel=-5.0, lx_rel=-0.4, ly=-0.75, brow_q=1.0, brow=0.2, smile=0.25),
    "suyt":          dict(**_arm("i", tx=-84, ty=-2, hx=0.0, hy=-1.0, fol=0.0, idx=1, oth=0.0, spr=0.0),
                          mr=1.0, brow=0.45, turn=0.0, lx=0.0, smile=0.2),
    "vay_tay":       dict(**_arm("o", tx=150, ty=-236, hx=0.12, hy=-1.0, fol=0.0, idx=1, oth=1, spr=1.0),
                          smile=1.0, brow=0.5, turn=0.0, lx=0.0),
    "nghieng_dau":   dict(**_arm("i", tx=86, ty=188, hx=0.85, hy=-0.55, fol=0.0, idx=1, oth=1, spr=0.5, fs=0.55),
                          tilt_rel=7.0, brow_q=1.0, brow=0.35, smile=0.5, turn_rel=0.15, lx_rel=0.4),
    # người nghe
    "nghe":          dict(turn_rel=0.42, lx_rel=0.85, ly=0.05, smile=0.62, tilt_rel=2.5),
    "nhin_theo":     dict(turn_rel=0.32, lx_rel=1.0, ly=-0.6, brow=0.4, smile=0.6),
    "nhin_camera":   dict(turn=0.0, lx=0.0, ly=0.0, smile=0.6),
    "nghe_giua":     dict(turn_rel=0.18, lx_rel=0.45, smile=0.55),
    "nhin_ban":      dict(turn_rel=0.34, lx_rel=0.85),
}

_K_VIEWER = ("dừng hình", "hỏi bạn", "thử thách", "bình luận", "các bạn", "bạn có biết", "bạn nghĩ", "bạn đoán", "theo bạn")


def chon_cu_chi(text, line_idx=0):
    """Chọn động tác cho người nói theo nội dung câu."""
    t = unicodedata.normalize("NFC", text or "").lower().strip()
    h = int(hashlib.md5(t.encode()).hexdigest()[:6], 16)
    if any(k in t for k in ("xin chào", "chào các", "chào cả", "tạm biệt", "hẹn gặp")):
        return "vay_tay"
    if any(k in t for k in _K_VIEWER):
        return "chi_nguoi_xem"
    if "suỵt" in t:
        return "suyt"
    if any(k in t for k in ("kìa", "nhìn xem", "ở đằng", "phía xa")):
        return "chi_ben"
    if "?" in t:
        if any(k in t for k in ("vì sao", "tại sao", "nhỉ", "đoán", "liệu", "thế nào", "sao lại", "làm sao")):
            return "suy_nghi"
        return "nghieng_dau"
    if t.startswith(("oa", "ồ", "wow", "trời", "ôi")) or "quá!" in t:
        return "hao_hung"
    if any(k in t for k in ("đây là", "đó là", "đây chính là")):
        return "trinh_bay"
    if "nhé" in t or "đi thôi" in t or "nào!" in t:
        return "trinh_bay" if h % 3 else "hai_tay"
    if "!" in t:
        return ("hai_tay", "trinh_bay", "hao_hung")[h % 3]
    return "noi"


def phan_tich_giong(wav, fps, n, offset=AUDIO_OFFSET):
    """Biên độ giọng (0..1) và độ tròn môi (0..1) cho từng khung; khung i ↔ thời điểm i/fps − offset trong WAV."""
    env = np.zeros(n, np.float32)
    rnd = np.zeros(n, np.float32)
    if not wav or not os.path.exists(wav):
        return env, rnd
    sr = 16000
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", wav, "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"],
                         capture_output=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    hop = sr / fps
    win = int(hop * 1.5)
    hann = np.hanning(win).astype(np.float32)
    freqs = np.fft.rfftfreq(win, 1 / sr)
    band = (freqs > 80) & (freqs < 4000)
    cen = np.zeros(n, np.float32)
    for i in range(n):
        s0 = int((i / fps - offset) * sr - (win - hop) / 2)
        if s0 + win <= 0 or s0 >= len(a):
            continue
        seg = a[max(s0, 0): s0 + win]
        if len(seg) < 32:
            continue
        env[i] = np.sqrt((seg ** 2).mean())
        sp = np.abs(np.fft.rfft(np.pad(seg, (0, win - len(seg))) * hann))[band]
        cen[i] = (sp * freqs[band]).sum() / max(sp.sum(), 1e-6)
    voiced = env > 1e-3
    ref = np.percentile(env[voiced], 92) if voiced.sum() > 10 else max(float(env.max()), 1e-4)
    e = np.clip(env / max(ref, 1e-4), 0, 1.3)
    e = np.clip((e - 0.10) / 0.85, 0, 1)
    rnd = np.clip((1450 - cen) / 850, 0, 1) * (e > 0.15)
    return e.astype(np.float32), rnd.astype(np.float32)


def _muot(x, up=0.65, down=0.38):
    y = np.zeros_like(x)
    v = 0.0
    for i, xi in enumerate(x):
        v += (xi - v) * (up if xi > v else down)
        y[i] = v
    return y


class KeHoach:
    """Lịch diễn của từng nhân vật trong cảnh: động tác theo câu, phản ứng người nghe, nháy mắt, liếc mắt."""

    def __init__(self, sc, chars, n, fps, offset, seed):
        self.fps, self.n = fps, n
        self.chars = chars
        names = [c.ten for c in chars]
        env, rnd = phan_tich_giong(sc.get("wav"), fps, n, offset)
        self.env = _muot(env, 0.5, 0.25)                       # nhịp cho đầu / tay
        self.mo = np.clip(_muot(env, 0.7, 0.42) * 1.12, 0, 1)  # độ mở miệng
        self.mr = _muot(rnd, 0.4, 0.3)
        self.speak = np.full(n, -1, np.int32)
        self.segs = [[] for _ in chars]
        self.nods = [[] for _ in chars]
        lines = sc.get("loi") or []
        bounds = sc.get("bounds") or []
        if not bounds and lines and sc.get("wav"):
            bounds = [(0.0, n / fps - offset)] if len(lines) == 1 else []
        for j, ((a, b), ln) in enumerate(zip(bounds, lines)):
            a, b = a + offset, b + offset
            sp, text = ln[0], ln[1] if len(ln) > 1 else ""
            dur = max(b - a, 0.3)
            if sp in names:
                k = names.index(sp)
                self.speak[max(0, int(a * fps)): min(n, int(math.ceil(b * fps)) + 1)] = k
                g = chon_cu_chi(text, j)
                end = a + min(dur, 2.3) if g == "vay_tay" else b
                prev = self.segs[k][-1] if self.segs[k] else None
                if prev and prev["g"] == g and a - prev["b"] < 0.7 and g != "vay_tay":
                    prev["b"] = end
                else:
                    self.segs[k].append(dict(a=a, b=end, g=g, line=j))
                tl = unicodedata.normalize("NFC", text).lower()
                if tl.startswith("cậu") or " cậu " in tl or "tớ" in tl.split()[:2]:
                    self.segs[k].append(dict(a=a, b=a + min(dur * 0.5, 1.8), g="nhin_ban", line=j))
                for o in range(len(chars)):
                    if o == k:
                        continue
                    lg = "nhin_theo" if g == "chi_ben" else "nhin_camera" if g in ("chi_nguoi_xem", "suyt") else "nghe"
                    self.segs[o].append(dict(a=a, b=b, g=lg, line=j))
                    self.nods[o] += [a + dur * 0.45, a + dur * 0.88] if dur > 1.8 else [a + dur * 0.7]
            else:
                for o in range(len(chars)):
                    self.segs[o].append(dict(a=a, b=b, g="nghe_giua", line=j))
                    self.nods[o].append(a + dur * 0.6)
        for s in self.segs:
            s.sort(key=lambda d: d["a"])
        # ngẫu nhiên riêng cho từng nhân vật
        self.rp = []
        T = n / fps + 1
        for c, ch in enumerate(chars):
            rng = np.random.default_rng(seed * 31 + c * 7 + 3)
            blinks, t = [], rng.uniform(0.4, 1.8)
            while t < T:
                blinks.append(t)
                if rng.random() < 0.15:
                    blinks.append(t + 0.28)
                t += rng.uniform(2.3, 4.8)
            sacc, t = [], 0.0
            while t < T:
                sacc.append((t, rng.uniform(-0.25, 0.25), rng.uniform(-0.12, 0.12)))
                t += rng.uniform(1.2, 2.8)
            self.rp.append(dict(blinks=blinks, sacc=sacc, ph=rng.uniform(0, 2 * PI, 12),
                                pb=rng.uniform(3.4, 4.2), pw=rng.uniform(6.5, 9.0)))

    def _w(self, t, s):
        g = s["g"]
        lead, rin, rout = (0.22, 0.38, 0.45) if g not in ("nghe", "nghe_giua", "nhin_theo", "nhin_camera", "nhin_ban") else (0.0, 0.3, 0.5)
        return _ss((t - (s["a"] - lead)) / rin) * (1 - _ss((t - s["b"]) / rout))

    def pose(self, c, t, i):
        ch = self.chars[c]
        hg = ch.huong
        r = self.rp[c]
        ph = r["ph"]
        br = math.sin(2 * PI * t / r["pb"] + ph[0])
        ws = math.sin(2 * PI * t / r["pw"] + ph[1])
        lx = ly = 0.0
        prev = None
        for (ts, ax, ay) in r["sacc"]:   # liếc mắt: chuyển nhanh rồi giữ
            if ts > t:
                break
            k = _ss((t - ts) / 0.09)
            lx, ly = (_lerp(prev[0], ax, k), _lerp(prev[1], ay, k)) if prev else (ax, ay)
            prev = (lx, ly)
        P = dict(hip=6.5 * ws, bob=-1.5 * abs(ws), lean=-0.9 * ws + 0.35 * math.sin(2 * PI * t / 5.1 + ph[2]),
                 breath=br, sway=-4.0 * ws,
                 tilt=1.3 * math.sin(2 * PI * t / 5.3 + ph[3]) + 0.6 * math.sin(2 * PI * t / 2.9 + ph[4]) + hg * 1.2,
                 nod=0.5 * math.sin(2 * PI * t / 3.7 + ph[5]),
                 turn=hg * 0.10 + 0.04 * math.sin(2 * PI * t / 6.1 + ph[6]),
                 lx=hg * 0.15 + lx, ly=0.04 + ly, blink=0.0, brow=0.0, brow_q=0.0, smile=0.55, mo=0.0, mr=0.0)
        for pre in ("i", "o"):
            for k, v in ARM_NGHI.items():
                P[pre + k] = v
            P[pre + "tx"] += 2.5 * math.sin(2 * PI * t / 4.7 + ph[7] + (pre == "o"))
            P[pre + "ty"] += 3.0 * br
        env = float(self.env[i]) if i < self.n else 0.0
        for s in self.segs[c]:
            w = self._w(t, s)
            if w <= 1e-3:
                continue
            G = dict(CU_CHI[s["g"]])
            tau = t - s["a"]
            g = s["g"]
            if g == "vay_tay":
                G["otx"] += 16 * math.sin(2 * PI * 2.1 * tau)
                G["ohx"] += 0.45 * math.sin(2 * PI * 2.1 * tau)
            elif g == "noi":
                pre = "i" if (s["line"] % 2 == 0) else "o"
                if pre == "o":
                    G = {("o" + k[1:]) if k[0] == "i" else k: v for k, v in G.items()}
                G[pre + "ty"] -= 20 * env
                G[pre + "tx"] += 8 * env
                G[pre + "hy"] -= 0.35 * env
            elif g == "trinh_bay":
                G["itx"] += 6 * math.sin(2 * PI * tau / 2.4)
                G["ity"] -= 10 * env
            elif g == "hai_tay":
                G["ity"] -= 8 * env; G["oty"] -= 8 * env
            elif g == "chi_nguoi_xem":
                G["ihs"] += 0.06 * math.sin(2 * PI * tau / 0.9)
            elif g == "suy_nghi":
                G["tilt_rel"] += 1.5 * math.sin(2 * PI * tau / 1.7)
            for k in list(G.keys()):
                if k.endswith("_rel"):
                    G[k[:-4]] = hg * G.pop(k)
            for k, v in G.items():
                P[k] = _lerp(P[k], v, w)
        for tn in self.nods[c]:   # gật đầu của người nghe
            u = (t - tn) / 0.5
            if 0 <= u <= 1:
                P["nod"] += 2.4 * math.sin(PI * u) * (1 - 0.3 * u)
        if 0 <= i < self.n and self.speak[i] == c:
            P["mo"] = float(self.mo[i])
            P["mr"] = max(P["mr"], float(self.mr[i]))
            P["nod"] += 1.6 * env - 0.4
            P["brow"] += 0.25 * env
        for tb in r["blinks"]:
            u = (t - tb) / 0.14
            if 0 <= u <= 1:
                P["blink"] = max(P["blink"], _cl(1.25 - abs(2 * u - 1) * 1.25) ** 0.5)
        return P


# ------------------------------------------------------------------ nền vẽ bằng code
def chon_nen(sc):
    if sc.get("nen"):
        return sc["nen"]
    h = unicodedata.normalize("NFC", sc.get("hinh") or "").lower()
    if "phòng thu" in h or "studio" in h:
        return "studio"
    if "bản đồ" in h:
        return "ban_do"
    if any(k in h for k in ("di tích", "đình", "tượng", "đền", "chùa", "lăng", "cổng thành", "thành cổ", "thành đất")):
        return "di_tich"
    if any(k in h for k in ("sông", "bờ sông", "bến", "biển", "hồ ", "đầm")):
        return "song"
    if any(k in h for k in ("lớp học", "bảng đen", "phòng học", "bàn học")):
        return "lop_hoc"
    if any(k in h for k in ("thư viện", "kệ sách", "bảo tàng", "phòng")):
        return "thu_vien"
    return "studio"


def _grad(x0, y0, x1, y1, stops):
    g = cairo.LinearGradient(x0, y0, x1, y1)
    for o, col in stops:
        g.add_color_stop_rgba(o, *_c(col[:3], col[3] if len(col) > 3 else 1.0))
    return g


def _glow(c, x, y, r, col, a):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, *_c(col, a)); g.add_color_stop_rgba(1, *_c(col, 0))
    c.set_source(g); c.new_path(); c.arc(x, y, r, 0, 2 * PI); c.fill()


def _may(c, x, y, s, col=(255, 255, 255), a=0.95):
    c.save()
    c.rectangle(x - 4 * s, y - 4 * s, 8 * s, 4.3 * s); c.clip()
    c.set_source_rgba(*_c(col, a)); c.new_path()
    for dx, dy, r in ((0, 0, 1.0), (-1.15, 0.3, 0.72), (1.2, 0.28, 0.78), (-0.55, -0.42, 0.78), (0.6, -0.36, 0.82), (2.0, 0.42, 0.5)):
        c.new_sub_path(); c.arc(x + dx * s, y + dy * s, r * s, 0, 2 * PI)
    c.fill()
    c.restore()


def _cong_kin(c, pts):
    """Đường cong kín mượt (Catmull-Rom) qua các điểm."""
    m = len(pts)
    c.move_to(*pts[0])
    for k in range(m):
        p0, p1, p2, p3 = pts[k - 1], pts[k], pts[(k + 1) % m], pts[(k + 2) % m]
        c.curve_to(p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6,
                   p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6, p2[0], p2[1])
    c.close_path()


def _tan_cay(c, x, y, r, col, rng, k=7):
    c.set_source_rgba(*_c(col)); c.new_path()
    for j in range(k):
        a = 2 * PI * j / k + rng.uniform(-0.3, 0.3)
        c.new_sub_path(); c.arc(x + math.cos(a) * r * 0.62, y + math.sin(a) * r * 0.42, r * rng.uniform(0.42, 0.6), 0, 2 * PI)
    c.new_sub_path(); c.arc(x, y, r * 0.66, 0, 2 * PI)
    c.fill()


def _dua(c, x, y, h, col, lean=0.1):
    """Cây dừa xa (bóng): thân cong + tàu lá."""
    c.set_source_rgba(*_c(col)); c.set_line_cap(cairo.LINE_CAP_ROUND)
    tx, ty = x + lean * h, y - h
    c.set_line_width(h * 0.05); c.move_to(x, y); c.curve_to(x + lean * h * 0.2, y - h * 0.5, tx - lean * h * 0.2, ty + h * 0.3, tx, ty); c.stroke()
    for a in (-2.7, -2.2, -1.75, -1.35, -0.95, -0.45, 0.05):
        L = h * 0.42
        ex, ey = tx + math.cos(a) * L, ty + math.sin(a) * L * 0.6 + L * 0.25
        c.set_line_width(h * 0.035)
        c.move_to(tx, ty); c.curve_to(tx + math.cos(a) * L * 0.5, ty + math.sin(a) * L * 0.6 - L * 0.12, ex, ey - L * 0.1, ex, ey); c.stroke()


def _mai(c, cx, ye, hw, yr, ht, lift, col, tile, lw=3.0):
    """Mái ngói cong, đầu đao vểnh (dáng chung của đình làng, không mô phỏng công trình cụ thể)."""
    def p():
        c.move_to(cx - hw - lift * 1.3, ye - lift * 1.1)
        c.curve_to(cx - hw + lift * 0.4, ye + 3, cx - hw * 0.55, ye + 8, cx, ye + 8)
        c.curve_to(cx + hw * 0.55, ye + 8, cx + hw - lift * 0.4, ye + 3, cx + hw + lift * 1.3, ye - lift * 1.1)
        c.curve_to(cx + hw - lift * 0.3, ye - lift * 0.9, cx + ht + (hw - ht) * 0.35, yr + (ye - yr) * 0.45, cx + ht, yr)
        c.line_to(cx - ht, yr)
        c.curve_to(cx - ht - (hw - ht) * 0.35, yr + (ye - yr) * 0.45, cx - hw + lift * 0.3, ye - lift * 0.9, cx - hw - lift * 1.3, ye - lift * 1.1)
        c.close_path()
    c.new_path(); p(); c.set_source_rgba(*_c(col)); c.fill()
    c.save(); c.new_path(); p(); c.clip()
    c.set_source_rgba(*_c(tile, 0.55)); c.set_line_width(lw)
    step = max(10.0, hw / 22)
    xx = cx - hw - lift * 1.5
    while xx < cx + hw + lift * 1.5:
        f = (xx - cx) / (hw + lift)
        c.move_to(cx + (xx - cx) * (ht / hw) * 1.05, yr); c.line_to(xx + f * lift * 0.6, ye + 10); c.stroke()
        xx += step
    c.set_source_rgba(*_c(tile, 0.9)); c.rectangle(cx - hw - 80, ye - 6, 2 * hw + 160, 16); c.fill()
    c.restore()
    c.new_path(); p(); c.set_source_rgba(*_c((70, 46, 38))); c.set_line_width(lw); c.stroke()


class Nen:
    """Nền nhiều lớp (vẽ một lần), mỗi lớp trôi theo máy quay với hệ số thị sai riêng."""
    M = 0.07

    def __init__(self, loai, W, H, seed=0, anh=None):
        self.W, self.H, self.loai = W, H, loai
        self.rng = np.random.default_rng(seed + 11)
        self.layers = []
        self.dong = []          # hàm vẽ chuyển động mỗi khung: (p, fn(ctx, t))
        self.anh = anh
        if anh and os.path.exists(anh):
            self._anh()
        else:
            getattr(self, "_" + loai, self._studio)()

    def _anh(self):
        """Nền là ảnh chụp thật của địa điểm (ví dụ di tích ngày nay): phủ kín khung, mờ nhẹ cho nhân vật nổi."""
        from PIL import Image, ImageFilter, ImageEnhance
        W, H = self.W, self.H
        mx, my = int(W * self.M), int(H * self.M)
        w, h = W + 2 * mx, H + 2 * my
        im = Image.open(self.anh).convert("RGB")
        k = max(w / im.width, h / im.height)
        im = im.resize((int(im.width * k) + 1, int(im.height * k) + 1), Image.LANCZOS)
        x0 = (im.width - w) // 2; y0 = max(0, int((im.height - h) * 0.35))
        im = im.crop((x0, y0, x0 + w, y0 + h)).filter(ImageFilter.GaussianBlur(max(2, W // 640)))
        im = ImageEnhance.Color(im).enhance(0.85)
        a = np.asarray(im, dtype=np.uint8)
        buf = np.empty((h, w, 4), np.uint8); buf[..., 0] = a[..., 2]; buf[..., 1] = a[..., 1]; buf[..., 2] = a[..., 0]; buf[..., 3] = 255
        surf = cairo.ImageSurface.create_for_data(memoryview(buf), cairo.FORMAT_RGB24, w, h, w * 4)
        self._anh_buf = buf
        def ve(c, W_, H_):
            c.set_source_surface(surf, -mx, -my); c.paint()
            g = _grad(0, H_ * 0.62, 0, H_ * 1.05, [(0, (0, 0, 0, 0)), (1, (0.08, 0.06, 0.04, 0.45))])
            c.set_source(g); c.rectangle(-mx, -my, w, h); c.fill()
        self._lop(0.35, ve, opaque=True)

    def _lop(self, p, fn, y0=0.0, y1=1.0, opaque=False):
        W, H = self.W, self.H
        mx, my = int(W * self.M), int(H * self.M)
        Y0 = int(y0 * H) if y0 > 0 else -my
        Y1 = int(y1 * H) if y1 < 1 else H + my
        w, h = W + 2 * mx, Y1 - Y0
        s = cairo.ImageSurface(cairo.FORMAT_RGB24 if opaque else cairo.FORMAT_ARGB32, w, h)
        c = cairo.Context(s); c.translate(mx, -Y0)
        c.set_line_join(cairo.LINE_JOIN_ROUND)
        fn(c, W, H)
        s.flush()
        self.layers.append((s, p, -mx, Y0, w, h, opaque))

    @staticmethod
    def tf(ctx, cam, p):
        cx, cy, z, Cx, Cy = cam
        zp = 1 + (z - 1) * p
        ctx.translate(Cx, Cy); ctx.scale(zp, zp); ctx.translate(-Cx - p * cx, -Cy - p * cy)

    def ve(self, ctx, t, cam):
        for s, p, X0, Y0, w, h, opaque in self.layers:
            ctx.save()
            self.tf(ctx, cam, p)
            ctx.set_source_surface(s, X0, Y0)
            pat = ctx.get_source(); pat.set_filter(cairo.FILTER_BILINEAR)
            if opaque:
                pat.set_extend(cairo.EXTEND_PAD); ctx.set_operator(cairo.OPERATOR_SOURCE); ctx.paint()
                ctx.set_operator(cairo.OPERATOR_OVER)
            else:
                ctx.rectangle(X0, Y0, w, h); ctx.fill()
            ctx.restore()
            for p2, fn in self.dong:
                if p2 == p:
                    ctx.save(); self.tf(ctx, cam, p); fn(ctx, t); ctx.restore()

    # ---- các bụi sáng trôi (dùng cho phòng)
    def _bui(self, p, x0, x1, y0, y1, k=14, col=(255, 248, 225), a=0.35):
        W, H = self.W, self.H
        rng = self.rng
        pts = [(rng.uniform(x0, x1) * W, rng.uniform(y0, y1) * H, rng.uniform(2, 5) * H / 1080, rng.uniform(6, 16) * H / 1080,
                rng.uniform(0, 2 * PI)) for _ in range(k)]
        span = (y1 - y0) * H

        def fn(c, t):
            for x, y, r, v, ph in pts:
                yy = y0 * H + ((y - y0 * H - v * t) % span)
                xx = x + 14 * H / 1080 * math.sin(t * 0.6 + ph)
                al = a * (0.5 + 0.5 * math.sin(t * 1.3 + ph))
                c.set_source_rgba(*_c(col, al)); c.new_path(); c.arc(xx, yy, r, 0, 2 * PI); c.fill()
        self.dong.append((p, fn))

    # ---- mặc định: phòng thu nền dịu
    def _studio(self):
        rng = self.rng

        def wall(c, W, H):
            c.set_source(_grad(0, 0, 0, H, [(0, (255, 241, 224)), (0.7, (250, 224, 192)), (1, (244, 210, 172))])); c.paint()
            _glow(c, W * 0.16, H * 0.26, H * 0.55, (255, 186, 120), 0.35)
            _glow(c, W * 0.78, H * 0.62, H * 0.5, (150, 196, 210), 0.18)
            c.set_source_rgba(*_c(CAM, 0.16)); c.set_line_width(3 * H / 1080)
            for r in (0.42, 0.5, 0.58):
                c.new_path(); c.arc(W * 0.5, H * 1.05, H * r * 1.6, PI * 1.08, PI * 1.92); c.stroke()
            y = H * 0.40   # trục thời gian mờ (mô-típ lịch sử)
            c.set_source_rgba(*_c((200, 120, 60), 0.22)); c.set_line_width(4 * H / 1080)
            c.move_to(-W * 0.1, y); c.line_to(W * 1.1, y); c.stroke()
            for k in range(-1, 14):
                x = W * (0.04 + k * 0.083)
                c.new_path(); c.arc(x, y, (10 if k % 3 else 15) * H / 1080, 0, 2 * PI)
                c.set_source_rgba(*_c((255, 248, 238), 0.9)); c.fill_preserve()
                c.set_source_rgba(*_c((200, 120, 60), 0.35)); c.stroke()
        self._lop(0.3, wall, opaque=True)

        def floor(c, W, H):
            y = H * 0.72
            c.set_source(_grad(0, y, 0, H * 1.1, [(0, (238, 206, 170)), (1, (226, 186, 146))]))
            c.rectangle(-W, y, 3 * W, H); c.fill()
            c.set_source_rgba(*_c((255, 250, 240), 0.55)); c.rectangle(-W, y - 3, 3 * W, 5); c.fill()
            g = cairo.RadialGradient(W * 0.5, H * 0.86, 0, W * 0.5, H * 0.86, W * 0.42)
            g.add_color_stop_rgba(0, *_c((255, 246, 230), 0.6)); g.add_color_stop_rgba(1, *_c((255, 246, 230), 0))
            c.save(); c.translate(W * 0.5, H * 0.86); c.scale(1, 0.22); c.translate(-W * 0.5, -H * 0.86)
            c.set_source(g); c.arc(W * 0.5, H * 0.86, W * 0.42, 0, 2 * PI); c.fill(); c.restore()
        self._lop(1.0, floor, y0=0.68)
        self._bui(0.8, 0.05, 0.75, 0.15, 0.65)

    # ---- bờ sông
    def _song(self):
        rng = self.rng

        def sky(c, W, H):
            c.set_source(_grad(0, 0, 0, H * 0.56, [(0, (128, 186, 224)), (0.65, (214, 220, 214)), (1, (255, 214, 172))])); c.paint()
            _glow(c, W * 0.2, H * 0.36, H * 0.42, (255, 236, 196), 0.95)
            c.set_source_rgba(*_c((255, 246, 222))); c.new_path(); c.arc(W * 0.2, H * 0.36, H * 0.045, 0, 2 * PI); c.fill()
            for x, y, s in ((0.08, 0.14, 0.05), (0.42, 0.11, 0.04), (0.6, 0.24, 0.032), (0.3, 0.27, 0.025)):
                _may(c, W * x, H * y, min(W, H) * s)
        self._lop(0.18, sky, y1=0.62, opaque=True)

        def far(c, W, H):
            yb = H * 0.50
            c.set_source_rgba(*_c((150, 182, 186))); c.move_to(-W * 0.1, yb)
            for k in range(13):
                x = -W * 0.1 + k * W * 0.11
                c.curve_to(x + W * 0.03, yb - H * rng.uniform(0.03, 0.09), x + W * 0.08, yb - H * rng.uniform(0.02, 0.08), x + W * 0.11, yb - H * 0.01)
            c.line_to(W * 1.2, yb + 20); c.line_to(-W * 0.1, yb + 20); c.close_path(); c.fill()
            for k in range(28):
                x = -W * 0.08 + k * W * 0.045 + rng.uniform(-10, 10)
                _tan_cay(c, x, yb - H * 0.012, H * rng.uniform(0.018, 0.03), (96, 138, 112), rng, 5)
            c.set_source_rgba(*_c((96, 138, 112))); c.rectangle(-W, yb - H * 0.012, 3 * W, H * 0.03); c.fill()
            for x in (0.04, 0.09, 0.27, 0.56, 0.86, 0.93):
                _dua(c, W * x, yb + H * 0.005, H * rng.uniform(0.08, 0.12), (78, 118, 96), rng.uniform(-0.15, 0.15))
        self._lop(0.42, far, y0=0.3, y1=0.6)

        def river(c, W, H):
            y0, y1 = H * 0.515, H * 0.72
            c.set_source(_grad(0, y0, 0, y1, [(0, (176, 206, 206)), (0.4, (124, 178, 194)), (1, (96, 156, 178))]))
            c.rectangle(-W, y0, 3 * W, y1 - y0 + 40); c.fill()
            c.set_source_rgba(*_c((255, 238, 200), 0.5))
            for k in range(26):
                yy = y0 + (y1 - y0) * (k / 26) ** 1.4 + 4
                ww = W * rng.uniform(0.02, 0.07) * (0.6 + yy / H)
                xx = W * (0.2 + rng.normal(0, 0.05)) if k % 2 == 0 else W * rng.uniform(-0.05, 1.05)
                c.rectangle(xx - ww / 2, yy, ww, 2.5 * H / 1080); c.fill()
            bx, by = W * 0.72, H * 0.555   # thuyền nhỏ xa
            c.set_source_rgba(*_c((70, 70, 72)))
            c.move_to(bx - 34, by); c.line_to(bx + 38, by); c.line_to(bx + 26, by + 9); c.line_to(bx - 24, by + 9); c.close_path(); c.fill()
            c.move_to(bx - 10, by); c.curve_to(bx - 8, by - 16, bx + 14, by - 16, bx + 16, by); c.close_path(); c.fill()
        self._lop(0.62, river, y0=0.48, y1=0.78)
        shim = [(rng.uniform(-0.05, 1.05), rng.uniform(0.53, 0.70), rng.uniform(0, 2 * PI), rng.uniform(0.02, 0.05)) for _ in range(16)]

        def shimmer(c, t):
            W, H = self.W, self.H
            for x, y, ph, w in shim:
                a = 0.5 * max(0.0, math.sin(t * 1.4 + ph))
                c.set_source_rgba(1, 1, 1, a); c.rectangle(W * x + 18 * math.sin(t * 0.5 + ph), H * y, W * w, 2.2 * H / 1080); c.fill()
        self.dong.append((0.62, shimmer))

        def bank(c, W, H):
            y = H * 0.70
            c.set_source_rgba(*_c((214, 194, 150))); c.move_to(-W, y + 6)
            c.curve_to(W * 0.3, y - 10, W * 0.7, y + 4, W * 2, y - 6); c.line_to(W * 2, H * 2); c.line_to(-W, H * 2); c.close_path(); c.fill()
            c.set_source(_grad(0, y, 0, H * 1.07, [(0, (162, 198, 112)), (1, (128, 170, 88))]))
            c.move_to(-W, y + 18); c.curve_to(W * 0.3, y + 4, W * 0.7, y + 18, W * 2, y + 8); c.line_to(W * 2, H * 2); c.line_to(-W, H * 2); c.close_path(); c.fill()
            c.set_source_rgba(*_c((112, 156, 80))); c.set_line_width(4 * H / 1080); c.set_line_cap(cairo.LINE_CAP_ROUND)
            for k in range(70):   # cỏ lau ven bờ, chỉ ở hai mép
                x = rng.uniform(-0.06, 0.13) if k % 2 else rng.uniform(0.87, 1.06)
                xx, yy = W * x, y + rng.uniform(10, 70) * H / 1080
                hh = rng.uniform(30, 80) * H / 1080
                c.move_to(xx, yy); c.curve_to(xx, yy - hh * 0.5, xx + rng.uniform(-12, 12), yy - hh * 0.8, xx + rng.uniform(-18, 18), yy - hh); c.stroke()
        self._lop(1.0, bank, y0=0.62)

    # ---- thư viện / lớp học
    def _thu_vien(self, lop_hoc=False):
        rng = self.rng

        def wall(c, W, H):
            c.set_source(_grad(0, 0, 0, H, [(0, (247, 234, 212)), (1, (236, 216, 188))])); c.paint()
            c.set_source_rgba(*_c((226, 204, 172), 0.45))
            for k in range(-2, 30):
                c.rectangle(W * k * 0.04, 0, 2, H); c.fill()
            yb = H * 0.56
            c.set_source_rgba(*_c((206, 166, 122))); c.rectangle(-W, yb, 3 * W, H * 0.2); c.fill()
            c.set_source_rgba(*_c((176, 132, 92))); c.rectangle(-W, yb - 8, 3 * W, 12); c.fill()
            c.set_source_rgba(*_c((176, 132, 92), 0.6)); c.set_line_width(2)
            for k in range(-2, 24):
                c.rectangle(W * (k * 0.06 + 0.01), yb + 18, W * 0.045, H * 0.12); c.stroke()
            # cửa sổ có nắng (bên trái)
            wx0, wy0, ww, wh = W * 0.04, H * 0.12, W * 0.2, H * 0.36
            c.set_source(_grad(0, wy0, 0, wy0 + wh, [(0, (170, 210, 236)), (1, (232, 240, 236))])); c.rectangle(wx0, wy0, ww, wh); c.fill()
            _may(c, wx0 + ww * 0.35, wy0 + wh * 0.35, wh * 0.08)
            c.set_source_rgba(*_c((150, 108, 74))); c.set_line_width(10 * H / 1080)
            c.rectangle(wx0, wy0, ww, wh); c.stroke()
            c.move_to(wx0 + ww / 2, wy0); c.line_to(wx0 + ww / 2, wy0 + wh); c.move_to(wx0, wy0 + wh / 2); c.line_to(wx0 + ww, wy0 + wh / 2); c.stroke()
            if lop_hoc:   # bảng xanh, phấn vẽ trục thời gian (không chữ)
                bx0, by0, bw, bh = W * 0.31, H * 0.12, W * 0.38, H * 0.34
                c.set_source_rgba(*_c((150, 108, 74))); c.rectangle(bx0 - 12, by0 - 12, bw + 24, bh + 24); c.fill()
                c.set_source(_grad(0, by0, 0, by0 + bh, [(0, (58, 98, 80)), (1, (48, 84, 68))])); c.rectangle(bx0, by0, bw, bh); c.fill()
                c.set_source_rgba(1, 1, 1, 0.55); c.set_line_width(4 * H / 1080)
                yy = by0 + bh * 0.62
                c.move_to(bx0 + bw * 0.08, yy); c.line_to(bx0 + bw * 0.9, yy); c.line_to(bx0 + bw * 0.86, yy - 10); c.move_to(bx0 + bw * 0.9, yy); c.line_to(bx0 + bw * 0.86, yy + 10); c.stroke()
                for k in range(5):
                    x = bx0 + bw * (0.15 + k * 0.17)
                    c.new_path(); c.arc(x, yy, 8 * H / 1080, 0, 2 * PI); c.stroke()
                    c.move_to(x - 22, yy - 40 - (k % 2) * 30); c.line_to(x + 22, yy - 40 - (k % 2) * 30); c.stroke()
                c.set_source_rgba(*_c((150, 108, 74))); c.rectangle(bx0 - 20, by0 + bh + 10, bw + 40, 12); c.fill()
            else:   # cửa sổ vòm giữa
                ax, ay, aw, ah = W * 0.42, H * 0.10, W * 0.16, H * 0.36
                def arch():
                    c.move_to(ax, ay + ah); c.line_to(ax, ay + aw / 2); c.arc(ax + aw / 2, ay + aw / 2, aw / 2, PI, 2 * PI)
                    c.line_to(ax + aw, ay + ah); c.close_path()
                c.new_path(); arch(); c.set_source(_grad(0, ay, 0, ay + ah, [(0, (186, 218, 238)), (1, (240, 238, 226))])); c.fill()
                c.new_path(); arch(); c.set_source_rgba(*_c((150, 108, 74))); c.set_line_width(10 * H / 1080); c.stroke()
                c.move_to(ax + aw / 2, ay); c.line_to(ax + aw / 2, ay + ah); c.stroke()
        self._lop(0.3, wall, opaque=True)
        pal = [(178, 70, 58), (60, 110, 124), (214, 160, 60), (46, 62, 102), (120, 140, 76), (226, 120, 50), (238, 226, 200), (128, 86, 120)]

        def ke_sach(c, x0, x1, y0, y1, nshelf):
            W, H = self.W, self.H
            c.set_source_rgba(*_c((146, 98, 62))); c.rectangle(x0, y0, x1 - x0, y1 - y0); c.fill()
            c.set_source_rgba(*_c((110, 70, 44))); c.rectangle(x0 + 10, y0 + 10, x1 - x0 - 20, y1 - y0 - 20); c.fill()
            sh = (y1 - y0 - 20) / nshelf
            for k in range(nshelf):
                yb = y0 + 10 + sh * (k + 1)
                x = x0 + 14
                while x < x1 - 30:
                    bw = rng.uniform(12, 26) * H / 1080; bh = sh * rng.uniform(0.55, 0.85)
                    col = pal[int(rng.integers(len(pal)))]
                    if rng.random() < 0.08 and x + bh < x1 - 20:   # sách nằm
                        c.set_source_rgba(*_c(col)); c.rectangle(x, yb - 12 - bw, bh, bw); c.fill(); x += bh + 4; continue
                    c.set_source_rgba(*_c(col)); c.rectangle(x, yb - 12 - bh, bw, bh); c.fill()
                    c.set_source_rgba(*_c((255, 255, 255), 0.25)); c.rectangle(x + 2, yb - 12 - bh * 0.8, bw - 4, 3); c.fill()
                    x += bw + rng.uniform(0, 3)
                c.set_source_rgba(*_c((160, 110, 70))); c.rectangle(x0 + 6, yb - 12, x1 - x0 - 12, 12); c.fill()

        def shelves(c, W, H):
            if lop_hoc:
                ke_sach(c, W * 0.76, W * 1.05, H * 0.30, H * 0.62, 2)
                gx, gy = W * 0.86, H * 0.255   # quả địa cầu trên kệ
                c.set_source_rgba(*_c((150, 108, 74))); c.rectangle(gx - 20, gy + 36, 40, 10); c.fill()
                c.new_path(); c.arc(gx, gy, 34 * H / 1080, 0, 2 * PI); c.set_source_rgba(*_c((110, 170, 200))); c.fill()
                c.set_source_rgba(*_c((150, 190, 110))); _ellipse(c, gx - 8, gy - 6, 14, 18); c.fill(); _ellipse(c, gx + 14, gy + 10, 9, 8); c.fill()
                # chậu cây
                px, py = W * 0.06, H * 0.70
                c.set_source_rgba(*_c((190, 110, 70))); c.move_to(px - 40, py - 70); c.line_to(px + 40, py - 70); c.line_to(px + 30, py); c.line_to(px - 30, py); c.close_path(); c.fill()
                for k in range(9):
                    a = -PI / 2 + (k - 4) * 0.28
                    c.set_source_rgba(*_c((88, 140, 86) if k % 2 else (110, 162, 98)))
                    _ellipse(c, px + math.cos(a) * 60, py - 70 + math.sin(a) * 90, 16, 40); c.fill()
            else:
                ke_sach(c, -W * 0.05, W * 0.27, H * 0.16, H * 0.74, 4)
                ke_sach(c, W * 0.73, W * 1.05, H * 0.22, H * 0.74, 4)
        self._lop(0.55, shelves, y0=0.1, y1=0.8)

        def floor(c, W, H):
            y = H * 0.72
            c.set_source(_grad(0, y, 0, H * 1.08, [(0, (200, 154, 110)), (1, (182, 136, 96))])); c.rectangle(-W, y, 3 * W, H); c.fill()
            c.set_source_rgba(*_c((150, 106, 70), 0.9)); c.rectangle(-W, y - 4, 3 * W, 8); c.fill()
            c.set_source_rgba(*_c((160, 116, 78), 0.35)); c.set_line_width(2)
            yy, step = y + 22, 22.0
            while yy < H * 1.08:
                c.move_to(-W, yy); c.line_to(2 * W, yy); c.stroke(); step *= 1.3; yy += step
            _glow(c, W * 0.28, H * 0.85, H * 0.35, (255, 240, 200), 0.25)
        self._lop(1.0, floor, y0=0.68)
        self._bui(0.55, 0.05, 0.45, 0.12, 0.7, k=18, a=0.45)

        def beam(c, t):
            W, H = self.W, self.H
            a = 0.10 + 0.02 * math.sin(t * 0.7)
            g = _grad(W * 0.1, H * 0.12, W * 0.45, H * 0.9, [(0, (255, 244, 210, a)), (1, (255, 244, 210, 0))])
            c.set_source(g); c.move_to(W * 0.04, H * 0.12); c.line_to(W * 0.24, H * 0.12); c.line_to(W * 0.62, H * 0.9); c.line_to(W * 0.22, H * 0.9); c.close_path(); c.fill()
        self.dong.append((0.55, beam))

    def _lop_hoc(self):
        self._thu_vien(lop_hoc=True)

    # ---- di tích: sân đình, mái cong (chung chung)
    def _di_tich(self):
        rng = self.rng

        def sky(c, W, H):
            c.set_source(_grad(0, 0, 0, H * 0.6, [(0, (136, 190, 226)), (0.7, (230, 226, 210)), (1, (252, 222, 186))])); c.paint()
            _glow(c, W * 0.12, H * 0.2, H * 0.4, (255, 240, 205), 0.7)
            for x, y, s in ((0.1, 0.12, 0.045), (0.5, 0.07, 0.035), (0.66, 0.2, 0.03)):
                _may(c, W * x, H * y, min(W, H) * s)
        self._lop(0.18, sky, y1=0.62, opaque=True)

        def far(c, W, H):
            yb = H * 0.55
            for k in range(22):
                x = -W * 0.08 + k * W * 0.058
                _tan_cay(c, x, yb - H * rng.uniform(0.02, 0.07), H * rng.uniform(0.05, 0.08), (128, 160, 120), rng)
            c.set_source_rgba(*_c((128, 160, 120))); c.rectangle(-W, yb - H * 0.03, 3 * W, H * 0.2); c.fill()
        self._lop(0.4, far, y0=0.3, y1=0.66)

        def temple(c, W, H):
            cx = W * 0.5
            # cây đa lớn bên trái, cây nhỏ bên phải (tránh góc logo)
            c.set_source_rgba(*_c((96, 74, 56))); c.rectangle(W * 0.05, H * 0.30, W * 0.03, H * 0.34); c.fill()
            for (x, y, r) in ((0.02, 0.18, 0.13), (0.11, 0.13, 0.1), (0.17, 0.24, 0.09), (-0.03, 0.32, 0.08)):
                _tan_cay(c, W * x, H * y, H * r, (92, 132, 90), rng, 8)
            c.set_source_rgba(*_c((96, 74, 56))); c.rectangle(W * 0.925, H * 0.38, W * 0.02, H * 0.26); c.fill()
            for (x, y, r) in ((0.93, 0.33, 0.085), (0.99, 0.38, 0.07), (0.88, 0.38, 0.06)):
                _tan_cay(c, W * x, H * y, H * r, (100, 140, 96), rng, 7)
            # nền đá + bậc
            c.set_source_rgba(*_c((196, 186, 170))); c.rectangle(W * 0.2, H * 0.585, W * 0.6, H * 0.05); c.fill()
            c.set_source_rgba(*_c((170, 160, 146))); c.rectangle(W * 0.2, H * 0.625, W * 0.6, H * 0.01); c.fill()
            for k in range(3):
                c.set_source_rgba(*_c((206 - k * 8, 196 - k * 8, 180 - k * 8)))
                c.rectangle(cx - W * (0.08 + k * 0.012), H * (0.6 + k * 0.012), W * 2 * (0.08 + k * 0.012), H * 0.013); c.fill()
            # tường gỗ, cửa bức bàn
            c.set_source_rgba(*_c((150, 92, 62))); c.rectangle(W * 0.24, H * 0.43, W * 0.52, H * 0.16); c.fill()
            c.set_source_rgba(*_c((116, 66, 44), 0.8)); c.set_line_width(2)
            for k in range(11):
                x = W * (0.25 + k * 0.047)
                c.rectangle(x, H * 0.45, W * 0.04, H * 0.13); c.stroke()
                for j in range(1, 5):
                    c.move_to(x, H * (0.45 + j * 0.026)); c.line_to(x + W * 0.04, H * (0.45 + j * 0.026)); c.stroke()
            # cột
            for k in range(7):
                x = W * (0.235 + k * 0.088)
                c.set_source_rgba(*_c((122, 54, 40))); c.rectangle(x, H * 0.42, W * 0.013, H * 0.17); c.fill()
                c.set_source_rgba(*_c((90, 40, 30))); c.rectangle(x + W * 0.009, H * 0.42, W * 0.004, H * 0.17); c.fill()
                c.set_source_rgba(*_c((176, 166, 150))); c.rectangle(x - 5, H * 0.585, W * 0.013 + 10, 10); c.fill()
            # mái hai tầng, đầu đao vểnh
            _mai(c, cx, H * 0.43, W * 0.31, H * 0.30, W * 0.2, H * 0.05, (122, 82, 64), (84, 54, 44))
            c.set_source_rgba(*_c((150, 92, 62))); c.rectangle(cx - W * 0.17, H * 0.27, W * 0.34, H * 0.035); c.fill()
            _mai(c, cx, H * 0.285, W * 0.2, H * 0.19, W * 0.12, H * 0.04, (128, 86, 66), (84, 54, 44))
            c.set_source_rgba(*_c((150, 120, 96))); c.rectangle(cx - W * 0.125, H * 0.178, W * 0.25, H * 0.014); c.fill()
            c.set_source_rgba(*_c((150, 120, 96))); c.set_line_width(6 * H / 1080)
            for s in (-1, 1):   # đầu kìm cuộn tròn (cách điệu)
                c.new_path(); c.arc(cx + s * W * 0.13, H * 0.17, H * 0.016, 0, 2 * PI * 0.8); c.stroke()
            c.new_path(); c.arc(cx, H * 0.172, H * 0.012, 0, 2 * PI); c.fill()
            # đèn lồng đỏ
            for s in (-1, 1):
                lx, ly = cx + s * W * 0.15, H * 0.475
                c.set_source_rgba(*_c((80, 50, 40))); c.set_line_width(2); c.move_to(lx, H * 0.44); c.line_to(lx, ly - 18); c.stroke()
                c.set_source_rgba(*_c((206, 56, 44))); _ellipse(c, lx, ly, 16 * H / 1080, 20 * H / 1080); c.fill()
                c.set_source_rgba(*_c((240, 190, 80))); c.rectangle(lx - 8, ly + 18 * H / 1080, 16, 5); c.fill()
        self._lop(0.62, temple, y0=0.04, y1=0.68)

        def yard(c, W, H):
            y = H * 0.64
            c.set_source(_grad(0, y, 0, H * 1.08, [(0, (206, 160, 124)), (1, (192, 142, 106))])); c.rectangle(-W, y, 3 * W, H); c.fill()
            c.set_source_rgba(*_c((170, 120, 90), 0.28)); c.set_line_width(2)
            vx, vy = W * 0.5, H * 0.3
            for k in range(-14, 15):
                x = W * 0.5 + k * W * 0.09
                c.move_to(vx + (x - vx) * (y - vy) / (H * 1.1 - vy) * 0.999, y); c.line_to(x, H * 1.1); c.stroke()
            yy, step = y + 12, 14.0
            while yy < H * 1.1:
                c.move_to(-W, yy); c.line_to(2 * W, yy); c.stroke(); step *= 1.28; yy += step
            c.set_source_rgba(*_c((150, 110, 84), 0.5)); c.rectangle(-W, y - 3, 3 * W, 6); c.fill()
        self._lop(1.0, yard, y0=0.6)
        leaves = [(rng.uniform(0, 1), rng.uniform(0, 2 * PI), rng.uniform(0.04, 0.08)) for _ in range(6)]

        def la_roi(c, t):
            W, H = self.W, self.H
            for x0, ph, v in leaves:
                y = ((t * v + ph / 6.28) % 1.0) * H * 0.7 + H * 0.05
                x = W * x0 + 40 * math.sin(t * 1.1 + ph)
                if x > W * 0.78 and y < H * 0.2:
                    continue
                c.save(); c.translate(x, y); c.rotate(t * 1.5 + ph)
                c.set_source_rgba(*_c((200, 160, 70), 0.85)); _ellipse(c, 0, 0, 9 * H / 1080, 4 * H / 1080); c.fill(); c.restore()
        self.dong.append((0.62, la_roi))

    # ---- tường bản đồ (bản đồ trang trí, đất liền tưởng tượng)
    def _ban_do(self):
        rng = self.rng
        mx0, my0, mx1, my1 = 0.20, 0.09, 0.78, 0.62

        def wall(c, W, H):
            c.set_source(_grad(0, 0, 0, H, [(0, (236, 224, 202)), (1, (226, 210, 184))])); c.paint()
            _glow(c, W * 0.5, H * 0.35, H * 0.7, (255, 240, 214), 0.5)
        self._lop(0.3, wall, opaque=True)
        isl = []
        for (cx, cy, r) in ((0.33, 0.30, 0.10), (0.62, 0.24, 0.08), (0.52, 0.47, 0.06), (0.70, 0.46, 0.045), (0.27, 0.50, 0.035)):
            ph, amp = rng.uniform(0, 2 * PI, 4), rng.uniform(0.06, 0.2, 4)
            pts = []
            for j in range(40):
                a = 2 * PI * j / 40
                rr = r * (1 + sum(amp[m] * math.sin((m + 2) * a + ph[m]) for m in range(4)))
                pts.append((cx + rr * math.cos(a) * 0.62, cy + rr * math.sin(a)))
            isl.append(pts)
        route = [(0.33, 0.33), (0.45, 0.38), (0.52, 0.46), (0.60, 0.40), (0.62, 0.27)]

        def mapl(c, W, H):
            x0, y0, x1, y1 = W * mx0, H * my0, W * mx1, H * my1
            c.set_source_rgba(*_c((60, 40, 30), 0.25)); c.rectangle(x0 + 10, y0 + 14, x1 - x0, y1 - y0); c.fill()
            c.set_source_rgba(*_c((132, 88, 56))); c.rectangle(x0 - 16, y0 - 16, x1 - x0 + 32, y1 - y0 + 32); c.fill()
            c.set_source_rgba(*_c((240, 224, 184))); c.rectangle(x0, y0, x1 - x0, y1 - y0); c.fill()
            g = cairo.RadialGradient((x0 + x1) / 2, (y0 + y1) / 2, H * 0.1, (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) * 0.62)
            g.add_color_stop_rgba(0, *_c((214, 226, 214), 0.5)); g.add_color_stop_rgba(1, *_c((190, 160, 110), 0.55))
            c.set_source(g); c.rectangle(x0, y0, x1 - x0, y1 - y0); c.fill()
            c.save(); c.rectangle(x0, y0, x1 - x0, y1 - y0); c.clip()
            c.set_source_rgba(*_c((170, 140, 100), 0.45)); c.set_line_width(1.6)
            for k in range(1, 12):
                xx = x0 + (x1 - x0) * k / 12; c.move_to(xx, y0); c.line_to(xx, y1); c.stroke()
            for k in range(1, 8):
                yy = y0 + (y1 - y0) * k / 8; c.move_to(x0, yy); c.line_to(x1, yy); c.stroke()
            for pts in isl:
                P = [(W * x, H * y) for x, y in pts]
                c.new_path(); _cong_kin(c, P); c.set_source_rgba(*_c((198, 200, 150))); c.fill_preserve()
                c.set_source_rgba(*_c((130, 104, 70))); c.set_line_width(2.4); c.stroke()
                c.save(); c.new_path(); _cong_kin(c, P); c.clip()
                cxm = sum(p[0] for p in P) / len(P); cym = sum(p[1] for p in P) / len(P)
                _glow(c, cxm, cym, H * 0.06, (150, 170, 110), 0.6); c.restore()
            # hoa gió
            rx, ry, R = x0 + (x1 - x0) * 0.1, y1 - (y1 - y0) * 0.16, H * 0.05
            for k in range(8):
                a = k * PI / 4 - PI / 2; L = R if k % 2 == 0 else R * 0.55
                c.move_to(rx, ry); c.line_to(rx + math.cos(a - 0.2) * L * 0.3, ry + math.sin(a - 0.2) * L * 0.3)
                c.line_to(rx + math.cos(a) * L, ry + math.sin(a) * L); c.line_to(rx + math.cos(a + 0.2) * L * 0.3, ry + math.sin(a + 0.2) * L * 0.3); c.close_path()
                c.set_source_rgba(*_c((170, 70, 50) if k == 0 else (120, 90, 60))); c.fill()
            c.new_path(); c.arc(rx, ry, R * 0.12, 0, 2 * PI); c.set_source_rgba(*_c((240, 224, 184))); c.fill()
            c.restore()
            c.set_source_rgba(*_c((90, 60, 40))); c.set_line_width(3)
            for s in (0.3, 0.7):   # dây treo
                xx = x0 + (x1 - x0) * s
                c.move_to(xx, y0 - 16); c.line_to(W * 0.5, y0 - H * 0.05); c.stroke()
            c.new_path(); c.arc(W * 0.5, y0 - H * 0.05, 6, 0, 2 * PI); c.fill()
        self._lop(0.55, mapl, y0=0.0, y1=0.7)

        def route_fn(c, t):
            W, H = self.W, self.H
            pts = [(W * x, H * y) for x, y in route]
            c.set_source_rgba(*_c((196, 60, 48), 0.9)); c.set_line_width(4 * H / 1080)
            c.set_dash([14 * H / 1080, 10 * H / 1080], -t * 30)
            c.move_to(*pts[0])
            for k in range(1, len(pts)):
                p0, p1 = pts[k - 1], pts[k]
                mxp, myp = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 - H * 0.02
                c.curve_to(mxp, myp, mxp, myp, p1[0], p1[1])
            c.stroke(); c.set_dash([])
            for k, (x, y) in enumerate(pts):
                if k in (0, len(pts) - 1):
                    c.new_path(); c.arc(x, y, 9 * H / 1080, 0, 2 * PI); c.set_source_rgba(*_c((196, 60, 48))); c.fill()
                    c.new_path(); c.arc(x, y, 3.5 * H / 1080, 0, 2 * PI); c.set_source_rgba(1, 1, 1, 1); c.fill()
        self.dong.append((0.55, route_fn))

        def floor(c, W, H):
            y = H * 0.72
            c.set_source(_grad(0, y, 0, H * 1.08, [(0, (214, 180, 140)), (1, (198, 162, 122))])); c.rectangle(-W, y, 3 * W, H); c.fill()
            c.set_source_rgba(*_c((170, 130, 92))); c.rectangle(-W, y - 5, 3 * W, 10); c.fill()
        self._lop(1.0, floor, y0=0.68)


# ------------------------------------------------------------------ dựng cảnh
def _bo_cuc(W, H, k_chars):
    """Vị trí chân + tỉ lệ vẽ cho từng nhân vật (ngang 16:9 hoặc dọc 9:16)."""
    if H > W:
        k = 0.50 * H / CHIEU_CAO
        foot = 0.835 * H
        xs = (0.285 * W, 0.715 * W)
    else:
        k = 0.84 * H / CHIEU_CAO
        foot = 0.978 * H
        xs = (0.335 * W, 0.665 * W)
    if k_chars == 1:
        xs = (0.5 * W,)
    return k, foot, xs


def frames(sc, W, H, n, fps=30, seed=None, audio_offset=AUDIO_OFFSET):
    """Sinh n khung RGB (H, W, 3) uint8 cho một cảnh dẫn chuyện vẽ bằng code."""
    seed = int(sc.get("so", 0) or 0) if seed is None else int(seed)
    ten = [t for t in (sc.get("nhan_vat") or NARR) if t in NARR] or list(NARR)
    chars = [NhanVat(t, +1 if t == "Nhật Minh" else -1) for t in ten]
    if len(chars) == 1:
        chars[0].huong = 1 if chars[0].ten == "Nhật Minh" else -1
    _na = sc.get("nen_anh")
    if _na and not os.path.isabs(_na):
        _na = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), _na)
    nen = Nen(chon_nen(sc), W, H, seed, anh=_na)
    plan = KeHoach(sc, chars, n, fps, audio_offset, seed)
    k, foot, xs = _bo_cuc(W, H, len(chars))
    T = max(n / fps, 1e-3)
    sgn = 1 if seed % 2 == 0 else -1
    Cx, Cy = W * 0.5, H * 0.62
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    buf = np.ndarray((H, surf.get_stride() // 4, 4), np.uint8, buffer=surf.get_data())
    for i in range(n):
        t = i / fps
        u = _ss(t / T)
        cam = (sgn * W * 0.018 * (2 * u - 1), H * 0.004 * math.sin(PI * t / T), 1.0 + 0.035 * u, Cx, Cy)
        ctx.identity_matrix()
        nen.ve(ctx, t, cam)
        ctx.save()
        Nen.tf(ctx, cam, 1.0)
        for ch, x in zip(chars, xs):   # bóng đổ dưới chân
            rx = 150 * k
            g = cairo.RadialGradient(x, foot, 0, x, foot, rx)
            g.add_color_stop_rgba(0, 0.25, 0.15, 0.08, 0.30); g.add_color_stop_rgba(1, 0.25, 0.15, 0.08, 0)
            ctx.save(); ctx.translate(x, foot); ctx.scale(1, 0.16); ctx.translate(-x, -foot)
            ctx.set_source(g); ctx.arc(x, foot, rx, 0, 2 * PI); ctx.fill(); ctx.restore()
        for c, (ch, x) in enumerate(zip(chars, xs)):
            P = plan.pose(c, t, i)
            ctx.save(); ctx.translate(x, foot); ctx.scale(k * ch.k, k * ch.k)
            ch.draw(ctx, P)
            ctx.restore()
        ctx.restore()
        surf.flush()
        if sc.get("nen_anh_nguon"):   # ghi nguồn ảnh nền (bắt buộc với ảnh CC BY/BY-SA)
            ctx.identity_matrix(); ctx.select_font_face("sans-serif"); ctx.set_font_size(max(14, H * 0.017))
            ctx.move_to(W * 0.018 + 1.5, H * 0.045 + 1.5); ctx.set_source_rgba(0, 0, 0, 0.55); ctx.show_text(sc["nen_anh_nguon"])
            ctx.move_to(W * 0.018, H * 0.045); ctx.set_source_rgba(1, 1, 1, 0.9); ctx.show_text(sc["nen_anh_nguon"])
            surf.flush()
        yield buf[:, :W, 2::-1].copy()


def khung_mau(sc, W=1920, H=1080, times=(0.5,), fps=30, n=None):
    """Lấy vài khung tại các thời điểm (giây) – để xem nhanh / làm bảng tiếp xúc."""
    n = n or int(max(times) * fps) + 1
    want = {int(round(t * fps)) for t in times}
    out = {}
    for i, fr in enumerate(frames(sc, W, H, n, fps)):
        if i in want:
            out[i] = fr
        if len(out) == len(want):
            break
    return [out[k] for k in sorted(out)]
