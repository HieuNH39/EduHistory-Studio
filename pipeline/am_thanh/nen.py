"""Âm nền (ambience) – mỗi loại là một VÒNG LẶP LIỀN MẠCH dài 24–32 s (tạo một lần, lưu ở renders/_cache/am_thanh/),
cộng thêm 'điểm xuyết' ngẫu nhiên mỗi cảnh (chim hót, lách tách, giọt nước, mòng biển, trống xa…) nên không nghe lặp máy móc.
Vòng lặp được chuẩn về độ to −23 LUFS (BS.1770, không cổng), đỉnh được nén nhẹ về ≤ −14 dBFS (hệ số đỉnh ~9 dB so với LUFS – nền đều, không có tiếng giật); mức thật do bộ trộn đặt (xem thiet_ke.MUC_NEN)."""
import os
import numpy as np
import soundfile as sf
from .dsp import (SR, so_mau, truc_tg, on_trang, on_hong, on_nau, lp, hp, bp, cong_huong, loc_quet, bao_exp,
                  bao_hinh_chuong, mo_dan, pan, stereo, vang, modal, chuan_rms, tao_vong_lap, dat_vao,
                  muot_ngau_nhien, do_rong, rms, tu_db, rang_cua, pan_dong, chuan_lufs, gioi_han_mem, gioi_han, lufs)
from . import nguon, su_kien

PHIEN_BAN = 7          # tăng khi sửa công thức để bộ nhớ đệm tự tạo lại
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE = os.path.join(ROOT, "renders/_cache/am_thanh")
XF = 3.0               # giây đan chéo khi khép vòng


def _hai_kenh(fn, n, rng, tuong_quan=0.5):
    """Tạo âm nổi tự nhiên: hai kênh từ hai nguồn ngẫu nhiên, trộn một phần chung (tương quan)."""
    a, b, c = fn(n, rng), fn(n, rng), fn(n, rng)
    k = np.sqrt(tuong_quan)
    return stereo(a * np.sqrt(1 - tuong_quan) + c * k, b * np.sqrt(1 - tuong_quan) + c * k)


