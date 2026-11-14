"""Lưu ảnh cảnh tải từ Gemini vào assets/episodes/<mã>/canh-XX.jpg: python3 tools/luu_anh.py <ảnh> <mã> <số cảnh>"""
import sys, os
from PIL import Image
src, ma, so = sys.argv[1], sys.argv[2], int(sys.argv[3])
d = f"/home/claude/eduhistory-studio/assets/episodes/{ma}"; os.makedirs(d, exist_ok=True)
im = Image.open(src).convert("RGB"); out = f"{d}/canh-{so:02d}.jpg"; im.save(out, quality=92)
im.resize((960, int(960 * im.height / im.width))).save(f"/home/claude/eduhistory-studio/tmp/qa/{ma}_canh-{so:02d}_xem.jpg", quality=80)
print(out, im.size)
