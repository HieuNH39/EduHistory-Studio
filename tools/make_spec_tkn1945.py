"""Sa bàn Tổng khởi nghĩa tháng Tám năm 1945 (theo bảng 'Diễn biến chính', SGK LSĐL 9 tr. 37–38).
Bản đồ Việt Nam luôn có quần đảo Hoàng Sa, Trường Sa; không vẽ ranh giới tỉnh (chỉ đánh dấu tỉnh lị/địa danh).
Địa danh vẽ theo màn hình (cỡ chữ cố định), cụm miền Bắc chỉ hiện khi máy quay zoom vào."""
import json, sys
sys.path.insert(0, "/home/claude/eduhistory-studio/tools")
from make_vn_map import xy, nen, dao, ROOT
P = lambda lon, lat: xy(lon, lat)
D = {"tan_trao": (105.43, 21.80), "thai_nguyen": (105.84, 21.59), "ha_noi": (105.85, 21.03), "bac_giang": (106.19, 21.27),
     "hai_duong": (106.33, 20.94), "ha_tinh": (105.90, 18.34), "quang_nam": (108.33, 15.88), "hue": (107.58, 16.46),
     "sai_gon": (106.70, 10.78), "dong_nai_thuong": (108.07, 11.58), "ha_tien": (104.48, 10.38),
     "thanh_hoa": (105.78, 19.80), "nghe_an": (105.68, 18.67), "quang_ngai": (108.80, 15.12), "khanh_hoa": (109.19, 12.24),
     "chau_tho": (106.15, 20.45), "thua_thien": (107.35, 16.30)}
