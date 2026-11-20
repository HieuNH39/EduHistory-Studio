/* L9-B15-02 · sinh tự động bởi _cong-cu/tao_trang.py từ sa bàn pipeline/maps/specs/dong-xuan-1953.json (đã dùng trong video) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  new W.MapPlayer(MP.khung(), { id: "l9-b15-02", spec: window.MP_BANDO["dong-xuan-1953"],
    phases: [{"key":"na_va","nhan":"Từ giữa năm 1953: Kế hoạch Na-va","canh":[4]},{"key":"tay_bac","nhan":"20 – 11 – 1953: Pháp nhảy dù xuống Điện Biên Phủ","canh":[7]},{"key":"trung_lao","nhan":"Cuối năm 1953: Trung Lào","canh":[8]},{"key":"thuong_lao","nhan":"1 – 1954: Thượng Lào","canh":[10]},{"key":"tay_nguyen","nhan":"Đầu 2 – 1954: Bắc Tây Nguyên","canh":[11]},{"key":"phan_tan","nhan":"Pháp phân tán lực lượng thành 5 nơi","canh":[12]}],
    am: { nen: ['gio'], batDau: 'trong', doiTuong: function (id, o) { if (o.loai === 'mui_ten_dich' || o.loai === 'mui_ten_ta') return ['vut_nhe', 'buoc_quan']; if (o.loai === 'sao') return 'trong_nho'; if (o.loai === 'nhan') return 'trong_nho'; } } });
});
