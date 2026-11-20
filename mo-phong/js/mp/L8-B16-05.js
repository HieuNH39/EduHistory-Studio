/* L8-B16-05 · sinh tự động bởi _cong-cu/tao_trang.py từ sa bàn pipeline/maps/specs/hoang-sa-truong-sa.json (đã dùng trong video) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  new W.MapPlayer(MP.khung(), { id: "l8-b16-05", spec: window.MP_BANDO["hoang-sa-truong-sa"],
    phases: [{"key":"tong_quan","nhan":"Toàn cảnh","canh":[3]},{"key":"gia_long","nhan":"Thời Gia Long: thuộc phủ Quảng Nghĩa","canh":[5]},{"key":"nam_1816","nhan":"Năm 1816","canh":[8]},{"key":"nam_1836","nhan":"Năm 1836 – Phạm Hữu Nhật","canh":[12]},{"key":"toan_do","nhan":"Toàn đồ","canh":[16]}],
    am: { nen: ['gio'], doiTuong: function (id, o) { if (o.loai === 'nhan' || o.loai === 'sao') return 'trong_nho'; } } });
});
