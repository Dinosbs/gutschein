#!/usr/bin/env python3
"""Baut die Pitch-Präsentation als eigenständige, offline-fähige HTML-Dateien.

    python3 build.py

    index.html                  allgemeine Fassung
    pitches/<slug>/index.html   eine Fassung je Eintrag in data/pitches.json
                                (online: https://dinosbs.github.io/pitch/<slug>/)

Quellen: src/template.html + src/style.css + src/app.js + src/icons.svg + data/*.json + assets/*
Design: INCENT-Relaunch (github.com/Dinosbs/incentde). Die Shop-Mockups sind dem echten
Vorteilsportal (vorteile.net) nachgebaut. Nur Standardbibliothek, keine Abhängigkeiten.
"""
from __future__ import annotations

import base64
import html
import json
import re
import shutil
import unicodedata
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC, DATA, ASSETS = ROOT / "src", ROOT / "data", ROOT / "assets"

RATE = 10                     # Beteiligung an jeder Bestellung in Prozent (je Pitch überschreibbar)
SNAPSHOT_DATE = "01.11.2026"  # Stand der Preise aus der Shop-Speicherung
RESERVED = {"assets", "data", "src", "tools", "screenshots", "pitches", "favicon.png"}

# Farben im Gestalter (Buttonfarbe = Akzentfarbe des Portals, wie --btn auf vorteile.net)
BTN_COLORS = [
    ("#1c87b8", "Portal-Blau"), ("#c0746a", "Rosé"), ("#a3245a", "Beere"), ("#a7856b", "Nude"),
    ("#5f8a72", "Salbei"), ("#7e6aa8", "Lavendel"), ("#222222", "Schwarz"),
]
NAV_COLORS = [("#ffffff", "Weiß"), ("#f8eeea", "Puder"), ("#f4efe8", "Creme"), ("#1d1b1e", "Schwarz")]
PRESETS = {"blau": "#1c87b8", "rose": "#c0746a", "rosé": "#c0746a", "beere": "#a3245a", "nude": "#a7856b",
           "salbei": "#5f8a72", "lavendel": "#7e6aa8", "schwarz": "#222222", "weiss": "#ffffff", "weiß": "#ffffff",
           "puder": "#f8eeea", "creme": "#f4efe8"}

DEAL_LOGOS = {
    "Shiseido": "shiseido", "NARS": "nars", "ghd - good hair day": "ghd-good-hair-day",
    "Rituals Cosmetics": "rituals", "Doctor Mi": "doctor-mi", "The Female Company": "the-female-company",
    "Yves Rocher": "yves-rocher", "LAYZIN": "layzin-skin", "lavera": "lavera", "KLIER": "klier",
    "Philips": "philips",
}
LUX = ["dior", "lancome", "chloe", "tom-ford", "yves-saint-laurent", "giorgio-armani", "hermes", "shiseido",
       "nars", "clinique", "rituals"]
DEALS_SHOWN = 8

CATEGORIES = [  # Reihenfolge = Priorität beim Zuordnen
    ("Düfte", r"^(EdP|EdT|Eau de|Deo|Deodorant|Luxe Body Mist|Boss Bottled)"),
    ("Haar-Styling", r"(Haartrockner|Föhn|Lockenstab|Glätt|Warmluftbürste|Welleneisen|Styler|Haarbürste|Stylingbürste)"),
    ("Beauty-Tech", r"(LED|IPL|FaceTite|Mikrodermabrasion|Gesichtsreinigungsbürste|Porenreiniger|Gesichtssauna|Hornhautentferner|Damenrasierer|Kosmetikspiegel|Selfie-Spiegel|Manikür|Aging)"),
    ("Pflege & Geschenksets", r"(Geschenkset|Giftset|gift set|Advent|Cream|Serum|Körperöl|Gesichtspflegeset|Reinigungsbalsam|Aquasource|Benefiance)"),
    ("Wellness & Self-Care", r"(Massage|Fußsprudelbad|Bademantel|tuch|Duftkerze|Duftzerstäuber|Heiz|Fußwärmer|Box|Fascia|Infrarot|Gun)"),
    ("Health & Grooming", r"(zahnbürste|Bürstenköpfe|Munddusche|Blutdruck|Thermometer|Waage|Insekten|Kartuschen|Zahnputzbecher|Seifenspender|Rasierer|Haarschneider|Trimmer|Scherkopf|Schleifscheiben)"),
]


