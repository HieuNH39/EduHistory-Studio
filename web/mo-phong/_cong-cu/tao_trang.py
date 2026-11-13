"""Tạo trang mô phỏng tương tác (đợt 1) cho website EduHistory Studio.

Chạy:  python3 web/mo-phong/_cong-cu/tao_trang.py   (từ thư mục gốc kho mã)

Đọc (chỉ đọc):  data/catalog/episodes.json, data/scripts/<MA>.json, pipeline/maps/specs/*.json, assets/geo/*.geojson
Ghi (chỉ trong web/mo-phong/):  data/tap/<MA>.js, data/ban-do/<ten>.js, data/geo/*.js, <MA>.html, index.html

Nguyên tắc nội dung: mọi dữ kiện hiển thị lấy từ kịch bản đã đối chiếu SGK (data/scripts) – trang chỉ chứa
các cảnh, câu hỏi được liệt kê trong CAU_HINH dưới đây; dòng nguồn (số trang) tính từ chính các cảnh/câu hỏi đó.
Thư mục bắt đầu bằng dấu gạch dưới không được GitHub Pages (Jekyll) xuất bản."""
import html, json, os, re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(ROOT, "web", "mo-phong")
DAN_CHUYEN = {"Nhật Minh", "Hân Hân"}

# ---------------------------------------------------------------- cấu hình từng tập
# loai: ban_do | ba_chieu | truc_thoi_gian (dùng cho nhãn trên thư viện)
# canh: số cảnh trong kịch bản được đưa vào trang (lời thuyết minh, mốc, dữ kiện)
# cau_hoi: ("ds", i) = câu thứ i trong danh sách "cau_hoi" cuối kịch bản; ("canh", so) = câu hỏi dừng hình của cảnh
CAU_HINH = {
 "L6-B3-03": dict(loai="truc_thoi_gian", nhan="Trục thời gian",
   mo_ta="Kéo hai mốc trên trục Công lịch để tính khoảng cách giữa năm trước Công nguyên và năm Công nguyên.",
   huong_dan=["Kéo hai chốt A và B trên trục thời gian (hoặc gõ số năm, chọn TCN/CN).",
              "Bảng kết quả cho biết hai mốc cách nhau bao nhiêu năm và cách tính.",
              "Bấm “Phóng to quanh năm 1” để thấy vì sao không có năm 0.",
              "Thử các ví dụ có sẵn và giải thử thách ở cuối mô phỏng."],
   canh=[2, 4, 6, 8, 9, 10, 11], cau_hoi=[("ds", 0), ("ds", 1), ("ds", 2)]),
 "L6-B7-04": dict(loai="ba_chieu", nhan="Mô hình 3D",
   mo_ta="Xoay mô hình 3D Kim tự tháp Kê-óp, bóc từng lớp đá để thấy các tảng đá xếp chồng không cần chất kết dính.",
   huong_dan=["Kéo (hoặc vuốt) để xoay, cuộn chuột/chụm hai ngón để phóng to.",
              "Kéo thanh “Bóc lớp đá” để gỡ dần các lớp từ đỉnh xuống.",
              "Kéo thanh “Tách các lớp” để nhìn rõ từng lớp đá xếp chồng; bật “Cắt một góc” để xem bên trong.",
              "Bấm “Xếp đá từ dưới lên” để xem mô phỏng cách xếp; chạm vào một tảng đá để xem thông tin."],
   canh=[8, 9, 10, 11], cau_hoi=[("canh", 10), ("ds", 3), ("ds", 0)],
   ghi_chu=["Mô hình 3D minh hoạ, giản lược: số lớp và số tảng đá ít hơn rất nhiều so với công trình thật; không theo tỉ lệ."]),
 "L6-B14-03": dict(loai="ba_chieu", nhan="Mô hình 3D",
   mo_ta="Mô hình 3D thành Cổ Loa xoay 360 độ: ba vòng thành xoáy trôn ốc, cổng thành và sông, ao hồ, đầm lầy bao quanh.",
   huong_dan=["Kéo (hoặc vuốt) để xoay 360 độ, cuộn chuột/chụm hai ngón để phóng to.",
              "Bật/tắt từng vòng thành và lớp nước để so sánh.",
              "Bấm “Dựng từng vòng thành” để xem lần lượt thành ngoại, thành trung, thành nội.",
              "Chọn “Nhìn từ trên xuống” để thấy rõ hình xoáy trôn ốc."],
   canh=[4, 5, 6, 7, 8, 9, 10], cau_hoi=[("canh", 6), ("ds", 2), ("ds", 3)], ban_do=["co-loa"],
   ghi_chu=["Mô hình 3D dựng theo sơ đồ thành Cổ Loa (Hình 3, SGK Lịch sử và Địa lí 6, tr. 62), giản lược; độ cao tường thành được phóng đại để dễ quan sát, không theo tỉ lệ."]),
 "L6-B18-04": dict(loai="ban_do", nhan="Bản đồ động",
   mo_ta="Hoạt hoạ trận Bạch Đằng năm 938: thuyền nhẹ giả thua dụ địch vào bãi cọc, nước triều rút, thuyền giặc mắc cọc.",
   huong_dan=["Chọn từng giai đoạn ở hàng nút phía trên lược đồ.",
              "Bấm Phát để xem hoạt hoạ; kéo thanh thời gian hoặc bấm nút bước để đi từng bước.",
              "Theo dõi thước mực nước: bãi cọc chìm khi triều lên, nhô lên khi triều rút.",
              "Kéo để di chuyển, cuộn chuột hoặc dùng nút +/− để phóng to lược đồ."],
   canh=[5, 7, 10, 11, 12, 13, 15], cau_hoi=[("ds", 0), ("ds", 2), ("canh", 6)], ban_do=["bach-dang-938"]),
 "L7-B12-02": dict(loai="ba_chieu", nhan="Mô hình 3D + lược đồ",
   mo_ta="Mô hình 3D phòng tuyến sông Như Nguyệt: đê cao, dậu tre dày mấy tầng, bộ binh Đại Việt chặn quân Tống ở bờ bắc.",
   huong_dan=["Kéo (hoặc vuốt) để xoay, cuộn chuột/chụm hai ngón để phóng to.",
              "Chọn góc nhìn có sẵn: toàn cảnh, từ bờ bắc, mặt cắt đê.",
              "Bấm “Quân Tống vượt sông” để xem mô phỏng quân Tống bị đẩy lùi.",
              "Chuyển sang thẻ “Lược đồ” để xem diễn biến trên bản đồ."],
   canh=[6, 7, 8, 9, 10, 12], cau_hoi=[("canh", 8), ("ds", 1), ("ds", 2)], ban_do=["nhu-nguyet-1077"],
   ghi_chu=["Mô hình 3D minh hoạ theo mô tả trong SGK, giản lược, không theo tỉ lệ."]),
 "L7-B14-02": dict(loai="ban_do", nhan="Bản đồ động",
   mo_ta="Lược đồ động kháng chiến năm 1258: quân Mông Cổ tiến vào Thăng Long, quân Trần tạm rút lui bảo toàn lực lượng, rồi tấn công quyết định ở Đông Bộ Đầu.",
   huong_dan=["Chọn từng giai đoạn ở hàng nút phía trên lược đồ.",
              "Bấm Phát để xem hoạt hoạ; kéo thanh thời gian hoặc bấm nút bước để đi từng bước.",
              "Đọc lời thuyết minh bên dưới lược đồ cho mỗi giai đoạn.",
              "Kéo để di chuyển, cuộn chuột hoặc dùng nút +/− để phóng to."],
   canh=[4, 6, 9, 10, 11, 12, 13], cau_hoi=[("ds", 0), ("ds", 2), ("ds", 3)], ban_do=["khang-chien-1258"]),
 "L7-B14-04": dict(loai="ban_do", nhan="Bản đồ động",
   mo_ta="Mô phỏng trận địa bãi cọc Bạch Đằng năm 1288: nước triều lên xuống, thuyền giặc mắc kẹt và kế hoả công.",
   huong_dan=["Chọn từng giai đoạn ở hàng nút phía trên sơ đồ.",
              "Bấm Phát để xem hoạt hoạ; kéo thanh thời gian hoặc bấm nút bước để đi từng bước.",
              "Theo dõi thước mực nước: nước triều rút nhanh làm thuyền giặc mắc kẹt ở bãi cọc.",
              "Kéo để di chuyển, cuộn chuột hoặc dùng nút +/− để phóng to."],
   canh=[8, 9, 10, 12, 13, 14, 15, 16, 17, 18], cau_hoi=[("canh", 11), ("ds", 1), ("ds", 2)], ban_do=["bach-dang-1288"]),
 "L7-B16-05": dict(loai="ban_do", nhan="Bản đồ động",
   mo_ta="Bản đồ động trận Chi Lăng – Xương Giang (1427): hướng tiến của viện binh Minh và các điểm phục kích của nghĩa quân.",
   huong_dan=["Chọn từng giai đoạn ở hàng nút phía trên lược đồ.",
              "Bấm Phát để xem hoạt hoạ; kéo thanh thời gian hoặc bấm nút bước để đi từng bước.",
              "Chú ý kí hiệu chữ T: các điểm quân ta mai phục.",
              "Kéo để di chuyển, cuộn chuột hoặc dùng nút +/− để phóng to."],
   canh=[3, 4, 6, 8, 10, 11, 15], cau_hoi=[("ds", 0), ("ds", 1), ("ds", 2)], ban_do=["chi-lang-xuong-giang"]),
 "L7-CD1-03": dict(loai="ba_chieu", nhan="Quả địa cầu 3D",
   mo_ta="Theo dấu đoàn tàu Ph. Ma-gien-lăng đi vòng quanh Trái Đất trên quả địa cầu 3D, với các điểm dừng chân quan trọng.",
   huong_dan=["Bấm Phát để tàu đi theo hành trình; kéo thanh thời gian để tua.",
              "Chọn từng chặng ở hàng nút phía trên quả địa cầu.",
              "Kéo (hoặc vuốt) để tự xoay quả địa cầu; bấm “Theo tàu” để quả địa cầu tự quay theo con tàu.",
              "Các chấm đỏ là điểm dừng chân quan trọng."],
   canh=[4, 5, 6, 7, 9, 10, 11, 12, 13, 14], cau_hoi=[("ds", 1), ("ds", 2), ("ds", 3)], geo=True, ban_do=["ma-gien-lang"],
   ghi_chu=["Đường đi trên quả địa cầu là sơ đồ minh hoạ hành trình, không phải hải trình chính xác; không vẽ biên giới quốc gia."]),
 "L8-B2-03": dict(loai="truc_thoi_gian", nhan="Bản đồ + trục thời gian",
   mo_ta="Bản đồ tương tác: sự kiện ở Pa-ri ngày 14 – 7 – 1789 và các mốc chuyển biến từ quân chủ lập hiến sang cộng hoà.",
   huong_dan=["Bấm vào từng mốc trên trục thời gian (hoặc dùng nút Trước/Sau).",
              "Bản đồ đánh dấu Pa-ri; thẻ sự kiện cho biết điều gì đã diễn ra.",
              "Thang “Chế độ chính trị” cho thấy nước Pháp chuyển từ quân chủ sang cộng hoà như thế nào.",
              "Bấm Phát để xem lần lượt toàn bộ tiến trình."],
   canh=[3, 4, 5, 7, 8, 9, 10, 11, 12, 13], cau_hoi=[("ds", 0), ("ds", 1), ("ds", 2)], geo=True,
   ghi_chu=["Bản đồ nền: Natural Earth (phạm vi công cộng), không vẽ biên giới quốc gia."]),
 "L8-B3-02": dict(loai="ba_chieu", nhan="Mô hình 3D",
   mo_ta="Mô phỏng 3D pít-tông máy hơi nước làm quay bánh đà, và nhà máy “dời” từ ven sông vào trung tâm thành phố.",
   huong_dan=["Thẻ “Máy hơi nước”: bấm từng bước 1 → 4 để xem lửa, hơi nước, pít-tông, bánh đà hoạt động.",
              "Kéo thanh “Ngọn lửa” để máy chạy nhanh hay chậm.",
              "Thẻ “Vị trí nhà máy”: kéo thanh mốc năm để thấy nhà máy rời bờ sông vào thành phố.",
              "Kéo (hoặc vuốt) để xoay, cuộn chuột/chụm hai ngón để phóng to."],
   canh=[3, 4, 5, 6, 7, 9], cau_hoi=[("ds", 1), ("ds", 2), ("canh", 8)],
   ghi_chu=["Mô hình 3D minh hoạ nguyên lí hoạt động theo mô tả trong SGK, giản lược, không theo tỉ lệ."]),
 "L8-B8-02": dict(loai="ban_do", nhan="Bản đồ động",
   mo_ta="Bản đồ động trận Rạch Gầm – Xoài Mút: quân Xiêm tiến vào, quân Tây Sơn mai phục hai bên bờ và dùng thuyền, bè lửa tấn công.",
   huong_dan=["Chọn từng giai đoạn ở hàng nút phía trên lược đồ.",
              "Bấm Phát để xem hoạt hoạ; kéo thanh thời gian hoặc bấm nút bước để đi từng bước.",
              "Giai đoạn 1 đo chiều dài, bề rộng khúc sông và làm nổi bật cù lao Thới Sơn.",
              "Kéo để di chuyển, cuộn chuột hoặc dùng nút +/− để phóng to."],
   canh=[4, 5, 6, 8, 9, 10, 11, 12, 13], cau_hoi=[("ds", 0), ("ds", 1), ("ds", 2)], ban_do=["rach-gam-xoai-mut"]),
 "L8-B8-03": dict(loai="ban_do", nhan="Bản đồ động",
   mo_ta="Sơ đồ mũi tên tiến công của quân Tây Sơn ra Thăng Long: các mũi đánh vào đồn Hà Hồi, Ngọc Hồi, Đống Đa (Tết 1789).",
   huong_dan=["Chọn từng giai đoạn ở hàng nút phía trên lược đồ.",
              "Bấm Phát để xem hoạt hoạ; kéo thanh thời gian hoặc bấm nút bước để đi từng bước.",
              "Mũi tên đỏ đậm: quân Tây Sơn tiến công; mũi tên nét đứt: quân Thanh rút chạy.",
              "Kéo để di chuyển, cuộn chuột hoặc dùng nút +/− để phóng to."],
   canh=[4, 5, 6, 8, 9, 11, 12, 13, 15, 16], cau_hoi=[("ds", 0), ("ds", 1), ("ds", 2)], ban_do=["ngoc-hoi-dong-da"]),
 "L9-B4-03": dict(loai="truc_thoi_gian", nhan="Trục thời gian kéo thả",
   mo_ta="Kéo thả các sự kiện từ năm 1942 đến năm 1945 vào đúng thứ tự trên trục thời gian, rồi xem lược đồ minh hoạ.",
   huong_dan=["Kéo từng thẻ sự kiện vào ô trống trên trục thời gian (trên điện thoại: chạm thẻ rồi chạm ô).",
              "Bấm “Kiểm tra” để xem thẻ nào đúng (xanh), thẻ nào sai (đỏ).",
              "Sắp đúng hết sẽ hiện ngày tháng của từng sự kiện.",
              "Xem thêm lược đồ minh hoạ ở phía dưới."],
   canh=[3, 6, 8, 10, 11], cau_hoi=[("ds", 0), ("ds", 1), ("ds", 3)], ban_do=["ctgt2-chau-au", "ctgt2-chau-a"]),
 "L9-B8-04": dict(loai="truc_thoi_gian", nhan="Bản đồ + dòng thời gian",
   mo_ta="Dòng thời gian tháng 8 – 1945: kéo theo từng ngày để thấy khởi nghĩa giành chính quyền ở các tỉnh lị trên bản đồ.",
   huong_dan=["Kéo thanh ngày (13 đến 28 – 8 – 1945) hoặc bấm vào từng mốc.",
              "Bấm Phát để xem lần lượt từng ngày.",
              "Ngôi sao đỏ: nơi giành chính quyền; vòng đỏ: khởi nghĩa ở nhiều xã, huyện.",
              "Bảng bên dưới liệt kê các tỉnh lị đã giành chính quyền tính đến ngày đang chọn."],
   canh=[1, 3, 4, 5, 7, 8, 9, 10, 12, 14], cau_hoi=[("ds", 1), ("ds", 3), ("canh", 13)], ban_do=["tong-khoi-nghia-1945"]),
 "L9-B15-03": dict(loai="ban_do", nhan="Bản đồ động",
   mo_ta="Mô phỏng 3 đợt tấn công trên sơ đồ chiến dịch Điện Biên Phủ, nhấn mạnh việc kiểm soát sân bay Mường Thanh.",
   huong_dan=["Chọn tập đoàn cứ điểm hoặc từng đợt tấn công ở hàng nút phía trên sơ đồ.",
              "Bấm Phát để xem hoạt hoạ; kéo thanh thời gian hoặc bấm nút bước để đi từng bước.",
              "Ở đợt 2, chú ý sân bay Mường Thanh bị quân ta kiểm soát.",
              "Kéo để di chuyển, cuộn chuột hoặc dùng nút +/− để phóng to."],
   canh=[4, 9, 10, 12, 14], cau_hoi=[("ds", 1), ("ds", 2), ("canh", 11)], ban_do=["dien-bien-phu"]),
 "L9-B17-05": dict(loai="ban_do", nhan="Bản đồ động",
   mo_ta="Lược đồ động ba chiến dịch lớn của cuộc Tổng tiến công và nổi dậy Xuân 1975 tiến về Sài Gòn.",
   huong_dan=["Chọn từng chiến dịch ở hàng nút phía trên lược đồ.",
              "Bấm Phát để xem hoạt hoạ; kéo thanh thời gian hoặc bấm nút bước để đi từng bước.",
              "Lược đồ luôn thể hiện quần đảo Hoàng Sa và quần đảo Trường Sa của Việt Nam.",
              "Kéo để di chuyển, cuộn chuột hoặc dùng nút +/− để phóng to."],
   canh=[3, 4, 5, 7, 8, 9, 10, 12, 13], cau_hoi=[("ds", 1), ("ds", 3), ("canh", 6)], ban_do=["xuan-1975"]),
}

