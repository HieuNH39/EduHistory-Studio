"""Sa bàn (saban2) 'Dương Đình Nghệ chống quân Nam Hán (930 – 931)'.
Vẽ lại, giản lược theo Hình 4 'Lược đồ cuộc kháng chiến chống quân Nam Hán lần thứ nhất (930 – 931)',
SGK Lịch sử và Địa lí 6, Bài 18, tr. 82, kết hợp sơ đồ diễn biến 5 bước dưới lược đồ.
Nền bản đồ Natural Earth 1:50m (phạm vi công cộng), toạ độ theo make_vn_map.xy (kinh độ, vĩ độ); sông vẽ giản lược.
Như lược đồ SGK, có ô bản đồ nhỏ Việt Nam thể hiện quần đảo Hoàng Sa, Trường Sa.
Vị trí các châu, làng Giàng, Đại La đặt theo địa danh ngày nay mà SGK ghi trong ngoặc (Hà Nội, Hàm Rồng – Thanh Hoá...)."""
import json, math, sys
sys.path.insert(0, "/home/claude/eduhistory-studio/tools")
from make_vn_map import xy, nen, ROOT
P = lambda lon, lat: xy(lon, lat)

D = {"dai_la": (105.85, 21.03), "lang_giang": (105.79, 19.86), "phong_chau": (105.22, 21.32), "hong_chau": (106.55, 20.86),
     "truong_chau": (105.97, 20.25), "luc_chau": (107.10, 21.10), "ai_chau": (105.55, 19.62)}
Q = lambda k: P(*D[k])

# ---- ô bản đồ nhỏ Việt Nam (khoảng trống bên trái, dưới chú giải)
IX0, IY0, IX1, IY1 = -110, 232, 52, 382
LON0, LAT0, KY = 101.8, 24.0, 9.6
KX = KY * math.cos(math.radians(15))
def ip(lon, lat): return [round(IX0 + (lon - LON0) * KX, 1), round(IY0 + (LAT0 - lat) * KY, 1)]

def clip(poly, x0, y0, x1, y1):
    """Cắt đa giác theo hình chữ nhật (Sutherland – Hodgman)."""
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

SONG = [
 {"ten": "S. Hồng", "nhan": P(104.55, 22.08), "goc": 38, "rong": 3.2, "diem": [P(*p) for p in [(103.95, 22.52), (104.4, 22.15), (104.87, 21.72), (105.2, 21.45), (105.43, 21.28), (105.65, 21.15), (105.86, 21.03), (106.05, 20.82), (106.25, 20.55), (106.55, 20.25)]]},
 {"ten": "S. Đà", "nhan": P(104.05, 21.45), "goc": 32, "rong": 2.6, "diem": [P(*p) for p in [(102.95, 22.55), (103.3, 22.1), (103.9, 21.55), (104.6, 21.05), (105.1, 20.85), (105.33, 20.95), (105.42, 21.25)]]},
 {"ten": "S. Mã", "nhan": P(104.6, 20.42), "goc": 28, "rong": 2.6, "diem": [P(*p) for p in [(103.6, 21.3), (104.2, 20.85), (104.8, 20.45), (105.25, 20.15), (105.6, 19.95), (105.85, 19.82), (106.0, 19.76)]]},
]

def dd(k, ten, lech, **kw): return {"ten": ten, "vi_tri": Q(k), "kieu": "diem", "man_hinh": True, "lech": lech, **kw}
DIA_DANH = [
 {"ten": "", "vi_tri": Q("dai_la"), "kieu": "thanh"}, dd("dai_la", "ĐẠI LA", [-34, -26], dam=True, co=21), dd("lang_giang", "LÀNG GIÀNG", [22, 4], dam=True, co=20),
 dd("phong_chau", "Phong Châu", [-14, -18], co=16), dd("hong_chau", "Hồng Châu", [16, 14], co=16),
 dd("truong_chau", "Trường Châu", [16, 6], co=16), dd("luc_chau", "Lục Châu", [6, 26], co=16),
 {"ten": "Ái Châu", "vi_tri": Q("ai_chau"), "man_hinh": True, "lech": [-6, 22], "co": 16},
 {"ten": "GIAO CHÂU", "vi_tri": P(105.35, 21.95), "man_hinh": True, "lech": [0, 0], "lon": True, "co": 30},
 {"ten": "NAM HÁN", "vi_tri": P(107.0, 22.95), "man_hinh": True, "lech": [0, 0], "lon": True, "co": 28},
 {"ten": "VỊNH BẮC BỘ", "vi_tri": P(107.55, 20.05), "man_hinh": True, "lech": [0, 0], "dam": True, "co": 18},
] + dao_inset(112.0, 16.5, "QĐ. Hoàng Sa", 5, .5, (0, -11)) + dao_inset(114.0, 9.6, "QĐ. Trường Sa", 6, .8, (0, -14)) \
  + [{"ten": "VIỆT NAM", "vi_tri": ip(105.3, 15.2), "co": 8, "dam": True}, {"ten": "Biển Đông", "vi_tri": ip(113.6, 13.0), "co": 8}]

def vong(lon, lat, rx=.16, ry=.13):
    return [P(lon + rx * c, lat + ry * s) for c, s in [(1, 0), (.7, .7), (0, 1), (-.7, .7), (-1, 0), (-.7, -.7), (0, -1), (.7, -.7), (1, 0)]]

