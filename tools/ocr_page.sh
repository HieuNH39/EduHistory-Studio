#!/bin/bash
# usage: ocr_page.sh <grade> <pdfpage>
g=$1; p=$2
out=/home/claude/sgk/ocr/LS$g
mkdir -p $out
f=$(printf "%s/p%03d" $out $p)
[ -s "$f.txt" ] && exit 0
pdftoppm -f $p -l $p -r 144 -gray -png /home/claude/sgk/LSDL$g.pdf $f.tmp >/dev/null 2>&1
img=$(ls $f.tmp*.png | head -1)
tesseract "$img" "$f" -l vie --psm 3 >/dev/null 2>&1
mv "$img" "$f.png"
