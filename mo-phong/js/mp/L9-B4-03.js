/* L9-B4-03 · Bước ngoặt Xta-lin-grát và ngày tàn của phát xít – kéo thả các sự kiện 1942 – 1945 vào đúng thứ tự.
   Sự kiện, mốc lấy từ cảnh "trục thời gian" (cảnh 11) của kịch bản; lược đồ minh hoạ: specs/ctgt2-chau-au.json, ctgt2-chau-a.json. */
MP.onReady(function () {
  var root = MP.khung(), el = MP.el;
  var C = MP.canh(11), MOC = C.moc.map(function (m, i) { return { id: i, ngay: m[0], su: m[1] }; });
  MP.nen(['gio', 'nen_em']);
  root.appendChild(el('h2', { style: { fontSize: '1.15rem' } }, 'Sắp xếp các sự kiện theo thứ tự thời gian (1942 – 1945)'));
  var khay = el('div', { class: 'ktt-khay', 'aria-label': 'Các thẻ sự kiện chưa xếp' });
  var truc = el('ol', { class: 'ktt-truc', 'aria-label': 'Trục thời gian: ô 1 sớm nhất' });
  var tb = el('p', { class: 'thong-bao', 'aria-live': 'polite' });
  var nutKT = el('button', { type: 'button', class: 'nut chinh' }, 'Kiểm tra');
  var nutLai = el('button', { type: 'button', class: 'nut' }, 'Xáo lại');
  var nutDA = el('button', { type: 'button', class: 'nut' }, 'Xem đáp án');
  root.appendChild(el('p', { style: { margin: '0 0 6px', fontSize: '.9rem', color: 'var(--chu-phu)' } }, 'Kéo từng thẻ vào ô trên trục (trên điện thoại: chạm thẻ, rồi chạm ô).'));
  root.appendChild(khay);
  root.appendChild(el('div', { style: { height: '12px' } }));
  var dauTruc = el('div', { style: { display: 'flex', justifyContent: 'space-between', fontWeight: 700, color: 'var(--do)', fontSize: '.9rem', margin: '0 0 6px' } }, el('span', null, '11 – 1942'), el('span', null, '8 – 1945'));
  root.appendChild(dauTruc); root.appendChild(truc);
  root.appendChild(el('div', { class: 'hang-nut', style: { marginTop: '12px' } }, nutKT, nutLai, nutDA));
  root.appendChild(tb);

  var o = MOC.map(function (m, i) {
    var cho = el('div', { class: 'cho', 'data-o': i, 'aria-label': 'Ô ' + (i + 1) });
    var li = el('li', { class: 'ktt-o' }, el('span', { class: 'so' }, String(i + 1)), cho);
    truc.appendChild(li); return cho;
  });
  var the = MOC.map(function (m) {
    var t = el('div', { class: 'ktt-the', tabindex: '0', role: 'button', 'data-id': m.id, 'aria-label': m.su }, el('span', { class: 'chu' }, m.su));
    return t;
  });
  var chon = null;
  function xao() {
    var ds = the.slice(); for (var i = ds.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var x = ds[i]; ds[i] = ds[j]; ds[j] = x; }
    if (ds.every(function (t, i) { return +t.dataset.id === i; })) ds.reverse();
    ds.forEach(function (t) { t.classList.remove('dung', 'sai', 'chon'); var n = t.querySelector('.ngay'); if (n) n.remove(); khay.appendChild(t); });
    tb.textContent = ''; tb.className = 'thong-bao'; chon = null;
  }
  function datVao(t, cho) {
    var cu = cho.querySelector('.ktt-the'), tu = t.parentNode;
    if (cu && cu !== t) { if (tu && tu.classList && tu.classList.contains('cho')) tu.appendChild(cu); else khay.appendChild(cu); }
    cho.appendChild(t); t.classList.remove('dung', 'sai', 'chon'); var n = t.querySelector('.ngay'); if (n) n.remove();
    MP.am('tick', { f: 1400 }); tb.textContent = '';
  }
  // kéo bằng con trỏ (chuột, bút, ngón tay)
  var keo = null;
  the.forEach(function (t) {
    t.addEventListener('pointerdown', function (e) {
      if (e.button) return;
      keo = { t: t, x0: e.clientX, y0: e.clientY, dang: false, id: e.pointerId };
      t.setPointerCapture(e.pointerId);
    });
    t.addEventListener('pointermove', function (e) {
      if (!keo || keo.t !== t) return;
      if (!keo.dang && Math.hypot(e.clientX - keo.x0, e.clientY - keo.y0) > 6) {
        keo.dang = true; var r = t.getBoundingClientRect(); keo.dx = e.clientX - r.left; keo.dy = e.clientY - r.top;
        keo.bong = t.cloneNode(true); keo.bong.classList.add('dang-keo'); keo.bong.style.width = r.width + 'px'; document.body.appendChild(keo.bong);
        t.style.opacity = 0.35; MP.am('click');
      }
      if (keo.dang) {
        keo.bong.style.left = (e.clientX - keo.dx) + 'px'; keo.bong.style.top = (e.clientY - keo.dy) + 'px';
        o.forEach(function (c) { c.classList.remove('tro'); });
        var duoi = document.elementFromPoint(e.clientX, e.clientY), c2 = duoi && duoi.closest('.cho'); if (c2) c2.classList.add('tro');
      }
    });
    function ket(e) {
      if (!keo || keo.t !== t) return;
      if (keo.dang) {
        keo.bong.remove(); t.style.opacity = '';
        o.forEach(function (c) { c.classList.remove('tro'); });
        var duoi = document.elementFromPoint(e.clientX, e.clientY), c2 = duoi && duoi.closest('.cho'), k2 = duoi && duoi.closest('.ktt-khay');
        if (c2) datVao(t, c2); else if (k2) { khay.appendChild(t); MP.am('tick', { f: 1100 }); }
      } else { // chạm: chọn thẻ
        if (chon === t) { t.classList.remove('chon'); chon = null; } else { if (chon) chon.classList.remove('chon'); chon = t; t.classList.add('chon'); MP.am('click'); }
      }
      keo = null;
    }
    t.addEventListener('pointerup', ket); t.addEventListener('pointercancel', function () { if (keo && keo.bong) keo.bong.remove(); t.style.opacity = ''; keo = null; });
    t.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); if (chon) chon.classList.remove('chon'); chon = t; t.classList.add('chon'); MP.am('click'); } });
  });
  o.forEach(function (c) {
    c.setAttribute('tabindex', '0'); c.setAttribute('role', 'button');
    function dat() { if (chon) { datVao(chon, c); chon.classList.remove('chon'); chon = null; } }
    c.addEventListener('click', function (e) { if (e.target === c) dat(); });
    c.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); dat(); } });
  });
  khay.addEventListener('click', function (e) { if (e.target === khay && chon) { khay.appendChild(chon); chon.classList.remove('chon'); chon = null; MP.am('tick', { f: 1100 }); } });

  function hienNgay(t, i) { if (!t.querySelector('.ngay')) t.insertBefore(el('span', { class: 'ngay' }, MOC[i].ngay), t.firstChild); }
  nutKT.addEventListener('click', function () {
    var dung = 0, trong = 0;
    o.forEach(function (c, i) {
      var t = c.querySelector('.ktt-the'); if (!t) { trong++; return; }
      var ok = +t.dataset.id === i; t.classList.toggle('dung', ok); t.classList.toggle('sai', !ok);
      if (ok) { dung++; hienNgay(t, i); } else { var n = t.querySelector('.ngay'); if (n) n.remove(); }
    });
    if (dung === MOC.length) { tb.className = 'thong-bao dung'; tb.textContent = 'Chính xác! Em đã sắp đúng cả ' + MOC.length + ' sự kiện. (' + MP.trang(C.tr) + ')'; MP.am('chuong'); MP.am('reo', { lv: 0.6, tre: 0.6 }); }
    else { tb.className = 'thong-bao sai'; tb.textContent = 'Đúng ' + dung + '/' + MOC.length + (trong ? ', còn ' + trong + ' ô trống' : '') + '. Các thẻ đỏ chưa đúng vị trí – kéo lại nhé!'; MP.am(dung ? 'xac_nhan' : 'sai'); if (dung) MP.am('sai', { tre: 0.25 }); }
  });
  nutLai.addEventListener('click', function () { xao(); MP.am('soat'); });
  nutDA.addEventListener('click', function () { o.forEach(function (c, i) { c.appendChild(the[i]); the[i].classList.remove('sai', 'chon'); the[i].classList.add('dung'); hienNgay(the[i], i); }); tb.className = 'thong-bao'; tb.textContent = 'Đây là thứ tự đúng. Bấm “Xáo lại” để tự làm nhé!'; MP.am('lat_trang'); });
  xao();

  // ---- lược đồ minh hoạ
  var W = window.SaBanWeb;
  root.appendChild(el('h2', { style: { fontSize: '1.15rem', marginTop: '22px' } }, 'Lược đồ minh hoạ'));
  var h1 = el('div'), h2 = el('div', { style: { marginTop: '18px' } }); root.appendChild(h1); root.appendChild(h2);
  new W.MapPlayer(h1, {
    id: 'eu', spec: window.MP_BANDO['ctgt2-chau-au'],
    phases: [
      { key: 'xtalingrat', nhan: 'Xta-lin-grát', canh: [3] },
      { key: 'noocmangdi', nhan: 'Noóc-măng-đi', canh: [6] },
      { key: 'beclin', nhan: 'Béc-lin', canh: [8] }
    ],
    am: { nen: ['gio', 'phao_xa'], batDau: 'mo_pha', doiTuong: function (id, o2) { if (o2.loai === 'mui_ten_ta') return ['vut', 'buoc_quan']; if (o2.loai === 'nhan') return 'lat_trang'; } }
  });
  new W.MapPlayer(h2, {
    id: 'as', spec: window.MP_BANDO['ctgt2-chau-a'],
    phases: [{ key: 'thang8', nhan: 'Tháng 8 – 1945', canh: [10] }],
    // không dùng âm thanh nổ cho sự kiện bom nguyên tử: chỉ chuyển trang nhẹ, giữ không khí trang nghiêm
    am: { nen: ['gio'], batDau: 'mo_pha', bang: 'mo_pha', trongBang: false, doiTuong: function (id, o2) { if (o2.loai === 'nhan') return 'lat_trang'; if (o2.loai === 'mui_ten_ta') return 'vut'; } }
  });
});
