"""Kiểm tra giọng đọc của một tập: Gemini nghe lại toàn bộ lời đọc → so với kịch bản (tỉ lệ khớp từ)."""
import sys, os, json, base64, subprocess, re, unicodedata, difflib
sys.path.insert(0, os.path.dirname(__file__)); import gemini
ROOT = "/home/claude/eduhistory-studio"
def norm(s):
    s = unicodedata.normalize("NFC", s.lower())
    for a, b in [("hoà", "hòa"), ("thuỷ", "thủy"), ("quý", "quí")]: s = s.replace(a, b)
    return re.sub(r"[^\w\s]", " ", s).split()
def main(ma):
    sp = json.load(open(f"{ROOT}/data/scripts/{ma}.json"))
    ref = " ".join(l[1] for c in sp["canh"] for l in c.get("loi", []))
    wav = f"{ROOT}/renders/_cache/{ma}/voice.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-ac", "1", "-ar", "16000", "-b:a", "48k", "/tmp/qa.mp3"], check=True)
    data = base64.b64encode(open("/tmp/qa.mp3", "rb").read()).decode()
    out, _ = gemini.generate([{"inline_data": {"mime_type": "audio/mp3", "data": data}},
                              {"text": "Chép lại chính xác toàn bộ lời nói tiếng Việt trong đoạn âm thanh, không thêm gì khác."}],
                             model="gemini-3.1-flash-lite", thinking=None, temperature=0, max_tokens=8000)
    a, b = norm(ref), norm(out)
    sm = difflib.SequenceMatcher(None, a, b); ratio = sm.ratio()
    diffs = [(" ".join(a[i1:i2]), " ".join(b[j1:j2])) for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag != "equal"]
    res = {"ma": ma, "khop_tu": round(ratio, 3), "so_tu": len(a), "khac_biet": diffs[:25]}
    os.makedirs(f"{ROOT}/data/qa", exist_ok=True)
    json.dump(res, open(f"{ROOT}/data/qa/giong-{ma}.json", "w"), ensure_ascii=False, indent=1)
    print(json.dumps(res, ensure_ascii=False)[:1500])
if __name__ == "__main__": main(sys.argv[1])
