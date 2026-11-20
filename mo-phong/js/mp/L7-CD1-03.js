/* L7-CD1-03 · Chuyến đi vòng quanh thế giới của Ph. Ma-gien-lăng (1519 – 1522) – quả địa cầu 3D.
   Đường đi, điểm dừng, các chặng lấy từ pipeline/maps/specs/ma-gien-lang.json (sơ đồ minh hoạ theo SGK LSĐL 7 tr. 166–169);
   nền đất liền Natural Earth 1:110m (phạm vi công cộng), không vẽ biên giới quốc gia; có quần đảo Hoàng Sa, Trường Sa của Việt Nam. */
MP.onReady(function () {
  var root = MP.khung(), el = MP.el, BC = window.BaChieu;
  var S = window.MP_BANDO['ma-gien-lang'];
  var NHAN_PHA = { ra_khoi: ['Ra khơi', [4, 5]], eo_bien: ['Eo biển Ma-gien-lăng', [6, 7]], thai_binh_duong: ['Thái Bình Dương', [9, 10]], tro_ve: ['Trở về Tây Ban Nha', [11, 12]], toan_canh: ['Toàn cảnh', [13]] };
  var SP = {
    ten: S.ten, phu_de: S.phu_de, duong: S.duong,
    moc: S.moc.map(function (m) { return { i: m.chi_so, chu: m.chu }; }),
    nhan: S.nhan.map(function (n) { return [n[0], n[1], n[2], n[3] === 'bien' ? 1 : 0]; }),
    pha: Object.keys(NHAN_PHA).map(function (k) { var p = S.pha[k]; return { key: k, nhan: NHAN_PHA[k][0], tu: p.tu_moc, den: p.den_moc, moc: p.moc_chu, canh: NHAN_PHA[k][1] }; })
  };
  var DAO_VN = [['QĐ. Hoàng Sa', 112.0, 16.5], ['QĐ. Trường Sa', 114.0, 9.5]];

  var tabs = el('div', { class: 'sb-pha', role: 'tablist', 'aria-label': 'Các chặng' });
  root.appendChild(el('div', { class: 'sb-tieu-de' }, el('b', null, SP.ten), el('span', null, SP.phu_de)));
  root.appendChild(tabs);
  var vung = el('div', { style: { marginTop: '8px' } }); root.appendChild(vung);
  MP.nen(['song_bien', 'gio']);
  var V = BC.tao(vung, { nen: 0x0f1d33, camPos: [0, 4, 15], target: [0, 0, 0], minDist: 7.5, maxDist: 30, maxPolar: Math.PI, nangPos: [10, 8, 14], nangManh: 2.4, hemi: 1.6, troi: 0xffffff, dat: 0x445566, tiLe: 16 / 10, tiLeNho: 0.95, goiY: 'Kéo để xoay quả địa cầu · Cuộn/chụm để phóng to', moTa: 'Quả địa cầu 3D với hành trình của Ma-gien-lăng.' });
  if (!V) return;
  var T = V.T, R = 5;
  var mocEl = el('div', { class: 'sb-moc', style: { opacity: 0 } }); V.el.appendChild(mocEl);

  // ---- kết cấu bề mặt (phép chiếu trụ đều) vẽ từ dữ liệu Natural Earth
  var W = 2048, H = 1024, cv = document.createElement('canvas'); cv.width = W; cv.height = H;
  var cx = cv.getContext('2d');
  function X(lon) { return (lon + 180) / 360 * W; } function Y(lat) { return (90 - lat) / 180 * H; }
  cx.fillStyle = '#bcd6e3'; cx.fillRect(0, 0, W, H);
  cx.strokeStyle = 'rgba(255,255,255,.55)'; cx.lineWidth = 1.2;
  for (var lo = -180; lo <= 180; lo += 30) { cx.beginPath(); cx.moveTo(X(lo), 0); cx.lineTo(X(lo), H); cx.stroke(); }
  for (var la = -60; la <= 60; la += 30) { cx.beginPath(); cx.moveTo(0, Y(la)); cx.lineTo(W, Y(la)); cx.stroke(); }
  cx.setLineDash([10, 8]); cx.strokeStyle = 'rgba(217,115,77,.6)'; cx.beginPath(); cx.moveTo(0, Y(0)); cx.lineTo(W, Y(0)); cx.stroke(); cx.setLineDash([]);
  (window.MP_GEO ? MP_GEO.vong : []).forEach(function (v) {
    cx.beginPath(); v.d.forEach(function (p, i) { if (i) cx.lineTo(X(p[0]), Y(p[1])); else cx.moveTo(X(p[0]), Y(p[1])); }); cx.closePath();
    cx.fillStyle = v.lo ? '#bcd6e3' : '#ece0c2'; cx.fill(); cx.strokeStyle = 'rgba(140,128,104,.9)'; cx.lineWidth = 1.1; cx.stroke();
  });
  DAO_VN.forEach(function (d) { for (var j = 0; j < 5; j++) { cx.fillStyle = '#6d6250'; cx.beginPath(); cx.arc(X(d[1]) + (j - 2) * 2.2, Y(d[2]) + ((j % 2) - 0.5) * 2.2, 1.3, 0, 7); cx.fill(); } });
  var tex = new T.CanvasTexture(cv); tex.colorSpace = T.SRGBColorSpace; tex.anisotropy = 4;
  var dia = new T.Mesh(new T.SphereGeometry(R, 96, 64), new T.MeshStandardMaterial({ map: tex, roughness: 0.85, metalness: 0 }));
  V.scene.add(dia);
  var khi = new T.Mesh(new T.SphereGeometry(R * 1.04, 64, 32), new T.MeshBasicMaterial({ color: 0x9fd0ff, transparent: true, opacity: 0.12, side: T.BackSide })); V.scene.add(khi);
  // sao nền
  var sao = new T.BufferGeometry(), sp = [], rnd = BC.rngSo(3);
  for (var s = 0; s < 500; s++) { var u = rnd() * 2 - 1, a = rnd() * Math.PI * 2, rr = 80 + rnd() * 40, q = Math.sqrt(1 - u * u); sp.push(rr * q * Math.cos(a), rr * u, rr * q * Math.sin(a)); }
  sao.setAttribute('position', new T.Float32BufferAttribute(sp, 3)); V.scene.add(new T.Points(sao, new T.PointsMaterial({ color: 0xffffff, size: 0.35, sizeAttenuation: true })));

  function P3(lon, lat, r) { var ph = (lon + 180) * Math.PI / 180, th = lat * Math.PI / 180, rr = r || R; return new T.Vector3(-rr * Math.cos(ph) * Math.cos(th), rr * Math.sin(th), rr * Math.sin(ph) * Math.cos(th)); }
  function che(v, cam) { var n = v.clone().normalize(), to = cam.position.clone().sub(v).normalize(); return n.dot(to) < 0.12; }

  // ---- đường đi (làm dày điểm), quãng đường tích luỹ như bản đồ trong video
  var D = SP.duong, dCum = [0];
  for (var i = 1; i < D.length; i++) dCum.push(dCum[i - 1] + Math.hypot((D[i][0] - D[i - 1][0]) * Math.cos(D[i - 1][1] * Math.PI / 180), D[i][1] - D[i - 1][1]));
  var TONG = dCum[dCum.length - 1];
  function viTri(L) {   // [lon, lat] tại quãng đường L
    L = MP.clamp(L, 0, TONG); var k = 1; while (k < dCum.length - 1 && dCum[k] < L) k++;
    var a = (L - dCum[k - 1]) / Math.max(1e-9, dCum[k] - dCum[k - 1]);
    return [D[k - 1][0] + (D[k][0] - D[k - 1][0]) * a, D[k - 1][1] + (D[k][1] - D[k - 1][1]) * a];
  }
  var NSEG = 900, pts = [];
  for (i = 0; i <= NSEG; i++) { var ll = viTri(TONG * i / NSEG); pts.push(P3(ll[0], ll[1], R * 1.006)); }
  var gTube = new T.TubeGeometry(new T.CatmullRomCurve3(pts), NSEG, 0.028, 6, false);
  var duong = new T.Mesh(gTube, new T.MeshBasicMaterial({ color: 0xc0281e })); V.scene.add(duong);
  var vetMo = new T.Mesh(new T.TubeGeometry(new T.CatmullRomCurve3(pts), NSEG, 0.012, 4, false), new T.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.35 })); V.scene.add(vetMo);
  function veDen(p) { gTube.setDrawRange(0, Math.floor(MP.clamp(p, 0, 1) * NSEG) * 6 * 6); }

  // ---- con tàu buồm giản lược
  var tau = new T.Group(), than = new T.Mesh(new T.BoxGeometry(0.1, 0.07, 0.26), new T.MeshStandardMaterial({ color: 0x6b4426 }));
  than.position.y = 0.035; tau.add(than);
  var cot = new T.Mesh(new T.CylinderGeometry(0.006, 0.006, 0.26, 4), new T.MeshStandardMaterial({ color: 0x3a2a1c })); cot.position.y = 0.17; tau.add(cot);
  var buom = new T.Mesh(new T.PlaneGeometry(0.15, 0.17), new T.MeshStandardMaterial({ color: 0xfaf6ea, side: T.DoubleSide })); buom.position.set(0, 0.19, 0.01); buom.rotation.y = Math.PI / 2; tau.add(buom);
  var co = new T.Mesh(new T.PlaneGeometry(0.05, 0.03), new T.MeshBasicMaterial({ color: 0xc0281e, side: T.DoubleSide })); co.position.set(0, 0.3, 0.02); co.rotation.y = Math.PI / 2; tau.add(co);
  tau.scale.setScalar(1.7); V.scene.add(tau);
  function datTau(L) {
    var a = viTri(L), b = viTri(Math.min(TONG, L + 0.6)), p = P3(a[0], a[1], R * 1.004), p2 = P3(b[0], b[1], R * 1.004);
    if (L >= TONG - 0.6) { var c = viTri(L - 0.6); p2 = p.clone().multiplyScalar(2).sub(P3(c[0], c[1], R * 1.004)); }
    tau.position.copy(p); tau.up.copy(p).normalize(); tau.lookAt(p2); return p;
  }

  // ---- điểm dừng, nhãn châu lục, đại dương, quần đảo
  var diem = SP.moc.map(function (m) {
    var p = P3(D[m.i][0], D[m.i][1], R * 1.01), cham = new T.Mesh(new T.SphereGeometry(0.075, 14, 10), new T.MeshBasicMaterial({ color: 0xc0281e }));
    cham.position.copy(p); V.scene.add(cham);
    var L = V.nhan(m.chu, P3(D[m.i][0], D[m.i][1], R * 1.03), 'do', { che: che });
    return { m: m, cham: cham, nhan: L, L: dCum[m.i] };
  });
  SP.nhan.forEach(function (n) { V.nhan(n[0], P3(n[1], n[2], R * 1.01), n[3] ? 'phang nuoc' : 'phang', { che: che }); });
  DAO_VN.forEach(function (d) { V.nhan(d[0], P3(d[1], d[2], R * 1.01), 'nho', { che: che }); });

  // ---- trình phát theo chặng
  var btnPrev = MP.nutIcon('prev', 'Chặng trước'), btnPlay = MP.nutIcon('play', 'Phát', 'chinh'), btnNext = MP.nutIcon('next', 'Chặng sau');
  var range = el('input', { type: 'range', min: '0', max: '1000', value: '0', 'aria-label': 'Tiến trình trong chặng' });
  var buocEl = el('span', { class: 'buoc' }), nutTheo = el('button', { type: 'button', class: 'nut', 'aria-pressed': 'true' }, 'Theo tàu');
  var loiEl = el('div', { class: 'sb-loi', 'aria-live': 'polite' });
  root.appendChild(el('div', { class: 'sb-dieu-khien', style: { marginTop: '10px' } }, btnPrev, btnPlay, btnNext, range, buocEl));
  root.appendChild(el('div', { class: 'hang-nut', style: { margin: '8px 0' } }, nutTheo));
  root.appendChild(loiEl);
  var tt = MP.canh(14);
  if (tt && tt.moc) {
    var ol = el('ol', { class: 'dong-moc' }); tt.moc.forEach(function (m) { ol.appendChild(el('li', null, el('b', null, m[0]), el('span', null, m[1]))); });
    root.appendChild(el('div', { class: 'tom-tat', style: { marginTop: '12px' } }, el('h3', null, 'Tóm tắt hành trình'), ol, el('p', { style: { fontSize: '.8rem', color: 'var(--chu-phu)', margin: '6px 0 0' } }, MP.trang(tt.tr))));
  }
  var st = { pi: 0, u: 0, chay: false, theo: true, giu: 0, daQua: {} };
  var tabBtns = SP.pha.map(function (p, i) {
    var b = el('button', { type: 'button', role: 'tab', 'aria-selected': 'false' }, el('span', { class: 'so' }, String(i + 1)), p.nhan);
    b.addEventListener('click', function () { dung(); chonPha(i, 0, true); }); tabs.appendChild(b); return b;
  });
  function Lhien() { var p = SP.pha[st.pi]; return dCum[p.tu] + (dCum[p.den] - dCum[p.tu]) * st.u; }
  function chonPha(i, u, am) {
    st.pi = i; st.u = u || 0; st.daQua = {};
    var p = SP.pha[i];
    tabBtns.forEach(function (b, j) { b.setAttribute('aria-selected', j === i ? 'true' : 'false'); });
    MP.hopLoi(loiEl, MP.loi(p.canh), MP.trangCanh(p.canh));
    mocEl.textContent = p.moc || ''; mocEl.style.opacity = p.moc ? 1 : 0;
    V.controls.autoRotate = p.key === 'toan_canh'; V.controls.autoRotateSpeed = 0.6;
    if (p.key === 'toan_canh') { st.theo = false; nutTheo.setAttribute('aria-pressed', 'false'); var c = P3(-185, 0, 17); V.bay([c.x, c.y + 3, c.z], [0, 0, 0], 1400); }
    diem.forEach(function (d) { d.daQua = Lhien() >= d.L - 1e-6; });
    if (am) MP.am('chuong_tau');
    capNhat();
  }
  function capNhat() {
    range.value = Math.round(st.u * 1000); MP.toThanh(range);
    var L = Lhien(), p = SP.pha[st.pi];
    veDen(L / TONG); var vt = datTau(L);
    diem.forEach(function (d) {
      var hien = L >= d.L - 1e-6 && !(p.key === 'toan_canh' && d.m.i === 0);
      d.cham.visible = L >= d.L - 1e-6; d.nhan.hien = hien;
      if (hien && !d.daQua && st.chay) MP.am(d.m.i === 15 ? 'mo_pha' : 'chuong_tau');
      d.daQua = L >= d.L - 1e-6;
    });
    buocEl.textContent = 'Chặng ' + (st.pi + 1) + '/' + SP.pha.length;
    return vt;
  }
  function choi() { if (st.u >= 0.999) { if (st.pi < SP.pha.length - 1) chonPha(st.pi + 1, 0, true); else chonPha(0, 0, true); } st.chay = true; MP.setIcon(btnPlay, 'pause', 'Tạm dừng'); MP.am('click'); }
  function dung() { st.chay = false; MP.setIcon(btnPlay, 'play', 'Phát'); }
  btnPlay.addEventListener('click', function () { st.chay ? dung() : choi(); });
  btnPrev.addEventListener('click', function () { dung(); chonPha(Math.max(0, st.pi - 1), 0, true); });
  btnNext.addEventListener('click', function () { dung(); chonPha(Math.min(SP.pha.length - 1, st.pi + 1), 0, true); });
  range.addEventListener('input', function () { dung(); st.u = range.value / 1000; capNhat(); MP.am('tick', { f: 1500 }); });
  nutTheo.addEventListener('click', function () { st.theo = !st.theo; nutTheo.setAttribute('aria-pressed', st.theo ? 'true' : 'false'); V.controls.autoRotate = false; MP.am('click'); });
  V.controls.addEventListener('start', function () { if (st.theo) { st.theo = false; nutTheo.setAttribute('aria-pressed', 'false'); } V.controls.autoRotate = false; });

  var camMuon = new T.Vector3(), kenTai = 0;
  V.moi(function (dt, t) {
    if (st.chay) {
      var p = SP.pha[st.pi], dai = (dCum[p.den] - dCum[p.tu]) / TONG, dur = p.key === 'toan_canh' ? 14 : 5 + 22 * dai;
      if (st.u < 1) { st.u = Math.min(1, st.u + dt / dur); capNhat(); kenTai += dt; if (kenTai > 2.6) { kenTai = 0; MP.am('keo_ket'); } }
      else { st.giu += dt; if (st.giu > 1.5) { st.giu = 0; if (st.pi < SP.pha.length - 2) chonPha(st.pi + 1, 0, true); else { dung(); MP.am('chuong'); if (SP.pha[st.pi].key === 'tro_ve') { V.bang('Chuyến đi chứng minh Trái Đất có dạng hình cầu', true); setTimeout(function () { V.bang('', false); }, 4000); } } } }
    }
    buom.scale.x = 1 + 0.06 * Math.sin(t * 3); co.rotation.z = Math.sin(t * 6) * 0.2;
    if (st.theo) {   // quay quả địa cầu theo tàu: nội suy hướng nhìn, giữ nguyên khoảng cách
      var kc = Math.max(11, Math.min(18, V.camera.position.length() < 10.5 ? 14 : V.camera.position.length()));
      camMuon.copy(tau.position).normalize(); camMuon.y += 0.22; camMuon.normalize();
      var huong = V.camera.position.clone().normalize();
      huong.lerp(camMuon, Math.min(1, dt * 2.2));
      if (huong.lengthSq() < 1e-6) huong.copy(camMuon);
      V.camera.position.copy(huong.normalize().multiplyScalar(kc)); V.controls.target.lerp(new T.Vector3(0, 0, 0), Math.min(1, dt * 2));
    }
  });
  chonPha(0, 0, false);
  datTau(0); (function () { var n = tau.position.clone().normalize().multiplyScalar(14); n.y += 3; V.camera.position.copy(n); })();
});
