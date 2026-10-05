#!/usr/bin/env python3
"""Baut die Mockups: fügt src/select-hinweis.{css,js} in die Original-Seiten ein.

    python3 build.py

original/*.html  ->  mockups/*.html  (Originale bleiben unverändert)
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
ORIGINAL = ROOT / "original"
MOCKUPS = ROOT / "mockups"

PAGES = ["gutscheinwelt.html", "warenkorb.html", "details-pruefen.html"]


def main() -> None:
    css = (SRC / "select-hinweis.css").read_text(encoding="utf-8")
    js = (SRC / "select-hinweis.js").read_text(encoding="utf-8")
    # Die SingleFile-Seiten haben kein </body>, daher einfach ans Ende anhängen.
    snippet = (
        f'\n<style id="select-hinweis-css">\n{css}</style>'
        f'\n<script id="select-hinweis-js">\n{js}</script>\n'
    )

    MOCKUPS.mkdir(exist_ok=True)
    for page in PAGES:
        html = (ORIGINAL / page).read_text(encoding="utf-8")
        (MOCKUPS / page).write_text(html + snippet, encoding="utf-8")
        print(f"mockups/{page}")


if __name__ == "__main__":
    main()
