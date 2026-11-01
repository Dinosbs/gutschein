# Community-Shop – Pitch Health & Beauty

Eine scroll-gesteuerte Präsentation, mit der wir Influencerinnen und ihrem Management im Meeting den INCENT-Community-Shop vorstellen. Danach bekommen sie den Link mit.

- **Live (allgemein):** https://dinosbs.github.io/pitch/
- **Sublink je Influencerin:** https://dinosbs.github.io/pitch/beispiel/ (Beispiel „Lena“, siehe unten)

Jeder Push auf `main` baut alle Fassungen neu und veröffentlicht sie über GitHub Pages (`.github/workflows/pages.yml`). Die Seiten sind mit `noindex, nofollow` markiert und erscheinen nicht in Suchmaschinen. Wer den Link hat, kann sie aber öffnen.

## So funktioniert die Präsentation

- **Am Desktop und Beamer (Querformat):** Jede Folie füllt den Bildschirm und rastet beim Scrollen ein. Ihre Inhalte laufen nacheinander ein, sobald die Folie erscheint, und das bei jedem erneuten Betreten. Jede Folie wird automatisch auf die Fensterhöhe eingepasst, von 1280 × 720 bis 1920 × 1080.
- **Weiterschalten:** Mausrad oder Trackpad, Pfeiltasten ↑ ↓, Bild↑/Bild↓, Leertaste oder Presenter. Oben zeigt die Präsentationsleiste das Kapitel und die Foliennummer (z. B. „04 Dein Verdienst · 5/14“). Rechts stehen Sprungpunkte zu jeder Folie.
- **Titel:** Beim ersten Scrollen steigt das vorteile.net-Portal auf und richtet sich auf. Dazu laufen Bestellungen ein („Neue Bestellung · +10,60 €“).
- **Cursor:** Portal, Handy, Rechner-Karte, Aufgabenliste und Diagramm neigen sich zum Cursor, so wie auf incent.de.
- **Am Handy (zum Nachlesen):** eine normale Scroll-Seite mit denselben Inhalten.
- **Ohne Website-Elemente:** Es gibt keine „Shop anfragen“-Buttons. Die letzte Folie fasst alles zusammen und nennt den Link zum Wiederöffnen.

## Folien

| # | Folie | Inhalt |
| --- | --- | --- |
| – | Titel → Dein Shop | „Dein eigener Beauty-Shop“. Danach erscheint der Shop auf vorteile.net in 3D, mit laufenden Bestellungen. |
| 01 | Die Idee | Vorteilspreise, die sonst nur Mitarbeitende bekommen, dazu drei Schritte und Kennzahlen. |
| 02 | Ein Verkauf, zwei Gewinner | Lancôme: regulär 156 €, im Shop 105,95 €. Die Community spart 50,05 €, Du verdienst 10,60 €. |
| 03 | Dein Look | Live-Gestalter: Logo, Name, Button- und Leistenfarbe, Hintergrund. Desktop und Handy ändern sich sofort mit. |
| 04 | Dein Verdienst | Sechs echte Produkte mit **fest 10 %** Beteiligung. |
| 05 | Dein Potenzial | Rechner mit Reichweite, Kaufquote und Warenkorb. Die Beteiligung steht fest auf 10 %. |
| 06 | Null Aufwand | „Ihr müsst nichts tun.“ Aufgaben, die sonst anfallen, werden durchgestrichen, INCENT übernimmt sie. Laufender Aufwand: 0 Stunden. |
| 07 | Passives Einkommen | „Verdienen, während Du schläfst.“ Ein Sperrbildschirm mit Bestellungen der Nacht und ein Vergleich Brand Deals ↔ Shop (schematisch). |
| 08 | Markenvielfalt | Luxusmarken, „+70 weitere“, Kategorien, Laufband und „Und vieles mehr: 450+ Markenpartner auf vorteile.net“. |
| 09 | Deine Edits | Sortimente in Reitern, mit „+ X € für Dich“ an jedem Produkt. |
| 10 | Partner-Deals | Acht Angebotskacheln im vorteile.net-Look. |
| 11 | Reichweite & Bindung | Story → Link → Shop, dazu vier Vorteile. |
| 12 | Dein Start | „Innerhalb einer Woche zur eigenen Plattform“, mit Tag 1 bis Live. |
| – | Auf einen Blick | Zusammenfassung zum Mitnehmen und Link zum Wiederöffnen. |

