"""Nguồn âm tự nhiên tổng hợp: giọng người xa (xì xào, hô vang), chim, côn trùng, ếch, bọt nước, giọt nước, lách tách lửa…
Đều là tổng hợp thuần bằng toán (không dùng mẫu thu âm), có ngẫu nhiên hoá để không lặp máy móc."""
import math
import numpy as np
from .dsp import (SR, so_mau, truc_tg, on_trang, on_hong, lp, hp, bp, cong_huong, bao_exp, rang_cua,
                  muot_ngau_nhien, pan, dat_vao, mo_dan, modal)

# formant (F1, F2, F3) nguyên âm tiếng Việt, giọng nam (Hz) – giọng nữ nhân ~1.17
NGUYEN_AM = {
    "a": (750, 1250, 2600), "e": (520, 1850, 2600), "i": (300, 2250, 3000), "o": (520, 900, 2500),
    "u": (330, 800, 2300), "ơ": (560, 1350, 2500), "ư": (350, 1350, 2400), "ô": (450, 850, 2450),
}
_NA = list(NGUYEN_AM)


def _thanh_dieu(n, rng):
    """Đường cao độ tương đối của một âm tiết theo 6 thanh tiếng Việt (ngang, huyền, sắc, hỏi, ngã, nặng) – cho tiếng xì xào nghe 'Việt' hơn."""
    u = np.linspace(0, 1, n, dtype=np.float32)
    k = rng.integers(0, 6)
    if k == 0: c = np.zeros_like(u)
    elif k == 1: c = -0.10 * u
    elif k == 2: c = 0.16 * u ** 1.5
    elif k == 3: c = -0.10 * np.sin(np.pi * u)
    elif k == 4: c = 0.14 * u - 0.10 * np.exp(-((u - .45) / .08) ** 2)
    else: c = -0.16 * u ** 0.7
    return 1 + c


def giong_xi_xao(n, rng, so_nguoi=10, nu_ti_le=0.4, gan=0.0, toc_do=1.0, la_tham=0.0):
    """Tiếng nhiều người nói chuyện xa (xì xào, chợ, triều đình). Mỗi 'người' là chuỗi âm tiết có thanh điệu,
    nguyên âm lọc formant, có khoảng nghỉ giữa câu. gan: 0 (xa, mờ) … 1 (gần, rõ hơn). la_tham: 0..1 tỉ lệ thì thầm (không thanh)."""
    out = np.zeros((n, 2), np.float32)
    for p in range(so_nguoi):
        nu = rng.random() < nu_ti_le
        f0b = rng.uniform(175, 245) if nu else rng.uniform(95, 140)
        fm = 1.17 if nu else 1.0
        thi_tham = rng.random() < la_tham
        mono = np.zeros(n, np.float32)
        t = rng.uniform(0, 1.5)
        while t < n / SR:
            # một câu: 3–12 âm tiết
            so_am = rng.integers(3, 13); decl = np.linspace(1.08, 0.92, so_am)
            for j in range(so_am):
                d = rng.uniform(0.10, 0.26) / toc_do
                s0 = so_mau(t); m = so_mau(d) + so_mau(0.04)
                if s0 + m >= n: break
                f0 = f0b * decl[j] * _thanh_dieu(m, rng) * (1 + 0.01 * rng.standard_normal())
                src = (on_trang(m, rng) * 0.6) if thi_tham else (rang_cua(f0) + 0.06 * on_trang(m, rng))
                F = NGUYEN_AM[_NA[rng.integers(0, len(_NA))]]
                v = (cong_huong(src, F[0] * fm, 6) + 0.6 * cong_huong(src, F[1] * fm, 10) + 0.3 * cong_huong(src, F[2] * fm, 14))
                e = bao_exp(m, 0.018, d * 0.45) * rng.uniform(0.45, 1.0)
                if rng.random() < 0.35:   # phụ âm xát đầu âm tiết
                    k = so_mau(0.03); v[:k] += bp(on_trang(k, rng), 2500, 6500) * 0.5
                mono[s0:s0 + m] += v * e
                t += d + rng.uniform(0.0, 0.05)
            t += rng.uniform(0.25, 1.2) / toc_do
        mono = lp(mono, 1600 + 2600 * gan + rng.uniform(-300, 300))
        out += pan(mono * rng.uniform(0.5, 1.0) * (1.0 if not thi_tham else 0.7), rng.uniform(-0.85, 0.85))
    return hp(out, 120)


