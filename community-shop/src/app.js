/* INCENT Community Shop – Pitch Health & Beauty
 *
 * Personalisieren per URL, z. B.:
 *   index.html?name=Lena&farbe=salbei&provision=12&reichweite=250000
 *   farbe: rose | nude | salbei | lavendel | noir
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

  const fmtEur = new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format;
  const fmtEur0 = new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format;
  const fmtInt = new Intl.NumberFormat('de-DE', { maximumFractionDigits: 0 }).format;
  const fmtPct = (v, d = 0) => v.toLocaleString('de-DE', { minimumFractionDigits: d, maximumFractionDigits: d }) + ' %';

  /* ------------------------------------------------------------ state */
  const params = new URLSearchParams(location.search);
  const THEME_ALIAS = { rose: 'rose', 'rosé': 'rose', nude: 'nude', salbei: 'sage', sage: 'sage', lavendel: 'lilac', lilac: 'lilac', noir: 'noir' };

  const state = {
    rate: clamp(Number(params.get('provision')) || D.defaults.rate, 5, 20),
    followers: clamp(Number(params.get('reichweite')) || D.defaults.followers, 5000, 1000000),
    conv: D.defaults.conv,
    basket: D.defaults.basket,
    name: (params.get('name') || '').trim().slice(0, 18),
    theme: THEME_ALIAS[(params.get('farbe') || '').toLowerCase()] || 'rose',
  };

  /* ------------------------------------------------------------ number tween */
  function tween(el, to, fmt, dur = 700) {
    const from = el._v ?? to;
    el._v = to;
    cancelAnimationFrame(el._raf);
    if (reduce || from === to) { el.textContent = fmt(to); return; }
    const t0 = performance.now();
    const step = (now) => {
      const k = Math.min(1, (now - t0) / dur);
      const e = 1 - Math.pow(1 - k, 3);
      el.textContent = fmt(from + (to - from) * e);
      if (k < 1) el._raf = requestAnimationFrame(step);
    };
    el._raf = requestAnimationFrame(step);
  }

  /* ------------------------------------------------------------ range fill */
  function paintRange(input) {
    const p = (input.value - input.min) / (input.max - input.min) * 100;
    input.style.setProperty('--p', p + '%');
  }

  /* ------------------------------------------------------------ provision */
  function renderRate() {
    $$('[data-out="rate"]').forEach((o) => { o.textContent = fmtPct(state.rate); });
    $$('input[data-input="rate"]').forEach((i) => { i.value = state.rate; paintRange(i); });
    $$('[data-earn]').forEach((el) => {
      const x = Number(el.dataset.earnX || 1);
      tween(el, Number(el.dataset.earn) * x * state.rate / 100, fmtEur, 450);
    });
  }

  /* ------------------------------------------------------------ calculator */
  const LOG_MIN = 5000, LOG_MAX = 1000000;
  const followersFromSlider = (v) => {
    const raw = LOG_MIN * Math.pow(LOG_MAX / LOG_MIN, v / 1000);
    const stepSize = raw < 20000 ? 500 : raw < 100000 ? 1000 : raw < 500000 ? 5000 : 10000;
    return Math.round(raw / stepSize) * stepSize;
  };
  const sliderFromFollowers = (f) => Math.round(1000 * Math.log(f / LOG_MIN) / Math.log(LOG_MAX / LOG_MIN));

  function renderCalc() {
    const orders = state.followers * state.conv / 100;
    const revenue = orders * state.basket;
    const month = revenue * state.rate / 100;
    const savings = revenue * D.avgDiscount / (1 - D.avgDiscount);
    const out = { orders, revenue, month, year: month * 12, savings };
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
    $$('input[data-input="rate"]').forEach((i) => i.addEventListener('input', () => {
      state.rate = Number(i.value);
      renderRate();
      renderCalc();
    }));
    $$('[data-preset]').forEach((btn) => btn.addEventListener('click', () => {
      state.followers = Number(btn.dataset.preset);
      f.value = sliderFromFollowers(state.followers);
      paintRange(f);
      renderCalc();
    }));
  }

  /* ------------------------------------------------------------ shop studio */
  const slugify = (s) => s.toLowerCase()
    .replace(/ä/g, 'ae').replace(/ö/g, 'oe').replace(/ü/g, 'ue').replace(/ß/g, 'ss')
    .normalize('NFD').replace(/[̀-ͯ]/g, '')
    .replace(/[^a-z0-9]+/g, '').slice(0, 24);

  function renderName() {
    const n = state.name;
    const slug = slugify(n) || 'deinname';
    const poss = n ? (/[sxzß]$/i.test(n) ? n + '’' : n + 's') : 'Dein';
    $$('[data-bind="name"]').forEach((el) => { el.textContent = n || 'Dein Name'; });
    $$('[data-bind="slug"]').forEach((el) => { el.textContent = slug; });
    $$('[data-bind="possessive"]').forEach((el) => { el.textContent = poss; });
    $$('[data-bind="handle"]').forEach((el) => { el.textContent = '@' + slug; });
    $$('[data-bind="initial"]').forEach((el) => { el.textContent = (n || 'D').charAt(0).toUpperCase(); });
  }

  function renderTheme() {
    const t = D.themes[state.theme];
    root.style.setProperty('--s-accent', t.accent);
    root.style.setProperty('--s-soft', t.soft);
    root.style.setProperty('--s-bg', t.bg);
    root.style.setProperty('--s-ink', t.ink);
  }

  function bindStudio() {
    const form = $('[data-studio]');
    const input = $('input[data-input="name"]');
    input.value = state.name;
    input.addEventListener('input', () => { state.name = input.value.trim(); renderName(); });

    const themeInput = $(`input[name="theme"][value="${state.theme}"]`);
    if (themeInput) themeInput.checked = true;

    form.addEventListener('change', (e) => {
      const el = e.target;
      if (el.name === 'theme') { state.theme = el.value; renderTheme(); }
      if (el.name === 'font') { root.dataset.font = el.value; }
      if (el.name === 'motif') { root.style.setProperty('--motif', `var(--motif-${el.value})`); }
    });
  }

  /* ------------------------------------------------------------ sales toasts */
  function bindToasts() {
    const box = $('[data-toasts]');
    const today = $('[data-today]');
    if (!box) return;
    const pool = $$('.pcard[data-product]').map((c) => ({
      brand: c.dataset.brand,
      title: c.dataset.title.replace(/^(EdP|EdT|EDP)\s+/, '').replace(/[„“"]/g, ''),
      price: Number(c.dataset.price),
      img: $('img', c).src,
    }));
    if (!pool.length) return;

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
      t.innerHTML = '<img alt=""><span class="toast__txt"><small>Neue Bestellung · gerade eben</small><span></span></span><b class="toast__amt"></b>';
      $('img', t).src = p.img;
      $('.toast__txt span', t).textContent = `${p.brand} · ${p.title}`;
      $('.toast__amt', t).textContent = '+' + fmtEur(amount);
      box.prepend(t);

      const items = $$('.toast:not(.is-out)', box);
      items.slice(2).forEach((old) => {
        old.classList.add('is-out');
        setTimeout(() => old.remove(), 500);
      });
      total += amount;
      tween(today, total, fmtEur, 900);
    };

    const start = () => { if (!timer) { push(); timer = setInterval(push, 3200); } };
    const stop = () => { clearInterval(timer); timer = null; };

    new IntersectionObserver(([e]) => {
      visible = e.isIntersecting;
      visible && !document.hidden ? start() : stop();
    }, { threshold: .25 }).observe($('#start'));
    document.addEventListener('visibilitychange', () => (visible && !document.hidden ? start() : stop()));
  }

  /* ------------------------------------------------------------ edits (tabs + rails) */
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
      rail.scrollBy({ left: Number(btn.dataset.rail) * rail.clientWidth * 0.8, behavior: reduce ? 'auto' : 'smooth' });
    }));
  }

  /* ------------------------------------------------------------ reveal + counters */
  function bindReveal() {
    const groups = new Map();
    $$('.reveal').forEach((el) => {
      const list = groups.get(el.parentElement) || [];
      list.push(el);
      groups.set(el.parentElement, list);
    });
    groups.forEach((list) => list.forEach((el, i) => el.style.setProperty('--d', Math.min(i * 90, 450) + 'ms')));
    $$('.dash__chart i').forEach((el, i) => el.style.setProperty('--i', i));

    const countUp = (scope) => $$('[data-count]', scope).forEach((el) => {
      if (el._counted) return;
      el._counted = true;
      el._v = 0;
      tween(el, Number(el.dataset.count), fmtInt, 1400);
    });

    if (!('IntersectionObserver' in window)) {
      $$('.reveal').forEach((el) => el.classList.add('is-in'));
      return;
    }
    const io = new IntersectionObserver((entries) => entries.forEach((e) => {
      if (!e.isIntersecting) return;
      e.target.classList.add('is-in');
      countUp(e.target);
      io.unobserve(e.target);
    }), { threshold: .12, rootMargin: '0px 0px -6% 0px' });
    $$('.reveal').forEach((el) => io.observe(el));
  }

  /* ------------------------------------------------------------ navigation */
  function bindNav() {
    const slides = $$('.slide');
    const dots = $('[data-dots]');
    const topbar = $('[data-topbar]');
    const navLinks = $$('.topbar__nav a');
    const hint = $('.keyhint');

    const setActive = (id) => {
      $$('[data-dot]').forEach((d) => d.classList.toggle('is-active', d.dataset.dot === id));
      navLinks.forEach((a) => a.classList.toggle('is-active', a.getAttribute('href') === '#' + id));
      const dark = $('#' + id)?.classList.contains('slide--dark');
      dots.classList.toggle('is-dark', !!dark);
    };
    const io = new IntersectionObserver((entries) => entries.forEach((e) => {
      if (e.isIntersecting) setActive(e.target.id);
    }), { rootMargin: '-45% 0px -50% 0px' });
    slides.forEach((s) => io.observe(s));

    const onScroll = () => {
      topbar.classList.toggle('is-scrolled', scrollY > 8);
      const under = slides.find((s) => { const r = s.getBoundingClientRect(); return r.top <= 32 && r.bottom > 32; });
      topbar.classList.toggle('is-dark', !!under && under.classList.contains('slide--dark'));
    };
    addEventListener('scroll', onScroll, { passive: true });
    onScroll();

    // Präsentationsmodus: Pfeiltasten / Presenter (PageUp/PageDown) springen von Folie zu Folie
    const go = (dir) => {
      const y = scrollY, vh = innerHeight, slack = 72;
      const tops = slides.map((s) => s.getBoundingClientRect().top + y);
      let cur = 0;
      tops.forEach((t, i) => { if (t <= y + slack) cur = i; });
      const curBottom = tops[cur] + slides[cur].offsetHeight;
      let target;
      if (dir > 0) {
        if (curBottom - (y + vh) > 60) target = Math.min(y + vh * 0.85, curBottom - vh);
        else target = tops[cur + 1];
      } else if (y - tops[cur] > vh * 0.9) target = y - vh * 0.85;
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

  /* ------------------------------------------------------------ contact */
  function bindContact() {
    if (!D.contact) return;
    $$('[data-contact]').forEach((a) => {
      a.href = `mailto:${D.contact}?subject=${encodeURIComponent('Community Shop – Lass uns sprechen')}`;
    });
  }

  /* ------------------------------------------------------------ go */
  renderName();
  renderTheme();
  bindStudio();
  bindCalc();
  renderRate();
  renderCalc();
  bindEdits();
  bindReveal();
  bindNav();
  bindToasts();
  bindContact();
})();
