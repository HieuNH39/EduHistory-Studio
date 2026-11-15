"""Thay lại tiếng của các video đã dựng từ bản mix trong bộ nhớ đệm (không dựng lại hình).

Dùng khi đổi cách mã hoá tiếng (ví dụ AAC 160k → 192k + lọc thông thấp 18 kHz để đỉnh thật không vượt −1 dBTP).
Ghi đè đúng tệp cũ (giữ liên kết cứng sang web/videos).

    python3 tools/thay_tieng.py [MÃ ...]      # không có mã: mọi video trong renders/v1
"""
import glob, json, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BO_QUA = {"L7-B13-01"}  # đang dựng lại toàn bộ


def thoi_luong(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                capture_output=True, text=True).stdout.strip() or 0)


def dinh_that(p):
    r = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-i", p, "-vn", "-af",
                        "loudnorm=I=-14:TP=-2:print_format=json", "-f", "null", "-"], capture_output=True, text=True)
    s = r.stderr[r.stderr.rfind("{"):]
    d = json.loads(s[:s.find("}") + 1])
    return float(d["input_i"]), float(d["input_tp"])


def main(ds):
    for v in ds:
        ma = os.path.basename(v)[:-4]
        if ma in BO_QUA: continue
        mix = os.path.join(ROOT, "renders/_cache", ma, "mix.wav")
        if not os.path.exists(mix):
            print(ma, "không có mix.wav – bỏ qua"); continue
        if os.path.getmtime(mix) > os.path.getmtime(v) + 5:
            print(ma, "mix.wav mới hơn video – bỏ qua (cần dựng lại)"); continue
        tmp = os.path.join(ROOT, "tmp", f"_thay_tieng_{ma}.mp4")
        subprocess.run(["nice", "-n", "10", "ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", v, "-i", mix,
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-aac_is", "0", "-aac_pns", "0",
                        "-movflags", "+faststart", "-shortest", tmp], check=True)
        a, b = thoi_luong(v), thoi_luong(tmp)
        if abs(a - b) > 0.25:
            print(ma, f"lệch thời lượng {a:.2f} → {b:.2f} – giữ bản cũ"); os.remove(tmp); continue
        cu = dinh_that(v)[1]
        I, tp = dinh_that(tmp)
        shutil.copyfile(tmp, v)  # ghi đè cùng inode
        os.remove(tmp)
        print(f"{ma}: đỉnh thật {cu:+.2f} → {tp:+.2f} dBTP, độ to {I:.2f} LUFS")


if __name__ == "__main__":
    args = sys.argv[1:]
    ds = [os.path.join(ROOT, "renders/v1", f"{m}.mp4") for m in args] if args else sorted(glob.glob(os.path.join(ROOT, "renders/v1/*.mp4")))
    main(ds)