def giong_ho(n, rng, so_nguoi=18, kieu="xung_tran", nu_ti_le=0.0):
    """Tiếng hô đồng thanh / reo hò ở xa (không phải tiếng kêu thét). kieu: 'xung_tran' (hô dồn, lên giọng),
    'reo' (reo mừng chiến thắng – 2–3 đợt), 'hieu_lenh' (một tiếng hô ngắn 'Đánh!')."""
    out = np.zeros((n, 2), np.float32)
    dot = {"xung_tran": [(0.0, 1.0)], "reo": [(0.0, .7), (0.95, .9), (1.9, .75)], "hieu_lenh": [(0.0, .5)]}[kieu]
    for p in range(so_nguoi):
        nu = rng.random() < nu_ti_le
        f0b = rng.uniform(200, 290) if nu else rng.uniform(150, 215)
        mono = np.zeros(n, np.float32)
        for (td, dd) in dot:
            t0 = td + rng.uniform(0, 0.28)
            d = dd * rng.uniform(0.75, 1.25) + (0.4 if kieu == "xung_tran" else 0)
            s0 = so_mau(t0); m = so_mau(d)
            if s0 + m > n: m = n - s0
            if m <= so_mau(0.1): continue
            u = np.linspace(0, 1, m, dtype=np.float32)
            glide = 1 + (0.12 * np.sin(np.pi * u) if kieu == "reo" else 0.10 * u)
            f0 = f0b * glide * (1 + 0.012 * np.sin(2 * np.pi * rng.uniform(4, 6) * u * d))
            src = rang_cua(f0) + 0.12 * on_trang(m, rng)
            F = NGUYEN_AM[["a", "ô", "ơ", "o"][rng.integers(0, 4)]]
            fm = 1.17 if nu else 1.05
            v = cong_huong(src, F[0] * fm, 5) + 0.7 * cong_huong(src, F[1] * fm, 8) + 0.35 * cong_huong(src, F[2] * fm, 12)
            e = np.minimum(u / 0.12, 1) * np.minimum((1 - u) / 0.35, 1) ** 1.5
            mono[s0:s0 + m] += v * e.astype(np.float32) * rng.uniform(0.6, 1.0)
        out += pan(mono, rng.uniform(-0.9, 0.9))
    return hp(lp(out, 2400), 150)


# ------------------------------------------------------------------ chim
def tieng_chim(rng, loai=None):
    """Một tiếng chim ngắn (mono). loai: chiep (sẻ), hot (chích choè hót), cu_gay, khuou (huýt), hai_au."""
    loai = loai or ["chiep", "hot", "hot", "khuou", "cu_gay"][rng.integers(0, 5)]
    if loai == "chiep":
        k = rng.integers(2, 6); parts = []
        for _ in range(k):
            d = rng.uniform(0.035, 0.07); m = so_mau(d); u = np.linspace(0, 1, m)
            f = rng.uniform(3200, 4200) * (1 - rng.uniform(0.1, 0.35) * u) if rng.random() < .7 else rng.uniform(2800, 3400) * (1 + .3 * u)
            ph = 2 * np.pi * np.cumsum(f) / SR
            s = (np.sin(ph) + 0.15 * np.sin(2 * ph)) * np.clip(np.sin(np.pi * u), 0, 1) ** 1.5
            parts += [s, np.zeros(so_mau(rng.uniform(0.06, 0.14)))]
        y = np.concatenate(parts)
    elif loai == "hot":
        k = rng.integers(5, 14); parts = []; base = rng.uniform(1900, 3200)
        for _ in range(k):
            d = rng.uniform(0.05, 0.16); m = so_mau(d); u = np.linspace(0, 1, m)
            f1 = base * rng.uniform(0.8, 1.45); f2 = base * rng.uniform(0.8, 1.45)
            f = f1 + (f2 - f1) * u + rng.uniform(40, 160) * np.sin(2 * np.pi * rng.uniform(18, 35) * u * d)
            ph = 2 * np.pi * np.cumsum(f) / SR
            s = (np.sin(ph) + 0.08 * np.sin(2 * ph)) * np.clip(np.sin(np.pi * u), 0, 1) ** 1.2
            parts += [s, np.zeros(so_mau(rng.uniform(0.02, 0.08)))]
        y = np.concatenate(parts)
    elif loai == "khuou":
        m = so_mau(rng.uniform(0.35, 0.6)); u = np.linspace(0, 1, m); f1, f2 = rng.uniform(1500, 2100), rng.uniform(2200, 2900)
        f = np.where(u < .45, f1, f2) * 1.0; f = np.convolve(f, np.ones(600) / 600, "same")
        ph = 2 * np.pi * np.cumsum(f) / SR
        y = np.sin(ph) * (np.minimum(u / .05, 1) * np.minimum((1 - u) / .12, 1)) * (1 - .6 * np.exp(-((u - .45) / .04) ** 2))
    elif loai == "cu_gay":   # chim cu gáy: "cù cu … cu" trầm
        parts = []
        for j, (d, g) in enumerate([(0.16, .7), (0.30, 1.0), (0.22, .8)][:rng.integers(2, 4)]):
            m = so_mau(d * rng.uniform(.9, 1.1)); u = np.linspace(0, 1, m)
            f = rng.uniform(470, 560) * (1 - 0.06 * u) * (0.94 if j == 0 else 1)
            ph = 2 * np.pi * np.cumsum(f) / SR
            s = (np.sin(ph) + 0.25 * np.sin(2 * ph)) * np.clip(np.sin(np.pi * u), 0, 1) ** 0.8 * g
            parts += [s, np.zeros(so_mau(rng.uniform(.12, .2)))]
        y = lp(np.concatenate(parts).astype(np.float32), 1500)
    else:  # hai_au – mòng biển, nhẹ và xa
        m = so_mau(rng.uniform(0.25, 0.4)); u = np.linspace(0, 1, m)
        f = rng.uniform(1250, 1500) * (1 - 0.35 * u ** 1.3)
        ph = 2 * np.pi * np.cumsum(f) / SR
        src = np.sin(ph) + .45 * np.sin(2 * ph) + .2 * np.sin(3 * ph)
        y = src * (0.75 + .25 * np.sin(2 * np.pi * 55 * u * m / SR)) * np.minimum(u / .08, 1) * np.minimum((1 - u) / .3, 1)
        y = bp(y.astype(np.float32), 700, 3500)
    return mo_dan(np.asarray(y, np.float32), 0.003, 0.01)


