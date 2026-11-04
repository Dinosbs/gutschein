#!/usr/bin/env python3
"""Baut die Pitch-Präsentation als eigenständige, offline-fähige HTML-Dateien.

    python3 build.py

    index.html                  Startseite: allgemeine Fassung über alle Kategorien (Thema „allgemein“)
    pitches/<slug>/index.html   eine Fassung je Eintrag in data/pitches.json (Thema „beauty“ oder „allgemein“)
                                (online: https://dinosbs.github.io/pitch/<slug>/)

Quellen: src/template.html + src/style.css + src/app.js + src/icons.svg + data/*.json + assets/*
Thema „beauty“: data/*.json + assets/* (Health & Beauty). Thema „allgemein“: data/general/*.json + assets/general/*
(alle gespeicherten Kategorien, siehe tools/extract_all.py), fehlende Bilder fallen auf assets/* zurück.
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

SHARE = 70                    # Beteiligung am Gewinn in Prozent (je Pitch: "beteiligung")
MARGIN = 25                   # Durchschnittsmarge pro Produkt in Prozent (je Pitch: "marge")
SNAPSHOT_DATE = "01.11.2026"  # Stand der Preise aus der Shop-Speicherung (Health & Beauty)
SNAPSHOT_GEN = "04.11.2026"   # Stand der Kategorien-Speicherungen (allgemeine Fassung)
RESERVED = {"assets", "data", "src", "tools", "screenshots", "pitches", "favicon.png", "index.html"}

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
    "Philips": "philips", "Braun": "braun", "happybrush": "happybrush", "SharkNinja": "sharkninja", "Oral-B": "oral-b",
    "Procter & Gamble Vorteils-Shop": "procter-gamble-vorteils-shop", "BIOGENA SPORTS": "biogena-sports", "Yazio": "yazio",
    "7Mind": "7mind", "BetterHelp": "betterhelp", "Brandl Nutrition": "brandl-nutrition", "WellCard": "wellcard",
    "ZENSPOTTING": "zenspotting", "Loop Earplugs": "loop-earplugs", "elaire": "elaire", "Kale & Me": "kale-me",
    "Frank Juice": "frank-juice", "fitnessRAUM.de": "fitnessraum-de",
}
LUX = ["dior", "lancome", "chloe", "tom-ford", "yves-saint-laurent", "giorgio-armani", "hermes", "shiseido",
       "nars", "clinique", "rituals"]
DEAL_ROW = 15  # Deals je Laufband-Reihe (zwei gegenläufige Reihen)

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
SEL_BEAUTY = sel  # render() schaltet sel je Fassung um (allgemein: data/general/selection.json)
by_key = {(norm(p["brand"]), norm(p["title"])): p for p in catalog}
brand_names = {b["slug"]: b["name"] for b in brands}

GEN, G_ASSETS = DATA / "general", ASSETS / "general"


def _load(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


gen_catalog = _load(GEN / "catalog.json", [])
gen_deals = {d["title"]: d for d in _load(GEN / "deals.json", [])}
gen_brands = _load(GEN / "brands.json", [])
gen_tree = _load(GEN / "kategorien.json", [])
gen_sel = _load(GEN / "selection.json", {})
gen_by_key = {(norm(p["brand"]), norm(p["title"])): p for p in gen_catalog}
gen_brand_slug = {b["name"]: b["slug"] for b in gen_brands}
gen_brand_names = {b["slug"]: b["name"] for b in gen_brands}

used_products: set[str] = set()
used_deals: set[str] = set()
used_logos: set[str] = set()
used_dlogos: set[str] = set()


def product(pair) -> dict:
    key = (norm(pair[0]), norm(pair[1]))
    p = gen_by_key[key] if CUR["theme"] == "allgemein" and key in gen_by_key else by_key[key]
    used_products.add(p["slug"])
    return p


def find(brand: str, which: str = "hero", index: int = 0) -> dict:
    return product([x for x in sel[which] if x[0] == brand][index])


def deal(title: str) -> dict:
    d = gen_deals[title] if CUR["theme"] == "allgemein" else deals[title]
    used_deals.add(d["slug"])
    return d


def dtext(title: str) -> str | None:
    """Kurzer Deal-Text aus der Beauty-Auswahl; die allgemeine Fassung nutzt den Text aus dem Portal."""
    return None if CUR["theme"] == "allgemein" else DEAL_TEXT.get(title)


def logo(slug: str, label: str = "") -> str:
    used_logos.add(slug)
    aria = f' role="img" aria-label="{esc(label)}"' if label else ""
    return f'<span class="logo lg-{slug}"{aria}></span>'


discounts = [(p["uvp"] - p["price"]) / p["uvp"] for p in catalog if p["uvp"]]
AVG_DISCOUNT = sum(discounts) / len(discounts)
_gd = [(p["uvp"] - p["price"]) / p["uvp"] for p in gen_catalog if p["uvp"]]
AVG_DISCOUNT_GEN = sum(_gd) / len(_gd) if _gd else AVG_DISCOUNT


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


def deal_logo(d: dict, title: str) -> str:
    """Logo im Deal: allgemeine Fassung = Logo aus der Deal-Kachel des Portals, sonst Markenlogo oder Schriftzug."""
    if CUR["theme"] == "allgemein":
        if any((G_ASSETS / "dlogos" / f"{d['slug']}.{e}").exists() for e in ("png", "svg")):
            used_dlogos.add(d["slug"])
            return f'<span class="logo dl-{d["slug"]}" role="img" aria-label="{esc(title)}"></span>'
        if title in gen_sel.get("dlogo_marke", {}):
            return logo(gen_sel["dlogo_marke"][title], title)
        return f'<b class="vp-deal__logo-text">{esc(title)}</b>'
    slug = DEAL_LOGOS.get(title)
    return logo(slug, title) if slug else f'<b class="vp-deal__logo-text">{esc(title)}</b>'


def deal_name(title: str) -> str:
    return title.replace(" | ", " ")


def vp_deal(title: str, text: str | None = None) -> str:
    d = deal(title)
    disc = d["discount"] or ""
    if CUR["theme"] == "allgemein":
        short = re.match(r"((?:bis zu|über)\s*)?([\d.,]+\s*(?:%|€))", disc)
        disc = (short.group(1) or "") + short.group(2) if short else disc
    m = re.match(r"(bis zu|über)?\s*(.*)", disc)
    pre = "<small>bis<br>zu</small>" if m.group(1) == "bis zu" else (f"<small>{esc(m.group(1))}</small>" if m.group(1) else "")
    logo_html = deal_logo(d, title)
    return (f'<span class="vp-deal"><span class="dimg di-{d["slug"]}"></span>'
            f'<span class="vp-deal__logo">{logo_html}</span>'
            f'<span class="vp-deal__badge">{pre}{esc(m.group(2).replace(" ", ""))}</span>'
            f'<span class="vp-deal__info"><b>{esc(deal_name(title))}</b><span>{esc(text or d["text"] or "")}</span></span></span>')


# --------------------------------------------------------------- Durchmischen je Fassung
# Persönliche Fassungen sollen nicht „vom Band“ aussehen: Reihenfolgen und Auswahl werden je slug gewürfelt
# (fester Startwert → stabil bei jedem Build). Die allgemeine Fassung bleibt in der kuratierten Reihenfolge.
CUR = {"slug": None, "i": 0, "theme": "beauty"}


def mixed(seq, salt: str) -> list:
    import random
    out = list(seq)
    if CUR["slug"]:
        random.Random(f"{CUR['slug']}|{salt}").shuffle(out)
    return out


def pick_one(seq, salt: str):
    """Ein Wert je Fassung – verschiedene Fassungen bekommen garantiert verschiedene Werte (solange genug da sind)."""
    import random
    order = list(seq)
    random.Random(f"alle|{salt}").shuffle(order)
    return order[CUR["i"] % len(order)]


STORIES = [  # (Produkt, Story-Text, Bildunterschrift im Feed) – Eintrag 0 = allgemeine Fassung
    (sel["edits"][4]["items"][1], "Der Adventskalender ist da ✨<br>Alle Deals in meinem Shop", "Mein Duft für den Herbst ✨ Exklusiv in meinem Shop"),
    (["SILK'N", 'LED Lichttherapiegerät Gesichtsmaske Pro'], "Mein Glow-Geheimnis ✨<br>Jetzt in meinem Shop", "Self-Care-Sunday 🤍 Alle Lieblinge in meinem Shop"),
    (["RITUALS", 'Geschenkset "The Ritual of Yozakura", M'], "Geschenkidee gefunden 🎁<br>Nur in meinem Shop", "Neu in meinem Shop ✨ Link in Bio"),
    (["SHISEIDO", '"Benefiance - Wrinkle Smoothing", 50 ml'], "Meine Skincare-Routine 🤍<br>Alles in meinem Shop", "Morning Routine ☀️ Alle Produkte in meinem Shop"),
    (["NUXE", 'Körperöl, "Huile Prodigieuse Treatment"'], "Mein Pflege-Liebling ✨<br>Jetzt in meinem Shop", "Glow-Time ✨ Den Link findet ihr in meiner Bio"),
    (["BABYLISS", 'Warmluftbürste "Air Power Volume AS95E"'], "Volumen in 5 Minuten ✨<br>Link in meinem Shop", "Hair Day 💫 Alles in meinem Shop"),
]
CAPTIONS = ["Signature Scent 🤍 Exklusiv in meinem Shop", "Duft-Liebe 💫 Alle Deals in meinem Shop", "Neu in meinem Shop ✨ Link in Bio",
            "Mein Duft für jeden Tag ✨ Jetzt in meinem Shop"]
POST_POOL = [["CHLOÉ", 'EdP "Chloé", 55 ml'], ["TOM FORD", 'EdP "Black Orchid", 50 ml'], ["YVES SAINT LAURENT", 'EdP "Libre", 30 ml'],
             ["PACO RABANNE", 'EdP "Lady Million" 50 ml'], ["GIORGIO ARMANI", 'EdP "Sì", 30 ml'], ["HERMES", 'EdT "Un Jardin sur le Nil", 100 ml'],
             ["DOLCE & GABBANA", 'EdT "Light Blue", 50 ml'], ["DIOR", 'EdT "Miss Blooming Bouquet", 50 ml']]


# --------------------------------------------------------------- Vorschau-Angebote je Fassung
# Die allgemeine Fassung zeigt die bewährte Auswahl. Jede persönliche Fassung bekommt eigene, gewürfelte
# Deals und Produkte (fester Startwert → bei jedem Build gleich, und keine zwei Fassungen teilen sich ein Angebot).
DEFAULT_PREVIEW = {
    "deals": ["Shiseido", "NARS", "ghd - good hair day"],
    "products": [("LANCÔME", 0), ("DIOR", 0), ("SILK'N", 0), ("RITUALS", 0), ("DIOR", 0), ("SILK'N", 0), ("RITUALS", 0), ("LANCÔME", 0)],
}
DEAL_TEXT = {t: txt for t, txt in sel["deals"]}


def preview_sets(pitches: list[dict]) -> dict[str, dict]:
    import random
    rng = random.Random("incent-community-shop-vorschau")
    taken_deals = set(DEFAULT_PREVIEW["deals"])
    beauty = ["Rituals Cosmetics", "Doctor Mi", "The Female Company", "Yves Rocher", "LAYZIN", "lavera", "KLIER", "Philips"]
    deal_pool = [t for t in beauty if t not in taken_deals]
    general = {(norm(b), norm(t)) for b, t in SEL_BEAUTY["hero"]}
    prod_pool = []
    for e in SEL_BEAUTY["edits"]:
        for b, t in e["items"]:
            key = (norm(b), norm(t))
            if key not in general and key not in {(norm(x), norm(y)) for x, y in prod_pool}:
                prod_pool.append([b, t])
    rng.shuffle(deal_pool)
    rng.shuffle(prod_pool)
    out = {}
    for pitch in pitches:
        if not pitch.get("name") or pitch.get("thema", "beauty") != "beauty":
            continue
        deals_ = [deal_pool.pop() for _ in range(4)]
        prods, brands_ = [], set()
        for item in list(prod_pool):  # möglichst verschiedene Marken je Fassung
            if len(prods) == 8:
                break
            if item[0] not in brands_ or len(brands_) >= 6:
                prods.append(item)
                brands_.add(item[0])
                prod_pool.remove(item)
        out[pitch["slug"]] = {"deals": deals_, "products": prods}
    return out


GEN_PREVIEW = {"deals": gen_sel.get("preview", {}).get("deals", []),
               "products": gen_sel.get("preview", {}).get("products", [])}


def pv_products(pv: dict) -> list[dict]:
    items = pv["products"]
    if items and isinstance(items[0], tuple):  # allgemeine Fassung: Marke + Index in sel["hero"]
        return [find(b, "hero", i) for b, i in items]
    return [product(x) for x in items]


VP_CATS = ('<i>Highlights</i><i>NEU</i><i class="is-on">Health &amp; Beauty</i><i>Düfte</i><i>Skincare</i>'
           '<i>Beauty-Tech</i><i>Haare</i><i>Wellness</i><i class="is-on">Alle Kategorien +</i>')
VP_CATS_GEN = ('<i class="is-on">Highlights</i><i>NEU</i><i>Mobilfunk &amp; Internet</i><i>Mobilität</i><i>Technik</i>'
               '<i>Health &amp; Beauty</i><i>Home &amp; Living</i><i>Reisen</i><i class="is-on">Alle Kategorien +</i>')
VPM_CATS = {"beauty": '<i class="is-on">Health &amp; Beauty</i><i>Düfte</i><i>Skincare</i><i>Beauty-Tech</i>',
            "allgemein": '<i class="is-on">Highlights</i><i>Technik</i><i>Reisen</i><i>Mode</i><i>Sport</i>'}
BEST_OF = {"beauty": "Best of Health &amp; Beauty", "allgemein": "Best of the Best"}


THEMES = {
    "beauty": {
        "page_title": "Beauty-Shop", "shop": "Beauty-Shop", "topic": "Health &amp; Beauty",
        "meta": "Dein eigener Beauty-Shop auf vorteile.net – exklusive Vorteilspreise für Deine Community, Beteiligung am Gewinn jeder Bestellung, null Aufwand.",
        "intro_lead": "Exklusive Vorteilspreise von über 80 Beauty-Marken – und weit darüber hinaus. Auf vorteile.net, in Deinem Look, nur für Deine Community. An jeder Bestellung verdienst Du mit.",
        "edits_example": "von „Meine Morning Routine“ bis „Geschenke unter 50&nbsp;€“",
        "marken_lead": "Vom Luxusduft bis zum LED-Beauty-Device: Allein in Health &amp; Beauty warten über 80 Marken und 250+ Produkte – und das ist nur ein Ausschnitt.",
        "lux_more": "<b>+&nbsp;70</b><span>weitere Marken in Health&nbsp;&amp;&nbsp;Beauty</span>",
        "logos_label": "Weitere Marken in Health &amp; Beauty",
        "more": "<strong>Und weit mehr als Beauty:</strong> Insgesamt über 450 Markenpartner, 3.000+ Markenprodukte und 70+ Partnergutscheine auf vorteile.net – von Mode und Sport bis Reisen und Technik. Dein Sortiment stellen wir passend zu Deiner Zielgruppe zusammen.",
        "edits_lead": "Stell Dein Sortiment zusammen wie Deinen Feed – Lieblingsprodukte, Routinen, Geschenkideen. Echte Produkte aus dem aktuellen Angebot, inklusive Deinem Anteil*.",
        "calc_basis": "Health-&amp;-Beauty-Sortiment",
        "step1": "Gemeinsam schneiden wir Dein Sortiment auf Deine Zielgruppe zu – Beauty und alles, was Deine Community sonst liebt.",
        "recap4": "<b>Beauty &amp; weit mehr</b><span>80+ Beauty-Marken, 450+ Markenpartner insgesamt – zugeschnitten auf Deine Community.</span>",
        "fine_kat": "Kategorie Health &amp; Beauty", "recap4_icon": "heart",
    },
    "allgemein": {
        "page_title": "Vorteils-Shop", "shop": "Vorteils-Shop", "topic": "15 Welten · 450+ Marken",
        "meta": "Dein eigener Vorteils-Shop auf vorteile.net – exklusive Vorteilspreise von über 450 Marken in 15 Welten für Deine Community, Beteiligung am Gewinn jeder Bestellung, null Aufwand.",
        "intro_lead": "Exklusive Vorteilspreise von über 450 Marken in 15 Welten – von Technik über Reisen bis Mode. Auf vorteile.net, in Deinem Look, nur für Deine Community. An jeder Bestellung verdienst Du mit.",
        "edits_example": "von „Meine Tech-Favoriten“ bis „Geschenke unter 50&nbsp;€“",
        "marken_lead": "Von Apple bis adidas, von Dyson bis Sixt: die großen Namen aus allen Welten – zu Preisen, die es sonst nur für Mitarbeitende gibt.",
        "lux_more": "<b>+&nbsp;440</b><span>weitere Marken in 15&nbsp;Welten</span>",
        "logos_label": "Weitere Marken aus allen Welten",
        "more": "<strong>Und das ist nur ein Ausschnitt:</strong> Insgesamt über 450 Markenpartner, 3.000+ Markenprodukte und 70+ Partnergutscheine auf vorteile.net – vom Mobilfunktarif bis zur Reise. Neue Deals kommen laufend dazu.",
        "edits_lead": "Stell Dein Sortiment zusammen wie Deinen Feed – Lieblingsprodukte, Tech-Favoriten, Reise-Essentials, Geschenkideen. Echte Produkte aus dem aktuellen Angebot, inklusive Deinem Anteil*.",
        "calc_basis": "Sortiment",
        "step1": "Gemeinsam schneiden wir Dein Sortiment auf Deine Zielgruppe zu – aus 15 Welten genau das, was Deine Community liebt.",
        "recap4": "<b>15 Welten</b><span>450+ Markenpartner – von Technik über Reisen bis Mode, zugeschnitten auf Deine Community.</span>",
        "fine_kat": "Kategorien Technik, Home &amp; Living, Mobilität, Mode &amp; Accessoires, Sport und Health &amp; Beauty",
        "recap4_icon": "layers",
    },
}


def tv(key: str) -> str:
    """Text der aktuellen Fassung (Thema)."""
    return THEMES[CUR["theme"]][key]


def vp_portal(pv: dict) -> str:
    products = pv_products(pv)[:4]
    d = pv["deals"]
    return f"""<div class="vp-frame">
  <div class="vp" aria-hidden="true">
    <div class="vp__bar"><span class="vp__dots"><i></i><i></i><i></i></span><span class="vp__url">{icon("lock")}<span><span data-bind="slug">deinname</span>.vorteile.net/de/dashboard</span></span><span class="vp__bar-end"></span></div>
    <div class="vp__header">
      <div class="vp__top">{vp_logo()}<span class="vp__search">Suchen{icon("search")}</span><span class="vp__account"><b>Community-Shop</b><small data-bind="name">Dein Name</small></span></div>
      <div class="vp__nav"><span class="vp__cats">{VP_CATS if CUR["theme"] == "beauty" else VP_CATS_GEN}</span><span class="vp__icons">{icon("heart")}{icon("user")}<span class="vp__cart">{icon("bag")}<b>1</b></span></span></div>
    </div>
    <div class="vp__stage">
      <span class="vp__bg vp__bg--image"></span><span class="vp__bg vp__bg--solid"></span><span class="vp__bg vp__bg--gradient"></span><span class="vp__fade"></span>
      <div class="vp__head"><strong>{BEST_OF[CUR["theme"]]}</strong><em>Exklusive Angebote</em></div>
      <div class="vp__grid">{vp_deal(d[0], dtext(d[0]))}{vp_deal(d[1], dtext(d[1]))}</div>
      <div class="vp__head vp__head--shop"><strong>Besonders beliebt im Vorteils-Shop</strong><em>Im Trend</em></div>
      <div class="vp__products">{"".join(vp_product(p) for p in products)}</div>
    </div>
  </div>