Q = lambda k: P(*D[k])
def dd(k, ten, lech, zt=0, zd=99, **kw): return {"ten": ten, "vi_tri": Q(k), "kieu": "diem", "man_hinh": True, "lech": lech, "zoom_tu": zt, "zoom_den": zd, **kw}
BAC = 2.0   # từ mức zoom này mới hiện cụm địa danh miền Bắc
S = {
 "phien_ban": 2, "ten": "Tổng khởi nghĩa tháng Tám năm 1945", "phu_de": "Diễn biến chính",
 "nguon": "Sơ đồ minh hoạ theo bảng diễn biến chính, SGK Lịch sử và Địa lí 9, tr. 37–38; nền bản đồ Natural Earth",
 "khung": P(96.5, 24.4) + P(125.9, 8.4), "sao_man_hinh": True, "nen_bien": [0.80, 0.88, 0.93], "chu_giai_xy": [0.03, 0.66],
 "vung_mau": nen([94, 5, 128, 27]),
 "dia_danh": [
  dd("tan_trao", "Tân Trào", [-24, -12], zt=BAC, dam=True), dd("thai_nguyen", "Thái Nguyên", [22, -16], zt=BAC),
  dd("bac_giang", "Bắc Giang", [14, -4], zt=BAC, dam=True), dd("hai_duong", "Hải Dương", [14, 8], zt=BAC),
  dd("ha_noi", "Hà Nội", [-14, 8], zt=BAC, dam=True), dd("ha_noi", "Hà Nội", [-12, 0], zd=BAC - 0.01, dam=True),
  dd("ha_tinh", "Hà Tĩnh", [14, 0]), dd("hue", "Huế", [-14, -4], dam=True), dd("quang_nam", "Quảng Nam", [14, 0]),
  dd("sai_gon", "Sài Gòn", [14, 6], dam=True), dd("dong_nai_thuong", "Đồng Nai Thượng", [14, -6]), dd("ha_tien", "Hà Tiên", [-12, 0]),
  {"ten": "LÀO", "vi_tri": P(103.6, 19.6), "lon": True, "man_hinh": True, "lech": [0, 0]},
  {"ten": "CAM-PU-CHIA", "vi_tri": P(104.6, 12.9), "lon": True, "man_hinh": True, "lech": [0, 0]},
  {"ten": "THÁI LAN", "vi_tri": P(101.0, 15.6), "lon": True, "man_hinh": True, "lech": [0, 0]},
  {"ten": "TRUNG QUỐC", "vi_tri": P(104.6, 23.2), "lon": True, "man_hinh": True, "lech": [0, 0], "zoom_tu": BAC},
  {"ten": "TRUNG QUỐC", "vi_tri": P(110.8, 23.0), "lon": True, "man_hinh": True, "lech": [0, 0], "zoom_den": BAC - 0.01},
  {"ten": "BIỂN ĐÔNG", "vi_tri": P(116.0, 14.2), "lon": True, "man_hinh": True, "lech": [0, 0]},
  {"ten": "VỊNH BẮC BỘ", "vi_tri": P(107.6, 19.9), "dam": True, "man_hinh": True, "lech": [0, 0], "zoom_tu": BAC, "co": 17}
 ] + dao(112.0, 16.5, "QĐ. Hoàng Sa") + dao(114.0, 9.6, "QĐ. Trường Sa", n=9, r=.8),
 "chu_giai": [{"loai": "vong", "nhan": "Khởi nghĩa ở nhiều xã, huyện"}, {"loai": "mui_ten_ta", "nhan": "Giải phóng quân tiến công"}, {"loai": "sao", "nhan": "Giành chính quyền"}],
 "doi_tuong": {
  "sao_tt": {"loai": "sao", "vi_tri": Q("tan_trao")},
  **{f"v_{k}": {"loai": "vong", "diem": [P(D[k][0] + .3 * c, D[k][1] + .24 * s) for c, s in [(1, 0), (.7, .7), (0, 1), (-.7, .7), (-1, 0), (-.7, -.7), (0, -1), (.7, -.7), (1, 0)]]}
     for k in ("chau_tho", "thanh_hoa", "nghe_an", "ha_tinh", "thua_thien", "quang_ngai", "khanh_hoa")},
  "tn": {"loai": "mui_ten_ta", "diem": [P(105.45, 21.78), P(105.62, 21.74), P(105.80, 21.62)], "w0": 4, "w1": 7},
  **{f"sao_{k}": {"loai": "sao", "vi_tri": Q(k)} for k in ("thai_nguyen", "bac_giang", "hai_duong", "ha_tinh", "quang_nam", "ha_noi", "hue", "sai_gon", "dong_nai_thuong", "ha_tien")}
 },
 "pha": {}
}
BAC_TAM, BAC_Z = P(105.95, 21.25), [2.7, 2.85]
def pha(**kw): return kw
S["pha"] = {
 "thoi_co": pha(mo_dau=True, zoom=[1.0, 1.04], chu_giai=[], moc=[{"chu": "Tháng 8 – 1945", "tu": 0.05, "den": 0.97}],
                bang={"chu": "15 – 8 – 1945: Nhật Bản đầu hàng Đồng minh không điều kiện", "tu": 0.25, "y": 0.70}),
 "tan_trao": pha(zoom=BAC_Z, tam=BAC_TAM, can_giua=[0.5, 0.5], chu_giai=[],
                 buoc=[{"id": "sao_tt", "tu": 0.05, "den": 0.15}],
                 moc=[{"chu": "13 – 8 – 1945: Quân lệnh số 1", "tu": 0.04, "den": 0.5}, {"chu": "14 và 15 – 8: Hội nghị toàn quốc của Đảng ở Tân Trào", "tu": 0.5, "den": 1.1}]),
 "dai_hoi": pha(zoom=[2.85, 2.95], tam=BAC_TAM, can_giua=[0.5, 0.5], chu_giai=[], hien=["sao_tt"],
                moc=[{"chu": "16 và 17 – 8: Đại hội Quốc dân ở Tân Trào", "tu": 0.04, "den": 1.1}]),
 "ngay_14": pha(zoom=[1.0, 1.06], chu_giai=["vong"], hien=["sao_tt"],
                moc=[{"chu": "14 – 8: khởi nghĩa ở nhiều xã, huyện", "tu": 0.05, "den": 1.1}],
                buoc=[{"id": f"v_{k}", "tu": 0.08 + .06 * i, "den": 0.2 + .06 * i} for i, k in enumerate(("chau_tho", "thanh_hoa", "nghe_an", "ha_tinh", "thua_thien", "quang_ngai", "khanh_hoa"))]),
 "ngay_16": pha(zoom=BAC_Z, tam=BAC_TAM, can_giua=[0.5, 0.5], chu_giai=["mui_ten_ta", "sao"], hien=["sao_tt"],
                moc=[{"chu": "16 – 8: Giải phóng quân tiến về Thái Nguyên", "tu": 0.05, "den": 1.1}],
                buoc=[{"id": "tn", "tu": 0.15, "den": 0.55}, {"id": "sao_thai_nguyen", "tu": 0.55, "den": 0.65}]),
 "ngay_18": pha(zoom=[1.0, 1.08], chu_giai=["sao"], hien=["sao_tt", "sao_thai_nguyen"],
                moc=[{"chu": "18 – 8: giành chính quyền ở tỉnh lị sớm nhất", "tu": 0.05, "den": 1.1}],
                buoc=[{"id": "sao_bac_giang", "tu": 0.08, "den": 0.16}, {"id": "sao_hai_duong", "tu": 0.14, "den": 0.22}, {"id": "sao_ha_tinh", "tu": 0.2, "den": 0.28}, {"id": "sao_quang_nam", "tu": 0.26, "den": 0.34}]),
 "ngay_19": pha(zoom=BAC_Z, tam=BAC_TAM, can_giua=[0.5, 0.5], chu_giai=["sao"], hien=["sao_tt", "sao_thai_nguyen", "sao_bac_giang", "sao_hai_duong"],
                moc=[{"chu": "19 – 8 – 1945: Hà Nội", "tu": 0.05, "den": 1.1}],
                buoc=[{"id": "sao_ha_noi", "tu": 0.12, "den": 0.24}]),
 "ngay_23_28": pha(zoom=[1.0, 1.04], chu_giai=["sao"], hien=["sao_tt", "sao_thai_nguyen", "sao_bac_giang", "sao_hai_duong", "sao_ha_tinh", "sao_quang_nam", "sao_ha_noi"],
                   moc=[{"chu": "23 – 8: Huế", "tu": 0.03, "den": 0.34}, {"chu": "24, 25 – 8: Sài Gòn", "tu": 0.34, "den": 0.7}, {"chu": "28 – 8: Đồng Nai Thượng, Hà Tiên", "tu": 0.7, "den": 1.1}],
                   buoc=[{"id": "sao_hue", "tu": 0.05, "den": 0.13}, {"id": "sao_sai_gon", "tu": 0.37, "den": 0.45}, {"id": "sao_dong_nai_thuong", "tu": 0.73, "den": 0.8}, {"id": "sao_ha_tien", "tu": 0.75, "den": 0.82}])
}
json.dump(S, open(f"{ROOT}/pipeline/maps/specs/tong-khoi-nghia-1945.json", "w"), ensure_ascii=False)
print("ok")
