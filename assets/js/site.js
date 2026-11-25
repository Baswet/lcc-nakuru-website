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
    window.addEventListener('resize', function () { if (window.innerWidth >= 1100) close(false); });
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
    var chips = d.querySelectorAll('.chip[data-filter]'), q = d.getElementById('q'), cat = 'all';
    var apply = function () {
      var term = (q && q.value || '').trim().toLowerCase(), n = 0;
      [].forEach.call(lib.querySelectorAll('.video'), function (v) {
        var ok = (cat === 'all' || v.getAttribute('data-cat') === cat) && (!term || v.getAttribute('data-title').indexOf(term) > -1);
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
  }
  bindFilters();

  /* Reveal on scroll */
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (en) { en.forEach(function (x) { if (x.isIntersecting) { x.target.classList.add('in'); io.unobserve(x.target); } }); }, { rootMargin: '0px 0px -8% 0px' });
    [].forEach.call(d.querySelectorAll('.sec .card, .intent, .video, .event'), function (el) { el.classList.add('reveal'); io.observe(el); });
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
      if (lib && c.videos && lib.querySelectorAll('.video').length !== c.videos.length) {
        var lab = { sermon: 'Message', worship: 'Worship', conference: 'Conference', story: 'Story' };
        lib.innerHTML = c.videos.map(function (v) {
          var meta = [v.speaker, lab[v.category]].filter(Boolean).join(' · ');
          return '<figure class="video" data-cat="' + esc(v.category) + '" data-title="' + esc((v.title + ' ' + (v.speaker || '')).toLowerCase()) + '"><div class="frame"><img src="https://i.ytimg.com/vi/' + esc(v.id) + '/hqdefault.jpg" alt="" width="480" height="360" loading="lazy"><button class="play" type="button" data-yt="' + esc(v.id) + '" aria-label="Play video: ' + esc(v.title) + '"></button></div><figcaption><b>' + esc(v.title) + '</b><small>' + esc(meta) + '</small></figcaption></figure>';
        }).join('');
      }
    }).catch(function () {});
  }
})();
