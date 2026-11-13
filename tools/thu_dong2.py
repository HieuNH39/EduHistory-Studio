"""Dựng thử một cảnh bằng dong2 (có tiếng) để kiểm tra: python3 tools/thu_dong2.py MA SO [giây]"""
import sys, os, json, time, subprocess
sys.path.insert(0, "/home/claude/eduhistory-studio/pipeline")
import render, dong2
ma, so = sys.argv[1], int(sys.argv[2]); sec = float(sys.argv[3]) if len(sys.argv) > 3 else None
spec = render.load_spec(f"data/scripts/{ma}.json"); sc = [c for c in spec["canh"] if c["so"] == so][0]
wav, bounds = render.voice_for(sc["loi"], pauses=sc.get("nghi_sau_cau"))
sc = dict(sc, wav=wav, bounds=bounds)
img = render.load_rgb(f"assets/episodes/{ma}/canh-{so:02d}.jpg")
W, H, fps = 1920, 1080, 30; n = int((sec or render.dur(wav) + 0.5) * fps)
out = f"tmp/qa/dong2_{ma}_{so:02d}.mp4"
ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
                       "-i", wav, "-af", "apad", "-t", f"{n / fps:.2f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p", "-c:a", "aac", out], stdin=subprocess.PIPE)
t0 = time.time()
for fr in dong2.frames(img, W, H, n, fps, sc=sc, seed=so): ff.stdin.write(fr.tobytes())
ff.stdin.close(); ff.wait(); print(out, n, "frames", round(time.time() - t0, 1), "s")
