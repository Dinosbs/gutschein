#!/usr/bin/env python3
"""Baut die Pitch-Seite als eine einzige, offline-fähige HTML-Datei.

    python3 build.py

src/template.html + src/style.css + src/app.js + data/*.json + assets/*
    ->  index.html   (alle Bilder und Schriften eingebettet)

Nur Standardbibliothek, keine Abhängigkeiten.
"""
from __future__ import annotations

import base64
import html
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC, DATA, ASSETS = ROOT / "src", ROOT / "data", ROOT / "assets"

DEFAULT_RATE = 0.10          # Provision, die beim ersten Öffnen eingestellt ist (Regler 5–20 %)
SNAPSHOT_DATE = "01.11.2026"  # Stand der Preise aus der Shop-Speicherung
CONTACT_MAIL = ""             # Empfänger für „Lass uns sprechen“ (leer = Mail ohne Empfänger)

THEMES = {
    "rose":  {"label": "Rosé",     "accent": "#B4705F", "soft": "#F6E6E0", "bg": "#FFFBF9", "ink": "#2A1F1D"},
    "nude":  {"label": "Nude",     "accent": "#97765C", "soft": "#F0E7DD", "bg": "#FDFAF6", "ink": "#2B241F"},
    "sage":  {"label": "Salbei",   "accent": "#5F7D68", "soft": "#E5EDE7", "bg": "#FAFCFA", "ink": "#1F2621"},
    "lilac": {"label": "Lavendel", "accent": "#7D6AA6", "soft": "#ECE8F5", "bg": "#FCFBFE", "ink": "#211D2B"},
    "noir":  {"label": "Noir",     "accent": "#1E1A1A", "soft": "#ECE9E6", "bg": "#FFFFFF", "ink": "#141212"},
}

DEAL_LOGOS = {
    "Shiseido": "shiseido", "NARS": "nars", "ghd - good hair day": "ghd-good-hair-day",
    "Rituals Cosmetics": "rituals", "Doctor Mi": "doctor-mi", "The Female Company": "the-female-company",
    "Yves Rocher": "yves-rocher", "LAYZIN": "layzin-skin", "lavera": "lavera", "KLIER": "klier",
    "Philips": "philips",
}

CATEGORIES = [  # Reihenfolge = Priorität beim Zuordnen
    ("Düfte", r"^(EdP|EdT|Eau de|Deo|Deodorant|Luxe Body Mist|Boss Bottled)"),
    ("Haar-Styling", r"(Haartrockner|Föhn|Lockenstab|Glätt|Warmluftbürste|Welleneisen|Styler|Haarbürste|Stylingbürste)"),
    ("Beauty-Tech", r"(LED|IPL|FaceTite|Mikrodermabrasion|Gesichtsreinigungsbürste|Porenreiniger|Gesichtssauna|Hornhautentferner|Damenrasierer|Kosmetikspiegel|Selfie-Spiegel|Manikür|Aging)"),
    ("Pflege & Geschenksets", r"(Geschenkset|Giftset|gift set|Advent|Cream|Serum|Körperöl|Gesichtspflegeset|Reinigungsbalsam|Aquasource|Benefiance)"),
    ("Wellness & Self-Care", r"(Massage|Fußsprudelbad|Bademantel|tuch|Duftkerze|Duftzerstäuber|Heiz|Fußwärmer|Box|Fascia|Infrarot|Gun)"),
    ("Health & Grooming", r"(zahnbürste|Bürstenköpfe|Munddusche|Blutdruck|Thermometer|Waage|Insekten|Kartuschen|Zahnputzbecher|Seifenspender|Rasierer|Haarschneider|Trimmer|Scherkopf|Schleifscheiben)"),
]

SECTIONS = [("start", "Start"), ("idee", "Die Idee"), ("look", "Dein Look"), ("marge", "Verdienst"),
            ("rechner", "Rechner"), ("marken", "Marken"), ("edits", "Edits"), ("deals", "Partner-Deals"),
            ("reichweite", "Reichweite"), ("service", "Rundum-Service"), ("los", "Los geht’s")]


# --------------------------------------------------------------- helpers
def esc(text) -> str:
    return html.escape(str(text), quote=True)


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text).replace("\xa0", " ")).strip()


_uri_cache: dict[Path, str] = {}


