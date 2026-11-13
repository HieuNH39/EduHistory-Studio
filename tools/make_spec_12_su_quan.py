"""Sa bàn (saban2) 'Cát cứ của 12 sứ quân và công cuộc thống nhất của Đinh Bộ Lĩnh'.
Vẽ lại, giản lược theo Hình 1 'Lược đồ cát cứ của 12 sứ quân', SGK Lịch sử và Địa lí 7, Bài 9, tr. 46:
toạ độ cục bộ đo trên ảnh lược đồ (khung 185..1285 × 500..1510), sông vẽ giản lược, vị trí thủ phủ và tên sứ quân đúng lược đồ.
Như lược đồ SGK, có ô bản đồ nhỏ Việt Nam (nền Natural Earth 1:50m) thể hiện quần đảo Hoàng Sa, Trường Sa.
SGK không ghi vị trí Hoa Lư trên lược đồ nên sa bàn không chấm Hoa Lư (chỉ nêu bằng băng chữ)."""
import json, math
ROOT = "/home/claude/eduhistory-studio"

# ---- 12 sứ quân: (khoá, tên vùng, tên sứ quân, vị trí thủ phủ, lệch nhãn [dx, dy] theo đơn vị lược đồ, canh trái/phải)
SQ = [("hoi_ho", "HỒI HỒ", "Kiều Thuận", (360, 640), (-12, 40)),
      ("phong_chau", "PHONG CHÂU", "Kiều Công Hãn", (460, 655), (90, 5)),
      ("duong_lam", "ĐƯỜNG LÂM", "Ngô Nhật Khánh", (505, 755), (-60, 8)),
      ("tam_dai", "TAM ĐÁI", "Nguyễn Khoan", (585, 735), (60, 3)),
      ("do_dong_giang", "ĐỖ ĐỘNG GIANG", "Đỗ Cảnh Thạc", (617, 872), (-95, 3)),
      ("tay_phu_liet", "TÂY PHÙ LIỆT", "Nguyễn Siêu", (740, 895), (-62, 30)),
      ("tien_du", "TIÊN DU", "Nguyễn Thủ Tiệp", (900, 805), (65, 3)),
      ("sieu_loai", "SIÊU LOẠI", "Lý Khuê", (850, 875), (58, 3)),
      ("te_giang", "TẾ GIANG", "Lữ Đường", (815, 930), (58, 3)),
      ("dang_chau", "ĐẰNG CHÂU", "Phạm Bạch Hổ", (885, 1025), (70, 3)),
      ("bo_hai_khau", "BỐ HẢI KHẨU", "Trần Lãm", (997, 1130), (75, 3)),
      ("binh_kieu", "BÌNH KIỀU", "Ngô Xương Xí", (568, 1445), (70, -22))]

def nhan_sq(key, ten, sq, p, l):
    x, y = p[0] + l[0], p[1] + l[1]
    return {f"n_{key}": {"loai": "nhan", "vi_tri": [x, y - 8], "chu": ten, "co": 13, "mau": "chu"},
            f"s_{key}": {"loai": "nhan", "vi_tri": [x, y + 11], "chu": f"({sq})", "co": 11, "mau": "dich"}}

