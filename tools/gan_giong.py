#!/usr/bin/env python3
"""Gán giọng VieNeu cho nhân vật mới trong data/scripts/_giong_can_them_*.json (chưa có trong pipeline/config.json).
Chọn theo mô tả (nữ / cao tuổi / trẻ / người nước ngoài) và tránh trùng giọng với người cùng nói trong một tập."""
import json, glob, os, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "pipeline/config.json")
cfg = json.load(open(P)); vv = cfg["tts"]["vieneu_voices"]
need = {}
for p in sorted(glob.glob(os.path.join(ROOT, "data/scripts/_giong_can_them_*.json"))):
    need.update(json.load(open(p)))
co = collections.defaultdict(set)
for f in glob.glob(os.path.join(ROOT, "data/scripts/L*.json")):
    d = json.load(open(f)); sp = {l[0] for c in d["canh"] for l in c.get("loi", [])}
    for a in sp: co[a] |= sp - {a}
    for a in sp:
        if a not in vv and a not in need and a not in ("Nhật Minh", "Hân Hân"): need[a] = "nam trung niên"
need = {k: v for k, v in need.items() if k not in vv}
TRE = ["Hải Đăng", "Quốc Tuấn", "Xuân Vĩnh", "Phạm Tuyên"]
TRUNG = ["Thiện Minh", "Minh Đức", "Xuân Vĩnh", "Phạm Tuyên", "Hải Đăng", "Quốc Tuấn", "Thanh Bình"]
GIA = ["Thiền Tâm Đức", "Thanh Bình", "Thiện Minh"]
NGOAI = ["Minh Triết", "Đức Trí", "Adam", "Thái Sơn", "Quang Sơn"]
NU = ["Đoan Trang", "Ngọc Linh", "Mai Anh", "Quỳnh Anh", "Trúc Ly", "Ngọc Huyền"]
NUOC_NGOAI = ["Anh", "Pháp", "Hy Lạp", "Ai Cập", "Ả Rập", "Hán", "Tống", "nhà Minh", "Thanh", "Nguyên", "Mông Cổ", "Giéc-man", "thổ dân",
              "Xiêm", "Ấn", "thái thú", "đô hộ", "thứ sử", "người nước ngoài", "Xu-me", "Lái buôn Hy Lạp"]
def ngoai(n, d):
    return ("-" in n and not n.startswith("Chế")) or any(k in d or k in n for k in NUOC_NGOAI)
gan = {}
for n, d in need.items():
    dl = d.lower()
    if dl.startswith("nữ") or " nữ " in f" {dl.split(',')[0]} " or n in ("Lý Chiêu Hoàng",): cand = NU
    elif "nhóm" in dl: cand = ["Thanh Bình", "Xuân Vĩnh"]
    elif ngoai(n, d): cand = NGOAI + TRUNG
    elif "cao tuổi" in dl: cand = GIA + TRUNG
    elif "trẻ" in dl or "thiếu niên" in dl: cand = TRE + TRUNG
    else: cand = TRUNG + GIA
    taken = {vv.get(p) or gan.get(p) for p in co.get(n, ())} | {vv["Nhật Minh"], vv["Hân Hân"]}
    gan[n] = next((c for c in cand if c not in taken), cand[0])
vv.update(gan)
json.dump(cfg, open(P, "w"), ensure_ascii=False, indent=1)
for n, v in gan.items(): print(f"{n}: {v}")