def data_uri(path: Path) -> str:
    if path not in _uri_cache:
        mime = {".jpg": "image/jpeg", ".png": "image/png", ".woff2": "font/woff2"}[path.suffix]
        _uri_cache[path] = f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()
    return _uri_cache[path]


def eur(value: float) -> str:
    s = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s}&nbsp;€"


def nice_title(title: str) -> str:
    """„Deutsche“ Anführungszeichen statt "gerader"."""
    return re.sub(r'"([^"]*)"', "„\\1“", title)


def nice_brand(brand: str) -> str:
    return {"HERMES": "HERMÈS", "Clinique": "CLINIQUE"}.get(brand, brand)


def earn(price: float) -> str:
    return f'<span data-earn="{price:.2f}">{eur(price * DEFAULT_RATE)}</span>'


# --------------------------------------------------------------- data
catalog = json.loads((DATA / "catalog.json").read_text(encoding="utf-8"))
deals = {d["title"]: d for d in json.loads((DATA / "deals.json").read_text(encoding="utf-8"))}
brands = json.loads((DATA / "brands.json").read_text(encoding="utf-8"))
sel = json.loads((DATA / "selection.json").read_text(encoding="utf-8"))
by_key = {(norm(p["brand"]), norm(p["title"])): p for p in catalog}


def product(pair) -> dict:
    p = by_key[(norm(pair[0]), norm(pair[1]))]
    return {**p, "img": data_uri(ASSETS / "products" / f"{p['slug']}.jpg"),
            "alt": f"{nice_brand(p['brand'])} {p['title']}"}


discounts = [(p["uvp"] - p["price"]) / p["uvp"] for p in catalog if p["uvp"]]
AVG_DISCOUNT = sum(discounts) / len(discounts)


# --------------------------------------------------------------- fragments
def frag_dots() -> str:
    return "\n".join(f'<a href="#{i}" data-dot="{i}"><span>{esc(t)}</span></a>' for i, t in SECTIONS)


def frag_hero_floaters() -> str:
    spots = ["f1", "f2", "f3"]
    picks = [product(x) for x in sel["hero"] if x[0] in ("LANCÔME", "DIOR", "SILK'N")][:3]
    return "\n".join(
        f'<figure class="floater floater--{s}"><img src="{p["img"]}" alt="{esc(p["alt"])}">'
        f'<figcaption><b>−{p["discount"]}&nbsp;%</b></figcaption></figure>'
        for s, p in zip(spots, picks))


def mini_card(p: dict, cls: str) -> str:
    return (f'<div class="{cls}"><div class="{cls}-img"><img src="{p["img"]}" alt="{esc(p["alt"])}">'
            f'<span class="{cls}-off">−{p["discount"]}&nbsp;%</span></div>'
            f'<span class="{cls}-brand">{esc(nice_brand(p["brand"]))}</span>'
            f'<span class="{cls}-price"><b>{eur(p["price"])}</b> <s>{eur(p["uvp"])}</s></span></div>')


def frag_phone_products() -> str:
    keys = [("LANCÔME",), ("DIOR",), ("SILK'N",), ("RITUALS",)]
    picks = [product(next(x for x in sel["hero"] if x[0] == k[0])) for k in keys]
    return "\n".join(mini_card(p, "pm") for p in picks)


def frag_browser_products() -> str:
    names = ["SHISEIDO", "CHLOÉ", "SILK'N", "RITUALS"]
    picks = [product(next(x for x in sel["hero"] if x[0] == n)) for n in names]
    notes = {0: "Mein Holy Grail"}
    out = []
    for i, p in enumerate(picks):
        note = f'<span class="bm-note">{notes[i]}</span>' if i in notes else ""
        out.append(mini_card(p, "bm").replace('<span class="bm-off">', note + '<span class="bm-off">', 1))
    return "\n".join(out)


def frag_winwin() -> str:
    p = product(sel["margin"][0])
    save = p["uvp"] - p["price"]
    return f"""
      <div class="winwin__product"><img src="{p['img']}" alt="{esc(p['alt'])}"><div><span>{esc(nice_brand(p['brand']))}</span><strong>{esc(nice_title(p['title']))}</strong></div></div>
      <div class="winwin__flow">
        <div class="ww"><span class="ww__label">Regulär</span><s class="ww__value">{eur(p['uvp'])}</s></div>
        <div class="ww"><span class="ww__label">In deinem Shop</span><span class="ww__value">{eur(p['price'])}</span></div>
        <div class="ww ww--community"><span class="ww__label">Deine Community spart</span><span class="ww__value">{eur(save)}</span></div>
        <div class="ww ww--you"><span class="ww__label">Du verdienst <output data-out="rate">{DEFAULT_RATE*100:.0f}&nbsp;%</output></span><span class="ww__value">{earn(p['price'])}</span></div>
      </div>"""


