/* L8-CD1-03 · sinh tự động bởi _cong-cu/tao_trang.py từ sa bàn pipeline/maps/specs/chau-tho-cuu-long.json (đã dùng trong video) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  new W.MapPlayer(MP.khung(), { id: "l8-cd1-03", spec: window.MP_BANDO["chau-tho-cuu-long"],
    phases: [{"key":"tong_quan","nhan":"Toàn cảnh","canh":[2]},{"key":"mua_lu","nhan":"Mùa lũ: tháng 7 – tháng 11","canh":[4]},{"key":"ton_le_sap","nhan":"Lũ được điều tiết bởi hồ Tôn-lê Sáp","canh":[6]},{"key":"vinh_te","nhan":"Đầu thế kỉ XIX: đào kênh Vĩnh Tế","canh":[14]}],
    am: { nen: ['gio'], doiTuong: function (id, o) { if (o.loai === 'nhan' || o.loai === 'sao') return 'trong_nho'; } } });
});
