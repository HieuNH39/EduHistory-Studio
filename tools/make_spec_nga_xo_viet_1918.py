"""Sa bàn 'Nước Nga Xô viết chống thù trong, giặc ngoài (1918 – 1920)' – vẽ lại, giản lược theo Hình 1.2, SGK LSĐL 9 tr. 8.
Kí hiệu như lược đồ SGK: mũi tên mảnh (chàm) = quân đế quốc can thiệp; ngọn lửa = quân nổi loạn; mũi tên đậm (đỏ) = hướng quân Xô viết tấn công.
Nền đất liền Natural Earth 1:110m, không vẽ biên giới quốc gia; vị trí gần đúng."""
import json, sys
sys.path.insert(0, "/home/claude/eduhistory-studio/tools")
from make_geo_map import Geo, ROOT
g = Geo(5, 72.5, 55); P = g.P
D = lambda *pts: [P(*p) for p in pts]
def tp(lon, lat, ten, nlon, nlat, dam=False): return {"ten": ten, "vi_tri": P(lon, lat), "kieu": "diem", "nhan": P(nlon, nlat), "dam": dam}
def nh(lon, lat, chu, co=15, mau="dich"): return {"loai": "nhan", "vi_tri": P(lon, lat), "chu": chu, "co": co, "mau": mau}
dich = lambda *pts: {"loai": "mui_ten_dich", "diem": D(*pts), "w0": 5, "w1": 9}
ta = lambda *pts: {"loai": "mui_ten_ta", "diem": D(*pts), "w0": 8, "w1": 14}
S = {
 "phien_ban": 2, "ten": "Nước Nga Xô viết (1918 – 1920)", "phu_de": "Chống thù trong, giặc ngoài",
 "nguon": "Vẽ lại, giản lược theo Hình 1.2, SGK Lịch sử và Địa lí 9, tr. 8; nền đất liền Natural Earth",
 "khung": P(5, 72.5) + P(68, 38.5), "nen_bien": [0.80, 0.88, 0.93], "chu_giai_xy": [0.03, 0.60],
 "vung_mau": g.dat([-20, 25, 100, 80]),
 "dia_danh": [
  tp(37.6, 55.75, "Mát-xcơ-va", 40.5, 55.2, True), tp(30.3, 59.94, "Pê-tơ-rô-grát", 30.3, 61.0), tp(33.1, 68.97, "Mu-rơ-man-xcơ", 38.5, 69.4),
  tp(40.5, 64.55, "Ác-khan-ghen", 45.0, 64.9), tp(33.5, 44.6, "Xê-va-xtô-pôn", 37.5, 44.0), tp(49.9, 40.4, "Ba-cu", 52.5, 40.1),
  {"ten": "NƯỚC NGA XÔ VIẾT", "vi_tri": P(46, 58.5), "lon": True}, {"ten": "BIỂN ĐEN", "vi_tri": P(34.5, 42.6), "dam": True},
  {"ten": "Vùng cách mạng kiểm soát năm 1919", "vi_tri": P(46, 57.0), "co": 14}
 ],
 "chu_giai": [{"loai": "mui_ten_dich", "nhan": "Quân đế quốc can thiệp"}, {"loai": "mui_ten_ta", "nhan": "Hướng quân Xô viết tấn công"}],
 "doi_tuong": {
  "a_bac": dich((0, 62.5), (10, 68.5), (20, 71.6), (32.5, 69.6)), "a_bac2": dich((22, 71.8), (34, 70.2), (40.2, 65.2)), "n_abac": nh(16, 68.6, "Quân Anh"),
  "a_ban": dich((10, 56.5), (20, 57.5), (29.3, 59.7)), "n_aban": nh(16.5, 58.6, "Quân Anh"),
  "bl": dich((15, 52.0), (21, 52.6), (27, 53.6)), "n_bl": nh(17.5, 53.6, "Quân Ba Lan"),
  "duc": dich((12, 49.0), (20, 49.4), (28, 50.6)), "n_duc": nh(15.5, 47.9, "Quân Đức"),
  "rm": dich((22, 45.6), (25.5, 46.8), (29, 48.0)), "n_rm": nh(22.5, 44.4, "Quân Ru-ma-ni"),
  "nam1": dich((26, 40.2), (30, 42.5), (33.2, 44.3)), "nam2": dich((27, 40.0), (32, 41.6), (38, 42.0)), "n_nam": nh(27.0, 38.9, "Quân Pháp, Anh, Thổ Nhĩ Kỳ"),
  "l_iu": {"loai": "lua", "diem": [P(39.2, 63.3)]}, "n_iu": nh(39.2, 62.2, "Quân I-u-đê-nhích", 13, "chu"),
  "l_cs": {"loai": "lua", "diem": [P(60.0, 57.5)]}, "n_cs": nh(60.0, 56.3, "Quân Côn-sắc", 13, "chu"),
  "l_dn": {"loai": "lua", "diem": [P(41.5, 48.8)]}, "n_dn": nh(42.5, 47.6, "Quân Đê-ni-kin", 13, "chu"),
  "l_vg": {"loai": "lua", "diem": [P(33.5, 47.8)]}, "n_vg": nh(32.0, 46.6, "Quân Van-ghen", 13, "chu"),
  "t_cs": ta((50, 57.2), (54, 57.4), (58.4, 57.5)), "t_dn": ta((40, 53.5), (40.8, 51.2), (41.3, 49.5)), "t_vg": ta((36, 52.5), (34.8, 50.2), (33.8, 48.4)),
  "t_bl": ta((32.5, 54.2), (30, 53.6), (27.8, 53.4)), "t_ak": ta((38.5, 59.8), (39.6, 61.6), (39.6, 62.9)), "t_mm": ta((34.4, 62.5), (33.8, 65.0), (33.3, 67.6)),
 },
 "pha": {
  "can_thiep": {"mo_dau": True, "zoom": [1.0, 1.05], "chu_giai": ["mui_ten_dich"], "moc": [{"chu": "1918 – 1920: 14 đế quốc can thiệp", "tu": 0.04, "den": 0.98}],
   "buoc": [{"id": "a_bac", "tu": 0.08, "den": 0.25}, {"id": "a_bac2", "tu": 0.1, "den": 0.28}, {"id": "n_abac", "tu": 0.2, "den": 0.28},
            {"id": "a_ban", "tu": 0.15, "den": 0.3}, {"id": "n_aban", "tu": 0.24, "den": 0.32}, {"id": "bl", "tu": 0.2, "den": 0.36}, {"id": "n_bl", "tu": 0.3, "den": 0.38},
            {"id": "duc", "tu": 0.22, "den": 0.38}, {"id": "n_duc", "tu": 0.32, "den": 0.4}, {"id": "rm", "tu": 0.25, "den": 0.4}, {"id": "n_rm", "tu": 0.34, "den": 0.42},
            {"id": "nam1", "tu": 0.28, "den": 0.45}, {"id": "nam2", "tu": 0.3, "den": 0.47}, {"id": "n_nam", "tu": 0.4, "den": 0.48},
            {"id": "l_iu", "tu": 0.55, "den": 0.62}, {"id": "n_iu", "tu": 0.56, "den": 0.63}, {"id": "l_cs", "tu": 0.6, "den": 0.67}, {"id": "n_cs", "tu": 0.61, "den": 0.68},
            {"id": "l_dn", "tu": 0.65, "den": 0.72}, {"id": "n_dn", "tu": 0.66, "den": 0.73}, {"id": "l_vg", "tu": 0.7, "den": 0.77}, {"id": "n_vg", "tu": 0.71, "den": 0.78}]},
  "phan_cong": {"zoom": [1.05, 1.1], "chu_giai": ["mui_ten_dich", "mui_ten_ta"],
   "hien": ["a_bac", "a_bac2", "n_abac", "a_ban", "n_aban", "bl", "n_bl", "duc", "n_duc", "rm", "n_rm", "nam1", "nam2", "n_nam", "l_iu", "n_iu", "l_cs", "n_cs", "l_dn", "n_dn", "l_vg", "n_vg"],
   "moc": [{"chu": "Hồng quân phản công (1919 – 1920)", "tu": 0.04, "den": 0.98}],
   "buoc": [{"id": "t_cs", "tu": 0.08, "den": 0.3}, {"id": "t_ak", "tu": 0.12, "den": 0.32}, {"id": "t_mm", "tu": 0.14, "den": 0.34}, {"id": "t_dn", "tu": 0.3, "den": 0.5},
            {"id": "t_vg", "tu": 0.35, "den": 0.55}, {"id": "t_bl", "tu": 0.4, "den": 0.58}],
   "bang": {"chu": "Cuối năm 1920: đánh tan thù trong, giặc ngoài", "tu": 0.66, "y": 0.70}},
 }
}
json.dump(S, open(f"{ROOT}/pipeline/maps/specs/nga-xo-viet-1918.json", "w"), ensure_ascii=False)
print("ok", len(S["vung_mau"]))
