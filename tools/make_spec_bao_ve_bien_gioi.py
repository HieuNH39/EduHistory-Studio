"""Sa bàn 'Bảo vệ biên giới Tây Nam và biên giới phía Bắc (1975 – 1989)' – bản đồ định vị theo SGK LSĐL 9 tr. 102 – 103.
SGK không có lược đồ cho mục này: chỉ đánh dấu các địa danh, mốc có trong SGK; toạ độ gần đúng; nền Natural Earth 1:50m;
luôn có quần đảo Hoàng Sa, Trường Sa. Mũi tên chỉ thể hiện ý 'tấn công Tây Ninh' và 'tổng phản công' của SGK."""
import json, sys
sys.path.insert(0, "/home/claude/eduhistory-studio/tools")
from make_vn_map import xy, nen, dao, ROOT
P = lambda lon, lat: xy(lon, lat)
L = lambda *pts: [P(*p) for p in pts]
def mh(x, y, ten, lech, **kw): return {"ten": ten, "vi_tri": P(x, y), "man_hinh": True, "lech": lech, **kw}
def nh(x, y, chu, co=15, mau="ta"): return {"loai": "nhan", "vi_tri": P(x, y), "chu": chu, "co": co, "mau": mau}
def diem(x, y): return {"loai": "sao", "vi_tri": P(x, y)}
S = {
 "phien_ban": 2, "ten": "Bảo vệ biên giới (1975 – 1989)", "phu_de": "Biên giới Tây Nam và biên giới phía Bắc",
 "nguon": "Bản đồ định vị vẽ bằng code theo SGK LSĐL 9, tr. 102 – 103; nền Natural Earth",
 "khung": P(99.5, 25.8) + P(116.5, 8.3), "nen_bien": [0.80, 0.88, 0.93], "chu_giai_xy": [0.03, 0.60], "sao_man_hinh": True, "lech_x": 0.08,
 "vung_mau": nen([95, 5, 120, 27]),
 "dia_danh": [
  mh(105.85, 21.03, "Hà Nội", [12, 2], kieu="diem", dam=True), mh(106.70, 10.78, "TP. Hồ Chí Minh", [12, 8], kieu="diem"),
  mh(104.8, 12.6, "CAM-PU-CHIA", [0, 0], lon=True), mh(103.6, 18.6, "LÀO", [0, 0], lon=True), mh(107.5, 23.3, "TRUNG QUỐC", [0, 0], lon=True),
  mh(111.8, 13.4, "BIỂN ĐÔNG", [0, 0], lon=True)
 ] + dao(112.0, 16.5, "QĐ. Hoàng Sa") + dao(114.0, 9.6, "QĐ. Trường Sa", n=9, r=.8),
 "chu_giai": [{"loai": "mui_ten_dich", "nhan": "Quân Pôn Pốt tấn công"}, {"loai": "mui_ten_ta", "nhan": "Quân đội Việt Nam tổng phản công"},
              {"loai": "sao", "nhan": "Địa danh được nêu trong SGK"}, {"loai": "tuong", "nhan": "Tuyến biên giới phía Bắc"}],
 "doi_tuong": {
  # Tây Nam
  "s_pq": diem(103.95, 10.23), "n_pq": nh(102.9, 10.6, "Đảo Phú Quốc", 15, "chu"),
  "s_tc": diem(103.47, 9.30), "n_tc": nh(102.5, 9.0, "Đảo Thổ Chu", 15, "chu"),
  "s_ag": diem(105.13, 10.52), "n_ag": nh(105.6, 10.0, "An Giang", 15, "chu"),
  "s_tn": diem(106.10, 11.31), "n_tn": nh(106.9, 11.75, "Tây Ninh", 15, "chu"),
  "d_tn": {"loai": "mui_ten_dich", "diem": L((104.9, 11.6), (105.5, 11.45), (106.0, 11.33)), "w0": 4, "w1": 8},
  "t_pc": {"loai": "mui_ten_ta", "diem": L((106.2, 11.0), (105.7, 11.0), (105.25, 11.15)), "w0": 7, "w1": 12},
  # phía Bắc
  "bg": {"loai": "tuong", "diem": L((103.35, 22.62), (104.0, 22.62), (104.9, 22.85), (105.6, 23.05), (106.3, 22.85), (106.7, 22.4), (106.9, 21.95), (107.4, 21.65), (107.97, 21.55)), "phia": 1},
  "s_mc": diem(107.97, 21.53), "n_mc": nh(108.7, 21.25, "Móng Cái", 12, "chu"),
  "s_pt": diem(103.35, 22.53), "n_pt": nh(102.6, 22.95, "Phong Thổ", 12, "chu"),
  "s_ls": diem(106.76, 21.85), "n_ls": nh(107.3, 21.2, "Lạng Sơn", 12, "chu"),
  "s_cb": diem(106.26, 22.67), "n_cb": nh(106.75, 23.05, "Cao Bằng", 12, "chu"),
  "s_lc": diem(103.97, 22.48), "n_lc": nh(104.0, 22.1, "Lào Cai", 12, "chu"),
  "s_vx": diem(104.98, 22.67), "n_vx": nh(105.0, 23.15, "Vị Xuyên", 13, "ta"),
 },
 "pha": {
  "tay_nam": {"mo_dau": True, "zoom": [1.3, 1.4], "tam": P(106.0, 12.0), "can_giua": [0.5, 0.5], "chu_giai": ["sao", "mui_ten_dich", "mui_ten_ta"],
   "moc": [{"chu": "Sau năm 1975: Pôn Pốt khiêu khích, xâm phạm", "tu": 0.04, "den": 0.4}, {"chu": "12 – 1978: tấn công Tây Ninh", "tu": 0.42, "den": 0.7}, {"chu": "23 – 12 – 1978: tổng phản công", "tu": 0.72, "den": 0.98}],
   "buoc": [{"id": "s_pq", "tu": 0.08, "den": 0.14}, {"id": "n_pq", "tu": 0.09, "den": 0.15}, {"id": "s_tc", "tu": 0.13, "den": 0.19}, {"id": "n_tc", "tu": 0.14, "den": 0.2},
            {"id": "s_ag", "tu": 0.22, "den": 0.28}, {"id": "n_ag", "tu": 0.23, "den": 0.29}, {"id": "s_tn", "tu": 0.27, "den": 0.33}, {"id": "n_tn", "tu": 0.28, "den": 0.34},
            {"id": "d_tn", "tu": 0.45, "den": 0.65}, {"id": "t_pc", "tu": 0.75, "den": 0.92}]},
  "phia_bac": {"zoom": [1.75, 1.85], "tam": P(105.6, 21.2), "can_giua": [0.5, 0.56], "chu_giai": ["tuong", "sao"],
   "moc": [{"chu": "17 – 2 – 1979", "tu": 0.04, "den": 0.6}, {"chu": "5 – 3 – 1979: Trung Quốc tuyên bố rút quân", "tu": 0.62, "den": 0.98}],
   "buoc": [{"id": "bg", "tu": 0.08, "den": 0.4}, {"id": "s_mc", "tu": 0.12, "den": 0.18}, {"id": "n_mc", "tu": 0.13, "den": 0.19}, {"id": "s_pt", "tu": 0.36, "den": 0.42}, {"id": "n_pt", "tu": 0.37, "den": 0.43},
            {"id": "s_ls", "tu": 0.48, "den": 0.53}, {"id": "n_ls", "tu": 0.49, "den": 0.54}, {"id": "s_cb", "tu": 0.52, "den": 0.57}, {"id": "n_cb", "tu": 0.53, "den": 0.58},
            {"id": "s_lc", "tu": 0.56, "den": 0.61}, {"id": "n_lc", "tu": 0.57, "den": 0.62}]},
  "vi_xuyen": {"zoom": [1.85, 2.0], "tam": P(105.4, 21.6), "can_giua": [0.5, 0.56], "chu_giai": ["tuong", "sao"], "hien": ["bg", "s_mc", "n_mc", "s_pt", "n_pt", "s_ls", "n_ls", "s_cb", "n_cb", "s_lc", "n_lc"],
   "moc": [{"chu": "Đến cuối những năm 80: mặt trận Vị Xuyên", "tu": 0.04, "den": 0.98}],
   "buoc": [{"id": "s_vx", "tu": 0.15, "den": 0.25}, {"id": "n_vx", "tu": 0.17, "den": 0.27}]},
 }
}
json.dump(S, open(f"{ROOT}/pipeline/maps/specs/bao-ve-bien-gioi.json", "w"), ensure_ascii=False)
print("ok", len(S["vung_mau"]))
