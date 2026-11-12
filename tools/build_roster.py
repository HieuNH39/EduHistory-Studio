"""Gộp danh sách nhân vật (characters_raw) thành bảng nhân vật dùng chung data/catalog/nhan-vat.json
và gắn nhân vật vào từng tập trong episodes.json.
Quy tắc nguồn hình (quyết định GVHD 13/11/2026):
- anh_tu_lieu: người có ảnh chụp/phim thật (thời hiện đại, hoặc thế kỉ XIX có ảnh chụp) → dùng ảnh thật, không vẽ AI.
- ve_theo_tham_chieu: nhân vật trước thời có ảnh chụp → thiết kế hoạt hình dựa trên tượng, tranh thờ, tranh lịch sử, hiện vật trang phục.
- nhom: nhóm người (nghĩa quân, quân đội, nông dân…) → thiết kế nhóm theo trang phục thời kì (vẽ), thời hiện đại thì vẽ chung hoặc ảnh tư liệu."""
import json, glob, unicodedata, re
ROOT = "/home/claude/eduhistory-studio"
def slug(s):
    s = unicodedata.normalize('NFD', s.lower()).replace('đ', 'd')
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')
ALIAS = {  # tên phụ → mã chuẩn
 "quang-trung": "nguyen-hue", "nguyen-hue-quang-trung": "nguyen-hue",
 "chu-tich-ho-chi-minh": "ho-chi-minh", "nguyen-ai-quoc": "ho-chi-minh", "nguyen-tat-thanh": "ho-chi-minh",
 "v-i-le-nin": "le-nin", "vua-gia-long": "nguyen-anh", "gia-long": "nguyen-anh", "vua-minh-mang": "minh-mang",
 "tran-canh": "tran-thai-tong", "hung-vuong": "vua-hung", "vua-ly-thai-tong": "ly-thai-tong", "vua-tu-duc": "tu-duc",
 "vua-ham-nghi": "ham-nghi", "tran-quoc-tuan": "tran-hung-dao", "c-mac": "mac", "ph-ang-ghen": "ang-ghen",
 "nhat-hoang": "hi-ro-hi-to", "thien-hoang-hi-ro-hi-to": "hi-ro-hi-to", "vua-ly-nhan-tong": "ly-nhan-tong", "vua-ly-anh-tong": "ly-anh-tong",
}
DROP = {"nhat-minh", "han-han", "vua", "nha-su", "nha-khoa-hoc", "nha-lanh-dao-my", "nha-lanh-dao-lien-xo", "nha-khoa-hoc-khi-tuong",
        "ky-su-nong-nghiep", "vua-tran", "thai-thuong-hoang", "vua-thoi-tien-le", "nguoi-xec-bi", "vua-le", "chua-trinh"}
TEN = {"nguyen-hue": "Nguyễn Huệ (Quang Trung)", "ho-chi-minh": "Hồ Chí Minh (Nguyễn Tất Thành, Nguyễn Ái Quốc)", "le-nin": "V. I. Lê-nin",
       "nguyen-anh": "Nguyễn Ánh (Gia Long)", "tran-hung-dao": "Trần Quốc Tuấn (Trần Hưng Đạo)", "vua-hung": "Vua Hùng (Hùng Vương)",
       "mac": "C. Mác", "ang-ghen": "Ph. Ăng-ghen", "tran-thai-tong": "Trần Thái Tông (Trần Cảnh)", "minh-mang": "Minh Mạng", "tu-duc": "Tự Đức", "ham-nghi": "Hàm Nghi"}
# người thế kỉ XIX có ảnh chụp thật → dùng ảnh tư liệu
CO_ANH = {"mac", "ang-ghen", "na-po-le-ong-iii", "nu-hoang-anh-vich-to-ri-a", "s-dac-uyn", "lep-ton-xtoi", "vich-to-huy-go", "p-i-trai-cop-xki",
          "ph-so-panh", "h-ban-dac", "ham-nghi", "phan-dinh-phung", "ton-that-thuyet", "hoang-hoa-tham", "ho-xe-ri-dan", "bo-ni-pha-xi-o",
          "ph-gac-ni-e", "h-ri-vi-e", "nguyen-truong-to", "tu-duc"}
