#!/usr/bin/env python3
"""Liest SingleFile-Speicherungen mehrerer INCENT-Kategorien aus – Grundlage der allgemeinen Fassung.

    python3 tools/extract_all.py "/pfad/Technik - incent.html" "/pfad/Sport - incent.html" ...

Schreibt:
    data/general/kategorien.json  alle Kategorien mit Unterkategorien (aus der Navigation des Portals)
                                  und Kennzahlen je gespeicherter Kategorie
    data/general/catalog.json     Produkte aller gespeicherten Kategorien
    data/general/deals.json       Partner-Deals aller gespeicherten Kategorien
    data/general/brands.json      Marken aus „Top Brands“ aller gespeicherten Kategorien
    assets/general/…              Bilder – nur für die Auswahl in data/general/selection.json
                                  (products/, deals/, dlogos/ = Logo im Deal, logos/, ui/bg-<kategorie>.jpg)

Benötigt Pillow (pip install pillow). Nutzt die Hilfsfunktionen aus tools/extract.py.
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

from extract import (IMG_TAG, Page, attr, decode_data_uri, euro, norm, save_image, slugify,  # noqa: E402
                     text_of)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "general"
ASSETS = ROOT / "assets" / "general"


def real_image(page: Page, tag: str) -> tuple[bytes, str] | None:
    """Bild eines <img>: Rasterbild (wie extract.Page.image_of) oder echtes SVG-Logo (base64, kein Platzhalter)."""
    raw = page.image_of(tag)
    if raw:
        return raw, "raster"
    src = attr(tag, "src") or ""
    if src.startswith("data:image/svg+xml;base64,") and len(src) > 600:
        return decode_data_uri(src), "svg"
    return None


def category_tree(body: str) -> list[dict]:
    """„Alle Kategorien“-Menü: Hauptkategorien mit Unterkategorien."""
    i = body.find("subcategory-all-groups__columns")
    seg = body[i:i + 60000]
    tree = []
    for g in re.finditer(r'class="?subcategory-group"?>(.*?)(?=class="?subcategory-group"?>|subcategory-sidebar|$)', seg, re.S):
        top = re.search(r'subcategory-group__top[^>]*>([^<]+)<', g.group(1))
        if not top:
            continue
        name = norm(html.unescape(top.group(1)))
        if name == "NEU":
            continue
        subs = [norm(html.unescape(k)) for k in re.findall(r'<li[^>]*>\s*<a[^>]*>([^<]+)</a>', g.group(1))]
        tree.append({"name": name, "slug": slugify(name), "subs": subs})
    return tree


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    OUT.mkdir(parents=True, exist_ok=True)
    sel_path = OUT / "selection.json"
    selection = json.loads(sel_path.read_text(encoding="utf-8")) if sel_path.exists() else {}

    products, deals, brands, tree, stats = {}, {}, {}, [], {}
    raw_products, raw_deals, raw_dlogos, raw_brands, raw_bgs = {}, {}, {}, {}, {}
    for f in sys.argv[1:]:
        s = Path(f).read_text(encoding="utf-8")
        page = Page(s)
        cat = norm(html.unescape(re.search(r"<title>([^<]+?) - incent</title>", s).group(1)))
        body = s[s.find("<body"):]
        tree = tree or category_tree(body)

        n_prod = n_deal = 0
        for m in re.finditer(r'class="product-card bg-white link">(.*?)class="card-link stretched-link"', body, re.S):
            b = m.group(1)
            brand, title = text_of(b, r"class=brand>([^<]*)<"), text_of(b, r'class="title title--single-line">([^<]*)<')
            if not brand or not title:
                continue
            n_prod += 1
            key = (brand, title)
            if key in products:
                products[key]["kategorien"].append(cat)
                continue
            price = euro(text_of(b, r"class=price><span[^>]*>([^<]*)<"))
            uvp = euro(text_of(b, r"class=before-price[^>]*>([^<]*)<"))
            products[key] = {"brand": brand, "title": title, "slug": slugify(f"{brand}-{title}")[:80], "price": price,
                             "uvp": uvp, "discount": round((uvp - price) / uvp * 100) if uvp else None, "kategorien": [cat]}
            img = re.search(IMG_TAG, b)
            if img:
                raw_products[key] = page.image_of(img.group(0))

        for m in re.finditer(r'class="featured-offer-card featured-offer-card--link">(.*?)</a>', body, re.S):
            b = m.group(1)
            title = text_of(b, r"class=title>([^<]*)<")
            if not title:
                continue
            n_deal += 1
            if title in deals:
                if cat not in deals[title]["kategorien"]:
                    deals[title]["kategorien"].append(cat)
                continue
            disc = re.search(r"class=discount>(.*?)</div>", b, re.S)
            disc = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", disc.group(1)))).strip() if disc else None
            deals[title] = {"title": title, "slug": slugify(title), "text": text_of(b, r"class=text>([^<]*)<"),
                            "discount": disc, "kategorien": [cat]}
            imgs = re.findall(IMG_TAG, b)
            if imgs:
                raw_deals[title] = page.image_of(imgs[0])
            if len(imgs) > 1:
                raw_dlogos[title] = real_image(page, imgs[1])

        i0 = body.find(">Top Brands<")
        i1 = body.find("section-header", i0 + 20)
        for tag in re.findall(IMG_TAG, body[i0:i1]):
            name = attr(tag, "alt")
            if not name:
                continue
            slug = slugify(name)
            if slug in brands:
                if cat not in brands[slug]["kategorien"]:
                    brands[slug]["kategorien"].append(cat)
                continue
            img = real_image(page, tag)
            if not img:
                continue
            brands[slug] = {"name": norm(name), "slug": slug, "kategorien": [cat]}
            raw_brands[slug] = img

        bg = re.search(r'--page-bkg-image:url\("?(data:image/[^")]+)"?\)', s)
        if bg:
            raw_bgs[slugify(cat)] = decode_data_uri(bg.group(1))
        pct = [int(x) for d in deals.values() if cat in d["kategorien"] for x in re.findall(r"(\d+)\s*%", d["discount"] or "")]
        stats[cat] = {"produkte": n_prod, "deals": n_deal, "marken": sum(cat in b["kategorien"] for b in brands.values()),
                      "max_rabatt": max(pct) if pct else None, "hintergrund": bool(bg)}
        print(f"{cat}: {n_prod} Produkte, {n_deal} Deals, {stats[cat]['marken']} Marken, max. {stats[cat]['max_rabatt']} %")

    for t in tree:
        t["gespeichert"] = stats.get(t["name"])
    (OUT / "kategorien.json").write_text(json.dumps(tree, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "catalog.json").write_text(json.dumps(list(products.values()), ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "deals.json").write_text(json.dumps(list(deals.values()), ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "brands.json").write_text(json.dumps(list(brands.values()), ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(tree)} Kategorien, {len(products)} Produkte, {len(deals)} Deals, {len(brands)} Marken")

    # Bilder nur für die Auswahl (hält das Repository und die Seiten schlank)
    want_products = {(norm(b), norm(t)) for b, t in selection.get("products", [])}
    for key, raw in raw_products.items():
        if (norm(key[0]), norm(key[1])) in want_products and raw:
            save_image(raw, ASSETS / "products" / f"{products[key]['slug']}.jpg", (640, 640), "JPEG", 80)
    want_deals = set(selection.get("deals", []))
    for title in want_deals:
        if title not in deals:
            print("! Deal nicht gefunden:", title)
            continue
        if raw_deals.get(title):
            save_image(raw_deals[title], ASSETS / "deals" / f"{deals[title]['slug']}.jpg", (800, 400), "JPEG", 74)
        logo = raw_dlogos.get(title)
        if logo and logo[1] == "raster":
            save_image(logo[0], ASSETS / "dlogos" / f"{deals[title]['slug']}.png", (320, 100), "PNG")
        elif logo:
            (ASSETS / "dlogos").mkdir(parents=True, exist_ok=True)
            (ASSETS / "dlogos" / f"{deals[title]['slug']}.svg").write_bytes(logo[0])
    want_brands = {slugify(n) for n in selection.get("brands", [])}
    for slug in want_brands:
        if slug not in raw_brands:
            print("! Marke nicht gefunden:", slug)
            continue
        raw, kind = raw_brands[slug]
        if kind == "raster":
            save_image(raw, ASSETS / "logos" / f"{slug}.png", (320, 120), "PNG")
        else:
            (ASSETS / "logos").mkdir(parents=True, exist_ok=True)
            (ASSETS / "logos" / f"{slug}.svg").write_bytes(raw)
    for slug, raw in raw_bgs.items():
        save_image(raw, ASSETS / "ui" / f"bg-{slug}.jpg", (1600, 900), "JPEG", 78)
    print("Bilder für die Auswahl gespeichert")


if __name__ == "__main__":
    main()