# ---------------------------------------------------------------- tiện ích
def doc(p): return json.load(open(os.path.join(ROOT, p), encoding="utf-8"))

def ghi(p, s):
    p = os.path.join(OUT, p); os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f: f.write(s)

def js_json(o): return json.dumps(o, ensure_ascii=False, separators=(",", ":"))

def trang_chu(trs):
    """[13, 14, 15, 17] -> '13–15, 17'"""
    trs = sorted(set(int(t) for t in trs)); out = []; i = 0
    while i < len(trs):
        j = i
        while j + 1 < len(trs) and trs[j + 1] == trs[j] + 1: j += 1
        out.append(str(trs[i]) if i == j else f"{trs[i]}–{trs[j]}"); i = j + 1
    return ", ".join(out)

def tron(o, nd=2):
    if isinstance(o, float): return round(o, nd)
    if isinstance(o, list): return [tron(x, nd) for x in o]
    if isinstance(o, dict): return {k: tron(v, nd) for k, v in o.items()}
    return o

E = html.escape

# ---------------------------------------------------------------- dữ liệu dùng chung: bản đồ, đất liền
def tao_ban_do(ten):
    S = doc(f"pipeline/maps/specs/{ten}.json")
    ghi(f"data/ban-do/{ten}.js", "window.MP_BANDO=window.MP_BANDO||{};MP_BANDO[" + json.dumps(ten) + "]=" + js_json(tron(S, 1)) + ";\n")

