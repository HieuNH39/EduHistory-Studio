"""Sinh sa bàn (saban2) 'can-vuong': phong trào Cần vương và khởi nghĩa Hương Khê (1885 – 1896)
(SGK LSĐL 8, Bài 18, tr. 84–86; Hình 18.4 'Lược đồ một số địa điểm diễn ra các cuộc khởi nghĩa tiêu biểu trong phong trào Cần vương').
Vị trí Tân Sở (13 – 7 – 1885), Bãi Sậy, Ba Đình, Hương Khê và các điểm khởi nghĩa khác đặt theo Hình 18.4; vùng hoạt động của nghĩa quân
Hương Khê (miền Tây Thanh Hoá, Nghệ An, Hà Tĩnh, Quảng Trị) và hướng Pháp bao vây Ngàn Trươi là minh hoạ theo lời văn SGK tr. 85–86.
Nền đất liền Natural Earth; quần đảo Hoàng Sa, Trường Sa vẽ bằng chấm, nhãn ghi rõ thuộc Việt Nam."""
import json, sys, random
sys.path.insert(0, "/home/claude/eduhistory-studio/tools")
from make_vn_map import xy, nen, ROOT
P = lambda lon, lat: xy(lon, lat)

def quan_dao(lon0, lon1, lat0, lat1, n, seed):
    random.seed(seed)
    return [[random.uniform(lon0, lon1), random.uniform(lat0, lat1)] for _ in range(n)]
HS = quan_dao(111.2, 112.8, 15.8, 17.1, 16, 7)
TS = quan_dao(112.0, 116.8, 8.0, 11.4, 26, 9)
def cham(pts, **kw): return [{"ten": "", "vi_tri": P(*p), "kieu": "diem", "man_hinh": True, "lech": [0, 0], **kw} for p in pts]
def nh(x, y, ten, **kw): return {"ten": ten, "vi_tri": P(x, y), "man_hinh": True, "lech": [0, 0], **kw}

S = {
 "phien_ban": 2, "ten": "Phong trào Cần vương", "phu_de": "1885 – 1896",
 "nguon": "Vẽ bằng code theo Hình 18.4, SGK Lịch sử và Địa lí 8, Bài 18, tr. 85; nền đất liền Natural Earth",
 "khung": P(99.0, 23.6) + P(119.5, 6.0), "nen_bien": [0.80, 0.88, 0.93], "chu_giai_xy": [0.03, 0.30], "sao_man_hinh": True,
 "vung_mau": nen([96, 4, 125, 27]),
 "dia_danh": cham(HS, zoom_den=1.6) + cham(TS, zoom_den=1.6) + [
  nh(112.0, 17.55, "QĐ. Hoàng Sa (Việt Nam)", dam=True, co=19, zoom_den=1.6), nh(114.4, 12.0, "QĐ. Trường Sa (Việt Nam)", dam=True, co=19, zoom_den=1.6),
  nh(111.0, 22.9, "TRUNG QUỐC", lon=True, zoom_den=1.6), nh(103.4, 19.2, "LÀO", lon=True, zoom_den=1.6), nh(104.7, 12.9, "CAM-PU-CHIA", lon=True, zoom_den=1.6),
  nh(101.0, 15.5, "THÁI LAN", lon=True, zoom_den=1.6), nh(116.6, 14.3, "BIỂN ĐÔNG", lon=True, zoom_den=1.6),
  nh(104.3, 18.7, "LÀO", lon=True, zoom_tu=1.6), nh(107.4, 18.9, "VỊNH BẮC BỘ", dam=True, co=18, zoom_tu=1.6),
 ]
}
S["chu_giai"] = [{"loai": "sao", "nhan": "Nơi ban Dụ Cần vương"}, {"loai": "vong", "nhan": "Địa bàn nghĩa quân Hương Khê"},
                 {"loai": "mui_ten_dich", "nhan": "Pháp bao vây, tấn công (minh hoạ)"}]
nhan = lambda lon, lat, chu, co=12, mau="ta": {"loai": "nhan", "vi_tri": P(lon, lat), "chu": chu, "co": co, "mau": mau}
VUNG = [(104.75, 20.25), (105.3, 20.1), (105.45, 19.1), (105.8, 18.2), (106.35, 17.25), (106.75, 16.6), (106.4, 16.35),
        (105.8, 17.1), (105.15, 17.95), (104.6, 18.75), (104.35, 19.6), (104.75, 20.25)]
