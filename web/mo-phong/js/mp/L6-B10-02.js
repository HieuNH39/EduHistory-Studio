/* L6-B10-02 · A-ten: đền Pác-tê-nông 3D, sơ đồ bộ máy nhà nước, trò bỏ phiếu bằng vỏ sò.
   Dữ kiện (SGK LSĐL 6 tr. 44, 46–47, qua kịch bản): A-ten là thành bang tiêu biểu cho chế độ dân chủ; trên đồi cao là đền Pác-tê-nông,
   công trình tiêu biểu của Hy Lạp cổ đại; Đại hội nhân dân gồm công dân nam từ 18 tuổi trở lên, bầu ra Hội đồng 500 người, Toà án
   6 000 thẩm phán, Hội đồng 10 tư lệnh; bỏ phiếu bằng vỏ sò: đủ 6 000 phiếu ghi tên một người thì người đó phải rời A-ten 10 năm.
   Mô hình 3D minh hoạ, giản lược số cột và trang trí, không theo tỉ lệ. */
MP.onReady(function () {
  var root = MP.khung(), el = MP.el, BC = window.BaChieu, H = window.MH;
  var bc = H.boCuc(root);
  MP.nen(['gio', 'chim']);
  var V = BC.tao(bc.trai, { nen: 0xd6e6f0, suongMu: [60, 150], camPos: [30, 16, 26], target: [0, 6, 0], minDist: 10, maxDist: 90,
    nangPos: [26, 34, 10], nangManh: 2.7, hemi: 1.1, troi: 0xfff6e6, dat: 0x9a8a62,
    moTa: 'Mô hình 3D đền Pác-tê-nông trên đồi cao. Kéo để xoay, cuộn để phóng to.' });
  if (!V) return;
  var T = V.T, PI = Math.PI, rnd = BC.rngSo(447);
  var dat = new T.Mesh(new T.CircleGeometry(120, 48), new T.MeshStandardMaterial({ color: 0x9caa6a, roughness: 1 })); dat.rotation.x = -PI / 2; V.scene.add(dat);
  // đồi đá (A-cờ-rô-pô-li)
  var doi = new T.Mesh(new T.CylinderGeometry(18, 24, 4.2, 14, 1), new T.MeshStandardMaterial({ color: 0xb4a17d, roughness: 1, flatShading: true }));
  doi.position.y = 2.1; doi.scale.z = .62; V.scene.add(doi);
  var Y0 = 4.2, da = new T.MeshStandardMaterial({ color: 0xece3d0, roughness: .85 });
  // nền bậc
  [[34, 15.5], [33, 14.5], [32, 13.5]].forEach(function (b, k) { var m = new T.Mesh(new T.BoxGeometry(b[0], .35, b[1]), da); m.position.y = Y0 + .175 + k * .35; V.scene.add(m); });
  var YC = Y0 + 1.05, HC = 6.4;
  // cột
  var cotG = new T.CylinderGeometry(.48, .58, HC, 16); cotG.translate(0, HC / 2, 0);
  var cot = [];
  for (var i = 0; i < 17; i++) for (var j = 0; j < 8; j++) {
    if (i > 0 && i < 16 && j > 0 && j < 7) continue;
    var m = new T.Mesh(cotG, da); m.position.set(-15 + i * 1.875, YC, -6.2 + j * 1.77); V.scene.add(m); cot.push(m);
    var dau = new T.Mesh(new T.BoxGeometry(1.25, .3, 1.25), da); dau.position.set(0, HC + .15, 0); m.add(dau);
  }
  cot.sort(function (a, b) { return (a.position.x + a.position.z * .3) - (b.position.x + b.position.z * .3); });
  // phần mái
  var mai = new T.Group(); V.scene.add(mai);
  var ytr = YC + HC + .3;
  var dam = new T.Mesh(new T.BoxGeometry(31.6, 1.0, 13.4), da); dam.position.y = ytr + .5; mai.add(dam);
  var dai = new T.Mesh(new T.BoxGeometry(31.8, .9, 13.6), new T.MeshStandardMaterial({ color: 0xd9cdb4, roughness: .9 })); dai.position.y = ytr + 1.45; mai.add(dai);
  var tg = new T.Shape(); tg.moveTo(-6.9, 0); tg.lineTo(6.9, 0); tg.lineTo(0, 2.2); tg.lineTo(-6.9, 0);
  var tamGiac = new T.ExtrudeGeometry(tg, { depth: 31.8, bevelEnabled: false });
  var maiNgoi = new T.Mesh(tamGiac, new T.MeshStandardMaterial({ color: 0xc9b896, roughness: .9 })); maiNgoi.rotation.y = PI / 2; maiNgoi.position.set(-15.9, ytr + 1.9, 0); mai.add(maiNgoi);
  // tường điện thờ bên trong
  var dien = new T.Mesh(new T.BoxGeometry(22, HC, 8.6), new T.MeshStandardMaterial({ color: 0xe2d8c2, roughness: .9 })); dien.position.y = YC + HC / 2; V.scene.add(dien);
  V.nhan('Đền Pác-tê-nông', new T.Vector3(0, ytr + 4.6, 0), 'cam');
  V.nhan('Trên đồi cao', new T.Vector3(16, 4.6, 8), 'nho');
  V.nhan('Hàng cột đá', new T.Vector3(-15, YC + HC * .6, 6.2), 'nho');

  var hien = cot.map(function () { return 1; }), st = { xep: -1, t: 0 }, tin;
  function capNhat() { cot.forEach(function (c, k) { c.scale.y = Math.max(.001, hien[k]); c.visible = hien[k] > .01; }); var xong = hien.every(function (h) { return h > .99; }); mai.visible = xong; }
  var nDung = H.nut('Dựng hàng cột', true, function () { hien.fill(0); capNhat(); st.xep = 0; st.t = 0; MP.am('click'); V.bay([34, 18, 30], [0, 6, 0], 900);
    tin('Dựng đền Pác-tê-nông', 'Những hàng cột đá vây quanh điện thờ, đỡ phần mái phía trên.'); });
  var nLai = H.nut('Toàn cảnh', false, function () { V.bay([30, 16, 26], [0, 6, 0], 1000); MP.am('click'); });
  var nGan = H.nut('Đứng dưới hàng cột', false, function () { V.bay([-11, YC + 2, 11], [0, YC + 5, 0], 1400); MP.am('soi'); });
  H.dieuKhien(bc.phai, 'Đền Pác-tê-nông', [H.hangNut([nDung, nLai]), H.hangNut([nGan])]);
  tin = H.theTin(bc.phai);
  tin('A-ten', 'A-ten là thành bang quan trọng nhất, tiêu biểu cho chế độ dân chủ ở Hy Lạp cổ đại. Trên đồi cao là đền Pác-tê-nông.');
  H.theoSGK(bc.phai, [5]);
  V.moi(function (dt) {
    if (st.xep < 0) return;
    st.t += dt; var doi = false;
    for (var k = 0; k < cot.length; k++) { var e = MP.clamp((st.t - k * .055) / .35, 0, 1); e = 1 - Math.pow(1 - e, 3); if (hien[k] !== e) { hien[k] = e; doi = true; } }
    var cur = Math.floor(st.t / .055); if (cur !== st.cu && cur < cot.length && cur % 4 === 0) { MP.am('da', { lv: .4 }); } st.cu = cur;
    if (doi) capNhat();
    if (st.t > cot.length * .055 + .4) { st.xep = -1; capNhat(); MP.am('chuong'); }
  });

  // ---------------- sơ đồ bộ máy nhà nước A-ten (bấm từng ô)
  var so = el('section', { class: 'the-tin so-do-aten', 'aria-labelledby': 'h-bo-may', style: { marginTop: '18px' } });
  so.appendChild(el('h3', { id: 'h-bo-may' }, 'Sơ đồ bộ máy nhà nước A-ten'));
  var O = [
    { id: 'dh', ten: 'Đại hội nhân dân', phu: 'toàn bộ công dân nam từ 18 tuổi trở lên', tin: 'Đại hội nhân dân gồm toàn bộ công dân nam từ 18 tuổi trở lên, có quyền thảo luận và biểu quyết tất cả những vấn đề hệ trọng của đất nước.' },
    { id: 'h5', ten: 'Hội đồng 500 người', tin: 'Đại hội nhân dân bầu ra Hội đồng 500 người.' },
    { id: 'ta', ten: 'Toà án 6 000 thẩm phán', tin: 'Đại hội nhân dân bầu ra Toà án 6 000 thẩm phán.' },
    { id: 'tl', ten: 'Hội đồng 10 tư lệnh', tin: 'Đại hội nhân dân bầu ra Hội đồng 10 tư lệnh.' }];
  var luoiSo = el('div', { class: 'cay-bo-may' });
  var tinSo = el('p', { class: 'tin-bo-may', 'aria-live': 'polite' }, 'Chạm vào từng ô để xem.');
  function oBM(o, lop) { var b = el('button', { type: 'button', class: 'o-bm ' + lop }, el('b', null, o.ten), o.phu ? el('span', null, o.phu) : null);
    b.addEventListener('click', function () { luoiSo.querySelectorAll('.o-bm').forEach(function (x) { x.classList.toggle('dang-chon', x === b); }); tinSo.textContent = o.tin; MP.am('tick'); }); return b; }
  luoiSo.appendChild(oBM(O[0], 'goc'));
  luoiSo.appendChild(el('div', { class: 'bau', 'aria-hidden': 'true' }, 'bầu ra'));
  var hang = el('div', { class: 'hang-bm' }); O.slice(1).forEach(function (o) { hang.appendChild(oBM(o, '')); }); luoiSo.appendChild(hang);
  so.appendChild(luoiSo); so.appendChild(tinSo);
  so.appendChild(el('p', { class: 'sb-loi tr', style: { background: 'none', border: 0, padding: '6px 0 0', fontSize: '.8rem' } }, MP.trang(MP.trangCanh([7, 9]))));
  root.appendChild(so);

  // ---------------- trò bỏ phiếu bằng vỏ sò
  var vs = el('section', { class: 'the-tin vo-so', 'aria-labelledby': 'h-vo-so', style: { marginTop: '14px' } });
  vs.appendChild(el('h3', { id: 'h-vo-so' }, 'Bỏ phiếu bằng vỏ sò'));
  vs.appendChild(el('p', null, 'Một công dân bị nghi ngờ có âm mưu đe doạ nền dân chủ. Mỗi người ghi tên người đó lên mảnh vỏ sò hoặc mảnh gốm. Thả phiếu vào bình và xem khi nào đủ 6 000 phiếu.'));
  var dem = 0, thanh = el('div', { class: 'thanh-phieu' }, el('i'));
  var so_ = el('p', { class: 'so-phieu', 'aria-live': 'polite' }, '0 / 6 000 phiếu');
  var ketQua = el('p', { class: 'ket-qua-phieu', 'aria-live': 'polite' });
  function tha(n) {
    if (dem >= 6000) return;
    dem = Math.min(6000, dem + n); thanh.firstChild.style.width = (dem / 60) + '%'; so_.textContent = MP.so(dem) + ' / 6 000 phiếu'; MP.am('go', { lv: .5 });
    if (dem >= 6000) { ketQua.textContent = 'Đủ 6 000 phiếu cùng ghi tên một người: người đó buộc phải rời khỏi A-ten trong thời hạn 10 năm. Bằng cách này, người A-ten bảo vệ nền dân chủ.'; MP.am('chuong'); }
  }
  vs.appendChild(thanh); vs.appendChild(so_);
  vs.appendChild(H.hangNut([H.nut('Thả 100 phiếu', false, function () { tha(100); }), H.nut('Thả 1 000 phiếu', true, function () { tha(1000); }),
    H.nut('Làm lại', false, function () { dem = 0; thanh.firstChild.style.width = '0'; so_.textContent = '0 / 6 000 phiếu'; ketQua.textContent = ''; MP.am('click'); })]));
  vs.appendChild(ketQua);
  vs.appendChild(el('p', { class: 'sb-loi tr', style: { background: 'none', border: 0, padding: '6px 0 0', fontSize: '.8rem' } }, MP.trang(MP.trangCanh([11, 12]))));
  root.appendChild(vs);
});
