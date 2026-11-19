#!/usr/bin/env python3
"""Dựng bản "mở đầu gây tò mò" cho video dọc đăng TikTok / YouTube Shorts (thầy duyệt 19/11).

Thêm 2 giây đầu: cảnh tái hiện/tư liệu kịch tính nhất của chính video (đang chuyển động, phóng nhẹ),
câu hỏi gợi tò mò cỡ chữ lớn ở nửa trên, tiếng "vút" ngắn – rồi nối vào video gốc nguyên vẹn.
Không thêm nội dung lịch sử mới: chữ lấy từ câu hỏi ôn tập trong kịch bản hoặc tên tập.

    python3 tools/mo_dau_hook.py MA [MA ...]       # L6-B1-01, TT-03 ...
Ra: renders/hook/<MA>.mp4  (1080x1920, H.264 High crf 18, AAC 48 kHz)
"""
import json, os, re, subprocess, sys, textwrap
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(ROOT, "assets/fonts/be-vietnam-pro-900-normal.ttf")
FONT2 = os.path.join(ROOT, "assets/fonts/be-vietnam-pro-700-normal.ttf")
W, H, DUR = 1080, 1920, 2.0
OUT = os.path.join(ROOT, "renders/hook")


def dur(f):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", f]))


def loi_cua(c):
    s = 0
    for x in c.get("loi") or []:
        if isinstance(x, list) and len(x) > 1:
            s += len(x[1])
    return s


def chon_thoi_diem(d, tong):
    """Ước lượng thời điểm giữa cảnh tái hiện đầu tiên theo độ dài lời đọc từng cảnh."""
    canh = d["canh"]
    w = []
    for c in canh:
        if c.get("lop") == "cau_hoi":
            w.append(140)
        else:
            w.append(loi_cua(c) + 25)
    tot = sum(w) or 1
    uu_tien = [i for i, c in enumerate(canh) if c.get("lop") == "tai_hien"] or \
              [i for i, c in enumerate(canh) if c.get("lop") in ("tu_lieu", "sa_ban", "mo_phong", "du_hanh")] or \
              [i for i, c in enumerate(canh) if c.get("lop") == "dan_chuyen"]  # tránh thẻ ghi nhớ/câu hỏi (nhiều chữ)
    i = uu_tien[0] if uu_tien else 0
    t = (sum(w[:i]) + w[i] * 0.45) / tot * tong
    return max(0.3, min(t, tong - DUR - 0.5))


def tim_khung(src, tong, du_phong):
    """Chọn đoạn mở đầu bằng cách xem chính video (1 khung/giây, ảnh thu nhỏ):
    bỏ các thẻ chữ nền xanh than (ghi nhớ, câu hỏi), ưu tiên đoạn hình ảnh chi tiết đầu tiên dài ≥ 3 giây."""
    import numpy as np
    w, h = 36, 64
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-vf", f"fps=1,scale={w}:{h}", "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    n = len(raw) // (w * h * 3)
    if n < 6:
        return du_phong
    f = np.frombuffer(raw, np.uint8)[:n * w * h * 3].reshape(n, h, w, 3).astype(int)
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    navy = ((r < 50) & (g < 70) & (b > 35) & (b < 120) & (b > r + 12)).mean(axis=(1, 2))
    flat = (np.abs(np.diff(f, axis=2)).sum(-1) < 12).mean(axis=(1, 2))
    gioi_han = int(min(n, tong * 0.75))

    def doan(dk):
        out, i = [], 1
        while i < gioi_han:
            if dk(i):
                j = i
                while j + 1 < gioi_han and dk(j + 1):
                    j += 1
                out.append((i, j))
                i = j + 1
            else:
                i += 1
        return out
    chi_tiet = [d for d in doan(lambda i: navy[i] < 0.12 and flat[i] < 0.38) if d[1] - d[0] >= 2]
    if chi_tiet:
        a, bb = chi_tiet[0]
        return min(a + 0.6 + min(1.5, (bb - a) * 0.3), tong - DUR - 0.5)
    sach = [d for d in doan(lambda i: navy[i] < 0.4) if d[1] - d[0] >= 2]  # thẻ chữ có navy ≥ 0.6
    if sach:
        a, bb = sach[0]
        return min(a + 0.6, tong - DUR - 0.5)
    return du_phong


# Câu mở đầu cho 12 video Chuyện sử – viết theo đúng lời trong video (không thêm dữ kiện mới)
MOC_TT = {
    "TT-01": "Đào đường ở Cổ Loa, công nhân trúng cả một hố mũi tên đồng!",
    "TT-02": "Một dòng sông đã 3 lần nhấn chìm quân xâm lược",
    "TT-03": "Ai đã đổi áo, giả làm Lê Lợi để cứu chủ tướng?",
    "TT-04": "Tết Kỷ Dậu 1789: cành đào nào gửi từ Thăng Long?",
    "TT-05": "Ra Hoàng Sa, mỗi người mang theo chiếc chiếu và dây mây. Vì sao?",
    "TT-06": "Cây cầu Nhật Bản giữa lòng Hội An có từ bao giờ?",
    "TT-07": "270 người ra đi, chỉ 18 người trở về",
    "TT-08": "Ai đã xây kim tự tháp? Một con ngựa vấp ngã đã giúp tìm ra câu trả lời",
    "TT-09": "Quả táo rơi trúng đầu Niu-tơn: thật hay đồn?",
    "TT-10": "Giêm Oát có thật nghĩ ra máy hơi nước nhờ ấm nước?",
    "TT-11": "162 hình đúc nổi trên 9 chiếc đỉnh đồng ở Huế",
    "TT-12": "Bài thơ nào vang lên giữa đêm bên sông Như Nguyệt?",
}


