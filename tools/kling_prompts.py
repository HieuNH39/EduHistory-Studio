"""Sinh lời nhắc chuyển động (image-to-video) cho Kling từ kịch bản: mỗi cảnh dẫn chuyện/tái hiện/du hành
có ảnh khung đầu (Gemini) → một lời nhắc tiếng Anh mô tả cử động nhân vật, máy quay, hiệu ứng môi trường.
Ghi ra data/kling/<mã>.json để dùng khi tạo clip trên web Kling."""
import json, sys, os, glob
sys.path.insert(0, os.path.dirname(__file__)); import gemini
ROOT = "/home/claude/eduhistory-studio"
SYS = ("You write motion prompts for an image-to-video model (Kling). The first frame is a 2D animated-film illustration "
       "for a Vietnamese school history video. Describe ONLY motion that should happen in about 5-10 seconds: what each visible "
       "character does (walks, gestures, turns head, speaks with natural lip movement, bows, rows, raises a flag...), "
       "environment motion (water flowing, flags waving, smoke drifting, leaves moving), and one simple camera move "
       "(slow push-in, slow pan, gentle orbit). Keep the art style, costumes and faces unchanged; no new characters, no text, "
       "no logos, no gore, no violence shown in detail. 45-80 words, present tense, one paragraph.")
MODELS = os.environ.get("KLING_MODELS", "gemini-3.1-flash-lite,gemini-3.5-flash-lite,gemini-3.5-flash").split(",")
NEG = "text, subtitles, watermark, logo, extra fingers, distorted face, morphing, flicker, blood, gore, modern objects in historical scenes"
def main(ma):
    sp = json.load(open(f"{ROOT}/data/scripts/{ma}.json")); out = {"ma": ma, "negative": NEG, "canh": []}
    for c in sp["canh"]:
        if c.get("lop") not in ("dan_chuyen", "tai_hien", "du_hanh"): continue
        speakers = sorted({l[0] for l in c.get("loi", [])})
        dur = 10 if sum(len(l[1]) for l in c.get("loi", [])) > 130 else 5
        q = (f"Scene description (Vietnamese): {c.get('hinh','')}\nScene type: {c['lop']}\n"
             f"People who speak in this scene (narrators Nhật Minh / Hân Hân are two 15-year-old students in orange polo shirts): {', '.join(speakers)}\n"
             f"Clip length: {dur} seconds. Write the motion prompt in English only.")
        txt = None
        for lan in range(6):
            if not MODELS: break
            try:
                txt, _ = gemini.generate([{"text": q}], model=MODELS[0], system=SYS, temperature=0.4, thinking=None, max_tokens=300); break
            except Exception as e:
                if "quota_day" in str(e):
                    if MODELS and MODELS[0] in str(e): print("  hết lượt ngày:", MODELS.pop(0), flush=True)
                    continue
                print("  lỗi", ma, c["so"], str(e)[:80], flush=True); import time; time.sleep(8 * (lan + 1))
        if not txt: continue
        out["canh"].append({"so": c["so"], "lop": c["lop"], "thoi_luong": dur, "prompt": txt.strip()})
        print(ma, c["so"], dur, txt.strip()[:90], flush=True)
    if not MODELS: print("  bỏ ghi", ma, "(hết lượt mọi mô hình)", flush=True); return
    os.makedirs(f"{ROOT}/data/kling", exist_ok=True)
    json.dump(out, open(f"{ROOT}/data/kling/{ma}.json", "w"), ensure_ascii=False, indent=1)
if __name__ == "__main__":
    ids = sys.argv[1:] or [os.path.basename(p)[:-5] for p in sorted(glob.glob(f"{ROOT}/data/scripts/*.json"))]
    for m in ids:
        if not os.path.exists(f"{ROOT}/data/kling/{m}.json"): main(m)
