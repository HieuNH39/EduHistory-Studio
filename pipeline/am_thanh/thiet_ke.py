"""Tự thiết kế âm thanh cho từng cảnh của một tập.

Nguồn quyết định (ưu tiên giảm dần):
 1. Trường tuỳ chọn "am_thanh" của cảnh:
    - dạng chuỗi (kịch bản đã có, vd "sóng vỗ nhẹ, chim, tiếng máy thuyền xa") → coi là gợi ý của người viết, trọng số cao nhất;
    - dạng đối tượng → điều khiển trực tiếp:
      {"nen": ["song", "gio"], "them_nen": [...], "su_kien": [{"t": 2.5, "loai": "trong_hoi", "muc": -18, "kieu": "don"}],
       "muc": 1.0 (hệ số cả cảnh), "tat": true (tắt hết âm mô phỏng của cảnh)}
 2. Mô tả hình "hinh" của cảnh, 3. lời thoại của cảnh (trọng số thấp – lời có thể nhắc chuyện không có trên hình).
 4. Sa bàn (lop = sa_ban): đọc tệp pipeline/maps/specs/<sa_ban>.json, lấy đúng mốc 'tu'/'den' của từng bước hoạt hình
    (mũi tên quân, thuyền, cọc, lửa, mắc cọc, sao, băng chữ…) → tiếng đặt đúng lúc hình chuyển động.
 5. Thẻ (trục thời gian, ghi nhớ, câu hỏi), cảnh chuyển trống đồng, mở/kết logo → tiếng giao diện đúng mốc hiện chữ.

Kết quả: kế hoạch gồm các đoạn nền (bed), sự kiện, điểm xuyết, và ghi chú tiếng Việt cho từng cảnh."""
import os, re, json, zlib, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SPECS = os.path.join(ROOT, "pipeline/maps/specs")
XFADE = 0.5

# mức nền (LUFS của riêng lớp nền ở bản cuối, khi đang có lời đọc)
MUC_NEN = {
    "gio": -28, "song": -24, "bien": -24, "mua": -26, "rung": -26, "dong_que": -27, "con_trung_dem": -27,
    "lua_chay": -25, "chien_tran_xa": -24, "chien_tran_hien_dai": -25, "dam_dong": -26, "cho": -25,
    "cung_dien": -28, "phong": -30, "trai_quan": -26, "hang_dong": -26, "pho": -28, "nha_may": -26, "bien_tau": -24,
}
HA_THEO_THU_TU = [0, -3, -5]          # nền chính / phụ / thứ ba
HA_SA_BAN = -5                         # sa bàn: nền lùi lại, nhường chỗ cho tiếng sự kiện (quân cờ, trống, thuyền…)
HA_CO_TIENG_CLIP = -7                  # clip Kling đã có tiếng hiện trường thật → nền tổng hợp chỉ bổ sung
HA_TU_LIEU = -4

# ------------------------------------------------------------------ từ khoá → nền
def _w(*ws): return [w for w in ws]
TU_KHOA_NEN = [
    # (mẫu regex, nền, trọng số)
    (r"sông|dòng sông|bờ sông|khúc sông|cửa sông|con rạch|rạch|kênh|lạch|bến sông|bến|thu[ỷy] chiến|th[ủu]y chiến", "song", 1.0),
    (r"nước triều|triều rút|nước rút|nước lên|lau sậy|dừa nước|đầm lầy|đầm|ao làng|mặt hồ|ven hồ|bờ hồ|hồ nước|hồ gươm|hồ hoàn kiếm|suối|mái chèo|chèo thuyền|bè|ven sông", "song", 0.8),
    (r"thuyền", "song", 0.5),
    (r"biển|bãi biển|vịnh|hải đảo|đại dương|eo biển|hải cảng|ven biển|hải trình|hạm đội|hải quân|ra khơi|cửa biển", "bien", 1.0),
    (r"sóng", "bien", 0.5), (r"sóng", "song", 0.4), (r"đảo", "bien", 0.5), (r"cảng", "bien", 0.6),
    (r"thuyền buồm|tàu buồm|vượt đại dương|đoàn tàu", "bien_tau", 1.0),
    (r"gió|núi|đèo|cao nguyên|thảo nguyên|sa mạc|cờ bay|heo may|đồi|gò cao|trên gò|đỉnh núi|vách đá", "gio", 0.9),
    (r"bão", "gio", 0.8), (r"mưa|giông|mưa phùn|lũ lụt", "mua", 1.2), (r"bão", "mua", 0.6),
    (r"rừng|núi rừng|cây cối|rậm rạp|lũy tre|luỹ tre|tre|bụi cây|tán lá|tán cây|chim(?! lạc)", "rung", 1.0),
    (r"làng|xóm|đồng ruộng|ruộng|lúa|cánh đồng|nông thôn|quê|vườn|cày|gặt|công viên|di tích|khu di tích|sân trường", "dong_que", 0.9),
    (r"đêm|ban đêm|khuya|trăng|dế|đêm tĩnh", "con_trung_dem", 1.2), (r"côn trùng", "con_trung_dem", 0.7),
    (r"lửa|bốc cháy|đuốc|ánh đuốc|bếp lửa|lò|đốt|ho[ảa] công|h[ỏo]a công|lửa trại|bè lửa|cháy", "lua_chay", 1.0),
    (r"khói", "lua_chay", 0.5), (r"nến|đèn dầu", "lua_chay", 0.3),
    (r"trận|giao chiến|chiến đấu|xung trận|công thành|phản công|quyết chiến|giáp chiến|chiến trường|xung phong|tiến công|tấn công|chặn đánh|đánh úp|vây hãm|bao vây|khói lửa|trống trận", "chien_tran_xa", 1.0),
    (r"đám đông|nhân dân|quần chúng|mít tinh|biểu tình|lễ hội|tụ tập|dân chúng|người dân|đoàn người|hàng vạn|hàng nghìn người|reo hò|đón chào|nhạc hội", "dam_dong", 1.0),
    (r"xì xào|bàn tán|tranh cãi", "dam_dong", 0.7),
    (r"chợ|buôn bán|phố phường|thương nhân|thương cảng|thương điếm|hàng ho[áa]|phố cổ|phiên chợ|tấp nập|thuyền buôn", "cho", 1.1),
    (r"cung điện|cung đình|triều đình|chính điện|trong điện|điện kính thiên|điện thái hoà|ngai vàng|ngai|bá quan|thiết triều|hoàng cung|nội cung", "cung_dien", 1.0),
    (r"lăng|đền(?! bù)|chùa|miếu|hoàng thành|quan lại", "cung_dien", 0.5),      # có thể là cảnh ngoài sân → cần thêm dấu hiệu
    (r"lều|trong lều|căn phòng|phòng|trong nhà|ngôi nhà|lớp học|thư viện|bảo tàng|hầm", "phong", 0.9),
    (r"doanh trại|trại quân|đại bản doanh|đóng quân|luyện quân|tập trận|binh khí|rèn vũ khí|lều chỉ huy|trại", "trai_quan", 1.0),
    (r"hang động|hang đá|hang|mái đá|người tối cổ|người nguyên th[ủu]y|người nguyên thuỷ|thời đá|đồ đá", "hang_dong", 1.1),
    (r"thành phố|đường phố|xe cộ|ô tô|xe máy|phố xá", "pho", 1.0), (r"phố", "pho", 0.4),
    (r"nhà máy|công xưởng|xưởng|máy móc|máy hơi nước|dệt|đầu máy|đường sắt|công nghiệp", "nha_may", 1.0),
]
NGOAI_TROI = {"gio", "song", "bien", "mua", "rung", "dong_que", "con_trung_dem", "chien_tran_xa", "pho", "bien_tau"}
TRONG_NHA = {"cung_dien", "phong", "hang_dong", "nha_may"}

