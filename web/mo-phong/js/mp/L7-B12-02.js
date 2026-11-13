/* L7-B12-02 · Phòng tuyến sông Như Nguyệt (1077) – mô hình 3D: đê cao như tường thành, trên đóng tre làm dậu dày mấy tầng,
   bộ binh Đại Việt đóng giữ ở bờ nam; quân bộ Tống (Quách Quỳ) ở bờ bắc tìm cách vượt sông và bị đẩy lùi.
   Thẻ thứ hai: lược đồ động theo Hình 3 SGK LSĐL 7 (pipeline/maps/specs/nhu-nguyet-1077.json). Mô hình minh hoạ, không theo tỉ lệ. */
MP.onReady(function () {
  var root = MP.khung(), el = MP.el, BC = window.BaChieu;
  var tab3 = el('button', { type: 'button', class: 'nut', role: 'tab', 'aria-selected': 'true' }, 'Mô hình 3D phòng tuyến');
  var tab2 = el('button', { type: 'button', class: 'nut', role: 'tab', 'aria-selected': 'false' }, 'Lược đồ diễn biến');
  var p3 = el('div', { role: 'tabpanel' }), p2 = el('div', { role: 'tabpanel', hidden: true });
  root.appendChild(el('div', { class: 'tab-3d', role: 'tablist', 'aria-label': 'Chọn cách xem' }, tab3, tab2));
  root.appendChild(p3); root.appendChild(p2);
  var player = null;
  function chonTab(i) {
    tab3.setAttribute('aria-selected', i === 0 ? 'true' : 'false'); tab2.setAttribute('aria-selected', i === 1 ? 'true' : 'false');
    p3.hidden = i !== 0; p2.hidden = i !== 1; MP.am('click');
    if (i === 1 && !player) taoLuocDo();
    if (i === 0) MP.nen(['nuoc', 'gio']); else if (player) player.setPhase(player.pi, player.u);
  }
  tab3.addEventListener('click', function () { chonTab(0); }); tab2.addEventListener('click', function () { chonTab(1); });
  function taoLuocDo() {
    player = new window.SaBanWeb.MapPlayer(p2, {
      id: 'nn', spec: window.MP_BANDO['nhu-nguyet-1077'], an: ['trai1_nhan'],
      phases: [
        { key: 'chuan_bi', nhan: 'Phòng tuyến bờ nam', canh: [6, 7] },
        { key: 'tong_tien', nhan: 'Quân Tống tiến sang (1077)', canh: [9, 10] },
        { key: 'vuot_song', nhan: 'Vượt sông – bị đẩy lùi', canh: [12] }
      ],
      am: {
        nen: ['nuoc', 'gio'], batDau: 'trong',
        doiTuong: function (id, o) { if (o.loai === 'mui_ten_dich') return ['vut_nhe', 'buoc_quan']; if (o.loai === 'chan_danh') return ['trong_nho', 'vut']; if (o.loai === 'nhan') return 'lat_trang'; }
      }
    });
  }

  // ===================== mô hình 3D
  MP.nen(['nuoc', 'gio']);
  var V = BC.tao(p3, { nen: 0xd6e6ee, suongMu: [60, 150], camPos: [18, 20, 32], target: [0, 0, 2], minDist: 5, maxDist: 90, nangPos: [-20, 30, 25], moTa: 'Mô hình 3D phòng tuyến sông Như Nguyệt. Kéo để xoay, cuộn hoặc chụm để phóng to.' });
  var phai = el('div', { class: 'bang-dk' }); p3.appendChild(phai);
  if (!V) return;
  var T = V.T, rnd = BC.rngSo(23);
  function zc(x) { return 1.4 * Math.sin(x * 0.11); }
  var X0 = -44, X1 = 44, DE_X0 = -32, DE_X1 = 32, BW = 3.4, TW = 1.1, HD = 1.9, DZ = 5.2, RIVER = 7;

  var dat = new T.Mesh(new T.PlaneGeometry(150, 110), new T.MeshStandardMaterial({ color: 0x9db06a, roughness: 1 }));
  dat.rotation.x = -Math.PI / 2; V.scene.add(dat);
  var song = [], xx;
  for (xx = X0; xx <= X1; xx += 1) song.push([xx, zc(xx)]);
  var bai = new T.Mesh(BC.dai(song, RIVER + 1.4, 0.012, false), new T.MeshStandardMaterial({ color: 0xb9a171, roughness: 1, side: T.DoubleSide })); V.scene.add(bai);
  // mặt nước có vân trôi nhẹ
  var cv = document.createElement('canvas'); cv.width = 256; cv.height = 64; var cx = cv.getContext('2d');
  cx.fillStyle = '#5f9fc0'; cx.fillRect(0, 0, 256, 64);
  for (var s = 0; s < 40; s++) { cx.strokeStyle = 'rgba(255,255,255,' + (0.05 + rnd() * 0.12) + ')'; cx.lineWidth = 1 + rnd() * 1.5; var yy = rnd() * 64, x0 = rnd() * 256; cx.beginPath(); cx.moveTo(x0, yy); cx.lineTo(x0 + 20 + rnd() * 50, yy + (rnd() - 0.5) * 3); cx.stroke(); }
  var texNuoc = new T.CanvasTexture(cv); texNuoc.wrapS = texNuoc.wrapT = T.RepeatWrapping; texNuoc.colorSpace = T.SRGBColorSpace;
  var gNuoc = BC.dai(song, RIVER, 0.03, false), uv = [];
  for (var i = 0; i < song.length; i++) uv.push(i / 6, 1, i / 6, 0);
  gNuoc.setAttribute('uv', new T.Float32BufferAttribute(uv, 2));
  var matNuoc = new T.MeshStandardMaterial({ map: texNuoc, roughness: 0.25, metalness: 0.05, side: T.DoubleSide });
  V.scene.add(new T.Mesh(gNuoc, matNuoc));

  // ---- đê đất (hình thang), chạy dọc bờ nam
  var de = [];
  for (xx = DE_X0; xx <= DE_X1; xx += 1) de.push([xx, zc(xx) + DZ]);
  function thanDe(pts) {
    var pos = [], col = [], cDat = new T.Color(0x9a7650), cCo = new T.Color(0x80924c), sec = [], n = pts.length, k;
    for (k = 0; k < n; k++) {
      var a = pts[Math.max(0, k - 1)], b = pts[Math.min(n - 1, k + 1)], tx = b[0] - a[0], tz = b[1] - a[1], l = Math.hypot(tx, tz), nx = -tz / l, nz = tx / l, p = pts[k];
      // n hướng về phía nam (+z): mặt hướng ra sông là phía -n
      sec.push([[p[0] - nx * BW / 2, 0, p[1] - nz * BW / 2], [p[0] - nx * TW / 2, HD, p[1] - nz * TW / 2], [p[0] + nx * TW / 2, HD, p[1] + nz * TW / 2], [p[0] + nx * BW / 2, 0, p[1] + nz * BW / 2]]);
    }
    function quad(A, B, C, D, c) { [A, B, C, A, C, D].forEach(function (q) { pos.push(q[0], q[1], q[2]); col.push(c.r, c.g, c.b); }); }
    for (k = 0; k < n - 1; k++) { var A = sec[k], B = sec[k + 1]; quad(A[0], B[0], B[1], A[1], cDat); quad(A[1], B[1], B[2], A[2], cCo); quad(A[2], B[2], B[3], A[3], cDat); }
    quad(sec[0][0], sec[0][1], sec[0][2], sec[0][3], cDat); quad(sec[n - 1][3], sec[n - 1][2], sec[n - 1][1], sec[n - 1][0], cDat);
    var g = new T.BufferGeometry(); g.setAttribute('position', new T.Float32BufferAttribute(pos, 3)); g.setAttribute('color', new T.Float32BufferAttribute(col, 3)); g.computeVertexNormals();
    return new T.Mesh(g, new T.MeshStandardMaterial({ vertexColors: true, roughness: 0.95, side: T.DoubleSide }));
  }
  var meshDe = thanDe(de); V.scene.add(meshDe);

  // ---- dậu tre: ba hàng cọc tre nghiêng về phía sông, có nẹp ngang
  function caoTai(o) { return o <= TW / 2 ? HD : HD * Math.max(0, (BW / 2 - o) / ((BW - TW) / 2)); }
  var HANG = [0.25, 0.95, 1.45], buoc = 0.26, cocs = [];
  HANG.forEach(function (o, hi) {
    for (var x = DE_X0 + 0.3; x <= DE_X1 - 0.3; x += buoc) cocs.push({ x: x + (rnd() - 0.5) * 0.06, z: zc(x) + DZ - o, y: caoTai(o), h: 1.15 + rnd() * 0.35 - hi * 0.05, hang: hi });
  });
  var gCoc = new T.CylinderGeometry(0.03, 0.055, 1, 5); gCoc.translate(0, 0.5, 0);
  var imCoc = new T.InstancedMesh(gCoc, new T.MeshStandardMaterial({ color: 0xffffff, roughness: 0.7 }), cocs.length);
  var M = new T.Matrix4(), Q = new T.Quaternion(), E = new T.Euler();
  cocs.forEach(function (c, k) {
    E.set(-0.38 - rnd() * 0.08, 0, (rnd() - 0.5) * 0.1); Q.setFromEuler(E);
    M.compose(new T.Vector3(c.x, c.y - 0.15, c.z), Q, new T.Vector3(1, c.h, 1)); imCoc.setMatrixAt(k, M);
    imCoc.setColorAt(k, BC.bienMau(0xb4a656, 0.12, rnd));
  });
  V.scene.add(imCoc);
  HANG.forEach(function (o) {
    var pts = [];
    for (var x = DE_X0 + 0.3; x <= DE_X1 - 0.3; x += 2) pts.push(new T.Vector3(x, caoTai(o) + 0.55, zc(x) + DZ - o - 0.2));
    var tube = new T.Mesh(new T.TubeGeometry(new T.CatmullRomCurve3(pts), 120, 0.03, 5, false), new T.MeshStandardMaterial({ color: 0x8d7a3e, roughness: 0.8 }));
    V.scene.add(tube);
  });

  // ---- người (khối giản lược): thân, đầu, giáo
  function quan(mau, ds, giao) {
    var n = ds.length, than = new T.InstancedMesh(new T.CylinderGeometry(0.13, 0.18, 0.62, 7), new T.MeshStandardMaterial({ color: mau, roughness: 0.8 }), n);
    var dau = new T.InstancedMesh(new T.SphereGeometry(0.11, 10, 8), new T.MeshStandardMaterial({ color: 0xd2ab83, roughness: 0.8 }), n);
    var gq = new T.CylinderGeometry(0.012, 0.012, 1.5, 4); gq.translate(0, 0.75, 0);
    var cay = new T.InstancedMesh(gq, new T.MeshStandardMaterial({ color: 0x5e4a33 }), n);
    var nhom = new T.Group(); nhom.add(than, dau, cay);
    nhom.dat = function (k, x, y, z) {
      M.compose(new T.Vector3(x, y + 0.31, z), new T.Quaternion(), new T.Vector3(1, 1, 1)); than.setMatrixAt(k, M);
      M.compose(new T.Vector3(x, y + 0.72, z), new T.Quaternion(), new T.Vector3(1, 1, 1)); dau.setMatrixAt(k, M);
      Q.setFromEuler(E.set(giao, 0, 0.08)); M.compose(new T.Vector3(x + 0.16, y + 0.2, z), Q, new T.Vector3(1, 1, 1)); cay.setMatrixAt(k, M);
      than.instanceMatrix.needsUpdate = dau.instanceMatrix.needsUpdate = cay.instanceMatrix.needsUpdate = true;
    };
    ds.forEach(function (p, k) { nhom.dat(k, p[0], p[1], p[2]); });
    return nhom;
  }
  var taDs = [];
  [-24, -14, -4, 6, 16, 26].forEach(function (cx0) { for (var r = 0; r < 2; r++) for (var c = 0; c < 4; c++) { var x = cx0 + c * 0.7 + r * 0.35; taDs.push([x, 0, zc(x) + DZ + 2.5 + r * 0.8]); } });
  V.scene.add(quan(0x8c2f23, taDs, 0.25));
  // cờ đỏ của quân ta
  var co = [];
  [-20, -8, 4, 14, 24].forEach(function (x) {
    var g = new T.Group(), z = zc(x) + DZ + 1.6;
    var cot = new T.Mesh(new T.CylinderGeometry(0.03, 0.03, 2.6, 5), new T.MeshStandardMaterial({ color: 0x5e4a33 })); cot.position.y = 1.3; g.add(cot);
    var la = new T.Mesh(new T.PlaneGeometry(0.9, 0.55, 6, 1), new T.MeshStandardMaterial({ color: 0xb8261e, side: T.DoubleSide, roughness: 0.7 })); la.position.set(0.45, 2.3, 0); g.add(la);
    g.position.set(x, 0, z); V.scene.add(g); co.push(la);
  });
  // quân Tống ở bờ bắc: lều trại, binh lính, bè mảng
  var leu = new T.InstancedMesh(new T.ConeGeometry(0.95, 1.25, 8), new T.MeshStandardMaterial({ color: 0x4b5a86, roughness: 0.9 }), 12);
  for (var t2 = 0; t2 < 12; t2++) { var lx = -26 + t2 * 4.6 + rnd(), lz = zc(lx) - 12 - rnd() * 4; M.compose(new T.Vector3(lx, 0.62, lz), new T.Quaternion(), new T.Vector3(1, 1, 1)); leu.setMatrixAt(t2, M); }
  V.scene.add(leu);
  var tongDs = [];
  [-18, -6, 6, 18].forEach(function (cx0) { for (var r = 0; r < 2; r++) for (var c = 0; c < 4; c++) { var x = cx0 + c * 0.75 + r * 0.35; tongDs.push([x, 0, zc(x) - 7.5 - r * 0.8]); } });
  V.scene.add(quan(0x2e3e73, tongDs, -0.25));
  var be = [], BE_X = [-16, -9, -2, 5, 12, 19];
  BE_X.forEach(function (x) {
    var g = new T.Group();
    var san = new T.Mesh(new T.BoxGeometry(1.7, 0.16, 1.0), new T.MeshStandardMaterial({ color: 0x7a6b55, roughness: 0.9 })); san.position.y = 0.08; g.add(san);
    for (var k = 0; k < 3; k++) { var ng = new T.Mesh(new T.CylinderGeometry(0.11, 0.14, 0.5, 6), new T.MeshStandardMaterial({ color: 0x2e3e73 })); ng.position.set(-0.5 + k * 0.5, 0.41, 0); g.add(ng); }
    g.zBo = zc(x) - RIVER / 2 - 0.9; g.position.set(x, 0.02, g.zBo); g.x0 = x; V.scene.add(g); be.push(g);
  });
  // dãy núi Tam Đảo phía thượng nguồn
  for (var mn = 0; mn < 9; mn++) {
    var h = 6 + rnd() * 6, nui = new T.Mesh(new T.ConeGeometry(5 + rnd() * 4, h, 9), new T.MeshStandardMaterial({ color: BC.bienMau(0x6c8752, 0.12, rnd), roughness: 1, flatShading: true }));
    nui.position.set(-48 - rnd() * 8, h / 2 - 0.2, -14 + mn * 3.6 + rnd() * 2); V.scene.add(nui);
  }
  // mũi tên chỉ đường bộ về Thăng Long (phía nam)
  var mt = new T.Shape(); mt.moveTo(-0.7, 0); mt.lineTo(0.7, 0); mt.lineTo(0.7, 6); mt.lineTo(1.6, 6); mt.lineTo(0, 8.2); mt.lineTo(-1.6, 6); mt.lineTo(-0.7, 6); mt.closePath();
  var muiTen = new T.Mesh(new T.ShapeGeometry(mt), new T.MeshStandardMaterial({ color: 0xd9a08a, roughness: 1, side: T.DoubleSide }));
  muiTen.rotation.x = Math.PI / 2; muiTen.position.set(2, 0.04, zc(2) + DZ + 5.2); V.scene.add(muiTen);

  // ---- nhãn
  V.nhan('Sông Như Nguyệt (đoạn sông Cầu)', new T.Vector3(-2, 0.3, zc(-2)), 'nuoc');
  V.nhan('Bờ bắc: quân bộ Tống (Quách Quỳ chỉ huy)', new T.Vector3(2, 1.6, zc(2) - 11), 'cham');
  V.nhan('Bờ nam: phòng tuyến Đại Việt', new T.Vector3(-8, 2.9, zc(-8) + DZ), 'cam');
  V.nhan('Đê cao như tường thành', new T.Vector3(10, 2.2, zc(10) + DZ + 0.6), 'nho');
  V.nhan('Dậu tre dày mấy tầng', new T.Vector3(-17, 3.0, zc(-17) + DZ - 0.6), 'nho');
  V.nhan('Bộ binh Đại Việt đóng giữ', new T.Vector3(16.5, 1.4, zc(16) + DZ + 3), 'do');
  V.nhan('Dãy núi Tam Đảo', new T.Vector3(-50, 10, 0), 'nho');
  V.nhan('Đường bộ tiến về Thăng Long', new T.Vector3(2, 0.4, zc(2) + DZ + 12.5), 'nho');
  var nhanMatCat = V.nhan('Mặt cắt đê: dậu tre trên đỉnh và mái đê', new T.Vector3(DE_X1, HD + 1.2, zc(DE_X1) + DZ), 'cam');
  nhanMatCat.hien = false;

  // ---- điều khiển, thông tin
  var GOC = {
    toan: { ten: 'Toàn cảnh', p: [18, 20, 32], t: [0, 0, 2] },
    bac: { ten: 'Nhìn từ bờ bắc', p: [3, 3.4, zc(3) - 15], t: [3, 1.4, zc(3) + DZ] },
    cat: { ten: 'Mặt cắt đê', p: [DE_X1 + 7.5, 2.6, zc(DE_X1) + DZ + 1.2], t: [DE_X1 - 1, 1.1, zc(DE_X1) + DZ] },
    tren: { ten: 'Từ trên cao', p: [0.01, 52, 3], t: [0, 0, 3] }
  };
  var nutGoc = Object.keys(GOC).map(function (k) {
    var b = el('button', { type: 'button', class: 'nut' }, GOC[k].ten);
    b.addEventListener('click', function () { V.bay(GOC[k].p, GOC[k].t, 1400); V.labels.forEach(function (L) { L.hien = k === 'cat' ? L === nhanMatCat : L !== nhanMatCat; }); MP.am('lat_trang'); });
    return b;
  });
  var nutVuot = el('button', { type: 'button', class: 'nut chinh' }, 'Quân Tống vượt sông');
  var trangThai = el('p', { 'aria-live': 'polite', style: { margin: '8px 0 0', fontWeight: 600 } });
  phai.appendChild(el('div', { class: 'the-tin' }, el('h3', null, 'Góc nhìn'), el('div', { class: 'hang-nut' }, nutGoc),
    el('h3', { style: { marginTop: '12px' } }, 'Mô phỏng'), nutVuot, trangThai));
  var tin = el('div', { class: 'the-tin' }, el('h3', null, 'Theo SGK'));
  var ul = el('ul'); MP.loi([6, 7, 9, 10, 12]).forEach(function (l) { ul.appendChild(el('li', null, l)); });
  tin.appendChild(ul); tin.appendChild(el('p', { style: { fontSize: '.8rem', color: 'var(--chu-phu)', margin: '6px 0 0' } }, MP.trang(MP.trangCanh([6, 7, 9, 10, 12]))));
  phai.appendChild(tin);

  // ---- hoạt cảnh vượt sông: hai đợt bè tiến sang, bị chặn đánh, lùi về bờ bắc
  var vuot = null, ten = [];
  var gTen = new T.CylinderGeometry(0.02, 0.02, 0.9, 4); gTen.rotateX(Math.PI / 2);
  for (var a = 0; a < 18; a++) { var m = new T.Mesh(gTen, new T.MeshBasicMaterial({ color: 0x5a1a10 })); m.visible = false; V.scene.add(m); ten.push(m); }
  nutVuot.addEventListener('click', function () {
    if (vuot) return;
    vuot = { t: 0, su: {} }; nutVuot.disabled = true; V.bay([14, 9, 20], [2, 0.5, 2], 1200);
    MP.nen(['nuoc', 'gio', 'dam_dong']); MP.am('buoc_quan'); trangThai.textContent = 'Quân Tống xuống bè, tìm cách vượt sông…';
  });
  function mot(key, fn) { if (!vuot.su[key]) { vuot.su[key] = 1; fn(); } }
  V.moi(function (dt, t) {
    texNuoc.offset.x -= dt * 0.12;
    co.forEach(function (la, k) { la.rotation.y = Math.sin(t * 2 + k) * 0.18; });
    if (!vuot) return;
    vuot.t += dt;
    var T1 = vuot.t;
    be.forEach(function (b, k) {
      var dot = k % 2, t0 = dot * 6.5, u = T1 - t0, z = b.zBo;
      if (u > 0 && u < 6.2) {
        var di = MP.ease(u / 2.6), lui = MP.ease((u - 3.4) / 2.2);
        z = b.zBo + (zc(b.x0) + RIVER / 2 - 1.2 - b.zBo) * di * (1 - lui);
        b.rotation.y = Math.sin(u * 3 + k) * 0.05;
      }
      b.position.z = z; b.position.y = 0.02 + Math.sin(T1 * 2.4 + k) * 0.03;
    });
    // tên bắn từ phòng tuyến
    ten.forEach(function (m, k) {
      var dot = k % 2, u = T1 - dot * 6.5 - 2.4 - (k % 9) * 0.12, b = be[(k % 3) * 2 + dot];
      if (u > 0 && u < 0.6) {
        var s0 = new T.Vector3(b.x0 + ((k * 7) % 5 - 2) * 0.5, HD + 0.6, zc(b.x0) + DZ - 0.8), s1 = new T.Vector3(b.position.x + (rnd() - 0.5), 0.5, b.position.z);
        m.visible = true; m.position.lerpVectors(s0, s1, u / 0.6); m.position.y += Math.sin(u / 0.6 * Math.PI) * 1.4; m.lookAt(s1);
      } else m.visible = false;
    });
    mot('a1', function () { MP.am('mai_cheo'); });
    if (T1 > 1.6) mot('a2', function () { MP.am('trong', { n: 3 }); trangThai.textContent = 'Quân ta trên phòng tuyến chặn đánh!'; });
    if (T1 > 2.5) mot('a3', function () { MP.am('vut'); });
    if (T1 > 3.0) mot('a4', function () { MP.am('te_nuoc'); });
    if (T1 > 3.6) mot('a5', function () { MP.am('buoc_quan'); trangThai.textContent = 'Quân Tống bị đẩy lùi về bờ bắc.'; });
    if (T1 > 6.5) mot('b1', function () { MP.am('mai_cheo'); trangThai.textContent = 'Quân Tống lại tìm cách vượt sông…'; });
    if (T1 > 8.1) mot('b2', function () { MP.am('trong', { n: 3 }); });
    if (T1 > 9.0) mot('b3', function () { MP.am('vut'); });
    if (T1 > 9.5) mot('b4', function () { MP.am('te_nuoc'); });
    if (T1 > 10.1) mot('b5', function () { MP.am('buoc_quan'); });
    if (T1 > 12.8) {
      vuot = null; nutVuot.disabled = false; MP.nen(['nuoc', 'gio']); MP.am('mo_pha');
      trangThai.textContent = 'Nhiều lần vượt sông đều bị đẩy lùi.';
      V.bang('Quân Tống bị chặn đứng trước phòng tuyến sông Như Nguyệt', true); setTimeout(function () { V.bang('', false); }, 4000);
    }
  });
});
