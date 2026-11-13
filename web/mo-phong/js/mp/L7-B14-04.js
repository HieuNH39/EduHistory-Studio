/* L7-B14-04 · Trận Bạch Đằng năm 1288 – bãi cọc, nước triều, kế hoả công (dữ liệu: pipeline/maps/specs/bach-dang-1288.json) */
MP.onReady(function () {
  var W = window.SaBanWeb, clamp = MP.clamp, seg = MP.seg;
  var tn = W.thuocNuoc();
  function muc(key, u) {
    switch (key) {
      case 'dia_the': return 0.6;
      case 'nhu': return 0.9;
      case 'nuoc_rut': return 0.9 - 0.72 * seg(u, 0.05, 0.35);
      default: return 0.18;
    }
  }
  var CHU = {
    dia_the: ['Bãi cọc ngầm', 'Cọc cắm dưới lòng sông'],
    nhu: ['Nước đang lên cao', 'Thuyền giặc chưa thấy bãi cọc'],
    nuoc_rut: ['Nước triều rút nhanh', 'Thuyền giặc mắc kẹt ở bãi cọc'],
    hoa_cong: ['Nước triều đã rút', 'Thuyền lửa thả trôi theo dòng nước'],
    ket_qua: ['Nước triều đã rút', 'Trận Bạch Đằng đại thắng']
  };
  new W.MapPlayer(MP.khung(), {
    id: 'bd1288', spec: window.MP_BANDO['bach-dang-1288'],
    phases: [
      { key: 'dia_the', nhan: 'Trận địa mai phục', canh: [8] },
      { key: 'nhu', nhan: 'Đoàn thuyền Ô Mã Nhi tiến vào', canh: [9, 10] },
      { key: 'nuoc_rut', nhan: 'Nước triều rút nhanh', canh: [12, 13] },
      { key: 'hoa_cong', nhan: 'Kế hoả công', canh: [14, 15] },
      { key: 'ket_qua', nhan: 'Đại thắng', canh: [16, 17] }
    ],
    overlay: tn.el,
    style: function (id, o, key, u) { return o.loai === 'coc' ? 1 - 0.62 * clamp((muc(key, u) - 0.45) / 0.45, 0, 1) : 1; },
    overlayUpdate: function (key, u) { var c = CHU[key]; tn.set(muc(key, u), c[0], c[1]); },
    am: {
      nen: ['nuoc', 'song_bien', 'gio'], batDau: 'trong',
      nenPha: { nuoc_rut: ['nuoc', 'gio', 'dam_dong'], hoa_cong: ['nuoc', 'lua', 'dam_dong'], ket_qua: ['nuoc', 'lua', 'gio'] },
      moc: { nuoc_rut: [[0.05, 'te_nuoc', { lv: 0.7 }]] },
      doiTuong: function (id, o) { if (o.loai === 'rut_chay') return 'te_nuoc'; }
    },
    tomTat: W.tomTat(18, 'Tóm tắt: kháng chiến 1287 – 1288')
  });
});
