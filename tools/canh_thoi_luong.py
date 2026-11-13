"""Tính thời lượng từng cảnh (giọng đọc đã có trong bộ nhớ đệm) để chọn độ dài clip Kling 5 s / 10 s."""
import json, sys, os, hashlib, subprocess
ROOT = "/home/claude/eduhistory-studio"; CACHE = f"{ROOT}/renders/_cache"
def dur(p): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout or 0)
def canh(ma):
    spec = json.load(open(f"{ROOT}/data/scripts/{ma}.json")); out = []
    for sc in spec["canh"]:
        lines = sc.get("loi", []); pauses = {"0": 3.4} if sc.get("lop") == "cau_hoi" else sc.get("nghi_sau_cau")
        if lines:
            key = hashlib.sha1(json.dumps([lines, pauses], ensure_ascii=False).encode()).hexdigest()[:16]
            w = f"{CACHE}/vn_scene_{key}.wav"; sp = dur(w) if os.path.exists(w) else None
        else: sp = sc.get("thoi_luong", 3.0)
        L = None if sp is None else max(sp + (0.45 if lines else 0), sc.get("thoi_luong_toi_thieu", 0)) + 0.5
        out.append((sc["so"], sc.get("lop"), L))
    return out
if __name__ == "__main__":
    for ma in sys.argv[1:]:
        for so, lop, L in canh(ma):
            if lop in ("dan_chuyen", "tai_hien", "du_hanh"): print(ma, so, lop, None if L is None else round(L, 1), "→", "?" if L is None else ("5s" if L <= 6.8 else "10s" if L <= 13 else "10s+kéo dài"))
