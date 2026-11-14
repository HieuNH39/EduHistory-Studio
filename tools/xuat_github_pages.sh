#!/bin/bash
# Xuất kho học liệu (web/) thành bản đăng GitHub Pages: chép trang tĩnh + nén lại video 720p (nhẹ cho mạng),
# rồi đẩy lên nhánh gh-pages của kho mã. Video gốc 1080p vẫn ở renders/v1 (không đưa lên GitHub).
# Cách dùng: bash tools/xuat_github_pages.sh [--khong-day]
set -e
cd "$(dirname "$0")/.."
OUT=tmp/pages
mkdir -p "$OUT"
# 1) trang tĩnh (trừ video), bỏ công cụ sinh trang
rm -rf "$OUT/site.tmp"; mkdir -p "$OUT/site.tmp"
tar -C web --exclude=./videos --exclude=./_cong-cu --exclude='*.py' -cf - . | tar -C "$OUT/site.tmp" -xf -
mkdir -p "$OUT/site/videos"; mv "$OUT/site/videos" "$OUT/site.tmp/videos"; rm -rf "$OUT/site"; mv "$OUT/site.tmp" "$OUT/site"
mkdir -p "$OUT/site/videos"
# 2) video: nén 720p (ngang 1280×720, dọc 720×1280), giữ tiếng, faststart để phát ngay khi đang tải
for v in web/videos/*.mp4; do
  [ -e "$v" ] || continue
  [ -n "$NHANH" ] && continue   # NHANH=1: đăng nhanh, chưa nén video mới
  ma=$(basename "$v" .mp4); dich="$OUT/site/videos/$ma.mp4"
  if [ -f "$dich" ] && [ "$dich" -nt "$v" ]; then continue; fi
  h=$(ffprobe -v error -select_streams v -show_entries stream=height -of csv=p=0 "$v")
  w=$(ffprobe -v error -select_streams v -show_entries stream=width -of csv=p=0 "$v")
  if [ "$h" -gt "$w" ]; then sc="scale=720:-2"; else sc="scale=-2:720"; fi
  nice -n 19 ffmpeg -v error -y -threads 2 -i "$v" -vf "$sc" -c:v libx264 -preset veryfast -crf 27 \
       -c:a aac -b:a 112k -movflags +faststart "$dich.tmp.mp4" && mv "$dich.tmp.mp4" "$dich"
  echo "nén $ma: $(du -h "$dich" | cut -f1)"
done
touch "$OUT/site/.nojekyll"
du -sh "$OUT/site"
[ "$1" == "--khong-day" ] && exit 0
# 3) đẩy lên nhánh gh-pages (lịch sử riêng, ghi đè)
cd "$OUT/site"
rm -rf .git; git init -q -b gh-pages
git add -A
git -c user.name=HieuNH39 -c user.email=HieuNH39@users.noreply.github.com commit -q -m "Bản đăng GitHub Pages của kho học liệu EduHistory Studio ($(date +%d/%m/%Y))

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01XUaCeG6RmrTP1nxBNNZ2CP"
git remote add origin https://github.com/HieuNH39/EduHistory-Studio.git
git -c http.postBuffer=524288000 push -q -f origin gh-pages
echo "Đã đẩy: https://hieunh39.github.io/EduHistory-Studio/"
