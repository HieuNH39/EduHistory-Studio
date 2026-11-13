"""Sa bàn chiến dịch Việt Bắc thu – đông 1947 và chiến dịch Biên giới thu – đông 1950 (saban2).
Vẽ lại, giản lược theo Hình 14.5 và Hình 14.7, SGK Lịch sử và Địa lí 9, tr. 71 – 72; diễn biến theo nội dung tr. 70 – 72.
Toạ độ địa danh là vị trí gần đúng; nền bản đồ Natural Earth 1:50m. Như lược đồ SGK, có ô bản đồ nhỏ Việt Nam
thể hiện quần đảo Hoàng Sa, Trường Sa (vì khung hình có một phần Vịnh Bắc Bộ)."""
import json, sys, copy
sys.path.insert(0, "/home/claude/eduhistory-studio/tools")
from make_vn_map import xy, nen, ROOT, VN_MAU, LANG_GIENG
P = lambda lon, lat: xy(lon, lat)
W, H = 1920, 1080
KHUNG = P(104.6, 23.65) + P(108.2, 20.55)
x0, y0, x1, y1 = KHUNG
s = min(W * 0.96 / (x1 - x0), H * 0.80 / (y1 - y0)); ox = (W - (x1 - x0) * s) / 2 - x0 * s; oy = H * 0.02 - y0 * s
def M(X, Y): return [round((X - ox) / s, 1), round((Y - oy) / s, 1)]   # toạ độ màn hình 1920×1080 → toạ độ bản đồ

def o_nho(X0, Y0, X1, Y1):
    """Ô bản đồ nhỏ Việt Nam (có Hoàng Sa, Trường Sa) đặt trong hộp màn hình (X0, Y0)–(X1, Y1)."""
    bb = (101.5, 7.5, 117.5, 23.8)   # kinh độ, vĩ độ của ô nhỏ
    A, B = xy(bb[0], bb[3]), xy(bb[2], bb[1]); sc = min((X1 - X0) / (B[0] - A[0]), (Y1 - Y0) / (B[1] - A[1]))
    def T(p): return M(X0 + (p[0] - A[0]) * sc, Y0 + (p[1] - A[1]) * sc)
    def T2(lon, lat): return T(xy(lon, lat))
    vung = [{"diem": [M(X0, Y0), M(X1, Y0), M(X1, Y1), M(X0, Y1)], "mau": [0.80, 0.88, 0.93], "vien": 2.0}]
    for v in nen([bb[0], bb[1], bb[2], bb[3]]):
        pts = [T(p) for p in v["diem"]]
        vung.append({"diem": pts, "mau": v["mau"], "vien": 0.6})
    import random; random.seed(7); dd = []
    for lon, lat, ten, n, r in ((112.0, 16.5, "QĐ. Hoàng Sa", 4, 0.5), (114.0, 9.8, "QĐ. Trường Sa", 6, 0.9)):
        for _ in range(n):
            dd.append({"ten": "", "vi_tri": T2(lon + random.uniform(-r, r), lat + random.uniform(-r, r)), "kieu": "diem", "man_hinh": True, "lech": [0, 0]})
        dd.append({"ten": ten, "vi_tri": T2(lon, lat), "man_hinh": True, "lech": [0, -20], "co": 13})
    dd.append({"ten": "Hà Nội", "vi_tri": T2(105.85, 21.03), "kieu": "diem", "man_hinh": True, "lech": [8, 0], "co": 12})
    dd.append({"ten": "VIỆT NAM", "vi_tri": T2(108.6, 14.2), "man_hinh": True, "lech": [0, 0], "co": 12})
    dd.append({"ten": "BIỂN ĐÔNG", "vi_tri": T2(113.6, 13.1), "man_hinh": True, "lech": [0, 0], "co": 12})
    return vung, dd

