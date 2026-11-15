/* L8-CD2-02 · sinh tự động bởi _cong-cu/tao_trang.py từ sa bàn pipeline/maps/specs/duong-co-so.json (đã dùng trong video) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  new W.MapPlayer(MP.khung(), { id: "l8-cd2-02", spec: window.MP_BANDO["duong-co-so"],
    phases: [{"key":"tong_quan","nhan":"Đường cơ sở: đường gãy khúc nối các điểm từ 0 đến A24","canh":[3]},{"key":"phia_nam","nhan":"Các điểm A1 – A10","canh":[4]},{"key":"phia_bac","nhan":"Các điểm A11 – A24","canh":[5]},{"key":"vinh_bac_bo","nhan":"25 – 12 – 2000: đường phân định qua 21 điểm","canh":[8]},{"key":"toan_canh","nhan":"Vùng biển Việt Nam: khoảng 1 triệu km²","canh":[10]}],
    am: { nen: ['gio'], doiTuong: function (id, o) { if (o.loai === 'nhan' || o.loai === 'sao') return 'trong_nho'; } } });
});