def frag_swatches() -> str:
    out = []
    for i, (key, t) in enumerate(THEMES.items()):
        checked = " checked" if i == 0 else ""
        out.append(f'<label class="swatch" style="--sw:{t["accent"]};--sw2:{t["soft"]}">'
                   f'<input type="radio" name="theme" value="{key}"{checked}><span aria-hidden="true"></span>'
                   f'<em>{esc(t["label"])}</em></label>')
    return "\n".join(out)


def frag_motifs() -> str:
    out = []
    for i, title in enumerate(sel["customizer_motifs"]):
        slug = deals[title]["slug"]
        checked = " checked" if i == 0 else ""
        out.append(f'<label class="motif"><input type="radio" name="motif" value="{slug}"{checked}>'
                   f'<span class="motif__img" style="background-image:var(--motif-{slug})"></span>'
                   f'<em class="sr">{esc(title)}</em></label>')
    return "\n".join(out)


def product_card(p: dict, extra_cls: str = "") -> str:
    uvp = f"<s>{eur(p['uvp'])}</s>" if p["uvp"] else ""
    off = f'<span class="pcard__off">−{p["discount"]}&nbsp;%</span>' if p["discount"] else ""
    return f"""<article class="pcard {extra_cls}" data-product data-brand="{esc(nice_brand(p['brand']))}" data-title="{esc(nice_title(p['title']))}" data-price="{p['price']:.2f}">
  <div class="pcard__img"><img src="{p['img']}" alt="{esc(p['alt'])}">{off}</div>
  <div class="pcard__body">
    <p class="pcard__brand">{esc(nice_brand(p['brand']))}</p>
    <h4 class="pcard__title">{esc(nice_title(p['title']))}</h4>
    <p class="pcard__price"><strong>{eur(p['price'])}</strong>{uvp}</p>
    <p class="pcard__earn"><span class="plus">+</span>{earn(p['price'])} für dich</p>
  </div>
</article>"""


def frag_margin_cards() -> str:
    out = []
    for pair in sel["margin"]:
        p = product(pair)
        save = p["uvp"] - p["price"]
        out.append(f"""<article class="mcard reveal">
  <div class="mcard__img"><img src="{p['img']}" alt="{esc(p['alt'])}"><span class="pcard__off">−{p['discount']}&nbsp;%</span></div>
  <div class="mcard__body">
    <p class="pcard__brand">{esc(nice_brand(p['brand']))}</p>
    <h3 class="mcard__title">{esc(nice_title(p['title']))}</h3>
    <dl class="mcard__rows">
      <div><dt>Regulär</dt><dd><s>{eur(p['uvp'])}</s></dd></div>
      <div><dt>In deinem Shop</dt><dd>{eur(p['price'])}</dd></div>
      <div class="is-save"><dt>Community spart</dt><dd>{eur(save)}</dd></div>
    </dl>
    <div class="mcard__earn"><span>Du verdienst</span><strong>{earn(p['price'])}</strong></div>
  </div>
</article>""")
    return "\n".join(out)


def frag_punch() -> str:
    p = product(sel["margin"][1])  # LED-Maske
    return (f'Schon <strong>10 verkaufte</strong> {esc(nice_brand(p["brand"]))} LED-Masken bringen dir '
            f'<strong class="hl" data-earn-x="10" data-earn="{p["price"]:.2f}">{eur(p["price"] * 10 * DEFAULT_RATE)}</strong>.')


def frag_names() -> str:
    names = sel["luxury_names"]
    half = len(names) // 2
    rows = []
    for r, chunk in enumerate([names[:half], names[half:]]):
        items = "".join(f'<span class="{"i" if i % 2 else ""}">{esc(n)}</span><i aria-hidden="true">✦</i>'
                        for i, n in enumerate(chunk))
        rows.append(f'<div class="names__row{" names__row--rev" if r else ""}">'
                    f'<div class="names__track">{items}</div>'
                    f'<div class="names__track" aria-hidden="true">{items}</div></div>')
    return "\n".join(rows)


