/* L7-B14-03 · sinh tự động bởi _cong-cu/tao_trang.py từ sa bàn pipeline/maps/specs/khang-chien-1285.json (đã dùng trong video) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  new W.MapPlayer(MP.khung(), { id: "l7-b14-03", spec: window.MP_BANDO["khang-chien-1285"],
    phases: [{"key":"tien_cong","nhan":"Tháng 1 – 1285","canh":[12]},{"key":"rut_lui","nhan":"Nhà Trần rút khỏi Thăng Long","canh":[14]},{"key":"hoi_quan","nhan":"Toa Đô hội quân với Thoát Hoan","canh":[16]},{"key":"phan_cong","nhan":"Tháng 5 – 1285","canh":[17]},{"key":"rut_chay","nhan":"Quân Nguyên rút chạy về nước","canh":[18]}],
    am: { nen: ['gio'], batDau: 'trong', doiTuong: function (id, o) { if (o.loai === 'mui_ten_dich' || o.loai === 'mui_ten_ta') return ['vut_nhe', 'buoc_quan']; if (o.loai === 'sao') return 'trong_nho'; if (o.loai === 'nhan') return 'trong_nho'; } } });
});
