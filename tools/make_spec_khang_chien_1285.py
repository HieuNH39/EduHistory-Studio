"""Sa bàn (saban2) 'Kháng chiến chống quân xâm lược Nguyên năm 1285'.
Sơ đồ minh hoạ, vẽ lại giản lược theo Hình 2 'Lược đồ cuộc kháng chiến chống quân Nguyên năm 1285',
SGK Lịch sử và Địa lí 7, Bài 14, tr. 70 (lời: tr. 70–71). Nền địa lí: Natural Earth 1:50m (phạm vi công cộng),
toạ độ x = (kinh độ − 102) × 100 × cos 15°, y = (23.5 − vĩ độ) × 100 (như tools/make_vn_map.py).
Vị trí Chương Dương – Hàm Tử – Tây Kết đặt giãn ra dọc sông Hồng (như lược đồ SGK) để đọc được khi phóng to.
Khung hình có vùng Biển Đông nơi có quần đảo Hoàng Sa → vẽ QĐ. Hoàng Sa đúng vị trí; thêm ô bản đồ nhỏ Việt Nam
(như lược đồ SGK) thể hiện cả quần đảo Hoàng Sa, Trường Sa.
Nhãn địa danh dùng chế độ 'man_hinh' (cỡ chữ cố định khi máy quay phóng to); tên sông là đối tượng 'nhan' màu nước,
chỉ hiện ở các pha nhìn toàn cảnh."""
import json, math, random, sys
sys.path.insert(0, "/home/claude/eduhistory-studio/tools")
from make_vn_map import xy, nen, ROOT
P = lambda lon, lat: xy(lon, lat)
W, H = 1920, 1080

# ---- khung và phép chiếu ra màn hình (giống SaBan2) – để đặt ô bản đồ nhỏ theo toạ độ màn hình
KHUNG = P(102.1, 23.45) + P(109.3, 16.2)
LECH_X = 0.06
_s = min(W * 0.96 / (KHUNG[2] - KHUNG[0]), H * 0.80 / (KHUNG[3] - KHUNG[1]))
_ox = (W - (KHUNG[2] - KHUNG[0]) * _s) / 2 - KHUNG[0] * _s + LECH_X * W
_oy = H * 0.02 - KHUNG[1] * _s
def man_hinh_ve_cuc_bo(sx, sy): return [round((sx - _ox) / _s, 1), round((sy - _oy) / _s, 1)]

# ---- ô bản đồ nhỏ Việt Nam (góc dưới trái, dưới chú giải – như lược đồ SGK đặt ô nhỏ góc dưới trái)
SX0, SY0, SX1, SY1 = 40, 600, 330, 880          # toạ độ màn hình 1080p
IX0, IY0 = man_hinh_ve_cuc_bo(SX0, SY0); IX1, IY1 = man_hinh_ve_cuc_bo(SX1, SY1)
LON0, LAT0 = 100.6, 24.2
KY = (IY1 - IY0) / 17.4                          # 24.2°B → 6.8°B
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
def o_nho():
    g = json.load(open(f"{ROOT}/assets/geo/ne_50m_dong_nam_a.geojson"))
    out = [{"diem": [[IX0, IY0], [IX1, IY0], [IX1, IY1], [IX0, IY1]], "mau": [0.80, 0.88, 0.93], "vien": 1.6}]
    for f in g["features"]:
        geo = f["geometry"]; polys = geo["coordinates"] if geo["type"] == "MultiPolygon" else [geo["coordinates"]]
        for poly in polys:
            pts = clip([ip(*c) for c in poly[0]], IX0, IY0, IX1, IY1)
            if len(pts) >= 3:
                out.append({"diem": [[round(x, 1), round(y, 1)] for x, y in pts],
                            "mau": [0.96, 0.89, 0.72] if f["properties"]["ADMIN"] == "Vietnam" else [0.88, 0.87, 0.83], "vien": 0.5})
    return out
