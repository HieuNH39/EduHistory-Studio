"""Sa bàn (saban2) 'Kháng chiến chống Tống năm 981' do Lê Hoàn lãnh đạo.
Vẽ lại, giản lược theo Hình 1 'Lược đồ cuộc kháng chiến chống Tống năm 981', SGK Lịch sử và Địa lí 7, Bài 10, tr. 49:
toạ độ cục bộ đo trên ảnh lược đồ (khung 137..1290 × 355..1125); sông, bờ biển, mũi tên giản lược theo lược đồ.
Như lược đồ SGK, có ô bản đồ nhỏ Việt Nam (nền Natural Earth 1:50m) thể hiện quần đảo Hoàng Sa, Trường Sa."""
import json, math
ROOT = "/home/claude/eduhistory-studio"

# ---- ô bản đồ nhỏ Việt Nam (đặt bên phải, ngoài khung lược đồ, tránh logo và thẻ mốc)
IX0, IY0, IX1, IY1 = 1320, 853, 1536, 1090
LON0, LAT0, KY = 101.0, 24.5, 12.8
KX = KY * math.cos(math.radians(15))
def ip(lon, lat): return [round(IX0 + (lon - LON0) * KX, 1), round(IY0 + (LAT0 - lat) * KY, 1)]
def clip(poly, x0, y0, x1, y1):
    def cut(pts, inside, inter):
        out = []
        for i in range(len(pts)):
            a, b = pts[i - 1], pts[i]
            if inside(b):
                if not inside(a): out.append(inter(a, b))
                out.append(b)
            elif inside(a): out.append(inter(a, b))
        return out
    def ix(a, b, x): t = (x - a[0]) / (b[0] - a[0]); return [x, a[1] + t * (b[1] - a[1])]
    def iy(a, b, y): t = (y - a[1]) / (b[1] - a[1]); return [a[0] + t * (b[0] - a[0]), y]
    for inside, inter in ((lambda p: p[0] >= x0, lambda a, b: ix(a, b, x0)), (lambda p: p[0] <= x1, lambda a, b: ix(a, b, x1)),
                          (lambda p: p[1] >= y0, lambda a, b: iy(a, b, y0)), (lambda p: p[1] <= y1, lambda a, b: iy(a, b, y1))):
        poly = cut(poly, inside, inter)
        if not poly: return []
    return poly
def inset():
    g = json.load(open(f"{ROOT}/assets/geo/ne_50m_dong_nam_a.geojson"))
    out = [{"diem": [[IX0, IY0], [IX1, IY0], [IX1, IY1], [IX0, IY1]], "mau": [0.80, 0.88, 0.93], "vien": 1.6}]
    for f in g["features"]:
        geo = f["geometry"]; polys = geo["coordinates"] if geo["type"] == "MultiPolygon" else [geo["coordinates"]]
        for poly in polys:
            pts = clip([ip(*c) for c in poly[0]], IX0, IY0, IX1, IY1)
            if len(pts) >= 3:
                out.append({"diem": [[round(x, 1), round(y, 1)] for x, y in pts], "mau": [0.96, 0.89, 0.72] if f["properties"]["ADMIN"] == "Vietnam" else [0.88, 0.87, 0.83], "vien": 0.5})
    return out
def dao_inset(lon, lat, ten, n, r, lech):
    import random; random.seed(int(lon * 100 + lat))
    pts = [ip(lon + random.uniform(-r, r), lat + random.uniform(-r, r)) for _ in range(n)]
    return [{"ten": "", "vi_tri": p, "kieu": "diem"} for p in pts] + [{"ten": ten, "vi_tri": [ip(lon, lat)[0] + lech[0], ip(lon, lat)[1] + lech[1]], "co": 8, "dam": True}]

# ---- biển Vịnh Bắc Bộ (góc dưới bên phải lược đồ) và vài đảo
BIEN = [[1700, 380], [1290, 470], [1200, 520], [1127, 570], [1060, 600], [1000, 630], [940, 670], [890, 720], [850, 770], [810, 805], [770, 840],
        [740, 880], [715, 920], [690, 960], [670, 1010], [640, 1050], [600, 1090], [560, 1180], [1700, 1180]]
DAO = [[[955, 690], [975, 680], [985, 700], [962, 708]], [[1010, 665], [1035, 655], [1040, 676], [1015, 684]], [[905, 745], [925, 738], [930, 757], [910, 762]],
       [[1070, 640], [1090, 632], [1096, 650], [1076, 656]], [[860, 790], [878, 782], [884, 800], [864, 806]], [[960, 1040], [972, 1036], [976, 1048], [964, 1052]]]
