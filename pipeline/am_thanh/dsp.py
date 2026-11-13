"""Khối xử lý tín hiệu cơ bản cho thư viện âm thanh EduHistory Studio.
Quy ước: 48 kHz; âm đơn (mono) là mảng (N,), âm nổi (stereo) là mảng (N, 2), kiểu float32, biên độ ±1.
Mọi hàm đều vector hoá bằng numpy/scipy (không lặp từng mẫu) để chạy nhanh trên máy 2 nhân."""
import math
import numpy as np
from scipy import signal

SR = 48000
_EPS = 1e-9


def so_mau(giay):
    return max(0, int(round(giay * SR)))


def truc_tg(n):
    """Trục thời gian (giây) cho n mẫu."""
    return np.arange(n, dtype=np.float32) / SR


def db(x):
    return 20 * math.log10(max(x, _EPS))


def tu_db(d):
    return 10 ** (d / 20)


# ------------------------------------------------------------------ bộ lọc
_SOS = {}


def _sos(kieu, f, bac):
    f = tuple(float(min(max(v, 15.0), SR / 2 * 0.97)) for v in np.atleast_1d(f))
    k = (kieu, f, bac)
    if k not in _SOS:
        _SOS[k] = signal.butter(bac, f if len(f) > 1 else f[0], btype=kieu, fs=SR, output="sos")
    return _SOS[k]


def loc(x, kieu, f, bac=2):
    return signal.sosfilt(_sos(kieu, f, bac), x, axis=0).astype(np.float32)


def lp(x, f, bac=2):
    return loc(x, "lowpass", f, bac)


def hp(x, f, bac=2):
    return loc(x, "highpass", f, bac)


def bp(x, lo, hi, bac=2):
    return loc(x, "bandpass", (lo, hi), bac)


def cong_huong(x, f, q):
    """Bộ cộng hưởng (đỉnh 0 dB tại f) – dùng cho formant giọng, cộng hưởng thân gỗ…"""
    f = min(max(f, 20.0), SR / 2 * 0.95)
    b, a = signal.iirpeak(f, max(q, 0.5), fs=SR)
    return signal.lfilter(b, a, x, axis=0).astype(np.float32)


def lp_dong(x, fc_dau, fc_cuoi):
    """Lọc thông thấp có tần số cắt thay đổi theo thời gian (nội suy giữa 2 bản lọc theo log tần số)."""
    a = lp(x, fc_dau); b = lp(x, fc_cuoi)
    w = np.linspace(0, 1, len(x), dtype=np.float32)
    if x.ndim == 2: w = w[:, None]
    return a * (1 - w) + b * w


