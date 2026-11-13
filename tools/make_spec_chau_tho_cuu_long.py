"""Sinh sa bàn (saban2) 'chau-tho-cuu-long': châu thổ sông Cửu Long, mùa lũ, kênh Vĩnh Tế (SGK LSĐL 8, Chủ đề chung 1, tr. 157–161).
Bản đồ định vị vẽ bằng code (nền Natural Earth; sông, kênh, hồ Tôn-lê Sáp vẽ tay giản lược). Pha mở đầu là toàn cảnh
Việt Nam có quần đảo Hoàng Sa, Trường Sa rồi máy quay tiến vào châu thổ. Vùng ngập lũ chỉ khoanh vị trí, không phải ranh giới đo đạc."""
import json, sys, random
sys.path.insert(0, "/home/claude/eduhistory-studio/tools")
from make_vn_map import xy, nen, ROOT
P = lambda lon, lat: xy(lon, lat)
def quan_dao(lon0, lon1, lat0, lat1, n, seed):
    random.seed(seed); return [[random.uniform(lon0, lon1), random.uniform(lat0, lat1)] for _ in range(n)]
def cham(pts): return [{"ten": "", "vi_tri": P(*p), "kieu": "diem", "man_hinh": True, "lech": [0, 0]} for p in pts]
def nh(x, y, ten, **kw): return {"ten": ten, "vi_tri": P(x, y), "man_hinh": True, "lech": [0, 0], **kw}
def dd(x, y, ten, lech, **kw): return {"ten": ten, "vi_tri": P(x, y), "kieu": "diem", "man_hinh": True, "lech": lech, **kw}
def song(pts, rong=3): return {"diem": [P(*p) for p in pts], "rong": rong}
VONG = lambda lon, lat, rx, ry: [P(lon + rx * c, lat + ry * s) for c, s in [(1, 0), (.7, .7), (0, 1), (-.7, .7), (-1, 0), (-.7, -.7), (0, -1), (.7, -.7), (1, 0)]]
Z = 2.0
S = {
 "phien_ban": 2, "ten": "Châu thổ sông Cửu Long", "phu_de": "Sông nước – mùa lũ – kênh đào",
 "nguon": "Bản đồ định vị vẽ bằng code theo nội dung SGK Lịch sử và Địa lí 8, Chủ đề chung 1, tr. 157–160; nền đất liền Natural Earth",
 "khung": P(99.0, 23.6) + P(119.5, 6.0), "nen_bien": [0.80, 0.88, 0.93], "chu_giai_xy": [0.03, 0.30], "sao_man_hinh": True,
 "vung_mau": nen([96, 4, 125, 27]),
 "ho": [{"elip": P(104.05, 12.85) + [52, 20, -35], "ten": ""}],
 "song": [song([(105.9, 14.1), (106.0, 13.0), (105.95, 12.5), (105.45, 11.95), (104.95, 11.6), (105.1, 11.1), (105.15, 10.95), (105.35, 10.8), (105.65, 10.45), (105.9, 10.27), (106.35, 10.35), (106.75, 10.1)], 3.5),
          song([(105.1, 11.1), (105.0, 10.9), (105.12, 10.7), (105.43, 10.38), (105.78, 10.03), (106.1, 9.75), (106.35, 9.55)], 3.5),
          song([(104.45, 12.55), (104.75, 12.0), (104.92, 11.62)], 2.5),
          song([(105.12, 10.7), (104.85, 10.6), (104.65, 10.48), (104.48, 10.38)], 1.6)],
 "dia_danh": cham(quan_dao(111.2, 112.8, 15.8, 17.1, 14, 7)) + cham(quan_dao(112.0, 116.8, 8.0, 11.4, 22, 9)) + [
  nh(112.0, 17.55, "QĐ. Hoàng Sa (Việt Nam)", dam=True, co=17), nh(114.4, 12.0, "QĐ. Trường Sa (Việt Nam)", dam=True, co=17, zoom_den=1.8), nh(112.7, 11.75, "QĐ. Trường Sa (Việt Nam)", dam=True, co=17, zoom_tu=1.8),
  nh(111.0, 22.9, "TRUNG QUỐC", lon=True, zoom_den=1.5), nh(103.4, 19.2, "LÀO", lon=True, zoom_den=1.5), nh(101.0, 15.5, "THÁI LAN", lon=True, zoom_den=1.5),
  nh(104.7, 12.4, "CAM-PU-CHIA", lon=True), nh(110.5, 9.2, "BIỂN ĐÔNG", lon=True), nh(103.2, 9.6, "VỊNH THÁI LAN", dam=True, co=18, zoom_tu=1.5),
  nh(103.6, 13.25, "hồ Tôn-lê Sáp", dam=True, co=16, zoom_tu=1.5),
  nh(106.5, 10.62, "s. Tiền", co=16, dam=True, zoom_tu=Z), nh(106.2, 9.9, "s. Hậu", co=16, dam=True, zoom_tu=Z),
  dd(105.12, 10.7, "Châu Đốc", [14, -12], co=17, zoom_tu=Z), dd(104.48, 10.38, "Hà Tiên", [-12, 10], co=17, zoom_tu=Z),
  nh(105.0, 8.85, "bán đảo Cà Mau", dam=True, co=17, zoom_tu=Z), nh(107.4, 10.5, "VIỆT NAM", lon=True, co=24, zoom_den=Z)
 ]
}
S["chu_giai"] = [{"loai": "vong", "nhan": "Vùng ngập lũ chủ yếu"}, {"loai": "sao", "nhan": "Hai đầu kênh Vĩnh Tế"}]
S["doi_tuong"] = {
 "vong_ct": {"loai": "vong", "diem": VONG(105.6, 9.95, 1.35, 1.2), "rong": 4},
 "n_ct": {"loai": "nhan", "vi_tri": P(107.6, 9.0), "chu": "Hơn 40 nghìn km²", "co": 9, "mau": "ta"},
 "vong_dtm": {"loai": "vong", "diem": VONG(105.85, 10.68, .42, .28), "rong": 3},
 "n_dtm": {"loai": "nhan", "vi_tri": P(106.25, 11.12), "chu": "Đồng Tháp Mười", "co": 7, "mau": "ta"},
 "vong_lx": {"loai": "vong", "diem": VONG(104.98, 10.3, .36, .26), "rong": 3},
 "n_lx": {"loai": "nhan", "vi_tri": P(104.55, 9.86), "chu": "Tứ giác Long Xuyên", "co": 7, "mau": "ta"},
 "sao_cd": {"loai": "sao", "vi_tri": P(105.12, 10.7)}, "sao_ht": {"loai": "sao", "vi_tri": P(104.48, 10.38)},
 "n_vt": {"loai": "nhan", "vi_tri": P(104.2, 10.97), "chu": "Kênh Vĩnh Tế (gần 90 km)", "co": 7, "mau": "ta"},
}
CT = dict(tam=P(105.5, 10.2), can_giua=[0.5, 0.45])
S["pha"] = {
 "tong_quan": {"mo_dau": True, "zoom": [1.05, 2.4], **CT, "chu_giai": [],
               "buoc": [{"id": "vong_ct", "tu": 0.55, "den": 0.8}, {"id": "n_ct", "tu": 0.75, "den": 0.85}]},
 "mua_lu": {"zoom": [2.5, 2.6], "tam": P(105.5, 10.2), "can_giua": [0.42, 0.45], "chu_giai": ["vong"],
            "moc": [{"chu": "Mùa lũ: tháng 7 – tháng 11", "tu": 0.03, "den": 1.1}],
            "buoc": [{"id": "vong_dtm", "tu": 0.2, "den": 0.4}, {"id": "n_dtm", "tu": 0.3, "den": 0.4}, {"id": "vong_lx", "tu": 0.4, "den": 0.6}, {"id": "n_lx", "tu": 0.5, "den": 0.6}]},
 "ton_le_sap": {"zoom": [1.9, 2.0], "tam": P(105.0, 11.0), "can_giua": [0.5, 0.45], "chu_giai": [],
                "moc": [{"chu": "Lũ được điều tiết bởi hồ Tôn-lê Sáp", "tu": 0.05, "den": 1.1}]},
 "vinh_te": {"zoom": [3.6, 3.8], "tam": P(104.85, 10.5), "can_giua": [0.5, 0.45], "chu_giai": ["sao"],
             "moc": [{"chu": "Đầu thế kỉ XIX: đào kênh Vĩnh Tế", "tu": 0.03, "den": 1.1}],
             "buoc": [{"id": "sao_cd", "tu": 0.15, "den": 0.25}, {"id": "sao_ht", "tu": 0.3, "den": 0.4}, {"id": "n_vt", "tu": 0.45, "den": 0.55}]}
}
json.dump(S, open(f"{ROOT}/pipeline/maps/specs/chau-tho-cuu-long.json", "w"), ensure_ascii=False)
print("ok")
