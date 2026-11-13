"""Âm thanh sự kiện (một lần): trống trận, cồng chiêng, trống đồng, tù và, mũi tên, đoàn quân, vó ngựa, thuyền, cọc gỗ,
nước bắn, mái chèo, lửa bùng, gươm (nhẹ), pháo/nổ (chỉ thời cận – hiện đại), tiếng hô, đào đắp, đá kéo, máy hơi nước…
Mỗi hàm nhận rng (numpy Generator) và trả về mảng stereo (N, 2) float32, đỉnh chuẩn về 0 dBFS (mức thật do bộ trộn đặt).
Nguyên tắc cho học sinh: không có tiếng chát/giật mình – mọi tiếng đều có tấn công mềm, cắt cao tần, đặt ở xa có vang."""
import math
import numpy as np
from .dsp import (SR, so_mau, truc_tg, on_trang, on_hong, on_nau, lp, hp, bp, cong_huong, loc_quet, bao_exp,
                  bao_hinh_chuong, mo_dan, pan, pan_dong, stereo, vang, modal, chuan_dinh, dat_vao, muot_ngau_nhien,
                  bao_hoa_mem, rang_cua, lp_dong, thanh_stereo)
from . import nguon


def _xong(x, dinh=0.0):
    x = hp(thanh_stereo(np.asarray(x, np.float32)), 24)        # chặn DC / hạ âm
    x = mo_dan(x, 0.0, 0.03)
    return chuan_dinh(x, dinh)


# ================================================================== trống, cồng, chiêng
def _mot_trong(rng, f0=None, luc=1.0, kich=1.0):
    """Một tiếng trống da lớn (mono): dao động riêng của mặt trống tròn + tiếng da bật + tiếng thùng."""
    f0 = f0 or rng.uniform(62, 80)
    n = so_mau(2.0 * kich)
    r = [1.0, 1.593, 2.136, 2.296, 2.653, 2.918, 3.156, 3.501]
    a = np.array([1.0, .5, .32, .22, .15, .10, .07, .05]) * np.array([1] + [luc ** .6] * 7)
    tau = np.array([.50, .26, .19, .15, .11, .09, .075, .06]) * kich
    body = modal(n, [f0 * x * rng.uniform(.995, 1.005) for x in r], a, tau, truot=0.3 * luc, truot_tg=0.045, rng=rng)
    m = so_mau(0.05)
    slap = np.zeros(n, np.float32)
    slap[:m] = bp(on_trang(m, rng), 500, 2600 + 900 * luc) * bao_exp(m, 0.0015, 0.010) * 0.35 * luc
    thump = lp(on_trang(n, rng), 140) * bao_exp(n, 0.003, 0.07) * 0.8
    y = body + slap + thump
    return bao_hoa_mem(y / (np.max(np.abs(y)) + 1e-9), 0.8)


def trong_tran(rng, luc=1.0, xa=0.3):
    """Một tiếng trống trận ('tùng'), vang ngoài trời."""
    y = _mot_trong(rng, luc=luc)
    y = lp(y, 5000 - 2500 * xa)
    return _xong(vang(pan(y, rng.uniform(-.15, .15)), t60=1.8 + xa, uot=0.25 + 0.35 * xa, hat=1))


def trong_hoi(rng, kieu="don", dai=3.0, xa=0.35):
    """Chuỗi trống: 'don' (trống dồn: chậm → nhanh, mạnh dần, chốt 2 tiếng), 'hanh_quan' (nhịp đều có nhấn),
    'hieu_lenh' (3 tiếng trống lệnh), 'thuc' (thúc quân: nhịp đôi dồn dập vừa phải)."""
    times, vels = [], []
    if kieu == "hieu_lenh":
        times = [0, .55, 1.1]; vels = [.8, .85, 1.0]
    elif kieu == "hanh_quan":
        t = 0.0; k = 0
        while t < dai: times.append(t); vels.append(1.0 if k % 4 == 0 else .62); t += .5 + rng.normal(0, .008); k += 1
    elif kieu == "thuc":
        t = 0.0; k = 0
        while t < dai: times += [t, t + .17]; vels += [.95, .7]; t += .55 + rng.normal(0, .01); k += 1
    else:
        t = 0.0; gap = 0.5
        while t < dai - 0.6:
            times.append(t); vels.append(0.45 + 0.5 * (t / dai)); t += gap + rng.normal(0, .006); gap = max(0.11, gap * 0.86)
        times += [t + .1, t + .55]; vels += [1.0, 1.0]
    n = so_mau(max(times) + 2.2)
    out = np.zeros(n, np.float32)
    f0 = rng.uniform(64, 78)
    for t, v in zip(times, vels):
        dat_vao(out, _mot_trong(rng, f0=f0 * rng.uniform(.98, 1.02), luc=v * rng.uniform(.9, 1.05), kich=0.8) * v, so_mau(t))
    out = lp(out, 5000 - 2500 * xa)
    return _xong(vang(pan(out, rng.uniform(-.1, .1)), t60=2.0 + xa, uot=0.25 + 0.35 * xa, hat=1))


