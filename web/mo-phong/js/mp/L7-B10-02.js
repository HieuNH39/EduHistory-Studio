/* L7-B10-02 · sinh tự động bởi _cong-cu/tao_trang.py từ sa bàn pipeline/maps/specs/chong-tong-981.json (đã dùng trong video) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  new W.MapPlayer(MP.khung(), { id: "l7-b10-02", spec: window.MP_BANDO["chong-tong-981"],
    phases: [{"key":"tong_tien","nhan":"Đầu năm 981","canh":[6]},{"key":"chan_danh","nhan":"Lê Hoàn lãnh đạo kháng chiến","canh":[8]},{"key":"ket_qua","nhan":"Quân Tống đại bại","canh":[10]}],
    am: { nen: ['gio'], batDau: 'trong', doiTuong: function (id, o) { if (o.loai === 'mui_ten_dich' || o.loai === 'mui_ten_ta') return ['vut_nhe', 'buoc_quan']; if (o.loai === 'sao') return 'trong_nho'; if (o.loai === 'nhan') return 'trong_nho'; } } });
});
