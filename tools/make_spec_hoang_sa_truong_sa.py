"""Sinh sa bàn (saban2) 'hoang-sa-truong-sa': nhà Nguyễn thực thi chủ quyền ở quần đảo Hoàng Sa và quần đảo Trường Sa
(SGK LSĐL 8, Bài 16, tr. 75 và tư liệu 2, 3). Bản đồ định vị vẽ bằng code (nền đất liền Natural Earth), không phải bản đồ cổ;
quần đảo Hoàng Sa, Trường Sa vẽ bằng nhiều chấm theo toạ độ khu vực, nhãn ghi rõ thuộc Việt Nam.
Hướng thuyền đi Hoàng Sa là minh hoạ (SGK không nêu nơi xuất phát; chỉ nêu hai quần đảo thuộc phủ Quảng Nghĩa thời Gia Long)."""
import json, sys, random
sys.path.insert(0, "/home/claude/eduhistory-studio/tools")
from make_vn_map import xy, nen, ROOT
P = lambda lon, lat: xy(lon, lat)

def quan_dao(lon0, lon1, lat0, lat1, n, seed):
    random.seed(seed)
    return [[random.uniform(lon0, lon1), random.uniform(lat0, lat1)] for _ in range(n)]
HS = quan_dao(111.2, 112.8, 15.8, 17.1, 16, 7)
TS = quan_dao(112.0, 116.8, 8.0, 11.4, 26, 9)
def cham(pts): return [{"ten": "", "vi_tri": P(*p), "kieu": "diem", "man_hinh": True, "lech": [0, 0]} for p in pts]
def nh(x, y, ten, **kw): return {"ten": ten, "vi_tri": P(x, y), "man_hinh": True, "lech": [0, 0], **kw}
def dd(x, y, ten, lech, **kw): return {"ten": ten, "vi_tri": P(x, y), "kieu": "diem", "man_hinh": True, "lech": lech, **kw}

