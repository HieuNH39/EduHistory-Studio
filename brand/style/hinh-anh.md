# Quy chuẩn hình ảnh EduHistory Studio

## Phân tầng
| Lớp hình | Công cụ | Dùng cho | Ràng buộc |
|---|---|---|---|
| Bản đồ, sơ đồ, mốc thời gian, số liệu, chữ trên hình | Code (pipeline/maps, render) | mọi thông tin cần chính xác | dữ liệu theo lược đồ SGK; bản đồ Việt Nam luôn đủ Hoàng Sa – Trường Sa |
| Cảnh minh hoạ, bối cảnh, đám đông, công trình | Ảnh AI (Gemini) | không khí, trang phục, không gian | không chữ, không cờ có chữ, không logo; không cận mặt nhân vật lịch sử |
| Cảnh chuyển động then chốt | Video AI (Kling) từ ảnh đã duyệt | 1–3 cảnh/tập | 5–10 giây, không thêm chi tiết lịch sử mới |
| Người dẫn chuyện | Ảnh AI theo bảng nhân vật v5 | mở – nối – kết tập; vài cảnh “du hành” vào bối cảnh lịch sử | Nhật Minh, Hân Hân 15 tuổi, polo cam FPT viền trắng, quần/váy kaki nâu nhạt |
| Nhân vật lịch sử (đến hết thời phong kiến) | Ảnh AI theo bảng thiết kế riêng từng nhân vật (brand/characters/lich-su) → Kling | cảnh tái hiện có hành động, lời thoại | thầy duyệt bảng thiết kế trước khi dùng; dùng thống nhất ở mọi tập |
| Lãnh tụ, nhân vật thời hiện đại | Ảnh, phim tư liệu công cộng (phục chế màu, chuyển động máy quay) | các bài lịch sử hiện đại | KHÔNG vẽ AI; AI chỉ dùng cho bộ đội, nhân dân nói chung |

## Phong cách ảnh AI (dán vào cuối mọi lệnh tạo ảnh)
`Style: painterly 2.5D historical illustration for a Vietnamese secondary-school history video, rich but soft colors, warm cinematic light, clear readable composition, no text, no letters, no logos, no watermark. Aspect ratio 16:9.` (tập dọc: 9:16)

## Quy tắc nội dung
- Nhân vật lịch sử thời phong kiến: vẽ theo bảng thiết kế đã duyệt, thần thái nghiêm trang, trang phục đúng thời; được cận cảnh khi có bảng thiết kế.
- Lãnh tụ, nhân vật thời hiện đại: không vẽ AI; dùng ảnh/phim tư liệu công cộng.
- Quân đội nước ngoài: không biếm hoạ, không bôi nhọ dân tộc khác.
- Không cảnh máu me; chiến trận thể hiện bằng khói, lửa, đội hình, cờ.

## Cấu trúc một tập (quyết định của GVHD, 13/11/2026)
1. **Dẫn chuyện** (Minh – Hân ở hiện tại): mở đầu, nối đoạn, giải thích, câu hỏi cuối — khoảng 20–30 % thời lượng.
2. **Du hành**: ở 1–2 cảnh then chốt, hai bạn bước qua “cổng thời gian trống đồng” vào bối cảnh lịch sử, chỉ đứng quan sát, không can thiệp sự kiện.
3. **Tái hiện**: cảnh phim có nhân vật lịch sử, hành động, âm thanh hiện trường; Minh – Hân thuyết minh lồng tiếng.
4. **Sa bàn**: bản đồ/sơ đồ động vẽ bằng code, xen kẽ với cảnh tái hiện.

## Lời thoại nhân vật lịch sử
- Được dựng đối thoại để câu chuyện sinh động. Lời thoại không được trái SGK, không đưa thêm số liệu, tên người, địa danh, sự kiện mà SGK không có.
- Số liệu, mốc thời gian, kết quả, ý nghĩa: do người dẫn chuyện nói, có trang SGK đi kèm.
- Cuối mỗi video có dòng: “Lời thoại của nhân vật lịch sử mang tính tái hiện; nội dung dựa trên SGK Lịch sử và Địa lí [lớp], Bài [x], tr. [..].”
