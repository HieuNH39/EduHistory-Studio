/* L8-B8-03 · Đại phá quân Thanh (Tết 1789) – sơ đồ mũi tên tiến công (dữ liệu: pipeline/maps/specs/ngoc-hoi-dong-da.json) */
MP.onReady(function () {
  var W = window.SaBanWeb;
  new W.MapPlayer(MP.khung(), {
    id: 'nhdd', spec: window.MP_BANDO['ngoc-hoi-dong-da'],
    phu_de: 'Ngọc Hồi – Đống Đa, Tết năm 1789',
    phases: [
      { key: 'boi_canh', nhan: 'Quân Thanh chiếm Thăng Long', canh: [4, 5, 6] },
      { key: 'ha_hoi', nhan: 'Gián Khẩu – Hà Hồi', canh: [8, 9] },
      { key: 'ngoc_hoi_dong_da', nhan: 'Ngọc Hồi – Đống Đa', canh: [11, 12, 13] },
      { key: 'thang_long', nhan: 'Tiến vào Thăng Long', canh: [15, 16] }
    ],
    // nhãn mốc chỉ ghi những gì có trong kịch bản
    moc: { ha_hoi: [{ chu: 'Đêm 30 Tết (25 – 1 – 1789): vượt sông Gián Khẩu', tu: 0.02, den: 0.45 }, { chu: 'Đêm mồng 3 Tết: vây đồn Hà Hồi', tu: 0.47 }] },
    am: {
      nen: ['gio', 'dam_dong'], batDau: 'trong',
      doiTuong: function (id, o, kieu) { if (kieu === 'mat') return 'gay_go'; if (o.loai === 'mui_ten_ta') return ['vut', 'buoc_quan']; if (o.loai === 'don_dich') return null; }
    }
  });
});