def tao_geo():
    out = {}
    for ten, khoa in (("ne_110m_land", "dat"), ("ne_110m_lakes", "ho")):
        g = doc(f"assets/geo/{ten}.geojson"); vong = []
        for f in g["features"]:
            geo = f["geometry"]; cs = geo["coordinates"]
            for poly in (cs if geo["type"] == "MultiPolygon" else [cs]):
                for i, ring in enumerate(poly):
                    (vong if True else None).append({"lo": 1 if (i > 0 or khoa == "ho") else 0, "d": [[round(x, 2), round(y, 2)] for x, y in ring]})
        out[khoa] = vong
    ghi("data/geo/dat-lien-110m.js", "/* Natural Earth 1:110m land + lakes (public domain), toạ độ [kinh độ, vĩ độ] làm tròn 0,01° */\n"
        "window.MP_GEO=" + js_json({"vong": out["dat"] + out["ho"]}) + ";\n")

# ---------------------------------------------------------------- dữ liệu từng tập
def du_lieu_tap(ma, ep, sc, cfg):
    canh = {c["so"]: c for c in sc["canh"]}
    ds_canh, trang = [], set()
    for so in cfg["canh"]:
        c = canh[so]; trang.update(c.get("nguon_trang") or [])
        d = {"so": so, "lop": c["lop"], "tr": c.get("nguon_trang") or [],
             "loi": [l[1] for l in c.get("loi", []) if l[0] in DAN_CHUYEN],
             "loi_nv": [[l[0], l[1]] for l in c.get("loi", []) if l[0] not in DAN_CHUYEN]}
        for k in ("sa_ban", "pha", "mo_phong", "che_do", "tieu_de", "moc", "y", "cau_hoi"):
            if k in c: d[k] = c[k]
        ds_canh.append(d)
    cau = []
    for loai, i in cfg["cau_hoi"]:
        if loai == "ds":
            q = sc["cau_hoi"][i]; cau.append({"hoi": q["hoi"], "dap_an": q["dap_an"], "dung": q["dung"], "tr": [q.get("trang")]})
            trang.add(q.get("trang"))
        else:
            c = canh[i]; q = c["cau_hoi"]
            cau.append({"hoi": q["hoi"], "dap_an": q["lua_chon"], "dung": q["dung"], "tr": c.get("nguon_trang") or []})
            trang.update(c.get("nguon_trang") or [])
    trang.discard(None)
    lop = ep["lop"]; bai = sc["nguon"]["bai"]
    m = re.match(r"(Bài \d+|Chủ đề chung \d+)\.\s*(.*)", bai)
    tap = {"ma": ma, "ten_tap": sc["ten_tap"], "lop": lop, "so_tap": ep["so"],
           "bai": m.group(1) if m else bai, "ten_bai": m.group(2) if m else "", "sach": sc["nguon"]["sach"],
           "mo_phong": ep["mo_phong"], "trang": sorted(trang), "canh": ds_canh, "cau_hoi": cau}
    return tap