def cong(rng, f0=None, xa=0.2):
    """Cồng/chiêng có núm: âm chính rõ, các bội gần hoà âm, phách nhẹ, ngân 4–5 s."""
    f0 = f0 or rng.uniform(170, 240)
    n = so_mau(5.5)
    r = [1.0, 1.004, 2.0, 2.012, 2.98, 4.16, 5.43, 6.79]
    a = [1.0, .5, .45, .25, .22, .12, .07, .04]
    tau = [3.2, 3.0, 1.9, 1.7, 1.2, .8, .55, .4]
    y = modal(n, [f0 * x for x in r], a, tau, truot=-0.012, truot_tg=0.4, rng=rng)
    y *= np.minimum(truc_tg(n) / 0.006, 1)
    m = so_mau(0.03); y[:m] += lp(on_trang(m, rng), 900) * bao_exp(m, 0.002, 0.008) * 0.4
    y = lp(y, 6000 - 2000 * xa)
    return _xong(vang(pan(y, rng.uniform(-.1, .1)), t60=2.6, uot=0.3 + 0.3 * xa, hat=2))


def trong_dong(rng, f0=None):
    """Trống đồng Đông Sơn: tiếng đồng trầm, ngân dài (dao động riêng không hoà âm) + tiếng 'thùm' của mặt trống."""
    f0 = f0 or rng.uniform(96, 110)
    n = so_mau(5.0)
    r = [1.0, 1.47, 1.98, 2.43, 2.91, 3.62, 4.38, 5.3, 6.6]
    a = [1.0, .55, .5, .35, .28, .18, .12, .08, .05]
    tau = [2.6, 2.0, 1.6, 1.2, 1.0, .7, .5, .35, .25]
    y = modal(n, [f0 * x * rng.uniform(.997, 1.003) for x in r], a, tau, truot=0.04, truot_tg=0.08, rng=rng)
    dat_vao(y, _mot_trong(rng, f0=f0 * 0.62, luc=0.7, kich=1.2), 0, 0.7)
    y *= np.minimum(truc_tg(n) / 0.004, 1)
    y = lp(y, 5500)
    return _xong(vang(y, t60=3.2, uot=0.4, rong=1.3, hat=3))


def tu_va(rng, dai=None, xa=0.5):
    """Tù và (sừng trâu) thổi hiệu lệnh: âm đồng thau ấm, tấn công chậm, hơi lên giọng đầu tiếng."""
    dai = dai or rng.uniform(1.6, 2.4)
    n = so_mau(dai); u = np.linspace(0, 1, n, dtype=np.float32)
    f0 = rng.uniform(210, 260) * (1 - 0.05 * np.exp(-u * dai / 0.15)) * (1 + 0.006 * np.sin(2 * np.pi * 5 * u * dai))
    src = rang_cua(f0) + 0.03 * on_trang(n, rng)
    y = cong_huong(src, 650, 3) + .7 * cong_huong(src, 1300, 4) + .3 * cong_huong(src, 2400, 6)
    e = np.minimum(u * dai / 0.18, 1) * np.minimum((1 - u) * dai / 0.5, 1)
    y = lp(y * e, 3000 - 1200 * xa)
    return _xong(vang(pan(y, rng.uniform(-.3, .3)), t60=3.0, uot=0.35 + 0.3 * xa, hat=4))


def chuong_chua(rng, f0=None):
    """Chuông chùa lớn ở xa: hum – prime – tierce – quint – nominal, ngân rất dài, tấn công mềm (dùi gỗ)."""
    f0 = f0 or rng.uniform(140, 180)
    n = so_mau(7.0)
    r = [0.5, 1.0, 1.19, 1.5, 2.0, 2.52, 2.66, 3.01]
    a = [.8, 1.0, .5, .3, .45, .2, .15, .1]
    tau = [5.5, 4.0, 3.0, 2.5, 2.0, 1.2, 1.0, .7]
    y = modal(n, [f0 * x for x in r], a, tau, rng=rng) * np.minimum(truc_tg(n) / 0.01, 1)
    return _xong(vang(lp(y, 3500), t60=3.5, uot=0.45, hat=5))