# ---- sông (giản lược theo lược đồ)
SONG = [
 {"ten": "S. Hồng", "nhan": [262, 560], "goc": 62, "rong": 9, "diem": [[280, 500], [292, 545], [320, 590], [362, 628], [402, 662], [442, 695], [492, 714], [534, 746], [584, 782], [640, 808], [700, 822], [748, 842], [772, 900], [790, 980], [818, 1050], [858, 1110], [880, 1165], [896, 1235], [922, 1300], [956, 1362], [990, 1405]]},
 {"ten": "S. Đáy", "nhan": [700, 1045], "goc": 65, "rong": 6, "diem": [[548, 728], [575, 770], [604, 812], [632, 870], [652, 925], [680, 990], [712, 1052], [742, 1122], [772, 1200], [808, 1280], [846, 1355], [882, 1428]]},
 {"ten": "S. Đuống", "nhan": [818, 812], "goc": -8, "rong": 5, "diem": [[748, 842], [800, 836], [852, 828], [905, 822], [962, 818], [1018, 830], [1060, 852]]},
 {"ten": "S. Cầu", "nhan": [842, 732], "goc": 55, "rong": 5, "diem": [[815, 705], [845, 738], [885, 760], [930, 790], [968, 812], [992, 840]]},
 {"ten": "S. Thái Bình", "nhan": [1010, 950], "goc": 62, "rong": 6, "diem": [[992, 840], [1000, 900], [1012, 960], [1040, 1015], [1070, 1060], [1092, 1110], [1110, 1160], [1135, 1215], [1160, 1262]]},
 {"ten": "S. Thương", "nhan": [1010, 605], "goc": -28, "rong": 5, "diem": [[1180, 540], [1110, 570], [1050, 610], [1010, 660], [992, 720], [985, 790], [992, 840]]},
 {"ten": "S. Lục Nam", "nhan": [1100, 690], "goc": -12, "rong": 5, "diem": [[1280, 655], [1200, 668], [1130, 690], [1060, 712], [1010, 735], [992, 760]]},
 {"ten": "S. Đá Bạc", "nhan": [1090, 862], "goc": 18, "rong": 5, "diem": [[1060, 852], [1110, 862], [1160, 885], [1210, 915], [1260, 940]]},
 {"ten": "S. Mã", "nhan": [455, 1235], "goc": 62, "rong": 6, "diem": [[360, 1040], [395, 1110], [430, 1175], [470, 1245], [505, 1315], [535, 1385], [560, 1460], [580, 1510]]},
]
# biển (góc dưới bên phải lược đồ)
BIEN = [[1900, 1180], [1285, 1235], [1240, 1250], [1190, 1275], [1150, 1305], [1105, 1335], [1060, 1372], [1015, 1410], [968, 1442], [930, 1470], [895, 1510], [850, 1600], [1900, 1600]]

# ---- ô bản đồ nhỏ Việt Nam (như lược đồ SGK) – đặt ở khoảng trống bên trái, dưới chú giải (tránh logo, thẻ mốc)
IX0, IY0, IX1, IY1 = -357, 870, -45, 1210
LON0, LAT0, KY = 101.0, 24.5, 18.9
KX = KY * math.cos(math.radians(15))
def ip(lon, lat): return [round(IX0 + (lon - LON0) * KX, 1), round(IY0 + (LAT0 - lat) * KY, 1)]

def clip(poly, x0, y0, x1, y1):
    """Cắt đa giác theo hình chữ nhật (Sutherland – Hodgman)."""
    def cut(pts, inside, inter):
        out = []
        for i in range(len(pts)):
            a, b = pts[i - 1], pts[i]
            if inside(b):
                if not inside(a): out.append(inter(a, b))
                out.append(b)
            elif inside(a): out.append(inter(a, b))
        return out
    def ix(a, b, x): t = (x - a[0]) / (b[0] - a[0]); return [x, a[1] + t * (b[1] - a[1])]
    def iy(a, b, y): t = (y - a[1]) / (b[1] - a[1]); return [a[0] + t * (b[0] - a[0]), y]
    for inside, inter in ((lambda p: p[0] >= x0, lambda a, b: ix(a, b, x0)), (lambda p: p[0] <= x1, lambda a, b: ix(a, b, x1)),
                          (lambda p: p[1] >= y0, lambda a, b: iy(a, b, y0)), (lambda p: p[1] <= y1, lambda a, b: iy(a, b, y1))):
        poly = cut(poly, inside, inter)
        if not poly: return []
    return poly

