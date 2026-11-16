"""Tạo lại "Kho học liệu số" (thư viện video) của website EduHistory Studio.

Chạy (từ thư mục gốc kho mã):
    python3 web/_cong-cu/tao_thu_vien.py
    python3 web/_cong-cu/tao_thu_vien.py --cach-dua-video sao-chep     # chép video thay vì liên kết cứng
    python3 web/_cong-cu/tao_thu_vien.py --khong-video-cuc-bo          # bản đăng GitHub Pages: chỉ tính video có link YouTube
    python3 web/_cong-cu/tao_thu_vien.py --kiem-tra                    # chỉ đọc, báo cáo, không ghi tệp

Đọc (chỉ đọc): data/catalog/lessons.json, data/catalog/episodes.json, data/scripts/<MA>.json,
               các thư mục video trong cau-hinh.json (mặc định renders/v1/<MA>.mp4),
               web/mo-phong/index.html và web/mo-phong/<MA>.html, web/du-lieu/lien-ket.json,
               assets/episodes/<MA>/canh-NN.jpg (ảnh bìa, nếu có).
Ghi (chỉ trong web/): index.html, gioi-thieu.html, tap/<MA>.html, du-lieu/thu-vien.json,
               du-lieu/anh-bia/<MA>.jpg (chỉ tạo khi chưa có), videos/<MA>.mp4 (liên kết cứng/bản chép).

Nguyên tắc nội dung:
- Chỉ đưa lên trang những gì có trong kịch bản đã đối chiếu SGK (data/scripts): ghi nhớ, mốc thời gian, câu hỏi, số trang.
- Tập chưa có kịch bản chỉ hiện tên tập, bài và trạng thái "đang viết kịch bản" (nội dung nháp của danh mục không đưa lên).
- Phần "giải thích" sau mỗi câu hỏi là câu thuyết minh của người dẫn chuyện (Nhật Minh, Hân Hân) hoặc ý ghi nhớ trong
  chính kịch bản có chứa đáp án; không tìm được câu khớp chắc chắn thì chỉ ghi số trang SGK.
- Không gọi mạng, không cookie, không theo dõi. Video YouTube chỉ tải khi người xem bấm.
Không chuyển mã video: chỉ đọc thông tin bằng ffprobe và cắt 1 khung hình làm ảnh bìa khi cần (chạy ở mức ưu tiên thấp).
Thư mục bắt đầu bằng dấu gạch dưới (như _cong-cu) không được GitHub Pages (Jekyll) xuất bản."""
import argparse, datetime, glob, html, json, os, re, shutil, subprocess, sys, time, unicodedata

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WEB = os.path.join(ROOT, "web")
CAU_HINH_TEP = os.path.join(WEB, "_cong-cu", "cau-hinh.json")
LIEN_KET_TEP = os.path.join(WEB, "du-lieu", "lien-ket.json")
CAU_HINH_MAC_DINH = {
    "nguon_video": ["renders/v1"],
    "thu_muc_video": "web/videos",
    "cach_dua_video": "lien-ket-cung",
    "tinh_video_cuc_bo": True,
    "anh_bia": True,
}
CACH_DUA = ("lien-ket-cung", "sao-chep", "lien-ket-mem", "khong")
DAN_CHUYEN = {"Nhật Minh", "Hân Hân"}
KHUNG = {"4-5p": "4–5 phút", "2-3p": "2–3 phút", "60s": "60 giây dọc"}
TT_CHU = {"co-video": "Đã có video", "co-kich-ban": "Video đang dựng, đã có câu hỏi ôn tập", "ke-hoach": "Đang viết kịch bản"}
MA_TAP = re.compile(r"^L[6-9]-(?:B|CD)\d+-\d+$")
TZ = datetime.timezone(datetime.timedelta(hours=7))
e = lambda s: html.escape(str(s), quote=True)
_GACH = ("–", "-", "—")
def _hoa(w):
    w = w.lstrip('("“‘«')
    return bool(w) and w[0].isupper()
def _so(w):
    return bool(re.match(r"^\(?\d|^[IVXLCDM]+[,.:;?!)”]*$", w))
def ten_nbsp(s):
    """Tên tập không bị ngắt dòng vô duyên: giữ trọn cụm tên riêng (Rạch Gầm – Xoài Mút, C. Mác, Đại Việt)
    và số đi liền chữ trước nó (năm 1285, thế kỉ XVIII) bằng dấu cách không ngắt (U+00A0)."""
    t = str(s).split(" ")
    out = t[0]
    for i in range(1, len(t)):
        p, c = t[i - 1], t[i]
        noi = False
        if p in _GACH:
            noi = False                                           # sau gạch có dấu cách: chỗ ngắt dự phòng khi quá hẹp
        elif re.match(r"^[A-ZĐ][a-z]?\.$", p):                    # chữ viết tắt tên người: C. Mác, Ph. Ăng-ghen
            noi = True
        elif _hoa(p) and not re.search(r"[:;.?!,]$", p) and (_hoa(c) or _so(c)):
            noi = True                                            # Rạch Gầm, Bạch Đằng 1288
        elif c in _GACH and _hoa(p):
            noi = True                                            # Gầm –
        elif _so(c) and len(c) > 0 and not re.search(r"[:;.?!,]$", p):
            noi = True                                            # năm 1285, kỉ XVIII
        out += ("\u00a0" if noi else " ") + c
    # gạch nối trong một từ (Ăng-ghen, Giéc-man, 1936-1939): thêm U+2060 để trình duyệt không ngắt ngay sau dấu gạch.
    # Gạch có dấu cách hai bên (Rạch Gầm – Xoài Mút) vẫn cho ngắt sau dấu gạch khi màn hình quá hẹp; tiêu đề đặt
    # text-wrap: balance nên khi đủ chỗ, cả cụm "Rạch Gầm – Xoài Mút" luôn nằm trọn một dòng.
    return re.sub(r"(?<=\w)([–\-—])(?=\w)", "\\1\u2060", out)
et = lambda s: e(ten_nbsp(s))
def lop_h1(t):
    n = len(str(t))
    return ' class="rat-dai"' if n > 52 else (' class="dai"' if n > 36 else "")
canh_bao = []
# liên hệ ở chân trang (sửa web/du-lieu/lien-he.json khi có kênh TikTok/YouTube)
LIEN_HE_TEP = os.path.join(WEB, "du-lieu", "lien-he.json")
LIEN_HE = {"tiktok": "", "youtube": "", "zalo": "0965479188", "ten_kenh": "EduHistory"}
if os.path.exists(LIEN_HE_TEP):
    LIEN_HE.update({k: v for k, v in json.load(open(LIEN_HE_TEP, encoding="utf-8")).items() if not k.startswith("_")})

# biểu tượng nét (24×24, nét tròn) – cùng một kiểu cho toàn site
def _ic(d, cls="ic"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" focusable="false" fill="none" '
            f'stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">{d}</svg>')
ICON = {
    "tim": _ic('<path d="M12 20.2s-7.6-4.6-7.6-10.1A4.3 4.3 0 0 1 12 7.6a4.3 4.3 0 0 1 7.6 2.5c0 5.5-7.6 10.1-7.6 10.1z"/>'),
    "chia_se": _ic('<circle cx="18" cy="5.5" r="2.6"/><circle cx="6" cy="12" r="2.6"/><circle cx="18" cy="18.5" r="2.6"/><path d="m8.3 10.8 7.4-4.1M8.3 13.2l7.4 4.1"/>'),
    "tai_ve": _ic('<path d="M12 3.8v11.4M7.4 10.8 12 15.4l4.6-4.6"/><path d="M4.5 16.6v1.6a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2v-1.6"/>'),
    "binh_luan": _ic('<path d="M20 11.4c0 4-3.6 7.1-8 7.1-1.1 0-2.2-.2-3.1-.6L4.4 19.6l1.3-3.6A6.6 6.6 0 0 1 4 11.4C4 7.5 7.6 4.3 12 4.3s8 3.2 8 7.1z"/><path d="M8.6 11.5h.01M12 11.5h.01M15.4 11.5h.01"/>'),
    "ma": _ic('<rect x="8.4" y="8.4" width="11.6" height="11.6" rx="2.4"/><path d="M15.6 8.4V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v7.6a2 2 0 0 0 2 2h2.4"/>'),
    "quay_lai": _ic('<path d="M19.5 12H5M11 5.6 4.6 12l6.4 6.4"/>'),
    "menu": _ic('<path d="M4 6.5h16M4 12h11M4 17.5h16"/>'),
    "dong": _ic('<path d="M6 6l12 12M18 6 6 18"/>'),
    "phat": _ic('<path d="M8 5.6v12.8a.8.8 0 0 0 1.2.7l10-6.4a.8.8 0 0 0 0-1.4l-10-6.4A.8.8 0 0 0 8 5.6z"/>'),
    "mo_phong": _ic('<path d="M12 3.6 20 8v8l-8 4.4L4 16V8z"/><path d="M4 8l8 4.4L20 8M12 12.4v8"/>'),
    "tiktok": _ic('<path d="M14.5 3.8v10.6a3.9 3.9 0 1 1-3.4-3.9"/><path d="M14.5 3.8c.6 2.4 2.4 4 4.8 4.2"/>'),
    "youtube": _ic('<rect x="3.2" y="5.6" width="17.6" height="12.8" rx="3.6"/><path d="m10.3 9.4 4.6 2.6-4.6 2.6z"/>'),
    "zalo": _ic('<path d="M20 11.2c0 3.9-3.6 7-8 7-1 0-2-.2-2.9-.5L4.6 19l1.1-3.3A6.5 6.5 0 0 1 4 11.2c0-3.9 3.6-7 8-7s8 3.1 8 7z"/><path d="M8.4 9.6h3.2l-3.2 3.6h3.2M14 9.6v3.6"/>'),
    "gui": _ic('<path d="M20 4 9.6 14.4M20 4l-6.4 16-4-5.6L4 10.4z"/>'),
    "xoa": _ic('<path d="M5 7h14M10 7V5h4v2M7 7l.8 12h8.4L17 7"/>'),
}

def chan_trang(goc="", cau=None):
    """Chân trang: liên hệ bên trái, giới thiệu bên phải."""
    ten = e(LIEN_HE.get("ten_kenh") or "EduHistory")
    def muc(icon, nhan, url, phu=""):
        noi = f'{ICON[icon]}<span><b>{nhan}:</b> {ten if icon != "zalo" else e(phu)}</span>'
        if url:
            return f'<li><a class="lien-he" href="{e(url)}" target="_blank" rel="noopener noreferrer">{noi}</a></li>'
        return f'<li><span class="lien-he chua-co" title="Kênh sắp ra mắt">{noi}<small>sắp ra mắt</small></span></li>'
    z = re.sub(r"\D", "", LIEN_HE.get("zalo") or "")
    z_hien = f"{z[:4]} {z[4:7]} {z[7:]}" if len(z) == 10 else z
    cau = cau or ("Hệ thống số hóa bài học Lịch sử thông qua video, mô phỏng, tương tác, câu hỏi ôn tập",
                  "Chúc các bạn có những giờ phút học tập hiệu quả với EduHistory")
    return (f'<footer class="chan"><div class="rong chan-luoi">'
            f'<div class="chan-lien-he"><h2 class="an-chu">Liên hệ</h2><ul>'
            + muc("tiktok", "TikTok", LIEN_HE.get("tiktok"))
            + muc("youtube", "YouTube", LIEN_HE.get("youtube"))
            + (muc("zalo", "Zalo", f"https://zalo.me/{z}", z_hien) if z else "")
            + f'</ul></div><div class="chan-gt">{trong_dong("chan-trong")}<p class="chan-ten">ChronoVibe Team - EduHistory</p>'
            f'<p>{e(cau[0])}</p><p class="chan-chuc">{e(cau[1])}</p></div></div></footer>')



def bao(msg):
    canh_bao.append(msg)
    print("  ! " + msg, file=sys.stderr)


# ---------------------------------------------------------------- tiện ích chữ
def bo_dau(s):
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s.replace("đ", "d").replace("Đ", "D").lower()).strip()


def trang_chu(trs, tien_to="tr. "):
    """[76, 77, 79] -> 'tr. 76–77, 79'"""
    t = sorted({int(x) for x in (trs or []) if isinstance(x, (int, float)) or (isinstance(x, str) and x.isdigit())})
    out, i = [], 0
    while i < len(t):
        j = i
        while j + 1 < len(t) and t[j + 1] == t[j] + 1:
            j += 1
        out.append(str(t[i]) if i == j else f"{t[i]}–{t[j]}")
        i = j + 1
    return (tien_to + ", ".join(out)) if out else ""


