/* L6-B3-03 · Giải mã Công lịch – trục thời gian kéo thả, tính khoảng cách giữa năm TCN và năm Công nguyên.
   Quy ước nội bộ: năm "thiên văn" a: năm n Công nguyên → n; năm n TCN → 1 − n (năm 1 TCN → 0). Không có năm 0 trong Công lịch,
   nên khoảng cách chính xác = |a − b|; theo cách tính trong SGK (cộng hai số năm) được số lớn hơn 1 (kịch bản cảnh 8). */
MP.onReady(function () {
  var root = MP.khung(), el = MP.el, NS = 'http://www.w3.org/2000/svg';
  var NAM_NAY = new Date().getFullYear();
  MP.nen(['dong_ho', 'nen_em']);
  function sv(tag, a) { var e = document.createElementNS(NS, tag); for (var k in a) e.setAttribute(k, a[k]); return e; }
  function ra(a) { return a >= 1 ? { so: a, tcn: false } : { so: 1 - a, tcn: true }; }
  function vao(so, tcn) { return tcn ? 1 - so : so; }
  // năm viết liền (2026, 3000 TCN) như SGK; số năm (khoảng cách) mới tách nhóm nghìn (2 233 năm)
  function ten(a) { var r = ra(a); return 'năm ' + r.so + (r.tcn ? ' TCN' : ''); }
  function TEN(a) { var r = ra(a); return 'Năm ' + r.so + (r.tcn ? ' TCN' : ''); }
  function nhan(a) { var r = ra(a); return r.so + (r.tcn ? ' TCN' : ''); }

  // ---- giao diện
  var st = { a: vao(208, true), b: 2026, view: 'rong', dv: 'the_ki' };
  var hop = el('div', { class: 'ttg-truc' }), svg = sv('svg', { role: 'img', 'aria-label': 'Trục Công lịch với hai chốt A và B' });
  hop.appendChild(svg);
  var nutRong = el('button', { type: 'button', class: 'nut', 'aria-pressed': 'true' }, 'Toàn trục');
  var nutHep = el('button', { type: 'button', class: 'nut', 'aria-pressed': 'false' }, 'Phóng to quanh năm 1');
  function oNhap(id, chip) {
    var so = el('input', { type: 'number', min: '1', max: '5000', step: '1', 'aria-label': 'Số năm của mốc ' + id });
    var ky = el('select', { 'aria-label': 'Trước hay sau Công nguyên (mốc ' + id + ')' }, el('option', { value: 'tcn' }, 'TCN'), el('option', { value: 'cn' }, 'Công nguyên'));
    var tru = el('button', { type: 'button', class: 'nut tron', 'aria-label': 'Lùi 1 năm' }, '−'), cong = el('button', { type: 'button', class: 'nut tron', 'aria-label': 'Tiến 1 năm' }, '+');
    return { w: el('div', { class: 'o-nhap' }, el('span', { class: 'chip ' + chip }, 'Mốc ' + id), so, ky, tru, cong), so: so, ky: ky, tru: tru, cong: cong };
  }
  var A = oNhap('A', 'a'), B = oNhap('B', 'b');
  var kq = el('div', { class: 'ket-qua', 'aria-live': 'polite' });
  var dvChon = el('div', { class: 'hang-nut', role: 'group', 'aria-label': 'Đơn vị thời gian' });
  var DV = { thap_ki: ['Thập kỉ', 10], the_ki: ['Thế kỉ', 100], thien_nien_ki: ['Thiên niên kỉ', 1000] };
  var nutDv = Object.keys(DV).map(function (k) { var b = el('button', { type: 'button', class: 'nut', 'aria-pressed': k === st.dv ? 'true' : 'false' }, DV[k][0] + ' (' + MP.so(DV[k][1]) + ' năm)'); b.addEventListener('click', function () { st.dv = k; nutDv.forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); }); MP.am('click'); ve(); }); dvChon.appendChild(b); return b; });
  var dvKq = el('div', { class: 'ket-qua', 'aria-live': 'polite' });
  var VD = [
    { ten: 'Thục Phán lập nước Âu Lạc (khoảng 208 TCN) → năm 2026', a: vao(208, true), b: 2026, canh: 8 },
    { ten: 'Năm 1 TCN → năm 1 Công nguyên', a: 0, b: 1, canh: 4 },
    { ten: 'Thế kỉ XXI: năm 2001 → năm 2100', a: 2001, b: 2100, canh: 6 }
  ];
  var vdW = el('div', { class: 'hang-nut' });
  VD.forEach(function (v) { var b = el('button', { type: 'button', class: 'nut' }, v.ten); b.addEventListener('click', function () { st.a = v.a; st.b = v.b; if (v.b <= 10 && v.a > -10) datView('hep'); else datView('rong'); MP.am('xac_nhan'); ve(); loiVd.textContent = MP.loi([v.canh]).join(' '); }); vdW.appendChild(b); });
  var loiVd = el('p', { 'aria-live': 'polite', style: { fontSize: '.9rem', color: 'var(--chu-phu)', margin: '6px 0 0' } });

  root.appendChild(el('div', { class: 'hang-nut', style: { marginBottom: '8px' } }, nutRong, nutHep));
  root.appendChild(hop);
  root.appendChild(el('div', { class: 'bang-dk' },
    el('div', { class: 'the-tin' }, el('h3', null, 'Đặt hai mốc'), A.w, el('div', { style: { height: '8px' } }), B.w, el('h3', { style: { marginTop: '12px' } }, 'Ví dụ có sẵn'), vdW, loiVd),
    el('div', null, kq, el('div', { style: { height: '10px' } }), el('div', { class: 'the-tin' }, el('h3', null, 'Đơn vị thời gian của mốc B'), dvChon, el('div', { style: { height: '8px' } }), dvKq))));

  // thử thách cuối video (cảnh 11): năm 2000 TCN cách năm nay bao nhiêu năm?
  var ttIn = el('input', { type: 'number', min: '0', max: '9999', 'aria-label': 'Câu trả lời thử thách' });
  var ttFb = el('p', { class: 'thong-bao', 'aria-live': 'polite' });
  var ttNut = el('button', { type: 'button', class: 'nut chinh' }, 'Kiểm tra');
  var ttGy = el('button', { type: 'button', class: 'nut' }, 'Xem trên trục');
  var gan = 2000 + NAM_NAY, chinhXac = 2000 + NAM_NAY - 1;
  ttNut.addEventListener('click', function () {
    var v = +ttIn.value;
    if (v === chinhXac || v === gan) { ttFb.className = 'thong-bao dung'; ttFb.textContent = 'Đúng rồi! Cộng hai số năm: 2000 + ' + NAM_NAY + ' = ' + MP.so(gan) + ' (khoảng). Tính thật chính xác thì trừ 1 vì không có năm 0: ' + MP.so(chinhXac) + ' năm.'; MP.am('chuong'); }
    else { ttFb.className = 'thong-bao sai'; ttFb.textContent = 'Chưa đúng. Gợi ý: một mốc trước Công nguyên, một mốc Công nguyên → cộng hai số năm lại.'; MP.am('sai'); }
  });
  ttGy.addEventListener('click', function () { st.a = vao(2000, true); st.b = NAM_NAY; datView('rong'); ve(); MP.am('lat_trang'); });
  root.appendChild(el('div', { class: 'the-tin', style: { marginTop: '12px' } }, el('h3', null, 'Thử thách'), el('p', null, MP.loi([11])[0] || ''),
    el('p', { style: { fontSize: '.86rem', color: 'var(--chu-phu)' } }, '(“Năm nay” lấy theo đồng hồ máy của em: năm ' + NAM_NAY + '.)'),
    el('div', { class: 'o-nhap' }, el('label', null, 'Đáp số:'), ttIn, el('span', null, 'năm'), ttNut, ttGy), ttFb));
  var ghiNho = MP.canh(10);
  if (ghiNho && ghiNho.y) { var ul = el('ul'); ghiNho.y.forEach(function (y) { ul.appendChild(el('li', null, y)); }); root.appendChild(el('div', { class: 'the-tin', style: { marginTop: '12px' } }, el('h3', null, 'Ghi nhớ'), ul, el('p', { style: { fontSize: '.8rem', color: 'var(--chu-phu)', margin: '6px 0 0' } }, MP.trang(ghiNho.tr)))); }

  // ---- vẽ trục
  var W = 900, H = 236, M = 34, Y0 = 128;
  function pham() { return st.view === 'hep' ? [-9, 10] : [-3200, 2200]; }
  function X(a) { var p = pham(); return M + (a - p[0]) / (p[1] - p[0]) * (W - 2 * M); }
  function nguoc(x) { var p = pham(); return Math.round(p[0] + (x - M) / (W - 2 * M) * (p[1] - p[0])); }
  function datView(v) { st.view = v; nutRong.setAttribute('aria-pressed', v === 'rong' ? 'true' : 'false'); nutHep.setAttribute('aria-pressed', v === 'hep' ? 'true' : 'false'); }
  nutRong.addEventListener('click', function () { datView('rong'); MP.am('lat_trang'); ve(); });
  nutHep.addEventListener('click', function () { datView('hep'); if (st.a < -9 || st.a > 10) st.a = 0; if (st.b < -9 || st.b > 10) st.b = 1; MP.am('lat_trang'); ve(); });
  function txt(x, y, s, o) { var t = sv('text', Object.assign({ x: x, y: y, 'font-size': 13, 'text-anchor': 'middle', fill: '#10233F', 'font-family': 'Be Vietnam Pro, system-ui, sans-serif' }, o || {})); t.textContent = s; return t; }
  function ve() {
    W = Math.max(320, Math.round(hop.clientWidth || 900)); var hep = W < 560;
    svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H); svg.setAttribute('width', W); svg.setAttribute('height', H);
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    var p = pham(), xB = X(0.5);
    svg.appendChild(sv('rect', { x: M, y: Y0 - 26, width: xB - M, height: 52, fill: '#fde6d8', rx: 6 }));
    svg.appendChild(sv('rect', { x: xB, y: Y0 - 26, width: W - M - xB, height: 52, fill: '#dfe6f6', rx: 6 }));
    svg.appendChild(txt((M + xB) / 2, Y0 + 20, 'TRƯỚC CÔNG NGUYÊN (TCN)', { 'font-size': hep ? 10 : 12, 'font-weight': 700, fill: '#a2410b' }));
    svg.appendChild(txt((xB + W - M) / 2, Y0 + 20, 'CÔNG NGUYÊN', { 'font-size': hep ? 10 : 12, 'font-weight': 700, fill: '#233a79' }));
    // dải sự kiện, đơn vị
    if (st.view === 'rong') {
      [[vao(3000, true), vao(2001, true), 'Người Ai Cập biết làm lịch (khoảng thiên niên kỉ III TCN)', '#C98B2B'], [2001, 2100, 'Thế kỉ XXI', '#1f7a4d']].forEach(function (d) {
        var x1 = X(d[0]), x2 = Math.max(X(d[1]), x1 + 4);
        svg.appendChild(sv('rect', { x: x1, y: Y0 + 30, width: x2 - x1, height: 8, fill: d[3], rx: 3, opacity: 0.85 }));
        svg.appendChild(txt(d[1] > 0 ? x2 : x1, Y0 + 52, d[2], { 'font-size': hep ? 9.5 : 11, fill: d[3], 'text-anchor': d[1] > 0 ? 'end' : 'start', 'font-weight': 600 }));
      });
    }
    var dv = DV[st.dv][1], bD = ra(st.b), so = Math.ceil(bD.so / dv), dau = (so - 1) * dv + 1, cuoi = so * dv;
    var u1 = vao(bD.tcn ? cuoi : dau, bD.tcn), u2 = vao(bD.tcn ? dau : cuoi, bD.tcn);
    var xu1 = Math.max(M, X(Math.min(u1, u2))), xu2 = Math.min(W - M, X(Math.max(u1, u2)));
    if (xu2 - xu1 >= 1) svg.appendChild(sv('rect', { x: xu1, y: Y0 - 30, width: Math.max(2, xu2 - xu1), height: 60, fill: 'rgba(46,62,115,.16)', stroke: '#2e3e73', 'stroke-dasharray': '4 3' }));
    // trục và vạch chia
    svg.appendChild(sv('line', { x1: M, y1: Y0, x2: W - M, y2: Y0, stroke: '#10233F', 'stroke-width': 3 }));
    if (st.view === 'rong') {
      var buoc = hep ? 1000 : 500;
      for (var n = -3000; n <= 2000; n += buoc) {
        var a = n <= 0 ? vao(-n, true) : n; if (n === 0) continue; var x = X(a);
        svg.appendChild(sv('line', { x1: x, y1: Y0 - 7, x2: x, y2: Y0 + 7, stroke: '#10233F', 'stroke-width': 1.5 }));
        svg.appendChild(txt(x, Y0 - 12, n < 0 ? (-n) + ' TCN' : String(n), { 'font-size': hep ? 9.5 : 11.5, fill: '#4a5872' }));
      }
    } else {
      for (var a2 = -9; a2 <= 10; a2++) {
        var x2_ = X(a2);
        svg.appendChild(sv('line', { x1: x2_, y1: Y0 - 7, x2: x2_, y2: Y0 + 7, stroke: '#10233F', 'stroke-width': 1.5 }));
        var r = ra(a2); svg.appendChild(txt(x2_, Y0 - 12, String(r.so) + (r.tcn && !hep ? ' TCN' : ''), { 'font-size': hep ? 9 : 11, fill: r.tcn ? '#a2410b' : '#233a79', 'font-weight': 600 }));
      }
      svg.appendChild(txt(xB, Y0 + 72, 'Không có năm 0: ngay trước năm 1 là năm 1 TCN', { 'font-size': hep ? 10.5 : 12.5, 'font-weight': 700, fill: '#b8261e' }));
    }
    // ranh giới năm 1
    svg.appendChild(sv('line', { x1: xB, y1: Y0 - 34, x2: xB, y2: Y0 + 34, stroke: '#b8261e', 'stroke-width': 2.5 }));
    svg.appendChild(txt(xB, Y0 - 40, 'Năm 1: Công nguyên bắt đầu', { 'font-size': hep ? 10 : 12, 'font-weight': 700, fill: '#b8261e' }));
    // ngoặc khoảng cách
    var xa = X(st.a), xb = X(st.b), lo = Math.min(xa, xb), hi = Math.max(xa, xb), yN = Y0 + 92;
    if (st.view === 'hep') yN = Y0 + 96;
    var khac = (st.a <= 0) !== (st.b <= 0);
    if (khac) {
      var xt = st.a <= 0 ? xa : xb, xc = st.a <= 0 ? xb : xa;
      svg.appendChild(sv('path', { d: 'M' + xt + ' ' + (yN - 6) + 'V' + yN + 'H' + xB + 'V' + (yN - 6), fill: 'none', stroke: '#c9520f', 'stroke-width': 2 }));
      svg.appendChild(sv('path', { d: 'M' + xB + ' ' + (yN - 6) + 'V' + yN + 'H' + xc + 'V' + (yN - 6), fill: 'none', stroke: '#2e3e73', 'stroke-width': 2 }));
      var sTCN = ra(Math.min(st.a, st.b)).so, sCN = Math.max(st.a, st.b);
      svg.appendChild(txt((xt + xB) / 2, yN + 16, sTCN + ' năm', { 'font-size': 11.5, 'font-weight': 700, fill: '#c9520f' }));
      svg.appendChild(txt((xB + xc) / 2, yN + 16, sCN + ' năm', { 'font-size': 11.5, 'font-weight': 700, fill: '#2e3e73' }));
    } else svg.appendChild(sv('path', { d: 'M' + lo + ' ' + (yN - 6) + 'V' + yN + 'H' + hi + 'V' + (yN - 6), fill: 'none', stroke: '#2e3e73', 'stroke-width': 2 }));
    // hai chốt
    [['A', st.a, '#F26B1D', 30], ['B', st.b, '#2e3e73', 62]].forEach(function (c) {
      var x = X(c[1]), g = sv('g', { class: 'chot', 'data-chot': c[0], style: 'cursor:grab', tabindex: '0', role: 'slider', 'aria-label': 'Mốc ' + c[0], 'aria-valuetext': TEN(c[1]) });
      g.appendChild(sv('line', { x1: x, y1: c[3] + 10, x2: x, y2: Y0, stroke: c[2], 'stroke-width': 2.5 }));
      g.appendChild(sv('circle', { cx: x, cy: Y0, r: 8, fill: '#fff', stroke: c[2], 'stroke-width': 3 }));
      var lab = c[0] + ': ' + nhan(c[1]), wl = lab.length * 7.4 + 16, xl = Math.min(Math.max(x - wl / 2, 2), W - wl - 2);
      g.appendChild(sv('rect', { x: xl, y: c[3] - 12, width: wl, height: 24, rx: 12, fill: c[2] }));
      g.appendChild(txt(xl + wl / 2, c[3] + 4.5, lab, { fill: '#fff', 'font-weight': 700, 'font-size': 12.5 }));
      g.appendChild(sv('rect', { x: x - 16, y: c[3] - 14, width: 32, height: Y0 - c[3] + 26, fill: 'transparent' }));
      svg.appendChild(g);
    });
    capNhatChu();
  }
  function capNhatChu() {
    A.so.value = ra(st.a).so; A.ky.value = ra(st.a).tcn ? 'tcn' : 'cn'; B.so.value = ra(st.b).so; B.ky.value = ra(st.b).tcn ? 'tcn' : 'cn';
    var khac = (st.a <= 0) !== (st.b <= 0), d = Math.abs(st.a - st.b);
    kq.innerHTML = '';
    kq.appendChild(el('div', null, 'Từ ', el('b', null, ten(Math.min(st.a, st.b))), ' đến ', el('b', null, ten(Math.max(st.a, st.b))), ':'));
    kq.appendChild(el('div', { class: 'lon' }, d === 0 ? 'Hai mốc trùng nhau' : MP.so(d) + ' năm'));
    if (khac) {
      var t = ra(Math.min(st.a, st.b)).so, c = Math.max(st.a, st.b);
      kq.appendChild(el('p', { style: { margin: '6px 0 0' } }, 'Một mốc trước Công nguyên, một mốc Công nguyên → cộng hai số năm: ', el('b', null, t + ' + ' + c + ' = ' + MP.so(t + c)), ' (khoảng ' + MP.so(t + c) + ' năm).'));
      kq.appendChild(el('p', { style: { margin: '4px 0 0' } }, 'Tính thật chính xác thì trừ 1 vì không có năm 0: ', el('b', null, MP.so(t + c) + ' − 1 = ' + MP.so(t + c - 1) + ' năm'), '.'));
    } else if (d) kq.appendChild(el('p', { style: { margin: '6px 0 0' } }, 'Hai mốc cùng ở ' + (st.a <= 0 ? 'trước Công nguyên' : 'Công nguyên') + ' → lấy số lớn trừ số nhỏ: ', el('b', null, Math.max(ra(st.a).so, ra(st.b).so) + ' − ' + Math.min(ra(st.a).so, ra(st.b).so) + ' = ' + MP.so(d) + ' năm'), '.'));
    // đơn vị của mốc B
    var r = ra(st.b), dv = DV[st.dv][1], so = Math.ceil(r.so / dv), dau = (so - 1) * dv + 1, cuoi = so * dv;
    var tenDv = st.dv === 'thap_ki' ? 'thập kỉ từ ' : st.dv === 'the_ki' ? 'thế kỉ ' + MP.laMa(so) + (r.tcn ? ' TCN' : '') + ', từ ' : 'thiên niên kỉ ' + MP.laMa(so) + (r.tcn ? ' TCN' : '') + ', từ ';
    dvKq.innerHTML = '';
    dvKq.appendChild(el('p', { style: { margin: 0 } }, TEN(st.b) + ' thuộc ', el('b', null, tenDv + 'năm ' + (r.tcn ? cuoi : dau) + (r.tcn ? ' TCN' : '') + ' đến năm ' + (r.tcn ? dau : cuoi) + (r.tcn ? ' TCN' : '')), '.'));
    dvKq.appendChild(el('p', { style: { margin: '6px 0 0', fontSize: '.86rem', color: 'var(--chu-phu)' } }, 'Mỗi khoảng được tính từ năm đầu tiên của nó. Ví dụ, thế kỉ XXI bắt đầu từ năm 2001 và kết thúc năm 2100. (' + MP.trang([15]) + ')'));
  }

  // ---- kéo chốt
  var keo = null, namCu = null;
  function diemSvg(e) { var r = svg.getBoundingClientRect(); return (e.clientX - r.left) / r.width * W; }
  svg.addEventListener('pointerdown', function (e) {
    var g = e.target.closest && e.target.closest('.chot'), x = diemSvg(e);
    var id = g ? g.getAttribute('data-chot') : (Math.abs(X(st.a) - x) < Math.abs(X(st.b) - x) ? 'A' : 'B');
    keo = id; namCu = null; svg.setPointerCapture(e.pointerId); MP.am('click'); diChuyen(e); e.preventDefault();
  });
  function diChuyen(e) {
    if (!keo) return;
    var p = pham(), a = MP.clamp(nguoc(diemSvg(e)), p[0], p[1]);
    if (st.view === 'rong') a = Math.round(a / 1) * 1;
    if (keo === 'A') st.a = a; else st.b = a;
    if (a !== namCu) { namCu = a; MP.am('tick', { f: a <= 0 ? 1500 : 1900, cach: 70 }); }
    ve();
  }
  svg.addEventListener('pointermove', diChuyen);
  svg.addEventListener('pointerup', function () { if (keo) MP.am('xac_nhan'); keo = null; });
  svg.addEventListener('pointercancel', function () { keo = null; });
  svg.addEventListener('keydown', function (e) {
    var g = e.target.closest && e.target.closest('.chot'); if (!g) return;
    var k = g.getAttribute('data-chot'), d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0; if (!d) return;
    e.preventDefault(); var step = e.shiftKey ? 100 : 1; if (k === 'A') st.a += d * step; else st.b += d * step; MP.am('tick'); ve(); svg.querySelector('[data-chot="' + k + '"]').focus();
  });
  function tuO(o, key) {
    function doc() { var n = MP.clamp(Math.round(+o.so.value || 1), 1, 5000); st[key] = vao(n, o.ky.value === 'tcn'); if (st[key] < pham()[0] || st[key] > pham()[1]) datView('rong'); ve(); }
    o.so.addEventListener('change', function () { doc(); MP.am('tick'); }); o.ky.addEventListener('change', function () { doc(); MP.am('click'); });
    o.tru.addEventListener('click', function () { st[key] -= 1; if (st[key] < pham()[0]) datView('rong'); MP.am('tick'); ve(); });
    o.cong.addEventListener('click', function () { st[key] += 1; if (st[key] > pham()[1]) datView('rong'); MP.am('tick'); ve(); });
  }
  tuO(A, 'a'); tuO(B, 'b');
  if ('ResizeObserver' in window) new ResizeObserver(function () { ve(); }).observe(hop); else window.addEventListener('resize', ve);
  MP.fontReady.then(ve); ve();
});
