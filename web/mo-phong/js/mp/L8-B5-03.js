/* L8-B5-03 · sinh tự động bởi _cong-cu/tao_trang.py từ sa bàn pipeline/maps/specs/trinh-nguyen.json (đã dùng trong video) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  new W.MapPlayer(MP.khung(), { id: "l8-b5-03", spec: window.MP_BANDO["trinh-nguyen"],
    phases: [{"key":"thuan_hoa","nhan":"Thuận Hoá","canh":[5]},{"key":"giao_tranh","nhan":"1627 – 1672: bảy lần giao chiến","canh":[8]},{"key":"luy_thay","nhan":"Luỹ Thầy (luỹ Đào Duy Từ)","canh":[11]},{"key":"chia_cat","nhan":"Đất nước bị chia cắt","canh":[13]}],
    am: { nen: ['gio'], doiTuong: function (id, o) { if (o.loai === 'nhan' || o.loai === 'sao') return 'trong_nho'; } } });
});
