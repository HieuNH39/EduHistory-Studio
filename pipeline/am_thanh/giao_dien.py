"""Âm thanh giao diện (UI) – nhẹ, êm, có cao độ ngũ cung cho hợp chất liệu Việt:
tích (mốc trục thời gian), bóp (ý ghi nhớ), tích tắc đồng hồ (dừng hình hỏi), chuông báo đáp án, vút chuyển cảnh,
lấp lánh (ngôi sao chiến thắng), thẻ hiện ra, nhạc hiệu logo mở đầu / kết thúc, cổng thời gian trống đồng.
Kênh UI KHÔNG bị hạ âm theo lời đọc, nên mọi tiếng ở đây ngắn và nhỏ."""
import numpy as np
from .dsp import (SR, so_mau, truc_tg, on_trang, on_hong, lp, hp, bp, loc_quet, bao_exp, bao_hinh_chuong, mo_dan,
                  pan, pan_dong, stereo, vang, modal, chuan_dinh, dat_vao, thanh_stereo)
from . import su_kien

# thang ngũ cung (Hz) quanh C5: C D F G A C' D' F' G' A'
NGU_CUNG = [523.25, 587.33, 698.46, 783.99, 880.0, 1046.5, 1174.66, 1396.91, 1567.98, 1760.0]


def _xong(x, dinh=0.0):
    x = mo_dan(hp(thanh_stereo(np.asarray(x, np.float32)), 24), 0.0, 0.02)
    return chuan_dinh(x, dinh)


def dan_tranh(f0, dai=1.8, rng=None, nhan=0.0):
    """Tiếng gảy đàn tranh (tổng hợp cộng các hoạ âm): vị trí gảy gần ngựa đàn, hoạ âm cao tắt nhanh,
    'nhấn' = luyến cao độ (bán cung) đặc trưng."""
    n = so_mau(dai); t = truc_tg(n).astype(np.float64)
    bend = 1.0 if not nhan else 2 ** (nhan * np.clip((t - 0.25) / 0.25, 0, 1) * np.exp(-np.maximum(t - .5, 0) / .6) / 12)
    y = np.zeros(n)
    for k in range(1, 15):
        a = abs(np.sin(k * np.pi * 0.17)) / k ** 0.9
        tau = 1.5 / (1 + 0.35 * (k - 1))
        fk = k * f0 * np.sqrt(1 + 0.00025 * k * k)
        ph = 2 * np.pi * np.cumsum(fk * bend) / SR
        y += a * np.sin(ph) * np.exp(-t / tau)
    m = so_mau(0.004)
    if rng is not None: y[:m] += bp(on_trang(m, rng), 2000, 6000) * 0.15
    y *= np.minimum(t / 0.0015, 1)
    return y.astype(np.float32)


def _marimba(f0, dai=0.8):
    n = so_mau(dai)
    y = modal(n, [f0, f0 * 3.93, f0 * 9.2], [1, .25, .06], [0.32, 0.07, 0.025])
    return y * np.minimum(truc_tg(n) / 0.002, 1)


def _chuong(f0, dai=1.6):
    n = so_mau(dai)
    y = modal(n, [f0, f0 * 2.76, f0 * 5.40, f0 * 8.93], [1, .35, .15, .06], [1.1, .45, .2, .1])
    return y * np.minimum(truc_tg(n) / 0.0015, 1)


def tich(rng, bac=0):
    """Mốc trục thời gian hiện ra: tiếng gõ gỗ nhỏ + một nốt marimba ngũ cung đi lên theo thứ tự mốc."""
    f = NGU_CUNG[min(bac, len(NGU_CUNG) - 1)] / 2
    y = _marimba(f, 0.7) * 0.8
    m = so_mau(0.02); y[:m] += bp(on_trang(m, rng), 1800, 4000) * bao_exp(m, 0.0005, 0.003) * 0.25
    return _xong(vang(pan(y, -0.3 + 0.6 * (bac % 5) / 4), t60=0.7, uot=0.15, hat=30))


def bop(rng, bac=0):
    """Ý ghi nhớ hiện ra (có dấu tích xanh): tiếng 'bóp' mềm (cao độ rơi nhanh) + nốt chuông nhỏ."""
    n = so_mau(0.12); t = truc_tg(n)
    f = 950 * np.exp(-t / 0.03) + 380
    ph = 2 * np.pi * np.cumsum(f) / SR
    p = np.sin(ph) * bao_exp(n, 0.002, 0.03)
    c = _chuong(NGU_CUNG[min(bac + 2, len(NGU_CUNG) - 1)], 1.0) * 0.18
    y = np.zeros(len(c), np.float32); y[:n] += p; y[so_mau(0.03):] += c[:len(c) - so_mau(0.03)]
    return _xong(vang(pan(y, 0.0), t60=0.8, uot=0.15, hat=31))


