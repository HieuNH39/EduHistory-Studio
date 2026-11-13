"""Sa bàn 'Chiến tranh lạnh' – bản đồ định vị các khu vực đối đầu (SGK LSĐL 9, Bài 9, bảng tr. 42, Hình 9.2 tr. 43).
SGK không có lược đồ cho mục này: đây là bản đồ định vị vẽ bằng code, chỉ ghi các nội dung có trong bảng SGK.
Nền đất liền Natural Earth 1:110m, không vẽ biên giới quốc gia. Màu quy ước: xanh chàm = Mỹ và các nước tư bản chủ nghĩa,
đỏ = Liên Xô và các nước xã hội chủ nghĩa (như hai cột của bảng SGK). Luôn vẽ quần đảo Hoàng Sa, Trường Sa của Việt Nam."""
import json, sys, random
sys.path.insert(0, "/home/claude/eduhistory-studio/tools")
from make_geo_map import Geo, ROOT
g = Geo(-112, 70, 35); P = g.P
def nh(lon, lat, chu, co, mau="chu"): return {"loai": "nhan", "vi_tri": P(lon, lat), "chu": chu, "co": co, "mau": mau}
def mh(lon, lat, ten, lech, zt=0, zd=99, **kw):
    return {"ten": ten, "vi_tri": P(lon, lat), "man_hinh": True, "lech": lech, "zoom_tu": zt, "zoom_den": zd, **kw}
def dao(lon, lat, ten, n=6, r=0.6):
    random.seed(int(lon * 100 + lat)); out = []
    for i in range(n):
        out.append({"ten": "", "vi_tri": P(lon + random.uniform(-r, r), lat + random.uniform(-r, r)), "kieu": "diem", "man_hinh": True, "lech": [0, 0]})
    out.append(mh(lon, lat, ten, [14, -16], co=15))
    return out
