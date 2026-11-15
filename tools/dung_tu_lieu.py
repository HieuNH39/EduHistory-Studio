"""Áp dụng lựa chọn ảnh tư liệu (tmp/tl/chon.json) → tải ảnh gốc từ Commons (bản ≤ 2560 px) → tools/tu_lieu.py dựng cảnh.
chon.json: {"MA/so": {"i": số thứ tự ứng viên (1-8), "chu_thich": "..."}  hoặc  "MA/so": "khong" (chưa có ảnh phù hợp)}"""
import json, os, subprocess, urllib.request, urllib.parse, re, time
ROOT = "/home/claude/eduhistory-studio"; OUT = f"{ROOT}/tmp/tl"
UA = {"User-Agent": "EduHistoryStudio/1.0 (school project; github.com/HieuNH39)"}
kq = {f"{x['ma']}/{x['so']}": x for x in json.load(open(f"{OUT}/ung_vien.json"))}
chon = json.load(open(f"{OUT}/chon.json"))
def tai(url, dst):
    for k in range(2):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r: open(dst, "wb").write(r.read())
            time.sleep(4); return
        except Exception as e:
            time.sleep(20 if "429" in str(e) else 3); err = e
    raise err
for key, c in chon.items():
    if c == "khong" or not isinstance(c, dict): continue
    ma, so = key.split("/"); so = int(so)
    if os.path.exists(f"{ROOT}/assets/episodes/{ma}/canh-{so:02d}.jpg") and not c.get("lam_lai"): continue
    u = kq[key]["ung_vien"][c["i"] - 1]
    # Commons chặn tải ảnh gốc (429) với máy chủ tự động → ưu tiên bản thu nhỏ cỡ chuẩn (1920/1280/960 px)
    goc = u["url"].split("?")[0]; rong = u.get("rong") or 0
    urls = []
    if "/commons/" in goc:
        fn = goc.rsplit("/", 1)[1]; th = goc.replace("/commons/", "/commons/thumb/")
        duoi = ".jpg" if fn.lower().endswith((".tif", ".tiff")) else ""
        urls = [f"{th}/{w}px-{fn}{duoi}" for w in (1920, 1280, 960) if w < rong]
    urls.append(goc)
    if "/commons/" in goc:   # ảnh gốc bị chặn: lấy bản thu nhỏ chuẩn nhỏ hơn (vẫn đủ cho khung tư liệu)
        urls += [f"{th}/{w}px-{fn}{duoi}" for w in (500,) if w < rong]
    ext = os.path.splitext(urls[0])[1].lower() or ".jpg"
    src = f"{OUT}/goc_{ma}_{so:02d}{ext}"
    if not os.path.exists(src):
        ok = False
        for url in urls:
            try: tai(url, src); ok = True; break
            except Exception as ex: loi = ex
        if not ok: print(key, "LỖI tải", str(loi)[:120], flush=True); continue
    tg = re.sub(r"\s+", " ", u.get("tac_gia") or "").strip()
    if not tg or re.search(r"unknown|anonymous|anonyme|inconnu", tg, re.I): tg = "khuyết danh"
    nam = None if c.get("bo_nam") else (re.search(r"\b(1[6-9]\d\d|20\d\d)\b", u.get("ngay") or "") or [None])[0]
    nguon = c.get("nguon") or f"Ảnh: {tg[:60]}{', ' + nam if nam else ''} (Wikimedia Commons)"
    gp = "Phạm vi công cộng" if re.search(r"public domain|^pd", u["giay_phep"], re.I) else u["giay_phep"]
    cmd = ["python3", f"{ROOT}/tools/tu_lieu.py", src, ma, str(so), "--nguon", nguon, "--giay-phep", gp, "--trang", u["trang"],
           "--tep", u["tep"], "--mo-ta", kq[key]["mo_ta"][:200]]
    if c.get("chu_thich"): cmd += ["--chu-thich", c["chu_thich"]]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(key, "OK" if r.returncode == 0 else "LỖI " + r.stderr[-300:], u["tep"][:60], flush=True)
