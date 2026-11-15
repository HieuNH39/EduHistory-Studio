/* L9-B9-03 · sinh tự động bởi _cong-cu/tao_trang.py từ sa bàn pipeline/maps/specs/chien-tranh-lanh.json (đã dùng trong video) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  new W.MapPlayer(MP.khung(), { id: "l9-b9-03", spec: window.MP_BANDO["chien-tranh-lanh"],
    phases: [{"key":"tong_quan","nhan":"Toàn cảnh","canh":[9]},{"key":"duc","nhan":"Đức: 1949","canh":[10]},{"key":"trieu_tien","nhan":"Triều Tiên: 1948","canh":[12]},{"key":"cu_ba","nhan":"Cu-ba: 1961 – 1962","canh":[14]},{"key":"viet_nam","nhan":"Việt Nam: 1950 – 1975","canh":[15]}],
    am: { nen: ['gio'], doiTuong: function (id, o) { if (o.loai === 'nhan' || o.loai === 'sao') return 'trong_nho'; } } });
});
