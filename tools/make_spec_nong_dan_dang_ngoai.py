"""Sinh sa bàn (saban2) 'nong-dan-dang-ngoai': một số cuộc khởi nghĩa lớn của phong trào nông dân Đàng Ngoài thế kỉ XVIII.
Vẽ lại, giản lược theo Hình 7.1 (SGK LSĐL 8, tr. 32) và bảng tóm tắt tr. 33. Nền đất liền Natural Earth; sông vẽ tay giản lược.
Pha mở đầu là toàn cảnh Việt Nam có quần đảo Hoàng Sa, Trường Sa, sau đó máy quay tiến vào miền Bắc.
Địa danh đương thời (trấn) viết như SGK; địa danh ngày nay theo đúng chú thích của SGK."""
import json, sys, random
sys.path.insert(0, "/home/claude/eduhistory-studio/tools")
from make_vn_map import xy, nen, ROOT
P = lambda lon, lat: xy(lon, lat)

def dao2(lon, lat, ten, n=7, r=0.35, lech=(0, -30)):
    random.seed(int(lon * 100 + lat))
    pts = [[lon + random.uniform(-r, r), lat + random.uniform(-r, r)] for _ in range(n)]
    return [{"ten": "", "vi_tri": P(*p), "kieu": "diem", "man_hinh": True, "lech": [0, 0]} for p in pts] + \
           [{"ten": ten, "vi_tri": P(lon, lat + r), "dam": True, "man_hinh": True, "lech": list(lech), "co": 17}]
def dd(x, y, ten, lech, **kw): return {"ten": ten, "vi_tri": P(x, y), "kieu": "diem", "man_hinh": True, "lech": lech, **kw}
def nh(x, y, ten, **kw): return {"ten": ten, "vi_tri": P(x, y), "man_hinh": True, "lech": [0, 0], **kw}
def song(pts, rong=3): return {"diem": [P(*p) for p in pts], "rong": rong}

D = {"thang_long": (105.85, 21.03), "son_nam": (106.17, 20.42), "thuong_du_th": (105.1, 20.15), "muong_thanh": (103.02, 21.39),
     "tam_dao": (105.6, 21.45), "son_tay": (105.5, 21.13), "thai_nguyen": (105.84, 21.59), "tuyen_quang": (105.22, 21.82),
     "do_son": (106.79, 20.72), "van_don": (107.45, 21.07), "kinh_bac": (106.07, 21.18), "thanh_hoa": (105.78, 19.8),
     "nghe_an": (105.68, 18.75), "hai_duong": (106.33, 20.94), "ninh_xa": (106.1, 21.08)}
