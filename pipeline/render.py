"""EduHistory Studio – dựng video tự động từ một tệp kịch bản (JSON).

Cách dùng:  python3 render.py duong-dan/kich-ban.json  [--out renders/]

Kịch bản (rút gọn):
{
  "id": "L7-B14-T04", "huong": "ngang" | "doc",
  "ten_tap": "...", "ten_tap_en": "...",
  "nhac": "assets/music/xxx.mp3" | null,
  "canh": [
    {"anh": "duong/dan/anh.png", "chuyen_dong": "vao|ra|trai|phai|len|xuong",
     "loi": [["Hân Hân", "câu tiếng Việt", "English line"], ...]},
    {"video": "duong/dan/clip.mp4", "loi": [...]}          # cảnh dựng sẵn bằng code (bản đồ, mô phỏng)
  ]
}
Mỗi cảnh: giọng đọc (Gemini TTS, có bộ nhớ đệm) → thời lượng cảnh → hình chuyển động mượt
→ ghép, chuyển cảnh mờ dần → phụ đề song ngữ (Việt trên, Anh dưới) → logo góc → nhạc nền tự hạ khi có lời
→ chuẩn âm lượng −14 LUFS → MP4 H.264.
"""
import sys, os, json, hashlib, subprocess, re, math, shutil, time
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
import tts_gemini

CFG = json.load(open(os.path.join(ROOT, "pipeline/config.json")))
FPS = CFG["video"]["fps"]
CACHE = os.path.join(ROOT, "renders/_cache"); os.makedirs(CACHE, exist_ok=True)
FONT_DIR = os.path.join(ROOT, "assets/fonts")
XFADE = 0.5           # giây chuyển cảnh
SCENE_PAD = 0.45      # khoảng lặng cuối mỗi cảnh

def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise RuntimeError(" ".join(cmd[:6]) + "...\n" + r.stderr[-1500:])
    return r

def dur(path):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).stdout.strip())

# ---------------------------------------------------------------- giọng đọc
_QUOTA_OUT = set()

def _tts_group(lines):
    voices = CFG["tts"]["voices"]
    speakers = {sp: voices.get(sp, "Puck") for sp, *_ in lines}
    for model in (CFG["tts"]["model"], CFG["tts"]["fallback_model"]):
        key = hashlib.sha1(json.dumps([lines, speakers, model], ensure_ascii=False).encode()).hexdigest()[:16]
        wav = os.path.join(CACHE, f"tts_{key}.wav")
        if os.path.exists(wav): return wav
    for model in (CFG["tts"]["model"], CFG["tts"]["fallback_model"]):
        if model in _QUOTA_OUT: continue
        key = hashlib.sha1(json.dumps([lines, speakers, model], ensure_ascii=False).encode()).hexdigest()[:16]
        wav = os.path.join(CACHE, f"tts_{key}.wav")
        try:
            tts_gemini.tts([(sp, t) for sp, t, *_ in lines], speakers, wav, model=model, retries=4)
            return wav
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower(): _QUOTA_OUT.add(model); continue
            raise
    raise RuntimeError("Hết hạn mức giọng đọc Gemini TTS ở mọi mô hình")

def voice_for(lines, gap=0.28, pauses=None):
    if CFG["tts"].get("engine") == "vieneu":
        import tts_vieneu
        key = hashlib.sha1(json.dumps([lines, pauses], ensure_ascii=False).encode()).hexdigest()[:16]
        out = os.path.join(CACHE, f"vn_scene_{key}.wav")
        return out, tts_vieneu.scene(lines, out, pauses=pauses)
    return _voice_gemini(lines, gap)

