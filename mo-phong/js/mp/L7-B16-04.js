/* L7-B16-04 · sinh tự động bởi _cong-cu/tao_trang.py từ sa bàn pipeline/maps/specs/tot-dong-chuc-dong.json (đã dùng trong video) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  new W.MapPlayer(MP.khung(), { id: "l7-b16-04", spec: window.MP_BANDO["tot-dong-chuc-dong"],
    phases: [{"key":"minh_tien","nhan":"Tháng 10 – 1426","canh":[6]},{"key":"mai_phuc","nhan":"Ngày 7 – 11 – 1426","canh":[9]},{"key":"ket_qua","nhan":"Quân Minh thất bại nặng nề","canh":[10]}],
    am: { nen: ['gio'], batDau: 'trong', doiTuong: function (id, o) { if (o.loai === 'mui_ten_dich' || o.loai === 'mui_ten_ta') return ['vut_nhe', 'buoc_quan']; if (o.loai === 'sao') return 'trong_nho'; if (o.loai === 'nhan') return 'trong_nho'; } } });
});
