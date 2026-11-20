/* L8-B16-02 · sinh tự động bởi _cong-cu/tao_trang.py từ sa bàn pipeline/maps/specs/hanh-chinh-nguyen.json (đã dùng trong video) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  new W.MapPlayer(MP.khung(), { id: "l8-b16-02", spec: window.MP_BANDO["hanh-chinh-nguyen"],
    phases: [{"key":"tong_quan","nhan":"Những năm 1831 – 1832: Cải cách Minh Mạng","canh":[7]},{"key":"bac","nhan":"Các tỉnh phía bắc","canh":[8]},{"key":"trung","nhan":"Phủ Thừa Thiên và các tỉnh miền Trung","canh":[9]},{"key":"nam","nhan":"Các tỉnh phía nam","canh":[10]},{"key":"toan_quoc","nhan":"Toàn quốc","canh":[11]}],
    am: { nen: ['gio'], doiTuong: function (id, o) { if (o.loai === 'nhan' || o.loai === 'sao') return 'trong_nho'; } } });
});