def phut_giay(s):
    s = int(round(s or 0))
    return f"{s // 60}:{s % 60:02d}"


def nhan_bai(ma_bai):
    """'B14' -> 'Bài 14', 'CD1' -> 'Chủ đề chung 1'"""
    m = re.match(r"^(B|CD)(\d+)$", ma_bai)
    if not m:
        return ma_bai
    return ("Bài " if m.group(1) == "B" else "Chủ đề chung ") + m.group(2)


def doc_json(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def ghi(p, noi_dung, kiem_tra):
    if kiem_tra:
        return
    os.makedirs(os.path.dirname(p), exist_ok=True)
    cu = None
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            cu = f.read()
    if cu != noi_dung:
        with open(p, "w", encoding="utf-8") as f:
            f.write(noi_dung)


# ---------------------------------------------------------------- giải thích đáp án
STOP = set("là của và các những một có được trong cho với đã ở đến từ theo vào này đó nào gì ai bao nhiêu mấy năm "
           "khi người ra không thì cũng như để về sau trước nhà em ta".split())
SO_CHU = {1: "một", 2: "hai", 3: "ba", 4: "bốn", 5: "năm", 6: "sáu", 7: "bảy", 8: "tám", 9: "chín", 10: "mười"}


def _chuan(s):
    s = unicodedata.normalize("NFC", s).lower()
    s = re.sub(r"[“”\"'‘’«»()\[\].,;:!?…]", " ", s)
    s = re.sub(r"\s*[–—-]\s*", " - ", s)
    return re.sub(r"\s+", " ", s).strip()


def _tu(s):
    return [w for w in _chuan(s).split() if len(w) > 1 and w not in STOP and w != "-"]


def cau_ung_vien(kb):
    out = []
    for c in kb.get("canh", []):
        tr = c.get("nguon_trang") or []
        if c.get("lop") == "ghi_nho":
            out += [(y, tr, "ghi_nho") for y in c.get("y", [])]
        if c.get("lop") == "truc_thoi_gian":
            out += [(m[0] + ": " + m[1], tr, "moc") for m in c.get("moc", []) if len(m) >= 2]
        if c.get("lop") == "cau_hoi":
            continue
        out += [(l[1], tr, "loi") for l in c.get("loi", []) if len(l) >= 2 and l[0] in DAN_CHUYEN]
    return out


def tim_giai_thich(q, ung_vien):
    """Câu trong kịch bản chứa đáp án đúng và liên quan tới câu hỏi; None nếu không chắc chắn."""
    if "KHÔNG" in q["hoi"]:
        return None
    ans = q["dap_an"][q["dung"]]
    a, at = _chuan(ans), _tu(ans)
    qt = set(_tu(q["hoi"])) - set(at)
    sai = [_chuan(x) for i, x in enumerate(q["dap_an"]) if i != q["dung"] and len(_chuan(x)) > 3]
    so = int(a) if re.fullmatch(r"\d+", a) else None
    best = None
    for text, tr, loai in ung_vien:
        t = _chuan(text)
        tw = set(t.split())
        full = bool(re.search(r"(?<!\w)" + re.escape(a) + r"(?!\w)", t)) or \
            (so in SO_CHU and bool(re.search(r"(?<!\w)" + SO_CHU[so] + r"(?!\w)", t)))
        if not full and (len(at) < 3 or any(w not in tw for w in at)):
            continue
        if so is not None:
            ok = False
            for x in [a] + ([SO_CHU[so]] if so in SO_CHU else []):
                m = re.search(r"(?<!\w)" + x + r" (\w+)", t)
                ok = ok or bool(m and m.group(1) in qt)
            if not ok:
                continue
            can = 1
        else:
            can = 0 if (len(at) >= 6 and full) else (1 if len(at) >= 2 else 2)
        ov = len(qt & set(_tu(text)))
        if ov < can:
            continue
        diem = ov * 2 + (3 if q.get("trang") in tr else 0) + (1 if loai == "loi" else 0) + (2 if full else 0) - len(t) / 400
        if any(w in t for w in sai):
            diem -= 3
        if best is None or diem > best[0]:
            best = (diem, text)
    return best[1] if best else None


# ---------------------------------------------------------------- nguồn dữ liệu
def doc_cau_hinh(args):
    ch = dict(CAU_HINH_MAC_DINH)
    if os.path.exists(CAU_HINH_TEP):
        try:
            ch.update({k: v for k, v in doc_json(CAU_HINH_TEP).items() if not k.startswith("_")})
        except Exception as ex:
            bao(f"Không đọc được {os.path.relpath(CAU_HINH_TEP, ROOT)}: {ex} – dùng cấu hình mặc định")
    if args.cach_dua_video:
        ch["cach_dua_video"] = args.cach_dua_video
    if args.khong_video_cuc_bo:
        ch["tinh_video_cuc_bo"] = False
    if args.khong_anh_bia:
        ch["anh_bia"] = False
    if ch["cach_dua_video"] not in CACH_DUA:
        bao(f"cach_dua_video không hợp lệ: {ch['cach_dua_video']} – dùng 'lien-ket-cung'")
        ch["cach_dua_video"] = "lien-ket-cung"
    if isinstance(ch["nguon_video"], str):
        ch["nguon_video"] = [ch["nguon_video"]]
    return ch


def doc_kich_ban():
    kb = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "data", "scripts", "*.json"))):
        ten = os.path.basename(p)[:-5]
        if ten.startswith("_") or not MA_TAP.match(ten):
            continue
        try:
            d = doc_json(p)
        except Exception as ex:
            bao(f"Bỏ qua kịch bản lỗi {ten}.json: {ex}")
            continue
        if d.get("ma") != ten:
            bao(f"Kịch bản {ten}.json có mã '{d.get('ma')}' khác tên tệp – bỏ qua")
            continue
        cau = []
        for q in d.get("cau_hoi") or []:
            try:
                if isinstance(q["hoi"], str) and len(q["dap_an"]) >= 2 and 0 <= int(q["dung"]) < len(q["dap_an"]):
                    cau.append(q)
            except (KeyError, TypeError, ValueError):
                pass
        if len(cau) != len(d.get("cau_hoi") or []):
            bao(f"{ten}: bỏ {len(d.get('cau_hoi') or []) - len(cau)} câu hỏi thiếu trường")
        d["cau_hoi"] = cau
        d.setdefault("canh", [])
        kb[ten] = d
    return kb


def ffprobe(p):
    try:
        r = subprocess.run(["nice", "-n", "19", "ffprobe", "-v", "error", "-show_entries",
                            "format=duration:stream=codec_type,width,height", "-of", "json", p],
                           capture_output=True, text=True, timeout=60)
        d = json.loads(r.stdout or "{}")
        v = [s for s in d.get("streams", []) if s.get("codec_type") == "video"]
        dur = float(d.get("format", {}).get("duration") or 0)
        if r.returncode != 0 or not v or dur <= 0:
            return None
        return {"thoi_luong": round(dur, 1), "rong": v[0].get("width"), "cao": v[0].get("height")}
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None


def dua_video(nguon, dich, cach):
    """Đưa video vào thư mục của website, không chuyển mã. Trả về True nếu tệp đích dùng được."""
    if os.path.exists(dich) or os.path.islink(dich):
        try:
            if os.path.samefile(nguon, dich):
                return True
        except OSError:
            pass
        s, d = os.stat(nguon), (os.stat(dich) if os.path.exists(dich) else None)
        if cach == "sao-chep" and d and d.st_size == s.st_size and d.st_mtime >= s.st_mtime:
            return True
        os.remove(dich)
    if cach == "lien-ket-mem":
        os.symlink(os.path.relpath(nguon, os.path.dirname(dich)), dich)
        return True
    if cach == "lien-ket-cung":
        try:
            os.link(nguon, dich)
            return True
        except OSError as ex:
            bao(f"Không tạo được liên kết cứng cho {os.path.basename(dich)} ({ex.strerror}) – chép tệp")
    shutil.copy2(nguon, dich)
    return True


def tim_video(ch, cac_ma, kiem_tra):
    """{ma: {tep (đường dẫn trong web/), thoi_luong, rong, cao}}"""
    thu_muc = os.path.join(ROOT, ch["thu_muc_video"])
    if not kiem_tra:
        os.makedirs(thu_muc, exist_ok=True)
    out = {}
    # video đang dựng dở: giữ thông tin của lần sinh trang trước (để trang tập không mất video giữa chừng)
    truoc = {}
    try:
        truoc = {x["ma"]: x["video"] for x in doc_json(os.path.join(WEB, "du-lieu", "thu-vien.json"))["tap"] if x.get("video")}
    except Exception:
        pass
    for ma in sorted(cac_ma):
        dich = os.path.join(thu_muc, ma + ".mp4")
        nguon = None
        for d in ch["nguon_video"]:
            p = os.path.join(ROOT, d, ma + ".mp4")
            if os.path.isfile(p):
                nguon = p
                break
        if nguon:
            if time.time() - os.path.getmtime(nguon) < 120:
                if ma in truoc:
                    out[ma] = truoc[ma]; bao(f"{ma}.mp4 đang dựng – giữ thông tin video của lần trước"); continue
                bao(f"{ma}.mp4 vừa được ghi (< 2 phút) – có thể đang dựng; bỏ qua lần này, chạy lại sau")
                nguon = None
            elif not ffprobe(nguon):
                if ma in truoc:
                    out[ma] = truoc[ma]; bao(f"{ma}.mp4 đang ghi dở – giữ thông tin video của lần trước"); continue
                bao(f"{os.path.relpath(nguon, ROOT)} không đọc được (tệp dở dang?) – bỏ qua")
                nguon = None
        if nguon and ch["cach_dua_video"] != "khong" and not kiem_tra:
            dua_video(nguon, dich, ch["cach_dua_video"])
        if ch["cach_dua_video"] == "khong" and nguon:
            p_web = nguon
        elif os.path.isfile(dich):
            p_web = dich
        elif kiem_tra and nguon:
            p_web = nguon
        else:
            continue
        info = ffprobe(p_web)
        if not info:
            continue
        info["tep"] = os.path.relpath(p_web, WEB).replace(os.sep, "/")
        out[ma] = info
    return out


def doc_lien_ket(kiem_tra):
    mau = {"_huong_dan": ("Đường dẫn video đã đăng cho từng tập (theo mã tập). Ví dụ: "
                          "\"L9-B17-05\": {\"youtube\": \"https://youtu.be/XXXXXXXXXXX\", "
                          "\"tiktok\": \"https://www.tiktok.com/@ten-kenh/video/1234567890\"}. "
                          "Sửa xong chạy lại: python3 web/_cong-cu/tao_thu_vien.py"),
           "tap": {}}
    if not os.path.exists(LIEN_KET_TEP):
        ghi(LIEN_KET_TEP, json.dumps(mau, ensure_ascii=False, indent=1) + "\n", kiem_tra)
        return {}
    try:
        d = doc_json(LIEN_KET_TEP)
    except Exception as ex:
        bao(f"lien-ket.json lỗi cú pháp ({ex}) – bỏ qua toàn bộ liên kết")
        return {}
    out = {}
    for ma, v in (d.get("tap") or {}).items():
        if not MA_TAP.match(ma) or not isinstance(v, dict):
            bao(f"lien-ket.json: mục '{ma}' không hợp lệ – bỏ qua")
            continue
        r = {}
        yt = (v.get("youtube") or "").strip()
        if yt:
            m = re.match(r"^https://(?:www\.|m\.)?(?:youtube\.com/(?:watch\?(?:.*&)?v=|shorts/|embed/|live/)|youtu\.be/)([A-Za-z0-9_-]{11})(?:[?&#].*)?$", yt)
            if m:
                r["youtube_id"] = m.group(1)
                r["youtube"] = "https://www.youtube.com/watch?v=" + m.group(1)
            else:
                bao(f"lien-ket.json: link YouTube của {ma} không nhận dạng được: {yt}")
        tt = (v.get("tiktok") or "").strip()
        if tt:
            if re.match(r"^https://(?:www\.|vt\.|vm\.)?tiktok\.com/[\w@./?=&%-]+$", tt):
                r["tiktok"] = tt
            else:
                bao(f"lien-ket.json: link TikTok của {ma} không hợp lệ: {tt}")
        if r:
            out[ma] = r
    return out


