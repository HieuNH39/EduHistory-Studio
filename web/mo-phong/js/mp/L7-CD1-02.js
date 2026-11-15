/* L7-CD1-02 · Tàu Ca-ra-ven 3D.
   Dữ kiện (SGK LSĐL 7 tr. 166–168, qua kịch bản): tàu Ca-ra-ven chở các nhà thám hiểm vượt đại dương; kĩ thuật đóng tàu có bước tiến
   mới: tàu dài có bánh lái và hệ thống buồm lớn; cuối thế kỉ XV la bàn được dùng phổ biến; tháng 8 – 1492 C. Cô-lôm-bô ra khơi trên
   ba chiếc tàu về phía tây. Mô hình minh hoạ, giản lược, không theo tỉ lệ. */
MP.onReady(function () {
  var root = MP.khung(), el = MP.el, BC = window.BaChieu, H = window.MH;
  var bc = H.boCuc(root);
  MP.nen(['song_bien', 'gio']);
  var V = BC.tao(bc.trai, { nen: 0xbcd6e6, suongMu: [60, 170], camPos: [18, 9, 16], target: [0, 3, 0], minDist: 6, maxDist: 70,
    nangPos: [20, 26, 8], nangManh: 2.5, hemi: 1.2, troi: 0xeaf4ff, dat: 0x2c5566,
    moTa: 'Mô hình 3D tàu Ca-ra-ven. Kéo để xoay, cuộn để phóng to. Đổi hướng gió để xem buồm xoay.' });
  if (!V) return;
  var T = V.T, PI = Math.PI;
  // ---- biển
  var bien = new T.Mesh(new T.PlaneGeometry(220, 220, 90, 90), new T.MeshStandardMaterial({ color: 0x2f6f8c, roughness: .35, metalness: .05 }));
  bien.rotation.x = -PI / 2; V.scene.add(bien);
  var pb = bien.geometry.attributes.position, gocB = pb.array.slice();

  // ---- tàu
  var tau = new T.Group(); V.scene.add(tau);
  var go = new T.MeshStandardMaterial({ color: 0x7a5232, roughness: .85 }), goSang = new T.MeshStandardMaterial({ color: 0xa47a4c, roughness: .85 });
  var than = new T.Mesh(new T.SphereGeometry(1, 40, 20, 0, PI * 2, PI / 2, PI / 2), go);   // nửa dưới quả cầu → thân tàu
  than.scale.set(5.2, 2.0, 1.55); than.position.y = 1.6; tau.add(than);
  var san = new T.Mesh(new T.CylinderGeometry(1, 1, .14, 40), goSang); san.scale.set(5.15, 1, 1.5); san.position.y = 1.62; tau.add(san);
  var lau = new T.Mesh(new T.BoxGeometry(2.2, 1.0, 2.6), goSang); lau.position.set(-3.7, 2.15, 0); tau.add(lau);     // lâu đuôi
  var lanCan = new T.Mesh(new T.BoxGeometry(2.3, .25, 2.7), go); lanCan.position.set(-3.7, 2.75, 0); tau.add(lanCan);
  var muiT = new T.Mesh(new T.ConeGeometry(.12, 3.2, 6), go); muiT.rotation.z = -PI / 2 - .25; muiT.position.set(5.9, 2.4, 0); tau.add(muiT);  // cột mũi
  // bánh lái + cần lái
  var lai = new T.Group(); tau.add(lai);
  var banhLai = new T.Mesh(new T.BoxGeometry(.9, 2.2, .14), go); banhLai.position.set(-5.35, .9, 0); lai.add(banhLai);
  var canLai = new T.Mesh(new T.CylinderGeometry(.05, .05, 2.2, 6), go); canLai.rotation.z = PI / 2; canLai.position.set(-4.4, 2.3, 0); lai.add(canLai);
  // la bàn trên lâu đuôi
  var laBan = new T.Group(); laBan.position.set(-3.1, 2.95, 0); tau.add(laBan);
  laBan.add(new T.Mesh(new T.CylinderGeometry(.32, .36, .3, 20), goSang));
  var mat = new T.Mesh(new T.CircleGeometry(.27, 24), new T.MeshStandardMaterial({ color: 0xf3ead2 })); mat.rotation.x = -PI / 2; mat.position.y = .16; laBan.add(mat);
  var kim = new T.Mesh(new T.ConeGeometry(.05, .42, 4), new T.MeshStandardMaterial({ color: 0xb8261e })); kim.rotation.x = PI / 2; kim.position.y = .18; laBan.add(kim);
  // cột buồm + buồm tam giác (buồm la-tinh) treo trên trục chéo
  function cotBuom(x, cao, rong) {
    var g = new T.Group(); g.position.set(x, 1.6, 0); tau.add(g);
    var cot = new T.Mesh(new T.CylinderGeometry(.09, .12, cao, 8), go); cot.position.y = cao / 2; g.add(cot);
    var truc = new T.Group(); truc.position.y = cao * .9; g.add(truc);
    var sao = new T.Mesh(new T.CylinderGeometry(.05, .06, rong * 1.25, 6), go); sao.rotation.z = PI / 2 - .55; truc.add(sao);
    var hinh = new T.Shape(); var x0 = -rong * .55 * Math.cos(.55), y0 = -rong * .55 * Math.sin(.55), x1 = rong * .55 * Math.cos(.55), y1 = rong * .55 * Math.sin(.55);
    hinh.moveTo(x0, y0); hinh.lineTo(x1, y1); hinh.lineTo(x0 + rong * .15, -cao * .78); hinh.lineTo(x0, y0);
    var buom = new T.Mesh(new T.ShapeGeometry(hinh), new T.MeshStandardMaterial({ color: 0xf3e9d2, emissive: 0x4a4232, side: T.DoubleSide, roughness: .95 }));
    truc.add(buom);
    var thap = new T.Mesh(new T.CircleGeometry(.4, 4), new T.MeshBasicMaterial({ color: 0xb8261e, side: T.DoubleSide })); thap.position.set(0, -cao * .35, .02); thap.rotation.z = PI / 4; truc.add(thap); // chữ thập trang trí
    return truc;
  }
  var trucs = [cotBuom(2.2, 7.2, 6.5), cotBuom(-.6, 6.2, 5.5), cotBuom(-3.2, 4.6, 3.8)];

  // nhãn bộ phận
  var BP = {
    'Bánh lái': { p: [-5.4, 1.4, 0], cam: [-11, 4, 6], tg: [-5, 1.6, 0], tin: ['Bánh lái', 'Tàu Ca-ra-ven có bánh lái ở đuôi tàu, giúp giữ và đổi hướng đi trên biển.'] },
    'Buồm lớn': { p: [2.2, 6.5, 0], cam: [10, 7, 12], tg: [1, 5, 0], tin: ['Hệ thống buồm lớn', 'Tàu có hệ thống buồm lớn để tận dụng sức gió khi vượt đại dương.'] },
    'La bàn': { p: [-3.1, 3.4, 0], cam: [-1.5, 5.2, 3.2], tg: [-3.1, 3, 0], tin: ['La bàn', 'Cuối thế kỉ XV, la bàn được dùng phổ biến, giúp xác định phương hướng giữa đại dương.'] },
    'Thân tàu dài': { p: [4, 2.2, 1.6], cam: [4, 3.4, 14], tg: [0, 1.6, 0], tin: ['Thân tàu dài', 'Kĩ thuật đóng tàu có bước tiến mới: đóng được những con tàu dài để vượt đại dương.'] }
  };
  var nh = {}; Object.keys(BP).forEach(function (k) { nh[k] = V.nhan(k, function () { return tau.localToWorld(new T.Vector3().fromArray(BP[k].p)); }, 'nho'); });
  var muiGio = new T.Group(); muiGio.position.set(-2, 10, 0); V.scene.add(muiGio);
  var matGio = new T.MeshBasicMaterial({ color: 0x2aa7e0 });
  var cGio = new T.Mesh(new T.CylinderGeometry(.08, .08, 3, 8), matGio); cGio.rotation.z = -PI / 2; cGio.position.x = 1.5; muiGio.add(cGio);
  var nGio2 = new T.Mesh(new T.ConeGeometry(.35, .9, 12), matGio); nGio2.rotation.z = -PI / 2; nGio2.position.x = 3.4; muiGio.add(nGio2);
  V.nhan('Hướng gió', new T.Vector3(-2, 10.8, 0), 'cham');

  var st = { gio: 15, chay: false, x: 0 }, tin;
  var tGio = H.truot('Hướng gió', -90, 90, 1, 15, function (v) { return v === 0 ? 'xuôi đuôi' : (v > 0 ? 'mạn phải ' : 'mạn trái ') + Math.abs(v) + '°'; },
    function (v) { st.gio = v; tin('Buồm xoay theo gió', 'Thuỷ thủ xoay buồm theo hướng gió để tàu đi tới; bánh lái giữ cho tàu đi đúng hướng.'); });
  tGio.r.addEventListener('change', function () { MP.am('gio'); });
  var nKhoi = H.nut('Ra khơi', true, function () { st.chay = !st.chay; nKhoi.textContent = st.chay ? 'Thả neo' : 'Ra khơi'; MP.am(st.chay ? 'song_bien' : 'click');
    if (st.chay) tin('Vượt đại dương', 'Tháng 8 năm 1492, C. Cô-lôm-bô cùng các thuỷ thủ giương buồm trên ba chiếc tàu, hướng về phía tây.'); });
  var nutBP = Object.keys(BP).map(function (k) { return H.nut(k, false, function () { var b = BP[k]; V.bay(b.cam, b.tg, 1300); tin(b.tin[0], b.tin[1]); MP.am('chuong_nho');
    Object.keys(nh).forEach(function (j) { nh[j].el.classList.toggle('cam', j === k); }); }); });
  H.dieuKhien(bc.phai, 'Điều khiển', [tGio.w, H.hangNut([nKhoi, H.nut('Toàn cảnh', false, function () { V.bay([18, 9, 16], [0, 3, 0], 1000); MP.am('click'); })]),
    el('p', { style: { margin: '10px 0 2px', fontWeight: 700, fontSize: '.86rem' } }, 'Bộ phận của tàu'), H.hangNut(nutBP.slice(0, 2)), H.hangNut(nutBP.slice(2))]);
  tin = H.theTin(bc.phai);
  tin('Tàu Ca-ra-ven', 'Bấm tên từng bộ phận để xem, hoặc đổi hướng gió rồi bấm “Ra khơi”.');
  H.theoSGK(bc.phai, [1, 4, 7]);

  V.moi(function (dt, t) {
    var g = st.gio * PI / 180;
    trucs.forEach(function (tr, i) { var dich = -g * .9; tr.rotation.y += (dich - tr.rotation.y) * Math.min(1, dt * 2.5); });
    muiGio.rotation.y = -g;
    var nghieng = Math.sin(g) * .08 * (st.chay ? 1.6 : 1);
    tau.rotation.x += (nghieng - tau.rotation.x) * Math.min(1, dt * 1.5);
    tau.position.y = Math.sin(t * 1.1) * .12; tau.rotation.z = Math.sin(t * .9) * .025;
    lai.rotation.y = Math.sin(g) * .25;
    kim.rotation.z = Math.sin(t * .7) * .05;
    var tocDo = st.chay ? 4 : 0; st.x += tocDo * dt;
    for (var i = 0; i < pb.count; i++) { var x = gocB[i * 3], y = gocB[i * 3 + 1];
      pb.setZ(i, Math.sin((x + st.x) * .35 + t * 1.4) * .22 + Math.cos(y * .28 + t * .9) * .18); }
    pb.needsUpdate = true; bien.geometry.computeVertexNormals();
  });
});
