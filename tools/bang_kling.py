"""Bảng đánh số mọi cảnh cần KlingAI (ảnh khung đầu Gemini + lời nhắc chuyển động) → tmp/kling_bang/Kling_EduHistory.xlsx
Thứ tự: A. đã có ảnh, chỉ cần Kling → B. cảnh tái hiện (chưa có ảnh thì tập chưa dựng được) → C. dẫn chuyện / du hành (đã có hình vẽ bằng code, Kling làm đẹp thêm).
Cảnh có nhân vật dùng ảnh tư liệu thật (nhan-vat.json: anh_tu_lieu) không làm AI → trang riêng."""
import json, glob, os, re
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
ROOT = "/home/claude/eduhistory-studio"
cat = json.load(open(f"{ROOT}/data/catalog/episodes.json"))
thu_tu = {t["ma"]: i for i, t in enumerate(cat["tap"])}
tap_cat = {t["ma"]: t for t in cat["tap"]}
nv = {x["id"]: x for x in json.load(open(f"{ROOT}/data/catalog/nhan-vat.json"))["nhan_vat"]}
rendered = {os.path.basename(p)[:-4] for p in glob.glob(f"{ROOT}/renders/v1/*.mp4")}
THAM = {os.path.basename(p).rsplit("-v", 1)[0]: p for p in sorted(glob.glob(f"{ROOT}/brand/characters/lich-su/nhap/*-v1.jpg"))}
THEO_BAI = {"L7-B14": ["khang-chien-1258", "bach-dang-1288"], "L7-B13": ["khang-chien-1258"], "L8-B8": ["nguyen-hue", "nhom-tay-son-xiem", "dai-pha-quan-thanh"]}
NEG = "text, subtitles, watermark, logo, extra fingers, distorted face, morphing, flicker, blood, gore, modern objects in historical scenes"
LOAI = {"dan_chuyen": "Dẫn chuyện", "tai_hien": "Tái hiện", "du_hanh": "Du hành thời gian"}
DONG_PHUC = ("Nhật Minh và Hân Hân giống hệt ảnh tham chiếu: 15 tuổi, áo polo cam FPT viền trắng mảnh ở cổ và tay, "
             "Nhật Minh quần kaki nâu, Hân Hân váy kaki xếp ly nâu, giày trắng, ba lô xanh đậm.")
def co_hai_ban(c):
    return c.get("lop") in ("dan_chuyen", "du_hanh") or re.search(r"Nhật Minh|Hân Hân|hai bạn", c.get("hinh", ""))
def anh_co_san(ma, c):
    b = f"{ROOT}/assets/episodes/{ma}/canh-{int(c['so']):02d}"
    for e in (".jpg", ".png", ".webp"):
        if os.path.exists(b + e): return b + e
    a = c.get("anh")
    if a and re.search(r"\.(jpe?g|png|webp)$", a) and "assets/episodes" in a and os.path.exists(os.path.join(ROOT, a)): return a
    return None
def loi_anh(ma, c, khung, t):
    doc = khung == "9:16"
    p = (f"Tranh minh hoạ cho video bài học Lịch sử, phong cách hoạt hình 2D vẽ tay chi tiết, ánh sáng điện ảnh ấm, màu tự nhiên, "
         f"khung {'dọc 9:16' if doc else 'ngang 16:9'}, độ phân giải cao. Bối cảnh bài học: {t.get('ten_bai','')} – {t.get('ten_tap','')}. "
         "Trang phục, khí giới, kiến trúc, đồ vật đúng thời kì của cảnh. Không có chữ, không chữ ký, không logo, không khung viền.\n"
         f"Cảnh: {c.get('hinh','').strip()}")
    if co_hai_ban(c): p += "\n" + DONG_PHUC
    if re.search(r"bản đồ|lược đồ", c.get("hinh", ""), re.I):
        p += "\nNếu có bản đồ Việt Nam thì phải thể hiện quần đảo Hoàng Sa và quần đảo Trường Sa; không ghi chữ trên bản đồ."
    return p
def tham_chieu(c):
    r = []
    if co_hai_ban(c): r.append("bang-nhan-vat-v5.png (Nhật Minh – Hân Hân)")
    for i in (c.get("nhan_vat") or []):
        if i in THAM: r.append(os.path.basename(THAM[i]))
    if c.get("lop") == "tai_hien":
        for k in THEO_BAI.get(c["_bai"], []):
            if k == "dai-pha-quan-thanh" and "Thanh" not in c.get("hinh", ""): continue
            if k in THAM and os.path.basename(THAM[k]) not in r: r.append(os.path.basename(THAM[k]))
    return "; ".join(r) or "(không cần)"
