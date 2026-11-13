"""Dựng âm thanh mô phỏng cho cả tập theo kế hoạch của thiet_ke.py → hai tệp khớp đúng trục thời gian video:
  sfx_nen.wav – nền + tiếng sự kiện trong cảnh: bị HẠ NHẸ khi có lời đọc (sidechain êm, tỉ số 2 → ~4–5 dB)
  sfx_ui.wav  – tiếng giao diện (tích, bóp, đồng hồ, chuông, vút, nhạc hiệu): ngắn, nhỏ, không bị hạ
Hiệu chỉnh mức: đo độ to lời đọc (voice.wav) để ước lượng mức khuếch đại của loudnorm −14 LUFS ở khâu cuối (G)
và mức bị hạ khi có lời (red), rồi ghi tệp ở mức sao cho SAU khi trộn: nền ≈ MUC_NEN (khi đang có lời),
sự kiện đạt đỉnh ≈ mức trong bảng (−16…−22 dBFS)."""
import os, re, json, math, inspect, subprocess, zlib
import numpy as np
import soundfile as sf
from .dsp import SR, so_mau, tu_db, cat_vong, mo_dan, dat_vao, rms, db, gioi_han
from . import nen, su_kien, giao_dien, thiet_ke

# bộ hạ âm êm cho kênh sfx_nen (khoá theo lời đọc) – dùng chung trong render.py và công cụ làm lại âm thanh
DUCK_SFX = dict(threshold=0.03, ratio=2, attack=40, release=700, knee=6)
DUCK_SFX_STR = "sidechaincompress=" + ":".join(f"{k}={v}" for k, v in DUCK_SFX.items())


def _bang(loai):
    if loai in su_kien.BANG: return su_kien.BANG[loai]
    if loai in giao_dien.BANG: return giao_dien.BANG[loai]
    raise KeyError(loai)


def _goi(fn, rng, kw):
    ok = inspect.signature(fn).parameters
    return fn(rng, **{k: v for k, v in kw.items() if k in ok})


