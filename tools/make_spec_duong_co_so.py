"""Sinh sa bàn (saban2) 'duong-co-so': đường cơ sở dùng để tính chiều rộng lãnh hải của lục địa Việt Nam và đường phân định
vịnh Bắc Bộ giữa Việt Nam và Trung Quốc (SGK LSĐL 8, Chủ đề chung 2, tr. 162–166; Bảng 2.1, Bảng 2.2, Hình 2.1, Hình 2.2).
Toạ độ các điểm A1 – A24 và 21 điểm phân định lấy đúng theo Bảng 2.1, Bảng 2.2 SGK (đã đối chiếu trên ảnh trang).
Điểm 0 không có toạ độ trong Bảng 2.1 nên không vẽ (Hình 2.1 SGK cũng chỉ vẽ từ A1).
saban2 chưa có kiểu 'đường thẳng mở', nên mỗi đường được vẽ bằng kiểu 'vong' theo lộ trình đi – về trùng nhau (nét đi hoàn tất ở nửa đầu bước).
Nền đất liền Natural Earth; quần đảo Hoàng Sa, Trường Sa vẽ bằng chấm, nhãn ghi rõ thuộc Việt Nam."""
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
dm = lambda d, m: d + m / 60                      # độ, phút thập phân (A1 – A10)
dms = lambda d, m, s: d + m / 60 + s / 3600       # độ, phút, giây

# Bảng 2.1 (vĩ độ Bắc, kinh độ Đông)
A = {1: (dm(9, 15.0), dm(103, 27.0)), 2: (dm(8, 22.8), dm(104, 52.4)), 3: (dm(8, 37.8), dm(106, 37.5)), 4: (dm(8, 38.9), dm(106, 40.3)),
     5: (dm(8, 39.7), dm(106, 42.1)), 6: (dm(9, 58.0), dm(109, 5.0)), 7: (dm(12, 39.0), dm(109, 28.0)), 8: (dm(12, 53.8), dm(109, 27.2)),
     9: (dm(13, 54.0), dm(109, 21.0)), 10: (dm(15, 23.1), dm(109, 9.0)),
     11: (dms(17, 10, 0.0), dms(107, 20, 36.0)), 12: (dms(17, 54, 48.1), dms(106, 40, 25.8)), 13: (dms(18, 7, 2.5), dms(106, 29, 23.7)),
     14: (dms(18, 47, 28.2), dms(105, 59, 20.5)), 15: (dms(19, 22, 36.7), dms(105, 56, 18.6)), 16: (dms(20, 36, 47.9), dms(107, 12, 32.2)),
     17: (dms(20, 42, 58.6), dms(107, 27, 14.9)), 18: (dms(20, 43, 21.3), dms(107, 27, 50.2)), 19: (dms(20, 59, 2.3), dms(107, 49, 20.9)),
     20: (dms(21, 1, 25.9), dms(107, 51, 46.5)), 21: (dms(21, 11, 19.6), dms(108, 1, 9.6)), 22: (dms(21, 11, 29.2), dms(108, 1, 17.7)),
     23: (dms(21, 28, 14.9), dms(108, 5, 32.8)), 24: (dms(21, 28, 12.5), dms(108, 6, 4.3))}
# Bảng 2.2
B = [(dms(21, 28, 12.5), dms(108, 6, 4.3)), (dms(21, 28, 1.7), dms(108, 6, 1.6)), (dms(21, 27, 50.1), dms(108, 5, 57.7)), (dms(21, 27, 39.5), dms(108, 5, 51.5)),
     (dms(21, 27, 28.2), dms(108, 5, 39.9)), (dms(21, 27, 23.1), dms(108, 5, 38.8)), (dms(21, 27, 8.2), dms(108, 5, 43.7)), (dms(21, 16, 32), dms(108, 8, 5)),
     (dms(21, 12, 35), dms(108, 12, 31)), (dms(20, 24, 5), dms(108, 22, 45)), (dms(19, 57, 33), dms(107, 55, 47)), (dms(19, 39, 33), dms(107, 31, 40)),
     (dms(19, 25, 26), dms(107, 21, 0)), (dms(19, 25, 26), dms(107, 12, 43)), (dms(19, 16, 4), dms(107, 11, 23)), (dms(19, 12, 55), dms(107, 9, 34)),
     (dms(18, 42, 52), dms(107, 9, 34)), (dms(18, 13, 49), dms(107, 34, 0)), (dms(18, 7, 8), dms(107, 37, 34)), (dms(18, 4, 13), dms(107, 39, 9)),
     (dms(17, 47, 0), dms(107, 58, 0))]