# ------------------------------------------------------------------ từ khoá → sự kiện (cảnh hình minh hoạ)
TU_KHOA_SU_KIEN = [
    # (mẫu, loại, tham số, mô tả)
    (r"trống lệnh|trống dồn|dồn dập", "trong_hoi", {"kieu": "don"}, "trống dồn"),
    (r"trống hành quân|trống trầm", "trong_hoi", {"kieu": "hanh_quan", "xa": 0.6}, "trống hành quân"),
    (r"trống trận|trống thúc|tiếng trống|trống làng|trống gỗ", "trong_hoi", {"kieu": "thuc"}, "trống trận"),
    (r"trống đồng", "trong_dong", {}, "trống đồng"),
    (r"cồng|chiêng", "cong", {}, "cồng chiêng"),
    (r"tù và", "tu_va", {}, "tù và"),
    (r"chuông chùa|tiếng chuông|chuông đồng|chuông", "chuong_chua", {}, "chuông"),
    (r"kỵ binh|kị binh", "vo_ngua", {"so_ngua": 6}, "kỵ binh phi"),
    (r"vó ngựa|ngựa phi|cưỡi ngựa|tiếng ngựa|ngựa", "vo_ngua", {"so_ngua": 2}, "vó ngựa"),
    (r"voi chiến|voi rống|voi", "buoc_nang", {}, "bước voi"),
    (r"mái chèo gấp|chèo gấp|chèo nhanh", "mai_cheo", {"gap": True}, "mái chèo gấp"),
    (r"mái chèo|chèo thuyền|chèo đò|bơi chèo", "mai_cheo", {}, "mái chèo"),
    (r"thuyền chiến|chiến thuyền|thuyền lớn|đoàn thuyền|tàu chiến|thuyền giặc", "nuoc_re", {}, "thuyền lớn rẽ nước"),
    (r"đóng cọc|đóng những hàng cọc|cọc gỗ", "dong_coc", {}, "đóng cọc"),
    (r"va vào bãi cọc|mắc kẹt|vỡ|đắm|gãy|chìm", "go_nut", {}, "gỗ vỡ"),
    (r"đắm|chìm|rơi xuống nước|nhảy xuống", "te_nuoc", {}, "nước bắn"),
    (r"mũi tên|cung tên|bắn tên|mưa tên|cung nỏ|nỏ thần|bắn nỏ", "mui_ten", {}, "loạt tên"),
    (r"gươm|thanh kiếm|vung kiếm|đao kiếm|gươm giáo|giáo mác|mũi giáo|ngọn giáo|cây giáo|giáo dài|đại đao|thanh đao|giáp chiến|đấu kiếm|giáp lá cà", "guom", {}, "gươm giáo (nhẹ)"),
    (r"đại bác|súng thần công|pháo kích|tiếng pháo|pháo binh|nã pháo|trận địa pháo|khẩu pháo|pháo(?! hoa| đài| hiệu)", "phao", {}, "pháo xa"),
    (r"bom|nổ tung|tiếng nổ|ném bom|đánh bom|bom nổ", "no", {}, "tiếng nổ xa"),
    (r"tiếng súng|súng nổ|bắn súng", "sung_xa", {}, "súng xa"),
    (r"reo hò|reo mừng|hoan hô|mừng chiến thắng|ăn mừng|reo vang", "ho_reo", {"kieu": "reo"}, "reo hò"),
    (r"tiếng hô|hô vang|hô xung trận|hò reo|đồng thanh hô|hô to|hô lớn", "ho_reo", {"kieu": "xung_tran"}, "tiếng hô"),
    (r"lửa bùng|bùng cháy|bốc cháy|phóng ho[ảa]|bè lửa|thả trôi.*cháy|ho[ảa] công", "lua_bung", {}, "lửa bùng"),
    (r"cuốc xẻng|đắp lu[ỹy]|đắp đê|đào hào|đắp thành|đào đắp", "dao_dat", {}, "đào đắp"),
    (r"kéo đá|khối đá|xếp đá", "da_keo", {}, "kéo đá"),
    (r"cờ bay|phần phật|cờ xí|lá cờ", "co_bay", {}, "cờ bay"),
    (r"gió cuốn|cơn gió|gió thổi mạnh", "gio_cuon", {}, "gió cuốn"),
    (r"sấm|giông", "sam", {}, "sấm xa"),
    (r"còi tàu", "coi_tau", {}, "còi tàu"),
    (r"đại quân|đoàn quân|hành quân|tiến quân|kéo quân|bước chân|bước quân|tiến về phía", "quan_tien", {}, "đoàn quân đi"),
    (r"rút chạy|tháo chạy|bỏ chạy|tan tác|quay đầu rút", "rut_chay", {}, "rút chạy"),
    (r"binh khí|leng keng", "leng_keng", {}, "khí giới"),
]
CHIEN_TRAN = {"trong_hoi", "mui_ten", "guom", "phao", "no", "sung_xa", "ho_reo", "quan_tien", "rut_chay", "vo_ngua",
              "buoc_nang", "lua_bung", "go_nut", "te_nuoc", "dong_coc", "nuoc_re"}
