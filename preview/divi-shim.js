/* Alleen voor de preview: inschuif-animaties en uitklapvragen,
   zoals Divi dat op de echte site zelf regelt. */
(function () {
  var els = document.querySelectorAll('[data-vv-anim]');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('vv-in'); io.unobserve(e.target); } });
    }, { threshold: 0.12 });
    els.forEach(function (el) { io.observe(el); });
  } else { els.forEach(function (el) { el.classList.add('vv-in'); }); }
  document.querySelectorAll('.et_pb_toggle_title').forEach(function (t) {
    t.addEventListener('click', function () {
      var item = t.parentNode;
      var open = item.classList.contains('et_pb_toggle_open');
      item.classList.toggle('et_pb_toggle_open', !open);
      item.classList.toggle('et_pb_toggle_close', open);
    });
  });
})();
