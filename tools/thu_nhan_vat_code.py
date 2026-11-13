"""Dựng thử một cảnh dẫn chuyện vẽ HOÀN TOÀN BẰNG CODE (pipeline/nhan_vat_code.py), có tiếng, để kiểm tra.

    python3 tools/thu_nhan_vat_code.py                       # 2 câu mẫu (L8-B3-02 cảnh 1), nền theo "hinh"
    python3 tools/thu_nhan_vat_code.py --ma L7-B16-05 --so 7 # lấy lời của một cảnh có sẵn trong data/scripts
    python3 tools/thu_nhan_vat_code.py --nen song --doc      # ép loại nền, khung dọc 9:16

Giọng đọc lấy qua render.voice_for (VieNeu-TTS, có bộ nhớ đệm từng câu): các câu mẫu mặc định đã có sẵn trong
renders/_cache/vieneu nên KHÔNG phải nạp mô hình TTS (~2–3 GB RAM). Câu mới thì mô hình sẽ được nạp một lần.
Đầu ra: tmp/qa/nhan_vat_code_demo.mp4 (lời đọc trễ 0,15 s giống render.py) + bảng 4 khung tmp/qa/nhan_vat_code_sheet.png.
Không chạy render.py, không ghi vào data/ hay assets/."""
import sys, os, json, time, argparse, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import render, nhan_vat_code

MAU = {   # L8-B3-02 cảnh 1 – hai câu đã có giọng trong bộ nhớ đệm
    "loi": [["Hân Hân", "Cỗ máy này từng làm thay đổi cả thế giới. Cậu đoán ra chưa?",
             "This machine once changed the whole world. Can you guess what it is?"],
            ["Nhật Minh", "Máy hơi nước! Cùng du hành về nước Anh thế kỉ XVIII nhé!",
             "A steam engine! Let's travel back to 18th-century Britain!"]],
    "hinh": "Nhật Minh và Hân Hân trong một bảo tàng khoa học, đứng trước mô hình máy hơi nước",
    "lop": "dan_chuyen", "so": 1,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ma"); ap.add_argument("--so", type=int)
    ap.add_argument("--nen", help="studio | song | thu_vien | lop_hoc | di_tich | ban_do")
    ap.add_argument("--hinh"); ap.add_argument("--doc", action="store_true")
    ap.add_argument("--max-giay", type=float, default=8.5)
    ap.add_argument("--out", default=os.path.join(ROOT, "tmp/qa/nhan_vat_code_demo.mp4"))
    a = ap.parse_args()
    sc = dict(MAU)
    if a.ma:
        spec = render.load_spec(os.path.join(ROOT, f"data/scripts/{a.ma}.json"))
        sc = dict([c for c in spec["canh"] if c.get("so") == a.so][0])
    if a.hinh: sc["hinh"] = a.hinh
    if a.nen: sc["nen"] = a.nen
    t0 = time.time()
    wav, bounds = render.voice_for(sc["loi"], pauses=sc.get("nghi_sau_cau"))
    sc.update(wav=wav, bounds=bounds)
    print("giọng:", os.path.relpath(wav, ROOT), [(round(x, 2), round(y, 2)) for x, y in bounds], f"({time.time() - t0:.1f}s)")
    print("nền:", nhan_vat_code.chon_nen(sc), "| động tác:", [nhan_vat_code.chon_cu_chi(l[1]) for l in sc["loi"]])
    W, H = (1080, 1920) if a.doc else (1920, 1080)
    fps = render.FPS
    secs = min(render.dur(wav) + nhan_vat_code.AUDIO_OFFSET + 0.4, a.max_giay)
    n = int(round(secs * fps))
    # 4 khung cho bảng tiếp xúc: giữa câu 1, câu 1 lúc miệng mở to nhất, giữa câu 2, cuối cảnh
    off = nhan_vat_code.AUDIO_OFFSET
    env, _ = nhan_vat_code.phan_tich_giong(wav, fps, n, off)
    (a1, b1), (a2, b2) = bounds[0], bounds[-1]
    i_loud = int(np.argmax(env[int((a2 + off) * fps): int((b2 + off) * fps)])) + int((a2 + off) * fps)
    picks = sorted({min(n - 1, int((a1 + off + (b1 - a1) * 0.55) * fps)), min(n - 1, int((a1 + off + 0.6) * fps)),
                    min(n - 1, i_loud), min(n - 1, int((b2 + off - 0.5) * fps))})
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
                           "-i", wav, "-filter_complex", f"[1]adelay={int(off * 1000)}|{int(off * 1000)},apad[a]", "-map", "0:v", "-map", "[a]",
                           "-t", f"{n / fps:.2f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", a.out], stdin=subprocess.PIPE)
    keep = {}
    t0 = time.time(); tmax = 0.0; tp = time.time()
    for i, fr in enumerate(nhan_vat_code.frames(sc, W, H, n, fps)):
        now = time.time(); tmax = max(tmax, now - tp) if i else tmax
        ff.stdin.write(fr.tobytes())
        if i in picks: keep[i] = fr
        tp = time.time()
    ff.stdin.close(); ff.wait()
    el = time.time() - t0
    print(f"{a.out}  {n} khung  {el:.1f}s  → {el / n:.3f} s/khung (kể cả mã hoá H.264; khung chậm nhất {tmax:.3f}s)")
    # bảng tiếp xúc 2×2, ghi thời điểm + người đang nói
    tw = 960 if not a.doc else 540
    th = int(tw * H / W)
    sheet = Image.new("RGB", (tw * 2, th * 2 + 0), "white")
    try:
        font = ImageFont.truetype(os.path.join(ROOT, "assets/fonts/be-vietnam-pro-600-normal.ttf"), 22)
    except Exception:
        font = ImageFont.load_default()
    for k, i in enumerate(picks):
        im = Image.fromarray(keep[i]).resize((tw, th), Image.LANCZOS)
        d = ImageDraw.Draw(im)
        t = i / fps - off
        who = next((ln[0] for (x, y), ln in zip(bounds, sc["loi"]) if x <= t <= y), "—")
        lab = f"t={i / fps:.2f}s  nói: {who}  mở miệng={env[i]:.2f}"
        d.rectangle([0, 0, int(d.textlength(lab, font=font)) + 20, 34], fill=(0, 0, 0))
        d.text((10, 4), lab, fill=(255, 255, 255), font=font)
        sheet.paste(im, ((k % 2) * tw, (k // 2) * th))
    sp = os.path.join(os.path.dirname(a.out), "nhan_vat_code_sheet.png")
    sheet.save(sp)
    print(sp)


if __name__ == "__main__":
    main()