def _voice_gemini(lines, gap=0.28):
    """Lời một cảnh → (wav, [(đầu, cuối) từng câu]). Gemini TTS nói nhiều giọng tối đa 2 người/lần,
    nên cảnh có ≥3 người nói được chia nhóm liên tiếp ≤2 người, đọc riêng rồi nối."""
    groups, cur = [], []
    for ln in lines:
        if cur and len({x[0] for x in cur} | {ln[0]}) > 2:
            groups.append(cur); cur = []
        cur.append(ln)
    if cur: groups.append(cur)
    wavs = [_tts_group(g) for g in groups]
    if len(wavs) == 1:
        return wavs[0], line_bounds(wavs[0], groups[0])
    key = hashlib.sha1("|".join(wavs).encode()).hexdigest()[:16]
    out = os.path.join(CACHE, f"tts_cat_{key}.wav")
    bounds, t = [], 0.0
    for w, g in zip(wavs, groups):
        bounds += [(a + t, b + t) for a, b in line_bounds(w, g)]; t += dur(w) + gap
    if not os.path.exists(out):
        inp = []; flt = []
        for k, w in enumerate(wavs):
            inp += ["-i", w]; flt.append(f"[{k}]aresample=24000,aformat=channel_layouts=mono,apad=pad_dur={gap}[a{k}]")
        run(["ffmpeg", "-y", "-loglevel", "error", *inp, "-filter_complex",
             ";".join(flt) + ";" + "".join(f"[a{k}]" for k in range(len(wavs))) + f"concat=n={len(wavs)}:v=0:a=1[o]", "-map", "[o]", out])
    return out, bounds