def doc_mo_phong():
    """{ma: {href, loai, mota}} từ web/mo-phong (chỉ đọc)."""
    mp = os.path.join(WEB, "mo-phong")
    out = {}
    idx = os.path.join(mp, "index.html")
    if os.path.exists(idx):
        s = open(idx, encoding="utf-8").read()
        for m in re.finditer(r'<a class="the-mp" href="([^"]+)\.html">(.*?)</a>', s, re.S):
            ma, khoi = m.group(1), m.group(2)
            loai = re.search(r'<span class="loai[^"]*">(.*?)</span>', khoi, re.S)
            mota = re.search(r'<span class="mota">(.*?)</span>', khoi, re.S)
            ten = re.search(r'<span class="ten">(.*?)</span>', khoi, re.S)
            if MA_TAP.match(ma) and os.path.exists(os.path.join(mp, ma + ".html")):
                out[ma] = {"href": f"mo-phong/{ma}.html",
                           "loai": html.unescape(loai.group(1)).strip() if loai else "Mô phỏng tương tác",
                           "mota": html.unescape(mota.group(1)).strip() if mota else "",
                           "ten": html.unescape(ten.group(1)).strip() if ten else ""}
    for p in glob.glob(os.path.join(mp, "L*.html")):
        ma = os.path.basename(p)[:-5]
        if MA_TAP.match(ma) and ma not in out:
            s = open(p, encoding="utf-8").read()
            mota = re.search(r'<meta name="description" content="([^"]*)"', s)
            out[ma] = {"href": f"mo-phong/{ma}.html", "loai": "Mô phỏng tương tác",
                       "mota": html.unescape(mota.group(1)) if mota else "", "ten": ""}
    return out


