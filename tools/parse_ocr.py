import re, glob, os, json, sys
UP = "A-ZĐÂĂÊÔƠƯÁÀẢÃẠẤẦẨẪẬẮẰẲẴẶÉÈẺẼẸẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢÚÙỦŨỤỨỪỬỮỰÝỲỶỸỴ"
def pages(g):
    out={}
    for f in sorted(glob.glob(f"/home/claude/sgk/ocr/LS{g}/p*.txt")):
        p=int(re.search(r"p(\d+)\.txt",f).group(1)); out[p]=open(f).read()
    return out
def lesson_starts(P):
    return [p for p,t in sorted(P.items()) if re.search(r"Học xong (bài|chủ đề) này", t) and p>8]
def title_before(t):
    i=t.find("Học xong")
    head=[l.strip() for l in t[:i].splitlines() if l.strip()]
    # lấy các dòng viết hoa gần nhất
    caps=[l for l in head if sum(c.isupper() for c in l) >= 0.6*sum(c.isalpha() for c in l) and sum(c.isalpha() for c in l)>3]
    return " ".join(caps[-3:])
def yccd(t):
    i=t.find("Học xong"); seg=t[i:i+900].splitlines()[1:]
    items=[]
    for l in seg:
        l=l.strip()
        if not l: continue
        if re.match(r"^[»«\-_•·*+.,~]+", l) or (items and len(items)<8 and l[0].islower()==False and len(l)>15):
            items.append(re.sub(r"^[»«\-_•·*+.,~\s]+","",l))
        if len(items)>=7: break
    return items[:7]
SEC = re.compile(rf"^\s*(\d{{1,2}})\s*[\.\)]\s*([{UP}][^\n]{{3,90}})$", re.M)
def sections(t):
    res=[]
    for m in SEC.finditer(t):
        s=m.group(2).strip()
        if len(s.split())>=2 and not re.search(r"\b(Quan sát|Em hãy|Hãy|Đọc|Dựa vào|Theo em)\b", s):
            res.append(f"{m.group(1)}. {s}")
    return res
if __name__=="__main__":
    g=sys.argv[1]; P=pages(g); S=lesson_starts(P)
    allp=sorted(P)
    for i,s in enumerate(S):
        e=(S[i+1]-1) if i+1<len(S) else s+6
        secs=[]
        for p in range(s,e+1):
            for x in sections(P.get(p,"")):
                if x not in secs: secs.append(x)
        print(f"--- pdf {s}-{e}: {title_before(P[s])}")
        for x in secs: print("    ", x)
