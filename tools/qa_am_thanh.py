"""Kiểm tra âm thanh (QA) – vì AI không tự nghe được, ta ĐO:
  python3 tools/qa_am_thanh.py <thư_mục_làm_việc> <video_ra.mp4>   → độ to (EBU R128), mức nền khi có lời, đỉnh sự kiện, ảnh phổ
  python3 tools/qa_am_thanh.py --mau tmp/qa/sfx                      → xuất mẫu ~10 s của từng âm nền / tiếng sự kiện + ảnh phổ để nghe duyệt
Thư mục làm việc phải được tạo với --do-muc (tools/lam_lai_am_thanh.py) để có các lớp tách."""
import os, re, sys, json, math, subprocess
import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))


def ebur(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    s = r[r.rfind("Summary:"):]
    g = lambda k: float(re.search(k + r":\s+(-?[\d.]+|-inf)", s).group(1).replace("-inf", "-120"))
    return dict(I=g("I"), LRA=g("LRA"), TP=g("Peak"))


def khung_db(x, f):
    k = len(x) // f
    p = np.mean(x[:k * f].reshape(k, f, -1) ** 2, axis=(1, 2))
    return 10 * np.log10(p + 1e-12)


def do(work, out_mp4, qa_dir=None):
    sid = os.path.basename(work.rstrip("/")).replace("_am_thanh_lai", "")
    qa_dir = qa_dir or os.path.join(ROOT, "tmp/qa"); os.makedirs(qa_dir, exist_ok=True)
    fin = ebur(out_mp4)
    pre = ebur(os.path.join(work, "tach_truoc_loudnorm.wav"))
    G = fin["I"] - pre["I"]
    v, sr = sf.read(os.path.join(work, "voice.wav"), dtype="float32", always_2d=True)
    sd, _ = sf.read(os.path.join(work, "tach_sfx_ha.wav"), dtype="float32", always_2d=True)
    ui, _ = sf.read(os.path.join(work, "sfx_ui.wav"), dtype="float32", always_2d=True)
    f = int(0.4 * sr)                                     # khung 400 ms
    vd = khung_db(v, f); sdd = khung_db(sd, f)[:len(vd)]; uid = khung_db(ui, f)[:len(vd)]
    co_loi = vd > -40; k_loi = (vd < -60) & (sdd > -80)
    pm = lambda a, m: 10 * math.log10(np.mean(10 ** (a[m] / 10))) if m.any() else float("nan")
    res = dict(id=sid, cuoi=fin, truoc_loudnorm_I=pre["I"], G_thuc=round(G, 2),
               nen_khi_co_loi_rms=round(pm(sdd, co_loi) + G, 1),
               nen_khi_co_loi_trung_vi=round(float(np.median(sdd[co_loi])) + G, 1) if co_loi.any() else None,
               nen_khi_khong_loi_rms=round(pm(sdd, k_loi) + G, 1),
               loi_rms=round(pm(vd, co_loi) + G, 1))
    # đỉnh: lấy theo khung 50 ms của tổng sfx (đã hạ) + ui, quy về bản cuối
    f2 = int(0.05 * sr); n = min(len(sd), len(ui)) // f2 * f2
    pk = np.max(np.abs(sd[:n] + ui[:n]).reshape(-1, f2, 2), axis=(1, 2))
    top = np.argsort(pk)[::-1]; chon = []
    for i in top:
        if all(abs(i - j) > 20 for j in chon): chon.append(i)
        if len(chon) >= 6: break
    res["dinh_sfx_lon_nhat"] = [dict(t=round(i * 0.05, 2), dbfs=round(20 * math.log10(pk[i] + 1e-9) + G, 1)) for i in sorted(chon)]
    res["dinh_ui_lon_nhat_dbfs"] = round(20 * math.log10(float(np.max(np.abs(ui))) + 1e-9) + G, 1)
    # ảnh phổ: bản cuối và lớp sfx
    for src, name in ((out_mp4, f"{sid}_pho_ban_cuoi.png"), (os.path.join(work, "sfx_nen.wav"), f"{sid}_pho_sfx_nen.png")):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-lavfi",
                        "showspectrumpic=s=1600x500:legend=1:scale=log:fscale=log:stop=16000", os.path.join(qa_dir, name)])
    # từng cảnh: mức lớp mô phỏng khi có lời / khi lặng
    plan = json.load(open(os.path.join(work, "am_thanh.json")))
    pm2 = lambda a: round(10 * math.log10(np.mean(10 ** (a / 10))) + G, 1) if len(a) else None
    theo_canh = {}
    for g in plan["ghi_chu"]:
        m = re.match(r"Cảnh (\d+) \((\w+), ([\d.]+)–([\d.]+)s\): (.*)", g)
        if not m: continue
        i0, i1 = int(float(m.group(3)) / 0.4) + 1, int(float(m.group(4)) / 0.4) - 1
        sv, ss = vd[i0:i1], sdd[i0:i1]
        theo_canh[int(m.group(1))] = (pm2(ss[sv > -40]), pm2(ss[(sv < -60) & (ss > -80)]))
    res["theo_canh"] = theo_canh
    json.dump(res, open(os.path.join(qa_dir, f"{sid}_muc.json"), "w"), ensure_ascii=False, indent=1)
    ghi_md(sid, res, plan, os.path.join(qa_dir, f"{sid}_am_thanh.md"), out_mp4)
    print(json.dumps({k: v for k, v in res.items() if k != "theo_canh"}, ensure_ascii=False, indent=1))
    return res