# ================================================================== quân, ngựa, voi
def mui_ten(rng, so=18, huong=None, xa=0.3):
    """Loạt tên bắn: tiếng dây cung bật trầm + nhiều mũi tên vút (lọc quét dần xuống) bay ngang + cắm đất xa."""
    huong = huong if huong is not None else (1 if rng.random() < .5 else -1)
    n = so_mau(2.2); out = np.zeros((n, 2), np.float32)
    for k in range(so):
        t0 = rng.uniform(0, 0.4) + (0.0 if k < so * .7 else 0.15)
        # dây cung
        m = so_mau(0.15); tw = modal(m, [rng.uniform(85, 150)], [1], [0.04], rng=rng) * 0.25
        dat_vao(out, pan(tw, -0.6 * huong + rng.uniform(-.2, .2)), so_mau(t0))
        # mũi tên bay
        d = rng.uniform(0.28, 0.55); m = so_mau(d)
        fc = np.linspace(rng.uniform(3200, 4200), rng.uniform(1200, 1800), 16)
        w = loc_quet(on_trang(m, rng), fc, bw_oct=0.7) * bao_hinh_chuong(m, rng.uniform(.45, .7), 1.5)
        p0 = -0.7 * huong + rng.uniform(-.2, .2); p1 = 0.7 * huong + rng.uniform(-.2, .2)
        dat_vao(out, pan_dong(w * rng.uniform(0.5, 1.0), p0, p1), so_mau(t0 + 0.04))
        # cắm xuống
        if rng.random() < .6:
            m = so_mau(0.06); th = lp(on_trang(m, rng), 900) * bao_exp(m, 0.002, 0.012) * 0.3
            dat_vao(out, pan(th, p1), so_mau(t0 + d + rng.uniform(0.0, .25)))
    out = lp(out, 7000 - 2500 * xa)
    return _xong(vang(out, t60=1.4, uot=0.15 + 0.3 * xa, hat=6))


def quan_tien(rng, dai=3.0, manh=1.0, p0=-0.5, p1=0.5, xa=0.3):
    """Đoàn quân tiến: rền trầm + rất nhiều bước chân (hạt) + leng keng khí giới rất nhỏ + vút nhẹ theo hướng mũi tên."""
    n = so_mau(dai + 0.6)
    e = bao_hinh_chuong(n, 0.45, 1.2)
    rumble = lp(on_nau(n, rng), 160 + 60 * manh) * e * 0.9
    steps = np.zeros(n, np.float32)
    t = 0.0
    while t < dai + 0.5:
        g = float(e[min(so_mau(t), n - 1)])
        dat_vao(steps, nguon.buoc_chan(rng, nang=rng.uniform(.8, 1.4)) * rng.uniform(.2, .6) * g, so_mau(t))
        t += rng.exponential(1 / (22 + 25 * manh))
    gear = np.zeros(n, np.float32)
    for _ in range(int(dai * 2.5 * manh)):
        dat_vao(gear, nguon.leng_keng(rng) * rng.uniform(.03, .08), so_mau(rng.uniform(0, dai)))
    fc = np.linspace(260, 700 + 250 * manh, 12) * np.r_[np.linspace(1, 1.25, 6), np.linspace(1.25, .9, 6)]
    wh = loc_quet(on_hong(n, rng), fc, bw_oct=1.4) * e * 0.35
    mono = rumble + steps * 0.8 + gear + wh
    out = pan_dong(mono, p0, p1) * 0.7 + pan(mono, 0) * 0.3
    out = lp(out, 4500 - 1800 * xa)
    return _xong(vang(out, t60=1.6, uot=0.2 + 0.3 * xa, hat=7))


def rut_chay(rng, dai=2.5, p0=0.3, p1=-0.6):
    """Quân thua rút chạy: vút trầm đi xuống + bước chân rời rạc thưa dần."""
    n = so_mau(dai + 0.5)
    e = bao_hinh_chuong(n, 0.25, 1.0)
    fc = np.linspace(900, 250, 12)
    wh = loc_quet(on_hong(n, rng), fc, bw_oct=1.3) * e * 0.5
    steps = np.zeros(n, np.float32); t = 0.0
    while t < dai:
        g = float(e[min(so_mau(t), n - 1)])
        dat_vao(steps, nguon.buoc_chan(rng) * rng.uniform(.3, .7) * g, so_mau(t))
        t += rng.exponential(1 / 14)
    out = pan_dong(wh + steps, p0, p1)
    return _xong(vang(lp(out, 3500), t60=1.5, uot=0.3, hat=7))


