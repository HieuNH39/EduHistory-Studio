/* L8-B18-02 · sinh tự động bởi _cong-cu/tao_trang.py từ sa bàn pipeline/maps/specs/can-vuong.json (đã dùng trong video) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  new W.MapPlayer(MP.khung(), { id: "l8-b18-02", spec: window.MP_BANDO["can-vuong"],
    phases: [{"key":"tong_quan","nhan":"13 – 7 – 1885: Dụ Cần vương","canh":[3]},{"key":"huong_khe","nhan":"Khởi nghĩa Hương Khê (1885 – 1896)","canh":[4]},{"key":"ngan_truoi","nhan":"Pháp bao vây, tấn công Ngàn Trươi","canh":[9]}],
    am: { nen: ['gio'], doiTuong: function (id, o) { if (o.loai === 'nhan' || o.loai === 'sao') return 'trong_nho'; } } });
});