SONG = [
 {"ten": "S. Hồng", "nhan": [462, 838], "goc": 62, "rong": 8, "diem": [[137, 650], [247, 645], [297, 675], [367, 705], [407, 727], [430, 775], [457, 825], [487, 875], [517, 925], [547, 965], [590, 1000], [660, 1030]]},
 {"ten": "", "nhan": [478, 700], "goc": -8, "rong": 5, "diem": [[407, 727], [440, 720], [490, 708], [530, 702], [565, 707]]},
 {"ten": "S. Cầu", "nhan": [430, 572], "goc": 62, "rong": 5, "diem": [[400, 520], [432, 585], [478, 640], [520, 677], [565, 707]]},
 {"ten": "S. Thương", "nhan": [625, 572], "goc": -38, "rong": 5, "diem": [[690, 520], [640, 560], [600, 610], [578, 660], [565, 707]]},
 {"ten": "", "nhan": [665, 640], "goc": -18, "rong": 5, "diem": [[760, 620], [700, 640], [640, 662], [600, 685], [565, 707]]},
 {"ten": "", "nhan": [672, 735], "goc": 18, "rong": 6, "diem": [[565, 707], [620, 725], [670, 743], [715, 760], [745, 800], [775, 840]]},
 {"ten": "S. Thái Bình", "nhan": [600, 815], "goc": 62, "rong": 6, "diem": [[565, 707], [585, 760], [612, 820], [650, 880], [690, 940]]},
 {"ten": "", "nhan": [560, 868], "goc": -10, "rong": 4, "diem": [[480, 868], [530, 862], [580, 866], [630, 875]]},
 {"ten": "S. Đáy", "nhan": [380, 880], "goc": 65, "rong": 5, "diem": [[330, 790], [352, 840], [380, 890], [410, 945], [440, 995], [470, 1050], [500, 1125]]},
 {"ten": "", "nhan": [820, 495], "goc": 22, "rong": 4, "diem": [[700, 462], [760, 480], [820, 505], [880, 532]]},
]
def dd(ten, p, kieu="diem", lech=None, **kw):
    d = {"ten": ten, "vi_tri": p, "kieu": kieu, **kw}
    if lech: d["nhan"] = [p[0] + lech[0], p[1] + lech[1]]
    return d
