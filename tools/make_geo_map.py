"""Sinh nền bản đồ khu vực (đất liền Natural Earth 1:110m, không vẽ biên giới) cho sa bàn saban2.
Phép chiếu trụ đều có hệ số cos(vĩ độ giữa): x = (lon − lon0)·100·cos(φ0), y = (lat_max − lat)·100."""
import json, math
ROOT = "/home/claude/eduhistory-studio"
class Geo:
    def __init__(self, lon0, lat_max, phi0):
        self.lon0, self.lat_max, self.k = lon0, lat_max, 100 * math.cos(math.radians(phi0))
    def P(self, lon, lat): return [round((lon - self.lon0) * self.k, 1), round((self.lat_max - lat) * 100, 1)]
    def dat(self, bbox, mau=(0.93, 0.89, 0.78), bien=(0.80, 0.88, 0.93)):
        """Đất liền + các vùng nước nội địa (lỗ trong đa giác như biển Ca-xpi, và hồ lớn) tô màu biển."""
        out, nuoc = [], []
        def trong(ring):
            xs = [c[0] for c in ring]; ys = [c[1] for c in ring]
            return not (max(xs) < bbox[0] or min(xs) > bbox[2] or max(ys) < bbox[1] or min(ys) > bbox[3])
        for ten in ("ne_110m_land", "ne_110m_lakes"):
            g = json.load(open(f"{ROOT}/assets/geo/{ten}.geojson"))
            for f in g["features"]:
                geo = f["geometry"]; polys = geo["coordinates"] if geo["type"] == "MultiPolygon" else [geo["coordinates"]]
                for poly in polys:
                    for i, ring in enumerate(poly):
                        if not trong(ring): continue
                        la_nuoc = ten.endswith("lakes") or i > 0
                        (nuoc if la_nuoc else out).append({"diem": [self.P(*c) for c in ring], "mau": list(bien if la_nuoc else mau)})
        return out + nuoc
