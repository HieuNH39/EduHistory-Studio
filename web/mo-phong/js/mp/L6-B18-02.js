/* L6-B18-02 · sinh tự động bởi _cong-cu/tao_trang.py từ sa bàn pipeline/maps/specs/duong-dinh-nghe-931.json (đã dùng trong video) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  new W.MapPlayer(MP.khung(), { id: "l6-b18-02", spec: window.MP_BANDO["duong-dinh-nghe-931"],
    phases: [{"key":"nam_han","nhan":"Mùa thu năm 930","canh":[4]},{"key":"tu_nghia","nhan":"Năm 931","canh":[6]},{"key":"dai_la","nhan":"Vây đánh thành Đại La","canh":[7]},{"key":"tiep_vien","nhan":"Chặn quân tiếp viện Nam Hán","canh":[10]},{"key":"thang_loi","nhan":"Thắng lợi","canh":[11]}],
    am: { nen: ['gio'], batDau: 'trong', doiTuong: function (id, o) { if (o.loai === 'mui_ten_dich' || o.loai === 'mui_ten_ta') return ['vut_nhe', 'buoc_quan']; if (o.loai === 'sao') return 'trong_nho'; if (o.loai === 'nhan') return 'trong_nho'; } } });
});
