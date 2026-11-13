/* L9-B8-04 · Thời cơ ngàn năm có một – dòng thời gian tháng 8 – 1945 theo từng ngày, khởi nghĩa giành chính quyền ở các tỉnh lị.
   Bản đồ: pipeline/maps/specs/tong-khoi-nghia-1945.json (có quần đảo Hoàng Sa, Trường Sa). Mọi ngày, địa danh lấy từ kịch bản (SGK LSĐL 9 tr. 37–38). */
MP.onReady(function () {
  var root = MP.khung(), el = MP.el, W = window.SaBanWeb, S = window.MP_BANDO['tong-khoi-nghia-1945'];
  var BAC = { z: 2.7, tam: [381.5, 225.0], can_giua: [0.5, 0.5] }, TOAN = { z: 1.0, tam: null };
  var VONG = ['v_chau_tho', 'v_thanh_hoa', 'v_nghe_an', 'v_ha_tinh', 'v_thua_thien', 'v_quang_ngai', 'v_khanh_hoa'];
  function L(so, i) { var c = MP.canh(so); return c && c.loi[i]; }
  var NGAY = [
    { d: 13, loi: [[4, 0]], cam: BAC, am: ['trong'] },
    { d: 14, loi: [[4, 1], [7, 0]], obj: VONG, cam: TOAN, am: ['trong_nho', 'trong_nho'], tanTrao: 1 },
    { d: 15, loi: [[3, 0], [3, 1]], cam: TOAN, am: ['mo_pha'], tanTrao: 1 },
    { d: 16, loi: [[5, 0], [1, 0], [8, 0]], obj: ['tn'], cam: BAC, am: ['vut', 'buoc_quan'], tanTrao: 2 },
    { d: 17, loi: [[5, 0], [5, 1]], cam: BAC, am: ['mo_pha'], tanTrao: 2 },
    { d: 18, loi: [[9, 0], [9, 1]], obj: ['sao_bac_giang', 'sao_hai_duong', 'sao_ha_tinh', 'sao_quang_nam'], cam: TOAN, am: ['trong'] },
    { d: 19, loi: [[10, 0], [10, 1]], obj: ['sao_ha_noi'], cam: BAC, am: ['trong', 'reo'] },
    { d: 23, loi: [[12, 0]], obj: ['sao_hue'], cam: TOAN, am: ['trong'] },
    { d: 24, loi: [[12, 1]], obj: ['sao_sai_gon'], cam: TOAN, am: ['trong'] },
    { d: 25, loi: [[12, 1]], cam: TOAN, am: ['reo'] },
    { d: 28, loi: [[12, 2]], obj: ['sao_dong_nai_thuong', 'sao_ha_tien'], cam: TOAN, am: ['trong', 'chuong'] }
  ];
  var BANG = [
    { d: 18, ngay: '18 – 8', noi: 'Bắc Giang, Hải Dương, Hà Tĩnh, Quảng Nam', gc: 'Giành chính quyền ở tỉnh lị sớm nhất trong cả nước' },
    { d: 19, ngay: '19 – 8', noi: 'Hà Nội', gc: 'Đến tối, cuộc khởi nghĩa giành thắng lợi hoàn toàn' },
    { d: 23, ngay: '23 – 8', noi: 'Huế', gc: 'Giành chính quyền về tay nhân dân' },
    { d: 24, ngay: '24, 25 – 8', noi: 'Sài Gòn', gc: 'Tối 24 – 8 khởi nghĩa cơ bản giành thắng lợi; 25 – 8 chính quyền cách mạng ra mắt nhân dân' },
    { d: 28, ngay: '28 – 8', noi: 'Đồng Nai Thượng, Hà Tiên', gc: 'Hai tỉnh cuối cùng giành được chính quyền' }
  ];
  MP.nen(['dam_dong', 'gio']);

  // ---- giao diện
  root.appendChild(el('div', { class: 'sb-tieu-de' }, el('b', null, S.ten), el('span', null, 'Tháng 8 – 1945, theo từng ngày')));
  var hangNgay = el('div', { class: 'ngay-truc', role: 'tablist', 'aria-label': 'Các ngày có sự kiện' });
  var nutNgay = NGAY.map(function (n, i) {
    var b = el('button', { type: 'button', role: 'tab', class: 'co-su-kien', 'aria-current': 'false' }, String(n.d), el('small', null, 'tháng 8'));
    b.addEventListener('click', function () { dung(); chonNgay(i, true); }); hangNgay.appendChild(b); return b;
  });
  var san = el('div', { class: 'sb-san', style: { marginTop: '6px' } }), cv = el('canvas', { role: 'img', 'aria-label': 'Bản đồ Việt Nam tháng 8 năm 1945' });
  var mocEl = el('div', { class: 'sb-moc' }); san.appendChild(cv); san.appendChild(mocEl);
  var btnPrev = MP.nutIcon('prev', 'Ngày trước'), btnPlay = MP.nutIcon('play', 'Phát', 'chinh'), btnNext = MP.nutIcon('next', 'Ngày sau');
  var thanh = el('input', { type: 'range', min: '13', max: '28', step: '1', value: '13', 'aria-label': 'Ngày trong tháng 8 năm 1945' });
  var nhanNgay = el('span', { class: 'buoc' });
  var chuGiai = el('div', { class: 'sb-chu-giai' });
  [['vong', 'Khởi nghĩa ở nhiều xã, huyện'], ['mui_ten_ta', 'Giải phóng quân tiến công'], ['sao', 'Giành chính quyền']].forEach(function (c) { var k = el('canvas', { 'aria-hidden': 'true' }); W.veChuGiai(k, c[0]); chuGiai.appendChild(el('span', null, k, c[1])); });
  var kTT = el('canvas', { 'aria-hidden': 'true', width: 44, height: 24 }); chuGiai.appendChild(el('span', null, kTT, 'Tân Trào'));
  (function () { var x = kTT.getContext('2d'); x.strokeStyle = '#C98B2B'; x.lineWidth = 3; x.beginPath(); x.arc(22, 12, 8, 0, 7); x.stroke(); x.fillStyle = '#3c2f22'; x.beginPath(); x.arc(22, 12, 3, 0, 7); x.fill(); })();
  var loiEl = el('div', { class: 'sb-loi', 'aria-live': 'polite' });
  var bang = el('table', { class: 'bang-tinh' }), tbody = el('tbody');
  bang.appendChild(el('thead', null, el('tr', null, el('th', null, 'Ngày'), el('th', null, 'Nơi giành chính quyền'), el('th', null, 'Ghi chú'))));
  bang.appendChild(tbody);
  root.appendChild(hangNgay); root.appendChild(san);
  root.appendChild(el('div', { class: 'sb-dieu-khien', style: { marginTop: '8px' } }, btnPrev, btnPlay, btnNext, thanh, nhanNgay));
  root.appendChild(chuGiai); root.appendChild(el('div', { style: { height: '8px' } })); root.appendChild(loiEl);
  root.appendChild(el('h3', { style: { margin: '16px 0 8px', fontSize: '1rem' } }, 'Các nơi đã giành chính quyền (tính đến ngày đang chọn)'));
  root.appendChild(el('div', { style: { overflowX: 'auto' } }, bang));

  // ---- bản đồ
  var sb = new W.SaBan(S, {}), ctx = cv.getContext('2d'), dpr = 1, cw = 600, ch = 340, AR = (S.khung[2] - S.khung[0]) / (S.khung[3] - S.khung[1]);
  var st = { i: 0, t0: 0, now: 0, cam: { z: 1, tam: null }, camTu: null, chay: false, cho: 0 };
  function kichThuoc() {
    cw = san.clientWidth || 600; ch = Math.round(Math.max(260, Math.min(cw / AR, window.innerHeight * 0.7)));
    san.style.height = ch + 'px'; dpr = Math.min(2, window.devicePixelRatio || 1);
    cv.width = Math.round(cw * dpr); cv.height = Math.round(ch * dpr); sb.layout(cw, ch); ve();
  }
  var TAM_TOAN = [(S.khung[0] + S.khung[2]) / 2, (S.khung[1] + S.khung[3]) / 2];
  function camLuc(k) {
    var a = st.camTu || st.cam, b = NGAY[st.i].cam, ta = a.tam || TAM_TOAN, tb = b.tam || TAM_TOAN, e = MP.ease(k);
    // máy quay: giữ tâm cố định khi phóng, chuyển dần giữa toàn cảnh và miền Bắc
    return { z: a.z + (b.z - a.z) * e, tam: [ta[0] + (tb[0] - ta[0]) * e, ta[1] + (tb[1] - ta[1]) * e], can_giua: [0.5, 0.5] };
  }
  function ve() {
    var tt = (performance.now() - st.t0) / 1000, cam = camLuc(Math.min(1, tt / 0.9)), items = [], objs = S.doi_tuong;
    NGAY.forEach(function (n, j) {
      if (j > st.i || !n.obj) return;
      n.obj.forEach(function (id, q) { var k = j < st.i ? 1 : MP.seg(tt, 0.5 + q * 0.18, 1.1 + q * 0.18); if (k > 0) items.push({ id: id, o: objs[id], k: k }); });
    });
    var tanTrao = NGAY[st.i].tanTrao;
    sb.render(ctx, dpr, {
      cam: cam, items: items, t: tt,
      after: function (c, s) {
        if (!tanTrao) return;
        var p = s.P(objs.sao_tt.vi_tri), r = (14 + 3 * Math.sin(tt * 3)) * Math.max(0.8, s.g * 1.6);
        c.save(); s.screenMode(c); c.strokeStyle = 'rgba(201,139,43,.95)'; c.lineWidth = 3; c.beginPath(); c.arc(p[0], p[1], r, 0, 7); c.stroke(); c.restore();
      }
    });
    return tt < 3.2 || tanTrao;
  }
  var raf = 0, hien = true;
  function vong() {
    raf = 0; var tiep = ve();
    if (st.chay && performance.now() - st.t0 > 3600) { if (st.i < NGAY.length - 1) chonNgay(st.i + 1, true); else dung(); }
    if ((tiep || st.chay) && hien) raf = requestAnimationFrame(vong);
  }
  function chay() { if (!raf && hien) raf = requestAnimationFrame(vong); }
  MP.khiHien(san, function (v) { hien = v; if (v) chay(); });

  function chonNgay(i, am) {
    var cu = st.i;
    st.camTu = camLuc(Math.min(1, (performance.now() - st.t0) / 1000 / 0.9)); st.i = i; st.t0 = performance.now();
    var n = NGAY[i];
    nutNgay.forEach(function (b, j) { b.setAttribute('aria-current', j === i ? 'true' : 'false'); b.classList.toggle('da-qua', j < i); });
    if (nutNgay[i].scrollIntoView && am) nutNgay[i].scrollIntoView({ block: 'nearest', inline: 'center' });
    thanh.value = n.d; MP.toThanh(thanh); nhanNgay.textContent = n.d + ' – 8 – 1945';
    mocEl.textContent = n.d + ' – 8 – 1945';
    var lines = n.loi.map(function (x) { return L(x[0], x[1]); }).filter(Boolean);
    if (n.d === 18) lines.push(L(9, 1));
    MP.hopLoi(loiEl, lines.filter(function (x, k) { return lines.indexOf(x) === k; }), MP.trangCanh(n.loi.map(function (x) { return x[0]; })));
    tbody.innerHTML = '';
    BANG.forEach(function (r) {
      if (r.d > n.d) return;
      tbody.appendChild(el('tr', { class: r.d === n.d || (r.d === 24 && n.d === 25) ? 'moi' : '' }, el('td', { class: 'ngay' }, r.ngay), el('td', null, el('b', null, r.noi)), el('td', null, r.gc)));
    });
    if (!tbody.childNodes.length) tbody.appendChild(el('tr', null, el('td', { colspan: '3', style: { color: 'var(--chu-phu)' } }, 'Chưa có tỉnh lị nào giành chính quyền trong bảng – hãy chuyển sang ngày 18 – 8.')));
    if (am && i !== cu) {
      MP.am('lat_trang');
      (n.am || []).forEach(function (a, k) { MP.am(a, { tre: 0.35 + k * 0.5, n: 3 }); });
      (n.obj || []).forEach(function (id, q) { if (id.indexOf('sao') === 0) MP.am('chuong_nho', { tre: 0.6 + q * 0.18, cach: 40 }); });
    }
    chay();
  }
  function dung() { st.chay = false; MP.setIcon(btnPlay, 'play', 'Phát'); }
  btnPlay.addEventListener('click', function () {
    if (st.chay) { dung(); return; }
    if (st.i >= NGAY.length - 1) chonNgay(0, true);
    st.chay = true; st.t0 = performance.now(); MP.setIcon(btnPlay, 'pause', 'Tạm dừng'); MP.am('click'); chay();
  });
  btnPrev.addEventListener('click', function () { dung(); if (st.i > 0) chonNgay(st.i - 1, true); });
  btnNext.addEventListener('click', function () { dung(); if (st.i < NGAY.length - 1) chonNgay(st.i + 1, true); });
  thanh.addEventListener('input', function () {
    dung(); var d = +thanh.value, j = 0;
    NGAY.forEach(function (n, k) { if (n.d <= d) j = k; });   // ngày không có sự kiện mới: giữ trạng thái của ngày có sự kiện gần nhất trước đó
    if (j !== st.i) chonNgay(j, true); else { MP.toThanh(thanh); nhanNgay.textContent = d + ' – 8 – 1945'; }
  });
  if ('ResizeObserver' in window) new ResizeObserver(kichThuoc).observe(san); else window.addEventListener('resize', kichThuoc);
  MP.fontReady.then(function () { ve(); });
  kichThuoc(); st.cam = { z: BAC.z, tam: BAC.tam }; chonNgay(0, false);
});
