"""Sinh sa bàn (saban2) 'hai-chau-tho': châu thổ sông Hồng và châu thổ sông Cửu Long được phù sa bồi đắp, tiến ra biển
(SGK LSĐL 8, Chủ đề chung 1, tr. 155–158). Tam giác châu thổ sông Hồng vẽ theo lời văn SGK: đỉnh Thanh Miếu (tỉnh Phú Thọ),
đáy là bờ biển từ nơi giáp giới Hải Phòng – Quảng Ninh đến cửa sông Đáy (tỉnh Ninh Bình). Phạm vi châu thổ sông Cửu Long, dòng sông
và mũi tên 'tiến ra biển' là minh hoạ. Nền đất liền Natural Earth; quần đảo Hoàng Sa, Trường Sa vẽ bằng chấm, nhãn ghi rõ thuộc Việt Nam."""
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
def song(pts, rong=3): return {"diem": [P(*p) for p in pts], "rong": rong}

S = {
 "phien_ban": 2, "ten": "Hai châu thổ lớn", "phu_de": "Sông Hồng – sông Cửu Long",
 "nguon": "Vẽ bằng code theo nội dung SGK Lịch sử và Địa lí 8, Chủ đề chung 1, tr. 155–158; nền đất liền Natural Earth",
 "khung": P(99.0, 23.6) + P(119.5, 6.0), "nen_bien": [0.80, 0.88, 0.93], "chu_giai_xy": [0.03, 0.30], "sao_man_hinh": True,
 "vung_mau": nen([96, 4, 125, 27]),
 "song": [song([(103.95, 22.5), (104.4, 22.1), (104.87, 21.72), (105.42, 21.3), (105.86, 21.03), (106.05, 20.65), (106.3, 20.4), (106.55, 20.25)], 3.2),
          song([(105.9, 14.1), (106.0, 13.0), (105.95, 12.5), (105.45, 11.95), (104.95, 11.6), (105.1, 11.1), (105.15, 10.95), (105.35, 10.8), (105.65, 10.45), (105.9, 10.27), (106.35, 10.35), (106.75, 10.1)], 3.5),
          song([(105.1, 11.1), (105.0, 10.9), (105.12, 10.7), (105.43, 10.38), (105.78, 10.03), (106.1, 9.75), (106.35, 9.55)], 3.5)],
 "dia_danh": cham(HS, zoom_den=2.0) + cham(TS, zoom_den=2.0) + [
  nh(112.0, 17.55, "QĐ. Hoàng Sa (Việt Nam)", dam=True, co=19, zoom_den=2.0), nh(114.4, 12.0, "QĐ. Trường Sa (Việt Nam)", dam=True, co=19, zoom_den=2.0),
  nh(111.0, 22.9, "TRUNG QUỐC", lon=True, zoom_den=2.0), nh(103.4, 19.2, "LÀO", lon=True, zoom_den=2.0), nh(104.7, 12.9, "CAM-PU-CHIA", lon=True, zoom_den=2.0),
  nh(101.0, 15.5, "THÁI LAN", lon=True, zoom_den=2.0), nh(116.6, 14.3, "BIỂN ĐÔNG", lon=True, zoom_den=2.0),
  nh(107.6, 20.0, "VỊNH BẮC BỘ", dam=True, co=19, zoom_tu=2.0), nh(108.2, 9.3, "BIỂN ĐÔNG", lon=True, zoom_tu=2.0),
  nh(104.0, 12.2, "CAM-PU-CHIA", lon=True, zoom_tu=2.0), nh(103.6, 9.6, "VỊNH THÁI LAN", dam=True, co=18, zoom_tu=2.0),
 ]
}
S["chu_giai"] = [{"loai": "vong", "nhan": "Phạm vi châu thổ (minh hoạ)"}, {"loai": "mui_ten_ta", "nhan": "Châu thổ bồi đắp, tiến ra biển"}]
nhan = lambda lon, lat, chu, co=12, mau="ta": {"loai": "nhan", "vi_tri": P(lon, lat), "chu": chu, "co": co, "mau": mau}
GOC = [(105.40, 21.30), (106.80, 20.85), (106.10, 19.98), (105.40, 21.30)]
TAM_GIAC = [(a[0] + (b[0] - a[0]) * t / 6, a[1] + (b[1] - a[1]) * t / 6) for a, b in zip(GOC, GOC[1:]) for t in range(6)] + [GOC[0]]
CL = [(104.5, 10.4), (105.15, 10.95), (106.0, 11.0), (106.75, 10.45), (106.65, 9.6), (105.6, 8.65), (104.75, 8.55), (104.8, 9.6), (104.5, 10.4)]
S["doi_tuong"] = {
 "tg_hong": {"loai": "vong", "diem": [P(*p) for p in TAM_GIAC], "rong": 4},
 "vg_cl": {"loai": "vong", "diem": [P(*p) for p in CL], "rong": 4},
 "n_hong_0": nhan(108.6, 21.3, "Châu thổ sông Hồng", 20), "n_cl_0": nhan(109.0, 10.4, "Châu thổ sông Cửu Long", 20),
 "n_dinh": nhan(104.95, 21.5, "Thanh Miếu (Phú Thọ)", 6.2), "n_day": nhan(105.55, 19.78, "cửa sông Đáy (Ninh Bình)", 6.2),
 "n_hpqn": nhan(107.85, 21.05, "giáp giới Hải Phòng – Quảng Ninh", 6.2),
 "t1": {"loai": "mui_ten_ta", "diem": [P(106.3, 20.12), P(106.55, 19.86), P(106.8, 19.64)], "w0": 3.0, "w1": 5.5},
 "t2": {"loai": "mui_ten_ta", "diem": [P(106.62, 20.42), P(106.88, 20.2), P(107.12, 20.02)], "w0": 3.0, "w1": 5.5},
 "n_song_tien": nhan(106.05, 10.5, "sông Tiền", 7.5, "chu"), "n_song_hau": nhan(105.55, 9.95, "sông Hậu", 7.5, "chu"),
 "n_ca_mau": nhan(104.6, 8.95, "bán đảo Cà Mau", 7.5, "chu"),
 "c1": {"loai": "mui_ten_ta", "diem": [P(104.95, 8.85), P(104.7, 8.6), P(104.45, 8.35)], "w0": 3.5, "w1": 6.5},
 "c2": {"loai": "mui_ten_ta", "diem": [P(105.35, 8.75), P(105.33, 8.48), P(105.3, 8.2)], "w0": 3.5, "w1": 6.5},
}
S["pha"] = {
 "tong_quan": {"mo_dau": True, "zoom": [1.0, 1.05], "chu_giai": ["vong"],
               "buoc": [{"id": "tg_hong", "tu": 0.15, "den": 0.4}, {"id": "n_hong_0", "tu": 0.3, "den": 0.45},
                        {"id": "vg_cl", "tu": 0.5, "den": 0.75}, {"id": "n_cl_0", "tu": 0.65, "den": 0.8}]},
 "song_hong": {"zoom": [3.2, 3.35], "tam": P(106.0, 20.75), "can_giua": [0.5, 0.5], "chu_giai": ["vong", "mui_ten_ta"],
               "moc": [{"chu": "Châu thổ sông Hồng: khoảng 15 000 km², dạng tam giác", "tu": 0.03, "den": 1.1}],
               "buoc": [{"id": "tg_hong", "tu": 0.08, "den": 0.35}, {"id": "n_dinh", "tu": 0.2, "den": 0.3}, {"id": "n_hpqn", "tu": 0.3, "den": 0.4},
                        {"id": "n_day", "tu": 0.38, "den": 0.48}, {"id": "t1", "tu": 0.6, "den": 0.85}, {"id": "t2", "tu": 0.65, "den": 0.9}]},
 "cuu_long": {"zoom": [2.6, 2.75], "tam": P(105.6, 9.9), "can_giua": [0.5, 0.45], "chu_giai": ["vong", "mui_ten_ta"],
              "moc": [{"chu": "Châu thổ sông Cửu Long: hơn 40 nghìn km², lớn nhất nước ta", "tu": 0.03, "den": 1.1}],
              "buoc": [{"id": "vg_cl", "tu": 0.08, "den": 0.35}, {"id": "n_song_tien", "tu": 0.3, "den": 0.4}, {"id": "n_song_hau", "tu": 0.36, "den": 0.46},
                       {"id": "n_ca_mau", "tu": 0.45, "den": 0.55}, {"id": "c1", "tu": 0.6, "den": 0.85}, {"id": "c2", "tu": 0.65, "den": 0.9}]},
}
json.dump(S, open(f"{ROOT}/pipeline/maps/specs/hai-chau-tho.json", "w"), ensure_ascii=False)
print("ok")
