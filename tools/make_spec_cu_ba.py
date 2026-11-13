"""Sa bàn 'Cách mạng Cu-ba (1952 – 1959)' – bản đồ định vị theo bảng 'Diễn biến chính của cách mạng Cu-ba' (SGK LSĐL 9 tr. 53)
và vị trí Cu-ba trên Hình 12.3 (Lược đồ một số nước ở khu vực Mỹ La-tinh). SGK không có lược đồ diễn biến: mũi tên chỉ minh hoạ
các bước trong bảng (sang Mê-hi-cô, trở về trên tàu Gran-ma, tổng công kích, tiến về La Ha-ba-na).
Nền đất liền Natural Earth 1:110m, không vẽ biên giới quốc gia."""
import json, sys
sys.path.insert(0, "/home/claude/eduhistory-studio/tools")
from make_geo_map import Geo, ROOT
g = Geo(-104, 32.5, 21); P = g.P
D = lambda *pts: [P(*p) for p in pts]
def nh(lon, lat, chu, co, mau="ta"): return {"loai": "nhan", "vi_tri": P(lon, lat), "chu": chu, "co": co, "mau": mau}
S = {
 "phien_ban": 2, "ten": "Cách mạng Cu-ba (1952 – 1959)", "phu_de": "Diễn biến chính",
 "nguon": "Bản đồ định vị theo bảng diễn biến và Hình 12.3, SGK Lịch sử và Địa lí 9, tr. 53; nền đất liền Natural Earth",
 "khung": P(-104, 32.5) + P(-66, 9.5), "nen_bien": [0.80, 0.88, 0.93], "chu_giai_xy": [0.03, 0.60],
 "vung_mau": g.dat([-130, 0, -40, 50]),
 "dia_danh": [
  {"ten": "MỸ", "vi_tri": P(-90, 30.6), "lon": True},
  {"ten": "MÊ-HI-CÔ", "vi_tri": P(-101.5, 22.5), "lon": True},
  {"ten": "CU-BA", "vi_tri": P(-79.2, 23.6), "co": 24, "dam": True},
  {"ten": "La Ha-ba-na", "vi_tri": P(-82.36, 23.13), "kieu": "diem", "nhan": P(-83.6, 23.8), "dam": True},
  {"ten": "ĐẠI TÂY DƯƠNG", "vi_tri": P(-71.5, 25.0), "dam": True},
  {"ten": "Vịnh Mê-hi-cô", "vi_tri": P(-93.5, 26.0), "dam": True},
  {"ten": "Biển Ca-ri-bê", "vi_tri": P(-76, 14.5), "dam": True}
 ],
 "chu_giai": [{"loai": "mui_ten_ta", "nhan": "Hoạt động của lực lượng cách mạng"}, {"loai": "rut_lui", "nhan": "Phi-đen bị trục xuất (1955)"},
              {"loai": "don_dich", "nhan": "Pháo đài Môn-ca-đa"}, {"loai": "sao", "nhan": "Cách mạng thắng lợi"}],
 "doi_tuong": {
  "n_bt": nh(-82.5, 19.0, "3 – 1952: chế độ độc tài Ba-ti-xta", 18, "dich"),
  "moncada": {"loai": "don_dich", "vi_tri": P(-75.83, 20.02)},
  "n_mc": nh(-75.3, 18.6, "Pháo đài Môn-ca-đa", 14, "dich"),
  "mc_atk": {"loai": "mui_ten_ta", "diem": D((-77.2, 19.4), (-76.5, 19.6), (-75.95, 19.95)), "w0": 6, "w1": 11},
  "truc_xuat": {"loai": "rut_lui", "diem": D((-82.6, 23.3), (-86.0, 22.9), (-91.0, 22.5), (-95.6, 19.8)), "w0": 4},
  "n_26": nh(-96.4, 18.0, "Phong trào 26 – 7", 15),
  "granma": {"loai": "mui_ten_ta", "diem": D((-95.4, 20.6), (-91.5, 22.4), (-86.6, 22.4), (-84.6, 20.7), (-80.6, 19.5), (-77.9, 19.9)), "w0": 7, "w1": 13},
  "n_gm": nh(-86.0, 18.6, "11 – 1956: tàu Gran-ma, 81 chiến sĩ", 16),
  "cong_kich1": {"loai": "mui_ten_ta", "diem": D((-76.6, 20.3), (-78.4, 21.3), (-80.2, 22.2)), "w0": 7, "w1": 12},
  "cong_kich2": {"loai": "mui_ten_ta", "diem": D((-80.2, 22.2), (-81.4, 22.7), (-82.2, 23.05)), "w0": 8, "w1": 14},
  "sao_hb": {"loai": "sao", "vi_tri": P(-82.36, 23.13)}
 },
 "pha": {
  "vi_tri": {"mo_dau": True, "zoom": [1.15, 1.3], "tam": P(-84, 22), "can_giua": [0.5, 0.47], "chu_giai": [], "buoc": [{"id": "n_bt", "tu": 0.62, "den": 0.72}]},
  "mon_ca_da": {"zoom": [2.0, 2.15], "tam": P(-77.5, 20.6), "can_giua": [0.52, 0.47], "chu_giai": ["mui_ten_ta", "don_dich"], "hien": [],
   "moc": [{"chu": "Tháng 7 – 1953", "tu": 0.03, "den": 0.98}],
   "buoc": [{"id": "moncada", "tu": 0.1, "den": 0.2}, {"id": "n_mc", "tu": 0.12, "den": 0.22}, {"id": "mc_atk", "tu": 0.35, "den": 0.65}]},
  "me_hi_co": {"zoom": [1.15, 1.22], "tam": P(-86, 21), "can_giua": [0.5, 0.47], "chu_giai": ["rut_lui"], "hien": ["moncada"],
   "moc": [{"chu": "Năm 1955", "tu": 0.03, "den": 0.98}],
   "buoc": [{"id": "truc_xuat", "tu": 0.1, "den": 0.45}, {"id": "n_26", "tu": 0.55, "den": 0.65}]},
  "gran_ma": {"zoom": [1.15, 1.22], "tam": P(-86, 21), "can_giua": [0.5, 0.47], "chu_giai": ["mui_ten_ta"], "hien": ["moncada", "n_26"],
   "moc": [{"chu": "Tháng 11 – 1956", "tu": 0.03, "den": 0.98}],
   "buoc": [{"id": "granma", "tu": 0.1, "den": 0.6}, {"id": "n_gm", "tu": 0.4, "den": 0.5}]},
  "toan_thang": {"zoom": [1.9, 2.05], "tam": P(-79.3, 21.6), "can_giua": [0.5, 0.47], "chu_giai": ["mui_ten_ta", "sao"], "hien": ["moncada"],
   "moc": [{"chu": "Cuối năm 1958", "tu": 0.03, "den": 0.45}, {"chu": "Ngày 1 – 1 – 1959", "tu": 0.47, "den": 0.98}],
   "buoc": [{"id": "cong_kich1", "tu": 0.08, "den": 0.38}, {"id": "cong_kich2", "tu": 0.5, "den": 0.68}, {"id": "sao_hb", "tu": 0.7, "den": 0.8}],
   "bang": {"chu": "Chế độ độc tài Ba-ti-xta bị lật đổ", "tu": 0.82, "y": 0.70}}
 }
}
json.dump(S, open(f"{ROOT}/pipeline/maps/specs/cu-ba.json", "w"), ensure_ascii=False)
print("ok", len(S["vung_mau"]))
