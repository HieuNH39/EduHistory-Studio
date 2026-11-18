/* EduHistory Studio – Kho học liệu số: lọc và tìm kiếm thư viện, phát video, câu hỏi luyện tập,
   mục lục bên trái, thả tim / chia sẻ / tải về / bình luận / sao chép mã video.
   Trang đã có sẵn nội dung (sinh bởi web/_cong-cu/tao_thu_vien.py); tệp này chỉ thêm tương tác.
   Không gọi mạng, không cookie. Tim và bình luận chỉ lưu trong bộ nhớ trình duyệt của chính người xem (localStorage). */
(function () {
  'use strict';

  function $(sel, root) { return (root || document).querySelector(sel); }
  function $$(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }
  /** Bỏ dấu tiếng Việt để tìm "bach dang" cũng ra "Bạch Đằng" (khớp cách sinh data-tim ở tao_thu_vien.py) */
  function boDau(s) {
    return String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '')
      .replace(/đ/g, 'd').replace(/Đ/g, 'D').toLowerCase().replace(/\s+/g, ' ').trim();
  }
  var itChuyenDong = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function cuonToi(elm) { if (elm) elm.scrollIntoView({ behavior: itChuyenDong ? 'auto' : 'smooth', block: 'start' }); }
  function doiDiaChi(hash) {
    try { history.replaceState(null, '', hash || (location.pathname + location.search)); } catch (e) { /* file:// cũ */ }
  }

  /* ================================================================ thư viện (index.html) */
  function thuVien() {
    var tv = document.getElementById('thu-vien');
    if (!tv) return;
    var dong = $$('.tap-dong[data-tim]', tv);
    var bai = $$('.bai', tv), chuong = $$('.chuong', tv), lop = $$('.lop', tv);
    var tim = document.getElementById('tim');
    var ketQua = document.getElementById('ket-qua');
    var khongThay = document.getElementById('khong-thay');
    var xoa = document.getElementById('xoa-loc');
    var chuyen = document.getElementById('chuyen-bai');
    var keVideo = $('.ke-video');
    var bia = $('.bia');
    var goiY = document.getElementById('goi-y-tim');
    var goiYGoc = goiY ? goiY.textContent : '';
    var oLop = $$('.o-lop');
    var chip = $$('.chip[data-nhom]');
    var st = { lop: '', khung: '', tt: '', q: '' };
    var hen = null, lanDau = true;

    function macDinh() { return !st.lop && !st.khung && !st.tt && !st.q; }

    function apDung() {
      var tu = boDau(st.q).split(' ').filter(Boolean);
      var nTap = 0, nBai = 0;
      dong.forEach(function (r) {
        var ok = (!st.lop || r.getAttribute('data-lop') === st.lop) &&
          (!st.khung || r.getAttribute('data-khung') === st.khung) &&
          (!st.tt || (st.tt === 'co-video') === (r.getAttribute('data-tt') === 'co-video'));
        if (ok && tu.length) {
          var t = r.getAttribute('data-tim');
          for (var i = 0; i < tu.length; i++) if (t.indexOf(tu[i]) < 0) { ok = false; break; }
        }
        r.hidden = !ok;
        if (ok) nTap++;
      });
      bai.forEach(function (b) {
        var co = !!b.querySelector('.tap-dong:not([hidden])');
        if (!b.querySelector('.tap-dong')) co = !tu.length && !st.khung && !st.tt && (!st.lop || b.getAttribute('data-lop') === st.lop);
        b.hidden = !co;
        if (co) nBai++;
      });
      chuong.forEach(function (c) { c.hidden = !c.querySelector('.bai:not([hidden])'); });
      lop.forEach(function (l) { l.hidden = !l.querySelector('.bai:not([hidden])'); });

      var md = macDinh();
      if (keVideo) keVideo.hidden = !md;
      // đang tìm: thu gọn ô chọn lớp để kết quả hiện gần ô tìm (nhất là trên điện thoại)
      if (bia) bia.classList.toggle('dang-tim', !!st.q);
      if (goiY) goiY.textContent = st.q ? (nTap ? 'Tìm thấy ' + nTap + ' tập, xem ngay bên dưới.' : 'Không tìm thấy tập nào.') : goiYGoc;
      xoa.hidden = md;
      ketQua.textContent = md
        ? 'Toàn bộ thư viện: ' + nTap + ' tập trong ' + nBai + ' bài.'
        : (nTap ? 'Đang hiện ' + nTap + ' tập trong ' + nBai + ' bài' + (st.lop ? ' của lớp ' + st.lop : '') + '.' : 'Không có tập nào phù hợp.');
      khongThay.hidden = nTap > 0;
      if (!nTap) {
        khongThay.textContent = (st.q ? 'Không tìm thấy tập nào khớp với “' + st.q + '”' : 'Không có tập nào phù hợp với bộ lọc đang chọn') +
          '. Hãy thử từ khoá ngắn hơn, chọn lớp khác hoặc bấm “Xoá bộ lọc”.';
      }
      chip.forEach(function (c) { c.setAttribute('aria-pressed', String(st[c.getAttribute('data-nhom')] === c.getAttribute('data-gt'))); });
      oLop.forEach(function (o) {
        if (o.getAttribute('data-lop') === st.lop) o.setAttribute('aria-current', 'true');
        else o.removeAttribute('aria-current');
      });
      // chuyển nhanh tới bài (khi đã chọn một lớp)
      var nhan = chuyen.parentNode;
      var dsBai = bai.filter(function (b) { return !b.hidden && b.getAttribute('data-lop') === st.lop; });
      nhan.hidden = !st.lop || dsBai.length < 2;
      if (!nhan.hidden) {
        chuyen.innerHTML = '';
        chuyen.appendChild(new Option('Chọn bài…', ''));
        dsBai.forEach(function (b) {
          chuyen.appendChild(new Option($('.so-bai', b).textContent + '. ' + $('h4', b).textContent, b.id));
        });
      }
      if (!lanDau) doiDiaChi(st.lop ? '#lop-' + st.lop : '');
    }

    function chonLop(l, cuon) {
      st.lop = l || '';
      apDung();
      if (cuon) {
        var h = st.lop ? $('#h-lop-' + st.lop) : null;
        cuonToi(st.lop ? document.getElementById('lop-' + st.lop) : tv);
        if (h) { h.setAttribute('tabindex', '-1'); h.focus({ preventScroll: true }); }
      }
    }

    chip.forEach(function (c) {
      c.addEventListener('click', function () {
        var nhom = c.getAttribute('data-nhom');
        st[nhom] = c.getAttribute('data-gt');
        apDung();
      });
    });
    oLop.forEach(function (o) {
      o.addEventListener('click', function (ev) {
        ev.preventDefault();
        chonLop(o.getAttribute('data-lop'), true);
      });
    });
    tim.addEventListener('input', function () {
      clearTimeout(hen);
      hen = setTimeout(function () { st.q = tim.value.trim(); apDung(); }, 220);
    });
    tim.addEventListener('keydown', function (ev) {
      if (ev.key === 'Enter') { ev.preventDefault(); clearTimeout(hen); st.q = tim.value.trim(); apDung(); cuonToi(tv); }
      if (ev.key === 'Escape') { tim.value = ''; st.q = ''; apDung(); }
    });
    xoa.addEventListener('click', function () {
      st = { lop: '', khung: '', tt: '', q: '' };
      tim.value = '';
      apDung();
      tim.focus();
    });
    chuyen.addEventListener('change', function () {
      var b = chuyen.value && document.getElementById(chuyen.value);
      if (!b) return;
      cuonToi(b);
      var h = $('h4', b);
      h.setAttribute('tabindex', '-1');
      h.focus({ preventScroll: true });
    });

    function theoDiaChi() {
      var h = decodeURIComponent(location.hash.slice(1));
      var m;
      bai.forEach(function (b) { b.classList.remove('duoc-chon'); });
      if ((m = /^lop-([6-9])$/.exec(h))) { chonLop(m[1], true); return; }
      if ((m = /^L([6-9])-(?:B|CD)\d+$/.exec(h)) && document.getElementById(h)) {
        st.lop = m[1];
        apDung();
        var b = document.getElementById(h);
        b.classList.add('duoc-chon');
        cuonToi(b);
        return;
      }
      apDung();
    }
    window.addEventListener('hashchange', theoDiaChi);
    theoDiaChi();
    lanDau = false;
  }

  /* ================================================================ trang tập: video */
  function video() {
    $$('.khung-video').forEach(function (k) {
      var v = $('video', k), loi = $('.video-loi', k), yt = $('.yt', k);
      if (v) {
        var src = $('source', v);
        var daBao = false;
        var hong = function () {
          if (daBao) return;
          daBao = true;
          v.hidden = true;
          k.classList.remove('co-dk');
          $$('.dk-video, .dk-giua, .dk-het, .dk-nhan', k.parentNode).forEach(function (x) { x.hidden = true; });
          if (yt) yt.hidden = false;
          else if (loi) loi.hidden = false;
        };
        if (src) src.addEventListener('error', hong);
        v.addEventListener('error', hong);
        if (v.networkState === 3) hong(); // NETWORK_NO_SOURCE: lỗi xảy ra trước khi tệp này chạy
        else dieuKhien(k, v);
      }
      if (yt) {
        var a = $('.nut-yt', yt);
        a.addEventListener('click', function (ev) {
          // Mở file:// thì YouTube từ chối nhúng – để liên kết mở YouTube ở thẻ mới.
          if (location.protocol !== 'http:' && location.protocol !== 'https:') return;
          ev.preventDefault();
          var f = document.createElement('iframe');
          f.src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(yt.getAttribute('data-yt')) + '?autoplay=1&rel=0';
          f.title = 'Video trên YouTube: ' + (yt.getAttribute('data-ten') || '');
          f.setAttribute('allow', 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share');
          f.setAttribute('allowfullscreen', '');
          f.setAttribute('referrerpolicy', 'strict-origin-when-cross-origin');
          yt.replaceChild(f, a);
          f.focus();
        });
      }
    });
  }

  /* ================================================================ trang tập: thanh điều khiển video
     Thay thanh mặc định của trình duyệt bằng thanh riêng: tập trước / lùi 15 giây / phát – dừng / tua 15 giây / tập sau,
     thanh thời gian, tắt tiếng, toàn màn hình. Không có JavaScript thì video vẫn dùng thanh mặc định (thuộc tính controls). */
  var ICV = {
    phat: '<path d="M8 5.5v13l11-6.5z" fill="currentColor"/>',
    dung: '<path d="M7 5h3.6v14H7zM13.4 5H17v14h-3.6z" fill="currentColor"/>',
    lui: '<path d="M12 5a7 7 0 1 1-6.6 9.3" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><path d="M12 2.2v5.6L8.2 5z" fill="currentColor"/><text x="12.2" y="15.6" text-anchor="middle" font-size="7.2" font-weight="700" fill="currentColor" font-family="system-ui,sans-serif">15</text>',
    toi: '<path d="M12 5a7 7 0 1 0 6.6 9.3" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><path d="M12 2.2v5.6L15.8 5z" fill="currentColor"/><text x="11.8" y="15.6" text-anchor="middle" font-size="7.2" font-weight="700" fill="currentColor" font-family="system-ui,sans-serif">15</text>',
    truoc: '<path d="M6 5h2.2v14H6zM19 5.5v13L9.6 12z" fill="currentColor"/>',
    sau: '<path d="M15.8 5H18v14h-2.2zM5 5.5v13L14.4 12z" fill="currentColor"/>',
    am: '<path d="M4 9.5h3.6L12 6v12l-4.4-3.5H4z" fill="currentColor"/><path d="M15 9a4.2 4.2 0 0 1 0 6M17.4 6.6a7.6 7.6 0 0 1 0 10.8" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
    tat: '<path d="M4 9.5h3.6L12 6v12l-4.4-3.5H4z" fill="currentColor"/><path d="M15.5 9.5l5 5M20.5 9.5l-5 5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
    to: '<path d="M4 9V4h5M15 4h5v5M20 15v5h-5M9 20H4v-5" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/>',
    nho: '<path d="M9 4v5H4M20 9h-5V4M15 20v-5h5M4 15h5v5" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/>'
  };
  function icv(ten) { return '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">' + ICV[ten] + '</svg>'; }
  function mmss(t) {
    if (!isFinite(t) || t < 0) t = 0;
    var m = Math.floor(t / 60), g = Math.floor(t % 60);
    return m + ':' + (g < 10 ? '0' : '') + g;
  }
  function dieuKhien(k, v) {
    var BUOC = 15;
    v.removeAttribute('controls');
    k.classList.add('co-dk');
    var nutTo = function (cls, ten, nhan, phim) {
      var b = el('button', 'dk ' + cls);
      b.type = 'button';
      b.innerHTML = icv(ten);
      b.setAttribute('aria-label', nhan);
      b.title = nhan + (phim ? ' (phím ' + phim + ')' : '');
      return b;
    };
    var lienKet = function (cls, ten, kieu, phim) {
      var href = k.getAttribute('data-' + kieu), tenTap = k.getAttribute('data-ten-' + kieu);
      var nhan = (kieu === 'truoc' ? 'Tập trước' : 'Tập sau');
      if (!href) {
        var tat = nutTo(cls, ten, nhan + ': không có');
        tat.setAttribute('aria-disabled', 'true'); tat.disabled = true;
        return tat;
      }
      var a = el('a', 'dk ' + cls);
      a.href = href; a.innerHTML = icv(ten);
      a.setAttribute('aria-label', nhan + ': ' + tenTap);
      a.title = nhan + ': ' + tenTap + ' (phím ' + phim + ')';
      return a;
    };
    var thanh = el('div', 'dk-video');
    thanh.setAttribute('role', 'group');
    thanh.setAttribute('aria-label', 'Điều khiển video');
    var tua = document.createElement('input');
    tua.type = 'range'; tua.className = 'dk-tua'; tua.min = '0'; tua.max = '1000'; tua.step = '1'; tua.value = '0';
    tua.setAttribute('aria-label', 'Thanh thời gian: kéo để tua video');
    var hang = el('div', 'dk-hang');
    var truoc = lienKet('dk-truoc', 'truoc', 'truoc', 'Shift + P');
    var lui = nutTo('dk-lui', 'lui', 'Lùi 15 giây', '←');
    var phat = nutTo('dk-phat', 'phat', 'Phát video', 'cách');
    var toi = nutTo('dk-toi', 'toi', 'Tua tới 15 giây', '→');
    var sau = lienKet('dk-sau', 'sau', 'sau', 'Shift + N');
    var tg = el('span', 'dk-tg', '0:00 / ' + mmss(v.duration));
    tg.setAttribute('aria-hidden', 'true');
    var dem = el('span', 'dk-dem');
    var am = nutTo('dk-am', 'am', 'Tắt tiếng', 'M');
    var to = nutTo('dk-to', 'to', 'Xem toàn màn hình', 'F');
    [truoc, lui, phat, toi, sau, tg, dem, am, to].forEach(function (x) { hang.appendChild(x); });
    thanh.appendChild(tua);
    thanh.appendChild(hang);
    var giua = el('button', 'dk-giua');
    giua.type = 'button'; giua.innerHTML = icv('phat'); giua.setAttribute('aria-label', 'Phát video');
    var het = el('div', 'dk-het'); het.hidden = true;
    var xemLai = el('button', 'dk-het-nut', 'Xem lại'); xemLai.type = 'button';
    het.appendChild(xemLai);
    var hrefSau = k.getAttribute('data-sau');
    if (hrefSau) {
      var tiep = el('a', 'dk-het-nut chinh'); tiep.href = hrefSau;
      tiep.appendChild(el('span', 'nho', 'Tập tiếp theo'));
      tiep.appendChild(el('span', null, k.getAttribute('data-ten-sau') || ''));
      het.appendChild(tiep);
    }
    k.appendChild(giua);
    k.appendChild(het);
    // thanh nằm ngay dưới khung hình (không che phụ đề gắn sẵn ở đáy video); khung + thanh cùng vào một vỏ để phóng toàn màn hình
    var vo = el('div', 'trinh-phat' + (k.classList.contains('doc') ? ' doc' : ''));
    k.parentNode.insertBefore(vo, k);
    vo.appendChild(k);
    vo.appendChild(thanh);

    function batTat() { if (v.paused || v.ended) { var p = v.play(); if (p && p.catch) p.catch(function () {}); } else v.pause(); }
    function nhay(d) {
      if (!isFinite(v.duration)) return;
      v.currentTime = Math.max(0, Math.min(v.duration - 0.05, v.currentTime + d));
      thongBaoNgan((d < 0 ? 'Lùi ' : 'Tua tới ') + Math.abs(d) + ' giây');
    }
    var nhanTam = el('div', 'dk-nhan'); nhanTam.setAttribute('aria-live', 'polite'); k.appendChild(nhanTam);
    var henNhan;
    function thongBaoNgan(chu) {
      nhanTam.textContent = chu; nhanTam.classList.add('hien');
      clearTimeout(henNhan); henNhan = setTimeout(function () { nhanTam.classList.remove('hien'); }, 900);
    }
    function capNhatPhat() {
      var dang = !v.paused && !v.ended;
      phat.innerHTML = icv(dang ? 'dung' : 'phat');
      phat.setAttribute('aria-label', dang ? 'Tạm dừng' : 'Phát video');
      phat.title = (dang ? 'Tạm dừng' : 'Phát video') + ' (phím cách)';
      k.classList.toggle('dang-phat', dang);
      giua.hidden = dang || v.ended;
      if (dang) het.hidden = true;
      hienThanh();
    }
    var keo = false;
    function capNhatTg() {
      var d = v.duration;
      if (!keo && isFinite(d) && d > 0) {
        tua.value = String(Math.round(v.currentTime / d * 1000));
        tua.style.setProperty('--da', (v.currentTime / d * 100) + '%');
      }
      tg.textContent = mmss(v.currentTime) + ' / ' + mmss(d);
      tua.setAttribute('aria-valuetext', mmss(v.currentTime) + ' trên ' + mmss(d));
    }
    tua.addEventListener('input', function () {
      keo = true;
      if (isFinite(v.duration)) {
        v.currentTime = tua.value / 1000 * v.duration;
        tua.style.setProperty('--da', (tua.value / 10) + '%');
      }
    });
    tua.addEventListener('change', function () { keo = false; capNhatTg(); });
    phat.addEventListener('click', batTat);
    giua.addEventListener('click', batTat);
    v.addEventListener('click', batTat);
    lui.addEventListener('click', function () { nhay(-BUOC); });
    toi.addEventListener('click', function () { nhay(BUOC); });
    am.addEventListener('click', function () { v.muted = !v.muted; });
    v.addEventListener('volumechange', function () {
      am.innerHTML = icv(v.muted ? 'tat' : 'am');
      am.setAttribute('aria-label', v.muted ? 'Bật tiếng' : 'Tắt tiếng');
      am.title = (v.muted ? 'Bật tiếng' : 'Tắt tiếng') + ' (phím M)';
    });
    var fsEl = function () { return document.fullscreenElement || document.webkitFullscreenElement; };
    to.addEventListener('click', function () {
      if (fsEl()) { (document.exitFullscreen || document.webkitExitFullscreen).call(document); return; }
      if (vo.requestFullscreen) vo.requestFullscreen();
      else if (vo.webkitRequestFullscreen) vo.webkitRequestFullscreen();
      else if (v.webkitEnterFullscreen) v.webkitEnterFullscreen(); // iPhone: chỉ phóng to được chính thẻ video
    });
    ['fullscreenchange', 'webkitfullscreenchange'].forEach(function (ev) {
      document.addEventListener(ev, function () {
        var dang = fsEl() === vo;
        vo.classList.toggle('toan-man-hinh', dang);
        to.innerHTML = icv(dang ? 'nho' : 'to');
        to.setAttribute('aria-label', dang ? 'Thoát toàn màn hình' : 'Xem toàn màn hình');
      });
    });
    xemLai.addEventListener('click', function () { v.currentTime = 0; batTat(); });
    ['play', 'pause', 'ended'].forEach(function (ev) { v.addEventListener(ev, capNhatPhat); });
    v.addEventListener('ended', function () { het.hidden = false; giua.hidden = true; var n = $('.dk-het-nut.chinh', het) || xemLai; n.focus(); });
    ['timeupdate', 'durationchange', 'loadedmetadata', 'seeked'].forEach(function (ev) { v.addEventListener(ev, capNhatTg); });
    // khi đang phát mà không đụng chuột 2,5 giây thì ẩn con trỏ trên khung hình
    var hen;
    function hienThanh() {
      k.classList.remove('an-dk');
      clearTimeout(hen);
      if (!v.paused && !v.ended) hen = setTimeout(function () { k.classList.add('an-dk'); }, 2500);
    }
    ['mousemove', 'touchstart'].forEach(function (ev) { k.addEventListener(ev, hienThanh, { passive: true }); });
    // phím tắt khi con trỏ không ở ô nhập chữ: cách/K phát–dừng, ←/→ lùi/tua 15 giây, M tắt tiếng, F toàn màn hình, Shift+N/P tập sau/trước
    document.addEventListener('keydown', function (ev) {
      var t = ev.target, tag = (t && t.tagName) || '';
      if (ev.altKey || ev.ctrlKey || ev.metaKey) return;
      if (/^(INPUT|TEXTAREA|SELECT)$/.test(tag) && t !== tua) return;
      if (t && t.isContentEditable) return;
      if (/^(BUTTON|A)$/.test(tag) && (ev.key === ' ' || ev.key === 'Enter') && !vo.contains(t)) return;
      // chỉ nhận phím khi con trỏ ở trong khung video, hoặc chưa chọn gì mà khung video đang hiện trên màn hình
      var r = k.getBoundingClientRect();
      var thay = r.bottom > 60 && r.top < (window.innerHeight || 800) - 60;
      if (!vo.contains(t) && !((t === document.body || t === document.documentElement || !t) && thay)) return;
      var ph = ev.key;
      if (ph === ' ' || ph === 'k' || ph === 'K') { if (/^(BUTTON|A)$/.test(tag) && ph === ' ') return; ev.preventDefault(); batTat(); }
      else if (ph === 'ArrowLeft' && t !== tua) { ev.preventDefault(); nhay(-BUOC); }
      else if (ph === 'ArrowRight' && t !== tua) { ev.preventDefault(); nhay(BUOC); }
      else if (ph === 'm' || ph === 'M') { v.muted = !v.muted; }
      else if (ph === 'f' || ph === 'F') { to.click(); }
      else if ((ph === 'N' || ph === 'n') && ev.shiftKey && k.getAttribute('data-sau')) { location.href = k.getAttribute('data-sau'); }
      else if ((ph === 'P' || ph === 'p') && ev.shiftKey && k.getAttribute('data-truoc')) { location.href = k.getAttribute('data-truoc'); }
      else return;
      hienThanh();
    });
    capNhatPhat(); capNhatTg();
  }

  /* ================================================================ trang tập: câu hỏi luyện tập */
  function luyenTap() {
    var hop = document.getElementById('cau-hoi');
    var nguon = document.getElementById('du-lieu-cau-hoi');
    if (!hop || !nguon) return;
    var du;
    try { du = JSON.parse(nguon.textContent); } catch (e) { return; }
    if (!du || !du.cau || !du.cau.length) return;
    var CHU = 'ABCDEFG';

    function tron(a) {
      for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)), t = a[i]; a[i] = a[j]; a[j] = t; }
      return a;
    }

    function ve(daoDapAn) {
      var dung = 0, xong = 0, n = du.cau.length;
      hop.innerHTML = '';
      var tong = el('div', 'tong-ket');
      tong.setAttribute('role', 'status');
      tong.hidden = true;

      du.cau.forEach(function (q, qi) {
        var thuTu = q.dap_an.map(function (_, i) { return i; });
        if (daoDapAn) tron(thuTu);
        var fs = el('fieldset', 'cau');
        var lg = el('legend');
        lg.appendChild(el('span', 'so-cau', 'Câu ' + (qi + 1) + '.'));
        lg.appendChild(document.createTextNode(q.hoi));
        fs.appendChild(lg);
        var luoi = el('div', 'lua-chon');
        var phanHoi = el('div', 'phan-hoi');
        phanHoi.setAttribute('aria-live', 'polite');
        var nut = thuTu.map(function (ai, vt) {
          var b = el('button');
          b.type = 'button';
          b.appendChild(el('b', null, CHU[vt]));
          b.appendChild(el('span', null, q.dap_an[ai]));
          b.addEventListener('click', function () { chon(vt); });
          luoi.appendChild(b);
          return b;
        });
        function chon(vt) {
          if (fs.getAttribute('data-xong')) return;
          fs.setAttribute('data-xong', '1');
          xong++;
          var ok = thuTu[vt] === q.dung;
          if (ok) dung++;
          var vtDung = thuTu.indexOf(q.dung);
          nut.forEach(function (b, p) {
            b.setAttribute('aria-disabled', 'true');
            if (p === vtDung) { b.classList.add('dung'); b.appendChild(el('span', 'an-chu', ' (đáp án đúng)')); }
            else if (p === vt) { b.classList.add('sai'); b.appendChild(el('span', 'an-chu', ' (em đã chọn)')); }
          });
          phanHoi.appendChild(el('p', 'ket ' + (ok ? 'dung' : 'sai'),
            ok ? 'Chính xác!' : 'Chưa đúng. Đáp án đúng: ' + CHU[vtDung] + '. ' + q.dap_an[q.dung] + '.'));
          if (q.giai_thich) phanHoi.appendChild(el('p', 'giai-thich', 'Trong video: “' + q.giai_thich + '”'));
          if (q.trang) {
            var xs = el('p', 'xem-sgk', 'Xem lại SGK ' + du.sach + ', ');
            if (du.sgk) {
              var lk = el('a', 'lk-sgk', 'trang ' + q.trang);
              lk.href = du.sgk + '#page=' + parseInt(q.trang, 10);
              lk.target = '_blank'; lk.rel = 'noopener noreferrer';
              lk.title = 'Mở SGK điện tử ở trang ' + q.trang + ' (thẻ mới)';
              xs.appendChild(lk); xs.appendChild(document.createTextNode('.'));
            } else xs.appendChild(document.createTextNode('trang ' + q.trang + '.'));
            phanHoi.appendChild(xs);
          }
          if (xong === n) ketThuc();
        }
        fs.appendChild(luoi);
        fs.appendChild(phanHoi);
        hop.appendChild(fs);
      });

      function ketThuc() {
        tong.innerHTML = '';
        var p = el('p');
        p.appendChild(el('span', 'diem', dung + '/' + n));
        p.appendChild(document.createTextNode(dung === n ? 'Tuyệt vời, em trả lời đúng tất cả!'
          : (dung * 2 >= n ? 'Khá lắm! Xem lại câu sai theo số trang SGK nhé.' : 'Hãy xem lại video và SGK rồi thử lại nhé.')));
        tong.appendChild(p);
        var lam = el('button', 'nut-lam-lai', 'Làm lại (đảo thứ tự đáp án)');
        lam.type = 'button';
        lam.addEventListener('click', function () {
          ve(true);
          var dau = $('.lua-chon button', hop);
          if (dau) dau.focus();
        });
        tong.appendChild(lam);
        tong.hidden = false;
      }
      hop.appendChild(tong);
    }
    ve(false);
  }


  /* ================================================================ bộ nhớ trên máy người xem (an toàn khi bị chặn) */
  var KHO = 'eduhistory:';
  function docKho(k, macDinh) {
    try { var v = window.localStorage.getItem(KHO + k); return v == null ? macDinh : JSON.parse(v); } catch (e) { return macDinh; }
  }
  function ghiKho(k, v) {
    try { window.localStorage.setItem(KHO + k, JSON.stringify(v)); return true; } catch (e) { return false; }
  }
  var goc = (document.body && document.body.getAttribute('data-goc')) || '';

  /* ================================================================ thông báo nhỏ */
  var henTat = null;
  function thongBao(chu) {
    var t = $('.thong-bao');
    if (!t) return;
    t.textContent = chu; t.hidden = false; t.classList.add('hien');
    clearTimeout(henTat);
    henTat = setTimeout(function () { t.classList.remove('hien'); setTimeout(function () { t.hidden = true; }, 250); }, 2400);
  }
  function saoChep(chu, xong) {
    function duPhong() {
      var o = el('textarea'); o.value = chu; o.setAttribute('readonly', ''); o.style.position = 'fixed'; o.style.opacity = '0';
      document.body.appendChild(o); o.select();
      var ok = false; try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
      document.body.removeChild(o);
      xong(ok);
    }
    if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(chu).then(function () { xong(true); }, duPhong);
    else duPhong();
  }

  /* ================================================================ mục lục bên trái */
  function mucLuc() {
    var nut = $('.nut-menu'), ngan = document.getElementById('ngan-menu'), nen = $('.nen-menu');
    if (!nut || !ngan) return;
    var daNap = false;
    function veDaThich() {
      var hop = $('.da-thich', ngan), ul = $('ul', hop), ds = docKho('tim', []), menu = window.EDU_MENU;
      ul.textContent = '';
      if (!ds.length || !menu) { hop.hidden = true; return; }
      var ten = {};
      menu.lop.forEach(function (l) { l.bai.forEach(function (b) { b.tap.forEach(function (t) { ten[t.ma] = t.ten; }); }); });
      ds.forEach(function (ma) {
        if (!ten[ma]) return;
        var li = el('li'), a = el('a', 'muc-tap co-video', ten[ma]);
        a.href = goc + 'tap/' + ma + '.html'; li.appendChild(a); ul.appendChild(li);
      });
      hop.hidden = !ul.children.length;
    }
    function dung() {
      var cay = $('.cay-menu', ngan), menu = window.EDU_MENU;
      cay.textContent = '';
      var tapNay = document.querySelector('[data-trang="tap"]');
      var maHienTai = tapNay ? tapNay.getAttribute('data-ma') : null;
      menu.lop.forEach(function (l) {
        var dl = el('details', 'menu-lop'), sl = el('summary');
        sl.appendChild(el('span', 'so', String(l.lop)));
        sl.appendChild(el('span', 'ten', 'Lịch sử ' + l.lop));
        var dv = 0; l.bai.forEach(function (b) { b.tap.forEach(function (t) { dv += t.v; }); });
        sl.appendChild(el('span', 'dem', dv + ' video'));
        dl.appendChild(sl);
        var ol = el('ol', 'menu-bai');
        l.bai.forEach(function (b) {
          var li = el('li'), db = el('details', 'menu-mot-bai'), sb = el('summary');
          sb.appendChild(el('span', 'nhan', b.nhan));
          sb.appendChild(el('span', 'ten', b.ten));
          db.appendChild(sb);
          var con = el('div', 'menu-con');
          var cv = b.tap.filter(function (t) { return t.v; });
          if (cv.length) {
            con.appendChild(el('p', 'nhom', 'Video'));
            var u = el('ul');
            cv.forEach(function (t) {
              var a = el('a', 'muc-tap co-video'); a.href = goc + 'tap/' + t.ma + '.html';
              a.appendChild(el('span', 'ten', t.ten)); if (t.tl) a.appendChild(el('span', 'tl', t.tl));
              if (t.ma === maHienTai) { a.setAttribute('aria-current', 'page'); db.open = true; dl.open = true; }
              var li2 = el('li'); li2.appendChild(a); u.appendChild(li2);
            });
            con.appendChild(u);
          }
          if (b.mp.length) {
            con.appendChild(el('p', 'nhom', 'Mô phỏng'));
            var u2 = el('ul');
            b.mp.forEach(function (m) {
              var a = el('a', 'muc-mp'); a.href = goc + m.href;
              a.appendChild(el('span', 'ten', m.ten)); a.appendChild(el('span', 'tl', m.loai));
              if (location.pathname.slice(-m.href.length) === m.href) { a.setAttribute('aria-current', 'page'); db.open = true; dl.open = true; }
              var li3 = el('li'); li3.appendChild(a); u2.appendChild(li3);
            });
            con.appendChild(u2);
          }
          var khac = b.tap.filter(function (t) { return !t.v; });
          if (khac.length) {
            con.appendChild(el('p', 'nhom', 'Ôn tập (video đang dựng)'));
            var u3 = el('ul');
            khac.forEach(function (t) {
              var a = el('a', 'muc-tap'); a.href = goc + 'tap/' + t.ma + '.html'; a.appendChild(el('span', 'ten', t.ten));
              if (t.ma === maHienTai) { a.setAttribute('aria-current', 'page'); db.open = true; dl.open = true; }
              var li4 = el('li'); li4.appendChild(a); u3.appendChild(li4);
            });
            con.appendChild(u3);
          }
          if (!con.children.length) con.appendChild(el('p', 'trong', 'Bài này đang được viết kịch bản.'));
          db.appendChild(con); li.appendChild(db); ol.appendChild(li);
        });
        dl.appendChild(ol); cay.appendChild(dl);
      });
      veDaThich();
      var dangMo = $('[aria-current="page"]', cay);
      if (dangMo) setTimeout(function () { dangMo.scrollIntoView({ block: 'center' }); }, 30);
    }
    function nap(xong) {
      if (window.EDU_MENU) { xong(); return; }
      var sc = document.createElement('script');
      sc.src = ngan.getAttribute('data-nguon');
      sc.onload = xong;
      sc.onerror = function () { $('.cay-menu', ngan).textContent = 'Không tải được mục lục.'; };
      document.head.appendChild(sc);
    }
    function mo() {
      ngan.hidden = false; nen.hidden = false;
      requestAnimationFrame(function () { ngan.classList.add('mo'); nen.classList.add('mo'); });
      nut.setAttribute('aria-expanded', 'true');
      document.documentElement.classList.add('khoa-cuon');
      if (!daNap) { daNap = true; nap(dung); } else veDaThich();
      setTimeout(function () { var d = $('.nut-dong-menu', ngan); if (d) d.focus(); }, 60);
    }
    function dong() {
      ngan.classList.remove('mo'); nen.classList.remove('mo');
      nut.setAttribute('aria-expanded', 'false');
      document.documentElement.classList.remove('khoa-cuon');
      setTimeout(function () { ngan.hidden = true; nen.hidden = true; }, itChuyenDong ? 0 : 240);
      nut.focus();
    }
    nut.addEventListener('click', function () { if (ngan.hidden) mo(); else dong(); });
    $('.nut-dong-menu', ngan).addEventListener('click', dong);
    nen.addEventListener('click', dong);
    document.addEventListener('keydown', function (ev) { if (ev.key === 'Escape' && !ngan.hidden) dong(); });
  }

  /* ================================================================ trang tập: quay lại, thanh hành động */
  function quayLai() {
    $$('[data-quay-lai]').forEach(function (a) {
      a.addEventListener('click', function (ev) {
        var cung = false;
        try { cung = document.referrer && new URL(document.referrer).origin === location.origin && history.length > 1; } catch (e) { cung = false; }
        if (cung) { ev.preventDefault(); history.back(); }
      });
    });
  }

  function hanhDong() {
    $$('.hanh-dong').forEach(function (h) {
      var ma = h.getAttribute('data-ma'), ten = h.getAttribute('data-ten') || ma;
      // thả tim
      var tim = $('.hd-tim', h);
      function veTim() {
        var co = docKho('tim', []).indexOf(ma) >= 0;
        tim.setAttribute('aria-pressed', co ? 'true' : 'false');
        $('span', tim).textContent = co ? 'Đã thích' : 'Thích';
      }
      veTim();
      tim.addEventListener('click', function () {
        var ds = docKho('tim', []), i = ds.indexOf(ma);
        if (i >= 0) ds.splice(i, 1); else ds.unshift(ma);
        if (!ghiKho('tim', ds)) { thongBao('Trình duyệt đang chặn bộ nhớ nên chưa lưu được lượt thích.'); return; }
        veTim();
        if (i < 0) { tim.classList.remove('no'); void tim.offsetWidth; tim.classList.add('no'); thongBao('Đã thêm vào “Video em đã thích” trong Mục lục.'); }
      });
      // chia sẻ
      $('.hd-chia-se', h).addEventListener('click', function () {
        var url = location.href.split('#')[0];
        var du = { title: ten + ' | EduHistory', text: 'Cùng xem video Lịch sử “' + ten + '” trên EduHistory', url: url };
        if (navigator.share && /^https?:/.test(location.protocol)) {
          navigator.share(du).catch(function () { /* người xem huỷ */ });
        } else {
          saoChep(url, function (ok) { thongBao(ok ? 'Đã sao chép đường link video để em gửi cho bạn.' : 'Chưa sao chép được, em hãy sao chép địa chỉ trên thanh trình duyệt.'); });
        }
      });
      // sao chép mã
      $('.hd-ma', h).addEventListener('click', function () {
        saoChep(ma, function (ok) { thongBao(ok ? 'Đã sao chép mã video ' + ma + '. Dán vào ô tìm kiếm của thư viện để mở lại.' : 'Mã video: ' + ma); });
      });
      // tải về: trên file:// trình duyệt có thể mở thay vì tải – vẫn để mặc định
      var tai = $('.hd-tai', h);
      if (tai) tai.addEventListener('click', function () { thongBao('Đang tải video ' + ma + ' về máy…'); });
      // bình luận
      var nutBl = $('.hd-bl', h), hop = document.getElementById('bl-' + ma);
      if (!nutBl || !hop) return;
      var ds = $('.bl-ds', hop), o = $('textarea', hop);
      function ve() {
        var bl = docKho('bl:' + ma, []);
        ds.textContent = '';
        bl.forEach(function (b, i) {
          var li = el('li'), tg = new Date(b.t);
          var dau = el('p', 'bl-dau');
          dau.appendChild(el('span', 'bl-ai', 'Em'));
          dau.appendChild(el('time', 'bl-tg', tg.toLocaleString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })));
          var x = el('button', 'bl-xoa'); x.type = 'button'; x.setAttribute('aria-label', 'Xoá bình luận này'); x.textContent = 'Xoá';
          x.addEventListener('click', function () { var b2 = docKho('bl:' + ma, []); b2.splice(i, 1); ghiKho('bl:' + ma, b2); ve(); });
          dau.appendChild(x);
          li.appendChild(dau); li.appendChild(el('p', 'bl-chu', b.c)); ds.appendChild(li);
        });
        $('span', nutBl).textContent = bl.length ? 'Bình luận (' + bl.length + ')' : 'Bình luận';
      }
      ve();
      nutBl.addEventListener('click', function () {
        var mo = hop.hidden;
        hop.hidden = !mo; nutBl.setAttribute('aria-expanded', mo ? 'true' : 'false');
        if (mo) o.focus();
      });
      $('form', hop).addEventListener('submit', function (ev) {
        ev.preventDefault();
        var c = o.value.replace(/\s+/g, ' ').trim();
        if (!c) { o.focus(); return; }
        var bl = docKho('bl:' + ma, []); bl.unshift({ c: c.slice(0, 500), t: Date.now() });
        if (!ghiKho('bl:' + ma, bl)) { thongBao('Trình duyệt đang chặn bộ nhớ nên chưa lưu được bình luận.'); return; }
        o.value = ''; ve(); thongBao('Đã lưu bình luận trên máy của em.');
      });
    });
  }

  function batDau() { mucLuc(); quayLai(); hanhDong(); thuVien(); video(); luyenTap(); }
  if (document.readyState !== 'loading') batDau();
  else document.addEventListener('DOMContentLoaded', batDau);
})();
