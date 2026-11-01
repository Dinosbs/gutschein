/* INCENT Community-Shop – Pitch Health & Beauty (scroll-gesteuerte Präsentation)
 *
 * Präsentieren: Scrollen, Pfeiltasten ↑ ↓, Bild↑/Bild↓, Leertaste oder Presenter – jede Folie rastet ein.
 * Personalisieren: Sublink je Influencerin (data/pitches.json → /pitch/<slug>/) oder per Adresse:
 *   index.html?name=Lena&farbe=rose&nav=weiss&hintergrund=bild
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
  const deckQuery = matchMedia('(min-width: 1000px) and (min-height: 560px) and (orientation: landscape)');
  const isDeck = () => deckQuery.matches;

  const fmtEur = new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format;
  const fmtEur0 = new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format;
  const fmtInt = new Intl.NumberFormat('de-DE', { maximumFractionDigits: 0 }).format;
  const fmtPct = (v, d = 0) => v.toLocaleString('de-DE', { minimumFractionDigits: d, maximumFractionDigits: d }) + ' %';
  const params = new URLSearchParams(location.search);
  const RATE = D.rate / 100;

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

  /* ============================================================ Marken-Profil (Name, Farben, Logo) */
  const parseColor = (v) => {
    if (!v) return null;
    v = String(v).trim().toLowerCase();
    if (D.presets[v]) return D.presets[v];
    if (/^#?[0-9a-f]{6}$/.test(v)) return v.startsWith('#') ? v : '#' + v;
    return null;
  };
  const BG = { bild: 'image', einfarbig: 'solid', verlauf: 'gradient', image: 'image', solid: 'solid', gradient: 'gradient' };
  const P = D.pitch || {};
  const initial = {
    btn: parseColor(params.get('farbe')) || parseColor(P.farbe) || D.defaults.btn,
    nav: parseColor(params.get('nav')) || parseColor(P.nav) || D.defaults.nav,
    bg: BG[(params.get('hintergrund') || '').toLowerCase()] || BG[(P.hintergrund || '').toLowerCase()] || 'image',
    name: (params.get('name') || P.name || '').trim().slice(0, 20),
    logo: P.logo || null,
    logoName: P.logo ? 'Dein Logo' : '',
  };
  const theme = { ...initial };

  const rgb = (hex) => { const n = parseInt(hex.slice(1), 16); return [n >> 16 & 255, n >> 8 & 255, n & 255]; };
  const lum = (hex) => {
    const f = (c) => { c /= 255; return c <= .03928 ? c / 12.92 : Math.pow((c + .055) / 1.055, 2.4); };
    const [r, g, b] = rgb(hex);
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b);
  };
  const mix = (a, b, t) => '#' + rgb(a).map((c, i) => Math.round(c + (rgb(b)[i] - c) * t).toString(16).padStart(2, '0')).join('');
  const slugify = (s) => s.toLowerCase().replace(/ä/g, 'ae').replace(/ö/g, 'oe').replace(/ü/g, 'ue').replace(/ß/g, 'ss')
    .normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, '').slice(0, 24);

  function applyTheme() {
    const s = root.style;
    s.setProperty('--btn', theme.btn);
    s.setProperty('--nav', theme.nav);
    s.setProperty('--bg-solid', mix(theme.btn, '#ffffff', .86));
    s.setProperty('--bg-g1', theme.btn);
    s.setProperty('--bg-g2', mix(theme.btn, '#071022', .72));
    root.dataset.btnTone = lum(theme.btn) > .45 ? 'light' : 'dark';
    root.dataset.navTone = lum(theme.nav) < .3 ? 'dark' : 'light';
    root.dataset.bg = theme.bg;
    root.dataset.logo = theme.logo ? 'custom' : (theme.name ? 'name' : 'incent');
    const mark = (attr, value) => $$(`[data-${attr}]`).forEach((el) => {
      const on = el.dataset[attr].toLowerCase() === value.toLowerCase();
      el.classList.toggle('is-on', on);
      el.setAttribute('aria-checked', on);
    });
    mark('btn', theme.btn);
    mark('nav', theme.nav);
    $$('[data-bg-opt]').forEach((b) => { const on = b.dataset.bgOpt === theme.bg; b.classList.toggle('is-on', on); b.setAttribute('aria-checked', on); });

    const prev = $('[data-logo-preview]');
    const label = $('[data-logo-name]');
    if (theme.logo) { prev.innerHTML = '<img alt="">'; $('img', prev).src = theme.logo; label.textContent = theme.logoName || 'Eigenes Logo'; }
    else if (theme.name) { prev.innerHTML = '<b></b>'; $('b', prev).textContent = theme.name; label.textContent = `Schriftzug „${theme.name}“`; }
    else { prev.innerHTML = prev.dataset.incent; label.textContent = 'INCENT-Logo'; }
    $('[data-logo-reset]').hidden = !theme.logo || theme.logo === initial.logo;
    $$('[data-logo-img]').forEach((img) => { if (theme.logo && img.src !== theme.logo) img.src = theme.logo; });
  }

  function applyName() {
    const n = theme.name;
    const slug = slugify(n) || 'deinname';
    const poss = n ? (/[sxzß]$/i.test(n) ? n + '’' : n + 's') : '';
    $$('[data-bind="name"]').forEach((el) => { el.textContent = n || 'Dein Name'; });
    $$('[data-bind="slug"]').forEach((el) => { el.textContent = slug; });
    $$('[data-bind="handle"]').forEach((el) => { el.textContent = slug; });
    $$('[data-bind="initial"]').forEach((el) => { el.textContent = (n || 'D').charAt(0).toUpperCase(); });
    $$('[data-bind="eyebrow"]').forEach((el) => { el.textContent = n ? `Exklusiv für ${n} · Health & Beauty` : 'Community-Shop · Health & Beauty'; });
    $$('[data-bind="thanks"]').forEach((el) => { el.textContent = n ? `${poss} Beauty-Shop.` : 'Dein Beauty-Shop.'; });
    $('[data-for-chip]').hidden = !n;
    document.title = n ? `${poss} Beauty-Shop · INCENT Community-Shop` : 'Dein eigener Beauty-Shop · INCENT Community-Shop';
  }

  function bindStudio() {
    const prev = $('[data-logo-preview]');
    prev.dataset.incent = prev.innerHTML;
    const input = $('input[data-input="name"]');
    input.value = theme.name;
    input.addEventListener('input', () => { theme.name = input.value.trim(); applyName(); applyTheme(); });
    $$('[data-btn]').forEach((s) => s.addEventListener('click', () => { theme.btn = s.dataset.btn; applyTheme(); }));
    $$('[data-nav]').forEach((s) => s.addEventListener('click', () => { theme.nav = s.dataset.nav; applyTheme(); }));
    $$('[data-custom]').forEach((c) => c.addEventListener('change', () => { theme[c.dataset.custom] = c.value; applyTheme(); }));
    $$('[data-bg-opt]').forEach((b) => b.addEventListener('click', () => { theme.bg = b.dataset.bgOpt; applyTheme(); }));
    const read = (file) => {
      if (!file || !/^image\//.test(file.type)) return;
      const fr = new FileReader();
      fr.onload = () => { theme.logo = fr.result; theme.logoName = file.name; applyTheme(); };
      fr.readAsDataURL(file);
    };
    const fileInput = $('[data-logo-input]');
    fileInput.addEventListener('change', () => read(fileInput.files[0]));
    $('[data-logo-reset]').addEventListener('click', () => { fileInput.value = ''; theme.logo = initial.logo; theme.logoName = initial.logoName; applyTheme(); });
    const drop = $('[data-logo-drop]');
    ['dragenter', 'dragover'].forEach((t) => drop.addEventListener(t, (e) => { e.preventDefault(); drop.classList.add('is-drag'); }));
    ['dragleave', 'drop'].forEach((t) => drop.addEventListener(t, (e) => { e.preventDefault(); drop.classList.remove('is-drag'); }));
    drop.addEventListener('drop', (e) => read(e.dataTransfer.files[0]));
    $('[data-reset-all]').addEventListener('click', () => {
      Object.assign(theme, initial);
      input.value = theme.name;
      fileInput.value = '';
      applyName();
      applyTheme();
    });
  }

  /* ============================================================ Rechner (Beteiligung fest) */
  const state = { followers: clamp(Number(params.get('reichweite')) || D.defaults.followers, 5000, 1000000), conv: D.defaults.conv, basket: D.defaults.basket };
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
    const month = revenue * RATE;
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
    $$('[data-preset]').forEach((btn) => btn.addEventListener('click', () => {
      state.followers = Number(btn.dataset.preset);
      f.value = sliderFromFollowers(state.followers);
      paintRange(f);
      renderCalc();
    }));
    renderCalc();
  }

  /* ============================================================ Panels folgen dem Cursor (wie incent.de) */
  const tilts = [];
  let pointer = null;
  function addTilt(el, opt = {}) {
    if (!finePointer || reduce || !el) return;
    const t = { el, rx: 5, ry: 8, tx: 14, ty: 8, reach: .42, center: null, visible: false, cur: { x: 0, y: 0 }, aim: { x: 0, y: 0 }, raf: 0, ...opt };
    tilts.push(t);
    new IntersectionObserver(([e]) => { t.visible = e.isIntersecting; if (t.visible) aim(t); }, { rootMargin: '120px 0px' }).observe(el);
  }
  function tick(t) {
    t.cur.x += (t.aim.x - t.cur.x) * .12;
    t.cur.y += (t.aim.y - t.cur.y) * .12;
    const s = t.el.style;
    s.setProperty('--ry', (t.cur.x * t.ry).toFixed(2) + 'deg');
    s.setProperty('--rx', (-t.cur.y * t.rx).toFixed(2) + 'deg');
    s.setProperty('--tx', (t.cur.x * t.tx).toFixed(1) + 'px');
    s.setProperty('--ty', (t.cur.y * t.ty).toFixed(1) + 'px');
    const moving = Math.abs(t.aim.x - t.cur.x) > .002 || Math.abs(t.aim.y - t.cur.y) > .002;
    t.raf = moving ? requestAnimationFrame(() => tick(t)) : 0;
  }
  function aim(t) {
    if (!pointer) { t.aim.x = t.aim.y = 0; }
    else {
      const r = t.el.getBoundingClientRect();
      const c = t.center ? t.center() : { x: r.left + r.width / 2 - t.cur.x * t.tx, y: r.top + r.height / 2 - t.cur.y * t.ty };
      const damp = t.el.matches(':focus-within') ? .3 : 1;
      t.aim.x = clamp((pointer.x - c.x) / (innerWidth * t.reach), -1, 1) * damp;
      t.aim.y = clamp((pointer.y - c.y) / (innerHeight * t.reach), -1, 1) * damp;
    }
    if (!t.raf) t.raf = requestAnimationFrame(() => tick(t));
  }
  function bindTilts() {
    addTilt($('[data-hero-stage]'), { rx: 6, ry: 10, tx: 22, ty: 12, reach: .5, center: () => ({ x: innerWidth / 2, y: innerHeight / 2 }) });
    $$('[data-tilt]').forEach((el) => addTilt(el));
    if (!tilts.length) return;
    const spot = $('[data-spot]');
    addEventListener('pointermove', (e) => {
      pointer = { x: e.clientX, y: e.clientY };
      tilts.forEach((t) => { if (t.visible) aim(t); });
      if (spot) { spot.style.setProperty('--sx', (e.clientX - innerWidth / 2) * .3 + 'px'); spot.style.setProperty('--sy', (e.clientY - innerHeight * .3) * .3 + 'px'); }
    }, { passive: true });
    document.addEventListener('pointerleave', () => { pointer = null; tilts.forEach((t) => t.visible && aim(t)); });
  }

  /* ============================================================ Bestellungen auf der Titelfolie */
  let toastsOn = false;
  function bindToasts() {
    const box = $('[data-toasts]');
    const today = $('[data-today]');
    const pool = $$('.ecard [data-product]').map((c) => ({ brand: c.dataset.brand, title: c.dataset.title, price: Number(c.dataset.price), img: c.dataset.img }));
    let total = 0, last = -1, timer = null;
    tween(today, 0, fmtEur);
    const push = () => {
      let i;
      do { i = Math.floor(Math.random() * pool.length); } while (i === last && pool.length > 1);
      last = i;
      const p = pool[i];
      const amount = Math.round(p.price * RATE * 100 + 1e-6) / 100;
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
    return (on) => {
      if (on === toastsOn || document.hidden && on) return;
      toastsOn = on;
      if (on) { push(); timer = setInterval(push, 3000); } else { clearInterval(timer); timer = null; }
    };
  }

  /* ============================================================ Folien: einpassen, einblenden, Leiste */
  function bindDeck() {
    const slides = $$('.slide');
    const title = $('#start');
    const total = slides.length;
    const bar = $('[data-deckbar]');
    const numEl = $('[data-chapter-num]');
    const titleEl = $('[data-chapter-title]');
    const nowEl = $('[data-slide-now]');
    const progress = $('[data-progress]');
    const dots = $$('[data-dot]');
    const hint = $('.keyhint');
    const toasts = bindToasts();
    $('[data-slide-total]').textContent = total;

    // gestaffeltes Einblenden je Folie
    slides.forEach((s) => {
      $$('[data-anim]', s).forEach((el, i) => el.style.setProperty('--d', Math.min(i * .07, .8).toFixed(2) + 's'));
      $$('.step', s).forEach((el, i) => el.style.setProperty('--i', i));
      $$('.tasks__list li', s).forEach((el, i) => el.style.setProperty('--i', i));
    });

    // Folie aufs Fenster einpassen (nur im Präsentationsmodus)
    const fit = () => {
      slides.forEach((s) => {
        const inner = $(':scope > .slide__inner', s);
        if (!inner) return;
        if (!isDeck()) { s.style.removeProperty('--fit'); return; }
        s.style.setProperty('--fit', 1);
        const cs = getComputedStyle(s);
        const avail = innerHeight - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom);
        const up = clamp((innerWidth - 140) / 1320, 1, 1.14);
        s.style.setProperty('--fit', clamp(avail / inner.offsetHeight, .5, up).toFixed(3));
      });
    };
    fit();
    let rt;
    addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(fit, 120); });
    deckQuery.addEventListener('change', fit);
    if (document.fonts) document.fonts.ready.then(fit);

    // Folie aktiv → Inhalte laufen ein (im Präsentationsmodus bei jedem Betreten erneut)
    const countUp = (scope) => $$('[data-count]', scope).forEach((el) => { el._v = 0; tween(el, Number(el.dataset.count), fmtInt, 1300); });
    const io = new IntersectionObserver((entries) => entries.forEach((e) => {
      const s = e.target;
      if (e.intersectionRatio >= .45 || (e.isIntersecting && !isDeck() && e.intersectionRatio > .12)) {
        if (!s.classList.contains('is-active')) { s.classList.add('is-active'); countUp(s); }
      } else if (!e.isIntersecting && isDeck()) {
        s.classList.remove('is-active');
      }
    }), { threshold: [0, .13, .45] });
    slides.filter((s) => s !== title).forEach((s) => io.observe(s));
    title.classList.add('is-active');

    // Leiste, Punkte, Titel-Fortschritt
    let current = -1, swapT;
    const setCurrent = (i, label, num) => {
      const key = i + '|' + label;
      if (key === current) return;
      current = key;
      bar.classList.add('is-swap');
      clearTimeout(swapT);
      swapT = setTimeout(() => {
        titleEl.textContent = label;
        numEl.textContent = num;
        numEl.classList.toggle('is-blank', !num);
        bar.classList.remove('is-swap');
      }, 180);
      nowEl.textContent = i + 1;
      dots.forEach((d, k) => d.classList.toggle('is-active', k === i));
    };
    const onScroll = () => {
      const vh = innerHeight;
      const r = title.getBoundingClientRect();
      const p = clamp(-r.top / (r.height - vh), 0, 1);
      title.style.setProperty('--p', p.toFixed(4));
      toasts(p > .55 && r.bottom > vh * .4);
      let idx = 0;
      slides.forEach((s, i) => { if (s.getBoundingClientRect().top <= vh * .4) idx = i; });
      const s = slides[idx];
      const label = idx === 0 ? (p > .5 ? 'Dein Shop auf vorteile.net' : s.dataset.title) : s.dataset.title;
      setCurrent(idx, label, s.dataset.num || '');
      const max = document.documentElement.scrollHeight - vh;
      progress.style.setProperty('--sp', max > 0 ? (scrollY / max).toFixed(4) : 0);
    };
    let ticking = false;
    addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(() => { ticking = false; onScroll(); }); } }, { passive: true });
    onScroll();

    // Präsentieren: Pfeiltasten, Bild↑/↓, Leertaste, Presenter → nächste Folie
    const targets = () => $$('[data-snap]').map((el) => Math.round(el.getBoundingClientRect().top + scrollY)).sort((a, b) => a - b);
    const go = (dir) => {
      const ts = targets();
      const y = scrollY;
      const next = dir > 0 ? ts.find((t) => t > y + 4) : [...ts].reverse().find((t) => t < y - 4);
      if (next === undefined) return;
      scrollTo({ top: next, behavior: reduce ? 'auto' : 'smooth' });
    };
    addEventListener('keydown', (e) => {
      if (!isDeck() || e.altKey || e.ctrlKey || e.metaKey) return;
      if (e.target.closest('input, textarea, select, [role="tab"], .rail')) return;
      if (e.key === ' ' && e.target.closest('button, a, label')) return;
      const dir = { ArrowDown: 1, PageDown: 1, ' ': e.shiftKey ? -1 : 1, ArrowUp: -1, PageUp: -1, Home: 0, End: 0 }[e.key];
      if (dir === undefined) return;
      e.preventDefault();
      hint?.classList.add('is-gone');
      if (e.key === 'Home') return scrollTo({ top: 0, behavior: 'smooth' });
      if (e.key === 'End') return scrollTo({ top: document.documentElement.scrollHeight, behavior: 'smooth' });
      go(dir);
    });
    setTimeout(() => hint?.classList.add('is-gone'), 14000);
  }

  /* ============================================================ Edits */
  function bindEdits() {
    const tabs = $$('[role="tab"]');
    const select = (tab, focus) => {
      tabs.forEach((t) => { const on = t === tab; t.setAttribute('aria-selected', on); t.tabIndex = on ? 0 : -1; $('#' + t.getAttribute('aria-controls')).hidden = !on; });
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

  /* ============================================================ Link zum Mitnehmen */
  function bindSelfLink() {
    const el = $('[data-self-link]');
    if (!el) return;
    if (/^https?:$/.test(location.protocol)) {
      el.textContent = (location.host + location.pathname).replace(/index\.html$/, '').replace(/\/$/, '');
    } else if (P.slug) {
      el.textContent = `dinosbs.github.io/pitch/${P.slug}`;
    }
  }

  /* ============================================================ Start */
  bindStudio();
  applyName();
  applyTheme();
  bindCalc();
  bindEdits();
  bindSelfLink();
  bindDeck();
  bindTilts();
})();
