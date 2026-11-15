/* L6-B16-01 · sinh tự động bởi _cong-cu/tao_trang.py từ sa bàn pipeline/maps/specs/hai-ba-trung-40.json (đã dùng trong video) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  new W.MapPlayer(MP.khung(), { id: "l6-b16-01", spec: window.MP_BANDO["hai-ba-trung-40"],
    phases: [{"key":"khoi_nghia","nhan":"Tháng 3 – năm 40","canh":[5]},{"key":"tien_quan","nhan":"Nghĩa quân tiến về Luy Lâu","canh":[6]},{"key":"luy_lau","nhan":"Tháng 4 – năm 40","canh":[8]},{"key":"thang_loi","nhan":"Thắng lợi","canh":[11]}],
    am: { nen: ['gio'], batDau: 'trong', doiTuong: function (id, o) { if (o.loai === 'mui_ten_dich' || o.loai === 'mui_ten_ta') return ['vut_nhe', 'buoc_quan']; if (o.loai === 'sao') return 'trong_nho'; if (o.loai === 'nhan') return 'trong_nho'; } } });
});