def cau_moc(ma, d):
    if ma.startswith("TT-"):
        return MOC_TT.get(ma, d.get("ten_tap", "").strip())
    for q in d.get("cau_hoi") or []:
        h = q["hoi"].strip()
        if 12 <= len(h) <= 85:
            # câu điền khuyết ("… là", "… theo") → thêm "…?" để người xem muốn biết đáp án
            return h if h[-1] in "?…" else h.rstrip(" :,.") + "…?"
    return d.get("ten_tap", "").strip()


def nhan(ma, d):
    if ma.startswith("TT-"):
        return "Chuyện sử EduHistory"
    m = re.match(r"L(\d+)-(B|CD)(\d+)", ma)
    return f"Lịch sử {m.group(1)} – " + (f"Bài {m.group(3)}" if m.group(2) == "B" else f"Chủ đề chung {m.group(3)}")


def lop_chu(png, text, tag):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    # dải tối phía trên cho chữ dễ đọc, dải tối phía dưới che phụ đề cũ (khu vực giao diện TikTok)
    for y in range(0, 1000):
        a = int(230 * (1 - y / 1000) ** 1.1)
        dr.line([(0, y), (W, y)], fill=(8, 12, 24, a))
    for y in range(1380, H):
        a = min(255, int(300 * ((y - 1380) / (H - 1380)) ** 0.7))
        dr.line([(0, y), (W, y)], fill=(8, 12, 24, a))
    size = 92
    while True:
        f = ImageFont.truetype(FONT, size)
        width_chars = max(8, int(940 / (size * 0.56)))
        lines = textwrap.wrap(text, width=width_chars)
        if len(lines) <= 4 and all(dr.textlength(l, font=f) <= 960 for l in lines):
            break
        size -= 4
    f2 = ImageFont.truetype(FONT2, 40)
    tw = dr.textlength(tag, font=f2)
    y0 = 250
    dr.rounded_rectangle([(W - tw) / 2 - 26, y0, (W + tw) / 2 + 26, y0 + 66], radius=33, fill=(242, 140, 40, 255))
    dr.text((W / 2, y0 + 33), tag, font=f2, fill=(255, 255, 255, 255), anchor="mm")
    y = y0 + 110
    for l in lines:
        dr.text((W / 2, y), l, font=f, fill=(255, 255, 255, 255), anchor="ma", stroke_width=6, stroke_fill=(10, 14, 28, 255))
        y += int(size * 1.18)
    img.save(png)


def dung(ma):
    tt = ma.startswith("TT-")
    src = os.path.join(ROOT, f"renders/tiktok/{ma}.mp4" if tt else f"renders/v1/{ma}.mp4")
    d = json.load(open(os.path.join(ROOT, f"data/tiktok/{ma}.json" if tt else f"data/scripts/{ma}.json"), encoding="utf-8"))
    tong = dur(src)
    t = 1.0 if tt else tim_khung(src, tong, chon_thoi_diem(d, tong))
    os.makedirs(OUT, exist_ok=True)
    png = f"/tmp/hook_{ma}.png"
    lop_chu(png, cau_moc(ma, d), nhan(ma, d))
    out = os.path.join(OUT, f"{ma}.mp4")
    tmp = out + ".tmp.mp4"
    # đoạn mở đầu đọc từ một đầu vào riêng (-ss) để ffmpeg không phải giữ hàng nghìn khung hình trong RAM
    fc = (f"[0:v]setpts=PTS-STARTPTS,scale={W*1.08:.0f}:{H*1.08:.0f},"
          f"crop={W}:{H}:'(iw-{W})/2*(1-t/{DUR})':'(ih-{H})/2*(1-t/{DUR})',fps=30,format=yuv420p[a0];"
          f"[a0][1:v]overlay=0:0,fade=t=in:st=0:d=0.12[iv];"
          # tiếng "vút" + nhịp trống trầm, tổng hợp bằng ffmpeg (không dùng nhạc có bản quyền)
          f"anoisesrc=d={DUR}:c=pink:a=0.5,highpass=f=300,lowpass=f=4000,afade=t=in:d=0.35,afade=t=out:st=0.5:d=0.6,"
          f"volume=0.35,aformat=sample_rates=48000:channel_layouts=stereo[wh];"
          f"sine=f=55:d={DUR},afade=t=in:st=0.55:d=0.03,afade=t=out:st=0.6:d=1.2,volume=0.9,"
          f"aformat=sample_rates=48000:channel_layouts=stereo[bm];"
          f"[wh][bm]amix=inputs=2:normalize=0,atrim=0:{DUR}[ia];"
          f"[2:v]fps=30,format=yuv420p,setpts=PTS-STARTPTS[mv];[2:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[ma];"
          f"[iv][ia][mv][ma]concat=n=2:v=1:a=1[v][a]")
    cmd = ["nice", "-n", "10", "ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-t", str(DUR), "-i", src,
           "-loop", "1", "-t", str(DUR), "-i", png, "-i", src,
           "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-profile:v", "high", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", tmp]
    subprocess.check_call(cmd)
    if abs(dur(tmp) - (tong + DUR)) > 0.4:
        raise SystemExit(f"{ma}: thời lượng lệch ({dur(tmp):.2f} so với {tong + DUR:.2f})")
    os.replace(tmp, out)
    print(f"{ma}: t={t:.1f}s, '{cau_moc(ma, d)}' → {out}")


if __name__ == "__main__":
    for m in sys.argv[1:]:
        dung(m)
