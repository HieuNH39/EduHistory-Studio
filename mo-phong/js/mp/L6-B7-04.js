/* L6-B7-04 · Kim tự tháp Kê-óp – mô hình 3D có thể bóc từng lớp đá, tách lớp, cắt một góc, xếp đá từ dưới lên.
   Dữ kiện (SGK LSĐL 6 tr. 32–33, qua kịch bản): cao 147 m; 2,3 triệu tảng đá, mỗi tảng 2,5 – 4 tấn; ghè đẽo theo kích thước
   đã định, tôi mài nhẵn, xếp chồng lên nhau, không dùng vật liệu kết dính. Mô hình giản lược: ít lớp, ít khối hơn thực tế. */
MP.onReady(function () {
  var root = MP.khung(), el = MP.el, BC = window.BaChieu;
  var luoi = el('div', { class: 'luoi-2' }), trai = el('div'), phai = el('div', { class: 'bang-dk' });
  luoi.appendChild(trai); luoi.appendChild(phai); root.appendChild(luoi);
  MP.nen(['gio']);
  var V = BC.tao(trai, { nen: 0xf1dfbd, suongMu: [70, 160], camPos: [34, 22, 40], target: [0, 8, 0], minDist: 12, maxDist: 110, nangPos: [30, 40, 18], nangManh: 2.6, hemi: 1.1, troi: 0xfff3dc, dat: 0xb08a55, moTa: 'Mô hình 3D Kim tự tháp Kê-óp. Kéo để xoay, cuộn hoặc chụm để phóng to. Chạm vào một tảng đá để xem thông tin.' });
  if (!V) return;
  var T = V.T, rnd = BC.rngSo(7);

  // ---- mặt đất (cát) và vài đụn cát xa
  var dat = new T.Mesh(new T.CircleGeometry(160, 64), new T.MeshStandardMaterial({ color: 0xe2c690, roughness: 1 }));
  dat.rotation.x = -Math.PI / 2; V.scene.add(dat);
  for (var d = 0; d < 9; d++) {
    var dun = new T.Mesh(new T.SphereGeometry(10 + rnd() * 12, 24, 12), new T.MeshStandardMaterial({ color: 0xdcbd84, roughness: 1 }));
    var a = d / 9 * Math.PI * 2 + rnd(); dun.scale.y = 0.18; dun.position.set(Math.cos(a) * (75 + rnd() * 30), -1, Math.sin(a) * (75 + rnd() * 30)); V.scene.add(dun);
  }

  // ---- các lớp đá: N lớp, mỗi lớp lùi vào một khối mỗi cạnh
  var N = 16, S = 2 * N - 1, H = 1.27, GAP = 0.05, khoi = [];
  for (var i = 0; i < N; i++) {
    var n = S - 2 * i;
    for (var x = 0; x < n; x++) for (var z = 0; z < n; z++) khoi.push({ lop: i, x: x - (n - 1) / 2, z: z - (n - 1) / 2 });
  }
  var geo = new T.BoxGeometry(1 - GAP, H - GAP, 1 - GAP);
  var mat = new T.MeshStandardMaterial({ color: 0xffffff, roughness: 0.92, metalness: 0 });
  var im = new T.InstancedMesh(geo, mat, khoi.length);
  var mauGoc = [];
  khoi.forEach(function (k, idx) { var c = BC.bienMau(0xd8b77f, 0.12, rnd); mauGoc.push(c); im.setColorAt(idx, c); });
  V.scene.add(im);
  var dinh = N * H;

  // trạng thái từng lớp: nhac (0 = đúng chỗ, 1 = đã bóc đi), tach (tách lớp), cat (cắt góc), xep (xếp từ dưới lên)
  var st = { boc: 0, tach: 0, cat: false, xep: -1 }, nhac = new Array(N).fill(0), hienLop = new Array(N).fill(1);
  var M = new T.Matrix4(), Q = new T.Quaternion(), P = new T.Vector3(), SC = new T.Vector3();
  function capNhatKhoi() {
    for (var j = 0; j < khoi.length; j++) {
      var k = khoi[j], L = k.lop, lift = nhac[L], h = hienLop[L];
      var catGoc = st.cat && k.x > 0 && k.z > 0;
      var s = catGoc ? 0 : (1 - lift) * h;
      P.set(k.x, L * H + H / 2 + L * st.tach * 1.1 + lift * 14 + (1 - h) * 9, k.z);
      SC.set(s, s, s); M.compose(P, Q, SC); im.setMatrixAt(j, M);
    }
    im.instanceMatrix.needsUpdate = true;
  }
  capNhatKhoi();

  // ---- thước chiều cao 147 m
  var thuoc = new T.Group(), ox = -S / 2 - 2.2;
  var vl = new T.Mesh(new T.CylinderGeometry(0.08, 0.08, dinh, 8), new T.MeshBasicMaterial({ color: 0xb8261e }));
  vl.position.set(ox, dinh / 2, 0); thuoc.add(vl);
  [0, dinh].forEach(function (yy) { var t = new T.Mesh(new T.BoxGeometry(1.4, 0.1, 0.1), new T.MeshBasicMaterial({ color: 0xb8261e })); t.position.set(ox, yy, 0); thuoc.add(t); });
  V.scene.add(thuoc);
  var nhanCao = V.nhan('Cao 147 m', new T.Vector3(ox, dinh / 2, 0), 'do');
  V.nhan('Đỉnh kim tự tháp', new T.Vector3(0, dinh + 0.6, 0), 'nho');
  var nhanKhoi = V.nhan('', null, 'cam');

  // ---- bảng điều khiển
  function truot(nhan, min, max, step, val, fmt) {
    var r = el('input', { type: 'range', min: min, max: max, step: step, value: val });
    var o = el('output', null, fmt(val)); MP.toThanh(r);
    var w = el('label', { class: 'nhan-truot' }, el('span', null, nhan), r, o);
    r.addEventListener('input', function () { o.textContent = fmt(+r.value); MP.toThanh(r); });
    return { w: w, r: r, o: o };
  }
  var tBoc = truot('Bóc lớp đá', 0, N - 1, 1, 0, function (v) { return v + '/' + (N - 1); });
  var tTach = truot('Tách các lớp', 0, 100, 1, 0, function (v) { return v + '%'; });
  var cat = el('input', { type: 'checkbox' });
  var nutXep = el('button', { type: 'button', class: 'nut chinh' }, 'Xếp đá từ dưới lên');
  var nutLai = el('button', { type: 'button', class: 'nut' }, 'Đặt lại');
  var tin = el('div', { class: 'the-tin', 'aria-live': 'polite' });
  phai.appendChild(el('div', { class: 'the-tin' }, el('h3', null, 'Điều khiển'), tBoc.w, tTach.w,
    el('label', { class: 'hop-chon', style: { margin: '6px 0' } }, cat, 'Cắt một góc để xem bên trong'),
    el('div', { class: 'hang-nut', style: { marginTop: '8px' } }, nutXep, nutLai)));
  phai.appendChild(tin);
  var facts = el('div', { class: 'the-tin' }, el('h3', null, 'Theo SGK'));
  var ul = el('ul'); MP.loi([9]).concat([MP.canh(8).loi[1]], MP.loi([11])).forEach(function (l) { if (l) ul.appendChild(el('li', null, l)); });
  facts.appendChild(ul); facts.appendChild(el('p', { class: 'sb-loi tr', style: { background: 'none', border: 0, padding: '6px 0 0', fontSize: '.8rem' } }, MP.trang(MP.trangCanh([8, 9, 11]))));
  phai.appendChild(facts);
  function datTin(tieuDe, noiDung) { tin.innerHTML = ''; tin.appendChild(el('h3', null, tieuDe)); [].concat(noiDung).forEach(function (p) { tin.appendChild(el('p', null, p)); }); }
  datTin('Bóc tách kim tự tháp', 'Kéo thanh “Bóc lớp đá” để gỡ dần các lớp từ đỉnh xuống: mỗi lớp là các tảng đá đặt sát nhau, lớp trên chồng lên lớp dưới.');

  var bocCu = 0;
  tBoc.r.addEventListener('input', function () {
    st.boc = +tBoc.r.value;
    if (st.boc !== bocCu) { MP.am(st.boc > bocCu ? 'da' : 'soi', { lv: 0.7 }); bocCu = st.boc; }
    datTin('Lớp đá thứ ' + (N - st.boc) + ' (tính từ dưới lên)', ['Các tảng đá được ghè đẽo theo kích thước đã định, tôi mài nhẵn rồi xếp sát nhau thành từng lớp.', 'Giữa các tảng đá không có vật liệu kết dính: chúng đứng vững nhờ được xếp chồng khít lên nhau.']);
  });
  tTach.r.addEventListener('input', function () { st.tach = tTach.r.value / 100; capNhatKhoi(); MP.am('soi'); });
  tTach.r.addEventListener('change', function () { MP.am('da', { lv: 0.5 }); });
  cat.addEventListener('change', function () {
    st.cat = cat.checked; capNhatKhoi(); MP.am(cat.checked ? 'soi' : 'da');
    if (cat.checked) { datTin('Nhìn vào bên trong', 'Bên trong cũng là các lớp đá xếp chồng lên nhau, không dùng bất cứ vật liệu kết dính nào.'); V.bay([26, 18, 26], [0, 6, 0], 1200); }
  });
  nutLai.addEventListener('click', function () {
    st.boc = 0; st.tach = 0; st.cat = false; st.xep = -1; tBoc.r.value = 0; tTach.r.value = 0; cat.checked = false;
    [tBoc, tTach].forEach(function (t) { t.r.dispatchEvent(new Event('input')); });
    hienLop.fill(1); capNhatKhoi(); V.bay([34, 22, 40], [0, 8, 0], 1000); MP.am('click');
  });
  nutXep.addEventListener('click', function () {
    st.boc = 0; tBoc.r.value = 0; tBoc.o.textContent = '0/' + (N - 1); MP.toThanh(tBoc.r);
    hienLop.fill(0); st.xep = 0; st.xepT = 0; MP.am('click');
    datTin('Xếp đá từ dưới lên', 'Từng lớp đá được xếp chồng lên lớp dưới, không dùng chất kết dính. Mô hình chỉ có ' + N + ' lớp và ' + MP.so(khoi.length) + ' khối – công trình thật dùng tới 2,3 triệu tảng đá.');
  });

  // chạm vào một tảng đá
  var ray = new T.Raycaster(), ndc = new T.Vector2(), chon = -1, down = null;
  V.renderer.domElement.addEventListener('pointerdown', function (e) { down = [e.clientX, e.clientY]; });
  V.renderer.domElement.addEventListener('pointerup', function (e) {
    if (!down || Math.hypot(e.clientX - down[0], e.clientY - down[1]) > 6) return;
    var r = V.renderer.domElement.getBoundingClientRect();
    ndc.set((e.clientX - r.left) / r.width * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
    ray.setFromCamera(ndc, V.camera);
    var hit = ray.intersectObject(im)[0];
    if (chon >= 0) { im.setColorAt(chon, mauGoc[chon]); }
    if (hit && hit.instanceId != null) {
      chon = hit.instanceId; im.setColorAt(chon, new T.Color(0xf26b1d)); im.instanceColor.needsUpdate = true;
      nhanKhoi.el.textContent = 'Một tảng đá: nặng 2,5 – 4 tấn'; nhanKhoi.pos = hit.point.clone(); nhanKhoi.hien = true;
      datTin('Một tảng đá', ['Để xây kim tự tháp Kê-óp, người ta dùng tới 2,3 triệu tảng đá, mỗi tảng nặng từ 2,5 đến 4 tấn.', 'Tảng đá được ghè đẽo theo kích thước đã định và tôi mài nhẵn.']);
      MP.am('chuong_nho');
    } else { chon = -1; nhanKhoi.hien = false; im.instanceColor.needsUpdate = true; }
  });
  nhanKhoi.hien = false;

  // ---- vòng lặp: hoạt hoạ bóc lớp và xếp đá
  V.moi(function (dt) {
    var doi = false;
    for (var L = 0; L < N; L++) {
      var dich = L >= N - st.boc ? 1 : 0;
      if (Math.abs(nhac[L] - dich) > 0.001) { nhac[L] += (dich - nhac[L]) * Math.min(1, dt * 6); if (Math.abs(nhac[L] - dich) < 0.002) nhac[L] = dich; doi = true; }
    }
    if (st.xep >= 0) {
      st.xepT += dt;
      var L2 = Math.floor(st.xepT / 0.42);
      for (var q = 0; q < N; q++) {
        var k = MP.clamp((st.xepT - q * 0.42) / 0.38, 0, 1);
        var e = k < 1 ? 1 - Math.pow(1 - k, 3) : 1;
        if (hienLop[q] !== e) { hienLop[q] = e; doi = true; }
      }
      if (L2 > st.xepCu || st.xepCu == null) { if (L2 < N) MP.am('da', { lv: 0.55 + 0.45 * (1 - L2 / N) }); st.xepCu = L2; }
      if (st.xepT > N * 0.42 + 0.4) { st.xep = -1; st.xepCu = null; MP.am('chuong'); V.bang('Kim tự tháp Kê-óp cao tới 147 m', true); setTimeout(function () { V.bang('', false); }, 3500); }
    }
    if (doi) capNhatKhoi();
    nhanCao.hien = st.boc === 0 && st.tach === 0;
  });
});