def dong_ho(rng, tac=False):
    """Tích tắc đồng hồ (dừng hình – thử tài): tiếng 'tích' cao hoặc 'tắc' thấp, rất ngắn và mềm."""
    f = 1650 if tac else 2300
    n = so_mau(0.06)
    y = modal(n, [f, f * 1.48, f * 2.3], [1, .4, .2], [0.008, 0.005, 0.003], rng=rng)
    y += bp(on_trang(n, rng), 2000, 5000) * bao_exp(n, 0.0003, 0.002) * 0.3
    return _xong(pan(lp(y, 7000), 0.12 if tac else -0.12))


def chuong_bao(rng, dung=True):
    """Chuông báo lật đáp án: ba nốt chuông ngũ cung đi lên (vui, nhẹ)."""
    notes = [NGU_CUNG[0] * 2, NGU_CUNG[2] * 2, NGU_CUNG[4] * 2] if dung else [NGU_CUNG[3] * 2, NGU_CUNG[1] * 2]
    n = so_mau(2.2); y = np.zeros(n, np.float32)
    for k, f in enumerate(notes):
        dat_vao(y, _chuong(f, 1.8) * (0.8 + 0.1 * k), so_mau(k * 0.075))
    y = lp(y, 9000)
    return _xong(vang(y, t60=1.4, uot=0.25, rong=1.3, hat=32))


def vut(rng, dai=0.7, huong=1, sang=1.0):
    """Tiếng vút chuyển cảnh: ồn lọc quét lên rồi xuống, lướt từ trái sang phải (hoặc ngược lại)."""
    n = so_mau(dai)
    fc = np.r_[np.linspace(300, 2200 * sang, 7), np.linspace(2200 * sang, 700, 9)]
    y = loc_quet(on_hong(n, rng), fc, bw_oct=1.2) * bao_hinh_chuong(n, 0.55, 1.6)
    return _xong(pan_dong(lp(y, 6000), -0.6 * huong, 0.6 * huong))


def the_vao(rng):
    """Thẻ (trục thời gian / ghi nhớ / câu hỏi) hiện ra: vút ngắn + tiếng 'bộp' giấy dày êm."""
    a = vut(rng, 0.45, 1, 0.7) * 0.7
    n = so_mau(0.15); th = lp(on_trang(n, rng), 500) * bao_exp(n, 0.003, 0.03)
    y = np.zeros((len(a) + n, 2), np.float32); y[:len(a)] += a; dat_vao(y, pan(th, 0), so_mau(0.33), 0.6)
    return _xong(y)


def lap_lanh(rng):
    """Ngôi sao chiến thắng hiện ra: chuỗi nốt chuông nhỏ lấp lánh đi lên."""
    n = so_mau(2.0); y = np.zeros((n, 2), np.float32)
    for k, i in enumerate([4, 5, 6, 7, 8, 9]):
        dat_vao(y, pan(_chuong(NGU_CUNG[i] * 2, 1.2) * (0.5 + 0.08 * k), -0.5 + k * 0.2), so_mau(k * 0.055))
    return _xong(vang(lp(y, 9000), t60=1.5, uot=0.3, rong=1.4, hat=33))


def moc_hien(rng):
    """Ô mốc thời gian (góc phải sa bàn) trượt vào: vút ngắn + nốt marimba trầm."""
    a = vut(rng, 0.4, -1, 0.6) * 0.6
    b = pan(_marimba(NGU_CUNG[0] / 2, 0.6), 0.5) * 0.7
    y = np.zeros((max(len(a), so_mau(0.25) + len(b)), 2), np.float32)
    y[:len(a)] += a; dat_vao(y, b, so_mau(0.25))
    return _xong(y)


def _do_soi(rng, dai, dinh):
    """Tiếng ồn dâng lên (đảo ngược) đến đỉnh tại 'dinh' giây – dùng trước một tiếng chốt."""
    n = so_mau(dai)
    e = np.clip(truc_tg(n) / dinh, 0, 1) ** 2.2 * (truc_tg(n) <= dinh)
    fc = np.linspace(250, 2600, 12)
    return loc_quet(on_hong(n, rng), fc, bw_oct=1.3) * e


