/* L7-B6-01 · sinh tự động bởi _cong-cu/tao_trang.py từ sa bàn pipeline/maps/specs/dong-nam-a-x-xvi.json (đã dùng trong video) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  new W.MapPlayer(MP.khung(), { id: "l7-b6-01", spec: window.MP_BANDO["dong-nam-a-x-xvi"],
    phases: [{"key":"x_xiii","nhan":"Thế kỉ X – XIII","canh":[4]},{"key":"xiii_xvi","nhan":"Thế kỉ XIII – XVI","canh":[7]},{"key":"ma_lac_ca","nhan":"Thế kỉ XV","canh":[]}],
    am: { nen: ['gio'], doiTuong: function (id, o) { if (o.loai === 'nhan' || o.loai === 'sao') return 'trong_nho'; } } });
});
