"""Tạo trang mô phỏng tương tác (đợt 1) cho website EduHistory Studio.

Chạy:  python3 web/mo-phong/_cong-cu/tao_trang.py   (từ thư mục gốc kho mã)

Đọc (chỉ đọc):  data/catalog/episodes.json, data/scripts/<MA>.json, pipeline/maps/specs/*.json, assets/geo/*.geojson
Ghi (chỉ trong web/mo-phong/):  data/tap/<MA>.js, data/ban-do/<ten>.js, data/geo/*.js, <MA>.html, index.html

Nguyên tắc nội dung: mọi dữ kiện hiển thị lấy từ kịch bản đã đối chiếu SGK (data/scripts) – trang chỉ chứa
các cảnh, câu hỏi được liệt kê trong CAU_HINH dưới đây; dòng nguồn (số trang) tính từ chính các cảnh/câu hỏi đó.
Thư mục bắt đầu bằng dấu gạch dưới không được GitHub Pages (Jekyll) xuất bản."""
import html, json, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(ROOT, "web", "mo-phong")
DAN_CHUYEN = {"Nhật Minh", "Hân Hân"}
sys.path.insert(0, os.path.join(ROOT, "web", "_cong-cu"))
import tao_thu_vien as TV   # dùng chung: biểu tượng, ngăn mục lục, chân trang (không chạy main)

# nhóm hiển thị trên trang danh sách
NHOM = {"tran": "Sơ đồ trận đánh", "ban": "Bản đồ lịch sử", "ba_chieu": "Mô hình 3D", "truc_thoi_gian": "Trục thời gian", "so_do": "Sơ đồ tương tác"}
TRAN_CO_SAN = {"L6-B18-04", "L7-B14-02", "L7-B14-04", "L7-B16-05", "L8-B8-02", "L8-B8-03", "L9-B15-03", "L9-B17-05"}

# ---------------------------------------------------------------- bản đồ động sinh tự động từ sa bàn đã dựng cho video (15/11/2026)
# (mã tập dùng sa bàn, tên sa bàn trong pipeline/maps/specs, nhóm) – dữ liệu sa bàn đã được kiểm tra khi dựng video
TU_DONG = [
 ("L6-B16-01", "hai-ba-trung-40", "tran"), ("L6-B18-02", "duong-dinh-nghe-931", "tran"), ("L7-B9-03", "12-su-quan", "tran"),
 ("L7-B10-02", "chong-tong-981", "tran"), ("L7-B12-01", "tien-cong-1075", "tran"), ("L7-B14-03", "khang-chien-1285", "tran"),
 ("L7-B16-04", "tot-dong-chuc-dong", "tran"), ("L9-B14-03", "viet-bac-1947", "tran"), ("L9-B14-04", "bien-gioi-1950", "tran"),
 ("L9-B15-02", "dong-xuan-1953", "tran"),
 ("L7-B6-01", "dong-nam-a-x-xvi", "ban"), ("L8-B5-02", "nam-bac-trieu", "ban"), ("L8-B5-03", "trinh-nguyen", "ban"),
 ("L8-B6-03", "hoang-sa-chua-nguyen", "ban"), ("L8-B7-02", "nong-dan-dang-ngoai", "ban"), ("L8-B16-02", "hanh-chinh-nguyen", "ban"),
 ("L8-B16-05", "hoang-sa-truong-sa", "ban"), ("L8-B18-02", "can-vuong", "ban"), ("L8-CD1-01", "hai-chau-tho", "ban"),
 ("L8-CD1-03", "chau-tho-cuu-long", "ban"), ("L8-CD2-02", "duong-co-so", "ban"), ("L9-B1-01", "nga-xo-viet-1918", "ban"),
 ("L9-B3-05", "dong-nam-a", "ban"), ("L9-B4-02", "ctgt2-giai-doan-1", "ban"), ("L9-B9-03", "chien-tranh-lanh", "ban"),
 ("L9-B12-02", "cu-ba", "ban"), ("L9-B12-06", "asean", "ban"), ("L9-B20-02", "bao-ve-bien-gioi", "ban"),
 ("L9-B20-03", "bien-dao-viet-nam", "ban"),
]
NHAN_PHA = {  # nhãn giai đoạn khi sa bàn không có mốc chữ
 ("khang-chien-1285", "rut_lui"): "Nhà Trần rút khỏi Thăng Long", ("khang-chien-1285", "hoi_quan"): "Toa Đô hội quân với Thoát Hoan",
 ("khang-chien-1285", "rut_chay"): "Quân Nguyên rút chạy về nước", ("duong-dinh-nghe-931", "dai_la"): "Vây đánh thành Đại La",
 ("duong-dinh-nghe-931", "tiep_vien"): "Chặn quân tiếp viện Nam Hán", ("duong-dinh-nghe-931", "thang_loi"): "Thắng lợi",
 ("hai-ba-trung-40", "tien_quan"): "Nghĩa quân tiến về Luy Lâu", ("hai-ba-trung-40", "thang_loi"): "Thắng lợi",
 ("chien-tranh-lanh", "tong_quan"): "Toàn cảnh", ("cu-ba", "vi_tri"): "Vị trí Cu-ba", ("trinh-nguyen", "thuan_hoa"): "Thuận Hoá",
 ("trinh-nguyen", "chia_cat"): "Đất nước bị chia cắt", ("hanh-chinh-nguyen", "toan_quoc"): "Toàn quốc",
 ("hoang-sa-chua-nguyen", "tong_quan"): "Toàn cảnh", ("hoang-sa-truong-sa", "tong_quan"): "Toàn cảnh",
 ("hoang-sa-truong-sa", "toan_do"): "Toàn đồ", ("dong-nam-a", "tong_quan"): "Toàn cảnh", ("bien-dao-viet-nam", "dac_khu"): "Toàn cảnh biển đảo",
 ("hai-chau-tho", "tong_quan"): "Toàn cảnh", ("chau-tho-cuu-long", "tong_quan"): "Toàn cảnh",
}

