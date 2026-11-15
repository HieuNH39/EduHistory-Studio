/* L9-B1-01 · sinh tự động bởi _cong-cu/tao_trang.py từ sa bàn pipeline/maps/specs/nga-xo-viet-1918.json (đã dùng trong video) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  new W.MapPlayer(MP.khung(), { id: "l9-b1-01", spec: window.MP_BANDO["nga-xo-viet-1918"],
    phases: [{"key":"can_thiep","nhan":"1918 – 1920: 14 đế quốc can thiệp","canh":[3]},{"key":"phan_cong","nhan":"Hồng quân phản công (1919 – 1920)","canh":[5]}],
    am: { nen: ['gio'], doiTuong: function (id, o) { if (o.loai === 'nhan' || o.loai === 'sao') return 'trong_nho'; } } });
});
