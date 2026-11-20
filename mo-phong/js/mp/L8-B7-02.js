/* L8-B7-02 · sinh tự động bởi _cong-cu/tao_trang.py từ sa bàn pipeline/maps/specs/nong-dan-dang-ngoai.json (đã dùng trong video) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  new W.MapPlayer(MP.khung(), { id: "l8-b7-02", spec: window.MP_BANDO["nong-dan-dang-ngoai"],
    phases: [{"key":"tong_quan","nhan":"Giữa thế kỉ XVIII","canh":[4]},{"key":"hoang_cong_chat","nhan":"Hoàng Công Chất (1739 – 1769)","canh":[6]},{"key":"nguyen_danh_phuong","nhan":"Nguyễn Danh Phương (1740 – 1751)","canh":[10]},{"key":"nguyen_huu_cau","nhan":"Nguyễn Hữu Cầu – Quận He (1741 – 1751)","canh":[13]}],
    am: { nen: ['gio'], doiTuong: function (id, o) { if (o.loai === 'nhan' || o.loai === 'sao') return 'trong_nho'; } } });
});
