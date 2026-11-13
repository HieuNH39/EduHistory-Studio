"""Sinh sa bàn (saban2) 'bien-dao-viet-nam': bản đồ định vị biển đảo Việt Nam cho các tập lớp 9 về chủ quyền biển đảo
(SGK LSĐL 9, Bài 20, tr. 103 – 104; Chủ đề 3, tr. 233 – 234). Vẽ bằng code (nền đất liền Natural Earth), vị trí các đảo gần đúng;
luôn có quần đảo Hoàng Sa và Trường Sa (ghi rõ thuộc Việt Nam). Không vẽ biên giới trên biển, không vẽ đường yêu sách.
Pha: dac_khu (L9-B20-03), gac_ma (L9-B20-03), sau_1954 (L9-CD3-02), tien_tieu (L9-CD3-04)."""
import json, sys, random
sys.path.insert(0, "/home/claude/eduhistory-studio/tools")
from make_vn_map import xy, nen, ROOT
P = lambda lon, lat: xy(lon, lat)

def quan_dao(lon0, lon1, lat0, lat1, n, seed):
    random.seed(seed)
    return [[random.uniform(lon0, lon1), random.uniform(lat0, lat1)] for _ in range(n)]
HS = quan_dao(111.2, 112.8, 15.8, 17.1, 16, 7)          # cùng cách vẽ với sa bàn hoang-sa-truong-sa
TS = quan_dao(112.0, 116.8, 8.0, 11.4, 26, 9)
DAO = {"blv": (107.72, 20.13), "coto": (107.77, 20.98), "con_co": (107.34, 17.16)}
def cham(pts): return [{"ten": "", "vi_tri": P(*p), "kieu": "diem", "man_hinh": True, "lech": [0, 0]} for p in pts]
def nh(x, y, ten, **kw): return {"ten": ten, "vi_tri": P(x, y), "man_hinh": True, "lech": [0, 0], **kw}
def dd(x, y, ten, lech, **kw): return {"ten": ten, "vi_tri": P(x, y), "kieu": "diem", "man_hinh": True, "lech": lech, **kw}
def nhan(x, y, chu, co=15, mau="ta"): return {"loai": "nhan", "vi_tri": P(x, y), "chu": chu, "co": co, "mau": mau}

