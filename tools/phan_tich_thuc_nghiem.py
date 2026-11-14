"""Phân tích số liệu thực nghiệm sư phạm EduHistory Studio (Lịch sử 7, Bài 14).

Đầu vào: các tệp CSV tải từ bảng tính "EduHistory Studio – Nhập và phân tích số liệu thực nghiệm"
(trang Tiền KT, Hậu KT, Duy trì, Hứng thú, SUS – mỗi trang tải về một tệp CSV, giữ nguyên dòng tiêu đề).
Bảng tính đã tự tính; script này tính lại độc lập bằng SciPy để đối chiếu, và vẽ biểu đồ cho báo cáo.

Cách dùng:
    python3 tools/phan_tich_thuc_nghiem.py <thư mục chứa CSV> [thư mục kết quả]
Tên tệp nhận theo chữ có trong tên: "tien", "hau", "duy", "hung", "sus" (không phân biệt hoa thường, có/không dấu).

Kết quả: ket_qua.json, ket_qua.md (bảng số liệu + kết luận từng giả thuyết), bieu_do_*.png.
Không có số liệu thì không in kết luận – script không bao giờ tự tạo số liệu.
"""
import json, os, sys, unicodedata, glob
import numpy as np
import pandas as pd
from scipy import stats

TN, DC = "Thực nghiệm", "Đối chứng"


def _khong_dau(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower().replace("đ", "d")


def doc_csv(thu_muc):
    tep = {}
    for p in glob.glob(os.path.join(thu_muc, "*.csv")):
        ten = _khong_dau(os.path.basename(p))
        for k in ("tien", "hau", "duy", "hung", "sus"):
            if k in ten and k not in tep:
                tep[k] = pd.read_csv(p, dtype=str).fillna("")
    return tep


def _so(x):
    try:
        return float(str(x).replace(",", "."))
    except ValueError:
        return np.nan


def bang_diem(df):
    """Trả về bảng Mã số, Nhóm, Điểm từ trang kiểm tra (cột 1, 2, 3 của bảng tính)."""
    if df is None or df.empty:
        return pd.DataFrame(columns=["ma", "nhom", "diem"])
    d = pd.DataFrame({"ma": df.iloc[:, 0].str.strip(), "nhom": df.iloc[:, 1].str.strip(), "diem": df.iloc[:, 2].map(_so)})
    return d[(d.ma != "") & d.diem.notna()]


def hung_thu(df):
    """Điểm hứng thú: 12 câu Likert (cột 8–19), đảo câu 3 và 8; trả về bảng + ma trận câu để tính alpha."""
    if df is None or df.empty:
        return pd.DataFrame(columns=["ma", "nhom", "lan", "diem"]), np.empty((0, 12))
    cau = df.iloc[:, 7:19].apply(lambda c: c.map(_so)).to_numpy()
    du = ~np.isnan(cau).any(axis=1)
    cau = cau[du].copy()
    cau[:, [2, 7]] = 6 - cau[:, [2, 7]]
    d = pd.DataFrame({"ma": df.iloc[:, 0].str.strip()[du].values, "nhom": df.iloc[:, 1].str.strip()[du].values,
                      "lan": df.iloc[:, 2].str.strip()[du].values, "diem": cau.mean(axis=1)})
    return d, cau


def sus(df):
    if df is None or df.empty:
        return pd.DataFrame(columns=["ma", "sus"])
    x = df.iloc[:, 2:12].apply(lambda c: c.map(_so)).to_numpy()
    du = ~np.isnan(x).any(axis=1)
    x = x[du]
    diem = 2.5 * ((x[:, 0::2] - 1).sum(axis=1) + (5 - x[:, 1::2]).sum(axis=1))
    return pd.DataFrame({"ma": df.iloc[:, 0].str.strip()[du].values, "sus": diem})


def cronbach(m):
    if m.shape[0] < 3:
        return None
    k = m.shape[1]
    return float(k / (k - 1) * (1 - m.var(axis=0, ddof=1).sum() / m.sum(axis=1).var(ddof=1)))


def cohen_d(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 2 or len(b) < 2:
        return None
    sp = np.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1)) / (len(a) + len(b) - 2))
    return float((a.mean() - b.mean()) / sp) if sp > 0 else None