S = {
 "phien_ban": 2, "ten": "Hoàng Sa – Trường Sa thời Nguyễn", "phu_de": "Thực thi chủ quyền",
 "nguon": "Bản đồ định vị vẽ bằng code theo nội dung SGK Lịch sử và Địa lí 8, Bài 16, tr. 75; nền đất liền Natural Earth",
 "khung": P(99.0, 23.6) + P(119.5, 6.0), "nen_bien": [0.80, 0.88, 0.93], "chu_giai_xy": [0.03, 0.30], "sao_man_hinh": True,
 "vung_mau": nen([96, 4, 125, 27]),
 "dia_danh": cham(HS) + cham(TS) + [
  nh(112.0, 17.55, "QĐ. Hoàng Sa (Việt Nam)", dam=True, co=19), nh(114.4, 12.0, "QĐ. Trường Sa (Việt Nam)", dam=True, co=19),
  nh(111.0, 22.9, "TRUNG QUỐC", lon=True), nh(103.4, 19.2, "LÀO", lon=True, zoom_den=1.5), nh(105.7, 15.9, "LÀO", lon=True, zoom_tu=1.5), nh(104.7, 12.9, "CAM-PU-CHIA", lon=True),
  nh(101.0, 15.5, "THÁI LAN", lon=True, zoom_den=1.5), nh(116.6, 14.3, "BIỂN ĐÔNG", lon=True), nh(118.4, 16.6, "PHI-LÍP-PIN", lon=True, co=18),
  nh(107.9, 13.6, "VIỆT NAM", lon=True, co=26, zoom_den=1.6),
  dd(105.85, 21.03, "Hà Nội", [-12, 0], co=17, zoom_den=1.6), dd(107.58, 16.46, "Huế", [-12, 0], co=18, zoom_tu=1.4),
  dd(108.8, 15.12, "phủ Quảng Nghĩa", [-14, 8], dam=True, co=19, zoom_tu=1.4)
 ]
}
S["chu_giai"] = [{"loai": "mui_ten_ta", "nhan": "Hải trình đội Hoàng Sa (minh hoạ)"}, {"loai": "sao", "nhan": "Dấu mốc thực thi chủ quyền"}]
VONG = lambda lon, lat, rx, ry: [P(lon + rx * c, lat + ry * s) for c, s in [(1, 0), (.7, .7), (0, 1), (-.7, .7), (-1, 0), (-.7, -.7), (0, -1), (.7, -.7), (1, 0)]]
S["doi_tuong"] = {
 "vong_hs": {"loai": "vong", "diem": VONG(112.0, 16.45, 1.15, .95), "rong": 4},
 "vong_ts": {"loai": "vong", "diem": VONG(114.4, 9.7, 3.0, 2.0), "rong": 4},
 "duong_hs": {"loai": "mui_ten_ta", "diem": [P(109.1, 15.25), P(110.0, 15.75), P(110.9, 16.2)], "w0": 3.2, "w1": 6},
 "thuyen_hs": {"loai": "thuyen_ta", "diem": [P(109.0, 15.2), P(109.9, 15.7), P(110.8, 16.15)], "so": 4, "bat_dau": 0.05},
 "duong_ts": {"loai": "mui_ten_ta", "diem": [P(109.4, 13.5), P(110.8, 12.2), P(112.1, 11.0)], "w0": 3.2, "w1": 6},
 "co_1816": {"loai": "sao", "vi_tri": P(112.3, 16.55)},
 "n_1816": {"loai": "nhan", "vi_tri": P(112.1, 15.15), "chu": "1816: treo cờ ở Hoàng Sa", "co": 11, "mau": "ta"},
 "dau_1836": {"loai": "sao", "vi_tri": P(111.7, 16.3)},
 "n_1836": {"loai": "nhan", "vi_tri": P(112.0, 15.15), "chu": "1836: đo đạc, dựng dấu bằng bài gỗ", "co": 11, "mau": "ta"},
 "n_mieu": {"loai": "nhan", "vi_tri": P(112.0, 14.7), "chu": "Dựng miếu thờ, trồng cây xanh", "co": 11, "mau": "ta"},
}
TRUNG = dict(tam=P(110.6, 14.4), can_giua=[0.5, 0.45])
S["pha"] = {
 "tong_quan": {"mo_dau": True, "zoom": [1.0, 1.05], "chu_giai": [],
               "buoc": [{"id": "vong_hs", "tu": 0.25, "den": 0.45}, {"id": "vong_ts", "tu": 0.45, "den": 0.7}]},
 "gia_long": {"zoom": [1.8, 1.9], **TRUNG, "chu_giai": ["mui_ten_ta"], "hien": ["vong_hs"],
              "moc": [{"chu": "Thời Gia Long: thuộc phủ Quảng Nghĩa", "tu": 0.03, "den": 1.1}],
              "buoc": [{"id": "duong_hs", "tu": 0.3, "den": 0.65}, {"id": "thuyen_hs", "tu": 0.3, "den": 0.95}]},
 "nam_1816": {"zoom": [1.9, 2.0], **TRUNG, "chu_giai": ["sao"], "hien": ["vong_hs", "duong_hs"],
              "moc": [{"chu": "Năm 1816", "tu": 0.03, "den": 1.1}],
              "buoc": [{"id": "co_1816", "tu": 0.2, "den": 0.3}, {"id": "n_1816", "tu": 0.25, "den": 0.35}]},
 "nam_1836": {"zoom": [1.9, 2.0], **TRUNG, "chu_giai": ["mui_ten_ta", "sao"], "hien": ["vong_hs"],
              "moc": [{"chu": "Năm 1836 – Phạm Hữu Nhật", "tu": 0.03, "den": 1.1}],
              "buoc": [{"id": "duong_hs", "tu": 0.08, "den": 0.35}, {"id": "thuyen_hs", "tu": 0.08, "den": 0.6}, {"id": "dau_1836", "tu": 0.55, "den": 0.65}, {"id": "n_1836", "tu": 0.6, "den": 0.7}]},
 "toan_do": {"zoom": [1.05, 1.1], "chu_giai": [], "hien": ["vong_hs", "vong_ts"],
             "bang": {"chu": "Khoảng 1838: Đại Nam nhất thống toàn đồ", "tu": 0.15, "y": 0.2}}
}
json.dump(S, open(f"{ROOT}/pipeline/maps/specs/hoang-sa-truong-sa.json", "w"), ensure_ascii=False)
print("ok")

# ------------------------------------------------------------------ biến thể thời các chúa Nguyễn (SGK Bài 6, tr. 29–30)
C = json.loads(json.dumps(S))
C.update({"ten": "Biển đảo thời các chúa Nguyễn", "phu_de": "Thế kỉ XVII – XVIII",
          "nguon": "Bản đồ định vị vẽ bằng code theo nội dung SGK Lịch sử và Địa lí 8, Bài 6, tr. 29–30; nền đất liền Natural Earth"})
