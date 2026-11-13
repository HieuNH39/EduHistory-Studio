"""Sa bàn (saban2) 'Khởi nghĩa Hai Bà Trưng (năm 40)'.
Vẽ lại, giản lược theo Hình 1 'Lược đồ khởi nghĩa Hai Bà Trưng (năm 40)', SGK Lịch sử và Địa lí 6, Bài 16, tr. 71:
toạ độ cục bộ đo trên ảnh lược đồ (ảnh trang thu về khổ 1425 px, khung 125..1315 × 135..877); sông vẽ giản lược.
Diễn biến theo sơ đồ 4 bước dưới lược đồ (tr. 71): phất cờ ở cửa sông Hát (Hát Môn) – theo sông Hồng đánh chiếm
Mê Linh, Cổ Loa – tấn công Luy Lâu, Tô Định rút chạy – Trưng Trắc lên ngôi, đóng đô ở Mê Linh.
Lược đồ là vùng nội địa Bắc Bộ, không vẽ biển, không vẽ đường biên giới."""
import json
ROOT = "/home/claude/eduhistory-studio"

SONG = [
 {"ten": "S. Hồng", "nhan": [395, 452], "goc": 22, "rong": 10, "diem": [[125, 378], [200, 393], [262, 418], [322, 443], [390, 470], [460, 495], [530, 517], [590, 535], [650, 546], [705, 552], [760, 562], [800, 578], [828, 603], [840, 643], [836, 693], [830, 745], [826, 805], [832, 877]]},
 {"ten": "S. Lô", "nhan": [300, 362], "goc": -62, "rong": 6, "diem": [[332, 140], [318, 200], [302, 255], [282, 310], [266, 360], [262, 418]]},
 {"ten": "S. Cà Lồ", "nhan": [712, 448], "goc": 14, "rong": 5, "diem": [[598, 418], [655, 436], [712, 455], [765, 472], [800, 500], [812, 540]]},
 {"ten": "S. Đuống", "nhan": [1125, 522], "goc": -6, "rong": 7, "diem": [[828, 603], [878, 575], [940, 556], [1010, 548], [1080, 542], [1150, 536], [1220, 545], [1315, 560]]},
 {"ten": "S. Hát", "nhan": [585, 690], "goc": 70, "rong": 5, "diem": [[530, 522], [548, 565], [540, 615], [528, 665], [540, 725], [556, 795], [566, 877]]},
 {"ten": "S. Thương", "nhan": [1195, 372], "goc": 72, "rong": 5, "diem": [[1120, 140], [1132, 210], [1148, 280], [1165, 345], [1195, 410], [1245, 448], [1315, 470]]},
]

# Địa danh chính (lớn) và nơi các đội nghĩa quân nổi dậy (nhỏ) – đúng tên trên lược đồ SGK
DIA_DANH = [
 {"ten": "HÁT MÔN", "vi_tri": [530, 522], "kieu": "diem", "nhan": [455, 555], "dam": True, "co": 19},
 {"ten": "MÊ LINH", "vi_tri": [637, 468], "kieu": "thanh", "nhan": [560, 420], "lon": True},
 {"ten": "CỔ LOA", "vi_tri": [805, 527], "kieu": "diem", "nhan": [905, 478], "lon": True},
 {"ten": "LUY LÂU", "vi_tri": [1017, 625], "kieu": "diem", "nhan": [1110, 680], "lon": True},
 {"ten": "GIAO CHỈ", "vi_tri": [968, 262], "co": 30},
 {"ten": "(Khu vực Bắc Bộ)", "vi_tri": [968, 300], "co": 14},
 {"ten": "Đề Nương", "vi_tri": [940, 178], "kieu": "diem", "nhan": [940, 155], "co": 13},
 {"ten": "Xuân Nương, Thiều Hoa", "vi_tri": [190, 432], "kieu": "diem", "nhan": [200, 408], "co": 13},
 {"ten": "Man Thiện", "vi_tri": [492, 690], "kieu": "diem", "nhan": [492, 666], "co": 13},
 {"ten": "Ông Cai", "vi_tri": [722, 760], "kieu": "diem", "nhan": [722, 736], "co": 13},
 {"ten": "Nàng Quốc", "vi_tri": [912, 755], "kieu": "diem", "nhan": [912, 731], "co": 13},
 {"ten": "Nguyễn Tam Trinh", "vi_tri": [842, 640], "kieu": "diem", "nhan": [745, 668], "co": 13},
 {"ten": "Vĩnh Huy", "vi_tri": [1020, 572], "kieu": "diem", "nhan": [1088, 580], "co": 13},
 {"ten": "Thành Thiên", "vi_tri": [1258, 488], "kieu": "diem", "nhan": [1258, 466], "co": 13},
 {"ten": "Lê Chân", "vi_tri": [1228, 815], "kieu": "diem", "nhan": [1228, 791], "co": 13},
]

