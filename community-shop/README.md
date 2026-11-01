# Community Shop – Pitch Health & Beauty

One-Pager im Präsentationsstil für den Pitch des INCENT Community Shops an Creator aus dem Bereich Health & Beauty. Alle Produkte, Preise, Deals und Logos stammen aus einer Speicherung der Kategorie „Health & Beauty“ im INCENT-Shop vom 01.11.2026.

**Ansehen:** `index.html` im Browser öffnen. Die Datei ist komplett eigenständig (Bilder und Schriften eingebettet, ca. 3,7 MB) und funktioniert offline. Man kann sie also auch einfach per Mail oder Link verschicken.

## Folien

| # | Folie | Inhalt |
| --- | --- | --- |
| – | Start | „Dein eigener Beauty-Shop.“ Handy-Mockup des Creator-Shops mit Live-Benachrichtigungen („Neue Bestellung · +10,60 €“) und Zähler „Heute verdient“. |
| 01 | Die Idee | Vorteilspreise, die sonst nur Mitarbeitende bekommen, jetzt für die Community. Drei Schritte und ein Rechenbeispiel: regulärer Preis → Shop-Preis → Ersparnis der Community → Verdienst. |
| 02 | Dein Look | Live-Gestalter: Shop-Name, Farbwelt, Schrift und Bildwelt ändern die Shop-Vorschau sofort, inklusive Adresse `deinname.vorteile.net`. |
| 03 | Verdienst | Sechs echte Produkte mit Ersparnis und Verdienst pro Verkauf. Der Provisionsregler (5–20 %) rechnet alle Beträge auf der Seite live um. |
| 04 | Rechner | Reichweite, Kaufquote, Ø Warenkorb, Provision → Verdienst pro Monat und Jahr. Dazu Profile Micro, Mid und Macro. |
| 05 | Marken | Laufband mit Luxusmarken, Produktzahl je Kategorie und eine Logowand mit 82 Marken. |
| 06 | Edits | Sortimentsbeispiele in fünf Tabs (Scents, Skin, Beauty Tech, Hair, Gifting), jeweils mit „+ X € für dich“. |
| 07 | Partner-Deals | Zwölf Beauty-Deals mit Bildern (Shiseido, NARS, ghd, Rituals …). |
| 08 | Reichweite | Story-Mockup und die Vorteile: Content-Anlässe, Bindung, Mehrwert statt Werbung, Sichtbarkeit für Marken, Saisonalität. |
| 09 | Service | Aufgabenteilung Du / INCENT, Zahlungsarten und ein Beispiel-Dashboard. Das Dashboard übernimmt die Werte aus dem Rechner. |
| 10 | Los geht’s | Drei Schritte zum Launch und ein Call-to-Action. |

**Präsentieren:** Mit den Pfeiltasten ↑ ↓ oder Bild↑/Bild↓ (also auch mit einem Presenter) springt man von Folie zu Folie. Bei langen Folien wird erst innerhalb der Folie weitergeblättert. Rechts zeigen Punkte, auf welcher Folie man gerade ist.

## Für eine bestimmte Creatorin personalisieren

Die Seite bleibt allgemein. Über URL-Parameter lässt sie sich aber für einen Pitch vorbelegen, ohne neu zu bauen:

```
index.html?name=Lena&farbe=salbei&provision=12&reichweite=250000
```

| Parameter | Wirkung |
| --- | --- |
| `name` | Shop-Name in allen Mockups, Adresse `lena.vorteile.net`, „Lenas Beauty Edit“, Story-Handle |
| `farbe` | `rose`, `nude`, `salbei`, `lavendel` oder `noir` |
| `provision` | Startwert des Provisionsreglers in Prozent (5–20) |
| `reichweite` | Startwert der Reichweite im Rechner |

## Anpassen

- **Provision beim Öffnen, Kontaktadresse, Preisstand:** oben in `build.py` (`DEFAULT_RATE`, `CONTACT_MAIL`, `SNAPSHOT_DATE`). Ist `CONTACT_MAIL` leer, öffnet „Lass uns sprechen“ eine Mail ohne Empfänger.
- **Welche Produkte und Deals gezeigt werden:** `data/selection.json` (Marke + exakter Titel aus `data/catalog.json`).
- **Texte und Aufbau:** `src/template.html`. Design: `src/style.css`. Interaktion: `src/app.js`.

Nach jeder Änderung neu bauen:

```
python3 build.py
```

## Daten aus einer neuen Shop-Speicherung holen

Seite im Shop komplett aufklappen und mit SingleFile speichern, dann:

```
pip install pillow
python3 tools/extract.py "/pfad/zu/Health & Beauty - incent.html"
python3 build.py
```

`extract.py` schreibt `data/catalog.json` (alle Produkte), `data/deals.json`, `data/brands.json` und die Bilder nach `assets/`. Produktbilder werden nur für Produkte aus `data/selection.json` exportiert.

## Aufbau

```
index.html            fertige Seite (generiert, alles eingebettet)
build.py              baut index.html aus src/ + data/ + assets/
tools/extract.py      liest eine SingleFile-Speicherung des Shops aus
src/                  template.html, style.css, app.js
data/                 catalog.json, deals.json, brands.json, selection.json
assets/               products/, deals/, logos/, ui/, fonts/ (Cormorant Garamond + Inter, OFL)
```

## Hinweise zu den Zahlen

- Preise, Vergleichspreise („Regulär“) und Rabatte sind eine Momentaufnahme vom 01.11.2026.
- „80+ Marken“, „250+ Produkte“, „bis 71 %“, „46 Partner-Deals“ und „Ø 27 %“ sind direkt aus den Shop-Daten berechnet.
- Provision (Standard 10 %), Kaufquote und Warenkorb sind **Beispielwerte**. Die Seite kennzeichnet sie als Beispielrechnung. Die echten Konditionen vor dem Pitch prüfen und gegebenenfalls `DEFAULT_RATE` anpassen.