# --------------------------------------------------------------- helpers
def esc(text) -> str:
    return html.escape(str(text), quote=True)


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text).replace("\xa0", " ")).strip()


MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp",
        ".svg": "image/svg+xml", ".woff2": "font/woff2"}


def data_uri(path: Path) -> str:
    return f"data:{MIME[path.suffix.lower()]};base64," + base64.b64encode(path.read_bytes()).decode()


def eur(value: float) -> str:
    value = float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    s = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s}&nbsp;€"


def nice_title(title: str) -> str:
    return re.sub(r'"([^"]*)"', "„\\1“", title)


def short_title(title: str) -> str:
    return re.sub(r'^(EdP|EdT|EDP)\s+', "", title).replace('"', "")


def nice_brand(brand: str) -> str:
    """Markenname in normaler Schreibweise für Fließtext (Mitteilungen)."""
    special = {"SILK'N": "Silk'n", "LANCÔME": "Lancôme", "HERMES": "Hermès", "PACO RABANNE": "Paco Rabanne",
               "TOM FORD": "Tom Ford", "YVES SAINT LAURENT": "YSL", "GIORGIO ARMANI": "Armani", "BABYLISS": "BaByliss"}
    return special.get(brand, brand.title() if brand.isupper() else brand)


def icon(name: str, cls: str = "i") -> str:
    return f'<svg class="{cls}" aria-hidden="true"><use href="#i-{name}"/></svg>'


# --------------------------------------------------------------- data
catalog = json.loads((DATA / "catalog.json").read_text(encoding="utf-8"))
deals = {d["title"]: d for d in json.loads((DATA / "deals.json").read_text(encoding="utf-8"))}
brands = json.loads((DATA / "brands.json").read_text(encoding="utf-8"))
sel = json.loads((DATA / "selection.json").read_text(encoding="utf-8"))
by_key = {(norm(p["brand"]), norm(p["title"])): p for p in catalog}
brand_names = {b["slug"]: b["name"] for b in brands}

used_products: set[str] = set()
used_deals: set[str] = set()
used_logos: set[str] = set()


def product(pair) -> dict:
    p = by_key[(norm(pair[0]), norm(pair[1]))]
    used_products.add(p["slug"])
    return p


def find(brand: str, which: str = "hero", index: int = 0) -> dict:
    return product([x for x in sel[which] if x[0] == brand][index])


def deal(title: str) -> dict:
    d = deals[title]
    used_deals.add(d["slug"])
    return d


def logo(slug: str, label: str = "") -> str:
    used_logos.add(slug)
    aria = f' role="img" aria-label="{esc(label)}"' if label else ""
    return f'<span class="logo lg-{slug}"{aria}></span>'


discounts = [(p["uvp"] - p["price"]) / p["uvp"] for p in catalog if p["uvp"]]
AVG_DISCOUNT = sum(discounts) / len(discounts)


# --------------------------------------------------------------- vorteile.net-Bausteine
def vp_logo() -> str:
    """Logo-Platz im Portal-Header: INCENT (Standard), Schriftzug mit Namen oder eigenes Logo."""
    return ('<span class="vp__logo"><span class="vp__logo-incent" role="img" aria-label="INCENT"></span>'
            '<span class="vp__logo-name" data-bind="name">Dein Name</span>'
            '<img class="vp__logo-custom" data-logo-img alt="" src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="></span>')


def vp_product(p: dict) -> str:
    off = f"<em>-{p['discount']}%</em>" if p["discount"] else ""
    old = f"<s>{eur(p['uvp'])}</s>" if p["uvp"] else "<s>&nbsp;</s>"
    return (f'<span class="vp-product" data-product data-brand="{esc(nice_brand(p["brand"]))}" '
            f'data-title="{esc(short_title(p["title"]))}" data-price="{p["price"]:.2f}" data-img="pi-{p["slug"]}">'
            f'{icon("heart", "i vp-product__fav")}'
            f'<span class="pimg pi-{p["slug"]}" role="img" aria-label="{esc(p["brand"] + " " + p["title"])}"></span>'
            f'<span class="vp-product__meta"><b>{esc(p["brand"])}</b><span>{esc(nice_title(p["title"]))}</span></span>'
            f'<span class="vp-product__cart">{icon("bag")}</span>'
            f'<span class="vp-product__price"><strong>{eur(p["price"])}</strong>{off}</span>{old}</span>')