# ---------------------------------------------------------------- mô hình 3D mới (15/11/2026): kiến trúc, hiện vật, phương tiện
MO_HINH_MOI = {
 "L6-B18-03": dict(loai="ba_chieu", nhan="Mô hình 3D",
   mo_ta="Bãi cọc Bạch Đằng 3D: kéo mực nước triều lên xuống để thấy cọc ngầm chìm rồi nhô lên, thuyền giặc mắc cọc khi triều rút.",
   huong_dan=["Kéo (hoặc vuốt) để xoay, cuộn chuột/chụm hai ngón để phóng to.",
              "Kéo thanh “Mực nước triều” để nâng, hạ mặt nước; cột đo trên bờ cho biết mức chênh.",
              "Bấm “Triều lên” để thuyền giặc tiến vào bãi cọc, rồi “Triều rút” để xem thuyền giặc mắc cọc.",
              "Bật “Nhìn sát mặt nước” để thấy rõ đầu cọc bịt sắt dưới nước."],
   canh=[6, 7, 8, 9, 11], cau_hoi=[("canh", 10), ("ds", 2), ("ds", 3)],
   ghi_chu=["Mô hình 3D minh hoạ theo mô tả trong SGK, giản lược; số cọc, khoảng cách và kích thước thuyền không theo tỉ lệ."]),
 "L6-B2-02": dict(loai="ba_chieu", nhan="Mô hình 3D",
   mo_ta="Trống đồng Ngọc Lũ 3D: xoay trống, soi từng vành hoa văn trên mặt trống – mái nhà cong, thuyền, người giã gạo, người múa hát.",
   huong_dan=["Kéo (hoặc vuốt) để xoay, cuộn chuột/chụm hai ngón để phóng to.",
              "Bấm các nút “Soi hoạ tiết” để máy quay bay tới từng vành hoa văn.",
              "Chạm vào mặt trống để xem hoạ tiết ở vị trí đó cho biết điều gì về đời sống người Việt cổ.",
              "Bật “Xoay chậm” để xem trống từ mọi phía."],
   canh=[2, 4, 5, 10], cau_hoi=[("canh", 6), ("ds", 0), ("ds", 2)],
   ghi_chu=["Mô hình 3D minh hoạ, giản lược hoa văn của trống đồng Đông Sơn; không phải bản sao chính xác của trống Ngọc Lũ."]),
 "L7-B18-02": dict(loai="ba_chieu", nhan="Mô hình 3D",
   mo_ta="Tháp Chăm 3D: xếp từng lớp gạch nung để dựng tháp, tách lớp để thấy các viên gạch gắn kết không dùng vữa.",
   huong_dan=["Kéo (hoặc vuốt) để xoay, cuộn chuột/chụm hai ngón để phóng to.",
              "Bấm “Xây tháp từ móng” để xem tháp được dựng lên từng lớp gạch.",
              "Kéo thanh “Tách lớp gạch” để thấy giữa các lớp không có vữa.",
              "Chạm vào một viên gạch để xem thông tin."],
   canh=[1, 3, 4, 7, 12], cau_hoi=[("canh", 5), ("ds", 1), ("ds", 0)],
   ghi_chu=["Mô hình 3D minh hoạ kiểu tháp Chăm (gạch nung, nhiều tầng thu nhỏ dần), giản lược, không theo tỉ lệ của tháp Pô Klong Ga-rai."]),
 "L7-CD1-02": dict(loai="ba_chieu", nhan="Mô hình 3D",
   mo_ta="Tàu Ca-ra-ven 3D: tàu dài có bánh lái và hệ thống buồm lớn; đổi hướng gió để xem buồm và bánh lái giúp tàu vượt đại dương.",
   huong_dan=["Kéo (hoặc vuốt) để xoay, cuộn chuột/chụm hai ngón để phóng to.",
              "Kéo thanh “Hướng gió” để xem buồm xoay theo gió.",
              "Bấm tên từng bộ phận (bánh lái, buồm, la bàn) để máy quay bay tới bộ phận đó.",
              "Bấm “Ra khơi” để tàu lướt sóng."],
   canh=[1, 4, 7, 13], cau_hoi=[("ds", 1), ("ds", 2), ("ds", 0)],
   ghi_chu=["Mô hình 3D minh hoạ một tàu ca-ra-ven thế kỉ XV, giản lược, không theo tỉ lệ."]),
 "L6-B13-04": dict(loai="ba_chieu", nhan="Mô hình 3D",
   mo_ta="Đền Bô-rô-bu-đua 3D: kì quan Phật giáo xây dựng vào thế kỉ VIII – dựng từng tầng nền vuông, tầng tròn và các tháp chuông.",
   huong_dan=["Kéo (hoặc vuốt) để xoay, cuộn chuột/chụm hai ngón để phóng to.",
              "Kéo thanh “Dựng từng tầng” hoặc bấm “Xây từ nền” để xem các tầng chồng lên nhau.",
              "Chọn góc nhìn “Từ trên xuống” để thấy mặt bằng hình mạn-đà-la.",
              "Đọc thẻ “Theo SGK” để biết vì sao kiến trúc Đông Nam Á chịu ảnh hưởng Ấn Độ."],
   canh=[4, 5, 9, 10], cau_hoi=[("canh", 12), ("ds", 2), ("ds", 0)],
   ghi_chu=["Mô hình 3D minh hoạ, giản lược số tầng, số tháp và phù điêu; không theo tỉ lệ."]),
 "L6-B10-02": dict(loai="ba_chieu", nhan="Mô hình 3D + sơ đồ",
   mo_ta="Đền Pác-tê-nông 3D trên đồi cao của A-ten, kèm sơ đồ bộ máy nhà nước A-ten và trò bỏ phiếu bằng vỏ sò.",
   huong_dan=["Kéo (hoặc vuốt) để xoay mô hình đền Pác-tê-nông; bấm “Dựng hàng cột” để xem đền được dựng lên.",
              "Trong sơ đồ bộ máy nhà nước, chạm vào từng cơ quan để xem Đại hội nhân dân bầu ra những cơ quan nào.",
              "Trò “Bỏ phiếu bằng vỏ sò”: thả phiếu và theo dõi khi nào đủ 6 000 phiếu.",
              "Làm câu hỏi “Thử nhanh” ở cuối trang."],
   canh=[5, 7, 9, 11, 12], cau_hoi=[("canh", 6), ("ds", 1), ("ds", 2)],
   ghi_chu=["Mô hình 3D minh hoạ, giản lược số cột và chi tiết trang trí; không theo tỉ lệ."]),
}

