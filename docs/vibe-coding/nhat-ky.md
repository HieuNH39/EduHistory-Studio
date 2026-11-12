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
| 11 | Chọn giọng đọc: thử Gemini TTS nhiều cặp giọng | Không tự nghe được âm thanh | Dùng Gemini nghe – chép lại để đo tỉ lệ lỗi từ (WER) và chấm độ tự nhiên: cặp Puck/Leda đạt WER 1,5 %, tự nhiên 10/10 → chọn làm giọng Nhật Minh/Hân Hân |
| 12 | Viết bộ dựng video tự động (`pipeline/render.py`): giọng đọc → hình chuyển động → phụ đề song ngữ → logo → nhạc → chuẩn âm lượng | Phụ đề tiếng Anh bị đẩy lên TRÊN tiếng Việt (thư viện phụ đề tự tránh chồng chữ) | Đặt phụ đề tiếng Anh ở lớp riêng, tính lại khoảng cách; kiểm tra bằng ảnh cắt từ video |
| 13 | Gắn logo góc màn hình | Chữ trắng của logo không đọc được trên nền sáng | Thêm nền viên thuốc xanh đậm bán trong suốt cho logo |
| 14 | Đường dẫn ảnh trong kịch bản | Lỗi không tìm thấy tệp do đường dẫn tương đối | Quy mọi đường dẫn về thư mục gốc dự án |
