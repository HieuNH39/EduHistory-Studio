/* EduHistory Studio – Sa bàn động trên web.
   Cổng JavaScript của pipeline/maps/saban2.py (định dạng "phien_ban": 2) và saban.py (định dạng cũ: Rạch Gầm – Xoài Mút).
   Đọc cùng tệp dữ liệu pipeline/maps/specs/<ten>.json (được sao thành data/ban-do/<ten>.js), vẽ trên <canvas>.
   Ý nghĩa dữ liệu: "khung" = hộp bao toạ độ cục bộ; "pha" = các giai đoạn, mỗi pha có "hien" (hiện sẵn), "buoc" (bước xuất
   hiện theo trục 0..1: tu → den), "mac_ket" (thuyền mắc kẹt), "da_mat" (đã bị tiêu diệt), "moc" (nhãn thời gian), "bang" (băng rôn). */
(function () {
  'use strict';
  var MP = window.MP;
  var C = {
    giay: [0.937, 0.905, 0.835], giay2: [0.902, 0.858, 0.760], nuoc: [0.612, 0.765, 0.835], bo: [0.400, 0.575, 0.690],
    dao: [0.860, 0.820, 0.640], cay: [0.365, 0.490, 0.300], chu: [0.235, 0.184, 0.133], chu_nuoc: [0.180, 0.370, 0.480],
    ta: [0.722, 0.149, 0.118], dich: [0.180, 0.243, 0.451], vang: [0.960, 0.760, 0.250]
  };
  var FONT = '"Be Vietnam Pro", system-ui, -apple-system, "Segoe UI", Arial, sans-serif';
  var PI = Math.PI, TAU = Math.PI * 2;

  function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }
  function ease(t) { t = clamp(t, 0, 1); return t * t * (3 - 2 * t); }
  function seg(u, a, b) { return ease((u - a) / Math.max(1e-6, b - a)); }
  function rgba(c, a) { return 'rgba(' + Math.round(c[0] * 255) + ',' + Math.round(c[1] * 255) + ',' + Math.round(c[2] * 255) + ',' + (a == null ? 1 : clamp(a, 0, 1)) + ')'; }

  /** Làm mượt đường gấp khúc (Catmull–Rom), như hàm catmull() của pipeline */
  function catmull(pts, n) {
    n = n || 16;
    var P = [pts[0]].concat(pts, [pts[pts.length - 1]]), out = [], i, k;
    for (i = 1; i < P.length - 2; i++) {
      var p0 = P[i - 1], p1 = P[i], p2 = P[i + 1], p3 = P[i + 2];
      for (k = 0; k < n; k++) {
        var t = k / n, t2 = t * t, t3 = t2 * t;
        out.push([
          0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3),
          0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
        ]);
      }
    }
    var last = pts[pts.length - 1]; out.push([last[0], last[1]]);
    return out;
  }
  function cumlen(path) {
    var d = [0];
    for (var i = 1; i < path.length; i++) d.push(d[i - 1] + Math.hypot(path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1]));
    return d;
  }
  function ssorted(d, L) { var lo = 0, hi = d.length; while (lo < hi) { var m = (lo + hi) >> 1; if (d[m] < L) lo = m + 1; else hi = m; } return lo; }
  /** Phần đầu của đường theo tỉ lệ độ dài */
  function cut(path, frac) {
    if (frac >= 1) return path;
    var d = cumlen(path), L = d[d.length - 1] * Math.max(0, frac), k = ssorted(d, L);
    if (k <= 0) return path.slice(0, 1);
    if (k >= path.length) return path;
    var a = (L - d[k - 1]) / Math.max(1e-9, d[k] - d[k - 1]);
    var out = path.slice(0, k);
    out.push([path[k - 1][0] + (path[k][0] - path[k - 1][0]) * a, path[k - 1][1] + (path[k][1] - path[k - 1][1]) * a]);
    return out;
  }
  function rng(seed) {
    var s = (seed * 2654435761) >>> 0;
    function r() { s = (s + 0x6D2B79F5) >>> 0; var t = s; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }
    return { r: r, n: function (mu, sd) { var u1 = Math.max(1e-9, r()), u2 = r(); return mu + sd * Math.sqrt(-2 * Math.log(u1)) * Math.cos(TAU * u2); } };
  }
  function pathOf(pts, close) {
    var p = new Path2D(); p.moveTo(pts[0][0], pts[0][1]);
    for (var i = 1; i < pts.length; i++) p.lineTo(pts[i][0], pts[i][1]);
    if (close) p.closePath();
    return p;
  }
  function closedSmooth(poly, n) { return catmull(poly.concat([poly[0]]), n); }

  // =====================================================================================================
  //  Bộ vẽ sa bàn phiên bản 2
  // =====================================================================================================
  function SaBan(spec, opts) {
    this.S = spec; this.opts = opts || {};
    var k = spec.khung; this.kw = k[2] - k[0]; this.kh = k[3] - k[1];
    this.s1080 = Math.min(1920 * 0.96 / this.kw, 1080 * 0.80 / this.kh);   // tỉ lệ của bản video 1080p
    this.K = Math.max(1.05, Math.min(1.6, this.s1080 / 0.7));            // hệ số cỡ nét/chữ như pipeline
    this.an = {}; (this.opts.an || []).forEach(function (id) { this.an[id] = 1; }, this);
    this.user = { s: 1, x: 0, y: 0 };
    this._prep();
  }
  SaBan.prototype._prep = function () {
    var S = this.S, me = this;
    this.pVung = (S.vung_mau || []).map(function (v) { return { p: pathOf(v.diem, true), mau: v.mau || C.dao, vien: v.vien || 1.2 }; });
    this.pNuoc = (S.vung_nuoc || []).map(function (poly) { return pathOf(closedSmooth(poly, 8), true); });
    this.pDat = (S.dat_noi || []).map(function (poly) { return pathOf(closedSmooth(poly, 8), true); });
    this.pHo = (S.ho || []).map(function (h) {
      if (h.elip) { var e = h.elip, p = new Path2D(); p.ellipse(e[0], e[1], e[2], e[3], e[4] * PI / 180, 0, TAU); return p; }
      return pathOf(closedSmooth(h.diem, 10), true);
    });
    this.pSong = (S.song || []).map(function (r) { return { p: pathOf(catmull(r.diem, 10), false), rong: r.rong || 6 }; });
    this.tuongThanh = (S.tuong_thanh || []).map(function (t) { return catmull(t, 12); });
    this.cache = {};
    this.pathCache = function (id, pts, n) { var key = id + ':' + n; if (!me.cache[key]) me.cache[key] = catmull(pts, n); return me.cache[key]; };
  };
  SaBan.prototype.layout = function (cw, ch) {
    var k = this.S.khung;
    this.cw = cw; this.ch = ch;
    this.s = Math.min(cw * 0.98 / this.kw, ch * 0.98 / this.kh);
    this.ox = (cw - this.kw * this.s) / 2 - k[0] * this.s;
    this.oy = (ch - this.kh * this.s) / 2 - k[1] * this.s;
    this.f = this.s / this.s1080;
    this.g = clamp(0.24 + 0.5 * this.f, Math.min(this.f, 0.7), 0.72);   // cỡ chữ/kí hiệu: nhỉnh hơn trên màn hình nhỏ, gọn hơn trên màn hình lớn
    this.u = this.g / this.s;                               // đơn vị bản đồ cho 1 "px video"
    this.geo = 1 / this.s1080;                              // khoảng cách hình học (không phóng theo màn hình)
  };
  SaBan.prototype.base = function (p) { return [this.ox + p[0] * this.s, this.oy + p[1] * this.s]; };
  /** Máy quay: z, tâm, can_giua (như frame() của pipeline) + phóng/kéo của người dùng */
  SaBan.prototype.setCam = function (cam) {
    var S = this.S, k = S.khung, z = cam.z || 1;
    var tam = cam.tam || S.tam || [(k[0] + k[2]) / 2, (k[1] + k[3]) / 2], F = this.base(tam), bx, by;
    if (cam.can_giua) {
      bx = this.cw * cam.can_giua[0] - z * F[0]; by = this.ch * cam.can_giua[1] - z * F[1];
      if (z >= 1) { bx = clamp(bx, this.cw - z * this.cw, 0); by = clamp(by, this.ch - z * this.ch, 0); }
    } else { bx = F[0] * (1 - z); by = F[1] * (1 - z); }
    var us = this.user.s;
    this.zc = z; this.z = z * us;
    this.a = this.s * z * us;
    this.bx = us * (z * this.ox + bx) + this.user.x;
    this.by = us * (z * this.oy + by) + this.user.y;
  };
  SaBan.prototype.P = function (p) { return [this.bx + p[0] * this.a, this.by + p[1] * this.a]; };
  SaBan.prototype.mapMode = function (ctx) { ctx.setTransform(this.dpr * this.a, 0, 0, this.dpr * this.a, this.dpr * this.bx, this.dpr * this.by); };
  SaBan.prototype.screenMode = function (ctx) { ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0); };

  /** Chữ vẽ trong toạ độ màn hình (nét rõ ở mọi mức phóng) */
  SaBan.prototype.text = function (ctx, s, mx, my, size, color, o) {
    o = o || {};
    if (!s) return;
    var p = o.screen ? [mx, my] : this.P([mx, my]);
    var px = o.fixed ? size * this.g : size * this.g * Math.pow(this.z, 0.4);   // chữ lớn dần chậm hơn bản đồ khi phóng to
    px = Math.max(px, o.min || 10.5);
    var alpha = o.alpha == null ? 1 : o.alpha;
    if (alpha <= 0.01) return;
    ctx.save(); this.screenMode(ctx); ctx.translate(p[0], p[1]);
    if (o.angle) ctx.rotate(o.angle * PI / 180);
    ctx.font = (o.italic ? 'italic ' : '') + (o.bold ? '700 ' : '400 ') + px.toFixed(1) + 'px ' + FONT;
    ctx.textAlign = o.align === 'l' ? 'left' : o.align === 'r' ? 'right' : 'center';
    ctx.textBaseline = 'middle';
    if (o.halo !== false) { ctx.lineJoin = 'round'; ctx.strokeStyle = rgba(C.giay, 0.88 * alpha); ctx.lineWidth = px * 0.26; ctx.strokeText(s, 0, 0); }
    ctx.fillStyle = rgba(color, alpha); ctx.fillText(s, 0, 0);
    ctx.restore();
  };

  SaBan.prototype.drawBase = function (ctx) {
    var S = this.S, me = this, u = this.u, K = this.K;
    this.screenMode(ctx);
    var g = ctx.createRadialGradient(this.cw * 0.5, this.ch * 0.45, this.ch * 0.2, this.cw * 0.5, this.ch * 0.5, this.cw * 0.75);
    g.addColorStop(0, rgba(C.giay)); g.addColorStop(1, rgba(C.giay2));
    ctx.fillStyle = g; ctx.fillRect(0, 0, this.cw, this.ch);
    if (S.nen_bien) { ctx.fillStyle = rgba(S.nen_bien); ctx.fillRect(0, 0, this.cw, this.ch); }
    this.mapMode(ctx);
    ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    this.pVung.forEach(function (v) {
      ctx.fillStyle = rgba(v.mau); ctx.fill(v.p);
      ctx.strokeStyle = rgba(C.bo, 0.9); ctx.lineWidth = v.vien * u * 0.8; ctx.stroke(v.p);
    });
    this.pNuoc.forEach(function (p) { ctx.fillStyle = rgba(C.nuoc); ctx.fill(p); ctx.strokeStyle = rgba(C.bo, 0.9); ctx.lineWidth = 1.8 * u; ctx.stroke(p); });
    this.pDat.forEach(function (p) { ctx.fillStyle = rgba(C.dao); ctx.fill(p); ctx.strokeStyle = rgba(C.bo, 0.9); ctx.lineWidth = 1.4 * u; ctx.stroke(p); });
    this.pHo.forEach(function (p) { ctx.fillStyle = rgba(C.nuoc); ctx.fill(p); ctx.strokeStyle = rgba(C.bo, 0.9); ctx.lineWidth = 1.6 * u; ctx.stroke(p); });
    this.pSong.forEach(function (r) {
      ctx.strokeStyle = rgba(C.bo, 0.9); ctx.lineWidth = r.rong + 2.5 * u; ctx.stroke(r.p);
      ctx.strokeStyle = rgba(C.nuoc); ctx.lineWidth = r.rong; ctx.stroke(r.p);
    });
    this.tuongThanh.forEach(function (pts) {
      ctx.strokeStyle = rgba(C.chu, 0.75); ctx.lineWidth = 2.2 * K * u;
      var d = cumlen(pts), step = 9 * K * u;
      for (var L = 0; L < d[d.length - 1]; L += step * 2) {
        var i = Math.min(ssorted(d, L), pts.length - 1), j = Math.min(ssorted(d, L + step), pts.length - 1);
        var a = pts[i], b = pts[j], vx = b[0] - a[0], vy = b[1] - a[1], ln = Math.hypot(vx, vy) + 1e-6, nx = -vy / ln * 5 * K * u, ny = vx / ln * 5 * K * u;
        ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(a[0] + nx, a[1] + ny); ctx.lineTo(b[0] + nx, b[1] + ny); ctx.lineTo(b[0], b[1]); ctx.stroke();
      }
    });
    (S.dia_danh || []).forEach(function (d) {
      if (d.man_hinh) return;
      if (d.kieu === 'thanh') me.citadel(ctx, d.vi_tri[0], d.vi_tri[1], 0);
      else if (d.kieu === 'diem') { me.mapMode(ctx); ctx.beginPath(); ctx.arc(d.vi_tri[0], d.vi_tri[1], 4 * K * u, 0, TAU); ctx.fillStyle = rgba(C.chu); ctx.fill(); }
    });
    (S.dia_danh || []).forEach(function (d) {
      if (d.man_hinh || !d.ten) return;
      var n = d.nhan || d.vi_tri;
      me.text(ctx, d.ten, n[0], n[1], (d.co || (d.lon ? 24 : 18)) * K, C.chu, { bold: !!(d.lon || d.dam) });
    });
    (S.song || []).forEach(function (r) { if (r.ten) me.text(ctx, r.ten, r.nhan[0], r.nhan[1], 16 * K, C.chu_nuoc, { italic: true, angle: r.goc || 0 }); });
    (S.ho || []).forEach(function (h) { if (h.ten) me.text(ctx, h.ten, h.nhan[0], h.nhan[1], 15 * K, C.chu_nuoc, { italic: true }); });
  };

  // ----- kí hiệu (vẽ trong toạ độ bản đồ, cỡ theo "px video")
  SaBan.prototype._sym = function (ctx, x, y, sc, angDeg) {
    this.mapMode(ctx); ctx.translate(x, y); if (angDeg) ctx.rotate(angDeg * PI / 180); ctx.scale(sc * this.u, sc * this.u);
  };
  SaBan.prototype.citadel = function (ctx, x, y, glow) {
    ctx.save(); this._sym(ctx, x, y, this.K, 0);
    var w = 34;
    if (glow > 0) {
      var g = ctx.createRadialGradient(0, 0, 0, 0, 0, w * 1.6); g.addColorStop(0, rgba(C.vang, 0.7 * glow)); g.addColorStop(1, rgba(C.vang, 0));
      ctx.fillStyle = g; ctx.beginPath(); ctx.arc(0, 0, w * 1.6, 0, TAU); ctx.fill();
    }
    ctx.fillStyle = 'rgb(84,77,69)';
    ctx.fillRect(-w / 2, -w * 0.1, w, w * 0.45);
    for (var i = 0; i < 4; i++) ctx.fillRect(-w / 2 + i * w / 3.2, -w * 0.22, w / 7, w * 0.14);
    ctx.beginPath(); ctx.moveTo(-w * 0.38, -w * 0.25); ctx.lineTo(0, -w * 0.55); ctx.lineTo(w * 0.38, -w * 0.25); ctx.closePath(); ctx.fill();
    ctx.restore();
  };
  SaBan.prototype.star = function (ctx, x, y, k, color, screenScale) {
    if (k <= 0) return;
    ctx.save();
    if (screenScale) { var p = this.P([x, y]); this.screenMode(ctx); ctx.translate(p[0], p[1]); ctx.scale(screenScale, screenScale); }
    else this._sym(ctx, x, y, 1, 0);
    var K = screenScale ? 1 : this.K;
    var r1 = 15 * K * (0.6 + 0.4 * k) * (1 + 0.3 * Math.sin(k * PI)), r2 = r1 * 0.45;
    var g = ctx.createRadialGradient(0, 0, 0, 0, 0, r1 * 2.2); g.addColorStop(0, rgba(C.vang, 0.6 * k)); g.addColorStop(1, rgba(C.vang, 0));
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(0, 0, r1 * 2.2, 0, TAU); ctx.fill();
    ctx.beginPath();
    for (var i = 0; i < 10; i++) { var a = -PI / 2 + i * PI / 5, r = i % 2 === 0 ? r1 : r2; if (i === 0) ctx.moveTo(r * Math.cos(a), r * Math.sin(a)); else ctx.lineTo(r * Math.cos(a), r * Math.sin(a)); }
    ctx.closePath(); ctx.fillStyle = rgba(color || C.ta, k); ctx.fill();
    ctx.strokeStyle = 'rgba(255,230,128,' + k + ')'; ctx.lineWidth = 1.5; ctx.stroke();
    ctx.restore();
  };
  SaBan.prototype.fort = function (ctx, x, y, k, color, gone) {
    if (k <= 0) return;
    gone = gone || 0;
    ctx.save(); this._sym(ctx, x, y, this.K, 0);
    var w = 13, K = this.K;
    ctx.strokeStyle = ctx.fillStyle = rgba(color, k * (1 - 0.6 * gone)); ctx.lineWidth = 2.4 / K;
    ctx.strokeRect(-w, -w, 2 * w, 2 * w);
    ctx.beginPath(); ctx.moveTo(-w * 0.1, -w); ctx.lineTo(-w * 0.1, -w * 2.4); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(-w * 0.1, -w * 2.4); ctx.lineTo(w * 1.1, -w * 2.0); ctx.lineTo(-w * 0.1, -w * 1.6); ctx.closePath(); ctx.fill();
    if (gone > 0) {
      ctx.strokeStyle = rgba(C.ta, gone); ctx.lineWidth = 3.5 / K; ctx.beginPath();
      ctx.moveTo(-w * 1.3, -w * 1.3); ctx.lineTo(w * 1.3, w * 1.3); ctx.moveTo(w * 1.3, -w * 1.3); ctx.lineTo(-w * 1.3, w * 1.3); ctx.stroke();
    }
    ctx.restore();
  };
  SaBan.prototype.block = function (ctx, x, y, k, ang) {
    if (k <= 0) return;
    ctx.save(); this._sym(ctx, x, y, this.K * (0.6 + 0.4 * k), ang || 0);
    ctx.fillStyle = rgba(C.ta, k); ctx.fillRect(-4, -18, 8, 36); ctx.fillRect(-4, -18, 18, 7); ctx.fillRect(-4, 11, 18, 7);
    ctx.restore();
  };
  SaBan.prototype.ambush = function (ctx, x, y, k, ang) {
    if (k <= 0) return;
    ctx.save(); this._sym(ctx, x, y, this.K * (0.6 + 0.4 * k) * (1 + 0.25 * Math.sin(k * PI)), ang || 0);
    ctx.fillStyle = rgba(C.ta, k); ctx.fillRect(-22, -3, 44, 6);
    [-10, 10].forEach(function (dx) {
      ctx.beginPath(); ctx.moveTo(dx - 2, -3); ctx.lineTo(dx - 2, -11); ctx.lineTo(dx - 6, -11); ctx.lineTo(dx, -18); ctx.lineTo(dx + 6, -11); ctx.lineTo(dx + 2, -11); ctx.lineTo(dx + 2, -3); ctx.closePath(); ctx.fill();
    });
    ctx.restore();
  };
  /** Mũi tên thuôn theo đường cong (pts: toạ độ bản đồ), vẽ tới tỉ lệ frac */
  SaBan.prototype.arrow = function (ctx, pts, frac, color, w0, w1, alpha, dashed, key) {
    if (frac <= 0.01) return;
    var full = key ? this.pathCache(key, pts, 12) : catmull(pts, 12);
    var path = cut(full, frac), n = path.length, u = this.u, K = this.K;
    if (n < 2) return;
    this.mapMode(ctx);
    ctx.fillStyle = ctx.strokeStyle = rgba(color, alpha);
    if (dashed) {
      ctx.lineWidth = w0 * K * u; ctx.setLineDash([12 * K * u, 8 * K * u]); ctx.lineCap = 'butt';
      var body = n > 4 ? path.slice(0, n - 3) : path;
      ctx.beginPath(); ctx.moveTo(body[0][0], body[0][1]); for (var i = 1; i < body.length; i++) ctx.lineTo(body[i][0], body[i][1]); ctx.stroke(); ctx.setLineDash([]);
      var tip = path[n - 1], q = path[Math.max(0, n - 4)], vx = tip[0] - q[0], vy = tip[1] - q[1], ln = Math.hypot(vx, vy) + 1e-9; vx /= ln; vy /= ln;
      var hs = w0 * 2.6 * K * u;
      ctx.beginPath(); ctx.moveTo(tip[0], tip[1]); ctx.lineTo(tip[0] - vx * hs * 1.4 - vy * hs, tip[1] - vy * hs * 1.4 + vx * hs);
      ctx.lineTo(tip[0] - vx * hs * 1.4 + vy * hs, tip[1] - vy * hs * 1.4 - vx * hs); ctx.closePath(); ctx.fill();
      ctx.lineCap = 'round';
      return;
    }
    var nrm = [], j;
    for (j = 0; j < n - 1; j++) { var dx = path[j + 1][0] - path[j][0], dy = path[j + 1][1] - path[j][1], L = Math.hypot(dx, dy) || 1e-6; nrm.push([-dy / L, dx / L]); }
    nrm.push(nrm[nrm.length - 1]);
    var w = path.map(function (_, i2) { return (w0 + (w1 - w0) * (n > 1 ? i2 / (n - 1) : 0)) * K * u; });
    var head = Math.min(n - 1, Math.max(1, Math.floor(n * 0.22)));
    var bodyN = head > 1 ? n - head + 1 : n;
    var left = [], right = [];
    for (j = 0; j < bodyN; j++) { left.push([path[j][0] + nrm[j][0] * w[j] / 2, path[j][1] + nrm[j][1] * w[j] / 2]); right.push([path[j][0] - nrm[j][0] * w[j] / 2, path[j][1] - nrm[j][1] * w[j] / 2]); }
    var tip2 = path[n - 1], base = path[bodyN - 1], bn = nrm[bodyN - 1], hw = w[bodyN - 1] * 1.9;
    ctx.beginPath(); ctx.moveTo(left[0][0], left[0][1]);
    for (j = 1; j < left.length; j++) ctx.lineTo(left[j][0], left[j][1]);
    ctx.lineTo(base[0] + bn[0] * hw / 2, base[1] + bn[1] * hw / 2); ctx.lineTo(tip2[0], tip2[1]); ctx.lineTo(base[0] - bn[0] * hw / 2, base[1] - bn[1] * hw / 2);
    for (j = right.length - 1; j >= 0; j--) ctx.lineTo(right[j][0], right[j][1]);
    ctx.closePath(); ctx.fill();
  };
  SaBan.prototype.fire = function (ctx, x, y, t, k, seed) {
    var R = rng(seed), K = this.K, j;
    ctx.save(); this._sym(ctx, x, y, 1, 0);
    for (j = 0; j < 6; j++) {
      var ph = R.r() * 6.28, r = (13 + 9 * R.r()) * K * k * (0.8 + 0.25 * Math.sin(t * 9 + ph));
      var dx = R.n(0, 7) * K, dy = R.n(0, 4) * K - 5 * K * Math.pow(Math.sin(t * 5 + ph), 2);
      if (r <= 0) continue;
      var g = ctx.createRadialGradient(dx, dy, 0, dx, dy, r);
      g.addColorStop(0, 'rgba(255,242,153,' + (0.95 * k) + ')'); g.addColorStop(0.45, 'rgba(255,140,26,' + (0.7 * k) + ')'); g.addColorStop(1, 'rgba(178,26,0,0)');
      ctx.fillStyle = g; ctx.beginPath(); ctx.arc(dx, dy, r, 0, TAU); ctx.fill();
    }
    for (j = 0; j < 3; j++) {
      var yy = -(18 + 36 * ((t * 0.35 + j / 3) % 1)) * K, rr = 22 * K;
      var g2 = ctx.createRadialGradient(0, yy, 0, 0, yy, rr); g2.addColorStop(0, 'rgba(64,56,51,' + (0.32 * k) + ')'); g2.addColorStop(1, 'rgba(64,56,51,0)');
      ctx.fillStyle = g2; ctx.beginPath(); ctx.arc(0, yy, rr, 0, TAU); ctx.fill();
    }
    ctx.restore();
  };

  /** Vẽ một đối tượng của pha */
  SaBan.prototype.drawObj = function (ctx, id, o, k, t, extra) {
    extra = extra || {};
    var me = this, K = this.K, u = this.u, typ = o.loai, gone = extra.gone || 0, alpha = extra.alpha == null ? 1 : extra.alpha;
    var pts, d, i, L, x, y;
    ctx.save(); ctx.globalAlpha = alpha;
    switch (typ) {
      case 'mui_ten_ta': this.arrow(ctx, o.diem, k, C.ta, o.w0 || 8, o.w1 || 14, 0.95, false, id); break;
      case 'mui_ten_dich': this.arrow(ctx, o.diem, k, C.dich, o.w0 || 3, o.w1 || 6, 0.9, false, id); break;
      case 'rut_chay': this.arrow(ctx, o.diem, k, C.dich, o.w0 || 4, 4, 0.85, true, id); break;
      case 'rut_lui': this.arrow(ctx, o.diem, k, C.ta, o.w0 || 6, 6, 0.85, true, id); break;
      case 'vong':
        pts = cut(this.pathCache(id + 'v', o.diem.concat([o.diem[0], o.diem[1]]), 12), k);
        if (pts.length >= 2) { this.mapMode(ctx); ctx.strokeStyle = rgba(C.ta, 0.75); ctx.lineWidth = (o.rong || 7) * K * u; ctx.stroke(pathOf(pts)); }
        break;
      case 'cu_diem':
        x = o.vi_tri[0]; y = o.vi_tri[1];
        ctx.save(); this._sym(ctx, x, y, 1, 0);
        var r = 7 * K * (0.6 + 0.4 * k) * (o.co || 1);
        ctx.fillStyle = 'rgba(38,38,46,' + k + ')'; ctx.beginPath(); ctx.arc(0, 0, r, PI, TAU); ctx.closePath(); ctx.fill();
        ctx.fillStyle = 'rgba(255,255,255,' + k + ')'; ctx.fillRect(-r * 0.45, -r * 0.45, r * 0.9, r * 0.3);
        if (gone) {
          ctx.strokeStyle = rgba(C.ta, gone); ctx.lineWidth = 3 * K / 1.4; ctx.beginPath();
          ctx.moveTo(-r * 1.3, -r * 1.3); ctx.lineTo(r * 1.3, r * 0.6); ctx.moveTo(-r * 1.3, r * 0.6); ctx.lineTo(r * 1.3, -r * 1.3); ctx.stroke();
        }
        ctx.restore(); break;
      case 'san_bay':
        ctx.save(); this._sym(ctx, o.vi_tri[0], o.vi_tri[1], K * (0.6 + 0.4 * k), o.goc || 0);
        ctx.fillStyle = 'rgba(245,245,240,' + k + ')'; ctx.fillRect(-40, -7, 80, 14);
        ctx.strokeStyle = rgba(C.dich, k); ctx.lineWidth = 1.6; ctx.strokeRect(-40, -7, 80, 14);
        ctx.lineWidth = 2.4; ctx.beginPath(); ctx.moveTo(-12, 0); ctx.lineTo(12, 0); ctx.moveTo(2, -9); ctx.lineTo(2, 9); ctx.moveTo(-10, -4); ctx.lineTo(-10, 4); ctx.stroke();
        if (gone) { ctx.strokeStyle = rgba(C.ta, gone); ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(-30, -14); ctx.lineTo(30, 14); ctx.moveTo(-30, 14); ctx.lineTo(30, -14); ctx.stroke(); }
        ctx.restore(); break;
      case 'tuong': case 'tran_tuyen':
        pts = cut(this.pathCache(id, o.diem, 12), k);
        if (pts.length < 2) break;
        d = cumlen(pts); this.mapMode(ctx);
        if (typ === 'tuong') {
          ctx.strokeStyle = ctx.fillStyle = 'rgba(107,102,97,0.95)'; ctx.lineWidth = 9 * K * u; ctx.stroke(pathOf(pts));
          var step = 11 * K * u, side = o.phia || 1;
          for (L = 0; L < d[d.length - 1] - step; L += step * 2) {
            i = ssorted(d, L); var j2 = Math.min(ssorted(d, L + step), pts.length - 1);
            if (j2 <= i) continue;
            var a = pts[i], b = pts[j2], vx = b[0] - a[0], vy = b[1] - a[1], ln = Math.hypot(vx, vy) + 1e-6, nx = -vy / ln * 9 * K * u * side, ny = vx / ln * 9 * K * u * side;
            ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(a[0] + nx, a[1] + ny); ctx.lineTo(b[0] + nx, b[1] + ny); ctx.lineTo(b[0], b[1]); ctx.closePath(); ctx.fill();
          }
        } else {
          var st2 = 13 * K * u, sd = 1; ctx.strokeStyle = 'rgba(31,31,36,0.9)'; ctx.lineWidth = 3.2 * K * u; ctx.beginPath();
          var first = true;
          for (L = 0; L < d[d.length - 1]; L += st2) {
            i = Math.min(ssorted(d, L), pts.length - 1); var j3 = Math.min(ssorted(d, L + st2), pts.length - 1);
            var a2 = pts[i], b2 = pts[j3], vx2 = b2[0] - a2[0], vy2 = b2[1] - a2[1], ln2 = Math.hypot(vx2, vy2) + 1e-6, nx2 = -vy2 / ln2 * 8 * K * u, ny2 = vx2 / ln2 * 8 * K * u;
            if (first) { ctx.moveTo(a2[0], a2[1]); first = false; }
            ctx.lineTo(a2[0] + nx2 * sd, a2[1] + ny2 * sd); ctx.lineTo(b2[0] + nx2 * sd, b2[1] + ny2 * sd); sd = -sd;
          }
          ctx.stroke();
        }
        break;
      case 'phong_tuyen':
        ctx.save(); this._sym(ctx, o.vi_tri[0], o.vi_tri[1], K * (0.6 + 0.4 * k), o.goc || 0);
        ctx.strokeStyle = ctx.fillStyle = rgba(C.ta, k); ctx.lineWidth = 8;
        ctx.beginPath(); ctx.arc(0, 26, 30, -150 * PI / 180, -30 * PI / 180); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(0, -16); ctx.lineTo(-9, -2); ctx.lineTo(9, -2); ctx.closePath(); ctx.fill(); ctx.fillRect(-3, -4, 6, 12);
        ctx.restore(); break;
      case 'sao':
        if (o.man_hinh || this.S.sao_man_hinh) this.star(ctx, o.vi_tri[0], o.vi_tri[1], k, null, this.g * (o.co || 1) * 1.05);
        else this.star(ctx, o.vi_tri[0], o.vi_tri[1], k);
        break;
      case 'don_dich': this.fort(ctx, o.vi_tri[0], o.vi_tri[1], k > 0 ? 1 : 0, C.dich, gone); break;
      case 'don_ta': this.fort(ctx, o.vi_tri[0], o.vi_tri[1], k, C.ta); break;
      case 'chan_danh': this.block(ctx, o.vi_tri[0], o.vi_tri[1], k, o.goc || 0); break;
      case 'mai_phuc': this.ambush(ctx, o.vi_tri[0], o.vi_tri[1], k, o.goc || 0); break;
      case 'thanh_sang': this.citadel(ctx, o.vi_tri[0], o.vi_tri[1], k * (0.75 + 0.25 * Math.sin(t * 5))); this.anim = true; break;
      case 'coc':
        this.mapMode(ctx); ctx.fillStyle = 'rgba(92,64,38,0.95)';
        o.diem.forEach(function (p, ii) {
          var kk = clamp(k * o.diem.length - ii * 0.6, 0, 1); if (kk <= 0) return;
          var h = 14 * K * u * kk;
          ctx.beginPath(); ctx.moveTo(p[0] - 3 * K * u, p[1]); ctx.lineTo(p[0], p[1] - h); ctx.lineTo(p[0] + 3 * K * u, p[1]); ctx.closePath(); ctx.fill();
        });
        break;
      case 'thuyen_dich': case 'thuyen_ta':
        var path = this.pathCache(id, o.diem, 20); d = this.cache[id + ':d20'] || (this.cache[id + ':d20'] = cumlen(path));
        var bd = o.bat_dau == null ? 0.15 : o.bat_dau, Lh = d[d.length - 1] * (bd + (1 - bd) * k), col = typ === 'thuyen_dich' ? C.dich : C.ta;
        var stuck = extra.ket || 0;
        for (var jj = 0; jj < (o.so || 6); jj++) {
          var Lj = Lh - jj * 34 * K * this.geo; if (Lj < 0) break;
          var q = clamp(ssorted(d, Lj), 1, path.length - 1), p0 = path[q], vv = [p0[0] - path[q - 1][0], p0[1] - path[q - 1][1]];
          var ang = Math.atan2(vv[1], vv[0]), off = ((jj % 3) - 1) * 14 * K * this.geo;
          var px = p0[0] - Math.sin(ang) * off, py = p0[1] + Math.cos(ang) * off;
          if (stuck > 0.05) {   // thuyền mắc cọc, chao lật: vòng sóng loang quanh thuyền
            this.mapMode(ctx); ctx.strokeStyle = 'rgba(255,255,255,' + (0.55 * stuck) + ')'; ctx.lineWidth = 1.4 * u;
            ctx.beginPath(); ctx.arc(px, py, 22 * K * u * (0.7 + 0.3 * stuck), 0, TAU); ctx.stroke();
          }
          ctx.save(); this._sym(ctx, px, py, K, 0); ctx.rotate(ang + stuck * (jj % 2 ? 0.5 : -0.4));
          if (stuck > 0.05 && jj % 3 === 0) ctx.scale(1, 1 - 1.6 * stuck);   // một số thuyền lật úp
          ctx.fillStyle = rgba(col, 1 - 0.4 * stuck);
          ctx.beginPath(); ctx.moveTo(-14, -4); ctx.bezierCurveTo(-7, -7, 9, -7, 16, 0); ctx.bezierCurveTo(9, 7, -7, 7, -14, 4); ctx.closePath(); ctx.fill();
          ctx.restore();
        }
        break;
      case 'lua':
        o.diem.forEach(function (p, ii) { var kk = clamp(k * 1.5 - ii * 0.1, 0, 1); if (kk > 0) me.fire(ctx, p[0], p[1], t, kk, 50 + ii); });
        this.anim = true; break;
      case 'nhan':
        this.text(ctx, o.chu, o.vi_tri[0], o.vi_tri[1], (o.co || 18) * K, C[o.mau || 'ta'] || C.ta, { bold: true, angle: o.goc || 0, alpha: k * alpha });
        break;
    }
    ctx.restore();
  };

  /** Nhãn cỡ cố định trên màn hình ("man_hinh"), hiện theo mức phóng */
  SaBan.prototype.screenLabels = function (ctx) {
    var me = this, z = this.z;
    (this.S.dia_danh || []).forEach(function (d) {
      if (!d.man_hinh || !d.ten) return;
      if (!((d.zoom_tu || 0) <= z && z <= (d.zoom_den == null ? 99 : d.zoom_den))) return;
      var a = d.zoom_tu ? Math.min(1, (z - d.zoom_tu) / 0.15) : 1, p = me.P(d.vi_tri), f = me.g;
      ctx.save(); me.screenMode(ctx);
      if (d.kieu === 'diem') { ctx.beginPath(); ctx.arc(p[0], p[1], Math.max(3, 5 * f), 0, TAU); ctx.fillStyle = rgba(C.chu, a); ctx.fill(); }
      ctx.restore();
      var l = d.lech || [0, -26], dx = l[0] * f, dy = l[1] * f;
      me.text(ctx, d.ten, p[0] + dx, p[1] + dy, d.co || (d.lon ? 24 : 19), C.chu, { screen: true, fixed: true, bold: !!(d.lon || d.dam), align: dx > 4 ? 'l' : dx < -4 ? 'r' : 'c', alpha: a, min: 10.5 });
    });
  };

  /** Danh sách đối tượng cần vẽ ở pha phKey, thời điểm u */
  SaBan.prototype.items = function (phKey, u) {
    var ph = this.S.pha[phKey], objs = this.S.doi_tuong || {}, an = this.an, out = [];
    (ph.hien || []).forEach(function (id) {
      if (an[id] || !objs[id]) return;
      var mk = ph.mac_ket && ph.mac_ket[id];
      out.push({ id: id, o: objs[id], k: 1, gone: (ph.da_mat || []).indexOf(id) >= 0 ? 1 : 0, ket: mk ? seg(u, mk[0], mk[1]) : 0 });
    });
    (ph.buoc || []).forEach(function (st) {
      var k = seg(u, st.tu, st.den);
      if (k <= 0 || an[st.id] || !objs[st.id]) return;
      if (st.hieu_ung === 'mat') out.push({ id: st.id, o: objs[st.id], k: 1, gone: k });
      else out.push({ id: st.id, o: objs[st.id], k: k });
    });
    return out;
  };
  SaBan.prototype.camFor = function (phKey, u) {
    var ph = this.S.pha[phKey], zz = ph.zoom || [1, 1.04];
    return { z: zz[0] + (zz[1] - zz[0]) * ease(u), tam: ph.tam, can_giua: ph.can_giua };
  };
  /** Vẽ toàn khung: state = {cam, items, t, style(id, o) -> alpha, after(ctx, sb)} */
  SaBan.prototype.render = function (ctx, dpr, state) {
    this.dpr = dpr; this.anim = false;
    this.setCam(state.cam);
    ctx.save();
    this.drawBase(ctx);
    var me = this;
    state.items.forEach(function (it) {
      var a = state.style ? state.style(it.id, it.o) : 1;
      me.drawObj(ctx, it.id, it.o, it.k, state.t, { gone: it.gone, ket: it.ket, alpha: a });
    });
    this.screenLabels(ctx);
    if (state.after) state.after(ctx, this);
    ctx.restore();
  };

  // =====================================================================================================
  //  Bộ vẽ định dạng cũ (saban.py): trận Rạch Gầm – Xoài Mút
  // =====================================================================================================
  function SaBanCu(spec) {
    this.S = spec; var k = spec.khung; this.kw = k[2] - k[0]; this.kh = k[3] - k[1];
    this.s1080 = Math.min(1920 / this.kw, 1080 * 0.8 / this.kh);
    this.user = { s: 1, x: 0, y: 0 };
    var R = rng(7), trees = [];
    (spec.cay || []).forEach(function (ab) {
      var a = ab[0], b = ab[1], L = Math.hypot(b[0] - a[0], b[1] - a[1]), dx = (b[0] - a[0]) / L, dy = (b[1] - a[1]) / L, nx = -dy, ny = dx;
      for (var i = 0; i < Math.floor(L / 9); i++) {
        var t = R.r(), side = R.n(0, 9), sg = R.r() > 0.5 ? 1 : -1;
        trees.push([a[0] + (b[0] - a[0]) * t + nx * side * sg * 1.6, a[1] + (b[1] - a[1]) * t + ny * side * sg * 1.6, 3.5 + R.r() * 3]);
      }
    });
    this.trees = trees;
    var bac = catmull(spec.song.bac, 16), nam = catmull(spec.song.nam, 16);
    this.pSong = pathOf(bac.concat(nam), true);
    this.duongXiem = catmull(spec.duong_xiem, 20); this.dXiem = cumlen(this.duongXiem);
    this.cache = {};
  }
  SaBanCu.prototype.layout = SaBan.prototype.layout;
  SaBanCu.prototype.base = SaBan.prototype.base;
  SaBanCu.prototype.setCam = SaBan.prototype.setCam;
  SaBanCu.prototype.P = SaBan.prototype.P;
  SaBanCu.prototype.mapMode = SaBan.prototype.mapMode;
  SaBanCu.prototype.screenMode = SaBan.prototype.screenMode;
  SaBanCu.prototype.text = function (ctx, s, mx, my, sizeMap, color, o) {
    // cỡ chữ của bản cũ tính theo đơn vị bản đồ (21 * s / 1.5 px ở 1080p)
    o = o || {};
    var px = Math.max(o.min || 10.5, sizeMap * 1.2 * this.a * this.b);
    var p = this.P([mx, my]), alpha = o.alpha == null ? 1 : o.alpha;
    ctx.save(); this.screenMode(ctx); ctx.translate(p[0], p[1]); if (o.angle) ctx.rotate(o.angle * PI / 180);
    ctx.font = (o.italic ? 'italic ' : '') + (o.bold ? '700 ' : '400 ') + px.toFixed(1) + 'px ' + FONT;
    ctx.textAlign = o.align === 'l' ? 'left' : 'center'; ctx.textBaseline = 'middle';
    if (o.halo !== false) { ctx.lineJoin = 'round'; ctx.strokeStyle = rgba(C.giay, 0.88 * alpha); ctx.lineWidth = px * 0.26; ctx.strokeText(s, 0, 0); }
    ctx.fillStyle = rgba(color, alpha); ctx.fillText(s, 0, 0); ctx.restore();
  };
  SaBanCu.prototype.ambush = function (ctx, x, y, ang, k) {
    if (k <= 0) return;
    var sc = this.b * (0.6 + 0.4 * k) * (1 + 0.25 * Math.sin(k * PI));
    ctx.save(); this.mapMode(ctx); ctx.translate(x, y); ctx.rotate(ang * PI / 180); ctx.scale(sc, sc);
    ctx.fillStyle = rgba(C.ta, k); ctx.fillRect(-26, -3.5, 52, 7);
    [-12, 12].forEach(function (dx) { ctx.beginPath(); ctx.moveTo(dx - 2.5, -3); ctx.lineTo(dx - 2.5, -13); ctx.lineTo(dx - 7, -13); ctx.lineTo(dx, -21); ctx.lineTo(dx + 7, -13); ctx.lineTo(dx + 2.5, -13); ctx.lineTo(dx + 2.5, -3); ctx.closePath(); ctx.fill(); });
    ctx.restore();
  };
  SaBanCu.prototype.arrow = function (ctx, pts, frac, color, w0, w1, alpha) {
    // dùng bộ vẽ mũi tên của bản 2 với K = 1, đơn vị = đơn vị bản đồ × hệ số b
    var save = { K: this.K, u: this.u, pathCache: this.pathCache };
    this.K = 1; this.u = this.b;
    SaBan.prototype.arrow.call(this, ctx, pts, frac, color, w0, w1, alpha, false, null);
    this.K = save.K; this.u = save.u;
  };
  SaBanCu.prototype.boat = function (ctx, x, y, ang, color, alpha) {
    ctx.save(); this.mapMode(ctx); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(this.b, this.b);
    ctx.fillStyle = rgba(color, alpha);
    ctx.beginPath(); ctx.moveTo(-16, -4); ctx.bezierCurveTo(-8, -7, 10, -7, 18, 0); ctx.bezierCurveTo(10, 7, -8, 7, -16, 4); ctx.closePath(); ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,' + (0.55 * alpha) + ')'; ctx.lineWidth = 1.6; ctx.beginPath(); ctx.moveTo(-6, 0); ctx.lineTo(8, 0); ctx.stroke();
    ctx.restore();
  };
  SaBanCu.prototype.fire = function (ctx, x, y, t, k, seed) {
    var R = rng(seed), j, s = this.b;
    this.mapMode(ctx);
    for (j = 0; j < 7; j++) {
      var ph = R.r() * 6.28, r = (14 + 10 * R.r()) * s * k * (0.8 + 0.25 * Math.sin(t * 9 + ph));
      var dx = R.n(0, 8) * s, dy = R.n(0, 5) * s - 6 * s * Math.pow(Math.sin(t * 5 + ph), 2);
      if (r <= 0) continue;
      var g = ctx.createRadialGradient(x + dx, y + dy, 0, x + dx, y + dy, r);
      g.addColorStop(0, 'rgba(255,242,153,' + (0.95 * k) + ')'); g.addColorStop(0.45, 'rgba(255,140,26,' + (0.7 * k) + ')'); g.addColorStop(1, 'rgba(178,26,0,0)');
      ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x + dx, y + dy, r, 0, TAU); ctx.fill();
    }
    for (j = 0; j < 4; j++) {
      var ph2 = R.r() * 6.28, yy = y - (20 + 40 * ((t * 0.35 + j / 4) % 1)) * s, rr = 26 * s, xx = x + 10 * Math.sin(ph2 + t) * s;
      var g2 = ctx.createRadialGradient(xx, yy, 0, xx, yy, rr); g2.addColorStop(0, 'rgba(64,56,51,' + (0.35 * k) + ')'); g2.addColorStop(1, 'rgba(64,56,51,0)');
      ctx.fillStyle = g2; ctx.beginPath(); ctx.arc(xx, yy, rr, 0, TAU); ctx.fill();
    }
    this.anim = true;
  };
  SaBanCu.prototype.hq = function (ctx, x, y, k) {
    var sz = 17 * this.b * (1 + 0.12 * Math.sin(k * 12));
    this.mapMode(ctx); ctx.lineWidth = 3 * this.b;
    ctx.fillStyle = 'rgba(255,255,255,0.9)'; ctx.fillRect(x - sz, y - sz, 2 * sz, 2 * sz);
    ctx.strokeStyle = ctx.fillStyle = rgba(C.ta); ctx.strokeRect(x - sz, y - sz, 2 * sz, 2 * sz); ctx.fillRect(x - sz * 0.5, y - sz * 0.5, sz, sz);
  };
  SaBanCu.prototype.island = function (ctx, d, glow) {
    this.mapMode(ctx);
    var p;
    if (d.diem) p = pathOf(closedSmooth(d.diem, 10), true);
    else { var e = d.elip; p = new Path2D(); p.ellipse(e[0], e[1], e[2], e[3], e[4] * PI / 180, 0, TAU); }
    ctx.fillStyle = rgba(C.dao); ctx.fill(p);
    if (glow) { ctx.fillStyle = rgba(C.vang, 0.55 * glow); ctx.fill(p); ctx.strokeStyle = rgba(C.ta, 0.9 * glow); ctx.lineWidth = 4 / this.a; ctx.stroke(p); }
    ctx.strokeStyle = rgba(C.bo, 0.9); ctx.lineWidth = 1.8 / this.a; ctx.stroke(p);
  };
  SaBanCu.prototype.camFor = function (phKey, u) {
    var z = { dia_the: 1 + 0.03 * u, mai_phuc: 1.03 + 0.03 * u, nhu_dich: 1.06 + 0.04 * u, ket_qua: 1.10 + 0.03 * u }[phKey] || 1;
    return { z: z, tam: [560, 420] };
  };
  SaBanCu.prototype.items = function () { return []; };
  SaBanCu.prototype.render = function (ctx, dpr, state) {
    var S = this.S, me = this, ph = state.phase, u = state.u, t = state.t, i;
    this.dpr = dpr; this.anim = false;
    this.setCam(state.cam);
    this.b = clamp(0.24 + 0.5 * this.f, Math.min(this.f, 0.7), 0.72) / this.f;   // hệ số phóng kí hiệu trên màn hình nhỏ
    ctx.save();
    this.screenMode(ctx);
    var g = ctx.createRadialGradient(this.cw * 0.5, this.ch * 0.45, this.ch * 0.2, this.cw * 0.5, this.ch * 0.5, this.cw * 0.75);
    g.addColorStop(0, rgba(C.giay)); g.addColorStop(1, rgba(C.giay2)); ctx.fillStyle = g; ctx.fillRect(0, 0, this.cw, this.ch);
    this.mapMode(ctx); ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    ctx.fillStyle = rgba(C.nuoc); ctx.fill(this.pSong); ctx.strokeStyle = rgba(C.bo, 0.9); ctx.lineWidth = 2.2 / this.a; ctx.stroke(this.pSong);
    S.dao.forEach(function (d) { me.island(ctx, d, 0); });
    S.rach.forEach(function (r) {
      me.mapMode(ctx); var p = pathOf(catmull(r.diem, 10));
      ctx.strokeStyle = rgba(C.bo, 0.9); ctx.lineWidth = r.rong * 0.9 + 2.5 / me.a; ctx.stroke(p);
      ctx.strokeStyle = rgba(C.nuoc); ctx.lineWidth = r.rong * 0.9; ctx.stroke(p);
    });
    this.mapMode(ctx); ctx.fillStyle = rgba(C.cay, 0.55);
    this.trees.forEach(function (tr) { ctx.beginPath(); ctx.arc(tr[0], tr[1], tr[2] * 0.55, 0, TAU); ctx.fill(); });
    S.dia_danh.forEach(function (d) { me.text(ctx, d.ten, d.vi_tri[0], d.vi_tri[1], 21 / 1.5, C.chu, { bold: true }); });
    S.song_nhan.forEach(function (d) { me.text(ctx, d.ten, d.vi_tri[0], d.vi_tri[1], 19 / 1.5, C.chu_nuoc, { italic: true, angle: d.goc }); });
    S.rach.forEach(function (r) { if (r.ten) me.text(ctx, r.ten, r.nhan[0], r.nhan[1], 16 / 1.5, C.chu_nuoc, { italic: true, angle: r.goc }); });
    S.dao.forEach(function (d) { me.text(ctx, d.ten, d.nhan[0], d.nhan[1], 15.5 / 1.5, C.chu, { italic: true, angle: d.goc }); });
    var k;
    if (ph === 'dia_the') {
      k = seg(u, 0.16, 0.34);
      if (k > 0) {
        var A = S.do_dai.tu, B = S.do_dai.den, L = Math.hypot(B[0] - A[0], B[1] - A[1]), dx = (B[0] - A[0]) / L, dy = (B[1] - A[1]) / L;
        var nx = dy * 46 / 1.5 * this.b, ny = -dx * 46 / 1.5 * this.b;
        var p0 = [A[0] + nx, A[1] + ny], p1 = [p0[0] + (B[0] - A[0]) * k, p0[1] + (B[1] - A[1]) * k];
        this.mapMode(ctx); ctx.strokeStyle = rgba(C.ta, 0.95); ctx.lineWidth = 3.2 / this.a * this.b; ctx.setLineDash([10 / this.a, 6 / this.a]);
        ctx.beginPath(); ctx.moveTo(p0[0], p0[1]); ctx.lineTo(p1[0], p1[1]); ctx.stroke(); ctx.setLineDash([]);
        [p0, k > 0.98 ? p1 : null].forEach(function (p) { if (p) { ctx.beginPath(); ctx.moveTo(p[0] - nx * 0.35, p[1] - ny * 0.35); ctx.lineTo(p[0] + nx * 0.35, p[1] + ny * 0.35); ctx.stroke(); } });
        if (k > 0.6) this.text(ctx, S.do_dai.nhan, (A[0] + B[0]) / 2 + nx * 1.7, (A[1] + B[1]) / 2 + ny * 1.7, 30 / 1.5, C.ta, { bold: true, angle: Math.atan2(dy, dx) * 180 / PI, alpha: seg(k, 0.6, 1) });
      }
      k = seg(u, 0.36, 0.5);
      if (k > 0) {
        var a = S.be_rong.tu, b = S.be_rong.den, q1 = [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k];
        this.mapMode(ctx); ctx.strokeStyle = rgba(C.dich, 0.95); ctx.lineWidth = 3 / this.a * this.b;
        ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(q1[0], q1[1]); ctx.stroke();
        [a, q1].forEach(function (p) { ctx.beginPath(); ctx.moveTo(p[0] - 10 / me.a, p[1]); ctx.lineTo(p[0] + 10 / me.a, p[1]); ctx.stroke(); });
        if (k > 0.7) this.text(ctx, S.be_rong.nhan, a[0] + 20 / this.a * this.b * 2, (a[1] + b[1]) / 2, 22 / 1.5, C.dich, { bold: true, align: 'l', alpha: seg(k, 0.7, 1) });
      }
      var gl = seg(u, 0.5, 0.58) * (1 - seg(u, 0.9, 1)) * (0.75 + 0.25 * Math.sin(t * 6));
      if (gl > 0) { this.anim = true; S.dao.forEach(function (d) { if (d.noi_bat) { me.island(ctx, d, gl); me.text(ctx, d.ten, d.nhan[0], d.nhan[1], 18 / 1.5, C.ta, { bold: true, angle: d.goc, alpha: gl }); } }); }
      k = seg(u, 0.64, 0.76) * (0.7 + 0.3 * Math.sin(t * 5));
      if (k > 0) {
        this.anim = true; this.mapMode(ctx);
        S.rach.forEach(function (r) { if (r.ten) { ctx.strokeStyle = rgba(C.vang, 0.7 * k); ctx.lineWidth = r.rong + 8 / me.a; ctx.stroke(pathOf(catmull(r.diem, 10))); } });
        ctx.fillStyle = rgba(C.cay, 0.55 * k);
        this.trees.forEach(function (tr) { ctx.beginPath(); ctx.arc(tr[0], tr[1], tr[2] * 0.62, 0, TAU); ctx.fill(); });
      }
    }
    if (ph === 'mai_phuc' || ph === 'nhu_dich' || ph === 'ket_qua') {
      S.mai_phuc.forEach(function (m, ii) { var kk = ph === 'mai_phuc' ? seg(u, 0.08 + ii * 0.07, 0.2 + ii * 0.07) : 1; me.ambush(ctx, m[0], m[1], m[2], kk); });
      this.hq(ctx, S.dai_ban_doanh[0], S.dai_ban_doanh[1], ph === 'mai_phuc' ? t : 0);
      if (ph === 'mai_phuc') this.anim = true;
    }
    if (ph === 'nhu_dich' || ph === 'ket_qua') {
      var prog = ph === 'nhu_dich' ? 0.15 + 0.85 * seg(u, 0.05, 0.9) : 1;
      S.xiem.forEach(function (a2, ii) { me.arrow(ctx, a2, seg(prog, ii * 0.22, ii * 0.22 + 0.3), C.dich, 4, 7, 0.9); });
      var path = this.duongXiem, d = this.dXiem, Lh = d[d.length - 1] * prog;
      for (i = 0; i < 9; i++) {
        var Lj = Lh - i * 38 / 1.5; if (Lj < 0) break;
        var q = clamp(ssorted(d, Lj), 1, path.length - 1), p2 = path[q], ang = Math.atan2(p2[1] - path[q - 1][1], p2[0] - path[q - 1][0]), off = ((i % 3) - 1) * 16 / 1.5;
        var bx = p2[0] - Math.sin(ang) * off, by = p2[1] + Math.cos(ang) * off;
        var burn = ph === 'ket_qua' ? seg(u, 0.25 + i * 0.03, 0.5 + i * 0.03) : 0;
        this.boat(ctx, bx, by, ang, C.dich, 1 - 0.45 * burn);
        if (burn > 0) this.fire(ctx, bx, by, t, burn, i);
      }
    }
    if (ph === 'ket_qua') {
      S.tay_son.forEach(function (a3, ii) { me.arrow(ctx, a3, seg(u, 0.04 + (ii % 5) * 0.03, 0.3 + (ii % 5) * 0.03), C.ta, 9, 14, 0.95); });
      S.dam_chay.forEach(function (p3, ii) { var kk = seg(u, 0.3 + ii * 0.04, 0.5 + ii * 0.04); if (kk > 0) me.fire(ctx, p3[0], p3[1], t, kk, 100 + ii); });
    }
    if (state.after) state.after(ctx, this);
    ctx.restore();
  };

  // =====================================================================================================
  //  Kí hiệu chú giải (vẽ vào canvas nhỏ trong HTML)
  // =====================================================================================================
  function veChuGiai(cv, loai) {
    var dpr = Math.min(2, window.devicePixelRatio || 1), w = 44, h = 24, ctx = cv.getContext('2d');
    cv.width = w * dpr; cv.height = h * dpr; ctx.scale(dpr, dpr);
    var cx = w / 2, cy = h / 2;
    var fake = Object.create(SaBan.prototype);
    fake.K = 1; fake.u = 1; fake.dpr = dpr; fake.a = 1; fake.bx = 0; fake.by = 0; fake.cache = {}; fake.pathCache = function (i, p, n) { return catmull(p, n); };
    fake.mapMode = function (c) { c.setTransform(dpr, 0, 0, dpr, 0, 0); }; fake.screenMode = fake.mapMode; fake._sym = function (c, x, y, sc, ang) { c.setTransform(dpr, 0, 0, dpr, 0, 0); c.translate(x, y); if (ang) c.rotate(ang * PI / 180); c.scale(sc, sc); };
    ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    switch (loai) {
      case 'mui_ten_ta': fake.arrow(ctx, [[cx - 19, cy], [cx + 19, cy]], 1, C.ta, 5, 8, 1); break;
      case 'mui_ten_dich': fake.arrow(ctx, [[cx - 19, cy], [cx + 19, cy]], 1, C.dich, 2.5, 4.5, 1); break;
      case 'rut_chay': fake.arrow(ctx, [[cx - 20, cy], [cx + 20, cy]], 1, C.dich, 2.5, 2.5, 1, true); break;
      case 'rut_lui': fake.arrow(ctx, [[cx - 20, cy], [cx + 20, cy]], 1, C.ta, 3, 3, 1, true); break;
      case 'vong': ctx.strokeStyle = rgba(C.ta, 0.75); ctx.lineWidth = 3.5; ctx.beginPath(); ctx.arc(cx, cy, 8, 0, TAU); ctx.stroke(); break;
      case 'cu_diem': ctx.fillStyle = 'rgb(38,38,46)'; ctx.beginPath(); ctx.arc(cx, cy + 5, 8, PI, TAU); ctx.closePath(); ctx.fill(); ctx.fillStyle = '#fff'; ctx.fillRect(cx - 3.6, cy + 1.4, 7.2, 2.4); break;
      case 'san_bay': fake._sym(ctx, cx, cy, 0.5, 0); ctx.fillStyle = '#f5f5f0'; ctx.fillRect(-40, -7, 80, 14); ctx.strokeStyle = rgba(C.dich); ctx.lineWidth = 2; ctx.strokeRect(-40, -7, 80, 14); ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(-12, 0); ctx.lineTo(12, 0); ctx.moveTo(2, -9); ctx.lineTo(2, 9); ctx.stroke(); break;
      case 'tuong': ctx.fillStyle = 'rgb(107,102,97)'; ctx.fillRect(cx - 18, cy - 1, 36, 6); [-16, -6, 4, 14].forEach(function (dx) { ctx.fillRect(cx + dx, cy - 7, 5, 6); }); break;
      case 'tran_tuyen': ctx.strokeStyle = 'rgb(31,31,36)'; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(cx - 18, cy); for (var q = 0; q < 4; q++) { var xx = cx - 18 + q * 9; ctx.lineTo(xx, q % 2 ? cy + 5 : cy - 5); ctx.lineTo(xx + 9, q % 2 ? cy + 5 : cy - 5); } ctx.stroke(); break;
      case 'phong_tuyen': fake._sym(ctx, cx, cy + 3, 0.45, 0); ctx.strokeStyle = ctx.fillStyle = rgba(C.ta); ctx.lineWidth = 8; ctx.beginPath(); ctx.arc(0, 26, 30, -150 * PI / 180, -30 * PI / 180); ctx.stroke(); ctx.beginPath(); ctx.moveTo(0, -16); ctx.lineTo(-9, -2); ctx.lineTo(9, -2); ctx.closePath(); ctx.fill(); break;
      case 'sao': fake.star(ctx, cx, cy, 0.8); break;
      case 'don_dich': fake._sym = function (c, x, y, sc) { c.setTransform(dpr, 0, 0, dpr, 0, 0); c.translate(x, y); c.scale(sc * 0.55, sc * 0.55); }; fake.fort(ctx, cx, cy + 5, 0.9, C.dich); break;
      case 'chan_danh': fake._sym = function (c, x, y, sc) { c.setTransform(dpr, 0, 0, dpr, 0, 0); c.translate(x, y); c.scale(sc * 0.55, sc * 0.55); }; fake.block(ctx, cx - 2, cy, 1, 0); break;
      case 'coc': ctx.fillStyle = 'rgb(92,64,38)'; [-8, 0, 8].forEach(function (dx) { ctx.beginPath(); ctx.moveTo(cx + dx - 3, cy + 8); ctx.lineTo(cx + dx, cy - 8); ctx.lineTo(cx + dx + 3, cy + 8); ctx.closePath(); ctx.fill(); }); break;
      case 'mai_phuc': fake._sym = function (c, x, y, sc, ang) { c.setTransform(dpr, 0, 0, dpr, 0, 0); c.translate(x, y); c.scale(0.7, 0.7); }; fake.ambush(ctx, cx, cy + 5, 1, 0); break;
      case 'hq': ctx.fillStyle = '#fff'; ctx.fillRect(cx - 8, cy - 8, 16, 16); ctx.strokeStyle = ctx.fillStyle = rgba(C.ta); ctx.lineWidth = 2; ctx.strokeRect(cx - 8, cy - 8, 16, 16); ctx.fillRect(cx - 4, cy - 4, 8, 8); break;
      case 'thuyen_dich': case 'thuyen_ta': ctx.translate(cx, cy); ctx.fillStyle = rgba(loai === 'thuyen_ta' ? C.ta : C.dich); ctx.beginPath(); ctx.moveTo(-14, -4); ctx.bezierCurveTo(-7, -7, 9, -7, 16, 0); ctx.bezierCurveTo(9, 7, -7, 7, -14, 4); ctx.closePath(); ctx.fill(); break;
      case 'lua': var gg = ctx.createRadialGradient(cx, cy, 0, cx, cy, 10); gg.addColorStop(0, 'rgba(255,242,153,1)'); gg.addColorStop(0.45, 'rgba(255,140,26,.8)'); gg.addColorStop(1, 'rgba(178,26,0,0)'); ctx.fillStyle = gg; ctx.beginPath(); ctx.arc(cx, cy, 10, 0, TAU); ctx.fill(); break;
      case 'thanh': fake._sym = function (c, x, y) { c.setTransform(dpr, 0, 0, dpr, 0, 0); c.translate(x, y); c.scale(0.55, 0.55); }; fake.citadel(ctx, cx, cy + 4, 0); break;
    }
  }

  // =====================================================================================================
  //  Trình phát: thanh pha, phát/dừng, tua, bước, phóng to, lời thuyết minh
  // =====================================================================================================
  function MapPlayer(root, cfg) {
    var me = this, el = MP.el;
    this.cfg = cfg; this.S = cfg.spec;
    this.sb = cfg.legacy ? new SaBanCu(cfg.spec) : new SaBan(cfg.spec, { an: cfg.an });
    this.phases = cfg.phases.filter(function (p) { return me.S.pha ? !!me.S.pha[p.key] : true; });
    this.pi = 0; this.u = 0; this.t = 0; this.playing = false; this.hold = 0; this.dirty = true; this.visible = true;
    this.dur = cfg.thoiLuong || 10;

    var wrap = el('div', { class: 'sb' });
    var title = el('div', { class: 'sb-tieu-de' }, el('b', null, cfg.ten || this.S.ten), el('span', null, cfg.phu_de || this.S.phu_de || ''));
    this.tabs = el('div', { class: 'sb-pha', role: 'tablist', 'aria-label': 'Các giai đoạn' });
    this.tabBtns = this.phases.map(function (p, i) {
      var b = el('button', { type: 'button', role: 'tab', 'aria-selected': 'false', id: 'pha-' + p.key + '-' + (cfg.id || '') }, el('span', { class: 'so' }, String(i + 1)), p.nhan);
      b.addEventListener('click', function () { me.setPhase(i, 0); me.stop(); });
      me.tabs.appendChild(b); return b;
    });
    this.stage = el('div', { class: 'sb-san', tabindex: '0', 'aria-label': 'Lược đồ. Phím cách: phát/dừng; mũi tên trái/phải: lùi/tiến một bước; + và −: phóng to/thu nhỏ.' });
    this.canvas = el('canvas', { role: 'img' });
    this.mocEl = el('div', { class: 'sb-moc', style: { opacity: 0 } });
    this.bangEl = el('div', { class: 'sb-bang', style: { opacity: 0 } });
    var zIn = MP.nutIcon('plus', 'Phóng to'), zOut = MP.nutIcon('minus', 'Thu nhỏ'), zRe = MP.nutIcon('reset', 'Về khung nhìn ban đầu');
    zIn.addEventListener('click', function () { me.zoomAt(me.cw / 2, me.ch / 2, 1.4); });
    zOut.addEventListener('click', function () { me.zoomAt(me.cw / 2, me.ch / 2, 1 / 1.4); });
    zRe.addEventListener('click', function () { me.sb.user = { s: 1, x: 0, y: 0 }; me.touchMode(); me.dirty = true; me.kick(); });
    this.stage.appendChild(this.canvas);
    this.stage.appendChild(el('div', { class: 'sb-phong' }, zIn, zOut, zRe));
    var khungSan = el('div', { class: 'sb-khung' }, this.stage, this.mocEl, this.bangEl);
    if (cfg.overlay) khungSan.appendChild(cfg.overlay);

    this.btnPrev = MP.nutIcon('prev', 'Lùi một bước'); this.btnPlay = MP.nutIcon('play', 'Phát', 'chinh'); this.btnNext = MP.nutIcon('next', 'Tiến một bước');
    this.range = el('input', { type: 'range', min: '0', max: '1000', value: '0', step: '1', 'aria-label': 'Thời gian trong giai đoạn' });
    this.buocEl = el('span', { class: 'buoc', 'aria-live': 'off' });
    this.btnPrev.addEventListener('click', function () { me.stop(); me.step(-1); });
    this.btnNext.addEventListener('click', function () { me.stop(); me.step(1); });
    this.btnPlay.addEventListener('click', function () { me.playing ? me.stop() : me.play(); });
    this.range.addEventListener('input', function () { me.stop(); me.u = me.range.value / 1000; me.amThanh(me.prevU, me.u); me.prevU = me.u; me.dirty = true; me.update(); me.kick(); });
    var ctr = el('div', { class: 'sb-dieu-khien' }, this.btnPrev, this.btnPlay, this.btnNext, this.range, this.buocEl);
    this.legend = el('div', { class: 'sb-chu-giai', 'aria-label': 'Chú giải' });
    this.loiEl = el('div', { class: 'sb-loi', 'aria-live': 'polite' });
    wrap.appendChild(title); wrap.appendChild(this.tabs); wrap.appendChild(khungSan); wrap.appendChild(ctr); wrap.appendChild(this.legend); wrap.appendChild(this.loiEl);
    if (cfg.tomTat) wrap.appendChild(cfg.tomTat);
    root.appendChild(wrap);
    this.ctx = this.canvas.getContext('2d');

    // tương tác: kéo, chụm, cuộn (Ctrl), chạm đúp
    var pts = {}, last = null, pinch0 = null;
    this.canvas.addEventListener('pointerdown', function (e) {
      pts[e.pointerId] = [e.offsetX, e.offsetY];
      if (Object.keys(pts).length === 1) last = [e.offsetX, e.offsetY];
      try { me.canvas.setPointerCapture(e.pointerId); } catch (er) { /* bỏ qua */ }
    });
    this.canvas.addEventListener('pointermove', function (e) {
      if (!pts[e.pointerId]) return;
      pts[e.pointerId] = [e.offsetX, e.offsetY];
      var ids = Object.keys(pts);
      if (ids.length === 2) {
        var a = pts[ids[0]], b = pts[ids[1]], dd = Math.hypot(a[0] - b[0], a[1] - b[1]);
        if (pinch0) me.zoomAt((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, dd / pinch0);
        pinch0 = dd; return;
      }
      if (last && (e.pointerType === 'mouse' || me.sb.user.s > 1.001)) {
        me.sb.user.x += e.offsetX - last[0]; me.sb.user.y += e.offsetY - last[1]; me.clampUser(); me.dirty = true; me.kick();
      }
      last = [e.offsetX, e.offsetY];
    });
    function up(e) { delete pts[e.pointerId]; pinch0 = null; last = Object.keys(pts).length === 1 ? pts[Object.keys(pts)[0]] : null; }
    this.canvas.addEventListener('pointerup', up); this.canvas.addEventListener('pointercancel', up);
    this.canvas.addEventListener('wheel', function (e) {
      if (!(e.ctrlKey || e.metaKey) && me.sb.user.s <= 1.001) return;   // cuộn trang bình thường; Ctrl + cuộn để phóng to
      e.preventDefault(); me.zoomAt(e.offsetX, e.offsetY, Math.exp(-e.deltaY * 0.0015));
    }, { passive: false });
    this.canvas.addEventListener('dblclick', function (e) { me.zoomAt(e.offsetX, e.offsetY, 1.6); });
    this.stage.addEventListener('keydown', function (e) {
      if (e.key === ' ' || e.key === 'Spacebar') { e.preventDefault(); me.playing ? me.stop() : me.play(); }
      else if (e.key === 'ArrowRight') { e.preventDefault(); me.stop(); me.step(1); }
      else if (e.key === 'ArrowLeft') { e.preventDefault(); me.stop(); me.step(-1); }
      else if (e.key === '+' || e.key === '=') me.zoomAt(me.cw / 2, me.ch / 2, 1.3);
      else if (e.key === '-') me.zoomAt(me.cw / 2, me.ch / 2, 1 / 1.3);
    });

    var k = this.S.khung, ar = clamp((k[2] - k[0]) / (k[3] - k[1]), cfg.tiLeMin || 0.78, 1.9);
    this.ar = ar;
    function resize() {
      var w = me.stage.clientWidth || 600, h = Math.round(Math.max(260, Math.min(w / ar, window.innerHeight * 0.74)));
      me.stage.style.height = h + 'px';
      me.cw = w; me.ch = h; me.dpr = Math.min(2, window.devicePixelRatio || 1);
      me.canvas.width = Math.round(w * me.dpr); me.canvas.height = Math.round(h * me.dpr);
      me.sb.layout(w, h); me.dirty = true; me.kick();
    }
    if ('ResizeObserver' in window) new ResizeObserver(resize).observe(this.stage); else window.addEventListener('resize', resize);
    resize();
    MP.khiHien(this.stage, function (v) { me.visible = v; if (v) me.kick(); });
    MP.fontReady.then(function () { me.dirty = true; me.kick(); });
    this.touchMode();
    this.setPhase(0, 0);
  }
  MapPlayer.prototype.touchMode = function () { this.canvas.style.touchAction = this.sb.user.s > 1.001 ? 'none' : 'pan-y'; };
  MapPlayer.prototype.clampUser = function () {
    var us = this.sb.user, cw = this.cw, ch = this.ch;
    us.x = clamp(us.x, cw * 0.7 - us.s * cw, cw * 0.3); us.y = clamp(us.y, ch * 0.7 - us.s * ch, ch * 0.3);
  };
  MapPlayer.prototype.zoomAt = function (x, y, fac) {
    var us = this.sb.user, ns = clamp(us.s * fac, 1, 6); fac = ns / us.s;
    us.x = x - (x - us.x) * fac; us.y = y - (y - us.y) * fac; us.s = ns;
    if (ns <= 1.001) { us.x = 0; us.y = 0; }
    this.clampUser(); this.touchMode(); this.dirty = true; this.kick();
  };
  MapPlayer.prototype.boundaries = function () {
    var ph = this.S.pha ? this.S.pha[this.phases[this.pi].key] : null, b = [];
    if (this.cfg.buoc && this.cfg.buoc[this.phases[this.pi].key]) b = this.cfg.buoc[this.phases[this.pi].key].slice();
    else if (ph) { (ph.buoc || []).forEach(function (s) { b.push(s.den); }); if (ph.bang) b.push(Math.min(1, ph.bang.tu + 0.12)); }
    b.push(1);
    b = b.map(function (x) { return Math.round(x * 1000) / 1000; }).sort(function (x, y) { return x - y; });
    var out = []; b.forEach(function (x) { if (!out.length || x - out[out.length - 1] > 0.035) out.push(x); else out[out.length - 1] = x; });
    return out;
  };
  MapPlayer.prototype.step = function (dir) {
    var B = this.boundaries(), u = this.u, i;
    if (dir > 0) {
      for (i = 0; i < B.length; i++) if (B[i] > u + 0.004) { this.u = B[i]; break; }
      if (i === B.length) { if (this.pi < this.phases.length - 1) this.setPhase(this.pi + 1, 0); return; }
      this.amThanh(u, this.u);
    } else {
      var prev = 0; for (i = B.length - 1; i >= 0; i--) if (B[i] < u - 0.004) { prev = B[i]; break; }
      if (u <= 0.004) { if (this.pi > 0) this.setPhase(this.pi - 1, 1); return; }
      this.u = i < 0 ? 0 : prev; MP.am('lat_trang');
    }
    this.prevU = this.u;
    this.dirty = true; this.update(); this.kick();
  };
  MapPlayer.prototype.setPhase = function (i, u) {
    var me = this;
    this.pi = i; this.u = u || 0; this.sb.user = { s: 1, x: 0, y: 0 }; this.touchMode();
    this.tabBtns.forEach(function (b, j) { b.setAttribute('aria-selected', j === i ? 'true' : 'false'); if (j === i && b.scrollIntoView && me.inited) b.scrollIntoView({ block: 'nearest', inline: 'nearest' }); });
    this.inited = true;
    var p = this.phases[i];
    this.canvas.setAttribute('aria-label', (this.cfg.ten || this.S.ten) + ' – ' + p.nhan);
    // chú giải
    this.legend.innerHTML = '';
    var ds = this.cfg.chuGiai ? this.cfg.chuGiai(p.key) : (this.S.chu_giai || []).filter(function (c) { var ph = me.S.pha[p.key]; return !ph.chu_giai || ph.chu_giai.indexOf(c.loai) >= 0; }).map(function (c) { return [c.loai, c.nhan]; });
    ds.forEach(function (c) { if (!c[1]) return; var cv = MP.el('canvas', { 'aria-hidden': 'true' }); veChuGiai(cv, c[0]); me.legend.appendChild(MP.el('span', null, cv, c[1])); });
    this.legend.hidden = !this.legend.childNodes.length;
    // lời thuyết minh từ kịch bản
    var lines = p.loi || MP.loi(p.canh || []), trs = p.tr || MP.trangCanh(p.canh || []);
    MP.hopLoi(this.loiEl, lines, trs);
    // âm thanh: nền theo pha, tiếng mở pha (trống trận...) khi người dùng chuyển pha
    var am = this.cfg.am || {};
    MP.nen((am.nenPha && am.nenPha[p.key]) || am.nen || []);
    if (this.inited2) MP.am(typeof am.batDau === 'function' ? am.batDau(p.key) : (am.batDau || 'mo_pha'), { n: 3 });
    this.inited2 = true; this.prevU = this.u;
    this.dirty = true; this.update(); this.kick();
    if (this.cfg.onPhase) this.cfg.onPhase(p.key, this);
  };
  /** Âm thanh gắn với từng bước của pha: khi thời gian đi qua điểm bắt đầu của bước */
  var AM_MAC_DINH = { mui_ten_ta: 'vut', mui_ten_dich: 'vut_nhe', rut_chay: 'buoc_quan', rut_lui: 'buoc_quan', sao: 'chuong_nho', mai_phuc: 'soat',
    coc: 'go', thuyen_ta: 'mai_cheo', thuyen_dich: 'mai_cheo', lua: 'lua_bung', vong: 'trong_nho', chan_danh: 'trong_nho', tuong: 'dat', phong_tuyen: 'trong_nho',
    don_dich: 'click', cu_diem: 'click', thanh_sang: 'chuong_nho', san_bay: 'click', tran_tuyen: 'buoc_quan', nhan: null };
  MapPlayer.prototype.amThanh = function (u0, u1) {
    var am = this.cfg.am; if (!am || !window.AT || u1 <= u0 || u1 - u0 > 0.6) return;
    var key = this.phases[this.pi].key, ph = this.S.pha ? this.S.pha[key] : null, objs = this.S.doi_tuong || {}, me = this, n = 0;
    function qua(x) { return x > u0 && x <= u1; }
    function chon(id, o, kieu) {
      var r = am.doiTuong ? am.doiTuong(id, o, kieu, key) : undefined;
      if (r !== undefined) return r;
      if (kieu === 'mat') return am.no ? 'no' : 'gay_go';
      return AM_MAC_DINH[o.loai];
    }
    if (ph) {
      (ph.buoc || []).forEach(function (st) {
        if (n >= 3 || !qua(st.tu) || me.sb.an && me.sb.an[st.id] || !objs[st.id]) return;
        var ten = chon(st.id, objs[st.id], st.hieu_ung === 'mat' ? 'mat' : 'hien');
        if (ten) { [].concat(ten).forEach(function (x) { MP.am(x); }); n++; }
      });
      Object.keys(ph.mac_ket || {}).forEach(function (id) { if (qua(ph.mac_ket[id][0])) { MP.am('cot_ket'); MP.am('te_nuoc', { tre: 0.6 }); } });
      var bang = (this.cfg.bang && this.cfg.bang[key] !== undefined) ? this.cfg.bang[key] : ph.bang;
      if (bang && qua(bang.tu)) { MP.am(am.bang || 'reo'); if (am.trongBang !== false) MP.am('trong', { n: 4, gap: 0.28, tre: 0.15 }); }
    }
    ((am.moc && am.moc[key]) || []).forEach(function (c) { if (qua(c[0])) MP.am(c[1], c[2]); });
  };
  MapPlayer.prototype.play = function () {
    if (this.u >= 0.999) { if (this.pi < this.phases.length - 1) this.setPhase(this.pi + 1, 0); else this.setPhase(0, 0); }
    this.playing = true; this.hold = 0; this.prevU = this.u; MP.setIcon(this.btnPlay, 'pause', 'Tạm dừng'); MP.am('click'); this.kick();
  };
  MapPlayer.prototype.stop = function () { this.playing = false; MP.setIcon(this.btnPlay, 'play', 'Phát'); };
  MapPlayer.prototype.kick = function () {
    var me = this;
    if (this.raf || !this.visible) return;
    this.raf = requestAnimationFrame(function loop(ts) {
      me.raf = 0;
      var dt = me.lastTs ? Math.min(0.1, (ts - me.lastTs) / 1000) : 0; me.lastTs = ts;
      if (me.playing) {
        if (me.u < 1) { me.u = Math.min(1, me.u + dt / me.dur); me.dirty = true; me.update(); me.amThanh(me.prevU, me.u); me.prevU = me.u; }
        else { me.hold += dt; if (me.hold > 1.4) { me.hold = 0; if (me.pi < me.phases.length - 1) me.setPhase(me.pi + 1, 0); else me.stop(); } }
      }
      if (me.dirty || me.sb.anim) { me.t += dt; me.draw(); me.dirty = false; }
      if ((me.playing || me.sb.anim) && me.visible) me.kick(); else me.lastTs = 0;
    });
  };
  MapPlayer.prototype.update = function () {
    this.range.value = Math.round(this.u * 1000); MP.toThanh(this.range);
    var B = this.boundaries(), n = 0; for (var i = 0; i < B.length; i++) if (B[i] <= this.u + 0.004) n++;
    this.buocEl.textContent = 'Bước ' + n + '/' + B.length;
    var key = this.phases[this.pi].key, ph = this.S.pha ? this.S.pha[key] : {}, u = this.u;
    // mốc thời gian
    var mocs = (this.cfg.moc && this.cfg.moc[key]) || (ph && ph.moc) || [], best = null, ba = 0;
    mocs.forEach(function (m) { var den = m.den == null ? 1.1 : m.den, a = seg(u, m.tu, m.tu + 0.06) * (1 - seg(u, den - 0.05, den)); if (u <= 0.001 && m.tu <= 0.06) a = 1; if (a > ba) { ba = a; best = m; } });
    this.mocEl.textContent = best ? best.chu : ''; this.mocEl.style.opacity = best ? ba : 0;
    // băng rôn
    var bang = (this.cfg.bang && this.cfg.bang[key] !== undefined) ? this.cfg.bang[key] : (ph && ph.bang);
    var bk = bang ? seg(u, bang.tu, bang.tu + 0.1) : 0;
    this.bangEl.textContent = bang ? bang.chu : ''; this.bangEl.style.opacity = bk; this.bangEl.style.setProperty('--k', 0.9 + 0.1 * bk);
    this.bangEl.classList.toggle('khong-co', !bang);
    if (this.cfg.overlayUpdate) this.cfg.overlayUpdate(key, u, this);
  };
  MapPlayer.prototype.draw = function () {
    var key = this.phases[this.pi].key, sb = this.sb, cfg = this.cfg, u = this.u;
    var cam = cfg.cam ? cfg.cam(key, u, sb) : sb.camFor(key, u);
    var items = sb.items(key, u);
    if (cfg.items) items = cfg.items(key, u, items, sb);
    var me = this;
    sb.render(this.ctx, this.dpr, {
      cam: cam, items: items, t: this.t, phase: key, u: u,
      style: cfg.style ? function (id, o) { return cfg.style(id, o, key, u, me); } : null,
      after: cfg.after ? function (ctx, s) { cfg.after(ctx, s, key, u, me); } : null
    });
  };

  /** Thước mực nước (dùng cho các trận Bạch Đằng) */
  function thuocNuoc(opts) {
    var el = MP.el, box = el('div', { class: 'thuoc-nuoc', 'aria-hidden': 'true' });
    var cot = el('div', { class: 'cot' }), nuoc = el('div', { class: 'nuoc' });
    [12, 40, 68, 96].forEach(function (x) { cot.appendChild(el('div', { class: 'coc', style: { left: x + '%' } })); });
    cot.appendChild(nuoc);
    var t1 = el('b'), t2 = el('span');
    box.appendChild(el('span', null, 'Mực nước')); box.appendChild(cot); box.appendChild(t1); box.appendChild(t2);
    return {
      el: box,
      set: function (muc, tieuDe, ghiChu) { nuoc.style.height = Math.round(clamp(muc, 0.05, 1) * 100) + '%'; t1.textContent = tieuDe || ''; t2.textContent = ghiChu || ''; box.style.display = tieuDe ? '' : 'none'; }
    };
  }

  /** Danh sách tóm tắt mốc thời gian lấy từ cảnh "trục thời gian" của kịch bản */
  function tomTat(soCanh, tieuDe) {
    var c = MP.canh(soCanh); if (!c || !c.moc) return null;
    var el = MP.el, ol = el('ol', { class: 'dong-moc' });
    c.moc.forEach(function (m) { ol.appendChild(el('li', null, el('b', null, m[0]), el('span', null, m[1]))); });
    return el('div', { class: 'tom-tat' }, el('h3', null, tieuDe || 'Tóm tắt diễn biến'), ol, el('p', { class: 'sb-loi tr', style: { background: 'none', border: 0, padding: '4px 0 0', fontSize: '.8rem', color: 'var(--chu-phu)' } }, MP.trang(c.tr)));
  }

  window.SaBanWeb = { SaBan: SaBan, SaBanCu: SaBanCu, MapPlayer: MapPlayer, veChuGiai: veChuGiai, thuocNuoc: thuocNuoc, tomTat: tomTat,
    C: C, rgba: rgba, catmull: catmull, cut: cut, cumlen: cumlen, seg: seg, ease: ease, FONT: FONT };
})();
