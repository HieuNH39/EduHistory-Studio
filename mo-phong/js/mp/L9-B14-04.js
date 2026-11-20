/* L9-B14-04 · sinh tự động bởi _cong-cu/tao_trang.py từ sa bàn pipeline/maps/specs/bien-gioi-1950.json (đã dùng trong video) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  new W.MapPlayer(MP.khung(), { id: "l9-b14-04", spec: window.MP_BANDO["bien-gioi-1950"],
    phases: [{"key":"ro_ve","nhan":"1950: Kế hoạch Rơ-ve","canh":[4]},{"key":"dong_khe","nhan":"Giữa tháng 9 – 1950: Đông Khê","canh":[7]},{"key":"duong_so_4","nhan":"Đường số 4","canh":[9]},{"key":"giai_phong","nhan":"Tháng 10 – 1950","canh":[10]}],
    am: { nen: ['gio'], batDau: 'trong', doiTuong: function (id, o) { if (o.loai === 'mui_ten_dich' || o.loai === 'mui_ten_ta') return ['vut_nhe', 'buoc_quan']; if (o.loai === 'sao') return 'trong_nho'; if (o.loai === 'nhan') return 'trong_nho'; } } });
});