# ------------------------------------------------------------------ công thức từng loại nền
def _gio(n, rng, manh=1.0):
    def mot(n, rng):
        gust = muot_ngau_nhien(n, rng, 0.18, 0.25, 1.0) ** 1.5
        base = on_nau(n, rng)
        lo, hi = lp(base, 220), lp(base, 900)
        y = lo * (1 - gust) + hi * gust
        return hp(y, 40) * (0.35 + 0.65 * gust)
    y = _hai_kenh(mot, n, rng, 0.55)
    # tiếng rít rất nhẹ (cộng hưởng di chuyển)
    w = loc_quet(on_hong(n, rng), muot_ngau_nhien(max(n // 4800, 8), rng, 1, 420, 950), bw_oct=0.25)
    y += pan(w * muot_ngau_nhien(n, rng, 0.2, 0, 1) ** 3 * 0.25, rng.uniform(-.4, .4))
    return y * manh


def _la_cay(n, rng):
    """Lá cây xào xạc theo gió."""
    def mot(n, rng):
        gust = muot_ngau_nhien(n, rng, 0.25, 0.15, 1.0) ** 2
        flut = muot_ngau_nhien(n, rng, 14, 0.4, 1.0)
        return bp(on_hong(n, rng), 1400, 6500) * gust * flut
    return _hai_kenh(mot, n, rng, 0.2)


def _song(n, rng):
    """Sông lớn: nền nước chảy rì rào (dải 120–1800 Hz, gợn nhanh) + sóng nhỏ vỗ bờ + bọt nước lác đác."""
    def mot(n, rng):
        wash = bp(on_hong(n, rng), 120, 1800) * muot_ngau_nhien(n, rng, 0.3, 0.6, 1.0) * muot_ngau_nhien(n, rng, 7, 0.8, 1.0)
        return wash
    y = _hai_kenh(mot, n, rng, 0.35) * 0.8
    y += pan(nguon.vo_bo(n, rng, 1.0), -0.35) * 0.7 + pan(nguon.vo_bo(n, rng, 0.8), 0.4) * 0.6
    gur = np.zeros(n, np.float32)
    for _ in range(int(n / SR * 2.5)):
        dat_vao(gur, nguon.bot_nuoc(rng, f0=rng.uniform(250, 700), tat=rng.uniform(.02, .05)) * rng.uniform(.05, .15), rng.integers(0, n))
    y += pan(gur, rng.uniform(-.3, .3))
    return lp(y, 7000)


def _bien(n, rng):
    """Biển: các con sóng dâng – vỡ – rút (chu kì 5–9 s, chồng nhau) + rì rầm sóng xa + bọt sóng."""
    y = np.zeros((n, 2), np.float32)
    far = _hai_kenh(lambda n, r: lp(on_nau(n, r), 400), n, rng, 0.5) * 0.35
    y += far
    t = rng.uniform(0, 2)
    while t < n / SR:
        d = rng.uniform(4.5, 7.0); m = so_mau(d)
        up = rng.uniform(0.35, 0.5)
        e = bao_hinh_chuong(m, up, 1.3)
        fc = np.r_[np.linspace(250, 1600, 6), np.linspace(1600, 500, 10)]
        w = loc_quet(on_trang(m, rng), fc * rng.uniform(.8, 1.2), bw_oct=2.4) * e
        foam = hp(on_trang(m, rng), 2500) * np.clip(e - 0.3, 0, 1) * 0.25
        dat_vao(y, pan(w + foam, rng.uniform(-.6, .6)), so_mau(t), rng.uniform(.6, 1.0))
        t += rng.uniform(4.0, 7.5)
    return lp(y, 8000)


def _mua(n, rng):
    """Mưa vừa, êm: nền hạt mưa dày (ồn cao tần mềm) + giọt rơi lách tách + tiếng nước đọng trầm."""
    y = _hai_kenh(lambda n, r: bp(on_hong(n, r), 900, 7000) * muot_ngau_nhien(n, r, 0.2, .75, 1.0), n, rng, 0.2)
    drops = np.zeros((n, 2), np.float32)
    for _ in range(int(n / SR * 40)):
        m = so_mau(0.02); d = on_trang(m, rng) * bao_exp(m, 0.0004, 0.003)
        d = cong_huong(np.pad(d, (0, 200)), rng.uniform(1500, 5000), 4)
        dat_vao(drops, pan(d, rng.uniform(-1, 1)), rng.integers(0, n), rng.uniform(.05, .35))
    y += drops + _hai_kenh(lambda n, r: lp(on_nau(n, r), 300), n, rng, 0.5) * 0.3
    return lp(y, 8500)


def _rung(n, rng):
    return _la_cay(n, rng) * 0.8 + _gio(n, rng, 0.5)


def _dong_que(n, rng):
    return _la_cay(n, rng) * 0.45 + _gio(n, rng, 0.45)


def _con_trung_dem(n, rng):
    """Đêm: nhiều con dế ở các vị trí khác nhau + tiếng rỉ rả cao rất nhỏ + gió đêm khẽ."""
    y = np.zeros((n, 2), np.float32)
    for k in range(7):
        y += pan(nguon.de_keu(n, rng, muc=rng.uniform(.3, 1.0)), rng.uniform(-.9, .9))
    hum = bp(on_hong(n, rng), 5500, 8000) * muot_ngau_nhien(n, rng, 0.2, .3, 1) * 0.08
    y = lp(y, 7000) * 0.8 + stereo(hum, hum[::-1].copy())
    return y + _gio(n, rng, 0.25)


def _lua_chay(n, rng):
    """Đám lửa/đuốc: ồn phừng phừng trầm + lách tách."""
    y = stereo(nguon.ao_lua(n, rng), nguon.ao_lua(n, rng)) * 0.9
    y += pan(nguon.lach_tach(n, rng, 7), -0.25) + pan(nguon.lach_tach(n, rng, 6), 0.3)
    return y


def _chien_tran_xa(n, rng, hien_dai=False):
    """Tiếng chiến trận vọng lại từ xa: rền trầm, hô vang lúc to lúc nhỏ, trống xa, binh khí rất mờ (thời cổ – trung đại)
    hoặc pháo – súng vọng xa (thời hiện đại). Đặt rất xa (cắt cao tần mạnh + vang dài) để không gây sợ."""
    y = _hai_kenh(lambda n, r: lp(on_nau(n, r), 140) * muot_ngau_nhien(n, r, 0.25, .4, 1), n, rng, 0.5) * 0.8
    if not hien_dai:
        roar = nguon.giong_ho(n, rng, so_nguoi=22, kieu="xung_tran")
        # giọng hô kéo dài suốt vòng: lặp nhiều đợt
        for _ in range(int(n / SR / 2.2)):
            m = so_mau(3.0); seg = nguon.giong_ho(m, rng, so_nguoi=10, kieu="xung_tran")
            dat_vao(roar, seg * rng.uniform(.4, 1.0), rng.integers(0, max(1, n - m)))
        y += lp(roar, 1100) * 0.9 * muot_ngau_nhien(n, rng, 0.3, .4, 1)[:, None]
        drum = np.zeros((n, 2), np.float32); t = 0.0
        while t < n / SR - 3:
            seq = su_kien.trong_hoi(rng, kieu="thuc", dai=rng.uniform(1.5, 3.0), xa=0.9)
            dat_vao(drum, seq, so_mau(t), rng.uniform(.15, .35)); t += rng.uniform(3, 7)
        y += lp(drum, 900)
        for _ in range(int(n / SR * 1.2)):
            dat_vao(y, pan(lp(nguon.leng_keng(rng), 2200), rng.uniform(-.8, .8)), rng.integers(0, n), rng.uniform(.03, .1))
    else:
        for _ in range(int(n / SR / 2.5)):
            dat_vao(y, lp(su_kien.phao(rng, xa=1.0), 500), rng.integers(0, n), rng.uniform(.2, .5))
        for _ in range(int(n / SR / 5)):
            dat_vao(y, lp(su_kien.sung_xa(rng, dai=rng.uniform(1, 3)), 800), rng.integers(0, n), rng.uniform(.1, .25))
    return vang(lp(y, 2600), t60=2.5, uot=0.35, rong=1.3, hat=40, giu_duoi=False)


def _dam_dong(n, rng):
    y = nguon.giong_xi_xao(n, rng, so_nguoi=14, gan=0.2)
    return vang(y, t60=1.2, uot=0.25, hat=41, giu_duoi=False)


def _cho(n, rng):
    """Chợ / phố buôn bán xưa: nhiều người nói, vài giọng gần hơn, bước chân, tiếng nồi niêu/đồ vật chạm nhẹ."""
    y = nguon.giong_xi_xao(n, rng, so_nguoi=18, gan=0.35, toc_do=1.1)
    y += nguon.giong_xi_xao(n, rng, so_nguoi=3, gan=0.8) * 0.6
    st = np.zeros(n, np.float32); t = 0.0
    while t < n / SR:
        dat_vao(st, nguon.buoc_chan(rng, 0.8) * rng.uniform(.1, .3), so_mau(t)); t += rng.exponential(0.18)
    y += pan(hp(st, 200), rng.uniform(-.3, .3))
    for _ in range(int(n / SR * 0.8)):
        dat_vao(y, pan(nguon.leng_keng(rng, f=rng.uniform(1200, 2400)), rng.uniform(-.8, .8)), rng.integers(0, n), rng.uniform(.05, .15))
    return vang(y, t60=1.0, uot=0.2, hat=42, giu_duoi=False)


def _cung_dien(n, rng):
    """Không gian cung điện / điện thờ: tiếng phòng lớn rất trầm, không khí, vang dài, xì xào thì thầm xa thỉnh thoảng."""
    room = _hai_kenh(lambda n, r: lp(on_nau(n, r), 180), n, rng, 0.6) * 0.8
    air = _hai_kenh(lambda n, r: bp(on_hong(n, r), 2000, 7000), n, rng, 0.1) * 0.05
    wh = nguon.giong_xi_xao(n, rng, so_nguoi=5, gan=0.1, la_tham=0.5, toc_do=0.9) * 0.35
    wh *= muot_ngau_nhien(n, rng, 0.15, 0.0, 1.0)[:, None] ** 2
    return room + air + vang(wh, t60=2.4, uot=0.5, hat=43, giu_duoi=False)


def _phong(n, rng):
    """Phòng nhỏ / lều: tiếng phòng trầm, rất khẽ."""
    return _hai_kenh(lambda n, r: lp(on_nau(n, r), 250), n, rng, 0.7) + _hai_kenh(lambda n, r: bp(on_hong(n, r), 1500, 6000), n, rng, 0.2) * 0.04


def _trai_quan(n, rng):
    """Doanh trại: lửa trại nhỏ, binh lính trò chuyện khẽ ở xa, khí giới lách cách, cờ bay."""
    y = _lua_chay(n, rng) * 0.35
    y += nguon.giong_xi_xao(n, rng, so_nguoi=6, nu_ti_le=0.0, gan=0.1) * 0.6
    for _ in range(int(n / SR * 0.6)):
        dat_vao(y, pan(nguon.leng_keng(rng), rng.uniform(-.8, .8)), rng.integers(0, n), rng.uniform(.04, .1))
    y += pan(nguon.phap_phoi(n, rng, 0.6), rng.uniform(-.5, .5)) * 0.25
    return vang(y + _gio(n, rng, 0.4) * 0.5, t60=1.2, uot=0.2, hat=44, giu_duoi=False)


def _hang_dong(n, rng):
    """Hang đá: tiếng phòng đá rất trầm, gió lùa khẽ, giọt nước rơi vang dài."""
    y = _hai_kenh(lambda n, r: lp(on_nau(n, r), 150), n, rng, 0.6)
    dr = np.zeros(n, np.float32)
    for _ in range(int(n / SR * 0.7)):
        dat_vao(dr, nguon.giot_nuoc(rng) * rng.uniform(.15, .5), rng.integers(0, n))
    y += vang(pan(dr, rng.uniform(-.5, .5)), t60=2.8, uot=0.55, hat=45, giu_duoi=False)
    return y + _gio(n, rng, 0.2)


def _pho(n, rng):
    """Phố hôm nay (cảnh dẫn chuyện hiện tại): xe cộ rì rầm xa, thỉnh thoảng xe máy chạy qua xa, chim sẻ."""
    y = _hai_kenh(lambda n, r: lp(on_nau(n, r), 380) * muot_ngau_nhien(n, r, 0.15, .6, 1), n, rng, 0.6)
    for _ in range(int(n / SR / 4)):
        m = so_mau(rng.uniform(2.5, 4.0)); u = np.linspace(0, 1, m)
        f0 = rng.uniform(85, 120) * (1.04 - 0.08 * u)
        s = lp(rang_cua(f0.astype(np.float32)), 700) * bao_hinh_chuong(m, .5, 2.0) * 0.25
        dat_vao(y, pan_dong(s, -0.8, 0.8) if rng.random() < .5 else pan_dong(s, 0.8, -0.8), rng.integers(0, max(1, n - m)))
    return y


def _nha_may(n, rng):
    """Xưởng máy thế kỉ XVIII–XIX: tiếng máy rền (50/100 Hz), khung cửi gõ nhịp, hơi xì."""
    t = truc_tg(n)
    hum = (np.sin(2 * np.pi * 50 * t) + 0.5 * np.sin(2 * np.pi * 100 * t) + 0.2 * np.sin(2 * np.pi * 150 * t)) * 0.25
    y = stereo(hum, hum) + _hai_kenh(lambda n, r: bp(on_hong(n, r), 150, 1500), n, rng, 0.5) * 0.4
    k = 0.0
    while k < n / SR:
        dat_vao(y, pan(nguon.go_go(rng, f=rng.uniform(400, 600)), rng.uniform(-.5, .5)), so_mau(k), 0.35); k += 0.36
    for _ in range(int(n / SR / 3)):
        dat_vao(y, su_kien.hoi_nuoc(rng, 0.5), rng.integers(0, n), 0.15)
    return vang(y, t60=1.4, uot=0.25, hat=46, giu_duoi=False)


def _bien_tau(n, rng):
    """Trên tàu buồm giữa biển (hành trình): sóng biển + gió lộng + buồm phần phật nhẹ."""
    return _bien(n, rng) * 0.8 + _gio(n, rng, 0.8) * 0.6 + pan(nguon.phap_phoi(n, rng, 0.5), 0.2) * 0.15


CONG_THUC = {
    "gio": (_gio, 24), "song": (_song, 24), "bien": (_bien, 32), "mua": (_mua, 24), "rung": (_rung, 24),
    "dong_que": (_dong_que, 24), "con_trung_dem": (_con_trung_dem, 24), "lua_chay": (_lua_chay, 24),
    "chien_tran_xa": (lambda n, r: _chien_tran_xa(n, r, False), 26), "chien_tran_hien_dai": (lambda n, r: _chien_tran_xa(n, r, True), 26),
    "dam_dong": (_dam_dong, 24), "cho": (_cho, 24), "cung_dien": (_cung_dien, 24), "phong": (_phong, 20),
    "trai_quan": (_trai_quan, 24), "hang_dong": (_hang_dong, 24), "pho": (_pho, 24), "nha_may": (_nha_may, 20),
    "bien_tau": (_bien_tau, 32),
}

TEN_VIET = {
    "gio": "gió", "song": "sông nước", "bien": "sóng biển", "mua": "mưa", "rung": "rừng (lá + gió)", "dong_que": "đồng quê",
    "con_trung_dem": "côn trùng đêm", "lua_chay": "lửa cháy", "chien_tran_xa": "chiến trận vọng xa",
    "chien_tran_hien_dai": "chiến trận hiện đại vọng xa", "dam_dong": "đám đông xì xào", "cho": "chợ / phố buôn bán",
    "cung_dien": "không gian cung điện", "phong": "phòng / lều", "trai_quan": "doanh trại", "hang_dong": "hang đá",
    "pho": "phố hôm nay", "nha_may": "xưởng máy", "bien_tau": "tàu giữa biển",
}


_LOOPS = {}


def vong_lap(ten):
    """Trả về vòng lặp (N, 2) float32 của loại nền 'ten' (tạo và lưu đệm nếu chưa có)."""
    if ten in _LOOPS: return _LOOPS[ten]
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f"nen_{ten}_v{PHIEN_BAN}.wav")
    if os.path.exists(path):
        x, _ = sf.read(path, dtype="float32")
    else:
        fn, dai = CONG_THUC[ten]
        rng = np.random.default_rng(sum(map(ord, ten)) * 7919 + PHIEN_BAN)   # cố định → tạo lại vẫn y hệt
        x = fn(so_mau(dai + XF), rng)
        x = x[:so_mau(dai + XF)]
        x = hp(x, 35)
        x = tao_vong_lap(x, XF)
        x = chuan_lufs(x, -23.0)
        x = gioi_han(x, -14.0)                 # nén đỉnh (hạ khuếch đại, không méo) …
        x = gioi_han(chuan_lufs(x, -23.0), -13.5)   # … rồi trả lại độ to −23 LUFS
        sf.write(path, x, SR, subtype="PCM_16")
    _LOOPS[ten] = x.astype(np.float32)
    return _LOOPS[ten]


# ------------------------------------------------------------------ điểm xuyết ngẫu nhiên theo cảnh (không lặp)
def diem_xuyet(ten, dai, rng, ban_ngay=True, co_nuoc=False):
    """Các tiếng lẻ tô điểm cho nền 'ten' trong 'dai' giây (đã ở thang đo của vòng lặp −23 LUFS).
    Trả về (mảng stereo, danh sách mô tả) hoặc (None, [])."""
    n = so_mau(dai)
    if n <= 0: return None, []
    y = np.zeros((n, 2), np.float32); mo_ta = []

    def rai(fn, mat_do, muc_db, ten_vn, le=0.4):
        t = rng.uniform(0.2, 1.5); k = 0
        while t < dai - le:
            s = fn()
            dat_vao(y, s, so_mau(t), tu_db(muc_db + rng.uniform(-4, 2))); k += 1
            t += rng.exponential(1 / mat_do) + le
        if k: mo_ta.append(f"{ten_vn}×{k}")

    if ten in ("rung", "dong_que") and ban_ngay:
        rai(lambda: su_kien.chim(rng), 0.35 if ten == "rung" else 0.22, -22, "chim hót")
        if ten == "dong_que" and rng.random() < .6:
            rai(lambda: su_kien.chim(rng, "cu_gay"), 0.06, -24, "chim cu gáy", 2.0)
    elif ten == "song" and ban_ngay:
        rai(lambda: su_kien.chim(rng, ["chiep", "hot", "khuou"][rng.integers(0, 3)]), 0.12, -26, "chim ven sông")
    elif ten in ("bien", "bien_tau"):
        rai(lambda: su_kien.chim(rng, "hai_au"), 0.08, -27, "mòng biển", 2.5)
        if ten == "bien_tau":
            rai(lambda: su_kien.cot_ket(rng), 0.25, -20, "thân tàu cót két", 1.0)
    elif ten == "con_trung_dem" and co_nuoc:
        rai(lambda: pan(nguon.ech_keu(rng), rng.uniform(-.8, .8)), 0.3, -24, "ếch nhái")
    elif ten == "lua_chay":
        rai(lambda: pan(nguon.lach_tach(so_mau(0.4), rng, 30, 1.2), rng.uniform(-.5, .5)), 0.5, -16, "củi nổ")
    elif ten == "chien_tran_xa":
        rai(lambda: su_kien.ho_reo(rng, "xung_tran", so=10, xa=0.9), 0.12, -18, "đợt hô xa", 2.0)
    elif ten == "pho" and ban_ngay:
        rai(lambda: su_kien.chim(rng, "chiep"), 0.2, -24, "chim sẻ")
    elif ten == "hang_dong":
        rai(lambda: vang(pan(nguon.giot_nuoc(rng), rng.uniform(-.7, .7)), t60=2.5, uot=.5, hat=45), 0.4, -18, "giọt nước")
    elif ten == "trai_quan":
        rai(lambda: su_kien.leng_keng(rng, 2), 0.12, -22, "khí giới lách cách", 1.0)
    elif ten == "cung_dien":
        rai(lambda: pan(nguon.buoc_chan(rng, 0.7) * 0.6, rng.uniform(-.6, .6)), 0.1, -26, "bước chân xa", 1.0)
    if not mo_ta: return None, []
    return y, mo_ta
