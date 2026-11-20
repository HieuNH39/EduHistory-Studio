/* L6-B18-03 · Bãi cọc Bạch Đằng 3D – thuỷ triều lên xuống (Bạch Đằng năm 938).
   Dữ kiện (SGK LSĐL 6 tr. 83–85, qua kịch bản): mực nước cửa sông lúc triều cao nhất và thấp nhất chênh 2 – 3 m; cọc lớn vạt nhọn,
   đầu bịt sắt, đóng ngầm trước cửa biển; thuyền giặc theo nước triều lên vào trong hàng cọc; triều rút, cọc nhô lên, thuyền giặc
   không còn đường thoát; hai bên bờ quân mai phục, thuyền chiến ta nấp sẵn. Mô hình minh hoạ, giản lược, không theo tỉ lệ. */
MP.onReady(function () {
  var root = MP.khung(), el = MP.el, BC = window.BaChieu, H = window.MH;
  var bc = H.boCuc(root);
  MP.nen(['song_bien', 'gio']);
  var V = BC.tao(bc.trai, { nen: 0xbfd8e2, suongMu: [60, 150], camPos: [20, 17, 21], target: [2, 1, 0], minDist: 10, maxDist: 90,
    nangPos: [20, 30, 12], nangManh: 2.4, hemi: 1.15, troi: 0xeaf6ff, dat: 0x6d6a4a,
    moTa: 'Mô hình 3D bãi cọc Bạch Đằng. Kéo để xoay, cuộn để phóng to. Dùng thanh Mực nước triều để thấy cọc chìm, cọc nhô.' });
  if (!V) return;
  var T = V.T, rnd = BC.rngSo(938);
  var THAP = 0.4, CAO = 3.0, DINH_COC = 2.2;   // mực nước thấp – cao (chênh 2,6 m), đỉnh cọc

  // ---- lòng sông, hai bờ, cây cỏ
  var day = new T.Mesh(new T.PlaneGeometry(140, 40, 1, 1), new T.MeshStandardMaterial({ color: 0x7a6748, roughness: 1 }));
  day.rotation.x = -Math.PI / 2; day.position.y = -0.3; V.scene.add(day);
  function bo(z, dau) {
    var g = new T.BoxGeometry(140, 4.2, 22), m = new T.Mesh(g, new T.MeshStandardMaterial({ color: 0x8a7a50, roughness: 1 }));
    m.position.set(0, 1.6, z + dau * 11); V.scene.add(m);
    var co = new T.Mesh(new T.PlaneGeometry(140, 22), new T.MeshStandardMaterial({ color: 0x5f8a45, roughness: 1 }));
    co.rotation.x = -Math.PI / 2; co.position.set(0, 3.72, z + dau * 11); V.scene.add(co);
    for (var i = 0; i < (dau > 0 ? 40 : 70); i++) {   // lau sậy, cây (bờ gần máy quay thưa hơn)
      var x = -66 + rnd() * 132, zz = z + dau * ((dau > 0 ? 7 : 1.2) + rnd() * 14);
      if (rnd() < 0.55) {
        var lau = new T.Mesh(new T.ConeGeometry(0.35, 1.6 + rnd(), 5), new T.MeshStandardMaterial({ color: rnd() < .5 ? 0x7d9a4a : 0x93a85a, roughness: 1 }));
        lau.position.set(x, 4.4, zz); V.scene.add(lau);
      } else {
        var than = new T.Mesh(new T.CylinderGeometry(0.15, 0.22, 2.2, 6), new T.MeshStandardMaterial({ color: 0x6b4f33 }));
        var tan = new T.Mesh(new T.SphereGeometry(1.1 + rnd() * .6, 10, 8), new T.MeshStandardMaterial({ color: rnd() < .5 ? 0x3f6b35 : 0x4d7a3c, roughness: 1 }));
        than.position.set(x, 4.8, zz); tan.position.set(x, 6.2, zz); V.scene.add(than); V.scene.add(tan);
      }
    }
  }
  bo(-10, -1); bo(10, 1);

  // ---- bãi cọc: hàng cọc gỗ vạt nhọn, đầu bịt sắt, nghiêng về phía biển
  var coc = [], xs = [-3, -1.2, 0.6, 2.4, 4.2];
  xs.forEach(function (x, r) { for (var z = -8.6; z <= 8.6; z += 1.15) coc.push([x + (rnd() - .5) * .4, z + (r % 2) * .55 + (rnd() - .5) * .25]); });
  var gCoc = new T.CylinderGeometry(0.2, 0.26, DINH_COC + 0.3, 7); gCoc.translate(0, (DINH_COC + 0.3) / 2 - 0.3, 0);
  var gMui = new T.ConeGeometry(0.21, 0.5, 7); gMui.translate(0, DINH_COC + 0.2, 0);
  var imCoc = new T.InstancedMesh(gCoc, new T.MeshStandardMaterial({ color: 0x5e3d22, roughness: .95 }), coc.length);
  var imMui = new T.InstancedMesh(gMui, new T.MeshStandardMaterial({ color: 0x3a3d42, roughness: .45, metalness: .6 }), coc.length);
  var M = new T.Matrix4(), Q = new T.Quaternion(), E = new T.Euler(), P = new T.Vector3(), S1 = new T.Vector3(1, 1, 1);
  coc.forEach(function (c, i) {
    E.set(0, 0, -0.32 + (rnd() - .5) * .06); Q.setFromEuler(E); P.set(c[0], 0, c[1]); M.compose(P, Q, S1);
    imCoc.setMatrixAt(i, M); imMui.setMatrixAt(i, M);
  });
  V.scene.add(imCoc); V.scene.add(imMui);

  // ---- mặt nước (trong suốt để thấy cọc ngầm)
  var nuoc = new T.Mesh(new T.PlaneGeometry(140, 20, 70, 10), new T.MeshStandardMaterial({ color: 0x2f7f9c, roughness: .2, metalness: .08, transparent: true, opacity: .5, depthWrite: false }));
  nuoc.rotation.x = -Math.PI / 2; V.scene.add(nuoc);
  var posN = nuoc.geometry.attributes.position, goc = posN.array.slice();

  // ---- cột đo mực nước trên bờ
  var cot = new T.Group(), cx = 9, cz = -9.4;
  var than = new T.Mesh(new T.BoxGeometry(0.3, 4.4, 0.3), new T.MeshStandardMaterial({ color: 0xf1ead8 })); than.position.set(cx, 2, cz); cot.add(than);
  for (var m = 0; m <= 3; m++) { var v = new T.Mesh(new T.BoxGeometry(0.5, 0.06, 0.34), new T.MeshBasicMaterial({ color: 0xb8261e })); v.position.set(cx, THAP + m * (CAO - THAP) / 2.6, cz); cot.add(v); }
  V.scene.add(cot);

  // ---- thuyền
  function thuyen(mauThan, mauBuom, co) {
    var g = new T.Group();
    var s = new T.Shape(); s.moveTo(-1.8, 0); s.quadraticCurveTo(0, -0.75, 1.9, 0); s.lineTo(-1.8, 0);
    var hull = new T.Mesh(new T.ExtrudeGeometry(s, { depth: 1.0, bevelEnabled: false }), new T.MeshStandardMaterial({ color: mauThan, roughness: .8 }));
    hull.position.set(0, 0.25, -0.5); g.add(hull);
    var san = new T.Mesh(new T.BoxGeometry(3.4, 0.12, 0.95), new T.MeshStandardMaterial({ color: 0x9b7a52 })); san.position.y = 0.26; g.add(san);
    var cotB = new T.Mesh(new T.CylinderGeometry(0.05, 0.06, 2.4, 6), new T.MeshStandardMaterial({ color: 0x5b4330 })); cotB.position.set(0, 1.45, 0); g.add(cotB);
    var buom = new T.Mesh(new T.PlaneGeometry(1.4, 1.6), new T.MeshStandardMaterial({ color: mauBuom, side: T.DoubleSide, roughness: 1 })); buom.position.set(0.05, 1.6, 0); buom.rotation.y = Math.PI / 2; g.add(buom);
    if (co) { var c = new T.Mesh(new T.PlaneGeometry(0.5, 0.32), new T.MeshBasicMaterial({ color: co, side: T.DoubleSide })); c.position.set(0.3, 2.7, 0); c.rotation.y = Math.PI / 2; g.add(c); }
    V.scene.add(g); return g;
  }
  var dich = [], ta = [];
  for (var i = 0; i < 6; i++) { var b = thuyen(0x2e3e73, 0xd9d2c0, 0x1a2342); b.userData = { x0: 30 + (i % 3) * 4.5, z: -5.5 + (i % 3) * 5.2 + (i > 2 ? 1.6 : 0), lech: i * 0.9 }; dich.push(b); }
  [[-14, -7.6], [-16, 7.6], [-12, 0]].forEach(function (p) { var b = thuyen(0x8a2a1e, 0xe8c38a, 0xd23a22); b.userData = { x: p[0], z: p[1] }; ta.push(b); });
  // quân mai phục trên bờ
  var quan = new T.InstancedMesh(new T.ConeGeometry(0.28, 0.9, 6), new T.MeshStandardMaterial({ color: 0xb8261e, roughness: .9 }), 40);
  for (var q = 0; q < 40; q++) { P.set(-6 + rnd() * 16, 4.2, (q % 2 ? 1 : -1) * (11 + rnd() * 3)); M.compose(P, Q.identity(), S1); quan.setMatrixAt(q, M); }
  quan.visible = false; V.scene.add(quan);

  // nhãn
  V.nhan('Bãi cọc ngầm', new T.Vector3(0.6, DINH_COC + 0.4, 0), 'do');
  V.nhan('Phía cửa biển', new T.Vector3(34, 3.4, 0), 'nho');
  V.nhan('Thượng nguồn', new T.Vector3(-30, 3.4, 0), 'nho');
  V.nhan('Cột đo mực nước', new T.Vector3(cx, 4.5, cz), 'nho');
  var nDich = V.nhan('Thuyền giặc Nam Hán', function () { return dich[1].position.clone().add(new T.Vector3(0, 3.1, 0)); }, 'cham');
  var nTa = V.nhan('Thuyền chiến của ta', function () { return ta[2].position.clone().add(new T.Vector3(0, 3.1, 0)); }, 'cam');
  var nMp = V.nhan('Quân mai phục', new T.Vector3(1, 5.4, 12), 'cam'); nMp.hien = false;

  // ---- trạng thái
  var st = { muc: 0.85, mucDich: 0.85, tien: 0, tienDich: 0, phanCong: 0, pcDich: 0, macCoc: false };
  function docMuc(k) { return THAP + (CAO - THAP) * k; }

  // ---- bảng điều khiển
  var tin = null;
  var tMuc = H.truot('Mực nước triều', 0, 100, 1, 85, function (v) { return (docMuc(v / 100) - THAP).toFixed(1).replace('.', ',') + ' m'; },
    function (v) { st.mucDich = v / 100; });
  var nLen = H.nut('Triều lên: giặc tiến vào', true, function () { st.mucDich = 1; st.tienDich = 1; st.macCoc = false; tMuc.dat(100); MP.am('song_bien'); MP.am('mai_cheo');
    tin('Nước triều lên', ['Bãi cọc chìm dưới mặt nước nên thuyền giặc không nhìn thấy.', 'Thuyền giặc theo nước triều lên tiến vào trong hàng cọc.']); });
  var nRut = H.nut('Triều rút: cọc nhô lên', true, function () { st.mucDich = 0; st.macCoc = st.tien > 0.6; tMuc.dat(0); MP.am('nuoc');
    tin('Nước triều rút', ['Mực nước hạ xuống 2 – 3 m, cọc nhô lên.', st.tien > 0.6 ? 'Thuyền giặc mắc cọc, không còn đường thoát.' : 'Bấm “Triều lên” trước để đưa thuyền giặc vào bãi cọc.']); });
  var nPC = H.nut('Ta phản công', false, function () { st.pcDich = 1; MP.am('trong'); MP.am('dam_dong');
    tin('Phản công', ['Quân mai phục hai bên bờ và thuyền chiến của ta đồng loạt tiến ra đánh.', 'Chiến thắng Bạch Đằng năm 938 chấm dứt thời kì Bắc thuộc.']); });
  var nLai = H.nut('Đặt lại', false, function () { st.mucDich = .85; st.tienDich = 0; st.tien = 0; st.pcDich = 0; st.phanCong = 0; st.macCoc = false; tMuc.dat(85); V.bay([20, 17, 21], [2, 1, 0], 900); MP.am('click');
    tin('Bãi cọc Bạch Đằng', 'Kéo thanh “Mực nước triều” hoặc bấm các nút để xem kế hoạch của Ngô Quyền.'); });
  H.dieuKhien(bc.phai, 'Điều khiển', [tMuc.w, H.hangNut([nLen, nRut]), H.hangNut([nPC, nLai]),
    el('label', { class: 'hop-chon', style: { marginTop: '8px' } }, (function () { var c = el('input', { type: 'checkbox' }); c.addEventListener('change', function () { V.bay(c.checked ? [5, 2.4, 9.5] : [20, 17, 21], c.checked ? [0.6, 1.2, 0] : [2, 1, 0], 1200); MP.am('soi'); }); return c; })(), 'Nhìn sát mặt nước')]);
  tin = H.theTin(bc.phai);
  tin('Bãi cọc Bạch Đằng', 'Kéo thanh “Mực nước triều” hoặc bấm các nút để xem kế hoạch của Ngô Quyền.');
  H.theoSGK(bc.phai, [7, 8, 9]);

  // ---- vòng lặp
  V.moi(function (dt, t) {
    st.muc += (st.mucDich - st.muc) * Math.min(1, dt * 0.9);
    st.tien += (st.tienDich - st.tien) * Math.min(1, dt * 0.35);
    st.phanCong += (st.pcDich - st.phanCong) * Math.min(1, dt * 0.6);
    var y = docMuc(st.muc);
    nuoc.position.y = y;
    for (var i = 0; i < posN.count; i++) posN.setZ(i, goc[i * 3 + 2] + Math.sin(goc[i * 3] * .35 + t * 1.6) * .05 + Math.cos(goc[i * 3 + 1] * .5 + t) * .04);
    posN.needsUpdate = true;
    dich.forEach(function (b, k) {
      var u = b.userData, x = u.x0 + (-2.6 + (k % 3) * 1.6 - u.x0) * st.tien;
      var yB = y - 0.05, nghieng = 0;
      if (st.macCoc && Math.abs(x - 0.6) < 4.6) { yB = Math.max(y - 0.05, DINH_COC - 0.25); nghieng = MP.clamp((DINH_COC - y) / 1.4, 0, 1) * (k % 2 ? .28 : -.22); }
      b.position.set(x, yB + Math.sin(t * 1.3 + u.lech) * .05, u.z); b.rotation.set(nghieng, Math.PI, nghieng * .6);
    });
    ta.forEach(function (b, k) {
      var u = b.userData; b.position.set(u.x + st.phanCong * (10 + k * 2), docMuc(st.muc) - 0.05 + Math.sin(t * 1.5 + k) * .05, u.z * (1 - .45 * st.phanCong));
    });
    quan.visible = st.phanCong > 0.05; nMp.hien = quan.visible;
    nDich.hien = true; nTa.hien = true;
  });
});
