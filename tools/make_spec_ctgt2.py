"""Sa bàn Chiến tranh thế giới thứ hai – giai đoạn II (SGK LSĐL 9 tr. 19–20): châu Âu và châu Á – Thái Bình Dương."""
import json, sys
sys.path.insert(0, "/home/claude/eduhistory-studio/tools")
from make_geo_map import Geo, ROOT
g = Geo(-14, 63.5, 50); P = g.P
EU = {
 "phien_ban": 2, "ten": "Đồng minh phản công (1942 – 1945)", "phu_de": "Mặt trận châu Âu",
 "nguon": "Sơ đồ minh hoạ theo SGK Lịch sử và Địa lí 9, Bài 4, tr. 19–20; nền đất liền Natural Earth",
 "khung": P(-14, 63.5) + P(56, 38.2), "nen_bien": [0.80, 0.88, 0.93], "chu_giai_xy": [0.03, 0.66],
 "vung_mau": g.dat([-30, 25, 70, 75]),
 "dia_danh": [
  {"ten": "Xta-lin-grát", "vi_tri": P(44.5, 48.7), "kieu": "diem", "nhan": P(48.6, 49.6), "dam": True},
  {"ten": "Mát-xcơ-va", "vi_tri": P(37.6, 55.75), "kieu": "diem", "nhan": P(37.6, 56.6)},
  {"ten": "Béc-lin", "vi_tri": P(13.4, 52.5), "kieu": "diem", "nhan": P(13.4, 53.4), "dam": True},
  {"ten": "Noóc-măng-đi", "vi_tri": P(-0.6, 49.3), "kieu": "diem", "nhan": P(-3.6, 48.3), "dam": True},
  {"ten": "Pa-ri", "vi_tri": P(2.35, 48.86), "kieu": "diem", "nhan": P(3.6, 48.2)},
  {"ten": "Luân Đôn", "vi_tri": P(-0.12, 51.5), "kieu": "diem", "nhan": P(-1.6, 52.2)},
  {"ten": "LIÊN XÔ", "vi_tri": P(42, 58.5), "lon": True}, {"ten": "ĐỨC", "vi_tri": P(10.5, 50.8), "lon": True},
  {"ten": "PHÁP", "vi_tri": P(3.2, 46.6), "lon": True}, {"ten": "ANH", "vi_tri": P(-2.0, 54.2), "lon": True}
 ],
 "chu_giai": [{"loai": "mui_ten_ta", "nhan": "Quân Đồng minh phản công"}, {"loai": "rut_chay", "nhan": "Quân phát xít rút chạy"}, {"loai": "sao", "nhan": "Thắng lợi quyết định"}],
 "doi_tuong": {
  "xt1": {"loai": "mui_ten_ta", "diem": [P(41.5, 51.0), P(43.2, 49.8), P(44.0, 48.9)], "w0": 7, "w1": 13},
  "xt2": {"loai": "mui_ten_ta", "diem": [P(46.5, 46.6), P(45.3, 47.8), P(44.7, 48.5)], "w0": 7, "w1": 13},
  "sao_xt": {"loai": "sao", "vi_tri": P(44.5, 48.7)},
  "n_xt": {"loai": "nhan", "vi_tri": P(42.5, 45.2), "chu": "Bước ngoặt: chuyển từ phòng ngự sang phản công", "co": 19, "mau": "ta"},
  "rut1": {"loai": "rut_chay", "diem": [P(42, 48.5), P(36, 49), P(30, 50.5)], "w0": 4},
  "nm": {"loai": "mui_ten_ta", "diem": [P(-1.5, 51.0), P(-1.0, 50.1), P(-0.6, 49.4)], "w0": 8, "w1": 14},
  "nm2": {"loai": "mui_ten_ta", "diem": [P(-0.6, 49.2), P(1.2, 48.9), P(2.3, 48.9)], "w0": 6, "w1": 11},
  "n_nm": {"loai": "nhan", "vi_tri": P(-7.5, 46.4), "chu": "Mở mặt trận thứ hai ở Tây Âu", "co": 19, "mau": "ta"},
  "bl_dong": {"loai": "mui_ten_ta", "diem": [P(28, 52.5), P(21, 52.6), P(14.2, 52.5)], "w0": 9, "w1": 16},
  "bl_tay": {"loai": "mui_ten_ta", "diem": [P(4, 50.5), P(8.5, 51.5), P(12.4, 52.3)], "w0": 7, "w1": 13},
  "sao_bl": {"loai": "sao", "vi_tri": P(13.4, 52.5)}
 },
 "pha": {
  "xtalingrat": {"mo_dau": True, "zoom": [1.0, 1.15], "tam": P(40, 50), "can_giua": [0.55, 0.47], "chu_giai": ["mui_ten_ta", "rut_chay", "sao"],
   "moc": [{"chu": "11 – 1942 đến 2 – 1943", "tu": 0.05, "den": 0.95}],
   "buoc": [{"id": "xt1", "tu": 0.12, "den": 0.35}, {"id": "xt2", "tu": 0.14, "den": 0.37}, {"id": "sao_xt", "tu": 0.4, "den": 0.5}, {"id": "rut1", "tu": 0.5, "den": 0.72}, {"id": "n_xt", "tu": 0.74, "den": 0.84}]},
  "noocmangdi": {"zoom": [1.2, 1.35], "tam": P(1, 50), "can_giua": [0.52, 0.47], "chu_giai": ["mui_ten_ta"], "hien": ["sao_xt"],
   "moc": [{"chu": "Tháng 6 – 1944", "tu": 0.05, "den": 0.95}],
   "buoc": [{"id": "nm", "tu": 0.1, "den": 0.4}, {"id": "nm2", "tu": 0.45, "den": 0.7}, {"id": "n_nm", "tu": 0.72, "den": 0.82}]},
  "beclin": {"zoom": [1.05, 1.1], "tam": P(18, 51), "can_giua": [0.52, 0.47], "chu_giai": ["mui_ten_ta", "sao"], "hien": ["sao_xt", "nm", "nm2"],
   "moc": [{"chu": "16 – 4 – 1945: Chiến dịch Béc-lin", "tu": 0.05, "den": 0.7}],
   "buoc": [{"id": "bl_dong", "tu": 0.1, "den": 0.45}, {"id": "bl_tay", "tu": 0.2, "den": 0.5}, {"id": "sao_bl", "tu": 0.55, "den": 0.65}],
   "bang": {"chu": "9 – 5 – 1945: Đức đầu hàng không điều kiện", "tu": 0.75}}
 }
}
json.dump(EU, open(f"{ROOT}/pipeline/maps/specs/ctgt2-chau-au.json", "w"), ensure_ascii=False)
g2 = Geo(96, 52.5, 38); Q = g2.P
AS = {
 "phien_ban": 2, "ten": "Chiến tranh kết thúc ở châu Á", "phu_de": "Tháng 8 – 1945",
 "nguon": "Sơ đồ minh hoạ theo SGK Lịch sử và Địa lí 9, Bài 4, tr. 20; nền đất liền Natural Earth",
 "khung": Q(96, 52.5) + Q(154.6, 26.5), "nen_bien": [0.80, 0.88, 0.93], "chu_giai_xy": [0.03, 0.66],
 "vung_mau": g2.dat([80, 5, 170, 70]),
 "dia_danh": [
  {"ten": "Hi-rô-si-ma", "vi_tri": Q(132.45, 34.4), "kieu": "diem", "nhan": Q(131.0, 33.2), "dam": True},
  {"ten": "Na-ga-sa-ki", "vi_tri": Q(129.87, 32.75), "kieu": "diem", "nhan": Q(127.5, 31.8), "dam": True},
  {"ten": "Tô-ki-ô", "vi_tri": Q(139.7, 35.7), "kieu": "diem", "nhan": Q(141.5, 35.0)},
  {"ten": "NHẬT BẢN", "vi_tri": Q(138.5, 38.5), "lon": True}, {"ten": "LIÊN XÔ", "vi_tri": Q(136, 50.2), "lon": True},
  {"ten": "Đông Bắc Trung Quốc", "vi_tri": Q(125.5, 43.3), "dam": True}, {"ten": "THÁI BÌNH DƯƠNG", "vi_tri": Q(147, 34), "lon": True}
 ],
 "chu_giai": [{"loai": "mui_ten_ta", "nhan": "Hồng quân Liên Xô tấn công"}],
 "doi_tuong": {
  "lx1": {"loai": "mui_ten_ta", "diem": [Q(117, 50), Q(121, 47.5), Q(124, 45.5)], "w0": 8, "w1": 14},
  "lx2": {"loai": "mui_ten_ta", "diem": [Q(133, 46), Q(130, 45.3), Q(127, 45)], "w0": 8, "w1": 14},
  "lx3": {"loai": "mui_ten_ta", "diem": [Q(127.5, 51), Q(127, 48.5), Q(126, 46.5)], "w0": 8, "w1": 14},
  "n_lx": {"loai": "nhan", "vi_tri": Q(116, 40.2), "chu": "8 – 8: tấn công quân Nhật ở Đông Bắc Trung Quốc", "co": 19, "mau": "ta"},
  "n_hr": {"loai": "nhan", "vi_tri": Q(137, 30.6), "chu": "6 và 9 – 8: hai quả bom nguyên tử", "co": 19, "mau": "dich"}
 },
 "pha": {
  "thang8": {"mo_dau": True, "zoom": [1.0, 1.05], "chu_giai": ["mui_ten_ta"],
   "moc": [{"chu": "Tháng 8 – 1945", "tu": 0.05, "den": 0.75}],
   "buoc": [{"id": "n_hr", "tu": 0.1, "den": 0.2}, {"id": "lx1", "tu": 0.3, "den": 0.55}, {"id": "lx2", "tu": 0.32, "den": 0.57}, {"id": "lx3", "tu": 0.34, "den": 0.59}, {"id": "n_lx", "tu": 0.6, "den": 0.7}],
   "bang": {"chu": "15 – 8 – 1945: Nhật Bản đầu hàng không điều kiện", "tu": 0.8}}
 }
}
json.dump(AS, open(f"{ROOT}/pipeline/maps/specs/ctgt2-chau-a.json", "w"), ensure_ascii=False)
print("ok")