</div>"""


def vpm_phone(pv: dict) -> str:
    all_ = pv_products(pv)
    products = [all_[0], all_[2]]
    d = pv["deals"]
    return f"""<div class="phone" aria-hidden="true">
  <div class="phone__screen">
    <div class="vpm">
      <div class="vpm__status"><span>9:41</span><span class="vpm__island"></span><span class="vpm__sig"><i></i><i></i><i></i></span></div>
      <div class="vpm__header">{vp_logo()}<span class="vpm__icons">{icon("search")}{icon("heart")}<span class="vp__cart">{icon("bag")}<b>1</b></span></span></div>
      <div class="vpm__cats">{VPM_CATS[CUR["theme"]]}</div>
      <div class="vpm__stage">
        <span class="vp__bg vp__bg--image"></span><span class="vp__bg vp__bg--solid"></span><span class="vp__bg vp__bg--gradient"></span><span class="vp__fade"></span>
        <div class="vp__head"><strong>{BEST_OF[CUR["theme"]]}</strong><em>Exklusive Angebote</em></div>
        {vp_deal(d[0], dtext(d[0]))}
        <div class="vpm__products">{"".join(vp_product(p) for p in products)}</div>
      </div>
    </div>
  </div>
</div>"""


# --------------------------------------------------------------- Folien-Bausteine
TIERS = [("a", "bis 10&nbsp;€"), ("b", "bis 50&nbsp;€"), ("c", "bis 100&nbsp;€"), ("d", "über 100&nbsp;€")]


def frag_winwin(rate: float) -> str:
    """„Ein Verkauf. Zwei Gewinner.“: Produkte aus vier Preisklassen wechseln sich ab, darunter zählt der Verdienst mit."""
    cards, first = [], None
    for tier, _ in TIERS:
        for pair in mixed(sel["cycle"][tier], f"cycle-{tier}"):
            p = product(pair)
            first = first or p
            cards.append(f'<div class="ww-card vreal" data-tier="{tier}" data-price="{p["price"]:.2f}" data-uvp="{p["uvp"]:.2f}" '
                         f'data-off="{p["discount"]}">{vp_product(p)}</div>')
    p = first
    return f"""<div class="winwin">
      <div class="ww-stage" data-anim="pop"><div class="tilt" data-tilt><div class="ww-cards" data-ww-cards>{"".join(cards)}</div></div></div>
      <div class="winwin__side">
        <div class="winwin__flow">
          <div class="ww ww--old" data-anim style="--d:.55s"><span class="ww__label">Regulär</span><span class="ww__value"><s data-ww="uvp">{eur(p['uvp'])}</s></span></div>
          <span class="ww__arrow" data-anim="pop" style="--d:.8s" aria-hidden="true">{icon("arrow-right")}</span>
          <div class="ww" data-anim style="--d:.9s"><span class="ww__label">In Deinem Shop</span><span class="ww__value" data-ww="price">{eur(p['price'])}</span></div>
          <div class="ww ww--community" data-anim style="--d:1.1s"><span class="ww__label">Deine Community spart</span><span class="ww__value" data-ww="save">{eur(p['uvp'] - p['price'])}</span><span class="ww__note">−<span data-ww="off">{p['discount']}</span>&nbsp;% gegenüber regulär</span></div>
          <div class="ww ww--you" data-anim style="--d:1.3s" data-ww-you><span class="ww__label">Du verdienst*</span><span class="ww__value" data-ww="earn">{eur(p['price'] * rate)}</span><span class="ww__note"><!--@share-->&nbsp;% vom Gewinn – ganz automatisch</span></div>
        </div>
      </div>
    </div>
    <div class="ww-sum" data-anim style="--d:1.6s">
      <span class="ww-sum__count"><b data-ww-count>0</b><span><span data-ww-noun>Verkäufe</span> in<br>Deinem Shop</span></span>
      <span class="ww-sum__total"><span>Dein Verdienst*</span><strong data-ww-total>0,00&nbsp;€</strong><em class="ww-sum__plus" data-ww-plus></em></span>
      <span class="ww-sum__claim">… und das <span class="grad-text">ohne einen Handgriff.</span></span>
    </div>
    <p class="finep" data-anim style="--d:1.8s"><!--@fine_rate--></p>"""


def swatches(colors, kind: str) -> str:
    return "\n".join(
        f'<button type="button" class="swatch{" is-on" if i == 0 else ""}" style="--c:{c}" data-{kind}="{c}" '
        f'role="radio" aria-checked="{"true" if i == 0 else "false"}" aria-label="{esc(label)}"></button>'
        for i, (c, label) in enumerate(colors))


def frag_lux() -> str:
    if CUR["theme"] == "allgemein":
        return "\n".join(f'<li data-anim="pop">{logo(gen_brand_slug[n], n)}</li>' for n in mixed(gen_sel["lux"], "lux"))
    return "\n".join(f'<li data-anim="pop">{logo(slug, brand_names.get(slug, slug))}</li>' for slug in mixed(LUX, "lux"))


def frag_categories() -> str:
    if CUR["theme"] == "allgemein":  # Top-Rabatt je gespeicherter Welt (aus den Partner-Deals)
        saved = sorted((t for t in gen_tree if t.get("gespeichert") and t["gespeichert"].get("max_rabatt")),
                       key=lambda t: -t["gespeichert"]["max_rabatt"])
        return "\n".join(f'<div><dt>{esc(t["name"])}</dt><dd><span class="stat__pre">bis</span> '
                         f'<span data-count="{t["gespeichert"]["max_rabatt"]}">{t["gespeichert"]["max_rabatt"]}</span>'
                         f'<span class="stat__suffix">&nbsp;%</span></dd></div>' for t in saved)
    counts = {name: 0 for name, _ in CATEGORIES}
    for p in catalog:
        for name, rx in CATEGORIES:
            if re.search(rx, p["title"], re.I):
                counts[name] += 1
                break
    return "\n".join(f'<div><dt>{esc(name)}</dt><dd><span data-count="{n}">{n}</span></dd></div>'
                     for name, n in counts.items())


def frag_logos() -> str:
    if CUR["theme"] == "allgemein":  # zwei gegenläufige Laufbänder mit bekannten Marken aus allen Welten
        out = []
        for n, row in enumerate(gen_sel["logos"]):
            row = mixed(row, f"logos-{n}")
            tiles = "".join(f"<li>{logo(gen_brand_slug[x], x)}</li>" for x in row)
            dup = "".join(f"<li>{logo(gen_brand_slug[x])}</li>" for x in row)
            out.append(f'<div class="marquee{" marquee--rev" if n else ""}" style="--dur:{110 + n * 20}s"><ul class="marquee__track">{tiles}</ul>'
                       f'<ul class="marquee__track" aria-hidden="true">{dup}</ul></div>')
        return "".join(out)
    rest = mixed([b for b in brands if b["slug"] not in LUX], "logos")
    tiles = "".join(f"<li>{logo(b['slug'], b['name'])}</li>" for b in rest)
    dup = "".join(f"<li>{logo(b['slug'])}</li>" for b in rest)
    return (f'<div class="marquee" style="--dur:140s"><ul class="marquee__track">{tiles}</ul>'
            f'<ul class="marquee__track" aria-hidden="true">{dup}</ul></div>')


def edits_order() -> list[dict]:
    return [{**e, "items": mixed(e["items"], f"edit-{e['id']}")} for e in mixed(sel["edits"], "edits")]


def frag_edit_tabs() -> str:
    return "\n".join(
        f'<button type="button" class="tab" role="tab" id="tab-{e["id"]}" aria-controls="edit-{e["id"]}" '
        f'aria-selected="{"true" if i == 0 else "false"}"{"" if i == 0 else " tabindex=\"-1\""}>{esc(e["name"])}'
        f'<span>{len(e["items"])}</span></button>'
        for i, e in enumerate(edits_order()))


def frag_edit_panels(rate: float) -> str:
    out = []
    for i, e in enumerate(edits_order()):
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
    """Zwei gegenläufige Laufbänder mit Partner-Deals (jede Reihe doppelt für eine nahtlose Schleife)."""
    if CUR["theme"] == "allgemein":
        wall = [(t, None) for t in mixed(gen_sel["wall"], "deals")]
        half = (len(wall) + 1) // 2
        rows = [wall[:half], wall[half:]]
    else:
        pool = mixed(sel["deals"][:2 * DEAL_ROW], "deals")
        rows = [pool[:DEAL_ROW], pool[DEAL_ROW:2 * DEAL_ROW]]
    out = []
    for n, row in enumerate(rows):
        tiles = "".join(f'<li class="vdeal vreal">{vp_deal(t, txt)}</li>' for t, txt in row)
        out.append(f'<div class="dealrow{" dealrow--rev" if n else ""}{" dealrow--compact" if CUR["theme"] == "allgemein" else ""}" style="--dur:{150 + n * 25}s">'
                   f'<ul class="dealrow__track">{tiles}</ul><ul class="dealrow__track" aria-hidden="true">{tiles}</ul></div>')
    return "\n".join(out)


def ig_phone(rate: float, pv: dict) -> str:
    """Handy mit Instagram: Feed → Story → Link → Webshop (vorteile.net) → zurück zur Story. Ablauf: CSS-Schleife."""
    if CUR["theme"] == "allgemein":  # allgemeine Fassung: Post und Story aus data/general/selection.json
        g = gen_sel["preview"]
        post, story_pair = product(g["post"]), g["story"]
        story_text, caption = g["story_text"], g["caption"]
    else:
        post = find("LANCÔME") if not CUR["slug"] else product(pick_one(POST_POOL, "post"))
        story_pair, story_text, caption = STORIES[0] if not CUR["slug"] else pick_one(STORIES[1:], "story")
        if CUR["slug"]:
            caption = pick_one(CAPTIONS, "caption")  # Feed-Post zeigt einen Duft – Bildunterschrift passend dazu
    st = product(story_pair)
    all_ = pv_products(pv)
    d = pv["deals"]
    page1 = [all_[4], all_[5]]
    pick = page1[1]  # dieses Produkt landet im Warenkorb
    page2 = [all_[6], all_[7]]
    friends = [("anna.m", "A", "#f2b6a8"), ("julia", "J", "#a9c1ff"), ("sophie", "S", "#ffd28a"), ("mara", "M", "#a8dcc0")]
    rings = "".join(f'<span class="ig__st"><span class="ig__ring"><i style="--av:{c}">{a}</i></span>{h}</span>' for h, a, c in friends)
    return f"""<div class="phone ig-phone" aria-hidden="true">
  <div class="phone__screen">
    <div class="ig">
      <span class="ig__island"></span>
      <div class="ig__feed">
        <div class="ig__status"><span>9:41</span><span class="ig__sig"><i></i><i></i><i></i><i></i></span></div>
        <div class="ig__top"><span class="ig__brand">Instagram</span><span class="ig__top-icons">{icon("heart")}{icon("message")}</span></div>
        <div class="ig__stories">
          <span class="ig__st ig__st--me"><span class="ig__ring"><i data-bind="initial">D</i></span><span data-bind="handle">deinname</span></span>{rings}
        </div>
        <div class="ig__post-head"><span class="ig__ava"><i data-bind="initial">D</i></span><b data-bind="handle">deinname</b>{icon("more")}</div>
        <div class="ig__post-img"><span class="pimg pi-{post['slug']}"></span><span class="ig__post-tag">{icon("bag")}<span><span data-bind="slug">deinname</span>.vorteile.net</span></span></div>
        <div class="ig__actions">{icon("heart")}{icon("message")}{icon("share")}<span class="ig__save">{icon("bookmark")}</span></div>
        <p class="ig__likes">Gefällt 2.418 Mal</p>
        <p class="ig__caption"><b data-bind="handle">deinname</b> {caption}</p>
        <div class="ig__tabbar">{icon("home")}{icon("search")}{icon("plus-square")}{icon("reels")}<span class="ig__me"><i data-bind="initial">D</i></span></div>
      </div>
      <div class="ig__story">
        <div class="ig__story-bars"><i></i><i></i><i></i></div>
        <div class="ig__story-head"><span class="ig__ava ig__ava--sm"><i data-bind="initial">D</i></span><b data-bind="handle">deinname</b><span class="ig__story-time">2 Std.</span>{icon("x")}</div>
        <div class="ig__story-product"><span class="pimg pi-{st['slug']}"></span></div>
        <div class="ig__story-sticker"><span>Nur in meinem Shop</span><strong>-{st['discount']}&nbsp;%</strong></div>
        <p class="ig__story-text">{story_text}</p>
        <span class="ig__story-link">{icon("arrow-up-right")}<span><span data-bind="slug">deinname</span>.vorteile.net</span></span>
        <div class="ig__story-foot"><span class="ig__story-input">Nachricht senden …</span>{icon("heart")}{icon("share")}</div>
      </div>
      <div class="ig__sheet">
        <div class="ig__bar"><span class="ig__close">{icon("x")}</span><span class="ig__url">{icon("lock")}<span><span data-bind="slug">deinname</span>.vorteile.net</span></span>{icon("more")}</div>
        <div class="ig__view">
          <div class="vpm ig__shophead"><div class="vpm__header">{vp_logo()}<span class="vpm__icons">{icon("search")}{icon("heart")}<span class="vp__cart ig__cartbtn">{icon("bag")}<b class="ig__badge">1</b></span></span></div></div>
          <div class="ig__scroll">
            <div class="vpm ig__page">
              <div class="vpm__cats">{VPM_CATS[CUR["theme"]]}</div>
              <div class="vpm__stage">
                <span class="vp__bg vp__bg--image"></span><span class="vp__bg vp__bg--solid"></span><span class="vp__bg vp__bg--gradient"></span><span class="vp__fade"></span>
                <div class="vp__head"><strong>{BEST_OF[CUR["theme"]]}</strong><em>Exklusive Angebote</em></div>
                {vp_deal(d[0], dtext(d[0]))}
                <div class="vpm__products">{vp_product(page1[0])}<span class="ig__pick">{vp_product(pick)}</span></div>
                <div class="vp__head vp__head--shop"><strong>Nur für Deine Community</strong><em>Partner-Deals</em></div>
                <div class="ig__deals">{vp_deal(d[-2], dtext(d[-2]))}{vp_deal(d[-1], dtext(d[-1]))}</div>
                <div class="vpm__products">{"".join(vp_product(x) for x in page2)}</div>
              </div>
            </div>
          </div>
          <p class="ig__toast">{icon("check")}Zum Warenkorb hinzugefügt</p>
          <div class="ig__cart">
            <p class="ig__cart-title">Warenkorb <span>(1 Artikel)</span></p>
            <div class="ig__cart-item"><span class="pimg pi-{pick['slug']}"></span><span class="ig__cart-meta"><b>{esc(pick['brand'])}</b><span>{esc(nice_title(pick['title']))}</span><span class="ig__cart-price"><strong>{eur(pick['price'])}</strong><s>{eur(pick['uvp'])}</s></span></span><span class="ig__cart-qty">1</span></div>
            <dl class="ig__cart-sum">
              <div><dt>Zwischensumme</dt><dd>{eur(pick['price'])}</dd></div>
              <div class="is-save"><dt>Du sparst</dt><dd>{eur(pick['uvp'] - pick['price'])}</dd></div>
              <div><dt>Versand</dt><dd>kostenlos</dd></div>
              <div class="is-total"><dt>Gesamt</dt><dd>{eur(pick['price'])}</dd></div>
            </dl>
            <span class="ig__checkout">Zur Kasse</span>
            <div class="ig__done"><span class="ig__done-check">{icon("check")}</span><b>Bestellung abgeschlossen</b><span>Danke für Deinen Einkauf!</span></div>
          </div>
        </div>
      </div>
      <span class="ig__tap"></span>
    </div>
  </div>
  <span class="reach__earn">{icon("coins")}+{eur(pick['price'] * rate)} für Dich</span>