SAO = {"dai_la": [407, 727], "tay_ket": [447, 785], "luc_dau": [565, 707], "bach_dang": [715, 760]}
doi = {
 "tong_thuy": {"loai": "mui_ten_dich", "diem": [[1190, 598], [1120, 636], [1030, 672], [900, 720], [770, 756]], "w0": 5, "w1": 10},
 "tong_bo": {"loai": "mui_ten_dich", "diem": [[1050, 585], [960, 612], [860, 645], [760, 672], [660, 692], [585, 704]], "w0": 5, "w1": 10},
 "tong_bo2": {"loai": "mui_ten_dich", "diem": [[550, 712], [500, 714], [440, 722]], "w0": 4, "w1": 8},
 "tong_tk": {"loai": "mui_ten_dich", "diem": [[540, 730], [500, 752], [462, 778]], "w0": 4, "w1": 8},
 "ta_dl": {"loai": "mui_ten_ta", "diem": [[372, 800], [388, 765], [401, 738]], "w0": 6, "w1": 11},
 "ta_tk": {"loai": "mui_ten_ta", "diem": [[420, 842], [436, 815], [445, 797]], "w0": 6, "w1": 11},
 "ta_ld": {"loai": "mui_ten_ta", "diem": [[515, 765], [540, 735], [557, 714]], "w0": 6, "w1": 11},
 "ta_bd1": {"loai": "mui_ten_ta", "diem": [[688, 832], [703, 798], [711, 772]], "w0": 6, "w1": 11},
 "ta_bd2": {"loai": "mui_ten_ta", "diem": [[790, 805], [756, 786], [726, 768]], "w0": 6, "w1": 11},
 "rut_bd": {"loai": "rut_chay", "diem": [[735, 790], [790, 838], [870, 850], [960, 822], [1080, 772], [1160, 742]]},
 "rut_ld": {"loai": "rut_chay", "diem": [[600, 690], [700, 662], [800, 632], [900, 602], [990, 578]]},
 "coc": {"loai": "coc", "diem": [[728, 805], [738, 812], [746, 806], [733, 818], [744, 822], [752, 815]]},
 **{f"sao_{k}": {"loai": "sao", "vi_tri": p} for k, p in SAO.items()},
 "pt": {"loai": "tuong", "phia": -1, "diem": [[422, 810], [457, 848], [482, 888], [507, 928], [532, 968]]},
 "khung_nho": {"loai": "vong", "rong": 2.0, "diem": [ip(105.0, 21.8), ip(108.0, 21.8), ip(108.0, 19.9), ip(105.0, 19.9)]},
}
NEN = ["khung_nho"]
S = {
 "phien_ban": 2, "ten": "Kháng chiến chống Tống năm 981", "phu_de": "Lê Hoàn trực tiếp lãnh đạo",
 "nguon": "Vẽ lại, giản lược theo Hình 1, SGK Lịch sử và Địa lí 7, Bài 10, tr. 49; ô nhỏ: nền Natural Earth",
 "khung": [137, 355, 1290, 1125], "tam": [700, 760], "chu_giai_xy": [0.69, 0.36],
 "vung_mau": [{"diem": BIEN, "mau": [0.612, 0.765, 0.835], "vien": 1.6}] + inset(),
 "dat_noi": DAO,
 "song": SONG,
 "dia_danh": [dd("TỐNG", [1000, 430], kieu=None, lon=True, co=20), dd("ĐẠI CỒ VIỆT", [430, 625], kieu=None, lon=True, co=20),
              dd("VỊNH BẮC BỘ", [1060, 880], kieu=None, dam=True, co=15),
              dd("Đại La", SAO["dai_la"], kieu=None, lech=(-42, -16), dam=True, co=13), dd("Tây Kết", SAO["tay_ket"], kieu=None, lech=(50, 6), dam=True, co=13),
              dd("Lục Đầu Giang", SAO["luc_dau"], kieu=None, lech=(-62, -30), dam=True, co=13), dd("Bạch Đằng", SAO["bach_dang"], kieu=None, lech=(-12, -40), dam=True, co=13),
              dd("Xa Sơn", [585, 748], lech=(-4, 17), co=11), dd("Thường Sơn", [668, 778], lech=(-6, 17), co=11), dd("Bằng Châu", [642, 847], lech=(36, 0), co=11),
              dd("Vân Sàng", [517, 1008], lech=(38, 0), co=11), dd("Nhân Phẩm", [509, 1080], lech=(42, 0), co=11),
              dd("HOA LƯ", [445, 990], kieu="thanh", lech=(0, 30), dam=True, co=13),
              {"ten": "VIỆT NAM", "vi_tri": ip(105.3, 15.4), "co": 7, "dam": True}]
             + dao_inset(112.0, 16.5, "QĐ. Hoàng Sa", 5, .5, (0, -15)) + dao_inset(114.0, 9.6, "QĐ. Trường Sa", 6, .8, (0, -20)),
 "chu_giai": [{"loai": "mui_ten_dich", "nhan": "Quân Tống tiến đánh"}, {"loai": "mui_ten_ta", "nhan": "Quân ta chặn đánh"},
              {"loai": "rut_chay", "nhan": "Quân Tống rút chạy"}, {"loai": "sao", "nhan": "Nơi diễn ra các trận đánh lớn"}],
 "doi_tuong": doi,
 "pha": {
  "tong_tien": {"mo_dau": True, "zoom": [1.0, 1.03], "hien": NEN, "chu_giai": ["mui_ten_dich"],
                "moc": [{"chu": "Đầu năm 981", "tu": 0.05, "den": 1.1}],
                "buoc": [{"id": "tong_thuy", "tu": 0.12, "den": 0.5}, {"id": "tong_bo", "tu": 0.3, "den": 0.75}, {"id": "tong_bo2", "tu": 0.72, "den": 0.88}, {"id": "tong_tk", "tu": 0.78, "den": 0.95}]},
  "chan_danh": {"zoom": [1.0, 1.03], "hien": NEN + ["tong_thuy", "tong_bo", "tong_bo2", "tong_tk"], "chu_giai": ["mui_ten_dich", "mui_ten_ta", "sao"],
                "moc": [{"chu": "Lê Hoàn lãnh đạo kháng chiến", "tu": 0.05, "den": 1.1}],
                "buoc": [{"id": "ta_dl", "tu": 0.08, "den": 0.22}, {"id": "sao_dai_la", "tu": 0.2, "den": 0.28}, {"id": "ta_ld", "tu": 0.28, "den": 0.42},
                         {"id": "sao_luc_dau", "tu": 0.4, "den": 0.48}, {"id": "ta_bd1", "tu": 0.48, "den": 0.6}, {"id": "ta_bd2", "tu": 0.52, "den": 0.64},
                         {"id": "coc", "tu": 0.55, "den": 0.68}, {"id": "sao_bach_dang", "tu": 0.64, "den": 0.72}, {"id": "ta_tk", "tu": 0.74, "den": 0.86}, {"id": "sao_tay_ket", "tu": 0.84, "den": 0.92}]},
  "ket_qua": {"zoom": [1.03, 1.0], "hien": NEN + ["tong_thuy", "tong_bo", "tong_bo2", "tong_tk", "ta_dl", "ta_ld", "ta_bd1", "ta_bd2", "ta_tk", "coc"] + [f"sao_{k}" for k in SAO],
              "chu_giai": ["mui_ten_dich", "mui_ten_ta", "rut_chay"],
              "moc": [{"chu": "Quân Tống đại bại", "tu": 0.05, "den": 1.1}],
              "buoc": [{"id": "rut_bd", "tu": 0.1, "den": 0.45}, {"id": "rut_ld", "tu": 0.25, "den": 0.6}],
              "bang": {"chu": "Hầu Nhân Bảo tử trận", "tu": 0.65, "y": 0.70}}
 }
}
json.dump(S, open(f"{ROOT}/pipeline/maps/specs/chong-tong-981.json", "w"), ensure_ascii=False)
print("ok")