def loc_quet(x, f_tam, bw_oct=1.0, nfft=1024, f_tron=None):
    """Lọc dải thông với tần số tâm thay đổi theo thời gian (qua STFT). f_tam: mảng tần số tâm rải đều trên thời lượng x.
    Dùng cho tiếng vút (whoosh), mũi tên bay, lửa bùng, sóng vỗ…"""
    n = len(x)
    if n < nfft:
        x = np.pad(x, (0, nfft - n))
    f, t, Z = signal.stft(x, fs=SR, nperseg=nfft, noverlap=nfft * 3 // 4, boundary="even")
    fc = np.interp(t, np.linspace(0, len(x) / SR, len(f_tam)), np.asarray(f_tam, float))
    lf = np.log2(np.maximum(f, 20.0))[:, None]
    lc = np.log2(np.maximum(fc, 20.0))[None, :]
    sig = max(bw_oct, 0.05) / 2.355
    M = np.exp(-0.5 * ((lf - lc) / sig) ** 2)
    _, y = signal.istft(Z * M, fs=SR, nperseg=nfft, noverlap=nfft * 3 // 4, boundary=True)
    return y[:n].astype(np.float32)


# ------------------------------------------------------------------ nguồn tiếng ồn
def on_trang(n, rng):
    return rng.standard_normal(n).astype(np.float32)


def _on_mau(n, rng, mu):
    """Tiếng ồn có phổ 1/f^mu (mu=1: hồng, mu=2: nâu), qua FFT, chuẩn độ lệch = 1.
    Cắt êm phần dưới 20 Hz (hạ âm không nghe được nhưng chiếm hết khoảng đỉnh – lỗi đã gặp: 98 % năng lượng
    'đoàn quân tiến' nằm dưới 25 Hz)."""
    if n <= 1: return np.zeros(n, np.float32)
    X = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR); f0 = np.maximum(f, 20.0)
    X /= f0 ** (mu / 2)
    X *= np.clip((f - 12.0) / 12.0, 0, 1) ** 2      # dốc êm 12–24 Hz
    x = np.fft.irfft(X, n)
    return (x / (np.std(x) + _EPS)).astype(np.float32)


def on_hong(n, rng):
    return _on_mau(n, rng, 1.0)


def on_nau(n, rng):
    return _on_mau(n, rng, 2.0)


def muot_ngau_nhien(n, rng, nhip_hz, lo=0.0, hi=1.0):
    """Đường điều khiển ngẫu nhiên mượt (nội suy cosin giữa các điểm ngẫu nhiên, nhịp ~nhip_hz điểm/giây)."""
    k = max(3, int(n / SR * nhip_hz) + 3)
    v = rng.uniform(lo, hi, k).astype(np.float32)
    x = np.linspace(0, k - 1.001, n, dtype=np.float32) if n else np.zeros(0, np.float32)
    i = x.astype(int); fr = x - i
    w = 0.5 - 0.5 * np.cos(np.pi * fr)
    return v[i] * (1 - w) + v[np.minimum(i + 1, k - 1)] * w


# ------------------------------------------------------------------ đường bao (envelope)
def bao_exp(n, tan_cong=0.002, tat=0.2, tre=0.0):
    """Tấn công tuyến tính (giây) rồi tắt dần hàm mũ (hằng số thời gian 'tat' giây)."""
    t = truc_tg(n) - tre
    a = np.clip(t / max(tan_cong, 1e-4), 0, 1)
    d = np.exp(-np.maximum(t - tan_cong, 0) / max(tat, 1e-4))
    e = a * d
    e[t < 0] = 0
    return e.astype(np.float32)


def bao_hinh_chuong(n, dinh=0.5, mu=2.0):
    """Đường bao lên – xuống mượt, đỉnh tại tỉ lệ 'dinh' của độ dài (dùng cho vút, sóng, đoàn quân đi qua)."""
    u = np.linspace(0, 1, n, dtype=np.float32)
    dinh = min(max(dinh, 0.02), 0.98)
    a = np.where(u < dinh, u / dinh, (1 - u) / (1 - dinh))
    return (np.sin(np.clip(a, 0, 1) * np.pi / 2) ** mu).astype(np.float32)


def mo_dan(x, vao=0.01, ra=0.05):
    """Mờ vào / mờ ra (giây) để không có tiếng bụp ở hai đầu."""
    x = x.copy(); n = len(x)
    a = min(so_mau(vao), n // 2); b = min(so_mau(ra), n // 2)
    if a > 0:
        w = np.sin(np.linspace(0, np.pi / 2, a, dtype=np.float32)) ** 2
        x[:a] *= w[:, None] if x.ndim == 2 else w
    if b > 0:
        w = np.cos(np.linspace(0, np.pi / 2, b, dtype=np.float32)) ** 2
        x[n - b:] *= w[:, None] if x.ndim == 2 else w
    return x


# ------------------------------------------------------------------ âm nổi
def pan(mono, p=0.0):
    """Đặt âm đơn vào trường stereo, luật công suất không đổi. p: -1 (trái) … +1 (phải)."""
    p = float(min(max(p, -1), 1))
    a = (p + 1) * np.pi / 4
    return np.stack([mono * math.cos(a), mono * math.sin(a)], axis=1).astype(np.float32)


def pan_dong(mono, p_dau, p_cuoi):
    """Âm di chuyển từ p_dau sang p_cuoi (đoàn quân, mũi tên bay ngang)."""
    p = np.linspace(p_dau, p_cuoi, len(mono), dtype=np.float32)
    a = (np.clip(p, -1, 1) + 1) * np.pi / 4
    return np.stack([mono * np.cos(a), mono * np.sin(a)], axis=1).astype(np.float32)


def stereo(l, r):
    return np.stack([l, r], axis=1).astype(np.float32)


def do_rong(x, k=1.0):
    """Chỉnh độ rộng stereo qua Mid/Side (k=0: mono, 1: giữ nguyên, >1: rộng hơn)."""
    m = (x[:, 0] + x[:, 1]) * 0.5; s = (x[:, 0] - x[:, 1]) * 0.5 * k
    return stereo(m + s, m - s)


def thanh_stereo(x):
    return x if x.ndim == 2 else pan(x, 0.0)


# ------------------------------------------------------------------ vang (reverb) bằng đáp ứng xung tổng hợp
_IR = {}


def dap_ung_vang(t60=1.2, tre=0.012, sang=6000, rong=1.0, hat=0):
    """Đáp ứng xung tổng hợp: tiếng ồn tắt dần hàm mũ, đuôi tối dần (hấp thụ cao tần), hai kênh khác nhau."""
    key = (round(t60, 2), round(tre, 3), int(sang), round(rong, 2), hat)
    if key in _IR: return _IR[key]
    rng = np.random.default_rng(1000 + hat)
    n = so_mau(min(t60 * 1.15, 4.5))
    t = truc_tg(n)
    e = np.exp(-6.91 * t / t60).astype(np.float32)
    raw = np.stack([on_trang(n, rng), on_trang(n, rng)], 1) * e[:, None]
    sangv = lp(raw, sang, 2); toi = lp(raw, max(sang * 0.25, 600), 2)
    w = np.clip(t / max(t60 * 0.6, 1e-3), 0, 1)[:, None]
    ir = sangv * (1 - w) + toi * w
    ir = mo_dan(ir, 0.004, 0.05)
    # giảm tương quan hai kênh theo 'rong'
    m = (ir[:, 0] + ir[:, 1]) * .5; s = (ir[:, 0] - ir[:, 1]) * .5 * rong
    ir = stereo(m + s, m - s)
    ir = np.vstack([np.zeros((so_mau(tre), 2), np.float32), ir])
    ir /= np.sqrt(np.sum(ir ** 2) / 2) + _EPS
    _IR[key] = ir.astype(np.float32)
    return _IR[key]


def vang(x, t60=1.2, uot=0.25, tre=0.012, sang=6000, rong=1.0, hat=0, giu_duoi=True):
    """Trộn tiếng vang: x (mono/stereo) → stereo. uot = tỉ lệ năng lượng vang (0..1). giu_duoi: nối dài để giữ đuôi vang."""
    x = thanh_stereo(x)
    ir = dap_ung_vang(t60, tre, sang, rong, hat)
    n = len(x)
    L = signal.oaconvolve(x[:, 0], ir[:, 0])
    R = signal.oaconvolve(x[:, 1], ir[:, 1])
    wet = stereo(L, R)
    if not giu_duoi: wet = wet[:n]
    out = np.zeros((len(wet), 2), np.float32)
    out[:n] += x * math.sqrt(1 - uot)
    out += wet * math.sqrt(uot) * 0.35
    return out


# ------------------------------------------------------------------ chuẩn mức
def rms(x):
    return float(np.sqrt(np.mean(np.square(x, dtype=np.float64)) + 1e-20))


def chuan_rms(x, dbfs):
    return (x * (tu_db(dbfs) / (rms(x) + _EPS))).astype(np.float32)


# bộ lọc K theo ITU-R BS.1770 (48 kHz): kệ cao tần + thông cao RLB → đo độ to cảm nhận (LUFS, không cổng)
_K1 = ([1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585])
_K2 = ([1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621])


def lufs(x):
    """Độ to tích hợp (không cổng) theo BS.1770 – đủ dùng để cân các vòng lặp nền với nhau."""
    x = thanh_stereo(x).astype(np.float64)
    y = signal.lfilter(*_K2, signal.lfilter(*_K1, x, axis=0), axis=0)
    return -0.691 + 10 * math.log10(float(np.sum(np.mean(y ** 2, axis=0))) + 1e-20)


def chuan_lufs(x, muc):
    return (x * tu_db(muc - lufs(x))).astype(np.float32)


def gioi_han_mem(x, tran_db=-4.0):
    """Giới hạn đỉnh mềm: phần vượt 'tran_db' bị nén êm bằng tanh (không méo cứng)."""
    c = tu_db(tran_db); k = 0.7 * c
    a = np.abs(x); over = a > k
    y = x.copy()
    y[over] = np.sign(x[over]) * (k + (c - k) * np.tanh((a[over] - k) / (c - k)))
    return y.astype(np.float32)


def gioi_han(x, tran_db=-10.0, nhin_truoc=0.005, nha=0.12):
    """Bộ giới hạn đỉnh kiểu 'hạ khuếch đại' (không méo dạng sóng): nhìn trước ~5 ms, nhả 120 ms.
    Chỉ tác động khi có đỉnh hiếm vượt ngưỡng; phần dư (nếu có) mới qua giới hạn mềm."""
    from scipy.ndimage import maximum_filter1d
    c = tu_db(tran_db)
    a = np.max(np.abs(x), axis=1) if x.ndim == 2 else np.abs(x)
    if float(a.max(initial=0)) <= c: return x
    k = max(3, so_mau(nhin_truoc) * 2 + 1)
    env = maximum_filter1d(a, size=k)
    r = np.clip(1 - c / np.maximum(env, 1e-9), 0, 1)          # mức cần hạ
    alpha = math.exp(-1 / (nha * SR))
    rs = signal.lfilter([1 - alpha], [1, -alpha], maximum_filter1d(r, size=so_mau(nha * 0.5)))
    g = (1 - np.maximum(rs, r)).astype(np.float32)
    y = x * (g[:, None] if x.ndim == 2 else g)
    return gioi_han_mem(y, tran_db + 0.5)


def chuan_dinh(x, dbfs):
    p = float(np.max(np.abs(x))) if len(x) else 0.0
    return (x * (tu_db(dbfs) / (p + _EPS))).astype(np.float32)


def bao_hoa_mem(x, nguong=0.5):
    """Bão hoà mềm (tanh) phía trên ngưỡng – làm tròn đỉnh, tránh tiếng chát."""
    return (np.tanh(x / nguong) * nguong).astype(np.float32)


# ------------------------------------------------------------------ vòng lặp liền mạch
def tao_vong_lap(x, xf_giay=2.0):
    """x dài (L + xf) mẫu → vòng lặp L mẫu nối liền: phần đầu được đan chéo (công suất không đổi) với phần đuôi thừa."""
    xf = so_mau(xf_giay); L = len(x) - xf
    out = x[:L].copy()
    w = np.linspace(0, np.pi / 2, xf, dtype=np.float32)
    if x.ndim == 2: w = w[:, None]
    out[:xf] = x[:xf] * np.sin(w) + x[L:L + xf] * np.cos(w)
    return out


def cat_vong(loop, bat_dau, n):
    """Lấy n mẫu từ vòng lặp (lặp lại liền mạch) bắt đầu ở vị trí bat_dau."""
    idx = (bat_dau + np.arange(n)) % len(loop)
    return loop[idx]


# ------------------------------------------------------------------ tổng hợp dao động riêng (modal)
def modal(n, tan_so, bien_do, tat, pha=None, truot=0.0, truot_tg=0.05, rng=None):
    """Tổng các dao động riêng tắt dần: sin(2π f t)·a·exp(-t/τ). truot: độ trượt tần số ban đầu (vd 0.3 = cao hơn 30% rồi về f)."""
    t = truc_tg(n)[:, None].astype(np.float64)
    f = np.asarray(tan_so, float)[None, :]
    a = np.asarray(bien_do, float)[None, :]
    tau = np.maximum(np.asarray(tat, float), 1e-4)[None, :]
    if pha is None:   # pha 0: dao động bắt đầu từ 0 → không có bước nhảy/độ lệch DC ở đầu tiếng gõ
        pha = np.zeros(f.shape[1])[None, :]
    # pha tích phân của f(t) = f·(1 + truot·exp(-t/τg))
    ph = 2 * np.pi * f * (t + truot * truot_tg * (1 - np.exp(-t / truot_tg))) + pha
    y = np.sum(np.sin(ph) * a * np.exp(-t / tau), axis=1)
    return y.astype(np.float32)


def rang_cua(f0_track):
    """Sóng răng cưa từ đường tần số (Hz theo từng mẫu) – nguồn kích cho giọng nói tổng hợp, tù và…"""
    ph = np.cumsum(f0_track / SR)
    return (2 * (ph % 1.0) - 1).astype(np.float32)


def dat_vao(dich, nguon, vi_tri, he_so=1.0):
    """Cộng 'nguon' vào 'dich' tại mẫu vi_tri (cắt phần tràn ra ngoài)."""
    if vi_tri >= len(dich) or len(nguon) == 0: return
    a = max(0, vi_tri); b = min(len(dich), vi_tri + len(nguon))
    if b <= a: return
    s = a - vi_tri
    src = nguon[s:s + (b - a)]
    if dich.ndim == 2 and src.ndim == 1: src = src[:, None]
    dich[a:b] += src * he_so
