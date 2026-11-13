"""Sinh sa bàn (saban2) 'hanh-chinh-nguyen': cả nước chia thành 30 tỉnh và 1 phủ (Thừa Thiên) sau Cải cách Minh Mạng
(SGK LSĐL 8, Bài 16, tr. 72, Hình 16.3 'Lược đồ hành chính Việt Nam thời Nguyễn').
Tên và vị trí tương đối các tỉnh lấy theo nhãn trên Hình 16.3; không vẽ ranh giới tỉnh (SGK không vẽ). Nền đất liền Natural Earth;
quần đảo Hoàng Sa, Trường Sa vẽ bằng chấm, nhãn ghi rõ thuộc Việt Nam."""
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

# (tên, lon, lat) – vị trí đặt nhãn theo Hình 16.3
BAC = [("CAO BẰNG", 106.25, 22.75), ("TUYÊN QUANG", 105.15, 22.05), ("LẠNG SƠN", 106.8, 21.95), ("THÁI NGUYÊN", 105.75, 21.68),
       ("HƯNG HOÁ", 104.25, 21.45), ("SƠN TÂY", 105.2, 21.13), ("BẮC NINH", 106.2, 21.34), ("QUẢNG YÊN", 107.2, 21.12),
       ("HÀ NỘI", 105.45, 20.93), ("HẢI DƯƠNG", 106.62, 20.95), ("HƯNG YÊN", 106.15, 20.68), ("NAM ĐỊNH", 106.4, 20.42),
       ("NINH BÌNH", 105.75, 20.22), ("THANH HOÁ", 105.45, 19.85), ("NGHỆ AN", 105.0, 19.1)]
TRUNG = [("HÀ TĨNH", 105.65, 18.35), ("QUẢNG BÌNH", 106.2, 17.55), ("QUẢNG TRỊ", 106.4, 16.95), ("QUẢNG NAM", 107.75, 15.75),
         ("QUẢNG NGÃI", 108.45, 15.05), ("BÌNH ĐỊNH", 108.65, 14.15), ("PHÚ YÊN", 108.85, 13.2), ("KHÁNH HOÀ", 108.75, 12.3),
         ("BÌNH THUẬN", 107.9, 11.3)]
NAM = [("BIÊN HOÀ", 107.15, 11.2), ("PHIÊN AN", 107.0, 10.75), ("ĐỊNH TƯỜNG", 106.55, 10.33), ("VĨNH LONG", 106.15, 9.9),
       ("AN GIANG", 104.95, 10.8), ("HÀ TIÊN", 104.45, 10.3)]

S = {
 "phien_ban": 2, "ten": "Việt Nam thời Nguyễn", "phu_de": "30 tỉnh và 1 phủ (Thừa Thiên)",
 "nguon": "Vẽ bằng code theo Hình 16.3, SGK Lịch sử và Địa lí 8, Bài 16, tr. 72; nền đất liền Natural Earth",
 "khung": P(99.0, 23.6) + P(119.5, 6.0), "nen_bien": [0.80, 0.88, 0.93], "chu_giai_xy": [0.03, 0.30], "sao_man_hinh": True,
 "vung_mau": nen([96, 4, 125, 27]),
 "dia_danh": cham(HS, zoom_den=2.8) + cham(TS) + [
  nh(112.0, 17.55, "QĐ. Hoàng Sa (Việt Nam)", dam=True, co=19, zoom_den=2.8), nh(114.4, 12.0, "QĐ. Trường Sa (Việt Nam)", dam=True, co=19),
  nh(111.0, 22.9, "TRUNG QUỐC", lon=True, zoom_den=1.5), nh(103.4, 19.2, "LÀO", lon=True, zoom_den=1.5), nh(104.7, 12.9, "CAM-PU-CHIA", lon=True, zoom_den=1.5),
  nh(101.0, 15.5, "THÁI LAN", lon=True, zoom_den=1.5), nh(116.6, 14.3, "BIỂN ĐÔNG", lon=True, zoom_den=1.5), nh(110.6, 13.0, "BIỂN ĐÔNG", lon=True, zoom_tu=1.5, zoom_den=2.2),
 ]
}
S["chu_giai"] = []
S["doi_tuong"] = {}
for ds, nhom in ((BAC, "b"), (TRUNG, "t"), (NAM, "n")):
    for i, (ten, lon, lat) in enumerate(ds):
        S["doi_tuong"][f"{nhom}{i}"] = {"loai": "nhan", "vi_tri": P(lon, lat), "chu": ten, "co": {"b": 7.6, "t": 13, "n": 11}[nhom], "mau": "chu"}