def vo_ngua(rng, dai=3.0, so_ngua=1, p0=-0.6, p1=0.6, xa=0.3):
    """Vó ngựa phi (nước đại 4 nhịp) trên đất, đi ngang qua; nhiều ngựa = kỵ binh (rền hơn)."""
    n = so_mau(dai + 0.5)
    e = bao_hinh_chuong(n, 0.5, 1.0)
    mono = np.zeros(n, np.float32)
    for h in range(so_ngua):
        stride = rng.uniform(0.40, 0.48); off = rng.uniform(0, stride)
        pat = np.array([0, .085, .19, .27]) * stride / 0.45
        amp = np.array([.75, .9, .7, 1.0])
        t = off
        while t < dai:
            for dt, a in zip(pat, amp):
                tt = t + dt + rng.normal(0, .004)
                if tt >= dai: break
                m = so_mau(0.09)
                hit = lp(on_trang(m, rng), rng.uniform(500, 900)) * bao_exp(m, 0.0015, 0.018)
                hit += modal(m, [rng.uniform(95, 135)], [0.9], [0.03], rng=rng)
                if rng.random() < .5:
                    hit[:so_mau(.004)] += bp(on_trang(so_mau(.004), rng), 1500, 3000) * .25
                dat_vao(mono, hit * a * rng.uniform(.75, 1.0) * float(e[min(so_mau(tt), n - 1)]), so_mau(tt))
            t += stride
    if so_ngua > 2:
        mono += lp(on_nau(n, rng), 120) * e * 0.25 * min(so_ngua / 6, 1.0)
    out = pan_dong(lp_dong(mono, 2500, 1200), p0, p1)
    out = lp(out, 4500 - 1500 * xa)
    return _xong(vang(out, t60=1.4, uot=0.15 + 0.3 * xa, hat=8))


def buoc_nang(rng, dai=3.0, xa=0.3):
    """Bước chân nặng (voi chiến) – tiếng thình thịch rất trầm, chậm, đất rung nhẹ."""
    n = so_mau(dai + 1.0); mono = np.zeros(n, np.float32); t = 0.0
    while t < dai:
        m = so_mau(0.4)
        hit = lp(on_trang(m, rng), 120) * bao_exp(m, 0.01, 0.08) + modal(m, [rng.uniform(38, 50)], [1.2], [0.12], rng=rng)
        dat_vao(mono, hit * rng.uniform(.7, 1.0), so_mau(t)); t += rng.uniform(0.55, 0.75)
    return _xong(vang(pan(lp(mono, 400), rng.uniform(-.4, .4)), t60=1.6, uot=0.2 + 0.3 * xa, hat=8))


# ================================================================== thuyền, gỗ, nước
def cot_ket(rng, dai=None):
    """Thân thuyền gỗ kêu cót két: chuỗi xung ma sát (nhanh/chậm thay đổi) qua cộng hưởng thân gỗ."""
    dai = dai or rng.uniform(0.7, 1.6)
    n = so_mau(dai); u = np.linspace(0, 1, n, dtype=np.float32)
    rate = muot_ngau_nhien(n, rng, 3, 18, 110)
    ph = np.cumsum(rate / SR)
    imp = np.zeros(n, np.float32)
    idx = np.nonzero(np.diff(np.floor(ph)) > 0)[0]
    imp[idx] = rng.uniform(0.4, 1.0, len(idx))
    y = sum(cong_huong(imp, f * rng.uniform(.9, 1.1), q) * g for f, q, g in [(310, 10, 1.0), (560, 12, .8), (920, 14, .5), (1550, 16, .25)])
    y *= np.clip(np.sin(np.pi * u), 0, 1) ** 0.7
    y = lp(y, 3000)
    return _xong(vang(pan(y, rng.uniform(-.5, .5)), t60=0.9, uot=0.25, hat=9))


def go_nut(rng, to=1.0):
    """Gỗ gãy / vỡ toác (thuyền va cọc): một tiếng 'rắc' chính (tấn công 1 ms, cắt cao tần) + chuỗi vụn nhỏ + tiếng 'thụp'."""
    n = so_mau(1.6)
    out = np.zeros(n, np.float32)
    m = so_mau(0.03)
    main = on_trang(m, rng) * bao_exp(m, 0.001, 0.006)
    out[:m] += sum(cong_huong(main, f, 4) for f in rng.uniform(500, 2400, 3)) * 0.8
    t = 0.01; rate = 60.0
    while t < 0.9 * to:
        mm = so_mau(rng.uniform(0.002, 0.01))
        c = on_trang(mm, rng) * np.exp(-np.linspace(0, 5, mm)).astype(np.float32)
        c = cong_huong(np.pad(c, (0, so_mau(0.015))), rng.uniform(450, 2600), rng.uniform(3, 8))
        dat_vao(out, c * rng.uniform(.1, .7) * math.exp(-t / (0.35 * to)), so_mau(t))
        t += rng.exponential(1 / rate); rate *= 0.97
    th = lp(on_trang(so_mau(0.3), rng), 160) * bao_exp(so_mau(0.3), 0.004, 0.07)
    out[:len(th)] += th * 0.8 * to
    out = lp(out, 5500)
    return _xong(vang(pan(out, rng.uniform(-.4, .4)), t60=1.2, uot=0.25, hat=10))