rows, tu_lieu, da_xong = [], [], 0
for f in sorted(glob.glob(f"{ROOT}/data/scripts/L*.json")):
    sp = json.load(open(f)); ma = sp["ma"]
    if "canh" not in sp: continue
    t = tap_cat.get(ma, {}); khung = "9:16" if sp.get("huong") == "doc" else "16:9"
    kp = {}
    if os.path.exists(f"{ROOT}/data/kling/{ma}.json"):
        kp = {int(x["so"]): x for x in json.load(open(f"{ROOT}/data/kling/{ma}.json"))["canh"]}
    for c in sp["canh"]:
        if c.get("chuyen_dong") != "kling": continue
        c["_bai"] = ma.rsplit("-", 1)[0]
        so = int(c["so"]); base = f"{ROOT}/assets/episodes/{ma}/canh-{so:02d}"
        if os.path.exists(base + ".mp4") or c.get("video"): da_xong += 1; continue
        thuc = [nv[i]["ten"] for i in (c.get("nhan_vat") or []) if i in nv and nv[i].get("nguon_hinh") == "anh_tu_lieu"]
        if thuc:
            tu_lieu.append([ma, so, sp.get("ten_tap", ""), ", ".join(thuc), c.get("hinh", "")]); continue
        anh = anh_co_san(ma, c)
        nhom = "A" if anh else ("B" if c.get("lop") == "tai_hien" else "C")
        dur = kp.get(so, {}).get("thoi_luong") or (10 if sum(len(l[1]) for l in c.get("loi", [])) > 130 else 5)
        rows.append(dict(nhom=nhom, ord=(nhom, thu_tu.get(ma, 999), so), ma=ma, so=so, ten=sp.get("ten_tap", ""), loai=LOAI.get(c.get("lop"), c.get("lop")),
                         khung=khung, dur=dur, anh="Đã có" if anh else "Cần tạo", loi_anh="(đã có ảnh – bỏ qua bước này)" if anh else loi_anh(ma, c, khung, t),
                         kling=kp.get(so, {}).get("prompt", ""), tham="" if anh else tham_chieu(c),
                         trang=", ".join(str(x) for x in (c.get("nguon_trang") or (sp.get("nguon", {}).get("trang") or []))),
                         dung=ma in rendered, anh_path=anh))
rows.sort(key=lambda r: r["ord"])
NHOM = {"A": "A · Đã có ảnh, chỉ cần Kling", "B": "B · Tái hiện: cần ảnh + Kling", "C": "C · Dẫn chuyện/du hành (không bắt buộc)"}
wb = Workbook(); ws = wb.active; ws.title = "Danh sách Kling"
H = ["STT", "Mã tập", "Cảnh", "Trạng thái", "Khung", "Thời lượng (giây)", "Ảnh khung đầu", "Lời nhắc tạo ảnh (Gemini)",
     "Lời nhắc chuyển động (Kling)", "Negative prompt (Kling)", "Ảnh tham chiếu đính kèm khi tạo ảnh", "Tên file ảnh (lưu vào Tải về)",
     "Tên file video (lưu vào Tải về)", "Nhóm", "Loại cảnh", "Tên tập", "Trang SGK"]
ws.append(H)
for i, r in enumerate(rows, 1):
    ws.append([i, r["ma"], r["so"], "Chưa làm", r["khung"], r["dur"], r["anh"], r["loi_anh"], r["kling"] or "(chưa có – Claude bổ sung)", NEG,
               r["tham"] or "—", f"{r['ma']}_canh-{r['so']:02d}.jpg" if r["anh"] == "Cần tạo" else f"Có sẵn trong tệp nén: anh-khung-dau-nhom-A/{r['ma']}_canh-{r['so']:02d}.jpg", f"{r['ma']}_canh-{r['so']:02d}.mp4",
               NHOM[r["nhom"]], r["loai"], r["ten"], r["trang"]])
W = [6, 11, 6, 14, 7, 9, 10, 60, 60, 30, 32, 26, 26, 30, 14, 34, 10]
for j, w in enumerate(W): ws.column_dimensions[chr(65 + j)].width = w
hdr = PatternFill("solid", fgColor="0B1A31"); bd = Side(style="thin", color="C9D3E3")
for c in ws[1]:
    c.font = Font(bold=True, color="F3E6CC", name="Arial", size=10); c.fill = hdr
    c.alignment = Alignment(wrap_text=True, vertical="center")
for row in ws.iter_rows(min_row=2):
    for c in row:
        c.font = Font(name="Arial", size=10); c.alignment = Alignment(vertical="top", wrap_text=c.column in (8, 9, 10, 11, 16))