def vp_deal(title: str, text: str | None = None) -> str:
    d = deal(title)
    m = re.match(r"(bis zu|über)?\s*(.*)", d["discount"] or "")
    pre = "<small>bis<br>zu</small>" if m.group(1) == "bis zu" else (f"<small>{esc(m.group(1))}</small>" if m.group(1) else "")
    slug = DEAL_LOGOS.get(title)
    logo_html = logo(slug, title) if slug else f'<b class="vp-deal__logo-text">{esc(title)}</b>'
    return (f'<span class="vp-deal"><span class="dimg di-{d["slug"]}"></span>'
            f'<span class="vp-deal__logo">{logo_html}</span>'
            f'<span class="vp-deal__badge">{pre}{esc(m.group(2).replace(" ", ""))}</span>'
            f'<span class="vp-deal__info"><b>{esc(title)}</b><span>{esc(text or d["text"] or "")}</span></span></span>')


VP_CATS = ('<i>Highlights</i><i>NEU</i><i class="is-on">Health &amp; Beauty</i><i>Düfte</i><i>Skincare</i>'
           '<i>Beauty-Tech</i><i>Haare</i><i>Wellness</i><i class="is-on">Alle Kategorien +</i>')


def vp_portal() -> str:
    products = [find("LANCÔME"), find("DIOR"), find("SILK'N"), find("RITUALS")]
    return f"""<div class="vp-frame">
  <div class="vp" aria-hidden="true">
    <div class="vp__bar"><span class="vp__dots"><i></i><i></i><i></i></span><span class="vp__url">{icon("lock")}<span><span data-bind="slug">deinname</span>.vorteile.net/de/dashboard</span></span><span class="vp__bar-end"></span></div>
    <div class="vp__header">
      <div class="vp__top">{vp_logo()}<span class="vp__search">Suchen{icon("search")}</span><span class="vp__account"><b>Community-Shop</b><small data-bind="name">Dein Name</small></span></div>
      <div class="vp__nav"><span class="vp__cats">{VP_CATS}</span><span class="vp__icons">{icon("heart")}{icon("user")}<span class="vp__cart">{icon("bag")}<b>1</b></span></span></div>
    </div>
    <div class="vp__stage">
      <span class="vp__bg vp__bg--image"></span><span class="vp__bg vp__bg--solid"></span><span class="vp__bg vp__bg--gradient"></span><span class="vp__fade"></span>
      <div class="vp__head"><strong>Best of Health &amp; Beauty</strong><em>Exklusive Angebote</em></div>
      <div class="vp__grid">{vp_deal("Shiseido")}{vp_deal("NARS")}</div>
      <div class="vp__head vp__head--shop"><strong>Besonders beliebt im Vorteils-Shop</strong><em>Im Trend</em></div>
      <div class="vp__products">{"".join(vp_product(p) for p in products)}</div>
    </div>
  </div>
</div>"""


def vpm_phone() -> str:
    products = [find("LANCÔME"), find("SILK'N")]
    return f"""<div class="phone" aria-hidden="true">
  <div class="phone__screen">
    <div class="vpm">
      <div class="vpm__status"><span>9:41</span><span class="vpm__island"></span><span class="vpm__sig"><i></i><i></i><i></i></span></div>
      <div class="vpm__header">{vp_logo()}<span class="vpm__icons">{icon("search")}{icon("heart")}<span class="vp__cart">{icon("bag")}<b>1</b></span></span></div>
      <div class="vpm__cats"><i class="is-on">Health &amp; Beauty</i><i>Düfte</i><i>Skincare</i><i>Beauty-Tech</i></div>
      <div class="vpm__stage">
        <span class="vp__bg vp__bg--image"></span><span class="vp__bg vp__bg--solid"></span><span class="vp__bg vp__bg--gradient"></span><span class="vp__fade"></span>
        <div class="vp__head"><strong>Best of Health &amp; Beauty</strong><em>Exklusive Angebote</em></div>
        {vp_deal("Shiseido")}
        <div class="vpm__products">{"".join(vp_product(p) for p in products)}</div>
      </div>
    </div>
  </div>
</div>"""


