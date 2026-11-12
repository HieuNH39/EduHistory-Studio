"""Gộp nháp chuỗi video (data/catalog/draft) thành danh mục tập chính thức data/catalog/episodes.json.
- Xác định lại trang SGK (trang in) cho từng tập bằng cách đối khớp từ khoá của tập với văn bản OCR từng trang của bài.
- Chuẩn hoá khung/hướng/ưu tiên, đánh mã tập: L7-B14-03."""
import json, glob, re, os, unicodedata
ROOT="/home/claude/eduhistory-studio"
L=json.load(open(f"{ROOT}/data/catalog/lessons.json"))["bai"]
def norm(s):
    s=unicodedata.normalize("NFC", s.lower())
    return re.sub(r"[^0-9a-zà-ỹđ ]+"," ",s)
def grams(s, n=2):
    w=norm(s).split(); return {" ".join(w[i:i+n]) for i in range(len(w)-n+1)}
def lesson_pages(les):
    g=les["lop"]; same=[x for x in L if x["lop"]==g]; i=same.index(les)
    start=les["pdf"]; nxt=[x["pdf"] for x in same[i+1:] if x["pdf"]>start]
    end=(nxt[0]-1) if nxt else start+9
    out={}
    for p in range(start, min(end, start+12)+1):
        f=f"/home/claude/sgk/ocr/LS{g}/p{p:03d}.txt"
        if os.path.exists(f): out[p-2]=grams(open(f).read())
    return out
STOP={"của các","và các","là một","trong các","có thể"}
def match_pages(ep, pages):
    q=grams(" ".join([ep["ten_tap"], ep["noi_dung"], *ep.get("kien_thuc_chot",[])]))-STOP
    sc={p:len(q & g) for p,g in pages.items()}
    if not sc: return []
    best=max(sc.values())
    if best<2: return []
    keep=sorted(p for p,v in sc.items() if v>=max(2, best*0.5))
    return keep
def main():
    eps=[]; byles={}
    for les in L:
        f=f"{ROOT}/data/catalog/draft/{les['id']}.json"
        if not os.path.exists(f): continue
        d=json.load(open(f)); pages=lesson_pages(les)
        lo=min(pages) if pages else les["trang_in"]; hi=max(pages) if pages else les["trang_in"]
        for t in d.get("tap",[]):
            pg=match_pages(t, pages)
            old=[int(x) for x in (t.get("trang_sgk") or []) if str(x).isdigit()]
            if not pg:
                # nháp có thể ghi số trang PDF: quy về trang in nếu lệch khỏi khoảng của bài
                pg=[p if lo<=p<=hi else p-2 for p in old]; pg=[p for p in pg if lo<=p<=hi] or [lo]
            e={"ma":f"{les['id']}-{int(t['so']):02d}","bai":les["id"],"lop":les["lop"],"ten_bai":les["ten"],
               "so":int(t["so"]),"ten_tap":t["ten_tap"].strip(),"noi_dung":t["noi_dung"].strip(),
               "kien_thuc_chot":t.get("kien_thuc_chot",[]),"khung":t.get("khung","2-3p"),"huong":t.get("huong","ngang"),
               "mo_phong":t.get("mo_phong"),"trang_sgk":pg,"uu_tien":t.get("uu_tien","P2"),"trang_thai":"nhap"}
            eps.append(e)
        byles[les["id"]]={"muc_chinh":d.get("muc_chinh"),"yeu_cau_can_dat":d.get("yeu_cau_can_dat"),
                          "mo_phong_tuong_tac":d.get("mo_phong_tuong_tac")}
    json.dump({"nguon":"Nháp Gemini 3.1 flash-lite từ OCR SGK, Claude rà soát; trang_sgk = trang in","so_tap":len(eps),
               "bai":byles,"tap":eps}, open(f"{ROOT}/data/catalog/episodes.json","w"), ensure_ascii=False, indent=1)
    print(len(eps))
if __name__=="__main__": main()
