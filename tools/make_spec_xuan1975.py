"""Sinh sa bàn Tổng tiến công và nổi dậy Xuân 1975 (theo Hình 17.5 và bảng tóm tắt SGK LSĐL 9 tr. 89–91)."""
import json, sys
sys.path.insert(0, "/home/claude/eduhistory-studio/tools")
from make_vn_map import xy, nen, dao, ROOT
P = lambda lon, lat: xy(lon, lat)
S = {
 "phien_ban": 2, "ten": "Tổng tiến công và nổi dậy Xuân 1975", "phu_de": "Ba chiến dịch lớn",
 "nguon": "Vẽ lại, giản lược theo Hình 17.5, SGK Lịch sử và Địa lí 9, tr. 89; nền bản đồ Natural Earth",
 "khung": P(102.6, 18.3) + P(117.0, 8.2), "nen_bien": [0.80, 0.88, 0.93], "chu_giai_xy": [0.03, 0.66],
 "vung_mau": nen([100, 5, 120, 20]),
 "dia_danh": [
  {"ten": "Huế", "vi_tri": P(107.58, 16.46), "kieu": "diem", "nhan": P(107.2, 16.62)},
  {"ten": "Đà Nẵng", "vi_tri": P(108.22, 16.05), "kieu": "diem", "nhan": P(108.85, 16.2)},
  {"ten": "Kon Tum", "vi_tri": P(108.0, 14.35), "kieu": "diem", "nhan": P(107.55, 14.4)},
  {"ten": "Plây-ku", "vi_tri": P(108.0, 13.98), "kieu": "diem", "nhan": P(107.55, 13.95)},
  {"ten": "Buôn Ma Thuột", "vi_tri": P(108.05, 12.68), "kieu": "diem", "nhan": P(107.35, 12.6), "dam": True},
  {"ten": "Tuy Hoà", "vi_tri": P(109.3, 13.08), "kieu": "diem", "nhan": P(109.75, 13.08)},
  {"ten": "SÀI GÒN", "vi_tri": P(106.7, 10.78), "kieu": "diem", "nhan": P(107.45, 10.45), "dam": True},
  {"ten": "Châu Đốc", "vi_tri": P(105.12, 10.7), "kieu": "diem", "nhan": P(104.75, 10.95)},
  {"ten": "CAM-PU-CHIA", "vi_tri": P(104.6, 12.8), "lon": True},
  {"ten": "LÀO", "vi_tri": P(105.6, 16.0), "lon": True},
  {"ten": "BIỂN ĐÔNG", "vi_tri": P(111.5, 13.2), "lon": True},
  {"ten": "VỊNH THÁI LAN", "vi_tri": P(103.6, 9.6), "dam": True}
 ] + dao(112.0, 16.5, "QĐ. Hoàng Sa") + dao(114.0, 9.6, "QĐ. Trường Sa", n=9, r=.8),
 "chu_giai": [
  {"loai": "mui_ten_ta", "nhan": "Quân ta tiến công"},
  {"loai": "rut_chay", "nhan": "Quân địch rút chạy"},
  {"loai": "sao", "nhan": "Nơi giành thắng lợi"}
 ],
 "doi_tuong": {
  "bmt_a": {"loai": "mui_ten_ta", "diem": [P(107.6, 13.3), P(107.85, 12.95), P(108.0, 12.72)], "w0": 7, "w1": 13},
  "bmt_b": {"loai": "mui_ten_ta", "diem": [P(108.6, 12.95), P(108.3, 12.75), P(108.08, 12.68)], "w0": 7, "w1": 13},
  "sao_bmt": {"loai": "sao", "vi_tri": P(108.05, 12.68)},
  "n_bmt": {"loai": "nhan", "vi_tri": P(108.05, 12.25), "chu": "10 – 3: Buôn Ma Thuột", "co": 11, "mau": "ta"},
  "rut_tn": {"loai": "rut_chay", "diem": [P(108.0, 13.95), P(108.5, 13.45), P(109.0, 13.2), P(109.28, 13.1)], "w0": 4},
  "n_tn": {"loai": "nhan", "vi_tri": P(109.2, 14.6), "chu": "24 – 3: Tây Nguyên giải phóng", "co": 11, "mau": "ta"},
  "hue_a": {"loai": "mui_ten_ta", "diem": [P(107.1, 16.9), P(107.35, 16.65), P(107.55, 16.48)], "w0": 7, "w1": 13},
  "hue_b": {"loai": "mui_ten_ta", "diem": [P(107.2, 16.1), P(107.4, 16.3), P(107.56, 16.44)], "w0": 7, "w1": 13},
  "sao_hue": {"loai": "sao", "vi_tri": P(107.58, 16.46)},
  "n_hue": {"loai": "nhan", "vi_tri": P(106.9, 16.95), "chu": "26 – 3: Huế", "co": 11, "mau": "ta"},
  "dn_a": {"loai": "mui_ten_ta", "diem": [P(107.75, 16.3), P(108.0, 16.15), P(108.18, 16.07)], "w0": 7, "w1": 13},
  "dn_b": {"loai": "mui_ten_ta", "diem": [P(107.8, 15.6), P(108.0, 15.85), P(108.19, 16.02)], "w0": 7, "w1": 13},
  "sao_dn": {"loai": "sao", "vi_tri": P(108.22, 16.05)},
  "n_dn": {"loai": "nhan", "vi_tri": P(108.95, 15.75), "chu": "29 – 3: Đà Nẵng", "co": 11, "mau": "ta"},
  "n_ts": {"loai": "nhan", "vi_tri": P(114.0, 11.6), "chu": "1 – 4 đến 29 – 4: làm chủ nhiều đảo", "co": 15, "mau": "ta"},
  "sg1": {"loai": "mui_ten_ta", "diem": [P(106.1, 11.35), P(106.4, 11.05), P(106.64, 10.83)], "w0": 7, "w1": 13},
  "sg2": {"loai": "mui_ten_ta", "diem": [P(106.65, 11.5), P(106.68, 11.15), P(106.69, 10.85)], "w0": 7, "w1": 13},
  "sg3": {"loai": "mui_ten_ta", "diem": [P(107.25, 11.25), P(107.0, 11.0), P(106.75, 10.82)], "w0": 7, "w1": 13},
  "sg4": {"loai": "mui_ten_ta", "diem": [P(107.35, 10.55), P(107.05, 10.68), P(106.76, 10.77)], "w0": 7, "w1": 13},
  "sg5": {"loai": "mui_ten_ta", "diem": [P(106.2, 10.35), P(106.45, 10.6), P(106.66, 10.75)], "w0": 7, "w1": 13},
  "sao_sg": {"loai": "sao", "vi_tri": P(106.7, 10.78)},
  "n_sg": {"loai": "nhan", "vi_tri": P(106.7, 10.25), "chu": "Năm cánh quân tiến vào trung tâm", "co": 9, "mau": "ta"},
  "sao_cd": {"loai": "sao", "vi_tri": P(105.12, 10.7)},
  "n_cd": {"loai": "nhan", "vi_tri": P(104.9, 10.3), "chu": "2 – 5: Châu Đốc", "co": 11, "mau": "ta"}
 },
 "pha": {
  "tong_quan": {"mo_dau": True, "zoom": [1.0, 1.04], "chu_giai": []},
  "tay_nguyen": {"zoom": [1.6, 1.75], "tam": P(108.3, 13.4), "can_giua": [0.5, 0.48], "chu_giai": ["mui_ten_ta", "rut_chay", "sao"],
   "moc": [{"chu": "Chiến dịch Tây Nguyên: 4 – 3 đến 24 – 3 – 1975", "tu": 0.02, "den": 0.98}],
   "buoc": [{"id": "bmt_a", "tu": 0.08, "den": 0.28}, {"id": "bmt_b", "tu": 0.1, "den": 0.3}, {"id": "sao_bmt", "tu": 0.3, "den": 0.38}, {"id": "n_bmt", "tu": 0.32, "den": 0.4},
            {"id": "rut_tn", "tu": 0.45, "den": 0.75}, {"id": "n_tn", "tu": 0.8, "den": 0.88}]},
  "hue_da_nang": {"zoom": [1.9, 2.0], "tam": P(107.9, 16.2), "can_giua": [0.5, 0.48], "chu_giai": ["mui_ten_ta", "sao"],
   "moc": [{"chu": "Chiến dịch Huế – Đà Nẵng: 21 – 3 đến 29 – 3 – 1975", "tu": 0.02, "den": 0.98}],
   "buoc": [{"id": "hue_a", "tu": 0.08, "den": 0.3}, {"id": "hue_b", "tu": 0.1, "den": 0.32}, {"id": "sao_hue", "tu": 0.32, "den": 0.4}, {"id": "n_hue", "tu": 0.34, "den": 0.42},
            {"id": "dn_a", "tu": 0.5, "den": 0.7}, {"id": "dn_b", "tu": 0.52, "den": 0.72}, {"id": "sao_dn", "tu": 0.72, "den": 0.8}, {"id": "n_dn", "tu": 0.74, "den": 0.82}]},
  "truong_sa": {"zoom": [1.1, 1.25], "tam": P(112.0, 11.0), "can_giua": [0.5, 0.5], "chu_giai": [],
   "buoc": [{"id": "n_ts", "tu": 0.2, "den": 0.32}]},
  "ho_chi_minh": {"zoom": [2.4, 2.6], "tam": P(106.7, 10.85), "can_giua": [0.5, 0.48], "chu_giai": ["mui_ten_ta", "sao"],
   "moc": [{"chu": "Chiến dịch Hồ Chí Minh: 26 – 4 đến 30 – 4 – 1975", "tu": 0.02, "den": 0.82}],
   "buoc": [{"id": "sg1", "tu": 0.08, "den": 0.4}, {"id": "sg2", "tu": 0.1, "den": 0.42}, {"id": "sg3", "tu": 0.12, "den": 0.44}, {"id": "sg4", "tu": 0.14, "den": 0.46}, {"id": "sg5", "tu": 0.16, "den": 0.48},
            {"id": "n_sg", "tu": 0.3, "den": 0.4}, {"id": "sao_sg", "tu": 0.55, "den": 0.65}],
   "bang": {"chu": "11 giờ 30 phút ngày 30 – 4 – 1975: Chiến dịch toàn thắng", "tu": 0.84}},
  "chau_doc": {"zoom": [1.6, 1.5], "tam": P(105.8, 10.6), "can_giua": [0.5, 0.5], "hien": ["sao_sg", "sg1", "sg2", "sg3", "sg4", "sg5"], "chu_giai": ["sao"],
   "buoc": [{"id": "sao_cd", "tu": 0.2, "den": 0.3}, {"id": "n_cd", "tu": 0.22, "den": 0.32}]}
 }
}
json.dump(S, open(f"{ROOT}/pipeline/maps/specs/xuan-1975.json", "w"), ensure_ascii=False)
print("ok", len(S["vung_mau"]))
