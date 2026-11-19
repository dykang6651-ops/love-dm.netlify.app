/* 지난 회차 숨기기와 하단 바 표시. 일정은 tools/schedule.py에서 빌드한다. */
(function () {
  var now = Date.now();
  var timed = document.querySelectorAll('[data-at]');
  for (var i = 0; i < timed.length; i++) {
    var t = Date.parse(timed[i].getAttribute('data-at'));
    if (!isNaN(t) && t <= now) timed[i].parentNode.removeChild(timed[i]);
  }
  // 묶음마다 남은 것 중 첫 회차만 보인다.
  var picks = document.querySelectorAll('[data-pick]');
  for (i = 0; i < picks.length; i++) {
    var kids = picks[i].children, first = null;
    for (var j = 0; j < kids.length; j++) {
      if (!kids[j].hasAttribute('data-at')) continue;
      if (!first) { first = kids[j]; first.hidden = false; } else { kids[j].hidden = true; }
    }
    for (j = 0; j < kids.length; j++) if (kids[j].hasAttribute('data-empty')) kids[j].hidden = !!first;
  }
  // 일정표: 가장 가까운 날짜 카드만 강조(class="near").
  var list = document.querySelector('[data-list]');
  if (list) {
    var cards = list.querySelectorAll('[data-at]');
    var empty = list.querySelector('[data-empty]');
    if (empty) empty.hidden = cards.length > 0;
    if (cards.length) {
      var day = cards[0].getAttribute('data-day');
      for (i = 0; i < cards.length; i++) {
        cards[i].classList.toggle('near', cards[i].getAttribute('data-day') === day);
      }
    }
  }
  // 일정표나 신청 띠가 화면에 보이면 하단 바를 내린다.
  var bar = document.querySelector('.mbar');
  if (bar && 'IntersectionObserver' in window) {
    var ids = ['schedule', 'apply'], seen = {};
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { seen[en.target.id] = en.isIntersecting; });
      var on = false;
      for (var k in seen) if (seen[k]) on = true;
      bar.classList.toggle('off', on);
    });
    ids.forEach(function (id) { var el = document.getElementById(id); if (el) io.observe(el); });
  }
})();

/* 클릭 반응, 헤더 그림자, 지금 보는 메뉴 표시, 스크롤하며 나타나기. 스타일은 assets/fx.css. */
(function () {
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // 누른 자리에서 물결이 퍼진다.
  document.addEventListener('pointerdown', function (ev) {
    if (reduce) return;
    var el = ev.target.closest && ev.target.closest('.btn, .btn-card, .chip, .lk, .mbar a, .nx, .toc a');
    if (!el || el.classList.contains('off') || el.classList.contains('on') && el.classList.contains('lk')) return;
    var r = el.getBoundingClientRect(), size = Math.max(r.width, r.height) * 2.2;
    var dot = document.createElement('span');
    var bg = getComputedStyle(el).backgroundColor;
    var light = /255, 255, 255|rgba\(0, 0, 0, 0\)|255, 244, 247|255, 247, 250/.test(bg);
    dot.className = 'rip' + (light ? ' dk' : '');
    dot.style.width = dot.style.height = size + 'px';
    dot.style.left = (ev.clientX - r.left - size / 2) + 'px';
    dot.style.top = (ev.clientY - r.top - size / 2) + 'px';
    el.appendChild(dot);
    setTimeout(function () { if (dot.parentNode) dot.parentNode.removeChild(dot); }, 650);
  });

  // 스크롤하면 헤더에 그림자.
  var hd = document.querySelector('.hd');
  function onScroll() { if (hd) hd.classList.toggle('scrolled', window.scrollY > 8); }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  if (!('IntersectionObserver' in window)) return;

  // 지금 보고 있는 섹션의 메뉴(홈 헤더, 서브페이지 목차)에 표시.
  var links = document.querySelectorAll('.nl[href^="#"], .toc a[href^="#"]');
  var byId = {};
  for (var i = 0; i < links.length; i++) {
    var id = links[i].getAttribute('href').slice(1);
    (byId[id] = byId[id] || []).push(links[i]);
  }
  var spy = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (!en.isIntersecting) return;
      for (var k = 0; k < links.length; k++) links[k].classList.remove('on');
      (byId[en.target.id] || []).forEach(function (a) {
        a.classList.add('on');
        if (a.parentNode && a.parentNode.scrollTo && a.closest('.toc')) {
          a.parentNode.scrollTo({ left: a.offsetLeft - 24, behavior: reduce ? 'auto' : 'smooth' });
        }
      });
    });
  }, { rootMargin: '-40% 0px -55% 0px' });
  Object.keys(byId).forEach(function (id) { var el = document.getElementById(id); if (el) spy.observe(el); });

  // 화면 아래에 있는 카드만 스크롤하며 나타난다. 다 나타나면 클래스를 지워 hover 움직임을 돌려준다.
  if (reduce) return;
  var sel = '.pt, .step, .sc-card, .price, .faq details, .stats .stat-n, .chip, .sec, .key, .info, .pts li, .lk';
  var items = document.querySelectorAll(sel), vh = window.innerHeight;
  var rv = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (!en.isIntersecting) return;
      var el = en.target;
      el.classList.add('in');
      rv.unobserve(el);
      setTimeout(function () { el.classList.remove('rv', 'in'); el.style.transitionDelay = ''; }, 900);
    });
  }, { rootMargin: '0px 0px -8% 0px' });
  for (i = 0; i < items.length; i++) {
    var el = items[i];
    if (el.getBoundingClientRect().top < vh) continue;
    var idx = Array.prototype.indexOf.call(el.parentNode.children, el);
    el.style.transitionDelay = Math.min(idx, 5) * 60 + 'ms';
    el.classList.add('rv');
    rv.observe(el);
  }
})();