D = {"ha_noi": (105.85, 21.03), "phu_tho": (105.22, 21.40), "doan_hung": (105.18, 21.62), "tuyen_quang": (105.22, 21.82),
     "khe_lau": (105.27, 21.89), "chiem_hoa": (105.27, 22.15), "cho_don": (105.58, 22.18), "cho_chu": (105.65, 21.90),
     "dai_tu": (105.64, 21.63), "thai_nguyen": (105.84, 21.59), "cho_moi": (105.78, 21.87), "bac_kan": (105.83, 22.15),
     "ngan_son": (105.98, 22.43), "cao_bang": (106.26, 22.67), "dong_khe": (106.43, 22.43), "that_khe": (106.47, 22.25),
     "bong_lau": (106.45, 22.36), "na_sam": (106.62, 22.05), "lang_son": (106.76, 21.85), "dinh_lap": (107.10, 21.54),
     "an_chau": (106.85, 21.33), "bac_giang": (106.20, 21.27), "vinh_yen": (105.60, 21.31), "hai_duong": (106.33, 20.94),
     "hai_phong": (106.68, 20.86), "hon_gai": (107.08, 20.95), "mong_cai": (107.97, 21.53), "ha_giang": (104.98, 22.82),
     "hoa_binh": (105.34, 20.82)}
Q = lambda k: P(*D[k])
def dd(k, ten, lech, co=19, dam=False): return {"ten": ten, "vi_tri": Q(k), "kieu": "diem", "man_hinh": True, "lech": lech, "co": co, "dam": dam}
L = lambda *pts: [P(*p) for p in pts]
SONG = [{"diem": L((104.98, 22.82), (105.10, 22.30), (105.22, 21.85), (105.18, 21.62), (105.43, 21.30)), "rong": 3.5, "ten": "S. Lô", "nhan": P(105.0, 22.35), "goc": -70},
        {"diem": L((105.33, 22.95), (105.27, 22.40), (105.27, 22.15), (105.26, 21.90)), "rong": 3.0, "ten": "S. Gâm", "nhan": P(105.40, 22.55), "goc": -80},
        {"diem": L((104.60, 22.10), (104.87, 21.72), (105.43, 21.30), (105.85, 21.06), (106.05, 20.75), (106.25, 20.45)), "rong": 4.5, "ten": "S. Hồng", "nhan": P(105.98, 20.72), "goc": -60},
        {"diem": L((105.83, 22.25), (105.84, 21.62), (106.05, 21.25), (106.35, 21.10)), "rong": 2.6}]
INSET_V, INSET_D = o_nho(40, 215, 300, 590)
BASE = {
 "phien_ban": 2, "khung": KHUNG, "nen_bien": [0.80, 0.88, 0.93], "chu_giai_xy": [0.69, 0.60], "sao_man_hinh": True,
 "vung_mau": nen([102, 19, 110, 25]) + INSET_V, "song": SONG,
 "dia_danh": INSET_D + [
  dd("ha_noi", "HÀ NỘI", [14, 10], 21, True), dd("thai_nguyen", "Thái Nguyên", [12, -4]), dd("tuyen_quang", "Tuyên Quang", [-12, 6]),
  dd("bac_kan", "Bắc Kạn", [12, -6]), dd("cao_bang", "CAO BẰNG", [12, -14], 21, True), dd("lang_son", "LẠNG SƠN", [14, 6], 21, True),
  dd("that_khe", "Thất Khê", [14, 4]), dd("phu_tho", "Phú Thọ", [-12, 8]), dd("vinh_yen", "Vĩnh Yên", [10, 14]),
  dd("bac_giang", "Bắc Giang", [10, 14]), dd("ha_giang", "Hà Giang", [12, -6]),
  {"ten": "TRUNG QUỐC", "vi_tri": P(107.6, 22.35), "lon": True, "man_hinh": True, "lech": [0, 0], "co": 26},
  {"ten": "Vịnh Bắc Bộ", "vi_tri": P(107.35, 20.72), "man_hinh": True, "lech": [0, 0], "co": 20}
 ],
}

# ---------------------------------------------------------------- Việt Bắc thu – đông 1947 (Hình 14.5; tr. 70 – 71)
A = copy.deepcopy(BASE)
A.update({"ten": "Việt Bắc thu – đông 1947", "phu_de": "Tháng 10 – 12 – 1947",
          "nguon": "Vẽ lại, giản lược theo Hình 14.5, SGK Lịch sử và Địa lí 9, tr. 71; nền Natural Earth"})
