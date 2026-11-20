/* L7-B18-02 · Tháp Chăm 3D – xây bằng gạch nung, gắn kết không dùng vữa.
   Dữ kiện (SGK LSĐL 7 tr. 92–93, qua kịch bản): người Chăm sáng tạo cách làm gạch và gắn kết khi xây đền tháp mà không dùng vữa;
   chất kết dính đến nay vẫn là bí ẩn; đền tháp xây bằng gạch nung, trang trí phù điêu (Dương Long, Bà Pô-na-ga, Pô Klong Ga-rai).
   Mô hình minh hoạ kiểu tháp Chăm: thân vuông, nhiều tầng mái thu nhỏ dần; giản lược, không theo tỉ lệ. */
MP.onReady(function () {
  var root = MP.khung(), el = MP.el, BC = window.BaChieu, H = window.MH;
  var bc = H.boCuc(root);
  MP.nen(['gio', 'chim']);
  var V = BC.tao(bc.trai, { nen: 0xd7e4ea, suongMu: [45, 110], camPos: [13, 9, 15], target: [0, 4.2, 0], minDist: 6, maxDist: 60,
    nangPos: [14, 22, 10], nangManh: 2.6, hemi: 1.1, troi: 0xfff1dc, dat: 0x9a7a52,
    moTa: 'Mô hình 3D tháp Chăm bằng gạch nung. Kéo để xoay, cuộn để phóng to, chạm vào một viên gạch để xem thông tin.' });
  if (!V) return;
  var T = V.T, rnd = BC.rngSo(1290);
  // nền đất, đồi
  var dat = new T.Mesh(new T.CircleGeometry(80, 48), new T.MeshStandardMaterial({ color: 0xb59a6a, roughness: 1 })); dat.rotation.x = -Math.PI / 2; V.scene.add(dat);
  for (var i = 0; i < 26; i++) { var a = rnd() * Math.PI * 2, rr = 16 + rnd() * 26;
    var bui = new T.Mesh(new T.SphereGeometry(0.8 + rnd() * 1.2, 8, 6), new T.MeshStandardMaterial({ color: 0x6f8c48, roughness: 1 }));
    bui.scale.y = .7; bui.position.set(Math.cos(a) * rr, .4, Math.sin(a) * rr); V.scene.add(bui); }

  // ---- danh sách lớp gạch: [nửa cạnh, độ cao đáy lớp, nhóm]
  var GH = 0.18, BL = 0.46, BW = 0.24, lop = [];
  function khoi(nuaCanh, y0, soLop, nhom) { for (var k = 0; k < soLop; k++) lop.push({ c: nuaCanh, y: y0 + k * GH, nhom: nhom }); return y0 + soLop * GH; }
  var y = khoi(2.9, 0, 4, 'Nền tháp');
  y = khoi(2.6, y, 3, 'Chân tháp');
  y = khoi(2.15, y, 30, 'Thân tháp');
  y = khoi(2.35, y, 2, 'Gờ mái');
  var tang = [[1.75, 9, 'Tầng mái thứ nhất'], [1.35, 8, 'Tầng mái thứ hai'], [0.98, 7, 'Tầng mái thứ ba']];
  tang.forEach(function (tg) { y = khoi(tg[0], y, tg[1], tg[2]); y = khoi(tg[0] + .16, y, 1, tg[2]); });
  var dinhY = y;
  // gạch theo chu vi hình vuông của từng lớp
  var gach = [];
  lop.forEach(function (L, li) {
    var c = L.c, n = Math.max(2, Math.round(2 * c / BL)), step = 2 * c / n, lech = (li % 2) * step / 2;
    for (var s = 0; s < 4; s++) for (var j = 0; j < n; j++) {
      var t = -c + lech + (j + .5) * step; if (t > c) t -= 2 * c;
      var x, z, rot;
      if (s === 0) { x = t; z = c; rot = 0; } else if (s === 1) { x = c; z = -t; rot = Math.PI / 2; } else if (s === 2) { x = -t; z = -c; rot = 0; } else { x = -c; z = t; rot = Math.PI / 2; }
      gach.push({ li: li, x: x, z: z, rot: rot, dai: step * .985 });
    }
  });
  var im = new T.InstancedMesh(new T.BoxGeometry(1, GH * .97, BW), new T.MeshStandardMaterial({ color: 0xffffff, roughness: .88 }), gach.length);
  var mauGoc = [];
  gach.forEach(function (g, k) { var cl = BC.bienMau(0x9c5640, .1, rnd); mauGoc.push(cl); im.setColorAt(k, cl); });
  V.scene.add(im);
  // cửa giả (vòm nhọn) ba mặt, cửa thật mặt đông có tiền sảnh
  var trangTri = new T.Group(); V.scene.add(trangTri);
  var matTT = new T.MeshStandardMaterial({ color: 0x8d4630, roughness: .9 });
  var yThan = 7 * GH;
  [0, 1, 2, 3].forEach(function (s) {
    var g = new T.Group();
    var khung = new T.Mesh(new T.BoxGeometry(1.5, 3.4, .25), matTT); khung.position.set(0, yThan + 1.9, 0); g.add(khung);
    var vom = new T.Mesh(new T.ConeGeometry(.95, 1.4, 4), matTT); vom.rotation.y = Math.PI / 4; vom.scale.z = .2; vom.position.set(0, yThan + 4.2, 0); g.add(vom);
    var lo = new T.Mesh(new T.BoxGeometry(.8, 2.4, .1), new T.MeshStandardMaterial({ color: s === 0 ? 0x1c120d : 0x6e3524 })); lo.position.set(0, yThan + 1.6, .13); g.add(lo);
    g.position.set(Math.sin(s * Math.PI / 2) * 2.2, 0, Math.cos(s * Math.PI / 2) * 2.2); g.rotation.y = s * Math.PI / 2;
    trangTri.add(g);
  });
  var sanh = new T.Mesh(new T.BoxGeometry(1.9, 2.6, 1.6), matTT); sanh.position.set(0, yThan + 1.3, 2.9); trangTri.add(sanh);
  var maiSanh = new T.Mesh(new T.ConeGeometry(1.3, 1.6, 4), matTT); maiSanh.rotation.y = Math.PI / 4; maiSanh.position.set(0, yThan + 3.4, 2.9); trangTri.add(maiSanh);
  // tháp nhỏ ở các góc mái, chóp đỉnh
  var dinh = new T.Mesh(new T.ConeGeometry(.75, 1.6, 8), new T.MeshStandardMaterial({ color: 0x9c5a3e, roughness: .85 })); dinh.position.y = dinhY + .8; trangTri.add(dinh);
  // lõi đặc bên trong từng khối (để nhìn từ trên không thấy rỗng)
  var matLoi = new T.MeshStandardMaterial({ color: 0x8a4a33, roughness: .95 }), dau = 0;
  for (var li2 = 1; li2 <= lop.length; li2++) {
    if (li2 === lop.length || lop[li2].c !== lop[dau].c) {
      var c2 = lop[dau].c, cao = (li2 - dau) * GH;
      var lb = new T.Mesh(new T.BoxGeometry(2 * c2 - BW * .6, cao, 2 * c2 - BW * .6), matLoi); lb.position.y = lop[dau].y + cao / 2; trangTri.add(lb);
      dau = li2;
    }
  }
  tang.forEach(function (tg, k) {
    var L0 = lop.findIndex(function (L) { return L.nhom === tg[2]; }), c = tg[0] + .16, y0 = lop[L0].y;
    [[1, 1], [1, -1], [-1, 1], [-1, -1]].forEach(function (d) {
      var p = new T.Mesh(new T.ConeGeometry(.24 - k * .04, .8 - k * .1, 4), matTT); p.position.set(d[0] * c, y0 + .4, d[1] * c); p.rotation.y = Math.PI / 4; trangTri.add(p);
    });
  });
  trangTri.visible = true;

  // ---- trạng thái: hien[li] (0..1 hiện), tach (giãn lớp)
  var hien = new Array(lop.length).fill(1), st = { tach: 0, xep: -1, xepT: 0 };
  var M = new T.Matrix4(), Q = new T.Quaternion(), E = new T.Euler(), P = new T.Vector3(), SC = new T.Vector3();
  function capNhat() {
    gach.forEach(function (g, k) {
      var L = lop[g.li], h = hien[g.li], dy = g.li * st.tach * .12;
      E.set(0, g.rot, 0); Q.setFromEuler(E); P.set(g.x, L.y + GH / 2 + dy + (1 - h) * 3, g.z); SC.set(g.dai * h, h, h);
      M.compose(P, Q, SC); im.setMatrixAt(k, M);
    });
    im.instanceMatrix.needsUpdate = true;
    trangTri.visible = st.tach < .02 && hien[hien.length - 1] > .99;
  }
  capNhat();

  var tin;
  var tTach = H.truot('Tách lớp gạch', 0, 100, 1, 0, function (v) { return v + '%'; }, function (v) {
    st.tach = v / 100; capNhat(); if (v > 0) tin('Không có lớp vữa', ['Các lớp gạch nung đặt khít trực tiếp lên nhau: giữa các lớp không có vữa.', 'Người Chăm đã dùng chất gì để kết dính các viên gạch đến nay vẫn còn là một bí ẩn.']); });
  tTach.r.addEventListener('change', function () { MP.am('da', { lv: .5 }); });
  var nXay = H.nut('Xây tháp từ móng', true, function () { st.tach = 0; tTach.dat(0); hien.fill(0); st.xep = 0; st.xepT = 0; st.xepCu = -1; capNhat(); MP.am('click');
    tin('Xây tháp bằng gạch nung', 'Từng lớp gạch được đặt khít lên lớp dưới. Mô hình có ' + MP.so(gach.length) + ' viên gạch.'); V.bay([15, 8, 17], [0, 4, 0], 1200); });
  var nLai = H.nut('Đặt lại', false, function () { st.xep = -1; hien.fill(1); st.tach = 0; tTach.dat(0); capNhat(); V.bay([13, 9, 15], [0, 4.2, 0], 1000); MP.am('click'); });
  var nDinh = H.nut('Nhìn các tầng mái', false, function () { V.bay([6, dinhY + 2, 7], [0, dinhY - 2.5, 0], 1300); MP.am('soi'); tin('Các tầng mái', 'Phía trên thân tháp là các tầng mái thu nhỏ dần, mỗi góc có tháp nhỏ trang trí.'); });
  H.dieuKhien(bc.phai, 'Điều khiển', [tTach.w, H.hangNut([nXay, nLai]), H.hangNut([nDinh])]);
  tin = H.theTin(bc.phai);
  tin('Tháp Chăm', 'Bấm “Xây tháp từ móng” để xem tháp được dựng từ từng lớp gạch, hoặc kéo “Tách lớp gạch”.');
  H.theoSGK(bc.phai, [1, 3, 4, 7]);
  var nhanGach = V.nhan('', null, 'cam'); nhanGach.hien = false;
  V.nhan('Thân tháp', new T.Vector3(2.4, 4.6, 2.4), 'nho'); V.nhan('Tầng mái', new T.Vector3(1.8, lop[37 + 2].y + 1, 1.8), 'nho');

  var ray = new T.Raycaster(), chon = -1;
  H.khiCham(V, function (ndc) {
    ray.setFromCamera(ndc, V.camera); var hit = ray.intersectObject(im)[0];
    if (chon >= 0) im.setColorAt(chon, mauGoc[chon]);
    if (hit && hit.instanceId != null) {
      chon = hit.instanceId; im.setColorAt(chon, new T.Color(0xf26b1d));
      nhanGach.el.textContent = 'Gạch nung · ' + lop[gach[chon].li].nhom; nhanGach.pos = hit.point.clone(); nhanGach.hien = true;
      tin('Một viên gạch nung', ['Gạch được nung chín rồi xếp khít, gắn kết với nhau mà không dùng vữa.', 'Nhờ vậy, trải qua hàng trăm năm, tháp vẫn vững chắc.']); MP.am('chuong_nho');
    } else { chon = -1; nhanGach.hien = false; }
    im.instanceColor.needsUpdate = true;
  });

  V.moi(function (dt) {
    if (st.xep < 0) return;
    st.xepT += dt; var toc = 0.07, doi = false;
    for (var li = 0; li < lop.length; li++) {
      var k = MP.clamp((st.xepT - li * toc) / .25, 0, 1), e = 1 - Math.pow(1 - k, 3);
      if (hien[li] !== e) { hien[li] = e; doi = true; }
    }
    var cur = Math.floor(st.xepT / toc);
    if (cur !== st.xepCu && cur < lop.length && cur % 3 === 0) MP.am('da', { lv: .35 });
    st.xepCu = cur;
    if (doi) capNhat();
    if (st.xepT > lop.length * toc + .4) { st.xep = -1; MP.am('chuong'); V.bang('Gạch nung gắn kết không dùng vữa', true); setTimeout(function () { V.bang('', false); }, 3200); }
  });
});
