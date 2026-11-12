"""Lập danh sách nhân vật lịch sử cho từng tập (nháp Gemini flash-lite, Claude rà soát).
Đầu ra: data/catalog/characters_raw/{bai}.json"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__)); import gemini
ROOT="/home/claude/eduhistory-studio"
E=json.load(open(f"{ROOT}/data/catalog/episodes.json"))["tap"]
OUT=f"{ROOT}/data/catalog/characters_raw"; os.makedirs(OUT, exist_ok=True)
def ocr(lop, pages):
    t=[]
    for p in sorted(set(pages)):
        f=f"/home/claude/sgk/ocr/LS{lop}/p{p+2:03d}.txt"
        if os.path.exists(f): t.append(f"--- trang {p} ---\n"+open(f).read()[:3000])
    return "\n".join(t)
PROMPT="""Đây là các tập video của bài {bai} ({ten_bai}, Lịch sử lớp {lop}). Với mỗi tập, liệt kê các NHÂN VẬT nên xuất hiện trên hình khi tái hiện lịch sử.
Gồm: nhân vật lịch sử có tên (vua, tướng, nhà cải cách, nhà khoa học, nhà văn...), và các nhóm người tiêu biểu (ví dụ "nghĩa quân Lam Sơn", "quân Minh", "nông dân Đàng Ngoài", "công nhân Anh thế kỉ XIX").
Chỉ lấy nhân vật/nhóm có trong văn bản SGK dưới đây hoặc thực sự cần cho cảnh tái hiện của tập. KHÔNG bịa.
Phân loại "thoi_ky": "co_dai_trung_dai" (đến hết thế kỉ XIX) hoặc "hien_dai" (từ đầu thế kỉ XX; dùng ảnh thật, không vẽ AI) — người sống sang thế kỉ XX tính theo thời điểm xuất hiện trong tập.
Trả về JSON: {{"tap":[{{"ma":"...","nhan_vat":[{{"ten":"tên tiếng Việt chuẩn SGK","loai":"ca_nhan"|"nhom","thoi_ky":"co_dai_trung_dai"|"hien_dai","quoc_gia":"...","vai_tro":"ngắn","the_ki":"ví dụ XVIII"}}]}}]}}

CÁC TẬP:
{taps}

VĂN BẢN SGK (OCR, có lỗi quét):
{txt}"""
def run(bai):
    eps=[e for e in E if e["bai"]==bai]
    pages=sorted({p for e in eps for p in e["trang_sgk"]})
    taps="\n".join(f'{e["ma"]}: {e["ten_tap"]} — {e["noi_dung"]} | {"; ".join(e["kien_thuc_chot"])}' for e in eps)
    out,_=gemini.generate([{"text":PROMPT.format(bai=bai, ten_bai=eps[0]["ten_bai"], lop=eps[0]["lop"], taps=taps, txt=ocr(eps[0]["lop"], pages)[:24000])}],
                          model="gemini-3.1-flash-lite", json_mode=True, thinking=None, temperature=0.2, max_tokens=6000)
    o=json.loads(out); o=o[0] if isinstance(o,list) else o
    json.dump(o, open(f"{OUT}/{bai}.json","w"), ensure_ascii=False, indent=1); return o
if __name__=="__main__":
    bais=sorted({e["bai"] for e in E}, key=lambda b:[e["bai"] for e in E].index(b))
    for b in bais:
        if os.path.exists(f"{OUT}/{b}.json"): continue
        try: o=run(b); print(b, sum(len(t["nhan_vat"]) for t in o["tap"]), flush=True)
        except Exception as ex: print(b,"FAIL",str(ex)[:120], flush=True); time.sleep(8)
