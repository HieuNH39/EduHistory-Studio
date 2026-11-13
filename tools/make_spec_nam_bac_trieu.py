"""Sinh hai sa bàn (saban2) cho Bài 5 SGK LSĐL 8: xung đột Nam – Bắc triều và xung đột Trịnh – Nguyễn.
Vẽ lại, giản lược theo Hình 5.2 (Lược đồ Nam – Bắc triều và Đàng Trong – Đàng Ngoài, tr. 24) và Hình 5.3
(Sơ đồ diễn biến chính của cuộc xung đột Nam – Bắc triều, tr. 25); diễn biến Trịnh – Nguyễn theo tr. 26.
Nền đất liền Natural Earth; sông vẽ tay giản lược. Luôn có quần đảo Hoàng Sa, Trường Sa (nhãn cỡ cố định trên màn hình).
Đầu ra: pipeline/maps/specs/nam-bac-trieu.json, pipeline/maps/specs/trinh-nguyen.json"""
import json, sys, random
sys.path.insert(0, "/home/claude/eduhistory-studio/tools")
from make_vn_map import xy, nen, ROOT
P = lambda lon, lat: xy(lon, lat)

def dao2(lon, lat, ten, n=7, r=0.35, lech=(0, -30)):
    """Quần đảo: chấm và nhãn cỡ cố định trên màn hình (không phóng to khi máy quay zoom)."""
    random.seed(int(lon * 100 + lat))
    pts = [[lon + random.uniform(-r, r), lat + random.uniform(-r, r)] for _ in range(n)]
    return [{"ten": "", "vi_tri": P(*p), "kieu": "diem", "man_hinh": True, "lech": [0, 0]} for p in pts] + \
           [{"ten": ten, "vi_tri": P(lon, lat + r), "dam": True, "man_hinh": True, "lech": list(lech), "co": 17}]

def dd(x, y, ten, lech, **kw): return {"ten": ten, "vi_tri": P(x, y), "kieu": "diem", "man_hinh": True, "lech": lech, **kw}
def nhan(x, y, ten, **kw): return {"ten": ten, "vi_tri": P(x, y), "man_hinh": True, "lech": [0, 0], **kw}
def song(ten, pts, nhan_xy=None, goc=0, rong=3):
    s = {"diem": [P(*p) for p in pts], "rong": rong}
    if ten: s.update(ten=ten, nhan=P(*nhan_xy), goc=goc)
    return s

# toạ độ (kinh độ, vĩ độ) – giản lược
DK, TD, CB = (105.85, 21.03), (105.60, 20.08), (106.26, 22.67)
GIANH = [(105.62, 17.88), (105.9, 17.86), (106.15, 17.84), (106.32, 17.78), (106.47, 17.72)]
NEN = {
 "phien_ban": 2, "khung": P(97.6, 24.0) + P(119.2, 8.0), "nen_bien": [0.80, 0.88, 0.93],
 "sao_man_hinh": True, "chu_giai_xy": [0.03, 0.30], "vung_mau": nen([96, 5, 125, 27]),
 "song": [
  song("", [(103.97, 22.5), (104.87, 21.72), (105.43, 21.3), (105.86, 21.03), (106.05, 20.65), (106.55, 20.25)]),
  song("", [(104.6, 20.55), (105.2, 20.25), (105.6, 20.0), (105.8, 19.82), (105.92, 19.76)]),
  song("", [(104.3, 19.35), (104.88, 19.05), (105.3, 18.9), (105.5, 18.72), (105.68, 18.7), (105.77, 18.77)]),
  song("", GIANH),
  song("", [(106.42, 17.28), (106.55, 17.38), (106.63, 17.49)], rong=2.5)
 ],
 "dia_danh": dao2(112.0, 16.5, "QĐ. Hoàng Sa") + dao2(114.0, 9.6, "QĐ. Trường Sa", n=9, r=.8) + [
  nhan(110.6, 23.2, "TRUNG QUỐC", lon=True, zoom_den=1.5), nhan(108.6, 23.0, "TRUNG QUỐC", lon=True, zoom_tu=1.5), nhan(103.2, 19.6, "LÀO", lon=True, zoom_den=3.0), nhan(104.75, 17.75, "LÀO", lon=True, zoom_tu=3.0), nhan(104.6, 12.9, "CAM-PU-CHIA", lon=True),
  nhan(100.8, 15.8, "THÁI LAN", lon=True), nhan(114.3, 13.6, "BIỂN ĐÔNG", lon=True),
  nhan(107.7, 19.9, "VỊNH BẮC BỘ", dam=True, co=17, zoom_tu=1.9)
 ]
}
CHUNG = lambda: json.loads(json.dumps(NEN))