def _cat_ti_le(im, tl, lech_y=0.5):
    """Cắt ảnh theo tỉ lệ rộng/cao tl; lech_y: vị trí theo chiều dọc (0 = trên, 0.5 = giữa)."""
    if im.width / im.height > tl:
        cw = round(im.height * tl)
        return im.crop(((im.width - cw) // 2, 0, (im.width - cw) // 2 + cw, im.height))
    ch_ = round(im.width / tl)
    y0 = int((im.height - ch_) * lech_y)
    return im.crop((0, y0, im.width, y0 + ch_))


def _bia_thuong_hieu(ma, dich, kt):
    """Bìa thương hiệu cho tập không có tranh cảnh: nền xanh đêm, mặt trống đồng mờ, số bài lớn màu đồng
    (tên tập đã ghi ngay dưới ảnh nên không lặp lại trên bìa; chừa trống góc dưới cho nhãn thời lượng)."""
    from PIL import Image, ImageDraw, ImageFont
    import math
    W, H = kt; im = Image.new("RGB", (W, H), (11, 26, 49)); d = ImageDraw.Draw(im, "RGBA")
    ox, oy, R = W * .80, H * .42, min(W, H) * .78
    for fr, wd in [(1.0, 4), (.88, 2), (.74, 3), (.6, 2), (.46, 2)]:
        r = R * fr; d.ellipse([ox - r, oy - r, ox + r, oy + r], outline=(201, 139, 43, 64), width=wd)
    for j in range(72):
        a = j * 2 * math.pi / 72; r1, r2 = R * .74, R * .86
        d.line([ox + r1 * math.cos(a), oy + r1 * math.sin(a), ox + r2 * math.cos(a), oy + r2 * math.sin(a)], fill=(201, 139, 43, 40), width=2)
    for j in range(14):
        a = j * 2 * math.pi / 14; r = R * .40
        d.polygon([(ox + r * .25 * math.cos(a), oy + r * .25 * math.sin(a)), (ox + r * math.cos(a), oy + r * math.sin(a)),
                   (ox + r * .25 * math.cos(a + .45), oy + r * .25 * math.sin(a + .45))], fill=(201, 139, 43, 70))
    fd = os.path.join(ROOT, "assets", "fonts")
    m = re.match(r"L(\d)-(B|CD)(\d+)", ma)
    lop, loai, so = (m.group(1), m.group(2), m.group(3)) if m else ("", "B", "")
    nhan = ("Bài " if loai == "B" else "Chủ đề ") + so
    f_big = ImageFont.truetype(os.path.join(fd, "be-vietnam-pro-900-normal.ttf"), int(min(W, H) * (.26 if W > H else .2)))
    f_sm = ImageFont.truetype(os.path.join(fd, "be-vietnam-pro-700-normal.ttf"), int(min(W, H) * .075))
    x = W * .08; y = H * (.22 if W > H else .30)
    d.text((x, y), "Edu", font=f_sm, fill=(255, 246, 230)); d.text((x + d.textlength("Edu", font=f_sm), y), "History", font=f_sm, fill=(242, 107, 29))
    y += f_sm.size * 1.5
    d.text((x, y), nhan, font=f_big, fill=(233, 182, 92)); y += f_big.size * 1.12
    d.text((x, y), f"Lớp {lop}", font=f_sm, fill=(255, 255, 255))
    im.save(dich, "JPEG", quality=84, optimize=True, progressive=True)


def tao_anh_bia(ma, kb, video, kiem_tra):
    """Ảnh bìa từ tranh cảnh của dự án (không phụ đề, không thẻ chữ): ưu tiên cảnh TÁI HIỆN (tranh lịch sử),
    rồi DU HÀNH, DẪN CHUYỆN; dự phòng 1 khung hình video. Luôn có bản 16:9 (<MA>.jpg, 800×450) cho lưới video;
    tập video dọc có thêm bản 9:16 (<MA>-doc.jpg) làm ảnh chờ của trình phát.
    Ảnh do giáo viên tự đặt: đặt tên <MA>.thay.jpg – công cụ dùng ảnh đó và không ghi đè."""
    thu_muc = os.path.join(WEB, "du-lieu", "anh-bia")
    dich = os.path.join(thu_muc, ma + ".jpg"); dich_doc = os.path.join(thu_muc, ma + "-doc.jpg")
    doc = (kb or {}).get("huong") == "doc"
    if kiem_tra:
        return os.path.exists(dich)
    os.makedirs(thu_muc, exist_ok=True)
    from PIL import Image
    tu_dat = os.path.join(thu_muc, ma + ".thay.jpg")
    nguon = None
    if os.path.exists(tu_dat):
        nguon = tu_dat
    else:
        uu_tien = {"tai_hien": 0, "du_hanh": 1, "dan_chuyen": 2, "tu_lieu": 3}
        ung = []
        for c in (kb or {}).get("canh", []):
            lop_c = c.get("lop")
            if lop_c not in uu_tien: continue
            p = os.path.join(ROOT, c["anh"]) if c.get("anh") else os.path.join(ROOT, "assets", "episodes", ma, f"canh-{int(c.get('so', 0)):02d}.jpg")
            if os.path.exists(p): ung.append((uu_tien[lop_c], int(c.get("so", 0)), p))
        if ung:
            nguon = sorted(ung)[0][2]
    if nguon:
        try:
            im = Image.open(nguon).convert("RGB")
            _cat_ti_le(im, 16 / 9, 0.38 if im.height > im.width else 0.5).resize((800, 450), Image.LANCZOS).save(
                dich, "JPEG", quality=82, optimize=True, progressive=True)
            if doc:
                _cat_ti_le(im, 9 / 16).resize((450, 800), Image.LANCZOS).save(dich_doc, "JPEG", quality=82, optimize=True, progressive=True)
            return True
        except Exception as ex:
            bao(f"Không tạo được ảnh bìa từ {os.path.relpath(nguon, ROOT)}: {ex}")
    try:   # không có tranh cảnh (tập dẫn chuyện vẽ bằng code): bìa thương hiệu có tên tập
        _bia_thuong_hieu(ma, dich, (800, 450))
        if doc: _bia_thuong_hieu(ma, dich_doc, (450, 800))
        return True
    except Exception as ex:
        bao(f"Không vẽ được bìa thương hiệu cho {ma}: {ex}")
    if video:
        src = os.path.join(WEB, video["tep"])
        t = max(1.0, video["thoi_luong"] * 0.25)
        r = subprocess.run(["nice", "-n", "19", "ffmpeg", "-v", "error", "-y", "-ss", f"{t:.1f}", "-i", src,
                            "-frames:v", "1", "-vf", "scale=800:-2", "-q:v", "5", dich],
                           capture_output=True, text=True, timeout=120)
        if r.returncode == 0 and os.path.exists(dich):
            return True
        bao(f"Không cắt được khung hình làm ảnh bìa cho {ma}")
    return False


# ---------------------------------------------------------------- mô hình dữ liệu
def dung_du_lieu(ch, kiem_tra):
    les = doc_json(os.path.join(ROOT, "data", "catalog", "lessons.json"))["bai"]
    cat = doc_json(os.path.join(ROOT, "data", "catalog", "episodes.json"))["tap"]
    kb = doc_kich_ban()
    bai_theo_id = {b["id"]: dict(b, tap=[]) for b in les}
    thu_tu_bai = {b["id"]: i for i, b in enumerate(les)}
    tap = {}
    for t in cat:
        if t.get("ma") and t.get("bai") in bai_theo_id:
            tap[t["ma"]] = dict(t)
    for ma, d in kb.items():
        if ma not in tap:
            bai = ma.rsplit("-", 1)[0]
            if bai not in bai_theo_id:
                bao(f"Kịch bản {ma}: không có bài {bai} trong lessons.json – bỏ qua")
                continue
            b = bai_theo_id[bai]
            tap[ma] = {"ma": ma, "bai": bai, "lop": b["lop"], "ten_bai": b["ten"], "so": int(ma.rsplit("-", 1)[1]),
                       "ten_tap": d.get("ten_tap", ma), "khung": d.get("khung"), "huong": d.get("huong"),
                       "trang_sgk": (d.get("nguon") or {}).get("trang", []), "nhan_vat": []}
            bao(f"Kịch bản {ma} chưa có trong danh mục episodes.json – vẫn đưa vào thư viện")
    video = tim_video(ch, tap.keys(), kiem_tra)
    lien_ket = doc_lien_ket(kiem_tra)
    for ma in lien_ket:
        if ma not in tap:
            bao(f"lien-ket.json: mã {ma} không có trong danh mục")
    mo_phong = doc_mo_phong()

    ds = []
    for ma, t in tap.items():
        d = kb.get(ma)
        v = video.get(ma) if ch["tinh_video_cuc_bo"] else None
        lk = lien_ket.get(ma, {})
        co_video = bool(v or lk.get("youtube_id"))
        tt = "co-video" if co_video else ("co-kich-ban" if d else "ke-hoach")
        b = bai_theo_id[t["bai"]]
        x = {
            "ma": ma, "bai": t["bai"], "lop": int(t["lop"]), "so": int(t.get("so") or 0),
            "ten_tap": (d or {}).get("ten_tap") or t.get("ten_tap") or ma,
            "ten_tap_en": (d or {}).get("ten_tap_en") or "",
            "khung": (d or {}).get("khung") or t.get("khung") or "",
            "huong": (d or {}).get("huong") or t.get("huong") or "ngang",
            "trang_thai": tt, "co_trang": bool(d or co_video),
            "trang_sgk": ((d or {}).get("nguon") or {}).get("trang") or t.get("trang_sgk") or [],
            "sach": ((d or {}).get("nguon") or {}).get("sach") or f"Lịch sử và Địa lí {t['lop']} (bộ sách dùng chung)",
            "video": v, "youtube": lk.get("youtube"), "youtube_id": lk.get("youtube_id"), "tiktok": lk.get("tiktok"),
            "mo_phong": mo_phong.get(ma),
            "nhan_vat": [n.get("ten") for n in (t.get("nhan_vat") or []) if isinstance(n, dict) and n.get("ten")],
            "kb": d,
        }
        x["anh_bia"] = None
        if co_video and ch["anh_bia"]:
            if tao_anh_bia(ma, d, v, kiem_tra):
                x["anh_bia"] = f"du-lieu/anh-bia/{ma}.jpg"
        elif os.path.exists(os.path.join(WEB, "du-lieu", "anh-bia", ma + ".jpg")):
            x["anh_bia"] = f"du-lieu/anh-bia/{ma}.jpg"
        ds.append(x)
    ds.sort(key=lambda x: (x["lop"], thu_tu_bai[x["bai"]], x["so"], x["ma"]))
    for x in ds:
        bai_theo_id[x["bai"]]["tap"].append(x)
    bai_ds = [bai_theo_id[b["id"]] for b in les]
    return bai_ds, ds


def ghi_nho(kb):
    out, thay = [], set()
    for c in kb.get("canh", []):
        if c.get("lop") != "ghi_nho":
            continue
        for y in c.get("y", []):
            k = bo_dau(y)
            if y and k not in thay:
                thay.add(k)
                out.append((y, c.get("nguon_trang") or []))
    return out


def moc_thoi_gian(kb):
    out = []
    for c in kb.get("canh", []):
        if c.get("lop") == "truc_thoi_gian" and c.get("moc"):
            out.append({"tieu_de": c.get("tieu_de") or "", "moc": [m for m in c["moc"] if len(m) >= 2],
                        "tr": c.get("nguon_trang") or []})
    return out


def chu_tim(x, bai):
    phan = [x["ma"], x["ten_tap"], x["ten_tap_en"], nhan_bai(bai["ma"]), bai["ten"], bai.get("chuong", ""), f"lop {x['lop']}"]
    phan += x["nhan_vat"]
    if x["kb"]:
        phan += [y for y, _ in ghi_nho(x["kb"])]
        for m in moc_thoi_gian(x["kb"]):
            phan += [a + " " + b for a, b in m["moc"]]
    if x["mo_phong"]:
        phan.append("mo phong")
    return bo_dau(" ".join(phan))


# ---------------------------------------------------------------- khuôn trang
def trong_dong(cls="trong-dong"):
    """Hoạ tiết trống đồng (vòng tròn đồng tâm, chấm, sao) – trang trí, không mang thông tin."""
    cham = []
    import math
    for k in range(36):
        a = 2 * math.pi * k / 36
        cham.append(f'<circle cx="{100 + 86 * math.cos(a):.1f}" cy="{100 + 86 * math.sin(a):.1f}" r="1.6"/>')
    sao = []
    for k in range(14):
        a1 = 2 * math.pi * k / 14 - math.pi / 2
        a2 = a1 + math.pi / 14
        sao.append(f"{100 + 30 * math.cos(a1):.1f},{100 + 30 * math.sin(a1):.1f} {100 + 11 * math.cos(a2):.1f},{100 + 11 * math.sin(a2):.1f}")
    return (f'<svg class="{cls}" viewBox="0 0 200 200" aria-hidden="true" focusable="false">'
            '<g fill="none" stroke="currentColor"><circle cx="100" cy="100" r="96" stroke-width="2.5"/>'
            '<circle cx="100" cy="100" r="78" stroke-width="1"/><circle cx="100" cy="100" r="62" stroke-width="1" stroke-dasharray="2 4"/>'
            '<circle cx="100" cy="100" r="44" stroke-width="1.5"/></g>'
            f'<g fill="currentColor">{"".join(cham)}<polygon points="{" ".join(sao)}"/></g></svg>')


def khuon(tieu_de, mo_ta, than, goc="", dang="", lop_body="", cap_nhat=""):
    nav = [("index.html", "Thư viện", "thu-vien"), ("mo-phong/index.html", "Mô phỏng", "mo-phong"),
           ("gioi-thieu.html", "Giới thiệu", "gioi-thieu")]
    hien = ' aria-current="page"'
    li = "".join(f'<li><a href="{goc}{h}"{hien if k == dang else ""}>{t}</a></li>' for h, t, k in nav)
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(tieu_de)}</title>
<meta name="description" content="{e(mo_ta)}">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta name="theme-color" content="#10233F">
<link rel="icon" href="{goc}chung/img/logo.svg" type="image/svg+xml">
<link rel="icon" href="{goc}chung/img/favicon-64.png" type="image/png" sizes="64x64">
<link rel="apple-touch-icon" href="{goc}chung/img/apple-touch-icon.png">
<link rel="stylesheet" href="{goc}chung/css/thu-vien.css">
<link rel="stylesheet" href="{goc}chung/css/khung-chung.css">
</head>
<body class="{lop_body}" data-goc="{goc}">
<a class="bo-qua" href="#noi-dung">Bỏ qua, tới nội dung chính</a>
<header class="dau">
  <button type="button" class="nut-menu" aria-controls="ngan-menu" aria-expanded="false">{ICON["menu"]}<span>Mục lục</span></button>
  <a class="thuong-hieu" href="{goc}index.html"><img src="{goc}chung/img/logo.svg" alt="" width="40" height="40"><span>EduHistory Studio<small>Kho học liệu số môn Lịch sử</small></span></a>
  <nav class="dieu-huong" aria-label="Điều hướng chính"><ul>{li}</ul></nav>
</header>
{ngan_menu(goc)}
<main id="noi-dung" tabindex="-1">
{than}
</main>
{chan_trang(goc)}
<div class="thong-bao" role="status" aria-live="polite" hidden></div>
<script src="{goc}chung/js/thu-vien.js"></script>
</body>
</html>
"""


def ngan_menu(goc=""):
    """Ngăn mục lục bên trái: Lớp → Bài → video và mô phỏng (dữ liệu nạp từ du-lieu/menu.js khi mở)."""
    return (f'<div class="nen-menu" hidden></div><nav id="ngan-menu" class="ngan-menu" aria-label="Mục lục bài học" hidden data-nguon="{goc}du-lieu/menu.js">'
            f'<div class="dau-ngan"><p class="ten-ngan">Mục lục</p><button type="button" class="nut-dong-menu" aria-label="Đóng mục lục">{ICON["dong"]}</button></div>'
            f'<div class="da-thich" hidden><p class="nhan-ngan">Video em đã thích</p><ul></ul></div>'
            f'<div class="cay-menu"><p class="dang-tai">Đang tải mục lục…</p></div></nav>')


def du_lieu_menu(bai_ds, mo_phong_them):
    """window.EDU_MENU cho ngăn mục lục: lớp → bài → tập (có trang) + mô phỏng của bài."""
    lop = []
    for l in (6, 7, 8, 9):
        bs = []
        for b in [b for b in bai_ds if b["lop"] == l]:
            tap = [{"ma": x["ma"], "ten": ten_nbsp(x["ten_tap"]), "v": 1 if x["trang_thai"] == "co-video" else 0,
                    "tl": phut_giay(x["video"]["thoi_luong"]) if x["video"] else ""} for x in b["tap"] if x["co_trang"]]
            mp = [{"ten": ten_nbsp(x["mo_phong"].get("ten") or x["ten_tap"]), "loai": x["mo_phong"]["loai"], "href": x["mo_phong"]["href"]}
                  for x in b["tap"] if x["mo_phong"]]
            mp += [m for m in mo_phong_them if m.get("bai") == b["id"]]
            bs.append({"id": b["id"], "nhan": nhan_bai(b["ma"]), "ten": b["ten"], "tap": tap, "mp": mp,
                       "tong": len(b["tap"])})
        lop.append({"lop": l, "bai": bs})
    return "window.EDU_MENU=" + json.dumps({"lop": lop}, ensure_ascii=False, separators=(",", ":")) + ";\n"


def doc_mo_phong_them():
    """Mô phỏng / mô hình 3D không gắn với một tập (web/mo-phong/data/danh-muc-them.json)."""
    p = os.path.join(WEB, "mo-phong", "data", "danh-muc-them.json")
    if not os.path.exists(p):
        return []
    out = []
    for m in json.load(open(p, encoding="utf-8")):
        if os.path.exists(os.path.join(WEB, m["href"])):
            out.append({"ten": m["ten"], "loai": m["loai"], "href": m["href"], "bai": m.get("bai")})
    return out


def dong_tap(x, goc=""):
    tt = x["trang_thai"]
    chu_tt = TT_CHU[tt]
    if tt == "co-video" and x["video"]:
        chu_tt += f" ({phut_giay(x['video']['thoi_luong'])})"
    ten = (f'<a class="ten-tap" href="{goc}tap/{x["ma"]}.html">{et(x["ten_tap"])}</a>' if x["co_trang"]
           else f'<span class="ten-tap">{et(x["ten_tap"])}</span>')
    meta = [f"<span>Tập {x['so']}</span>", f"<span>{e(KHUNG.get(x['khung'], x['khung']))}</span>",
            f'<span class="tt">{e(chu_tt)}</span>']
    if x["mo_phong"]:
        meta.append('<span class="co-mp">Có mô phỏng</span>')
    return (f'<li class="tap-dong tt-{tt}" data-lop="{x["lop"]}" data-khung="{e(x["khung"])}" data-tt="{tt}">'
            f'<span class="dau-tt" aria-hidden="true"></span><div class="tap-than">{ten}'
            f'<p class="tap-meta">{"".join(meta)}</p></div></li>')


# ---------------------------------------------------------------- trang chủ (thư viện)
def trang_index(bai_ds, ds, cap_nhat, tt_ds=()):
    lop_ds = [6, 7, 8, 9]
    THOI_KY = {6: "Từ thời nguyên thuỷ đến thế kỉ X", 7: "Thời trung đại, đến thế kỉ XVI",
               8: "Thế kỉ XVI – đầu thế kỉ XX", 9: "Từ năm 1918 đến nay"}
    o_lop = []
    for l in lop_ds:
        tl = [x for x in ds if x["lop"] == l]
        nb = len([b for b in bai_ds if b["lop"] == l])
        dv = sum(1 for x in tl if x["trang_thai"] == "co-video")
        dk = sum(1 for x in tl if x["trang_thai"] == "co-kich-ban")
        n = max(1, len(tl))
        thanh = (f'<span class="thanh" aria-hidden="true"><i class="v" style="width:{100 * dv / n:.1f}%"></i>'
                 f'<i class="k" style="width:{100 * dk / n:.1f}%"></i></span>')
        o_lop.append(f'<li><a class="o-lop" href="#lop-{l}" data-lop="{l}">{trong_dong()}'
                     f'<span class="so-lop" aria-hidden="true">{l}</span><span class="ten-lop">Lớp {l}</span>'
                     f'<span class="thoi-ky">{THOI_KY[l]}</span>'
                     f'<span class="dem">{nb} bài, {len(tl)} tập</span>{thanh}'
                     f'<span class="dem-phu">{dv} video, {dk + dv} tập có câu hỏi ôn tập</span></a></li>')
    the_video = []
    for x in [x for x in ds if x["trang_thai"] == "co-video"]:
        b = next(bb for bb in bai_ds if bb["id"] == x["bai"])
        anh = (f'<img src="{e(x["anh_bia"])}" alt="" width="800" height="450" loading="lazy">' if x["anh_bia"]
               else trong_dong("anh-thay"))
        tl = f'<span class="thoi-luong">{phut_giay(x["video"]["thoi_luong"])}</span>' if x["video"] else ""
        tl += '<span class="nut-phat-nho" aria-hidden="true"></span>'
        the_video.append(f'<li><a class="the-video" href="tap/{x["ma"]}.html"><span class="khung-anh">{anh}{tl}</span>'
                         f'<span class="lop-bai">Lớp {x["lop"]}, {e(nhan_bai(b["ma"]))}</span>'
                         f'<span class="ten" title="{e(x["ten_tap"])}">{et(x["ten_tap"])}</span></a></li>')
    ke_video = ""
    if the_video:
        ke_video = (f'<section class="ke-video" aria-labelledby="tieu-de-video"><div class="rong">'
                    f'<div class="dau-muc"><h2 id="tieu-de-video">Video bài học</h2><p>{len(the_video)} video đã hoàn thành, xem ngay trên trình duyệt.</p></div><ul class="luoi-video">{"".join(the_video)}</ul></div></section>')
    # thư viện theo lớp – chương – bài – tập
    khoi = []
    for l in lop_ds:
        cac_bai = [b for b in bai_ds if b["lop"] == l]
        chuong_ds, cur = [], None
        for b in cac_bai:
            if cur is None or cur[0] != b.get("chuong"):
                cur = (b.get("chuong"), [])
                chuong_ds.append(cur)
            cur[1].append(b)
        phan = [f'<section class="lop" id="lop-{l}" data-lop="{l}" aria-labelledby="h-lop-{l}">'
                f'<h2 id="h-lop-{l}"><span class="so-lop" aria-hidden="true">{l}</span>Lớp {l}</h2>']
        for ten_ch, bs in chuong_ds:
            phan.append(f'<div class="chuong"><h3>{e(ten_ch or "")}</h3>')
            for b in bs:
                dong = "".join(f'<li data-tim="{e(chu_tim(x, b))}"' + dong_tap(x)[3:] for x in b["tap"])
                if not b["tap"]:
                    dong = '<li class="tap-trong">Chưa có tập nào trong danh mục.</li>'
                phan.append(f'<section class="bai" id="{b["id"]}" data-lop="{l}" aria-labelledby="h-{b["id"]}">'
                            f'<div class="dau-bai"><span class="so-bai">{e(nhan_bai(b["ma"]))}</span>'
                            f'<h4 id="h-{b["id"]}">{e(b["ten"])}</h4><span class="tr-bai">SGK tr. {e(b.get("trang_in", ""))}</span></div>'
                            f'<ol class="ds-tap">{dong}</ol></section>')
            phan.append("</div>")
        phan.append("</section>")
        khoi.append("".join(phan))
    n_v = sum(1 for x in ds if x["trang_thai"] == "co-video")
    n_k = sum(1 for x in ds if x["trang_thai"] != "ke-hoach")
    nut = lambda nhom, gt, chu, chon=False: (f'<button type="button" class="chip" data-nhom="{nhom}" data-gt="{gt}" '
                                            f'aria-pressed="{"true" if chon else "false"}">{chu}</button>')
    than = f"""<section class="bia" aria-labelledby="tieu-de-trang">
<div class="rong bia-luoi">
 <div class="bia-chu">
  <h1 id="tieu-de-trang" class="mot-dong">ChronoVibe Team&nbsp;-&nbsp;EduHistory</h1>
  <p class="dan dan-lon">Số hóa bài học Lịch sử thông qua hệ thống video bài học, ghi nhớ kiến thức, mô phỏng tương tác, câu hỏi ôn&nbsp;tập</p>
  <div class="o-tim" role="search">
    <label for="tim" class="an-chu">Tìm trong thư viện</label>
    <input type="search" id="tim" name="tim" autocomplete="off" spellcheck="false" placeholder="Tìm bài, nhân vật, sự kiện…" aria-describedby="goi-y-tim">
    <p id="goi-y-tim" class="goi-y">Ví dụ: Bạch Đằng, Lê Lợi, 1945. Gõ có dấu hay không dấu đều được.</p>
  </div>
  <dl class="so-lieu"><div><dt>video đã hoàn thành</dt><dd>{n_v}</dd></div><div><dt>tập có câu hỏi ôn tập</dt><dd>{n_k}</dd></div><div><dt>tập trong kế hoạch</dt><dd>{len(ds)}</dd></div></dl>
 </div>
 <div class="bia-trong" aria-hidden="true">{trong_dong("trong-lon")}</div>
</div>
<div class="rong"><ul class="chon-lop" aria-label="Chọn lớp">{"".join(o_lop)}</ul></div>
</section>
{ke_chuyen_su(list(tt_ds))}
{ke_video}
<section class="thu-vien" id="thu-vien" aria-label="Danh sách bài học và tập video">
<div class="rong">
  <div class="bo-loc" role="region" aria-label="Bộ lọc">
    <div class="nhom-loc" role="group" aria-labelledby="nhan-lop"><span class="nhan" id="nhan-lop">Lớp</span>{nut("lop", "", "Tất cả", True)}{"".join(nut("lop", l, f"Lớp {l}") for l in lop_ds)}</div>
    <div class="nhom-loc" role="group" aria-labelledby="nhan-khung"><span class="nhan" id="nhan-khung">Thời lượng</span>{nut("khung", "", "Tất cả", True)}{"".join(nut("khung", k, v) for k, v in KHUNG.items())}</div>
    <div class="nhom-loc" role="group" aria-labelledby="nhan-tt"><span class="nhan" id="nhan-tt">Tình trạng</span>{nut("tt", "", "Tất cả", True)}{nut("tt", "co-video", "Đã có video")}{nut("tt", "dang-san-xuat", "Đang sản xuất")}</div>
    <div class="hang-ket-qua"><p class="ket-qua" id="ket-qua" aria-live="polite"></p>
      <label class="chuyen-bai" hidden>Tới bài <select id="chuyen-bai"></select></label>
      <button type="button" class="nut-xoa" id="xoa-loc" hidden>Xoá bộ lọc</button></div>
    <p class="chu-giai"><span class="cg tt-co-video"><span class="dau-tt" aria-hidden="true"></span>Đã có video</span><span class="cg tt-co-kich-ban"><span class="dau-tt" aria-hidden="true"></span>Đã có câu hỏi ôn tập, video đang dựng</span><span class="cg tt-ke-hoach"><span class="dau-tt" aria-hidden="true"></span>Đang viết kịch bản</span></p>
  </div>
  <p class="khong-thay" id="khong-thay" hidden></p>
  {"".join(khoi)}
</div>
</section>"""
    return khuon("ChronoVibe Team - EduHistory | Kho học liệu số môn Lịch sử",
                 "Thư viện video bài học Lịch sử lớp 6–9 theo SGK Lịch sử và Địa lí: video, ghi nhớ, câu hỏi ôn tập và mô phỏng tương tác.",
                 than, dang="thu-vien", lop_body="trang-thu-vien", cap_nhat=cap_nhat)


# ---------------------------------------------------------------- trang tập
def khoi_video(x, goi_y="Trong lúc chờ, em hãy đọc phần ghi nhớ và làm câu hỏi ôn tập bên dưới."):
    ma, doc = x["ma"], x["huong"] == "doc"
    lop_khung = "khung-video doc" if doc else "khung-video"
    bia = x["anh_bia"]
    if bia and doc and os.path.exists(os.path.join(WEB, bia.replace(".jpg", "-doc.jpg"))):
        bia = bia.replace(".jpg", "-doc.jpg")
    anh = f' poster="../{e(bia)}"' if bia else ""
    yt = ""
    if x["youtube_id"]:
        yt = (f'<div class="yt"{" hidden" if x["video"] else ""} data-yt="{e(x["youtube_id"])}" data-ten="{e(x["ten_tap"])}">'
              f'<a class="nut-yt" href="{e(x["youtube"])}" target="_blank" rel="noopener noreferrer">'
              f'{trong_dong("anh-thay")}<span class="nut-phat" aria-hidden="true"></span>'
              f'<span class="chu-yt">Phát video từ YouTube</span>'
              f'<span class="chu-yt-phu">Trình phát YouTube chỉ được tải khi em bấm (kết nối tới youtube-nocookie.com).</span></a></div>')
    if x["video"]:
        loi = ("Không mở được tệp video trên máy này. Bản website công khai không kèm tệp video; "
               + ("hãy xem bản trên YouTube bên dưới." if x["youtube_id"] else "video được chiếu tại lớp hoặc trên máy tính của trường."))
        return (f'<div class="{lop_khung}" data-ma="{ma}">'
                f'<video controls playsinline preload="metadata"{anh} aria-describedby="ghi-chu-phu-de">'
                f'<source src="../{e(x["video"]["tep"])}" type="video/mp4">'
                f'<p>Trình duyệt không phát được video. <a href="../{e(x["video"]["tep"])}">Tải tệp video</a>.</p></video>'
                f'<div class="video-loi" hidden role="status">{trong_dong("anh-thay")}<p>{e(loi)}</p></div>{yt}</div>')
    if x["youtube_id"]:
        return f'<div class="{lop_khung}" data-ma="{ma}">{yt}</div>'
    return (f'<div class="{lop_khung} giu-cho" data-ma="{ma}">'
            f'{trong_dong("anh-thay")}<p class="giu-cho-chu"><b>Đang sản xuất</b>'
            f'<span>Video của tập này đang được dựng. {e(goi_y)}</span></p></div>')


def thanh_hanh_dong(x):
    """Thả tim, chia sẻ, tải về, bình luận, sao chép mã – tim và bình luận chỉ lưu trên máy người xem."""
    if not (x["video"] or x["youtube_id"]):
        return ""
    ma = x["ma"]
    nut = lambda cls, icon, chu, them="": (f'<button type="button" class="hd {cls}"{them}>{ICON[icon]}<span>{chu}</span></button>')
    tai = ""
    if x["video"]:
        ten_tep = f'EduHistory_{ma}.mp4'
        tai = (f'<a class="hd hd-tai" href="../{e(x["video"]["tep"])}" download="{ten_tep}">{ICON["tai_ve"]}<span>Tải về</span></a>')
    cong_khai = [(f'<a href="{e(u)}" target="_blank" rel="noopener noreferrer">{t}</a>') for u, t in
                 ((x["tiktok"], "TikTok"), (x["youtube"], "YouTube")) if u]
    ngoai = (f'<p class="bl-ngoai">Bình luận công khai trên {" hoặc ".join(cong_khai)}.</p>' if cong_khai else "")
    return (f'<div class="hanh-dong" data-ma="{ma}" data-ten="{e(x["ten_tap"])}">'
            + nut("hd-tim", "tim", "Thích", ' aria-pressed="false"')
            + nut("hd-chia-se", "chia_se", "Chia sẻ")
            + tai
            + nut("hd-bl", "binh_luan", "Bình luận", ' aria-expanded="false" aria-controls="bl-' + ma + '"')
            + nut("hd-ma", "ma", f"Mã {ma}", f' data-ma="{ma}" title="Sao chép mã video"')
            + '</div>'
            f'<section class="binh-luan" id="bl-{ma}" hidden aria-label="Bình luận của em">'
            f'<form class="bl-form"><label for="bl-o-{ma}" class="an-chu">Viết bình luận</label>'
            f'<textarea id="bl-o-{ma}" rows="2" maxlength="500" placeholder="Em nghĩ gì về video này? Ghi lại điều em nhớ nhất…"></textarea>'
            f'<button type="submit" class="bl-gui">{ICON["gui"]}<span>Gửi</span></button></form>'
            f'<p class="bl-ghi-chu">Bình luận và lượt thích được lưu ngay trên máy của em, không gửi đi đâu, không cần đăng nhập.</p>{ngoai}'
            f'<ol class="bl-ds"></ol></section>')


def trang_tap(x, bai, truoc, sau, cap_nhat):
    kb = x["kb"] or {}
    ma, lop = x["ma"], x["lop"]
    nb = nhan_bai(bai["ma"])
    so_tap_bai = len(bai["tap"])
    # --- đầu trang
    vi_tri = (f'<nav class="vet" aria-label="Vị trí"><ol><li><a href="../index.html">Thư viện</a></li>'
              f'<li><a href="../index.html#lop-{lop}">Lớp {lop}</a></li>'
              f'<li><a href="../index.html#{bai["id"]}">{e(nb)}</a></li><li aria-current="page">Tập {x["so"]}</li></ol></nav>')
    the = [f'<span class="the the-lop">Lớp {lop}</span>',
           f'<span class="the">{e(KHUNG.get(x["khung"], x["khung"]).replace(" dọc", ""))}</span>',
           f'<span class="the tt-{x["trang_thai"]}"><span class="dau-tt" aria-hidden="true"></span>{e(TT_CHU[x["trang_thai"]])}</span>']
    if x["video"]:
        the.append(f'<span class="the">{phut_giay(x["video"]["thoi_luong"])}</span>')
    quay = (f'<a class="nut-quay-lai" href="../index.html#{bai["id"]}" data-quay-lai>{ICON["quay_lai"]}<span>Quay lại</span></a>')
    dau = (f'<div class="dau-tap">{quay}{vi_tri}<p class="bai-cua-tap">{e(nb)}. {e(bai["ten"])}</p>'
           f'<h1{lop_h1(x["ten_tap"])}>{et(x["ten_tap"])}</h1>'
           + (f'<p class="ten-en" lang="en">{e(x["ten_tap_en"])}</p>' if x["ten_tap_en"] else "")
           + f'<p class="cac-the">{"".join(the)}</p></div>')
    # --- video + ghi chú phụ đề
    if x["video"] or x["youtube_id"]:
        phu_de = ("Phụ đề song ngữ gắn sẵn trong video: tiếng Việt ở dòng trên, tiếng Anh ở dòng dưới. "
                  + ("Bản chữ đầy đủ của lời thoại ở mục “Lời thoại” cuối trang." if kb else ""))
    else:
        phu_de = "Khi hoàn thành, video có phụ đề song ngữ gắn sẵn: tiếng Việt ở dòng trên, tiếng Anh ở dòng dưới."
    lien_ket_ngoai = []
    if x["youtube"] and x["video"]:
        lien_ket_ngoai.append(f'<a href="{e(x["youtube"])}" target="_blank" rel="noopener noreferrer">Xem trên YouTube</a>')
    if x["tiktok"]:
        lien_ket_ngoai.append(f'<a href="{e(x["tiktok"])}" target="_blank" rel="noopener noreferrer">Xem trên TikTok</a>')
    ngoai = (f'<p class="lien-ket-ngoai">{"".join(lien_ket_ngoai)}<span>(mở trang web bên ngoài)</span></p>'
             if lien_ket_ngoai else "")
    co_gn, co_cau = bool(kb and ghi_nho(kb)), bool(kb and kb.get("cau_hoi"))
    goi_y = ("Trong lúc chờ, em hãy đọc phần ghi nhớ và làm câu hỏi ôn tập bên dưới." if co_gn and co_cau else
             "Trong lúc chờ, em hãy làm câu hỏi ôn tập bên dưới." if co_cau else
             "Trong lúc chờ, em hãy đọc phần ghi nhớ bên dưới." if co_gn else "Em hãy quay lại sau nhé.")
    video = (f'<section class="muc-video" aria-label="Video">{khoi_video(x, goi_y)}{thanh_hanh_dong(x)}'
             f'<p class="ghi-chu-phu-de" id="ghi-chu-phu-de"><span class="bieu-tuong-cc" aria-hidden="true">CC</span>{e(phu_de)}</p>{ngoai}</section>')
    # --- cột bên: SGK, mô phỏng
    nguon = kb.get("nguon") or {}
    ben = [f'<section class="o-ben" aria-labelledby="h-sgk"><h2 id="h-sgk">Bài học trong SGK</h2>'
           f'<p><i>{e(x["sach"])}</i></p><p>{e(nguon.get("bai") or (nb + ". " + bai["ten"]))}</p>'
           f'<p class="tr-lon">{e(trang_chu(x["trang_sgk"]) or ("tr. " + str(bai.get("trang_in", ""))))}</p></section>']
    if x["mo_phong"]:
        m = x["mo_phong"]
        ben.append(f'<section class="o-ben o-mp" aria-labelledby="h-mp"><h2 id="h-mp">Mô phỏng tương tác</h2>'
                   f'<p class="loai-mp">{e(m["loai"])}</p><p>{e(m["mota"])}</p>'
                   f'<a class="nut-chinh" href="../{e(m["href"])}">Mở mô phỏng</a></section>')
    else:
        cung_bai = [t for t in bai["tap"] if t["mo_phong"] and t["ma"] != ma]
        if cung_bai:
            m = cung_bai[0]
            ben.append(f'<section class="o-ben o-mp" aria-labelledby="h-mp"><h2 id="h-mp">Mô phỏng cùng bài</h2>'
                       f'<p class="loai-mp">{e(m["mo_phong"]["loai"])}</p><p>{e(m["mo_phong"]["mota"])}</p>'
                       f'<a class="nut-phu" href="../{e(m["mo_phong"]["href"])}">Mở mô phỏng của tập {m["so"]}</a></section>')
    # --- nội dung chính
    muc = []
    gn = ghi_nho(kb) if kb else []
    if gn:
        li = "".join(f'<li><span>{e(y)}</span>' + (f' <span class="tr">({e(trang_chu(tr))})</span>' if tr else "") + "</li>"
                     for y, tr in gn)
        muc.append(f'<section class="muc" aria-labelledby="h-ghi-nho"><h2 id="h-ghi-nho">Ghi nhớ</h2><ul class="ghi-nho">{li}</ul></section>')
    for i, m in enumerate(moc_thoi_gian(kb) if kb else []):
        tieu = m["tieu_de"].split("·", 1)[-1].strip() if m["tieu_de"] else ""
        tieu = tieu[:1] + tieu[1:].lower() if tieu.isupper() else tieu
        li = "".join(f'<li><b>{e(a)}</b><span>{e(b)}</span></li>' for a, b in m["moc"])
        muc.append(f'<section class="muc" aria-labelledby="h-moc-{i}"><h2 id="h-moc-{i}">Mốc thời gian</h2>'
                   + (f'<p class="phu-de-muc">{e(tieu)}</p>' if tieu else "")
                   + f'<ol class="dong-moc">{li}</ol>' + (f'<p class="tr">{e(trang_chu(m["tr"], "SGK tr. "))}</p>' if m["tr"] else "")
                   + "</section>")
    cau = []
    if kb and kb.get("cau_hoi"):
        uv = cau_ung_vien(kb)
        for q in kb["cau_hoi"]:
            cau.append({"hoi": q["hoi"], "dap_an": q["dap_an"], "dung": int(q["dung"]), "trang": q.get("trang"),
                        "giai_thich": tim_giai_thich(q, uv)})
        sach = re.sub(r"\s*\(.*?\)\s*$", "", x["sach"])
        du_phong = "".join(
            f'<li><p class="hoi">{e(q["hoi"])}</p><ol class="dap-an-tinh" type="A">' + "".join(f"<li>{e(a)}</li>" for a in q["dap_an"])
            + f'</ol><details><summary>Xem đáp án</summary><p>{"ABCDEFG"[q["dung"]]}. {e(q["dap_an"][q["dung"]])}'
            + (f' ({e(trang_chu([q["trang"]], "SGK tr. "))})' if q.get("trang") else "") + "</p></details></li>"
            for q in cau)
        du_lieu = json.dumps({"sach": sach, "cau": cau}, ensure_ascii=False).replace("</", "<\\/")
        muc.append(f'<section class="muc luyen-tap" aria-labelledby="h-luyen-tap"><h2 id="h-luyen-tap">Luyện tập nhanh</h2>'
                   f'<p class="phu-de-muc">{len(cau)} câu trắc nghiệm. Chọn một đáp án cho mỗi câu; máy chấm ngay và chỉ ra trang SGK để em xem lại.</p>'
                   f'<div id="cau-hoi" class="cau-hoi"><ol class="du-phong">{du_phong}</ol></div>'
                   f'<script type="application/json" id="du-lieu-cau-hoi">{du_lieu}</script></section>')
    # lời thoại (bản chữ của video) – chỉ khi đã có video
    if kb and (x["video"] or x["youtube_id"]):
        canh = []
        for c in kb.get("canh", []):
            loi = [l for l in c.get("loi", []) if len(l) >= 2]
            if not loi:
                continue
            dong = []
            for l in loi:
                tai_hien = l[0] not in DAN_CHUYEN
                dong.append(f'<div class="cau-thoai{" tai-hien" if tai_hien else ""}"><p class="nguoi-noi">{e(l[0])}'
                            + ('<span class="nhan-tai-hien">lời tái hiện</span>' if tai_hien else "") + "</p>"
                            + f'<p>{e(l[1])}</p>' + (f'<p class="en" lang="en">{e(l[2])}</p>' if len(l) > 2 and l[2] else "") + "</div>")
            canh.append(f'<li>{"".join(dong)}</li>')
        if canh:
            muc.append(f'<section class="muc" aria-labelledby="h-loi"><h2 id="h-loi">Lời thoại</h2>'
                       f'<details class="loi-thoai"><summary>Xem bản chữ song ngữ của video ({len(canh)} đoạn)</summary>'
                       f'<ol class="ds-thoai">{"".join(canh)}</ol></details></section>')
    if not kb:
        muc.append('<section class="muc"><h2>Nội dung</h2><p>Kịch bản của tập này chưa được đưa vào thư viện.</p></section>')
    # các tập cùng bài
    cung = "".join(dong_tap(t, "../").replace('class="tap-dong', 'class="tap-dong' + (" hien-tai" if t["ma"] == ma else ""), 1)
                   .replace(f'href="../tap/{ma}.html"', f'href="../tap/{ma}.html" aria-current="page"')
                   for t in bai["tap"])
    cung = cung.replace('href="../tap/', 'href="')
    muc.append(f'<section class="muc" aria-labelledby="h-cung-bai"><h2 id="h-cung-bai">Các tập của {e(nb)}</h2>'
               f'<p class="phu-de-muc">{so_tap_bai} tập</p><ol class="ds-tap">{cung}</ol></section>')
    # chú thích nguồn
    ghi_chu = kb.get("ghi_chu_tai_hien") or ""
    nguon_dong = (f'<section class="nguon-tap" aria-label="Nguồn"><p><b>Nguồn:</b> {e(x["sach"])}, {e(nb)}, '
                  f'{e(trang_chu(x["trang_sgk"]) or "")}. Kịch bản đã đối chiếu với SGK; mỗi ý ghi nhớ và câu hỏi có số trang để em tự kiểm tra.</p>'
                  + (f'<p>{e(ghi_chu)}</p>' if ghi_chu else "") + "</section>")
    trc = (f'<a class="tap-truoc" href="{truoc["ma"]}.html"><span>Tập trước</span>{et(truoc["ten_tap"])}</a>' if truoc else "<span></span>")
    sau_ = (f'<a class="tap-sau" href="{sau["ma"]}.html"><span>Tập sau</span>{et(sau["ten_tap"])}</a>' if sau else "<span></span>")
    than = (f'<article class="trang-tap" data-trang="tap" data-ma="{ma}">'
            f'<section class="rap{" rap-doc" if x["huong"] == "doc" else ""}" aria-label="Video và thông tin bài học"><div class="rong">{dau}'
            f'<div class="luoi-tap"><div class="vung-video">{video}</div><aside class="cot-ben" aria-label="Thông tin bài học">{"".join(ben)}</aside></div>'
            f'</div></section><div class="rong"><div class="cot-chinh">{"".join(muc)}</div>'
            f'{nguon_dong}<nav class="truoc-sau" aria-label="Tập khác">{trc}{sau_}</nav></div></article>')
    mo_ta = f"Lịch sử lớp {lop}, {nb}. {bai['ten']}: {x['ten_tap']}."
    if gn:
        mo_ta += " " + gn[0][0]
    return khuon(f"{x['ten_tap']} – Lớp {lop}, {nb} | EduHistory Studio", mo_ta, than, goc="../", lop_body="trang-tap-body",
                 cap_nhat=cap_nhat)


# ---------------------------------------------------------------- trang giới thiệu
def trang_gioi_thieu(ds, cap_nhat):
    n_v = sum(1 for x in ds if x["trang_thai"] == "co-video")
    n_k = sum(1 for x in ds if x["kb"])
    n_mp = len({x["ma"] for x in ds if x["mo_phong"]})
    n_cau = sum(len(x["kb"]["cau_hoi"]) for x in ds if x["kb"])
    buoc = [
        ("Chọn và chuẩn hoá nội dung",
         "Lập danh mục bài học và tập video theo SGK <i>Lịch sử và Địa lí</i> 6–9. Kho dữ kiện chỉ lưu ý đã diễn đạt lại kèm số trang, không chép nguyên văn sách."),
        ("Tạo video bằng AI",
         "Kịch bản có hai bạn dẫn chuyện Nhật Minh và Hân Hân. AI tạo sinh vẽ cảnh minh hoạ và đọc lời thuyết minh; bản đồ, sơ đồ trận đánh, mốc thời gian và chữ trên hình được dựng bằng code từ dữ liệu đã kiểm tra."),
        ("Kiểm chứng với SGK",
         "Từng câu thoại gắn số trang SGK. Câu hỏi, số liệu và đáp án được đối chiếu lại với văn bản SGK đã số hoá trước khi dựng video. Theo nguyên tắc của dự án, giáo viên hướng dẫn duyệt lần cuối trước khi đăng."),
        ("Dùng trong lớp học và mạng xã hội",
         "Video được chiếu trong tiết học. Bản dọc 60 giây dự kiến đăng thành video ngắn (TikTok, YouTube Shorts) để học sinh ôn bài ngoài giờ."),
        ("Đóng gói thành kho học liệu",
         "Website này: tìm theo lớp, bài, từ khoá; mỗi tập có video, ghi nhớ, câu hỏi ôn tập và mô phỏng tương tác nếu có."),
    ]
    ol = "".join(f'<li><span class="so-buoc" aria-hidden="true">{i}</span><div><h3>{t}</h3><p>{p}</p></div></li>'
                 for i, (t, p) in enumerate(buoc, 1))
    than = f"""<div class="rong gioi-thieu">
<header class="dau-gt">
  <h1 class="mot-dong">ChronoVibe Team&nbsp;-&nbsp;EduHistory</h1>
  <p class="dan dan-lon">Số hóa bài học Lịch sử thông qua hệ thống video bài học, ghi nhớ kiến thức, mô phỏng tương tác, câu hỏi ôn&nbsp;tập</p>
  <p class="dan">EduHistory Studio chuyển bài học Lịch sử lớp 6–9 thành video hoạt hình ngắn, kèm ghi nhớ, câu hỏi ôn tập và mô phỏng tương tác. Đây là dự án dự thi FPT School STEMPETITION 2027 (bảng THCS, Challenge 3: Smart Education) của đội ChronoVibe, Trường TH, THCS &amp; THPT FPT Bắc Giang.</p>
</header>
<dl class="so-lieu so-lieu-gt"><div><dt>Video đã hoàn thành</dt><dd>{n_v}</dd></div><div><dt>Kịch bản đã đối chiếu SGK</dt><dd>{n_k}</dd></div><div><dt>Câu hỏi ôn tập</dt><dd>{n_cau}</dd></div><div><dt>Mô phỏng tương tác</dt><dd>{n_mp}</dd></div></dl>
<p class="ghi-chu-so">Số liệu tính tự động từ kho dữ liệu của dự án tại thời điểm cập nhật ({cap_nhat}). Kế hoạch gồm {len(ds)} tập; các tập còn lại đang được sản xuất dần.</p>

<section class="muc-gt" aria-labelledby="h-quy-trinh">
  <h2 id="h-quy-trinh">Quy trình 5 bước</h2>
  <ol class="quy-trinh">{ol}</ol>
</section>

<section class="muc-gt" aria-labelledby="h-chinh-xac">
  <h2 id="h-chinh-xac">Giữ đúng kiến thức SGK</h2>
  <p>AI tạo sinh có thể “bịa” chi tiết. Dự án đặt ra các quy tắc sau để hạn chế điều đó:</p>
  <ul class="quy-tac">
    <li><b>Phân tầng hình ảnh.</b> AI chỉ vẽ lớp minh hoạ (bối cảnh, trang phục, không khí). Bản đồ, niên đại, số liệu và chữ trên hình dựng bằng code từ dữ liệu đã thẩm định; bản đồ Việt Nam luôn có quần đảo Hoàng Sa và Trường Sa.</li>
    <li><b>Mọi câu đều có nguồn.</b> Mỗi câu thoại, ý ghi nhớ và câu hỏi gắn với lớp, bài, trang SGK. Trên website, số trang hiện ngay cạnh nội dung để học sinh tự mở sách kiểm tra.</li>
    <li><b>Đối chiếu với SGK đã số hoá.</b> Kịch bản được so lại với văn bản SGK (nhận dạng chữ từ ảnh trang sách); công cụ kiểm tra tự động soát số trang, số liệu, đáp án. Chỗ nào sửa kiến thức phải dẫn được dòng SGK làm căn cứ.</li>
    <li><b>Lời thoại tái hiện được ghi rõ.</b> Lời của nhân vật lịch sử là lời dựng lại cho sinh động, không đưa thêm sự kiện, số liệu ngoài SGK; cuối mỗi video và trong mục “Lời thoại” đều ghi chú điều này.</li>
    <li><b>Lịch sử hiện đại dùng tư liệu thật.</b> Lãnh tụ và nhân vật thời hiện đại không do AI vẽ; dùng ảnh, phim tư liệu có nguồn.</li>
    <li><b>Con người duyệt cuối cùng.</b> Nguyên tắc của dự án: giáo viên hướng dẫn thẩm định trước khi sản xuất và trước khi đăng.</li>
  </ul>
</section>

<section class="muc-gt" aria-labelledby="h-vibe">
  <h2 id="h-vibe">Vibe Coding</h2>
  <p>Các công cụ của dự án – bộ dựng video tự động, bản đồ động, mô phỏng tương tác và chính website này – được làm bằng cách mô tả yêu cầu bằng tiếng Việt cho trợ lý AI lập trình, chạy thử, phát hiện lỗi rồi yêu cầu sửa. Mỗi phiên được ghi vào nhật ký Vibe Coding trong kho mã (<code>docs/vibe-coding/nhat-ky.md</code>): yêu cầu, việc AI làm, lỗi phát hiện khi kiểm tra và cách xử lý.</p>
</section>

<section class="muc-gt" aria-labelledby="h-rieng-tu">
  <h2 id="h-rieng-tu">Quyền riêng tư</h2>
  <p>Website không cần tài khoản, không dùng cookie, không gửi dữ liệu đi đâu. Kết quả làm câu hỏi chỉ nằm trên trình duyệt và mất khi tải lại trang. Lượt thích và bình luận dưới mỗi video được lưu ngay trên máy của em (bộ nhớ trình duyệt), chỉ em nhìn thấy và có thể xoá bất cứ lúc nào. Phông chữ và hình ảnh nằm sẵn trong website; trang chỉ kết nối ra ngoài khi em chủ động bấm “Phát video từ YouTube” hoặc mở link TikTok của một tập.</p>
</section>

<section class="muc-gt" aria-labelledby="h-doi">
  <h2 id="h-doi">Đội thực hiện</h2>
  <dl class="doi">
    <div><dt>Đội thi</dt><dd>ChronoVibe – học sinh THCS, Trường TH, THCS &amp; THPT FPT Bắc Giang</dd></div>
    <div><dt>Giáo viên hướng dẫn</dt><dd>Nguyễn Hữu Hiệu, Trần Khánh Ly</dd></div>
    <div><dt>Nguồn kiến thức</dt><dd>SGK <i>Lịch sử và Địa lí</i> 6, 7, 8, 9 (Kết nối tri thức với cuộc sống), bộ sách dùng chung</dd></div>
    <div><dt>Phông chữ</dt><dd>Be Vietnam Pro, Playfair Display (giấy phép SIL Open Font License 1.1)</dd></div>
  </dl>
  <p class="ghi-chu-so">Website hỗ trợ việc học, không thay thế SGK và bài giảng của thầy cô. Nếu phát hiện chỗ chưa đúng, hãy báo cho giáo viên hướng dẫn kèm mã tập (ví dụ L7-B14-04) và số trang SGK.</p>
</section>
</div>"""
    return khuon("Giới thiệu | ChronoVibe Team - EduHistory",
                 "EduHistory Studio – dự án STEMPETITION 2027 của đội ChronoVibe: video Lịch sử 6–9 tạo bằng AI, kiểm chứng với SGK, Vibe Coding.",
                 than, dang="gioi-thieu", lop_body="trang-gt", cap_nhat=cap_nhat)


# ---------------------------------------------------------------- chuyện sử mở rộng (12 video dọc ~1 phút, bản đăng TikTok)
TT_THU_MUC = os.path.join(ROOT, "data", "tiktok")
TT_VIDEO = os.path.join(ROOT, "renders", "tiktok")


def _bai_cua_tt(nguon, bai_ds):
    """'Lịch sử và Địa lí 6' + 'Bài 14. …' -> (bài trong thư viện hoặc None, nhãn ngắn 'Lớp 6, Bài 14')."""
    sach, bai = nguon.get("sach", ""), nguon.get("bai", "")
    cac_lop = re.findall(r"\d", sach)
    m = re.search(r"(Bài|Chủ đề chung)\s*(\d+)", bai)
    b = None
    if cac_lop and m:
        bid = f"L{cac_lop[0]}-{'B' if m.group(1) == 'Bài' else 'CD'}{m.group(2)}"
        b = next((x for x in bai_ds if x["id"] == bid), None)
    if len(cac_lop) > 1:
        nhan = "Lớp " + ", ".join(cac_lop)
    elif cac_lop and b:
        nhan = f"Lớp {cac_lop[0]}, {nhan_bai(b['ma'])}"
    else:
        nhan = "Lớp " + (cac_lop[0] if cac_lop else "")
    return b, nhan


def _bia_tt(ma, video_tep, kiem_tra):
    """Ảnh bìa dọc 540×960 từ tranh cảnh mở đầu (không phụ đề); dự phòng 1 khung hình video."""
    thu_muc = os.path.join(WEB, "du-lieu", "anh-bia"); dich = os.path.join(thu_muc, ma + ".jpg")
    rel = f"du-lieu/anh-bia/{ma}.jpg"
    if kiem_tra or os.path.exists(dich):
        return rel if os.path.exists(dich) else None
    from PIL import Image
    nguon = os.path.join(ROOT, "assets", "episodes", ma, "canh-01.jpg")
    try:
        if not os.path.exists(nguon):
            nguon = os.path.join(thu_muc, ma + ".khung.jpg")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "4", "-i", video_tep, "-frames:v", "1", nguon], check=True, timeout=60)
        im = Image.open(nguon).convert("RGB")
        _cat_ti_le(im, 9 / 16, 0.5).resize((540, 960), Image.LANCZOS).save(dich, "JPEG", quality=84, optimize=True, progressive=True)
        if nguon.endswith(".khung.jpg"):
            os.remove(nguon)
        return rel
    except Exception as ex:
        bao(f"Không tạo được ảnh bìa {ma}: {ex}")
        return None


def doc_chuyen_su(ch, bai_ds, kiem_tra):
    lien_ket = (doc_json(LIEN_KET_TEP).get("tap", {}) if os.path.exists(LIEN_KET_TEP) else {})
    ds = []
    for p in sorted(glob.glob(os.path.join(TT_THU_MUC, "TT-*.json"))):
        t = doc_json(p); ma = t["ma"]
        nguon_v = os.path.join(TT_VIDEO, ma + ".mp4")
        if not os.path.exists(nguon_v):
            continue
        tt = ffprobe(nguon_v)
        if not tt:
            bao(f"{ma}.mp4 chưa đọc được (có thể đang dựng) – bỏ qua lần này"); continue
        tep = f"videos/{ma}.mp4"
        if not kiem_tra:
            os.makedirs(os.path.join(WEB, "videos"), exist_ok=True)
            dua_video(nguon_v, os.path.join(WEB, tep), ch["cach_dua_video"])
        bai, nhan = _bai_cua_tt(t.get("nguon", {}), bai_ds)
        lk = lien_ket.get(ma, {})
        ds.append({"ma": ma, "ten_tap": t["ten_tap"], "ten_tap_en": t.get("ten_tap_en", ""), "huong": "doc",
                   "video": dict(tt, tep=tep), "anh_bia": _bia_tt(ma, nguon_v, kiem_tra),
                   "youtube_id": None, "youtube": lk.get("youtube"), "tiktok": lk.get("tiktok"),
                   "sach": t.get("nguon", {}).get("sach", ""), "bai_chu": t.get("nguon", {}).get("bai", ""),
                   "bai": bai, "nhan": nhan, "nguon_mo_rong": t.get("nguon_mo_rong", []),
                   "ghi_chu": t.get("ghi_chu_tai_hien", ""),
                   "loi": [l for c in t.get("canh", []) for l in c.get("loi", []) if len(l) >= 2]})
    return ds


def the_chuyen_su(x, goc=""):
    anh = (f'<img src="{goc}{e(x["anh_bia"])}" alt="" width="540" height="960" loading="lazy">' if x["anh_bia"]
           else trong_dong("anh-thay"))
    return (f'<li><a class="the-video doc" href="{goc}chuyen-su/{x["ma"]}.html"><span class="khung-anh">{anh}'
            f'<span class="thoi-luong">{phut_giay(x["video"]["thoi_luong"])}</span><span class="nut-phat-nho" aria-hidden="true"></span></span>'
            f'<span class="lop-bai">Mở rộng từ {e(x["nhan"])}</span>'
            f'<span class="ten" title="{e(x["ten_tap"])}">{et(x["ten_tap"])}</span></a></li>')


def ke_chuyen_su(tt_ds):
    if not tt_ds:
        return ""
    return (f'<section class="ke-video ke-doc" id="chuyen-su" aria-labelledby="tieu-de-chuyen-su"><div class="rong">'
            f'<div class="dau-muc"><h2 id="tieu-de-chuyen-su">Chuyện sử mở rộng</h2>'
            f'<p>{len(tt_ds)} video dọc khoảng một phút, kể thêm những câu chuyện quanh bài học trong SGK. '
            f'Mỗi video ghi rõ bài học gốc và nguồn để em tự kiểm chứng.</p></div>'
            f'<ul class="luoi-doc" tabindex="0" aria-label="Danh sách chuyện sử, cuộn ngang để xem thêm">{"".join(the_chuyen_su(x) for x in tt_ds)}</ul></div></section>')


def _ten_mien(u):
    m = re.match(r"https?://(?:www\.)?([^/]+)", u)
    return m.group(1) if m else u


def trang_chuyen_su(x, truoc, sau, cap_nhat):
    ma = x["ma"]
    vi_tri = (f'<nav class="vet" aria-label="Vị trí"><ol><li><a href="../index.html">Thư viện</a></li>'
              f'<li><a href="../index.html#chuyen-su">Chuyện sử mở rộng</a></li><li aria-current="page">{e(ma)}</li></ol></nav>')
    the = ['<span class="the the-lop">Chuyện sử mở rộng</span>', '<span class="the">Video dọc</span>',
           f'<span class="the">{phut_giay(x["video"]["thoi_luong"])}</span>']
    quay = f'<a class="nut-quay-lai" href="../index.html#chuyen-su" data-quay-lai>{ICON["quay_lai"]}<span>Quay lại</span></a>'
    dau = (f'<div class="dau-tap">{quay}{vi_tri}<p class="bai-cua-tap">Mở rộng từ {e(x["nhan"])}</p>'
           f'<h1{lop_h1(x["ten_tap"])}>{et(x["ten_tap"])}</h1>'
           + (f'<p class="ten-en" lang="en">{e(x["ten_tap_en"])}</p>' if x["ten_tap_en"] else "")
           + f'<p class="cac-the">{"".join(the)}</p></div>')
    lien_ket_ngoai = [f'<a href="{e(u)}" target="_blank" rel="noopener noreferrer">Xem trên {t}</a>'
                      for u, t in ((x["tiktok"], "TikTok"), (x["youtube"], "YouTube")) if u]
    ngoai = (f'<p class="lien-ket-ngoai">{"".join(lien_ket_ngoai)}<span>(mở trang web bên ngoài)</span></p>' if lien_ket_ngoai else "")
    video = (f'<section class="muc-video" aria-label="Video">{khoi_video(x)}{thanh_hanh_dong(x)}'
             f'<p class="ghi-chu-phu-de" id="ghi-chu-phu-de"><span class="bieu-tuong-cc" aria-hidden="true">CC</span>'
             f'Phụ đề song ngữ gắn sẵn trong video: tiếng Việt ở dòng trên, tiếng Anh ở dòng dưới. Bản chữ đầy đủ ở mục “Lời kể”.</p>{ngoai}</section>')
    b = x["bai"]
    ben = (f'<section class="o-ben" aria-labelledby="h-sgk"><h2 id="h-sgk">Bài học gốc trong SGK</h2>'
           f'<p><i>{e(x["sach"])}</i></p><p>{e(x["bai_chu"])}</p>'
           + (f'<a class="nut-phu" href="../index.html#{e(b["id"])}">Xem các tập video của bài này</a>' if b else "")
           + '</section>')
    muc = []
    if x["loi"]:
        dong = "".join(f'<li><div class="cau-thoai"><p class="nguoi-noi">{e(l[0])}</p><p>{e(l[1])}</p>'
                       + (f'<p class="en" lang="en">{e(l[2])}</p>' if len(l) > 2 and l[2] else "") + "</div></li>" for l in x["loi"])
        muc.append(f'<section class="muc" aria-labelledby="h-loi"><h2 id="h-loi">Lời kể</h2>'
                   f'<details class="loi-thoai" open><summary>Bản chữ song ngữ của video ({len(x["loi"])} câu)</summary>'
                   f'<ol class="ds-thoai">{dong}</ol></details></section>')
    if x["nguon_mo_rong"]:
        li = "".join(f'<li><a href="{e(u)}" target="_blank" rel="noopener noreferrer">{e(_ten_mien(u))}</a></li>' for u in x["nguon_mo_rong"])
        muc.append(f'<section class="muc" aria-labelledby="h-nguon-mr"><h2 id="h-nguon-mr">Nguồn kiểm chứng</h2>'
                   f'<p class="phu-de-muc">Phần kể thêm ngoài SGK được đối chiếu với các bài viết sau (mở trang web bên ngoài).</p>'
                   f'<ul class="ds-nguon">{li}</ul></section>')
    nguon_dong = (f'<section class="nguon-tap" aria-label="Nguồn"><p><b>Nguồn:</b> {e(x["sach"])}, {e(x["bai_chu"])}; '
                  f'các bài viết ở mục “Nguồn kiểm chứng”.</p>' + (f'<p>{e(x["ghi_chu"])}</p>' if x["ghi_chu"] else "") + "</section>")
    trc = (f'<a class="tap-truoc" href="{truoc["ma"]}.html"><span>Chuyện trước</span>{et(truoc["ten_tap"])}</a>' if truoc else "<span></span>")
    sau_ = (f'<a class="tap-sau" href="{sau["ma"]}.html"><span>Chuyện sau</span>{et(sau["ten_tap"])}</a>' if sau else "<span></span>")
    than = (f'<article class="trang-tap" data-trang="tap" data-ma="{ma}">'
            f'<section class="rap rap-doc" aria-label="Video và thông tin"><div class="rong">{dau}'
            f'<div class="luoi-tap"><div class="vung-video">{video}</div><aside class="cot-ben" aria-label="Bài học gốc">{ben}</aside></div>'
            f'</div></section><div class="rong"><div class="cot-chinh">{"".join(muc)}</div>'
            f'{nguon_dong}<nav class="truoc-sau" aria-label="Chuyện khác">{trc}{sau_}</nav></div></article>')
    mo_ta = f"Chuyện sử mở rộng từ {x['sach']}, {x['bai_chu']}: {x['ten_tap']}."
    return khuon(f"{x['ten_tap']} – Chuyện sử mở rộng | EduHistory Studio", mo_ta, than, goc="../",
                 lop_body="trang-tap-body", cap_nhat=cap_nhat)


# ---------------------------------------------------------------- chạy
def main():
    ap = argparse.ArgumentParser(description="Tạo lại Kho học liệu số (web/index.html, web/tap/*.html, web/du-lieu/thu-vien.json)")
    ap.add_argument("--cach-dua-video", choices=CACH_DUA, help="ghi đè cach_dua_video trong cau-hinh.json")
    ap.add_argument("--khong-video-cuc-bo", action="store_true", help="không tính video cục bộ (bản đăng GitHub Pages)")
    ap.add_argument("--khong-anh-bia", action="store_true", help="không tạo ảnh bìa mới")
    ap.add_argument("--kiem-tra", action="store_true", help="chỉ đọc và báo cáo, không ghi tệp nào")
    args = ap.parse_args()
    ch = doc_cau_hinh(args)
    bai_ds, ds = dung_du_lieu(ch, args.kiem_tra)
    # ngày cập nhật = thời điểm sửa mới nhất của dữ liệu đầu vào (để chạy lại không đổi tệp nếu dữ liệu không đổi)
    moc = [os.path.getmtime(p) for p in glob.glob(os.path.join(ROOT, "data", "scripts", "L*.json"))]
    moc += [os.path.getmtime(os.path.join(ROOT, "data", "catalog", f)) for f in ("episodes.json", "lessons.json")]
    moc += [os.path.getmtime(os.path.join(WEB, x["video"]["tep"])) for x in ds if x["video"]]
    if os.path.exists(LIEN_KET_TEP):
        moc.append(os.path.getmtime(LIEN_KET_TEP))
    cap_nhat = datetime.datetime.fromtimestamp(max(moc), TZ).strftime("%d/%m/%Y")

    trang = [x for x in ds if x["co_trang"]]
    bai_id = {b["id"]: b for b in bai_ds}
    for i, x in enumerate(trang):
        ghi(os.path.join(WEB, "tap", x["ma"] + ".html"),
            trang_tap(x, bai_id[x["bai"]], trang[i - 1] if i > 0 else None, trang[i + 1] if i + 1 < len(trang) else None, cap_nhat),
            args.kiem_tra)
    # xoá trang tập cũ không còn trong thư viện
    con = {x["ma"] for x in trang}
    for p in glob.glob(os.path.join(WEB, "tap", "*.html")):
        ma = os.path.basename(p)[:-5]
        if MA_TAP.match(ma) and ma not in con and not args.kiem_tra:
            os.remove(p)
    tt_ds = doc_chuyen_su(ch, bai_ds, args.kiem_tra)
    for i, x in enumerate(tt_ds):
        ghi(os.path.join(WEB, "chuyen-su", x["ma"] + ".html"),
            trang_chuyen_su(x, tt_ds[i - 1] if i > 0 else None, tt_ds[i + 1] if i + 1 < len(tt_ds) else None, cap_nhat),
            args.kiem_tra)
    ghi(os.path.join(WEB, "index.html"), trang_index(bai_ds, ds, cap_nhat, tt_ds), args.kiem_tra)
    ghi(os.path.join(WEB, "gioi-thieu.html"), trang_gioi_thieu(ds, cap_nhat), args.kiem_tra)
    ghi(os.path.join(WEB, "du-lieu", "menu.js"), du_lieu_menu(bai_ds, doc_mo_phong_them()), args.kiem_tra)
    if not os.path.exists(LIEN_HE_TEP) and not args.kiem_tra:
        ghi(LIEN_HE_TEP, json.dumps(dict(LIEN_HE, _ghi_chu="Điền link kênh TikTok/YouTube khi có, rồi chạy lại tao_thu_vien.py và tao_trang.py."), ensure_ascii=False, indent=1) + "\n", False)
    # dữ liệu máy đọc được (cho công cụ khác, ứng dụng sau này)
    du_lieu = {
        "nguon": "Sinh tự động bởi web/_cong-cu/tao_thu_vien.py từ data/catalog, data/scripts, video đã dựng, web/mo-phong, web/du-lieu/lien-ket.json",
        "cap_nhat": cap_nhat,
        "bai": [{"id": b["id"], "lop": b["lop"], "ten": b["ten"], "nhan": nhan_bai(b["ma"]), "chuong": b.get("chuong"),
                 "trang_in": b.get("trang_in"), "tap": [x["ma"] for x in b["tap"]]} for b in bai_ds],
        "tap": [dict({k: x[k] for k in ("ma", "bai", "lop", "so", "ten_tap", "ten_tap_en", "khung", "huong", "trang_thai",
                                          "trang_sgk", "video", "youtube", "tiktok", "anh_bia")},
                     trang=f"tap/{x['ma']}.html" if x["co_trang"] else None,
                     mo_phong=x["mo_phong"]["href"] if x["mo_phong"] else None,
                     so_cau_hoi=len(x["kb"]["cau_hoi"]) if x["kb"] else 0) for x in ds],
        "chuyen_su": [{"ma": x["ma"], "ten": x["ten_tap"], "ten_en": x["ten_tap_en"], "trang": f"chuyen-su/{x['ma']}.html",
                       "video": x["video"], "anh_bia": x["anh_bia"], "bai_goc": x["bai"]["id"] if x["bai"] else None,
                       "sach": x["sach"], "bai": x["bai_chu"], "nguon_mo_rong": x["nguon_mo_rong"]} for x in tt_ds],
    }
    ghi(os.path.join(WEB, "du-lieu", "thu-vien.json"), json.dumps(du_lieu, ensure_ascii=False, indent=1) + "\n", args.kiem_tra)

    n = {k: sum(1 for x in ds if x["trang_thai"] == k) for k in TT_CHU}
    print(f"Thư viện: {len(ds)} tập trong {len(bai_ds)} bài | có video: {n['co-video']} | có kịch bản, đang dựng: {n['co-kich-ban']} "
          f"| đang viết kịch bản: {n['ke-hoach']} | trang tập: {len(trang)} | mô phỏng liên kết: {sum(1 for x in ds if x['mo_phong'])}")
    gt = sum(1 for x in ds if x["kb"] for q in x["kb"]["cau_hoi"] if tim_giai_thich(q, cau_ung_vien(x["kb"])))
    tong = sum(len(x["kb"]["cau_hoi"]) for x in ds if x["kb"])
    print(f"Câu hỏi: {tong} | có câu giải thích lấy từ kịch bản: {gt}")
    print(f"Chuyện sử mở rộng (video dọc): {len(tt_ds)}")
    if args.kiem_tra:
        print("(chế độ kiểm tra: không ghi tệp)")
    if canh_bao:
        print(f"{len(canh_bao)} cảnh báo (xem ở trên).")


if __name__ == "__main__":
    main()
