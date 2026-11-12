"""Giọng đọc bằng Gemini TTS (một hoặc nhiều người nói). Đầu ra WAV 24 kHz mono.
lines: danh sách (tên người nói, câu). speakers: {tên: voiceName}."""
import sys, os, json, base64, subprocess, urllib.request, urllib.error, time
sys.path.insert(0, "/home/claude/eduhistory-studio/tools"); import gemini
def tts(lines, speakers, out_wav, model="gemini-3.8-flash-tts", style=None, retries=5):
    multi = len(speakers) > 1
    if model.startswith("gemini-2.5"):
        text = "\n".join(f"{s}: {t}" for s, t in lines)
        parts = [{"text": (style + "\n\n" if style else "") + text}]
    else:
        parts = [{"text": t, "speechMetadata": {"speaker": s}} for s, t in lines] if multi else [{"text": " ".join(t for _, t in lines)}]
        if style: parts.insert(0, {"text": style}) if not multi else None
    cfg = {"responseModalities": ["AUDIO"]}
    if multi:
        cfg["speechConfig"] = {"multiSpeakerVoiceConfig": {"speakerVoiceConfigs": [
            {"speaker": n, "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": v}}} for n, v in speakers.items()]}}
    else:
        cfg["speechConfig"] = {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": list(speakers.values())[0]}}}
    body = json.dumps({"contents": [{"role": "user", "parts": parts}], "generationConfig": cfg}).encode()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini._key()}"
    for i in range(retries):
        try:
            req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
            d = json.load(urllib.request.urlopen(req, context=gemini._ctx, timeout=300))
            p = [x for x in d["candidates"][0]["content"]["parts"] if "inlineData" in x][0]["inlineData"]
            data = base64.b64decode(p["data"])
            if data[:4] == b"RIFF":
                open(out_wav, "wb").write(data)
            else:
                raw = out_wav + ".pcm"; open(raw, "wb").write(data)
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "s16le", "-ar", "24000", "-ac", "1", "-i", raw, out_wav], check=True)
                os.remove(raw)
            return out_wav
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:300]
            if e.code == 429 and "quota" in msg.lower():
                raise RuntimeError(f"429 quota {msg}")
            if e.code in (429, 500, 502, 503, 504) and i < retries - 1:
                print("[tts]", e.code, msg[:150], flush=True); time.sleep(10 * (i + 1)); continue
            raise RuntimeError(f"{e.code} {msg}")
