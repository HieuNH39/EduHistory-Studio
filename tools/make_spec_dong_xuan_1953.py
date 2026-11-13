"""Sa bàn Kế hoạch Na-va và cuộc Tiến công chiến lược Đông – Xuân 1953 – 1954 (SGK LSĐL 9 tr. 75 – 76).
SGK không có lược đồ riêng cho Đông – Xuân: đây là bản đồ định vị vẽ bằng code, chỉ ghi các địa danh, mốc, hướng tiến công
có trong SGK (Tây Bắc – Lai Châu, Trung Lào – Thà Khẹt, Thượng Lào – Phong Xa-lì, Bắc Tây Nguyên – Kon Tum) và năm nơi Pháp
tập trung quân. Toạ độ gần đúng; nền Natural Earth 1:50m; luôn có quần đảo Hoàng Sa, Trường Sa."""
import json, sys
sys.path.insert(0, "/home/claude/eduhistory-studio/tools")
from make_vn_map import xy, nen, dao, ROOT
P = lambda lon, lat: xy(lon, lat)
L = lambda *pts: [P(*p) for p in pts]
def mh(x, y, ten, lech, **kw): return {"ten": ten, "vi_tri": P(x, y), "man_hinh": True, "lech": lech, **kw}
def nh(lon, lat, chu, co=15, mau="ta"): return {"loai": "nhan", "vi_tri": P(lon, lat), "chu": chu, "co": co, "mau": mau}
S = {
 "phien_ban": 2, "ten": "Đông – Xuân 1953 – 1954", "phu_de": "Phá sản bước đầu Kế hoạch Na-va",
 "nguon": "Bản đồ định vị vẽ bằng code theo SGK LSĐL 9, tr. 75 – 76; nền Natural Earth",
 "khung": P(99.5, 23.8) + P(116.5, 8.3), "nen_bien": [0.80, 0.88, 0.93], "chu_giai_xy": [0.03, 0.60], "sao_man_hinh": True, "lech_x": 0.08,
 "vung_mau": nen([95, 5, 120, 27]),
 "dia_danh": [
  mh(105.85, 21.03, "Hà Nội", [12, 2], kieu="diem", dam=True), mh(103.02, 21.39, "Điện Biên Phủ", [-12, 10], kieu="diem", dam=True),
  mh(104.80, 17.40, "Thà Khẹt", [-12, -6], kieu="diem"), mh(105.00, 16.65, "Xê-nô", [-12, 8], kieu="diem"),
  mh(102.10, 21.68, "Phong Xa-lì", [-12, -6], kieu="diem"), mh(102.13, 19.89, "Luông Pha-bang", [-12, 6], kieu="diem"),
  mh(101.98, 20.69, "Mường Sài", [-12, 0], kieu="diem"), mh(103.15, 22.05, "Lai Châu", [12, -10], kieu="diem"),
  mh(108.00, 14.35, "Kon Tum", [12, -4], kieu="diem"), mh(108.00, 13.98, "Plây-ku", [12, 8], kieu="diem"),
  mh(103.6, 18.6, "LÀO", [0, 0], lon=True), mh(104.8, 12.6, "CAM-PU-CHIA", [0, 0], lon=True), mh(101.0, 15.4, "THÁI LAN", [0, 0], lon=True),
  mh(107.5, 23.3, "TRUNG QUỐC", [0, 0], lon=True), mh(111.8, 13.4, "BIỂN ĐÔNG", [0, 0], lon=True)
 ] + dao(112.0, 16.5, "QĐ. Hoàng Sa") + dao(114.0, 9.6, "QĐ. Trường Sa", n=9, r=.8),
 "chu_giai": [{"loai": "mui_ten_ta", "nhan": "Quân ta tiến công"}, {"loai": "sao", "nhan": "Nơi ta giải phóng"},
              {"loai": "don_dich", "nhan": "Nơi Pháp tập trung quân"}, {"loai": "mui_ten_dich", "nhan": "Quân Pháp nhảy dù"}],
 "doi_tuong": {
  "f_bb": {"loai": "don_dich", "vi_tri": P(106.3, 20.6)}, "n_bb": nh(108.4, 20.2, "Đồng bằng Bắc Bộ", 17, "dich"),
  "n_44": nh(108.6, 19.45, "lúc cao điểm: 44 tiểu đoàn", 15, "dich"),
  "du_dbp": {"loai": "mui_ten_dich", "diem": L((102.3, 22.3), (102.95, 21.5)), "w0": 4, "w1": 8},
  "f_dbp": {"loai": "don_dich", "vi_tri": P(103.02, 21.39)},
  "t_lc": {"loai": "mui_ten_ta", "diem": L((104.7, 21.0), (103.9, 21.7), (103.25, 22.0)), "w0": 7, "w1": 12}, "s_lc": {"loai": "sao", "vi_tri": P(103.15, 22.05)},
  "t_tk": {"loai": "mui_ten_ta", "diem": L((106.0, 17.75), (105.4, 17.55), (104.9, 17.42)), "w0": 7, "w1": 12}, "s_tk": {"loai": "sao", "vi_tri": P(104.8, 17.4)},
  "f_xn": {"loai": "don_dich", "vi_tri": P(105.0, 16.65)},
  "t_px": {"loai": "mui_ten_ta", "diem": L((103.3, 21.0), (102.6, 21.5), (102.2, 21.66)), "w0": 7, "w1": 12}, "s_px": {"loai": "sao", "vi_tri": P(102.1, 21.68)},
  "f_lpb": {"loai": "don_dich", "vi_tri": P(102.13, 19.89)}, "f_ms": {"loai": "don_dich", "vi_tri": P(101.98, 20.69)},
  "t_kt": {"loai": "mui_ten_ta", "diem": L((107.3, 15.6), (107.75, 14.9), (107.98, 14.42)), "w0": 7, "w1": 12}, "s_kt": {"loai": "sao", "vi_tri": P(108.0, 14.35)},
  "f_pk": {"loai": "don_dich", "vi_tri": P(108.0, 13.98)},
 },
 "pha": {
  "na_va": {"mo_dau": True, "zoom": [1.0, 1.05], "chu_giai": ["don_dich"], "moc": [{"chu": "Từ giữa năm 1953: Kế hoạch Na-va", "tu": 0.04, "den": 0.98}],
   "buoc": [{"id": "f_bb", "tu": 0.35, "den": 0.45}, {"id": "n_bb", "tu": 0.38, "den": 0.48}, {"id": "n_44", "tu": 0.55, "den": 0.65}]},
  "tay_bac": {"zoom": [1.25, 1.35], "tam": P(105.5, 18.0), "can_giua": [0.5, 0.47], "chu_giai": ["mui_ten_dich", "mui_ten_ta", "sao"], "hien": ["f_bb", "n_bb"],
   "moc": [{"chu": "20 – 11 – 1953: Pháp nhảy dù xuống Điện Biên Phủ", "tu": 0.04, "den": 0.45}, {"chu": "Đầu 12 – 1953: tiến công Tây Bắc", "tu": 0.47, "den": 0.98}],
   "buoc": [{"id": "du_dbp", "tu": 0.08, "den": 0.25}, {"id": "f_dbp", "tu": 0.25, "den": 0.3}, {"id": "t_lc", "tu": 0.5, "den": 0.75}, {"id": "s_lc", "tu": 0.75, "den": 0.82}]},
  "trung_lao": {"zoom": [1.25, 1.35], "tam": P(105.5, 17.0), "can_giua": [0.5, 0.47], "chu_giai": ["mui_ten_ta", "sao", "don_dich"], "hien": ["f_bb", "n_bb", "f_dbp", "t_lc", "s_lc"],
   "moc": [{"chu": "Cuối năm 1953: Trung Lào", "tu": 0.04, "den": 0.98}],
   "buoc": [{"id": "t_tk", "tu": 0.15, "den": 0.45}, {"id": "s_tk", "tu": 0.45, "den": 0.52}, {"id": "f_xn", "tu": 0.65, "den": 0.72}]},
  "thuong_lao": {"zoom": [1.25, 1.35], "tam": P(104.5, 18.6), "can_giua": [0.5, 0.47], "chu_giai": ["mui_ten_ta", "sao", "don_dich"], "hien": ["f_bb", "n_bb", "f_dbp", "t_lc", "s_lc", "t_tk", "s_tk", "f_xn"],
   "moc": [{"chu": "1 – 1954: Thượng Lào", "tu": 0.04, "den": 0.98}],
   "buoc": [{"id": "t_px", "tu": 0.12, "den": 0.4}, {"id": "s_px", "tu": 0.4, "den": 0.48}, {"id": "f_lpb", "tu": 0.6, "den": 0.67}, {"id": "f_ms", "tu": 0.64, "den": 0.71}]},
  "tay_nguyen": {"zoom": [1.1, 1.18], "tam": P(106.0, 16.0), "can_giua": [0.5, 0.5], "chu_giai": ["mui_ten_ta", "sao", "don_dich"],
   "hien": ["f_bb", "n_bb", "f_dbp", "t_lc", "s_lc", "t_tk", "s_tk", "f_xn", "t_px", "s_px", "f_lpb", "f_ms"],
   "moc": [{"chu": "Đầu 2 – 1954: Bắc Tây Nguyên", "tu": 0.04, "den": 0.98}],
   "buoc": [{"id": "t_kt", "tu": 0.12, "den": 0.4}, {"id": "s_kt", "tu": 0.4, "den": 0.48}, {"id": "f_pk", "tu": 0.62, "den": 0.7}]},
  "phan_tan": {"zoom": [1.05, 1.0], "chu_giai": ["don_dich", "sao"],
   "hien": ["f_bb", "n_bb", "f_dbp", "s_lc", "s_tk", "f_xn", "s_px", "f_lpb", "s_kt", "f_pk"],
   "moc": [{"chu": "Pháp phân tán lực lượng thành 5 nơi", "tu": 0.04, "den": 0.98}],
   "bang": {"chu": "Phá sản bước đầu Kế hoạch Na-va", "tu": 0.62, "y": 0.70}},
 }
}
json.dump(S, open(f"{ROOT}/pipeline/maps/specs/dong-xuan-1953.json", "w"), ensure_ascii=False)
print("ok", len(S["vung_mau"]))
