/* L8-CD1-01 · sinh tự động bởi _cong-cu/tao_trang.py từ sa bàn pipeline/maps/specs/hai-chau-tho.json (đã dùng trong video) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  new W.MapPlayer(MP.khung(), { id: "l8-cd1-01", spec: window.MP_BANDO["hai-chau-tho"],
    phases: [{"key":"tong_quan","nhan":"Toàn cảnh","canh":[2]},{"key":"song_hong","nhan":"Châu thổ sông Hồng: khoảng 15 000 km², dạng tam giác","canh":[5]},{"key":"cuu_long","nhan":"Châu thổ sông Cửu Long: hơn 40 nghìn km², lớn nhất nước ta","canh":[9]}],
    am: { nen: ['gio'], doiTuong: function (id, o) { if (o.loai === 'nhan' || o.loai === 'sao') return 'trong_nho'; } } });
});