Q = lambda k: P(*D[k])
Z = 2.0   # từ mức zoom này hiện các nhãn trấn
S = {
 "phien_ban": 2, "ten": "Phong trào nông dân Đàng Ngoài", "phu_de": "Giữa thế kỉ XVIII",
 "nguon": "Vẽ lại, giản lược theo Hình 7.1 và bảng tóm tắt, SGK Lịch sử và Địa lí 8, tr. 32–33; nền bản đồ Natural Earth",
 "khung": P(97.6, 24.0) + P(119.2, 8.0), "nen_bien": [0.80, 0.88, 0.93], "chu_giai_xy": [0.03, 0.30], "sao_man_hinh": True,
 "vung_mau": nen([96, 5, 125, 27]),
 "song": [song([(103.97, 22.5), (104.87, 21.72), (105.43, 21.3), (105.86, 21.03), (106.05, 20.65), (106.55, 20.25)]),
          song([(103.4, 22.3), (103.6, 21.6), (104.3, 21.1), (104.95, 20.85), (105.35, 21.15), (105.43, 21.3)], 2.5),
          song([(105.0, 22.6), (105.2, 22.0), (105.3, 21.6), (105.43, 21.3)], 2.5),
          song([(104.6, 20.55), (105.2, 20.25), (105.6, 20.0), (105.8, 19.82), (105.92, 19.76)]),
          song([(104.3, 19.35), (104.88, 19.05), (105.3, 18.9), (105.5, 18.72), (105.68, 18.7), (105.77, 18.77)])],
 "dia_danh": dao2(112.0, 16.5, "QĐ. Hoàng Sa") + dao2(114.0, 9.6, "QĐ. Trường Sa", n=9, r=.8) + [
  nh(110.6, 23.2, "TRUNG QUỐC", lon=True, zoom_den=1.5), nh(108.4, 22.95, "TRUNG QUỐC", lon=True, zoom_tu=1.5, zoom_den=3.0),
  nh(103.2, 19.6, "LÀO", lon=True), nh(104.6, 12.9, "CAM-PU-CHIA", lon=True), nh(100.8, 15.8, "THÁI LAN", lon=True),
  nh(114.3, 13.6, "BIỂN ĐÔNG", lon=True), nh(107.8, 19.8, "VỊNH BẮC BỘ", dam=True, co=17, zoom_tu=Z),
  dd(*D["thang_long"], "THĂNG LONG", [0, 22], dam=True, co=20),
  nh(106.55, 20.3, "SƠN NAM", dam=True, co=16, zoom_tu=Z), nh(105.55, 19.6, "THANH HOÁ", dam=True, co=16, zoom_tu=Z),
  nh(105.2, 18.55, "NGHỆ AN", dam=True, co=16, zoom_tu=Z), nh(106.45, 21.35, "KINH BẮC", dam=True, co=16, zoom_tu=Z),
  nh(105.05, 21.22, "SƠN TÂY", dam=True, co=16, zoom_tu=Z), nh(106.25, 21.75, "THÁI NGUYÊN", dam=True, co=16, zoom_tu=Z),
  nh(105.0, 22.2, "TUYÊN QUANG", dam=True, co=16, zoom_tu=Z), nh(106.78, 20.97, "HẢI DƯƠNG", dam=True, co=15, zoom_tu=Z),
  nh(104.3, 21.75, "HƯNG HOÁ", dam=True, co=16, zoom_tu=Z),
  nh(105.0, 20.95, "ĐÀNG NGOÀI", dam=True, co=22, zoom_tu=1.3, zoom_den=Z)
 ]
}
S["chu_giai"] = [{"loai": "mui_ten_ta", "nhan": "Hướng hoạt động của nghĩa quân"}, {"loai": "sao", "nhan": "Căn cứ chính của nghĩa quân"}]
O = {}
# toàn cảnh: lửa ở những nơi xảy ra khởi nghĩa (một điểm đại diện cho mỗi cuộc, theo các số 1–7 của Hình 7.1)
for i, k in enumerate(["ninh_xa", "son_nam", "hai_duong", "muong_thanh", "tam_dao", "thanh_hoa", "son_tay", "nghe_an", "tuyen_quang"]):
    O[f"lua_{k}"] = {"loai": "lua", "diem": [Q(k)]}
