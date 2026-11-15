/* L9-B20-03 · sinh tự động bởi _cong-cu/tao_trang.py từ sa bàn pipeline/maps/specs/bien-dao-viet-nam.json (đã dùng trong video) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  new W.MapPlayer(MP.khung(), { id: "l9-b20-03", spec: window.MP_BANDO["bien-dao-viet-nam"],
    phases: [{"key":"dac_khu","nhan":"Toàn cảnh biển đảo","canh":[4]},{"key":"gac_ma","nhan":"Tháng 3 – 1988","canh":[7]},{"key":"sau_1954","nhan":"Sau năm 1954","canh":[]},{"key":"tien_tieu","nhan":"Căn cứ tiền tiêu hướng đông","canh":[]}],
    am: { nen: ['gio'], doiTuong: function (id, o) { if (o.loai === 'nhan' || o.loai === 'sao') return 'trong_nho'; } } });
});