def inset():
    g = json.load(open(f"{ROOT}/assets/geo/ne_50m_dong_nam_a.geojson"))
    out = [{"diem": [[IX0, IY0], [IX1, IY0], [IX1, IY1], [IX0, IY1]], "mau": [0.80, 0.88, 0.93], "vien": 1.6}]
    for f in g["features"]:
        geo = f["geometry"]; polys = geo["coordinates"] if geo["type"] == "MultiPolygon" else [geo["coordinates"]]
        for poly in polys:
            pts = clip([ip(*c) for c in poly[0]], IX0, IY0, IX1, IY1)
            if len(pts) >= 3:
                out.append({"diem": [[round(x, 1), round(y, 1)] for x, y in pts], "mau": [0.96, 0.89, 0.72] if f["properties"]["ADMIN"] == "Vietnam" else [0.88, 0.87, 0.83], "vien": 0.5})
    return out

def dao_inset(lon, lat, ten, n, r, lech):
    import random; random.seed(int(lon * 100 + lat))
    pts = [ip(lon + random.uniform(-r, r), lat + random.uniform(-r, r)) for _ in range(n)]
    return [{"ten": "", "vi_tri": p, "kieu": "diem"} for p in pts] + [{"ten": ten, "vi_tri": [ip(lon, lat)[0] + lech[0], ip(lon, lat)[1] + lech[1]], "co": 9.5, "dam": True}]

doi = {}
for key, ten, sq, p, l in SQ:
    doi[f"t_{key}"] = {"loai": "don_dich", "vi_tri": list(p)}
    doi.update(nhan_sq(key, ten, sq, p, l))
doi["khung_nho"] = {"loai": "vong", "rong": 2.2, "diem": [ip(104.9, 21.6), ip(106.9, 21.6), ip(106.9, 19.8), ip(104.9, 19.8)]}
TAT = [f"t_{k}" for k, *_ in SQ] + [f"n_{k}" for k, *_ in SQ] + [f"s_{k}" for k, *_ in SQ]

S = {
 "phien_ban": 2, "ten": "Dẹp loạn 12 sứ quân", "phu_de": "Đinh Bộ Lĩnh thống nhất đất nước",
 "nguon": "Vẽ lại, giản lược theo Hình 1, SGK Lịch sử và Địa lí 7, Bài 9, tr. 46; ô nhỏ: nền Natural Earth",
 "khung": [255, 560, 1285, 1500], "lech_x": 0.06, "tam": [760, 1040],
 "vung_mau": [{"diem": BIEN, "mau": [0.612, 0.765, 0.835], "vien": 1.8}] + inset(),
 "song": SONG,
 "dia_danh": [{"ten": "BIỂN ĐÔNG", "vi_tri": [1175, 1430], "co": 20, "dam": True}]
             + dao_inset(112.0, 16.5, "QĐ. Hoàng Sa", 5, .5, (0, -16)) + dao_inset(114.0, 9.6, "QĐ. Trường Sa", 6, .8, (0, -22))
             + [{"ten": "VIỆT NAM", "vi_tri": ip(105.2, 15.2), "co": 9, "dam": True}, {"ten": "Biển Đông", "vi_tri": ip(113.6, 13.0), "co": 9}],
 "chu_giai": [{"loai": "don_dich", "nhan": "Thủ phủ của các sứ quân"}],
 "doi_tuong": doi,
 "pha": {
  "cat_cu": {"mo_dau": True, "zoom": [1.0, 1.015], "hien": ["khung_nho"], "chu_giai": ["don_dich"],
             "moc": [{"chu": "Năm 965", "tu": 0.06, "den": 1.1}],
             "buoc": [{"id": x, "tu": 0.1 + 0.055 * i, "den": 0.16 + 0.055 * i} for i, (k, *_) in enumerate(SQ) for x in (f"t_{k}", f"n_{k}", f"s_{k}")]},
  "chia_cat": {"zoom": [1.0, 1.02], "hien": ["khung_nho"] + TAT, "chu_giai": ["don_dich"],
               "moc": [{"chu": "Đất nước bị chia cắt", "tu": 0.05, "den": 1.1}],
               "bang": {"chu": "Đinh Bộ Lĩnh – Vạn Thắng Vương", "tu": 0.35, "y": 0.62}},
  "thong_nhat": {"zoom": [1.02, 1.0], "hien": ["khung_nho"] + TAT, "chu_giai": ["don_dich"],
                 "moc": [{"chu": "Năm 966 – 967", "tu": 0.04, "den": 1.1}],
                 "buoc": [{"id": f"t_{k}", "tu": 0.08 + 0.05 * i, "den": 0.14 + 0.05 * i, "hieu_ung": "mat"} for i, (k, *_) in enumerate(SQ)],
                 "bang": {"chu": "Thống nhất đất nước, lập ra nhà Đinh", "tu": 0.78, "y": 0.62}}
 }
}
json.dump(S, open(f"{ROOT}/pipeline/maps/specs/12-su-quan.json", "w"), ensure_ascii=False)
print("ok", len(S["vung_mau"]), "vùng")