C["dia_danh"] = [d for d in C["dia_danh"] if d.get("ten") not in ("phủ Quảng Nghĩa", "Huế", "Hà Nội", "BIỂN ĐÔNG")] + [
 nh(116.6, 14.3, "BIỂN ĐÔNG", lon=True, zoom_den=1.8), nh(110.2, 12.6, "BIỂN ĐÔNG", lon=True, zoom_tu=1.8),
 dd(106.6, 8.68, "cù lao Côn Lôn", [14, 8], dam=True, co=17, zoom_tu=1.3), dd(104.0, 10.15, "các đảo ở Hà Tiên", [-12, 12], dam=True, co=17, zoom_tu=1.3),
 nh(102.9, 9.6, "VỊNH THÁI LAN", dam=True, co=17, zoom_tu=1.3)]
C["chu_giai"] = [{"loai": "mui_ten_ta", "nhan": "Hải trình đội dân binh (minh hoạ)"}]
C["doi_tuong"] = {
 "vong_hs": S["doi_tuong"]["vong_hs"], "vong_ts": S["doi_tuong"]["vong_ts"],
 "di_hs": {"loai": "mui_ten_ta", "diem": [P(109.1, 15.3), P(110.0, 15.8), P(110.9, 16.2)], "w0": 3.2, "w1": 6},
 "di_ts": {"loai": "mui_ten_ta", "diem": [P(109.3, 13.6), P(110.7, 12.3), P(112.0, 11.0)], "w0": 3.2, "w1": 6},
 "thuyen_hs": {"loai": "thuyen_ta", "diem": [P(109.0, 15.25), P(109.9, 15.75), P(110.8, 16.15)], "so": 3, "bat_dau": 0.05},
 "thuyen_ts": {"loai": "thuyen_ta", "diem": [P(109.2, 13.65), P(110.6, 12.35), P(111.9, 11.1)], "so": 3, "bat_dau": 0.05},
 "di_cl": {"loai": "mui_ten_ta", "diem": [P(106.9, 10.2), P(106.8, 9.5), P(106.65, 8.9)], "w0": 2.4, "w1": 4.4},
 "di_ht": {"loai": "mui_ten_ta", "diem": [P(105.0, 9.5), P(104.5, 9.85), P(104.15, 10.1)], "w0": 2.4, "w1": 4.4},
 "n_dd": {"loai": "nhan", "vi_tri": P(112.3, 14.2), "chu": "Đội Hoàng Sa, đội Bắc Hải", "co": 11, "mau": "ta"},
}
C["pha"] = {
 "tong_quan": {"mo_dau": True, "zoom": [1.0, 1.05], "chu_giai": [],
               "buoc": [{"id": "vong_hs", "tu": 0.25, "den": 0.45}, {"id": "vong_ts", "tu": 0.45, "den": 0.7}]},
 "doi_dan_binh": {"zoom": [1.45, 1.55], "tam": P(110.8, 13.7), "can_giua": [0.5, 0.45], "chu_giai": ["mui_ten_ta"], "hien": ["vong_hs", "vong_ts"],
                  "moc": [{"chu": "Thế kỉ XVII – XVIII: hoạt động có tổ chức, liên tục", "tu": 0.03, "den": 1.1}],
                  "buoc": [{"id": "di_hs", "tu": 0.1, "den": 0.4}, {"id": "thuyen_hs", "tu": 0.1, "den": 0.9}, {"id": "di_ts", "tu": 0.2, "den": 0.5}, {"id": "thuyen_ts", "tu": 0.2, "den": 0.95}, {"id": "n_dd", "tu": 0.5, "den": 0.6}]},
 "bac_hai": {"zoom": [1.9, 2.0], "tam": P(106.2, 9.8), "can_giua": [0.5, 0.45], "chu_giai": ["mui_ten_ta"], "hien": ["vong_ts"],
             "moc": [{"chu": "Đội Bắc Hải: xứ Bắc Hải, cù lao Côn Lôn, các đảo ở Hà Tiên", "tu": 0.03, "den": 1.1}],
             "buoc": [{"id": "di_cl", "tu": 0.2, "den": 0.45}, {"id": "di_ht", "tu": 0.35, "den": 0.6}]}
}
json.dump(C, open(f"{ROOT}/pipeline/maps/specs/hoang-sa-chua-nguyen.json", "w"), ensure_ascii=False)
print("ok chua-nguyen")
