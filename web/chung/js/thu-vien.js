/* EduHistory Studio – Kho học liệu số: lọc và tìm kiếm thư viện, phát video, câu hỏi luyện tập.
   Trang đã có sẵn nội dung (sinh bởi web/_cong-cu/tao_thu_vien.py); tệp này chỉ thêm tương tác.
   Không gọi mạng, không cookie, không lưu dữ liệu người xem. */
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
          if (yt) yt.hidden = false;
          else if (loi) loi.hidden = false;
        };
        if (src) src.addEventListener('error', hong);
        v.addEventListener('error', hong);
        if (v.networkState === 3) hong(); // NETWORK_NO_SOURCE: lỗi xảy ra trước khi tệp này chạy
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
          if (q.trang) phanHoi.appendChild(el('p', 'xem-sgk', 'Xem lại SGK ' + du.sach + ', trang ' + q.trang + '.'));
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

  function batDau() { thuVien(); video(); luyenTap(); }
  if (document.readyState !== 'loading') batDau();
  else document.addEventListener('DOMContentLoaded', batDau);
})();
