#!/usr/bin/env python3
"""Hoàn tất một tập từ phần hình đã dựng sẵn trong bộ nhớ đệm (renders/_cache/<MA>/video.mp4) khi bước âm thanh
hoặc ghép cuối bị lỗi/bị ngắt: tính lại mốc (giọng đọc có sẵn trong bộ nhớ đệm) → trộn âm thanh → phụ đề → logo + ghép.
Không dựng lại hình.

Dùng: python3 tools/hoan_tat_tu_cache.py data/scripts/L7-B14-04.json renders/v1
"""
import os, sys, time, json, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
import render  # noqa: E402


def main(spec_path, out_dir):
    spec = render.load_spec(spec_path)
    vertical = spec.get("huong") == "doc"
    W, H = render.CFG["video"]["portrait"] if vertical else render.CFG["video"]["landscape"]
    work = os.path.join(render.CACHE, spec["id"])
    silent = os.path.join(work, "video.mp4")
    assert os.path.exists(silent), "chưa có hình trong bộ nhớ đệm: " + silent
    scenes, starts, total, intro, outro = render.tinh_moc_canh(spec)
    dv = render.dur(silent)
    print(f"{spec['id']}: tính lại {total:.2f}s – hình {dv:.2f}s")
    if abs(dv - total) > 1.0:
        raise SystemExit("Lệch > 1 s: kịch bản/giọng đã đổi, cần dựng lại hình.")
    log = {"id": spec["id"], "bat_dau": time.time(), "khau": {}, "ghi_chu": "hoàn tất từ bộ nhớ đệm"}
    t0 = time.time()
    mix = render.dung_am_thanh(spec, scenes, starts, total, intro, outro, work, log)
    log["khau"]["am_thanh_s"] = round(time.time() - t0, 1)
    cues = []
    for k, s in enumerate(scenes):
        if not s["wav"]: continue
        for (a, b), ln in zip(s["bounds"], s["loi"]):
            cues.append((starts[k] + 0.15 + a, starts[k] + 0.15 + b, ln[1], ln[2] if len(ln) > 2 else ""))
    ass = os.path.join(work, "subs.ass"); open(ass, "w").write(render.build_ass(cues, W, H, vertical))
    wm = os.path.join(ROOT, render.CFG["logo"]["watermark"])
    wm_w = int(W * (0.30 if vertical else 0.17)); margin = int(W * 0.025)
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"{spec['id']}.mp4"); tmp = out + ".tam.mp4"
    t0 = time.time()
    render.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", mix, "-i", wm, "-filter_complex",
                f"[2]scale={wm_w}:-1,format=rgba,colorchannelmixer=aa=0.92[w];"
                f"[0][w]overlay=W-w-{margin}:{margin}:enable='between(t,{intro:.2f},{total-outro:.2f})'[v1];"
                f"[v1]ass={ass}:fontsdir={render.FONT_DIR}[v]",
                "-map", "[v]", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-shortest", tmp])
    os.replace(tmp, out)
    log["khau"]["ghep_cuoi_s"] = round(time.time() - t0, 1); log["thoi_luong_video_s"] = round(total, 1)
    with open(os.path.join(ROOT, "data/logs/san-xuat.jsonl"), "a") as f:
        f.write(json.dumps(log, ensure_ascii=False) + "\n")
    print("→", out, json.dumps(log["khau"], ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "renders"))
