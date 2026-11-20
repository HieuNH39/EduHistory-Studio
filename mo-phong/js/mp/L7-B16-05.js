/* L7-B16-05 · Chi Lăng – Xương Giang (1427) – bản đồ động (dữ liệu: pipeline/maps/specs/chi-lang-xuong-giang.json) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  new W.MapPlayer(MP.khung(), {
    id: 'cl1427', spec: window.MP_BANDO['chi-lang-xuong-giang'],
    phases: [
      { key: 'vien_binh', nhan: 'Viện binh Minh tiến vào', canh: [3, 4] },
      { key: 'nhu_dich', nhan: 'Nhử địch vào trận địa', canh: [6] },
      { key: 'chi_lang', nhan: 'Phục kích ở ải Chi Lăng', canh: [8] },
      { key: 'xuong_giang', nhan: 'Cần Trạm, Phố Cát, Xương Giang', canh: [10, 11] }
    ],
    am: {
      nen: ['gio', 'chim'], nenPha: { chi_lang: ['gio', 'dam_dong'], xuong_giang: ['gio', 'dam_dong'] }, batDau: 'trong',
      doiTuong: function (id, o) { if (o.loai === 'mui_ten_dich') return ['vut_nhe', 'buoc_quan']; if (o.loai === 'nhan') return 'trong_nho'; }
    },
    tomTat: W.tomTat(15, 'Tóm tắt: 1427 – 1428')
  });
});