# --------------------------------------------------------------- Folien-Bausteine
def frag_winwin(rate: float) -> str:
    p = product(sel["margin"][0])
    save = p["uvp"] - p["price"]
    return f"""
      <div class="winwin__card vreal" data-anim="pop"><div class="tilt" data-tilt>{vp_product(p)}</div></div>
      <div class="winwin__flow">
        <div class="ww ww--old" data-anim style="--d:.55s"><span class="ww__label">Regulär</span><span class="ww__value"><s>{eur(p['uvp'])}</s></span></div>
        <span class="ww__arrow" data-anim="pop" style="--d:.9s" aria-hidden="true">{icon("arrow-right")}</span>
        <div class="ww" data-anim style="--d:1.1s"><span class="ww__label">In Deinem Shop</span><span class="ww__value" data-countto="{p['price']:.2f}" data-from="{p['uvp']:.2f}" data-delay="1300">{eur(p['price'])}</span></div>
        <div class="ww ww--community" data-anim style="--d:1.6s"><span class="ww__label">Deine Community spart</span><span class="ww__value" data-countto="{save:.2f}" data-delay="1800">{eur(save)}</span><span class="ww__note">−{p['discount']}&nbsp;% gegenüber regulär</span></div>
        <div class="ww ww--you" data-anim style="--d:2.1s"><span class="ww__label">Du verdienst</span><span class="ww__value" data-countto="{p['price'] * rate:.2f}" data-delay="2300">{eur(p['price'] * rate)}</span><span class="ww__note">{rate * 100:.0f}&nbsp;% Beteiligung – ganz automatisch</span></div>
      </div>"""


def swatches(colors, kind: str) -> str:
    return "\n".join(
        f'<button type="button" class="swatch{" is-on" if i == 0 else ""}" style="--c:{c}" data-{kind}="{c}" '
        f'role="radio" aria-checked="{"true" if i == 0 else "false"}" aria-label="{esc(label)}"></button>'
        for i, (c, label) in enumerate(colors))


def frag_margin_cards(rate: float) -> str:
    out = []
    for pair in sel["margin"]:
        p = product(pair)
        out.append(f"""<article class="mcard" data-anim="flip">
  <div class="mcard__product vreal">{vp_product(p)}</div>
  <div class="mcard__calc">
    <dl class="mcard__rows">
      <div><dt>Regulär</dt><dd><s>{eur(p['uvp'])}</s></dd></div>
      <div><dt>In Deinem Shop</dt><dd>{eur(p['price'])}</dd></div>
      <div class="is-save"><dt>Community spart</dt><dd>{eur(p['uvp'] - p['price'])}</dd></div>
    </dl>
    <div class="mcard__earn"><span>Du verdienst</span><strong data-countto="{p['price'] * rate:.2f}">{eur(p['price'] * rate)}</strong></div>
  </div>
</article>""")
    return "\n".join(out)


def frag_punch(rate: float) -> str:
    p = product(sel["margin"][1])  # LED-Maske
    return (f'Schon <strong>10 verkaufte</strong> LED-Masken von {esc(nice_brand(p["brand"]))} bringen Dir '
            f'<span class="grad-text">{eur(p["price"] * 10 * rate)}</span> – ohne einen Handgriff.')


def frag_lux() -> str:
    return "\n".join(f'<li data-anim="pop">{logo(slug, brand_names.get(slug, slug))}</li>' for slug in LUX)


def frag_categories() -> str:
    counts = {name: 0 for name, _ in CATEGORIES}
    for p in catalog:
        for name, rx in CATEGORIES:
            if re.search(rx, p["title"], re.I):
                counts[name] += 1
                break
    return "\n".join(f'<div><dt>{esc(name)}</dt><dd><span data-count="{n}">{n}</span></dd></div>'
                     for name, n in counts.items())


def frag_logos() -> str:
    rest = [b for b in brands if b["slug"] not in LUX]
    tiles = "".join(f"<li>{logo(b['slug'], b['name'])}</li>" for b in rest)
    dup = "".join(f"<li>{logo(b['slug'])}</li>" for b in rest)
    return (f'<div class="marquee" style="--dur:140s"><ul class="marquee__track">{tiles}</ul>'
            f'<ul class="marquee__track" aria-hidden="true">{dup}</ul></div>')


def frag_edit_tabs() -> str:
    return "\n".join(
        f'<button type="button" class="tab" role="tab" id="tab-{e["id"]}" aria-controls="edit-{e["id"]}" '
        f'aria-selected="{"true" if i == 0 else "false"}"{"" if i == 0 else " tabindex=\"-1\""}>{esc(e["name"])}'
        f'<span>{len(e["items"])}</span></button>'
        for i, e in enumerate(sel["edits"]))


