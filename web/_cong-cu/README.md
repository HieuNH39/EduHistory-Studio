# Kho học liệu số – cách cập nhật và xuất bản video

Website tĩnh, không cần cài đặt hay bước "build": mở thẳng `web/index.html` bằng trình duyệt (file://) hoặc đăng lên GitHub Pages.
Không đăng nhập, không cookie, không theo dõi; phông chữ và hình ảnh nằm sẵn trong `web/`.

| Đường dẫn | Nội dung | Ai tạo |
| --- | --- | --- |
| `web/index.html` | Thư viện: chọn lớp → bài → tập, tìm kiếm, lọc theo thời lượng và tình trạng | công cụ |
| `web/tap/<MA>.html` | Trang từng tập: video, SGK và số trang, ghi nhớ, mốc thời gian, luyện tập nhanh, lời thoại, mô phỏng | công cụ |
| `web/gioi-thieu.html` | Giới thiệu dự án (số liệu tự tính từ dữ liệu) | công cụ |
| `web/du-lieu/thu-vien.json` | Danh mục máy đọc được (cho công cụ, ứng dụng khác) | công cụ |
| `web/du-lieu/anh-bia/<MA>.jpg` | Ảnh bìa 640×360 – tự tạo một lần, có thể thay bằng ảnh của mình (công cụ không ghi đè) | công cụ / người |
| `web/du-lieu/lien-ket.json` | Link YouTube, TikTok của từng tập | **người sửa** |
| `web/videos/` | Tệp video `<MA>.mp4` cho dùng tại lớp – **không đưa lên git** | công cụ (liên kết tới `renders/v1`) |
| `web/chung/` | CSS, JS, phông, logo dùng chung | người viết |
| `web/_cong-cu/cau-hinh.json` | Cấu hình: thư mục video nguồn, cách đưa video vào web | người sửa |

## Cập nhật khi có kịch bản hoặc video mới

```bash
python3 web/_cong-cu/tao_thu_vien.py              # từ thư mục gốc kho mã
python3 web/_cong-cu/tao_thu_vien.py --kiem-tra   # chỉ báo cáo, không ghi tệp
```

Công cụ đọc `data/catalog/`, `data/scripts/`, video trong `renders/v1/`, `web/mo-phong/` và `web/du-lieu/lien-ket.json`, rồi tạo lại toàn bộ trang.
Chạy mất vài giây; không chuyển mã video (chỉ đọc thông tin bằng `ffprobe`, cắt 1 khung hình làm ảnh bìa khi chưa có ảnh).
Video vừa được ghi trong 2 phút gần nhất (có thể đang dựng) được bỏ qua – chạy lại sau.

Tình trạng một tập:
- **Đã có video**: có tệp `<MA>.mp4` hợp lệ hoặc có link YouTube.
- **Video đang dựng, đã có câu hỏi ôn tập**: đã có kịch bản đối chiếu SGK (trang tập có ghi nhớ và câu hỏi).
- **Đang viết kịch bản**: chỉ có trong danh mục; chưa có trang riêng (nội dung nháp của danh mục không đưa lên web).

## Xuất bản video

**1. Dùng tại lớp (máy của trường, USB).** Công cụ đưa video từ `renders/v1/` vào `web/videos/` bằng liên kết cứng – không tốn thêm dung lượng.
Chép cả thư mục `web/` sang USB là có đủ video (lệnh chép thông thường chép nội dung tệp). Đổi cách làm trong `cau-hinh.json`
(`cach_dua_video`: `lien-ket-cung` | `sao-chep` | `lien-ket-mem` | `khong`) hoặc tạm thời: `--cach-dua-video sao-chep`.

**2. Đăng công khai (GitHub Pages).** GitHub không nhận tệp trên 100 MB và kho mã không nên chứa video, nên `web/videos/` đã được bỏ qua bằng `.gitignore`.
Đăng video lên YouTube (chế độ công khai/không công khai do giáo viên quyết định), rồi thêm link vào `web/du-lieu/lien-ket.json`:

```json
{
 "tap": {
  "L9-B17-05": { "youtube": "https://youtu.be/XXXXXXXXXXX", "tiktok": "https://www.tiktok.com/@ten-kenh/video/1234567890" }
 }
}
```

Trước khi commit bản công khai, chạy `python3 web/_cong-cu/tao_thu_vien.py --khong-video-cuc-bo` để chỉ những tập có link YouTube được ghi "Đã có video".
Nếu quên, trang vẫn hoạt động: khi không mở được tệp video, trang tự chuyển sang nút YouTube (nếu có) hoặc báo "video được chiếu tại lớp".

**Quyền riêng tư với YouTube/TikTok.** Trang không tải gì từ YouTube cho tới khi người xem bấm "Phát video từ YouTube";
khi đó trình phát được nhúng từ `youtube-nocookie.com`. Mở trang bằng file:// thì YouTube không cho nhúng, nên nút sẽ mở YouTube ở thẻ mới.
TikTok chỉ là liên kết ra ngoài.

## Nguyên tắc nội dung (đã cài trong công cụ)
- Ghi nhớ, mốc thời gian, câu hỏi, số trang lấy nguyên từ kịch bản đã đối chiếu SGK (`data/scripts`).
- "Trong video: …" sau mỗi câu hỏi là câu thuyết minh của Nhật Minh/Hân Hân hoặc ý ghi nhớ trong kịch bản có chứa đáp án
  và liên quan tới câu hỏi; không chắc chắn thì chỉ ghi số trang SGK (câu hỏi dạng "KHÔNG phải" luôn chỉ ghi số trang).
- Lời thoại (bản chữ song ngữ) chỉ hiện khi tập đã có video; lời nhân vật lịch sử được gắn nhãn "lời tái hiện".

## Kiểm tra nhanh
- Mở `web/index.html` trực tiếp, hoặc chạy máy chủ thử: `python3 -m http.server 8000 -d web` rồi vào http://localhost:8000.
- Thư mục `_cong-cu` bắt đầu bằng dấu gạch dưới nên GitHub Pages (Jekyll) không xuất bản.