# ------------------------------------------------------------------ côn trùng, ếch
def de_keu(n, rng, fc=None, muc=1.0):
    """Một con dế: sóng mang 3.8–5 kHz điều biên thành xung (25–40 Hz) gom thành tiếng 'ri ri' lặp 1.5–3 lần/giây."""
    t = truc_tg(n).astype(np.float64)
    fc = fc or rng.uniform(3800, 4900)
    pr = rng.uniform(26, 40); cr = rng.uniform(1.4, 2.8); cw = rng.uniform(0.09, 0.2)
    jit = muot_ngau_nhien(n, rng, 0.3, -0.04, 0.04)
    chirp_ph = (t * cr + jit) % 1.0
    win = (chirp_ph < cw * cr).astype(np.float32)
    win = np.convolve(win, np.ones(96) / 96, "same")
    pulse = (0.5 - 0.5 * np.cos(2 * np.pi * pr * t)) ** 3
    amp = muot_ngau_nhien(n, rng, 0.15, 0.4, 1.0)
    y = np.sin(2 * np.pi * fc * t) * pulse * win * amp
    return (y * muc).astype(np.float32)


def ech_keu(rng):
    """Tiếng ếch/nhái 'ộp' ở xa: chuỗi xung cộng hưởng 450–900 Hz."""
    k = rng.integers(6, 14); rate = rng.uniform(22, 34); f = rng.uniform(450, 900)
    m = so_mau(k / rate + 0.1); y = np.zeros(m, np.float32)
    imp = np.zeros(m, np.float32)
    for j in range(k):
        imp[so_mau(j / rate + rng.uniform(0, 0.004))] = rng.uniform(0.6, 1.0) * math.sin(math.pi * (j + .5) / k)
    y = cong_huong(imp, f, 9) + 0.5 * cong_huong(imp, f * 2.1, 12)
    return lp(y, 1800)


# ------------------------------------------------------------------ nước
def bot_nuoc(rng, f0=None, tat=None):
    """Một bọt khí vỡ (mô hình Minnaert): sin tắt dần, cao độ hơi đi lên."""
    f0 = f0 or rng.uniform(350, 1500); tat = tat or rng.uniform(0.008, 0.035)
    m = so_mau(tat * 6); t = truc_tg(m)
    f = f0 * (1 + 0.6 * t / (tat * 6))
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * np.exp(-t / tat) * np.minimum(t / 0.0015, 1)).astype(np.float32)


def giot_nuoc(rng):
    """Giọt nước nhỏ xuống vũng (trong hang): tiếng 'tóc' cao độ đi lên nhanh."""
    m = so_mau(0.09); t = truc_tg(m); f0 = rng.uniform(900, 1700)
    f = f0 * (1 + 1.2 * np.minimum(t / 0.03, 1))
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * np.exp(-t / 0.018) * np.minimum(t / 0.001, 1)).astype(np.float32)


