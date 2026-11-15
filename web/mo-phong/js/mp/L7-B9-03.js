/* L7-B9-03 · sinh tự động bởi _cong-cu/tao_trang.py từ sa bàn pipeline/maps/specs/12-su-quan.json (đã dùng trong video) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  new W.MapPlayer(MP.khung(), { id: "l7-b9-03", spec: window.MP_BANDO["12-su-quan"],
    phases: [{"key":"cat_cu","nhan":"Năm 965","canh":[4]},{"key":"chia_cat","nhan":"Đất nước bị chia cắt","canh":[9]},{"key":"thong_nhat","nhan":"Năm 966 – 967","canh":[11]}],
    am: { nen: ['gio'], batDau: 'trong', doiTuong: function (id, o) { if (o.loai === 'mui_ten_dich' || o.loai === 'mui_ten_ta') return ['vut_nhe', 'buoc_quan']; if (o.loai === 'sao') return 'trong_nho'; if (o.loai === 'nhan') return 'trong_nho'; } } });
});