def do_loi_doc(voice_wav):
    """→ (I_voice LUFS, mức RMS khi đang nói dBFS) của tệp lời đọc."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", voice_wav, "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r)
    I = float(m[-1]) if m else -20.0
    x, sr = sf.read(voice_wav, dtype="float32", always_2d=True)
    x = x[:, 0]; f = int(0.05 * sr); k = len(x) // f
    p = np.mean(x[:k * f].reshape(k, f) ** 2, axis=1)
    act = p[p > 10 ** (-45 / 10)]
    a = 10 * math.log10(float(np.mean(act))) if len(act) else -30.0
    return I, a


def hieu_chinh(voice_wav):
    """Ước lượng G (dB loudnorm sẽ cộng thêm) và red (dB kênh sfx_nen bị hạ khi có lời)."""
    I, a = do_loi_doc(voice_wav)
    G = -14.0 - I                       # (đo thực tế lệch ±0.5 dB so với ước lượng này)
    thr = 20 * math.log10(DUCK_SFX["threshold"])
    red = max(0.0, (a - thr) * (1 - 1 / DUCK_SFX["ratio"]))
    return dict(I_loi=round(I, 1), rms_loi=round(a, 1), G=round(G, 2), red=round(min(red, 12.0), 2))


def _dung_nen(out, kh, total, off, seed, fps_ctrl=100):
    """Mỗi loại nền là một dải liên tục trên trục thời gian (không khởi động lại giữa hai cảnh cùng nền),
    độ to theo từng cảnh, chuyển mượt 0.7 s ở ranh giới cảnh."""
    N = len(out); nc = int(total * fps_ctrl) + 2
    for ten in sorted({s["ten"] for s in kh.nen}):
        ctrl = np.full(nc, -120.0)
        for s in kh.nen:
            if s["ten"] != ten: continue
            a = int(s["t0"] * fps_ctrl); b = int(s["t1"] * fps_ctrl)
            ctrl[a:b] = np.maximum(ctrl[a:b], s["muc"])
        g = np.where(ctrl > -100, 10 ** ((ctrl + 23.0 + off) / 20), 0.0)
        w = np.hanning(int(0.7 * fps_ctrl)); w /= w.sum()
        g = np.convolve(g, w, "same")
        act = np.nonzero(g > 1e-5)[0]
        if not len(act): continue
        loop = nen.vong_lap(ten)
        rng = np.random.default_rng(zlib.crc32(f"{seed}|{ten}".encode()))
        start = int(rng.integers(0, len(loop)))
        i0 = int(act[0] / fps_ctrl * SR); i1 = min(N, int((act[-1] + 1) / fps_ctrl * SR))
        step = SR * 20
        for a in range(i0, i1, step):          # theo khúc 20 s cho nhẹ bộ nhớ
            b = min(i1, a + step)
            gg = np.interp(np.arange(a, b) / SR * fps_ctrl, np.arange(nc), g).astype(np.float32)
            out[a:b] += cat_vong(loop, start + a, b - a) * gg[:, None]


def dung(kh, total, work, cal, seed="eduhistory"):
    """Kế hoạch → work/sfx_nen.wav, work/sfx_ui.wav. cal = hieu_chinh(...). Trả về (đường_dẫn_nền, đường_dẫn_ui, thống_kê)."""
    N = so_mau(total)
    nen_bus = np.zeros((N, 2), np.float32); ui_bus = np.zeros((N, 2), np.float32)
    G, red = cal["G"], cal["red"]
    off_nen = red - G                       # nền: mức ghi = mức muốn (khi có lời) + red − G
    _dung_nen(nen_bus, kh, total, off_nen, seed)
    # điểm xuyết (chim, lách tách, giọt nước…) theo từng cảnh
    for d in kh.diem:
        rng = np.random.default_rng(zlib.crc32(f"{seed}|{d['canh']}|{d['ten']}|diem".encode()))
        y, mo_ta = nen.diem_xuyet(d["ten"], d["t1"] - d["t0"], rng, d.get("ban_ngay", True), d.get("co_nuoc", False))
        if y is None: continue
        y = mo_dan(y, 0.4, 0.6) * tu_db(d["muc"] + 23.0 + off_nen)
        dat_vao(nen_bus, y, so_mau(d["t0"]))
        d["mo_ta"] = mo_ta
    # sự kiện
    loi = []
    for k, e in enumerate(kh.su_kien):
        try:
            fn, muc0, kenh = _bang(e["loai"])
        except KeyError:
            loi.append(f"không có loại '{e['loai']}'"); continue
        rng = np.random.default_rng(zlib.crc32(f"{seed}|{e.get('canh')}|{e['loai']}|{k}".encode()))
        try:
            y = _goi(fn, rng, e["kw"])
        except Exception as ex:
            loi.append(f"{e['loai']}: {ex}"); continue
        muc = e["muc"] if e["muc"] is not None else muc0
        bus = ui_bus if kenh == "ui" else nen_bus
        dat_vao(bus, y * tu_db(muc - G), so_mau(e["t"]))
    p_nen = os.path.join(work, "sfx_nen.wav"); p_ui = os.path.join(work, "sfx_ui.wav")
    # giới hạn an toàn (chỉ bắt đỉnh hiếm khi nhiều tiếng chồng nhau): bản cuối kênh nền ≤ −11 dBFS, giao diện ≤ −14 dBFS
    nen_bus[:] = gioi_han(nen_bus, -11.0 - G); ui_bus[:] = gioi_han(ui_bus, -14.0 - G)
    for p, b in ((p_nen, nen_bus), (p_ui, ui_bus)):
        np.clip(b, -0.99, 0.99, out=b)
        sf.write(p, b, SR, subtype="PCM_24")
    tk = dict(cal, rms_nen=round(db(rms(nen_bus)), 1), dinh_nen=round(db(float(np.max(np.abs(nen_bus)))), 1),
              rms_ui=round(db(rms(ui_bus)), 1), dinh_ui=round(db(float(np.max(np.abs(ui_bus)))), 1),
              so_su_kien=len(kh.su_kien), so_doan_nen=len(kh.nen), loi=loi)
    with open(os.path.join(work, "am_thanh.json"), "w") as f:
        json.dump(dict(thong_ke=tk, nen=kh.nen, su_kien=kh.su_kien, diem=kh.diem, ghi_chu=kh.ghi_chu), f, ensure_ascii=False, indent=1, default=str)
    return p_nen, p_ui, tk


def tao_sfx(spec, scenes, starts, total, intro, outro, work, voice_wav, fps=30):
    """Một lệnh cho render.py: thiết kế + dựng. Trả về (sfx_nen.wav, sfx_ui.wav, thống kê, ghi chú)."""
    cal = hieu_chinh(voice_wav)
    kh = thiet_ke.thiet_ke(spec, scenes, starts, total, intro, outro, fps=fps)
    p_nen, p_ui, tk = dung(kh, total, work, cal, seed=spec.get("id", "x"))
    return p_nen, p_ui, tk, kh.ghi_chu
