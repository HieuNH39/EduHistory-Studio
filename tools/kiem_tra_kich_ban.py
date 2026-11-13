"""Kiểm tra kịch bản trước khi dựng: nguồn trang, số liệu có trong OCR SGK, câu hỏi, sa bàn, giọng nhân vật."""
import json, sys, re, os, glob
ROOT = "/home/claude/eduhistory-studio"; OCR = "/home/claude/sgk/ocr"
CFG = json.load(open(f"{ROOT}/pipeline/config.json"))
def ocr_text(lop, trang):
    t = ""
    for p in trang:
        f = f"{OCR}/LS{lop}/p{int(p) + 2:03d}.txt"
        if os.path.exists(f): t += open(f).read()
    return re.sub(r"\s+", " ", t)
def so(s): return set(re.findall(r"\d+", s))
def kiem(ma):
    S = json.load(open(f"{ROOT}/data/scripts/{ma}.json")); lop = int(ma[1]); loi = []
    giong = set(CFG["tts"].get("vieneu_voices", {})) | {"Nhật Minh", "Hân Hân"}
    for sc in S["canh"]:
        tag = f"cảnh {sc['so']}"
        if sc.get("loi") and not sc.get("nguon_trang"): loi.append(f"{tag}: thiếu nguon_trang")
        txt = ocr_text(lop, sc.get("nguon_trang", []))
        sgk_so = so(txt)
        for ten, vi, *en in sc.get("loi", []):
            if ten not in giong: loi.append(f"{tag}: chưa có giọng cho '{ten}'")
            if not en or not en[0].strip(): loi.append(f"{tag}: thiếu phụ đề EN")
            for n in so(vi) - sgk_so:
                if len(n) >= 2 or sc.get("lop") not in ("cau_hoi",): loi.append(f"{tag}: số '{n}' không thấy trong OCR tr. {sc.get('nguon_trang')}")
        if sc.get("lop") == "sa_ban":
            f = f"{ROOT}/pipeline/maps/specs/{sc['sa_ban']}.json"
            if not os.path.exists(f): loi.append(f"{tag}: thiếu sa bàn {sc['sa_ban']}")
            elif (json.load(open(f)).get("phien_ban") == 2 or json.load(open(f)).get("loai") == "the_gioi") and sc["pha"] not in json.load(open(f)).get("pha", {}): loi.append(f"{tag}: sa bàn {sc['sa_ban']} không có pha {sc['pha']}")
        if sc.get("lop") == "cau_hoi":
            q = sc["cau_hoi"]
            if not 0 <= q["dung"] < len(q["lua_chon"]): loi.append(f"{tag}: đáp án ngoài phạm vi")
            dap = "ABCD"[q["dung"]]
            if not any(f"là {dap}" in l[1] for l in sc["loi"]): loi.append(f"{tag}: lời đọc đáp án không khớp {dap}")
    for q in S.get("cau_hoi", []):
        if not 0 <= q["dung"] < len(q["dap_an"]): loi.append(f"câu hỏi '{q['hoi'][:30]}': đáp án ngoài phạm vi")
    return loi
if __name__ == "__main__":
    for ma in sys.argv[1:] or [os.path.basename(f)[:-5] for f in sorted(glob.glob(f"{ROOT}/data/scripts/*.json"))]:
        r = kiem(ma); print(ma, "OK" if not r else ""); [print("  -", x) for x in r]