def di_ve(latlon, n=8):
    """Lộ trình đi – về qua các điểm, chia nhỏ từng đoạn để nét giữ thẳng sau khi làm trơn."""
    pts = []
    for (a, b) in zip(latlon, latlon[1:]):
        for t in range(n): pts.append((a[1] + (b[1] - a[1]) * t / n, a[0] + (b[0] - a[0]) * t / n))
    pts.append((latlon[-1][1], latlon[-1][0]))
    return [P(*p) for p in pts + pts[-2::-1]]

S = {
 "phien_ban": 2, "ten": "Đường cơ sở – vịnh Bắc Bộ", "phu_de": "Theo Bảng 2.1, 2.2 SGK",
 "nguon": "Vẽ bằng code theo Bảng 2.1, 2.2 và Hình 2.1, 2.2, SGK Lịch sử và Địa lí 8, Chủ đề chung 2, tr. 163–166; nền đất liền Natural Earth",
 "khung": P(99.0, 23.6) + P(119.5, 6.0), "nen_bien": [0.80, 0.88, 0.93], "chu_giai_xy": [0.03, 0.30], "sao_man_hinh": True,
 "vung_mau": nen([96, 4, 125, 27]),
 "dia_danh": cham(HS) + cham(TS) + [
  nh(112.0, 17.55, "QĐ. Hoàng Sa (Việt Nam)", dam=True, co=19, zoom_den=1.5), nh(112.0, 17.55, "QĐ. Hoàng Sa (Việt Nam)", dam=True, co=19, zoom_tu=1.9),
  nh(112.9, 15.0, "QĐ. Hoàng Sa (Việt Nam)", dam=True, co=19, zoom_tu=1.5, zoom_den=1.9), nh(114.4, 12.0, "QĐ. Trường Sa (Việt Nam)", dam=True, co=19),
  nh(111.0, 22.9, "TRUNG QUỐC", lon=True, zoom_den=1.6), nh(103.4, 19.2, "LÀO", lon=True, zoom_den=1.6), nh(104.7, 12.9, "CAM-PU-CHIA", lon=True, zoom_den=1.6),
  nh(101.0, 15.5, "THÁI LAN", lon=True, zoom_den=1.6), nh(116.6, 14.3, "BIỂN ĐÔNG", lon=True, zoom_den=1.6), nh(102.4, 10.6, "VỊNH THÁI LAN", dam=True, co=17, zoom_den=1.6),
  nh(106.9, 22.75, "TRUNG QUỐC", lon=True, zoom_tu=1.6),
  nh(109.6, 19.2, "đảo Hải Nam", dam=True, co=18, zoom_tu=1.6), nh(104.3, 19.0, "LÀO", lon=True, zoom_tu=1.6),
 ]
}
S["chu_giai"] = []
nhan = lambda lat, lon, chu, co=8, mau="ta": {"loai": "nhan", "vi_tri": P(lon, lat), "chu": chu, "co": co, "mau": mau}
S["doi_tuong"] = {"duong_cs": {"loai": "vong", "diem": di_ve([A[i] for i in range(1, 25)]), "rong": 3.2},
                  "phan_dinh": {"loai": "vong", "diem": di_ve(B), "rong": 3.2}}
# nhãn toàn cảnh (zoom 1) – chữ to
for ten, (lat, lon), dx, dy in [("A1", A[1], -0.9, 0.0), ("A2", A[2], 0.0, -0.55), ("A3 – A5", A[4], 0.9, -0.6), ("A6", A[6], 0.75, 0.0),
                                ("A10", A[10], 0.8, 0.0), ("A11", A[11], 0.85, 0.0), ("A24", A[24], 0.75, 0.25)]:
    S["doi_tuong"][f"z_{ten}"] = nhan(lat + dy, lon + dx, ten, 17)
# nhãn phía nam (A1 – A10)
for i, dx, dy, ten in [(1, -0.75, 0.0, "A1 Hòn Nhạn"), (2, 0.0, -0.3, "A2 Hòn Đá Lẻ"), (4, 0.0, -0.32, "A3 – A5 Côn Đảo"), (6, 0.95, 0.0, "A6 Hòn Hải"),
                       (7, 0.95, -0.12, "A7 Hòn Đôi"), (8, 1.1, 0.12, "A8 mũi Đại Lãnh"), (9, 0.95, 0.0, "A9 Hòn Ông Căn"), (10, 0.85, 0.0, "A10 Lý Sơn")]:
    S["doi_tuong"][f"n{i}"] = nhan(A[i][0] + dy, A[i][1] + dx * 1.15, ten, 9.5)
