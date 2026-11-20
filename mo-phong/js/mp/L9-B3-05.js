/* L9-B3-05 · sinh tự động bởi _cong-cu/tao_trang.py từ sa bàn pipeline/maps/specs/dong-nam-a.json (đã dùng trong video) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  new W.MapPlayer(MP.khung(), { id: "l9-b3-05", spec: window.MP_BANDO["dong-nam-a"],
    phases: [{"key":"tong_quan","nhan":"Toàn cảnh","canh":[3]},{"key":"dang_cs","nhan":"Các Đảng Cộng sản ra đời","canh":[5]},{"key":"khoi_nghia","nhan":"Khởi nghĩa, cao trào cách mạng","canh":[7]},{"key":"dan_chu_ts","nhan":"Các chính đảng dân chủ tư sản","canh":[9]},{"key":"dong_duong","nhan":"Đông Dương","canh":[11]},{"key":"ctgt2","nhan":"1940: Nhật Bản xâm lược Đông Nam Á","canh":[12]}],
    am: { nen: ['gio'], doiTuong: function (id, o) { if (o.loai === 'nhan' || o.loai === 'sao') return 'trong_nho'; } } });
});
