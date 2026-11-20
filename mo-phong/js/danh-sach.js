/* Trang danh sách mô phỏng: lọc theo loại và theo lớp; tạm dừng hình động khi người xem chọn giảm chuyển động. */
(function () {
  'use strict';
  var loai = 'tat-ca', lop = 'tat-ca';
  var nutLoai = [].slice.call(document.querySelectorAll('.nut-loc[data-loc]'));
  var nutLop = [].slice.call(document.querySelectorAll('.nut-loc[data-lop]'));
  function ve() {
    var con = 0;
    document.querySelectorAll('.luoi-the > li').forEach(function (li) {
      var hien = (loai === 'tat-ca' || li.getAttribute('data-nhom') === loai) && (lop === 'tat-ca' || li.getAttribute('data-lop') === lop);
      li.hidden = !hien; if (hien) con++;
    });
    document.querySelectorAll('.nhom-lop').forEach(function (s) { s.hidden = !s.querySelector('li:not([hidden])'); });
    var kc = document.querySelector('.khong-co'); if (kc) kc.hidden = con > 0;
  }
  function chon(ds, nut) {
    ds.forEach(function (m) { var on = m === nut; m.classList.toggle('dang-chon', on); m.setAttribute('aria-pressed', on ? 'true' : 'false'); });
  }
  nutLoai.forEach(function (n) { n.addEventListener('click', function () { loai = n.getAttribute('data-loc'); chon(nutLoai, n); ve(); }); });
  nutLop.forEach(function (n) { n.addEventListener('click', function () { lop = n.getAttribute('data-lop'); chon(nutLop, n); ve(); }); });
  var holo = document.querySelector('svg.holo');
  if (holo && window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches && holo.pauseAnimations) holo.pauseAnimations();
})();