ws.freeze_panes = "D2"
dv = DataValidation(type="list", formula1='"Chưa làm,Đã có ảnh,Đã có video,Lỗi – làm lại,Bỏ qua"', allow_blank=True)
ws.add_data_validation(dv); dv.add(f"D2:D{len(rows)+1}")
# Hướng dẫn
g = wb.create_sheet("Hướng dẫn")
from collections import Counter
cn = Counter(r["nhom"] for r in rows)
L = [["Cách làm một dòng (theo số thứ tự từ 1)"], [""],
 ["1", "Tạo ảnh khung đầu (chỉ khi cột Ảnh khung đầu ghi “Cần tạo”): mở Gemini (gói Pro), đính kèm các ảnh ở cột “Ảnh tham chiếu”, dán “Lời nhắc tạo ảnh”, chọn đúng khung (16:9 hoặc 9:16). Ảnh sai đồng phục, có chữ lạ, tay chân dị dạng thì tạo lại."],
 ["2", "Tải ảnh về, đổi tên đúng cột “Tên file ảnh”, để trong thư mục Tải về (Downloads) của máy Mac."],
 ["3", "Mở KlingAI → Image to Video: tải ảnh khung đầu lên (nhóm A: ảnh có sẵn trong thư mục anh-khung-dau-nhom-A của tệp nén Claude gửi kèm), dán “Lời nhắc chuyển động”, dán “Negative prompt” nếu Kling có ô này, chọn thời lượng theo cột “Thời lượng”."],
 ["4", "Tải video về (giữ nguyên dấu nước Kling, không cắt), đổi tên đúng cột “Tên file video”, để trong thư mục Tải về."],
 ["5", "Đổi cột “Trạng thái” thành “Đã có video” (hoặc “Đã có ảnh” nếu mới xong bước ảnh). Khi Claude làm việc trở lại, Claude đọc cột này, lấy file trong Tải về theo đúng tên, kiểm tra rồi dựng video hoàn chỉnh."],
 [""], ["Thứ tự ưu tiên"],
 ["A", f"{cn['A']} cảnh đã có ảnh khung đầu: chỉ cần làm bước 3–5."],
 ["B", f"{cn['B']} cảnh tái hiện: chưa có ảnh thì tập chưa dựng được, nên làm theo đúng số thứ tự (đi hết từng tập)."],
 ["C", f"{cn['C']} cảnh dẫn chuyện / du hành: đã có hình hai bạn vẽ bằng code, Kling chỉ làm đẹp thêm, làm khi còn thời gian."],
 [""], ["Lưu ý"],
 ["•", "Ảnh tham chiếu: bang-nhan-vat-v5.png và các bảng nhân vật lịch sử *-v1.jpg nằm trong thư mục anh-tham-chieu của tệp nén Claude gửi kèm."],
 ["•", f"{len(tu_lieu)} cảnh có nhân vật dùng ảnh tư liệu thật không đưa vào danh sách (xem trang “Không làm AI”)."],
 ["•", "Không tạo ảnh chân dung lãnh tụ bằng AI; bản đồ Việt Nam luôn có Hoàng Sa, Trường Sa; không mua thêm gói Kling."],
 ["•", f"{da_xong} cảnh đã có clip Kling từ trước, không nằm trong danh sách."]]
for x in L: g.append(x)
g.column_dimensions["A"].width = 6; g.column_dimensions["B"].width = 110
for rr in g.iter_rows():
    for c in rr: c.font = Font(name="Arial", size=11); c.alignment = Alignment(wrap_text=True, vertical="top")
for r_ in (1, 9, 14): g.cell(r_, 1).font = Font(name="Arial", size=13, bold=True, color="0B1A31")
t2 = wb.create_sheet("Không làm AI")
t2.append(["Mã tập", "Cảnh", "Tên tập", "Nhân vật dùng ảnh tư liệu", "Mô tả cảnh"])
for x in tu_lieu: t2.append(x)
for j, w in enumerate([11, 6, 34, 34, 80]): t2.column_dimensions[chr(65 + j)].width = w
os.makedirs(f"{ROOT}/tmp/kling_bang", exist_ok=True)
wb.save(f"{ROOT}/tmp/kling_bang/Kling_EduHistory.xlsx")
json.dump([dict(r, ord=None) for r in rows if r["nhom"] == "A"], open(f"{ROOT}/tmp/kling_bang/nhom_a.json", "w"), ensure_ascii=False)
print(len(rows), dict(cn), "tư liệu", len(tu_lieu), "đã xong", da_xong, "thiếu prompt", sum(1 for r in rows if not r["kling"]))