# ------------------------------------------------------------------ Nam – Bắc triều (1533 – 1592)
NB = CHUNG()
NB.update({"ten": "Xung đột Nam – Bắc triều", "phu_de": "1533 – 1592",
           "nguon": "Vẽ lại, giản lược theo Hình 5.2 và Hình 5.3, SGK Lịch sử và Địa lí 8, tr. 24–25; nền bản đồ Natural Earth"})
NB["dia_danh"] += [
 dd(*DK, "Đông Kinh", [14, -14], dam=True, co=20, zoom_den=1.6), dd(*DK, "Đông Kinh (Thăng Long)", [-14, -16], dam=True, co=21, zoom_tu=1.6, zoom_den=1.99), dd(*DK, "Đông Kinh (Thăng Long)", [14, -16], dam=True, co=21, zoom_tu=2.0), dd(*TD, "Tây Đô", [-14, 14], dam=True, co=21),
 dd(*CB, "Cao Bằng", [14, -10], zoom_tu=2.0),
 nhan(105.2, 19.25, "THANH – NGHỆ", dam=True, co=19, zoom_tu=2.0), nhan(106.45, 20.62, "SƠN NAM", dam=True, co=17, zoom_tu=2.0),
 nhan(107.35, 16.95, "Thuận Hoá", dam=True, co=19, zoom_tu=1.6, zoom_den=2.6),
]
NB["chu_giai"] = [{"loai": "mui_ten_ta", "nhan": "Quân Nam triều (nhà Lê)"}, {"loai": "mui_ten_dich", "nhan": "Quân Bắc triều (nhà Mạc)"},
                  {"loai": "rut_lui", "nhan": "Nam triều rút về căn cứ"}, {"loai": "rut_chay", "nhan": "Nhà Mạc chạy lên Cao Bằng"},
                  {"loai": "sao", "nhan": "Chiếm được kinh đô"}]