S = {
 "phien_ban": 2, "ten": "Biển đảo Việt Nam", "phu_de": "Chủ quyền biển đảo",
 "nguon": "Bản đồ định vị vẽ bằng code theo SGK Lịch sử và Địa lí 9, tr. 103 – 104, 233 – 234; vị trí gần đúng; nền đất liền Natural Earth",
 "khung": P(99.0, 23.6) + P(119.5, 6.0), "nen_bien": [0.80, 0.88, 0.93], "chu_giai_xy": [0.03, 0.30], "sao_man_hinh": True,
 "vung_mau": nen([96, 4, 125, 27]),
 "dia_danh": cham(HS) + cham(TS) + cham([DAO["blv"], DAO["coto"], DAO["con_co"]]) + [
  nh(112.0, 17.55, "QĐ. Hoàng Sa (Việt Nam)", dam=True, co=19), nh(114.4, 12.0, "QĐ. Trường Sa (Việt Nam)", dam=True, co=19),
  nh(111.0, 22.9, "TRUNG QUỐC", lon=True), nh(103.4, 19.2, "LÀO", lon=True, zoom_den=1.5), nh(104.7, 12.9, "CAM-PU-CHIA", lon=True, zoom_den=1.5),
  nh(101.0, 15.5, "THÁI LAN", lon=True, zoom_den=1.5), nh(116.6, 14.3, "BIỂN ĐÔNG", lon=True, zoom_den=1.5), nh(118.4, 16.6, "PHI-LÍP-PIN", lon=True, co=18, zoom_den=1.5),
  nh(107.9, 13.6, "VIỆT NAM", lon=True, co=26, zoom_den=1.6), dd(105.85, 21.03, "Hà Nội", [-12, 0], co=17, zoom_den=1.6),
 ]
}
S["chu_giai"] = [{"loai": "sao", "nhan": "Nơi diễn ra sự kiện (vị trí gần đúng)"}]
VONG = lambda lon, lat, rx, ry: [P(lon + rx * c, lat + ry * s) for c, s in [(1, 0), (.7, .7), (0, 1), (-.7, .7), (-1, 0), (-.7, -.7), (0, -1), (.7, -.7), (1, 0)]]
S["doi_tuong"] = {
 "vong_hs": {"loai": "vong", "diem": VONG(112.0, 16.45, 1.15, .95), "rong": 4},
 "vong_ts": {"loai": "vong", "diem": VONG(114.4, 9.7, 3.0, 2.0), "rong": 4},
 # pha dac_khu – tên đặc khu theo SGK tr. 103
 "dk_blv": nhan(111.4, 20.15, "Đặc khu Bạch Long Vĩ (TP Hải Phòng)"),
 "dk_hs": nhan(112.0, 15.05, "Đặc khu Hoàng Sa (TP Đà Nẵng)"),
 "dk_ts": nhan(114.4, 12.9, "Đặc khu Trường Sa (tỉnh Khánh Hoà)"),
 # pha gac_ma – SGK tr. 104
 "sao_gm": {"loai": "sao", "vi_tri": P(114.29, 9.74)},
 "n_gm": nhan(114.3, 10.4, "Gạc Ma, Cô Lin, Len Đao", co=8),
 # pha sau_1954 – SGK tr. 233
 "s54_blv": nhan(110.9, 20.15, "Bạch Long Vĩ – TP Hải Phòng"),
 "s54_coto": nhan(111.7, 21.0, "Cô Tô – tỉnh Hải Ninh (nay Quảng Ninh)"),
 "s54_hs": nhan(112.0, 15.05, "Thuộc tỉnh Quảng Nam (nay TP Đà Nẵng)"),
 "s54_ts": nhan(114.4, 12.9, "Thuộc tỉnh Phước Tuy (từ 1989: tỉnh Khánh Hoà)"),
 # pha tien_tieu – SGK tr. 234
 "sao_blv": {"loai": "sao", "vi_tri": P(*DAO["blv"])},
 "sao_cc": {"loai": "sao", "vi_tri": P(*DAO["con_co"])},
 "tt_blv": nhan(109.3, 20.3, "Bạch Long Vĩ"),
 "tt_cc": nhan(108.6, 17.75, "Cồn Cỏ"),
}
S["pha"] = {
 "dac_khu": {"mo_dau": True, "zoom": [1.0, 1.05], "chu_giai": [],
             "buoc": [{"id": "vong_hs", "tu": 0.12, "den": 0.28}, {"id": "vong_ts", "tu": 0.18, "den": 0.36},
                      {"id": "dk_blv", "tu": 0.40, "den": 0.48}, {"id": "dk_hs", "tu": 0.52, "den": 0.60}, {"id": "dk_ts", "tu": 0.64, "den": 0.72}]},
 "gac_ma": {"zoom": [2.3, 2.5], "tam": P(113.9, 10.0), "can_giua": [0.56, 0.50], "chu_giai": ["sao"],
            "moc": [{"chu": "Tháng 3 – 1988", "tu": 0.04, "den": 1.1}],
            "buoc": [{"id": "sao_gm", "tu": 0.25, "den": 0.35}, {"id": "n_gm", "tu": 0.32, "den": 0.42}]},
 "sau_1954": {"mo_dau": True, "zoom": [1.0, 1.05], "chu_giai": [],
              "moc": [{"chu": "Sau năm 1954", "tu": 0.04, "den": 1.1}],
              "buoc": [{"id": "vong_hs", "tu": 0.10, "den": 0.24}, {"id": "vong_ts", "tu": 0.14, "den": 0.30},
                       {"id": "s54_blv", "tu": 0.32, "den": 0.40}, {"id": "s54_coto", "tu": 0.40, "den": 0.48},
                       {"id": "s54_ts", "tu": 0.55, "den": 0.63}, {"id": "s54_hs", "tu": 0.68, "den": 0.76}]},
 "tien_tieu": {"mo_dau": True, "zoom": [1.0, 1.05], "chu_giai": [],
               "moc": [{"chu": "Căn cứ tiền tiêu hướng đông", "tu": 0.04, "den": 1.1}],
               "buoc": [{"id": "sao_blv", "tu": 0.15, "den": 0.25}, {"id": "tt_blv", "tu": 0.2, "den": 0.3},
                        {"id": "sao_cc", "tu": 0.3, "den": 0.4}, {"id": "tt_cc", "tu": 0.35, "den": 0.45},
                        {"id": "vong_hs", "tu": 0.5, "den": 0.65}, {"id": "vong_ts", "tu": 0.6, "den": 0.78}]},
}
json.dump(S, open(f"{ROOT}/pipeline/maps/specs/bien-dao-viet-nam.json", "w"), ensure_ascii=False)
print("ok")
