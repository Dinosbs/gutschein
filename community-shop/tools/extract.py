#!/usr/bin/env python3
"""Zieht Produkte, Partner-Deals, Marken-Logos und Bilder aus einer
SingleFile-Speicherung der INCENT-Kategorie „Health & Beauty“.

    python3 tools/extract.py "/pfad/zu/Health & Beauty - incent.html"

Schreibt:
    data/catalog.json   alle Produkte (einmalig je Marke + Titel)
    data/deals.json     alle Partner-Deals
    data/brands.json    alle Marken-Logos aus „Top Brands“
    assets/products/    Bilder der Produkte aus data/selection.json
    assets/deals/       Bilder der Deals aus data/selection.json
    assets/logos/       alle Marken-Logos
    assets/ui/          Zahlungsarten + Hintergrundbild der Kategorie

Benötigt Pillow (pip install pillow).
"""
from __future__ import annotations

import base64
import html
import io
import json
import re
import sys
import unicodedata
import urllib.parse
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
ASSETS = ROOT / "assets"


# --------------------------------------------------------------- helpers
def slugify(text: str) -> str:
    text = (text.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
            .replace("ß", "ss").replace("ô", "o").replace("é", "e").replace("è", "e")
            .replace("ì", "i").replace("'", ""))
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def euro(text: str | None) -> float | None:
    if not text:
        return None
    return float(text.replace("€", "").replace("\xa0", "").replace(".", "").replace(",", ".").strip())


def decode_data_uri(uri: str) -> bytes:
    header, payload = uri.split(",", 1)
    if ";base64" in header:
        return base64.b64decode(payload)
    return urllib.parse.unquote(payload).encode()


def attr(tag: str, name: str) -> str | None:
    m = re.search(rf'\b{name}=("([^"]*)"|\'([^\']*)\'|([^\s>]+))', tag)
    if not m:
        return None
    return html.unescape(m.group(2) if m.group(2) is not None else m.group(3) if m.group(3) is not None else m.group(4))


IMG_TAG = r"""<img\b(?:[^>"']|"[^"]*"|'[^']*')*>"""  # Attribute dürfen ">" enthalten (SVG-Platzhalter)


def text_of(block: str, pattern: str) -> str | None:
    m = re.search(pattern, block, re.S)
    return norm(html.unescape(m.group(1))) if m else None


def norm(text: str) -> str:
    """Einheitliche Schreibweise (NFC, normale Leerzeichen), damit selection.json sicher passt."""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text).replace("\xa0", " ")).strip()


class Page:
    def __init__(self, source: str):
        self.s = source
        # SingleFile legt viele Bilder als CSS-Variablen ab
        self.vars = {m.group(1): m.group(2) for m in
                     re.finditer(r'--sf-img-(\d+):\s*url\("?(data:[^")]+)"?\)', source)}

    def image_of(self, img_tag: str) -> bytes | None:
        """Echtes Bild eines <img>: entweder src=data:… oder background-image:var(--sf-img-N)."""
        src = attr(img_tag, "src") or ""
        if src.startswith("data:") and not src.startswith("data:image/svg") and len(src) > 400:
            return decode_data_uri(src)
        v = re.search(r"var\(--sf-img-(\d+)\)", img_tag)
        if v and v.group(1) in self.vars:
            return decode_data_uri(self.vars[v.group(1)])
        return None


def knockout_white(im: Image.Image) -> Image.Image:
    """Weißen Hintergrund transparent machen (INCENT-Logo liegt im Shop auf Weiß)."""
    im = im.convert("RGBA")
    r, g, b, a = im.split()
    white = ImageChops.multiply(ImageChops.multiply(r.point(lambda v: 255 if v > 242 else 0),
                                                    g.point(lambda v: 255 if v > 242 else 0)),
                                b.point(lambda v: 255 if v > 242 else 0))
    im.putalpha(ImageChops.multiply(a, ImageChops.invert(white)))
    return im


def save_image(raw: bytes, path: Path, size: tuple[int, int], fmt: str, quality: int = 82,
               background: str | None = None, transparent_white: bool = False) -> None:
    im = Image.open(io.BytesIO(raw))
    if transparent_white:
        im = knockout_white(im)
    if fmt == "JPEG":
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, background or "white")
        bg.alpha_composite(im)
        im = bg.convert("RGB")
    else:
        im = im.convert("RGBA")
        # transparente und weiße Ränder abschneiden, damit Logos optisch gleich groß wirken
        rgb = im.convert("RGB").point(lambda v: 255 if v < 240 else 0).convert("L")
        visible = ImageChops.multiply(rgb.point(lambda v: 255 if v else 0),
                                      im.getchannel("A").point(lambda v: 255 if v > 16 else 0))
        bbox = visible.getbbox()
        if bbox:
            im = im.crop(bbox)
    im.thumbnail(size, Image.LANCZOS)
    path.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "JPEG":
        im.save(path, "JPEG", quality=quality, optimize=True, progressive=True)
    else:
        # 8-Bit-Palette mit Alpha: Logos bleiben scharf, die Datei wird deutlich kleiner
        im = im.quantize(colors=96, method=Image.Quantize.FASTOCTREE)
        im.save(path, "PNG", optimize=True)


