"""Vẽ bảng ứng viên ảnh tư liệu (mỗi cảnh một hàng, tối đa 6 ảnh, số 1–6) để chọn: tmp/tl/bang_NN.jpg"""
import json, os, sys, io, urllib.request, textwrap
from PIL import Image, ImageDraw, ImageFont
ROOT = "/home/claude/eduhistory-studio"; OUT = f"{ROOT}/tmp/tl"
UA = {"User-Agent": "EduHistoryStudio/1.0 (https://github.com/HieuNH39/EduHistory-Studio; school project) python-urllib/3"}
F = lambda s: ImageFont.truetype(f"{ROOT}/assets/fonts/be-vietnam-pro-600-normal.ttf", s)
kq = json.load(open(f"{OUT}/ung_vien.json"))
chon = {}
try: chon = json.load(open(f"{OUT}/chon.json"))
except Exception: pass
ds = [x for x in kq if f"{x['ma']}/{x['so']}" not in chon and x.get("ung_vien")]
moi = int(sys.argv[1]) if len(sys.argv) > 1 else 5
TW, TH = 250, 180
for k in range(0, len(ds), moi):
    nhom = ds[k:k + moi]; Wb = 330 + 8 * (TW + 8); Hb = len(nhom) * (TH + 46)
    im = Image.new("RGB", (Wb, Hb), "white"); d = ImageDraw.Draw(im)
    for i, x in enumerate(nhom):
        y = i * (TH + 46)
        d.text((8, y + 6), f"{x['ma']} c{x['so']}", font=F(20), fill="#B5490C")
        for j, line in enumerate(textwrap.wrap(x["mo_ta"], 34)[:8]): d.text((8, y + 34 + j * 22), line, font=F(15), fill="#10233F")
        for j, u in enumerate(x["ung_vien"]):
            cache = f"{OUT}/th_{abs(hash(u['thumb'])) % 10**10}.jpg"
            if not os.path.exists(cache):
                try:
                    with urllib.request.urlopen(urllib.request.Request(u["thumb"], headers=UA), timeout=40) as r: open(cache, "wb").write(r.read())
                except Exception: continue
            t = Image.open(cache).convert("RGB"); t.thumbnail((TW, TH))
            x0 = 330 + j * (TW + 8); im.paste(t, (x0, y + 4))
            d.rectangle([x0, y + 4, x0 + 30, y + 32], fill="#10233F"); d.text((x0 + 8, y + 6), str(j + 1), font=F(20), fill="white")
            d.text((x0, y + TH + 8), f"{u['giay_phep'][:18]} · {u['ngay'][:12]}", font=F(13), fill="#555")
            d.text((x0, y + TH + 24), u["tep"][5:45], font=F(12), fill="#888")
    p = f"{OUT}/bang_{k // moi:02d}.jpg"; im.save(p, quality=82); print(p, im.size)