# ================================================================ BẢN DỌC (1080 × 1920) cho tập 60 giây L7-B9-02
# Khung hình dọc: tỉ lệ s = 1,1; nội dung lược đồ nằm trong dải y ≈ 295 – 1345 px, tránh thẻ tiêu đề (trên trái),
# logo (trên phải, cao ~ 145 px) và phụ đề dọc (y ≈ 1360 – 1540 px). Ô bản đồ nhỏ Việt Nam đặt trong vùng biển,
# góc dưới bên phải lược đồ – vẫn thể hiện QĐ. Hoàng Sa, QĐ. Trường Sa như lược đồ SGK. Không dùng thẻ mốc góc phải.
IX0, IY0, IX1, IY1 = 1032, 1278, 1254, 1514
LON0, LAT0, KY = 101.5, 24.0, 13.9
KX = KY * math.cos(math.radians(15))
doi_doc = {k: v for k, v in doi.items() if k != "khung_nho"}
doi_doc["khung_nho"] = {"loai": "vong", "rong": 2.0, "diem": [ip(104.9, 21.6), ip(106.9, 21.6), ip(106.9, 19.8), ip(104.9, 19.8)]}
D = {
 "phien_ban": 2, "ten": "Cát cứ 12 sứ quân", "phu_de": "Năm 965",
 "nguon": S["nguon"],
 "khung": [300, 326.7, 1120, 1723.1], "lech_x": -0.0685, "tam": [710, 1035], "chu_giai_xy": [0.026, 0.1156],
 "vung_mau": [{"diem": BIEN, "mau": [0.612, 0.765, 0.835], "vien": 1.8}] + inset(),
 "song": SONG,
 "dia_danh": [{"ten": "BIỂN ĐÔNG", "vi_tri": [960, 1490], "co": 14, "dam": True}]
             + dao_inset(112.0, 16.5, "QĐ. Hoàng Sa", 4, .9, (0, -20)) + dao_inset(114.0, 9.6, "QĐ. Trường Sa", 5, 1.3, (-8, -26))
             + [{"ten": "VIỆT NAM", "vi_tri": ip(105.0, 15.6), "co": 8, "dam": True}, {"ten": "Biển Đông", "vi_tri": ip(113.4, 12.8), "co": 8}],
 "chu_giai": S["chu_giai"],
 "doi_tuong": doi_doc,
 "pha": {
  "cat_cu": {"mo_dau": True, "zoom": [1.0, 1.015], "hien": ["khung_nho"], "chu_giai": ["don_dich"],
             "buoc": [{"id": x, "tu": 0.1 + 0.055 * i, "den": 0.16 + 0.055 * i} for i, (k, *_) in enumerate(SQ) for x in (f"t_{k}", f"n_{k}", f"s_{k}")],
             "bang": {"chu": "Đất nước bị chia cắt", "tu": 0.84, "y": 0.53}}
 }
}
json.dump(D, open(f"{ROOT}/pipeline/maps/specs/12-su-quan-doc.json", "w"), ensure_ascii=False)
print("ok (dọc)", len(D["vung_mau"]), "vùng")
