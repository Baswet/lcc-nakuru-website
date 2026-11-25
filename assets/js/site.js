/* LCC Nakuru — progressive enhancement. The site works without JS. */
(function () {
  'use strict';
  var d = document;
  var esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); };

  /* Mobile menu: disclosure with focus containment and Esc to close */
  var btn = d.querySelector('.menu-toggle'), nav = d.getElementById('site-nav');
  if (btn && nav) {
    var close = function (focusBtn) { nav.classList.remove('open'); nav.style.paddingTop = ''; btn.setAttribute('aria-expanded', 'false'); btn.textContent = 'Menu'; d.body.classList.remove('menu-open'); if (focusBtn) btn.focus(); };
    btn.addEventListener('click', function () {
      var open = btn.getAttribute('aria-expanded') !== 'true';
      if (!open) return close(false);
      nav.style.paddingTop = Math.round(d.querySelector('.site-header').getBoundingClientRect().bottom + 16) + 'px';
      nav.classList.add('open'); btn.setAttribute('aria-expanded', 'true'); btn.textContent = 'Close'; d.body.classList.add('menu-open');
      var first = nav.querySelector('a'); if (first) first.focus();
    });
    d.addEventListener('keydown', function (ev) {
      if (!nav.classList.contains('open')) return;
      if (ev.key === 'Escape') return close(true);
      if (ev.key === 'Tab') {
        var f = [btn].concat([].slice.call(nav.querySelectorAll('a')));
        var i = f.indexOf(d.activeElement);
        if (ev.shiftKey && i <= 0) { ev.preventDefault(); f[f.length - 1].focus(); }
        else if (!ev.shiftKey && i === f.length - 1) { ev.preventDefault(); f[0].focus(); }
      }
    });
    nav.addEventListener('click', function (ev) { if (ev.target.closest('a')) close(false); });
    window.addEventListener('resize', function () { if (window.innerWidth >= 1200) close(false); });
  }

  /* Lite YouTube: load the privacy-enhanced iframe only on click */
  d.addEventListener('click', function (ev) {
    var b = ev.target.closest('button.play[data-yt]');
    if (!b) return;
    var id = b.getAttribute('data-yt');
    if (!/^[A-Za-z0-9_-]{11}$/.test(id)) return;
    var f = d.createElement('iframe');
    f.src = 'https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0';
    f.title = b.getAttribute('aria-label').replace('Play video: ', '');
    f.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
    f.allowFullscreen = true;
    f.referrerPolicy = 'strict-origin-when-cross-origin';
    b.parentNode.appendChild(f);
    b.remove();
    f.focus();
  });

  /* Sermon library filter + search */
  var lib = d.getElementById('library');
  function bindFilters() {
    if (!lib) return;
    var chips = d.querySelectorAll('.chip[data-filter]'), q = d.getElementById('q'), sp = d.getElementById('speaker'), cat = 'all';
    var apply = function () {
      var term = (q && q.value || '').trim().toLowerCase(), n = 0;
      [].forEach.call(lib.querySelectorAll('.video'), function (v) {
        var ok = (cat === 'all' || v.getAttribute('data-cat') === cat) && (!term || v.getAttribute('data-title').indexOf(term) > -1) && (!sp || !sp.value || v.getAttribute('data-speaker') === sp.value);
        v.hidden = !ok; if (ok) n++;
      });
      var em = d.getElementById('empty'); if (em) em.hidden = n > 0;
      var c = d.getElementById('count'); if (c) c.textContent = n + ' videos shown';
    };
    [].forEach.call(chips, function (c) {
      c.addEventListener('click', function () {
        cat = c.getAttribute('data-filter');
        [].forEach.call(chips, function (x) { x.setAttribute('aria-pressed', String(x === c)); });
        apply();
      });
    });
    if (q) q.addEventListener('input', apply);
    if (sp) sp.addEventListener('change', apply);
  }
  bindFilters();

  /* Reveal on scroll */
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (en) { en.forEach(function (x) { if (x.isIntersecting) { x.target.classList.add('in'); io.unobserve(x.target); } }); }, { rootMargin: '0px 0px -8% 0px' });
    [].forEach.call(d.querySelectorAll('.sec .card, .intent, .ecard, .value, .timeline li'), function (el) { el.classList.add('reveal'); io.observe(el); });
  }

  /* Forms: POST to api/submit.php when the site runs on PHP hosting.
     On static hosting (GitHub Pages) nothing is sent anywhere; we show the phone/email instead. */
  [].forEach.call(d.querySelectorAll('form[data-form]'), function (form) {
    var status = form.querySelector('.form-status');
    var show = function (cls, msg) { status.className = 'form-status show ' + cls; status.innerHTML = msg; };
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var bad = [];
      [].forEach.call(form.querySelectorAll('[required]'), function (el) {
        var ok = el.type === 'checkbox' ? el.checked : el.value.trim() !== '';
        el.setAttribute('aria-invalid', String(!ok)); if (!ok) bad.push(el);
      });
      if (bad.length) { show('err', 'Please complete the highlighted fields.'); bad[0].focus(); return; }
      var fallback = 'Online forms are not active on this preview site yet, so <b>nothing was sent</b>. Please call <a href="tel:+254722864864">0722 864 864</a> or email <a href="mailto:lccnakuru@yahoo.com">lccnakuru@yahoo.com</a>.';
      if (/github\.io$/.test(location.hostname) || location.protocol === 'file:') { show('info', fallback); return; }
      var submit = form.querySelector('[type=submit]'); submit.disabled = true;
      fetch('api/csrf.php', { credentials: 'same-origin' })
        .then(function (r) { if (!r.ok) throw 0; return r.json(); })
        .then(function (t) {
          var fd = new FormData(form); fd.append('csrf', t.token);
          return fetch(form.getAttribute('action'), { method: 'POST', body: fd, credentials: 'same-origin' });
        })
        .then(function (r) { return r.json().then(function (j) { if (!r.ok) throw j; return j; }); })
        .then(function () { form.reset(); show('ok', form.dataset.form === 'prayer' ? 'Thank you. Your prayer request was sent privately to the pastoral team.' : 'Thank you. Your message was sent to the church office.'); })
        .catch(function (j) { show(j && j.error ? 'err' : 'info', j && j.error ? esc(j.error) : fallback); })
        .then(function () { submit.disabled = false; });
    });
  });

  /* CMS hydration: when admin edits data/content.json on PHP hosting, dynamic regions refresh without a rebuild. */
  if (location.protocol !== 'file:' && d.querySelector('[data-cms]')) {
    fetch('data/content.json', { cache: 'no-cache' }).then(function (r) { return r.ok ? r.json() : null; }).then(function (c) {
      if (!c) return;
      var n = d.querySelector('[data-cms=notice]');
      if (n) { if (c.notice && c.notice.show) n.innerHTML = '<a href="' + esc(c.notice.link) + '">' + esc(c.notice.text) + ' →</a>'; else n.remove(); }
      var g = d.querySelector('[data-cms=giving]');
      if (g && c.giving && c.giving.verified && c.giving.mpesa_paybill) {
        g.outerHTML = '<div class="give-card" data-cms="giving"><span class="eyebrow">M-Pesa</span><h3>Paybill ' + esc(c.giving.mpesa_paybill) + '</h3><p>Account: <b>' + esc(c.giving.mpesa_account) + '</b></p><p class="muted">Confirmed by the LCC church office.</p></div>';
      }
      if (lib && c.videos && lib.querySelectorAll('.video').length !== c.videos.length) { /* admin added or removed videos */
        var lab = { sermon: 'Message', service: 'Sunday service', praise: 'Praise Express', special: 'Special service', worship: 'Worship', conference: 'Conference', story: 'Story' };
        lib.innerHTML = c.videos.map(function (v) {
          var meta = [v.speaker, lab[v.category]].filter(Boolean).join(' · ');
          return '<figure class="video" data-cat="' + esc(v.category) + '" data-speaker="' + esc(v.speaker || '') + '" data-title="' + esc((v.title + ' ' + (v.speaker || '')).toLowerCase()) + '"><div class="frame"><img src="https://i.ytimg.com/vi/' + esc(v.id) + '/hqdefault.jpg" alt="" width="480" height="360" loading="lazy"><button class="play" type="button" data-yt="' + esc(v.id) + '" aria-label="Play video: ' + esc(v.title) + '"></button></div><figcaption><b>' + esc(v.title) + '</b><small>' + esc(meta) + '</small></figcaption></figure>';
        }).join('');
      }
    }).catch(function () {});
  }

  /* ---------------- v2 interactions ---------------- */
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* YouTube still fallback: maxresdefault is missing for some streams */
  d.addEventListener('error', function (ev) {
    var t = ev.target;
    if (t && t.tagName === 'IMG' && t.dataset.fallback && t.src !== t.dataset.fallback) { t.src = t.dataset.fallback; }
  }, true);
  /* YouTube returns a 120x90 grey placeholder (not an error) when maxres is missing */
  [].forEach.call(d.querySelectorAll('img[data-fallback]'), function (im) {
    var chk = function () { if (im.naturalWidth && im.naturalWidth <= 120 && im.src !== im.dataset.fallback) im.src = im.dataset.fallback; };
    if (im.complete) chk(); else im.addEventListener('load', chk);
  });

  /* Slideshow: crossfade, dots, prev/next, pause; no autoplay with reduced motion */
  var sl = d.querySelector('[data-slides]');
  if (sl) {
    var slides = sl.querySelectorAll('.slide'), dots = sl.querySelectorAll('[data-slide-to]'), cap = sl.querySelector('[data-slide-cap]');
    var pauseBtn = sl.querySelector('[data-slide-pause]'), i = 0, timer = null, paused = reduce;
    var show = function (n) {
      i = (n + slides.length) % slides.length;
      [].forEach.call(slides, function (s, k) { s.classList.toggle('on', k === i); s.setAttribute('aria-hidden', String(k !== i)); });
      [].forEach.call(dots, function (b, k) { if (k === i) b.setAttribute('aria-current', 'true'); else b.removeAttribute('aria-current'); });
      if (cap) cap.innerHTML = slides[i].getAttribute('data-cap') || '';
    };
    var tick = function () { clearInterval(timer); if (!paused) timer = setInterval(function () { show(i + 1); }, 7000); };
    sl.querySelector('[data-slide-prev]').addEventListener('click', function () { show(i - 1); tick(); });
    sl.querySelector('[data-slide-next]').addEventListener('click', function () { show(i + 1); tick(); });
    [].forEach.call(dots, function (b) { b.addEventListener('click', function () { show(+b.getAttribute('data-slide-to')); tick(); }); });
    var setPause = function (p) { paused = p; pauseBtn.setAttribute('aria-pressed', String(p)); pauseBtn.textContent = p ? 'Play' : 'Pause'; tick(); };
    pauseBtn.addEventListener('click', function () { setPause(!paused); });
    setPause(paused);
    sl.addEventListener('focusin', function () { clearInterval(timer); });
    sl.addEventListener('focusout', tick);
  }

  /* Horizontal rails */
  d.addEventListener('click', function (ev) {
    var b = ev.target.closest('[data-rail]');
    if (!b) return;
    var r = d.getElementById(b.getAttribute('data-rail'));
    if (r) r.scrollBy({ left: (+b.getAttribute('data-dir')) * r.clientWidth * 0.9, behavior: reduce ? 'auto' : 'smooth' });
  });
  [].forEach.call(d.querySelectorAll('.rail'), function (r) {
    var upd = function () {
      var bs = d.querySelectorAll('[data-rail="' + r.id + '"]');
      if (bs.length === 2) { bs[0].disabled = r.scrollLeft < 4; bs[1].disabled = r.scrollLeft + r.clientWidth >= r.scrollWidth - 4; }
    };
    r.addEventListener('scroll', upd, { passive: true }); upd();
  });

  /* Lightbox (gallery and collage): plays the source video */
  var lb = d.getElementById('lightbox');
  if (lb && typeof lb.showModal === 'function') {
    var frame = d.getElementById('lb-frame'), ttl = d.getElementById('lb-title'), list = [], cur = 0, opener = null;
    var load = function (k) {
      cur = (k + list.length) % list.length;
      var b = list[cur], id = b.getAttribute('data-lightbox');
      frame.innerHTML = '';
      var f = d.createElement('iframe');
      f.src = 'https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0';
      f.title = b.getAttribute('data-title'); f.allow = 'autoplay; encrypted-media; picture-in-picture'; f.allowFullscreen = true;
      frame.appendChild(f);
      ttl.innerHTML = esc(b.getAttribute('data-title')) + ' · <a href="https://www.youtube.com/watch?v=' + id + '" target="_blank" rel="noopener">YouTube ↗</a>';
    };
    d.addEventListener('click', function (ev) {
      var b = ev.target.closest('[data-lightbox]');
      if (!b) return;
      opener = b;
      list = [].filter.call(d.querySelectorAll('[data-lightbox][data-group="' + b.getAttribute('data-group') + '"]'), function (x) { return !x.closest('[hidden]'); });
      lb.showModal(); load(list.indexOf(b));
    });
    lb.addEventListener('click', function (ev) {
      var a = ev.target.closest('[data-lb]');
      if (ev.target === lb || (a && a.getAttribute('data-lb') === 'close')) lb.close();
      else if (a) load(cur + (a.getAttribute('data-lb') === 'next' ? 1 : -1));
    });
    lb.addEventListener('keydown', function (ev) { if (ev.key === 'ArrowRight') load(cur + 1); if (ev.key === 'ArrowLeft') load(cur - 1); });
    lb.addEventListener('close', function () { frame.innerHTML = ''; if (opener) opener.focus(); });
  }

  /* Generic chip filters for gallery and past events */
  [['gfilter', '.collage figure'], ['efilter', '#past .ecard']].forEach(function (cfg) {
    var chips = d.querySelectorAll('[data-' + cfg[0] + ']');
    [].forEach.call(chips, function (c) {
      c.addEventListener('click', function () {
        var v = c.getAttribute('data-' + cfg[0]);
        [].forEach.call(chips, function (x) { x.setAttribute('aria-pressed', String(x === c)); });
        [].forEach.call(d.querySelectorAll(cfg[1]), function (it) { it.hidden = !(v === 'all' || it.getAttribute('data-cat') === v); });
      });
    });
  });

  /* Countdown to official conference start */
  [].forEach.call(d.querySelectorAll('[data-countdown]'), function (el) {
    var end = new Date(el.getAttribute('data-countdown')).getTime();
    var draw = function () {
      var s = Math.max(0, Math.floor((end - Date.now()) / 1000));
      if (!s) { el.innerHTML = '<div><b>Now</b><small>happening</small></div>'; return; }
      var u = [[Math.floor(s / 86400), 'days'], [Math.floor(s % 86400 / 3600), 'hours'], [Math.floor(s % 3600 / 60), 'mins']];
      el.innerHTML = u.map(function (x) { return '<div><b>' + x[0] + '</b><small>' + x[1] + '</small></div>'; }).join('');
    };
    draw(); setInterval(draw, 30000);
  });

  /* Share: native share sheet, else copy link */
  d.addEventListener('click', function (ev) {
    var b = ev.target.closest('[data-share]');
    if (!b) return;
    var data = { title: d.title, url: location.href.split('#')[0] };
    if (navigator.share) { navigator.share(data).catch(function () {}); return; }
    var done = function () { var t = b.innerHTML; b.textContent = 'Link copied'; setTimeout(function () { b.innerHTML = t; }, 1800); };
    if (navigator.clipboard) navigator.clipboard.writeText(data.url).then(done, function () { prompt('Copy this link', data.url); });
    else prompt('Copy this link', data.url);
  });

  /* Click-to-load map (privacy) */
  d.addEventListener('click', function (ev) {
    var b = ev.target.closest('[data-map-load]');
    if (!b) return;
    var box = b.closest('[data-map]'), f = d.createElement('iframe');
    f.src = box.getAttribute('data-map'); f.title = 'Map: Deliverance Church LCC, Kariba Street, Nakuru'; f.loading = 'lazy';
    f.referrerPolicy = 'no-referrer-when-downgrade';
    box.innerHTML = ''; box.appendChild(f);
  });

  /* About sub-navigation: highlight the section in view */
  var sub = d.querySelectorAll('.subnav a');
  if (sub.length && 'IntersectionObserver' in window) {
    var map = {};
    [].forEach.call(sub, function (a) { map[a.getAttribute('href').slice(1)] = a; });
    var so = new IntersectionObserver(function (en) {
      en.forEach(function (x) {
        if (x.isIntersecting && map[x.target.id]) {
          [].forEach.call(sub, function (a) { a.classList.remove('active'); a.removeAttribute('aria-current'); });
          map[x.target.id].classList.add('active'); map[x.target.id].setAttribute('aria-current', 'true');
          map[x.target.id].scrollIntoView({ block: 'nearest', inline: 'center' });
        }
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    Object.keys(map).forEach(function (id) { var s = d.getElementById(id); if (s) so.observe(s); });
  }
})();
