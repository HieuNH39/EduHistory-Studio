# EduHistory Studio – Thông tin chung dùng cho mọi tài liệu hồ sơ (một nguồn duy nhất)

Cập nhật: 14/11/2026. Số liệu định lượng LUÔN lấy từ `data/thong_ke/du_an.json` (chạy lại `python3 tools/thong_ke_du_an.py` trước khi chốt). Không tự bịa số liệu; số liệu chưa có thì ghi "đang thu thập" / để ô trống có ghi chú.

## Định danh
- Cuộc thi: FPT School STEMPETITION 2027 – "Vibe ý tưởng, Làm chủ công nghệ, Kiến tạo tương lai".
- Vòng cấp trường (10–12/2026): 5 phút thuyết trình + 5 phút hỏi đáp với BGK. Báo cáo dự án ngày thứ Tư 18/11/2026; chung kết cấp trường 26/12/2026.
- Tiểu ban: **Nghiên cứu khoa học** (bảng THCS). Challenge chính: **Challenge 3 – Smart Education**; giá trị bổ trợ: Challenge 5 – Future Technology. SDG 4.
- Đề tài (giữ đúng tên đã đăng ký): **EduHistory Studio: Số hóa bài học Lịch sử qua hệ thống video AI đa nền tảng** (sản phẩm: EduHistory Studio; gồm chuỗi video, mô phỏng tương tác và kho học liệu số).
- Trường: Trường Tiểu học, THCS và THPT FPT Bắc Giang (tỉnh Bắc Ninh). Đội: **ChronoVibe**.
- Học sinh: Trần Hà Thu Hoài (8A1), Nguyễn Thị Kim Phượng (8A1), Trần Ngọc Như Ý (6E1).
- GVHD: thầy Nguyễn Hữu Hiệu, cô Trần Khánh Ly.

## Bài toán thực tiễn
- Kiến thức Lịch sử nhiều niên đại, nhân vật, diễn biến trận đánh → khó hình dung, khó nhớ lâu; SGK là văn bản tĩnh, lược đồ tĩnh.
- Giáo viên thiếu thời gian/kỹ năng làm video hoạt hình chất lượng (một video 3–5 phút làm thủ công mất nhiều giờ).
- Học sinh tiêu thụ video ngắn (TikTok/Shorts) nhưng dễ gặp nội dung "chế sử", sai lệch.

## Sản phẩm (đã có, vận hành thật)
1. **Hệ thống sản xuất video tự động (AI pipeline + Vibe Coding)**: kịch bản đối chiếu SGK → tranh nhân vật/bối cảnh (Gemini), clip chuyển động (Kling, Gemini) hoặc chuyển động bằng code 2.5D (độ sâu, khẩu hình, nháy mắt, lửa – nước – cờ) → giọng đọc VieNeu-TTS (2 giọng dẫn chuyện cố định + giọng riêng cho nhân vật lịch sử) → sa bàn động vẽ lại theo lược đồ SGK → âm thanh mô phỏng tổng hợp (34 hiệu ứng sự kiện, 19 âm nền, 11 âm giao diện, tự thiết kế theo cảnh và theo từng bước sa bàn) → phụ đề song ngữ Việt trên – Anh dưới, logo dự án → chuẩn âm lượng −14 LUFS.
2. **Chuỗi video Lịch sử 6–9**: danh mục 359 tập/85 bài (~919 phút), 3 khung: 4–5 phút ngang, 2–3 phút ngang, 60 giây dọc (TikTok/Shorts). Cấu trúc tập: hai bạn dẫn chuyện Nhật Minh – Hân Hân (HS FPT, áo polo cam) → du hành về quá khứ (chỉ quan sát) → tái hiện có nhân vật lịch sử (lời thoại tái hiện, ghi rõ) → sa bàn động → trục thời gian, thẻ ghi nhớ → câu hỏi dừng hình A/B/C → thử thách bình luận.
3. **17 mô phỏng tương tác** (web/mo-phong): bản đồ động 2D (Bạch Đằng 938, 1288, Rạch Gầm – Xoài Mút, Ngọc Hồi – Đống Đa, Chi Lăng – Xương Giang, kháng chiến 1258, Điện Biên Phủ, Xuân 1975), 3D Three.js (thành Cổ Loa, kim tự tháp, phòng tuyến Như Nguyệt, máy hơi nước, quả địa cầu hành trình Ma-gien-lăng), trục thời gian kéo thả (Công lịch, CTTG II, Tổng khởi nghĩa 1945, Cách mạng Pháp). Mọi trang có âm thanh tổng hợp + nút tắt tiếng + câu hỏi.
4. **Kho học liệu số (website tĩnh, web/)**: theo lớp → bài → tập; tìm kiếm có/không dấu; trang tập: video, trang SGK, ghi nhớ, mini-quiz chấm tự động có giải thích + trang SGK, bản chép lời song ngữ, liên kết mô phỏng. Không đăng nhập, không cookie, không theo dõi, chạy offline.
5. **Minh chứng Vibe Coding**: nhật ký `docs/vibe-coding/nhat-ky.md` (các phiên, mỗi dòng: AI làm gì → lỗi phát hiện → cách sửa), lịch sử commit GitHub (HieuNH39/EduHistory-Studio), nhật ký prompt Kling/Gemini (`data/kling/nhat_ky_kling.jsonl`, `data/gemini/`), nhật ký máy dựng (`data/logs/san-xuat.jsonl`).

