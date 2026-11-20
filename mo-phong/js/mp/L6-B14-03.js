/* L6-B14-03 · Bí ẩn thành Cổ Loa – mô hình 3D xoay 360 độ.
   Hình dáng ba vòng thành, vị trí cổng, ao hồ, sông lấy từ sơ đồ vẽ lại theo Hình 3 SGK LSĐL 6 tr. 62 (pipeline/maps/specs/co-loa.json).
   Kịch bản chỉ nêu: xoáy trôn ốc, ba vòng khép kín (ngoại – trung – nội), tổng chiều dài 16 000 m, nhiều cổng, sông – ao hồ – đầm lầy
   xen giữa và bao quanh. Không có số đo chiều cao/bề rộng nên mô hình không ghi số đo nào khác; độ cao được phóng đại để dễ quan sát. */
MP.onReady(function () {
  var root = MP.khung(), el = MP.el, BC = window.BaChieu, S = window.MP_BANDO['co-loa'];
  var luoi = el('div', { class: 'luoi-2' }), trai = el('div'), phai = el('div', { class: 'bang-dk' });
  luoi.appendChild(trai); luoi.appendChild(phai); root.appendChild(luoi);
  MP.nen(['gio', 'chim', 'nuoc']);
  var V = BC.tao(trai, { nen: 0xdbe8ec, suongMu: [45, 110], camPos: [6, 10.5, 15.5], target: [0, 0, 0.5], minDist: 6, maxDist: 60, nangPos: [14, 24, 12], moTa: 'Mô hình 3D thành Cổ Loa với ba vòng thành. Kéo để xoay, cuộn hoặc chụm để phóng to.' });
  if (!V) return;
  var T = V.T, SC = 0.03, CX = 668, CZ = 581, rnd = BC.rngSo(11);
  function P(p) { return [(p[0] - CX) * SC, (p[1] - CZ) * SC]; }

  var dat = new T.Mesh(new T.CircleGeometry(60, 64), new T.MeshStandardMaterial({ color: 0x9fb273, roughness: 1 }));
  dat.rotation.x = -Math.PI / 2; V.scene.add(dat);
  // ruộng, bãi quanh thành (mảng màu nhẹ cho đỡ đơn điệu)
  for (var r = 0; r < 26; r++) {
    var m = new T.Mesh(new T.PlaneGeometry(1.5 + rnd() * 3, 1.5 + rnd() * 3), new T.MeshStandardMaterial({ color: BC.bienMau(0xa9b878, 0.1, rnd), roughness: 1 }));
    var ang = rnd() * Math.PI * 2, rr = 15 + rnd() * 20; m.rotation.x = -Math.PI / 2; m.rotation.z = rnd() * 3; m.position.set(Math.cos(ang) * rr, 0.005, Math.sin(ang) * rr); V.scene.add(m);
  }
  var NUOC = new T.MeshStandardMaterial({ color: 0x6aa6c2, roughness: 0.3, metalness: 0.05, polygonOffset: true, polygonOffsetFactor: -1 });

  // ---- vòng thành
  var cong = (S.dia_danh || []).filter(function (d) { return /^Cửa /.test(d.ten); }).map(function (d) { return { ten: d.ten, p: P(d.vi_tri) }; });
  var CAU_HINH = { ngoai: { h: 1.05, bw: 1.0, tw: 0.42, ten: 'Thành ngoại' }, trung: { h: 0.92, bw: 0.92, tw: 0.38, ten: 'Thành trung' }, noi: { h: 0.75, bw: 0.75, tw: 0.32, ten: 'Thành nội' } };
  var vong = {};
  ['ngoai', 'trung', 'noi'].forEach(function (id) {
    var pts = S.doi_tuong[id].diem.slice(0, -1).map(P);
    vong[id] = { pts: BC.lamMuot(pts, 8, true), cfg: CAU_HINH[id], gap: {} };
  });
  cong.forEach(function (c) {   // gán mỗi cổng vào vòng thành gần nhất
    var best = null;
    Object.keys(vong).forEach(function (id) { vong[id].pts.forEach(function (p, i) { var d = Math.hypot(p[0] - c.p[0], p[1] - c.p[1]); if (!best || d < best.d) best = { id: id, i: i, d: d }; }); });
    var v = vong[best.id]; c.vong = best.id; c.i = best.i; c.pos = v.pts[best.i];
    v.pts.forEach(function (p, i) { if (Math.hypot(p[0] - c.pos[0], p[1] - c.pos[1]) < 0.5) v.gap[i] = true; });
  });
  function dienTich(pts) { var a = 0; for (var i = 0; i < pts.length; i++) { var p = pts[i], q = pts[(i + 1) % pts.length]; a += p[0] * q[1] - q[0] * p[1]; } return a / 2; }
  function tuong(v) {
    var pts = v.pts, n = pts.length, c = v.cfg, sg = dienTich(pts) > 0 ? 1 : -1, pos = [], col = [], i;
    var cDat = new T.Color(0x9b7a52), cCo = new T.Color(0x75944a), sec = [];
    for (i = 0; i < n; i++) {
      var a = pts[(i - 1 + n) % n], b = pts[(i + 1) % n], tx = b[0] - a[0], tz = b[1] - a[1], l = Math.hypot(tx, tz) || 1, nx = tz / l * sg, nz = -tx / l * sg;
      var p = pts[i];
      sec.push([[p[0] + nx * c.bw / 2, 0, p[1] + nz * c.bw / 2], [p[0] + nx * c.tw / 2, c.h, p[1] + nz * c.tw / 2], [p[0] - nx * c.tw / 2, c.h, p[1] - nz * c.tw / 2], [p[0] - nx * c.bw / 2, 0, p[1] - nz * c.bw / 2]]);
    }
    function quad(A, B, C, D, cl) { [A, B, C, A, C, D].forEach(function (q) { pos.push(q[0], q[1], q[2]); col.push(cl.r, cl.g, cl.b); }); }
    function nap(s, cl) { quad(s[0], s[1], s[2], s[3], cl); }
    for (i = 0; i < n; i++) {
      var j = (i + 1) % n;
      if (v.gap[i] || v.gap[j]) continue;
      var A = sec[i], B = sec[j];
      quad(A[0], B[0], B[1], A[1], cDat); quad(A[1], B[1], B[2], A[2], cCo); quad(A[2], B[2], B[3], A[3], cDat);
      if (v.gap[(i - 1 + n) % n]) nap(A, cDat);
      if (v.gap[(j + 1) % n]) nap(B, cDat);
    }
    var g = new T.BufferGeometry(); g.setAttribute('position', new T.Float32BufferAttribute(pos, 3)); g.setAttribute('color', new T.Float32BufferAttribute(col, 3)); g.computeVertexNormals();
    var mesh = new T.Mesh(g, new T.MeshStandardMaterial({ vertexColors: true, roughness: 0.95, side: T.DoubleSide }));
    // hào nước bao ngoài vòng thành (ngắt ở chỗ có cổng)
    var hp = [], d0 = c.bw / 2 + 0.55, w = 0.55;
    for (i = 0; i < n; i++) {
      var j2 = (i + 1) % n; if (v.gap[i] || v.gap[j2]) continue;
      var s0 = sec[i][0], s1 = sec[j2][0], k0 = [(s0[0] - pts[i][0]), (s0[2] - pts[i][1])], k1 = [(s1[0] - pts[j2][0]), (s1[2] - pts[j2][1])];
      var l0 = Math.hypot(k0[0], k0[1]), l1 = Math.hypot(k1[0], k1[1]);
      var o0 = [pts[i][0] + k0[0] / l0 * d0, pts[i][1] + k0[1] / l0 * d0], o1 = [pts[j2][0] + k1[0] / l1 * d0, pts[j2][1] + k1[1] / l1 * d0];
      var e0 = [pts[i][0] + k0[0] / l0 * (d0 + w), pts[i][1] + k0[1] / l0 * (d0 + w)], e1 = [pts[j2][0] + k1[0] / l1 * (d0 + w), pts[j2][1] + k1[1] / l1 * (d0 + w)];
      [o0, o1, e1, o0, e1, e0].forEach(function (q) { hp.push(q[0], 0.025, q[1]); });
    }
    var gh = new T.BufferGeometry(); gh.setAttribute('position', new T.Float32BufferAttribute(hp, 3)); gh.computeVertexNormals();
    var hao = new T.Mesh(gh, NUOC); hao.material.side = T.DoubleSide;
    V.scene.add(mesh); V.scene.add(hao);
    v.mesh = mesh; v.hao = hao;
  }
  Object.keys(vong).forEach(function (id) { tuong(vong[id]); });

  // ---- ao hồ, sông Hoàng Giang
  var nuocNhom = new T.Group(); V.scene.add(nuocNhom);
  (S.ho || []).forEach(function (h) {
    var sh = new T.Shape(BC.lamMuot(h.diem.map(P), 6, true).map(function (p) { return new T.Vector2(p[0], -p[1]); }));
    var m = new T.Mesh(new T.ShapeGeometry(sh), NUOC); m.rotation.x = -Math.PI / 2; m.position.y = 0.02; nuocNhom.add(m);
  });
  (S.song || []).forEach(function (s) { var m = new T.Mesh(BC.dai(BC.lamMuot(s.diem.map(P), 8, false), 0.7, 0.02, false), NUOC); m.material.side = T.DoubleSide; nuocNhom.add(m); });
  Object.keys(vong).forEach(function (id) { nuocNhom.add(vong[id].hao); });

  // ---- cổng thành: hai trụ gỗ và xà ngang
  var GO = new T.MeshStandardMaterial({ color: 0x6b4a2e, roughness: 0.8 }), congNhom = new T.Group(); V.scene.add(congNhom);
  cong.forEach(function (c) {
    var v = vong[c.vong], pts = v.pts, n = pts.length, a = pts[(c.i - 1 + n) % n], b = pts[(c.i + 1) % n], gocQ = Math.atan2(b[1] - a[1], b[0] - a[0]);
    var g = new T.Group(); g.position.set(c.pos[0], 0, c.pos[1]); g.rotation.y = -gocQ;
    [-0.42, 0.42].forEach(function (dx) { var tr = new T.Mesh(new T.BoxGeometry(0.08, v.cfg.h * 0.95, 0.08), GO); tr.position.set(dx, v.cfg.h * 0.47, 0); g.add(tr); });
    var xa = new T.Mesh(new T.BoxGeometry(0.98, 0.07, 0.1), GO); xa.position.y = v.cfg.h * 0.9; g.add(xa);
    congNhom.add(g); c.nhom = g;
  });

  // ---- khu thành nội: đền An Dương Vương và Giếng Ngọc (hiện nay)
  var den = new T.Group(), pd = P([722, 600]); den.position.set(pd[0], 0, pd[1]);
  var nen = new T.Mesh(new T.BoxGeometry(1.0, 0.1, 0.75), new T.MeshStandardMaterial({ color: 0xbfb39b })); nen.position.y = 0.05; den.add(nen);
  var than = new T.Mesh(new T.BoxGeometry(0.72, 0.34, 0.5), new T.MeshStandardMaterial({ color: 0xa8432c, roughness: 0.7 })); than.position.y = 0.27; den.add(than);
  var mai = new T.Mesh(new T.ConeGeometry(0.66, 0.36, 4), new T.MeshStandardMaterial({ color: 0x4d3b33, roughness: 0.8 })); mai.position.y = 0.62; mai.rotation.y = Math.PI / 4; mai.scale.z = 0.78; den.add(mai);
  V.scene.add(den);
  var pg = P([722, 642]), gieng = new T.Group(); gieng.position.set(pg[0], 0, pg[1]);
  var thanhGieng = new T.Mesh(new T.CylinderGeometry(0.2, 0.22, 0.14, 24, 1, true), new T.MeshStandardMaterial({ color: 0x8f8a80, side: T.DoubleSide })); thanhGieng.position.y = 0.07; gieng.add(thanhGieng);
  var matGieng = new T.Mesh(new T.CircleGeometry(0.19, 24), NUOC); matGieng.rotation.x = -Math.PI / 2; matGieng.position.y = 0.08; gieng.add(matGieng);
  V.scene.add(gieng);
  // vài lùm cây trên đất (trang trí)
  var cay = new T.InstancedMesh(new T.ConeGeometry(0.35, 0.9, 7), new T.MeshStandardMaterial({ color: 0x4f7a3a, roughness: 1 }), 120), Mx = new T.Matrix4();
  for (var q = 0; q < 120; q++) { var aa = rnd() * Math.PI * 2, rq = 14.5 + rnd() * 16; var s2 = 0.7 + rnd() * 0.8; Mx.compose(new T.Vector3(Math.cos(aa) * rq, 0.45 * s2, Math.sin(aa) * rq), new T.Quaternion(), new T.Vector3(s2, s2, s2)); cay.setMatrixAt(q, Mx); }
  V.scene.add(cay);

  // ---- nhãn
  function ganNhat(v, p) { var b = v.pts[0], bd = 1e9; v.pts.forEach(function (q) { var d = Math.hypot(q[0] - p[0], q[1] - p[1]); if (d < bd) { bd = d; b = q; } }); return b; }
  var nhanVong = {};
  [['ngoai', S.doi_tuong.nhan_ngoai.vi_tri], ['trung', S.doi_tuong.nhan_trung.vi_tri], ['noi', [722, 556]]].forEach(function (x) {
    var v = vong[x[0]], q = ganNhat(v, P(x[1])); nhanVong[x[0]] = V.nhan(v.cfg.ten, new T.Vector3(q[0], v.cfg.h + 0.15, q[1]), 'cam');
  });
  var nhanCong = cong.map(function (c) { return V.nhan(c.ten, new T.Vector3(c.pos[0], vong[c.vong].cfg.h + 0.1, c.pos[1]), 'nho'); });
  V.nhan('Đền An Dương Vương', new T.Vector3(pd[0], 0.85, pd[1]), 'do');
  V.nhan('Giếng Ngọc', new T.Vector3(pg[0], 0.25, pg[1]), 'nuoc nho');
  var nhanNuoc = [];
  (S.ho || []).forEach(function (h) { if (h.ten) { var p = P(h.nhan || h.diem[0]); nhanNuoc.push(V.nhan(h.ten, new T.Vector3(p[0], 0.15, p[1]), 'nuoc nho')); } });
  (S.song || []).forEach(function (s) { if (s.ten) { var p = P(s.nhan); nhanNuoc.push(V.nhan(s.ten, new T.Vector3(p[0], 0.15, p[1]), 'nuoc nho')); } });
  nhanCong.forEach(function (L) { L.hien = false; });
  var vh = vong.ngoai.hao.geometry.attributes.position; nhanNuoc.push(V.nhan('Hào nước', new T.Vector3(vh.getX(0), 0.15, vh.getZ(0)), 'nuoc nho'));

  // ---- bảng điều khiển
  function hop(nhan, on, fn) { var c = el('input', { type: 'checkbox' }); c.checked = on; c.addEventListener('change', function () { fn(c.checked); MP.am('click'); }); return { w: el('label', { class: 'hop-chon' }, c, nhan), c: c }; }
  var hops = {};
  ['ngoai', 'trung', 'noi'].forEach(function (id) {
    hops[id] = hop(vong[id].cfg.ten, true, function (on) { vong[id].mesh.visible = on; vong[id].hao.visible = on && hops.nuoc.c.checked; nhanVong[id].hien = on; cong.forEach(function (c, i) { if (c.vong === id) { c.nhom.visible = on; nhanCong[i].hien = on && hops.cong.c.checked; } }); });
  });
  hops.nuoc = hop('Sông, ao hồ, hào nước', true, function (on) { nuocNhom.visible = on; Object.keys(vong).forEach(function (id) { vong[id].hao.visible = on && vong[id].mesh.visible; }); nhanNuoc.forEach(function (L) { L.hien = on; }); if (on) MP.nen(['gio', 'chim', 'nuoc']); else MP.nen(['gio', 'chim']); });
  hops.cong = hop('Tên các cổng thành', false, function (on) { nhanCong.forEach(function (L, i) { L.hien = on && vong[cong[i].vong].mesh.visible; }); });
  var nutDung = el('button', { type: 'button', class: 'nut chinh' }, 'Dựng từng vòng thành');
  var nutTren = el('button', { type: 'button', class: 'nut' }, 'Nhìn từ trên xuống');
  var nutBay = el('button', { type: 'button', class: 'nut', 'aria-pressed': 'false' }, 'Bay quanh thành');
  var nutLai = el('button', { type: 'button', class: 'nut' }, 'Đặt lại góc nhìn');
  phai.appendChild(el('div', { class: 'the-tin' }, el('h3', null, 'Bật/tắt'), el('div', { style: { display: 'grid', gap: '6px' } }, hops.ngoai.w, hops.trung.w, hops.noi.w, hops.nuoc.w, hops.cong.w),
    el('div', { class: 'hang-nut', style: { marginTop: '10px' } }, nutDung, nutTren, nutBay, nutLai)));
  var tin = el('div', { class: 'the-tin' }, el('h3', null, 'Theo SGK'));
  var ul = el('ul'); MP.loi([4, 5, 7]).concat([MP.canh(8).loi[0]], MP.loi([9, 10])).forEach(function (l) { if (l) ul.appendChild(el('li', null, l)); });
  tin.appendChild(ul); tin.appendChild(el('p', { style: { fontSize: '.8rem', color: 'var(--chu-phu)', margin: '6px 0 0' } }, MP.trang(MP.trangCanh([4, 5, 7, 8, 9, 10]))));
  phai.appendChild(tin);

  nutTren.addEventListener('click', function () { V.controls.autoRotate = false; nutBay.setAttribute('aria-pressed', 'false'); V.bay([0.01, 22, 0.6], [0, 0, 0.5], 1400); MP.am('lat_trang'); V.bang('Hình xoáy trôn ốc – ba vòng khép kín', true); setTimeout(function () { V.bang('', false); }, 3200); });
  nutBay.addEventListener('click', function () { var on = !V.controls.autoRotate; V.controls.autoRotate = on; V.controls.autoRotateSpeed = 1.2; nutBay.setAttribute('aria-pressed', on ? 'true' : 'false'); MP.am('click'); if (on) V.bay([12, 9, 16], [0, 0, 0.5], 1000); });
  nutLai.addEventListener('click', function () { V.bay([6, 10.5, 15.5], [0, 0, 0.5], 1000); MP.am('click'); });
  var dung = null;
  nutDung.addEventListener('click', function () {
    ['ngoai', 'trung', 'noi'].forEach(function (id) { hops[id].c.checked = true; hops[id].c.dispatchEvent(new Event('change')); vong[id].mesh.scale.y = 0.001; vong[id].hao.visible = false; });
    cong.forEach(function (c) { c.nhom.visible = false; });
    dung = { t: 0, buoc: -1 }; V.bay([9, 13, 20], [0, 0, 0.5], 1000); MP.am('click'); V.bang('', false);
  });
  var THU_TU = ['ngoai', 'trung', 'noi'];
  V.moi(function (dt) {
    if (!dung) return;
    dung.t += dt;
    var b = Math.floor(dung.t / 1.6);
    THU_TU.forEach(function (id, i) {
      var k = MP.ease((dung.t - i * 1.6) / 1.2);
      vong[id].mesh.scale.y = Math.max(0.001, k);
      if (k >= 1) { vong[id].hao.visible = hops.nuoc.c.checked; cong.forEach(function (c) { if (c.vong === id) c.nhom.visible = true; }); }
    });
    if (b !== dung.buoc && b < 3) { dung.buoc = b; MP.am('dat'); V.bang(vong[THU_TU[b]].cfg.ten, true); }
    if (dung.t > 4.9 && !dung.xong1) { dung.xong1 = true; V.bang('Hình xoáy trôn ốc – ba vòng khép kín', true); MP.am('mo_pha'); }
    if (dung.t > 7.2) { dung = null; V.bang('Tổng chiều dài các vòng thành: 16 000 m', true); MP.am('chuong'); setTimeout(function () { V.bang('', false); }, 4000); }
  });
});