KEO_DAI = {"mai_cheo", "quan_tien", "vo_ngua", "co_bay", "nuoc_re", "dao_dat", "buoc_nang", "sung_xa"}
LENH_TAN_CONG = re.compile(r"^\s*(Đánh|Xung phong|Tiến lên|Giết giặc|Phóng ho[ảa]|Bắn|Tấn công)[^\w]*!", re.I)
SA_BAN_HIEN_DAI = {"dien-bien-phu", "xuan-1975", "ctgt2-chau-a", "ctgt2-chau-au", "ctgt2-giai-doan-1", "chien-tranh-lanh",
                   "tong-khoi-nghia-1945", "dong-nam-a"}


def _rng(*keys):
    return np.random.default_rng(zlib.crc32("|".join(map(str, keys)).encode()))


def _chuan(s):
    return (s or "").lower().replace("thủy", "thuỷ").replace("hỏa", "hoả").replace("hòa", "hoà")


def _khop(pat, text):
    return re.search(r"(?<!\w)(?:" + pat + r")(?!\w)", text) is not None


# ------------------------------------------------------------------ thời kì (để chặn tiếng pháo/nổ sai thời đại)
def nam_tap(spec):
    """Ước lượng năm trung vị mà tập nói tới (âm = TCN)."""
    texts = [spec.get("ten_tap", ""), json.dumps(spec.get("nguon", {}), ensure_ascii=False)]
    for sc in spec.get("canh", []):
        texts += [ln[1] for ln in sc.get("loi", []) if len(ln) > 1] + [sc.get("chu", "") or ""]
        for m in sc.get("moc", []) or []: texts.append(m[0] if isinstance(m, list) else str(m))
    ys = []
    for t in texts:
        for m in re.finditer(r"(?<![\d–-])(\d{3,4})(?!\d)(\s*TCN)?", t):
            y = int(m.group(1))
            if m.group(2): ys.append(-y)
            elif 40 <= y <= 2030: ys.append(y)
    if ys: return float(np.median(ys))
    lop = str(spec.get("id", ""))[:2]
    return {"L6": -500, "L7": 1300, "L8": 1750, "L9": 1950}.get(lop, 1500)


def _cho_phep(loai, nam):
    if loai == "phao": return nam >= 1800
    if loai in ("no", "sung_xa", "coi_tau"): return nam >= 1858
    return True


# ------------------------------------------------------------------ kế hoạch
class KeHoach:
    def __init__(self):
        self.nen = []        # {"ten", "t0", "t1", "muc", "canh"}
        self.su_kien = []    # {"t", "loai", "kw", "muc", "canh", "mo_ta"}
        self.diem = []       # {"ten", "t0", "t1", "muc", "canh", "ban_ngay", "co_nuoc"}
        self.ghi_chu = []

    def them_nen(self, ten, t0, t1, muc, canh):
        if t1 - t0 > 0.2: self.nen.append(dict(ten=ten, t0=t0, t1=t1, muc=muc, canh=canh))

    def them(self, t, loai, muc=None, canh=None, mo_ta=None, **kw):
        self.su_kien.append(dict(t=float(t), loai=loai, kw=kw, muc=muc, canh=canh, mo_ta=mo_ta or loai))


def _diem_nen(texts, tran_loi=0.7):
    """texts: [(văn bản, trọng số, là_lời_thoại)] → {nền: điểm}. Lời thoại góp tối đa 'tran_loi' điểm cho mỗi nền
    (ngưỡng chọn là 1.4) → lời thoại chỉ củng cố, không tự quyết một nền (vd cảnh hôm nay nhắc tới 'trận' cũ)."""
    d = {}; tu_loi = {}
    for text, w, la_loi in texts:
        t = _chuan(text)
        for pat, ten, tw in TU_KHOA_NEN:
            if _khop(pat, t):
                if la_loi: tu_loi[ten] = tu_loi.get(ten, 0) + w * tw
                else: d[ten] = d.get(ten, 0) + w * tw
    for ten, v in tu_loi.items(): d[ten] = d.get(ten, 0) + min(v, tran_loi)
    return d


def _chon_nen(diem, nam, lop, ban_dem):
    if nam >= 1900 and "chien_tran_xa" in diem:
        diem["chien_tran_hien_dai"] = diem.pop("chien_tran_xa")
    if ban_dem and "rung" in diem: diem["con_trung_dem"] = diem.get("con_trung_dem", 0) + diem["rung"] * 0.5
    if ban_dem and "dong_que" in diem: diem["con_trung_dem"] = diem.get("con_trung_dem", 0) + diem.pop("dong_que")
    if "song" in diem and "bien" in diem and diem["bien"] <= diem["song"]:   # 'sóng' ở cảnh sông ≠ biển
        diem.pop("bien")
    trong_nha = max([diem.get(k, 0) for k in TRONG_NHA] + [0])
    if trong_nha >= 1.5:   # cảnh trong nhà: bỏ bớt nền ngoài trời yếu
        diem = {k: v for k, v in diem.items() if k in TRONG_NHA or v >= trong_nha * 0.9 or k in ("lua_chay", "dam_dong", "chien_tran_xa", "chien_tran_hien_dai")}
    chon = [k for k, v in sorted(diem.items(), key=lambda kv: -kv[1]) if v >= 1.4][:3]
    return chon