def dao_o_nho(lon, lat, ten, n, r, lech):
    random.seed(int(lon * 100 + lat))
    pts = [ip(lon + random.uniform(-r, r), lat + random.uniform(-r, r)) for _ in range(n)]
    return [{"ten": "", "vi_tri": p, "kieu": "diem"} for p in pts] + \
           [{"ten": ten, "vi_tri": [ip(lon, lat)[0] + lech[0], ip(lon, lat)[1] + lech[1]], "co": 8, "dam": True}]

# ---- quần đảo Hoàng Sa trên bản đồ chính (đúng vị trí, nằm trong khung hình toàn cảnh)
def dao_chinh(lon, lat, ten, n=7, r=0.3, lech=(-14, -30)):
    random.seed(int(lon * 100 + lat))
    pts = [P(lon + random.uniform(-r, r), lat + random.uniform(-r, r)) for _ in range(n)]
    return [{"ten": "", "vi_tri": p, "kieu": "diem"} for p in pts] + \
           [{"ten": ten, "vi_tri": P(lon, lat), "man_hinh": True, "co": 17, "dam": True, "lech": list(lech), "zoom_den": 1.45}]

# ---- sông (vẽ lại giản lược, toạ độ kinh – vĩ độ)
def S(*pts): return [P(*p) for p in pts]
SONG = [
 {"ten": "", "rong": 2.6, "diem": S((102.9, 23.38), (103.45, 22.85), (103.97, 22.5), (104.15, 22.33), (104.4, 22.08), (104.62, 21.92), (104.85, 21.72),
                                    (105.08, 21.55), (105.25, 21.42), (105.42, 21.29), (105.5, 21.16), (105.68, 21.1), (105.86, 21.04), (105.89, 20.96),
                                    (105.92, 20.88), (105.97, 20.79), (106.03, 20.69), (106.09, 20.58), (106.16, 20.48), (106.24, 20.39), (106.36, 20.31),
                                    (106.48, 20.26), (106.6, 20.24))},
 {"ten": "", "rong": 1.8, "diem": S((102.35, 22.6), (102.7, 22.35), (103.15, 22.05), (103.55, 21.85), (103.95, 21.55), (104.2, 21.37), (104.55, 21.2),
                                    (104.9, 21.04), (105.15, 20.9), (105.32, 20.84), (105.38, 20.96), (105.37, 21.12), (105.42, 21.29))},
 {"ten": "", "rong": 1.6, "diem": S((104.95, 23.15), (105.03, 22.8), (105.12, 22.45), (105.2, 22.1), (105.22, 21.82), (105.17, 21.63), (105.26, 21.5),
                                    (105.33, 21.4), (105.42, 21.29))},
 {"ten": "", "rong": 1.4, "diem": S((104.3, 22.78), (104.5, 22.48), (104.72, 22.18), (104.93, 21.93), (105.08, 21.72), (105.17, 21.63))},
 {"ten": "", "rong": 1.6, "diem": S((103.25, 21.55), (103.75, 21.05), (104.1, 20.75), (104.6, 20.52), (104.95, 20.4), (105.2, 20.32), (105.45, 20.2),
                                    (105.62, 20.0), (105.78, 19.86), (105.9, 19.78))},
 {"ten": "", "rong": 1.6, "diem": S((103.9, 19.55), (104.4, 19.3), (104.9, 19.05), (105.3, 18.9), (105.5, 18.73), (105.74, 18.77))},
 {"ten": "", "rong": 1.3, "diem": S((105.85, 17.75), (106.1, 17.85), (106.3, 17.78), (106.46, 17.7))},
 {"ten": "", "rong": 1.2, "diem": S((106.7, 16.98), (106.9, 17.02), (107.08, 17.02))},
 # sông nhỏ không ghi tên (bối cảnh quanh Vạn Kiếp): sông Đuống, sông Thái Bình, sông Thương
 {"ten": "", "rong": 1.3, "diem": S((105.88, 21.06), (106.05, 21.05), (106.2, 21.07), (106.36, 21.1))},
 {"ten": "", "rong": 1.4, "diem": S((106.36, 21.1), (106.43, 20.96), (106.55, 20.82), (106.68, 20.68), (106.76, 20.6))},
 {"ten": "", "rong": 1.2, "diem": S((106.8, 21.85), (106.62, 21.6), (106.46, 21.32), (106.39, 21.14))},
]
def ten_song(lon, lat, chu, goc): return {"loai": "nhan", "vi_tri": P(lon, lat), "chu": chu, "co": 9.5, "mau": "chu_nuoc", "goc": goc}
TEN_SONG = {
 "ts_hong": ten_song(104.25, 22.05, "S. Hồng", 40), "ts_chay": ten_song(104.55, 22.3, "S. Chảy", 52), "ts_lo": ten_song(105.36, 22.2, "S. Lô", 78),
 "ts_da": ten_song(103.85, 21.4, "S. Đà", 35), "ts_ma": ten_song(104.5, 20.43, "S. Mã", 15), "ts_ca": ten_song(104.6, 19.07, "S. Cả", -22),
 "ts_gianh": ten_song(106.05, 17.98, "S. Gianh", -12), "ts_ben_hai": ten_song(106.78, 16.86, "S. Bến Hải", 0),
}
TS = list(TEN_SONG)