HUONG = {"ban_do": "ban-do", "ba_chieu": "ba-chieu", "truc_thoi_gian": "truc-thoi-gian"}

def trang_html(tap, cfg):
    ma = tap["ma"]
    scripts = [f"data/tap/{ma}.js"] + [f"data/ban-do/{b}.js" for b in cfg.get("ban_do", [])]
    if cfg.get("geo"): scripts.append("data/geo/dat-lien-110m.js")
    scripts += ["js/am-thanh.js", "js/chung.js"]
    if cfg.get("ban_do") and ma not in ("L6-B14-03", "L7-CD1-03"): scripts.append("js/saban.js")
    if cfg["loai"] == "ba_chieu": scripts += ["vendor/three.min.js", "js/ba-chieu.js"]
    scripts.append(f"js/mp/{ma}.js")
    nguon = f"Theo SGK {tap['sach'].replace('(bộ sách dùng chung)', '(bộ sách dùng chung)')}, tr. {trang_chu(tap['trang'])}."
    ghi_chu = list(cfg.get("ghi_chu", []))
    for b in cfg.get("ban_do", []):
        if ma == "L6-B14-03": continue  # mô hình 3D: đã có ghi chú riêng
        S = doc(f"pipeline/maps/specs/{b}.json")
        g = S["nguon"].replace("; nền đất liền Natural Earth", "; nền đất liền: Natural Earth (phạm vi công cộng)").replace("; nền bản đồ Natural Earth", "; nền bản đồ: Natural Earth (phạm vi công cộng)")
        ghi_chu.append("Lược đồ: " + g[0].lower() + g[1:] + ("" if g.endswith(".") else "."))
    li = "".join(f"<li>{E(h)}</li>" for h in cfg["huong_dan"])
    gc = "".join(f'<span class="ghi-chu">{E(g)}</span>' for g in ghi_chu)
    sc_tags = "\n".join(f'<script src="{s}"></script>' for s in scripts)
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(tap['ten_tap'])} – Mô phỏng | EduHistory Studio</title>
<meta name="description" content="{E(cfg['mo_ta'])}">
<meta name="theme-color" content="#10233F">
<link rel="icon" href="img/logo.svg" type="image/svg+xml">
<link rel="stylesheet" href="css/mo-phong.css">
</head>
<body class="loai-{HUONG[cfg['loai']]}" data-ma="{ma}">
<a class="bo-qua" href="#mo-phong">Bỏ qua, tới mô phỏng</a>
<header class="dau-trang">
  <a class="thuong-hieu" href="index.html"><img src="img/logo.svg" alt="" width="40" height="40"><span>EduHistory Studio<small>Mô phỏng tương tác</small></span></a>
  <a class="ve-danh-sach" href="index.html">Tất cả mô phỏng</a>