# --------------------------------------------------------------- extractors
def extract_products(page: Page):
    s = page.s
    catalog, raw_images = {}, {}
    for m in re.finditer(r'class="product-card bg-white link">(.*?)class="card-link stretched-link"', s, re.S):
        block = m.group(1)
        brand = text_of(block, r"class=brand>([^<]*)<")
        title = text_of(block, r'class="title title--single-line">([^<]*)<')
        if not brand or not title or (brand, title) in catalog:
            continue
        price = euro(text_of(block, r"class=price><span[^>]*>([^<]*)<"))
        uvp = euro(text_of(block, r"class=before-price[^>]*>([^<]*)<"))
        href = re.search(r"href=(\S+)\s+class=\"card-link", s[m.end() - 300:m.end() + 5])
        img = re.search(IMG_TAG, block)
        catalog[(brand, title)] = {
            "brand": brand,
            "title": title,
            "slug": slugify(f"{brand}-{title}")[:80],
            "price": price,
            "uvp": uvp,
            "discount": round((uvp - price) / uvp * 100) if uvp else None,
            "url": href.group(1) if href else None,
        }
        if img:
            raw_images[(brand, title)] = page.image_of(img.group(0))
    return list(catalog.values()), raw_images


def extract_deals(page: Page):
    deals, raw_images = {}, {}
    for m in re.finditer(r'class="featured-offer-card featured-offer-card--link">(.*?)</a>', page.s, re.S):
        block = m.group(1)
        title = text_of(block, r"class=title>([^<]*)<")
        if not title or title in deals:
            continue
        disc = re.search(r"class=discount>(.*?)</div>", block, re.S)
        disc = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", disc.group(1)))).strip() if disc else None
        imgs = re.findall(IMG_TAG, block)
        deals[title] = {
            "title": title,
            "slug": slugify(title),
            "text": text_of(block, r"class=text>([^<]*)<"),
            "discount": disc,
            "url": attr(block[block.rfind("<a "):], "href") if "<a " in block else None,
        }
        if imgs:
            raw_images[title] = page.image_of(imgs[0])
    return list(deals.values()), raw_images


def extract_brand_logos(page: Page):
    s = page.s
    start = s.find(">Top Brands<")
    end = s.find("Best of Health", start)
    logos, seen = [], set()
    for tag in re.findall(IMG_TAG, s[start:end]):
        name = attr(tag, "alt")
        raw = page.image_of(tag)
        if not name or not raw:
            continue
        key = hash(raw)
        if key in seen:
            continue
        seen.add(key)
        logos.append((name, raw))
    return logos


def extract_ui(page: Page):
    s = page.s
    out = {}
    k = s.find("payment-methods payment-methods--fixed")
    for tag in re.findall(IMG_TAG, s[k:k + 60000]):
        name = attr(tag, "alt") or ""
        if name in {"VISA", "Mastercard", "Klarna", "Apple Pay", "PayPal"}:
            out["pay-" + slugify(name)] = decode_data_uri(attr(tag, "src"))
    return out


# --------------------------------------------------------------- main
def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    page = Page(Path(sys.argv[1]).read_text(encoding="utf-8"))
    selection = json.loads((DATA / "selection.json").read_text(encoding="utf-8"))

    # Produkte
    catalog, prod_raw = extract_products(page)
    (DATA / "catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=1), encoding="utf-8")
    wanted = {(norm(b), norm(t)) for b, t in selection["hero"] + selection["margin"]}
    for edit in selection["edits"]:
        wanted |= {(norm(b), norm(t)) for b, t in edit["items"]}
    by_key = {(p["brand"], p["title"]): p for p in catalog}
    for key in sorted(wanted):
        if key not in by_key or not prod_raw.get(key):
            print("! Produkt nicht gefunden:", key)
            continue
        save_image(prod_raw[key], ASSETS / "products" / f"{by_key[key]['slug']}.jpg", (640, 640), "JPEG", 80)
    print(f"{len(catalog)} Produkte, {len(wanted)} Bilder")

    # Deals
    deals, deal_raw = extract_deals(page)
    (DATA / "deals.json").write_text(json.dumps(deals, ensure_ascii=False, indent=1), encoding="utf-8")
    for title, _ in selection["deals"]:
        deal = next((d for d in deals if d["title"] == title), None)
        if not deal or not deal_raw.get(title):
            print("! Deal-Bild fehlt:", title)
            continue
        save_image(deal_raw[title], ASSETS / "deals" / f"{deal['slug']}.jpg", (1000, 500), "JPEG", 78)
    print(f"{len(deals)} Deals")

    # Marken-Logos
    brands = []
    for name, raw in extract_brand_logos(page):
        slug = slugify(name)
        save_image(raw, ASSETS / "logos" / f"{slug}.png", (320, 120), "PNG")
        brands.append({"name": name, "slug": slug})
    (DATA / "brands.json").write_text(json.dumps(brands, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(brands)} Logos")

    # UI: Zahlungsarten + Hintergrundbild der Kategorie (so sieht „Health & Beauty“ auf vorteile.net aus)
    for name, raw in extract_ui(page).items():
        save_image(raw, ASSETS / "ui" / f"{name}.png", (400, 200), "PNG")
    bg = re.search(r'--page-bkg-image:url\("?(data:image/[^")]+)"?\)', page.s)
    if bg:
        save_image(decode_data_uri(bg.group(1)), ASSETS / "ui" / "bg-health-beauty.jpg", (1600, 900), "JPEG", 80)
    print("UI-Grafiken ok")


if __name__ == "__main__":
    main()
