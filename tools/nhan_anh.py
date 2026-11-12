"""Nhận ảnh Gemini đã đưa về (uploads/Downloads) → lưu đúng chỗ (JPEG chất lượng cao) + ảnh xem nhanh /tmp/xem.jpg"""
import sys
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGB")
# xoá dấu ✦ của Gemini ở góc phải dưới bằng cách lấy mẫu vùng bên cạnh
w, h = im.size; s = int(min(w, h) * 0.1)
patch = im.crop((w - 2 * s, h - s, w - s, h)); im.paste(patch, (w - s, h - s))
im.save(dst, quality=93)
t = im.copy(); t.thumbnail((1100, 640)); t.save("/tmp/xem.jpg", quality=80)
print(dst, im.size)