# ---- địa danh (tên ghi đúng như lược đồ SGK). man_hinh: cỡ chữ cố định trên màn hình
def vung(ten, lon, lat, **kw): return dict({"ten": ten, "vi_tri": P(lon, lat), "man_hinh": True, "co": 16, "dam": True, "lech": [0, 0]}, **kw)
def diem(ten, lon, lat, lech, **kw): return dict({"ten": ten, "vi_tri": P(lon, lat), "kieu": "diem", "man_hinh": True, "co": 18, "lech": lech}, **kw)
TL = (105.85, 21.03); VK = (106.38, 21.10); CD = (105.91, 20.88); HT = (105.96, 20.78); TK = (106.01, 20.68)
TT = (106.17, 20.45); BV = (105.78, 19.83); TV = (104.9, 21.8); PN = (105.25, 21.44)
DIA_DANH = [
 vung("QUY HOÁ", 103.7, 21.95, zoom_den=2.0), vung("ĐÀ GIANG", 103.0, 21.25, zoom_den=1.5), vung("TUYÊN HOÁ", 105.75, 22.5), vung("LẠNG CHÂU", 106.05, 21.8),
 vung("THANH HOÁ", 105.05, 19.72), vung("DIỄN CHÂU", 105.2, 19.2), vung("NGHỆ AN", 105.35, 18.5), vung("BỐ CHÍNH", 106.2, 17.45),
 vung("THUẬN CHÂU", 107.05, 16.55),
 vung("THIÊN TRƯỜNG", TT[0], TT[1], lech=[40, 4], co=17),
 vung("VỊNH BẮC BỘ", 107.8, 19.3, co=17, zoom_den=1.9),
 vung("BIỂN ĐÔNG", 110.6, 17.5, co=19, zoom_den=1.9),
 diem("THĂNG LONG", *TL, [-14, -6], co=21, dam=True),
 diem("Vạn Kiếp", *VK, [14, 14]),
 diem("Chương Dương", *CD, [-28, 0], zoom_tu=2.4),
 diem("Hàm Tử", *HT, [-28, 0], zoom_tu=2.4),
 diem("Tây Kết", *TK, [-28, 0], zoom_tu=2.4),
 diem("Bố Vệ", *BV, [12, 4]),
 diem("Thu Vật", *TV, [-12, -2], zoom_den=2.3),
 diem("Phù Ninh", *PN, [-12, 0], zoom_den=2.3),
] + dao_chinh(112.0, 16.5, "QĐ. Hoàng Sa")
O_NHO_DD = [{"ten": "VIỆT NAM", "vi_tri": ip(105.4, 15.6), "co": 7, "dam": True}, {"ten": "BIỂN ĐÔNG", "vi_tri": ip(112.6, 13.2), "co": 7}] \
    + dao_o_nho(112.0, 16.5, "QĐ. Hoàng Sa", 5, .5, (0, -16)) + dao_o_nho(114.0, 9.6, "QĐ. Trường Sa", 6, .8, (0, -22))