A["dia_danh"] = A["dia_danh"] + [dd("doan_hung", "Đoan Hùng", [-12, 8], 19, True), dd("khe_lau", "Khe Lau", [-12, -4], 19, True),
  dd("cho_don", "Chợ Đồn", [-12, -8]), dd("cho_moi", "Chợ Mới", [12, 4]), dd("chiem_hoa", "Chiêm Hoá", [-12, -6]),
  dd("ngan_son", "Ngân Sơn", [12, -4]), dd("dai_tu", "Đại Từ", [-10, 10])]
A["chu_giai"] = [{"loai": "mui_ten_dich", "nhan": "Hướng tiến công của quân Pháp"}, {"loai": "mui_ten_ta", "nhan": "Quân ta tiến công, chặn đánh"},
                 {"loai": "rut_chay", "nhan": "Quân Pháp rút chạy"}, {"loai": "sao", "nhan": "Thắng lợi lớn"}]
du = lambda k, n=0.32: {"loai": "mui_ten_dich", "diem": [P(D[k][0], D[k][1] + n), P(D[k][0], D[k][1] + 0.05)], "w0": 4, "w1": 8}
A["doi_tuong"] = {
 "du_bk": du("bac_kan"), "du_cd": du("cho_don"), "du_cm": du("cho_moi"),
 "n_du": {"loai": "nhan", "vi_tri": P(105.70, 22.62), "chu": "Quân Pháp nhảy dù", "co": 13, "mau": "dich"},
 "d_ls": {"loai": "mui_ten_dich", "diem": L((106.76, 21.88), (106.60, 22.08), (106.47, 22.28), (106.30, 22.60)), "w0": 4, "w1": 8},
 "d_cb": {"loai": "mui_ten_dich", "diem": L((106.22, 22.64), (105.98, 22.45), (105.86, 22.20)), "w0": 4, "w1": 8},
 "d_lo": {"loai": "mui_ten_dich", "diem": L((105.80, 21.08), (105.30, 21.36), (105.17, 21.62), (105.23, 21.86), (105.27, 22.11)), "w0": 4, "w1": 8},
 "d_cc": {"loai": "mui_ten_dich", "diem": L((105.58, 22.14), (105.66, 21.92), (105.64, 21.67)), "w0": 4, "w1": 7},
 "d_cm": {"loai": "mui_ten_dich", "diem": L((105.83, 22.11), (105.79, 21.91)), "w0": 4, "w1": 7},
 "t_bl": {"loai": "mui_ten_ta", "diem": L((106.05, 22.25), (106.25, 22.32), (106.41, 22.36)), "w0": 7, "w1": 12},
 "s_bl": {"loai": "sao", "vi_tri": Q("bong_lau")}, "n_bl": {"loai": "nhan", "vi_tri": P(106.92, 22.45), "chu": "Bản Sao – đèo Bông Lau", "co": 13, "mau": "ta"},
 "n_d4": {"loai": "nhan", "vi_tri": P(106.95, 22.12), "chu": "Đường số 4", "co": 12, "mau": "chu"},
 "t_dh": {"loai": "mui_ten_ta", "diem": L((104.85, 21.50), (105.02, 21.58), (105.15, 21.62)), "w0": 7, "w1": 12}, "s_dh": {"loai": "sao", "vi_tri": Q("doan_hung")},
 "t_kl": {"loai": "mui_ten_ta", "diem": L((104.95, 21.98), (105.12, 21.93), (105.24, 21.89)), "w0": 7, "w1": 12}, "s_kl": {"loai": "sao", "vi_tri": Q("khe_lau")},
 "n_lo": {"loai": "nhan", "vi_tri": P(104.75, 21.25), "chu": "Phục kích trên sông Lô", "co": 13, "mau": "ta"},
 "t_cd": {"loai": "mui_ten_ta", "diem": L((105.40, 21.98), (105.50, 22.08), (105.56, 22.15)), "w0": 6, "w1": 10},
 "t_bk": {"loai": "mui_ten_ta", "diem": L((106.15, 22.00), (106.00, 22.10), (105.88, 22.14)), "w0": 6, "w1": 10},
 "r_cb": {"loai": "rut_chay", "diem": L((106.30, 22.62), (106.42, 22.45), (106.46, 22.30)), "w0": 4},
 "r_tq": {"loai": "rut_chay", "diem": L((105.24, 21.78), (105.20, 21.60), (105.55, 21.35)), "w0": 4},
 "r_tn": {"loai": "rut_chay", "diem": L((105.84, 21.55), (105.86, 21.30), (105.86, 21.10)), "w0": 4},
}
DICH = ["du_bk", "du_cd", "du_cm", "n_du", "d_ls", "d_cb", "d_lo", "d_cc", "d_cm"]
A["pha"] = {
 "am_muu": {"mo_dau": True, "zoom": [1.0, 1.05], "chu_giai": ["mui_ten_dich"], "moc": [{"chu": "10 – 1947: khoảng 12 000 quân Pháp", "tu": 0.04, "den": 0.98}],
   "buoc": [{"id": "du_bk", "tu": 0.22, "den": 0.3}, {"id": "du_cd", "tu": 0.24, "den": 0.32}, {"id": "du_cm", "tu": 0.26, "den": 0.34}, {"id": "n_du", "tu": 0.28, "den": 0.36},
            {"id": "d_ls", "tu": 0.42, "den": 0.62}, {"id": "d_cb", "tu": 0.5, "den": 0.68}, {"id": "d_lo", "tu": 0.55, "den": 0.82}, {"id": "d_cc", "tu": 0.6, "den": 0.78}, {"id": "d_cm", "tu": 0.62, "den": 0.75}]},
 "huong_dong": {"zoom": [1.04, 1.07], "chu_giai": ["mui_ten_dich", "mui_ten_ta", "sao"], "hien": DICH, "moc": [{"chu": "Hướng đông: Đường số 4", "tu": 0.04, "den": 0.98}],
   "buoc": [{"id": "n_d4", "tu": 0.08, "den": 0.16}, {"id": "t_bl", "tu": 0.25, "den": 0.5}, {"id": "s_bl", "tu": 0.52, "den": 0.6}, {"id": "n_bl", "tu": 0.54, "den": 0.62}]},
 "huong_tay": {"zoom": [1.04, 1.07], "chu_giai": ["mui_ten_dich", "mui_ten_ta", "sao"], "hien": DICH + ["n_d4", "t_bl", "s_bl", "n_bl"], "moc": [{"chu": "Hướng tây: sông Lô", "tu": 0.04, "den": 0.98}],
   "buoc": [{"id": "n_lo", "tu": 0.12, "den": 0.2}, {"id": "t_dh", "tu": 0.25, "den": 0.45}, {"id": "s_dh", "tu": 0.45, "den": 0.52}, {"id": "t_kl", "tu": 0.55, "den": 0.75}, {"id": "s_kl", "tu": 0.75, "den": 0.82},
            {"id": "t_cd", "tu": 0.6, "den": 0.75}, {"id": "t_bk", "tu": 0.62, "den": 0.78}]},
 "ket_qua": {"zoom": [1.0, 1.04], "chu_giai": ["mui_ten_ta", "rut_chay", "sao"], "hien": ["t_bl", "s_bl", "n_bl", "t_dh", "s_dh", "t_kl", "s_kl", "n_lo", "t_cd", "t_bk"],
   "moc": [{"chu": "Tháng 12 – 1947", "tu": 0.04, "den": 0.98}],
   "buoc": [{"id": "r_cb", "tu": 0.1, "den": 0.35}, {"id": "r_tq", "tu": 0.15, "den": 0.4}, {"id": "r_tn", "tu": 0.2, "den": 0.45}],
   "bang": {"chu": "Cơ quan đầu não kháng chiến an toàn", "tu": 0.55, "y": 0.45}},
}
json.dump(A, open(f"{ROOT}/pipeline/maps/specs/viet-bac-1947.json", "w"), ensure_ascii=False)