def cau_hinh_tu_dong(ma, spec, nhom):
    S = doc(f"pipeline/maps/specs/{spec}.json"); sc = doc(f"data/scripts/{ma}.json")
    canh_sb = [c for c in sc["canh"] if c.get("sa_ban") == spec]
    pha = []
    for k, v in S["pha"].items():
        moc = v.get("moc") or []
        nhan = NHAN_PHA.get((spec, k)) or (moc[0]["chu"] if moc else k.replace("_", " ").capitalize())
        pha.append({"key": k, "nhan": nhan, "canh": [c["so"] for c in canh_sb if c.get("pha") == k]})
    canh = sorted({c["so"] for c in canh_sb} | {so for p_ in pha for so in p_["canh"]})
    nq = len(sc.get("cau_hoi", []))
    ten = S.get("ten") or sc["ten_tap"]
    mo_ta = (f"{ten}" + (f" – {S['phu_de']}" if S.get("phu_de") else "") + ": "
             + ("sơ đồ diễn biến từng giai đoạn trên lược đồ, có hoạt hoạ mũi tên tiến công và âm thanh trận đánh."
                if nhom == "tran" else "bản đồ động theo từng giai đoạn, phóng to các vùng quan trọng."))
    hd = ["Chọn từng giai đoạn ở hàng nút phía trên " + ("sơ đồ." if nhom == "tran" else "bản đồ."),
          "Bấm Phát để xem hoạt hoạ; kéo thanh thời gian hoặc bấm nút bước để đi từng bước.",
          "Đọc lời thuyết minh bên dưới để hiểu diễn biến của giai đoạn đang xem.",
          "Kéo để di chuyển, cuộn chuột hoặc dùng nút +/− để phóng to."]
    return dict(loai="ban_do", nhom=nhom, nhan=NHOM[nhom], mo_ta=mo_ta, huong_dan=hd, canh=canh,
                cau_hoi=[("ds", i) for i in range(min(3, nq))], ban_do=[spec], tu_dong={"spec": spec, "pha": pha})

