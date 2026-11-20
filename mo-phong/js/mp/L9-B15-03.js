/* L9-B15-03 · Chiến dịch Điện Biên Phủ – 3 đợt tấn công, nhấn mạnh sân bay Mường Thanh (dữ liệu: pipeline/maps/specs/dien-bien-phu.json) */
MP.onReady(function () {
  var W = window.SaBanWeb, S = window.MP_BANDO['dien-bien-phu'], sb = S.doi_tuong.sb_mt;
  new W.MapPlayer(MP.khung(), {
    id: 'dbp', spec: S,
    phases: [
      { key: 'tap_doan', nhan: 'Tập đoàn cứ điểm', canh: [4] },
      { key: 'dot1', nhan: 'Đợt 1', canh: [9] },
      { key: 'dot2', nhan: 'Đợt 2 – sân bay Mường Thanh', canh: [10] },
      { key: 'dot3', nhan: 'Đợt 3 – toàn thắng', canh: [12] }
    ],
    // làm nổi bật sân bay Mường Thanh trong đợt 2 (vòng sáng nhấp nháy quanh kí hiệu sân bay)
    after: function (ctx, s, key, u, pl) {
      if (key !== 'dot2' || u < 0.5) return;
      var p = s.P(sb.vi_tri), k = MP.seg(u, 0.5, 0.62), r = (34 + 6 * Math.sin(pl.t * 4)) * s.g * s.z;
      ctx.save(); s.screenMode(ctx); ctx.strokeStyle = 'rgba(242,107,29,' + (0.9 * k) + ')'; ctx.lineWidth = 3; ctx.setLineDash([8, 6]);
      ctx.beginPath(); ctx.arc(p[0], p[1], r, 0, Math.PI * 2); ctx.stroke(); ctx.restore(); s.anim = true;
    },
    am: {
      nen: ['gio', 'phao_xa'], nenPha: { tap_doan: ['gio', 'chim'] }, no: true,
      batDau: function (k) { return k === 'tap_doan' ? 'mo_pha' : 'trong'; },
      doiTuong: function (id, o, kieu) { if (kieu === 'hien' && o.loai === 'cu_diem') return 'tick'; if (o.loai === 'nhan') return id === 'san_bay_nhan' ? 'chuong_nho' : null; }
    },
    tomTat: W.tomTat(14, 'Tóm tắt: chiến dịch Điện Biên Phủ')
  });
});