NB["doi_tuong"] = {
 "n_bac": {"loai": "nhan", "vi_tri": P(108.9, 21.55), "chu": "BẮC TRIỀU (nhà Mạc)", "co": 14, "mau": "dich"},
 "n_nam": {"loai": "nhan", "vi_tri": P(108.25, 20.05), "chu": "NAM TRIỀU (nhà Lê)", "co": 14, "mau": "ta"},
 "cc1": {"loai": "mui_ten_ta", "diem": [P(105.75, 20.05), P(106.0, 20.25), P(106.25, 20.45)], "w0": 3, "w1": 5},
 "cc2": {"loai": "mui_ten_ta", "diem": [P(105.5, 20.15), P(105.35, 20.7), P(105.3, 21.25)], "w0": 3, "w1": 5},
 "cc1r": {"loai": "rut_lui", "diem": [P(106.22, 20.28), P(106.02, 20.04), P(105.8, 19.96)], "w0": 1.6},
 "cc2r": {"loai": "rut_lui", "diem": [P(105.12, 21.15), P(105.1, 20.62), P(105.42, 20.12)], "w0": 1.6},
 "bt1": {"loai": "mui_ten_dich", "diem": [P(105.85, 20.95), P(106.0, 20.4), P(105.9, 19.85)], "w0": 2.2, "w1": 4},
 "bt2": {"loai": "mui_ten_dich", "diem": [P(106.05, 20.9), P(106.3, 19.9), P(105.95, 18.9)], "w0": 2.2, "w1": 4},
 "bt3": {"loai": "mui_ten_dich", "diem": [P(106.35, 20.8), P(106.75, 19.4), P(106.45, 17.9), P(107.25, 16.75)], "w0": 2.2, "w1": 4},
 "lua_bb": {"loai": "lua", "diem": [P(106.05, 19.5), P(106.0, 18.6), P(106.4, 17.85), P(106.75, 17.3)]},
 "n_cl": {"loai": "nhan", "vi_tri": P(108.5, 18.2), "chu": "Chiến trường khốc liệt", "co": 8, "mau": "dich"},
 "rb1": {"loai": "mui_ten_ta", "diem": [P(105.55, 20.2), P(105.55, 20.65), P(105.78, 20.98)], "w0": 3.4, "w1": 6},
 "rb2": {"loai": "mui_ten_ta", "diem": [P(105.85, 20.1), P(106.1, 20.55), P(105.92, 20.98)], "w0": 3.4, "w1": 6},
 "sao_dk": {"loai": "sao", "vi_tri": P(*DK)},
 "mac_chay": {"loai": "rut_chay", "diem": [P(105.95, 21.12), P(106.15, 21.7), P(106.05, 22.2), P(106.22, 22.58)], "w0": 1.8},
}
NB["pha"] = {
 "tong_quan": {"mo_dau": True, "zoom": [1.1, 1.75], "tam": P(106.6, 20.2), "can_giua": [0.5, 0.47], "chu_giai": [],
               "moc": [{"chu": "1533 – 1592: gần 60 năm xung đột", "tu": 0.3, "den": 1.1}],
               "buoc": [{"id": "n_bac", "tu": 0.42, "den": 0.52}, {"id": "n_nam", "tu": 0.5, "den": 0.6}]},
 "cam_cu": {"zoom": [2.9, 3.05], "tam": P(105.75, 20.55), "can_giua": [0.52, 0.5], "chu_giai": ["mui_ten_ta", "rut_lui"],
            "moc": [{"chu": "1533 – 1570: hai bên cầm cự", "tu": 0.03, "den": 1.1}],
            "buoc": [{"id": "cc1", "tu": 0.1, "den": 0.35}, {"id": "cc2", "tu": 0.15, "den": 0.4}, {"id": "cc1r", "tu": 0.6, "den": 0.8}, {"id": "cc2r", "tu": 0.62, "den": 0.82}]},
 "bac_trieu_tien": {"zoom": [2.1, 2.2], "tam": P(106.4, 18.9), "can_giua": [0.55, 0.5], "chu_giai": ["mui_ten_dich"],
                    "moc": [{"chu": "1570 – 1583: Bắc triều đánh vào Thanh – Nghệ", "tu": 0.03, "den": 1.1}],
                    "buoc": [{"id": "bt1", "tu": 0.08, "den": 0.3}, {"id": "bt2", "tu": 0.12, "den": 0.36}, {"id": "bt3", "tu": 0.16, "den": 0.45},
                             {"id": "lua_bb", "tu": 0.45, "den": 0.75}, {"id": "n_cl", "tu": 0.55, "den": 0.65}]},
 "ra_bac": {"zoom": [2.6, 2.75], "tam": P(105.9, 21.3), "can_giua": [0.52, 0.5], "chu_giai": ["mui_ten_ta", "rut_chay", "sao"],
            "moc": [{"chu": "1583 – 1592: Nam triều đánh ra Bắc", "tu": 0.03, "den": 0.45}, {"chu": "1592: chiếm Thăng Long (Đông Kinh)", "tu": 0.45, "den": 0.8}],
            "buoc": [{"id": "rb1", "tu": 0.08, "den": 0.35}, {"id": "rb2", "tu": 0.1, "den": 0.38}, {"id": "sao_dk", "tu": 0.42, "den": 0.5},
                     {"id": "mac_chay", "tu": 0.52, "den": 0.75}],
            "bang": {"chu": "1592: Xung đột Nam – Bắc triều chấm dứt", "tu": 0.82, "y": 0.74}}
}
json.dump(NB, open(f"{ROOT}/pipeline/maps/specs/nam-bac-trieu.json", "w"), ensure_ascii=False)

