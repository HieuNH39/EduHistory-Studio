/* L6-B13-04 · Đền Bô-rô-bu-đua 3D.
   Dữ kiện (SGK LSĐL 6 tr. 56–58, qua kịch bản): đền Bô-rô-bu-đua ở In-đô-nê-xi-a được xây dựng vào thế kỉ VIII, được coi là kì quan
   Phật giáo lớn nhất thế giới; kiến trúc, điêu khắc Đông Nam Á chịu ảnh hưởng đậm nét của Ấn Độ giáo, Phật giáo; điêu khắc gồm phù điêu,
   chạm nổi, tượng thần, tượng Phật. Mô hình minh hoạ: các tầng nền vuông, tầng tròn và tháp chuông, giản lược, không theo tỉ lệ. */
MP.onReady(function () {
  var root = MP.khung(), el = MP.el, BC = window.BaChieu, H = window.MH;
  var bc = H.boCuc(root);
  MP.nen(['chim', 'gio']);
  var V = BC.tao(bc.trai, { nen: 0xcfe2ea, suongMu: [70, 170], camPos: [30, 20, 32], target: [0, 4, 0], minDist: 10, maxDist: 100, maxPolar: Math.PI * .5,
    nangPos: [24, 36, 14], nangManh: 2.5, hemi: 1.1, troi: 0xf4f8ff, dat: 0x6a7a4a,
    moTa: 'Mô hình 3D đền Bô-rô-bu-đua. Kéo để xoay, cuộn để phóng to. Dựng từng tầng bằng thanh trượt.' });
  if (!V) return;
  var T = V.T, PI = Math.PI, rnd = BC.rngSo(800);
  var dat = new T.Mesh(new T.CircleGeometry(110, 48), new T.MeshStandardMaterial({ color: 0x6f8c4a, roughness: 1 })); dat.rotation.x = -PI / 2; V.scene.add(dat);
  for (var i = 0; i < 40; i++) { var a = rnd() * PI * 2, r = 30 + rnd() * 50;
    var tan = new T.Mesh(new T.SphereGeometry(1.4 + rnd() * 1.6, 8, 6), new T.MeshStandardMaterial({ color: rnd() < .5 ? 0x3f6b35 : 0x547d3e, roughness: 1 }));
    tan.position.set(Math.cos(a) * r, 2.2, Math.sin(a) * r); V.scene.add(tan);
    var th = new T.Mesh(new T.CylinderGeometry(.2, .3, 2.4, 6), new T.MeshStandardMaterial({ color: 0x5b4330 })); th.position.set(Math.cos(a) * r, .9, Math.sin(a) * r); V.scene.add(th); }

  var da = function (h) { return new T.MeshStandardMaterial({ color: h || 0x8f8b80, roughness: .95 }); };
  var tangs = [];   // mỗi tầng: Group, cao y0..y1
  var HT = 1.25, y = 0;
  // chuông tháp (stupa) dạng tiện
  function chuong(r, h, kieu) {
    var p = [[0, 0], [r, 0], [r, h * .08], [r * .95, h * .12], [r * 1.0, h * .45], [r * .7, h * .65], [r * .3, h * .72], [r * .22, h * .8], [r * .3, h * .82], [r * .12, h * .95], [r * .04, h], [0, h]];
    var m = new T.Mesh(new T.LatheGeometry(p.map(function (q) { return new T.Vector2(q[0], q[1]); }), kieu ? 28 : 14), da(0x8a8679));
    return m;
  }
  // 6 tầng nền vuông, có tường lan can và tháp nhỏ trên lan can
  var canh = [26, 22.5, 19.5, 17, 14.6, 12.4];
  canh.forEach(function (c, k) {
    var g = new T.Group(); V.scene.add(g);
    var nen = new T.Mesh(new T.BoxGeometry(c, HT, c), da(k % 2 ? 0x8f8b80 : 0x88847a)); nen.position.y = y + HT / 2; g.add(nen);
    [[1, 0], [-1, 0], [0, 1], [0, -1]].forEach(function (d) {   // phần lồi giữa mỗi cạnh
      var l = new T.Mesh(new T.BoxGeometry(d[0] ? 1.2 : c * .45, HT, d[0] ? c * .45 : 1.2), da(0x8b877c));
      l.position.set(d[0] * (c / 2 + .55), y + HT / 2, d[1] * (c / 2 + .55)); g.add(l);
    });
    if (k > 0) {   // lan can + tháp nhỏ
      [[0, 1], [0, -1], [1, 0], [-1, 0]].forEach(function (d) {   // tường lan can bốn cạnh
        var w = new T.Mesh(new T.BoxGeometry(d[0] ? .5 : c, .8, d[0] ? c : .5), da(0x7f7b70));
        w.position.set(d[0] * (c / 2 - .25), y + HT + .4, d[1] * (c / 2 - .25)); g.add(w); });
      var n = Math.round(c / 1.6);
      for (var j = 0; j < n; j++) { var t = -c / 2 + .5 + j * (c - 1) / (n - 1);
        [[t, c / 2 - .2], [t, -c / 2 + .2], [c / 2 - .2, t], [-c / 2 + .2, t]].forEach(function (q) { var s = chuong(.28, .9); s.position.set(q[0], y + HT + .7, q[1]); g.add(s); }); }
    }
    // cầu thang bốn mặt
    [[0, 1], [0, -1], [1, 0], [-1, 0]].forEach(function (d) { var cb = new T.Mesh(new T.BoxGeometry(d[0] ? 1.5 : 1.6, HT + .02, d[0] ? 1.6 : 1.5), da(0x7d796f));
      cb.position.set(d[0] * (c / 2 + 1.2), y + HT / 2, d[1] * (c / 2 + 1.2)); g.add(cb); });
    tangs.push({ g: g, ten: k === 0 ? 'Nền móng' : 'Tầng nền vuông thứ ' + k, y: y }); y += HT;
  });
  // 3 tầng tròn với các tháp chuông
  [[5.4, 16], [4.3, 12], [3.2, 8]].forEach(function (q, k) {
    var g = new T.Group(); V.scene.add(g);
    var nen = new T.Mesh(new T.CylinderGeometry(q[0] + .9, q[0] + 1.1, HT * .8, 48), da(0x8d897e)); nen.position.y = y + HT * .4; g.add(nen);
    for (var j = 0; j < q[1] * 2; j++) { var a2 = j / (q[1] * 2) * PI * 2; var s = chuong(.55, 1.7); s.position.set(Math.cos(a2) * q[0], y + HT * .8, Math.sin(a2) * q[0]); g.add(s); }
    tangs.push({ g: g, ten: 'Tầng tròn thứ ' + (k + 1), y: y }); y += HT * .8;
  });
  var gDinh = new T.Group(); V.scene.add(gDinh);
  var dinh = chuong(2.2, 5.2, true); dinh.position.y = y; gDinh.add(dinh);
  tangs.push({ g: gDinh, ten: 'Tháp chuông lớn trên đỉnh', y: y });
  var N = tangs.length;
  V.nhan('Các tầng nền vuông', new T.Vector3(13.6, 3.2, 0), 'nho');
  V.nhan('Các tầng tròn, tháp chuông', new T.Vector3(5.6, y - .4, 0), 'nho');
  V.nhan('Tháp chuông lớn', new T.Vector3(0, y + 5.6, 0), 'cam');

  var hien = new Array(N).fill(1), st = { muc: N, xep: -1, t: 0 }, tin;
  function capNhat() { tangs.forEach(function (tg, k) { var h = hien[k]; tg.g.visible = h > .01; tg.g.position.y = (1 - h) * 8; tg.g.scale.setScalar(.85 + .15 * h); }); }
  var tTang = H.truot('Dựng từng tầng', 1, N, 1, N, function (v) { return v + '/' + N; }, function (v) {
    st.xep = -1; for (var k = 0; k < N; k++) hien[k] = k < v ? 1 : 0; capNhat(); MP.am('da', { lv: .5 }); tin(tangs[v - 1].ten, v < 7 ? 'Các tầng nền vuông chồng lên nhau, nhỏ dần về phía trên, có lan can và nhiều tháp nhỏ.' : 'Trên cùng là các tầng tròn với những tháp hình chuông bao quanh tháp chuông lớn.'); });
  var nXay = H.nut('Xây từ nền', true, function () { hien.fill(0); capNhat(); st.xep = 0; st.t = 0; MP.am('click'); V.bay([34, 18, 36], [0, 4, 0], 1000);
    tin('Xây từ nền', 'Các tầng đá được xếp chồng lên nhau theo hình một ngọn núi, trên cùng là tháp chuông lớn.'); });
  var nTren = H.nut('Từ trên xuống', false, function () { V.bay([0.1, 52, 0.1], [0, 0, 0], 1500); MP.am('soi'); tin('Nhìn từ trên xuống', 'Nhìn từ trên cao, các tầng vuông và tròn lồng vào nhau quanh một tâm.'); });
  var nLai = H.nut('Toàn cảnh', false, function () { V.bay([30, 20, 32], [0, 4, 0], 1000); MP.am('click'); });
  H.dieuKhien(bc.phai, 'Điều khiển', [tTang.w, H.hangNut([nXay, nTren, nLai])]);
  tin = H.theTin(bc.phai);
  tin('Đền Bô-rô-bu-đua', 'Kéo thanh “Dựng từng tầng” hoặc bấm “Xây từ nền” để xem công trình được dựng lên.');
  H.theoSGK(bc.phai, [5, 9, 10]);
  V.moi(function (dt) {
    if (st.xep < 0) return;
    st.t += dt; var doi = false;
    for (var k = 0; k < N; k++) { var e = MP.clamp((st.t - k * .55) / .5, 0, 1); e = 1 - Math.pow(1 - e, 3); if (hien[k] !== e) { hien[k] = e; doi = true; } }
    var cur = Math.floor(st.t / .55); if (cur !== st.cu && cur < N) { MP.am('da', { lv: .6 }); st.cu = cur; }
    if (doi) capNhat();
    if (st.t > N * .55 + .5) { st.xep = -1; tTang.dat(N); MP.am('chuong'); V.bang('Kì quan Phật giáo lớn nhất thế giới (thế kỉ VIII)', true); setTimeout(function () { V.bang('', false); }, 3200); }
  });
});
