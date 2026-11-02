# Community-Shop – Pitch Health & Beauty

Eine scroll-gesteuerte Präsentation, mit der wir Influencerinnen und ihrem Management im Meeting den INCENT-Community-Shop vorstellen. Danach bekommen sie den Link mit.

- **Live (allgemein):** https://dinosbs.github.io/pitch/
- **Sublink je Influencerin:** https://dinosbs.github.io/pitch/beispiel/ (Beispiel „Lena“, siehe unten)

Jeder Push auf `main` baut alle Fassungen neu und veröffentlicht sie über GitHub Pages (`.github/workflows/pages.yml`). Die Seiten sind mit `noindex, nofollow` markiert und erscheinen nicht in Suchmaschinen. Wer den Link hat, kann sie aber öffnen.

## So funktioniert die Präsentation

- **Feste 16:9-Bühne:** Jede Folie ist eine Fläche von 1600 × 900 Pixeln. Sie wächst mit dem Bildschirm bis 2560 × 1440 (1440p). Auf größeren Monitoren (4K, Ultrawide) bleibt sie in dieser Größe und wird nur zentriert. Leiste, Legende und Tastenhinweis liegen auf derselben Fläche und bleiben deshalb immer bündig mit den Folien.
- **Weiterschalten:** Mausrad, Trackpad, Wischen, Pfeiltasten, Bild↑/Bild↓, Leertaste, Pos1/Ende, Presenter oder Klick in der Legende.
  - Den Wechsel steuert die Präsentation selbst, nicht das Einrasten des Browsers. Jede Bewegung setzt sofort ein und läuft weich aus.
  - Der Nachlauf eines Trackpads löst keinen zweiten Wechsel aus.
- **Orientierung:**
  - Oben zeigt die Leiste die vier Kapitel (Dein Shop · Deine Community · Dein Verdienst · Dein Start) mit Fortschritt und die Foliennummer.
  - Rechts steht die Legende. Bei Hover wird sie größer und zeigt Nummer und Titel jeder Folie.
- **Roter Faden:** Zuerst wird der Shop gestaltet, danach erscheint alles im gewählten Look: Portal, Handys, Produktkarten, iPhone-Mitteilungen und Instagram-Story.
- **Animationen:**
  - Überschriften bauen sich Wort für Wort auf, Inhalte laufen gestaffelt ein, Zahlen zählen hoch. Das passiert bei jedem Betreten einer Folie erneut.
  - Die alte Folie weicht in die Tiefe zurück, die neue schiebt sich darüber.
  - Endlos-Schleifen nutzen nur `transform` und `opacity` und pausieren außerhalb des Bildes.
  - Hover-Effekte (Karten, Logos, Deals) bleiben animiert.
- **Cursor:** Portal, Handys, Rechner-Karte und Aufgabenliste neigen sich zum Cursor, wie auf incent.de.
- **Am Handy (zum Nachlesen):** eine normale Scroll-Seite mit denselben Inhalten.
- **Ohne Website-Elemente:** Es gibt keine „Shop anfragen“-Buttons. Die letzte Folie fasst alles zusammen und nennt den Link zum Wiederöffnen.

## Folien

| # | Kapitel | Folie | Inhalt |
| --- | --- | --- | --- |
| 01 | Dein Shop | Titel | „Dein eigener Beauty-Shop“: 80+ Beauty-Marken „und weit darüber hinaus“. Unten ragt schon das Portal ins Bild. |
| 02 | Dein Shop | Dein Shop | Das vorteile.net-Portal richtet sich in 3D auf. Bestellungen laufen ein, der Tageszähler steigt. |
| 03 | Dein Shop | Dein Look | Der Gestalter fährt ein: Logo, Name, Button- und Leistenfarbe und Hintergrund. Ohne Klick probiert eine Live-Demo selbst Looks durch. Ohne eigene Wahl kehrt beim Weiterschalten der Ausgangslook zurück. |
| 04 | Deine Community | Die Idee | Vorteilspreise, die sonst nur Mitarbeitende bekommen, dazu drei Schritte und Kennzahlen. |
| 05 | Deine Community | Markenvielfalt | Luxusmarken, „+ 70 weitere“, Kategorien, Laufband und „Und weit mehr als Beauty: 450+ Markenpartner“. |
| 06 | Deine Community | Partner-Deals | 30 echte Deals in zwei gegenläufigen Laufbändern (Hover hält eine Reihe an), dazu „46 exklusive Partner-Deals allein in Health & Beauty“. |
| 07 | Deine Community | Deine Edits | Sortimente in Reitern mit „+ X € für Dich“. Die Reiter wechseln von selbst, bis jemand klickt. |
| 08 | Deine Community | Mehr als Beauty | „Beauty ist erst der Anfang.“ Man wählt eine Zielgruppe (Beauty, Fitness, Family, Lifestyle), und die passenden Sortimentswelten leuchten auf. Die Auswahl wechselt von selbst, bis jemand klickt. |
| 09 | Dein Verdienst | Zwei Gewinner | Lancôme: regulär 156 €, im Shop 105,95 €. Die Community spart 50,05 €, Du verdienst 10,60 €. |
| 10 | Dein Verdienst | Dein Verdienst | Sechs echte Produkte mit **fest 10 %** Beteiligung. |
| 11 | Dein Verdienst | Dein Potenzial | Rechner mit Reichweite, Kaufquote und Warenkorb. Die Beteiligung steht fest auf 10 %. |
| 12 | Dein Verdienst | Null Aufwand | „Ihr müsst nichts tun.“ Aufgaben werden durchgestrichen und an INCENT übergeben. Der Aufwand zählt von 40 auf 0 Stunden. |
| 13 | Dein Verdienst | Passives Einkommen | iPhone-Sperrbildschirm im iOS-Stil. Mitteilungen („+8,40 € für Dich“) schieben sich fortlaufend von unten ein, der ganze Stapel gleitet hoch, oben blendet die älteste aus. Uhr, Summe und Bestellzähler laufen mit. |
| 14 | Dein Start | Reichweite & Bindung | Ein Handy mit Instagram, als Schleife: Story antippen → Link antippen → Webshop öffnet sich, Deals und Produkte werden durchgescrollt → Shop schließen → zurück zur Story → kurze Pause → von vorn. Die vier Schritte darunter leuchten synchron mit. |
| 15 | Dein Start | Dein Start | „Innerhalb einer Woche zur eigenen Plattform“, mit Tag 1 bis Live. Schritt 1 heißt: Sortiment auf die Zielgruppe zuschneiden. |
| 16 | Dein Start | Auf einen Blick | Zusammenfassung zum Mitnehmen („Beauty & weit mehr“) und Link zum Wiederöffnen. |

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
- **Produkte und Deals:** `data/selection.json` (Marke + exakter Titel aus `data/catalog.json`). Die ersten 30 Deals füllen die zwei Laufbänder (`DEAL_ROW` in `build.py`). Ihre Bilder holt `tools/extract.py`.
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
