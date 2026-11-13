/* L6-B18-04 · Chiến thắng Bạch Đằng năm 938 – hoạt hoạ trận đánh trên lược đồ (dữ liệu: pipeline/maps/specs/bach-dang-938.json) */
MP.onReady(function () {
  var W = window.SaBanWeb, clamp = MP.clamp, seg = MP.seg;
  var tn = W.thuocNuoc();
  // mực nước 0..1 theo từng pha (minh hoạ định tính: triều lên – bãi cọc chìm; triều rút – cọc nhô lên)
  function muc(key, u) {
    switch (key) {
      case 'trien_khai': return 0.5;
      case 'tien_vao': return 0.5 + 0.42 * seg(u, 0.3, 0.9);
      case 'nhu': return 0.94;
      case 'trieu_rut': return 0.94 - 0.76 * seg(u, 0.0, 0.32);
      default: return 0.18;
    }
  }
  var CHU = {
    trien_khai: ['Bãi cọc ngầm', 'Cọc lớn vạt nhọn, đầu bịt sắt'],
    tien_vao: ['Nước triều lên', 'Thuyền nhẹ ra khiêu chiến'],
    nhu: ['Triều lên – cọc chìm', 'Quân giặc không hề hay biết'],
    trieu_rut: ['Triều rút – cọc nhô lên', 'Thuyền giặc mắc cọc'],
    ket_qua: ['Nước triều đã rút', 'Thuyền giặc lật úp, tan vỡ']
  };
  new W.MapPlayer(MP.khung(), {
    id: 'bd938', spec: window.MP_BANDO['bach-dang-938'],
    phases: [
      { key: 'trien_khai', nhan: 'Bố trí trận địa', canh: [5] },
      { key: 'tien_vao', nhan: 'Quân Nam Hán tiến vào', canh: [7] },
      { key: 'nhu', nhan: 'Giả thua, nhử địch', canh: [10] },
      { key: 'trieu_rut', nhan: 'Triều rút – phản công', canh: [11, 12] },
      { key: 'ket_qua', nhan: 'Kết quả', canh: [13] }
    ],
    overlay: tn.el,
    style: function (id, o, key, u) { return o.loai === 'coc' ? 1 - 0.62 * clamp((muc(key, u) - 0.45) / 0.5, 0, 1) : 1; },
    overlayUpdate: function (key, u) { var c = CHU[key]; tn.set(muc(key, u), c[0], key === 'trien_khai' ? 'Triều cao và thấp chênh nhau 2 – 3\u00A0m' : c[1]); },
    am: {
      nen: ['nuoc', 'song_bien', 'gio'], batDau: 'trong',
      nenPha: { trieu_rut: ['nuoc', 'gio', 'dam_dong'], ket_qua: ['nuoc', 'gio', 'dam_dong'] },
      moc: { trieu_rut: [[0.02, 'te_nuoc', { lv: 0.6 }]], nhu: [[0.02, 'te_nuoc', { lv: 0.5 }]] }
    },
    tomTat: W.tomTat(15, 'Tóm tắt: trận Bạch Đằng năm 938')
  });
});
