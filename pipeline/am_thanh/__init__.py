"""Thư viện âm thanh mô phỏng EduHistory Studio (tổng hợp thuần bằng numpy/scipy, 48 kHz stereo).
- dsp.py: lọc, ồn, đường bao, vang, vòng lặp liền mạch, tổng hợp dao động riêng
- nguon.py: nguồn tự nhiên (giọng xa, chim, dế, ếch, bọt nước, lửa, gỗ, kim loại)
- su_kien.py: tiếng sự kiện (trống, cồng, trống đồng, tên bay, quân tiến, ngựa, thuyền, cọc, nước, lửa, gươm, pháo…)
- giao_dien.py: tiếng giao diện (tích, bóp, đồng hồ, chuông, vút, nhạc hiệu logo, cổng thời gian)
- nen.py: âm nền lặp liền mạch + điểm xuyết ngẫu nhiên
- thiet_ke.py: tự thiết kế âm thanh cho từng cảnh (từ khoá mô tả/lời, dữ liệu sa bàn, mốc hiện chữ)
- tron.py: dựng hai kênh sfx_nen.wav (bị hạ dưới lời đọc) và sfx_ui.wav (không hạ) khớp trục thời gian tập
"""
from .dsp import SR