def js_tu_dong(ma, cfg):
    t = cfg["tu_dong"]; nhom = cfg["nhom"]
    pha = [{"key": p["key"], "nhan": p["nhan"], "canh": p["canh"]} for p in t["pha"]]
    am = ("{ nen: ['gio'], batDau: 'trong', doiTuong: function (id, o) { if (o.loai === 'mui_ten_dich' || o.loai === 'mui_ten_ta') return ['vut_nhe', 'buoc_quan']; "
          "if (o.loai === 'sao') return 'trong_nho'; if (o.loai === 'nhan') return 'trong_nho'; } }") if nhom == "tran" else \
         "{ nen: ['gio'], doiTuong: function (id, o) { if (o.loai === 'nhan' || o.loai === 'sao') return 'trong_nho'; } }"
    return (f"/* {ma} · sinh tự động bởi _cong-cu/tao_trang.py từ sa bàn pipeline/maps/specs/{t['spec']}.json (đã dùng trong video) */\n"
            "MP.onReady(function () {\n  var W = window.SaBanWeb;\n"
            f"  new W.MapPlayer(MP.khung(), {{ id: {json.dumps(ma.lower())}, spec: window.MP_BANDO[{json.dumps(t['spec'])}],\n"
            f"    phases: {js_json(pha)},\n    am: {am} }});\n}});\n")


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
           "mo_phong": ep.get("mo_phong") or cfg.get("mo_ta"), "trang": sorted(trang), "canh": ds_canh, "cau_hoi": cau}
    return tap

HUONG = {"ban_do": "ban-do", "ba_chieu": "ba-chieu", "truc_thoi_gian": "truc-thoi-gian"}

