# Nguồn âm thanh mô phỏng (SFX)

**Không dùng tệp âm thanh bên ngoài nào.** Toàn bộ âm nền và tiếng sự kiện của EduHistory Studio được **tổng hợp bằng toán**
(numpy/scipy) trong `pipeline/am_thanh/` – không có mẫu thu âm, không có thư viện BBC/RemArc, không có tệp Freesound –
nên không phát sinh vấn đề bản quyền. Tác giả mã: nhóm ChronoVibe cùng trợ lý AI lập trình (Claude), tháng 11/2026.

| Loại | Cách tạo (tóm tắt) |
|---|---|
| Âm nền (sông, biển, gió, mưa, rừng, đồng quê, côn trùng đêm, lửa, chiến trận xa, đám đông, chợ, cung điện, phòng, doanh trại, hang đá, phố, xưởng máy, tàu giữa biển) | tiếng ồn hồng/nâu lọc + điều biên ngẫu nhiên mượt; sóng vỗ, bọt nước (mô hình Minnaert), dế (sóng mang điều biên), giọng người xa (âm tiết có thanh điệu tiếng Việt + lọc formant) – mỗi loại là vòng lặp 20–32 s nối liền mạch |
| Trống trận, trống đồng, cồng chiêng, chuông chùa, gỗ, kim loại, gươm | tổng hợp dao động riêng (modal) theo tỉ lệ tần số của mặt trống tròn / chiêng núm / chuông |
| Mũi tên, gió cuốn, vút chuyển cảnh, lửa bùng, sóng | lọc dải thông có tần số tâm thay đổi theo thời gian (STFT) |
| Đàn tranh trong nhạc hiệu logo | tổng hợp cộng hoạ âm (thang ngũ cung, có “nhấn” luyến cao độ) |
| Vang (reverb) | đáp ứng xung tổng hợp (tiếng ồn tắt dần hàm mũ, đuôi tối dần) |

Vòng lặp nền tạo một lần và lưu đệm ở `renders/_cache/am_thanh/nen_<loại>_v<phiên bản>.wav` (có thể nghe trực tiếp).
Nếu sau này có thêm mẫu thu âm từ ngoài, CHỈ nhận mẫu CC0/phạm vi công cộng có giấy phép rõ ràng và ghi từng tệp vào bảng dưới đây.

| Tệp | Nguồn (đường dẫn) | Giấy phép | Ngày tải |
|---|---|---|---|
| (chưa có) | | | |