def _khe_lang(sc, length):
    """Các khoảng không có lời trong cảnh (giây, tính từ đầu cảnh) – nơi đặt tiếng sự kiện cho rõ."""
    b = [(a + 0.15, c + 0.15) for a, c in sc.get("bounds", [])]
    if not b: return [(0.0, length)]
    gaps = []; cur = 0.0
    for a, c in b:
        if a - cur > 0.22: gaps.append((cur, a))
        cur = max(cur, c)
    if length - cur > 0.22: gaps.append((cur, length))
    return gaps


def _thoi_diem_dat(sc, length, uu_tien=0.5, toi_thieu=0.25):
    """Chọn thời điểm đặt một tiếng: khe lặng đầu tiên đủ dài sau 'uu_tien' giây; không có thì 'uu_tien'."""
    for a, c in _khe_lang(sc, length):
        if c - max(a, uu_tien) >= toi_thieu: return max(a, uu_tien) + 0.05
    return min(uu_tien, max(length - 1.0, 0.1))


def _x_pan(spec, pts):
    x0, _, x1, _ = spec.get("khung", [0, 0, 1000, 1000])
    cx = (x0 + x1) / 2; hw = (x1 - x0) / 2
    return [float(np.clip((p[0] - cx) / hw * 0.85, -0.9, 0.9)) for p in (pts[0], pts[-1])]


