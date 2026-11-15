"""Minimal Gemini REST client used by the EduHistory pipeline."""
import os, json, base64, time, urllib.request, urllib.error, ssl
def _key():
    k = os.environ.get("GEMINI_API_KEY")
    if not k:
        for line in open("/home/claude/eduhistory/.env"):
            if line.startswith("GEMINI_API_KEY="): k = line.strip().split("=",1)[1]
    return k
_ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
def generate(parts, model="gemini-3.5-flash", temperature=0.1, json_mode=False, retries=6, system=None, max_tokens=None, thinking="minimal"):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={_key()}"
    cfg = {"temperature": temperature}
    if json_mode: cfg["responseMimeType"] = "application/json"
    if max_tokens: cfg["maxOutputTokens"] = max_tokens
    if thinking: cfg["thinkingConfig"] = {"thinkingLevel": thinking}
    body = {"contents":[{"role":"user","parts":parts}], "generationConfig": cfg}
    if system: body["systemInstruction"] = {"parts":[{"text":system}]}
    data = json.dumps(body).encode()
    for i in range(retries):
        req = urllib.request.Request(url, data=data, headers={"Content-Type":"application/json"})
        try:
            with urllib.request.urlopen(req, context=_ctx, timeout=300) as r:
                d = json.load(r)
            c = d["candidates"][0]
            txt = "".join(p.get("text","") for p in c["content"]["parts"] if not p.get("thought"))
            return txt, d.get("usageMetadata",{})
        except urllib.error.HTTPError as e:
            full = e.read().decode(); msg = full[:400]
            if e.code == 429 and "PerDay" in full:
                raise RuntimeError(f"quota_day {model}: hết lượt trong ngày")
            if e.code in (429,500,503):
                wait = min(60, 8*(i+1)); print(f"[gemini] {e.code} retry in {wait}s: {msg[:120]}", flush=True); time.sleep(wait); continue
            raise RuntimeError(f"{e.code} {msg}")
    raise RuntimeError("gemini: retries exhausted")
def image_part(path, mime="image/png"):
    return {"inlineData":{"mimeType":mime,"data":base64.b64encode(open(path,"rb").read()).decode()}}
