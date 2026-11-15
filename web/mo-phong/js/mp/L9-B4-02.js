/* L9-B4-02 · sinh tự động bởi _cong-cu/tao_trang.py từ sa bàn pipeline/maps/specs/ctgt2-giai-doan-1.json (đã dùng trong video) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  new W.MapPlayer(MP.khung(), { id: "l9-b4-02", spec: window.MP_BANDO["ctgt2-giai-doan-1"],
    phases: [{"key":"ba_lan","nhan":"1 – 9 – 1939","canh":[4]},{"key":"phap","nhan":"Tháng 4 – 7 – 1940","canh":[7]},{"key":"mua_he_1941","nhan":"Mùa hè 1941","canh":[8]},{"key":"lien_xo","nhan":"22 – 6 – 1941: Đức tấn công Liên Xô","canh":[9]}],
    am: { nen: ['gio'], doiTuong: function (id, o) { if (o.loai === 'nhan' || o.loai === 'sao') return 'trong_nho'; } } });
});
