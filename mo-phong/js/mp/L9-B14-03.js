/* L9-B14-03 · sinh tự động bởi _cong-cu/tao_trang.py từ sa bàn pipeline/maps/specs/viet-bac-1947.json (đã dùng trong video) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  new W.MapPlayer(MP.khung(), { id: "l9-b14-03", spec: window.MP_BANDO["viet-bac-1947"],
    phases: [{"key":"am_muu","nhan":"10 – 1947: khoảng 12 000 quân Pháp","canh":[8]},{"key":"huong_dong","nhan":"Hướng đông: Đường số 4","canh":[9]},{"key":"huong_tay","nhan":"Hướng tây: sông Lô","canh":[10]},{"key":"ket_qua","nhan":"Tháng 12 – 1947","canh":[12]}],
    am: { nen: ['gio'], batDau: 'trong', doiTuong: function (id, o) { if (o.loai === 'mui_ten_dich' || o.loai === 'mui_ten_ta') return ['vut_nhe', 'buoc_quan']; if (o.loai === 'sao') return 'trong_nho'; if (o.loai === 'nhan') return 'trong_nho'; } } });
});
