"""Sa bàn (saban2) 'Tiến công trước để tự vệ' – giai đoạn thứ nhất kháng chiến chống Tống (1075).
Vẽ lại, giản lược theo Hình 2 'Lược đồ cuộc kháng chiến chống quân xâm lược Tống giai đoạn thứ nhất (1075)',
SGK Lịch sử và Địa lí 7, Bài 12, tr. 59: toạ độ cục bộ đo trên ảnh lược đồ (khung 137..1290 × 330..1200).
Không vẽ đường biên giới (giản lược); như lược đồ SGK, có ô bản đồ nhỏ Việt Nam thể hiện quần đảo Hoàng Sa, Trường Sa."""
import json, math
ROOT = "/home/claude/eduhistory-studio"

# ---- ô bản đồ nhỏ Việt Nam (đặt bên phải lược đồ, dưới logo và thẻ mốc)
IX0, IY0, IX1, IY1 = 1360, 600, 1640, 905
LON0, LAT0, KY = 101.0, 24.5, 16.4
KX = KY * math.cos(math.radians(15))
def ip(lon, lat): return [round(IX0 + (lon - LON0) * KX, 1), round(IY0 + (LAT0 - lat) * KY, 1)]
def clip(poly, x0, y0, x1, y1):
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
    return [{"ten": "", "vi_tri": p, "kieu": "diem"} for p in pts] + [{"ten": ten, "vi_tri": [ip(lon, lat)[0] + lech[0], ip(lon, lat)[1] + lech[1]], "co": 8, "dam": True}]


BIEN = [[560, 1075], [650, 1022], [740, 995], [800, 975], [860, 955], [900, 932], [922, 900], [945, 878], [975, 892], [1030, 925], [1100, 950],
        [1180, 975], [1300, 990], [1700, 990], [1700, 1400], [500, 1400]]
DAO = [[[700, 1040], [716, 1034], [722, 1048], [706, 1054]], [[760, 1030], [778, 1024], [782, 1040], [764, 1044]], [[830, 1000], [846, 994], [850, 1008], [834, 1012]]]
SONG = [
 {"ten": "S. Kì Cùng", "nhan": [470, 930], "goc": 22, "rong": 4, "diem": [[380, 880], [430, 905], [480, 935], [540, 960], [600, 975]]},
 {"ten": "", "rong": 4, "diem": [[180, 1010], [240, 985], [300, 965], [360, 950]]},
 {"ten": "", "rong": 4, "diem": [[150, 1090], [230, 1075], [300, 1065], [380, 1060]]},
 {"ten": "", "rong": 4, "diem": [[137, 1150], [200, 1140], [255, 1127], [330, 1150], [400, 1165]]},
]
TA = {"quang_nguyen": ([252, 615], "QUẢNG NGUYÊN", (0, 26)), "mon": ([302, 753], "MÔN", (-30, 0)), "quang_lang": ([399, 883], "QUANG LANG", (-70, 6)),
      "to_mau": ([600, 1010], "TÔ MẬU", (0, 26)), "vinh_an": ([765, 993], "VĨNH AN", (-50, -14)), "van_xuan": ([255, 1127], "VẠN XUÂN", (0, -24))}
