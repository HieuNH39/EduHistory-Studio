"""Sinh tệp sa bàn (saban2) cho bản đồ Việt Nam từ dữ liệu Natural Earth 1:50m (phạm vi công cộng).
Toạ độ: x = (kinh độ − 102) × 100 × cos 15°, y = (23.5 − vĩ độ) × 100. Luôn vẽ quần đảo Hoàng Sa, Trường Sa của Việt Nam."""
import json, math, sys
ROOT = "/home/claude/eduhistory-studio"
K = 100 * math.cos(math.radians(15))
def xy(lon, lat): return [round((lon - 102) * K, 1), round((23.5 - lat) * 100, 1)]
VN_MAU = [0.96, 0.89, 0.72]; LANG_GIENG = [0.88, 0.87, 0.83]
def nen(bbox):
    g = json.load(open(f"{ROOT}/assets/geo/ne_50m_dong_nam_a.geojson")); out = []
    for f in g["features"]:
        geo = f["geometry"]; polys = geo["coordinates"] if geo["type"] == "MultiPolygon" else [geo["coordinates"]]
        for poly in polys:
            ring = poly[0]; xs = [c[0] for c in ring]; ys = [c[1] for c in ring]
            if max(xs) < bbox[0] or min(xs) > bbox[2] or max(ys) < bbox[1] or min(ys) > bbox[3]: continue
            out.append({"diem": [xy(*c) for c in ring], "mau": VN_MAU if f["properties"]["ADMIN"] == "Vietnam" else LANG_GIENG})
    return out
def dao(lon, lat, ten, n=7, r=0.35):
    import random; random.seed(int(lon * 100 + lat))
    pts = [[lon + random.uniform(-r, r), lat + random.uniform(-r, r)] for _ in range(n)]
    return [{"ten": "", "vi_tri": xy(*p), "kieu": "diem"} for p in pts] + [{"ten": ten, "vi_tri": xy(lon, lat + r + .35), "dam": True}]