O.update({
 # Hoàng Công Chất (1739 – 1769)
 "hcc1": {"loai": "mui_ten_ta", "diem": [P(106.05, 20.35), P(105.6, 20.1), P(105.15, 20.15)], "w0": 3, "w1": 5},
 "hcc2": {"loai": "mui_ten_ta", "diem": [P(105.0, 20.3), P(104.2, 20.8), P(103.5, 21.1), P(103.1, 21.32)], "w0": 3, "w1": 5},
 "sao_mt": {"loai": "sao", "vi_tri": Q("muong_thanh")},
 "n_hcc0": {"loai": "nhan", "vi_tri": P(107.25, 20.1), "chu": "Tập hợp dân nghèo ở Sơn Nam", "co": 6.5, "mau": "ta"},
 "n_hcc1": {"loai": "nhan", "vi_tri": P(104.6, 19.9), "chu": "Thượng du Thanh Hoá", "co": 6.5, "mau": "ta"},
 "n_hcc2": {"loai": "nhan", "vi_tri": P(103.25, 21.05), "chu": "Căn cứ Mường Thanh (Điện Biên)", "co": 6.5, "mau": "ta"},
 # Nguyễn Danh Phương (1740 – 1751)
 "sao_td": {"loai": "sao", "vi_tri": Q("tam_dao")},
 "ndp1": {"loai": "mui_ten_ta", "diem": [P(105.55, 21.4), P(105.5, 21.28), P(105.48, 21.17)], "w0": 2.6, "w1": 4.4},
 "ndp2": {"loai": "mui_ten_ta", "diem": [P(105.66, 21.48), P(105.75, 21.55), P(105.82, 21.58)], "w0": 2.6, "w1": 4.4},
 "ndp3": {"loai": "mui_ten_ta", "diem": [P(105.55, 21.52), P(105.4, 21.68), P(105.25, 21.8)], "w0": 2.6, "w1": 4.4},
 "n_ndp": {"loai": "nhan", "vi_tri": P(104.55, 21.55), "chu": "Căn cứ Tam Đảo (Phú Thọ)", "co": 5.2, "mau": "ta"},
 # Nguyễn Hữu Cầu (1741 – 1751)
 "sao_ds": {"loai": "sao", "vi_tri": Q("do_son")}, "sao_vd": {"loai": "sao", "vi_tri": Q("van_don")},
 "n_nhc": {"loai": "nhan", "vi_tri": P(107.6, 20.62), "chu": "Đồ Sơn (Hải Phòng)", "co": 6.5, "mau": "ta"},
 "n_nhc2": {"loai": "nhan", "vi_tri": P(107.85, 21.32), "chu": "Vân Đồn (Quảng Ninh)", "co": 6.5, "mau": "ta"},
 "nhc1": {"loai": "mui_ten_ta", "diem": [P(106.75, 20.8), P(106.45, 21.05), P(106.12, 21.17)], "w0": 3, "w1": 5},
 "nhc2": {"loai": "mui_ten_ta", "diem": [P(106.05, 21.15), P(105.97, 21.09), P(105.92, 21.05)], "w0": 2.2, "w1": 4},
 "n_uh": {"loai": "nhan", "vi_tri": P(106.35, 21.55), "chu": "Uy hiếp kinh thành Thăng Long", "co": 6.5, "mau": "ta"},
 "nhc3": {"loai": "mui_ten_ta", "diem": [P(106.6, 20.75), P(106.4, 20.55), P(106.2, 20.45)], "w0": 2.6, "w1": 4.4},
 "nhc4": {"loai": "mui_ten_ta", "diem": [P(106.15, 20.35), P(105.95, 20.0), P(105.8, 19.85)], "w0": 2.6, "w1": 4.4},
 "nhc5": {"loai": "mui_ten_ta", "diem": [P(105.78, 19.75), P(105.78, 19.25), P(105.7, 18.82)], "w0": 2.6, "w1": 4.4},
})
S["doi_tuong"] = O
BAC = dict(tam=P(105.15, 20.6), can_giua=[0.52, 0.44])
S["pha"] = {
 "tong_quan": {"mo_dau": True, "zoom": [1.1, 2.4], **BAC, "chu_giai": [],
               "moc": [{"chu": "Giữa thế kỉ XVIII", "tu": 0.05, "den": 1.1}],
               "buoc": [{"id": f"lua_{k}", "tu": 0.45 + .05 * i, "den": 0.55 + .05 * i} for i, k in enumerate(["son_nam", "hai_duong", "son_tay", "tam_dao", "tuyen_quang", "thanh_hoa", "nghe_an", "muong_thanh"])]},
 "hoang_cong_chat": {"zoom": [2.4, 2.5], **BAC, "chu_giai": ["mui_ten_ta", "sao"],
                     "moc": [{"chu": "Hoàng Công Chất (1739 – 1769)", "tu": 0.03, "den": 1.1}],
                     "buoc": [{"id": "n_hcc0", "tu": 0.05, "den": 0.15}, {"id": "hcc1", "tu": 0.15, "den": 0.35}, {"id": "n_hcc1", "tu": 0.3, "den": 0.4},
                              {"id": "hcc2", "tu": 0.42, "den": 0.65}, {"id": "sao_mt", "tu": 0.65, "den": 0.72}, {"id": "n_hcc2", "tu": 0.66, "den": 0.74}]},
 "nguyen_danh_phuong": {"zoom": [3.6, 3.75], "tam": P(105.55, 21.4), "can_giua": [0.5, 0.45], "chu_giai": ["mui_ten_ta", "sao"],
                        "moc": [{"chu": "Nguyễn Danh Phương (1740 – 1751)", "tu": 0.03, "den": 1.1}],
                        "buoc": [{"id": "sao_td", "tu": 0.08, "den": 0.16}, {"id": "n_ndp", "tu": 0.1, "den": 0.18},
                                 {"id": "ndp1", "tu": 0.3, "den": 0.45}, {"id": "ndp2", "tu": 0.35, "den": 0.5}, {"id": "ndp3", "tu": 0.4, "den": 0.55}]},
 "nguyen_huu_cau": {"zoom": [2.7, 2.8], "tam": P(106.2, 20.4), "can_giua": [0.52, 0.45], "chu_giai": ["mui_ten_ta", "sao"],
                    "moc": [{"chu": "Nguyễn Hữu Cầu – Quận He (1741 – 1751)", "tu": 0.03, "den": 1.1}],
                    "buoc": [{"id": "sao_ds", "tu": 0.05, "den": 0.12}, {"id": "n_nhc", "tu": 0.06, "den": 0.14}, {"id": "sao_vd", "tu": 0.1, "den": 0.17}, {"id": "n_nhc2", "tu": 0.11, "den": 0.19},
                             {"id": "nhc1", "tu": 0.22, "den": 0.38}, {"id": "nhc2", "tu": 0.38, "den": 0.45},
                             {"id": "nhc3", "tu": 0.58, "den": 0.68}, {"id": "nhc4", "tu": 0.66, "den": 0.76}, {"id": "nhc5", "tu": 0.74, "den": 0.84}]}
}
json.dump(S, open(f"{ROOT}/pipeline/maps/specs/nong-dan-dang-ngoai.json", "w"), ensure_ascii=False)
print("ok")
