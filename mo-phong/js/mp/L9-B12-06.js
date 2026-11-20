/* L9-B12-06 · sinh tự động bởi _cong-cu/tao_trang.py từ sa bàn pipeline/maps/specs/asean.json (đã dùng trong video) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  new W.MapPlayer(MP.khung(), { id: "l9-b12-06", spec: window.MP_BANDO["asean"],
    phases: [{"key":"thanh_lap","nhan":"8 – 8 – 1967: thành lập ASEAN","canh":[3]},{"key":"bru_nay","nhan":"1984: Bru-nây gia nhập","canh":[11]},{"key":"dong_duong","nhan":"Quan hệ Đông Dương – ASEAN dần cải thiện","canh":[12]},{"key":"asean6","nhan":"ASEAN 6 (đến năm 1991)","canh":[]},{"key":"viet_nam","nhan":"7 – 1995: thành viên thứ 7","canh":[]},{"key":"lao_mianma","nhan":"7 – 1997: Lào, Mi-an-ma gia nhập","canh":[]},{"key":"cam_pu_chia","nhan":"4 – 1999: thành viên thứ 10","canh":[]}],
    am: { nen: ['gio'], doiTuong: function (id, o) { if (o.loai === 'nhan' || o.loai === 'sao') return 'trong_nho'; } } });
});