# ------------------------------------------------------------------ Trịnh – Nguyễn (1627 – 1672)
LUY = [(106.64, 17.47), (106.58, 17.5), (106.5, 17.55), (106.42, 17.6), (106.33, 17.64)]
TN = CHUNG()
TN.update({"ten": "Xung đột Trịnh – Nguyễn", "phu_de": "1627 – 1672",
           "nguon": "Vẽ lại, giản lược theo Hình 5.2, SGK Lịch sử và Địa lí 8, tr. 24, và nội dung tr. 25–26; nền bản đồ Natural Earth"})
TN["dia_danh"] += [
 dd(*DK, "Thăng Long", [14, -14], dam=True, co=20), dd(*TD, "Thanh Hoá", [-14, 12], co=19, zoom_tu=1.5, zoom_den=2.4),
 nhan(107.3, 16.85, "Thuận Hoá", dam=True, co=20, zoom_den=4.0),
 nhan(105.3, 18.62, "s. Lam", co=16, zoom_tu=2.0), nhan(105.9, 17.98, "s. Gianh", co=17, dam=True, zoom_tu=2.0),
 nhan(105.45, 18.3, "Hà Tĩnh", co=16, zoom_tu=2.0), nhan(106.05, 17.35, "Quảng Bình", co=16, zoom_tu=2.0),
 nhan(106.75, 17.3, "s. Nhật Lệ", co=15, zoom_tu=2.0), dd(106.5, 17.6, "Luỹ Thầy", [-16, -16], dam=True, co=18, zoom_tu=2.0),
]
TN["chu_giai"] = [{"loai": "mui_ten_ta", "nhan": "Họ Nguyễn, quân Nguyễn"}, {"loai": "mui_ten_dich", "nhan": "Quân Trịnh tấn công"},
                  {"loai": "tuong", "nhan": "Luỹ Thầy"}, {"loai": "tran_tuyen", "nhan": "Ranh giới Đàng Ngoài – Đàng Trong"}]