def dong_coc(rng, so=4, xa=0.3):
    """Đóng cọc gỗ: các nhát 'cộc' trầm cách nhau ~0.6 s (vồ gỗ nện đầu cọc)."""
    n = so_mau(so * 0.62 + 1.0); out = np.zeros(n, np.float32)
    for k in range(so):
        m = so_mau(0.25)
        h = nguon.go_go(rng, f=rng.uniform(260, 380), cung=2.0)[:m]
        h = np.pad(h, (0, m - len(h))) + lp(on_trang(m, rng), 180) * bao_exp(m, 0.003, 0.05) * 0.9
        dat_vao(out, h * rng.uniform(.8, 1.0), so_mau(k * 0.62 + rng.normal(0, .02)))
    return _xong(vang(pan(lp(out, 4000), rng.uniform(-.3, .3)), t60=1.5, uot=0.2 + 0.3 * xa, hat=10))


def te_nuoc(rng, to=1.0):
    """Nước bắn / vật rơi xuống nước: thân tiếng (ồn lọc quét xuống) + tiếng 'tõm' trầm + nhiều bọt nước."""
    d = 0.5 + 0.4 * to; n = so_mau(d + 0.4)
    m = so_mau(d)
    body = loc_quet(on_trang(m, rng), np.linspace(2200, 600, 10) * (1.2 - 0.3 * to), bw_oct=1.8) * bao_exp(m, 0.008, 0.12 * to + 0.05)
    out = np.zeros(n, np.float32); out[:m] += body
    plop = modal(so_mau(0.2), [rng.uniform(80, 150) / to], [1], [0.04], truot=0.5, rng=rng)
    out[:len(plop)] += plop * 0.6
    for _ in range(int(25 * to)):
        tt = rng.exponential(0.12 * to)
        if tt < d: dat_vao(out, nguon.bot_nuoc(rng) * rng.uniform(0.05, 0.3), so_mau(tt + 0.02))
    out = lp(out, 7000)
    return _xong(vang(pan(out, rng.uniform(-.3, .3)), t60=1.0, uot=0.2, hat=11))


def mai_cheo(rng, dai=4.0, gap=False, so_cheo=4, xa=0.3):
    """Mái chèo khua nước: mỗi nhịp có tiếng then chèo gõ gỗ, tiếng xé nước, tiếng nước nhỏ giọt. Nhiều tay chèo hơi lệch nhịp."""
    n = so_mau(dai + 1.0); out = np.zeros((n, 2), np.float32)
    chu_ky = rng.uniform(0.75, 0.9) if gap else rng.uniform(1.25, 1.6)
    for c in range(so_cheo):
        p = rng.uniform(-.8, .8); t = rng.uniform(0, 0.08) + (0.0 if c % 2 == 0 else 0.02)
        mono = np.zeros(n, np.float32)
        while t < dai:
            dat_vao(mono, nguon.go_go(rng, f=rng.uniform(700, 1100)) * 0.18, so_mau(t))                 # then chèo
            m = so_mau(0.42); sw = bp(on_trang(m, rng), 300, 1400) * bao_hinh_chuong(m, .3, 1.5) * 0.55
            dat_vao(mono, sw, so_mau(t + 0.05))                                                          # xé nước
            for _ in range(rng.integers(2, 6)):
                dat_vao(mono, nguon.bot_nuoc(rng) * rng.uniform(.05, .2), so_mau(t + rng.uniform(.3, .7)))
            t += chu_ky * rng.uniform(.97, 1.03)
        out += pan(mono, p)
    out = lp(out, 6000 - 2000 * xa)
    return _xong(vang(out, t60=1.0, uot=0.15 + 0.25 * xa, hat=11))


def nuoc_re(rng, dai=3.0, to=1.0, p0=-0.4, p1=0.4):
    """Thuyền lớn rẽ nước: tiếng ồn nước xô ở mũi thuyền, sóng lan, có lúc dâng lúc lắng."""
    n = so_mau(dai)
    e = bao_hinh_chuong(n, 0.5, 0.8) * muot_ngau_nhien(n, rng, 1.2, 0.6, 1.0)
    y = bp(on_hong(n, rng), 180, 1400 + 600 * to) * e
    y += nguon.vo_bo(n, rng, mat_do=1.5) * 0.6 * e
    return _xong(pan_dong(lp(y, 4000), p0, p1))