S = {
 "phien_ban": 2, "ten": "Chiến tranh lạnh (1947 – 1989)", "phu_de": "Những khu vực đối đầu",
 "nguon": "Bản đồ định vị vẽ bằng code theo bảng SGK Lịch sử và Địa lí 9, Bài 9, tr. 42; nền đất liền Natural Earth",
 "khung": P(-112, 70) + P(152, 2), "nen_bien": [0.80, 0.88, 0.93], "chu_giai_xy": [0.03, 0.62], "sao_man_hinh": True,
 "vung_mau": g.dat([-180, -60, 180, 85]),
 "dia_danh": dao(112.0, 16.5, "QĐ. Hoàng Sa") + dao(114.0, 9.6, "QĐ. Trường Sa", n=8, r=1.0) + [
  mh(-40, 33, "ĐẠI TÂY DƯƠNG", [0, 0], co=17, zd=1.6), mh(-150, 30, "THÁI BÌNH DƯƠNG", [0, 0], co=17, zd=1.6),
  mh(137, 21, "THÁI BÌNH DƯƠNG", [0, 0], co=17, zd=1.6), mh(113, 13.2, "BIỂN ĐÔNG", [0, 0], co=17, zt=2.0, dam=True)],
 "chu_giai": [{"loai": "mui_ten_dich", "nhan": "Mỹ và các nước tư bản chủ nghĩa"}, {"loai": "mui_ten_ta", "nhan": "Liên Xô và các nước xã hội chủ nghĩa"},
              {"loai": "sao", "nhan": "Khu vực đối đầu"}],
 "doi_tuong": {
  # toàn cảnh
  "my": nh(-99, 40, "MỸ", 26, "dich"), "lx": nh(85, 60, "LIÊN XÔ", 26, "ta"),
  "s_duc": {"loai": "sao", "vi_tri": P(10.5, 51.2)}, "s_tt": {"loai": "sao", "vi_tri": P(127.3, 38.6)},
  "s_cb": {"loai": "sao", "vi_tri": P(-79.5, 21.8)}, "s_vn": {"loai": "sao", "vi_tri": P(106.5, 15.5)},
  "t_duc": nh(10.5, 56.5, "Đức", 18), "t_tt": nh(127.3, 44.0, "Triều Tiên", 18),
  "t_cb": nh(-79.5, 16.0, "Cu-ba", 18), "t_vn": nh(97.0, 13.0, "Việt Nam", 18),
  # Đức (zoom ≈ 4)
  "d_tay": nh(6.4, 50.2, "Tây Đức: CHLB Đức (9 – 1949)", 5.4, "dich"), "d_dong": nh(14.6, 52.6, "Đông Đức: CHDC Đức (10 – 1949)", 5.4, "ta"),
  # Triều Tiên (zoom ≈ 4)
  "tt_bac": nh(127.2, 41.4, "Phía bắc: CHDCND Triều Tiên (9 – 1948)", 5.2, "ta"), "tt_nam": nh(128.0, 34.1, "Phía nam: Đại Hàn Dân quốc (8 – 1948)", 5.2, "dich"),
  # Cu-ba (zoom ≈ 4)
  "cb_my": nh(-79.0, 26.6, "Mỹ: phong toả hải quân (10 – 1962)", 5.2, "dich"), "cb_lx": nh(-78.5, 17.4, "Liên Xô: đưa quân, tên lửa vào Cu-ba (10 – 1962)", 5.2, "ta"),
  # Việt Nam (zoom ≈ 3)
  "vn_my": nh(98.0, 20.3, "Mỹ: giúp Pháp (1950 – 1954)", 6.2, "dich"),
  "vn_my2": nh(97.6, 18.0, "Chiến tranh xâm lược ở miền Nam (1954 – 1975)", 6.2, "dich"),
  "vn_lx": nh(98.0, 11.6, "Liên Xô: ủng hộ kháng chiến, xây dựng CNXH", 6.2, "ta")
 },
 "pha": {
  "tong_quan": {"mo_dau": True, "zoom": [1.0, 1.05], "chu_giai": ["sao"],
   "buoc": [{"id": "my", "tu": 0.06, "den": 0.16}, {"id": "lx", "tu": 0.1, "den": 0.2},
            {"id": "s_duc", "tu": 0.4, "den": 0.48}, {"id": "t_duc", "tu": 0.42, "den": 0.5},
            {"id": "s_tt", "tu": 0.52, "den": 0.6}, {"id": "t_tt", "tu": 0.54, "den": 0.62},
            {"id": "s_cb", "tu": 0.64, "den": 0.72}, {"id": "t_cb", "tu": 0.66, "den": 0.74},
            {"id": "s_vn", "tu": 0.76, "den": 0.84}, {"id": "t_vn", "tu": 0.78, "den": 0.86}]},
  "duc": {"zoom": [3.6, 3.9], "tam": P(10.5, 51.2), "can_giua": [0.5, 0.45], "chu_giai": [], "hien": ["s_duc"],
   "moc": [{"chu": "Đức: 1949", "tu": 0.03, "den": 0.98}],
   "buoc": [{"id": "d_tay", "tu": 0.12, "den": 0.22}, {"id": "d_dong", "tu": 0.55, "den": 0.65}]},
  "trieu_tien": {"zoom": [3.6, 3.9], "tam": P(127.5, 38.0), "can_giua": [0.5, 0.45], "chu_giai": [], "hien": ["s_tt"],
   "moc": [{"chu": "Triều Tiên: 1948", "tu": 0.03, "den": 0.6}, {"chu": "Chiến tranh 1950 – 1953", "tu": 0.62, "den": 0.98}],
   "buoc": [{"id": "tt_nam", "tu": 0.1, "den": 0.2}, {"id": "tt_bac", "tu": 0.3, "den": 0.4}]},
  "cu_ba": {"zoom": [3.6, 3.9], "tam": P(-79.0, 22.0), "can_giua": [0.5, 0.45], "chu_giai": [], "hien": ["s_cb"],
   "moc": [{"chu": "Cu-ba: 1961 – 1962", "tu": 0.03, "den": 0.98}],
   "buoc": [{"id": "cb_my", "tu": 0.3, "den": 0.4}, {"id": "cb_lx", "tu": 0.62, "den": 0.72}]},
  "viet_nam": {"zoom": [3.0, 3.2], "tam": P(106.5, 15.0), "can_giua": [0.5, 0.45], "chu_giai": [], "hien": ["s_vn"],
   "moc": [{"chu": "Việt Nam: 1950 – 1975", "tu": 0.03, "den": 0.98}],
   "buoc": [{"id": "vn_my", "tu": 0.08, "den": 0.18}, {"id": "vn_my2", "tu": 0.3, "den": 0.4}, {"id": "vn_lx", "tu": 0.62, "den": 0.72}]}
 }
}
json.dump(S, open(f"{ROOT}/pipeline/maps/specs/chien-tranh-lanh.json", "w"), ensure_ascii=False)
print("ok", len(S["vung_mau"]))
