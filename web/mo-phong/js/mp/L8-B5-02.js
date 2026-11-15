/* L8-B5-02 · sinh tự động bởi _cong-cu/tao_trang.py từ sa bàn pipeline/maps/specs/nam-bac-trieu.json (đã dùng trong video) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  new W.MapPlayer(MP.khung(), { id: "l8-b5-02", spec: window.MP_BANDO["nam-bac-trieu"],
    phases: [{"key":"tong_quan","nhan":"1533 – 1592: gần 60 năm xung đột","canh":[6]},{"key":"cam_cu","nhan":"1533 – 1570: hai bên cầm cự","canh":[7]},{"key":"bac_trieu_tien","nhan":"1570 – 1583: Bắc triều đánh vào Thanh – Nghệ","canh":[10]},{"key":"ra_bac","nhan":"1583 – 1592: Nam triều đánh ra Bắc","canh":[12]}],
    am: { nen: ['gio'], doiTuong: function (id, o) { if (o.loai === 'nhan' || o.loai === 'sao') return 'trong_nho'; } } });
});
