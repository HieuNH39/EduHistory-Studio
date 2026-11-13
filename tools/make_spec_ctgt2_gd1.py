"""Sa bàn Chiến tranh thế giới thứ hai – giai đoạn I (1 – 9 – 1939 đến 11 – 1942), mặt trận châu Âu.
Vẽ lại, giản lược theo Hình 4.3 'Lược đồ quân Đức đánh chiếm châu Âu (1939 – 1941)', SGK LSĐL 9 tr. 19; mốc theo nội dung tr. 19.
Nền đất liền Natural Earth 1:110m, không vẽ biên giới quốc gia (chỉ ghi tên nước như lược đồ SGK)."""
import json, sys
sys.path.insert(0, "/home/claude/eduhistory-studio/tools")
from make_geo_map import Geo, ROOT
g = Geo(-12, 64.5, 52); P = g.P
def nuoc(lon, lat, ten, co=17): return {"ten": ten, "vi_tri": P(lon, lat), "co": co, "dam": True}
def tp(lon, lat, ten, nlon, nlat, dam=False): return {"ten": ten, "vi_tri": P(lon, lat), "kieu": "diem", "nhan": P(nlon, nlat), "dam": dam}
def ten(lon, lat, chu, co=16, mau="dich"): return {"loai": "nhan", "vi_tri": P(lon, lat), "chu": chu, "co": co, "mau": mau}
D = lambda *pts: [P(*p) for p in pts]
S = {
 "phien_ban": 2, "ten": "Quân Đức đánh chiếm châu Âu", "phu_de": "Giai đoạn I (1939 – 1941)",
 "nguon": "Vẽ lại, giản lược theo Hình 4.3, SGK Lịch sử và Địa lí 9, tr. 19; nền đất liền Natural Earth",
 "khung": P(-12, 64.5) + P(50, 36.0), "nen_bien": [0.80, 0.88, 0.93], "chu_giai_xy": [0.03, 0.58],
 "vung_mau": g.dat([-30, 25, 70, 75]),
 "dia_danh": [
  tp(13.4, 52.5, "Béc-lin", 13.4, 53.3, True), tp(21.0, 52.23, "Vác-sa-va", 23.4, 51.7),
  tp(2.35, 48.86, "Pa-ri", 3.9, 48.4), tp(-0.12, 51.5, "Luân Đôn", -1.4, 52.2), tp(-0.58, 44.84, "Boóc-đô", -3.0, 44.6),
  tp(30.3, 59.94, "Lê-nin-grát", 34.0, 60.4), tp(37.6, 55.75, "Mát-xcơ-va", 41.5, 55.6, True), tp(30.5, 50.45, "Ki-ép", 32.6, 49.7),
  nuoc(10.0, 51.0, "ĐỨC"), nuoc(18.6, 53.9, "BA LAN"), nuoc(2.6, 46.6, "PHÁP"), nuoc(-1.8, 53.6, "ANH"),
  nuoc(39.0, 52.4, "LIÊN XÔ", 22), nuoc(12.6, 42.9, "I-TA-LI-A"), nuoc(9.0, 61.2, "NA UY"),
  nuoc(19.6, 44.2, "NAM TƯ"), nuoc(22.0, 39.6, "HY LẠP"), nuoc(5.4, 52.6, "HÀ LAN", 13), nuoc(4.4, 50.5, "BỈ", 13),
  {"ten": "ĐẠI TÂY DƯƠNG", "vi_tri": P(-7.5, 47.5), "dam": True}, {"ten": "ĐỊA TRUNG HẢI", "vi_tri": P(6.0, 38.6), "dam": True},
  {"ten": "BIỂN ĐEN", "vi_tri": P(34.0, 43.3), "dam": True}
 ],
 "chu_giai": [{"loai": "mui_ten_dich", "nhan": "Hướng tấn công của quân Đức"}],
 "doi_tuong": {
  "bl1": {"loai": "mui_ten_dich", "diem": D((14.6, 52.4), (17.6, 52.6), (20.4, 52.3)), "w0": 6, "w1": 11},
  "bl2": {"loai": "mui_ten_dich", "diem": D((18.0, 49.4), (19.6, 50.6), (20.7, 51.8)), "w0": 6, "w1": 11},
  "n_bl": ten(16.0, 50.6, "1 – 9 – 1939"),
  "hl": {"loai": "mui_ten_dich", "diem": D((8.0, 52.2), (6.8, 52.3), (5.6, 52.1)), "w0": 5, "w1": 9},
  "ph1": {"loai": "mui_ten_dich", "diem": D((7.2, 50.6), (5.0, 50.2), (2.8, 49.2)), "w0": 6, "w1": 11},
  "ph2": {"loai": "mui_ten_dich", "diem": D((2.2, 48.6), (1.0, 46.8), (-0.3, 45.2)), "w0": 6, "w1": 11},
  "anh": {"loai": "mui_ten_dich", "diem": D((2.0, 50.6), (1.0, 51.0), (0.3, 51.3)), "w0": 5, "w1": 9},
  "n_ph": ten(7.4, 47.6, "4 – 7 – 1940"),
  "nt": {"loai": "mui_ten_dich", "diem": D((15.6, 47.6), (17.6, 46.0), (19.2, 44.9)), "w0": 6, "w1": 11},
  "hyl": {"loai": "mui_ten_dich", "diem": D((21.4, 42.6), (22.0, 41.2), (22.6, 39.9)), "w0": 6, "w1": 11},
  "lx1": {"loai": "mui_ten_dich", "diem": D((21.8, 55.0), (26.0, 57.6), (29.9, 59.6)), "w0": 7, "w1": 13},
  "lx2": {"loai": "mui_ten_dich", "diem": D((24.0, 53.6), (30.0, 54.8), (36.6, 55.6)), "w0": 8, "w1": 14},
  "lx3": {"loai": "mui_ten_dich", "diem": D((24.0, 50.6), (27.2, 50.6), (30.1, 50.5)), "w0": 7, "w1": 13},
  "n_lx": ten(31.5, 52.6, "22 – 6 – 1941", 16)
 },
 "pha": {
  "ba_lan": {"mo_dau": True, "zoom": [1.0, 1.08], "tam": P(16, 52), "can_giua": [0.5, 0.47], "chu_giai": ["mui_ten_dich"],
   "moc": [{"chu": "1 – 9 – 1939", "tu": 0.05, "den": 0.98}],
   "buoc": [{"id": "bl1", "tu": 0.45, "den": 0.75}, {"id": "bl2", "tu": 0.5, "den": 0.8}, {"id": "n_bl", "tu": 0.78, "den": 0.86}]},
  "phap": {"zoom": [1.35, 1.45], "tam": P(4, 50), "can_giua": [0.5, 0.47], "chu_giai": ["mui_ten_dich"], "hien": ["bl1", "bl2"],
   "moc": [{"chu": "Tháng 4 – 7 – 1940", "tu": 0.05, "den": 0.98}],
   "buoc": [{"id": "hl", "tu": 0.12, "den": 0.3}, {"id": "ph1", "tu": 0.15, "den": 0.4}, {"id": "ph2", "tu": 0.4, "den": 0.62},
            {"id": "n_ph", "tu": 0.5, "den": 0.6}, {"id": "anh", "tu": 0.7, "den": 0.85}]},
  "mua_he_1941": {"zoom": [1.0, 1.04], "chu_giai": ["mui_ten_dich"], "hien": ["bl1", "bl2", "hl", "ph1", "ph2", "anh"],
   "moc": [{"chu": "Mùa hè 1941", "tu": 0.05, "den": 0.98}],
   "buoc": [{"id": "nt", "tu": 0.1, "den": 0.35}, {"id": "hyl", "tu": 0.15, "den": 0.4}],
   "bang": {"chu": "Đức chiếm hầu hết các nước tư bản châu Âu", "tu": 0.5, "y": 0.70}},
  "lien_xo": {"zoom": [1.25, 1.35], "tam": P(29, 55), "can_giua": [0.55, 0.47], "chu_giai": ["mui_ten_dich"], "hien": ["bl1", "bl2"],
   "moc": [{"chu": "22 – 6 – 1941: Đức tấn công Liên Xô", "tu": 0.05, "den": 0.6}],
   "buoc": [{"id": "lx1", "tu": 0.12, "den": 0.4}, {"id": "lx2", "tu": 0.14, "den": 0.45}, {"id": "lx3", "tu": 0.16, "den": 0.42}, {"id": "n_lx", "tu": 0.3, "den": 0.4}],
   "bang": {"chu": "Tháng 10 – 1941: quân Đức uy hiếp Mát-xcơ-va", "tu": 0.65, "y": 0.70}}
 }
}
json.dump(S, open(f"{ROOT}/pipeline/maps/specs/ctgt2-giai-doan-1.json", "w"), ensure_ascii=False)
print("ok", len(S["vung_mau"]))
