/* INCENT Community-Shop – Pitch Health & Beauty (scroll-gesteuerte Präsentation)
 *
 * Präsentieren: Scrollen, Pfeiltasten ↑ ↓, Bild↑/Bild↓, Leertaste, Pos1/Ende oder Presenter – jede Folie rastet ein.
 * Jede Folie ist eine feste 16:9-Fläche (1600 × 900), die auf jeden Bildschirm skaliert wird (--k).
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
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const easeIO = (t) => (t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
  const easeOut = (t) => 1 - Math.pow(1 - t, 3);
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const finePointer = matchMedia('(hover: hover) and (pointer: fine)').matches;
  const deckQuery = matchMedia('(orientation: landscape) and (min-width: 900px) and (min-height: 480px)');
  const isDeck = () => deckQuery.matches;
  const W = 1600, H = 900; // Folienfläche in Canvas-Pixeln

  const fmtEur = new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format;
  const fmtEur0 = new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format;
  const fmtInt = new Intl.NumberFormat('de-DE', { maximumFractionDigits: 0 }).format;
  const fmtPct = (v, d = 0) => v.toLocaleString('de-DE', { minimumFractionDigits: d, maximumFractionDigits: d }) + ' %';
  const cents = (v) => Math.round(v * 100 + 1e-6) / 100;
  const params = new URLSearchParams(location.search);
  const RATE = D.rate / 100;

  /* Zahl weich auf einen neuen Wert zählen */
  function tween(el, to, fmt, dur = 800, from = el._v ?? to) {
    el._v = to;
    cancelAnimationFrame(el._raf);
    if (reduce || from === to) { el.textContent = fmt(to); return; }
    const t0 = performance.now();
    const step = (now) => {
      const k = Math.min(1, (now - t0) / dur);
      el.textContent = fmt(from + (to - from) * easeOut(k));
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
  const personalised = Boolean(initial.name || P.farbe || P.nav || params.get('farbe') || params.get('nav') || P.logo);
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
  const possessive = (n) => (n ? (/[sxzß]$/i.test(n) ? n + '’' : n + 's') : '');

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

  const splitHosts = new Set();
  function applyName() {
    const n = theme.name;
    const slug = slugify(n) || 'deinname';
    $$('[data-bind="name"]').forEach((el) => { el.textContent = n || 'Dein Name'; });
    $$('[data-bind="slug"]').forEach((el) => { el.textContent = slug; });
    $$('[data-bind="handle"]').forEach((el) => { el.textContent = slug; });
    $$('[data-bind="initial"]').forEach((el) => { el.textContent = (n || 'D').charAt(0).toUpperCase(); });
    $$('[data-bind="eyebrow"]').forEach((el) => { el.textContent = n ? `Exklusiv für ${n} · Health & Beauty` : 'Community-Shop · Health & Beauty'; });
    $$('[data-bind="thanks"]').forEach((el) => { el.textContent = n ? `${possessive(n)} Beauty-Shop.` : 'Dein Beauty-Shop.'; });
    $$('[data-bind="app"]').forEach((el) => { el.textContent = n ? `${possessive(n)} Shop` : 'Community-Shop'; });
    $('[data-for-chip]').hidden = !n;
    document.title = n ? `${possessive(n)} Beauty-Shop · INCENT Community-Shop` : 'Dein eigener Beauty-Shop · INCENT Community-Shop';
    splitHosts.forEach(splitWords); // Überschriften mit Namen neu in Wörter teilen
  }

  const studioTouched = { v: false };
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
    const studio = $('[data-studio]');
    ['pointerdown', 'keydown', 'input', 'dragenter'].forEach((t) => studio.addEventListener(t, () => { studioTouched.v = true; }, { capture: true }));
  }

  /* Live-Demo im Gestalter: solange niemand klickt, probiert der Shop selbst ein paar Looks durch.
     Verlässt man den Gestalter ohne eigene Wahl, kehrt er zum Ausgangslook zurück. */
  function bindDemo() {
    const looks = [
      { btn: '#c0746a', nav: '#f8eeea', bg: 'image' },
      { btn: '#a3245a', nav: '#ffffff', bg: 'gradient' },
      { btn: '#5f8a72', nav: '#f4efe8', bg: 'solid' },
      { btn: '#c0746a', nav: '#1d1b1e', bg: 'image' },
      { btn: '#7e6aa8', nav: '#ffffff', bg: 'gradient' },
      { btn: initial.btn, nav: initial.nav, bg: initial.bg },
    ];
    const studio = $('[data-studio]');
    let timer = 0, i = 0, on = false, hover = false, changed = false;
    studio.addEventListener('pointerenter', () => { hover = true; });
    studio.addEventListener('pointerleave', () => { hover = false; });
    const step = () => {
      if (studioTouched.v) return stop(false);
      if (!hover && !document.hidden) {
        Object.assign(theme, looks[i % looks.length]);
        i++;
        changed = true;
        applyTheme();
      }
      timer = setTimeout(step, 2600);
    };
    const stop = (restore) => {
      clearTimeout(timer);
      timer = 0;
      if (restore && changed && !studioTouched.v) {
        Object.assign(theme, { btn: initial.btn, nav: initial.nav, bg: initial.bg });
        applyTheme();
      }
      changed = false;
      i = 0;
    };
    return (want) => {
      if (personalised || reduce || studioTouched.v) want = false;
      if (want === on) return;
      on = want;
      if (on) timer = setTimeout(step, 1400); else stop(true);
    };
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
  const tiltCss = (t) => `perspective(1400px) translate3d(${(t.cur.x * t.tx).toFixed(1)}px, ${(t.cur.y * t.ty).toFixed(1)}px, 0) rotateX(${(-t.cur.y * t.rx).toFixed(2)}deg) rotateY(${(t.cur.x * t.ry).toFixed(2)}deg)`;
  function addTilt(el, opt = {}) {
    if (!finePointer || reduce || !el) return null;
    const t = { el, rx: 5, ry: 8, tx: 14, ty: 8, reach: .42, center: null, apply: null, visible: false, cur: { x: 0, y: 0 }, aim: { x: 0, y: 0 }, raf: 0, ...opt };
    tilts.push(t);
    new IntersectionObserver(([e]) => { t.visible = e.isIntersecting; if (t.visible) aimAt(t); }, { rootMargin: '120px 0px' }).observe(el);
    return t;
  }
  function tick(t) {
    t.cur.x += (t.aim.x - t.cur.x) * .12;
    t.cur.y += (t.aim.y - t.cur.y) * .12;
    if (t.apply) t.apply(t); else t.el.style.transform = tiltCss(t);
    const moving = Math.abs(t.aim.x - t.cur.x) > .002 || Math.abs(t.aim.y - t.cur.y) > .002;
    t.raf = moving ? requestAnimationFrame(() => tick(t)) : 0;
  }
  function aimAt(t) {
    if (!pointer) { t.aim.x = t.aim.y = 0; }
    else {
      const r = t.el.getBoundingClientRect();
      const c = t.center ? t.center() : { x: r.left + r.width / 2, y: r.top + r.height / 2 };
      const damp = t.el.matches(':focus-within') ? .3 : 1;
      t.aim.x = clamp((pointer.x - c.x) / (innerWidth * t.reach), -1, 1) * damp;
      t.aim.y = clamp((pointer.y - c.y) / (innerHeight * t.reach), -1, 1) * damp;
    }
    if (!t.raf) t.raf = requestAnimationFrame(() => tick(t));
  }
  function bindPointer() {
    if (!tilts.length) return;
    const spot = $('[data-spot]');
    addEventListener('pointermove', (e) => {
      pointer = { x: e.clientX, y: e.clientY };
      tilts.forEach((t) => { if (t.visible) aimAt(t); });
      if (spot) spot.style.translate = `${((e.clientX - innerWidth / 2) * .3).toFixed(0)}px ${((e.clientY - innerHeight * .3) * .3).toFixed(0)}px`;
    }, { passive: true });
    document.addEventListener('pointerleave', () => { pointer = null; tilts.forEach((t) => t.visible && aimAt(t)); });
  }

  /* ============================================================ Wörter einzeln einblenden */
  function splitWords(host) {
    splitHosts.add(host);
    const walk = (node) => {
      [...node.childNodes].forEach((n) => {
        if (n.nodeType === 3) {
          if (!n.textContent.trim()) return;
          const frag = document.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach((part) => {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.append(document.createTextNode(' ')); return; }
            const w = document.createElement('span');
            w.className = 'w';
            const i = document.createElement('span');
            i.className = 'w__i';
            i.textContent = part;
            w.append(i);
            frag.append(w);
          });
          n.replaceWith(frag);
        } else if (n.nodeType === 1 && !n.classList.contains('w')) {
          if (n.classList.contains('grad-text')) n.classList.add('is-split');
          walk(n);
        }
      });
    };
    walk(host);
    const base = parseFloat(host.dataset.splitDelay || '.15');
    $$('.w__i', host).forEach((el, k) => el.style.setProperty('--wd', (base + k * .075).toFixed(3) + 's'));
  }

  /* ============================================================ Zähler beim Betreten einer Folie */
  const animDelay = (el) => {
    const a = el.closest('[data-anim]');
    return a ? (parseFloat(a.style.getPropertyValue('--d')) || 0) * 1000 : 0;
  };
  function resetCounters(scope) {
    $$('[data-countto]', scope).forEach((el) => {
      clearTimeout(el._t);
      cancelAnimationFrame(el._raf);
      const fmt = el.dataset.fmt === 'int' ? fmtInt : fmtEur;
      el._v = Number(el.dataset.from || 0);
      el.textContent = fmt(el._v);
    });
    $$('[data-count]', scope).forEach((el) => { clearTimeout(el._t); cancelAnimationFrame(el._raf); el._v = 0; el.textContent = '0'; });
  }
  function runCounters(scope) {
    $$('[data-countto]', scope).forEach((el) => {
      const fmt = el.dataset.fmt === 'int' ? fmtInt : fmtEur;
      const from = Number(el.dataset.from || 0);
      const to = Number(el.dataset.countto);
      el._v = from;
      el.textContent = fmt(from);
      clearTimeout(el._t);
      const delay = el.dataset.delay ? Number(el.dataset.delay) : animDelay(el) + 650;
      el._t = setTimeout(() => tween(el, to, fmt, 1600, from), delay);
    });
    $$('[data-count]', scope).forEach((el) => {
      el._v = 0;
      el.textContent = '0';
      clearTimeout(el._t);
      el._t = setTimeout(() => tween(el, Number(el.dataset.count), fmtInt, 1600, 0), animDelay(el) + 250);
    });
  }

  /* ============================================================ Bestellungen am Portal (Einstieg, Schritt 2) */
  const pool = () => $$('.ecard [data-product]').map((c) => ({ brand: c.dataset.brand, title: c.dataset.title, price: Number(c.dataset.price), img: c.dataset.img }));
  function bindToasts() {
    const box = $('[data-toasts]');
    const today = $('[data-today]');
    const items = pool();
    let total = 0, last = -1, timer = 0, on = false;
    today.textContent = fmtEur(0);
    const push = () => {
      let i;
      do { i = Math.floor(Math.random() * items.length); } while (i === last && items.length > 1);
      last = i;
      const p = items[i];
      const amount = cents(p.price * RATE);
      const t = document.createElement('div');
      t.className = 'toast';
      t.innerHTML = '<span class="pimg"></span><span class="toast__txt"><small>Neue Bestellung · gerade eben</small><span></span></span><b class="toast__amt"></b>';
      $('.pimg', t).classList.add(p.img);
      $('.toast__txt span', t).textContent = `${p.brand} · ${p.title}`;
      $('.toast__amt', t).textContent = '+' + fmtEur(amount);
      box.prepend(t);
      $$('.toast:not(.is-out)', box).slice(3).forEach((old) => { old.classList.add('is-out'); setTimeout(() => old.remove(), 600); });
      total += amount;
      tween(today, total, fmtEur, 1000);
    };
    return (want) => {
      if (document.hidden) want = false;
      if (want === on) return;
      on = want;
      clearInterval(timer);
      if (on) { push(); timer = setInterval(push, 2800); }
    };
  }

  /* ============================================================ iPhone-Sperrbildschirm: Mitteilungen schieben sich von unten ein */
  function bindLockscreen() {
    const list = $('[data-ios-notes]');
    if (!list) return () => {};
    const timeEl = $('[data-ios-time]');
    const dateEl = $('[data-ios-date]');
    const totalEl = $('[data-ios-total]');
    const countEl = $('[data-ios-count]');
    const ring = $('[data-ios-ring]');
    const items = pool();
    const fmtDate = new Intl.DateTimeFormat('de-DE', { weekday: 'long', day: 'numeric', month: 'long' }).format;
    const fmtMonth = new Intl.DateTimeFormat('de-DE', { month: 'long' }).format;
    const monthEl = $('[data-ios-month]');
    const now = new Date();
    const clock = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 22, 58);
    const MAX = 3;
    let total = 0, count = 0, members = 0, timer = 0, on = false, last = -1;
    const paintClock = () => {
      timeEl.textContent = `${clock.getHours()}:${String(clock.getMinutes()).padStart(2, '0')}`;
      dateEl.textContent = fmtDate(clock);
      monthEl.textContent = fmtMonth(clock);
    };
    paintClock();
    const ago = (m) => (m < 1 ? 'Jetzt' : m < 60 ? `vor ${m} Min.` : `vor ${Math.floor(m / 60)} Std.`);
    const appIcon = '<svg class="i" aria-hidden="true"><use href="#i-bag"/></svg>';
    const note = (title, text) => {
      const li = document.createElement('li');
      li.className = 'ios-note';
      li._at = clock.getTime();
      li.innerHTML = `<span class="ios-note__icon">${appIcon}</span><span class="ios-note__body"><span class="ios-note__top"><b data-bind="app"></b><time>Jetzt</time></span><span class="ios-note__title"></span><span class="ios-note__text"></span></span>`;
      $('[data-bind="app"]', li).textContent = theme.name ? `${possessive(theme.name)} Shop` : 'Community-Shop';
      $('.ios-note__title', li).textContent = title;
      $('.ios-note__text', li).textContent = text;
      return li;
    };
    const make = () => {
      if (count > 2 && Math.random() < .16) {
        const n = 2 + Math.floor(Math.random() * 4);
        members += n;
        return note(`${n} neue Mitglieder`, `Deine Community wächst – ${fmtInt(members)} neue Mitglieder heute Nacht.`);
      }
      let i;
      do { i = Math.floor(Math.random() * items.length); } while (i === last && items.length > 1);
      last = i;
      const p = items[i];
      const amount = cents(p.price * RATE);
      total = cents(total + amount);
      count++;
      return note(`Neue Bestellung · +${fmtEur(amount)}`, `${p.brand} · ${p.title}`);
    };
    const paintTotals = (animate) => {
      if (animate) tween(totalEl, total, fmtEur, 1100); else { totalEl._v = total; totalEl.textContent = fmtEur(total); }
      countEl.textContent = fmtInt(count);
      ring.style.setProperty('--ring', (100 - Math.min(100, count / 40 * 100)).toFixed(1));
    };
    const push = (animate = true) => {
      clock.setMinutes(clock.getMinutes() + 2 + Math.floor(Math.random() * 8));
      paintClock();
      const old = $$('.ios-note:not(.is-leaving)', list);
      const before = animate ? old.map((el) => el.getBoundingClientRect().top) : [];
      const li = make();
      if (animate) {
        li.classList.add('is-new');
        li.addEventListener('animationend', () => li.classList.remove('is-new'), { once: true });
      }
      list.append(li);
      // ältere Mitteilungen rücken nach oben (FLIP – nur transform)
      if (animate) {
        old.forEach((el, k) => {
          const dy = before[k] - el.getBoundingClientRect().top;
          if (!dy) return;
          el.style.transition = 'none';
          el.style.transform = `translate3d(0, ${dy}px, 0)`;
          requestAnimationFrame(() => requestAnimationFrame(() => {
            el.style.transition = 'transform .85s cubic-bezier(.2, .9, .25, 1)';
            el.style.transform = '';
          }));
        });
      }
      const live = [...old, li];
      live.slice(0, Math.max(0, live.length - MAX)).forEach((el) => {
        if (!animate) { el.remove(); return; }
        el.classList.add('is-leaving');
        setTimeout(() => el.remove(), 650);
      });
      $$('.ios-note', list).forEach((el) => { $('time', el).textContent = ago(Math.round((clock.getTime() - el._at) / 60000)); });
      paintTotals(animate);
    };
    // Startzustand: ein paar Mitteilungen aus der Nacht liegen schon da
    push(false); push(false); push(false);
    return (want) => {
      if (document.hidden) want = false;
      if (want === on) return;
      on = want;
      clearInterval(timer);
      if (on) timer = setInterval(push, 2600);
    };
  }

  /* ============================================================ Edits: Reiter wechseln von selbst, bis jemand klickt */
  function bindEdits() {
    const tabs = $$('[role="tab"]');
    const bar = $('[data-tabs]');
    let auto = !reduce, timer = 0, running = false;
    const select = (tab, focus) => {
      tabs.forEach((t) => { const on = t === tab; t.setAttribute('aria-selected', on); t.tabIndex = on ? 0 : -1; $('#' + t.getAttribute('aria-controls')).hidden = !on; });
      if (focus) tab.focus();
      const rail = $('#' + tab.getAttribute('aria-controls') + ' .rail');
      if (rail) rail.scrollLeft = 0;
    };
    const stopAuto = () => { auto = false; clearTimeout(timer); bar.classList.remove('is-auto'); };
    tabs.forEach((t, i) => {
      t.addEventListener('click', () => { stopAuto(); select(t); });
      t.addEventListener('keydown', (e) => {
        const d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
        if (!d) return;
        e.preventDefault();
        stopAuto();
        select(tabs[(i + d + tabs.length) % tabs.length], true);
      });
    });
    $$('.ecard').forEach((c) => c.style.setProperty('--ci', [...c.parentNode.children].indexOf(c)));
    $$('[data-rail]').forEach((btn) => btn.addEventListener('click', () => {
      stopAuto();
      const rail = $('.rail', btn.closest('.edit'));
      rail.scrollBy({ left: Number(btn.dataset.rail) * rail.clientWidth * .8, behavior: reduce ? 'auto' : 'smooth' });
    }));
    $$('.rail').forEach((r) => r.addEventListener('pointerdown', stopAuto));
    const DUR = 6500;
    bar.style.setProperty('--auto', DUR + 'ms');
    const next = () => {
      const i = tabs.findIndex((t) => t.getAttribute('aria-selected') === 'true');
      select(tabs[(i + 1) % tabs.length]);
      timer = setTimeout(next, DUR);
    };
    return (want) => {
      want = want && auto && !document.hidden;
      if (want === running) return;
      running = want;
      clearTimeout(timer);
      bar.classList.toggle('is-auto', want);
      if (want) {
        // Timer-Leiste am aktiven Reiter neu starten
        const cur = tabs.find((t) => t.getAttribute('aria-selected') === 'true');
        if (cur) { cur.setAttribute('aria-selected', 'false'); void cur.offsetWidth; cur.setAttribute('aria-selected', 'true'); }
        timer = setTimeout(next, DUR);
      }
    };
  }

  /* ============================================================ Präsentation: skalieren, Einstieg, Folienwechsel, Leiste */
  function bindDeck() {
    const deck = $('.deck');
    const intro = $('#start');
    const sections = [intro, ...$$('.slide')];
    const slides = $$('.slide');
    const snaps = $$('[data-snap]');
    const acts = $$('.acts li');
    const nowEl = $('[data-slide-now]');
    const hint = $('.keyhint');
    const legend = $('[data-legend]');
    $('[data-slide-total]').textContent = String(snaps.length).padStart(2, '0');

    const toasts = bindToasts();
    const lock = bindLockscreen();
    const edits = bindEdits();
    const demo = bindDemo();

    // gestaffeltes Einblenden: Eyebrow → Überschrift (Wort für Wort) → Inhalte nacheinander
    sections.forEach((s) => {
      $$('[data-split]', s).forEach(splitWords);
      let k = 0;
      $$('[data-anim]', s).forEach((el) => {
        if (el.style.getPropertyValue('--d')) return;
        const isEyebrow = el.classList.contains('eyebrow');
        el.style.setProperty('--d', (isEyebrow ? 0 : Math.min(.45 + k++ * .13, 1.9)).toFixed(2) + 's');
      });
      $$('.step', s).forEach((el, i) => el.style.setProperty('--i', i));
      $$('.tasks__list li', s).forEach((el, i) => el.style.setProperty('--i', i));
      $$('.mcard', s).forEach((el, i) => el.style.setProperty('--mi', i));
    });
    // Titel: erst nach dem Laden einblenden
    $$('[data-anim]', intro).forEach((el, i) => el.style.setProperty('--d', (i === 0 ? .2 : .9 + i * .14).toFixed(2) + 's'));
    $$('.w__i', intro).forEach((el, k) => el.style.setProperty('--wd', (.35 + k * .11).toFixed(3) + 's'));

    // Legende rechts: jede Folie ein Punkt, bei Hover mit Nummer und Titel
    const ol = document.createElement('ol');
    let prevAct = null;
    snaps.forEach((s, i) => {
      const li = document.createElement('li');
      const act = s.closest('[data-act]').dataset.act;
      if (prevAct !== null && act !== prevAct) li.dataset.actStart = '';
      prevAct = act;
      const a = document.createElement('a');
      a.href = '#';
      a.innerHTML = '<span class="legend__num"></span><span class="legend__label"></span><span class="legend__dot"></span>';
      $('.legend__num', a).textContent = String(i + 1).padStart(2, '0');
      $('.legend__label', a).textContent = s.dataset.label;
      a.setAttribute('aria-label', `${i + 1}: ${s.dataset.label}`);
      a.addEventListener('click', (e) => { e.preventDefault(); goTo(i); });
      li.append(a);
      ol.append(li);
    });
    legend.append(ol);
    const marks = $$('a', legend);

    // Maße (Dokument-Positionen) – bei Größenänderung neu
    let vh = innerHeight, k = 1, snapTops = [], slideTops = [], introTop = 0;
    const measure = () => {
      vh = innerHeight;
      if (isDeck()) {
        k = Math.min(innerWidth / W, innerHeight / H);
        root.style.setProperty('--k', k.toFixed(4));
      } else {
        k = 1;
        root.style.removeProperty('--k');
      }
      const y = scrollY;
      snapTops = snaps.map((s) => Math.round(s.getBoundingClientRect().top + y));
      slideTops = slides.map((s) => s.getBoundingClientRect().top + y);
      introTop = intro.getBoundingClientRect().top + y;
    };

    // Folieninhalt einmalig in die Fläche einpassen (Canvas-Pixel, unabhängig vom Bildschirm)
    const fit = () => {
      $$('.content').forEach((c) => {
        if (!isDeck()) { c.style.removeProperty('--fit'); return; }
        c.style.setProperty('--fit', 1);
        const box = c.parentElement.getBoundingClientRect().height;
        const h = c.getBoundingClientRect().height;
        c.style.setProperty('--fit', h > box ? (box / h).toFixed(3) : 1);
      });
    };

    // Einstieg: eine Bühne, drei Schritte. Titel → das Portal richtet sich auf → Gestalter fährt ein
    const titleEl = $('[data-intro-title]');
    const capEl = $('[data-intro-cap]');
    const stage = $('[data-hero-stage]');
    const floats = $$('.float', stage);
    const studio = $('[data-studio]');
    const phone = $('.intro__phone');
    const cue = $('.scroll-cue');
    const liveEl = $('[data-intro-live]');
    const introShell = $('.shell', intro);
    const S = {
      A: { px: 0, py: 660, prx: 26, pry: 0, ps: .94 },
      B: { px: 0, py: 132, prx: 0, pry: 0, ps: .86 },
      C: { px: 106, py: 112, prx: 0, pry: -5, ps: .8 },
    };
    const pose = { ...S.A };
    let stageTilt = null;
    const paintStage = () => {
      const t = stageTilt ? stageTilt.cur : { x: 0, y: 0 };
      stage.style.transform = `translate3d(${pose.px.toFixed(1)}px, ${pose.py.toFixed(1)}px, 0) rotateX(${pose.prx.toFixed(2)}deg) rotateY(${pose.pry.toFixed(2)}deg) translate3d(${(t.x * 22).toFixed(1)}px, ${(t.y * 12).toFixed(1)}px, 0) rotateX(${(-t.y * 6).toFixed(2)}deg) rotateY(${(t.x * 9).toFixed(2)}deg) scale(${pose.ps.toFixed(4)})`;
    };
    stageTilt = addTilt(stage, { reach: .5, center: () => ({ x: innerWidth / 2, y: innerHeight / 2 }), apply: paintStage });
    const clearIntro = () => [titleEl, capEl, stage, studio, phone, cue, liveEl, introShell, ...floats].forEach((el) => { el.style.transform = ''; el.style.opacity = ''; });

    let builder = null;
    const paintIntro = (P) => {
      const ia = easeIO(clamp(P)), ib = easeIO(clamp(P - 1));
      const from = ib > 0 ? S.B : S.A, to = ib > 0 ? S.C : S.B, t = ib > 0 ? ib : ia;
      for (const key in pose) pose[key] = lerp(from[key], to[key], t);
      paintStage();
      titleEl.style.opacity = clamp(1 - ia * 2.2).toFixed(3);
      titleEl.style.transform = `translate3d(0, ${(-120 * ia).toFixed(1)}px, 0) scale(${(1 - ia * .06).toFixed(4)})`;
      const cap = clamp((ia - .5) / .3) * (1 - clamp(ib / .3));
      capEl.style.opacity = cap.toFixed(3);
      capEl.style.transform = `translate3d(0, ${((1 - cap) * 16).toFixed(1)}px, 0)`;
      const fl = clamp((ia - .55) / .3) * (1 - clamp(ib / .35));
      floats.forEach((f) => { f.style.opacity = fl.toFixed(3); });
      studio.style.opacity = ib.toFixed(3);
      studio.style.transform = `translate3d(${((1 - ib) * -560).toFixed(1)}px, 0, 0)`;
      phone.style.opacity = ib.toFixed(3);
      phone.style.transform = `translate3d(0, ${((1 - ib) * 620).toFixed(1)}px, 0) rotate(${((1 - ib) * 10).toFixed(2)}deg)`;
      cue.style.opacity = clamp(1 - ia * 5).toFixed(3);
      const isB = ib > .5;
      if (isB !== builder) { builder = isB; intro.classList.toggle('is-builder', isB); }
      liveEl.style.opacity = clamp((ib - .6) / .4).toFixed(3);
      toasts(fl > .3);
    };

    // Folienwechsel mit Tiefe: die alte Folie weicht zurück, die neue schiebt sich darüber
    const depth = new Map();
    const paintDepth = (el, p) => {
      const key = p > 0 ? p.toFixed(3) : '0';
      if (depth.get(el) === key) return;
      depth.set(el, key);
      if (p <= 0) { el.style.transform = ''; el.style.opacity = ''; return; }
      const e = easeOut(p);
      el.style.transform = `translate3d(0, ${(p * vh * .62).toFixed(1)}px, 0) scale(${(1 - e * .08).toFixed(4)})`;
      el.style.opacity = (1 - e * .7).toFixed(3);
    };

    // aktuelle Folie → Leiste, Legende, Zähler
    let cur = -1;
    const paintCurrent = () => {
      const y = scrollY + vh * .5;
      let i = 0;
      snapTops.forEach((t, k2) => { if (t <= y) i = k2; });
      if (i === cur) return;
      cur = i;
      nowEl.textContent = String(i + 1).padStart(2, '0');
      marks.forEach((m, k2) => m.classList.toggle('is-active', k2 === i));
      const act = Number(snaps[i].closest('[data-act]').dataset.act);
      acts.forEach((li, a) => {
        const inAct = snaps.filter((s) => Number(s.closest('[data-act]').dataset.act) === a);
        const pos = inAct.indexOf(snaps[i]);
        li.classList.toggle('is-current', a === act);
        li.classList.toggle('is-done', a < act);
        li.style.setProperty('--ap', a < act ? 1 : a > act ? 0 : ((pos + 1) / inAct.length).toFixed(3));
      });
    };

    let lastP = null;
    const onScroll = () => {
      if (isDeck()) {
        const P = (scrollY - introTop) / vh;
        const Pc = Math.round(clamp(P, 0, 2) * 2000) / 2000;
        if (Pc !== lastP) { lastP = Pc; paintIntro(Pc); }
        demo(P > 1.8 && P < 2.25);
        paintDepth(introShell, clamp(P - 2));
        slides.forEach((s, i) => paintDepth(s.firstElementChild, clamp((scrollY - slideTops[i]) / vh)));
      }
      paintCurrent();
    };
    let ticking = false;
    const queue = () => { if (!ticking) { ticking = true; requestAnimationFrame(() => { ticking = false; onScroll(); }); } };
    addEventListener('scroll', queue, { passive: true });

    const relayout = () => {
      measure();
      if (!isDeck()) {
        clearIntro();
        depth.forEach((_, el) => { el.style.transform = ''; el.style.opacity = ''; });
        depth.clear();
        intro.classList.remove('is-builder');
        builder = null;
        toasts(true);
      }
      cur = -1;
      lastP = null;
      onScroll();
    };
    let rt;
    addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(relayout, 100); measure(); onScroll(); });
    deckQuery.addEventListener('change', () => { measure(); fit(); relayout(); });
    measure();
    fit();
    relayout();
    if (document.fonts) document.fonts.ready.then(() => { fit(); relayout(); });

    // Folie aktiv → Inhalte laufen ein (im Präsentationsmodus bei jedem Betreten erneut); Schleifen nur in der Nähe
    const loops = (s, on) => {
      if (s.id === 'passiv') lock(on);
      if (s.id === 'edits') edits(on && s.classList.contains('is-active'));
      if (s === intro && !isDeck()) toasts(on);
    };
    const activate = (s, on) => {
      if (s.classList.contains('is-active') === on) return;
      s.classList.toggle('is-active', on);
      if (on) runCounters(s); else resetCounters(s);
      if (s.id === 'edits') edits(on);
    };
    const io = new IntersectionObserver((entries) => entries.forEach((e) => {
      const s = e.target;
      if (isDeck()) {
        if (s === intro) activate(s, e.isIntersecting);
        else if (e.intersectionRatio >= .5) activate(s, true);
        else if (!e.isIntersecting) activate(s, false);
      } else if (e.isIntersecting && (e.intersectionRatio > .12 || e.intersectionRect.height > innerHeight * .3)) {
        activate(s, true);
      }
    }), { threshold: [0, .13, .5] });
    const near = new IntersectionObserver((entries) => entries.forEach((e) => {
      e.target.classList.toggle('is-near', e.isIntersecting);
      loops(e.target, e.isIntersecting);
    }), { rootMargin: '100% 0px' });
    sections.forEach((s) => { resetCounters(s); io.observe(s); near.observe(s); });

    document.addEventListener('visibilitychange', () => {
      const vis = !document.hidden;
      lock(vis && $('#passiv').classList.contains('is-near'));
      edits(vis && $('#edits').classList.contains('is-active'));
      if (!vis) toasts(false); else onScroll();
    });

    // Präsentieren: Pfeiltasten, Bild↑/↓, Leertaste, Pos1/Ende, Presenter → nächster Haltepunkt
    function goTo(i) {
      i = clamp(i, 0, snapTops.length - 1);
      scrollTo({ top: snapTops[i], behavior: reduce ? 'auto' : 'smooth' });
    }
    addEventListener('keydown', (e) => {
      if (!isDeck() || e.altKey || e.ctrlKey || e.metaKey) return;
      if (e.target.closest('input, textarea, select, [role="tab"], .rail')) return;
      if (e.key === ' ' && e.target.closest('button, a, label')) return;
      const dir = { ArrowDown: 1, PageDown: 1, ArrowRight: 1, ' ': e.shiftKey ? -1 : 1, ArrowUp: -1, PageUp: -1, ArrowLeft: -1, Home: 0, End: 0 }[e.key];
      if (dir === undefined) return;
      e.preventDefault();
      hint?.classList.add('is-gone');
      if (e.key === 'Home') return goTo(0);
      if (e.key === 'End') return goTo(snapTops.length - 1);
      const y = scrollY;
      const target = dir > 0 ? snapTops.findIndex((t) => t > y + 4) : snapTops.map((t, k2) => [t, k2]).filter(([t]) => t < y - 4).pop()?.[1];
      if (target === undefined || target < 0) return;
      goTo(target);
    });
    setTimeout(() => hint?.classList.add('is-gone'), 14000);
    deck.classList.add('is-ready');
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
  applyTheme();
  bindCalc();
  bindSelfLink();
  $$('[data-tilt]').forEach((el) => addTilt(el));
  bindDeck();
  applyName();
  bindPointer();
})();