</header>
<main class="khung">
  <section class="mo-dau">
    <p class="nhan-bai"><span class="the-lop">Lớp {tap['lop']}</span> {E(tap['bai'])}. {E(tap['ten_bai'])} <span class="ma-tap">{ma}</span></p>
    <h1>{E(tap['ten_tap'])}</h1>
    <p class="mo-ta">{E(cfg['mo_ta'])}</p>
  </section>
  <details class="huong-dan" open>
    <summary>Cách sử dụng</summary>
    <ul>{li}</ul>
  </details>
  <section class="mo-phong" id="mo-phong" aria-label="Mô phỏng: {E(tap['ten_tap'])}">
    <noscript><p class="bao-loi">Cần bật JavaScript để xem mô phỏng.</p></noscript>
  </section>
  <section class="thu-nhanh" aria-labelledby="tieu-de-thu-nhanh">
    <h2 id="tieu-de-thu-nhanh">Thử nhanh</h2>
    <div id="cau-hoi"></div>
  </section>
  <p class="nguon"><strong>{E(nguon)}</strong>{gc}</p>
</main>
<footer class="chan-trang">EduHistory Studio – ChronoVibe, FPT School Bắc Giang</footer>
{sc_tags}
</body>
</html>
"""

def index_html(ds):
    nhom = {}
    for tap, cfg in ds: nhom.setdefault(tap["lop"], []).append((tap, cfg))
    phan = []
    for lop in sorted(nhom):
        the = []
        for tap, cfg in nhom[lop]:
            the.append(f"""<li><a class="the-mp" href="{tap['ma']}.html">