## Cơ chế chống "bịa đặt" (anti-hallucination) – có số liệu thật
- Số hoá 4 cuốn SGK (OCR Tesseract tiếng Việt 503+ trang) làm kho đối chiếu (bản riêng tư, không công bố).
- Mỗi cảnh ghi `nguon_trang` (trang SGK); công cụ `tools/kiem_tra_kich_ban.py` tự soát: nguồn trang, số liệu/năm có trong trang SGK, đáp án, giọng.
- Số kịch bản phát hiện và sửa sai lệch của bản nháp danh mục so với SGK: xem `kich_ban.so_kich_ban_phat_hien_sai_lech_danh_muc` (ví dụ: "Thái thượng hoàng" → SGK ghi "Thượng hoàng"; 1226 không phải 1228; Bô-rô-bu-đua là công trình Phật giáo chứ không phải "đền núi"; "viên ngọc quý" không có trong SGK → bỏ…).
- Quy tắc: không sửa kiến thức theo trí nhớ; số liệu OCR sót thì đọc ảnh trang SGK và ghi chú.
- Kiểm tra giọng đọc tự động: Gemini nghe – chép lại, khớp ~98 %.
- Nguyên tắc hình ảnh: không vẽ chân dung lãnh tụ Việt Nam bằng AI; nhân vật hiện đại chỉ dùng ảnh tư liệu thật (phạm vi công cộng/CC, ghi nguồn trên hình); bản đồ có Việt Nam luôn có Hoàng Sa, Trường Sa; bản đồ thế giới không vẽ biên giới.
- Người duyệt cuối: GVHD (đã uỷ quyền Claude tự duyệt theo quy tắc trên từ 13/11; mọi chỉnh sửa có ghi chú đối chiếu).

## Câu hỏi nghiên cứu
- Chính: Học tập bằng chuỗi video trực quan hoá + mô phỏng tương tác của EduHistory Studio có giúp HS THCS ghi nhớ mốc sự kiện, hiểu bản chất diễn biến lịch sử và hứng thú học tập hơn so với học bằng SGK/bài giảng thông thường không?
- Phụ: (1) Quy trình AI + Vibe Coding rút ngắn thời gian sản xuất một video chuẩn hoá bao nhiêu? (2) Mức độ chính xác học thuật của video sau bước kiểm chứng đạt ra sao? (3) Mức độ dễ dùng (SUS) của kho học liệu và mô phỏng? (4) Video ngắn trên mạng xã hội tác động thế nào đến việc tự tìm hiểu Lịch sử ngoài giờ?

## Giả thuyết (thống nhất với bộ công cụ thực nghiệm)
- H1: Điểm tiến bộ (hậu – tiền kiểm tra) của nhóm thực nghiệm cao hơn nhóm đối chứng có ý nghĩa thống kê (p < 0,05); điểm hậu kiểm tra cao hơn ít nhất 15 %.
- H2: Sau 7 ngày, nhóm thực nghiệm giữ lại kiến thức tốt hơn (mức giảm điểm ít hơn).
- H3: Điểm hứng thú (phiếu 12 câu Likert) của nhóm thực nghiệm cao hơn nhóm đối chứng.
- H4: Điểm SUS của kho học liệu và mô phỏng đạt từ 68 trở lên (mức "tốt").
- H5 (kỹ thuật): Quy trình AI + Vibe Coding rút ngắn thời gian sản xuất một video chuẩn hoá trên 70 % so với làm thủ công (đo bằng nhật ký máy dựng `data/logs/san-xuat.jsonl` so với ước lượng làm thủ công do GV khảo sát – số liệu so sánh đang thu thập, không tự đặt số).