TN["doi_tuong"] = {
 "nh": {"loai": "mui_ten_ta", "diem": [P(105.75, 19.95), P(106.2, 19.0), P(106.55, 17.9), P(107.25, 16.85)], "w0": 3, "w1": 6},
 "n_nh": {"loai": "nhan", "vi_tri": P(108.6, 18.45), "chu": "Nguyễn Hoàng vào trấn thủ Thuận Hoá", "co": 10, "mau": "ta"},
 "luy": {"loai": "tuong", "diem": [P(*p) for p in LUY], "phia": 1},
 "t1": {"loai": "mui_ten_dich", "diem": [P(105.85, 18.35), P(106.1, 18.0), P(106.3, 17.66)], "w0": 1.6, "w1": 3},
 "t2": {"loai": "mui_ten_dich", "diem": [P(106.2, 18.25), P(106.42, 17.9), P(106.5, 17.66)], "w0": 1.6, "w1": 3},
 "t3": {"loai": "mui_ten_dich", "diem": [P(105.7, 18.1), P(105.95, 17.75), P(106.3, 17.62)], "w0": 1.6, "w1": 3},
 "ng": {"loai": "mui_ten_ta", "diem": [P(106.25, 17.65), P(106.0, 18.0), P(105.82, 18.4), P(105.68, 18.62)], "w0": 1.6, "w1": 3},
 "n_ng": {"loai": "nhan", "vi_tri": P(104.55, 18.95), "chu": "Quân Nguyễn một lần vượt sông Gianh", "co": 5.5, "mau": "ta"},
 "n_ac": {"loai": "nhan", "vi_tri": P(107.25, 17.95), "chu": "Chiến trường ác liệt", "co": 6, "mau": "dich"},
 "n_dng": {"loai": "nhan", "vi_tri": P(104.4, 21.75), "chu": "ĐÀNG NGOÀI", "co": 20, "mau": "dich"},
 "n_dng2": {"loai": "nhan", "vi_tri": P(104.4, 21.2), "chu": "vua Lê – chúa Trịnh", "co": 14, "mau": "dich"},
 "n_dtr": {"loai": "nhan", "vi_tri": P(109.0, 15.6), "chu": "ĐÀNG TRONG", "co": 20, "mau": "ta"},
 "n_dtr2": {"loai": "nhan", "vi_tri": P(109.0, 15.05), "chu": "chúa Nguyễn", "co": 14, "mau": "ta"},
 "lua_qb": {"loai": "lua", "diem": [P(105.85, 18.3), P(106.25, 17.95), P(106.38, 17.55), P(105.95, 18.05)]},
 "ranh": {"loai": "tran_tuyen", "diem": [P(*p) for p in GIANH]},
}
TN["pha"] = {
 "thuan_hoa": {"mo_dau": True, "zoom": [1.8, 1.95], "tam": P(106.4, 18.6), "can_giua": [0.52, 0.5], "chu_giai": ["mui_ten_ta"],
               "buoc": [{"id": "nh", "tu": 0.12, "den": 0.5}, {"id": "n_nh", "tu": 0.45, "den": 0.55}]},
 "giao_tranh": {"zoom": [3.2, 3.35], "tam": P(106.0, 18.0), "can_giua": [0.5, 0.52], "chu_giai": ["mui_ten_ta", "mui_ten_dich", "tuong"], "hien": ["luy"],
                "moc": [{"chu": "1627 – 1672: bảy lần giao chiến", "tu": 0.03, "den": 1.1}],
                "buoc": [{"id": "t1", "tu": 0.08, "den": 0.25}, {"id": "t2", "tu": 0.14, "den": 0.31}, {"id": "t3", "tu": 0.2, "den": 0.37},
                         {"id": "ng", "tu": 0.45, "den": 0.62}, {"id": "n_ng", "tu": 0.58, "den": 0.66}, {"id": "n_ac", "tu": 0.75, "den": 0.85}]},
 "luy_thay": {"zoom": [3.5, 3.7], "tam": P(106.35, 17.6), "can_giua": [0.5, 0.5], "chu_giai": ["mui_ten_dich", "tuong"],
              "moc": [{"chu": "Luỹ Thầy (luỹ Đào Duy Từ)", "tu": 0.03, "den": 1.1}],
              "buoc": [{"id": "luy", "tu": 0.08, "den": 0.45}, {"id": "t2", "tu": 0.5, "den": 0.7}, {"id": "t1", "tu": 0.55, "den": 0.75}]},
 "chia_cat": {"zoom": [1.3, 1.35], "tam": P(106.5, 18.3), "can_giua": [0.5, 0.5], "chu_giai": ["tran_tuyen", "tuong"], "hien": ["luy"],
              "buoc": [{"id": "ranh", "tu": 0.08, "den": 0.35}, {"id": "n_dng", "tu": 0.3, "den": 0.4}, {"id": "n_dng2", "tu": 0.33, "den": 0.43}, {"id": "n_dtr", "tu": 0.42, "den": 0.52}, {"id": "n_dtr2", "tu": 0.45, "den": 0.55}],
              "bang": {"chu": "Sông Gianh: ranh giới chia cắt đất nước", "tu": 0.6, "y": 0.74}}
}
json.dump(TN, open(f"{ROOT}/pipeline/maps/specs/trinh-nguyen.json", "w"), ensure_ascii=False)
print("ok", len(NB["vung_mau"]))