def A(*pts): return [P(*p) for p in pts]
doi = {
 **TEN_SONG,
 "khung_nho": {"loai": "vong", "rong": 1.6, "diem": [ip(102.1, 23.45), ip(109.3, 23.45), ip(109.3, 16.2), ip(102.1, 16.2)]},
 # 1. quân Nguyên tiến công từ biên giới phía Bắc (Thoát Hoan: hướng đông bắc qua Lạng Châu; một cánh theo sông Chảy – sông Hồng)
 "n_db1": {"loai": "mui_ten_dich", "diem": A((108.25, 22.12), (107.6, 22.0), (106.98, 21.86)), "w0": 4, "w1": 8},
 "n_db2": {"loai": "mui_ten_dich", "diem": A((106.95, 21.75), (106.75, 21.45), (106.5, 21.2)), "w0": 4, "w1": 8},
 "n_tb1": {"loai": "mui_ten_dich", "diem": A((104.25, 23.15), (104.72, 22.7), (105.0, 22.32)), "w0": 4, "w1": 8},
 "n_tb2": {"loai": "mui_ten_dich", "diem": A((105.08, 22.12), (105.38, 21.68), (105.72, 21.17)), "w0": 4, "w1": 8},
 "n_so": {"loai": "nhan", "vi_tri": P(108.25, 21.32), "chu": "Thoát Hoan – hơn 50 vạn quân", "co": 9, "mau": "dich"},
 # 2. quân Trần lui về Vạn Kiếp
 "l_vk": {"loai": "rut_lui", "diem": A((106.5, 21.88), (106.32, 21.52), (106.36, 21.17)), "w0": 4},
 # 3. quân Nguyên vào Thăng Long; nhà Trần rút từ Thăng Long về Thiên Trường ("vườn không nhà trống")
 "n_vk_tl": {"loai": "mui_ten_dich", "diem": A((106.3, 21.16), (106.1, 21.17), (105.93, 21.08)), "w0": 3, "w1": 6},
 "l_tl_tt": {"loai": "rut_lui", "diem": A((105.82, 20.97), (105.77, 20.76), (105.93, 20.6), (106.12, 20.52)), "w0": 4},
 "vktn": {"loai": "nhan", "vi_tri": P(105.1, 20.55), "chu": "“Vườn không nhà trống”", "co": 7, "mau": "ta"},
 # 4. kế hoạch hội quân của Toa Đô (từ Chăm-pa đánh ra) và Thoát Hoan ở Thiên Trường bị phá vỡ
 "td1": {"loai": "mui_ten_dich", "diem": A((108.1, 16.35), (107.6, 16.55), (107.12, 16.85)), "w0": 4, "w1": 8},
 "td2": {"loai": "mui_ten_dich", "diem": A((106.95, 16.95), (106.45, 17.5), (105.98, 18.18), (105.62, 18.85)), "w0": 4, "w1": 8},
 "td3": {"loai": "mui_ten_dich", "diem": A((105.55, 19.08), (105.62, 19.45), (105.74, 19.74)), "w0": 4, "w1": 8},
 "td4": {"loai": "mui_ten_dich", "diem": A((105.84, 19.9), (105.92, 20.0), (105.97, 20.08)), "w0": 3, "w1": 6},
 "td_nhan": {"loai": "nhan", "vi_tri": P(108.75, 17.0), "chu": "Toa Đô (từ Chăm-pa đánh ra)", "co": 9, "mau": "dich"},
 "th_tt": {"loai": "mui_ten_dich", "diem": A((106.0, 21.0), (106.2, 20.9), (106.28, 20.78)), "w0": 3, "w1": 6},
 "vong_tt": {"loai": "vong", "rong": 3.2, "diem": A((106.17, 20.6), (106.32, 20.45), (106.17, 20.3), (106.02, 20.45))},
 "ct_bac": {"loai": "mui_ten_ta", "diem": A((106.2, 20.58), (106.24, 20.68), (106.27, 20.76)), "w0": 3, "w1": 5.5},
 "ct_nam": {"loai": "mui_ten_ta", "diem": A((106.1, 20.33), (106.02, 20.22), (105.96, 20.12)), "w0": 3, "w1": 5.5},
 "bch_nhan": {"loai": "nhan", "vi_tri": P(106.95, 20.47), "chu": "Bộ chỉ huy kháng chiến", "co": 6.5, "mau": "ta"},
 "hq_nhan": {"loai": "nhan", "vi_tri": P(107.2, 20.0), "chu": "Phá vỡ kế hoạch hội quân", "co": 7, "mau": "ta"},
 # 5. quân Nguyên rút về Thăng Long (thiếu lương thực, bị động); tháng 5 – 1285 quân Trần phản công
 "n_ve_tl": {"loai": "rut_chay", "diem": A((106.33, 20.58), (106.3, 20.86), (106.15, 21.0), (105.97, 21.03)), "w0": 1.6},
 "tl_nhan": {"loai": "nhan", "vi_tri": P(106.7, 20.72), "chu": "Thiếu lương thực, bị động", "co": 3, "mau": "dich"},
 "p_tk": {"loai": "mui_ten_ta", "diem": A((106.21, 20.49), (106.12, 20.6), (106.035, 20.665)), "w0": 1.6, "w1": 3},
 "p_ht": {"loai": "mui_ten_ta", "diem": A((106.05, 20.7), (106.0, 20.745), (105.98, 20.77)), "w0": 1.5, "w1": 2.8},
 "p_cd": {"loai": "mui_ten_ta", "diem": A((106.0, 20.8), (105.955, 20.845), (105.93, 20.872)), "w0": 1.5, "w1": 2.8},
 "p_tl": {"loai": "mui_ten_ta", "diem": A((105.945, 20.9), (105.895, 20.97), (105.865, 21.015)), "w0": 1.5, "w1": 2.8},
 "p_vk": {"loai": "mui_ten_ta", "diem": A((106.33, 21.15), (106.12, 21.18), (105.88, 21.06)), "w0": 1.6, "w1": 3},
 "s_tk": {"loai": "sao", "vi_tri": P(*TK)}, "s_ht": {"loai": "sao", "vi_tri": P(*HT)}, "s_cd": {"loai": "sao", "vi_tri": P(*CD)},
 "s_tl": {"loai": "sao", "vi_tri": P(*TL)},
 "gp_nhan": {"loai": "nhan", "vi_tri": P(105.62, 21.14), "chu": "Giải phóng Thăng Long", "co": 3.2, "mau": "ta"},
 # 6. quân Nguyên rút chạy về nước; quân Trần truy kích
 "c_db": {"loai": "rut_chay", "diem": A((106.0, 21.12), (106.3, 21.42), (106.68, 21.8), (107.2, 22.3), (107.85, 22.75)), "w0": 4},
 "c_tb": {"loai": "rut_chay", "diem": A((105.72, 21.22), (105.42, 21.62), (105.12, 22.02), (104.8, 22.55), (104.45, 23.05)), "w0": 4},
 "t_lc": {"loai": "mui_ten_ta", "diem": A((106.05, 21.68), (106.3, 21.66), (106.55, 21.62)), "w0": 4, "w1": 7.5},
 "t_tv": {"loai": "mui_ten_ta", "diem": A((104.52, 21.42), (104.6, 21.56), (104.72, 21.66)), "w0": 4, "w1": 7.5},
 "t_pn": {"loai": "mui_ten_ta", "diem": A((104.98, 21.1), (105.08, 21.24), (105.19, 21.32)), "w0": 4, "w1": 7.5},
}
DA_VE_1 = ["n_db1", "n_db2", "n_tb1", "n_tb2", "l_vk"]
S_SPEC = {
 "phien_ban": 2, "ten": "Kháng chiến năm 1285", "phu_de": "Chống quân xâm lược Nguyên",
 "nguon": "Sơ đồ minh hoạ theo Lược đồ Hình 2 SGK, tr. 70 · nền Natural Earth",
 "khung": KHUNG, "lech_x": LECH_X, "nen_bien": [0.80, 0.88, 0.93], "sao_man_hinh": True,
 "vung_mau": nen([94, 12, 114, 26]) + o_nho(),
 "song": SONG,
 "dia_danh": DIA_DANH + O_NHO_DD,
 "chu_giai": [
  {"loai": "mui_ten_dich", "nhan": "Quân Nguyên tiến công"},
  {"loai": "rut_lui", "nhan": "Quân Trần rút lui"},
  {"loai": "vong", "nhan": "Bảo vệ bộ chỉ huy kháng chiến"},
  {"loai": "mui_ten_ta", "nhan": "Quân Trần phản công"},
  {"loai": "sao", "nhan": "Nơi quân Trần chiến thắng"},
  {"loai": "rut_chay", "nhan": "Quân Nguyên rút chạy"},
 ],
 "doi_tuong": doi,
 "pha": {
  # Cảnh 12 – Tháng 1 – 1285: hơn 50 vạn quân Nguyên do Thoát Hoan chỉ huy tràn vào; Trần Quốc Tuấn lui quân về Vạn Kiếp
  # (bước khớp lời: câu 1 ≈ u 0–0,5, câu 2 ≈ u 0,5–0,93; không dùng mo_dau để nhãn không hiện trên nền giấy trống)
  "tien_cong": {"zoom": [1.55, 1.7], "tam": P(105.55, 21.85), "can_giua": [0.55, 0.45], "hien": TS, "chu_giai": ["mui_ten_dich", "rut_lui"],
                "moc": [{"chu": "Tháng 1 – 1285", "tu": 0.03, "den": 1.1}],
                "buoc": [{"id": "n_db1", "tu": 0.05, "den": 0.22}, {"id": "n_tb1", "tu": 0.08, "den": 0.25}, {"id": "n_so", "tu": 0.18, "den": 0.3},
                         {"id": "n_db2", "tu": 0.22, "den": 0.38}, {"id": "n_tb2", "tu": 0.25, "den": 0.42}, {"id": "l_vk", "tu": 0.55, "den": 0.8}]},
  # Cảnh 14 – "vườn không nhà trống", rút từ Thăng Long về Thiên Trường; quân Nguyên vào Thăng Long (một câu ≈ u 0–0,9)
  "rut_lui": {"zoom": [1.9, 2.3], "tam": P(105.98, 20.78), "can_giua": [0.58, 0.45], "hien": DA_VE_1,
              "chu_giai": ["mui_ten_dich", "rut_lui"],
              "buoc": [{"id": "vktn", "tu": 0.15, "den": 0.28}, {"id": "l_tl_tt", "tu": 0.38, "den": 0.72}, {"id": "n_vk_tl", "tu": 0.6, "den": 0.8}]},
  # Cảnh 16 – kế hoạch hội quân của Toa Đô (từ Chăm-pa đánh ra) và Thoát Hoan tại vùng Thiên Trường bị phá vỡ
  # (câu 1 ≈ u 0–0,38: toàn cảnh, có QĐ. Hoàng Sa và ô bản đồ nhỏ; câu 2 ≈ u 0,38–0,95: máy quay tiến vào Thiên Trường)
  "hoi_quan": {"zoom": [1.0, 1.7], "tam": P(*TT), "can_giua": [0.58, 0.5], "hien": ["khung_nho"] + DA_VE_1 + ["n_vk_tl", "l_tl_tt"] + TS,
               "chu_giai": ["mui_ten_dich", "rut_lui", "vong", "mui_ten_ta"],
               "buoc": [{"id": "td1", "tu": 0.04, "den": 0.12}, {"id": "td_nhan", "tu": 0.05, "den": 0.14}, {"id": "td2", "tu": 0.11, "den": 0.22},
                        {"id": "td3", "tu": 0.2, "den": 0.26}, {"id": "td4", "tu": 0.25, "den": 0.31}, {"id": "th_tt", "tu": 0.26, "den": 0.34},
                        {"id": "vong_tt", "tu": 0.45, "den": 0.58},
                        {"id": "ct_bac", "tu": 0.62, "den": 0.7}, {"id": "ct_nam", "tu": 0.62, "den": 0.7}, {"id": "hq_nhan", "tu": 0.7, "den": 0.8}]},
  # Cảnh 17 – quân Nguyên rút về Thăng Long (thiếu lương thực, bị động); tháng 5 – 1285 quân Trần phản công: Tây Kết, Hàm Tử,
  # Chương Dương, giải phóng Thăng Long (câu 1 ≈ u 0–0,42; câu 2 ≈ u 0,42–0,95, tên các trận ≈ u 0,69 / 0,72 / 0,77, Thăng Long ≈ 0,88)
  "phan_cong": {"zoom": [4.2, 4.7], "tam": P(106.02, 20.8), "can_giua": [0.55, 0.47], "hien": [],
                "chu_giai": ["rut_chay", "mui_ten_ta", "sao"],
                "moc": [{"chu": "Tháng 5 – 1285", "tu": 0.43, "den": 1.1}],
                "buoc": [{"id": "n_ve_tl", "tu": 0.05, "den": 0.22}, {"id": "tl_nhan", "tu": 0.15, "den": 0.27},
                         {"id": "p_tk", "tu": 0.52, "den": 0.66}, {"id": "s_tk", "tu": 0.66, "den": 0.71},
                         {"id": "p_ht", "tu": 0.69, "den": 0.73}, {"id": "s_ht", "tu": 0.72, "den": 0.76},
                         {"id": "p_cd", "tu": 0.75, "den": 0.79}, {"id": "s_cd", "tu": 0.78, "den": 0.82},
                         {"id": "p_vk", "tu": 0.8, "den": 0.88}, {"id": "p_tl", "tu": 0.82, "den": 0.88}, {"id": "s_tl", "tu": 0.88, "den": 0.93},
                         {"id": "gp_nhan", "tu": 0.88, "den": 0.95}]},
  # Cảnh 18 – quân giặc rút chạy về nước, kháng chiến thắng lợi (một câu ≈ u 0–0,65)
  "rut_chay": {"zoom": [2.2, 1.6], "tam": P(105.6, 21.7), "can_giua": [0.6, 0.45],
               "hien": ["p_tk", "p_ht", "p_cd", "p_tl", "p_vk", "s_tk", "s_ht", "s_cd", "s_tl"] + TS,
               "chu_giai": ["mui_ten_ta", "sao", "rut_chay"],
               "buoc": [{"id": "c_db", "tu": 0.05, "den": 0.4}, {"id": "c_tb", "tu": 0.08, "den": 0.42},
                        {"id": "t_lc", "tu": 0.3, "den": 0.45}, {"id": "t_tv", "tu": 0.33, "den": 0.48}, {"id": "t_pn", "tu": 0.35, "den": 0.5}],
               "bang": {"chu": "Kháng chiến năm 1285 thắng lợi", "tu": 0.5, "y": 0.62}},
 }
}
json.dump(S_SPEC, open(f"{ROOT}/pipeline/maps/specs/khang-chien-1285.json", "w"), ensure_ascii=False)
print("ok", len(S_SPEC["vung_mau"]), "s=%.3f" % _s, "o_nho cục bộ", IX0, IY0, IX1, IY1)
