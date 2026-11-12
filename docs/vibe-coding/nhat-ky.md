# Nhật ký Vibe Coding – EduHistory Studio

Ghi lại các phiên làm việc thật giữa người hướng dẫn và trợ lý AI lập trình (Claude): yêu cầu bằng ngôn ngữ tự nhiên → AI làm gì → kiểm tra thấy lỗi gì → sửa thế nào.
Mỗi mục có thể đối chiếu với lịch sử commit của kho mã.

## Phiên 1 – 12–13/11/2026: Khởi động dự án

**Yêu cầu:** đọc thể lệ STEMPETITION 2027, lập quy trình tổng thể; số hóa 4 cuốn SGK Lịch sử và Địa lí 6–9 (PDF ảnh scan) để làm kho dữ liệu đối chiếu.

| # | AI làm | Lỗi / vấn đề phát hiện khi kiểm tra | Cách xử lý |
| --- | --- | --- | --- |
| 1 | Thử giọng đọc tiếng Việt bằng thư viện edge-tts | Kết nối bị từ chối (dịch vụ dùng WebSocket, môi trường chặn) | Chuyển sang mô hình giọng Piper chạy offline làm phương án dự phòng; giọng chính dùng Vbee/FPT.AI |
| 2 | Kiểm tra PDF SGK | PDF chỉ chứa ảnh, không có lớp chữ | Viết script OCR Tesseract tiếng Việt chạy song song 2 luồng, 503 trang |
| 3 | Chép lại trang SGK bằng Gemini (đọc ảnh) | Mô hình lặp một chữ hàng trăm lần (“quá quá quá…”) | Viết bộ phát hiện lặp bằng biểu thức chính quy, tự chép lại trang lỗi với cấu hình khác |
| 4 | Tiếp tục chép nguyên văn | Gemini dừng với lý do RECITATION (nội dung có bản quyền) | Đổi thiết kế: không chép nguyên văn, chỉ **trích dữ kiện diễn đạt lại + số trang** – đúng nguyên tắc bản quyền của dự án |
| 5 | Chạy hàng loạt trên Gemini | Hết hạn mức miễn phí theo ngày của mô hình | Kho dữ kiện dựng từ OCR Tesseract + trợ lý AI trích theo từng bài; Gemini dùng cho kiểm tra chéo và trợ lý hỏi đáp |
| 6 | Tải phông chữ Be Vietnam Pro | Bản phân phối tách riêng bộ chữ Latin và tiếng Việt | Dùng fonttools gộp các phần thành một phông đầy đủ dấu tiếng Việt |
| 7 | Thiết kế 3 phương án logo bằng mã SVG | – | Kết xuất PNG nền sáng/tối để giáo viên chọn |
| 8 | Dò đầu bài tự động trên văn bản OCR (tìm cụm “Học xong bài này”) | Bỏ sót bài có trang đầu OCR kém; tiêu đề mục lẫn câu hỏi bài tập | Đối chiếu với ảnh mục lục SGK, chốt danh mục 78 bài + 7 chủ đề chung vào `data/catalog/lessons.json` |
| 9 | Thử dùng trình duyệt trong ứng dụng Claude để tạo ảnh trên Gemini | Trình duyệt tích hợp không gắn được vào cuộc trò chuyện đang chạy | Chuyển sang tiện ích Claude in Chrome trên máy giáo viên |
| 10 | Tạo bảng thiết kế hai nhân vật trên Gemini (qua trình duyệt) | Lần 1 đồng phục sai (áo trắng, quần xanh); máy tính bảng có logo thương hiệu; bạn nữ trông nhỏ tuổi hơn | Sửa theo yêu cầu giáo viên: áo polo cam FPT, quần/váy nâu, 15 tuổi; xóa logo trên đạo cụ (bản v4) |
| 11 | Chọn giọng đọc: thử Gemini TTS nhiều cặp giọng | Không tự nghe được âm thanh | Dùng Gemini nghe – chép lại để đo tỉ lệ lỗi từ (WER) và chấm độ tự nhiên: cặp Puck/Leda đạt WER 1,5 %, tự nhiên 10/10; giáo viên nghe và đổi giọng nữ sang Zephyr (nhẹ, thanh hơn) → chốt Puck (Nhật Minh) – Zephyr (Hân Hân) |
| 12 | Viết bộ dựng video tự động (`pipeline/render.py`): giọng đọc → hình chuyển động → phụ đề song ngữ → logo → nhạc → chuẩn âm lượng | Phụ đề tiếng Anh bị đẩy lên TRÊN tiếng Việt (thư viện phụ đề tự tránh chồng chữ) | Đặt phụ đề tiếng Anh ở lớp riêng, tính lại khoảng cách; kiểm tra bằng ảnh cắt từ video |
| 13 | Gắn logo góc màn hình | Chữ trắng của logo không đọc được trên nền sáng | Thêm nền viên thuốc xanh đậm bán trong suốt cho logo |
| 14 | Đường dẫn ảnh trong kịch bản | Lỗi không tìm thấy tệp do đường dẫn tương đối | Quy mọi đường dẫn về thư mục gốc dự án |
| 15 | Gộp nháp 359 tập thành danh mục chính thức (`tools/build_episodes.py`, `tools/review_episodes.py`) | AI soạn nháp ghi lẫn số trang PDF và số trang in; một bài có hai tập cùng số 1;  vài tên tập giật gân hoặc đánh giá lệch | Xác định lại trang SGK bằng đối khớp cụm từ với văn bản OCR từng trang; đánh số lại; đối chiếu OCR để sửa kiến thức; đổi tên tập theo cách diễn đạt của SGK; gắn cờ lưu ý (lãnh tụ, chủ quyền, lịch sử hiện đại) để giáo viên duyệt kĩ |
| 16 | Kịch bản kiểu mới (dẫn chuyện – du hành – tái hiện – sa bàn) và bộ dựng nâng cấp | Gemini TTS chỉ đọc tối đa 2 giọng/lần; hạn mức miễn phí hết sau vài chục lượt; lỗi 502 từ proxy | Chia lời thành nhóm ≤2 người nói rồi nối; tự chuyển sang mô hình giọng dự phòng khi hết hạn mức; thử lại khi 502 |
| 17 | Sa bàn trận Rạch Gầm – Xoài Mút vẽ bằng code (`pipeline/maps/saban.py`) theo Lược đồ hình 8.4 SGK | Bản đầu: chú giải đè lên địa danh Mỹ Tho; ký hiệu mũi tên trong chú giải không hiện (đổi toạ độ hai lần); ký tự “≈” không có trong phông | Dời chú giải sang trái, thêm tham số toạ độ màn hình, đổi nhãn thành “khoảng 6 km”; kiểm tra bằng ảnh khung hình |
| 18 | Lấy ảnh từ Gemini về máy không cần giáo viên bấm lưu | Trình duyệt trong app luôn hỏi nơi lưu; trang Gemini chặn gửi ảnh ra ngoài (CSP); Chrome chặn tải nhiều tệp liên tiếp | Chuyển sang Chrome (Claude in Chrome), tải về tự động; đưa ảnh tham chiếu vào Gemini bằng cách tạo ô chọn tệp ẩn rồi “dán” ảnh vào khung chat; ghép nhiều ảnh tham chiếu thành 1 tệp |
| 19 | Giọng đọc miễn phí bằng VieNeu-TTS v3 Turbo (`pipeline/tts_vieneu.py`) | ONNX Runtime từ chối mô hình vì tệp dữ liệu nằm khác thư mục (bộ nhớ đệm HuggingFace dùng liên kết tượng trưng) | Tải mô hình về thư mục riêng và thay liên kết bằng tệp thật; nhân bản giọng Puck/Zephyr đã duyệt; kiểm tra tự động bằng Gemini nghe – chép lại (khớp 98 %) |
| 20 | Tự động tạo ảnh cảnh trên Gemini (Chrome) theo bảng nhân vật | Lệnh JavaScript bị cắt sau 45 giây; Chrome chặn tải tệp thứ hai trên cùng một lần mở trang; nút tải chỉ hiện khi rê chuột | Tách thành “gửi lệnh” và “chờ ảnh” ngắn; tải lại trang trước mỗi lần tải ảnh; dùng nút thật thay vì bấm bằng mã |
| 21 | Rà lại kiến thức khi viết kịch bản tập Bạch Đằng 1288 | Ở bước rà danh mục (mục 15), Claude đã bỏ chi tiết “kế hoả công” vì cho là AI soạn nháp bịa – nhưng SGK LS7 tr. 72 có ghi rõ kế hoả công | Khôi phục chi tiết; quy tắc mới: mọi chỉnh sửa kiến thức phải dẫn được dòng SGK (OCR) làm căn cứ, không sửa theo trí nhớ |