# ================================================================== lửa, binh khí, hoả khí
def lua_bung(rng, to=1.0):
    """Lửa bùng lên (bè lửa bắt cháy): 'phừng' – ồn quét lên nhanh rồi cháy đều, lách tách; cắt cao tần để không chói."""
    d = 2.2; n = so_mau(d)
    fc = np.r_[np.linspace(180, 1300, 4), np.linspace(1300, 700, 12)]
    roar = loc_quet(on_hong(n, rng), fc, bw_oct=2.2)
    e = np.minimum(truc_tg(n) / 0.18, 1) * (0.35 + 0.65 * np.exp(-truc_tg(n) / 0.7))
    whomp = modal(so_mau(0.4), [55], [1], [0.09], truot=0.6, rng=rng)
    y = roar * e; y[:len(whomp)] += whomp * 0.5
    y += nguon.lach_tach(n, rng, mat_do=12 * to, co=0.8) * 0.5
    y = lp(y, 5000)
    return _xong(vang(pan(y, rng.uniform(-.3, .3)), t60=1.2, uot=0.2, hat=12))


def guom(rng, so=3, xa=0.45):
    """Gươm giáo chạm nhau – NHẸ và ở xa (không chát): dao động kim loại tắt nhanh + tiếng miết."""
    n = so_mau(so * 0.6 + 1.0); out = np.zeros((n, 2), np.float32); t = 0.0
    for k in range(so):
        m = so_mau(0.5); f = rng.uniform(1700, 2600)
        y = modal(m, [f, f * 1.61, f * 2.27, f * 2.9], [1, .6, .4, .2], [.18, .12, .08, .05], rng=rng)
        sc = bp(on_trang(m, rng), 2500, 6000) * bao_exp(m, 0.002, 0.03) * 0.25
        thp = lp(on_trang(m, rng), 400) * bao_exp(m, 0.002, 0.02) * 0.5
        y = (y + sc + thp) * np.minimum(truc_tg(m) / 0.0015, 1)
        dat_vao(out, pan(y * rng.uniform(.6, 1.0), rng.uniform(-.6, .6)), so_mau(t))
        t += rng.uniform(0.28, 0.65)
    out = lp(out, 6500 - 3000 * xa)
    return _xong(vang(out, t60=1.3, uot=0.2 + 0.35 * xa, hat=13))


def phao(rng, xa=0.6):
    """Đại bác bắn ở xa (CHỈ dùng cho thời kì có hoả khí): tiếng ùm trầm, tấn công mềm, vọng lại."""
    n = so_mau(3.5)
    boom = modal(n, [rng.uniform(40, 52)], [1], [0.45], truot=0.8, truot_tg=0.08, rng=rng)
    body = lp(on_trang(n, rng), 350) * bao_exp(n, 0.012, 0.35) * 1.2
    crack = lp(on_trang(n, rng), 1800 - 800 * xa) * bao_exp(n, 0.004, 0.04) * 0.35
    y = boom + body + crack
    echo = np.zeros(n, np.float32); dat_vao(echo, lp(y, 600) * 0.3, so_mau(rng.uniform(0.35, 0.7)))
    y = lp(y + echo, 3000 - 1200 * xa) * np.minimum(truc_tg(n) / 0.01, 1)
    return _xong(vang(pan(y, rng.uniform(-.5, .5)), t60=3.0, uot=0.35 + 0.25 * xa, hat=14))


def no(rng, xa=0.6):
    """Tiếng nổ ở xa (bom, đồn bị phá – CHỈ thời cận – hiện đại): ầm trầm + đất đá rơi lả tả, không chói."""
    n = so_mau(4.0)
    y = lp(on_nau(n, rng), 300) * bao_exp(n, 0.02, 0.6) * 1.4
    y += modal(n, [rng.uniform(35, 45)], [1], [0.5], truot=0.6, rng=rng)
    debris = np.zeros(n, np.float32)
    for _ in range(40):
        dat_vao(debris, lp(on_trang(so_mau(0.03), rng), 2000) * bao_exp(so_mau(0.03), .001, .008) * rng.uniform(.05, .2), so_mau(rng.uniform(0.4, 2.5)))
    y = lp(y + debris, 2500 - 1000 * xa) * np.minimum(truc_tg(n) / 0.02, 1)
    return _xong(vang(pan(y, rng.uniform(-.5, .5)), t60=3.0, uot=0.4, hat=15))


def sung_xa(rng, dai=3.0):
    """Tiếng súng nổ lác đác rất xa (thời hiện đại) – trầm, đục."""
    n = so_mau(dai + 1.0); out = np.zeros(n, np.float32); t = rng.uniform(0, .3)
    while t < dai:
        m = so_mau(0.25); s = lp(on_trang(m, rng), 900) * bao_exp(m, 0.003, 0.05)
        dat_vao(out, s * rng.uniform(.3, 1.0), so_mau(t)); t += rng.exponential(0.35)
    return _xong(vang(pan(out, rng.uniform(-.6, .6)), t60=2.5, uot=0.5, hat=15))