def vo_bo(n, rng, mat_do=0.8, sang=1.0):
    """Sóng nhỏ vỗ bờ sông/hồ: các nhịp 'óc ách' ngẫu nhiên (tiếng ồn lọc 250–1600 Hz, bao mềm) + vài bọt nước."""
    out = np.zeros(n, np.float32); t = rng.uniform(0, 0.8)
    while t < n / SR:
        d = rng.uniform(0.18, 0.55); m = so_mau(d)
        u = np.linspace(0, 1, m, dtype=np.float32)
        e = np.sin(np.pi * u ** 0.6) ** 2
        s = bp(on_trang(m, rng), 220 * sang, rng.uniform(900, 1700) * sang) * e * rng.uniform(0.4, 1.0)
        dat_vao(out, s, so_mau(t))
        for _ in range(rng.integers(0, 4)):
            dat_vao(out, bot_nuoc(rng) * rng.uniform(0.05, 0.18), so_mau(t + rng.uniform(0.02, d)))
        t += rng.uniform(0.35, 1.6) / mat_do
    return out


# ------------------------------------------------------------------ lửa
def lach_tach(n, rng, mat_do=6.0, co=1.0):
    """Tiếng nổ lách tách của củi/đuốc: xung ngắn lọc ngẫu nhiên, đi thành cụm."""
    out = np.zeros(n, np.float32)
    t = 0.0
    while t < n / SR:
        cum = rng.integers(1, 5)
        for _ in range(cum):
            m = so_mau(rng.uniform(0.002, 0.012))
            s = on_trang(m, rng) * np.exp(-np.linspace(0, 6, m)).astype(np.float32)
            f = rng.uniform(900, 4500) if rng.random() < .8 else rng.uniform(300, 800)
            s = cong_huong(np.pad(s, (0, so_mau(0.02))), f, rng.uniform(2, 6))
            dat_vao(out, s * rng.uniform(0.15, 1.0) ** 1.5 * co, so_mau(t + rng.uniform(0, 0.05)))
        t += rng.exponential(1 / mat_do)
    return lp(out, 6500)


def ao_lua(n, rng, co=1.0):
    """Tiếng 'phừng phừng' của đám lửa: ồn trầm, chập chờn."""
    base = on_hong(n, rng)
    flick = muot_ngau_nhien(n, rng, 6, 0.55, 1.0) * muot_ngau_nhien(n, rng, 0.4, 0.6, 1.0)
    roar = lp(hp(base, 60), 380 + 300 * co) * flick
    hiss = hp(on_trang(n, rng), 3000) * 0.05 * muot_ngau_nhien(n, rng, 2, 0.3, 1.0)
    return (roar + hiss).astype(np.float32)


# ------------------------------------------------------------------ gỗ, kim loại
def go_go(rng, f=None, cung=1.0):
    """Tiếng gõ gỗ ngắn (cọc, quân cờ sa bàn, then chèo)."""
    f = f or rng.uniform(550, 950)
    m = so_mau(0.12)
    y = _mo(m, [f, f * 2.7, f * 5.2], [1, .4, .15], [0.035 * cung, 0.012, 0.006], rng)
    th = lp(on_trang(m, rng), 300) * bao_exp(m, 0.001, 0.02) * 0.6
    return mo_dan((y + th).astype(np.float32), 0.0008, 0.02)


def _mo(m, fs, amps, taus, rng):
    return modal(m, fs, amps, taus, rng=rng)


def leng_keng(rng, f=None):
    """Tiếng kim loại nhỏ va nhau (binh khí trong trại, nồi niêu ở chợ) – nhẹ."""
    f = f or rng.uniform(1800, 3200)
    m = so_mau(0.35)
    y = _mo(m, [f, f * 1.51, f * 2.37, f * 3.1], [1, .6, .35, .2], [0.12, 0.08, 0.05, 0.03], rng)
    return lp(mo_dan(y, 0.0008, 0.05), 6000)


def phap_phoi(n, rng, manh=1.0):
    """Cờ bay phần phật: tiếng ồn điều biên bởi nhịp đập 5–12 Hz không đều."""
    t = truc_tg(n)
    rate = muot_ngau_nhien(n, rng, 0.5, 5, 11)
    ph = 2 * np.pi * np.cumsum(rate) / SR
    flap = np.maximum(np.sin(ph), 0) ** 6 * muot_ngau_nhien(n, rng, 0.6, 0.3, 1.0)
    y = bp(on_trang(n, rng), 180, 2600) * (0.25 + flap) * manh
    return y.astype(np.float32)


def buoc_chan(rng, nang=1.0):
    """Một bước chân trên đất (đơn): tiếng 'thịch' trầm + sạo sạo nhỏ."""
    m = so_mau(0.12)
    th = lp(on_trang(m, rng), rng.uniform(220, 420) / nang) * bao_exp(m, 0.004, 0.025 * nang)
    sc = bp(on_trang(m, rng), 1500, 4000) * bao_exp(m, 0.002, 0.012) * 0.15
    return (th + sc).astype(np.float32)
