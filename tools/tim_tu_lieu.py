"""Tìm ảnh tư liệu cho cảnh lop=tu_lieu trên Wikimedia Commons (chỉ phạm vi công cộng, CC0, CC BY, CC BY-SA).
Ghi ứng viên (tối đa 6/cảnh) vào tmp/tl/ung_vien.json và bảng ảnh xem nhanh tmp/tl/bang_XX.jpg để Claude chọn.
Dùng: python3 tools/tim_tu_lieu.py [mã tập ...]   (mặc định: mọi tập chưa dựng, chỉ cảnh chưa có ảnh)"""
import json, glob, os, re, sys, io, time, urllib.request, urllib.parse, html
from PIL import Image, ImageDraw, ImageFont
ROOT = "/home/claude/eduhistory-studio"; OUT = f"{ROOT}/tmp/tl"; os.makedirs(OUT, exist_ok=True)
API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "EduHistoryStudio/1.0 (https://github.com/HieuNH39/EduHistory-Studio; school project) python-urllib/3"}
OK = re.compile(r"public domain|^pd|cc0|cc[- ]by(?![- ]n)", re.I)
def get(params):
    q = API + "?" + urllib.parse.urlencode({**params, "format": "json"})
    for k in range(6):
        try:
            time.sleep(1.2)
            with urllib.request.urlopen(urllib.request.Request(q, headers=UA), timeout=40) as r: return json.load(r)
        except Exception as e:
            time.sleep(15 * (k + 1) if "429" in str(e) else 3 * (k + 1)); err = e
    raise err
def sach(s): return re.sub(r"<[^>]+>", "", html.unescape(s or "")).strip()
def tim(q, n=14):
    d = get({"action": "query", "generator": "search", "gsrsearch": q + " filetype:bitmap", "gsrnamespace": 6, "gsrlimit": n,
             "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata", "iiurlwidth": 360})
    out = []
    for p in sorted((d.get("query") or {}).get("pages", {}).values(), key=lambda p: p.get("index", 99)):
        ii = (p.get("imageinfo") or [{}])[0]; md = ii.get("extmetadata") or {}
        lic = sach(md.get("LicenseShortName", {}).get("value"))
        if ii.get("mime") not in ("image/jpeg", "image/png", "image/tiff") or not OK.search(lic) or re.search(r"\bNC\b|\bND\b|non-free|fair use", lic, re.I): continue
        if (ii.get("width") or 0) < 700: continue
        out.append({"tep": p["title"], "trang": ii.get("descriptionurl"), "url": ii.get("url"), "thumb": ii.get("thumburl"),
                    "rong": ii.get("width"), "cao": ii.get("height"), "giay_phep": lic,
                    "tac_gia": sach(md.get("Artist", {}).get("value"))[:80], "ngay": sach(md.get("DateTimeOriginal", {}).get("value"))[:40],
                    "mo_ta": sach(md.get("ImageDescription", {}).get("value"))[:160]})
    return out
def can_tim(ids):
    rend = {os.path.basename(p)[:-4] for p in glob.glob(f"{ROOT}/renders/v1/*.mp4")}
    ds = []
    for f in sorted(glob.glob(f"{ROOT}/data/scripts/L*.json")):
        sp = json.load(open(f)); ma = sp["ma"]
        if (ids and ma not in ids) or (not ids and ma in rend): continue
        for c in sp["canh"]:
            if c.get("lop") != "tu_lieu": continue
            b = f"{ROOT}/assets/episodes/{ma}/canh-{int(c['so']):02d}"
            if any(os.path.exists(b + e) for e in (".jpg", ".png", ".webp")): continue
            tl = c.get("tu_lieu") or {}
            ds.append({"ma": ma, "so": int(c["so"]), "huong": sp.get("huong"), "mo_ta": tl.get("mo_ta") or c.get("hinh", ""),
                       "tim": tl.get("tim") or "", "yeu_cau": tl.get("yeu_cau", ""), "loi": [l[1] for l in c.get("loi", [])]})
    return ds
if __name__ == "__main__":
    ids = sys.argv[1:]
    TV = {}
    if os.path.exists(f"{OUT}/truy_van.txt"):
        for ln in open(f"{OUT}/truy_van.txt"):
            p = ln.rstrip("\n").split("|")
            if len(p) == 3: TV[f"{p[0]}|{p[1]}"] = [q.strip() for q in p[2].split(";") if q.strip()]
    ds = can_tim(ids); kq = []
    try: kq = json.load(open(f"{OUT}/ung_vien.json"))
    except Exception: pass
    xong = {(x["ma"], x["so"]) for x in kq}
    for x in ds:
        if (x["ma"], x["so"]) in xong: continue
        qs = TV.get(f'{x["ma"]}|{x["so"]}') or [x["tim"]]
        uv = []
        for q in qs:
            for u in tim(q, 10):
                if u["tep"] not in {v["tep"] for v in uv}: uv.append(u)
            if len(uv) >= 12: break
        x["ung_vien"] = uv[:8]; x["truy_van"] = qs; kq.append(x)
        print(x["ma"], x["so"], len(x["ung_vien"]), x["tim"][:50], flush=True)
        json.dump(kq, open(f"{OUT}/ung_vien.json", "w"), ensure_ascii=False, indent=1)
