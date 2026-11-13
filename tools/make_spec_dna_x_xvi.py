"""Sa bàn (saban2) 'Các vương quốc phong kiến Đông Nam Á (nửa sau thế kỉ X – nửa đầu thế kỉ XVI)'.
Vẽ lại, giản lược theo Hình 2, SGK Lịch sử và Địa lí 7, Bài 6, tr. 36: nền đất liền Natural Earth 1:50m (đường viền là
biên giới quốc gia ngày nay, như chú giải lược đồ SGK), tên vương quốc đặt theo vị trí trên lược đồ, tên quốc gia ngày nay
trong ngoặc. Luôn có quần đảo Hoàng Sa, Trường Sa của Việt Nam. Chỉ ghi các vương quốc có trong lược đồ / bài học."""
import json, sys
sys.path.insert(0, "/home/claude/eduhistory-studio/tools")
from make_vn_map import xy, dao, ROOT

DAT, DAT_VN = [0.93, 0.89, 0.78], [0.96, 0.89, 0.72]
def nen(bbox):
    g = json.load(open(f"{ROOT}/assets/geo/ne_50m_dong_nam_a.geojson")); out = []
    for f in g["features"]:
        geo = f["geometry"]; polys = geo["coordinates"] if geo["type"] == "MultiPolygon" else [geo["coordinates"]]
        for poly in polys:
            ring = poly[0]; xs = [c[0] for c in ring]; ys = [c[1] for c in ring]
            if max(xs) < bbox[0] or min(xs) > bbox[2] or max(ys) < bbox[1] or min(ys) > bbox[3]: continue
            out.append({"diem": [xy(*c) for c in ring], "mau": DAT_VN if f["properties"]["ADMIN"] == "Vietnam" else DAT, "vien": 0.9})
    return out

# vương quốc: khoá, tên, [kinh độ, vĩ độ] vị trí nhãn (theo lược đồ Hình 2), cỡ chữ
VQ1 = [("pa_gan", "PA-GAN", (95.0, 22.3), 15), ("ha_ri", "HA-RI-PUN-GIAY-A", (98.9, 19.6), 14), ("dai_viet", "ĐẠI VIỆT", (105.3, 22.5), 15),
       ("cham_pa", "CHĂM-PA", (110.9, 12.6), 15), ("cam_pu_chia", "CAM-PU-CHIA", (104.5, 13.9), 15), ("sri", "SRI VI-GIAY-A", (100.0, -2.8), 15)]
VQ2 = [("a_ut", "A-ÚT-THAY-A", (100.3, 15.7), 15), ("lan_xang", "LAN XANG", (102.8, 20.9), 15),
       ("mo_gio", "MÔ-GIÔ-PA-HÍT", (111.0, -9.0), 15), ("ma_lac_ca", "MA-LẮC-CA", (104.8, 1.7), 15)]
NAY = [("(MI-AN-MA)", (95.3, 20.9)), ("(THÁI LAN)", (100.3, 14.6)), ("(LÀO)", (103.7, 19.4)), ("(VIỆT NAM)", (106.7, 21.0)),
       ("(CAM-PU-CHIA)", (104.6, 12.8)), ("(MA-LAI-XI-A)", (101.5, 4.7)), ("(IN-ĐÔ-NÊ-XI-A)", (114.0, -2.0)), ("(PHI-LÍP-PIN)", (122.6, 12.0))]

doi = {}
for k, ten, p, co in VQ1 + VQ2:
    doi[f"v_{k}"] = {"loai": "nhan", "vi_tri": xy(*p), "chu": ten, "co": co, "mau": "ta"}
doi["eo_bien"] = {"loai": "nhan", "vi_tri": xy(98.6, 6.4), "chu": "Eo biển Ma-lắc-ca", "co": 12, "mau": "dich"}
doi["vong_mlc"] = {"loai": "vong", "rong": 4, "diem": [xy(101.1 + 2.3 * c, 3.3 + 2.3 * s) for c, s in [(1, 0), (.7, .7), (0, 1), (-.7, .7), (-1, 0), (-.7, -.7), (0, -1), (.7, -.7)]]}
V1 = [f"v_{k}" for k, *_ in VQ1]; V2 = [f"v_{k}" for k, *_ in VQ2]

S = {
 "phien_ban": 2, "ten": "Đông Nam Á (thế kỉ X – XVI)", "phu_de": "Các vương quốc phong kiến",
 "nguon": "Vẽ lại, giản lược theo Hình 2, SGK Lịch sử và Địa lí 7, Bài 6, tr. 36; nền bản đồ Natural Earth",
 "khung": xy(91, 25) + xy(125, -9.6), "nen_bien": [0.80, 0.88, 0.93], "chu_giai_xy": [0.03, 0.66], "lech_x": 0.08,
 "vung_mau": nen([88, -13, 130, 30]),
 "dia_danh": [{"ten": t, "vi_tri": xy(*p), "co": 10.5} for t, p in NAY]
             + [{"ten": "BIỂN ĐÔNG", "vi_tri": xy(114.0, 14.2), "co": 17, "dam": True}, {"ten": "ẤN ĐỘ DƯƠNG", "vi_tri": xy(94.5, -6.0), "co": 15, "dam": True},
                {"ten": "THÁI BÌNH DƯƠNG", "vi_tri": xy(123.5, 6.5), "co": 13, "dam": True}]
             + dao(112.0, 16.5, "QĐ. Hoàng Sa") + dao(114.0, 9.6, "QĐ. Trường Sa", n=9, r=.8),
 "chu_giai": [],
 "doi_tuong": doi,
 "pha": {
  "x_xiii": {"mo_dau": True, "zoom": [1.0, 1.03], "moc": [{"chu": "Thế kỉ X – XIII", "tu": 0.05, "den": 1.1}],
             "buoc": [{"id": v, "tu": 0.12 + 0.12 * i, "den": 0.2 + 0.12 * i} for i, v in enumerate(V1)]},
  "xiii_xvi": {"zoom": [1.03, 1.0], "hien": V1, "moc": [{"chu": "Thế kỉ XIII – XVI", "tu": 0.05, "den": 1.1}],
               "buoc": [{"id": v, "tu": 0.15 + 0.17 * i, "den": 0.25 + 0.17 * i} for i, v in enumerate(V2)]},
  "ma_lac_ca": {"zoom": [1.0, 1.75], "tam": xy(101.5, 2.0), "hien": V1 + V2, "moc": [{"chu": "Thế kỉ XV", "tu": 0.05, "den": 1.1}],
                "buoc": [{"id": "vong_mlc", "tu": 0.45, "den": 0.65}, {"id": "eo_bien", "tu": 0.6, "den": 0.75}]}
 }
}
json.dump(S, open(f"{ROOT}/pipeline/maps/specs/dong-nam-a-x-xvi.json", "w"), ensure_ascii=False)
print("ok", len(S["vung_mau"]))