DT = {
 "tri_so": {"loai": "nhan", "vi_tri": P(106.3, 21.45), "chu": "Trị sở chính quyền đô hộ", "co": 13, "mau": "dich"},
 "tu_nghia": {"loai": "vong", "rong": 6, "diem": vong(*D["lang_giang"], rx=.2, ry=.16)},
 "tu_nghia_nhan": {"loai": "nhan", "vi_tri": P(106.55, 19.62), "chu": "Hào kiệt khắp nơi về tụ nghĩa", "co": 13, "mau": "ta"},
 "tien_dl": {"loai": "mui_ten_ta", "diem": [P(105.8, 20.02), P(105.98, 20.4), P(106.0, 20.72), P(105.9, 20.95)], "w0": 5, "w1": 9},
 "vay_dl": {"loai": "vong", "rong": 5, "diem": vong(*D["dai_la"], rx=.17, ry=.13)},
 "sao_dl": {"loai": "sao", "vi_tri": Q("dai_la")},
 "tiep_vien": {"loai": "mui_ten_dich", "diem": [P(108.15, 21.55), P(107.6, 21.33), P(107.0, 21.2), P(106.45, 21.12)], "w0": 4, "w1": 8},
 "chan": {"loai": "mui_ten_ta", "diem": [P(105.97, 21.08), P(106.12, 21.1), P(106.28, 21.12)], "w0": 5, "w1": 9},
 "chan_ky": {"loai": "chan_danh", "vi_tri": P(106.36, 21.12), "goc": 0},
 "rut": {"loai": "rut_chay", "diem": [P(106.5, 21.28), P(107.1, 21.5), P(107.7, 21.75), P(108.1, 21.9)], "w0": 3},
}
NEN = ["tri_so"]
PHA = {
 "nam_han": {"mo_dau": True, "zoom": [1.0, 1.04], "chu_giai": [], "hien": NEN,
             "moc": [{"chu": "Mùa thu năm 930", "tu": 0.06, "den": 1.1}],
             "bang": {"chu": "Nam Hán lập lại quyền cai trị", "tu": 0.4, "y": 0.72}},
 "tu_nghia": {"zoom": [1.04, 1.12], "tam": P(105.85, 20.3), "chu_giai": ["vong"], "hien": NEN,
              "moc": [{"chu": "Năm 931", "tu": 0.05, "den": 1.1}],
              "buoc": [{"id": "tu_nghia", "tu": 0.12, "den": 0.45}, {"id": "tu_nghia_nhan", "tu": 0.4, "den": 0.55}]},
 "dai_la": {"zoom": [1.1, 1.14], "tam": P(105.9, 20.6), "chu_giai": ["vong", "mui_ten_ta", "sao"], "hien": NEN + ["tu_nghia"],
            "buoc": [{"id": "tien_dl", "tu": 0.08, "den": 0.45}, {"id": "vay_dl", "tu": 0.45, "den": 0.7}, {"id": "sao_dl", "tu": 0.72, "den": 0.85}]},
 "tiep_vien": {"zoom": [1.12, 1.04], "tam": P(106.5, 20.9), "chu_giai": ["mui_ten_ta", "mui_ten_dich", "chan_danh", "rut_chay"],
               "hien": ["tu_nghia", "tien_dl", "vay_dl", "sao_dl"],
               "buoc": [{"id": "tiep_vien", "tu": 0.06, "den": 0.35}, {"id": "chan", "tu": 0.36, "den": 0.5}, {"id": "chan_ky", "tu": 0.46, "den": 0.56},
                        {"id": "rut", "tu": 0.58, "den": 0.8}]},
 "thang_loi": {"zoom": [1.04, 1.0], "chu_giai": [], "hien": ["tu_nghia", "tien_dl", "vay_dl", "sao_dl", "tiep_vien", "chan", "chan_ky", "rut"],
               "bang": {"chu": "Dương Đình Nghệ tự xưng Tiết độ sứ", "tu": 0.2, "y": 0.72}},
}

spec = {
 "phien_ban": 2,
 "ten": "Dương Đình Nghệ chống quân Nam Hán",
 "phu_de": "Năm 930 – 931",
 "nguon": "Vẽ lại, giản lược theo Hình 4, SGK Lịch sử và Địa lí 6, Bài 18, tr. 82; nền bản đồ Natural Earth",
 "khung": P(102.6, 23.45) + P(108.6, 19.25),
 "nen_bien": [0.80, 0.88, 0.93],
 "chu_giai_xy": [0.015, 0.24],
 "sao_man_hinh": True,
 "vung_mau": nen([101.5, 18.5, 109.5, 24.5]) + inset(),
 "song": SONG,
 "dia_danh": DIA_DANH,
 "chu_giai": [
  {"loai": "vong", "nhan": "Nơi tập hợp lực lượng / vây thành"},
  {"loai": "mui_ten_ta", "nhan": "Đường tiến của quân ta"},
  {"loai": "sao", "nhan": "Chiếm thành Đại La"},
  {"loai": "mui_ten_dich", "nhan": "Quân Nam Hán tiếp viện"},
  {"loai": "chan_danh", "nhan": "Chặn đánh quân tiếp viện"},
  {"loai": "rut_chay", "nhan": "Quân Nam Hán rút chạy"},
 ],
 "doi_tuong": DT,
 "pha": PHA,
}

if __name__ == "__main__":
    out = f"{ROOT}/pipeline/maps/specs/duong-dinh-nghe-931.json"
    json.dump(spec, open(out, "w"), ensure_ascii=False)
    print("đã ghi", out, len(spec["vung_mau"]), "vùng")
