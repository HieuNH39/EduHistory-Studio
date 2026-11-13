#!/usr/bin/env python3
"""Soạn "phiếu giao việc" cho Gemini (Tạo video – Gemini Omni) từ kịch bản tập phim.

Mỗi cảnh hình (dẫn chuyện / du hành / tái hiện) thành một lời nhắc gồm:
  - khung hình đầu: ảnh cảnh đã duyệt (assets/episodes/<MA>/canh-XX.jpg) để giữ đúng nhân vật, trang phục, phong cách;
  - kịch bản của cảnh: diễn biến + nguyên văn lời thoại tiếng Việt, ai nói, giọng thế nào;
  - yêu cầu chất lượng: 16:9, nét, màu ấm theo tranh, chuyển động mượt, không chữ/phụ đề, không máu me;
  - âm thanh hiện trường kỹ lưỡng theo bối cảnh.
Lời dẫn của hai bạn dẫn chuyện (Nhật Minh, Hân Hân) khi KHÔNG xuất hiện trên hình vẫn do hệ thống đọc bằng giọng
cố định (để giọng giống nhau suốt 359 tập); Gemini lo hình + tiếng hiện trường + lời nhân vật nói trên hình.

Dùng:  python3 tools/gemini_video_brief.py L7-B14-04 [L8-B8-02 ...]
Ra:    data/gemini/hang_doi/<MA>.json  (thứ tự ưu tiên: cảnh hành động trước)
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GIONG = {
    "Nhật Minh": "a cheerful 13-year-old Vietnamese boy, clear northern Vietnamese accent",
    "Hân Hân": "a bright, warm 13-year-old Vietnamese girl, clear northern Vietnamese accent",
}
GIONG_MAC_DINH = "a calm, dignified adult Vietnamese man, northern accent"
GIONG_RIENG = {   # nhân vật lịch sử thường gặp
    "Trần Quốc Tuấn": "a resolute, deep-voiced Vietnamese general in his fifties, northern accent",
    "Trần Hưng Đạo": "a resolute, deep-voiced Vietnamese general in his fifties, northern accent",
    "Trần Nhân Tông": "a composed young Vietnamese king in his thirties, northern accent",
    "Quang Trung": "a powerful, commanding Vietnamese commander in his late thirties",
    "Nguyễn Huệ": "a powerful, commanding Vietnamese commander in his late thirties",
}
NHAN_VAT_DAN = {"Nhật Minh", "Hân Hân"}

# âm thanh hiện trường theo từ khoá trong mô tả cảnh
AM = [
    (r"sông|nước|thuyền|cọc|bến|đò", "flowing river water, lapping waves against wooden hulls, oars"),
    (r"biển|vịnh|đảo|sóng", "sea waves, wind over open water, gulls far away"),
    (r"lửa|cháy|đốt|khói", "roaring and crackling fire, burning wood popping, smoke wind"),
    (r"trận|giao chiến|tấn công|chiến đấu|phản công|xung trận", "distant battle shouts, war drums, clashing weapons (no gore)"),
    (r"ngựa|kỵ binh", "horse hooves and neighing, armour rattling"),
    (r"cung điện|triều đình|điện|ngai", "quiet palace hall ambience, soft footsteps, rustling silk robes"),
    (r"vắng|bỏ trống|trống không", "eerie silence of an abandoned city, wind through empty streets, a loose shutter creaking"),
    (r"(kinh thành|thành phố|phố|chợ)(?!.*(vắng|trống))", "town ambience, distant crowd murmur"),
    (r"va vào|vỡ|đắm|mắc kẹt|nghiêng", "heavy wooden hulls cracking and splintering, creaking timbers, big splashes"),
    (r"đóng cọc|đóng những", "wooden mallets hammering stakes into the riverbed, workers' short calls"),
    (r"bắt sống|giải lên|trói", "footsteps in mud, rope creaking, low murmur of soldiers"),
    (r"rừng|lau sậy|cỏ|ven sông", "wind in reeds and leaves, birds, insects"),
    (r"hoàng hôn|bình minh|sáng sớm", "calm morning/evening air, soft birdsong"),
    (r"di tích|tượng|đài", "gentle outdoor ambience at a memorial site, light breeze, faint birds"),
    (r"mưa", "rain"),
]


def am_thanh(text):
    out = [s for pat, s in AM if re.search(pat, text, re.I)]
    return out or ["natural outdoor ambience matching the scene"]


def tren_hinh(sc):
    """Những người nói có mặt trên hình (nhân vật dẫn chuyện chỉ tính khi cảnh dẫn chuyện/du hành)."""
    lop = sc.get("lop")
    if lop in ("dan_chuyen",):
        return True
    return False


def phieu(spec, sc):
    ma = spec["ma"]; so = int(sc["so"])
    anh = os.path.join("assets/episodes", ma, f"canh-{so:02d}.jpg")
    hinh = sc.get("hinh", "")
    loi = sc.get("loi", [])
    noi_tren_hinh, loi_dan = [], []
    for ln in loi:
        ai, vi = ln[0], ln[1]
        if ai in NHAN_VAT_DAN and sc.get("lop") != "dan_chuyen":
            loi_dan.append(vi)                       # lời dẫn ngoài hình -> hệ thống đọc
        else:
            noi_tren_hinh.append((ai, vi))
    dong = []
    dong.append("Create a 10-second 16:9 landscape video. Use the attached image as the exact FIRST FRAME and keep its "
                "hand-drawn storybook illustration style, line work, warm colour palette, lighting, character designs, "
                "costumes and composition throughout (no style change, no photorealism, no new main characters).")
    dong.append(f"What happens (Vietnamese history, {spec.get('nguon', {}).get('bai', '')}): {hinh}.")
    if noi_tren_hinh:
        dong.append("Dialogue - spoken in natural Vietnamese, word for word exactly as written, with accurate lip sync, "
                    "by the character on screen:")
        for ai, vi in noi_tren_hinh:
            dong.append(f'  {ai} ({GIONG.get(ai) or GIONG_RIENG.get(ai, GIONG_MAC_DINH)}): "{vi}"')
    else:
        dong.append("No one speaks on screen (the narration is added later) - characters act and move naturally, "
                    "mouths closed or only reacting, no talking to camera.")
    if loi_dan:
        dong.append("Pace the action so it illustrates this narration that will play over it (do NOT speak it): "
                    + " ".join(f'"{x}"' for x in loi_dan))
    dong.append("Sound design (important, detailed and realistic, well balanced): " + "; ".join(am_thanh(hinh))
                + ". No background music.")
    dong.append("Quality: sharp, highest resolution, smooth natural motion of people, water, fire, smoke and cloth; "
                "steady cinematic camera (slow push-in or gentle pan); clothing, weapons, boats and buildings accurate to the "
                "period shown in the image; maps if any must show Vietnam with Hoàng Sa and Trường Sa. "
                "No text, no captions, no subtitles, no logos, no blood or gore, nothing frightening for 12-year-old students.")
    hd = bool(re.search(r"trận|cháy|lửa|tấn công|va vào|thuyền|ngựa|kéo|đóng cọc|phục kích|bắt", hinh))
    return {"ma": ma, "canh": so, "lop": sc.get("lop"), "anh": anh, "co_anh": os.path.exists(os.path.join(ROOT, anh)),
            "uu_tien": 0 if hd else 1, "noi_tren_hinh": bool(noi_tren_hinh), "loi_nhac": "\n".join(dong),
            "da_co_clip": os.path.exists(os.path.join(ROOT, "assets/episodes", ma, f"canh-{so:02d}.mp4"))}


def main(mas):
    os.makedirs(os.path.join(ROOT, "data/gemini/hang_doi"), exist_ok=True)
    for ma in mas:
        spec = json.load(open(os.path.join(ROOT, "data/scripts", f"{ma}.json")))
        spec.setdefault("ma", ma)
        ds = [phieu(spec, sc) for sc in spec["canh"] if sc.get("hinh")]
        ds.sort(key=lambda p: (p["da_co_clip"], p["uu_tien"], p["canh"]))
        out = os.path.join(ROOT, "data/gemini/hang_doi", f"{ma}.json")
        json.dump(ds, open(out, "w"), ensure_ascii=False, indent=1)
        print(ma, len(ds), "cảnh;", sum(not p["da_co_clip"] for p in ds), "chưa có clip ->", os.path.relpath(out, ROOT))


if __name__ == "__main__":
    main(sys.argv[1:] or ["L7-B14-04"])