# ------------------------------------------------------------------ sa bàn
def _sa_ban(kh, spec_id, sc, t0, length, nam, so):
    ten = sc.get("sa_ban"); pha = sc.get("pha")
    path = os.path.join(SPECS, f"{ten}.json")
    if not os.path.exists(path): return ["(không thấy tệp sa bàn)"]
    S = json.load(open(path)); notes = []
    hien_dai = ten in SA_BAN_HIEN_DAI or nam >= 1900
    n = int(round(length * 30)); L = (n - 1) / 30.0              # u = i/(n-1) → t = u·L (khớp saban*.frames)
    T = lambda u: t0 + float(u) * L
    rng = _rng(spec_id, so, "sa_ban")

    if S.get("loai") == "the_gioi":           # hành trình trên biển
        ph = S["pha"][pha]
        kh.them_nen("bien_tau", t0, t0 + length, MUC_NEN["bien_tau"] + HA_SA_BAN, so)
        kh.them_nen("gio", t0, t0 + length, MUC_NEN["gio"] + HA_SA_BAN - 3, so)
        if ph.get("moc_chu"): kh.them(t0 + 0.1, "moc_hien", canh=so, mo_ta="ô mốc thời gian")
        # thời điểm tàu đi qua từng điểm mốc: L(u) = L0 + (L1-L0)·min(1, ease(u)/ve_xong)
        R = np.array(S["duong"], float)
        d = np.r_[0, np.cumsum(np.hypot(np.diff(R[:, 0]) * np.cos(np.radians(R[:-1, 1])), np.diff(R[:, 1])))]
        L0, L1 = d[ph["tu_moc"]], d[ph["den_moc"]]; vx = ph.get("ve_xong", .9)
        uu = np.linspace(0, 1, 400); ee = uu * uu * (3 - 2 * uu); Lc = L0 + (L1 - L0) * np.minimum(1, ee / vx)
        k = 0
        for m in S.get("moc", []):
            i = m["chi_so"]
            if ph["tu_moc"] < i <= ph["den_moc"] and i not in ph.get("an_moc", []):
                u = uu[min(np.searchsorted(Lc, d[i] - 1e-6), len(uu) - 1)]
                kh.them(T(u), "tich", canh=so, bac=k % 6, mo_ta="tàu tới mốc"); k += 1
        for j in range(max(1, int(length / 4))):
            kh.them(t0 + rng.uniform(0.5, max(length - 1.5, 0.6)), "cot_ket", canh=so, mo_ta="thân tàu cót két")
        notes.append(f"hành trình biển: sóng + gió, {k} tiếng mốc, thân tàu cót két")
        return notes

    if S.get("phien_ban") != 2:               # sa bàn bản 1 (Rạch Gầm – Xoài Mút), mốc viết cứng trong saban.py
        return _sa_ban_v1(kh, S, pha, t0, length, L, T, so, rng)

    ph = S["pha"][pha]; objs = S["doi_tuong"]
    co_nuoc = bool(S.get("song") or S.get("vung_nuoc") or S.get("ho") or S.get("nen_bien"))
    loai_hien = {objs[o]["loai"] for o in ph.get("hien", []) if o in objs}
    loai_buoc = {objs[b["id"]]["loai"] for b in ph.get("buoc", []) if b["id"] in objs}
    co_thuyen = bool({"thuyen_ta", "thuyen_dich"} & (loai_hien | loai_buoc))
    if co_nuoc and (co_thuyen or "coc" in (loai_hien | loai_buoc)):
        kh.them_nen("song", t0, t0 + length, MUC_NEN["song"] + HA_SA_BAN, so); notes.append("nền: sông nước (nhẹ)")
    elif S.get("nen_bien"):
        kh.them_nen("bien", t0, t0 + length, MUC_NEN["bien"] + HA_SA_BAN - 2, so); notes.append("nền: biển (nhẹ)")
    kh.them_nen("gio", t0, t0 + length, MUC_NEN["gio"] + HA_SA_BAN, so)
    if "lua" in loai_hien:
        kh.them_nen("lua_chay", t0, t0 + length, MUC_NEN["lua_chay"] + HA_SA_BAN, so); notes.append("lửa đang cháy")

    if ph.get("mo_dau"):
        kh.them(t0 + 0.02, "giay", canh=so, mo_ta="trải sa bàn")
        kh.them(t0 + 0.35, "cong", canh=so, muc=-22, xa=0.5, mo_ta="cồng mở sa bàn")
    tan_cong = [b for b in ph.get("buoc", []) if objs.get(b["id"], {}).get("loai") in ("mui_ten_ta", "mui_ten_dich", "vong", "chan_danh")]
    if tan_cong and not ph.get("mo_dau"):
        kh.them(t0 + 0.12, "trong_tran", canh=so, muc=-21, luc=0.8, xa=0.5, mo_ta="trống mở pha")
        kh.them(t0 + 0.62, "trong_tran", canh=so, muc=-20, luc=1.0, xa=0.5, mo_ta="trống mở pha")
    # chiến trận vọng xa từ lúc mũi tên tấn công đầu tiên chạy
    if tan_cong or ph.get("mac_ket") or "lua" in loai_buoc:
        u0 = min([b["tu"] for b in tan_cong] + [v[0] for v in ph.get("mac_ket", {}).values()] +
                 [b["tu"] for b in ph.get("buoc", []) if objs.get(b["id"], {}).get("loai") == "lua"] + [1.0])
        bed = "chien_tran_hien_dai" if hien_dai else "chien_tran_xa"
        kh.them_nen(bed, T(u0), t0 + length, MUC_NEN[bed] + HA_SA_BAN, so); notes.append(f"chiến trận vọng xa từ {T(u0) - t0:.1f}s")

    dem = {}
    def them_sk(u, loai, mo_ta, **kw):
        dem[mo_ta] = dem.get(mo_ta, 0) + 1
        kh.them(T(u), loai, canh=so, mo_ta=mo_ta, **kw)

    for b in ph.get("buoc", []):
        o = objs.get(b["id"]);
        if not o: continue
        typ = o["loai"]; tu, den = b["tu"], b["den"]; dai = max((den - tu) * L, 0.4)
        if b.get("hieu_ung") == "mat":
            if hien_dai: them_sk(tu, "no", "đồn bị phá (nổ xa)", xa=0.7)
            else: them_sk(tu, "go_nut", "đồn bị phá (gỗ vỡ)"); them_sk(tu + 0.02, "ho_reo", "tiếng hô", kieu="hieu_lenh", so=10, muc=-23)
            continue
        if typ in ("mui_ten_ta", "mui_ten_dich"):
            p0, p1 = _x_pan(S, o["diem"])
            if "lua" in b["id"]:
                them_sk(tu, "lua_bung", "bè lửa bùng cháy"); them_sk(tu, "nuoc_re", "bè lửa trôi", dai=dai, p0=p0, p1=p1, muc=-24)
            else:
                ta = typ == "mui_ten_ta"
                them_sk(tu, "quan_tien", "quân ta tiến công" if ta else "quân địch tiến", dai=dai, manh=1.0 if ta else 0.6,
                        p0=p0, p1=p1, muc=-19 if ta else -22)
        elif typ in ("rut_chay", "rut_lui"):
            p0, p1 = _x_pan(S, o["diem"]); them_sk(tu, "rut_chay", "rút chạy", dai=dai, p0=p0, p1=p1)
        elif typ == "thuyen_ta":
            them_sk(tu, "mai_cheo", "thuyền ta chèo", dai=dai, gap=True, so_cheo=3, muc=-23)
        elif typ == "thuyen_dich":
            p0, p1 = _x_pan(S, o["diem"])
            them_sk(tu, "nuoc_re", "đoàn thuyền địch rẽ nước", dai=dai, p0=p0, p1=p1, muc=-22)
            for j in range(max(1, int(dai / 3))): them_sk(tu + (j + 0.5) * (den - tu) / max(1, int(dai / 3)), "cot_ket", "thân thuyền cót két", muc=-23)
        elif typ == "coc":
            k = int(min(6, max(2, dai / 0.62))); them_sk(tu, "dong_coc", "đóng cọc", so=k)
        elif typ in ("mai_phuc", "don_ta", "cu_diem", "phong_tuyen", "san_bay", "don_dich"):
            them_sk(tu, "quan_co", "đặt kí hiệu lên sa bàn")
        elif typ == "sao":
            them_sk(tu, "lap_lanh", "sao chiến thắng"); them_sk(tu + 0.01, "cong", "cồng mừng thắng", muc=-21)
        elif typ == "vong":
            them_sk(tu, "trong_hoi", "trống vây", kieu="don", dai=dai, muc=-20)
        elif typ in ("tuong", "tran_tuyen"):
            them_sk(tu, "dao_dat", "đắp phòng tuyến", dai=dai, muc=-24)
        elif typ == "chan_danh":
            them_sk(tu, "trong_tran", "chặn đánh", luc=1.0)
            if not hien_dai: them_sk(tu + 0.1 / max(L, 1), "guom", "gươm giáo (nhẹ)", so=2)
        elif typ == "thanh_sang":
            them_sk(tu, "lap_lanh", "thành sáng lên", muc=-25)
        elif typ == "lua":
            them_sk(tu, "lua_bung", "lửa bùng")
            kh.them_nen("lua_chay", T(tu), t0 + length, MUC_NEN["lua_chay"] + HA_SA_BAN + 2, so)
    for oid, (a, c) in ph.get("mac_ket", {}).items():
        if c - a < 0.05: continue
        them_sk(a + 0.15 * (c - a), "go_nut", "thuyền va cọc – gỗ vỡ")
        them_sk(a + 0.35 * (c - a), "cot_ket", "thân thuyền cót két")
        them_sk(a + 0.5 * (c - a), "te_nuoc", "nước bắn", to=1.2)
        them_sk(a + 0.75 * (c - a), "go_nut", "thuyền va cọc – gỗ vỡ", to=0.7, muc=-21)
    for m in ph.get("moc", []): them_sk(m["tu"], "moc_hien", "ô mốc thời gian")
    if ph.get("bang"):
        bg = ph["bang"]; them_sk(bg["tu"], "cong", "cồng – băng chữ kết quả", muc=-19)
        if re.search(r"thắng|giải phóng|thành công|bắt sống", bg.get("chu", ""), re.I):
            them_sk(bg["tu"] + 0.4 / max(L, 1), "ho_reo", "reo mừng chiến thắng", kieu="reo", muc=-21)
    notes += [f"{k}×{v}" if v > 1 else k for k, v in dem.items()]
    return notes