def coi_tau(rng):
    """Còi tàu thuỷ hơi nước ở xa (thời cận – hiện đại): hợp âm trầm, êm."""
    d = 2.4; n = so_mau(d); u = np.linspace(0, 1, n)
    y = sum(rang_cua(np.full(n, f)) * g for f, g in [(146.8, 1), (185.0, .8), (220.0, .6)])
    y = lp(y, 1200) * (np.minimum(u * d / 0.2, 1) * np.minimum((1 - u) * d / 0.6, 1))
    return _xong(vang(pan(y.astype(np.float32), .2), t60=3.0, uot=0.5, hat=16))


# ================================================================== người, lao động, máy
def ho_reo(rng, kieu="xung_tran", so=18, xa=0.5):
    """Tiếng hô đồng thanh/reo hò của nhiều người ở xa (không có tiếng kêu đau, không thét)."""
    d = {"xung_tran": 2.2, "reo": 3.3, "hieu_lenh": 1.0}[kieu]
    n = so_mau(d + 0.6)
    y = nguon.giong_ho(n, rng, so_nguoi=so, kieu=kieu)
    y = lp(y, 2600 - 1200 * xa)
    return _xong(vang(y, t60=2.0, uot=0.25 + 0.35 * xa, rong=1.3, hat=17))


def dao_dat(rng, dai=3.0):
    """Cuốc xẻng, đắp luỹ: nhịp xẻng xắn đất + đất đổ, nhiều người lệch nhịp."""
    n = so_mau(dai + 0.6); out = np.zeros((n, 2), np.float32)
    for w in range(4):
        p = rng.uniform(-.7, .7); t = rng.uniform(0, .6); mono = np.zeros(n, np.float32)
        while t < dai:
            m = so_mau(0.18); sc = bp(on_trang(m, rng), 800, 3000) * bao_exp(m, 0.01, 0.05) * .4
            th = lp(on_trang(m, rng), 300) * bao_exp(m, 0.003, 0.04)
            dat_vao(mono, sc + th, so_mau(t))
            m2 = so_mau(0.35); dirt = bp(on_trang(m2, rng), 300, 2000) * bao_hinh_chuong(m2, .2, 1) * .3
            dat_vao(mono, dirt, so_mau(t + .5)); t += rng.uniform(1.0, 1.5)
        out += pan(mono, p)
    return _xong(vang(lp(out, 5000), t60=1.2, uot=0.3, hat=18))


def da_keo(rng):
    """Khối đá lớn được kéo trên gỗ lăn rồi đặt xuống: tiếng rền ma sát + tiếng 'thịch' nặng."""
    n = so_mau(2.4)
    scrape = bp(on_hong(n, rng), 120, 900) * bao_hinh_chuong(n, .4, 1) * muot_ngau_nhien(n, rng, 8, .4, 1)
    m = so_mau(0.6); th = lp(on_trang(m, rng), 150) * bao_exp(m, 0.006, 0.09) + modal(m, [rng.uniform(45, 60)], [1], [.1], rng=rng)
    y = scrape * 0.5; dat_vao(y, th * 1.2, so_mau(1.7))
    return _xong(vang(pan(lp(y, 3000), rng.uniform(-.3, .3)), t60=1.8, uot=0.25, hat=19))


def hoi_nuoc(rng, to=1.0):
    """Một nhịp xả hơi của máy hơi nước ('xình'): ồn dải rộng tắt nhanh + tiếng kim loại nhẹ."""
    n = so_mau(0.6)
    y = bp(on_trang(n, rng), 400, 4500) * bao_exp(n, 0.012, 0.09) * to
    dat_vao(y, nguon.leng_keng(rng, f=rng.uniform(900, 1300)), 0, 0.08)
    return _xong(pan(lp(y, 6000), rng.uniform(-.2, .2)))


def giay(rng, dai=0.9):
    """Tấm bản đồ giấy được trải ra / sa bàn mở: tiếng giấy sột soạt nhẹ."""
    n = so_mau(dai); out = np.zeros(n, np.float32); t = 0.0
    e = bao_hinh_chuong(n, 0.35, 1.0)
    while t < dai:
        m = so_mau(rng.uniform(0.004, 0.02))
        c = bp(on_trang(m, rng), rng.uniform(1500, 3000), rng.uniform(5000, 8000)) * np.hanning(m).astype(np.float32)
        dat_vao(out, c * rng.uniform(.2, 1.0) * float(e[min(so_mau(t), n - 1)]), so_mau(t))
        t += rng.exponential(0.006)
    out += lp(on_hong(n, rng), 900) * e * 0.15
    return _xong(vang(pan(lp(out, 7500), rng.uniform(-.2, .2)), t60=0.6, uot=0.15, hat=20))


