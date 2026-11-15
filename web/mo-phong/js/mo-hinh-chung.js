/* EduHistory – tiện ích chung cho các trang mô hình 3D mới (15/11/2026): bố cục hai cột, thanh trượt,
   thẻ thông tin, thẻ "Theo SGK" lấy lời thuyết minh từ kịch bản đã đối chiếu SGK (MP_TAP). */
(function () {
  'use strict';
  var el = MP.el;
  function boCuc(root) {
    var luoi = el('div', { class: 'luoi-2' }), trai = el('div'), phai = el('div', { class: 'bang-dk' });
    luoi.appendChild(trai); luoi.appendChild(phai); root.appendChild(luoi);
    return { trai: trai, phai: phai };
  }
  function truot(nhan, min, max, step, val, fmt, onInput) {
    var r = el('input', { type: 'range', min: min, max: max, step: step, value: val });
    var o = el('output', null, fmt(val)); MP.toThanh(r);
    var w = el('label', { class: 'nhan-truot' }, el('span', null, nhan), r, o);
    r.addEventListener('input', function () { o.textContent = fmt(+r.value); MP.toThanh(r); if (onInput) onInput(+r.value); });
    return { w: w, r: r, o: o, dat: function (v) { r.value = v; o.textContent = fmt(+v); MP.toThanh(r); } };
  }
  function nut(chu, chinh, fn) {
    var b = el('button', { type: 'button', class: 'nut' + (chinh ? ' chinh' : '') }, chu);
    b.addEventListener('click', fn); return b;
  }
  function theTin(phai) {
    var t = el('div', { class: 'the-tin', 'aria-live': 'polite' }); phai.appendChild(t);
    return function (tieuDe, noiDung) {
      t.innerHTML = ''; t.appendChild(el('h3', null, tieuDe));
      [].concat(noiDung).forEach(function (p) { t.appendChild(el('p', null, p)); });
    };
  }
  function theoSGK(phai, soCanh, them) {
    var c = el('div', { class: 'the-tin' }, el('h3', null, 'Theo SGK'));
    var ul = el('ul');
    MP.loi(soCanh).concat(them || []).forEach(function (l) { if (l) ul.appendChild(el('li', null, l)); });
    c.appendChild(ul);
    c.appendChild(el('p', { class: 'sb-loi tr', style: { background: 'none', border: 0, padding: '6px 0 0', fontSize: '.8rem' } }, MP.trang(MP.trangCanh(soCanh))));
    phai.appendChild(c); return c;
  }
  function dieuKhien(phai, tieuDe, items) {
    var c = el('div', { class: 'the-tin' }, el('h3', null, tieuDe));
    items.forEach(function (x) { c.appendChild(x); });
    phai.appendChild(c); return c;
  }
  function hangNut(list) { var h = el('div', { class: 'hang-nut', style: { marginTop: '8px' } }); list.forEach(function (b) { h.appendChild(b); }); return h; }
  /** chạm (không kéo) lên canvas → gọi fn(ndc) */
  function khiCham(V, fn) {
    var down = null, ndc = new V.T.Vector2();
    V.renderer.domElement.addEventListener('pointerdown', function (e) { down = [e.clientX, e.clientY]; });
    V.renderer.domElement.addEventListener('pointerup', function (e) {
      if (!down || Math.hypot(e.clientX - down[0], e.clientY - down[1]) > 6) return;
      var r = V.renderer.domElement.getBoundingClientRect();
      ndc.set((e.clientX - r.left) / r.width * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
      fn(ndc);
    });
  }
  /** ô vải/giấy vẽ bằng canvas 2D làm vân bề mặt */
  function vanCanvas(w, h, ve) {
    var c = document.createElement('canvas'); c.width = w; c.height = h; ve(c.getContext('2d'), w, h);
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; return t;
  }
  window.MH = { boCuc: boCuc, truot: truot, nut: nut, theTin: theTin, theoSGK: theoSGK, dieuKhien: dieuKhien, hangNut: hangNut, khiCham: khiCham, vanCanvas: vanCanvas };
})();