# ---------------------------------------------------------------- Biên giới thu – đông 1950 (Hình 14.7; tr. 71 – 72)
B = copy.deepcopy(BASE)
B.update({"ten": "Biên giới thu – đông 1950", "phu_de": "Tháng 9 – 10 – 1950",
          "nguon": "Vẽ lại, giản lược theo Hình 14.7, SGK Lịch sử và Địa lí 9, tr. 72; nền Natural Earth"})
B["dia_danh"] = B["dia_danh"] + [dd("dong_khe", "Đông Khê", [-14, -4], 20, True), dd("na_sam", "Na Sầm", [-12, 0]),
  dd("dinh_lap", "Đình Lập", [12, -4]), dd("an_chau", "An Châu", [10, 12]), dd("hai_duong", "Hải Dương", [0, 18]),
  dd("hai_phong", "Hải Phòng", [12, 10]), dd("hon_gai", "Hòn Gai", [12, 8]), dd("hoa_binh", "Hoà Bình", [-12, 8]), dd("mong_cai", "Móng Cái", [-12, -10])]
B["chu_giai"] = [{"loai": "don_dich", "nhan": "Cứ điểm của Pháp"}, {"loai": "tran_tuyen", "nhan": "Hành lang Đông – Tây"},
                 {"loai": "mui_ten_ta", "nhan": "Quân ta tấn công"}, {"loai": "chan_danh", "nhan": "Quân ta chặn đánh"},
                 {"loai": "mui_ten_dich", "nhan": "Quân Pháp tiến đánh"}, {"loai": "rut_chay", "nhan": "Quân Pháp rút chạy"}]
