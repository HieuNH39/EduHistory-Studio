/* L9-B20-02 · sinh tự động bởi _cong-cu/tao_trang.py từ sa bàn pipeline/maps/specs/bao-ve-bien-gioi.json (đã dùng trong video) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  new W.MapPlayer(MP.khung(), { id: "l9-b20-02", spec: window.MP_BANDO["bao-ve-bien-gioi"],
    phases: [{"key":"tay_nam","nhan":"Sau năm 1975: Pôn Pốt khiêu khích, xâm phạm","canh":[4]},{"key":"phia_bac","nhan":"17 – 2 – 1979","canh":[8]},{"key":"vi_xuyen","nhan":"Đến cuối những năm 80: mặt trận Vị Xuyên","canh":[10]}],
    am: { nen: ['gio'], doiTuong: function (id, o) { if (o.loai === 'nhan' || o.loai === 'sao') return 'trong_nho'; } } });
});