</div>"""


# --------------------------------------------------------------- allgemeine Fassung: Welten, Zielgruppen, Top-Deals
def frag_zielgruppen() -> str:
    return "\n".join(
        f'<button type="button" class="aud__btn" data-aud-btn="{z["id"]}" aria-pressed="{"true" if i == 0 else "false"}">'
        f'{icon(z["icon"])}<span><b>{esc(z["label"])}</b><small>{esc(z["sub"])}</small></span></button>'
        for i, z in enumerate(gen_sel["zielgruppen"]))


def frag_welten() -> str:
    """Alle Kategorien des Portals (Navigation) mit Unterkategorien; Top-Rabatt, wo eine Speicherung vorliegt."""
    cfg = {w["name"]: w for w in gen_sel["welten"]}
    out = []
    for t in gen_tree:
        w = cfg[t["name"]]
        subs = t["subs"]
        line = " · ".join(subs[:3]) + (" …" if len(subs) > 3 else "") if subs else w.get("text", "")
        mx = (t.get("gespeichert") or {}).get("max_rabatt")
        badge = f'<em class="world__badge">bis {mx}&nbsp;%</em>' if mx else ""
        tip = esc(" · ".join(subs)) if subs else esc(line)
        out.append(f'<li data-world="{w["gruppen"]}" title="{tip}"><span class="world__icon">{icon(w["icon"])}</span>'
                   f'<b>{esc(t["name"])}</b><small>{esc(line)}</small>{badge}</li>')
    return "\n".join(out)


def spot_card(title: str, on: bool) -> str:
    d = deal(title)
    m = re.match(r"(bis zu|über)?\s*([\d.,]+)\s*(%|€)?", d["discount"] or "")
    pre, num, unit = (m.group(1) or ""), int(m.group(2).replace(".", "").replace(",", "")), (m.group(3) or "")
    shown = f"{num:,}".replace(",", ".")
    pre_html = f"<small>{esc(pre)}</small>" if pre else ""
    return (f'<article class="spot__card{" is-on" if on else ""}" data-spot-card>'
            f'<span class="dimg di-{d["slug"]}"></span><span class="spot__shade"></span>'
            f'<span class="spot__logo">{deal_logo(d, title)}</span><span class="spot__cat">{esc(d["kategorien"][0])}</span>'
            f'<span class="spot__val">{pre_html}<b data-spot-num="{num}">{shown}</b><em>{"&nbsp;" + unit if unit else ""}</em></span>'
            f'<span class="spot__title">{esc(deal_name(title))}</span><span class="spot__text">{esc(d["text"] or "")}</span></article>')


def frag_spotlight(slots: int = 4) -> str:
    """Top-Deals: vier Plätze, jeder wechselt zwischen zwei großen Deals (Schleife in app.js)."""
    items = mixed(gen_sel["spotlight"], "spot")
    return "".join(f'<div class="spot__slot" style="--si:{i}">{"".join(spot_card(t, k == 0) for k, t in enumerate(items[i::slots]))}</div>'
                   for i in range(slots))


def frag_lockscreen() -> str:
    """iPhone-Sperrbildschirm (iOS-Stil). Mitteilungen schiebt app.js fortlaufend von unten ein."""
    return f"""<div class="ios" aria-hidden="true">
  <div class="ios__screen">
    <div class="ios__wall"><i></i><i></i><i></i></div>
    <div class="ios__status"><span class="ios__bars"><i></i><i></i><i></i><i></i></span><span class="ios__island"></span><span class="ios__right"><b>5G</b><span class="ios__bat"></span></span></div>
    <div class="ios__lock">{icon("lock")}</div>
    <p class="ios__date" data-ios-date>Montag, 2. November</p>
    <p class="ios__time" data-ios-time>23:41</p>
    <div class="ios__stack"><ul class="ios__notes" data-ios-notes></ul></div>
    <div class="ios__live" data-ios-live>
      <span class="ios__live-head"><span class="ios__live-icon">{icon("bag")}</span><b data-bind="app">Community-Shop</b><span class="ios__live-since" data-ios-since>seit 22:58</span></span>
      <span class="ios__live-label">Heute Nacht verdient</span>
      <span class="ios__live-row"><strong data-ios-total>0,00 €</strong><em data-ios-last></em></span>
    </div>
    <div class="ios__bottom"><span class="ios__btn"><svg viewBox="0 0 24 24"><path d="M9 2h6l-1 6h-4zM10 8h4v12a2 2 0 0 1-4 0z"/></svg></span><span class="ios__btn"><svg viewBox="0 0 24 24"><path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/></svg></span></div>
    <span class="ios__home"></span>
  </div>