def trang_html(tap, cfg):
    ma = tap["ma"]
    scripts = [f"data/tap/{ma}.js"] + [f"data/ban-do/{b}.js" for b in cfg.get("ban_do", [])]
    if cfg.get("geo"): scripts.append("data/geo/dat-lien-110m.js")
    scripts += ["js/am-thanh.js", "js/chung.js"]
    if cfg.get("ban_do") and ma not in ("L6-B14-03", "L7-CD1-03"): scripts.append("js/saban.js")
    if cfg["loai"] == "ba_chieu": scripts += ["vendor/three.min.js", "js/ba-chieu.js", "js/mo-hinh-chung.js"]
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
<link rel="stylesheet" href="../chung/css/khung-chung.css">
</head>
<body class="loai-{HUONG[cfg['loai']]} trang-mp" data-ma="{ma}" data-goc="../">
<a class="bo-qua" href="#mo-phong">Bỏ qua, tới mô phỏng</a>
{dau_trang()}
<nav class="ve-lai" aria-label="Quay lại"><a class="nut-ve" href="../tap/{ma}.html">{TV.ICON["phat"]}<span>Về video của tập này</span></a><a class="nut-ve phu" href="index.html">{TV.ICON["mo_phong"]}<span>Tất cả mô phỏng</span></a><a class="nut-ve phu" href="../index.html">{TV.ICON["quay_lai"]}<span>Trang chính EduHistory</span></a></nav>
<main class="khung">
  <section class="mo-dau">
    <p class="nhan-bai"><span class="the-lop">Lớp {tap['lop']}</span><span class="the-nhom">{E(NHOM[nhom_cua(tap['ma'], cfg)])}</span> {E(tap['bai'])}. {E(tap['ten_bai'])} <span class="ma-tap">{ma}</span></p>
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
{chan_trang_mp()}
<div class="thong-bao" role="status" aria-live="polite" hidden></div>
<script src="../chung/js/thu-vien.js"></script>
{sc_tags}
</body>
</html>
"""

def dau_trang():
    return (f'<header class="dau dau-trang">'
            f'<button type="button" class="nut-menu" aria-controls="ngan-menu" aria-expanded="false">{TV.ICON["menu"]}<span>Mục lục</span></button>'
            f'<a class="thuong-hieu" href="../index.html" title="Về trang chính EduHistory"><img src="img/logo.svg" alt="" width="40" height="40">'
            f'<span>EduHistory Studio<small>Kho học liệu số môn Lịch sử</small></span></a>'
            f'<nav class="dieu-huong-mp" aria-label="Điều hướng chính"><ul><li><a href="../index.html">Thư viện</a></li>'
            f'<li><a href="index.html" aria-current="page">Mô phỏng</a></li><li><a href="../gioi-thieu.html">Giới thiệu</a></li></ul></nav>'
            f'</header>{TV.ngan_menu("../")}')

def chan_trang_mp():
    return TV.chan_trang("../", ("Hệ thống mô phỏng tương tác môn Lịch sử: sơ đồ trận đánh, bản đồ lịch sử, mô hình 3D, trục thời gian",
                                 "Chúc các bạn khám phá Lịch sử thật thú vị cùng mô phỏng EduHistory"))

def nhom_cua(ma, cfg):
    if cfg.get("nhom"): return cfg["nhom"]
    if cfg["loai"] == "ban_do": return "tran" if ma in TRAN_CO_SAN else "ban"
    return cfg["loai"]

def sa_ban_holo():
    """Sa bàn dạng ảnh toàn ký (SVG động) ở đầu trang danh sách – trang trí, không mang dữ kiện."""
    coc = "".join(f'<line x1="{x}" y1="{y}" x2="{x + 5}" y2="{y - 12}"/>' for x, y in
                  ((262, 214), (276, 220), (290, 226), (304, 231), (318, 236), (270, 236), (284, 242), (298, 247), (312, 252)))
    return f"""<svg class="holo" viewBox="0 0 520 420" aria-hidden="true" focusable="false">
