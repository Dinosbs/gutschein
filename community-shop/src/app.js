/* INCENT Community-Shop – Pitch Health & Beauty
 *
 * Personalisieren per URL, z. B.:
 *   index.html?name=Lena&farbe=rose&nav=ffffff&hintergrund=bild&provision=12&reichweite=250000
 *   farbe/nav: blau | rose | beere | nude | salbei | lavendel | schwarz | Hex-Wert (z. B. c0746a)
 *   hintergrund: bild | einfarbig | verlauf
 */
(() => {
  'use strict';

  const D = window.SHOP_DATA;
  const root = document.documentElement;
  root.classList.add('js');

  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const finePointer = matchMedia('(hover: hover) and (pointer: fine)').matches;

  const fmtEur = new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format;
  const fmtEur0 = new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format;
  const fmtInt = new Intl.NumberFormat('de-DE', { maximumFractionDigits: 0 }).format;
  const fmtPct = (v, d = 0) => v.toLocaleString('de-DE', { minimumFractionDigits: d, maximumFractionDigits: d }) + ' %';

  const params = new URLSearchParams(location.search);

  /* ------------------------------------------------------------ Zahlen weich hochzählen */
  function tween(el, to, fmt, dur = 700) {
    const from = el._v ?? to;
    el._v = to;
    cancelAnimationFrame(el._raf);
    if (reduce || from === to) { el.textContent = fmt(to); return; }
    const t0 = performance.now();
    const step = (now) => {
      const k = Math.min(1, (now - t0) / dur);
      el.textContent = fmt(from + (to - from) * (1 - Math.pow(1 - k, 3)));
      if (k < 1) el._raf = requestAnimationFrame(step);
    };
    el._raf = requestAnimationFrame(step);
  }
  const paintRange = (input) => input.style.setProperty('--p', ((input.value - input.min) / (input.max - input.min) * 100) + '%');

  /* ============================================================ Marken-Profil (Gestalter) */
  const parseColor = (v) => {
    if (!v) return null;
    v = v.trim().toLowerCase();
    if (D.presets[v]) return D.presets[v];
    if (/^#?[0-9a-f]{6}$/.test(v)) return v.startsWith('#') ? v : '#' + v;
    return null;
  };
  const BG = { bild: 'image', einfarbig: 'solid', verlauf: 'gradient', image: 'image', solid: 'solid', gradient: 'gradient' };
  const theme = {
    btn: parseColor(params.get('farbe')) || D.defaults.btn,
    nav: parseColor(params.get('nav')) || D.defaults.nav,
    bg: BG[(params.get('hintergrund') || '').toLowerCase()] || 'image',
    name: (params.get('name') || '').trim().slice(0, 20),
    logo: null,
    logoName: '',
  };

  const rgb = (hex) => { const n = parseInt(hex.slice(1), 16); return [n >> 16 & 255, n >> 8 & 255, n & 255]; };
  const lum = (hex) => {
    const f = (c) => { c /= 255; return c <= .03928 ? c / 12.92 : Math.pow((c + .055) / 1.055, 2.4); };
    const [r, g, b] = rgb(hex);
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b);
  };
  const mix = (a, b, t) => '#' + rgb(a).map((c, i) => Math.round(c + (rgb(b)[i] - c) * t).toString(16).padStart(2, '0')).join('');
  const slugify = (s) => s.toLowerCase()
    .replace(/ä/g, 'ae').replace(/ö/g, 'oe').replace(/ü/g, 'ue').replace(/ß/g, 'ss')
    .normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, '').slice(0, 24);

  function applyTheme() {
    root.style.setProperty('--btn', theme.btn);
    root.style.setProperty('--nav', theme.nav);
    root.style.setProperty('--bg-solid', mix(theme.btn, '#ffffff', .86));
    root.style.setProperty('--bg-g1', theme.btn);
    root.style.setProperty('--bg-g2', mix(theme.btn, '#071022', .72));
    root.dataset.btnTone = lum(theme.btn) > .45 ? 'light' : 'dark';
    root.dataset.navTone = lum(theme.nav) < .3 ? 'dark' : 'light';
    root.dataset.bg = theme.bg;
    root.dataset.logo = theme.logo ? 'custom' : (theme.name ? 'name' : 'incent');

    const mark = (attr, value) => $$(`[data-${attr}]`).forEach((s) => {
      const on = s.dataset[attr].toLowerCase() === value.toLowerCase();
      s.classList.toggle('is-on', on);
      s.setAttribute('aria-checked', on);
    });
    mark('btn', theme.btn);
    mark('nav', theme.nav);
    $$('[data-bg-opt]').forEach((b) => {
      const on = b.dataset.bgOpt === theme.bg;
      b.classList.toggle('is-on', on);
      b.setAttribute('aria-checked', on);
    });

    // Vorschau im Logo-Feld
    const prev = $('[data-logo-preview]');
    const label = $('[data-logo-name]');
    if (prev) {
      if (theme.logo) {
        prev.innerHTML = '<img alt="">';
        $('img', prev).src = theme.logo;
        label.textContent = theme.logoName || 'Eigenes Logo';
      } else if (theme.name) {
        prev.innerHTML = '<b></b>';
        $('b', prev).textContent = theme.name;
        label.textContent = `Schriftzug „${theme.name}“`;
      } else {
        prev.innerHTML = prev.dataset.incent;
        label.textContent = 'INCENT-Logo';
      }
    }
    $('[data-logo-reset]').hidden = !theme.logo;
  }

  function applyName() {
    const n = theme.name;
    const slug = slugify(n) || 'deinname';
    $$('[data-bind="name"]').forEach((el) => { el.textContent = n || 'Dein Name'; });
    $$('[data-bind="slug"]').forEach((el) => { el.textContent = slug; });
    $$('[data-bind="handle"]').forEach((el) => { el.textContent = slug; });
    $$('[data-bind="initial"]').forEach((el) => { el.textContent = (n || 'D').charAt(0).toUpperCase(); });
    $$('[data-bind="eyebrow"]').forEach((el) => { el.textContent = n ? `Exklusiv für ${n} · Health & Beauty` : 'Community-Shop · Health & Beauty'; });
    const poss = n ? (/[sxzß]$/i.test(n) ? n + '’' : n + 's') : '';
    document.title = n ? `${poss} Beauty-Shop · INCENT Community-Shop` : 'Dein eigener Beauty-Shop · INCENT Community-Shop';
  }

  function setLogo(url, name) {
    theme.logo = url;
    theme.logoName = name || '';
    $$('[data-logo-img]').forEach((img) => { if (url) img.src = url; });
    applyTheme();
  }

  function bindStudio() {
    const prev = $('[data-logo-preview]');
    if (prev) prev.dataset.incent = prev.innerHTML;
    const input = $('input[data-input="name"]');
    input.value = theme.name;
    input.addEventListener('input', () => { theme.name = input.value.trim(); applyName(); applyTheme(); });

    $$('[data-btn]').forEach((s) => s.addEventListener('click', () => { theme.btn = s.dataset.btn; applyTheme(); }));
    $$('[data-nav]').forEach((s) => s.addEventListener('click', () => { theme.nav = s.dataset.nav; applyTheme(); }));
    $$('[data-custom]').forEach((c) => c.addEventListener('input', () => { theme[c.dataset.custom] = c.value; applyTheme(); }));
    $$('[data-bg-opt]').forEach((b) => b.addEventListener('click', () => { theme.bg = b.dataset.bgOpt; applyTheme(); }));

    const read = (file) => {
      if (!file || !/^image\//.test(file.type)) return;
      const fr = new FileReader();
      fr.onload = () => setLogo(fr.result, file.name);
      fr.readAsDataURL(file);
    };
    $('[data-logo-input]').addEventListener('change', (e) => read(e.target.files[0]));
    $('[data-logo-reset]').addEventListener('click', () => { $('[data-logo-input]').value = ''; setLogo(null); });
    const drop = $('[data-logo-drop]');
    ['dragenter', 'dragover'].forEach((t) => drop.addEventListener(t, (e) => { e.preventDefault(); drop.classList.add('is-drag'); }));
    ['dragleave', 'drop'].forEach((t) => drop.addEventListener(t, (e) => { e.preventDefault(); drop.classList.remove('is-drag'); }));
    drop.addEventListener('drop', (e) => read(e.dataTransfer.files[0]));

    $('[data-reset-all]').addEventListener('click', () => {
      Object.assign(theme, { btn: D.defaults.btn, nav: D.defaults.nav, bg: 'image', name: '', logo: null, logoName: '' });
      input.value = '';
      $('[data-logo-input]').value = '';
      applyName();
      applyTheme();
    });
  }

  /* ============================================================ Beteiligung + Rechner */
  const state = {
    rate: clamp(Number(params.get('provision')) || D.defaults.rate, 5, 20),
    followers: clamp(Number(params.get('reichweite')) || D.defaults.followers, 5000, 1000000),
    conv: D.defaults.conv,
    basket: D.defaults.basket,
  };

  function renderRate() {
    $$('[data-out="rate"]').forEach((o) => { o.textContent = fmtPct(state.rate); });
    $$('input[data-input="rate"]').forEach((i) => { i.value = state.rate; paintRange(i); });
    $$('[data-earn]').forEach((el) => tween(el, Number(el.dataset.earn) * Number(el.dataset.earnX || 1) * state.rate / 100, fmtEur, 450));
  }

  const LOG_MIN = 5000, LOG_MAX = 1000000;
  const followersFromSlider = (v) => {
    const raw = LOG_MIN * Math.pow(LOG_MAX / LOG_MIN, v / 1000);
    const s = raw < 20000 ? 500 : raw < 100000 ? 1000 : raw < 500000 ? 5000 : 10000;
    return Math.round(raw / s) * s;
  };
  const sliderFromFollowers = (f) => Math.round(1000 * Math.log(f / LOG_MIN) / Math.log(LOG_MAX / LOG_MIN));

  function renderCalc() {
    const orders = state.followers * state.conv / 100;
    const revenue = orders * state.basket;
    const month = revenue * state.rate / 100;
    const out = { orders, revenue, month, year: month * 12, savings: revenue * D.avgDiscount / (1 - D.avgDiscount) };
    const fmt = { orders: fmtInt, revenue: fmtEur0, month: fmtEur0, year: fmtEur0, savings: fmtEur0 };
    $$('[data-res]').forEach((el) => tween(el, out[el.dataset.res], fmt[el.dataset.res]));
    $('[data-out="followers"]').textContent = fmtInt(state.followers);
    $('[data-out="conv"]').textContent = fmtPct(state.conv, 1);
    $('[data-out="basket"]').textContent = fmtEur0(state.basket);
    $$('[data-preset]').forEach((b) => b.classList.toggle('is-on', Number(b.dataset.preset) === state.followers));
  }

  function bindCalc() {
    const f = $('input[data-input="followers"]');
    const c = $('input[data-input="conv"]');
    const b = $('input[data-input="basket"]');
    f.value = sliderFromFollowers(state.followers);
    c.value = Math.round(state.conv * 10);
    b.value = state.basket;
    [f, c, b].forEach(paintRange);
    f.addEventListener('input', () => { state.followers = followersFromSlider(Number(f.value)); paintRange(f); renderCalc(); });
    c.addEventListener('input', () => { state.conv = Number(c.value) / 10; paintRange(c); renderCalc(); });
    b.addEventListener('input', () => { state.basket = Number(b.value); paintRange(b); renderCalc(); });
    $$('input[data-input="rate"]').forEach((i) => i.addEventListener('input', () => { state.rate = Number(i.value); renderRate(); renderCalc(); }));
    $$('[data-preset]').forEach((btn) => btn.addEventListener('click', () => {
      state.followers = Number(btn.dataset.preset);
      f.value = sliderFromFollowers(state.followers);
      paintRange(f);
      renderCalc();
    }));
  }

  /* ============================================================ Bestellungen im Hero */
  function bindToasts() {
    const box = $('[data-toasts]');
    const today = $('[data-today]');
    const pool = $$('.ecard [data-product]').map((c) => ({
      brand: c.dataset.brand,
      title: c.dataset.title.replace(/^(EdP|EdT|EDP)\s+/, '').replace(/[„“"]/g, ''),
      price: Number(c.dataset.price),
      img: c.dataset.img,
    }));
    if (!box || !pool.length) return;
    let total = 0, last = -1, timer = null, visible = false;
    tween(today, 0, fmtEur);

    const push = () => {
      let i;
      do { i = Math.floor(Math.random() * pool.length); } while (i === last && pool.length > 1);
      last = i;
      const p = pool[i];
      const amount = p.price * state.rate / 100;
      const t = document.createElement('div');
      t.className = 'toast';
      t.innerHTML = '<span class="pimg"></span><span class="toast__txt"><small>Neue Bestellung · gerade eben</small><span></span></span><b class="toast__amt"></b>';
      $('.pimg', t).classList.add(p.img);
      $('.toast__txt span', t).textContent = `${p.brand} · ${p.title}`;
      $('.toast__amt', t).textContent = '+' + fmtEur(amount);
      box.prepend(t);
      $$('.toast:not(.is-out)', box).slice(2).forEach((old) => { old.classList.add('is-out'); setTimeout(() => old.remove(), 450); });
      total += amount;
      tween(today, total, fmtEur, 900);
    };
    const start = () => { if (!timer) { setTimeout(push, 600); timer = setInterval(push, 3200); } };
    const stop = () => { clearInterval(timer); timer = null; };
    new IntersectionObserver(([e]) => { visible = e.isIntersecting; visible && !document.hidden ? start() : stop(); }, { threshold: .15 }).observe($('.hero__view'));
    document.addEventListener('visibilitychange', () => (visible && !document.hidden ? start() : stop()));
  }

  /* ============================================================ Portal: neigt sich zum Cursor, richtet sich beim Scrollen auf */
  function bindStage() {
    const stage = $('[data-stage]');
    const view = $('.hero__view');
    const spot = $('[data-spot]');
    const hero = $('.hero');
    if (!stage || reduce) { if (stage) stage.style.setProperty('--p', 1); return; }
    let raf = 0, mx = 0, my = 0;
    const update = () => {
      raf = 0;
      const r = view.getBoundingClientRect();
      stage.style.setProperty('--p', clamp((innerHeight - r.top) / (innerHeight * .8), 0, 1).toFixed(3));
      if (finePointer) {
        stage.style.setProperty('--rx', (-(my / innerHeight - .5) * 5).toFixed(2) + 'deg');
        stage.style.setProperty('--ry', ((mx / innerWidth - .5) * 7).toFixed(2) + 'deg');
        const hr = hero.getBoundingClientRect();
        spot.style.setProperty('--sx', (mx - hr.width / 2) * .25 + 'px');
        spot.style.setProperty('--sy', (my - hr.top - hr.height * .26) * .25 + 'px');
      }
    };
    const queue = () => { if (!raf) raf = requestAnimationFrame(update); };
    addEventListener('scroll', queue, { passive: true });
    addEventListener('resize', queue);
    if (finePointer) addEventListener('pointermove', (e) => { mx = e.clientX; my = e.clientY; queue(); }, { passive: true });
    mx = innerWidth / 2; my = innerHeight / 2;
    update();
  }

  /* ============================================================ Edits */
  function bindEdits() {
    const tabs = $$('[role="tab"]');
    const select = (tab, focus) => {
      tabs.forEach((t) => {
        const on = t === tab;
        t.setAttribute('aria-selected', on);
        t.tabIndex = on ? 0 : -1;
        $('#' + t.getAttribute('aria-controls')).hidden = !on;
      });
      if (focus) tab.focus();
      const rail = $('#' + tab.getAttribute('aria-controls') + ' .rail');
      if (rail) rail.scrollLeft = 0;
    };
    tabs.forEach((t, i) => {
      t.addEventListener('click', () => select(t));
      t.addEventListener('keydown', (e) => {
        const d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
        if (!d) return;
        e.preventDefault();
        select(tabs[(i + d + tabs.length) % tabs.length], true);
      });
    });
    $$('[data-rail]').forEach((btn) => btn.addEventListener('click', () => {
      const rail = $('.rail', btn.closest('.edit'));
      rail.scrollBy({ left: Number(btn.dataset.rail) * rail.clientWidth * .8, behavior: reduce ? 'auto' : 'smooth' });
    }));
  }

  /* ============================================================ Einblenden, Zähler, Ablauf */
  function bindReveal() {
    $$('.dash__chart i').forEach((el, i) => el.style.setProperty('--i', i));
    const countUp = (scope) => $$('[data-count]', scope).forEach((el) => {
      if (el._counted) return;
      el._counted = true;
      el._v = 0;
      tween(el, Number(el.dataset.count), fmtInt, 1400);
    });
    const io = new IntersectionObserver((entries) => entries.forEach((e) => {
      if (!e.isIntersecting) return;
      e.target.classList.add('is-in');
      countUp(e.target);
      io.unobserve(e.target);
    }), { threshold: .12, rootMargin: '0px 0px -6% 0px' });
    $$('[data-reveal], .dash').forEach((el) => io.observe(el));

    const steps = $('[data-steps]');
    new IntersectionObserver(([e], obs) => {
      if (!e.isIntersecting) return;
      obs.disconnect();
      steps.style.setProperty('--p', 1);
      $$('.step', steps).forEach((s, i) => setTimeout(() => s.classList.add('is-on'), reduce ? 0 : 250 + i * 420));
    }, { threshold: .4 }).observe(steps);
  }

  /* ============================================================ Navigation + Präsentationsmodus */
  function bindNav() {
    const slides = $$('.slide');
    const nav = $('[data-nav]');
    const links = $$('.nav__link');
    const progress = $('[data-progress]');
    const hint = $('.keyhint');
    const map = { idee: 'idee', design: 'design', verdienst: 'verdienst', rechner: 'verdienst', marken: 'marken', edits: 'marken', deals: 'marken', reichweite: 'reichweite', service: 'reichweite', ablauf: 'ablauf' };
    const io = new IntersectionObserver((entries) => entries.forEach((e) => {
      if (!e.isIntersecting) return;
      const id = e.target.id;
      $$('[data-dot]').forEach((d) => d.classList.toggle('is-active', d.dataset.dot === id));
      links.forEach((a) => a.classList.toggle('is-active', a.getAttribute('href') === '#' + map[id]));
    }), { rootMargin: '-45% 0px -50% 0px' });
    slides.forEach((s) => io.observe(s));

    const onScroll = () => {
      nav.classList.toggle('is-scrolled', scrollY > 10);
      const max = document.documentElement.scrollHeight - innerHeight;
      progress.style.setProperty('--sp', max > 0 ? (scrollY / max).toFixed(4) : 0);
    };
    addEventListener('scroll', onScroll, { passive: true });
    onScroll();

    const go = (dir) => {
      const y = scrollY, vh = innerHeight, slack = 80;
      const tops = slides.map((s) => s.getBoundingClientRect().top + y);
      let cur = 0;
      tops.forEach((t, i) => { if (t <= y + slack) cur = i; });
      const bottom = tops[cur] + slides[cur].offsetHeight;
      let target;
      if (dir > 0) target = bottom - (y + vh) > 60 ? Math.min(y + vh * .85, bottom - vh) : tops[cur + 1];
      else if (y - tops[cur] > vh * .9) target = y - vh * .85;
      else if (y - tops[cur] > slack) target = tops[cur];
      else target = tops[cur - 1];
      if (target === undefined) return;
      scrollTo({ top: Math.max(0, target), behavior: reduce ? 'auto' : 'smooth' });
    };
    addEventListener('keydown', (e) => {
      if (e.altKey || e.ctrlKey || e.metaKey) return;
      if (e.target.closest('input, textarea, select, [role="tab"], .rail')) return;
      const dir = { ArrowDown: 1, PageDown: 1, ArrowUp: -1, PageUp: -1 }[e.key];
      if (!dir) return;
      e.preventDefault();
      go(dir);
      hint?.classList.add('is-gone');
    });
    setTimeout(() => hint?.classList.add('is-gone'), 12000);
  }

  /* ============================================================ Kontakt */
  function bindContact() {
    if (!D.contact) return;
    $$('[data-contact]').forEach((a) => { a.href = `mailto:${D.contact}?subject=${encodeURIComponent('Community-Shop – Lass uns sprechen')}`; });
  }

  /* ============================================================ Start */
  bindStudio();
  applyName();
  applyTheme();
  bindCalc();
  renderRate();
  renderCalc();
  bindEdits();
  bindReveal();
  bindNav();
  bindStage();
  bindToasts();
  bindContact();
})();
