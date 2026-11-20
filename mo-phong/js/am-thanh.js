/* EduHistory Studio – Âm thanh mô phỏng, tổng hợp hoàn toàn bằng Web Audio API (không tệp âm thanh, không gọi mạng).
   - Chỉ phát sau lần tương tác đầu tiên của người dùng (quy tắc tự phát của trình duyệt).
   - Có nút bật/tắt và thanh âm lượng; mặc định âm lượng vừa phải, không có tiếng chói, giật mình.
   - Nền âm (lặp): nuoc, song_bien, gio, lua, dam_dong, con_trung, chim, dong_co, phao_xa, dong_ho, nen_em, banh_xe_nuoc, may_hoi
   - Âm sự kiện: trong, trong_nho, vut, vut_nhe, buoc_quan, ngua, mai_cheo, te_nuoc, cot_ket, keo_ket, gay_go, go, no, no_xa, lua_bung,
     chuong, chuong_nho, sai, click, xac_nhan, tick, mo_pha, reo, chuong_tau, hoi_nuoc, cach, da, soi, dat, lat_trang, soat
   Dùng: AT.nen(['nuoc','gio']); AT.phat('trong', {n: 3}); AT.ui(khung) – thêm nút âm thanh. */
(function () {
  'use strict';
  var AT = { san_sang: false, tat: false, luong: 0.7 };
  try { var l = localStorage.getItem('mp-am-luong'); if (l != null) AT.luong = Math.max(0, Math.min(1, +l)); AT.tat = localStorage.getItem('mp-am-tat') === '1'; } catch (e) { /* bỏ qua */ }
  var Ctor = window.AudioContext || window.webkitAudioContext;
  var ctx = null, master = null, bedBus = null, fxBus = null, BUF = {}, beds = {}, want = [], last = {}, burst = [], uiList = [];

  function now() { return ctx.currentTime; }
  function mkNoise(kind, sec) {
    var n = Math.floor(ctx.sampleRate * sec), b = ctx.createBuffer(1, n, ctx.sampleRate), d = b.getChannelData(0), i;
    if (kind === 'trang') for (i = 0; i < n; i++) d[i] = Math.random() * 2 - 1;
    else if (kind === 'hong') {   // nhiễu hồng (bộ lọc Paul Kellet)
      var b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0;
      for (i = 0; i < n; i++) { var w = Math.random() * 2 - 1; b0 = 0.99886 * b0 + w * 0.0555179; b1 = 0.99332 * b1 + w * 0.0750759; b2 = 0.96900 * b2 + w * 0.1538520; b3 = 0.86650 * b3 + w * 0.3104856; b4 = 0.55000 * b4 + w * 0.5329522; b5 = -0.7616 * b5 - w * 0.0168980; d[i] = (b0 + b1 + b2 + b3 + b4 + b5 + b6 + w * 0.5362) * 0.11; b6 = w * 0.115926; }
    } else {   // nhiễu nâu
      var lastv = 0; for (i = 0; i < n; i++) { var w2 = Math.random() * 2 - 1; lastv = (lastv + 0.02 * w2) / 1.02; d[i] = lastv * 3.5; }
    }
    return b;
  }
  function tao() {
    if (ctx || !Ctor) return;
    try { ctx = new Ctor(); } catch (e) { ctx = null; return; }
    var comp = ctx.createDynamicsCompressor();
    comp.threshold.value = -16; comp.knee.value = 12; comp.ratio.value = 4; comp.attack.value = 0.01; comp.release.value = 0.25;
    master = ctx.createGain(); master.gain.value = AT.tat ? 0 : AT.luong * 0.9;
    bedBus = ctx.createGain(); fxBus = ctx.createGain(); bedBus.connect(master); fxBus.connect(master);
    master.connect(comp); comp.connect(ctx.destination);
    BUF.trang = mkNoise('trang', 2); BUF.hong = mkNoise('hong', 4); BUF.nau = mkNoise('nau', 4);
    AT.san_sang = true; datNen(want);
    uiList.forEach(capNhatUi);
  }
  function moKhoa() {
    if (!Ctor) return;
    if (!ctx) tao();
    if (ctx && ctx.state === 'suspended') ctx.resume();
  }
  ['pointerdown', 'keydown', 'touchend'].forEach(function (ev) { document.addEventListener(ev, moKhoa, { capture: true, passive: true }); });
  document.addEventListener('visibilitychange', function () { if (!ctx) return; if (document.hidden) ctx.suspend(); else if (!AT.tat) ctx.resume(); });

  // ---------------------------------------------------------------- khối dựng âm
  function G(v, dest) { var g = ctx.createGain(); g.gain.value = v == null ? 1 : v; if (dest) g.connect(dest); return g; }
  function src(buf, loop, t0, dur) {
    var s = ctx.createBufferSource(); s.buffer = BUF[buf]; s.loop = !!loop;
    var off = Math.random() * (s.buffer.duration - 0.5);
    s.start(t0, Math.max(0, off)); if (dur) s.stop(t0 + dur + 0.05);
    return s;
  }
  function F(type, f, q, dest) { var b = ctx.createBiquadFilter(); b.type = type; b.frequency.value = f; if (q != null) b.Q.value = q; if (dest) b.connect(dest); return b; }
  function O(type, f, t0, dur) { var o = ctx.createOscillator(); o.type = type; o.frequency.setValueAtTime(f, t0); o.start(t0); o.stop(t0 + dur + 0.05); return o; }
  /** đường bao: lên trong a giây tới đỉnh p, tắt dần (mũ) tới t0+dur */
  function env(g, t0, a, p, dur) {
    g.gain.setValueAtTime(0.0001, t0); g.gain.linearRampToValueAtTime(p, t0 + a); g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
  }
  function lfo(f, depth, param, type) { var o = ctx.createOscillator(); o.type = type || 'sine'; o.frequency.value = f; var g = G(depth); o.connect(g); g.connect(param); o.start(); return o; }
  function noiseHit(t0, buf, ftype, freq, q, peak, a, dur, dest) {
    var g = G(0, dest), f = F(ftype, freq, q, g), s = src(buf, false, t0, dur); s.connect(f); env(g, t0, a, peak, dur); return { g: g, f: f, s: s };
  }
  function tone(t0, type, f, peak, a, dur, dest, fEnd) {
    var g = G(0, dest), o = O(type, f, t0, dur); if (fEnd) o.frequency.exponentialRampToValueAtTime(fEnd, t0 + dur * 0.8); o.connect(g); env(g, t0, a, peak, dur); return o;
  }
  function crackle(t0, dest, lv) { noiseHit(t0, 'trang', 'highpass', 1800 + Math.random() * 2000, 0.7, (0.012 + Math.random() * 0.045) * (lv || 1), 0.001, 0.008 + Math.random() * 0.02, dest); }

  // ---------------------------------------------------------------- âm sự kiện
  var SFX = {
    trong: function (t, d, o) {
      var n = o.n || 3, gap = o.gap || 0.34, lv = o.lv || 1;
      for (var i = 0; i < n; i++) {
        var ti = t + i * gap, k = (i === n - 1 ? 1.12 : 0.92) * lv;
        tone(ti, 'sine', 118, 0.34 * k, 0.004, 0.6, d, 46);
        tone(ti, 'triangle', 190, 0.06 * k, 0.003, 0.18, d, 95);
        noiseHit(ti, 'trang', 'bandpass', 900, 0.8, 0.07 * k, 0.002, 0.06, d);
      }
    },
    trong_nho: function (t, d) { SFX.trong(t, d, { n: 1, lv: 0.6 }); },
    vut: function (t, d, o) {
      var lv = o.lv || 1, h = noiseHit(t, 'trang', 'bandpass', 380, 1.3, 0.15 * lv, 0.22, 0.7, d);
      h.f.frequency.exponentialRampToValueAtTime(2100, t + 0.3); h.f.frequency.exponentialRampToValueAtTime(520, t + 0.68);
    },
    vut_nhe: function (t, d) { SFX.vut(t, d, { lv: 0.55 }); },
    buoc_quan: function (t, d, o) { for (var i = 0; i < (o.n || 6); i++) noiseHit(t + i * 0.21, 'nau', 'lowpass', 190, 0.7, (i % 2 ? 0.075 : 0.1) * (o.lv || 1), 0.006, 0.16, d); },
    ngua: function (t, d) { for (var r = 0; r < 4; r++) [0, 0.09, 0.18].forEach(function (x, i) { noiseHit(t + r * 0.46 + x, 'nau', 'lowpass', 320, 0.8, 0.06 + i * 0.012, 0.004, 0.08, d); }); },
    mai_cheo: function (t, d) { for (var i = 0; i < 3; i++) { var h = noiseHit(t + i * 0.55, 'trang', 'bandpass', 950, 0.9, 0.06, 0.05, 0.4, d); h.f.frequency.exponentialRampToValueAtTime(480, t + i * 0.55 + 0.35); } },
    te_nuoc: function (t, d, o) {
      var lv = o.lv || 1, h = noiseHit(t, 'trang', 'lowpass', 4200, 0.6, 0.2 * lv, 0.008, 0.8, d);
      h.f.frequency.exponentialRampToValueAtTime(320, t + 0.7);
      for (var i = 0; i < 5; i++) tone(t + 0.1 + Math.random() * 0.5, 'sine', 500 + Math.random() * 600, 0.025 * lv, 0.004, 0.05, d, 1100 + Math.random() * 600);
    },
    cot_ket: function (t, d) {
      var g = G(0, d), bp = F('bandpass', 650, 7, g), o = O('sawtooth', 82, t, 1.0);
      var l = ctx.createOscillator(), lg = G(14); l.frequency.value = 6.5; l.connect(lg); lg.connect(o.frequency); l.start(t); l.stop(t + 1.05);
      o.connect(bp);
      g.gain.setValueAtTime(0.0001, t); g.gain.linearRampToValueAtTime(0.11, t + 0.15); g.gain.linearRampToValueAtTime(0.07, t + 0.6); g.gain.exponentialRampToValueAtTime(0.0001, t + 0.95);
      SFX.gay_go(t + 0.72, d, {});
    },
    keo_ket: function (t, d) {   // tiếng gỗ thuyền kẽo kẹt nhẹ (không có tiếng gãy)
      var g = G(0, d), bp = F('bandpass', 560 + Math.random() * 200, 8, g), o = O('sawtooth', 70 + Math.random() * 25, t, 0.9);
      var l = ctx.createOscillator(), lg = G(10); l.frequency.value = 5 + Math.random() * 3; l.connect(lg); lg.connect(o.frequency); l.start(t); l.stop(t + 0.95);
      o.connect(bp); g.gain.setValueAtTime(0.0001, t); g.gain.linearRampToValueAtTime(0.055, t + 0.25); g.gain.exponentialRampToValueAtTime(0.0001, t + 0.85);
    },
    gay_go: function (t, d) {
      noiseHit(t, 'trang', 'highpass', 1400, 0.7, 0.24, 0.001, 0.08, d);
      noiseHit(t + 0.05, 'trang', 'highpass', 2000, 0.7, 0.12, 0.001, 0.05, d);
      noiseHit(t, 'nau', 'lowpass', 230, 0.7, 0.2, 0.003, 0.3, d);
    },
    go: function (t, d) { for (var i = 0; i < 3; i++) { tone(t + i * 0.15, 'sine', 430, 0.09, 0.002, 0.1, d, 300); noiseHit(t + i * 0.15, 'trang', 'bandpass', 2100, 1, 0.035, 0.001, 0.025, d); } },
    no: function (t, d, o) {
      var lv = o.lv || 1, h = noiseHit(t, 'nau', 'lowpass', o.xa ? 260 : 620, 0.5, 0.3 * lv, 0.018, 1.6, d);
      h.f.frequency.exponentialRampToValueAtTime(90, t + 1.2);
      tone(t, 'sine', o.xa ? 48 : 58, 0.24 * lv, 0.012, 1.1, d, 30);
      if (!o.xa) noiseHit(t, 'trang', 'lowpass', 1600, 0.5, 0.05 * lv, 0.004, 0.25, d);
    },
    no_xa: function (t, d) { SFX.no(t, d, { xa: true, lv: 0.45 }); },
    lua_bung: function (t, d) {
      var h = noiseHit(t, 'hong', 'bandpass', 250, 0.7, 0.16, 0.35, 1.3, d);
      h.f.frequency.exponentialRampToValueAtTime(1100, t + 0.8);
      for (var i = 0; i < 14; i++) crackle(t + 0.2 + Math.random() * 1.1, d, 1.2);
    },
    chuong: function (t, d) { [1046.5, 1318.5, 1568].forEach(function (f, i) { tone(t + i * 0.09, 'sine', f, 0.1, 0.006, 1.1, d); tone(t + i * 0.09, 'sine', f * 2, 0.025, 0.004, 0.5, d); }); },
    chuong_nho: function (t, d) { tone(t, 'sine', 1318.5, 0.055, 0.004, 0.6, d); tone(t, 'sine', 1975.5, 0.025, 0.003, 0.35, d); },
    sai: function (t, d) { var g = G(1, d), f = F('lowpass', 1400, 0.7, g); tone(t, 'triangle', 311, 0.075, 0.01, 0.2, f); tone(t + 0.16, 'triangle', 233, 0.075, 0.01, 0.3, f); },
    click: function (t, d) { tone(t, 'sine', 1000, 0.04, 0.002, 0.04, d); },
    xac_nhan: function (t, d) { tone(t, 'sine', 660, 0.055, 0.004, 0.09, d); tone(t + 0.07, 'sine', 990, 0.055, 0.004, 0.14, d); },
    tick: function (t, d, o) { tone(t, 'sine', o.f || 1800, 0.022, 0.001, 0.02, d); },
    mo_pha: function (t, d) { [[220, 0.08, 2.2], [607, 0.025, 1.4], [1188, 0.012, 0.8]].forEach(function (p) { tone(t, 'sine', p[0], p[1], 0.012, p[2], d); }); },
    reo: function (t, d, o) {
      var lv = o.lv || 1, g = G(0, d), s = src('hong', false, t, 3.2);
      [[600, 2], [1150, 2.5], [2500, 3]].forEach(function (p) { var f = F('bandpass', p[0], p[1], g); s.connect(f); });
      var l = ctx.createOscillator(), lg = G(0.03 * lv); l.frequency.value = 8.5; l.connect(lg); lg.connect(g.gain); l.start(t); l.stop(t + 3.2);
      g.gain.setValueAtTime(0.0001, t); g.gain.linearRampToValueAtTime(0.12 * lv, t + 0.6); g.gain.linearRampToValueAtTime(0.09 * lv, t + 1.7); g.gain.exponentialRampToValueAtTime(0.0001, t + 3.1);
    },
    chuong_tau: function (t, d) { [[784, 0.07, 1.8], [1882, 0.025, 0.9], [3058, 0.01, 0.4]].forEach(function (p) { tone(t, 'sine', p[0], p[1], 0.003, p[2], d); }); },
    hoi_nuoc: function (t, d, o) { var g = G(1, d), h = F('highpass', 1500, 0.7, g); var x = noiseHit(t, 'trang', 'bandpass', 3200, 0.6, 0.1 * (o.lv || 1), 0.025, 0.34, h); return x; },
    cach: function (t, d) { [1250, 1870, 2600].forEach(function (f) { tone(t, 'sine', f, 0.028, 0.001, 0.15, d); }); noiseHit(t, 'trang', 'bandpass', 3000, 1, 0.03, 0.001, 0.02, d); },
    da: function (t, d, o) {
      var lv = o.lv || 1;
      noiseHit(t, 'nau', 'lowpass', 200, 0.7, 0.26 * lv, 0.004, 0.38, d); tone(t, 'sine', 76, 0.18 * lv, 0.003, 0.26, d, 52);
      for (var i = 0; i < 6; i++) noiseHit(t + 0.02 + Math.random() * 0.25, 'trang', 'bandpass', 2000, 1, 0.02 * lv, 0.001, 0.02, d);
    },
    soi: function (t, d) { for (var i = 0; i < 22; i++) noiseHit(t + Math.random() * 0.7, 'trang', 'bandpass', 1300 + Math.random() * 900, 1, 0.012 + Math.random() * 0.025, 0.001, 0.012 + Math.random() * 0.015, d); },
    dat: function (t, d) {
      var g = G(0, d), f = F('lowpass', 140, 0.7, g), s = src('nau', false, t, 1.5); s.connect(f);
      g.gain.setValueAtTime(0.0001, t); g.gain.linearRampToValueAtTime(0.22, t + 0.4); g.gain.exponentialRampToValueAtTime(0.0001, t + 1.45);
      SFX.soi(t + 0.1, d, {});
    },
    lat_trang: function (t, d) { noiseHit(t, 'trang', 'bandpass', 2600, 0.7, 0.045, 0.08, 0.3, d); },
    soat: function (t, d) { for (var i = 0; i < 8; i++) noiseHit(t + i * 0.05 + Math.random() * 0.03, 'hong', 'bandpass', 3400, 0.6, 0.02, 0.01, 0.06, d); }
  };

  // ---------------------------------------------------------------- nền âm (lặp)
  function hen(bed, fn, minS, maxS) {   // hẹn giờ lặp ngẫu nhiên cho các nền âm có tiếng rời (lửa lách tách, chim, côn trùng...)
    (function lap() { if (bed.dung) return; fn(now() + 0.05); bed.timers.push(setTimeout(lap, (minS + Math.random() * (maxS - minS)) * 1000)); })();
  }
  var BED = {
    nuoc: function (b) {
      var s1 = src('nau', true, now()), g1 = G(0.11, b.g), f1 = F('bandpass', 450, 0.6, g1); s1.connect(f1); b.nodes.push(s1, lfo(0.11, 0.035, g1.gain));
      var s2 = src('trang', true, now()); var g2 = G(0.012, b.g); var f2 = F('bandpass', 1800, 1.2, g2); s2.connect(f2); b.nodes.push(s2, lfo(0.37, 0.008, g2.gain));
    },
    song_bien: function (b) {
      var s = src('hong', true, now()), g = G(0.07, b.g), f = F('lowpass', 700, 0.7, g); s.connect(f); b.nodes.push(s, lfo(0.1, 0.06, g.gain));
      var s2 = src('trang', true, now()), g2 = G(0.006, b.g), f2 = F('highpass', 3000, 0.7, g2); s2.connect(f2); b.nodes.push(s2, lfo(0.1, 0.005, g2.gain));
    },
    gio: function (b) {
      var s = src('hong', true, now()), g = G(0.05, b.g), f = F('bandpass', 520, 2, g); s.connect(f);
      b.nodes.push(s, lfo(0.07, 300, f.frequency), lfo(0.05, 0.022, g.gain));
    },
    lua: function (b) {
      var s = src('nau', true, now()), g = G(0.045, b.g), f = F('lowpass', 260, 0.7, g); s.connect(f); b.nodes.push(s);
      hen(b, function (t) { crackle(t, b.g, 0.9); if (Math.random() < 0.3) crackle(t + 0.03, b.g, 0.6); }, 0.04, 0.28);
    },
    dam_dong: function (b) {
      var s = src('hong', true, now()), g = G(0.03, b.g);
      [[500, 2], [1100, 2.5], [2400, 3]].forEach(function (p) { var f = F('bandpass', p[0], p[1], g); s.connect(f); });
      b.nodes.push(s, lfo(0.27, 0.012, g.gain), lfo(3.1, 0.006, g.gain));
    },
    con_trung: function (b) {
      hen(b, function (t) { var f = 4300 + Math.random() * 500, n = 3 + Math.floor(Math.random() * 3); for (var i = 0; i < n; i++) tone(t + i * 0.055, 'sine', f, 0.0065, 0.004, 0.03, b.g); }, 0.3, 0.9);
    },
    chim: function (b) {
      hen(b, function (t) { var n = 2 + Math.floor(Math.random() * 3), f0 = 2400 + Math.random() * 700; for (var i = 0; i < n; i++) tone(t + i * 0.12, 'sine', f0, 0.016, 0.006, 0.08, b.g, f0 * 1.5); }, 2.5, 7);
    },
    dong_co: function (b) {
      var t = now(), o = ctx.createOscillator(); o.type = 'sawtooth'; o.frequency.value = 48; var g = G(0.022, b.g), f = F('lowpass', 170, 0.7, g); o.connect(f); o.start(t);
      var o2 = ctx.createOscillator(); o2.frequency.value = 96; var g2 = G(0.008, b.g); o2.connect(g2); o2.start(t);
      b.nodes.push(o, o2, lfo(0.4, 3, o.frequency));
    },
    phao_xa: function (b) { hen(b, function (t) { SFX.no(t, b.g, { xa: true, lv: 0.35 + Math.random() * 0.2 }); }, 3.5, 9); },
    dong_ho: function (b) { var k = 0; hen(b, function (t) { SFX.tick(t, b.g, { f: (k++ % 2) ? 1300 : 1700 }); }, 1, 1); },
    nen_em: function (b) {
      [196, 293.66, 392].forEach(function (f, i) { var o = ctx.createOscillator(); o.frequency.value = f; var g = G(0.006, b.g); o.connect(g); o.start(); b.nodes.push(o, lfo(0.07 + i * 0.03, 0.004, g.gain), lfo(0.05, 0.8, o.frequency)); });
    },
    banh_xe_nuoc: function (b) { hen(b, function (t) { var h = noiseHit(t, 'trang', 'bandpass', 900, 0.9, 0.03, 0.03, 0.35, b.g); h.f.frequency.exponentialRampToValueAtTime(500, t + 0.3); }, 0.55, 0.75); },
    may_hoi: function (b) {
      var o = ctx.createOscillator(); o.frequency.value = 62; var g = G(0.012, b.g); o.connect(g); o.start(); b.nodes.push(o);
      var s = src('nau', true, now()), g2 = G(0.02, b.g), f = F('lowpass', 380, 0.7, g2); s.connect(f); b.nodes.push(s);
    }
  };
  function batNen(ten) {
    if (beds[ten] || !BED[ten]) return;
    var b = { g: G(0, bedBus), nodes: [], timers: [], dung: false };
    try { BED[ten](b); } catch (e) { return; }
    b.g.gain.setValueAtTime(0.0001, now()); b.g.gain.linearRampToValueAtTime(1, now() + 1.6);
    beds[ten] = b;
  }
  function tatNen(ten) {
    var b = beds[ten]; if (!b) return; delete beds[ten];
    b.dung = true; b.timers.forEach(clearTimeout);
    var t = now(); b.g.gain.cancelScheduledValues(t); b.g.gain.setValueAtTime(b.g.gain.value, t); b.g.gain.linearRampToValueAtTime(0.0001, t + 1.1);
    setTimeout(function () { b.nodes.forEach(function (n) { try { n.stop(); } catch (e) { /* đã dừng */ } }); b.g.disconnect(); }, 1300);
  }
  function datNen(list) {
    if (!ctx) return;
    Object.keys(beds).forEach(function (k) { if (list.indexOf(k) < 0) tatNen(k); });
    list.forEach(batNen);
  }

  // ---------------------------------------------------------------- API
  AT.nen = function (list) { want = (list || []).slice(); if (ctx) datNen(want); };
  AT.phat = function (ten, o) {
    o = o || {};
    if (!ctx || AT.tat || !SFX[ten] || ctx.state !== 'running') return;
    var ms = performance.now() + (o.tre || 0) * 1000;   // thời điểm phát thực (có tính độ trễ hẹn trước)
    if (last[ten] != null && Math.abs(ms - last[ten]) < (o.cach || 110)) return;
    burst = burst.filter(function (x) { return Math.abs(ms - x) < 300; });
    if (burst.length >= 5) return;
    last[ten] = ms; burst.push(ms);
    try { SFX[ten](now() + 0.02 + (o.tre || 0), fxBus, o); } catch (e) { /* không để lỗi âm thanh làm hỏng mô phỏng */ }
  };
  AT.datTat = function (v) {
    AT.tat = !!v;
    try { localStorage.setItem('mp-am-tat', AT.tat ? '1' : '0'); } catch (e) { /* bỏ qua */ }
    if (ctx) { var t = now(); master.gain.cancelScheduledValues(t); master.gain.setTargetAtTime(AT.tat ? 0 : AT.luong * 0.9, t, 0.08); if (!AT.tat && ctx.state === 'suspended') ctx.resume(); }
    uiList.forEach(capNhatUi);
  };
  AT.datLuong = function (v) {
    AT.luong = Math.max(0, Math.min(1, v));
    try { localStorage.setItem('mp-am-luong', String(AT.luong)); } catch (e) { /* bỏ qua */ }
    if (ctx && !AT.tat) master.gain.setTargetAtTime(AT.luong * 0.9, now(), 0.05);
    uiList.forEach(capNhatUi);
  };
  AT.hoTro = !!Ctor;

  var LOA = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9h4l5-4v14l-5-4H4z"/><path d="M15.5 8.5a5 5 0 0 1 0 7M18 6a8.5 8.5 0 0 1 0 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>';
  var LOA_TAT = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9h4l5-4v14l-5-4H4z"/><path d="M16 9l6 6M22 9l-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>';
  function capNhatUi(u) {
    u.btn.innerHTML = (AT.tat ? LOA_TAT : LOA) + '<span>' + (AT.tat ? 'Âm thanh: tắt' : 'Âm thanh: bật') + '</span>';
    u.btn.setAttribute('aria-pressed', AT.tat ? 'false' : 'true');
    u.range.value = Math.round(AT.luong * 100); u.range.style.setProperty('--pct', (AT.luong * 100) + '%');
    u.range.disabled = AT.tat;
    u.hint.hidden = !!ctx || AT.tat;
  }
  AT.ui = function (container) {
    if (!container || !Ctor) return null;
    var wrap = document.createElement('div'); wrap.className = 'am-thanh'; wrap.setAttribute('role', 'group'); wrap.setAttribute('aria-label', 'Âm thanh mô phỏng');
    var btn = document.createElement('button'); btn.type = 'button'; btn.className = 'nut am-nut';
    var range = document.createElement('input'); range.type = 'range'; range.min = '0'; range.max = '100'; range.setAttribute('aria-label', 'Âm lượng');
    var hint = document.createElement('span'); hint.className = 'am-goi-y'; hint.textContent = 'Âm thanh phát sau lần chạm/bấm đầu tiên';
    btn.addEventListener('click', function () { moKhoa(); AT.datTat(!AT.tat); if (!AT.tat) AT.phat('xac_nhan'); });
    range.addEventListener('input', function () { moKhoa(); AT.datLuong(range.value / 100); });
    range.addEventListener('change', function () { AT.phat('tick', { f: 1200 }); });
    wrap.appendChild(hint); wrap.appendChild(btn); wrap.appendChild(range);
    container.insertBefore(wrap, container.firstChild);
    var u = { btn: btn, range: range, hint: hint }; uiList.push(u); capNhatUi(u);
    return wrap;
  };
  window.AT = AT;
  function auto() { var k = document.getElementById('mo-phong'); if (k && !k.querySelector('.am-thanh')) AT.ui(k); }
  if (document.readyState !== 'loading') auto(); else document.addEventListener('DOMContentLoaded', auto);
})();