TONG = {"thai_binh": ([562, 597], "Thái Bình", (12, 22)), "tu_minh": ([505, 758], "TƯ MINH", (50, 6)), "co_van": ([649, 876], "CỔ VẠN", (48, 0))}
THANH = {"ung_chau": ([882, 570], "UNG CHÂU", (58, 28)), "kham_chau": ([942, 830], "KHÂM CHÂU", (78, 4)), "liem_chau": ([1162, 958], "LIÊM CHÂU", (88, 2))}
dd = []
for k, (p, ten, l) in TA.items(): dd.append({"ten": ten, "vi_tri": p, "kieu": "diem", "nhan": [p[0] + l[0], p[1] + l[1]], "co": 12, "dam": True})
for k, (p, ten, l) in TONG.items(): dd.append({"ten": ten, "vi_tri": p, "kieu": "diem", "nhan": [p[0] + l[0], p[1] + l[1]], "co": 12})
for k, (p, ten, l) in THANH.items(): dd.append({"ten": ten, "vi_tri": p, "kieu": None, "nhan": [p[0] + l[0], p[1] + l[1]], "co": 13, "dam": True})
doi = {
 "a1": {"loai": "mui_ten_ta", "diem": [[297, 585], [397, 578], [507, 588]], "w0": 6, "w1": 11},
 "a2": {"loai": "mui_ten_ta", "diem": [[622, 585], [717, 560], [835, 566]], "w0": 6, "w1": 11},
 "a3": {"loai": "mui_ten_ta", "diem": [[392, 870], [427, 800], [487, 770]], "w0": 6, "w1": 11},
 "a4": {"loai": "mui_ten_ta", "diem": [[607, 995], [637, 950], [650, 900]], "w0": 6, "w1": 11},
 "a5": {"loai": "mui_ten_ta", "diem": [[790, 1050], [900, 1010], [935, 860]], "w0": 6, "w1": 11},
 "a6": {"loai": "mui_ten_ta", "diem": [[972, 845], [1060, 885], [1130, 940]], "w0": 6, "w1": 11},
 "a7": {"loai": "mui_ten_ta", "diem": [[950, 800], [928, 700], [900, 612]], "w0": 6, "w1": 11},
 "rut1": {"loai": "rut_lui", "diem": [[870, 600], [905, 700], [928, 790], [915, 900], [860, 990], [790, 1010]]},
 "rut2": {"loai": "rut_lui", "diem": [[540, 610], [440, 612], [320, 628]]},
 **{f"thanh_{k}": {"loai": "don_dich", "vi_tri": p} for k, (p, *_) in THANH.items()},
 **{f"sao_{k}": {"loai": "sao", "vi_tri": [p[0] + 30, p[1] - 30]} for k, (p, *_) in THANH.items()},
 "khung_nho": {"loai": "vong", "rong": 2.0, "diem": [ip(105.5, 23.3), ip(109.5, 23.3), ip(109.5, 21.2), ip(105.5, 21.2)]},
}
THANH_IDS = [f"thanh_{k}" for k in THANH]
S = {
 "phien_ban": 2, "ten": "Tiến công trước để tự vệ (1075)", "phu_de": "Lý Thường Kiệt chỉ huy hơn 10 vạn quân thuỷ, bộ",
 "nguon": "Vẽ lại, giản lược theo Hình 2, SGK Lịch sử và Địa lí 7, Bài 12, tr. 59; ô nhỏ: nền Natural Earth",
 "khung": [137, 330, 1290, 1200], "tam": [700, 780], "chu_giai_xy": [0.015, 0.55],
 "vung_mau": [{"diem": BIEN, "mau": [0.612, 0.765, 0.835], "vien": 1.6}] + inset(),
 "dat_noi": DAO, "song": SONG,
 "dia_danh": [{"ten": "TỐNG", "vi_tri": [847, 458], "lon": True, "co": 22}, {"ten": "ĐẠI VIỆT", "vi_tri": [412, 1006], "lon": True, "co": 22},
              {"ten": "VỊNH BẮC BỘ", "vi_tri": [960, 1120], "dam": True, "co": 15}, {"ten": "VIỆT NAM", "vi_tri": ip(105.3, 15.4), "co": 7, "dam": True}]
             + dd + dao_inset(112.0, 16.5, "QĐ. Hoàng Sa", 5, .5, (0, -15)) + dao_inset(114.0, 9.6, "QĐ. Trường Sa", 6, .8, (0, -20)),
 "chu_giai": [{"loai": "mui_ten_ta", "nhan": "Quân ta tiến công năm 1075"}, {"loai": "don_dich", "nhan": "Thành của quân Tống"},
              {"loai": "sao", "nhan": "Nơi quân ta giành chiến thắng"}, {"loai": "rut_lui", "nhan": "Quân ta rút về nước"}],
 "doi_tuong": doi,
 "pha": {
  "tien_cong": {"mo_dau": True, "zoom": [1.0, 1.02], "hien": ["khung_nho"] + THANH_IDS, "chu_giai": ["mui_ten_ta", "don_dich"],
                "moc": [{"chu": "Tháng 10 – 1075", "tu": 0.05, "den": 1.1}],
                "buoc": [{"id": "a1", "tu": 0.1, "den": 0.3}, {"id": "a3", "tu": 0.15, "den": 0.35}, {"id": "a4", "tu": 0.2, "den": 0.4},
                         {"id": "a5", "tu": 0.35, "den": 0.6}, {"id": "a6", "tu": 0.55, "den": 0.75}, {"id": "a2", "tu": 0.6, "den": 0.85}, {"id": "a7", "tu": 0.7, "den": 0.9}]},
  "ung_chau": {"zoom": [1.0, 1.03], "hien": ["khung_nho", "a1", "a2", "a3", "a4", "a5", "a6", "a7"] + THANH_IDS, "chu_giai": ["mui_ten_ta", "don_dich", "sao"],
               "moc": [{"chu": "Sau 42 ngày chiến đấu", "tu": 0.05, "den": 1.1}],
               "buoc": [{"id": "sao_kham_chau", "tu": 0.12, "den": 0.22}, {"id": "sao_liem_chau", "tu": 0.22, "den": 0.32}, {"id": "sao_ung_chau", "tu": 0.4, "den": 0.55},
                        {"id": "thanh_ung_chau", "tu": 0.55, "den": 0.7, "hieu_ung": "mat"}],
               "bang": {"chu": "Hạ thành Ung Châu, tiêu huỷ kho lương", "tu": 0.62, "y": 0.70}},
  "rut_ve": {"zoom": [1.03, 1.0], "hien": ["khung_nho", "a1", "a2", "a3", "a4", "a5", "a6", "a7"] + THANH_IDS + [f"sao_{k}" for k in THANH],
             "da_mat": ["thanh_ung_chau"], "chu_giai": ["mui_ten_ta", "sao", "rut_lui"],
             "moc": [{"chu": "Rút về chuẩn bị phòng tuyến", "tu": 0.05, "den": 1.1}],
             "buoc": [{"id": "rut1", "tu": 0.1, "den": 0.55}, {"id": "rut2", "tu": 0.3, "den": 0.65}]}
 }
}
json.dump(S, open(f"{ROOT}/pipeline/maps/specs/tien-cong-1075.json", "w"), ensure_ascii=False)
print("ok")
