/* L7-B14-02 · Kháng chiến năm 1258 – lược đồ động (dữ liệu: pipeline/maps/specs/khang-chien-1258.json) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  new W.MapPlayer(MP.khung(), {
    id: 'kc1258', spec: window.MP_BANDO['khang-chien-1258'],
    phases: [
      { key: 'tien_quan', nhan: 'Quân Mông Cổ tiến vào', canh: [4] },
      { key: 'binh_le_nguyen', nhan: 'Bình Lệ Nguyên – tạm rút lui', canh: [6] },
      { key: 'thanh_trong', nhan: 'Vườn không nhà trống', canh: [9, 10] },
      { key: 'dong_bo_dau', nhan: 'Phản công ở Đông Bộ Đầu', canh: [11, 12] }
    ],
    am: {
      nen: ['gio', 'dam_dong'], nenPha: { thanh_trong: ['gio'] }, batDau: function (k) { return k === 'thanh_trong' ? 'mo_pha' : 'trong'; },
      doiTuong: function (id, o) { if (o.loai === 'mui_ten_dich') return ['vut_nhe', 'buoc_quan']; if (o.loai === 'nhan') return 'lat_trang'; }
    },
    tomTat: W.tomTat(13, 'Tóm tắt: kháng chiến năm 1258')
  });
});
