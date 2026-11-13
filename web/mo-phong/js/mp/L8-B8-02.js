/* L8-B8-02 · Trận thuỷ chiến Rạch Gầm – Xoài Mút (19 – 1 – 1785) – bản đồ động (định dạng cũ: pipeline/maps/saban.py, specs/rach-gam-xoai-mut.json) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  var MAI = [['mai_phuc', 'Quân Tây Sơn mai phục'], ['hq', 'Đại bản doanh quân Tây Sơn']];
  var mp = []; for (var i = 0; i < 8; i++) mp.push([0.08 + i * 0.07, 'soat']);
  new W.MapPlayer(MP.khung(), {
    id: 'rgxm', spec: window.MP_BANDO['rach-gam-xoai-mut'], legacy: true,
    phases: [
      { key: 'dia_the', nhan: 'Địa thế khúc sông', canh: [6] },
      { key: 'mai_phuc', nhan: 'Bày trận mai phục', canh: [5, 8] },
      { key: 'nhu_dich', nhan: 'Nhử quân Xiêm', canh: [9, 10, 11] },
      { key: 'ket_qua', nhan: 'Đánh tan quân Xiêm', canh: [12, 13] }
    ],
    chuGiai: function (k) {
      if (k === 'dia_the') return [];
      if (k === 'mai_phuc') return MAI;
      if (k === 'nhu_dich') return MAI.concat([['mui_ten_dich', 'Quân Xiêm tiến công']]);
      return MAI.concat([['mui_ten_dich', 'Quân Xiêm tiến công'], ['mui_ten_ta', 'Quân Tây Sơn tấn công'], ['lua', 'Thuyền, bè lửa đốt thuyền giặc']]);
    },
    moc: { nhu_dich: [{ chu: '19 – 1 – 1785', tu: 0.0 }], ket_qua: [{ chu: '19 – 1 – 1785', tu: 0.0, den: 0.6 }] },
    bang: { dia_the: null, mai_phuc: null, nhu_dich: null, ket_qua: { chu: 'Thắng lợi hoàn toàn chỉ trong một ngày', tu: 0.62 } },
    buoc: { dia_the: [0.34, 0.5, 0.58, 0.76], mai_phuc: [0.2, 0.34, 0.48, 0.62, 0.76], nhu_dich: [0.3, 0.52, 0.74, 0.9], ket_qua: [0.3, 0.5, 0.74] },
    am: {
      nenPha: { dia_the: ['nuoc', 'chim', 'gio'], mai_phuc: ['nuoc', 'con_trung'], nhu_dich: ['nuoc', 'con_trung'], ket_qua: ['nuoc', 'lua', 'dam_dong'] },
      batDau: function (k) { return k === 'ket_qua' ? 'trong' : 'mo_pha'; },
      moc: {
        dia_the: [[0.16, 'lat_trang'], [0.36, 'lat_trang'], [0.5, 'chuong_nho'], [0.64, 'soat']],
        mai_phuc: mp,
        nhu_dich: [[0.05, 'mai_cheo'], [0.3, 'vut_nhe'], [0.55, 'mai_cheo'], [0.75, 'vut_nhe']],
        ket_qua: [[0.04, 'vut'], [0.12, 'trong', { n: 4, gap: 0.22 }], [0.25, 'lua_bung'], [0.42, 'te_nuoc'], [0.62, 'reo']]
      }
    }
  });
});
