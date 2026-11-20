/* L8-B2-03 · Ngày 14/7: Khi pháo đài Ba-xti sụp đổ – bản đồ tương tác + trục thời gian Cách mạng tư sản Pháp (1789 – 1794).
   Sự kiện, ngày tháng lấy từ kịch bản (SGK LSĐL 8 tr. 13–14). Nền đất liền Natural Earth 1:110m, không vẽ biên giới quốc gia. */
MP.onReady(function () {
  var root = MP.khung(), el = MP.el;
  function L(so, i) { var c = MP.canh(so); return c ? (i == null ? c.loi : [c.loi[i]]) : []; }
  var NGAY0 = Date.UTC(1789, 6, 14), NGAY1 = Date.UTC(1794, 6, 27);
  function vt(y, m, d) { return (Date.UTC(y, m - 1, d) - NGAY0) / (NGAY1 - NGAY0); }
  var CHE_DO = ['Quân chủ chuyên chế', 'Quân chủ lập hiến', 'Nền cộng hoà đầu tiên', 'Chuyên chính dân chủ cách mạng Gia-cô-banh', 'Cách mạng kết thúc'];
  var BUOC = [
    { ngay: 'Trước năm 1789', tieu: 'Nước Pháp trước cách mạng', loi: L(3), canh: [3], x: null, cd: 0, cam: 'rong', am: ['lat_trang'], nen: ['gio', 'nen_em'] },
    { ngay: '14 – 7 – 1789', tieu: 'Tấn công pháo đài – nhà tù Ba-xti', loi: L(5), canh: [4, 5], x: vt(1789, 7, 14), cd: 0.5, cam: 'pa_ri', am: ['trong', 'reo'], nen: ['dam_dong', 'gio'], co: true },
    { ngay: '26 – 8 – 1789', tieu: 'Tuyên ngôn Nhân quyền và Dân quyền', loi: L(7), canh: [7, 8], x: vt(1789, 8, 26), cd: 0.5, cam: 'pa_ri', am: ['lat_trang', 'chuong_nho'], nen: ['gio', 'nen_em'], emCoBiet: true },
    { ngay: 'Giai đoạn 1 (14 – 7 – 1789 đến 10 – 8 – 1792)', tieu: 'Kết quả giai đoạn thứ nhất', loi: L(9, 2), canh: [9], x: null, cd: 1, cam: 'rong', am: ['mo_pha'], nen: ['gio', 'nen_em'] },
    { ngay: '10 – 8 – 1792', tieu: 'Giai đoạn thứ hai', loi: L(10), canh: [10], x: vt(1792, 8, 10), cd: 2, cam: 'rong', am: ['mo_pha', 'reo'], nen: ['dam_dong', 'gio'] },
    { ngay: '2 – 6 – 1793', tieu: 'Giai đoạn thứ ba', loi: L(11), canh: [11], x: vt(1793, 6, 2), cd: 3, cam: 'rong', am: ['trong'], nen: ['gio', 'nen_em'] },
    { ngay: '27 – 7 – 1794', tieu: 'Cách mạng kết thúc', loi: L(12), canh: [12], x: vt(1794, 7, 27), cd: 4, cam: 'rong', am: ['mo_pha'], nen: ['gio'] }
  ];
  var GIAI = [[0, vt(1792, 8, 10), 'Giai đoạn 1', '#F26B1D'], [vt(1792, 8, 10), vt(1793, 6, 2), 'Giai đoạn 2', '#C98B2B'], [vt(1793, 6, 2), 1, 'Giai đoạn 3', '#2e3e73']];

  // ---- bố cục
  var san = el('div', { class: 'sb-san' }), cv = el('canvas', { role: 'img', 'aria-label': 'Bản đồ Tây Âu, đánh dấu Pa-ri' });
  var mocEl = el('div', { class: 'sb-moc' }); san.appendChild(cv); san.appendChild(mocEl);
  var truc = el('div', { style: { position: 'relative', height: '92px', margin: '46px 14px 4px' } });
  var nutBuoc = [];
  GIAI.forEach(function (g) { truc.appendChild(el('div', { style: { position: 'absolute', left: (g[0] * 100) + '%', width: ((g[1] - g[0]) * 100) + '%', top: '38px', height: '10px', background: g[3], opacity: 0.85, borderRadius: '5px' } })); truc.appendChild(el('div', { style: { position: 'absolute', left: (g[0] * 100) + '%', width: ((g[1] - g[0]) * 100) + '%', top: '52px', fontSize: '.72rem', fontWeight: 700, color: g[3], textAlign: 'center' } }, g[2])); });
  [1789, 1790, 1791, 1792, 1793, 1794].forEach(function (y) { var x = y === 1789 ? 0 : vt(y, 1, 1); truc.appendChild(el('div', { style: { position: 'absolute', left: (x * 100) + '%', top: '72px', transform: 'translateX(-50%)', fontSize: '.72rem', color: 'var(--chu-phu)' } }, String(y))); });
  BUOC.forEach(function (b, i) {
    if (b.x == null) return;
    var n = el('button', { type: 'button', class: 'nut tron', 'aria-label': b.ngay + ': ' + b.tieu, title: b.ngay, style: { position: 'absolute', left: 'calc(' + (b.x * 100) + '% - 21px)', top: (i === 2 ? '-22px' : '22px'), width: '42px', height: '42px', fontWeight: 800 } }, String(i));
    n.addEventListener('click', function () { dung(); chon(i, true); }); truc.appendChild(n); nutBuoc[i] = n;
  });
  var btnPrev = MP.nutIcon('prev', 'Mốc trước'), btnPlay = MP.nutIcon('play', 'Phát', 'chinh'), btnNext = MP.nutIcon('next', 'Mốc sau');
  var nutTruoc = el('button', { type: 'button', class: 'nut' }, 'Trước năm 1789'), nutKQ = el('button', { type: 'button', class: 'nut' }, 'Kết quả giai đoạn 1');
  nutTruoc.addEventListener('click', function () { dung(); chon(0, true); }); nutKQ.addEventListener('click', function () { dung(); chon(3, true); });
  var the = el('div', { class: 'sb-loi', 'aria-live': 'polite' }), thang = el('ol', { class: 'cac-buoc', style: { counterReset: 'none' } });
  var CO = el('canvas', { width: 54, height: 36, 'aria-hidden': 'true', style: { width: '54px', height: '36px', flex: 'none' } });
  (function () { var x = CO.getContext('2d'); [['#1f3f9b', 0], ['#ffffff', 18], ['#c8202a', 36]].forEach(function (c) { x.fillStyle = c[0]; x.fillRect(c[1], 0, 18, 36); }); x.strokeStyle = '#999'; x.strokeRect(0.5, 0.5, 53, 35); })();
  var coBox = el('div', { class: 'the-tin', style: { display: 'none', alignItems: 'center', gap: '12px' } }, CO, el('span', null, MP.canh(4).loi[1]));
  var emBox = el('div', { class: 'the-tin', style: { display: 'none', borderLeft: '4px solid var(--vang)' } }, el('h3', null, 'Em có biết?'), el('p', null, (MP.canh(8).y || [])[0] || ''), el('p', { style: { fontSize: '.8rem', color: 'var(--chu-phu)' } }, MP.trang(MP.canh(8).tr)));
  CHE_DO.forEach(function (c) { thang.appendChild(el('li', null, el('div', { class: 'nut', style: { width: '100%', justifyContent: 'flex-start', cursor: 'default' } }, el('b', null, '•'), c))); });
  root.appendChild(el('div', { class: 'sb-tieu-de' }, el('b', null, 'Cách mạng tư sản Pháp'), el('span', null, '14 – 7 – 1789 đến 27 – 7 – 1794')));
  root.appendChild(el('div', { style: { height: '8px' } }));
  root.appendChild(san);
  root.appendChild(truc);
  root.appendChild(el('div', { class: 'hang-nut', style: { justifyContent: 'space-between' } }, el('div', { class: 'hang-nut' }, btnPrev, btnPlay, btnNext), el('div', { class: 'hang-nut' }, nutTruoc, nutKQ)));
  root.appendChild(el('div', { class: 'bang-dk' }, el('div', null, the, el('div', { style: { height: '10px' } }), coBox, emBox), el('div', { class: 'the-tin' }, el('h3', null, 'Chế độ chính trị ở Pháp'), thang)));

  // ---- bản đồ
  var ctx = cv.getContext('2d'), dpr = 1, cw = 600, ch = 360;
  var VONG = (window.MP_GEO ? MP_GEO.vong : []).map(function (v) { var b = [999, 999, -999, -999]; v.d.forEach(function (p) { b[0] = Math.min(b[0], p[0]); b[1] = Math.min(b[1], p[1]); b[2] = Math.max(b[2], p[0]); b[3] = Math.max(b[3], p[1]); }); return { d: v.d, lo: v.lo, b: b }; });
  var CAM = { rong: { lon: 3, lat: 48.3, span: 30 }, pa_ri: { lon: 1.6, lat: 48.6, span: 13 } }, PARI = [2.35, 48.86];
  var st = { i: 0, cam: { lon: 3, lat: 48.3, span: 30 }, camTu: null, t0: 0, chay: false };
  function kichThuoc() { cw = san.clientWidth || 600; ch = Math.round(Math.max(240, Math.min(cw / (cw < 600 ? 1.25 : 1.9), window.innerHeight * 0.55))); san.style.height = ch + 'px'; dpr = Math.min(2, window.devicePixelRatio || 1); cv.width = Math.round(cw * dpr); cv.height = Math.round(ch * dpr); ve(); }
  function ve() {
    var tt = (performance.now() - st.t0) / 1000, e = MP.ease(Math.min(1, tt / 1.1)), a = st.camTu || CAM.rong, b = CAM[BUOC[st.i].cam];
    var cam = { lon: a.lon + (b.lon - a.lon) * e, lat: a.lat + (b.lat - a.lat) * e, span: Math.exp(Math.log(a.span) + (Math.log(b.span) - Math.log(a.span)) * e) };
    st.cam = cam;
    var cl = Math.cos(cam.lat * Math.PI / 180), k = cw / (cam.span * cl);
    function X(lon) { return cw / 2 + (lon - cam.lon) * cl * k; } function Y(lat) { return ch / 2 - (lat - cam.lat) * k; }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.fillStyle = '#cfe2ec'; ctx.fillRect(0, 0, cw, ch);
    ctx.strokeStyle = 'rgba(255,255,255,.6)'; ctx.lineWidth = 1;
    var lo0 = cam.lon - cam.span, lo1 = cam.lon + cam.span, la0 = cam.lat - cam.span, la1 = cam.lat + cam.span;
    VONG.forEach(function (v) {
      if (v.b[2] < lo0 || v.b[0] > lo1 || v.b[3] < la0 || v.b[1] > la1) return;
      ctx.beginPath(); v.d.forEach(function (p, j) { if (j) ctx.lineTo(X(p[0]), Y(p[1])); else ctx.moveTo(X(p[0]), Y(p[1])); }); ctx.closePath();
      ctx.fillStyle = v.lo ? '#cfe2ec' : '#efe4c8'; ctx.fill(); ctx.strokeStyle = 'rgba(130,118,96,.85)'; ctx.lineWidth = 1.2; ctx.stroke();
    });
    function chu(s, x, y, px, o) {
      o = o || {}; ctx.font = (o.it ? 'italic ' : '') + (o.dam ? '700 ' : '400 ') + px + 'px "Be Vietnam Pro", system-ui, sans-serif'; ctx.textAlign = o.can || 'center'; ctx.textBaseline = 'middle';
      ctx.lineJoin = 'round'; ctx.strokeStyle = 'rgba(244,239,228,.9)'; ctx.lineWidth = px * 0.28; ctx.strokeText(s, x, y); ctx.fillStyle = o.mau || '#3c2f22'; ctx.fillText(s, x, y);
    }
    var gan = cam.span < 16;
    if (!gan) chu('PHÁP', X(2.4), Y(46.6), Math.max(14, cw / 40), { dam: true, mau: 'rgba(60,47,34,.7)' });
    var px = X(PARI[0]), py = Y(PARI[1]), nhip = 1 + 0.25 * Math.sin(tt * 4);
    if (st.i > 0) { ctx.beginPath(); ctx.arc(px, py, 14 * nhip, 0, 7); ctx.strokeStyle = 'rgba(184,38,30,.6)'; ctx.lineWidth = 2.5; ctx.stroke(); }
    ctx.beginPath(); ctx.arc(px, py, 6, 0, 7); ctx.fillStyle = '#b8261e'; ctx.fill(); ctx.strokeStyle = '#fff'; ctx.lineWidth = 2; ctx.stroke();
    chu('Pa-ri', px + 12, py - 12, gan ? 18 : 14, { dam: true, can: 'left' });
    if (BUOC[st.i].co) {   // pháo đài – nhà tù Ba-xti và lá cờ ba màu
      var fx = px - 70, fy = py + 46, s = Math.min(1.2, Math.max(0.7, cw / 800));
      ctx.save(); ctx.translate(fx, fy); ctx.scale(s, s);
      ctx.fillStyle = '#7d756a'; ctx.fillRect(-36, -18, 72, 30);
      [-36, -12, 12].forEach(function (tx) { ctx.fillRect(tx, -34, 24, 46); ctx.fillStyle = '#6a6359'; for (var m = 0; m < 3; m++) ctx.fillRect(tx + m * 9, -40, 6, 6); ctx.fillStyle = '#7d756a'; });
      ctx.fillStyle = '#3d362e'; ctx.fillRect(-6, -2, 12, 14);
      ctx.restore();
      chu('Pháo đài – nhà tù Ba-xti', fx, fy + 26 * s, gan ? 13 : 12, { dam: true });
      var gx = px + 34, gy = py + 10, w = 48 * s, h = 30 * s;
      ctx.strokeStyle = '#4d3b2a'; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(gx, gy + 44 * s); ctx.lineTo(gx, gy - 4); ctx.stroke();
      ['#1f3f9b', '#ffffff', '#c8202a'].forEach(function (c, j) {
        ctx.fillStyle = c; ctx.beginPath();
        for (var q = 0; q <= 8; q++) { var xx = gx + (j + q / 8) * w / 3, yy = gy - 2 + Math.sin(tt * 5 + (j * 8 + q) * 0.35) * 2.5 * (j + q / 8) / 3; if (q === 0) ctx.moveTo(xx, yy); else ctx.lineTo(xx, yy); }
        for (q = 8; q >= 0; q--) { var x2 = gx + (j + q / 8) * w / 3, y2 = gy - 2 + h + Math.sin(tt * 5 + (j * 8 + q) * 0.35) * 2.5 * (j + q / 8) / 3; ctx.lineTo(x2, y2); }
        ctx.closePath(); ctx.fill();
      });
      ctx.strokeStyle = 'rgba(0,0,0,.25)'; ctx.lineWidth = 1; ctx.strokeRect(gx, gy - 2, w, h);
    }
    return tt < 1.3 || st.i > 0;
  }
  var raf = 0, hien = true;
  function vong() { raf = 0; var tiep = ve(); if (st.chay && performance.now() - st.t0 > 4500) { if (st.i < BUOC.length - 1) chon(st.i + 1, true); else dung(); } if ((tiep || st.chay) && hien) raf = requestAnimationFrame(vong); }
  function chay() { if (!raf && hien) raf = requestAnimationFrame(vong); }
  MP.khiHien(san, function (v) { hien = v; if (v) chay(); });

  function chon(i, am) {
    st.camTu = { lon: st.cam.lon, lat: st.cam.lat, span: st.cam.span }; st.i = i; st.t0 = performance.now();
    var b = BUOC[i];
    nutBuoc.forEach(function (n, j) { if (n) n.setAttribute('aria-pressed', j === i ? 'true' : 'false'); });
    nutTruoc.setAttribute('aria-pressed', i === 0 ? 'true' : 'false'); nutKQ.setAttribute('aria-pressed', i === 3 ? 'true' : 'false');
    mocEl.textContent = b.ngay;
    the.innerHTML = ''; the.appendChild(el('p', null, el('b', { style: { color: 'var(--do)' } }, b.ngay), ' · ', el('b', null, b.tieu)));
    b.loi.forEach(function (l) { if (l) the.appendChild(el('p', null, l)); }); the.appendChild(el('p', { class: 'tr' }, MP.trang(MP.trangCanh(b.canh))));
    coBox.style.display = b.co ? 'flex' : 'none'; emBox.style.display = b.emCoBiet ? '' : 'none';
    [].forEach.call(thang.children, function (li, j) {
      var nn = li.firstChild, xong = j < b.cd, nay = j === Math.round(b.cd) || (b.cd % 1 && j === Math.floor(b.cd));
      nn.classList.toggle('dang-chon', j === b.cd); nn.style.opacity = j > Math.ceil(b.cd) ? 0.45 : 1;
      nn.firstChild.textContent = xong && j !== b.cd ? '✓' : '•';
      nn.style.borderColor = nay ? 'var(--cam)' : '';
    });
    if (am) { MP.nen(b.nen); b.am.forEach(function (a, k) { MP.am(a, { tre: k * 0.5, n: 4, lv: 0.7 }); }); } else MP.nen(b.nen);
    chay();
  }
  function dung() { st.chay = false; MP.setIcon(btnPlay, 'play', 'Phát'); }
  btnPlay.addEventListener('click', function () { if (st.chay) { dung(); return; } if (st.i >= BUOC.length - 1) chon(0, true); st.chay = true; st.t0 = performance.now(); MP.setIcon(btnPlay, 'pause', 'Tạm dừng'); MP.am('click'); chay(); });
  btnPrev.addEventListener('click', function () { dung(); if (st.i > 0) chon(st.i - 1, true); });
  btnNext.addEventListener('click', function () { dung(); if (st.i < BUOC.length - 1) chon(st.i + 1, true); });
  var tt2 = MP.canh(13);
  if (tt2 && tt2.moc) { var ol = el('ol', { class: 'dong-moc' }); tt2.moc.forEach(function (m) { ol.appendChild(el('li', null, el('b', null, m[0]), el('span', null, m[1]))); }); root.appendChild(el('div', { class: 'tom-tat', style: { marginTop: '14px' } }, el('h3', null, 'Tiến trình Cách mạng tư sản Pháp'), ol, el('p', { style: { fontSize: '.8rem', color: 'var(--chu-phu)', margin: '6px 0 0' } }, MP.trang(tt2.tr)))); }
  if ('ResizeObserver' in window) new ResizeObserver(kichThuoc).observe(san); else window.addEventListener('resize', kichThuoc);
  MP.fontReady.then(ve);
  kichThuoc(); chon(0, false);
});