def frag_categories() -> str:
    counts = {name: 0 for name, _ in CATEGORIES}
    for p in catalog:
        for name, rx in CATEGORIES:
            if re.search(rx, p["title"], re.I):
                counts[name] += 1
                break
    return "\n".join(f'<li class="reveal"><strong data-count="{n}">{n}</strong><span>{esc(name)}</span></li>'
                     for name, n in counts.items())


def frag_logos() -> str:
    rows = [brands[i::3] for i in range(3)]
    out = []
    for r, row in enumerate(rows):
        tiles = "".join(f'<span class="logo lg-{b["slug"]}" role="img" aria-label="{esc(b["name"])}"></span>'
                        for b in row)
        dup = "".join(f'<span class="logo lg-{b["slug"]}"></span>' for b in row)
        out.append(f'<div class="logos__row{" logos__row--rev" if r == 1 else ""}" style="--dur:{70 + r * 12}s">'
                   f'<div class="logos__track">{tiles}</div><div class="logos__track" aria-hidden="true">{dup}</div></div>')
    return "\n".join(out)


def frag_edit_tabs() -> str:
    return "\n".join(
        f'<button type="button" role="tab" id="tab-{e["id"]}" aria-controls="edit-{e["id"]}" '
        f'aria-selected="{"true" if i == 0 else "false"}"{"" if i == 0 else " tabindex=\"-1\""}>{esc(e["name"])}'
        f'<span>{len(e["items"])}</span></button>'
        for i, e in enumerate(sel["edits"]))


def frag_edit_panels() -> str:
    out = []
    for i, e in enumerate(sel["edits"]):
        cards = "\n".join(product_card(product(x)) for x in e["items"])
        hidden = "" if i == 0 else " hidden"
        out.append(f"""<div class="edit" role="tabpanel" id="edit-{e['id']}" aria-labelledby="tab-{e['id']}"{hidden}>
  <div class="wrap edit__head"><p class="edit__claim">{esc(e['claim'])}</p>
    <div class="edit__arrows"><button type="button" data-rail="-1" aria-label="Zurück">←</button><button type="button" data-rail="1" aria-label="Weiter">→</button></div></div>
  <div class="rail" tabindex="0" aria-label="{esc(e['name'])}">{cards}</div>
</div>""")
    return "\n".join(out)


def frag_deals() -> str:
    out = []
    for i, (title, text) in enumerate(sel["deals"]):
        d = deals[title]
        disc = d["discount"] or ""
        m = re.match(r"(bis zu|über)?\s*(.*)", disc)
        pre = f"<small>{esc(m.group(1))}</small>" if m.group(1) else ""
        val = esc(m.group(2).replace("%", " %"))
        logo = DEAL_LOGOS.get(title)
        logo_html = (f'<span class="deal__logo"><span class="logo lg-{logo}" role="img" aria-label="{esc(title)}"></span></span>'
                     if logo else f'<span class="deal__logo deal__logo--text">{esc(title)}</span>')
        size = " deal--xl" if i < 2 else ""
        img = data_uri(ASSETS / "deals" / f"{d['slug']}.jpg")
        out.append(f"""<article class="deal{size} reveal">
  <img src="{img}" alt="" class="deal__img">
  {logo_html}
  <span class="deal__off">{pre}{val}</span>
  <span class="deal__copy"><strong>{esc(title)}</strong><span>{esc(text)}</span></span>
</article>""")
    return "\n".join(out)


def frag_story_product() -> str:
    p = product(sel["edits"][4]["items"][1])  # Rituals Classic Advent Calendar
    return (f'<div class="story__product"><img src="{p["img"]}" alt=""></div>'
            f'<div class="story__sticker"><span>Nur in meinem Shop</span><strong>−{p["discount"]}&nbsp;%</strong></div>'
            f'<p class="story__text">Der Adventskalender ist da ✨<br>Link in Bio!</p>')


