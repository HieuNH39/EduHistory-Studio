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