def ghi_md(sid, r, plan, path, out_mp4):
    """Ghi chú tiếng Việt: số đo + từng cảnh được những âm thanh gì."""
    tk = plan["thong_ke"]; f = lambda v: "–" if v is None else f"{v}"
    out = [f"# Âm thanh mô phỏng – {sid}", "",
           f"Tệp nghe thử: `{os.path.relpath(out_mp4, ROOT)}` (hình giữ nguyên, chỉ thay âm thanh). Ảnh phổ: `tmp/qa/{sid}_pho_ban_cuoi.png`, `tmp/qa/{sid}_pho_sfx_nen.png`.", "",
           "## Số đo (EBU R128, đo trên tệp MP4 cuối)", "",
           f"- Độ to tích hợp **{r['cuoi']['I']} LUFS** (mục tiêu −14), LRA {r['cuoi']['LRA']} LU, đỉnh thật **{r['cuoi']['TP']} dBTP** (mục tiêu ≤ −1.5)",
           f"- Lời đọc khi đang nói: {r['loi_rms']} dBFS RMS",
           f"- Lớp mô phỏng khi có lời: {r['nen_khi_co_loi_rms']} dBFS RMS (trung bình cả tập, kể cả cảnh thẻ không có nền); khi lặng: {r['nen_khi_khong_loi_rms']} dBFS RMS",
           f"- Đỉnh lớn nhất của lớp mô phỏng (nhiều tiếng chồng nhau, đã qua bộ giới hạn): {max(d['dbfs'] for d in r['dinh_sfx_lon_nhat'])} dBFS; tiếng giao diện: {r['dinh_ui_lon_nhat_dbfs']} dBFS",
           f"- Hiệu chỉnh tự động: lời đọc {tk['I_loi']} LUFS → loudnorm ước cộng {tk['G']} dB (thực tế {r['G_thuc']} dB); kênh nền hạ ~{tk['red']} dB khi có lời; {tk['so_su_kien']} tiếng sự kiện, {tk['so_doan_nen']} đoạn nền", "",
           "## Từng cảnh được gì", "", "| Cảnh | Lớp mô phỏng khi có lời (dBFS RMS) | Khi lặng | Âm thanh |", "|---|---|---|---|"]
    for g in plan["ghi_chu"]:
        m = re.match(r"Cảnh (\d+) \((\w+), ([\d.]+)–([\d.]+)s\): (.*)", g)
        if m:
            a, b = r["theo_canh"].get(int(m.group(1)), (None, None))
            out.append(f"| {m.group(1)} ({m.group(2)}, {m.group(3)}–{m.group(4)} s) | {f(a)} | {f(b)} | {m.group(5)} |")
        else: out.append(f"| – | | | {g} |")
    out += ["", "Cảnh có clip Kling mang sẵn tiếng hiện trường thật: nền tổng hợp chỉ bổ sung (−7 dB) nên số đo thấp hơn có chủ ý. "
            "Cảnh thẻ (trục thời gian, ghi nhớ, câu hỏi) không có nền – chỉ có tiếng giao diện. "
            "Vạch ngang ~750 Hz trên ảnh phổ là lỗi hiển thị của showspectrumpic (phổ Welch không có âm đơn nào ở đó)."]
    open(path, "w").write("\n".join(out) + "\n")


def mau(out_dir):
    """Xuất mẫu nghe thử: mỗi âm nền 10 s (kèm điểm xuyết), mỗi tiếng sự kiện/giao diện một tệp; kèm ảnh phổ."""
    from am_thanh import nen, su_kien, giao_dien
    from am_thanh.dsp import SR, so_mau, chuan_dinh, cat_vong, tu_db, lufs
    os.makedirs(out_dir, exist_ok=True)
    rows = []
    for ten in nen.CONG_THUC:
        loop = nen.vong_lap(ten); x = cat_vong(loop, so_mau(3.0), so_mau(10))
        y, mt = nen.diem_xuyet(ten, 10, np.random.default_rng(5))
        if y is not None: x = x + y
        x = x * tu_db(-20 - lufs(x))                  # mọi mẫu nền ở cùng độ to −20 LUFS để so sánh
        p = os.path.join(out_dir, f"nen_{ten}.wav"); sf.write(p, np.clip(x, -1, 1), SR, subtype="PCM_16"); rows.append((p, f"nền {ten} {mt}"))
    for bang in (su_kien.BANG, giao_dien.BANG):
        for ten, (fn, muc, kenh) in bang.items():
            y = fn(np.random.default_rng(11))
            y = np.vstack([y, np.zeros((so_mau(0.3), 2), np.float32)]) * tu_db(-3)
            p = os.path.join(out_dir, f"{'ui' if kenh == 'ui' else 'sk'}_{ten}.wav"); sf.write(p, y, SR, subtype="PCM_16"); rows.append((p, ten))
    for p, _ in rows:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", p, "-lavfi",
                        "showspectrumpic=s=800x300:legend=0:scale=log:fscale=log:stop=16000", p[:-4] + ".png"])
    print(f"{len(rows)} mẫu → {out_dir}")


if __name__ == "__main__":
    if sys.argv[1] == "--mau": mau(sys.argv[2])
    else: do(sys.argv[1], sys.argv[2])