</div>"""


# --------------------------------------------------------------- CSS-Kopf (Schriften + Bilder, jedes nur einmal)
def asset_file(kind: str, slug: str, exts=("jpg",)) -> Path | None:
    """Bild der aktuellen Fassung: allgemeine Fassung zuerst assets/general/<kind>/, sonst assets/<kind>/."""
    dirs = [G_ASSETS / kind, ASSETS / kind] if CUR["theme"] == "allgemein" else [ASSETS / kind]
    for d in dirs:
        for e in exts:
            if (d / f"{slug}.{e}").exists():
                return d / f"{slug}.{e}"
    return None


def css_head(bg_image: Path | None = None) -> str:
    fonts = ASSETS / "fonts"
    parts = []
    for weight, style, file in [(400, "normal", "400"), (500, "normal", "500"), (600, "normal", "600"),
                                (600, "italic", "600-italic"), (700, "normal", "700"), (800, "normal", "800")]:
        parts.append(f'@font-face{{font-family:"Barlow Semi Condensed";font-weight:{weight};font-style:{style};'
                     f'font-display:swap;src:url({data_uri(fonts / f"barlow-semi-condensed-{file}.woff2")}) format("woff2")}}')
    # Inter (OFL) als iOS-nahe Schrift für iPhone und Instagram, falls kein San Francisco vorhanden ist
    parts.append(f'@font-face{{font-family:"Inter";font-weight:100 900;font-style:normal;font-display:swap;'
                 f'src:url({data_uri(fonts / "inter-latin-var.woff2")}) format("woff2")}}')
    ui = ASSETS / "ui"
    parts.append(f".vp__logo-incent{{background-image:url({data_uri(ui / 'incent-logo-dark.png')})}}")
    parts.append(f".vp-theme[data-nav-tone=\"dark\"] .vp__logo-incent{{background-image:url({data_uri(ui / 'incent-logo-white.png')})}}")
    default_bg = G_ASSETS / "ui" / "bg-technik.jpg" if CUR["theme"] == "allgemein" else ui / "bg-health-beauty.jpg"
    parts.append(f".vp__bg--image,.bg-opt__thumb--image{{background-image:url({data_uri(bg_image or default_bg)})}}")
    parts += [f".pi-{s}{{background-image:url({data_uri(asset_file('products', s))})}}" for s in sorted(used_products)]
    parts += [f".di-{s}{{background-image:url({data_uri(asset_file('deals', s))})}}" for s in sorted(used_deals)]
    parts += [f".lg-{s}{{background-image:url({data_uri(f)})}}" for s in sorted(used_logos)
              if (f := asset_file("logos", s, ("png",) if CUR["theme"] == "beauty" else ("png", "svg")))]
    parts += [f".dl-{s}{{background-image:url({data_uri(f)})}}" for s in sorted(used_dlogos)
              if (f := next((G_ASSETS / "dlogos" / f"{s}.{e}" for e in ("png", "svg") if (G_ASSETS / "dlogos" / f"{s}.{e}").exists()), None))]
    return "\n".join(parts) + "\n"


# --------------------------------------------------------------- Seite bauen
def render(pitch: dict | None, pv: dict | None = None) -> str:
    global sel
    pitch = pitch or {}
    CUR["theme"] = pitch.get("thema", "beauty")
    if CUR["theme"] not in THEMES:
        raise SystemExit(f"Unbekanntes Thema: {CUR['theme']!r} (beauty oder allgemein)")
    sel = gen_sel if CUR["theme"] == "allgemein" else SEL_BEAUTY
    for used in (used_products, used_deals, used_logos, used_dlogos):  # jede Seite bettet nur ihre eigenen Bilder ein
        used.clear()
    pv = pv or (GEN_PREVIEW if CUR["theme"] == "allgemein" else DEFAULT_PREVIEW)
    CUR["slug"] = pitch.get("slug") if pitch.get("name") else None
    named = [x["slug"] for x in json.loads((DATA / "pitches.json").read_text(encoding="utf-8")).get("pitches", []) if x.get("name")]
    CUR["i"] = named.index(CUR["slug"]) if CUR["slug"] in named else 0
    share = float(pitch.get("beteiligung", SHARE))
    margin = float(pitch.get("marge", MARGIN))
    rate = round(share * margin / 10000, 6)  # Verdienst je Euro Umsatz: Marge × Gewinnbeteiligung (25 % × 70 % = 17,5 %)
    name = (pitch.get("name") or "").strip()
    page = (SRC / "template.html").read_text(encoding="utf-8")
    # Fassung anwenden: <!--@if thema-->…<!--@end--> und Texte <!--@t:schlüssel-->
    page = re.sub(r"<!--@if (\w+)-->(.*?)<!--@end-->", lambda m: m.group(2) if m.group(1) == CUR["theme"] else "", page, flags=re.S)
    page = re.sub(r"<!--@t:(\w+)-->", lambda m: tv(m.group(1)), page)
    poss = (name + ("’" if re.search(r"[sxzß]$", name, re.I) else "s")) if name else ""
    general = CUR["theme"] == "allgemein"
    fragments = {
        "icons": (SRC / "icons.svg").read_text(encoding="utf-8"),
        "page_title": esc(f"{poss} {tv('page_title')} · INCENT Community-Shop" if name else f"Dein eigener {tv('page_title')} · INCENT Community-Shop"),
        "vp_hero": vp_portal(pv), "vpm_phone": vpm_phone(pv), "winwin": frag_winwin(rate),
        "swatches_btn": swatches(BTN_COLORS, "btn"), "swatches_nav": swatches(NAV_COLORS, "nav"),
        "lux": frag_lux(),
        "categories": frag_categories(), "logos": frag_logos(), "edit_tabs": frag_edit_tabs(),
        "edit_panels": frag_edit_panels(rate), "deals": frag_deals(), "ig_phone": ig_phone(rate, pv),
        "lockscreen": frag_lockscreen(), "snapshot_date": SNAPSHOT_GEN if general else SNAPSHOT_DATE, "thema": CUR["theme"],
        "avg": f"{round((AVG_DISCOUNT_GEN if general else AVG_DISCOUNT) * 100)}",
    }
    if general:
        fragments.update({"spotlight": frag_spotlight(), "welten": frag_welten(), "zielgruppen": frag_zielgruppen(),
                          "welten_n": str(len(gen_tree)), "deal_count": str(len(gen_deals) // 10 * 10)})
    else:
        fragments["deal_count"] = str(len(deals))
    for key, value in fragments.items():
        page = page.replace(f"<!--@{key}-->", value)
    pct = lambda v: f"{v:g}".replace(".", ",")
    page = page.replace("<!--@fine_rate-->", f"*Durchschnittsmarge ist rund {pct(margin)}&nbsp;%")
    page = page.replace("<!--@share-->", pct(share)).replace("<!--@margin-->", pct(margin))
    page = re.sub(r"\{\{ui:([a-z0-9-]+)\}\}", lambda m: data_uri(ASSETS / "ui" / f"{m.group(1)}.png"), page)

    logo_uri = None
    if pitch.get("logo"):
        logo_uri = data_uri(DATA / "pitches" / pitch["logo"])
    data = {
        "rate": rate * 100, "share": share, "margin": margin,
        "night": pick_one(["23:06", "22:41", "23:17", "22:49", "23:24"], "night") if CUR["slug"] else "22:58",
        "audStart": pick_one([1, 2, 3], "aud") if CUR["slug"] else 0,
        "defaults": {"followers": 100_000, "conv": 0.5, "basket": 75,
                     "btn": BTN_COLORS[0][0], "nav": NAV_COLORS[0][0]},
        "pitch": {"name": name, "farbe": pitch.get("farbe"), "nav": pitch.get("nav"),
                  "hintergrund": pitch.get("hintergrund"), "hintergrundfarbe": pitch.get("hintergrundfarbe"),
                  "hintergrundton": pitch.get("hintergrundton"),
                  "reichweite": pitch.get("reichweite"),
                  "logo": logo_uri, "slug": pitch.get("slug")},
        "avgDiscount": round(AVG_DISCOUNT_GEN if general else AVG_DISCOUNT, 4),
        "t": {"topic": html.unescape(tv("topic")), "shop": tv("shop")},
        "presets": PRESETS,
    }
    page = page.replace("/*@CSS*/", css_head(DATA / "pitches" / pitch["hintergrundbild"] if pitch.get("hintergrundbild") else None) + (SRC / "style.css").read_text(encoding="utf-8"), 1)
    page = page.replace("/*@DATA*/", "window.SHOP_DATA = " + json.dumps(data, ensure_ascii=False) + ";", 1)
    page = page.replace("/*@JS*/", (SRC / "app.js").read_text(encoding="utf-8"), 1)
    left = re.findall(r"<!--@\w+-->|\{\{[a-z]+:[^}]+\}\}", page)
    if left:
        raise SystemExit(f"Nicht ersetzt: {left}")
    return page


START = "beauty"  # https://dinosbs.github.io/pitch/ leitet hierhin weiter


def redirect_page(slug: str) -> str:
    """Startseite /pitch/: leitet auf die allgemeine Fassung weiter (keine eigene Präsentation mehr)."""
    return f"""<!DOCTYPE html>
