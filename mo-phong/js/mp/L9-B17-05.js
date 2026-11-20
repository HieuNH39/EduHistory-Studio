/* L9-B17-05 · Đại thắng mùa Xuân 1975 – lược đồ động ba chiến dịch lớn (dữ liệu: pipeline/maps/specs/xuan-1975.json; luôn có Hoàng Sa, Trường Sa) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  new W.MapPlayer(MP.khung(), {
    id: 'x1975', spec: window.MP_BANDO['xuan-1975'], tiLeMin: 0.9,
    phases: [
      { key: 'tong_quan', nhan: 'Tổng quan', canh: [3] },
      { key: 'tay_nguyen', nhan: 'Chiến dịch Tây Nguyên', canh: [4] },
      { key: 'hue_da_nang', nhan: 'Chiến dịch Huế – Đà Nẵng', canh: [5] },
      { key: 'truong_sa', nhan: 'Quần đảo Trường Sa', canh: [7] },
      { key: 'ho_chi_minh', nhan: 'Chiến dịch Hồ Chí Minh', canh: [8, 9, 10] },
      { key: 'chau_doc', nhan: 'Giải phóng hoàn toàn', canh: [12] }
    ],
    am: {
      nen: ['gio', 'dong_co', 'phao_xa'], nenPha: { tong_quan: ['gio'], truong_sa: ['song_bien', 'gio'], chau_doc: ['gio', 'dam_dong'] },
      batDau: function (k) { return k === 'tong_quan' || k === 'truong_sa' ? 'mo_pha' : 'trong'; },
      doiTuong: function (id, o) { if (o.loai === 'nhan') return 'lat_trang'; if (o.loai === 'sao') return ['chuong_nho']; }
    },
    tomTat: W.tomTat(13, 'Tóm tắt: Xuân 1975')
  });
});
