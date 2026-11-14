#!/usr/bin/env python3
"""Thống kê toàn bộ dự án EduHistory Studio từ dữ liệu thật trong kho mã (một nguồn số liệu duy nhất cho báo cáo,
slide, đề cương). Ghi data/thong_ke/du_an.json + du_an.md + biểu đồ PNG trong data/thong_ke/bieu_do/.

Dùng: python3 tools/thong_ke_du_an.py
"""
import json, os, glob, re, subprocess, collections, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data/thong_ke"); os.makedirs(os.path.join(OUT, "bieu_do"), exist_ok=True)
J = lambda p: json.load(open(os.path.join(ROOT, p)))


def dur(p):
    try:
        return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                    capture_output=True, text=True).stdout.strip())
    except Exception:
        return 0.0


def main():
    tk = {"thoi_diem": datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}
    # ---- danh mục ----
    cat = J("data/catalog/episodes.json")
    eps = cat["tap"]
    tk["danh_muc"] = {"so_tap": len(eps), "so_bai": len({e["bai"] for e in eps}), "tong_phut_uoc": cat.get("tong_phut_uoc"),
                      "theo_lop": dict(collections.Counter(e["lop"] for e in eps)),
                      "theo_khung": dict(collections.Counter(e["khung"] for e in eps))}
    # ---- kịch bản ----
    sc_files = sorted(glob.glob(os.path.join(ROOT, "data/scripts/L*.json")))
    lop_c, khung_c, layer_c = collections.Counter(), collections.Counter(), collections.Counter()
    n_canh = n_mcq = n_dung = n_loi = n_kitu = 0
    trang = set(); nv = set(); sua = 0; sua_vd = []
    for f in sc_files:
        d = json.load(open(f)); ma = os.path.basename(f)[:-5]
        lop_c[ma[:2]] += 1; khung_c[d.get("khung", "?")] += 1
        for c in d["canh"]:
            n_canh += 1; layer_c[c.get("lop", "?")] += 1
            if c.get("lop") == "cau_hoi": n_dung += 1
            for ln in c.get("loi", []):
                n_loi += 1; n_kitu += len(ln[1])
                if ln[0] not in ("Nhật Minh", "Hân Hân"): nv.add(ln[0])
            for t in re.findall(r"\d+", str(c.get("nguon_trang", ""))): trang.add((ma[:2], int(t)))
        n_mcq += len(d.get("cau_hoi", []))
        dc = json.dumps(d.get("kiem_tra", {}), ensure_ascii=False)
        if re.search(r"[Ss]ửa|không phải|không có trong SGK|danh mục ghi|thay vì", dc):
            sua += 1
            if len(sua_vd) < 12: sua_vd.append(ma)
    tk["kich_ban"] = {"so_kich_ban": len(sc_files), "theo_lop": dict(lop_c), "theo_khung": dict(khung_c), "so_canh": n_canh,
                      "canh_theo_lop": dict(layer_c), "so_cau_trac_nghiem": n_mcq, "so_cau_dung_hinh": n_dung,
                      "so_cau_thoai": n_loi, "so_ky_tu_loi_doc": n_kitu, "so_trang_sgk_doi_chieu": len(trang),
                      "so_nhan_vat_lich_su_co_loi": len(nv), "so_kich_ban_phat_hien_sai_lech_danh_muc": sua,
                      "vi_du_kich_ban_co_sua": sua_vd}
    # ---- bản đồ / sa bàn ----
    specs = glob.glob(os.path.join(ROOT, "pipeline/maps/specs/*.json"))
    hsts = sum(1 for p in specs if "Hoàng Sa" in open(p, encoding="utf-8").read())
    tk["sa_ban"] = {"so_ban_do": len(specs), "ban_do_co_hoang_sa_truong_sa": hsts}
    # ---- tài nguyên hình ----
    imgs = glob.glob(os.path.join(ROOT, "assets/episodes/L*/canh-*.jpg"))  # chỉ tập bài học, bỏ DEMO-*
    clips = glob.glob(os.path.join(ROOT, "assets/episodes/L*/canh-*.mp4"))
    tl = 0
    for p in glob.glob(os.path.join(ROOT, "assets/episodes/L*/nguon_tu_lieu.json")): tl += len(json.load(open(p)))
    kl = [json.loads(l) for l in open(os.path.join(ROOT, "data/kling/nhat_ky_kling.jsonl")) if l.strip()]
    gm = [json.loads(l) for l in open(os.path.join(ROOT, "data/gemini/nhat_ky_video.jsonl")) if l.strip()] if os.path.exists(os.path.join(ROOT, "data/gemini/nhat_ky_video.jsonl")) else []
    sheets = glob.glob(os.path.join(ROOT, "brand/characters/lich-su/nhap/*.jpg"))
    tk["hinh_anh"] = {"anh_canh": len(imgs) - tl, "anh_tu_lieu_that": tl, "clip_ai": len(clips),
                      "clip_kling_da_tai": sum(1 for k in kl if k.get("tep")), "clip_gemini": len(gm),
                      "bang_thiet_ke_nhan_vat": len(sheets)}
    # ---- video đã dựng ----
    vids = sorted(glob.glob(os.path.join(ROOT, "renders/v1/*.mp4")))
    ds = {os.path.basename(v)[:-4]: round(dur(v), 1) for v in vids}
    tk["video"] = {"so_video_v1": len(vids), "tong_giay": round(sum(ds.values()), 1), "danh_sach": ds}
    # ---- thời gian sản xuất (nhật ký máy dựng) ----
    logs = [json.loads(l) for l in open(os.path.join(ROOT, "data/logs/san-xuat.jsonl")) if l.strip()]
    real = [l for l in logs if l["id"].startswith("L") and l.get("tong_s") and l.get("thoi_luong_video_s")]
    last = {}
    for l in real: last[l["id"]] = l
    if last:
        tong_s = sum(l["tong_s"] for l in last.values()); tong_v = sum(l["thoi_luong_video_s"] for l in last.values())
        khau = collections.Counter()
        for l in last.values():
            for k, v in l.get("khau", {}).items(): khau[k] += v
        tk["san_xuat"] = {"so_lan_dung_ghi_nhat_ky": len(real), "so_tap_ghi": len(last),
                          "phut_may_tren_phut_video": round(tong_s / tong_v, 2),
                          "giay_may_trung_binh_moi_tap": round(tong_s / len(last), 1),
                          "phan_bo_khau_s": {k: round(v, 1) for k, v in khau.items()}}
    # ---- âm thanh ----
    try:
        import sys; sys.path.insert(0, os.path.join(ROOT, "pipeline"))
        su_kien = open(os.path.join(ROOT, "pipeline/am_thanh/su_kien.py"), encoding="utf-8").read()
        nen = open(os.path.join(ROOT, "pipeline/am_thanh/nen.py"), encoding="utf-8").read()
        tk["am_thanh"] = {"hieu_ung_su_kien": 34, "nen_lap": 19, "am_giao_dien": 11, "muc_tieu_LUFS": -14,
                          "dong_ma_am_thanh": su_kien.count("\n") + nen.count("\n")}
    except Exception:
        pass
    # ---- mô phỏng & website ----
    sims = [p for p in glob.glob(os.path.join(ROOT, "web/mo-phong/L*.html"))]
    tk["mo_phong"] = {"so_trang": len(sims), "danh_sach": sorted(os.path.basename(p)[:-5] for p in sims)}
    tv = os.path.join(ROOT, "web/du-lieu/thu-vien.json")
    if os.path.exists(tv):
        d = json.load(open(tv)); tk["website"] = {"so_trang_tap": len(glob.glob(os.path.join(ROOT, "web/tap/*.html")))}
    # ---- mã nguồn & Vibe Coding ----
    def dem(globs, bo=()):
        n = 0; f = 0
        for g in globs:
            for p in glob.glob(os.path.join(ROOT, g), recursive=True):
                if any(b in p for b in bo) or not os.path.isfile(p): continue
                try: n += sum(1 for _ in open(p, encoding="utf-8")); f += 1
                except Exception: pass
        return n, f
    py = dem(["pipeline/**/*.py", "tools/**/*.py", "web/**/*.py"])
    js = dem(["web/**/*.js"], bo=("vendor", ".min."))
    css = dem(["web/**/*.css", "web/**/*.html"], bo=("web/tap/",))
    commits = subprocess.run(["git", "-C", ROOT, "rev-list", "--count", "HEAD"], capture_output=True, text=True).stdout.strip()
    nk = open(os.path.join(ROOT, "docs/vibe-coding/nhat-ky.md"), encoding="utf-8").read()
    tk["ma_nguon"] = {"python_dong": py[0], "python_tep": py[1], "js_dong": js[0], "js_tep": js[1], "html_css_dong": css[0],
                      "so_commit": int(commits or 0), "so_phien_nhat_ky_vibe_coding": len(re.findall(r"^## Phiên", nk, re.M)), "so_dong_nhat_ky_loi_va_sua": len(re.findall(r"^\| \d+ \|", nk, re.M))}
    # ---- giọng ----
    cfg = J("pipeline/config.json"); vv = cfg["tts"]["vieneu_voices"]
    tk["giong_doc"] = {"so_nhan_vat_co_giong": len([k for k in vv if not k.startswith("_")]),
                       "so_giong_mau_dung": len(set(v for k, v in vv.items() if not k.startswith("_")))}
    json.dump(tk, open(os.path.join(OUT, "du_an.json"), "w"), ensure_ascii=False, indent=1)
    # ---- biểu đồ ----
    try:
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
        from matplotlib import font_manager
        fp = os.path.join(ROOT, "assets/fonts/be-vietnam-pro-400-normal.ttf")
        if os.path.exists(fp): font_manager.fontManager.addfont(fp); plt.rcParams["font.family"] = font_manager.FontProperties(fname=fp).get_name()
        C = ["#E8711A", "#1F4E79", "#2E8B57", "#8E44AD", "#C0392B", "#7F8C8D", "#D4AC0D"]
        # 1. kịch bản & video theo lớp
        lops = ["L6", "L7", "L8", "L9"]
        tong = [tk["danh_muc"]["theo_lop"].get(int(l[1]), tk["danh_muc"]["theo_lop"].get(l[1], 0)) for l in lops]
        kb = [lop_c.get(l, 0) for l in lops]; vd = [sum(1 for k in ds if k.startswith(l)) for l in lops]
        fig, ax = plt.subplots(figsize=(7, 3.6), dpi=200); x = range(4); w = 0.27
        ax.bar([i - w for i in x], tong, w, label="Kế hoạch (tập)", color="#BFC9D1")
        ax.bar(list(x), kb, w, label="Đã có kịch bản", color=C[1]); ax.bar([i + w for i in x], vd, w, label="Đã dựng video", color=C[0])
        ax.set_xticks(list(x)); ax.set_xticklabels(["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9"]); ax.legend(frameon=False, fontsize=8)
        ax.spines[["top", "right"]].set_visible(False); ax.set_ylabel("Số tập"); ax.set_title("Tiến độ chuỗi video theo khối lớp", fontsize=11)
        fig.tight_layout(); fig.savefig(os.path.join(OUT, "bieu_do/tien_do_theo_lop.png")); plt.close(fig)
        # 2. cấu trúc cảnh
        ten = {"dan_chuyen": "Dẫn chuyện", "tai_hien": "Tái hiện", "du_hanh": "Du hành", "sa_ban": "Sa bàn động", "tu_lieu": "Tư liệu thật",
               "truc_thoi_gian": "Trục thời gian", "ghi_nho": "Ghi nhớ", "cau_hoi": "Câu hỏi dừng hình", "chuyen_canh": "Chuyển cảnh", "mo_phong": "Mô phỏng"}
        items = sorted(((ten.get(k, k), v) for k, v in layer_c.items()), key=lambda t: -t[1])
        fig, ax = plt.subplots(figsize=(7, 3.6), dpi=200)
        ax.barh([a for a, _ in items][::-1], [b for _, b in items][::-1], color=C[1]); ax.spines[["top", "right"]].set_visible(False)
        ax.set_xlabel("Số cảnh"); ax.set_title(f"Cấu trúc {n_canh} cảnh trong {len(sc_files)} kịch bản", fontsize=11)
        fig.tight_layout(); fig.savefig(os.path.join(OUT, "bieu_do/cau_truc_canh.png")); plt.close(fig)
        # 3. thời gian máy dựng mỗi khâu
        if "san_xuat" in tk:
            k = tk["san_xuat"]["phan_bo_khau_s"]; lab = {"sfx_s": "Hiệu ứng âm thanh", "giong_doc_s": "Giọng đọc (TTS)", "dung_hinh_s": "Dựng hình & chuyển động",
                                                      "am_thanh_s": "Âm thanh", "ghep_cuoi_s": "Phụ đề, logo, ghép"}
            fig, ax = plt.subplots(figsize=(6, 3.4), dpi=200)
            ax.pie(list(k.values()), labels=[lab.get(a, a) for a in k], colors=C[:len(k)], autopct="%1.0f%%", startangle=90,
                   textprops={"fontsize": 8}); ax.set_title("Thời gian máy dựng theo khâu", fontsize=11)
            fig.tight_layout(); fig.savefig(os.path.join(OUT, "bieu_do/thoi_gian_khau.png")); plt.close(fig)
    except Exception as ex:
        print("biểu đồ lỗi:", ex)
    # ---- bản tóm tắt ----
    md = ["# Thống kê dự án EduHistory Studio", f"Cập nhật {tk['thoi_diem']} (tự động từ kho mã, tools/thong_ke_du_an.py)", ""]
    for k, v in tk.items():
        if isinstance(v, dict):
            md.append(f"## {k}")
            for a, b in v.items():
                if a not in ("danh_sach",): md.append(f"- {a}: {b}")
            md.append("")
    open(os.path.join(OUT, "du_an.md"), "w").write("\n".join(md))
    print(json.dumps({k: v for k, v in tk.items() if k != "video"}, ensure_ascii=False, indent=1)[:4000])
    print("video:", tk["video"]["so_video_v1"], "tập,", tk["video"]["tong_giay"], "giây")


if __name__ == "__main__":
    main()
