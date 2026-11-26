/* LCC Nakuru — photography & motion layer. Progressive enhancement only:
   every element is visible without this file, and with prefers-reduced-motion. No dependencies. */
(function () {
  'use strict';
  var d = document, root = d.documentElement;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var desktop = window.matchMedia('(min-width: 861px)');
  var fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  if (reduce) root.classList.add('no-motion');
  var $$ = function (s, c) { return [].slice.call((c || d).querySelectorAll(s)); };


  /* ---------- Image fallbacks: maxres -> hq still -> brand background (never a broken icon) ---------- */
  var toFallback = function (im) {
    if (im.dataset.fallback && im.getAttribute('src') !== im.dataset.fallback) { im.removeAttribute('srcset'); im.src = im.dataset.fallback; return true; }
    return false;
  };
  d.addEventListener('error', function (ev) {
    var t = ev.target; if (!t || t.tagName !== 'IMG') return;
    if (!toFallback(t)) t.classList.add('img-failed');
  }, true);
  $$('img[data-fallback]').forEach(function (im) {
    var chk = function () { if (im.complete && im.naturalWidth === 0) { if (!toFallback(im)) im.classList.add('img-failed'); } else if (im.naturalWidth && im.naturalWidth <= 120) toFallback(im); };
    chk(); im.addEventListener('load', chk);
  });

  /* ---------- Split text: words / chars / lines ---------- */
  function splitText(el) {
    var mode = el.getAttribute('data-split');
    if (el.dataset.done) return; el.dataset.done = 1;
    el.classList.add('tsplit');
    var label = el.textContent.replace(/\s+/g, ' ').trim();
    el.setAttribute('aria-label', label);
    var i = 0;
    var walk = function (node) {
      [].slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          var frag = d.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(function (tok) {
            if (!tok) return;
            if (/^\s+$/.test(tok)) { frag.appendChild(d.createTextNode(' ')); return; }
            var w = d.createElement('span'); w.className = 'w'; w.setAttribute('aria-hidden', 'true');
            if (mode === 'chars') {
              tok.split('').forEach(function (ch) { var c = d.createElement('span'); c.className = 'c'; c.style.setProperty('--i', i++); c.textContent = ch; w.appendChild(c); });
            } else { w.style.setProperty('--i', i++); w.textContent = tok; }
            frag.appendChild(w);
          });
          node.replaceChild(frag, n);
        } else if (n.nodeType === 1 && n.tagName !== 'BR') { n.setAttribute('aria-hidden', 'true'); walk(n); }
      });
    };
    if (mode === 'lines') {
      // Lines are authored with <br> or data-lines="a|b|c" for reliable results across widths
      var parts = el.getAttribute('data-lines') ? el.getAttribute('data-lines').split('|') : el.innerHTML.split(/<br\s*\/?>/i);
      el.innerHTML = parts.map(function (p, k) { return '<span class="lm" aria-hidden="true"><span class="ln" style="--i:' + k + '">' + p.trim() + '</span></span>'; }).join('');
      return;
    }
    walk(el);
  }

  /* Scroll-ink: wrap words; colour follows reading progress */
  function inkify(el) {
    if (el.dataset.done) return; el.dataset.done = 1;
    var walk = function (node) {
      [].slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          var frag = d.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(function (tok) {
            if (!tok) return;
            if (/^\s+$/.test(tok)) { frag.appendChild(d.createTextNode(tok)); return; }
            var w = d.createElement('span'); w.className = 'w'; w.textContent = tok; frag.appendChild(w);
          });
          node.replaceChild(frag, n);
        } else if (n.nodeType === 1) walk(n);
      });
    };
    walk(el);
  }

  $$('[data-split]').forEach(function (el) { if (!reduce) splitText(el); });
  var inks = $$('.ink'); if (!reduce) inks.forEach(inkify);

  /* ---------- Reveal on view ---------- */
  var targets = $$('[data-reveal],[data-split],[data-stagger],.hl,.uline');
  $$('[data-stagger]').forEach(function (g) { [].forEach.call(g.children, function (c, i) { c.style.setProperty('--i', i); }); });
  if (reduce || !('IntersectionObserver' in window)) {
    targets.forEach(function (t) { t.classList.add('on'); });
  } else {
    var io = new IntersectionObserver(function (en) {
      en.forEach(function (x) { if (x.isIntersecting) { x.target.classList.add('on'); io.unobserve(x.target); } });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.08 });
    targets.forEach(function (t) { io.observe(t); });
    // Safety net: anything still hidden after 4s (e.g. printed, or observer quirks) becomes visible
    setTimeout(function () { targets.forEach(function (t) { var r = t.getBoundingClientRect(); if (r.top < innerHeight) t.classList.add('on'); }); }, 4000);
  }

  /* ---------- One rAF scroll loop for ink, parallax, pin, expand, scenes ---------- */
  var plx = $$('[data-parallax]'), pins = $$('.pinstory'), expands = $$('.expand'), scenes = $$('[data-scene]');
  var ticking = false;
  function frame() {
    ticking = false;
    var vh = innerHeight;
    if (!reduce) {
      inks.forEach(function (el) {
        var r = el.getBoundingClientRect(); if (r.bottom < 0 || r.top > vh) return;
        var p = Math.min(1, Math.max(0, (vh * 0.85 - r.top) / (r.height + vh * 0.35)));
        var ws = el.querySelectorAll('.w'), n = Math.round(p * ws.length);
        for (var i = 0; i < ws.length; i++) ws[i].classList.toggle('lit', i < n);
      });
      if (desktop.matches) plx.forEach(function (el) {
        var r = el.getBoundingClientRect(); if (r.bottom < -200 || r.top > vh + 200) return;
        var k = parseFloat(el.getAttribute('data-parallax')) || 0.1;
        el.style.setProperty('--p', ((r.top + r.height / 2 - vh / 2) * -k).toFixed(1));
      });
      if (desktop.matches) expands.forEach(function (el) {
        var r = el.getBoundingClientRect(); var span = r.height - vh;
        var x = Math.min(1, Math.max(0, -r.top / (span * 0.75)));
        el.style.setProperty('--x', x.toFixed(3));
      });
    }
    pins.forEach(function (el) {
      if (!desktop.matches) return;
      var steps = el.querySelectorAll('.step'), pics = el.querySelectorAll('.visual .pic'), on = 0;
      steps.forEach(function (s, i) { var r = s.getBoundingClientRect(); if (r.top < vh * 0.55) on = i; });
      steps.forEach(function (s, i) { s.classList.toggle('is-on', i === on); });
      pics.forEach(function (p, i) { p.classList.toggle('is-on', i === Math.min(on, pics.length - 1)); });
    });
    if (scenes.length) {
      var cls = '';
      scenes.forEach(function (s) { var r = s.getBoundingClientRect(); if (r.top < vh * 0.5 && r.bottom > vh * 0.5) cls = s.getAttribute('data-scene'); });
      d.body.classList.toggle('scene-night', cls === 'night');
      d.body.classList.toggle('scene-sand', cls === 'sand');
    }
  }
  var onScroll = function () { if (!ticking) { ticking = true; requestAnimationFrame(frame); } };
  if (inks.length || plx.length || pins.length || expands.length || scenes.length) {
    addEventListener('scroll', onScroll, { passive: true }); addEventListener('resize', onScroll); frame();
  }

  /* ---------- Pointer tilt (fine pointers only) ---------- */
  if (fine && !reduce) $$('.tilt').forEach(function (el) {
    el.addEventListener('pointermove', function (e) { var r = el.getBoundingClientRect(); el.style.setProperty('--rx', (((e.clientX - r.left) / r.width - .5) * 6).toFixed(2)); el.style.setProperty('--ry', (((e.clientY - r.top) / r.height - .5) * -6).toFixed(2)); });
    el.addEventListener('pointerleave', function () { el.style.setProperty('--rx', 0); el.style.setProperty('--ry', 0); });
  });

  /* ---------- Slideshow ---------- */
  var ICON = {
    prev: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7" fill="none" stroke="currentColor" stroke-width="2"/></svg>',
    next: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5l7 7-7 7" fill="none" stroke="currentColor" stroke-width="2"/></svg>',
    pause: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14M16 5v14" stroke="currentColor" stroke-width="2.5"/></svg>',
    play: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 4l13 8-13 8z" fill="currentColor"/></svg>',
    full: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5" fill="none" stroke="currentColor" stroke-width="2"/></svg>'
  };
  $$('.xshow').forEach(function (show) {
    var slides = $$('.slide', show), n = slides.length; if (n < 2) return;
    var stage = show.querySelector('.stage'), cur = 0, timer = null;
    var interval = parseInt(show.getAttribute('data-interval'), 10) || 6000;
    show.style.setProperty('--interval', interval + 'ms');
    var auto = show.hasAttribute('data-autoplay') && !reduce;
    show.setAttribute('role', 'region'); show.setAttribute('aria-roledescription', 'carousel');
    stage.setAttribute('aria-live', auto ? 'off' : 'polite');
    slides.forEach(function (s, i) { s.setAttribute('role', 'group'); s.setAttribute('aria-roledescription', 'slide'); s.setAttribute('aria-label', (i + 1) + ' of ' + n); });
    var bar = d.createElement('div'); bar.className = 'bar';
    var name = show.getAttribute('aria-label') || 'photographs';
    bar.innerHTML = '<button class="ctl prev" type="button" aria-label="Previous photo">' + ICON.prev + '</button>' +
      '<button class="ctl next" type="button" aria-label="Next photo">' + ICON.next + '</button>' +
      '<div class="xdots" role="group" aria-label="Choose photo">' + slides.map(function (s, i) { return '<button class="xdot" type="button" aria-label="Show photo ' + (i + 1) + '"></button>'; }).join('') + '</div>' +
      '<span class="count" aria-hidden="true"></span>' +
      (show.hasAttribute('data-autoplay') ? '<button class="ctl toggle" type="button"></button>' : '') +
      (d.fullscreenEnabled ? '<button class="ctl full" type="button" aria-label="View ' + name + ' full screen">' + ICON.full + '</button>' : '');
    show.appendChild(bar);
    var dots = $$('.xdot', bar), count = bar.querySelector('.count'), tog = bar.querySelector('.toggle');
    var thumbs = show.querySelector('.thumbs');
    if (thumbs) $$('button', thumbs).forEach(function (b, i) { b.addEventListener('click', function () { go(i, true); }); });
    function go(i, user) {
      var prev = cur; cur = (i + n) % n; if (prev === cur) return paint();
      slides.forEach(function (s) { s.classList.remove('was-on'); });
      slides[prev].classList.add('was-on'); slides[prev].classList.remove('is-on');
      slides[cur].classList.add('is-on');
      // lazy-load next image
      var nx = slides[(cur + 1) % n].querySelector('img[loading=lazy]'); if (nx) nx.loading = 'eager';
      paint(); if (user) restart();
    }
    function paint() {
      dots.forEach(function (b, i) { b.setAttribute('aria-current', String(i === cur)); });
      if (thumbs) $$('button', thumbs).forEach(function (b, i) { b.setAttribute('aria-current', String(i === cur)); });
      count.textContent = String(cur + 1).padStart(2, '0') + ' / ' + String(n).padStart(2, '0');
      if (tog) { tog.innerHTML = auto ? ICON.pause : ICON.play; tog.setAttribute('aria-label', auto ? 'Pause slideshow' : 'Play slideshow'); }
      show.classList.toggle('playing', !!auto);
    }
    function restart() { clearInterval(timer); if (auto) timer = setInterval(function () { go(cur + 1); }, interval); }
    slides[0].classList.add('is-on');
    bar.querySelector('.prev').addEventListener('click', function () { go(cur - 1, true); });
    bar.querySelector('.next').addEventListener('click', function () { go(cur + 1, true); });
    dots.forEach(function (b, i) { b.addEventListener('click', function () { go(i, true); }); });
    if (tog) tog.addEventListener('click', function () { auto = !auto; stage.setAttribute('aria-live', auto ? 'off' : 'polite'); paint(); restart(); });
    var full = bar.querySelector('.full');
    if (full) full.addEventListener('click', function () { if (d.fullscreenElement) d.exitFullscreen(); else show.requestFullscreen && show.requestFullscreen(); });
    show.addEventListener('keydown', function (e) { if (e.key === 'ArrowLeft') go(cur - 1, true); if (e.key === 'ArrowRight') go(cur + 1, true); });
    // pause on hover/focus (WCAG 2.2.2)
    show.addEventListener('mouseenter', function () { clearInterval(timer); });
    show.addEventListener('mouseleave', restart);
    show.addEventListener('focusin', function () { clearInterval(timer); });
    // swipe
    var x0 = null;
    stage.addEventListener('pointerdown', function (e) { x0 = e.clientX; });
    stage.addEventListener('pointerup', function (e) { if (x0 === null) return; var dx = e.clientX - x0; if (Math.abs(dx) > 40) go(cur + (dx < 0 ? 1 : -1), true); x0 = null; });
    stage.style.touchAction = 'pan-y';
    // only run while visible
    if ('IntersectionObserver' in window) new IntersectionObserver(function (en) { en.forEach(function (x) { if (x.isIntersecting) restart(); else clearInterval(timer); }); }).observe(show);
    else restart();
    paint();
  });

  /* ---------- Film strip: drag to scroll + buttons ---------- */
  $$('.strip').forEach(function (s) {
    var rail = s.querySelector('.xrail'); if (!rail) return;
    var down = false, sx = 0, sl = 0, moved = false;
    rail.addEventListener('pointerdown', function (e) { if (e.pointerType !== 'mouse') return; down = true; moved = false; sx = e.clientX; sl = rail.scrollLeft; });
    addEventListener('pointermove', function (e) { if (!down) return; var dx = e.clientX - sx; if (Math.abs(dx) > 4) { moved = true; rail.classList.add('drag'); } rail.scrollLeft = sl - dx; });
    addEventListener('pointerup', function () { if (!down) return; down = false; rail.classList.remove('drag'); });
    rail.addEventListener('click', function (e) { if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; } }, true);
    $$('[data-strip]', s).forEach(function (b) { b.addEventListener('click', function () { rail.scrollBy({ left: (b.getAttribute('data-strip') === 'next' ? 1 : -1) * rail.clientWidth * 0.7, behavior: reduce ? 'auto' : 'smooth' }); }); });
  });

  /* ---------- Lightbox (shared by wall, strip, spread, frames) ---------- */
  var groups = {};
  $$('[data-lb]').forEach(function (el) { var g = el.getAttribute('data-lb'); (groups[g] = groups[g] || []).push(el); });
  if (Object.keys(groups).length && window.HTMLDialogElement) {
    var dlg = d.createElement('dialog'); dlg.className = 'lb'; dlg.setAttribute('aria-label', 'Photo viewer');
    dlg.innerHTML = '<div class="top"><span class="lb-count" aria-live="polite"></span><button class="lb-close" type="button" aria-label="Close photo viewer"><svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M5 5l14 14M19 5L5 19" stroke="currentColor" stroke-width="2"/></svg></button></div>' +
      '<div class="view"><button class="prev" type="button" aria-label="Previous photo">' + ICON.prev + '</button><img alt=""><button class="next" type="button" aria-label="Next photo">' + ICON.next + '</button></div><p class="cap"></p>';
    d.body.appendChild(dlg);
    var img = dlg.querySelector('img'), cap = dlg.querySelector('.cap'), cnt = dlg.querySelector('.lb-count');
    var list = [], at = 0, opener = null;
    var visible = function (arr) { return arr.filter(function (e) { return !e.hidden && e.offsetParent !== null; }); };
    var show = function (i) {
      at = (i + list.length) % list.length; var el = list[at];
      img.src = el.getAttribute('data-full') || el.querySelector('img').currentSrc;
      img.alt = el.querySelector('img').alt;
      cap.textContent = el.getAttribute('data-caption') || img.alt;
      cnt.textContent = (at + 1) + ' of ' + list.length;
      img.style.animation = 'none'; void img.offsetWidth; img.style.animation = '';
    };
    Object.keys(groups).forEach(function (g) {
      groups[g].forEach(function (el) {
        el.addEventListener('click', function (e) { e.preventDefault(); list = visible(groups[g]); opener = el; show(list.indexOf(el)); dlg.showModal(); dlg.querySelector('.lb-close').focus(); });
      });
    });
    dlg.querySelector('.prev').addEventListener('click', function () { show(at - 1); });
    dlg.querySelector('.next').addEventListener('click', function () { show(at + 1); });
    dlg.querySelector('.lb-close').addEventListener('click', function () { dlg.close(); });
    dlg.addEventListener('close', function () { if (opener) opener.focus(); });
    dlg.addEventListener('keydown', function (e) { if (e.key === 'ArrowLeft') show(at - 1); if (e.key === 'ArrowRight') show(at + 1); });
    var tx = null; dlg.addEventListener('touchstart', function (e) { tx = e.touches[0].clientX; }, { passive: true });
    dlg.addEventListener('touchend', function (e) { if (tx === null) return; var dx = e.changedTouches[0].clientX - tx; if (Math.abs(dx) > 50) show(at + (dx < 0 ? 1 : -1)); tx = null; });
    dlg.addEventListener('click', function (e) { if (e.target === dlg || e.target.classList.contains('view')) dlg.close(); });
  }

  /* ---------- Gallery filter (wall) ---------- */
  $$('[data-gallery-filter]').forEach(function (bar) {
    var wall = d.getElementById(bar.getAttribute('data-gallery-filter')); if (!wall) return;
    var chips = $$('.chip', bar), status = bar.querySelector('[role=status]');
    chips.forEach(function (c) { c.addEventListener('click', function () {
      var f = c.getAttribute('data-f'), n = 0;
      chips.forEach(function (x) { x.setAttribute('aria-pressed', String(x === c)); });
      $$('button', wall).forEach(function (b) { var ok = f === 'all' || b.getAttribute('data-cat-key') === f; b.hidden = !ok; if (ok) n++; });
      if (status) status.textContent = n + ' photographs';
    }); });
  });
})();