def _sa_ban_v1(kh, S, pha, t0, length, L, T, so, rng):
    """Mốc theo saban.py (bản 1, trận Rạch Gầm – Xoài Mút)."""
    notes = []
    kh.them_nen("song", t0, t0 + length, MUC_NEN["song"] + HA_SA_BAN, so)
    kh.them_nen("gio", t0, t0 + length, MUC_NEN["gio"] + HA_SA_BAN, so)
    def sk(u, loai, mo_ta, **kw): kh.them(T(u), loai, canh=so, mo_ta=mo_ta, **kw); notes.append(mo_ta)
    if pha == "dia_the":
        sk(0.0, "giay", "trải sa bàn"); sk(0.03, "cong", "cồng mở sa bàn", muc=-22, xa=0.5)
        sk(0.16, "vut", "vạch độ dài khúc sông", dai=0.9, muc=-28); sk(0.36, "vut", "vạch bề rộng", dai=0.8, muc=-28, huong=-1)
        sk(0.50, "lap_lanh", "cù lao Thới Sơn sáng lên", muc=-26); sk(0.64, "tich", "kênh rạch nổi bật", bac=2)
    elif pha == "mai_phuc":
        for i in range(len(S.get("mai_phuc", []))):
            kh.them(T(.08 + i * .07), "quan_co", canh=so, mo_ta="đặt kí hiệu mai phục")
        notes.append(f"đặt kí hiệu mai phục×{len(S.get('mai_phuc', []))}")
        kh.them_nen("con_trung_dem", t0, t0 + length, MUC_NEN["con_trung_dem"] - 6, so)
    elif pha == "nhu_dich":
        sk(0.05, "nuoc_re", "đoàn thuyền Xiêm xuôi dòng", dai=0.85 * L, p0=-0.6, p1=0.4, muc=-22)
        for j in range(3): kh.them(T(0.15 + j * 0.25), "cot_ket", canh=so, muc=-23, mo_ta="thân thuyền cót két")
        for i in range(len(S.get("xiem", []))):
            kh.them(T(0.05 + 0.85 * min(1, i * .22 / 0.85)), "quan_tien", canh=so, dai=0.3 * L, manh=0.5, muc=-24, mo_ta="quân Xiêm tiến")
    elif pha == "ket_qua":
        sk(0.02, "trong_hoi", "trống lệnh dồn", kieu="don", dai=2.5, muc=-18)
        sk(0.05, "ho_reo", "tiếng hô xung trận", kieu="xung_tran", muc=-21)
        sk(0.04, "quan_tien", "thuyền và quân Tây Sơn đổ ra", dai=0.3 * L, manh=1.0, muc=-20)
        for j in range(0, 9, 3): kh.them(T(.25 + j * .03), "lua_bung", canh=so, muc=-20, mo_ta="thuyền Xiêm bốc cháy")
        sk(0.35, "go_nut", "thuyền vỡ"); sk(0.45, "te_nuoc", "nước bắn")
        kh.them_nen("lua_chay", T(0.27), t0 + length, MUC_NEN["lua_chay"] + HA_SA_BAN + 2, so)
        kh.them_nen("chien_tran_xa", T(0.04), t0 + length, MUC_NEN["chien_tran_xa"] + HA_SA_BAN, so)
        sk(0.62, "cong", "cồng – băng chữ thắng lợi", muc=-19); sk(0.66, "ho_reo", "reo mừng chiến thắng", kieu="reo", muc=-21)
    return notes


