"""Tìm trang chép bị lặp chữ (lỗi mô hình) và chép lại từng trang với cấu hình khác."""
import sys, os, re, glob, subprocess
sys.path.insert(0, os.path.dirname(__file__)); import gemini
REP = re.compile(r"(\b\w+\b)(?:\s+\1\b){6,}", re.U)
def bad(path):
    t=open(path).read()
    return bool(REP.search(t)) or len(t) > 20000
def redo(g, p):
    jpg=f"/tmp/fx_{g}_{p}.jpg"
    subprocess.run(["convert", f"/home/claude/sgk/ocr/LS{g}/p{p:03d}.png","-resize","1400x","-quality","85",jpg],check=True)
    prompt=f"""Đây là trang PDF {p} của sách giáo khoa Lịch sử và Địa lí {g}. Viết dòng đầu:
=== PDF {p} | IN {{số trang in ở chân trang, nếu không thấy thì ?}} | PHẦN {{LICH_SU hoặc DIA_LI hoặc CHU_DE_CHUNG hoặc KHAC}} ===
rồi chép lại CHÍNH XÁC toàn bộ chữ trên trang dưới dạng Markdown (tiêu đề #/##/###, gạch đầu dòng, "[Hình x. ...]" cho chú thích hình, "> " cho khung tư liệu). Không tóm tắt, không bình luận."""
    for th,temp in (("low",0.3),("medium",0.5)):
        txt,_=gemini.generate([gemini.image_part(jpg,"image/jpeg"),{"text":prompt}], thinking=th, temperature=temp, max_tokens=8000)
        if not REP.search(txt) and txt.startswith("=== PDF"):
            return txt
    return txt
for g in sys.argv[1:]:
    for f in sorted(glob.glob(f"/home/claude/eduhistory/data/sgk/LS{g}/p*.md")):
        if bad(f):
            p=int(re.search(r"p(\d+)\.md",f).group(1))
            t=redo(g,p); open(f,"w").write(t.strip()+"\n")
            print(f"fixed LS{g} p{p}: still_bad={bool(REP.search(t))}", flush=True)