# nhãn phía bắc (A11 – A24)
for i, dx, dy, ten in [(11, 0.75, 0.0, "A11 Cồn Cỏ"), (12, 0.8, -0.05, "A12 Hòn Gió Lớn"), (13, 0.75, 0.08, "A13 Hòn Chim"), (14, 0.85, 0.0, "A14 Hòn Mắt Con"),
                       (15, 0.75, 0.0, "A15 Hòn Mê"), (16, 0.2, -0.22, "A16 Long Châu Đông"), (19, 0.85, -0.12, "A17 – A20"), (23, 0.85, 0.05, "A21 – A24")]:
    S["doi_tuong"][f"n{i}"] = nhan(A[i][0] + dy, A[i][1] + dx, ten, 6.2)
S["doi_tuong"]["d1"] = nhan(B[0][0] + 0.12, B[0][1] + 0.75, "Điểm số 1", 6.2)
S["doi_tuong"]["d10"] = nhan(B[9][0], B[9][1] + 0.62, "Điểm số 10", 6.2)
S["doi_tuong"]["d21"] = nhan(B[20][0] - 0.15, B[20][1] + 0.6, "Điểm số 21", 6.2)
S["doi_tuong"]["vbb_1"] = nhan(19.0, 107.6, "VỊNH BẮC BỘ", 7.5, "chu")
S["doi_tuong"]["vbb_2"] = nhan(18.95, 106.45, "VỊNH BẮC BỘ", 7.5, "chu")
S["doi_tuong"]["bach_long_vi"] = nhan(20.13, 107.72, "đảo Bạch Long Vĩ", 5.6, "chu")

def lan_luot(ids, tu, den):
    st = (den - tu) / len(ids)
    return [{"id": x, "tu": round(tu + i * st, 3), "den": round(tu + i * st + 0.08, 3)} for i, x in enumerate(ids)]
nam_ids = [f"n{i}" for i in (1, 2, 4, 6, 7, 8, 9, 10)]; bac_ids = [f"n{i}" for i in (11, 12, 13, 14, 15, 16, 19, 23)]
z_ids = ["z_A1", "z_A2", "z_A3 – A5", "z_A6", "z_A10", "z_A11", "z_A24"]
S["pha"] = {
 "tong_quan": {"mo_dau": True, "zoom": [1.0, 1.05], "chu_giai": [],
               "moc": [{"chu": "Đường cơ sở: đường gãy khúc nối các điểm từ 0 đến A24", "tu": 0.03, "den": 1.1}],
               "buoc": [{"id": "duong_cs", "tu": 0.08, "den": 1.3}] + lan_luot(z_ids, 0.1, 0.72)},
 "phia_nam": {"zoom": [1.62, 1.68], "tam": P(106.6, 10.9), "can_giua": [0.5, 0.5], "chu_giai": [], "hien": ["duong_cs"],
              "moc": [{"chu": "Các điểm A1 – A10", "tu": 0.03, "den": 1.1}], "buoc": lan_luot(nam_ids, 0.08, 0.8)},
 "phia_bac": {"zoom": [2.5, 2.6], "tam": P(106.8, 19.4), "can_giua": [0.5, 0.47], "chu_giai": [], "hien": ["duong_cs", "vbb_1"],
              "moc": [{"chu": "Các điểm A11 – A24", "tu": 0.03, "den": 1.1}], "buoc": lan_luot(bac_ids, 0.08, 0.8)},
 "vinh_bac_bo": {"zoom": [2.5, 2.6], "tam": P(107.6, 19.6), "can_giua": [0.5, 0.47], "chu_giai": [], "hien": ["vbb_2"],
                 "moc": [{"chu": "25 – 12 – 2000: đường phân định qua 21 điểm", "tu": 0.03, "den": 1.1}],
                 "buoc": [{"id": "phan_dinh", "tu": 0.08, "den": 1.2}, {"id": "d1", "tu": 0.1, "den": 0.2}, {"id": "d10", "tu": 0.35, "den": 0.45},
                          {"id": "d21", "tu": 0.6, "den": 0.7}, {"id": "bach_long_vi", "tu": 0.3, "den": 0.4}]},
 "toan_canh": {"zoom": [1.0, 1.05], "chu_giai": [], "hien": ["duong_cs", "phan_dinh"],
               "moc": [{"chu": "Vùng biển Việt Nam: khoảng 1 triệu km²", "tu": 0.05, "den": 1.1}]},
}
json.dump(S, open(f"{ROOT}/pipeline/maps/specs/duong-co-so.json", "w"), ensure_ascii=False)
print("ok", len(A), "điểm cơ sở,", len(B), "điểm phân định")