S["doi_tuong"] = {
 "tan_so": {"loai": "sao", "vi_tri": P(106.95, 16.78)},
 "n_tan_so": nhan(104.9, 16.45, "Tân Sở, 13 – 7 – 1885", 21),
 "lua_khac": {"loai": "lua", "diem": [P(103.6, 22.3), P(106.3, 21.85), P(108.75, 15.1), P(109.0, 13.9), P(108.0, 11.0)]},
 "bai_say": {"loai": "sao", "vi_tri": P(106.05, 20.9)}, "n_bai_say": nhan(107.55, 21.25, "Bãi Sậy", 21),
 "ba_dinh": {"loai": "sao", "vi_tri": P(105.95, 20.05)}, "n_ba_dinh": nhan(107.45, 20.0, "Ba Đình", 21),
 "huong_khe": {"loai": "sao", "vi_tri": P(105.72, 18.18)}, "n_huong_khe": nhan(107.45, 18.3, "Hương Khê", 21),
 "vung": {"loai": "vong", "diem": [P(*p) for p in VUNG], "rong": 4},
 "n_thanh": nhan(104.65, 19.72, "miền Tây Thanh Hoá", 6.2, "chu"), "n_nghe": nhan(104.9, 19.1, "miền Tây Nghệ An", 6.2, "chu"),
 "n_ha_tinh": nhan(105.3, 17.75, "Hà Tĩnh", 6.2, "chu"), "n_quang_tri": nhan(106.45, 16.85, "Quảng Trị", 6.2, "chu"),
 "can_cu": {"loai": "sao", "vi_tri": P(105.72, 18.18)}, "n_can_cu": nhan(106.35, 18.02, "Hương Khê", 7),
 "ngan_truoi": {"loai": "sao", "vi_tri": P(105.45, 18.38)}, "n_ngan_truoi": nhan(105.0, 18.55, "Ngàn Trươi", 7),
 "d1": {"loai": "mui_ten_dich", "diem": [P(105.85, 19.05), P(105.65, 18.8), P(105.5, 18.52)], "w0": 2.2, "w1": 3.6},
 "d2": {"loai": "mui_ten_dich", "diem": [P(106.3, 18.65), P(105.9, 18.5), P(105.56, 18.42)], "w0": 2.2, "w1": 3.6},
 "d3": {"loai": "mui_ten_dich", "diem": [P(105.75, 17.6), P(105.55, 17.95), P(105.47, 18.3)], "w0": 2.2, "w1": 3.6},
}
HK = dict(tam=P(105.6, 18.3), can_giua=[0.55, 0.47])
S["pha"] = {
 "tong_quan": {"mo_dau": True, "zoom": [1.0, 1.05], "chu_giai": ["sao"],
               "moc": [{"chu": "13 – 7 – 1885: Dụ Cần vương", "tu": 0.05, "den": 1.1}],
               "buoc": [{"id": "tan_so", "tu": 0.1, "den": 0.2}, {"id": "n_tan_so", "tu": 0.15, "den": 0.25}, {"id": "lua_khac", "tu": 0.35, "den": 0.9},
                        {"id": "bai_say", "tu": 0.45, "den": 0.55}, {"id": "n_bai_say", "tu": 0.5, "den": 0.6},
                        {"id": "ba_dinh", "tu": 0.55, "den": 0.65}, {"id": "n_ba_dinh", "tu": 0.6, "den": 0.7},
                        {"id": "huong_khe", "tu": 0.65, "den": 0.75}, {"id": "n_huong_khe", "tu": 0.7, "den": 0.8}]},
 "huong_khe": {"zoom": [2.7, 2.85], **HK, "chu_giai": ["vong"], "hien": ["can_cu", "n_can_cu"],
               "moc": [{"chu": "Khởi nghĩa Hương Khê (1885 – 1896)", "tu": 0.03, "den": 1.1}],
               "buoc": [{"id": "vung", "tu": 0.15, "den": 0.5}, {"id": "n_thanh", "tu": 0.45, "den": 0.55}, {"id": "n_nghe", "tu": 0.52, "den": 0.62},
                        {"id": "n_ha_tinh", "tu": 0.59, "den": 0.69}, {"id": "n_quang_tri", "tu": 0.66, "den": 0.76}]},
 "ngan_truoi": {"zoom": [3.3, 3.5], "tam": P(105.65, 18.35), "can_giua": [0.55, 0.47], "chu_giai": ["mui_ten_dich"], "hien": ["vung", "can_cu", "n_can_cu"],
                "moc": [{"chu": "Pháp bao vây, tấn công Ngàn Trươi", "tu": 0.03, "den": 1.1}],
                "buoc": [{"id": "ngan_truoi", "tu": 0.08, "den": 0.18}, {"id": "n_ngan_truoi", "tu": 0.12, "den": 0.22},
                         {"id": "d1", "tu": 0.3, "den": 0.6}, {"id": "d2", "tu": 0.38, "den": 0.68}, {"id": "d3", "tu": 0.46, "den": 0.76}]},
}
json.dump(S, open(f"{ROOT}/pipeline/maps/specs/can-vuong.json", "w"), ensure_ascii=False)
print("ok")