<defs><radialGradient id="hg" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#5ED0FF" stop-opacity=".22"/><stop offset="1" stop-color="#5ED0FF" stop-opacity="0"/></radialGradient>
<linearGradient id="quet" x1="0" x2="1"><stop offset="0" stop-color="#5ED0FF" stop-opacity="0"/><stop offset="1" stop-color="#5ED0FF" stop-opacity=".35"/></linearGradient></defs>
<g class="holo-ban" transform="translate(260 215) scale(1 .8) rotate(-10) translate(-260 -215)">
 <circle cx="260" cy="215" r="196" fill="url(#hg)"/>
 <g class="luoi" stroke="#5ED0FF" stroke-opacity=".16" fill="none">{"".join(f'<circle cx="260" cy="215" r="{r}"/>' for r in (60, 110, 160, 196))}
  {"".join(f'<line x1="{260 + 196 * __import__("math").cos(a / 6 * 3.14159)}" y1="{215 + 196 * __import__("math").sin(a / 6 * 3.14159)}" x2="{260 - 196 * __import__("math").cos(a / 6 * 3.14159)}" y2="{215 - 196 * __import__("math").sin(a / 6 * 3.14159)}"/>' for a in range(6))}</g>
 <path class="song" d="M70 120 C160 150 200 200 260 230 S380 300 470 300" fill="none" stroke="#5ED0FF" stroke-width="16" stroke-opacity=".28" stroke-linecap="round"/>
 <path class="song2" d="M70 120 C160 150 200 200 260 230 S380 300 470 300" fill="none" stroke="#9BE6FF" stroke-width="2" stroke-dasharray="6 10"/>
 <g class="coc" stroke="#E9B65C" stroke-width="3" stroke-linecap="round">{coc}</g>
 <g class="thuyen" fill="#7FA6D9"><path id="thuyen" d="M-14 -4 C-7 -7 9 -7 16 0 C9 7 -7 7 -14 4Z"><animateMotion dur="9s" repeatCount="indefinite" rotate="auto" path="M470 300 C380 300 320 262 290 240"/></path>
  <path d="M-14 -4 C-7 -7 9 -7 16 0 C9 7 -7 7 -14 4Z"><animateMotion dur="9s" begin="1.6s" repeatCount="indefinite" rotate="auto" path="M480 318 C392 316 330 278 300 252"/></path></g>
 <path class="mui-ta" d="M150 330 C200 300 230 270 262 246" fill="none" stroke="#FF6A3D" stroke-width="5" stroke-linecap="round"/>
 <path class="mui-ta mt2" d="M380 150 C350 190 320 214 296 232" fill="none" stroke="#FF6A3D" stroke-width="5" stroke-linecap="round"/>
 <g class="quet"><path d="M260 215 L456 215 A196 196 0 0 0 398 76 Z" fill="url(#quet)"/></g>
 <circle class="chop" cx="276" cy="232" r="7" fill="none" stroke="#FFD27A" stroke-width="2"/>
</g></svg>"""

def index_html(ds):
    nhom = {}
    for tap, cfg in ds: nhom.setdefault(tap["lop"], []).append((tap, cfg))
    dem = {}
    for tap, cfg in ds: dem[nhom_cua(tap["ma"], cfg)] = dem.get(nhom_cua(tap["ma"], cfg), 0) + 1
    phan = []
    for lop in sorted(nhom):
        the = []
        for tap, cfg in nhom[lop]:
            nh = nhom_cua(tap["ma"], cfg)
            anh = f"img/anh/{tap['ma']}.jpg"
            hinh = (f'<img src="{anh}" alt="" width="640" height="400" loading="lazy">' if os.path.exists(os.path.join(OUT, anh))
                    else f'<span class="anh-trong">{TV.trong_dong("anh-thay")}</span>')
            the.append(f"""<li data-nhom="{nh}" data-lop="{lop}"><a class="the-mp" href="{tap['href'] if tap.get('href') else tap['ma'] + '.html'}">