def frag_dash_top() -> str:
    picks = [product(sel["margin"][0]), product(sel["margin"][1]), product(sel["margin"][4])]
    shares = [0.31, 0.22, 0.14]
    return "\n".join(
        f'<li><img src="{p["img"]}" alt=""><span><b>{esc(nice_brand(p["brand"]))}</b>{esc(nice_title(p["title"]))}</span>'
        f'<i style="--w:{int(s * 100 / shares[0])}%"></i></li>'
        for p, s in zip(picks, shares))


# --------------------------------------------------------------- css head
def css_head() -> str:
    fonts = ASSETS / "fonts"
    parts = [
        f"@font-face{{font-family:'Cormorant';font-style:normal;font-weight:300 700;font-display:swap;src:url({data_uri(fonts / 'cormorant.woff2')}) format('woff2')}}",
        f"@font-face{{font-family:'Cormorant';font-style:italic;font-weight:300 700;font-display:swap;src:url({data_uri(fonts / 'cormorant-italic.woff2')}) format('woff2')}}",
        f"@font-face{{font-family:'Inter';font-style:normal;font-weight:100 900;font-display:swap;src:url({data_uri(fonts / 'inter.woff2')}) format('woff2')}}",
    ]
    used_logos = {b["slug"] for b in brands} | set(DEAL_LOGOS.values())
    parts += [f".lg-{slug}{{background-image:url({data_uri(ASSETS / 'logos' / f'{slug}.png')})}}"
              for slug in sorted(used_logos) if (ASSETS / "logos" / f"{slug}.png").exists()]
    motif_vars = ";".join(f"--motif-{deals[t]['slug']}:url({data_uri(ASSETS / 'deals' / (deals[t]['slug'] + '.jpg'))})"
                          for t in sel["customizer_motifs"])
    first = deals[sel["customizer_motifs"][0]]["slug"]
    parts.append(f":root{{{motif_vars};--motif:var(--motif-{first})}}")
    return "\n".join(parts) + "\n"


# --------------------------------------------------------------- main
def main() -> None:
    page = (SRC / "template.html").read_text(encoding="utf-8")
    css = css_head() + (SRC / "style.css").read_text(encoding="utf-8")
    js = (SRC / "app.js").read_text(encoding="utf-8")
    data = {
        "themes": THEMES,
        "defaults": {"rate": DEFAULT_RATE * 100, "followers": 100_000, "conv": 0.5, "basket": 75},
        "avgDiscount": round(AVG_DISCOUNT, 4),
        "contact": CONTACT_MAIL,
    }

    fragments = {
        "dots": frag_dots(), "hero_floaters": frag_hero_floaters(), "phone_products": frag_phone_products(),
        "browser_products": frag_browser_products(), "winwin": frag_winwin(), "swatches": frag_swatches(),
        "motifs": frag_motifs(), "margin_cards": frag_margin_cards(), "punch": frag_punch(),
        "names": frag_names(), "categories": frag_categories(), "logos": frag_logos(),
        "edit_tabs": frag_edit_tabs(), "edit_panels": frag_edit_panels(), "deals": frag_deals(),
        "story_product": frag_story_product(), "dash_top": frag_dash_top(), "snapshot_date": SNAPSHOT_DATE,
    }
    for key, value in fragments.items():
        marker = f"<!--@{key}-->"
        if marker not in page:
            raise SystemExit(f"Marker fehlt im Template: {marker}")
        page = page.replace(marker, value)

    def asset(m: re.Match) -> str:
        kind, name = m.group(1), m.group(2)
        folder = {"ui": "ui", "deal": "deals"}[kind]
        ext = ".png" if kind == "ui" else ".jpg"
        return data_uri(ASSETS / folder / f"{name}{ext}")

    page = re.sub(r"\{\{(ui|deal):([a-z0-9-]+)\}\}", asset, page)
    # Erst ganz am Ende CSS/JS einsetzen, damit deren Inhalt nicht als Marker gelesen wird
    page = page.replace("/*@CSS*/", css, 1)
    page = page.replace("/*@DATA*/", "window.SHOP_DATA = " + json.dumps(data, ensure_ascii=False) + ";", 1)
    page = page.replace("/*@JS*/", js, 1)

    left = re.findall(r"<!--@\w+-->|\{\{[a-z]+:[^}]+\}\}", page)
    if left:
        raise SystemExit(f"Nicht ersetzt: {left}")
    out = ROOT / "index.html"
    out.write_text(page, encoding="utf-8")
    print(f"{out.relative_to(ROOT)}  {out.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