def frag_edit_panels(rate: float) -> str:
    out = []
    for i, e in enumerate(sel["edits"]):
        cards = "".join(
            f'<div class="ecard vreal">{vp_product(p)}<p class="ecard__earn">+&nbsp;{eur(p["price"] * rate)} für Dich</p></div>'
            for p in (product(x) for x in e["items"]))
        hidden = "" if i == 0 else " hidden"
        out.append(f"""<div class="edit" role="tabpanel" id="edit-{e['id']}" aria-labelledby="tab-{e['id']}"{hidden}>
  <div class="edit__head"><p class="edit__claim">{esc(e['claim'])}</p>
    <div class="edit__arrows"><button type="button" data-rail="-1" aria-label="Zurück">{icon("chevron-left")}</button><button type="button" data-rail="1" aria-label="Weiter">{icon("chevron-right")}</button></div></div>
  <div class="rail" tabindex="0" aria-label="{esc(e['name'])}">{cards}</div>
</div>""")
    return "\n".join(out)


def frag_deals() -> str:
    return "\n".join(f'<div class="vdeal vreal" data-anim="flip">{vp_deal(t, txt)}</div>' for t, txt in sel["deals"][:DEALS_SHOWN])


def frag_story_product() -> str:
    p = product(sel["edits"][4]["items"][1])  # Rituals Classic Advent Calendar
    return (f'<div class="story__product"><span class="pimg pi-{p["slug"]}"></span></div>'
            f'<div class="story__sticker"><span>Nur in meinem Shop</span><strong>-{p["discount"]}&nbsp;%</strong></div>'
            f'<p class="story__text">Der Adventskalender ist da ✨<br>Link in Bio!</p>')


def frag_lockscreen() -> str:
    """iPhone-Sperrbildschirm (iOS-Stil). Mitteilungen schiebt app.js fortlaufend von unten ein."""
    return f"""<div class="ios" aria-hidden="true">
  <div class="ios__screen">
    <div class="ios__wall"><i></i><i></i><i></i></div>
    <div class="ios__status"><span class="ios__bars"><i></i><i></i><i></i><i></i></span><span class="ios__island"></span><span class="ios__right"><b>5G</b><span class="ios__bat"></span></span></div>
    <div class="ios__lock">{icon("lock")}</div>
    <p class="ios__date" data-ios-date>Montag, 2. November</p>
    <p class="ios__time" data-ios-time>23:41</p>
    <div class="ios__widgets">
      <div class="ios__widget ios__widget--wide"><span class="ios__wlabel">{icon("bag")}<span data-bind="app">Community-Shop</span> · <span data-ios-month>November</span></span><b data-ios-total>0,00 €</b></div>
      <div class="ios__widget ios__widget--ring"><svg viewBox="0 0 44 44"><circle cx="22" cy="22" r="18"/><circle class="ios__ring" cx="22" cy="22" r="18" pathLength="100" data-ios-ring/></svg><b data-ios-count>0</b></div>
    </div>
    <ul class="ios__notes" data-ios-notes></ul>
    <div class="ios__bottom"><span class="ios__btn"><svg viewBox="0 0 24 24"><path d="M9 2h6l-1 6h-4zM10 8h4v12a2 2 0 0 1-4 0z"/></svg></span><span class="ios__btn"><svg viewBox="0 0 24 24"><path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/></svg></span></div>
    <span class="ios__home"></span>
  </div>
</div>"""


# --------------------------------------------------------------- CSS-Kopf (Schriften + Bilder, jedes nur einmal)
def css_head() -> str:
    fonts = ASSETS / "fonts"
    parts = []
    for weight, style, file in [(400, "normal", "400"), (500, "normal", "500"), (600, "normal", "600"),
                                (600, "italic", "600-italic"), (700, "normal", "700"), (800, "normal", "800")]:
        parts.append(f'@font-face{{font-family:"Barlow Semi Condensed";font-weight:{weight};font-style:{style};'
                     f'font-display:swap;src:url({data_uri(fonts / f"barlow-semi-condensed-{file}.woff2")}) format("woff2")}}')
    ui = ASSETS / "ui"
    parts.append(f".vp__logo-incent{{background-image:url({data_uri(ui / 'incent-logo-dark.png')})}}")
    parts.append(f".vp-theme[data-nav-tone=\"dark\"] .vp__logo-incent{{background-image:url({data_uri(ui / 'incent-logo-white.png')})}}")
    parts.append(f".vp__bg--image,.bg-opt__thumb--image{{background-image:url({data_uri(ui / 'bg-health-beauty.jpg')})}}")
    parts += [f".pi-{s}{{background-image:url({data_uri(ASSETS / 'products' / f'{s}.jpg')})}}" for s in sorted(used_products)]
    parts += [f".di-{s}{{background-image:url({data_uri(ASSETS / 'deals' / f'{s}.jpg')})}}" for s in sorted(used_deals)]
    parts += [f".lg-{s}{{background-image:url({data_uri(ASSETS / 'logos' / f'{s}.png')})}}" for s in sorted(used_logos)
              if (ASSETS / "logos" / f"{s}.png").exists()]
    return "\n".join(parts) + "\n"