<html lang="de"><head><meta charset="utf-8"><meta name="robots" content="noindex, nofollow">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>INCENT Community-Shop</title><meta http-equiv="refresh" content="0; url={slug}/">
<script>location.replace("{slug}/" + location.search + location.hash)</script></head>
<body style="font-family:system-ui,sans-serif;padding:40px"><p><a href="{slug}/">Weiter zur Präsentation</a></p></body></html>
"""


def main() -> None:
    cfg = json.loads((DATA / "pitches.json").read_text(encoding="utf-8"))
    out = ROOT / "index.html"
    if cfg.get("startseite"):  # https://dinosbs.github.io/pitch/ zeigt die allgemeine Fassung direkt
        out.write_text(render(cfg["startseite"]), encoding="utf-8")
        print(f"index.html  {out.stat().st_size / 1e6:.1f} MB  →  /pitch/  (Thema {CUR['theme']})")
    else:
        out.write_text(redirect_page(START), encoding="utf-8")
        print(f"index.html  Weiterleitung  →  /pitch/{START}/")
    previews = preview_sets(cfg.get("pitches", []))
    for slug, pv in previews.items():
        print(f"  Vorschau {slug}: {', '.join(pv['deals'])} | {', '.join(b for b, _ in pv['products'])}")
    target = ROOT / "pitches"
    if target.exists():
        shutil.rmtree(target)
    for pitch in cfg.get("pitches", []):
        slug = pitch.get("slug", "")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,40}", slug) or slug in RESERVED:
            raise SystemExit(f"Ungültiger slug in data/pitches.json: {slug!r} (nur a–z, 0–9, Bindestrich)")
        path = target / slug / "index.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(pitch, previews.get(slug)), encoding="utf-8")
        print(f"pitches/{slug}/index.html  {path.stat().st_size / 1e6:.1f} MB  →  /pitch/{slug}/")


if __name__ == "__main__":
    main()
