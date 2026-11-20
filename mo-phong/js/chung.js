/* EduHistory Studio – tiện ích dùng chung cho các trang mô phỏng.
   Dữ liệu tập (MP_TAP) do _cong-cu/tao_trang.py sinh từ kịch bản đã đối chiếu SGK. Không gọi mạng, không theo dõi người dùng. */
(function () {
  'use strict';
  var TAP = window.MP_TAP || { canh: [], cau_hoi: [] };

  function el(tag, attrs) {
    var e = document.createElement(tag), i, k;
    if (attrs) for (k in attrs) {
      if (!Object.prototype.hasOwnProperty.call(attrs, k) || attrs[k] == null || attrs[k] === false) continue;
      if (k === 'class') e.className = attrs[k];
      else if (k === 'text') e.textContent = attrs[k];
      else if (k === 'html') e.innerHTML = attrs[k];
      else if (k.slice(0, 2) === 'on' && typeof attrs[k] === 'function') e.addEventListener(k.slice(2), attrs[k]);
      else if (k === 'style' && typeof attrs[k] === 'object') Object.assign(e.style, attrs[k]);
      else e.setAttribute(k, attrs[k] === true ? '' : attrs[k]);
    }
    for (i = 2; i < arguments.length; i++) {
      var c = arguments[i];
      if (c == null || c === false) continue;
      if (Array.isArray(c)) c.forEach(function (x) { if (x != null) e.appendChild(typeof x === 'string' ? document.createTextNode(x) : x); });
      else e.appendChild(typeof c === 'string' || typeof c === 'number' ? document.createTextNode(String(c)) : c);
    }
    return e;
  }

  var ICON = {
    play: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 4.5v15a1 1 0 0 0 1.5.86l12.2-7.5a1 1 0 0 0 0-1.72L8.5 3.64A1 1 0 0 0 7 4.5z"/></svg>',
    pause: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 4h4v16H6zM14 4h4v16h-4z"/></svg>',
    prev: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 5h2.5v14H6zM20 5.6v12.8a.8.8 0 0 1-1.25.66L9.6 12.66a.8.8 0 0 1 0-1.32l9.15-6.4A.8.8 0 0 1 20 5.6z"/></svg>',
    next: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15.5 5H18v14h-2.5zM4 5.6v12.8a.8.8 0 0 0 1.25.66l9.15-6.4a.8.8 0 0 0 0-1.32l-9.15-6.4A.8.8 0 0 0 4 5.6z"/></svg>',
    plus: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M11 5h2v6h6v2h-6v6h-2v-6H5v-2h6z"/></svg>',
    minus: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 11h14v2H5z"/></svg>',
    reset: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5a7 7 0 1 1-6.93 8h2.03A5 5 0 1 0 12 7v3L7.5 6 12 2z"/></svg>',
    check: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9.5 16.2 5.3 12l-1.4 1.4 5.6 5.6L20.1 8.4 18.7 7z"/></svg>'
  };
  function nutIcon(name, label, extraClass) {
    var b = el('button', { type: 'button', class: 'nut tron ' + (extraClass || ''), 'aria-label': label, title: label });
    b.innerHTML = ICON[name];
    return b;
  }
  function setIcon(btn, name, label) { btn.innerHTML = ICON[name]; btn.setAttribute('aria-label', label); btn.title = label; }

  function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }
  function lerp(a, b, t) { return a + (b - a) * t; }
  function ease(t) { t = clamp(t, 0, 1); return t * t * (3 - 2 * t); }
  function seg(u, a, b) { return ease((u - a) / Math.max(1e-6, b - a)); }

  /** 2233 -> "2 233" (dấu cách không ngắt, như cách viết số trong SGK) */
  function so(n) {
    var s = String(Math.abs(Math.round(n))), out = '';
    while (s.length > 3) { out = ' ' + s.slice(-3) + out; s = s.slice(0, -3); }
    return (n < 0 ? '−' : '') + s + out;
  }
  function laMa(n) {
    var v = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1], r = ['M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I'], s = '';
    for (var i = 0; i < v.length; i++) while (n >= v[i]) { s += r[i]; n -= v[i]; }
    return s;
  }
  function trang(trs) {
    var t = (trs || []).filter(function (x, i, a) { return x != null && a.indexOf(x) === i; }).map(Number).sort(function (a, b) { return a - b; });
    var out = [], i = 0;
    while (i < t.length) { var j = i; while (j + 1 < t.length && t[j + 1] === t[j] + 1) j++; out.push(i === j ? String(t[i]) : t[i] + '–' + t[j]); i = j + 1; }
    return out.length ? 'SGK tr. ' + out.join(', ') : '';
  }

  /** Cảnh theo số; lời thuyết minh (người dẫn chuyện) của một hoặc nhiều cảnh */
  function canh(so_) { for (var i = 0; i < TAP.canh.length; i++) if (TAP.canh[i].so === so_) return TAP.canh[i]; return null; }
  function canhSaBan(ten, pha) { return TAP.canh.filter(function (c) { return c.sa_ban === ten && (pha == null || c.pha === pha); }); }
  function loi(soList) {
    var out = [];
    [].concat(soList).forEach(function (s) { var c = typeof s === 'object' ? s : canh(s); if (c) out = out.concat(c.loi); });
    return out;
  }
  function trangCanh(soList) {
    var t = [];
    [].concat(soList).forEach(function (s) { var c = typeof s === 'object' ? s : canh(s); if (c) t = t.concat(c.tr || []); });
    return t;
  }
  function moc(so_) { var c = canh(so_); return c && c.moc ? c.moc : []; }

  /** Hộp lời thuyết minh: các đoạn văn + dòng trang SGK */
  /** Âm thanh (nếu có js/am-thanh.js) */
  function am(ten, o) { if (window.AT) window.AT.phat(ten, o); }
  function nen(list) { if (window.AT) window.AT.nen(list); }

  function hopLoi(container, lines, trs) {
    container.innerHTML = '';
    (lines || []).forEach(function (l) { container.appendChild(el('p', null, l)); });
    if (trs && trs.length) container.appendChild(el('p', { class: 'tr' }, trang(trs)));
  }

  /** Câu hỏi nhanh: lấy từ danh sách câu hỏi của kịch bản */
  function quiz(container, questions) {
    if (!container) return;
    var dung = 0, xong = 0, L = 'ABCD';
    container.innerHTML = '';
    var diem = el('p', { class: 'diem-so', 'aria-live': 'polite' });
    questions.forEach(function (q, qi) {
      var fb = el('p', { class: 'phan-hoi', 'aria-live': 'polite' });
      var grid = el('div', { class: 'lua-chon', role: 'group', 'aria-label': 'Các lựa chọn câu ' + (qi + 1) });
      var buttons = q.dap_an.map(function (a, ai) {
        var b = el('button', { type: 'button', class: 'nut' }, el('b', null, L[ai]), el('span', null, a));
        b.addEventListener('click', function () {
          if (grid.dataset.xong) return;
          grid.dataset.xong = '1'; xong++;
          var ok = ai === q.dung;
          if (ok) dung++;
          if (window.AT) window.AT.phat(ok ? 'chuong' : 'sai');
          buttons.forEach(function (bb, bi) {
            bb.setAttribute('aria-disabled', 'true');
            if (bi === q.dung) bb.classList.add('dung');
            else if (bi === ai) bb.classList.add('sai');
          });
          fb.className = 'phan-hoi ' + (ok ? 'dung' : 'sai');
          fb.textContent = (ok ? 'Chính xác! ' : 'Chưa đúng. Đáp án đúng: ' + L[q.dung] + '. ' + q.dap_an[q.dung] + '. ') + '(' + trang(q.tr) + ')';
          capNhat();
        });
        return b;
      });
      buttons.forEach(function (b) { grid.appendChild(b); });
      container.appendChild(el('div', { class: 'cau' }, el('p', { class: 'hoi' }, el('span', null, 'Câu ' + (qi + 1) + '.'), q.hoi), grid, fb));
    });
    var lam = el('button', { type: 'button', class: 'nut', onclick: function () { quiz(container, questions); } }, 'Làm lại');
    container.appendChild(diem);
    function capNhat() {
      diem.innerHTML = '';
      if (xong === questions.length) {
        if (window.AT && dung === questions.length) window.AT.phat('reo', { lv: 0.6, tre: 0.9 });
        diem.appendChild(el('span', null, 'Kết quả: đúng ' + dung + '/' + questions.length + ' câu. ' + (dung === questions.length ? 'Tuyệt vời!' : 'Xem lại mô phỏng rồi thử lại nhé!')));
        diem.appendChild(lam);
      }
    }
  }

  /** Thanh trượt: tô phần đã đi */
  function toThanh(r) { var mn = +r.min || 0, mx = +r.max || 100; r.style.setProperty('--pct', ((r.value - mn) / (mx - mn) * 100) + '%'); }

  /** Chờ phông chữ (để vẽ chữ trên canvas đúng phông) */
  var fontReady = (document.fonts && document.fonts.load)
    ? Promise.all(['400 16px "Be Vietnam Pro"', '700 16px "Be Vietnam Pro"', '600 16px "Be Vietnam Pro"', 'italic 400 16px "Be Vietnam Pro"', '800 16px "Be Vietnam Pro"']
      .map(function (f) { return document.fonts.load(f, 'ĐđƯơ'); })).catch(function () {})
    : Promise.resolve();

  function onReady(fn) { if (document.readyState !== 'loading') fn(); else document.addEventListener('DOMContentLoaded', fn); }

  /** Chỉ chạy vòng lặp khi khối đang hiện trên màn hình */
  function khiHien(elm, cb) {
    if (!('IntersectionObserver' in window)) { cb(true); return; }
    new IntersectionObserver(function (es) { es.forEach(function (e) { cb(e.isIntersecting); }); }, { threshold: 0.01 }).observe(elm);
  }

  window.MP = {
    tap: TAP, el: el, ICON: ICON, nutIcon: nutIcon, setIcon: setIcon, clamp: clamp, lerp: lerp, ease: ease, seg: seg,
    so: so, laMa: laMa, trang: trang, canh: canh, canhSaBan: canhSaBan, loi: loi, trangCanh: trangCanh, moc: moc,
    hopLoi: hopLoi, quiz: quiz, am: am, nen: nen, toThanh: toThanh, fontReady: fontReady, onReady: onReady, khiHien: khiHien,
    khung: function () { return document.getElementById('mo-phong'); }
  };

  onReady(function () { quiz(document.getElementById('cau-hoi'), TAP.cau_hoi || []); });
})();
