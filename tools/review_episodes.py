"""Rà soát danh mục tập (sau build_episodes.py): sửa tên/nội dung sai hoặc chưa phù hợp, chuẩn hoá khung–hướng,
gắn cờ lưu ý sản xuất, xếp đợt sản xuất. Mọi chỉnh sửa ghi tường minh ở đây để tái lập được."""
import json, re
ROOT="/home/claude/eduhistory-studio"; F=f"{ROOT}/data/catalog/episodes.json"
d=json.load(open(F)); E=d["tap"]
# 1) Đánh số lại tập theo thứ tự trong từng bài (nháp L9-CD2 có hai tập số 1)
from collections import defaultdict
cnt=defaultdict(int)
for e in E:
    cnt[e["bai"]]+=1; e["so"]=cnt[e["bai"]]; e["ma"]=f"{e['bai']}-{e['so']:02d}"
by={e["ma"]:e for e in E}
# 2) Sửa tên tập (tránh giọng giật gân, đánh giá lệch, cách gọi chưa chuẩn)
TEN={
 "L6-B7-04":"Kim tự tháp và những phát minh của Ai Cập, Lưỡng Hà",
 "L8-B4-03":"Đông Nam Á dưới ách cai trị thực dân",
 "L8-B5-02":"Chiến tranh Nam – Bắc triều",
 "L8-B14-01":"Trung Quốc trước sự xâm lược của các nước đế quốc",
 "L8-B14-03":"Duy tân Minh Trị: Nhật Bản cải cách toàn diện",
 "L9-B1-03":"Liên Xô xây dựng chủ nghĩa xã hội: những thành tựu",
 "L9-B1-04":"Nhìn lại thành tựu và hạn chế của Liên Xô",
 "L9-B10-04":"Nguyên nhân sụp đổ của chế độ xã hội chủ nghĩa ở Liên Xô và Đông Âu",
 "L9-B17-03":"Chiến lược Việt Nam hoá chiến tranh và cuộc chiến đấu của quân dân ta",
 "L9-B18-04":"Thế giới đa cực: cơ hội và thách thức",
 "L6-B12-03":"Thử thách: Em có phải là thương nhân cổ đại?",
 "L6-B4-04":"Thử thách: Em có phải là nhà khảo cổ?",
}
for k,v in TEN.items(): by[k]["ten_tap"]=v
# 3) Sửa nội dung/kiến thức chốt đã đối chiếu OCR SGK
by["L7-B14-04"]["noi_dung"]=("Diễn biến cuộc kháng chiến lần thứ ba (1287–1288): trận Vân Đồn – Cửa Lục chặn đoàn thuyền lương, "
                             "rồi trận Bạch Đằng: bãi cọc ngầm, nước triều rút và kế hoả công tiêu diệt thuỷ quân Nguyên (SGK LS7 tr. 72).")
by["L9-B12-05"]["kien_thuc_chot"]=["1947: Ấn Độ được hưởng quy chế tự trị (kế hoạch Mao-bát-tơn)",
    "26-1-1950: thành lập nước Cộng hoà Ấn Độ","Thành công của 'Cách mạng xanh'","Chế tạo bom nguyên tử (1974), phóng vệ tinh (1975)"]
