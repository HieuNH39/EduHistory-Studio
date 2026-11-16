"""Sửa riêng đoạn kết (logo + tên tập + ghi chú tái hiện) của video đã dựng, không dựng lại cả video.

Lỗi gốc: ghi chú tái hiện dài được vẽ thành MỘT dòng nên tràn ra ngoài hai mép khung (83 kịch bản bài học),
video dọc TikTok thì ghi chú nằm sát đáy, bị chữ/nút của ứng dụng che.
Cách sửa: giữ nguyên phần đầu video (sao chép luồng, không nén lại), chỉ nén lại từ khung khoá cuối cùng trước
đoạn kết, vẽ đoạn kết mới bằng ident_frames() đã sửa (tự xuống dòng), ghép lại và giữ nguyên âm thanh gốc.

Dùng: python3 tools/sua_ket_video.py <video.mp4> <kich_ban.json> [--ep]   (--ep: sửa cả khi ghi chú vừa một dòng)
"""
import json, os, subprocess, sys, tempfile, shutil
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
import render  # noqa: E402


def probe(path, *args):
    return subprocess.run(["ffprobe", "-v", "error", *args, path], capture_output=True, text=True, check=True).stdout


def main(video, spec_path, ep=False):
    spec = render.load_spec(spec_path)
    note = spec.get("ghi_chu_tai_hien")
    if not note:
        print("bo qua (khong co ghi chu)", video); return 0
    vertical = spec.get("huong") == "doc"
    W, H = render.CFG["video"]["portrait"] if vertical else render.CFG["video"]["landscape"]
    FPS = render.FPS
    size = int(min(W, H) * 0.34)
    from PIL import ImageFont
    f_old = ImageFont.truetype(os.path.join(render.FONT_DIR, "be-vietnam-pro-400-italic.ttf"), int(size * 0.075))
    if not ep and not vertical and f_old.getlength(note) <= W * 0.94:
        print("bo qua (ghi chu vua khung)", video); return 0

    outro = (2.6 if vertical else 3.0) + 1.2
    n_out = int(outro * FPS)
    N = int(probe(video, "-select_streams", "v", "-count_packets", "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0").strip())
    o0 = N - n_out
    # kiểm tra khung đầu đoạn kết đúng là nền xanh đậm của ident (16,35,63)
    fr = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{(o0 + 2) / FPS:.4f}", "-i", video, "-frames:v", "1",
                         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(fr, np.uint8).reshape(H, W, 3).astype(np.int16)
    corner = a[: H // 5, : W // 5].reshape(-1, 3).mean(0)
    if np.abs(corner - np.array([16, 35, 63])).max() > 10:
        print("LOI: khung", o0, "khong phai dau doan ket", corner.round(1), video); return 2

    kfs = [float(x.split(",")[0]) for x in probe(video, "-select_streams", "v", "-skip_frame", "nokey", "-show_entries", "frame=pts_time",
                                   "-of", "csv=p=0").split()]
    k_idx = max(int(round(t * FPS)) for t in kfs if int(round(t * FPS)) <= o0)
    tmp = tempfile.mkdtemp(dir=os.path.join(ROOT, "tmp"))
    try:
        head, tail, cat, out = (os.path.join(tmp, x) for x in ("head.mp4", "tail.mp4", "cat.mp4", "out.mp4"))
        if k_idx > 0:
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-map", "0:v", "-c", "copy", "-frames:v", str(k_idx), head], check=True)
        enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                                "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
                                "-pix_fmt", "yuv420p", tail], stdin=subprocess.PIPE)
        n_mid = o0 - k_idx
        if n_mid > 0:
            dec = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{k_idx / FPS:.4f}", "-i", video, "-frames:v", str(n_mid),
                                    "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
            got = 0
            while True:
                b = dec.stdout.read(W * H * 3)
                if len(b) < W * H * 3: break
                enc.stdin.write(b); got += 1
            dec.wait()
            if got != n_mid:
                print("LOI: doc duoc", got, "/", n_mid, "khung", video); enc.stdin.close(); enc.wait(); return 3
        for f in render.ident_frames(W, H, outro, title=spec.get("ten_tap"), note=note):
            enc.stdin.write(np.ascontiguousarray(f).tobytes())
        enc.stdin.close(); enc.wait()
        parts = ([head] if k_idx > 0 else []) + [tail]
        lst = os.path.join(tmp, "list.txt")
        open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", cat], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", cat, "-i", video, "-map", "0:v", "-map", "1:a", "-c", "copy",
                        "-movflags", "+faststart", out], check=True)
        N2 = int(probe(out, "-select_streams", "v", "-count_packets", "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0").strip())
        if N2 != N:
            print("LOI: so khung", N2, "!=", N, video); return 4
        shutil.move(out, video)
        print("da sua", video, "khung", N, "noi tu", k_idx, "doan ket tu", o0)
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    sys.exit(main(args[0], args[1], ep="--ep" in sys.argv))