DT = {
 "tam_dao": {"loai": "nhan", "vi_tri": [612, 232], "chu": "DÃY TAM ĐẢO", "co": 20, "mau": "chu", "goc": 50},
 "hm_co": {"loai": "nhan", "vi_tri": [420, 600], "chu": "Phất cờ khởi nghĩa", "co": 17, "mau": "ta"},
 "a1": {"loai": "mui_ten_ta", "diem": [[548, 520], [588, 505], [622, 485]], "w0": 8, "w1": 15},
 "a2": {"loai": "mui_ten_ta", "diem": [[668, 482], [715, 497], [768, 515]], "w0": 8, "w1": 15},
 "sao_cl": {"loai": "sao", "vi_tri": [805, 527]},
 "a3": {"loai": "mui_ten_ta", "diem": [[868, 548], [925, 578], [978, 610]], "w0": 8, "w1": 15},
 "a4": {"loai": "mui_ten_ta", "diem": [[862, 652], [915, 650], [972, 642]], "w0": 7, "w1": 13},
 "sao_ll": {"loai": "sao", "vi_tri": [1017, 625]},
 "chay": {"loai": "rut_chay", "diem": [[1085, 618], [1160, 598], [1245, 578]], "w0": 4},
 "chay_nhan": {"loai": "nhan", "vi_tri": [1172, 640], "chu": "Tô Định rút chạy", "co": 16, "mau": "dich", "goc": -12},
 "do_me_linh": {"loai": "thanh_sang", "vi_tri": [637, 468]},
}

PHA = {
 "khoi_nghia": {"mo_dau": True, "zoom": [1.0, 1.04], "chu_giai": [], "hien": ["tam_dao"],
                "moc": [{"chu": "Tháng 3 – năm 40", "tu": 0.08, "den": 1.1}],
                "buoc": [{"id": "hm_co", "tu": 0.15, "den": 0.3}],
                "bang": {"chu": "Tướng lĩnh khắp 65 thành trì quy tụ", "tu": 0.6, "y": 0.72}},
 "tien_quan": {"zoom": [1.04, 1.1], "tam": [700, 520], "chu_giai": ["mui_ten_ta", "sao"], "hien": ["tam_dao", "hm_co"],
               "buoc": [{"id": "a1", "tu": 0.08, "den": 0.38}, {"id": "a2", "tu": 0.42, "den": 0.72}, {"id": "sao_cl", "tu": 0.72, "den": 0.86}]},
 "luy_lau": {"zoom": [1.06, 1.12], "tam": [900, 590], "chu_giai": ["mui_ten_ta", "sao", "rut_chay"], "hien": ["tam_dao", "hm_co", "a1", "a2", "sao_cl"],
             "moc": [{"chu": "Tháng 4 – năm 40", "tu": 0.05, "den": 1.1}],
             "buoc": [{"id": "a3", "tu": 0.08, "den": 0.36}, {"id": "a4", "tu": 0.2, "den": 0.45}, {"id": "sao_ll", "tu": 0.45, "den": 0.58},
                      {"id": "chay", "tu": 0.6, "den": 0.82}, {"id": "chay_nhan", "tu": 0.7, "den": 0.82}]},
 "thang_loi": {"zoom": [1.08, 1.0], "tam": [760, 560], "chu_giai": [],
               "hien": ["tam_dao", "a1", "a2", "a3", "a4", "sao_cl", "sao_ll", "chay", "chay_nhan"],
               "buoc": [{"id": "do_me_linh", "tu": 0.1, "den": 0.3}],
               "bang": {"chu": "Trưng Trắc lên ngôi, đóng đô ở Mê Linh", "tu": 0.35, "y": 0.72}},
}

spec = {
 "phien_ban": 2,
 "ten": "Khởi nghĩa Hai Bà Trưng",
 "phu_de": "Năm 40",
 "nguon": "Vẽ lại, giản lược theo Hình 1, SGK Lịch sử và Địa lí 6, Bài 16, tr. 71",
 "khung": [125, 135, 1315, 877],
 "tam": [720, 506],
 "chu_giai_xy": [0.015, 0.62],
 "song": SONG,
 "dia_danh": DIA_DANH,
 "chu_giai": [
  {"loai": "mui_ten_ta", "nhan": "Hướng tiến quân của Hai Bà Trưng"},
  {"loai": "sao", "nhan": "Bản doanh của Tô Định bị đánh chiếm"},
  {"loai": "rut_chay", "nhan": "Hướng rút chạy của Tô Định"},
  {"loai": "thanh", "nhan": "Nơi đóng đô của Trưng Vương"},
 ],
 "doi_tuong": DT,
 "pha": PHA,
}

if __name__ == "__main__":
    out = f"{ROOT}/pipeline/maps/specs/hai-ba-trung-40.json"
    json.dump(spec, open(out, "w"), ensure_ascii=False, indent=1)
    print("đã ghi", out)
