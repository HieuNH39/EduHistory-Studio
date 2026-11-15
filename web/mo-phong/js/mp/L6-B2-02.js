/* L6-B2-02 · Trống đồng Ngọc Lũ 3D – tư liệu hiện vật.
   Dữ kiện (SGK LSĐL 6 tr. 11, 63–64, qua kịch bản): trống đồng Ngọc Lũ là hiện vật tiêu biểu của văn minh Việt cổ, trưng bày tại
   Bảo tàng Lịch sử quốc gia, được coi là đẹp nhất trong các trống đồng Đông Sơn; hoạ tiết mặt trống có mái nhà cong, hình thuyền,
   người giã gạo, người múa hát… giúp hình dung nơi ở, việc làm, phương tiện đi lại và lễ hội của người Việt cổ.
   Mô hình minh hoạ: hoa văn vẽ giản lược theo kiểu trống Đông Sơn, không phải bản sao chính xác. */
MP.onReady(function () {
  var root = MP.khung(), el = MP.el, BC = window.BaChieu, H = window.MH;
  var bc = H.boCuc(root);
  MP.nen(['nen_em']);
  var V = BC.tao(bc.trai, { nen: 0x1d2b3a, camPos: [0, 9.5, 8.5], target: [0, 1.6, 0], minDist: 3.2, maxDist: 22, maxPolar: Math.PI * 0.62,
    nangPos: [6, 12, 6], nangManh: 2.8, hemi: 1.05, troi: 0xfff2dc, dat: 0x3a2a1a, phoiSang: 1.12,
    moTa: 'Mô hình 3D trống đồng kiểu Đông Sơn. Kéo để xoay, cuộn để phóng to, chạm vào mặt trống để xem hoạ tiết.' });
  if (!V) return;
  var T = V.T, PI = Math.PI, TAU = PI * 2;
  var DONG = '#c49556', DONG_T = '#5b3a17', DONG_S = '#e7c48a';

  // ---------- vẽ hoa văn mặt trống
  function hinhNguoi(c, s, kieu) {          // người đội mũ lông chim; kieu: 'mua' | 'gia'
    c.beginPath(); c.arc(0, -s * 1.15, s * .22, 0, TAU); c.fill();                       // đầu
    c.beginPath(); c.moveTo(-s * .05, -s * 1.3); c.quadraticCurveTo(-s * .9, -s * 2.4, -s * 1.3, -s * 1.5); c.quadraticCurveTo(-s * .5, -s * 1.7, -s * .1, -s * 1.1); c.fill();   // mũ lông chim
    c.beginPath(); c.moveTo(-s * .25, -s * .95); c.lineTo(s * .25, -s * .95); c.lineTo(s * .35, -s * .1); c.lineTo(-s * .35, -s * .1); c.closePath(); c.fill();   // thân, váy
    c.lineWidth = s * .12; c.beginPath(); c.moveTo(-s * .15, -s * .1); c.lineTo(-s * .3, s * .45); c.moveTo(s * .15, -s * .1); c.lineTo(s * .32, s * .45); c.stroke();   // chân
    c.beginPath();
    if (kieu === 'gia') { c.moveTo(s * .2, -s * .8); c.lineTo(s * .7, -s * 1.45); }   // tay cầm chày
    else { c.moveTo(-s * .2, -s * .75); c.lineTo(-s * .75, -s * .95); c.moveTo(s * .2, -s * .75); c.lineTo(s * .7, -s * 1.2); }
    c.stroke();
  }
  function giaGao(c, s) {
    c.save(); c.translate(-s * .8, 0); hinhNguoi(c, s, 'gia'); c.restore();
    c.save(); c.translate(s * .8, 0); c.scale(-1, 1); hinhNguoi(c, s, 'gia'); c.restore();
    c.fillRect(-s * .28, -s * .32, s * .56, s * .4);   // cối
    c.lineWidth = s * .1; c.beginPath(); c.moveTo(0, -s * 1.5); c.lineTo(0, -s * .3); c.stroke();   // chày
  }
  function nhaSan(c, s) {
    c.lineWidth = s * .1;
    for (var k = -2; k <= 2; k++) { c.beginPath(); c.moveTo(k * s * .5, 0); c.lineTo(k * s * .5, -s * .9); c.stroke(); }   // cột sàn
    c.fillRect(-s * 1.2, -s * 1.05, s * 2.4, s * .16);   // sàn
    c.beginPath(); c.moveTo(-s * 1.9, -s * 2.4); c.quadraticCurveTo(-s * 1.1, -s * 1.3, -s * .9, -s * 1.05); c.lineTo(s * .9, -s * 1.05);
    c.quadraticCurveTo(s * 1.1, -s * 1.3, s * 1.9, -s * 2.4); c.quadraticCurveTo(0, -s * 1.6, -s * 1.9, -s * 2.4); c.fill();   // mái cong hình thuyền
    c.beginPath(); c.arc(-s * 1.9, -s * 2.5, s * .14, 0, TAU); c.arc(s * 1.9, -s * 2.5, s * .14, 0, TAU); c.fill();             // chim trên đầu mái
  }
  function chimLac(c, s) {
    c.beginPath(); c.moveTo(s * 1.6, 0); c.lineTo(s * .55, -s * .08); c.quadraticCurveTo(s * .2, -s * .2, -s * .1, -s * .12);     // mỏ dài, đầu
    c.quadraticCurveTo(-s * .6, -s * .9, -s * 1.1, -s * .7); c.quadraticCurveTo(-s * .7, -s * .2, -s * .9, 0);                  // cánh
    c.lineTo(-s * 1.6, s * .35); c.lineTo(-s * 1.2, -s * .02); c.quadraticCurveTo(-s * .2, s * .25, s * .55, s * .06); c.closePath(); c.fill();
    c.beginPath(); c.moveTo(-s * .2, s * .05); c.lineTo(-s * .45, s * .5); c.moveTo(0, s * .05); c.lineTo(-s * .15, s * .5); c.stroke();   // chân dài
  }
  function vongTiepTuyen(c, cx, cy, r, n, rr) {
    for (var i = 0; i < n; i++) { var a = TAU * i / n, x = cx + r * Math.cos(a), y = cy + r * Math.sin(a);
      c.beginPath(); c.arc(x, y, rr, 0, TAU); c.stroke(); c.beginPath(); c.arc(x, y, rr * .3, 0, TAU); c.fill();
      var a2 = TAU * (i + 1) / n; c.beginPath(); c.moveTo(x + rr * Math.cos(a + 1.4), y + rr * Math.sin(a + 1.4)); c.lineTo(cx + r * Math.cos(a2) + rr * Math.cos(a2 - 1.7), cy + r * Math.sin(a2) + rr * Math.sin(a2 - 1.7)); c.stroke(); }
  }
  function vach(c, cx, cy, r0, r1, n) { c.beginPath(); for (var i = 0; i < n; i++) { var a = TAU * i / n; c.moveTo(cx + r0 * Math.cos(a), cy + r0 * Math.sin(a)); c.lineTo(cx + r1 * Math.cos(a), cy + r1 * Math.sin(a)); } c.stroke(); }
  function vong(c, cx, cy, r) { c.beginPath(); c.arc(cx, cy, r, 0, TAU); c.stroke(); }
  function quanhVong(c, cx, cy, r, a, ve) { c.save(); c.translate(cx + r * Math.cos(a), cy + r * Math.sin(a)); c.rotate(a + PI / 2); ve(); c.restore(); }

  var VUNG = [ // [r0, r1, tên, mô tả] – dùng khi chạm vào mặt trống
    [0, .2, 'Ngôi sao giữa mặt trống', 'Ở chính giữa mặt trống là ngôi sao nhiều cánh, các vành hoa văn toả ra xung quanh.'],
    [.34, .52, 'Vành người và nhà', 'Vành này có mái nhà cong, người giã gạo, người múa hát: giúp hình dung nơi ở, việc làm và lễ hội của người Việt cổ.'],
    [.62, .78, 'Vành chim bay', 'Những con chim mỏ dài bay quanh mặt trống, nối tiếp nhau thành vòng.'],
    [0, 1, 'Các vành hoa văn', 'Giữa các vành hình người, chim là các vành hoa văn hình học: vạch ngắn, vòng tròn tiếp tuyến.']];
  var vanMat = H.vanCanvas(2048, 2048, function (c, W) {
    var cx = W / 2, cy = W / 2, R = W / 2 - 4;
    var g = c.createRadialGradient(cx - R * .2, cy - R * .25, R * .1, cx, cy, R); g.addColorStop(0, '#d9ad6e'); g.addColorStop(1, '#a7763e');
    c.fillStyle = g; c.beginPath(); c.arc(cx, cy, R, 0, TAU); c.fill();
    c.strokeStyle = DONG_T; c.fillStyle = DONG_T; c.lineWidth = 3;
    [.2, .24, .3, .34, .52, .56, .62, .78, .82, .88, .92].forEach(function (k) { vong(c, cx, cy, R * k); });
    vach(c, cx, cy, R * .2, R * .24, 120); vach(c, cx, cy, R * .3, R * .34, 160); vach(c, cx, cy, R * .52, R * .56, 220); vach(c, cx, cy, R * .78, R * .82, 300);
    vongTiepTuyen(c, cx, cy, R * .27, 28, R * .022); vongTiepTuyen(c, cx, cy, R * .59, 54, R * .022); vongTiepTuyen(c, cx, cy, R * .85, 80, R * .02);
    c.lineWidth = 2; c.beginPath(); for (var z = 0; z <= 240; z++) { var a = TAU * z / 240, rr = R * (z % 2 ? .9 : .915); c.lineTo(cx + rr * Math.cos(a), cy + rr * Math.sin(a)); } c.stroke();
    // ngôi sao 14 cánh và hoạ tiết lông công giữa các cánh
    c.fillStyle = DONG_S; c.beginPath();
    for (var i = 0; i < 28; i++) { var a2 = PI * i / 14 - PI / 2, r2 = R * (i % 2 ? .05 : .2); c.lineTo(cx + r2 * Math.cos(a2), cy + r2 * Math.sin(a2)); }
    c.closePath(); c.fill(); c.strokeStyle = DONG_T; c.stroke();
    c.fillStyle = DONG_T;
    for (i = 0; i < 14; i++) { var a3 = TAU * (i + .5) / 14 - PI / 2; quanhVong(c, cx, cy, R * .14, a3, function () { c.beginPath(); c.moveTo(0, -R * .05); c.quadraticCurveTo(R * .02, 0, 0, R * .04); c.quadraticCurveTo(-R * .02, 0, 0, -R * .05); c.fill(); }); }
    // vành người: 2 nhà sàn, 2 cặp giã gạo, đoàn người múa
    c.fillStyle = DONG_T; c.strokeStyle = DONG_T; c.lineCap = 'round';
    var rN = R * .47, s = R * .045, cum = [['nha', 0], ['gia', .55], ['mua', 1.0], ['mua', 1.28], ['mua', 1.56], ['mua', 1.84], ['nha', PI], ['gia', PI + .55], ['mua', PI + 1.0], ['mua', PI + 1.28], ['mua', PI + 1.56], ['mua', PI + 1.84]];
    cum.forEach(function (x) { quanhVong(c, cx, cy, rN, x[1] - PI / 2, function () { c.translate(0, s * .9); if (x[0] === 'nha') nhaSan(c, s * 1.05); else if (x[0] === 'gia') giaGao(c, s); else hinhNguoi(c, s, 'mua'); }); });
    // vành chim lạc
    for (i = 0; i < 18; i++) { quanhVong(c, cx, cy, R * .7, TAU * i / 18, function () { c.rotate(-PI / 2); chimLac(c, R * .045); }); }
  });

  var vanThan = H.vanCanvas(2048, 512, function (c, W, Hh) {
    var g = c.createLinearGradient(0, 0, 0, Hh); g.addColorStop(0, '#b98a4e'); g.addColorStop(1, '#8e6534'); c.fillStyle = g; c.fillRect(0, 0, W, Hh);
    c.strokeStyle = DONG_T; c.fillStyle = DONG_T; c.lineWidth = 3;
    [40, 56, 230, 246, 470, 486].forEach(function (y) { c.beginPath(); c.moveTo(0, y); c.lineTo(W, y); c.stroke(); });
    for (var i = 0; i < 6; i++) {   // thuyền có người đội mũ lông chim (vành tang trống)
      var x0 = i * W / 6 + 30, y0 = 180;
      c.beginPath(); c.moveTo(x0, y0 - 40); c.quadraticCurveTo(x0 + 20, y0 + 10, x0 + 90, y0 + 12); c.lineTo(x0 + 240, y0 + 12); c.quadraticCurveTo(x0 + 300, y0 + 10, x0 + 320, y0 - 46);
      c.quadraticCurveTo(x0 + 290, y0 - 6, x0 + 250, y0 - 2); c.lineTo(x0 + 70, y0 - 2); c.quadraticCurveTo(x0 + 30, y0 - 6, x0, y0 - 40); c.fill();
      for (var k = 0; k < 4; k++) { c.save(); c.translate(x0 + 95 + k * 45, y0 - 4); hinhNguoi(c, 30, 'mua'); c.restore(); }
    }
    for (i = 0; i < 16; i++) { var xx = i * W / 16 + 64; c.save(); c.translate(xx, 430); hinhNguoi(c, 44, 'mua'); c.restore(); c.beginPath(); c.moveTo(xx + 64, 256); c.lineTo(xx + 64, 466); c.stroke(); }
  });
  vanThan.wrapS = T.RepeatWrapping;

  // ---------- thân trống (tiện tròn): chân loe, thân thẳng, tang phình, mặt hơi chìa ra
  var R = 2.4, prof = [[2.55, 0], [2.45, 0.12], [2.1, 0.55], [1.98, 1.2], [1.98, 1.9], [2.05, 2.15], [2.35, 2.7], [2.48, 3.15], [2.42, 3.55], [2.5, 3.62], [0.01, 3.62]];
  var thanG = new T.LatheGeometry(prof.map(function (p) { return new T.Vector2(p[0], p[1]); }), 96);
  var matDong = new T.MeshStandardMaterial({ color: 0xffffff, map: vanThan, metalness: .45, roughness: .42 });
  var trong = new T.Group(); V.scene.add(trong);
  var than = new T.Mesh(thanG, matDong); trong.add(than);
  var mat = new T.Mesh(new T.CircleGeometry(2.5, 128), new T.MeshStandardMaterial({ map: vanMat, metalness: .4, roughness: .4 }));
  mat.rotation.x = -PI / 2; mat.position.y = 3.625; trong.add(mat);
  for (var q = 0; q < 4; q++) {   // 4 đôi quai
    var a = q * PI / 2 + PI / 4;
    for (var d = -1; d <= 1; d += 2) {
      var quai = new T.Mesh(new T.TorusGeometry(0.3, 0.06, 8, 16, PI), new T.MeshStandardMaterial({ color: 0x8e6534, metalness: .5, roughness: .45 }));
      quai.position.set(Math.cos(a + d * .09) * 2.32, 2.55, Math.sin(a + d * .09) * 2.32); quai.rotation.set(0, -a + PI / 2, PI / 2); trong.add(quai);
    }
  }
  var de = new T.Mesh(new T.CylinderGeometry(3.4, 3.6, 0.5, 64), new T.MeshStandardMaterial({ color: 0x2b2420, roughness: .7 }));
  de.position.y = -0.25; V.scene.add(de);
  var den = new T.SpotLight(0xffe2b0, 60, 30, 0.5, 0.6); den.position.set(0, 12, 2); den.target = mat; V.scene.add(den);

  // ---------- nhãn và các điểm soi
  var DIEM = [
    { ten: 'Ngôi sao giữa', cam: [0, 7.2, 1.2], tg: [0, 3.6, 0], p: [0, 3.7, 0], tin: VUNG[0] },
    { ten: 'Nhà sàn mái cong', cam: [0, 6.2, -2.8], tg: [0, 3.6, -1.15], p: [0, 3.75, -1.15], tin: ['Mái nhà cong', 'Hình nhà sàn mái cong trên mặt trống giúp hình dung nơi ở của người Việt cổ.'] },
    { ten: 'Người giã gạo', cam: [1.9, 6.0, -3.0], tg: [.61, 3.6, -1.0], p: [.61, 3.75, -1.0], tin: ['Người giã gạo', 'Cảnh người giã gạo cho biết một công việc hằng ngày của người Việt cổ.'] },
    { ten: 'Người múa hát', cam: [2.6, 6.0, 0.4], tg: [1.15, 3.6, .2], p: [1.15, 3.75, .2], tin: ['Người múa hát', 'Đoàn người đội mũ lông chim múa hát giúp hình dung lễ hội của người Việt cổ.'] },
    { ten: 'Chim bay', cam: [0, 6.0, 4.2], tg: [0, 3.6, 1.7], p: [0, 3.75, 1.7], tin: VUNG[2] },
    { ten: 'Thuyền ở thân trống', cam: [0, 3.2, 6.6], tg: [0, 2.6, 0], p: [0, 2.95, 2.5], tin: ['Hình thuyền', 'Hình thuyền chở người đội mũ lông chim cho biết phương tiện đi lại trên sông nước của người Việt cổ.'] }
  ];
  var nhanDiem = DIEM.map(function (d) { var L = V.nhan(d.ten, new T.Vector3().fromArray(d.p), 'nho'); return L; });
  var tin;
  function soi(i) {
    var d = DIEM[i]; V.bay(d.cam, d.tg, 1300); MP.am('chuong_nho');
    nhanDiem.forEach(function (L, k) { L.el.classList.toggle('cam', k === i); });
    tin(d.tin[2] ? d.tin[2] : d.tin[0], d.tin[3] ? d.tin[3] : d.tin[1]);
    xoay.checked = false; trong.rotation.y = 0;
  }
  var nutSoi = DIEM.map(function (d, i) { return H.nut(d.ten, false, function () { soi(i); }); });
  var xoay = el('input', { type: 'checkbox' });
  H.dieuKhien(bc.phai, 'Soi hoạ tiết', [H.hangNut(nutSoi.slice(0, 3)), H.hangNut(nutSoi.slice(3)),
    H.hangNut([H.nut('Toàn cảnh', true, function () { V.bay([0, 9.5, 8.5], [0, 1.6, 0], 1100); MP.am('click'); nhanDiem.forEach(function (L) { L.el.classList.remove('cam'); }); })]),
    el('label', { class: 'hop-chon', style: { marginTop: '8px' } }, xoay, 'Xoay chậm')]);
  tin = H.theTin(bc.phai);
  tin('Trống đồng Ngọc Lũ', 'Chạm vào mặt trống hoặc bấm một nút “Soi hoạ tiết” để xem hình ảnh trên trống kể gì về người Việt cổ.');
  H.theoSGK(bc.phai, [2, 4, 5]);

  // chạm vào mặt trống
  var ray = new T.Raycaster();
  H.khiCham(V, function (ndc) {
    ray.setFromCamera(ndc, V.camera);
    var hit = ray.intersectObject(mat)[0];
    if (!hit) return;
    var lp = trong.worldToLocal(hit.point.clone()); hit.point = lp;
    var r = Math.hypot(hit.point.x, hit.point.z) / 2.5;
    var v = VUNG.find(function (x) { return r >= x[0] && r <= x[1]; }) || VUNG[3];
    if (r >= .34 && r <= .52) {   // xác định cụm hình gần nhất trong vành người
      var a = Math.atan2(hit.point.z, hit.point.x) + PI / 2; a = ((a % TAU) + TAU) % TAU; var k = a % PI;
      v = k < .35 ? [0, 0, 'Mái nhà cong', 'Hình nhà sàn mái cong giúp hình dung nơi ở của người Việt cổ.'] :
          k < .8 ? [0, 0, 'Người giã gạo', 'Cảnh người giã gạo cho biết một công việc hằng ngày của người Việt cổ.'] :
          [0, 0, 'Người múa hát', 'Đoàn người đội mũ lông chim múa hát giúp hình dung lễ hội của người Việt cổ.'];
    }
    tin(v[2], v[3]); MP.am('tick');
  });
  V.moi(function (dt) { if (xoay.checked) trong.rotation.y += dt * .25; });
});