S["doi_tuong"]["kinh_do"] = {"loai": "thanh_sang", "vi_tri": P(107.58, 16.47)}
S["doi_tuong"]["thua_thien"] = {"loai": "nhan", "vi_tri": P(106.1, 16.3), "chu": "PHỦ THỪA THIÊN", "co": 13.5, "mau": "ta"}
S["doi_tuong"]["phu_xuan"] = {"loai": "nhan", "vi_tri": P(109.25, 16.95), "chu": "Phú Xuân (kinh đô)", "co": 12, "mau": "ta"}

def lan_luot(nhom, n, tu=0.12, den=0.85):
    st = (den - tu) / n
    return [{"id": f"{nhom}{i}", "tu": round(tu + i * st, 3), "den": round(tu + i * st + 0.06, 3)} for i in range(n)]
bac_ids = [f"b{i}" for i in range(len(BAC))]; trung_ids = [f"t{i}" for i in range(len(TRUNG))]; nam_ids = [f"n{i}" for i in range(len(NAM))]
S["pha"] = {
 "tong_quan": {"mo_dau": True, "zoom": [1.0, 1.05], "chu_giai": [],
               "moc": [{"chu": "Những năm 1831 – 1832: Cải cách Minh Mạng", "tu": 0.05, "den": 1.1}],
               "buoc": [{"id": "kinh_do", "tu": 0.3, "den": 0.45}]},
 "bac": {"zoom": [2.95, 3.05], "tam": P(105.6, 21.05), "can_giua": [0.5, 0.5], "chu_giai": [],
         "moc": [{"chu": "Các tỉnh phía bắc", "tu": 0.03, "den": 1.1}], "buoc": lan_luot("b", len(BAC))},
 "trung": {"zoom": [1.55, 1.62], "tam": P(108.4, 14.6), "can_giua": [0.5, 0.45], "chu_giai": [], "hien": ["kinh_do"],
           "moc": [{"chu": "Phủ Thừa Thiên và các tỉnh miền Trung", "tu": 0.03, "den": 1.1}],
           "buoc": [{"id": "thua_thien", "tu": 0.06, "den": 0.14}, {"id": "phu_xuan", "tu": 0.1, "den": 0.18}] + lan_luot("t", len(TRUNG), 0.22, 0.88)},
 "nam": {"zoom": [2.1, 2.2], "tam": P(107.6, 10.2), "can_giua": [0.5, 0.42], "chu_giai": [],
         "moc": [{"chu": "Các tỉnh phía nam", "tu": 0.03, "den": 1.1}], "buoc": lan_luot("n", len(NAM), 0.12, 0.7)},
 "toan_quoc": {"zoom": [1.0, 1.05], "chu_giai": [], "hien": ["kinh_do"],
               "bang": {"chu": "Cả nước: 30 tỉnh và 1 phủ (Thừa Thiên)", "tu": 0.15, "y": 0.2}}
}
json.dump(S, open(f"{ROOT}/pipeline/maps/specs/hanh-chinh-nguyen.json", "w"), ensure_ascii=False)
print("ok", len(BAC) + len(TRUNG) + len(NAM), "tỉnh")