# ------------------------------------------------------------------ cảnh minh hoạ (ảnh / clip)
def _canh_hinh(kh, spec_id, sc, t0, length, nam, so, co_tieng_clip):
    at = sc.get("am_thanh"); ghi = []
    goi_y = at if isinstance(at, str) else ""
    texts = [(goi_y, 3.0, False), (sc.get("hinh", ""), 2.0, False)] + [(ln[1], 0.7, True) for ln in sc.get("loi", []) if len(ln) > 1]
    tat_ca = _chuan(" ".join(t for t, _, _ in texts))
    hinh = _chuan(goi_y + " " + (sc.get("hinh") or ""))
    ban_dem = _khop(r"đêm|ban đêm|khuya|trăng|đêm tĩnh", hinh)
    diem = _diem_nen(texts)
    if isinstance(at, dict) and at.get("nen") is not None:
        chon = [x for x in at["nen"] if x in MUC_NEN]
    else:
        chon = _chon_nen(diem, nam, sc.get("lop"), ban_dem)
        if isinstance(at, dict): chon += [x for x in at.get("them_nen", []) if x in MUC_NEN and x not in chon]
        if not chon:   # mặc định: ngoài trời nhẹ (gió + đồng quê) hoặc phòng nếu là cảnh trong nhà
            if _khop(r"trong|bên trong", hinh): chon = ["phong"]
            elif ban_dem: chon = ["con_trung_dem"]
            elif sc.get("lop") in ("dan_chuyen", "du_hanh") or _khop(r"yên bình|thanh bình|êm đềm|hoàng hôn|bình minh", hinh): chon = ["dong_que", "gio"]
            else: chon = ["gio"]       # cảnh tái hiện không rõ bối cảnh: chỉ gió nhẹ (không chim hót giữa cảnh hành quân)
    ha = 0
    if co_tieng_clip: ha += HA_CO_TIENG_CLIP
    if sc.get("lop") == "tu_lieu": ha += HA_TU_LIEU
    if _khop(r"im lặng|tĩnh lặng|yên ả|yên tĩnh", hinh): ha -= 3
    for i, ten in enumerate(chon[:3]):
        kh.them_nen(ten, t0, t0 + length, MUC_NEN[ten] + HA_THEO_THU_TU[min(i, 2)] + ha, so)
        kh.diem.append(dict(ten=ten, t0=t0, t1=t0 + length, muc=MUC_NEN[ten] + HA_THEO_THU_TU[min(i, 2)] + ha, canh=so,
                            ban_ngay=not ban_dem, co_nuoc=any(x in chon for x in ("song", "bien"))))
    ghi.append("nền: " + ", ".join(chon[:3]) + (f" ({ha:+d} dB vì clip đã có tiếng)" if co_tieng_clip else ""))

    # sự kiện theo từ khoá (gợi ý + mô tả hình là chính; lời thoại chỉ xét các tiếng chắc chắn)
    if isinstance(at, dict) and at.get("tat"): return ghi
    da = set(); n_sk = 0
    hien_tai = sc.get("lop") == "dan_chuyen"      # cảnh hai bạn dẫn chuyện ở hiện tại (bảo tàng, tượng đài…)
    # lệnh tấn công trong lời thoại ("Đánh!") → trống dồn + tiếng hô ngay sau câu (thay cho trống/hô theo từ khoá)
    for (a, c), ln in zip(sc.get("bounds", []), sc.get("loi", [])):
        if LENH_TAN_CONG.match(ln[1]):
            kh.them(t0 + c + 0.2, "trong_hoi", canh=so, kieu="don", dai=2.4, muc=-18, mo_ta="trống lệnh sau hiệu lệnh")
            kh.them(t0 + c + 0.3, "ho_reo", canh=so, kieu="xung_tran", muc=-21, mo_ta="hô xung trận")
            ghi.append(f"hiệu lệnh “{ln[1].strip()}” → trống dồn + hô"); da |= {"trong_hoi", "ho_reo"}; n_sk += 1
            break
    for pat, loai, kw, mo_ta in TU_KHOA_SU_KIEN:
        if n_sk >= 3: break
        o_hinh = _khop(pat, hinh)
        o_loi = _khop(pat, tat_ca) and loai in ("trong_hoi", "cong", "mui_ten", "vo_ngua", "lua_bung", "dong_coc", "phao", "no", "tu_va")
        if hien_tai and loai in CHIEN_TRAN:   # hiện tại: tiếng chiến trận chỉ khi người viết ghi rõ trong gợi ý "am_thanh"
            o_hinh = _khop(pat, _chuan(goi_y)); o_loi = False
        if not (o_hinh or o_loi) or loai in da or not _cho_phep(loai, nam): continue
        if loai == "ho_reo" and "ho_reo" in da: continue
        if loai == "go_nut" and not _khop(r"thuyền|cọc|gỗ|cổng|thành", hinh): continue
        if loai == "te_nuoc" and not _khop(r"thuyền|sông|biển|nước", hinh): continue
        da.add(loai); n_sk += 1
        kw = dict(kw)
        if loai in KEO_DAI:
            n_dai = sum(1 for x in da if x in KEO_DAI)          # đã có bao nhiêu lớp kéo dài trong cảnh (kể cả lớp này)
            if n_dai > 2: da.discard(loai); n_sk -= 1; continue  # tối đa 2 lớp kéo dài/cảnh
            bat_dau = 0.3 + 0.8 * (n_dai - 1)                    # so le để không cùng dâng một lúc
            kw["dai"] = min(max(length - bat_dau - 0.7, 1.5), 12.0)
            kh.them(t0 + bat_dau, loai, canh=so, mo_ta=mo_ta, muc=(-24 if o_hinh else -26) - 2 * (n_dai - 1), **kw)
        else:
            t = _thoi_diem_dat(sc, length, uu_tien=0.4 + 0.6 * n_sk)
            muc = None if o_hinh else -24
            if loai in ("trong_hoi",) and "dai" not in kw: kw["dai"] = min(3.0, max(length - t - 0.5, 1.2))
            kh.them(t0 + t, loai, canh=so, mo_ta=mo_ta, muc=muc, **kw)
        ghi.append(mo_ta)
    if isinstance(at, dict):
        for e in at.get("su_kien", []):
            e = dict(e); t = float(e.pop("t", 0.5)); loai = e.pop("loai"); muc = e.pop("muc", None)
            kh.them(t0 + t, loai, canh=so, muc=muc, mo_ta=f"{loai} (kịch bản chỉ định)", **e); ghi.append(f"{loai} @{t}s (chỉ định)")
    return ghi