B["doi_tuong"] = {
 "f_cb": {"loai": "don_dich", "vi_tri": Q("cao_bang")}, "f_dk": {"loai": "don_dich", "vi_tri": Q("dong_khe")},
 "f_tk": {"loai": "don_dich", "vi_tri": Q("that_khe")}, "f_ns": {"loai": "don_dich", "vi_tri": Q("na_sam")}, "f_ls": {"loai": "don_dich", "vi_tri": Q("lang_son")},
 "n_d4": {"loai": "nhan", "vi_tri": P(107.05, 22.18), "chu": "Đường số 4", "co": 14, "mau": "dich"},
 "hanh_lang": {"loai": "tran_tuyen", "diem": L((105.34, 20.82), (105.60, 20.95), (105.85, 21.03), (106.10, 20.98), (106.33, 20.94), (106.70, 20.92), (107.05, 20.97))},
 "n_hl": {"loai": "nhan", "vi_tri": P(106.45, 20.70), "chu": "Hành lang Đông – Tây", "co": 14, "mau": "dich"},
 "t_dk1": {"loai": "mui_ten_ta", "diem": L((106.05, 22.30), (106.25, 22.36), (106.40, 22.42)), "w0": 8, "w1": 14},
 "t_dk2": {"loai": "mui_ten_ta", "diem": L((106.62, 22.75), (106.52, 22.58), (106.45, 22.46)), "w0": 7, "w1": 12},
 "s_dk": {"loai": "sao", "vi_tri": Q("dong_khe")},
 "d_tk": {"loai": "mui_ten_dich", "diem": L((106.47, 22.27), (106.45, 22.34), (106.43, 22.40)), "w0": 4, "w1": 8},
 "r_cb": {"loai": "rut_chay", "diem": L((106.27, 22.63), (106.36, 22.53), (106.42, 22.46)), "w0": 4},
 "c1": {"loai": "chan_danh", "vi_tri": P(106.33, 22.56), "goc": 40}, "c2": {"loai": "chan_danh", "vi_tri": P(106.48, 22.33), "goc": 80},
 "n_mp": {"loai": "nhan", "vi_tri": P(105.55, 22.62), "chu": "Mai phục, chặn đánh trên Đường số 4", "co": 13, "mau": "ta"},
 "r_d4": {"loai": "rut_chay", "diem": L((106.47, 22.22), (106.60, 22.05), (106.75, 21.88), (107.05, 21.58), (106.88, 21.36), (106.35, 21.28)), "w0": 4},
 "t_d4a": {"loai": "mui_ten_ta", "diem": L((106.15, 22.10), (106.30, 22.18), (106.44, 22.24)), "w0": 6, "w1": 10},
 "t_d4b": {"loai": "mui_ten_ta", "diem": L((106.35, 21.95), (106.50, 22.00), (106.60, 22.04)), "w0": 6, "w1": 10},
 "s_cb": {"loai": "sao", "vi_tri": Q("cao_bang")}, "s_tk": {"loai": "sao", "vi_tri": Q("that_khe")}, "s_ls": {"loai": "sao", "vi_tri": Q("lang_son")},
}
F = ["f_cb", "f_dk", "f_tk", "f_ns", "f_ls"]
B["pha"] = {
 "ro_ve": {"mo_dau": True, "zoom": [1.0, 1.05], "chu_giai": ["don_dich", "tran_tuyen"], "moc": [{"chu": "1950: Kế hoạch Rơ-ve", "tu": 0.04, "den": 0.98}],
   "buoc": [{"id": k, "tu": 0.2 + 0.04 * i, "den": 0.26 + 0.04 * i} for i, k in enumerate(F)] + [{"id": "n_d4", "tu": 0.38, "den": 0.46},
            {"id": "hanh_lang", "tu": 0.55, "den": 0.8}, {"id": "n_hl", "tu": 0.78, "den": 0.86}]},
 "dong_khe": {"zoom": [1.03, 1.07], "chu_giai": ["don_dich", "mui_ten_ta", "sao"], "hien": F + ["n_d4", "hanh_lang", "n_hl"], "moc": [{"chu": "Giữa tháng 9 – 1950: Đông Khê", "tu": 0.04, "den": 0.98}],
   "buoc": [{"id": "t_dk1", "tu": 0.15, "den": 0.45}, {"id": "t_dk2", "tu": 0.18, "den": 0.48}, {"id": "f_dk", "tu": 0.5, "den": 0.62, "hieu_ung": "mat"}, {"id": "s_dk", "tu": 0.6, "den": 0.7}]},
 "duong_so_4": {"zoom": [1.03, 1.07], "chu_giai": ["mui_ten_dich", "rut_chay", "chan_danh"], "hien": F + ["n_d4", "hanh_lang", "n_hl", "s_dk"], "da_mat": ["f_dk"],
   "moc": [{"chu": "Đường số 4", "tu": 0.04, "den": 0.98}],
   "buoc": [{"id": "d_tk", "tu": 0.1, "den": 0.35}, {"id": "r_cb", "tu": 0.15, "den": 0.4}, {"id": "c1", "tu": 0.5, "den": 0.6}, {"id": "c2", "tu": 0.55, "den": 0.65}, {"id": "n_mp", "tu": 0.6, "den": 0.7}]},
 "giai_phong": {"zoom": [1.0, 1.04], "chu_giai": ["mui_ten_ta", "rut_chay", "sao"], "hien": F + ["n_d4", "hanh_lang", "n_hl", "s_dk", "c1", "c2"], "da_mat": ["f_dk"],
   "moc": [{"chu": "Tháng 10 – 1950", "tu": 0.04, "den": 0.98}],
   "buoc": [{"id": "t_d4a", "tu": 0.08, "den": 0.3}, {"id": "t_d4b", "tu": 0.1, "den": 0.32}, {"id": "r_d4", "tu": 0.2, "den": 0.55},
            {"id": "f_cb", "tu": 0.3, "den": 0.4, "hieu_ung": "mat"}, {"id": "f_tk", "tu": 0.35, "den": 0.45, "hieu_ung": "mat"}, {"id": "f_ns", "tu": 0.4, "den": 0.5, "hieu_ung": "mat"},
            {"id": "f_ls", "tu": 0.45, "den": 0.55, "hieu_ung": "mat"}, {"id": "s_cb", "tu": 0.5, "den": 0.6}, {"id": "s_tk", "tu": 0.52, "den": 0.62}, {"id": "s_ls", "tu": 0.55, "den": 0.65}],
   "bang": {"chu": "Giải phóng vùng biên giới", "tu": 0.68, "y": 0.45}},
}
json.dump(B, open(f"{ROOT}/pipeline/maps/specs/bien-gioi-1950.json", "w"), ensure_ascii=False)
print("ok viet-bac-1947, bien-gioi-1950", len(BASE["vung_mau"]))
