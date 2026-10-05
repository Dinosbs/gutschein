/*
 * Select-Hinweis
 * Markiert Gutscheine, die nicht mit dem Select-Einkaufsgutschein kaufbar sind –
 * in der Gutscheinwelt (Icon + Tooltip), im Warenkorb und im Checkout (Hinweis am Artikel)
 * sowie am Gutscheincode-Feld („Details prüfen“).
 */
(() => {
  'use strict';

  // Prototyp: Zuordnung über den Markennamen. Im echten Shop käme das als Flag
  // pro Produkt aus der API (z. B. `selectVoucherExcluded: true`).
  const EXCLUDED_BRANDS = ['flixbus', 'circle k de', 'wellcard'];

  const VOUCHER_NAME = 'Select-Einkaufsgutschein';
  const VOUCHER_HTML = `<span class="sh-nowrap">${VOUCHER_NAME}</span>`; // kein Umbruch nach „Select-“
  const HINT_HTML = `Dieser Gutschein ist <strong>nicht</strong> mit dem ${VOUCHER_HTML} kaufbar`;
  const HINT_TEXT = `Dieser Gutschein ist nicht mit dem ${VOUCHER_NAME} kaufbar`;

  const ICON = '<svg class="sh-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M3 7.5A1.5 1.5 0 0 1 4.5 6h15A1.5 1.5 0 0 1 21 7.5V10a2 2 0 0 0 0 4v2.5a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 16.5V14a2 2 0 0 0 0-4Z"/><path d="m9.75 9.75 4.5 4.5m0-4.5-4.5 4.5"/></svg>';
  const CHEVRON = '<svg class="sh-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="m6 9 6 6 6-6"/></svg>';

  const normalize = (text) => (text || '').replace(/\s+/g, ' ').trim().toLowerCase();
  const isExcluded = (brand) => EXCLUDED_BRANDS.includes(normalize(brand));
  const plural = (n, one, many) => (n === 1 ? one : many);

  /* ---------------------------------------------------------------- */
  /* Tooltip                                                            */
  /* ---------------------------------------------------------------- */

  const tooltip = document.createElement('div');
  tooltip.className = 'sh-tooltip';
  tooltip.id = 'sh-tooltip';
  tooltip.setAttribute('role', 'tooltip');
  tooltip.dataset.placement = 'bottom';
  tooltip.innerHTML = `<span class="sh-tooltip__icon">${ICON}</span><p class="sh-tooltip__text">${HINT_HTML}</p><span class="sh-tooltip__arrow"></span>`;
  document.body.appendChild(tooltip);

  let activeBadge = null;
  let pinned = false;
  let hideTimer = 0;
  let frame = 0;

  function positionTooltip() {
    if (!activeBadge) return;
    const GAP = 10;
    const MARGIN = 12;
    const rect = activeBadge.getBoundingClientRect();
    const viewportWidth = document.documentElement.clientWidth;
    const viewportHeight = window.innerHeight;

    if (rect.bottom < 0 || rect.top > viewportHeight) {
      hideTooltip(true);
      return;
    }

    const width = tooltip.offsetWidth;
    const height = tooltip.offsetHeight;
    const centerX = rect.left + rect.width / 2;

    // bevorzugt unterhalb, Sprechblase links am Icon verankert
    let placement = 'bottom';
    let top = rect.bottom + GAP;
    if (top + height > viewportHeight - MARGIN && rect.top - GAP - height > MARGIN) {
      placement = 'top';
      top = rect.top - GAP - height;
    }

    let left = centerX - 28;
    left = Math.max(MARGIN, Math.min(left, viewportWidth - width - MARGIN));
    const arrowX = Math.max(16, Math.min(centerX - left, width - 16));

    tooltip.dataset.placement = placement;
    tooltip.style.left = `${Math.round(left)}px`;
    tooltip.style.top = `${Math.round(top)}px`;
    tooltip.style.setProperty('--sh-arrow-x', `${Math.round(arrowX)}px`);
  }

  function showTooltip(badge) {
    clearTimeout(hideTimer);
    if (activeBadge && activeBadge !== badge) activeBadge.classList.remove('is-active');
    activeBadge = badge;
    badge.classList.add('is-active');
    positionTooltip();
    tooltip.classList.add('is-visible');
  }

  function hideTooltip(immediately = false) {
    clearTimeout(hideTimer);
    const hide = () => {
      tooltip.classList.remove('is-visible');
      if (activeBadge) activeBadge.classList.remove('is-active');
      activeBadge = null;
      pinned = false;
    };
    if (immediately) hide();
    else hideTimer = setTimeout(hide, 90);
  }

  const schedulePosition = () => {
    if (!activeBadge) return;
    cancelAnimationFrame(frame);
    frame = requestAnimationFrame(positionTooltip);
  };
  window.addEventListener('scroll', schedulePosition, { passive: true, capture: true });
  window.addEventListener('resize', schedulePosition, { passive: true });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && activeBadge) hideTooltip(true);
  });

  document.addEventListener('click', (event) => {
    if (activeBadge && !event.target.closest('.sh-badge')) hideTooltip(true);
  });

  function createBadge() {
    const badge = document.createElement('button');
    badge.type = 'button';
    badge.className = 'sh-badge';
    badge.setAttribute('aria-label', `Hinweis zum ${VOUCHER_NAME}`);
    badge.setAttribute('aria-describedby', tooltip.id);
    badge.innerHTML = ICON;

    badge.addEventListener('mouseenter', () => showTooltip(badge));
    badge.addEventListener('mouseleave', () => { if (!pinned) hideTooltip(); });
    badge.addEventListener('focus', () => showTooltip(badge));
    badge.addEventListener('blur', () => hideTooltip());
    badge.addEventListener('click', (event) => {
      // Karte ist komplett verlinkt – der Klick aufs Icon soll nicht zur Produktseite führen
      event.preventDefault();
      event.stopPropagation();
      if (pinned && activeBadge === badge) {
        hideTooltip(true);
      } else {
        showTooltip(badge);
        pinned = true;
      }
    });
    return badge;
  }

  /* ---------------------------------------------------------------- */
  /* Gutscheinwelt: Produktkarten                                       */
  /* ---------------------------------------------------------------- */

  function decorateProductCards() {
    document.querySelectorAll('.product-card').forEach((card) => {
      if (card.querySelector('.sh-badge')) return;
      const brand = card.querySelector('.card-info .brand');
      if (!brand || !isExcluded(brand.textContent)) return;
      const host = card.querySelector('.card-image .image-wrapper') || card.querySelector('.card-image');
      if (!host) return;
      card.classList.add('sh-excluded');
      host.appendChild(createBadge());
    });
  }

  function addLegend() {
    if (document.querySelector('.sh-legend') || !document.querySelector('.product-card.sh-excluded')) return;
    const group = document.querySelector('.product-card-grid-section__control-group');
    if (!group) return;
    const legend = document.createElement('div');
    legend.className = 'sh-legend';
    legend.innerHTML = `<span class="sh-legend__icon">${ICON}</span><span>Nicht mit ${VOUCHER_HTML} kaufbar</span>`;
    group.prepend(legend);
  }

  /* ---------------------------------------------------------------- */
  /* Warenkorb & Checkout: Artikel                                      */
  /* ---------------------------------------------------------------- */

  function excludedCartItems() {
    return [...document.querySelectorAll('.cart-line-item')].filter((item) => {
      const brand = item.querySelector('.cart-line-item__brand-name') || item.querySelector('.cart-line-item__name');
      return brand && isExcluded(brand.textContent);
    });
  }

  // Unterhalb dieser Breite ist die Spalte neben dem Bild zu schmal – der Hinweis rutscht unter den Artikel.
  const narrowLayout = window.matchMedia('(max-width: 1199.98px)');

  function decorateCartItems(items) {
    items.forEach((item) => {
      if (item.classList.contains('sh-excluded')) return;
      item.classList.add('sh-excluded');

      const media = item.querySelector('.cart-line-item__image');
      const row = media && media.parentElement;
      if (row) {
        row.classList.add('sh-media-host');
        row.appendChild(createBadge());
      }

      const details = item.querySelector('.cart-line-item__details');
      if (details && row) {
        const note = document.createElement('div');
        note.className = 'sh-note';
        note.innerHTML = `${ICON}<span>${HINT_HTML}</span>`;
        const place = () => {
          note.classList.toggle('sh-note--below', narrowLayout.matches);
          if (narrowLayout.matches) row.after(note);
          else details.appendChild(note);
        };
        place();
        narrowLayout.addEventListener('change', place);
      }
    });
  }

  const textOf = (root, selector) => (root.querySelector(selector)?.textContent || '').trim();
  const itemName = (item) => textOf(item, '.cart-line-item__name');
  const itemPrice = (item) => textOf(item, '.cart-line-item__price .price');

  function focusCartItem(item) {
    item.scrollIntoView({ behavior: 'smooth', block: 'center' });
    const wasFlagged = item.classList.contains('sh-flagged');
    item.classList.remove('sh-flash');
    void item.offsetWidth; // Animation neu starten
    item.classList.add('sh-flagged', 'sh-flash');
    setTimeout(() => {
      item.classList.remove('sh-flash');
      if (!wasFlagged && !document.querySelector('.sh-voucher.is-open')) item.classList.remove('sh-flagged');
    }, 2100);
  }

  function chipsFor(items) {
    const list = document.createElement('ul');
    list.className = 'sh-chips';
    items.forEach((item) => {
      const li = document.createElement('li');
      const chip = document.createElement('button');
      chip.type = 'button';
      chip.className = 'sh-chip';
      chip.innerHTML = `${ICON}<span></span>`;
      chip.lastElementChild.textContent = itemName(item);
      chip.addEventListener('click', () => focusCartItem(item));
      li.appendChild(chip);
      list.appendChild(li);
    });
    return list;
  }

  /* Warenkorb: Zusammenfassung über dem Checkout-Button */
  function addCartSummary(items) {
    const checkout = document.querySelector('.cart-summary__checkout');
    if (!checkout || !items.length || document.querySelector('.sh-summary')) return;

    const box = document.createElement('div');
    box.className = 'sh-summary';
    box.setAttribute('role', 'note');
    box.innerHTML = `
      <span class="sh-summary__icon">${ICON}</span>
      <div class="sh-summary__body">
        <p><strong>${items.length} Artikel</strong> im Warenkorb ${plural(items.length, 'ist', 'sind')} nicht mit dem ${VOUCHER_HTML} kaufbar:</p>
      </div>`;
    box.querySelector('.sh-summary__body').appendChild(chipsFor(items));
    checkout.parentElement.insertBefore(box, checkout);
  }

  /* Details prüfen: Warnung am Gutscheincode-Feld */
  function addVoucherWarning(items) {
    const entry = document.querySelector('.cart-summary__voucher-entry');
    const fieldset = entry && entry.querySelector('.voucher-code-input');
    if (!fieldset || !items.length || document.querySelector('.sh-voucher')) return;

    const count = items.length;
    const total = document.querySelectorAll('.cart-line-item').length;
    const title = count < total
      ? `Nicht alle Artikel sind mit dem ${VOUCHER_HTML} kaufbar`
      : `${plural(count, 'Der Artikel ist', 'Die Artikel sind')} nicht mit dem ${VOUCHER_HTML} kaufbar`;
    const col = document.createElement('div');
    col.className = 'col-12';
    col.innerHTML = `
      <div class="sh-voucher" id="sh-voucher">
        <button type="button" class="sh-voucher__head" aria-expanded="false" aria-controls="sh-voucher-panel">
          <span class="sh-voucher__badge">${ICON}</span>
          <span class="sh-voucher__title"><strong>Achtung:</strong> ${title}</span>
          <span class="sh-voucher__chevron">${CHEVRON}</span>
        </button>
        <div class="sh-voucher__panel" id="sh-voucher-panel" inert>
          <div class="sh-voucher__panel-inner">
            <div class="sh-voucher__content">
              <ul class="sh-voucher__list"></ul>
              <p class="sh-voucher__text">${ICON}<span>${plural(count, HINT_HTML, `Diese Gutscheine sind <strong>nicht</strong> mit dem ${VOUCHER_HTML} kaufbar`)}</span></p>
            </div>
          </div>
        </div>
        <span class="sh-visually-hidden" id="sh-voucher-desc"></span>
      </div>`;

    col.querySelector('#sh-voucher-desc').textContent =
      `${plural(count, HINT_TEXT, `Diese Gutscheine sind nicht mit dem ${VOUCHER_NAME} kaufbar`)}: ${items.map(itemName).join(', ')}`;

    const list = col.querySelector('.sh-voucher__list');
    items.forEach((item) => {
      const li = document.createElement('li');
      const row = document.createElement('button');
      row.type = 'button';
      row.className = 'sh-voucher__item';
      row.innerHTML = `<span class="sh-voucher__thumb"><span class="sh-voucher__thumb-mark">${ICON}</span></span><span class="sh-voucher__name"></span><span class="sh-voucher__price"></span>`;
      const img = item.querySelector('.cart-line-item__image-asset');
      if (img) {
        const thumb = img.cloneNode(true);
        thumb.removeAttribute('class');
        thumb.alt = '';
        row.querySelector('.sh-voucher__thumb').prepend(thumb);
      }
      row.querySelector('.sh-voucher__name').textContent = itemName(item);
      row.querySelector('.sh-voucher__price').textContent = itemPrice(item);
      row.addEventListener('click', () => focusCartItem(item));
      row.addEventListener('mouseenter', () => item.classList.add('sh-flash'));
      row.addEventListener('mouseleave', () => item.classList.remove('sh-flash'));
      li.appendChild(row);
      list.appendChild(li);
    });

    fieldset.closest('.col-12').after(col);

    const box = col.querySelector('.sh-voucher');
    const head = box.querySelector('.sh-voucher__head');
    const panel = box.querySelector('.sh-voucher__panel');
    const inputs = [...fieldset.querySelectorAll('input')];
    let manuallyOpened = false;

    inputs.forEach((input) => {
      const ids = (input.getAttribute('aria-describedby') || '').split(' ').filter(Boolean);
      input.setAttribute('aria-describedby', [...ids, 'sh-voucher-desc'].join(' '));
    });

    const setOpen = (open) => {
      box.classList.toggle('is-open', open);
      head.setAttribute('aria-expanded', String(open));
      panel.inert = !open;
      items.forEach((item) => item.classList.toggle('sh-flagged', open));
    };

    const hasCode = () => inputs.some((input) => input.value.trim() !== '');

    // Sobald der Kunde einen Gutscheincode eingeben will, klappt die Warnung auf
    fieldset.addEventListener('focusin', () => setOpen(true));
    fieldset.addEventListener('input', () => setOpen(true));
    fieldset.addEventListener('focusout', () => {
      setTimeout(() => {
        const stillInside = box.contains(document.activeElement) || fieldset.contains(document.activeElement);
        if (!stillInside && !hasCode() && !manuallyOpened) setOpen(false);
      }, 120);
    });

    head.addEventListener('click', () => {
      const open = !box.classList.contains('is-open');
      manuallyOpened = open;
      setOpen(open);
    });

    const redeem = entry.querySelector('.cart-summary__voucher-redeem');
    if (redeem) {
      redeem.addEventListener('click', () => {
        setOpen(true);
        box.classList.remove('is-nudged');
        void box.offsetWidth;
        box.classList.add('is-nudged');
      });
    }
    box.addEventListener('animationend', () => box.classList.remove('is-nudged'));
  }

  /* ---------------------------------------------------------------- */

  function init() {
    decorateProductCards();
    addLegend();
    const items = excludedCartItems();
    decorateCartItems(items);
    addCartSummary(items);
    addVoucherWarning(items);
  }

  init();

  // nachgeladene Karten („Mehr laden“) ebenfalls markieren
  let pending = 0;
  new MutationObserver(() => {
    cancelAnimationFrame(pending);
    pending = requestAnimationFrame(() => { decorateProductCards(); addLegend(); });
  }).observe(document.body, { childList: true, subtree: true });
})();