<span class="khung-anh">{hinh}<span class="loai loai-{nh}">{E(NHOM[nh])}</span></span>
<span class="than-the"><span class="bai">Lớp {lop} · {E(tap['bai'])}</span>
<span class="ten">{E(tap['ten_tap'])}</span>
<span class="mota">{E(cfg['mo_ta'])}</span></span></a></li>""")
        phan.append(f'<section class="nhom-lop" aria-labelledby="lop-{lop}"><h2 id="lop-{lop}"><span class="so-lop">{lop}</span>Lịch sử {lop}</h2><ul class="luoi-the">{"".join(the)}</ul></section>')
    thu_tu = ["tran", "ban", "ba_chieu", "truc_thoi_gian", "so_do"]
    so = "".join(f'<div><dt>{E(NHOM[k])}</dt><dd>{dem[k]}</dd></div>' for k in thu_tu if dem.get(k))
    loc = "".join(f'<button type="button" class="nut-loc" data-loc="{k}" aria-pressed="false">{E(NHOM[k])}</button>' for k in thu_tu if dem.get(k))
    loc_lop = "".join(f'<button type="button" class="nut-loc" data-lop="{l}" aria-pressed="false">Lớp {l}</button>' for l in sorted(nhom))
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Hệ thống mô phỏng tương tác môn Lịch sử | EduHistory</title>
<meta name="description" content="{len(ds)} mô phỏng tương tác môn Lịch sử: sơ đồ trận đánh, bản đồ lịch sử, mô hình 3D, trục thời gian – ChronoVibe Team, EduHistory.">
<meta name="theme-color" content="#07162B">
<link rel="icon" href="img/logo.svg" type="image/svg+xml">
<link rel="stylesheet" href="css/mo-phong.css">
<link rel="stylesheet" href="../chung/css/khung-chung.css">
</head>
<body class="trang-thu-vien trang-mp" data-goc="../">
<a class="bo-qua" href="#danh-sach">Bỏ qua, tới danh sách mô phỏng</a>
{dau_trang()}
<section class="bia-mp" aria-labelledby="tieu-de-mp">
 <div class="khung bia-mp-luoi">
  <div class="bia-mp-chu">
   <h1 id="tieu-de-mp">Hệ thống mô phỏng tương tác môn Lịch sử</h1>
   <p class="mo-ta">Xem lại trận đánh trên sa bàn, lật từng giai đoạn trên bản đồ, xoay mô hình 3D công trình và vũ khí, kéo các mốc trên trục thời gian.</p>
   <dl class="so-mp">{so}</dl>
  </div>
  <div class="bia-mp-holo">{sa_ban_holo()}</div>
 </div>
</section>
<main class="khung" id="danh-sach">
  <div class="loc-mp" role="group" aria-label="Lọc mô phỏng">
    <div class="hang-loc"><span class="nhan-loc">Loại</span><button type="button" class="nut-loc dang-chon" data-loc="tat-ca" aria-pressed="true">Tất cả ({len(ds)})</button>{loc}</div>
    <div class="hang-loc"><span class="nhan-loc">Lớp</span><button type="button" class="nut-loc dang-chon" data-lop="tat-ca" aria-pressed="true">Tất cả</button>{loc_lop}</div>
  </div>
  {"".join(phan)}
  <p class="khong-co" hidden>Chưa có mô phỏng nào khớp bộ lọc.</p>
</main>
{chan_trang_mp()}
<div class="thong-bao" role="status" aria-live="polite" hidden></div>
<script src="../chung/js/thu-vien.js"></script>
<script src="js/danh-sach.js"></script>
</body>
</html>
"""

def main():
    cat = doc("data/catalog/episodes.json")
    tat_ca = {e["ma"]: e for e in cat["tap"]}
    for ma, cfg in MO_HINH_MOI.items():
        if os.path.exists(os.path.join(OUT, "js", "mp", ma + ".js")):   # chỉ đưa vào khi đã có mã mô hình
            CAU_HINH[ma] = cfg
    for ma, spec, nhom in TU_DONG:
        assert ma not in CAU_HINH, ma
        CAU_HINH[ma] = cau_hinh_tu_dong(ma, spec, nhom)
        ghi(f"js/mp/{ma}.js", js_tu_dong(ma, CAU_HINH[ma]))
    eps = {ma: tat_ca[ma] for ma in CAU_HINH}
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
