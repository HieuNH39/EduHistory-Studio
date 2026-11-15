/* L7-B12-01 · sinh tự động bởi _cong-cu/tao_trang.py từ sa bàn pipeline/maps/specs/tien-cong-1075.json (đã dùng trong video) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  new W.MapPlayer(MP.khung(), { id: "l7-b12-01", spec: window.MP_BANDO["tien-cong-1075"],
    phases: [{"key":"tien_cong","nhan":"Tháng 10 – 1075","canh":[7]},{"key":"ung_chau","nhan":"Sau 42 ngày chiến đấu","canh":[9]},{"key":"rut_ve","nhan":"Rút về chuẩn bị phòng tuyến","canh":[10]}],
    am: { nen: ['gio'], batDau: 'trong', doiTuong: function (id, o) { if (o.loai === 'mui_ten_dich' || o.loai === 'mui_ten_ta') return ['vut_nhe', 'buoc_quan']; if (o.loai === 'sao') return 'trong_nho'; if (o.loai === 'nhan') return 'trong_nho'; } } });
});
