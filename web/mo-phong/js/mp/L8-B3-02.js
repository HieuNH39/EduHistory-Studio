/* L8-B3-02 · Giêm Oát và máy hơi nước – mô phỏng 3D.
   Thẻ 1: nguyên lí theo kịch bản (SGK LSĐL 8 tr. 16): lửa đun nóng nồi hơi → hơi nước đẩy pít-tông chuyển động qua lại →
   pít-tông làm quay bánh đà → bánh đà kéo máy móc chạy theo. Mô hình minh hoạ nguyên lí, không phải bản vẽ cỗ máy của Giêm Oát.
   Thẻ 2: nhà máy từ ven sông chảy xiết (xưởng dệt 1771, máy chạy bằng sức nước) “dời” vào trung tâm thành phố sau khi có máy hơi nước (1784). */
MP.onReady(function () {
  var root = MP.khung(), el = MP.el, BC = window.BaChieu;
  var tabA = el('button', { type: 'button', class: 'nut', role: 'tab', 'aria-selected': 'true' }, 'Máy hơi nước');
  var tabB = el('button', { type: 'button', class: 'nut', role: 'tab', 'aria-selected': 'false' }, 'Vị trí nhà máy');
  var pA = el('div', { role: 'tabpanel' }), pB = el('div', { role: 'tabpanel', hidden: true });
  root.appendChild(el('div', { class: 'tab-3d', role: 'tablist', 'aria-label': 'Chọn mô phỏng' }, tabA, tabB)); root.appendChild(pA); root.appendChild(pB);
  var mayChay = true, nhaMay = null;
  function chon(i) {
    tabA.setAttribute('aria-selected', i === 0 ? 'true' : 'false'); tabB.setAttribute('aria-selected', i === 1 ? 'true' : 'false');
    pA.hidden = i !== 0; pB.hidden = i !== 1; MP.am('click');
    if (i === 1) { if (!nhaMay) nhaMay = taoNhaMay(); else nhaMay.nen(); } else MP.nen(mayChay ? ['lua', 'may_hoi'] : ['lua']);
  }
  tabA.addEventListener('click', function () { chon(0); }); tabB.addEventListener('click', function () { chon(1); });

  function vatLieu(c, o) { return new (window.THREE.MeshStandardMaterial)(Object.assign({ color: c, roughness: 0.6, metalness: 0.2 }, o || {})); }
  function khoi(T, w, h, d, m, x, y, z) { var b = new T.Mesh(new T.BoxGeometry(w, h, d), m); b.position.set(x, y, z); return b; }
  function truX(T, r, len, m, seg) { var g = new T.CylinderGeometry(r, r, len, seg || 24); g.rotateZ(Math.PI / 2); return new T.Mesh(g, m); }
  function truZ(T, r, len, m, seg) { var g = new T.CylinderGeometry(r, r, len, seg || 24); g.rotateX(Math.PI / 2); return new T.Mesh(g, m); }
  function vetKhoi(T) {
    var c = document.createElement('canvas'); c.width = c.height = 64; var x = c.getContext('2d'), g = x.createRadialGradient(32, 32, 2, 32, 32, 30);
    g.addColorStop(0, 'rgba(255,255,255,0.95)'); g.addColorStop(1, 'rgba(255,255,255,0)'); x.fillStyle = g; x.fillRect(0, 0, 64, 64);
    var t = new T.CanvasTexture(c); t.colorSpace = T.SRGBColorSpace; return t;
  }

  // =============================== THẺ 1: MÁY HƠI NƯỚC
  MP.nen(['lua', 'may_hoi']);
  var V = BC.tao(pA, { nen: 0xe8e1d3, camPos: [4, 7.5, 17], target: [4, 2.4, 0], minDist: 5, maxDist: 45, nangPos: [8, 16, 12], moTa: 'Mô hình 3D máy hơi nước: lửa, nồi hơi, pít-tông, bánh đà, máy móc. Kéo để xoay.' });
  var phaiA = el('div', { class: 'bang-dk' }); pA.appendChild(phaiA);
  if (!V) return;
  var T = V.T;
  var san = new T.Mesh(new T.PlaneGeometry(80, 60), new T.MeshStandardMaterial({ color: 0xcfc2a6, roughness: 1 })); san.rotation.x = -Math.PI / 2; V.scene.add(san);
  var mDa = vatLieu(0x8c8579, { roughness: 0.9, metalness: 0 }), mGach = vatLieu(0x9b4a35, { roughness: 0.95, metalness: 0 }), mSat = vatLieu(0x3f4a47, { metalness: 0.6, roughness: 0.45 });
  var mDong = vatLieu(0xb08d57, { metalness: 0.7, roughness: 0.35 }), mGo = vatLieu(0x7a5534, { roughness: 0.8, metalness: 0 });
  V.scene.add(khoi(T, 20.5, 0.4, 5.4, mDa, 4, 0.2, 0));
  // lò lửa + ống khói
  var mLo = vatLieu(0x9b4a35, { roughness: 0.95, metalness: 0 });
  V.scene.add(khoi(T, 3.2, 1.8, 2.6, mLo, -3.5, 1.3, 0));
  var cua = new T.Mesh(new T.PlaneGeometry(1.5, 0.9), new T.MeshBasicMaterial({ color: 0x1a0d08 })); cua.position.set(-3.5, 1.0, 1.31); V.scene.add(cua);
  var mLua = new T.MeshStandardMaterial({ color: 0xff7a1a, emissive: 0xff5a00, emissiveIntensity: 1.6, roughness: 1 });
  var lua = []; [-0.35, 0.05, 0.4].forEach(function (dx, k) { var c = new T.Mesh(new T.ConeGeometry(0.22, 0.7, 8), k === 1 ? new T.MeshStandardMaterial({ color: 0xffd34d, emissive: 0xffb000, emissiveIntensity: 1.8 }) : mLua); c.position.set(-3.5 + dx, 0.9, 1.15); V.scene.add(c); lua.push(c); });
  var den = new T.PointLight(0xff8a2a, 6, 7, 1.6); den.position.set(-3.5, 1.2, 2.0); V.scene.add(den);
  var ongKhoi = new T.Mesh(new T.CylinderGeometry(0.28, 0.34, 4.2, 14), mSat); ongKhoi.position.set(-5.2, 3.2, -0.9); V.scene.add(ongKhoi);
  // nồi hơi
  var mNoi = vatLieu(0x56645b, { metalness: 0.55, roughness: 0.45 });
  var noi = truX(T, 1.15, 3.8, mNoi, 32); noi.position.set(-3.5, 3.25, 0); V.scene.add(noi);
  [-4.9, -3.5, -2.1].forEach(function (x) { var r = new T.Mesh(new T.TorusGeometry(1.17, 0.05, 8, 40), mDong); r.rotation.y = Math.PI / 2; r.position.set(x, 3.25, 0); V.scene.add(r); });
  var vom = new T.Mesh(new T.CylinderGeometry(0.34, 0.38, 0.55, 18), mDong); vom.position.set(-3.0, 4.55, 0); V.scene.add(vom);
  // ống dẫn hơi tới hộp van trên xi-lanh
  var mOng = vatLieu(0x8d6b3e, { metalness: 0.7, roughness: 0.35 });
  var ong = new T.Mesh(new T.TubeGeometry(new T.CatmullRomCurve3([new T.Vector3(-3.0, 4.75, 0), new T.Vector3(-1.6, 5.1, 0), new T.Vector3(0.6, 4.6, 0), new T.Vector3(1.6, 3.9, 0), new T.Vector3(2.0, 3.55, 0)]), 40, 0.13, 10), mOng);
  V.scene.add(ong);
  var van = khoi(T, 2.2, 0.5, 0.7, mSat, 2.2, 3.35, 0); V.scene.add(van);
  var ongXa = new T.Mesh(new T.CylinderGeometry(0.1, 0.1, 0.9, 10), mSat); ongXa.position.set(3.0, 3.95, 0); V.scene.add(ongXa);
  // xi-lanh trong suốt, pít-tông, hơi nước
  var xl = truX(T, 0.72, 3.2, new T.MeshStandardMaterial({ color: 0xa9c3cf, transparent: true, opacity: 0.28, roughness: 0.1, metalness: 0.1, side: T.DoubleSide, depthWrite: false }), 28);
  xl.geometry = (function () { var g = new T.CylinderGeometry(0.72, 0.72, 3.2, 28, 1, true); g.rotateZ(Math.PI / 2); return g; })();
  xl.position.set(2.2, 2.6, 0); V.scene.add(xl);
  [0.6, 3.8].forEach(function (x) { var n = truX(T, 0.8, 0.14, mSat); n.position.set(x, 2.6, 0); V.scene.add(n); });
  [[0.6, -0.55], [3.8, -0.55]].forEach(function (p) { V.scene.add(khoi(T, 0.4, 1.6, 1.2, mDa, p[0], 1.2, 0)); });
  var mPit = vatLieu(0xb08d57, { metalness: 0.7, roughness: 0.3 });
  var pit = truX(T, 0.68, 0.26, mPit); pit.position.set(2.2, 2.6, 0); V.scene.add(pit);
  var mHoi = new T.MeshStandardMaterial({ color: 0xffffff, emissive: 0xdde8ee, emissiveIntensity: 0.4, transparent: true, opacity: 0.45, depthWrite: false });
  var gHoi = new T.CylinderGeometry(0.66, 0.66, 1, 20); gHoi.rotateZ(Math.PI / 2);
  var hoi = new T.Mesh(gHoi, mHoi); hoi.position.y = 2.6; V.scene.add(hoi);
  var gCan = new T.CylinderGeometry(0.07, 0.07, 1, 10); gCan.rotateZ(Math.PI / 2);
  var can = new T.Mesh(gCan, mDong); can.position.y = 2.6; V.scene.add(can);
  [2.25, 2.95].forEach(function (y) { V.scene.add(khoi(T, 2.4, 0.08, 0.5, mSat, 4.9, y, 0)); });
  var conTruot = khoi(T, 0.5, 0.55, 0.6, mSat, 4.8, 2.6, 0); V.scene.add(conTruot);
  // bánh đà, tay quay, thanh truyền
  var XW = 8, YW = 2.6, RC = 1.0, LTT = 3.2, LCAN = 2.6;
  var mBanh = vatLieu(0x2f3533, { metalness: 0.6, roughness: 0.4 });
  var banh = new T.Group(); banh.position.set(XW, YW, 0.35);
  banh.add(new T.Mesh(new T.TorusGeometry(2.0, 0.2, 12, 56), mBanh));
  for (var k = 0; k < 6; k++) { var nan = khoi(T, 3.9, 0.14, 0.12, mBanh, 0, 0, 0); nan.rotation.z = k * Math.PI / 6 * 2 / 2; banh.add(nan); }
  banh.add(truZ(T, 0.32, 0.5, mDong));
  var chot = truZ(T, 0.1, 0.5, mDong); chot.position.set(RC, 0, -0.35); banh.add(chot);
  V.scene.add(banh);
  [-1.6, 1.6].forEach(function (z) { V.scene.add(khoi(T, 0.5, 2.2, 0.4, mDa, XW, 1.5, z)); });
  var truc = truZ(T, 0.12, 3.6, mSat); truc.position.set(XW, YW, 0.4); V.scene.add(truc);
  var gTT = new T.BoxGeometry(1, 0.16, 0.14); var thanhTruyen = new T.Mesh(gTT, mSat); thanhTruyen.position.z = 0; V.scene.add(thanhTruyen);
  // puli, dây curoa, máy móc (máy kéo sợi giản lược)
  var puli = truZ(T, 0.5, 0.3, mGo); puli.position.set(XW, YW, 1.95); V.scene.add(puli);
  var XM = 13.2, YM = 1.7;
  var mMay = vatLieu(0x8a6a44, { roughness: 0.8, metalness: 0 });
  V.scene.add(khoi(T, 3.0, 1.7, 2.2, mMay, XM, 1.25, 0.6));
  var tang = truZ(T, 0.42, 0.3, mGo); tang.position.set(XM - 1.2, YM, 1.95); V.scene.add(tang);
  var day = [];
  [[0.5, 0.42], [-0.5, -0.42]].forEach(function (r) { var d = khoi(T, 1, 0.05, 0.22, new T.MeshStandardMaterial({ color: 0x3a2a1c, roughness: 0.9 }), 0, 0, 1.95); V.scene.add(d); day.push({ m: d, r: r }); });
  (function () { day.forEach(function (d) { var a = new T.Vector3(XW, YW + d.r[0], 1.95), b = new T.Vector3(XM - 1.2, YM + d.r[1], 1.95); d.m.position.copy(a).add(b).multiplyScalar(0.5); d.m.scale.x = a.distanceTo(b); d.m.rotation.z = Math.atan2(b.y - a.y, b.x - a.x); }); })();
  var coc = [];
  for (k = 0; k < 6; k++) { var cs = new T.Mesh(new T.CylinderGeometry(0.06, 0.09, 0.8, 10), mDong); cs.position.set(XM - 1.0 + (k % 3) * 1.0, 2.5, 0.1 + Math.floor(k / 3) * 0.9); V.scene.add(cs); coc.push(cs); var sb = new T.Mesh(new T.CylinderGeometry(0.16, 0.16, 0.35, 12), new T.MeshStandardMaterial({ color: 0xece3cf, roughness: 1 })); sb.position.set(0, 0.05, 0); cs.add(sb); }

  // khói, hơi
  var texK = vetKhoi(T), khois = [];
  for (k = 0; k < 22; k++) { var sp = new T.Sprite(new T.SpriteMaterial({ map: texK, color: 0xffffff, transparent: true, opacity: 0, depthWrite: false })); sp.visible = false; V.scene.add(sp); khois.push({ s: sp, life: 0 }); }
  function phutKhoi(x, y, z, mau, to) { for (var i = 0; i < khois.length; i++) if (khois[i].life <= 0) { var o = khois[i]; o.life = 1; o.x = x; o.y = y; o.z = z; o.to = to || 1; o.s.material.color.set(mau || 0xffffff); o.s.visible = true; return; } }

  // nhãn
  var NH = {
    lua: V.nhan('1. Lửa', new T.Vector3(-3.5, 2.4, 1.6), 'do'),
    noi: V.nhan('Nồi hơi', new T.Vector3(-3.5, 4.6, 0.6), ''),
    hoi: V.nhan('Hơi nước', new T.Vector3(-1.2, 5.3, 0), 'nuoc nho'),
    pit: V.nhan('2. Pít-tông (trong xi-lanh)', new T.Vector3(2.2, 3.7, 0.7), 'cam'),
    banh: V.nhan('3. Bánh đà', new T.Vector3(XW, YW + 2.4, 0.4), 'cam'),
    may: V.nhan('4. Máy móc', new T.Vector3(XM, 3.2, 0.6), 'cam')
  };
  var BUOC = [
    { ten: 'Lửa đun nóng nồi hơi', m: [mLo, mNoi], cam: [-1, 4, 10], t: [-3.5, 2.2, 0] },
    { ten: 'Hơi nước đẩy pít-tông chuyển động qua lại', m: [mPit, mOng], cam: [2.4, 4.6, 7.4], t: [2.2, 2.6, 0] },
    { ten: 'Pít-tông làm quay bánh đà', m: [mBanh, mDong], cam: [6.5, 4.2, 10.5], t: [6.2, 2.6, 0] },
    { ten: 'Bánh đà kéo máy móc chạy theo', m: [mMay, mGo], cam: [11, 4.8, 10], t: [11, 2, 0.5] }
  ];
  var sang = null;
  var ol = el('ol', { class: 'cac-buoc' }), moTaBuoc = el('p', { 'aria-live': 'polite', style: { margin: '8px 0 0' } });
  BUOC.forEach(function (b, i) {
    var nut = el('button', { type: 'button', class: 'nut' }, el('b', null, String(i + 1)), b.ten);
    nut.addEventListener('click', function () { V.bay(b.cam, b.t, 1200); sang = { m: b.m, t: 0 }; moTaBuoc.textContent = b.ten + '.'; MP.am(['xac_nhan', 'lat_trang', 'cach', 'tick'][i]); });
    ol.appendChild(el('li', null, nut));
  });
  var nutChay = el('button', { type: 'button', class: 'nut chinh', 'aria-pressed': 'true' }, 'Tạm dừng máy');
  var nutToan = el('button', { type: 'button', class: 'nut' }, 'Toàn cảnh');
  var rLua = el('input', { type: 'range', min: '15', max: '100', value: '55' }); MP.toThanh(rLua);
  var oLua = el('output', null, 'vừa');
  rLua.addEventListener('input', function () { MP.toThanh(rLua); var v = +rLua.value; oLua.textContent = v < 40 ? 'nhỏ' : v < 75 ? 'vừa' : 'to'; });
  rLua.addEventListener('change', function () { MP.am('lua_bung'); });
  nutChay.addEventListener('click', function () { mayChay = !mayChay; nutChay.textContent = mayChay ? 'Tạm dừng máy' : 'Cho máy chạy'; nutChay.setAttribute('aria-pressed', mayChay ? 'true' : 'false'); MP.nen(mayChay ? ['lua', 'may_hoi'] : ['lua']); MP.am('click'); });
  nutToan.addEventListener('click', function () { V.bay([4, 7.5, 17], [4, 2.4, 0], 1100); MP.am('click'); });
  phaiA.appendChild(el('div', { class: 'the-tin' }, el('h3', null, 'Máy hoạt động thế nào?'), ol, moTaBuoc));
  phaiA.appendChild(el('div', { class: 'the-tin' }, el('h3', null, 'Điều khiển'), el('label', { class: 'nhan-truot' }, el('span', null, 'Ngọn lửa'), rLua, oLua),
    el('div', { class: 'hang-nut', style: { marginTop: '8px' } }, nutChay, nutToan),
    el('p', { style: { fontSize: '.86rem', color: 'var(--chu-phu)', margin: '8px 0 0' } }, 'Lửa càng to, hơi nước càng mạnh, máy chạy càng nhanh (mô phỏng minh hoạ).')));
  var tin = el('div', { class: 'the-tin' }, el('h3', null, 'Theo SGK'));
  var ul = el('ul'); MP.loi([5]).slice(0, 1).concat(MP.loi([6, 9])).forEach(function (l) { ul.appendChild(el('li', null, l)); });
  tin.appendChild(ul); tin.appendChild(el('p', { style: { fontSize: '.8rem', color: 'var(--chu-phu)', margin: '6px 0 0' } }, MP.trang(MP.trangCanh([5, 6, 9]))));
  phaiA.appendChild(tin);

  var theta = Math.PI * 0.6, nuaVong = Math.floor(theta / Math.PI), viTri = new T.Vector3();
  V.moi(function (dt, t) {
    var f = +rLua.value / 100;
    // lửa bập bùng
    lua.forEach(function (c, i) { var s = (0.6 + f * 0.8) * (0.85 + 0.2 * Math.sin(t * (9 + i * 3) + i)); c.scale.set(s, s * (1 + 0.15 * Math.sin(t * 13 + i)), s); });
    den.intensity = (3 + 6 * f) * (0.85 + 0.15 * Math.sin(t * 17));
    if (mayChay) theta += dt * (0.5 + 3.3 * f);
    banh.rotation.z = theta;
    var cx = XW + RC * Math.cos(theta), cy = YW + RC * Math.sin(theta);
    var xc = cx - Math.sqrt(LTT * LTT - Math.pow(cy - YW, 2)), xp = xc - LCAN;
    conTruot.position.x = xc;
    thanhTruyen.position.set((xc + cx) / 2, (YW + cy) / 2, 0.05); thanhTruyen.scale.x = Math.hypot(cx - xc, cy - YW); thanhTruyen.rotation.z = Math.atan2(cy - YW, cx - xc);
    pit.position.x = xp; can.position.x = (xp + xc) / 2; can.scale.x = xc - xp;
    // hơi nước nằm ở phía đang đẩy pít-tông (đổi phía mỗi nửa vòng)
    var dayPhai = Math.sin(theta) > 0;
    var a0 = dayPhai ? 0.67 : xp + 0.13, a1 = dayPhai ? xp - 0.13 : 3.73;
    hoi.position.x = (a0 + a1) / 2; hoi.scale.x = Math.max(0.01, a1 - a0); hoi.material.opacity = mayChay ? 0.3 + 0.25 * f : 0.12;
    // mỗi điểm chết: xả hơi, tiếng xì và tiếng va kim loại
    var nv = Math.floor(theta / Math.PI);
    if (nv !== nuaVong) { nuaVong = nv; phutKhoi(3.0, 4.4, 0, 0xffffff, 0.8); MP.am('hoi_nuoc', { lv: 0.6 + 0.5 * f }); if (nv % 2 === 0) MP.am('cach', { tre: 0.05 }); }
    if (Math.random() < dt * (1.5 + 3 * f)) phutKhoi(-5.2 + (Math.random() - 0.5) * 0.2, 5.3, -0.9, 0x6d6a66, 1.4);
    khois.forEach(function (o) {
      if (o.life <= 0) return;
      o.life -= dt * 0.45; o.y += dt * 1.1; o.x += dt * 0.25;
      var s = (1.4 - o.life) * 1.3 * o.to; o.s.scale.set(s, s, s); o.s.position.set(o.x, o.y, o.z); o.s.material.opacity = Math.max(0, o.life) * 0.6;
      if (o.life <= 0) o.s.visible = false;
    });
    tang.rotation.z = theta * 1.2; coc.forEach(function (c) { c.rotation.y = theta * 6; });
    // làm sáng bộ phận đang giải thích
    if (sang) {
      sang.t += dt; var k2 = Math.max(0, Math.sin(sang.t * 4)) * Math.max(0, 1 - sang.t / 3.2);
      sang.m.forEach(function (m) { if (m.emissive && m !== mLua) { m.emissive.setRGB(0.95 * k2, 0.42 * k2, 0.1 * k2); } });
      if (sang.t > 3.2) { sang.m.forEach(function (m) { if (m.emissive) m.emissive.setRGB(0, 0, 0); }); sang = null; }
    }
    viTri.set(xp, 2.6, 0.75); NH.pit.pos = viTri;
  });

  // =============================== THẺ 2: VỊ TRÍ NHÀ MÁY
  function taoNhaMay() {
    var W = BC.tao(pB, { nen: 0xd9e7ee, suongMu: [55, 130], camPos: [-3, 22, 34], target: [-1, 0, 0], minDist: 8, maxDist: 75, nangPos: [-15, 25, 18], moTa: 'Mô hình 3D: nhà máy bên sông và nhà máy trong thành phố. Kéo để xoay.' });
    var phaiB = el('div', { class: 'bang-dk' }); pB.appendChild(phaiB);
    if (!W) return { nen: function () {} };
    var rnd = BC.rngSo(5);
    var dat = new T.Mesh(new T.PlaneGeometry(120, 90), new T.MeshStandardMaterial({ color: 0xa3b673, roughness: 1 })); dat.rotation.x = -Math.PI / 2; W.scene.add(dat);
    // sông chảy xiết
    var cv = document.createElement('canvas'); cv.width = 256; cv.height = 64; var cx = cv.getContext('2d');
    cx.fillStyle = '#4f93b6'; cx.fillRect(0, 0, 256, 64);
    for (var s = 0; s < 70; s++) { cx.strokeStyle = 'rgba(255,255,255,' + (0.08 + rnd() * 0.2) + ')'; cx.lineWidth = 1 + rnd() * 2; var y0 = rnd() * 64, x0 = rnd() * 256; cx.beginPath(); cx.moveTo(x0, y0); cx.lineTo(x0 + 25 + rnd() * 40, y0); cx.stroke(); }
    var tex = new T.CanvasTexture(cv); tex.wrapS = tex.wrapT = T.RepeatWrapping; tex.repeat.set(10, 1); tex.colorSpace = T.SRGBColorSpace;
    var songM = new T.Mesh(new T.PlaneGeometry(90, 5.5), new T.MeshStandardMaterial({ map: tex, roughness: 0.25 })); songM.rotation.x = -Math.PI / 2; songM.position.set(0, 0.03, -9); W.scene.add(songM);
    var bo = new T.Mesh(new T.PlaneGeometry(90, 7), new T.MeshStandardMaterial({ color: 0xb9a171 })); bo.rotation.x = -Math.PI / 2; bo.position.set(0, 0.015, -9); W.scene.add(bo);
    function nha(w, h, d, mau, mai) {
      var g = new T.Group(); var than = khoi(T, w, h, d, new T.MeshStandardMaterial({ color: mau, roughness: 0.9 }), 0, h / 2, 0); g.add(than);
      var gm = new T.CylinderGeometry(0.01, d * 0.62, w + 0.2, 3, 1); gm.rotateZ(Math.PI / 2); var m = new T.Mesh(gm, new T.MeshStandardMaterial({ color: mai || 0x4a3b33, roughness: 0.9, flatShading: true })); m.scale.set(1, 0.55, 1); m.position.y = h + d * 0.16; g.add(m);
      return g;
    }
    function nhaMayG(coOngKhoi) {
      var g = new T.Group(), b = nha(6, 3, 3.2, 0x9b4a35, 0x3d3330); g.add(b);
      for (var i = 0; i < 5; i++) { var cs = khoi(T, 0.6, 0.8, 0.05, new T.MeshStandardMaterial({ color: 0x2a2320 }), -2.4 + i * 1.2, 1.8, 1.63); g.add(cs); }
      if (coOngKhoi) { var o = new T.Mesh(new T.CylinderGeometry(0.35, 0.5, 6, 12), new T.MeshStandardMaterial({ color: 0x6b3a2c, roughness: 0.9 })); o.position.set(2.2, 3, -1); g.add(o); g.mieng = new T.Vector3(2.2, 6.2, -1); }
      return g;
    }
    // xưởng dệt ven sông + guồng nước
    var xuong = nhaMayG(false); xuong.position.set(-11, 0, -4.4); W.scene.add(xuong);
    var guong = new T.Group(); guong.position.set(-7.4, 1.25, -6.9);
    guong.add(new T.Mesh(new T.TorusGeometry(1.45, 0.08, 8, 36), mGo));
    for (var p = 0; p < 10; p++) { var cg = khoi(T, 0.5, 0.08, 0.7, mGo, 0, 0, 0); var a = p / 10 * Math.PI * 2; cg.position.set(Math.cos(a) * 1.45, Math.sin(a) * 1.45, 0); cg.rotation.z = a; guong.add(cg); var nn = khoi(T, 2.9, 0.06, 0.06, mGo, 0, 0, 0); nn.rotation.z = a; guong.add(nn); }
    W.scene.add(guong);
    // thành phố
    var thanhPho = new T.Group(); W.scene.add(thanhPho);
    for (var h = 0; h < 30; h++) {
      var ang = rnd() * Math.PI * 2, rr = 3.2 + rnd() * 7.5, x = 8 + Math.cos(ang) * rr * 1.2, z = 6 + Math.sin(ang) * rr * 0.75;
      if (Math.hypot(x - 8, z - 6) < 3.3) continue;
      var n = nha(0.9 + rnd() * 0.8, 0.7 + rnd() * 0.9, 0.9 + rnd() * 0.6, BC.bienMau(0xcbb595, 0.18, rnd).getHex(), 0x5a3f33); n.position.set(x, 0, z); n.rotation.y = rnd() * 0.6; thanhPho.add(n);
    }
    var quangTruong = new T.Mesh(new T.CircleGeometry(3.1, 32), new T.MeshStandardMaterial({ color: 0xc9bfa8 })); quangTruong.rotation.x = -Math.PI / 2; quangTruong.position.set(8, 0.02, 6); W.scene.add(quangTruong);
    // máy hơi nước nhỏ (biểu tượng 1784) và các nhà máy mới có ống khói
    var mayNho = new T.Group(); mayNho.position.set(8, 0, 6);
    var nn2 = truX(T, 0.5, 1.6, mNoi); nn2.position.y = 0.7; mayNho.add(nn2);
    var bd = new T.Mesh(new T.TorusGeometry(0.7, 0.08, 8, 24), mBanh); bd.position.set(1.2, 0.8, 0.4); mayNho.add(bd);
    mayNho.visible = false; W.scene.add(mayNho);
    var nmMoi = [nhaMayG(true), nhaMayG(true)];
    nmMoi[0].position.set(6.2, 0, 4.8); nmMoi[0].rotation.y = 0.15; nmMoi[1].position.set(11.4, 0, 8.6); nmMoi[1].rotation.y = -0.3; nmMoi[1].scale.setScalar(0.8);
    nmMoi.forEach(function (g) { g.visible = false; W.scene.add(g); });
    var ma = nhaMayG(false); ma.traverse(function (o) { if (o.material) { o.material = o.material.clone(); o.material.transparent = true; o.material.opacity = 0.45; } }); ma.visible = false; W.scene.add(ma);
    var duong = new T.CatmullRomCurve3([new T.Vector3(-11, 0.1, -4.4), new T.Vector3(-4, 0.1, 2.5), new T.Vector3(3, 0.1, 5), new T.Vector3(6.2, 0.1, 4.8)]);
    var gl = new T.BufferGeometry().setFromPoints(duong.getPoints(60)), vet = new T.Line(gl, new T.LineDashedMaterial({ color: 0xb8261e, dashSize: 0.6, gapSize: 0.4 })); vet.computeLineDistances(); vet.visible = false; W.scene.add(vet);
    var texK2 = vetKhoi(T), ks = [];
    for (var q = 0; q < 26; q++) { var sp = new T.Sprite(new T.SpriteMaterial({ map: texK2, color: 0x77726c, transparent: true, opacity: 0, depthWrite: false })); sp.visible = false; W.scene.add(sp); ks.push({ s: sp, life: 0 }); }

    W.nhan('Sông chảy xiết', new T.Vector3(-22, 0.3, -9), 'nuoc');
    var nXuong = W.nhan('Xưởng dệt bên bờ sông (Man-che-xtơ, 1771)', new T.Vector3(-11, 4.6, -4.4), 'cam');
    var nGuong = W.nhan('Guồng nước: máy chạy bằng sức nước', new T.Vector3(-7.4, 3.0, -6.9), 'nuoc nho');
    W.nhan('Trung tâm thành phố', new T.Vector3(8, 0.5, 6), 'nho');
    var nMay = W.nhan('Máy hơi nước (1784)', new T.Vector3(8, 2.2, 6), 'do');
    var nMoi = W.nhan('Nhà máy xây ở nơi thuận lợi, không phải bám theo bờ sông', new T.Vector3(8.5, 7.4, 6.5), 'cam');

    var MOC = [
      { nam: '1769', canh: [[3, 0]] }, { nam: '1771', canh: [[3, 1], [4, 0]] }, { nam: '1784', canh: [[5, 0]] }, { nam: 'Sau đó', canh: [[7, 0], [9, 0]] }
    ];
    var r = el('input', { type: 'range', min: '0', max: '3', step: '1', value: '0', 'aria-label': 'Mốc thời gian' }); MP.toThanh(r);
    var oNam = el('output', null, '1769'), loiB = el('div', { class: 'sb-loi', 'aria-live': 'polite' });
    var nutMoc = MOC.map(function (m, i) { var b = el('button', { type: 'button', class: 'nut' }, m.nam); b.addEventListener('click', function () { r.value = i; datMoc(i, true); }); return b; });
    phaiB.appendChild(el('div', { class: 'the-tin' }, el('h3', null, 'Kéo theo mốc năm'), el('label', { class: 'nhan-truot' }, el('span', null, 'Mốc'), r, oNam), el('div', { class: 'hang-nut', style: { marginTop: '6px' } }, nutMoc), loiB));
    var st = { i: -1, t: 0 };
    function datMoc(i, am) {
      i = +i; MP.toThanh(r); oNam.textContent = MOC[i].nam;
      nutMoc.forEach(function (b, j) { b.setAttribute('aria-pressed', j === i ? 'true' : 'false'); });
      var lines = MOC[i].canh.map(function (c) { return MP.canh(c[0]).loi[c[1]]; });
      MP.hopLoi(loiB, lines, MP.trangCanh(MOC[i].canh.map(function (c) { return c[0]; })));
      xuong.visible = guong.visible = i >= 1; nXuong.hien = nGuong.hien = i >= 1;
      mayNho.visible = i >= 2; nMay.hien = i === 2;
      nmMoi.forEach(function (g) { g.visible = i >= 3; }); nMoi.hien = i >= 3; vet.visible = i >= 3;
      if (i === 3 && st.i !== 3) { st.t = 0; ma.visible = true; nmMoi.forEach(function (g) { g.scale.y = 0.01; }); W.bay([-2, 20, 30], [0, 0, 1], 1200); if (am) MP.am('dat'); }
      else if (i < 3) { ma.visible = false; nmMoi.forEach(function (g) { g.scale.y = 1; }); }
      if (am && i !== st.i) MP.am(i === 1 ? 'te_nuoc' : i === 2 ? 'hoi_nuoc' : i === 0 ? 'lat_trang' : 'mo_pha');
      st.i = i; capNen();
    }
    function capNen() { MP.nen(st.i <= 0 ? ['nuoc', 'gio'] : st.i === 1 ? ['nuoc', 'gio', 'banh_xe_nuoc'] : st.i === 2 ? ['nuoc', 'banh_xe_nuoc', 'may_hoi'] : ['nuoc', 'dam_dong', 'may_hoi']); }
    r.addEventListener('input', function () { datMoc(r.value, true); });
    var tin2 = el('div', { class: 'the-tin' }, el('h3', null, 'Vì sao nhà máy “rời” bờ sông?'),
      el('p', null, MP.canh(4).loi[0]), el('p', null, MP.canh(4).loi[1]), el('p', null, MP.canh(7).loi[0]),
      el('p', { style: { fontSize: '.8rem', color: 'var(--chu-phu)' } }, MP.trang(MP.trangCanh([3, 4, 5, 7, 9]))));
    phaiB.appendChild(tin2);
    datMoc(0, false);
    W.moi(function (dt, t) {
      tex.offset.x -= dt * 0.9;
      if (guong.visible) guong.rotation.z -= dt * 1.6;
      if (st.i === 3 && ma.visible) {
        st.t += dt; var k = MP.ease(st.t / 2.6), pt = duong.getPoint(k);
        ma.position.copy(pt); ma.position.y = 0;
        nmMoi.forEach(function (g, j) { g.scale.y = Math.max(0.01, MP.ease((st.t - 2.2 - j * 0.4) / 0.8)); });
        if (st.t > 3.6) { ma.visible = false; MP.am('chuong'); W.bang('Nhà máy có thể xây ở bất cứ nơi nào thuận lợi', true); setTimeout(function () { W.bang('', false); }, 3500); }
      }
      if (st.i >= 3) nmMoi.forEach(function (g) { if (g.mieng && Math.random() < dt * 2.2) { var w = g.localToWorld(g.mieng.clone()); for (var i = 0; i < ks.length; i++) if (ks[i].life <= 0) { var o = ks[i]; o.life = 1; o.p = w; o.s.visible = true; break; } } });
      ks.forEach(function (o) { if (o.life <= 0) return; o.life -= dt * 0.35; o.p.y += dt * 1.0; o.p.x += dt * 0.5; var s = (1.3 - o.life) * 2; o.s.scale.set(s, s, s); o.s.position.copy(o.p); o.s.material.opacity = Math.max(0, o.life) * 0.55; if (o.life <= 0) o.s.visible = false; });
    });
    return { nen: capNen };
  }
});
