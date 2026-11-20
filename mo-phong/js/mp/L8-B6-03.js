/* L8-B6-03 · sinh tự động bởi _cong-cu/tao_trang.py từ sa bàn pipeline/maps/specs/hoang-sa-chua-nguyen.json (đã dùng trong video) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  new W.MapPlayer(MP.khung(), { id: "l8-b6-03", spec: window.MP_BANDO["hoang-sa-chua-nguyen"],
    phases: [{"key":"tong_quan","nhan":"Toàn cảnh","canh":[3]},{"key":"doi_dan_binh","nhan":"Thế kỉ XVII – XVIII: hoạt động có tổ chức, liên tục","canh":[5]},{"key":"bac_hai","nhan":"Đội Bắc Hải: xứ Bắc Hải, cù lao Côn Lôn, các đảo ở Hà Tiên","canh":[8]}],
    am: { nen: ['gio'], doiTuong: function (id, o) { if (o.loai === 'nhan' || o.loai === 'sao') return 'trong_nho'; } } });
});