def mo_ta(x):
    x = np.asarray(x, float)
    return {"n": int(len(x)), "tb": float(x.mean()) if len(x) else None, "dlc": float(x.std(ddof=1)) if len(x) > 1 else None}


def welch(a, b):
    if len(a) < 2 or len(b) < 2:
        return None
    r = stats.ttest_ind(a, b, equal_var=False)
    return {"t": float(r.statistic), "p": float(r.pvalue)}


def ghep_cap(a, b):
    if len(a) < 2:
        return None
    r = stats.ttest_rel(a, b)
    return {"t": float(r.statistic), "p": float(r.pvalue)}


def phan_tich(tep):
    tien, hau, duy = bang_diem(tep.get("tien")), bang_diem(tep.get("hau")), bang_diem(tep.get("duy"))
    g = tien.merge(hau[["ma", "diem"]], on="ma", how="left", suffixes=("_tien", "_hau")) \
            .merge(duy[["ma", "diem"]].rename(columns={"diem": "diem_duy"}), on="ma", how="left")
    g["tien_bo"] = g.diem_hau - g.diem_tien
    g["giam"] = g.diem_hau - g.diem_duy
    ht, cau = hung_thu(tep.get("hung"))
    if not ht.empty:
        for lan, cot in (("Trước", "ht1"), ("Sau", "ht2")):
            g = g.merge(ht[ht.lan == lan][["ma", "diem"]].rename(columns={"diem": cot}), on="ma", how="left")
    else:
        g["ht1"] = np.nan; g["ht2"] = np.nan
    g = g.merge(sus(tep.get("sus")), on="ma", how="left")
    kq = {"so_hs": {TN: int((g.nhom == TN).sum()), DC: int((g.nhom == DC).sum())}}
    def nhom(cot, ten):
        return g[(g.nhom == ten) & g[cot].notna()][cot].to_numpy()
    for cot in ("diem_tien", "diem_hau", "tien_bo", "diem_duy", "giam", "ht1", "ht2", "sus"):
        kq[cot] = {TN: mo_ta(nhom(cot, TN)), DC: mo_ta(nhom(cot, DC))}
    kq["kiem_dinh"] = {
        "tuong_duong_tien_kt": welch(nhom("diem_tien", TN), nhom("diem_tien", DC)),
        "H1_tien_bo": welch(nhom("tien_bo", TN), nhom("tien_bo", DC)),
        "H1_cohen_d": cohen_d(nhom("tien_bo", TN), nhom("tien_bo", DC)),
        "H2_giam_sau_7_ngay": welch(nhom("giam", TN), nhom("giam", DC)),
        "H3_hung_thu_lan_2": welch(nhom("ht2", TN), nhom("ht2", DC)),
        "alpha_hung_thu": cronbach(cau),
    }
    for ten, key in ((TN, "ghep_cap_TN"), (DC, "ghep_cap_DC")):
        s = g[(g.nhom == ten) & g.tien_bo.notna()]
        kq["kiem_dinh"][key] = ghep_cap(s.diem_tien.to_numpy(), s.diem_hau.to_numpy())
    tb_tn, tb_dc = kq["diem_hau"][TN]["tb"], kq["diem_hau"][DC]["tb"]
    kq["kiem_dinh"]["H1_hau_kt_cao_hon_pct"] = (tb_tn / tb_dc - 1) * 100 if tb_tn and tb_dc else None
    kq["kiem_dinh"]["H4_sus_tb"] = kq["sus"][TN]["tb"]
    return g, kq


