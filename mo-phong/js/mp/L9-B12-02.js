/* L9-B12-02 · sinh tự động bởi _cong-cu/tao_trang.py từ sa bàn pipeline/maps/specs/cu-ba.json (đã dùng trong video) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  new W.MapPlayer(MP.khung(), { id: "l9-b12-02", spec: window.MP_BANDO["cu-ba"],
    phases: [{"key":"vi_tri","nhan":"Vị trí Cu-ba","canh":[3]},{"key":"mon_ca_da","nhan":"Tháng 7 – 1953","canh":[4]},{"key":"me_hi_co","nhan":"Năm 1955","canh":[5]},{"key":"gran_ma","nhan":"Tháng 11 – 1956","canh":[7]},{"key":"toan_thang","nhan":"Cuối năm 1958","canh":[8]}],
    am: { nen: ['gio'], doiTuong: function (id, o) { if (o.loai === 'nhan' || o.loai === 'sao') return 'trong_nho'; } } });
});