# ------------------------------------------------------------------ toàn tập
def thiet_ke(spec, scenes, starts, total, intro, outro, fps=30):
    """scenes: danh sách cảnh đã có wav/bounds/length (từ render.tinh_moc_canh), starts: mốc bắt đầu từng cảnh (giây).
    Trả về KeHoach."""
    kh = KeHoach(); sid = spec.get("id"); nam = nam_tap(spec)
    kh.ghi_chu.append(f"Tập {sid} – năm ước lượng {nam:.0f} → {'cho phép' if nam >= 1858 else 'không dùng'} tiếng nổ/súng; "
                      f"{'cho phép' if nam >= 1800 else 'không dùng'} tiếng pháo.")
    if intro:
        kh.them(0.0, "logo_mo", dai=intro, mo_ta="nhạc hiệu mở đầu")
        kh.ghi_chu.append(f"Mở đầu 0–{intro:.1f}s: nhạc hiệu logo (vút dâng → trống đồng khi logo đáp → rải đàn tranh ngũ cung)")
    huong = 1
    for k, s in enumerate(scenes):
        t0 = starts[k]; L = s["length"]; lop = s.get("lop"); so = s.get("so", k + 1)
        at = s.get("am_thanh")
        ghi = []
        if isinstance(at, dict) and at.get("tat"):
            kh.ghi_chu.append(f"Cảnh {so} ({lop}): tắt âm mô phỏng theo kịch bản"); continue
        n0 = len(kh.su_kien)
        # chuyển cảnh: vút nhẹ ở ranh giới (trừ cảnh trống đồng có tiếng riêng, thẻ có tiếng 'thẻ vào')
        if k > 0 and lop != "chuyen_canh" and scenes[k - 1].get("lop") != "chuyen_canh" and lop not in ("truc_thoi_gian", "ghi_nho", "cau_hoi"):
            kh.them(t0 - 0.1, "vut", huong=huong, canh=so, mo_ta="vút chuyển cảnh"); huong = -huong
        if lop == "chuyen_canh":
            kh.them(t0, "cong_thoi_gian", dai=L, canh=so, mo_ta="cổng thời gian trống đồng")
            ghi.append("cổng thời gian: gió cuốn, trống đồng khi hiện mốc năm, dâng lên chớp sáng")
        elif lop == "sa_ban":
            ghi += _sa_ban(kh, sid, s, t0, L, nam, so)
        elif lop in ("truc_thoi_gian", "ghi_nho"):
            kh.them(t0 + 0.02, "the_vao", canh=so, mo_ta="thẻ hiện ra")
            items = s.get("moc") if lop == "truc_thoi_gian" else s.get("y")
            m = len(items or []); times = s.get("_hien_luc")
            if not times or len(times) != m:
                dur_s = int(round(L * fps)) / fps
                times = [(0.4 if lop == "truc_thoi_gian" else 0.5) + j * (dur_s - 1.5) / max(m, 1) for j in range(m)]
            for j, tt in enumerate(times):
                kh.them(t0 + tt, "tich" if lop == "truc_thoi_gian" else "bop", bac=j, canh=so)
            ghi.append(f"thẻ vào + {m} tiếng {'tích (nốt ngũ cung đi lên)' if lop == 'truc_thoi_gian' else 'bóp + chuông nhỏ'} lúc " +
                       ", ".join(f"{x:.1f}s" for x in times))
        elif lop == "cau_hoi":
            b = s.get("bounds") or [(0, 3), (6, 8)]
            q_end = b[0][1] + 0.15; reveal = b[-1][0] + 0.15
            kh.them(t0 + 0.02, "the_vao", canh=so, mo_ta="thẻ câu hỏi")
            j = 1; nt = 0
            while reveal - j * 0.5 >= q_end - 0.01:
                kh.them(t0 + reveal - j * 0.5, "dong_ho", tac=(j % 2 == 1), canh=so); j += 1; nt += 1
            kh.them(t0 + reveal, "chuong_bao", canh=so, mo_ta="chuông lật đáp án")
            ghi.append(f"thẻ vào, {nt} tiếng tích tắc {q_end:.1f}–{reveal:.1f}s, chuông đáp án lúc {reveal:.1f}s")
        elif lop == "mo_phong":
            ghi += _mo_phong(kh, s, t0, L, so)
        else:
            cp = s.get("_clip"); co_tieng = bool(s.get("_clip_co_tieng"))
            ghi += _canh_hinh(kh, sid, s, t0, L, nam, so, co_tieng)
        kh.ghi_chu.append(f"Cảnh {so} ({lop}, {t0:.1f}–{t0 + L:.1f}s): " + "; ".join(ghi))
    kh.them(total - outro, "logo_ket", dai=outro, mo_ta="nhạc hiệu kết")
    kh.ghi_chu.append(f"Kết {total - outro:.1f}–{total:.1f}s: nhạc hiệu kết (trống đồng + rải đàn tranh đi xuống)")
    # gộp các tiếng cùng loại quá sát nhau (vd 4 mũi tên tiến công cách nhau 0.2 s) để không bị cộng dồn quá to
    kh.su_kien = _gop(kh.su_kien)
    return kh


def _gop(evs):
    evs = sorted(evs, key=lambda e: e["t"]); out = []
    for e in evs:
        p = next((x for x in reversed(out[-6:]) if x["loai"] == e["loai"] and e["loai"] in ("quan_tien", "rut_chay", "nuoc_re", "lua_bung", "mai_cheo", "go_nut", "cong", "ho_reo")
                  and e["t"] - x["t"] < 0.7), None)
        if p:
            p["_so"] = p.get("_so", 1) + 1
            if "dai" in e["kw"]: p["kw"]["dai"] = max(p["kw"].get("dai", 0), e["kw"]["dai"] + (e["t"] - p["t"]))
            if "p0" in e["kw"] and "p0" in p["kw"]:
                p["kw"]["p0"] = (p["kw"]["p0"] + e["kw"]["p0"]) / 2; p["kw"]["p1"] = (p["kw"]["p1"] + e["kw"]["p1"]) / 2
            continue
        out.append(e)
    for e in out:
        if e.get("_so", 1) > 1 and e["muc"] is not None: e["muc"] = e["muc"] + min(3.0, 1.5 * math.log2(e["_so"]))
    return out


def _mo_phong(kh, s, t0, L, so):
    name = s.get("mo_phong"); ghi = [f"mô phỏng {name}"]
    if name == "may_hoi_nuoc":
        kh.them_nen("nha_may", t0, t0 + L, MUC_NEN["nha_may"] - 4, so)
        kh.them_nen("lua_chay", t0, t0 + L, MUC_NEN["lua_chay"] - 6, so)
        j = 0
        while j * math.pi / 2.4 < L - 0.3:       # bánh đà quay 2.4 rad/s → 2 lần xả hơi mỗi vòng
            kh.them(t0 + j * math.pi / 2.4 + 0.05, "hoi_nuoc", canh=so, muc=-24, to=0.9 if j % 2 else 1.0); j += 1
        ghi.append(f"tiếng máy + lò lửa + {j} nhịp xả hơi khớp vòng quay bánh đà")
    elif name == "nha_may":
        kh.them_nen("song", t0, t0 + L, MUC_NEN["song"] - 3, so)
        kh.them_nen("nha_may", t0 + 0.35 * L, t0 + L, MUC_NEN["nha_may"] - 3, so)
        ghi.append("sông + bánh xe nước, xưởng máy nổi lên khi nhà máy xuất hiện (35%)")
    elif name == "kim_tu_thap":
        kh.them_nen("gio", t0, t0 + L, MUC_NEN["gio"] + 2, so)
        layers = 26; prev = 0; k = 0
        for i in range(1, int(L * 30)):
            u = i / (L * 30); x = min(u / 0.7, 1); built = int(x * x * (3 - 2 * x) * layers + 1e-4)
            if built > prev and built % 3 == 0: kh.them(t0 + u * L - 1.7, "da_keo", canh=so, muc=-23); k += 1
            prev = built
        ghi.append(f"gió sa mạc + {k} tiếng kéo – đặt đá khớp lớp đá xây lên")
    else:
        kh.them(t0 + 0.05, "the_vao", canh=so); ghi.append("tiếng thẻ nhẹ")
    return ghi
