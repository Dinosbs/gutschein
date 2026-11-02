# Community-Shop – Pitch Health & Beauty

Eine scroll-gesteuerte Präsentation, mit der wir Influencerinnen und ihrem Management im Meeting den INCENT-Community-Shop vorstellen. Danach bekommen sie den Link mit.

- **Live (allgemein):** https://dinosbs.github.io/pitch/
- **Sublink je Influencerin:** https://dinosbs.github.io/pitch/beispiel/ (Beispiel „Lena“, siehe unten)

Jeder Push auf `main` baut alle Fassungen neu und veröffentlicht sie über GitHub Pages (`.github/workflows/pages.yml`). Die Seiten sind mit `noindex, nofollow` markiert und erscheinen nicht in Suchmaschinen. Wer den Link hat, kann sie aber öffnen.

## So funktioniert die Präsentation

- **Feste 16:9-Bühne:** Jede Folie ist eine Fläche von 1600 × 900 Pixeln, die auf jeden Bildschirm skaliert und zentriert wird. Das gilt von 1280 × 720 über 1920 × 1080 bis 4K und Ultrawide. Bei abweichendem Seitenverhältnis entstehen ruhige Ränder, nichts wird abgeschnitten.
- **Weiterschalten:** Mausrad oder Trackpad, Pfeiltasten, Bild↑/Bild↓, Leertaste, Pos1/Ende oder Presenter. Jede Folie rastet ein.
- **Orientierung:**
  - Oben zeigt die Leiste die vier Kapitel (Dein Shop · Deine Community · Dein Verdienst · Dein Start), jeweils mit Fortschrittsbalken, dazu die Foliennummer (z. B. „09 / 15“).
  - Rechts steht die Legende. Fährt man mit der Maus darüber, wird sie größer und zeigt Nummer und Titel jeder Folie. Ein Klick springt direkt dorthin.
- **Roter Faden:** Zuerst wird der Shop gestaltet, danach erscheint alles im gewählten Look: Portal, Handys, Produktkarten und iPhone-Mitteilungen.
- **Animationen:**
  - Überschriften bauen sich Wort für Wort auf, Inhalte laufen gestaffelt ein, Zahlen zählen hoch. Das passiert bei jedem Betreten einer Folie erneut.
  - Beim Weiterschalten weicht die alte Folie in die Tiefe zurück, die neue schiebt sich darüber.
  - Dazu laufen Endlos-Schleifen: Bestellungen am Portal, iPhone-Mitteilungen, Glanz auf Verlaufsschrift, Laufband, Ken-Burns auf den Deals, wechselnde Edits und anderes.
  - Schleifen nutzen nur `transform` und `opacity` und pausieren auf Folien außerhalb des Bildes. So kann man jederzeit vor- und zurückspringen.
- **Cursor:** Portal, Handys, Rechner-Karte, Aufgabenliste und Produktkarten neigen sich zum Cursor, wie auf incent.de.
- **Am Handy (zum Nachlesen):** eine normale Scroll-Seite mit denselben Inhalten.
- **Ohne Website-Elemente:** Es gibt keine „Shop anfragen“-Buttons. Die letzte Folie fasst alles zusammen und nennt den Link zum Wiederöffnen.

## Folien

| # | Kapitel | Folie | Inhalt |
| --- | --- | --- | --- |
| 01 | Dein Shop | Titel | „Dein eigener Beauty-Shop“. Unten ragt schon das Portal ins Bild. |
| 02 | Dein Shop | Dein Shop | Das vorteile.net-Portal richtet sich in 3D auf. Bestellungen laufen ein („+10,60 €“), der Tageszähler steigt. |
| 03 | Dein Shop | Dein Look | Der Gestalter fährt von links ein, das Handy von unten. Gestaltbar sind Logo, Name, Button- und Leistenfarbe und Hintergrund. Ohne Klick probiert eine Live-Demo selbst Looks durch. Verlässt man die Folie ohne eigene Wahl, kehrt der Ausgangslook zurück. |
| 04 | Deine Community | Die Idee | Vorteilspreise, die sonst nur Mitarbeitende bekommen, dazu drei Schritte und Kennzahlen. |
| 05 | Deine Community | Markenvielfalt | Luxusmarken, „+ 70 weitere“, Kategorien, Laufband und „Und vieles mehr: 450+ Markenpartner auf vorteile.net“. |
| 06 | Deine Community | Deine Edits | Sortimente in Reitern mit „+ X € für Dich“. Die Reiter wechseln von selbst, bis jemand klickt. |
| 07 | Deine Community | Partner-Deals | Acht Angebotskacheln im vorteile.net-Look. |
| 08 | Dein Verdienst | Zwei Gewinner | Lancôme: regulär 156 € (durchgestrichen), im Shop 105,95 €. Die Community spart 50,05 €, Du verdienst 10,60 €. Alle Beträge zählen live. |
| 09 | Dein Verdienst | Dein Verdienst | Sechs echte Produkte mit **fest 10 %** Beteiligung. |
| 10 | Dein Verdienst | Dein Potenzial | Rechner mit Reichweite, Kaufquote und Warenkorb. Die Beteiligung steht fest auf 10 %. |
| 11 | Dein Verdienst | Null Aufwand | „Ihr müsst nichts tun.“ Aufgaben werden nacheinander durchgestrichen und an INCENT übergeben. Der Aufwand zählt von 40 auf 0 Stunden. |
| 12 | Dein Verdienst | Passives Einkommen | Ein iPhone-Sperrbildschirm im iOS-Stil. Fortlaufend schieben sich Mitteilungen von unten ein („Neue Bestellung · +8,40 €“), die Uhr läuft durch die Nacht, Summe und Bestellzähler steigen. Dazu ein Vergleich Brand Deals ↔ Shop (schematisch). |
| 13 | Dein Start | Reichweite & Bindung | Story → Link → Shop, dazu vier Vorteile. |
| 14 | Dein Start | Dein Start | „Innerhalb einer Woche zur eigenen Plattform“, mit Tag 1 bis Live. |
| 15 | Dein Start | Auf einen Blick | Zusammenfassung zum Mitnehmen und Link zum Wiederöffnen. |

Vorschaubilder liegen in `screenshots/`.

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
| `name` | erscheint überall: „Exklusiv für Lena“, Schriftzug im Portal, `lena.vorteile.net`, „Für Lena“ in der Leiste, „Lenas Shop“ in den iPhone-Mitteilungen, „Lenas Beauty-Shop.“ |
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
- **Neue Folie:** `<section class="slide" data-act="…" data-snap data-label="…">` mit `.shell > .bg + .frame > .frame__in > .content`. Legende, Zähler und Kapitelbalken übernehmen sie automatisch. Inhalte werden in Canvas-Pixeln (1600 × 900) gestaltet. Passt eine Folie nicht ganz, verkleinert app.js nur ihren Inhalt.

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
