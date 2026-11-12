"""Soạn NHÁP chuỗi video cho từng bài từ văn bản OCR (Gemini flash-lite). Claude rà soát và chỉnh sau.
Kết quả: data/catalog/draft/{id}.json"""
import sys, os, json, glob, time
sys.path.insert(0, os.path.dirname(__file__)); import gemini
ROOT="/home/claude/eduhistory-studio"
L=json.load(open(f"{ROOT}/data/catalog/lessons.json"))["bai"]
OUT=f"{ROOT}/data/catalog/draft"; os.makedirs(OUT, exist_ok=True)
def pages(lesson):
    g=lesson["lop"]; same=[x for x in L if x["lop"]==g]; i=same.index(lesson)
    start=lesson["pdf"]; end=(same[i+1]["pdf"]-1) if i+1<len(same) and same[i+1]["pdf"]>start else start+6
    end=min(end, start+9)
    return [(p, open(f"/home/claude/sgk/ocr/LS{g}/p{p:03d}.txt").read()) for p in range(start,end+1) if os.path.exists(f"/home/claude/sgk/ocr/LS{g}/p{p:03d}.txt")]
SYS=("Bạn là biên tập viên nội dung video giáo dục Lịch sử cho học sinh THCS Việt Nam. Văn bản đầu vào là bản OCR (có lỗi chính tả do quét) "
     "của một bài trong SGK Lịch sử và Địa lí (bộ Kết nối tri thức). Bạn KHÔNG chép nguyên văn sách; mọi nội dung viết bằng lời của bạn, giữ đúng tên riêng, niên đại.")
PROMPT="""Bài: {id} – {ten} (Lớp {lop}, {chuong}). Văn bản OCR các trang (số trang in = số PDF − 2):
{txt}

Hãy lập kế hoạch CHUỖI VIDEO cho bài này. Mỗi bài tách thành nhiều video ngắn (thường 3–8 tập), mỗi tập kể MỘT nội dung như một câu chuyện, do hai học sinh dẫn chuyện Nhật Minh và Hân Hân dẫn dắt.
Trả về JSON:
{{"muc_chinh": ["các mục chính của bài theo SGK, đúng thứ tự"],
 "yeu_cau_can_dat": ["diễn đạt ngắn"],
 "tap": [{{"so": 1, "ten_tap": "tên hấp dẫn, ngắn", "noi_dung": "1–2 câu: tập này kể gì", "kien_thuc_chot": ["2–4 ý học sinh phải nhớ, đúng SGK"],
          "khung": "60s"|"2-3p"|"4-5p", "huong": "doc"|"ngang", "mo_phong": null hoặc "mô tả cảnh mô phỏng bằng code/tương tác nếu nội dung có không gian, diễn biến, cơ chế",
          "trang_sgk": [số trang in liên quan], "uu_tien": "P1"|"P2"|"P3"}}],
 "mo_phong_tuong_tac": null hoặc "đề xuất 1 mô phỏng tương tác cho cả bài (học sinh thao tác gì)"}}
Quy tắc: "doc" cho tập 60s kiểu mạng xã hội, "ngang" cho tập dài có bản đồ/diễn biến. P1 = trọng tâm hoặc có diễn biến/không gian; P3 = khái quát khó trực quan."""
def run(lesson):
    txt="\n".join(f"--- TRANG PDF {p} ---\n{t[:3500]}" for p,t in pages(lesson))
    out,_=gemini.generate([{"text":PROMPT.format(txt=txt, **lesson)}], model="gemini-3.1-flash-lite", json_mode=True, system=SYS, thinking=None, temperature=0.4, max_tokens=8000)
    o=json.loads(out); o=o[0] if isinstance(o,list) else o
    o["id"]=lesson["id"]; o["ten"]=lesson["ten"]; o["lop"]=lesson["lop"]; o["chuong"]=lesson["chuong"]
    json.dump(o, open(f"{OUT}/{lesson['id']}.json","w"), ensure_ascii=False, indent=1)
    return o
if __name__=="__main__":
    ids=sys.argv[1:]
    todo=[x for x in L if (not ids or x["id"] in ids) and not os.path.exists(f"{OUT}/{x['id']}.json")]
    for x in todo:
        try: o=run(x); print(x["id"], len(o.get("tap",[])), "tập", flush=True)
        except Exception as e: print(x["id"], "FAIL", str(e)[:150], flush=True); time.sleep(10)