def line_bounds(wav, lines):
    """Ước lượng thời điểm bắt đầu/kết thúc từng câu: tìm khoảng lặng, khớp với số câu; dự phòng chia theo độ dài chữ."""
    total = dur(wav)
    n = len(lines)
    if n == 1:
        return [(0.0, total)]
    r = subprocess.run(["ffmpeg", "-i", wav, "-af", "silencedetect=noise=-33dB:d=0.18", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    sil = [(float(a), float(b)) for a, b in zip(re.findall(r"silence_start: ([\d.]+)", r), re.findall(r"silence_end: ([\d.]+)", r))]
    sil = [s for s in sil if 0.3 < s[0] < total - 0.3]
    weights = [len(t) for _, t, *_ in lines]
    expect = []; acc = 0
    for w in weights[:-1]:
        acc += w; expect.append(total * acc / sum(weights))
    cuts = []
    for e in expect:                       # khoảng lặng gần vị trí dự kiến nhất
        cand = [s for s in sil if s not in cuts]
        if cand:
            best = min(cand, key=lambda s: abs((s[0] + s[1]) / 2 - e))
            if abs((best[0] + best[1]) / 2 - e) < total * 0.18:
                cuts.append(best); continue
        cuts.append((e, e))
    cuts.sort()
    bounds = []; start = 0.0
    for a, b in cuts:
        bounds.append((start, a)); start = b
    bounds.append((start, total))
    return bounds

# ---------------------------------------------------------------- phụ đề song ngữ (ASS)
def ass_time(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def chunk(text, maxlen):
    """Chia câu dài thành các đoạn ngắn, ưu tiên ngắt ở dấu câu."""
    words = text.split(); out = []; cur = ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > maxlen:
            out.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
        if cur and cur[-1] in ",.;:!?" and len(cur) > maxlen * 0.55:
            out.append(cur); cur = ""
    if cur: out.append(cur)
    # tránh đoạn cuối quá ngắn (vd. "ta."): gộp hai đoạn cuối rồi chia đôi cho cân
    if len(out) >= 2 and len(out[-1]) < maxlen * 0.35:
        ws = (out[-2] + " " + out[-1]).split(); tot = sum(len(w) + 1 for w in ws); c = 0; best = None
        for i, w in enumerate(ws[:-1]):
            c += len(w) + 1; cost = abs(c / tot - 0.5) - (0.08 if w[-1] in ",.;:!?" else 0)
            if best is None or cost < best[0]: best = (cost, i)
        k = best[1] + 1; out[-2:] = [" ".join(ws[:k]), " ".join(ws[k:])]
    return out

def align_en(en, vparts):
    """Chia phụ đề tiếng Anh thành đúng số đoạn của tiếng Việt, theo tỉ lệ độ dài,
    ưu tiên ngắt sau dấu câu gần điểm cắt để hai dòng song ngữ khớp ý."""
    n = len(vparts); words = en.split()
    if n <= 1 or not words: return [en] + [""] * (n - 1) if n else []
    tot_v = sum(len(v) for v in vparts); cum = []; c = 0
    for w in words: c += len(w) + 1; cum.append(c)
    tot_e = cum[-1]; cuts = []; acc = 0; start = 0
    for v in vparts[:-1]:
        acc += len(v); f = acc / tot_v; best = None
        for i in range(start, len(words) - 1):
            g = cum[i] / tot_e; cost = abs(g - f) - (0.07 if words[i][-1] in ",.;:!?" else 0)
            if best is None or cost < best[0]: best = (cost, i)
        if best is None: cuts.append(len(words) - 1); continue
        cuts.append(best[1]); start = best[1] + 1
    out = []; s = 0
    for ci in cuts: out.append(" ".join(words[s:ci + 1])); s = ci + 1
    out.append(" ".join(words[s:]))
    return out

def build_ass(cues, W, H, vertical):
    vi_size = int(H * (0.034 if vertical else 0.046))
    en_size = int(vi_size * 0.78)
    mv_en = int(H * (0.20 if vertical else 0.055))
    mv_vi = mv_en + int(en_size * 1.25) + 2 * max(4, en_size // 6) + 6
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: VI,Be Vietnam Pro,{vi_size},&H00FFFFFF,&H00FFFFFF,&H7A1A1206,&H7A1A1206,-1,0,0,0,100,100,0,0,3,{max(4,vi_size//6)},0,2,60,60,{mv_vi},1
Style: EN,Be Vietnam Pro,{en_size},&H00A8E6FF,&H00A8E6FF,&H7A1A1206,&H7A1A1206,0,-1,0,0,100,100,0,0,3,{max(4,en_size//6)},0,2,60,60,{mv_en},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    maxlen = 34 if vertical else 58
    ev = []
    for t0, t1, vi, en in cues:
        ml = maxlen
        while True:
            vparts = chunk(vi, ml)
            eparts = align_en(en or "", vparts)
            if ml <= 22 or all(len(e) <= ml * 1.45 for e in eparts): break
            ml -= 6
        weights = [max(len(v), 1) for v in vparts]; span = t1 - t0; acc = t0
        for v, e, w in zip(vparts, eparts, weights):
            d = span * w / sum(weights)
            ev.append(f"Dialogue: 0,{ass_time(acc)},{ass_time(acc + d)},VI,,0,0,0,,{v}")
            if e: ev.append(f"Dialogue: 1,{ass_time(acc)},{ass_time(acc + d)},EN,,0,0,0,,{e}")
            acc += d
    return head + "\n".join(ev) + "\n"

# ---------------------------------------------------------------- hình chuyển động
def load_rgb(path):
    im = cv2.imread(path, cv2.IMREAD_COLOR)
    if im is None: raise FileNotFoundError(path)
    return cv2.cvtColor(im, cv2.COLOR_BGR2RGB)

def ease(t):  # chậm – nhanh – chậm
    return 0.5 - 0.5 * math.cos(math.pi * min(max(t, 0), 1))

def still_frames(img, W, H, nframes, motion="vao", strength=0.12):
    """Chuyển động máy quay mượt (sub-pixel) trên ảnh tĩnh."""
    h, w = img.shape[:2]
    base = max(W / w, H / h)                         # phủ kín khung
    for i in range(nframes):
        t = ease(i / max(nframes - 1, 1))
        z0, z1 = (1.0, 1.0 + strength) if motion != "ra" else (1.0 + strength, 1.0)
        z = base * (z0 + (z1 - z0) * t)
        dx = dy = 0.0
        slack_x = (w * z - W) / 2; slack_y = (h * z - H) / 2
        if motion == "trai":  dx = slack_x * (1 - 2 * t) * 0.9
        if motion == "phai":  dx = -slack_x * (1 - 2 * t) * 0.9
        if motion == "len":   dy = slack_y * (1 - 2 * t) * 0.9
        if motion == "xuong": dy = -slack_y * (1 - 2 * t) * 0.9
        M = np.array([[z, 0, W / 2 - w * z / 2 + dx], [0, z, H / 2 - h * z / 2 + dy]], dtype=np.float32)
        yield cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)

def video_frames(path, W, H, nframes):
    tmp = os.path.join(CACHE, "vclip_" + hashlib.sha1(f"{path}{W}{H}".encode()).hexdigest()[:10] + ".rgb")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-vf",
         f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", tmp])
    data = np.fromfile(tmp, dtype=np.uint8); os.remove(tmp)
    frames = data.reshape(-1, H, W, 3)
    for i in range(nframes):
        yield frames[min(i, len(frames) - 1)]

# ---------------------------------------------------------------- hình hiệu logo (mở đầu / kết)
def ident_frames(W, H, seconds=2.6, title=None, note=None):
    icon = Image.open(os.path.join(ROOT, CFG["logo"]["icon"])).convert("RGBA")
    size = int(min(W, H) * 0.34); icon = icon.resize((size, size), Image.LANCZOS)
    f_big = ImageFont.truetype(os.path.join(FONT_DIR, "be-vietnam-pro-900-normal.ttf"), int(size * 0.34))
    f_small = ImageFont.truetype(os.path.join(FONT_DIR, "be-vietnam-pro-600-normal.ttf"), int(size * 0.13))
    n = int(seconds * FPS)
    for i in range(n):
        t = i / n
        bg = Image.new("RGB", (W, H), (16, 35, 63))
        # vòng sáng mờ
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(glow)
        r = int(size * (0.62 + 0.08 * math.sin(t * math.pi)))
        d.ellipse([W // 2 - r, int(H * 0.42) - r, W // 2 + r, int(H * 0.42) + r], fill=(201, 139, 43, int(40 * ease(t * 2))))
        bg.paste(glow, (0, 0), glow)
        k = ease(min(t / 0.45, 1)); s = max(int(size * (0.6 + 0.4 * k)), 2)
        ic = icon.rotate(-90 * (1 - k), resample=Image.BICUBIC).resize((s, s), Image.LANCZOS)
        a = ic.split()[3].point(lambda p: int(p * k)); ic.putalpha(a)
        bg.paste(ic, (W // 2 - s // 2, int(H * 0.42) - s // 2), ic)
        kt = ease(min(max((t - 0.35) / 0.35, 0), 1))
        if kt > 0:
            txt = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(txt)
            y = int(H * 0.42 + size * 0.62 + (1 - kt) * 30)
            w1 = d.textlength("Edu", font=f_big); w2 = d.textlength("History", font=f_big)
            x = W // 2 - int((w1 + w2) / 2)
            d.text((x, y), "Edu", font=f_big, fill=(255, 246, 230, int(255 * kt)))
            d.text((x + w1, y), "History", font=f_big, fill=(242, 107, 29, int(255 * kt)))
            sub = "S T U D I O"; ws = d.textlength(sub, font=f_small)
            d.text((W // 2 - ws / 2, y + int(size * 0.42)), sub, font=f_small, fill=(201, 139, 43, int(255 * kt)))
            if title:
                f_t = ImageFont.truetype(os.path.join(FONT_DIR, "be-vietnam-pro-700-normal.ttf"), int(size * 0.12))
                wt = d.textlength(title, font=f_t)
                d.text((W // 2 - wt / 2, y + int(size * 0.68)), title, font=f_t, fill=(255, 255, 255, int(230 * kt)))
            if note:
                f_n = ImageFont.truetype(os.path.join(FONT_DIR, "be-vietnam-pro-400-italic.ttf"), int(size * 0.075))
                wn = d.textlength(note, font=f_n)
                d.text((W // 2 - wn / 2, H - int(size * 0.32)), note, font=f_n, fill=(220, 210, 190, int(220 * kt)))
            bg.paste(txt, (0, 0), txt)
        fade = min(1, (n - i) / (0.35 * FPS))
        arr = np.asarray(bg).astype(np.float32) * fade
        yield arr.astype(np.uint8)

# ---------------------------------------------------------------- dựng tập
def load_spec(path):
    spec = json.load(open(path))
    spec.setdefault("id", spec.get("ma"))
    if isinstance(spec.get("nhac"), dict): spec["nhac"] = spec["nhac"].get("tep")
    return spec

def scene_source(spec, sc, W, H, n):
    """Chọn nguồn hình: sa bàn code / chuyển cảnh trống đồng / clip video / ảnh tĩnh / khung chờ."""
    rp = lambda x: x if os.path.isabs(x) else os.path.join(ROOT, x)
    lop = sc.get("lop")
    if lop == "sa_ban":
        spec_file = os.path.join(ROOT, "pipeline/maps/specs", sc["sa_ban"] + ".json")
        if json.load(open(spec_file)).get("phien_ban") == 2:
            sys.path.insert(0, os.path.join(ROOT, "pipeline/maps"))
            import saban2
            return saban2.frames(sc["sa_ban"], sc["pha"], W, H, n, FPS)
        from maps import saban
        return saban.frames(sc["sa_ban"], sc["pha"], W, H, n, FPS)
    if lop == "chuyen_canh":
        import effects
        return effects.trong_dong(W, H, n, sc.get("chu", ""))
    if lop == "cau_hoi":
        import effects
        b = sc.get("bounds") or [(0, 3), (6, 8)]
        return effects.cau_hoi(W, H, n, sc["cau_hoi"], FPS, q_end=b[0][1] + 0.15, reveal=b[-1][0] + 0.15)
    if lop in ("truc_thoi_gian", "ghi_nho"):
        import effects
        items = sc["moc"] if lop == "truc_thoi_gian" else sc["y"]
        b = sc.get("bounds") or []
        if sc.get("hien_luc"): times = sc["hien_luc"]
        elif len(b) == len(items): times = [x[0] + 0.1 for x in b]
        elif b:
            a0, a1 = b[0][0], b[-1][1]; m = len(items)
            times = [a0 + 0.1 + k * (a1 - a0) / m for k in range(m)]
        else: times = None
        fn = effects.truc_thoi_gian if lop == "truc_thoi_gian" else effects.ghi_nho
        return fn(W, H, n, items, FPS, times=times, **({"title": sc["tieu_de"]} if sc.get("tieu_de") else {}))
    base = os.path.join(ROOT, "assets/episodes", spec["id"], f"canh-{int(sc.get('so', 0)):02d}")
    vid = sc.get("video") or (base + ".mp4" if os.path.exists(base + ".mp4") else None)
    img = sc.get("anh") or next((base + e for e in (".png", ".jpg", ".webp") if os.path.exists(base + e)), None)
    if vid: return video_frames(rp(vid), W, H, n)
    if img: return still_frames(load_rgb(rp(img)), W, H, n, sc.get("chuyen_dong") if sc.get("chuyen_dong") in ("vao", "ra", "trai", "phai", "len", "xuong") else "vao")
    import effects
    return effects.cho(W, H, n, sc)

def render(spec_path, out_dir=None):
    spec = load_spec(spec_path)
    vertical = spec.get("huong") == "doc"
    W, H = CFG["video"]["portrait"] if vertical else CFG["video"]["landscape"]
    out_dir = out_dir or os.path.join(ROOT, "renders"); os.makedirs(out_dir, exist_ok=True)
    work = os.path.join(CACHE, spec["id"]); shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    log = {"id": spec["id"], "bat_dau": time.time(), "khau": {}}

    t0 = time.time()
    scenes = []
    for sc in spec["canh"]:
        lines = sc.get("loi", [])
        pauses = {"0": 3.4} if sc.get("lop") == "cau_hoi" else sc.get("nghi_sau_cau")
        wav, bounds = voice_for(lines, pauses=pauses) if lines else (None, [])
        speech = dur(wav) if wav else sc.get("thoi_luong", 3.0)
        length = max(speech + (SCENE_PAD if wav else 0), sc.get("thoi_luong_toi_thieu", 0)) + XFADE
        scenes.append(dict(sc, wav=wav, bounds=bounds, speech=speech, length=length))
    log["khau"]["giong_doc_s"] = round(time.time() - t0, 1)

    intro = 0 if vertical else 2.6
    outro = (2.6 if vertical else 3.0) + (1.2 if spec.get("ghi_chu_tai_hien") else 0)
    # mốc thời gian
    starts = []; cur = intro
    for s in scenes:
        starts.append(cur); cur += s["length"] - XFADE
    total = cur + XFADE + outro

    # ---- hình
    t0 = time.time()
    silent = os.path.join(work, "video.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
                           "-pix_fmt", "yuv420p", silent], stdin=subprocess.PIPE)
    def write(fr): ff.stdin.write(np.ascontiguousarray(fr).tobytes())
    if intro:
        for fr in ident_frames(W, H, intro): write(fr)
    prev_tail = None
    xf = int(XFADE * FPS)
    for k, s in enumerate(scenes):
        n = int(round(s["length"] * FPS))
        frames_iter = iter(scene_source(spec, s, W, H, n))
        for i in range(n):
            fr = next(frames_iter)
            if i < xf and prev_tail is not None:
                a = (i + 1) / xf
                fr = (prev_tail[i].astype(np.float32) * (1 - a) + fr.astype(np.float32) * a).astype(np.uint8)
            elif i < xf and k == 0:
                fr = (fr.astype(np.float32) * ((i + 1) / xf)).astype(np.uint8)
            if i >= n - xf and k < len(scenes) - 1:
                if i == n - xf: tail = []
                tail.append(fr); continue
            write(fr)
        prev_tail = tail if k < len(scenes) - 1 else None
    for fr in ident_frames(W, H, outro, title=spec.get("ten_tap"), note=spec.get("ghi_chu_tai_hien")): write(fr)
    ff.stdin.close(); ff.wait()
    log["khau"]["dung_hinh_s"] = round(time.time() - t0, 1)

    # ---- âm thanh: lời đọc đặt đúng mốc + nhạc nền tự hạ
    t0 = time.time()
    voice = os.path.join(work, "voice.wav")
    inputs = []; filt = []
    for k, s in enumerate(scenes):
        if s["wav"]:
            inputs += ["-i", s["wav"]]
            filt.append(f"[{len(inputs)//2 - 1}]adelay={int(starts[k]*1000 + 150)}|{int(starts[k]*1000 + 150)},aresample=48000[a{k}]")
    labels = "".join(f"[a{k}]" for k, s in enumerate(scenes) if s["wav"])
    cnt = sum(1 for s in scenes if s["wav"])
    run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex",
         ";".join(filt) + f";{labels}amix=inputs={cnt}:normalize=0,apad=whole_dur={total:.2f},atrim=0:{total:.2f}[v]",
         "-map", "[v]", "-ac", "2", "-ar", "48000", voice])
    mix = os.path.join(work, "mix.wav")
    music = spec.get("nhac")
    if music and os.path.exists(os.path.join(ROOT, music)):
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", voice, "-stream_loop", "-1", "-i", os.path.join(ROOT, music), "-filter_complex",
             f"[1]atrim=0:{total:.2f},volume=0.22,afade=t=in:d=1.5,afade=t=out:st={total-2.5:.2f}:d=2.5,aresample=48000[m];"
             f"[0]asplit=2[v1][v2];[m][v2]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[md];"
             f"[v1][md]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[o]", "-map", "[o]", "-ar", "48000", mix])
    else:
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", voice, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", mix])
    log["khau"]["am_thanh_s"] = round(time.time() - t0, 1)

    # ---- phụ đề
    cues = []
    for k, s in enumerate(scenes):
        if not s["wav"]: continue
        for (a, b), ln in zip(s["bounds"], s["loi"]):
            cues.append((starts[k] + 0.15 + a, starts[k] + 0.15 + b, ln[1], ln[2] if len(ln) > 2 else ""))
    ass = os.path.join(work, "subs.ass"); open(ass, "w").write(build_ass(cues, W, H, vertical))

    # ---- ghép cuối: logo góc + phụ đề + âm thanh
    t0 = time.time()
    wm = os.path.join(ROOT, CFG["logo"]["watermark"])
    wm_w = int(W * (0.30 if vertical else 0.17)); margin = int(W * 0.025)
    out = os.path.join(out_dir, f"{spec['id']}.mp4")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", mix, "-i", wm, "-filter_complex",
         f"[2]scale={wm_w}:-1,format=rgba,colorchannelmixer=aa=0.92[w];"
         f"[0][w]overlay=W-w-{margin}:{margin}:enable='between(t,{intro:.2f},{total-outro:.2f})'[v1];"
         f"[v1]ass={ass}:fontsdir={FONT_DIR}[v]",
         "-map", "[v]", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-shortest", out])
    log["khau"]["ghep_cuoi_s"] = round(time.time() - t0, 1)
    log["tong_s"] = round(time.time() - log["bat_dau"], 1); log["thoi_luong_video_s"] = round(total, 1)
    os.makedirs(os.path.join(ROOT, "data/logs"), exist_ok=True)
    with open(os.path.join(ROOT, "data/logs/san-xuat.jsonl"), "a") as f:
        f.write(json.dumps(log, ensure_ascii=False) + "\n")
    return out, log

if __name__ == "__main__":
    o, l = render(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print(o, json.dumps(l, ensure_ascii=False))