<span class="loai loai-{HUONG[cfg['loai']]}">{E(cfg['nhan'])}</span>
<span class="ten">{E(tap['ten_tap'])}</span>
<span class="bai">Lớp {lop} · {E(tap['bai'])}. {E(tap['ten_bai'])}</span>
<span class="mota">{E(cfg['mo_ta'])}</span>
<span class="ma-tap">{tap['ma']}</span></a></li>""")
        phan.append(f'<section class="nhom-lop" aria-labelledby="lop-{lop}"><h2 id="lop-{lop}">Lớp {lop}</h2><ul class="luoi-the">{"".join(the)}</ul></section>')
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Mô phỏng tương tác Lịch sử 6–9 | EduHistory Studio</title>
<meta name="description" content="{len(ds)} mô phỏng tương tác Lịch sử lớp 6–9: bản đồ động, mô hình 3D, trục thời gian – EduHistory Studio.">
<meta name="theme-color" content="#10233F">
<link rel="icon" href="img/logo.svg" type="image/svg+xml">
<link rel="stylesheet" href="css/mo-phong.css">
</head>
<body class="trang-thu-vien">
<header class="dau-trang">
  <a class="thuong-hieu" href="index.html"><img src="img/logo.svg" alt="" width="40" height="40"><span>EduHistory Studio<small>Mô phỏng tương tác</small></span></a>
</header>
<main class="khung">
  <section class="mo-dau">
    <p class="nhan-bai">Đợt 1 · {len(ds)} mô phỏng</p>
    <h1>Mô phỏng tương tác Lịch sử 6 – 9</h1>
    <p class="mo-ta">Bản đồ động, mô hình 3D và trục thời gian đi kèm các video bài học của EduHistory Studio. Mọi dữ kiện lấy từ kịch bản đã đối chiếu SGK <em>Lịch sử và Địa lí</em> (bộ sách dùng chung), có ghi số trang ở cuối mỗi trang.</p>
    <div class="loc" role="group" aria-label="Lọc theo loại mô phỏng">
      <button type="button" class="nut-loc dang-chon" data-loc="tat-ca" aria-pressed="true">Tất cả</button>
      <button type="button" class="nut-loc" data-loc="ban-do" aria-pressed="false">Bản đồ động</button>
      <button type="button" class="nut-loc" data-loc="ba-chieu" aria-pressed="false">Mô hình 3D</button>
      <button type="button" class="nut-loc" data-loc="truc-thoi-gian" aria-pressed="false">Trục thời gian</button>
    </div>
  </section>
  {"".join(phan)}
</main>
<footer class="chan-trang">EduHistory Studio – ChronoVibe, FPT School Bắc Giang</footer>
<script>
(function(){{var b=document.querySelectorAll('.nut-loc');b.forEach(function(n){{n.addEventListener('click',function(){{
var l=n.getAttribute('data-loc');b.forEach(function(m){{var on=m===n;m.classList.toggle('dang-chon',on);m.setAttribute('aria-pressed',on?'true':'false');}});
document.querySelectorAll('.the-mp').forEach(function(a){{var li=a.parentNode;li.hidden=!(l==='tat-ca'||a.querySelector('.loai').classList.contains('loai-'+l));}});
document.querySelectorAll('.nhom-lop').forEach(function(s){{s.hidden=!s.querySelector('li:not([hidden])');}});}});}});}})();
</script>
</body>
</html>
"""

def main():
    cat = doc("data/catalog/episodes.json")
    eps = {e["ma"]: e for e in cat["tap"] if e.get("dot") == 1}
    assert set(eps) == set(CAU_HINH), set(eps) ^ set(CAU_HINH)
    ban_do = sorted({b for c in CAU_HINH.values() for b in c.get("ban_do", [])})
    for b in ban_do: tao_ban_do(b)
    tao_geo()
    ds = []
    for ma in sorted(eps, key=lambda m: (eps[m]["lop"], [int(x) if x.isdigit() else x for x in re.findall(r"\d+|\D+", m)])):
        cfg = CAU_HINH[ma]; sc = doc(f"data/scripts/{ma}.json")
        tap = du_lieu_tap(ma, eps[ma], sc, cfg)
        ghi(f"data/tap/{ma}.js", "window.MP_TAP=" + js_json(tap) + ";\n")
        ghi(f"{ma}.html", trang_html(tap, cfg))
        ds.append((tap, cfg))
    ghi("index.html", index_html(ds))
    print("Đã tạo", len(ds), "trang mô phỏng,", len(ban_do), "bản đồ.")

if __name__ == "__main__":
    main()