def logo_mo(rng, dai=2.6):
    """Nhạc hiệu mở đầu (khớp hình logo: biểu tượng xoay vào và đáp xuống ~45% thời lượng, chữ hiện 35–70%):
    tiếng dâng lên → trống đồng chạm nhẹ khi logo đáp → rải đàn tranh ngũ cung khi chữ hiện → chuông ngân."""
    n = so_mau(dai); y = np.zeros((n, 2), np.float32)
    t_dap = 0.45 * dai
    dat_vao(y, pan_dong(_do_soi(rng, t_dap + 0.02, t_dap), -0.4, 0.2), 0, 0.35)
    td = su_kien.trong_dong(rng, f0=104)
    dat_vao(y, td, so_mau(t_dap - 0.01), 0.55)
    for k, i in enumerate([0, 1, 3, 4, 5]):
        f = NGU_CUNG[i] / 2
        dat_vao(y, pan(dan_tranh(f, 1.6, rng, nhan=(1 if k == 4 else 0)), -0.5 + k * 0.25), so_mau(0.36 * dai + k * 0.09), 0.32)
    dat_vao(y, pan(_chuong(NGU_CUNG[5] * 2, 1.4), 0.3), so_mau(0.7 * dai), 0.12)
    y = vang(y, t60=1.6, uot=0.22, rong=1.3, hat=34, giu_duoi=False)
    # tắt dần khớp hình mờ cuối (0.35 s)
    k = so_mau(0.5); y[n - k:] *= np.linspace(1, 0, k, dtype=np.float32)[:, None] ** 1.5
    return _xong(y)


def logo_ket(rng, dai=3.0):
    """Nhạc hiệu kết: trống đồng nhẹ khi logo đáp + rải đàn tranh đi xuống, kết ở nốt chủ, ngân và tắt hết trước khi hết hình."""
    n = so_mau(dai); y = np.zeros((n, 2), np.float32)
    t_dap = 0.45 * dai
    dat_vao(y, pan_dong(_do_soi(rng, t_dap + 0.02, t_dap), 0.3, -0.2), 0, 0.25)
    dat_vao(y, su_kien.trong_dong(rng, f0=98), so_mau(t_dap - 0.01), 0.5)
    for k, i in enumerate([5, 4, 3, 1, 0]):
        dat_vao(y, pan(dan_tranh(NGU_CUNG[i] / 2, 1.8, rng, nhan=(-1 if k == 3 else 0)), 0.5 - k * 0.25),
                so_mau(t_dap + 0.12 + k * 0.13), 0.3)
    y = vang(y, t60=1.8, uot=0.25, rong=1.3, hat=35, giu_duoi=False)
    k = so_mau(0.8); y[n - k:] *= np.linspace(1, 0, k, dtype=np.float32)[:, None] ** 1.5
    return _xong(y)


def cong_thoi_gian(rng, dai=2.0):
    """Cổng thời gian (cảnh chuyển 'trống đồng xoay'): gió cuốn xoáy suốt cảnh, tiếng trống đồng khi hiện mốc năm (~18%),
    tiếng dâng lên dồn vào chớp sáng (~82%) rồi một tiếng 'ùm' mềm."""
    n = so_mau(dai + 1.2); y = np.zeros((n, 2), np.float32)
    g = su_kien.gio_cuon(rng, dai=dai, p0=-0.8, p1=0.8)
    dat_vao(y, g, 0, 0.45)
    dat_vao(y, su_kien.trong_dong(rng), so_mau(0.16 * dai), 0.75)
    t_fl = 0.82 * dai
    dat_vao(y, pan(_do_soi(rng, t_fl + 0.01, t_fl), 0), 0, 0.3)
    m = so_mau(0.8); um = modal(m, [62], [1], [0.15], truot=0.5, rng=rng) + lp(on_trang(m, rng), 300) * bao_exp(m, .004, .1) * .5
    dat_vao(y, pan(um, 0), so_mau(t_fl), 0.35)
    dat_vao(y, pan(_chuong(NGU_CUNG[7] * 2, 1.2), 0.2), so_mau(t_fl), 0.08)
    return _xong(vang(y, t60=1.5, uot=0.2, rong=1.4, hat=36, giu_duoi=False))


# tên → (hàm, mức đỉnh mặc định dBFS ở bản trộn cuối, kênh)
BANG = {
    "tich": (tich, -21, "ui"), "bop": (bop, -21, "ui"), "dong_ho": (dong_ho, -27, "ui"),
    "chuong_bao": (chuong_bao, -19, "ui"), "vut": (vut, -27, "ui"), "the_vao": (the_vao, -25, "ui"),
    "lap_lanh": (lap_lanh, -21, "ui"), "moc_hien": (moc_hien, -24, "ui"), "logo_mo": (logo_mo, -16, "ui"),
    "logo_ket": (logo_ket, -17, "ui"), "cong_thoi_gian": (cong_thoi_gian, -17, "ui"),
}