# nhân vật bổ sung khi viết kịch bản chi tiết (data/scripts/*.json → nhan_vat_lich_su)
BO_SUNG = {
 "le-chieu-thong": {"ten": "Lê Chiêu Thống", "loai": "ca_nhan", "thoi_ky": "can_dai", "quoc_gia": "Việt Nam",
                    "vai_tro": "Vua cuối cùng nhà Lê, cầu cứu nhà Thanh (1788)", "the_ki": "XVIII"},
 "hoa-mau": {"ten": "Hoà Mâu", "loai": "ca_nhan", "thoi_ky": "trung_dai", "quoc_gia": "Tống",
             "vai_tro": "Chỉ huy quân thuỷ Tống năm 1077", "the_ki": "XI"},
 "quan-ngo-quyen": {"ten": "Quân của Ngô Quyền", "loai": "nhom", "thoi_ky": "trung_dai", "quoc_gia": "Việt Nam",
                    "vai_tro": "Quân dân đánh trận Bạch Đằng năm 938", "the_ki": "X"},
 "quan-doi-nha-tran": {"ten": "Quân đội nhà Trần", "loai": "nhom", "thoi_ky": "trung_dai", "quoc_gia": "Đại Việt",
                       "vai_tro": "Quân dân nhà Trần trong ba lần kháng chiến chống Mông – Nguyên", "the_ki": "XIII"},
}
def main():
    cu = {}
    try:
        cu = {a["id"]: a for a in json.load(open(f"{ROOT}/data/catalog/nhan-vat.json"))["nhan_vat"]}
    except Exception: pass
    agg = {}
    for f in sorted(glob.glob(f"{ROOT}/data/catalog/characters_raw/*.json")):
        for t in json.load(open(f)).get("tap", []):
            for nv in t.get("nhan_vat", []):
                k = slug(re.sub(r"\s*\(.*?\)", "", nv["ten"])); k = ALIAS.get(k, k)
                if k in DROP or not k: continue
                a = agg.setdefault(k, {"id": k, "ten": TEN.get(k, nv["ten"]), "loai": nv.get("loai"), "thoi_ky": nv.get("thoi_ky"),
                                       "quoc_gia": nv.get("quoc_gia"), "vai_tro": nv.get("vai_tro"), "the_ki": nv.get("the_ki"), "tap": []})
                if t["ma"] not in a["tap"]: a["tap"].append(t["ma"])
    for f in sorted(glob.glob(f"{ROOT}/data/scripts/*.json")):
        sc = json.load(open(f))
        for k in sc.get("nhan_vat_lich_su", []):
            if k not in agg and k in BO_SUNG: agg[k] = {"id": k, **BO_SUNG[k], "tap": []}
            if k in agg and sc["ma"] not in agg[k]["tap"]: agg[k]["tap"].append(sc["ma"])
    for k, a in agg.items():
        if a["loai"] == "nhom": a["nguon_hinh"] = "nhom_ve" if a["thoi_ky"] != "hien_dai" else "nhom_tu_lieu_hoac_ve"
        elif a["thoi_ky"] == "hien_dai" or k in CO_ANH: a["nguon_hinh"] = "anh_tu_lieu"
        else: a["nguon_hinh"] = "ve_theo_tham_chieu"
        a["thiet_ke"] = cu.get(k, {}).get("thiet_ke", "chua")  # chua | nhap | duyet (giữ trạng thái cũ)
        if cu.get(k, {}).get("ban_thiet_ke"): a["ban_thiet_ke"] = cu[k]["ban_thiet_ke"]
    json.dump({"ghi_chu": __doc__, "nhan_vat": sorted(agg.values(), key=lambda a: (-len(a["tap"]), a["ten"]))},
              open(f"{ROOT}/data/catalog/nhan-vat.json", "w"), ensure_ascii=False, indent=1)
    # gắn vào tập
    E = json.load(open(f"{ROOT}/data/catalog/episodes.json"))
    by = {}
    for a in agg.values():
        for m in a["tap"]: by.setdefault(m, []).append(a)
    for e in E["tap"]:
        e["nhan_vat"] = [{"id": a["id"], "ten": a["ten"], "nguon_hinh": a["nguon_hinh"]} for a in by.get(e["ma"], [])]
    json.dump(E, open(f"{ROOT}/data/catalog/episodes.json", "w"), ensure_ascii=False, indent=1)
    from collections import Counter
    print(len(agg), Counter(a["nguon_hinh"] for a in agg.values()))
    print("tập không có nhân vật:", sum(1 for e in E["tap"] if not e["nhan_vat"]))
if __name__ == "__main__": main()
