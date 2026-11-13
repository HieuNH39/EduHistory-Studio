"""Làm lại RIÊNG phần âm thanh cho một tập đã dựng (không dựng lại hình): lời đọc (bộ nhớ đệm giọng) + nhạc nền
+ tiếng hiện trường của clip + âm thanh mô phỏng mới → ghép vào video cũ (chép nguyên luồng hình, giữ phụ đề/logo đã in sẵn).

Cách dùng:
  python3 tools/lam_lai_am_thanh.py data/scripts/L8-B8-02.json renders/v1/L8-B8-02.mp4 [ra.mp4] [--ghi-de] [--do-muc] [--khong-sfx]
    ra.mp4     : tệp ra (mặc định: <tên>_amthanh.mp4 cạnh tệp vào)
    --ghi-de   : thay luôn tệp video vào (ghi tạm rồi đổi tên, an toàn)
    --do-muc   : ghi thêm các lớp tách + đo mức (xem tools/qa_am_thanh.py)
    --khong-sfx: trộn như bản cũ (không có âm thanh mô phỏng) – để so sánh
Mốc thời gian lấy từ render.tinh_moc_canh() – đúng hàm mà render.py dùng, nên âm thanh khớp hình đã dựng."""
import os, sys, json, shutil, time, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
import render  # noqa: E402


def main(argv):
    flags = {a for a in argv if a.startswith("--")}
    args = [a for a in argv if not a.startswith("--")]
    if len(args) < 2:
        print(__doc__); return 2
    spec_path, video = args[0], args[1]
    if "--khong-sfx" in flags: os.environ["EDU_KHONG_SFX"] = "1"
    spec = render.load_spec(spec_path)
    t0 = time.time()
    scenes, starts, total, intro, outro = render.tinh_moc_canh(spec)
    dv = render.dur(video)
    print(f"{spec['id']}: thời lượng tính lại {total:.2f}s – video {dv:.2f}s – {len(scenes)} cảnh")
    if abs(dv - total) > 1.0 and "--ep" not in flags:
        print("LỖI: độ dài lệch > 1 s – kịch bản/giọng đọc đã đổi sau khi dựng video; cần dựng lại hình (hoặc thêm --ep để vẫn làm).")
        return 1
    if abs(dv - total) > 0.25:
        print(f"Cảnh báo: lệch {dv - total:+.2f}s")
    # clip Kling mới thêm SAU khi dựng video thì hình trong video chưa có clip đó → bỏ tiếng hiện trường của clip ấy
    t_video = os.path.getmtime(video)
    for s in scenes:
        cp = s.get("_clip")
        if cp and os.path.getmtime(cp) > t_video:
            print(f"  cảnh {s.get('so')}: clip {os.path.basename(cp)} mới hơn video → không dùng tiếng của clip này")
            s.pop("_clip")
    work = os.path.join(render.CACHE, f"{spec['id']}_am_thanh_lai")   # thư mục riêng, không đụng thư mục làm việc của render.py
    shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    log = {"id": spec["id"], "khau": {}}
    mix = render.dung_am_thanh(spec, scenes, starts, total, intro, outro, work, log, tach="--do-muc" in flags)
    if len(args) > 2: out = args[2]
    elif "--ghi-de" in flags: out = video
    else: out = os.path.splitext(video)[0] + "_amthanh.mp4"
    tmp = out + ".tam.mp4" if os.path.abspath(out) == os.path.abspath(video) else out
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    render.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-i", mix, "-map", "0:v:0", "-map", "1:a:0",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-shortest", tmp])   # 160k như render.py (bộ mã AAC ở 192k từng vọt đỉnh +3.8 dB trên tiếng TTS sắc)
    if tmp != out: os.replace(tmp, out)
    notes = os.path.join(work, "am_thanh.txt")
    print(f"→ {out}  ({time.time() - t0:.0f}s; sfx {log['khau'].get('sfx_s', '–')}s)")
    if os.path.exists(notes): print(open(notes).read())
    if log.get("am_thanh"): print("hiệu chỉnh:", json.dumps(log["am_thanh"], ensure_ascii=False))
    if "--do-muc" in flags:
        import qa_am_thanh
        qa_am_thanh.do(work, out)
    return 0


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    sys.exit(main(sys.argv[1:]))
