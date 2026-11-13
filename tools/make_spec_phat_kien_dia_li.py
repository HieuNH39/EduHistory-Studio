"""Bản đồ hành trình (the_gioi) cho ba cuộc phát kiến địa lí: B. Đi-a-xơ (1487), C. Cô-lôm-bô (1492), V. Ga-ma (1497 – 1498).
Vẽ lại, giản lược theo Hình 1 'Lược đồ một số cuộc phát kiến địa lí lớn', SGK Lịch sử và Địa lí 7, Bài 2, tr. 14
(đường đi là minh hoạ gần đúng, bám theo nét mũi tên trên lược đồ; không vẽ biên giới quốc gia).
Hành trình Ma-gien-lăng dùng lại tệp có sẵn ma-gien-lang.json. Toạ độ [kinh độ, vĩ độ]."""
import json
ROOT = "/home/claude/eduhistory-studio"
NGUON = "Vẽ lại, giản lược theo Hình 1, SGK Lịch sử và Địa lí 7, Bài 2, tr. 14; nền đất liền Natural Earth"
NHAN = [["CHÂU ÂU", 18, 52], ["CHÂU PHI", 20, 8], ["CHÂU MỸ", -98, 40], ["NAM MỸ", -60, -12], ["CHÂU Á", 95, 50],
        ["Đại Tây Dương", -38, 32, "bien"], ["Đại Tây Dương", -22, -22, "bien"], ["Ấn Độ Dương", 78, -18, "bien"]]
LIXBON = [-9.4, 38.6]

def spec(ten, phu_de, duong, moc, pha, nhan=NHAN):
    return {"loai": "the_gioi", "ten": ten, "phu_de": phu_de, "nguon": NGUON, "duong": duong, "moc": moc, "nhan": nhan, "pha": pha}

# B. Đi-a-xơ: men theo bờ tây châu Phi xuống mũi cực Nam (mũi Hảo Vọng)
dia = [LIXBON, [-12.5, 33], [-18, 24], [-19.5, 14], [-15, 7], [-6, 3.2], [3, 1], [8, -4], [11.5, -14], [13.5, -24], [16.5, -31.5], [18.6, -35.3]]
S1 = spec("Hành trình của B. Đi-a-xơ", "Năm 1487: đến mũi cực Nam châu Phi", dia,
          [{"chi_so": 0, "chu": "Li-xbon (Bồ Đào Nha)", "dx": 14, "dy": -14, "canh": "l"},
           {"chi_so": len(dia) - 1, "chu": "Mũi Hảo Vọng (1487)", "dx": 20, "dy": -24, "canh": "l"}],
          {"hanh_trinh": {"tu_moc": 0, "den_moc": len(dia) - 1, "tam_nhin": 110, "vi_do_khoang": [-25, 25], "moc_chu": "Năm 1487", "ve_xong": .9},
           "toan_canh": {"tu_moc": 0, "den_moc": len(dia) - 1, "tam_nhin": 210, "camera": [20, 1], "moc_chu": "Năm 1487", "ve_xong": .7}})

# C. Cô-lôm-bô: từ Pa-lốt (Tây Ban Nha) đi về phía tây, vượt Đại Tây Dương
col = [[-6.9, 37.1], [-11, 32.5], [-16, 28.3], [-26, 27.6], [-40, 26.8], [-55, 25.8], [-67, 24.8], [-74.6, 24.0]]
S2 = spec("Hành trình của C. Cô-lôm-bô", "Năm 1492: vượt Đại Tây Dương, tìm ra châu Mỹ", col,
          [{"chi_so": 0, "chu": "Pa-lốt (Tây Ban Nha)", "dx": -14, "dy": -20, "canh": "r"},
           {"chi_so": len(col) - 1, "chu": "Châu Mỹ (1492)", "dx": -14, "dy": 30, "canh": "r"}],
          {"hanh_trinh": {"tu_moc": 0, "den_moc": len(col) - 1, "tam_nhin": 110, "vi_do_khoang": [18, 28], "moc_chu": "Năm 1492", "ve_xong": .9},
           "toan_canh": {"tu_moc": 0, "den_moc": len(col) - 1, "tam_nhin": 150, "camera": [-45, 18], "moc_chu": "Năm 1492", "ve_xong": .7}})

# V. Ga-ma: vòng rộng qua Đại Tây Dương, vòng mũi cực Nam châu Phi, men bờ đông châu Phi, sang Ca-li-cút
gam = [LIXBON, [-14.5, 29], [-22, 17], [-27, 4], [-27, -10], [-19, -24], [-5, -33], [10, -37], [19, -36.6], [27, -35], [33.5, -30],
       [38.5, -22], [41.5, -15], [42.5, -8], [41.5, -3.2], [49, 3.5], [59, 8.5], [69, 10.8], [75.4, 11.3]]
MUI = 8
S3 = spec("Hành trình của V. Ga-ma", "1497 – 1498: tìm ra đường biển sang Ấn Độ", gam,
          [{"chi_so": 0, "chu": "Li-xbon (1497)", "dx": 14, "dy": -14, "canh": "l"},
           {"chi_so": MUI, "chu": "Mũi Hảo Vọng", "dx": 20, "dy": -24, "canh": "l"},
           {"chi_so": len(gam) - 1, "chu": "Ca-li-cút (1498)", "dx": -16, "dy": -26, "canh": "r"}],
          {"vong_chau_phi": {"tu_moc": 0, "den_moc": MUI, "tam_nhin": 110, "vi_do_khoang": [-25, 25], "moc_chu": "Năm 1497", "ve_xong": .9},
           "an_do": {"tu_moc": MUI, "den_moc": len(gam) - 1, "tam_nhin": 110, "vi_do_khoang": [-22, 12], "moc_chu": "Năm 1498", "ve_xong": .9},
           "toan_canh": {"tu_moc": 0, "den_moc": len(gam) - 1, "tam_nhin": 220, "camera": [38, 1], "moc_chu": "1497 – 1498", "ve_xong": .7}})

for ten, S in (("di-a-xo-1487", S1), ("co-lom-bo-1492", S2), ("ga-ma-1497", S3)):
    json.dump(S, open(f"{ROOT}/pipeline/maps/specs/{ten}.json", "w"), ensure_ascii=False)
print("ok")