# --------------------------------------------------------------- Seite bauen
def render(pitch: dict | None) -> str:
    pitch = pitch or {}
    rate = float(pitch.get("beteiligung", RATE)) / 100
    name = (pitch.get("name") or "").strip()
    page = (SRC / "template.html").read_text(encoding="utf-8")
    poss = (name + ("’" if re.search(r"[sxzß]$", name, re.I) else "s")) if name else ""
    fragments = {
        "icons": (SRC / "icons.svg").read_text(encoding="utf-8"),
        "page_title": esc(f"{poss} Beauty-Shop · INCENT Community-Shop" if name else "Dein eigener Beauty-Shop · INCENT Community-Shop"),
        "vp_hero": vp_portal(), "vpm_phone": vpm_phone(), "vpm_phone_2": vpm_phone(), "winwin": frag_winwin(rate),
        "swatches_btn": swatches(BTN_COLORS, "btn"), "swatches_nav": swatches(NAV_COLORS, "nav"),
        "margin_cards": frag_margin_cards(rate), "punch": frag_punch(rate), "lux": frag_lux(),
        "categories": frag_categories(), "logos": frag_logos(), "edit_tabs": frag_edit_tabs(),
        "edit_panels": frag_edit_panels(rate), "deals": frag_deals(), "story_product": frag_story_product(),
        "lockscreen": frag_lockscreen(), "snapshot_date": SNAPSHOT_DATE,
    }
    for key, value in fragments.items():
        marker = f"<!--@{key}-->"
        if marker not in page:
            raise SystemExit(f"Marker fehlt im Template: {marker}")
        page = page.replace(marker, value)
    page = page.replace("<!--@rate_text-->", f"{rate * 100:.0f}")
    page = re.sub(r"\{\{ui:([a-z0-9-]+)\}\}", lambda m: data_uri(ASSETS / "ui" / f"{m.group(1)}.png"), page)

    logo_uri = None
    if pitch.get("logo"):
        logo_uri = data_uri(DATA / "pitches" / pitch["logo"])
    data = {
        "rate": rate * 100,
        "defaults": {"followers": 100_000, "conv": 0.5, "basket": 75,
                     "btn": BTN_COLORS[0][0], "nav": NAV_COLORS[0][0]},
        "pitch": {"name": name, "farbe": pitch.get("farbe"), "nav": pitch.get("nav"),
                  "hintergrund": pitch.get("hintergrund"), "logo": logo_uri, "slug": pitch.get("slug")},
        "avgDiscount": round(AVG_DISCOUNT, 4),
        "presets": PRESETS,
    }
    page = page.replace("/*@CSS*/", css_head() + (SRC / "style.css").read_text(encoding="utf-8"), 1)
    page = page.replace("/*@DATA*/", "window.SHOP_DATA = " + json.dumps(data, ensure_ascii=False) + ";", 1)
    page = page.replace("/*@JS*/", (SRC / "app.js").read_text(encoding="utf-8"), 1)
    left = re.findall(r"<!--@\w+-->|\{\{[a-z]+:[^}]+\}\}", page)
    if left:
        raise SystemExit(f"Nicht ersetzt: {left}")
    return page


def main() -> None:
    out = ROOT / "index.html"
    out.write_text(render(None), encoding="utf-8")
    print(f"index.html  {out.stat().st_size / 1e6:.1f} MB")

    cfg = json.loads((DATA / "pitches.json").read_text(encoding="utf-8"))
    target = ROOT / "pitches"
    if target.exists():
        shutil.rmtree(target)
    for pitch in cfg.get("pitches", []):
        slug = pitch.get("slug", "")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,40}", slug) or slug in RESERVED:
            raise SystemExit(f"Ungültiger slug in data/pitches.json: {slug!r} (nur a–z, 0–9, Bindestrich)")
        path = target / slug / "index.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(pitch), encoding="utf-8")
        print(f"pitches/{slug}/index.html  {path.stat().st_size / 1e6:.1f} MB  →  /pitch/{slug}/")


if __name__ == "__main__":
    main()