## Thiết kế thực nghiệm sư phạm (thống nhất cho mọi tài liệu)
- Dạng: thực nghiệm nhóm đối chứng không tương đương, có tiền – hậu kiểm tra + kiểm tra duy trì sau 7 ngày.
- Đối tượng: 2 lớp khối 7 (40–50 HS), một lớp thực nghiệm, một lớp đối chứng; HS ẩn danh bằng mã số; không tính vào điểm chính thức; BGH phê duyệt.
- Nội dung: Lịch sử 7 – Bài 14 "Ba lần kháng chiến chống quân xâm lược Mông – Nguyên (thế kỉ XIII)" (đã có video L7-B14-02 kháng chiến 1258, L7-B14-04 Bạch Đằng 1288 và mô phỏng tương ứng).
- Nhóm thực nghiệm: tiết học có video + mô phỏng + mini-quiz; nhóm đối chứng: cùng GV, cùng thời lượng, học bằng SGK + bài giảng thường.
- Công cụ: đề kiểm tra 20 câu (tiền/hậu, hai đề tương đương), phiếu hứng thú 12 câu Likert 5 mức, thang SUS 10 câu (chỉ nhóm thực nghiệm), phỏng vấn nhóm 6 HS.
- Phân tích: thống kê mô tả, kiểm định t độc lập trên điểm tiến bộ, t ghép cặp trong từng nhóm, cỡ hiệu ứng Cohen's d, Cronbach's alpha cho phiếu hứng thú; script phân tích viết bằng Vibe Coding.
- Lịch: 18–19/11 duyệt công cụ, xin phép BGH, thông báo phụ huynh; 23/11 phiếu hứng thú lần 1 + tiền kiểm tra; 24–25/11 hai tiết học; 26/11 hậu kiểm tra + hứng thú lần 2 + SUS + phỏng vấn nhóm; 03/12 kiểm tra duy trì; 04–10/12 phân tích; cập nhật báo cáo trước 15/12.
- Học liệu nhóm thực nghiệm: 5 tập video Bài 14 (L7-B14-01 … L7-B14-05), mô phỏng kháng chiến 1258 và Bạch Đằng 1288, mini-quiz trên kho học liệu. Bộ công cụ chi tiết: Claude Docs "EduHistory Studio – Bộ công cụ thực nghiệm sư phạm (Lịch sử 7, Bài 14)" (đề kiểm tra 2 đề × 20 câu: 10 nhận biết, 7 thông hiểu, 3 vận dụng, mỗi câu 0,5 điểm).
- **Kết quả thực nghiệm chưa có tại thời điểm 14/11/2026 – tuyệt đối không điền số giả.** Ô kết quả ghi: "sẽ cập nhật sau thực nghiệm (23/11–03/12/2026)".

## Kế hoạch (cập nhật)
- 05/10–10/11: đề cương, nghiên cứu, danh mục 359 tập, thiết kế nhân vật, hệ thống dựng (đã xong).
- 11/11–17/11: sản xuất Đợt 1 (17 tập tiêu biểu) + kịch bản Đợt 2; mô phỏng; website (đang làm).
- 18/11: báo cáo tiến độ dự án.
- 23/11–03/12: thực nghiệm sư phạm; đăng thử video 60 giây lên TikTok/YouTube Shorts (kênh của GVHD).
- 03/12–15/12: hoàn thiện toàn bộ video, phân tích số liệu, báo cáo hoàn chỉnh, video demo.
- 26/12/2026: vòng chung kết cấp trường.

## Căn cứ pháp lý, bản quyền, an toàn dữ liệu
- Chương trình GDPT 2018 môn Lịch sử và Địa lí (Thông tư 32/2018/TT-BGDĐT); bộ SGK dùng chung toàn quốc năm học 2026–2027 (Lịch sử và Địa lí 6–9).
- Luật Sở hữu trí tuệ: hình ảnh/clip do AI tạo mới hoặc tư liệu phạm vi công cộng/giấy phép mở (ghi nguồn); không chép nguyên văn SGK; nhạc nền Pixabay; phông OFL; âm thanh tự tổng hợp bằng code.
- Bảo vệ dữ liệu cá nhân (Luật 91/2025/QH15, Nghị định 356/2025/NĐ-CP): website không đăng nhập, không cookie theo dõi; không đưa ảnh học sinh thật vào công cụ AI; khoá API chỉ để trong tệp .env, không công khai.
- Điều khoản AI: giữ dấu "KlingAI"/dấu Gemini trên clip; mọi kịch bản qua kiểm chứng trước khi phát hành.

## Tài liệu tham khảo chọn lọc
- Bộ GD&ĐT (2018). Chương trình GDPT 2018 – Lịch sử và Địa lí.
- Mayer, R. E. (2002/2009). Multimedia learning. Cambridge University Press.
- Sweller, J. (1988). Cognitive load during problem solving. Cognitive Science, 12(2), 257–285.
- Chi, M. T. H., & Wylie, R. (2014). The ICAP framework. Educational Psychologist, 49(4), 219–243.
- Brooke, J. (1996). SUS: A "quick and dirty" usability scale.
- Bangor, A., Kortum, P., & Miller, J. (2009). Determining what individual SUS scores mean. Journal of Usability Studies, 4(3), 114–123.
- Cohen, J. (1988). Statistical power analysis for the behavioral sciences (2nd ed.).
- FPT Schools (2026). Kế hoạch STEMPETITION 2027.