def bieu_do(g, kq, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fp = os.path.join(root, "assets/fonts/be-vietnam-pro-400-normal.ttf")
    if os.path.exists(fp):
        font_manager.fontManager.addfont(fp); plt.rcParams["font.family"] = "Be Vietnam Pro"
    mau = {TN: "#F26B1D", DC: "#1F4E79"}
    # Điểm trung bình tiền – hậu – duy trì, có thanh sai số (độ lệch chuẩn)
    fig, ax = plt.subplots(figsize=(7, 4), dpi=200)
    x = np.arange(3)
    for k, ten in enumerate((TN, DC)):
        tb = [kq[c][ten]["tb"] or 0 for c in ("diem_tien", "diem_hau", "diem_duy")]
        sd = [kq[c][ten]["dlc"] or 0 for c in ("diem_tien", "diem_hau", "diem_duy")]
        ax.bar(x + (k - .5) * .38, tb, .38, yerr=sd, capsize=4, color=mau[ten], label=f"{ten} (n = {kq['so_hs'][ten]})")
    ax.set_xticks(x, ["Tiền kiểm tra", "Hậu kiểm tra", "Sau 7 ngày"]); ax.set_ylim(0, 10); ax.set_ylabel("Điểm (thang 10)")
    ax.legend(frameon=False); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(os.path.join(out, "bieu_do_diem.png")); plt.close(fig)


def bao_cao_md(kq):
    def f(v, nd=2):
        return "–" if v is None else f"{v:.{nd}f}".replace(".", ",")
    kd = kq["kiem_dinh"]
    p = lambda r: "–" if not r else f"t = {f(r['t'])}; p = {f(r['p'], 3)}"
    dong = ["# Kết quả thực nghiệm (tính lại bằng SciPy)", "",
            f"Số HS: thực nghiệm {kq['so_hs'][TN]}, đối chứng {kq['so_hs'][DC]}.", "",
            "| Chỉ số | Thực nghiệm (TB ± ĐLC) | Đối chứng (TB ± ĐLC) |", "| --- | --- | --- |"]
    ten = {"diem_tien": "Tiền kiểm tra", "diem_hau": "Hậu kiểm tra", "tien_bo": "Tiến bộ", "diem_duy": "Sau 7 ngày",
           "giam": "Mức giảm sau 7 ngày", "ht1": "Hứng thú lần 1", "ht2": "Hứng thú lần 2", "sus": "SUS"}
    for k, v in ten.items():
        a, b = kq[k][TN], kq[k][DC]
        dong.append(f"| {v} | {f(a['tb'])} ± {f(a['dlc'])} (n = {a['n']}) | {f(b['tb'])} ± {f(b['dlc'])} (n = {b['n']}) |")
    dong += ["", f"- Hai lớp tương đương ở tiền kiểm tra: {p(kd['tuong_duong_tien_kt'])}",
             f"- H1 – tiến bộ TN so với ĐC (Welch): {p(kd['H1_tien_bo'])}; Cohen's d = {f(kd['H1_cohen_d'])}; hậu kiểm tra TN cao hơn ĐC {f(kd['H1_hau_kt_cao_hon_pct'], 1)} %",
             f"- Tiến bộ trong lớp TN (ghép cặp): {p(kd['ghep_cap_TN'])}; trong lớp ĐC: {p(kd['ghep_cap_DC'])}",
             f"- H2 – mức giảm sau 7 ngày (Welch): {p(kd['H2_giam_sau_7_ngay'])}",
             f"- H3 – hứng thú lần 2 (Welch): {p(kd['H3_hung_thu_lan_2'])}; Cronbach's alpha = {f(kd['alpha_hung_thu'])}",
             f"- H4 – SUS trung bình lớp TN: {f(kd['H4_sus_tb'], 1)}"]
    return "\n".join(dong) + "\n"


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    vao = sys.argv[1]; ra = sys.argv[2] if len(sys.argv) > 2 else vao
    os.makedirs(ra, exist_ok=True)
    tep = doc_csv(vao)
    if "tien" not in tep or "hau" not in tep:
        print("Chưa có đủ tệp Tiền KT và Hậu KT – không phân tích."); sys.exit(2)
    g, kq = phan_tich(tep)
    g.to_csv(os.path.join(ra, "ghep_theo_hs.csv"), index=False)
    json.dump(kq, open(os.path.join(ra, "ket_qua.json"), "w"), ensure_ascii=False, indent=1)
    open(os.path.join(ra, "ket_qua.md"), "w").write(bao_cao_md(kq))
    bieu_do(g, kq, ra)
    print(bao_cao_md(kq))


if __name__ == "__main__":
    main()
