"""Giọng đọc VieNeu-TTS v3 Turbo (miễn phí, chạy CPU, Apache-2.0) – quyết định GVHD 13/11/2026.
- Nhật Minh, Hân Hân: nhân bản giọng từ mẫu Puck / Zephyr mà GVHD đã duyệt (brand/voices/ref).
- Nhân vật lịch sử: giọng người Việt có sẵn của VieNeu, chọn theo vùng miền (pipeline/config.json → tts.vieneu_voices).
Mỗi câu đọc riêng → nối lại, nên biết chính xác mốc từng câu cho phụ đề."""
import os, json, hashlib, re
import numpy as np, soundfile as sf
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(ROOT, "pipeline/config.json")))
CACHE = os.path.join(ROOT, "renders/_cache/vieneu"); os.makedirs(CACHE, exist_ok=True)
MODEL_DIR = os.environ.get("VIENEU_ONNX_DIR", "/home/claude/models/vieneu-v3/onnx_update")
_tts = None

def engine():
    global _tts
    if _tts is None:
        from vieneu import Vieneu
        _tts = Vieneu(onnx_dir=MODEL_DIR)
    return _tts

# đọc đúng một số từ viết tắt / số liệu hay gặp
_REPL = [(r"\bTCN\b", "trước Công nguyên"), (r"\bSGK\b", "sách giáo khoa"), (r"(\d)\s*km\b", r"\1 ki-lô-mét"), (r"(\d)\s*m\b", r"\1 mét")]
def normalize(text):
    for a, b in _REPL: text = re.sub(a, b, text)
    return text

def voice_kw(speaker):
    v = CFG["tts"]["vieneu_voices"].get(speaker) or CFG["tts"]["vieneu_voices"]["_mac_dinh"]
    if v.startswith("ref:"): return {"ref_audio": os.path.join(ROOT, v[4:])}
    return {"voice": engine().get_preset_voice(v)}

def line_wav(speaker, text):
    v = CFG["tts"]["vieneu_voices"].get(speaker) or CFG["tts"]["vieneu_voices"]["_mac_dinh"]
    key = hashlib.sha1(json.dumps([speaker, v, text, "v3turbo"], ensure_ascii=False).encode()).hexdigest()[:16]
    out = os.path.join(CACHE, f"{key}.wav")
    if not os.path.exists(out):
        t = engine(); w = t.infer(normalize(text), **voice_kw(speaker))
        sf.write(out, w, t.sample_rate)
    return out

def scene(lines, out_wav, gap=0.32):
    """lines: [(người nói, câu, ...)] → ghi out_wav (48 kHz mono), trả về [(đầu, cuối)] từng câu."""
    parts, bounds, t, sr = [], [], 0.0, 48000
    for sp, text, *_ in lines:
        w, sr = sf.read(line_wav(sp, text), dtype="float32")
        # cắt lặng hai đầu cho gọn
        nz = np.where(np.abs(w) > 0.008)[0]
        if len(nz): w = w[max(0, nz[0] - int(0.05 * sr)): nz[-1] + int(0.12 * sr)]
        bounds.append((t, t + len(w) / sr)); parts += [w, np.zeros(int(gap * sr), np.float32)]; t += len(w) / sr + gap
    sf.write(out_wav, np.concatenate(parts[:-1]) if parts else np.zeros(1, np.float32), sr)
    return bounds
