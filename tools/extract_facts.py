"""Trích DỮ KIỆN (không chép nguyên văn) từ ảnh trang SGK bằng Gemini -> data/kb/LS{g}/p{NNN}.json
Mỗi dữ kiện được diễn đạt lại ngắn gọn, giữ chính xác tên riêng, niên đại, số liệu, kèm số trang in để trích dẫn."""
import sys, os, re, glob, subprocess, time, json
sys.path.insert(0, os.path.dirname(__file__)); import gemini
g = sys.argv[1]; only = sys.argv[2:] 
OUT=f"/home/claude/eduhistory/data/kb/LS{g}"; os.makedirs(OUT, exist_ok=True)
pages=[int(re.search(r"p(\d+)\.png",p).group(1)) for p in sorted(glob.glob(f"/home/claude/sgk/ocr/LS{g}/p*.png"))]
if only: pages=[int(x) for x in only]
todo=[p for p in pages if not os.path.exists(f"{OUT}/p{p:03d}.json")]
SYS="Bạn là chuyên viên biên tập học liệu Lịch sử. Bạn KHÔNG chép nguyên văn sách; bạn trích dữ kiện và diễn đạt lại bằng lời của mình, giữ chính xác tuyệt đối tên riêng, niên đại, số liệu."
PROMPT="""Các ảnh là trang PDF {lst} (theo thứ tự) của SGK Lịch sử và Địa lí {g}, bộ Kết nối tri thức với cuộc sống.
Trả về MỘT mảng JSON, mỗi phần tử ứng với một trang, dạng:
{{"pdf": số trang PDF, "in": số trang in ở chân trang (số nguyên hoặc null), "phan": "LICH_SU"|"DIA_LI"|"CHU_DE_CHUNG"|"KHAC",
 "chuong": tên chương nếu trang mở đầu chương hoặc ghi ở đầu trang, ngược lại null,
 "bai": "Bài N. Tên bài" nếu trang thuộc một bài (kể cả trang giữa bài, suy từ tiêu đề hoặc ngữ cảnh), ngược lại null,
 "bat_dau_bai": true nếu bài bắt đầu ở trang này,
 "muc": [các tiêu đề mục/tiểu mục xuất hiện trên trang, ví dụ "2. Diễn biến"],
 "yeu_cau_can_dat": [nếu trang có phần "Học xong bài này, em sẽ" thì liệt kê ý chính, diễn đạt ngắn gọn],
 "du_kien": [{{"loai": "su_kien"|"nhan_vat"|"dia_danh"|"so_lieu"|"khai_niem"|"nguyen_nhan"|"dien_bien"|"ket_qua"|"y_nghia"|"van_hoa"|"kinh_te_xa_hoi"|"khac",
              "noi_dung": "một câu diễn đạt lại bằng lời của bạn",
              "thoi_gian": "mốc thời gian nếu có, đúng như sách", "nhan_vat": [tên], "dia_danh": [tên]}}],
 "hinh": [{{"so": "Hình x", "mo_ta": "loại hình (ảnh hiện vật, lược đồ, tranh...) và nội dung chính"}}],
 "co_the_mo_phong": "nếu trang có nội dung về không gian, diễn biến, trận đánh, công trình, quy trình... phù hợp để làm mô phỏng/hoạt hình thì mô tả ngắn, ngược lại null"}}
Trang Địa lí hoặc trang không có nội dung lịch sử: chỉ cần pdf, in, phan và để các trường khác rỗng.
Lấy ĐẦY ĐỦ mọi dữ kiện lịch sử trên trang (kể cả trong khung tư liệu, chú thích hình, bảng), mỗi dữ kiện một câu ngắn."""
def run(batch):
    parts=[]
    for p in batch:
        jpg=f"/tmp/kb_{g}_{p}.jpg"
        subprocess.run(["convert", f"/home/claude/sgk/ocr/LS{g}/p{p:03d}.png","-resize","1400x","-quality","80",jpg],check=True)
        parts.append(gemini.image_part(jpg,"image/jpeg"))
    parts.append({"text":PROMPT.format(lst=", ".join(map(str,batch)), g=g)})
    txt,u=gemini.generate(parts, json_mode=True, system=SYS, thinking="minimal", temperature=0.2, max_tokens=24000)
    arr=json.loads(txt)
    if isinstance(arr, dict): arr=[arr]
    done=set()
    for o in arr:
        p=int(o.get("pdf",-1))
        if p in batch:
            json.dump(o, open(f"{OUT}/p{p:03d}.json","w"), ensure_ascii=False, indent=1); done.add(p)
    return u, [p for p in batch if p not in done]
q=[todo[i:i+3] for i in range(0,len(todo),3)]
while q:
    batch=q.pop(0)
    try:
        t=time.time(); u,miss=run(batch)
        print(f"[LS{g}] {batch} ok {time.time()-t:.0f}s out={u.get('candidatesTokenCount')} miss={miss}", flush=True)
    except Exception as e:
        print(f"[LS{g}] {batch} FAIL {str(e)[:160]}", flush=True)
        if len(batch)>1: q[0:0]=[[p] for p in batch]   # thử lại từng trang
        time.sleep(5)