## Sublinks je Influencerin

Für jeden Pitch kommt ein Eintrag in `data/pitches.json`:

```json
{
  "slug": "lena",
  "name": "Lena",
  "farbe": "rose",
  "nav": "weiss",
  "hintergrund": "image",
  "logo": "lena-logo.png",
  "beteiligung": 10
}
```

| Feld | Bedeutung |
| --- | --- |
| `slug` | Adresse: `https://dinosbs.github.io/pitch/<slug>/`. Erlaubt sind nur a–z, 0–9 und Bindestrich. |
| `name` | erscheint überall: „Exklusiv für Lena“, Schriftzug im Portal, `lena.vorteile.net`, „Für Lena“ in der Leiste, „Lenas Beauty-Shop.“ |
| `farbe`, `nav` | Button- und Leistenfarbe: `blau`, `rose`, `beere`, `nude`, `salbei`, `lavendel`, `schwarz`, `weiss`, `puder`, `creme` oder ein Hex-Wert |
| `hintergrund` | `image` (Health-&-Beauty-Motiv), `solid` oder `gradient` |
| `logo` | optional: Logo-Datei in `data/pitches/`. Sie ersetzt den Schriftzug in allen Mockups. |
| `beteiligung` | optional, Standard 10 (Prozent) |

Danach `python3 build.py` ausführen (das erzeugt `pitches/<slug>/index.html`) und auf `main` pushen. Der Workflow veröffentlicht die Seite unter `/<slug>/`. Der Eintrag `beispiel` ist nur eine Vorlage und kann gelöscht werden.

Für schnelle Tests geht es auch ohne neuen Build: `index.html?name=Lena&farbe=rose&nav=schwarz&hintergrund=verlauf`

## Anpassen

- **Beteiligung, Preisstand, Farben im Gestalter:** oben in `build.py` (`RATE`, `SNAPSHOT_DATE`, `BTN_COLORS`, `NAV_COLORS`)
- **Produkte und Deals:** `data/selection.json` (Marke + exakter Titel aus `data/catalog.json`)
- **Texte und Folien:** `src/template.html`. Design: `src/style.css`. Ablauf und Animationen: `src/app.js`. Icons: `src/icons.svg`.

```
python3 build.py
```

## Daten aus einer neuen Shop-Speicherung holen

Seite im INCENT-Shop komplett aufklappen und mit SingleFile speichern, dann:

```
pip install pillow
python3 tools/extract.py "/pfad/zu/Health & Beauty - incent.html"
python3 build.py
```

## Aufbau

```
index.html                  allgemeine Fassung (generiert, alles eingebettet, offline-fähig)
pitches/<slug>/index.html   Fassung je Influencerin (generiert)
build.py                    baut alle Fassungen aus src/ + data/ + assets/
tools/extract.py            liest eine SingleFile-Speicherung des Shops aus
src/                        template.html, style.css, app.js, icons.svg
data/                       catalog.json, deals.json, brands.json, selection.json, pitches.json, pitches/ (Logos)
assets/                     products/, deals/, logos/, ui/ (INCENT-Logos, Zahlungsarten, Kategorie-Hintergrund), fonts/
screenshots/                Vorschaubilder
.github/workflows/pages.yml baut und veröffentlicht auf GitHub Pages
```

## Hinweise zu den Zahlen

- Preise, Vergleichspreise („Regulär“) und Rabatte sind eine Momentaufnahme vom 01.11.2026 aus dem INCENT-Vorteilsportal, Kategorie Health & Beauty.
- „80+ Marken“, „250+ Produkte“, „bis 71 %“, „46 Partner-Deals“ und „Ø 27 %“ sind aus diesen Daten berechnet. „4.400 Unternehmen“, „450+ Markenpartner“, „3.000+ Markenprodukte“ und „70+ Partnergutscheine“ stammen von incent.de.
- Die Beteiligung ist fest mit 10 % angesetzt. Reichweiten- und Umsatzwerte im Rechner sowie das Diagramm sind als Beispiel bzw. schematisch gekennzeichnet.