by["L6-B14-03"]["kien_thuc_chot"]=["Thành xây theo hình xoáy trôn ốc, ba vòng khép kín","Tổng chiều dài khoảng 16 000 m","Lẫy nỏ, mũi tên đồng tìm thấy ở Cổ Loa"]
by["L7-B14-04"]["kien_thuc_chot"]=["Trần Khánh Dư phục kích đoàn thuyền lương ở Vân Đồn – Cửa Lục","Trận Bạch Đằng (4-1288): bãi cọc ngầm, nước triều rút, kế hoả công","Ô Mã Nhi bị bắt sống"]
# 3b) Sửa trang SGK khi viết kịch bản chi tiết phát hiện lệch (đối chiếu OCR)
TRANG={"L6-B18-04":[83,84,85],"L6-B14-03":[61,62]}
for k,v in TRANG.items(): by[k]["trang_sgk"]=v
# 3c) Khung thời lượng chỉnh theo lượng kiến thức SGK thực có (không kéo dài bằng chi tiết ngoài SGK)
KHUNG={"L6-B14-03":"2-3p"}
for k,v in KHUNG.items(): by[k]["khung"]=v
# 4) Chuẩn hoá khung – hướng: 60s dọc (mạng xã hội); 2–5 phút ngang (bản đồ, diễn biến). Mỗi tập ngang có thêm 1 bản cắt dọc 60s.
for e in E:
    e["huong"]="doc" if e["khung"]=="60s" else "ngang"
    e["ban_cat_doc"]= e["khung"]!="60s"
# 5) Cờ lưu ý sản xuất
LANH_TU=re.compile(r"Hồ Chí Minh|Nguyễn Ái Quốc|Nguyễn Tất Thành|\bBác\b|Chủ tịch")
CHU_QUYEN=re.compile(r"Hoàng Sa|Trường Sa|biển đảo|Biển Đông|chủ quyền|biên giới|Gạc Ma|đường cơ sở|vịnh Bắc Bộ")
for e in E:
    txt=" ".join([e["ten_tap"],e["noi_dung"],*e["kien_thuc_chot"],e.get("mo_phong") or ""])
    f=[]
    if LANH_TU.search(txt): f.append("lãnh tụ: không vẽ AI chân dung, chỉ dùng ảnh tư liệu công cộng hoặc biểu tượng")
    if CHU_QUYEN.search(txt): f.append("chủ quyền: bản đồ vẽ bằng code từ dữ liệu chuẩn, đủ Hoàng Sa – Trường Sa; GV duyệt kĩ lời dẫn")
    if e["lop"]==9 and re.search(r"19[4-9]\d|20\d\d", txt) and not f: f.append("lịch sử hiện đại: lời dẫn bám sát cách diễn đạt SGK")
    e["luu_y"]=f
# 6) Ưu tiên: các nội dung thầy nêu là trọng tâm mô phỏng (bố trí trận địa, xây Kim tự tháp)
by["L6-B7-04"]["uu_tien"]="P1"
# 7) Đợt sản xuất. Đợt 1 = tập tiêu biểu (trận địa, công trình, bước ngoặt) dùng cho vòng trường 12/2026.
DOT1=["L6-B3-03","L6-B7-04","L6-B14-03","L6-B18-04","L7-B12-02","L7-B14-02","L7-B14-04","L7-B16-05","L7-CD1-03",
      "L8-B2-03","L8-B3-02","L8-B8-02","L8-B8-03","L9-B4-03","L9-B8-04","L9-B15-03","L9-B17-05"]
for e in E:
    e["dot"]=1 if e["ma"] in DOT1 else {"P1":2,"P2":3,"P3":4}[e["uu_tien"]]
PHUT={"60s":1,"2-3p":2.5,"4-5p":4.5}
d["so_tap"]=len(E); d["tong_phut_uoc"]=sum(PHUT[e["khung"]] for e in E)
d["ghi_chu"]=("Danh mục đã rà soát. trang_sgk = trang in (đối khớp OCR). Kiến thức chốt là định hướng; "
              "khi viết kịch bản, từng câu được đối chiếu lại trang SGK và GV duyệt.")
json.dump(d, open(F,"w"), ensure_ascii=False, indent=1)
from collections import Counter
print(d["so_tap"], "tập; ước", d["tong_phut_uoc"], "phút")
print(Counter(e["dot"] for e in E), Counter(e["huong"] for e in E), Counter(e["khung"] for e in E))
print("lưu ý:", Counter(x.split(":")[0] for e in E for x in e["luu_y"]))
