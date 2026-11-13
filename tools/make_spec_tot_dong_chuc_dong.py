"""Sa bàn (saban2) 'Trận Tốt Động – Chúc Động' (7 – 11 – 1426).
Vẽ lại, giản lược theo Hình 3 'Lược đồ trận Tốt Động – Chúc Động', SGK Lịch sử và Địa lí 7, Bài 16, tr. 80:
toạ độ cục bộ đo trên ảnh lược đồ (khung 230..1195 × 1162..1800). Ảnh SGK in đen trắng nên màu hai bên không phân biệt được;
hướng mũi tên vẽ theo hình dạng lược đồ, bên tiến công/rút chạy xác định theo chú giải hình dạng (nét đứt = quân Minh rút chạy)
và lời SGK (quân Minh tấn công, quân ta mai phục, chặn đánh ở Tốt Động – Chúc Động). Lược đồ không có biển."""
import json
ROOT = "/home/claude/eduhistory-studio"
CAO_BO, NINH_KIEU = [301, 1499], [842, 1291]
CHUC_DONG, GIUA, TOT_DONG = [712, 1362], [757, 1445], [580, 1704]
S = {
 "phien_ban": 2, "ten": "Trận Tốt Động – Chúc Động", "phu_de": "Ngày 7 – 11 – 1426",
 "nguon": "Vẽ lại, giản lược theo Hình 3, SGK Lịch sử và Địa lí 7, Bài 16, tr. 80",
 "khung": [230, 1162, 1195, 1800], "tam": [700, 1480], "chu_giai_xy": [0.675, 0.43],
 "ho": [{"elip": [735, 1215, 16, 42, 12]}, {"elip": [962, 1478, 13, 8, 0]}],
 "song": [
  {"ten": "S. Đáy", "nhan": [1060, 1212], "goc": -14, "rong": 7, "diem": [[1195, 1190], [1090, 1215], [990, 1250], [900, 1268], [862, 1305], [862, 1352], [895, 1400], [950, 1450], [1020, 1500], [1100, 1540], [1195, 1560]]},
  {"ten": "S. Yên Duyệt", "nhan": [400, 1730], "goc": -4, "rong": 5, "diem": [[230, 1640], [290, 1680], [350, 1702], [420, 1708], [480, 1700], [540, 1720], [580, 1760], [600, 1800]]},
  {"ten": "", "rong": 3, "diem": [[560, 1270], [600, 1330], [650, 1400], [640, 1480], [610, 1560], [600, 1640]]}],
 "dia_danh": [
  {"ten": "CAO BỘ", "vi_tri": CAO_BO, "kieu": "diem", "nhan": [CAO_BO[0] + 52, CAO_BO[1]], "co": 13, "dam": True},
  {"ten": "NINH KIỀU", "vi_tri": NINH_KIEU, "kieu": "diem", "nhan": [NINH_KIEU[0] + 52, NINH_KIEU[1] + 28], "co": 13, "dam": True},
  {"ten": "CHÚC ĐỘNG", "vi_tri": CHUC_DONG, "kieu": None, "nhan": [CHUC_DONG[0] - 36, CHUC_DONG[1] + 34], "co": 13, "dam": True},
  {"ten": "TỐT ĐỘNG", "vi_tri": TOT_DONG, "kieu": None, "nhan": [TOT_DONG[0] + 86, TOT_DONG[1] - 8], "co": 13, "dam": True}],
 "chu_giai": [{"loai": "mui_ten_dich", "nhan": "Quân Minh tiến công"}, {"loai": "mai_phuc", "nhan": "Quân ta mai phục"},
              {"loai": "mui_ten_ta", "nhan": "Quân ta tiến công"}, {"loai": "sao", "nhan": "Quân ta giành thắng lợi"}, {"loai": "rut_chay", "nhan": "Quân Minh rút chạy"}],
 "doi_tuong": {
  "minh1": {"loai": "mui_ten_dich", "diem": [[830, 1300], [785, 1336], [735, 1356]], "w0": 6, "w1": 12},
  "minh2": {"loai": "mui_ten_dich", "diem": [[835, 1325], [808, 1392], [770, 1435]], "w0": 6, "w1": 12},
  "minh3": {"loai": "mui_ten_dich", "diem": [[735, 1478], [675, 1562], [600, 1675]], "w0": 6, "w1": 12},
  "mp1": {"loai": "mai_phuc", "vi_tri": [715, 1432], "goc": 80}, "mp2": {"loai": "mai_phuc", "vi_tri": [812, 1458], "goc": -80},
  "mp3": {"loai": "mai_phuc", "vi_tri": [655, 1312], "goc": 150}, "mp4": {"loai": "mai_phuc", "vi_tri": [512, 1650], "goc": 60},
  "mp5": {"loai": "mai_phuc", "vi_tri": [600, 1752], "goc": 0},
  "ta1": {"loai": "mui_ten_ta", "diem": [[300, 1525], [350, 1612], [445, 1665], [555, 1698]], "w0": 7, "w1": 12},
  "ta2": {"loai": "mui_ten_ta", "diem": [[300, 1475], [325, 1395], [410, 1338], [560, 1330], [688, 1352]], "w0": 7, "w1": 12},
  "ta3": {"loai": "mui_ten_ta", "diem": [[750, 1740], [690, 1720], [610, 1708]], "w0": 6, "w1": 11},
  "sao_cd": {"loai": "sao", "vi_tri": CHUC_DONG}, "sao_g": {"loai": "sao", "vi_tri": GIUA}, "sao_td": {"loai": "sao", "vi_tri": TOT_DONG},
  "rut1": {"loai": "rut_chay", "diem": [[740, 1345], [800, 1310], [850, 1282], [930, 1262], [1030, 1238], [1110, 1215]]},
  "rut2": {"loai": "rut_chay", "diem": [[605, 1680], [665, 1590], [735, 1500], [800, 1400], [845, 1310]]}
 },
 "pha": {
  "minh_tien": {"mo_dau": True, "zoom": [1.0, 1.03], "chu_giai": ["mui_ten_dich"], "moc": [{"chu": "Tháng 10 – 1426", "tu": 0.05, "den": 1.1}],
                "buoc": [{"id": "minh1", "tu": 0.2, "den": 0.45}, {"id": "minh2", "tu": 0.3, "den": 0.55}, {"id": "minh3", "tu": 0.5, "den": 0.8}]},
  "mai_phuc": {"zoom": [1.03, 1.06], "hien": ["minh1", "minh2", "minh3"], "chu_giai": ["mui_ten_dich", "mai_phuc", "mui_ten_ta", "sao"],
               "moc": [{"chu": "Ngày 7 – 11 – 1426", "tu": 0.05, "den": 1.1}],
               "buoc": [{"id": "mp1", "tu": 0.08, "den": 0.18}, {"id": "mp2", "tu": 0.1, "den": 0.2}, {"id": "mp3", "tu": 0.12, "den": 0.22}, {"id": "mp4", "tu": 0.14, "den": 0.24}, {"id": "mp5", "tu": 0.16, "den": 0.26},
                        {"id": "ta2", "tu": 0.3, "den": 0.55}, {"id": "ta1", "tu": 0.35, "den": 0.6}, {"id": "ta3", "tu": 0.45, "den": 0.65},
                        {"id": "sao_cd", "tu": 0.6, "den": 0.7}, {"id": "sao_g", "tu": 0.66, "den": 0.76}, {"id": "sao_td", "tu": 0.72, "den": 0.82}]},
  "ket_qua": {"zoom": [1.06, 1.0], "hien": ["minh1", "minh2", "minh3", "mp1", "mp2", "mp3", "mp4", "mp5", "ta1", "ta2", "ta3", "sao_cd", "sao_g", "sao_td"],
              "chu_giai": ["mai_phuc", "mui_ten_ta", "sao", "rut_chay"], "moc": [{"chu": "Quân Minh thất bại nặng nề", "tu": 0.05, "den": 1.1}],
              "buoc": [{"id": "rut2", "tu": 0.1, "den": 0.45}, {"id": "rut1", "tu": 0.25, "den": 0.6}],
              "bang": {"chu": "Siết chặt vây hãm thành Đông Quan", "tu": 0.65, "y": 0.70}}
 }
}
json.dump(S, open(f"{ROOT}/pipeline/maps/specs/tot-dong-chuc-dong.json", "w"), ensure_ascii=False)
print("ok")