def quan_co(rng):
    """Đặt quân cờ/kí hiệu gỗ lên sa bàn: tiếng 'cộc' gỗ nhỏ, ấm."""
    y = nguon.go_go(rng, f=rng.uniform(480, 720), cung=1.3)
    return _xong(vang(pan(y, rng.uniform(-.4, .4)), t60=0.5, uot=0.12, hat=21))


def co_bay(rng, dai=3.0):
    """Cờ bay phần phật trong gió."""
    n = so_mau(dai)
    y = nguon.phap_phoi(n, rng) * bao_hinh_chuong(n, .5, .6)
    return _xong(pan(lp(y, 4000), rng.uniform(-.5, .5)))


def gio_cuon(rng, dai=2.0, p0=-0.7, p1=0.7):
    """Một cơn gió cuốn qua (lọc quét lên rồi xuống, di chuyển trái → phải)."""
    n = so_mau(dai)
    fc = np.r_[np.linspace(250, 1100, 6), np.linspace(1100, 300, 8)]
    y = loc_quet(on_hong(n, rng), fc, bw_oct=1.6) * bao_hinh_chuong(n, .45, 1.2)
    return _xong(pan_dong(y, p0, p1))


def sam(rng):
    """Sấm rền ở rất xa (không có tiếng sét đánh gần)."""
    n = so_mau(5.0)
    y = lp(on_nau(n, rng), 160) * bao_hinh_chuong(n, .2, .8) * muot_ngau_nhien(n, rng, 4, .4, 1)
    return _xong(vang(pan(y, rng.uniform(-.6, .6)), t60=3.0, uot=0.4, hat=22))


def leng_keng(rng, so=3):
    n = so_mau(so * 0.5 + 0.5); out = np.zeros((n, 2), np.float32)
    for _ in range(so):
        dat_vao(out, pan(nguon.leng_keng(rng), rng.uniform(-.7, .7)) * rng.uniform(.4, 1), so_mau(rng.uniform(0, so * 0.5)))
    return _xong(vang(out, t60=1.0, uot=0.2, hat=23))


def chim(rng, loai=None):
    y = nguon.tieng_chim(rng, loai)
    return _xong(vang(pan(lp(y, 6500), rng.uniform(-.8, .8)), t60=1.0, uot=0.25, hat=24))


# bảng tra: tên → (hàm, mức đỉnh mặc định dBFS ở bản trộn cuối (khi không có lời đọc), kênh 'nen' | 'ui')
BANG = {
    "trong_tran": (trong_tran, -17, "nen"), "trong_hoi": (trong_hoi, -17, "nen"), "cong": (cong, -18, "nen"),
    "trong_dong": (trong_dong, -16, "ui"), "tu_va": (tu_va, -20, "nen"), "chuong_chua": (chuong_chua, -21, "nen"),
    "mui_ten": (mui_ten, -20, "nen"), "quan_tien": (quan_tien, -19, "nen"), "rut_chay": (rut_chay, -22, "nen"),
    "vo_ngua": (vo_ngua, -19, "nen"), "buoc_nang": (buoc_nang, -19, "nen"), "cot_ket": (cot_ket, -21, "nen"),
    "go_nut": (go_nut, -18, "nen"), "dong_coc": (dong_coc, -19, "nen"), "te_nuoc": (te_nuoc, -19, "nen"),
    "mai_cheo": (mai_cheo, -21, "nen"), "nuoc_re": (nuoc_re, -22, "nen"), "lua_bung": (lua_bung, -18, "nen"),
    "guom": (guom, -22, "nen"), "phao": (phao, -17, "nen"), "no": (no, -17, "nen"), "sung_xa": (sung_xa, -24, "nen"),
    "coi_tau": (coi_tau, -22, "nen"), "ho_reo": (ho_reo, -19, "nen"), "dao_dat": (dao_dat, -21, "nen"),
    "da_keo": (da_keo, -19, "nen"), "hoi_nuoc": (hoi_nuoc, -21, "nen"), "giay": (giay, -24, "ui"),
    "quan_co": (quan_co, -18, "nen"), "co_bay": (co_bay, -23, "nen"), "gio_cuon": (gio_cuon, -21, "nen"),
    "sam": (sam, -22, "nen"), "leng_keng": (leng_keng, -25, "nen"), "chim": (chim, -26, "nen"),
}
