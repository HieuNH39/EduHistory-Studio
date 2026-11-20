/* EduHistory Studio – khung dựng mô hình 3D dùng chung (Three.js r187 gói sẵn trong vendor/three.min.js, chạy ngoại tuyến).
   Tạo cảnh, máy quay, điều khiển xoay (OrbitControls), nhãn chữ HTML gắn với điểm 3D, chuyển cảnh máy quay mượt. */
(function () {
  'use strict';
  var T = window.THREE;

  function coWebGL() {
    try { var c = document.createElement('canvas'); return !!(window.WebGLRenderingContext && (c.getContext('webgl2') || c.getContext('webgl'))); } catch (e) { return false; }
  }

  function tao(container, opts) {
    opts = opts || {};
    var el = MP.el;
    var box = el('div', { class: 'ba-chieu', tabindex: '0', 'aria-label': opts.moTa || 'Mô hình 3D. Kéo để xoay, cuộn hoặc chụm hai ngón để phóng to.' });
    var labelsEl = el('div', { class: 'nhan-3d', 'aria-hidden': 'true' });
    var goiY = el('div', { class: 'goi-y-3d' }, opts.goiY || 'Kéo để xoay · Cuộn/chụm để phóng to');
    var bang = el('div', { class: 'bang-3d', style: { opacity: 0 } });
    container.appendChild(box);
    if (!T || !coWebGL()) {
      box.style.height = '220px'; box.style.display = 'grid'; box.style.placeItems = 'center';
      box.appendChild(el('p', { class: 'bao-loi' }, 'Trình duyệt hoặc máy này chưa hỗ trợ WebGL nên không hiển thị được mô hình 3D. Hãy thử trình duyệt Chrome, Edge, Firefox hoặc Safari bản mới.'));
      return null;
    }
    var renderer;
    try { renderer = new T.WebGLRenderer({ antialias: true, alpha: false, powerPreference: 'high-performance' }); }
    catch (e) { box.appendChild(el('p', { class: 'bao-loi' }, 'Không khởi tạo được WebGL trên máy này.')); return null; }
    renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
    renderer.outputColorSpace = T.SRGBColorSpace;
    renderer.toneMapping = T.ACESFilmicToneMapping; renderer.toneMappingExposure = opts.phoiSang || 1.05;
    if (opts.bong) { renderer.shadowMap.enabled = true; renderer.shadowMap.type = T.PCFSoftShadowMap; }
    box.appendChild(renderer.domElement); box.appendChild(labelsEl); box.appendChild(goiY); box.appendChild(bang);

    var scene = new T.Scene();
    scene.background = new T.Color(opts.nen || 0xdfe9ee);
    if (opts.suongMu) scene.fog = new T.Fog(opts.nen || 0xdfe9ee, opts.suongMu[0], opts.suongMu[1]);
    var camera = new T.PerspectiveCamera(opts.fov || 45, 1.6, opts.gan || 0.1, opts.xa || 500);
    camera.position.set.apply(camera.position, opts.camPos || [10, 8, 12]);
    var controls = new T.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true; controls.dampingFactor = 0.08;
    controls.target.set.apply(controls.target, opts.target || [0, 0, 0]);
    if (opts.minDist) controls.minDistance = opts.minDist;
    if (opts.maxDist) controls.maxDistance = opts.maxDist;
    controls.maxPolarAngle = opts.maxPolar == null ? Math.PI * 0.49 : opts.maxPolar;
    controls.screenSpacePanning = true;
    controls.update();

    var hemi = new T.HemisphereLight(opts.troi || 0xeaf3ff, opts.dat || 0x8a7a5a, opts.hemi == null ? 1.3 : opts.hemi); scene.add(hemi);
    var sun = new T.DirectionalLight(opts.nang || 0xfff1d6, opts.nangManh == null ? 2.2 : opts.nangManh);
    sun.position.set.apply(sun.position, opts.nangPos || [12, 20, 10]); scene.add(sun);
    if (opts.bong) {
      sun.castShadow = true; sun.shadow.mapSize.set(1024, 1024);
      var sc = opts.bongKhung || 20; sun.shadow.camera.left = -sc; sun.shadow.camera.right = sc; sun.shadow.camera.top = sc; sun.shadow.camera.bottom = -sc; sun.shadow.camera.far = 80; sun.shadow.bias = -0.0005;
    }

    var V = { T: T, scene: scene, camera: camera, renderer: renderer, controls: controls, el: box, sun: sun, hemi: hemi, labels: [], ticks: [], t: 0, visible: true, bangEl: bang };
    var ar = opts.tiLe || 16 / 10;
    function resize() {
      var w = box.clientWidth || 600, small = w < 600, a = small ? (opts.tiLeNho || Math.min(ar, 1.05)) : ar;
      var h = Math.round(Math.max(300, Math.min(w / a, window.innerHeight * (opts.caoToiDa || 0.72))));
      box.style.height = h + 'px';
      renderer.setSize(w, h, false); renderer.domElement.style.width = w + 'px'; renderer.domElement.style.height = h + 'px';
      camera.aspect = w / h; camera.fov = (w / h < 1.25 ? (opts.fovNho || 60) : (opts.fov || 45)); camera.updateProjectionMatrix(); V.w = w; V.h = h;   // màn hình hẹp: góc nhìn rộng hơn
    }
    if ('ResizeObserver' in window) new ResizeObserver(resize).observe(box); else window.addEventListener('resize', resize);
    resize();
    var daTuongTac = false;
    controls.addEventListener('start', function () { if (!daTuongTac) { daTuongTac = true; goiY.style.opacity = 0; } V.huyBay(); });

    /** Nhãn chữ HTML gắn với một điểm 3D (hoặc hàm trả về điểm). cls: cam | do | cham | nuoc | nho | phang */
    V.nhan = function (text, pos, cls, opt) {
      var d = el('div', { class: 'nh ' + (cls || '') }, text);
      labelsEl.appendChild(d);
      var L = { el: d, pos: pos, hien: true, opt: opt || {} };
      V.labels.push(L); return L;
    };
    var v3 = new T.Vector3(), camDir = new T.Vector3();
    function capNhatNhan() {
      camera.getWorldDirection(camDir);
      V.labels.forEach(function (L) {
        if (!L.hien) { L.el.classList.add('an'); return; }
        var p = typeof L.pos === 'function' ? L.pos() : L.pos;
        if (!p) { L.el.classList.add('an'); return; }
        v3.copy(p);
        if (L.opt.che && L.opt.che(v3, camera)) { L.el.classList.add('an'); return; }
        var dx = v3.x - camera.position.x, dy = v3.y - camera.position.y, dz = v3.z - camera.position.z;
        if (dx * camDir.x + dy * camDir.y + dz * camDir.z <= 0) { L.el.classList.add('an'); return; }
        v3.project(camera);
        if (Math.abs(v3.x) > 1.15 || Math.abs(v3.y) > 1.15) { L.el.classList.add('an'); return; }
        L.el.classList.remove('an');
        L.el.style.left = ((v3.x + 1) / 2 * V.w).toFixed(1) + 'px'; L.el.style.top = ((1 - v3.y) / 2 * V.h).toFixed(1) + 'px';
        if (L.opt.mo != null) L.el.style.opacity = L.opt.mo;
      });
    }
    /** Bay máy quay tới vị trí mới (đồng thời đổi điểm nhìn) trong ms mili giây */
    var bay = null;
    V.bay = function (pos, target, ms) {
      bay = { p0: camera.position.clone(), p1: new T.Vector3().fromArray(pos), t0: controls.target.clone(), t1: new T.Vector3().fromArray(target), t: 0, d: (ms || 1200) / 1000 };
    };
    V.huyBay = function () { bay = null; };
    V.moi = function (fn) { V.ticks.push(fn); };
    V.bang = function (text, hien) { bang.textContent = text || ''; bang.style.opacity = hien ? 1 : 0; };

    var tCu = performance.now(), clock = { getDelta: function () { var n = performance.now(), d = (n - tCu) / 1000; tCu = n; return d; } };
    function loop() {
      if (!V.visible) { V.raf = 0; return; }
      V.raf = requestAnimationFrame(loop);
      var dt = Math.min(0.1, clock.getDelta()); V.t += dt;
      if (bay) {
        bay.t += dt; var k = MP.ease(bay.t / bay.d);
        camera.position.lerpVectors(bay.p0, bay.p1, k); controls.target.lerpVectors(bay.t0, bay.t1, k);
        if (bay.t >= bay.d) bay = null;
      }
      for (var i = 0; i < V.ticks.length; i++) V.ticks[i](dt, V.t);
      controls.update();
      renderer.render(scene, camera);
      capNhatNhan();
    }
    MP.khiHien(box, function (v) { V.visible = v; if (v && !V.raf) { clock.getDelta(); loop(); } });
    document.addEventListener('visibilitychange', function () { V.visible = !document.hidden; if (V.visible && !V.raf) { clock.getDelta(); loop(); } });
    loop();
    (window.MP_3D = window.MP_3D || []).push(V);   // để kiểm thử tự động / gỡ lỗi
    MP.fontReady.then(function () { capNhatNhan(); });
    return V;
  }

  /** Chuẩn hoá màu ngẫu nhiên quanh một màu gốc (dùng cho đá, đất) */
  function bienMau(hex, d, rnd) {
    var c = new T.Color(hex), hsl = {}; c.getHSL(hsl);
    c.setHSL(hsl.h + (rnd() - 0.5) * d * 0.15, MP.clamp(hsl.s + (rnd() - 0.5) * d * 0.4, 0, 1), MP.clamp(hsl.l + (rnd() - 0.5) * d, 0, 1));
    return c;
  }
  function rngSo(seed) { var s = seed >>> 0; return function () { s = (s + 0x6D2B79F5) >>> 0; var t = Math.imul(s ^ (s >>> 15), s | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }

  /** Dải băng theo đường (dùng cho sông, hào nước): pts = [[x,z],...], rộng w, cao y */
  function dai(pts, w, y, close) {
    var pos = [], idx = [], n = pts.length, i;
    for (i = 0; i < n; i++) {
      var a = pts[(i - 1 + n) % n], b = pts[(i + 1) % n];
      if (!close) { a = pts[Math.max(0, i - 1)]; b = pts[Math.min(n - 1, i + 1)]; }
      var tx = b[0] - a[0], tz = b[1] - a[1], l = Math.hypot(tx, tz) || 1, nx = -tz / l, nz = tx / l;
      var ww = typeof w === 'function' ? w(i) : w;
      pos.push(pts[i][0] + nx * ww / 2, y, pts[i][1] + nz * ww / 2, pts[i][0] - nx * ww / 2, y, pts[i][1] - nz * ww / 2);
    }
    var m = close ? n : n - 1;
    for (i = 0; i < m; i++) { var j = (i + 1) % n; idx.push(i * 2, j * 2, i * 2 + 1, i * 2 + 1, j * 2, j * 2 + 1); }
    var g = new T.BufferGeometry(); g.setAttribute('position', new T.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals();
    return g;
  }
  /** Catmull–Rom 2D (khép kín hoặc không) */
  function lamMuot(pts, n, close) {
    var P = close ? [pts[pts.length - 1]].concat(pts, [pts[0], pts[1]]) : [pts[0]].concat(pts, [pts[pts.length - 1]]), out = [];
    for (var i = 1; i < P.length - 2; i++) {
      var p0 = P[i - 1], p1 = P[i], p2 = P[i + 1], p3 = P[i + 2];
      for (var k = 0; k < n; k++) {
        var t = k / n, t2 = t * t, t3 = t2 * t;
        out.push([0, 1].map(function (c) { return 0.5 * ((2 * p1[c]) + (-p0[c] + p2[c]) * t + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * t2 + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * t3); }));
      }
    }
    if (!close) out.push(pts[pts.length - 1].slice());
    return out;
  }

  window.BaChieu = { tao: tao, bienMau: bienMau, rngSo: rngSo, dai: dai, lamMuot: lamMuot };
})();
