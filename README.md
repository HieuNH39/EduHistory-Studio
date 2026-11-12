# EduHistory Studio

Hệ thống học liệu Lịch sử lớp 6–9 bằng video kể chuyện, video mô phỏng dựng bằng code, mô phỏng tương tác và website học tập có trợ lý hỏi đáp AI.

Dự án dự thi **FPT School STEMPETITION 2027** – Tiểu ban Nghiên cứu khoa học, bảng THCS, Challenge 3 Smart Education.
Đội **ChronoVibe** – Trường TH, THCS & THPT FPT Bắc Giang. Giáo viên hướng dẫn: Nguyễn Hữu Hiệu, Trần Khánh Ly.

## Nguồn kiến thức
Bộ SGK *Lịch sử và Địa lí* 6–9 (Kết nối tri thức với cuộc sống), bộ sách dùng chung toàn quốc từ năm học 2026–2027.
Kho dữ liệu chỉ lưu **dữ kiện đã diễn đạt lại kèm số trang** để đối chiếu; không lưu và không công bố nguyên văn sách.

## Cấu trúc
| Thư mục | Nội dung |
| --- | --- |
| `brand/` | Logo, bộ nhận diện, nhân vật dẫn chuyện |
| `assets/fonts/` | Phông Be Vietnam Pro, Playfair Display (giấy phép SIL OFL 1.1) |
| `data/catalog/` | Danh mục bài học, chuỗi video, mô phỏng |
| `data/kb/` | Kho dữ kiện SGK (diễn đạt lại, có số trang) |
| `pipeline/` | Mã dựng video tự động: giọng đọc, phụ đề song ngữ, ghép hình, nhạc, logo |
| `web/` | Website EduHistory Studio (GitHub Pages) |
| `tools/` | Công cụ xử lý: OCR, trích dữ kiện, gọi Gemini |
| `docs/vibe-coding/` | Nhật ký Vibe Coding: yêu cầu → kết quả AI → lỗi phát hiện → cách sửa |

## Nguyên tắc
1. **Phân tầng chính xác:** AI tạo sinh chỉ vẽ lớp minh họa; bản đồ, niên đại, số liệu, chữ trên hình dựng bằng code từ dữ liệu đã thẩm định.
2. **Mọi câu đều có nguồn:** mỗi câu lời thoại gắn lớp – bài – trang SGK.
3. **Giáo viên thẩm định cuối cùng** trước khi sản xuất và trước khi đăng.
4. Bí mật (API key) chỉ nằm trong `.env`, không bao giờ đưa lên kho mã.
