# Community-Shop – Pitch Health & Beauty

Eine scroll-gesteuerte Präsentation, mit der wir Influencerinnen und ihrem Management im Meeting den INCENT-Community-Shop vorstellen. Danach bekommen sie den Link mit.

- **Allgemein (Beauty):** https://dinosbs.github.io/pitch/beauty/ (die Startadresse https://dinosbs.github.io/pitch/ leitet dorthin weiter)
- **Ariel61:** https://dinosbs.github.io/pitch/ariel61/ – Shop vorgebaut mit eigenem Logo (`data/pitches/ariel61-logo.png`), Creme-Leiste, Buttons in #790b0a, cremefarbener Hintergrund
- **Yeliz Koc:** https://dinosbs.github.io/pitch/yelizkoc/ – eigenes Logo (`data/pitches/yelizkoc-logo.png`), überwiegend weiß mit schwarzen Akzenten

Persönliche Fassungen sollen nicht „vom Band“ aussehen. Deshalb wird je Fassung beim Build gewürfelt, mit festem Startwert, sodass jeder Build gleich aussieht:

- **Vorschau-Angebote:** Portal, Shop-Handy und Instagram-Shop zeigen eigene Beauty-Deals und Produkte. Keine zwei Fassungen teilen sich ein Angebot (`preview_sets`).
- **Reihenfolgen:** Partner-Deals im Laufband, Reiter und Produkte der Edits, Luxusmarken, Logo-Laufband und die Produkte bei „Zwei Gewinner“.
- **Einzelwerte:** Story-Produkt und Story-Text, Feed-Post, Startzeit am iPhone und die Start-Zielgruppe bei „Mehr als Beauty“. Zwei Fassungen bekommen hier nie denselben Wert (`pick_one`).

Die allgemeine Fassung behält die kuratierte Auswahl und Reihenfolge.

**Verdienst:** 70 % vom Gewinn jeder Bestellung. Alle Beträge rechnen mit 25 % Durchschnittsmarge (also 17,5 % vom Verkaufspreis). Auf den Folien steht dazu als Kleingedrucktes „*Durchschnittsmarge ist rund 25 %“.

Jeder Push auf `main` baut alle Fassungen neu und veröffentlicht sie über GitHub Pages (`.github/workflows/pages.yml`). Die Seiten sind mit `noindex, nofollow` markiert und erscheinen nicht in Suchmaschinen. Wer den Link hat, kann sie aber öffnen.

## So funktioniert die Präsentation

- **Feste 16:9-Bühne:** Jede Folie ist eine Fläche von 1600 × 900 Pixeln. Sie wächst mit dem Bildschirm bis 2560 × 1440 (1440p). Auf größeren Monitoren (4K, Ultrawide) bleibt sie in dieser Größe und wird nur zentriert. Leiste, Legende und Tastenhinweis liegen auf derselben Fläche und bleiben deshalb immer bündig mit den Folien.
- **Weiterschalten:** Mausrad, Trackpad, Wischen, Pfeiltasten, Bild↑/Bild↓, Leertaste, Pos1/Ende, Presenter oder Klick in der Legende.
  - Den Wechsel steuert die Präsentation selbst, nicht das Einrasten des Browsers. Jede Bewegung setzt sofort ein und läuft weich aus.
  - Der Nachlauf eines Trackpads löst keinen zweiten Wechsel aus.
- **Orientierung:**
  - Oben zeigt die Leiste die vier Kapitel (Dein Shop · Deine Community · Dein Verdienst · Dein Start) mit Fortschritt und die Foliennummer.
  - Die Leiste ist klickbar: Das INCENT-Logo springt zum Anfang, ein Kapitel zu seiner ersten Folie, die Foliennummer eine Folie weiter. „Für Name“ führt zum Gestalter.
  - Rechts steht die Legende. Bei Hover wird sie größer und zeigt Nummer und Titel jeder Folie.
- **Roter Faden:** Zuerst wird der Shop gestaltet, danach erscheint alles im gewählten Look: Portal, Handys, Produktkarten, iPhone-Mitteilungen und Instagram-Story.
- **Animationen:**
  - Überschriften bauen sich Wort für Wort auf, Inhalte laufen gestaffelt ein, Zahlen zählen hoch. Das passiert bei jedem Betreten einer Folie erneut.
  - Die alte Folie weicht in die Tiefe zurück, die neue schiebt sich darüber.
  - Endlos-Schleifen nutzen nur `transform` und `opacity` und pausieren außerhalb des Bildes.
  - Hover-Effekte (Karten, Logos, Deals) bleiben animiert.
- **Cursor:** Portal, Handys, Rechner-Karte und Aufgabenliste neigen sich zum Cursor, wie auf incent.de.
- **Am Handy (zum Nachlesen):** eine normale Scroll-Seite mit denselben Inhalten. Kompakte Abstände, im Einstieg das Shop-Handy statt des Desktop-Portals, Reiter zum Wischen, auf Tablets eine angenehme Lesebreite.
- **Foliennummern:** Die Nummer in den Überschriften stimmt immer mit der Nummer in der Leiste und in der Legende überein (app.js setzt sie aus der Reihenfolge der Folien).
- **Ohne Website-Elemente:** Es gibt keine „Shop anfragen“-Buttons. Die letzte Folie fasst alles zusammen und nennt den Link zum Wiederöffnen.

## Folien

| # | Kapitel | Folie | Inhalt |
| --- | --- | --- | --- |
| 01 | Dein Shop | Titel | „Dein eigener Beauty-Shop“: 80+ Beauty-Marken „und weit darüber hinaus“. Unten ragt schon das Portal ins Bild. |
| 02 | Dein Shop | Dein Shop | Das vorteile.net-Portal richtet sich in 3D auf. Bestellungen laufen ein, der Tageszähler steigt. |
| 03 | Dein Shop | Dein Look | Der Gestalter fährt ein: Logo, Name, Button- und Leistenfarbe und Hintergrund. Ohne Klick probiert eine Live-Demo selbst Looks durch. Ohne eigene Wahl kehrt beim Weiterschalten der Ausgangslook zurück. |
| 04 | Deine Community | Die Idee | Vorteilspreise, die sonst nur Mitarbeitende bekommen, dazu drei Schritte und Kennzahlen. |
| 05 | Deine Community | Markenvielfalt | Luxusmarken, „+ 70 weitere“, Kategorien, Laufband und „Und weit mehr als Beauty: 450+ Markenpartner“. |
| 06 | Deine Community | Partner-Deals | 30 echte Deals in zwei gegenläufigen Laufbändern (Hover hält eine Reihe an) und „46 exklusive Partner-Deals allein in Health & Beauty“. |
| 07 | Deine Community | Deine Edits | Sortimente in Reitern mit „+ X € für Dich“. Die Reiter wechseln von selbst, bis jemand klickt. |
| 08 | Deine Community | Mehr als Beauty | „Beauty ist erst der Anfang.“ Man wählt eine Zielgruppe, und die passenden Sortimentswelten leuchten auf. |
| 09 | Dein Verdienst | Ein Verkauf, zwei Gewinner | Echte Produkte von unter 10 € bis über 100 € wechseln sich ab, immer reihum aus vier Preisbereichen. Jeweils zu sehen: regulär → im Shop → Community spart → Du verdienst (70 % vom Gewinn bei rund 25 % Durchschnittsmarge). Darunter zählen Verkäufe und Verdienst mit: „… und das ohne einen Handgriff.“ Die Produkte stehen in `data/selection.json` unter `cycle`. |
| 10 | Dein Verdienst | Dein Potenzial | Rechner mit Reichweite, Kaufquote und Warenkorb. Die Beteiligung steht fest auf 70 % vom Gewinn, gerechnet mit rund 25 % Durchschnittsmarge. |
| 11 | Dein Verdienst | Null Aufwand | „Ihr müsst nichts tun.“ Aufgaben werden durchgestrichen und an INCENT übergeben. Der Aufwand zählt von 40 auf 0 Stunden. |
| 12 | Dein Verdienst | Passives Einkommen | iPhone-Sperrbildschirm im iOS-Stil. Unten ist eine Live-Aktivität angeheftet, die den Gewinn der Nacht mitzählt („Heute Nacht verdient“ mit dem letzten Betrag in Grün). Darüber schieben sich Bestellungen von unten ein, die Uhr läuft durch die Nacht. Als iOS-Schrift dient San Francisco, wo vorhanden, sonst das eingebettete Inter. |
| 13 | Dein Start | Reichweite & Bindung | Ein Handy mit Instagram, als 24-Sekunden-Schleife. Der Ablauf steht unter der Tabelle. |
| 14 | Dein Start | Dein Start | „Innerhalb einer Woche zur eigenen Plattform“, mit Tag 1 bis Live. Schritt 1 heißt: Sortiment auf die Zielgruppe zuschneiden. |
| 15 | Dein Start | Auf einen Blick | Zusammenfassung zum Mitnehmen („Beauty & weit mehr“) und Link zum Wiederöffnen. |

Ablauf der Instagram-Schleife auf Folie 13:

1. Story antippen.
2. Link antippen.
3. Der Webshop öffnet sich. Ein Produkt kommt in den Warenkorb („Zum Warenkorb hinzugefügt“, das Symbol zeigt 1).
4. Durch die Deals scrollen.
5. Warenkorb öffnen, „Zur Kasse“ antippen. Es erscheint „Bestellung abgeschlossen“ und neben dem Handy „+X € für Dich“.
6. Den Shop schließen. Zurück geht es zur Story, nach einer kurzen Pause zum Feed, und die Schleife beginnt von vorn.

Der Warenkorb ist im Stil von vorteile.net nachempfunden, die echte Warenkorb-Seite war nicht in der Shop-Speicherung enthalten.

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
  "hintergrundfarbe": null,
  "logo": "lena-logo.png",
  "beteiligung": 70,
  "marge": 25
}
```

| Feld | Bedeutung |
| --- | --- |
| `slug` | Adresse: `https://dinosbs.github.io/pitch/<slug>/`. Erlaubt sind nur a–z, 0–9 und Bindestrich. |
| `name` | erscheint überall: „Exklusiv für Lena“, Schriftzug im Portal, `lena.vorteile.net`, „Für Lena“ in der Leiste, „Lenas Shop“ auf dem iPhone, „Lenas Beauty-Shop.“ – leer lassen für die allgemeine Fassung |
| `farbe`, `nav` | Button- und Leistenfarbe: `blau`, `rose`, `beere`, `nude`, `salbei`, `lavendel`, `schwarz`, `weiss`, `puder`, `creme` oder ein Hex-Wert |
| `hintergrund` | `image` (Health-&-Beauty-Motiv), `solid` oder `gradient` |
| `logo` | optional: Logo-Datei in `data/pitches/`. Sie ersetzt den Schriftzug in allen Mockups. |
| `hintergrundfarbe` | optional: Hex-Wert für den einfarbigen Hintergrund (sonst aus der Buttonfarbe abgeleitet) |
| `beteiligung` | optional, Standard 70 (Prozent vom Gewinn) |
| `marge` | optional, Standard 25 (Durchschnittsmarge pro Produkt in Prozent) |

Danach `python3 build.py` ausführen (das erzeugt `pitches/<slug>/index.html`) und auf `main` pushen. Der Workflow veröffentlicht die Seite unter `/<slug>/`. Ein Eintrag ohne `name` ist die allgemeine Fassung (`beauty`).

Für schnelle Tests geht es auch ohne neuen Build: `pitches/beauty/index.html?name=Lena&farbe=rose&nav=schwarz&hintergrund=verlauf`

## Anpassen

- **Beteiligung, Beispiel-Marge, Preisstand, Farben im Gestalter:** oben in `build.py` (`SHARE`, `MARGIN` = Durchschnittsmarge, `SNAPSHOT_DATE`, `BTN_COLORS`, `NAV_COLORS`)
- **Produkte und Deals:** `data/selection.json` (Marke + exakter Titel aus `data/catalog.json`). Die ersten 30 Deals füllen die zwei Laufbänder (`DEAL_ROW` in `build.py`), `cycle` legt die Produkte je Preisklasse fest. Die Bilder holt `tools/extract.py`.
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
index.html                  Weiterleitung auf /beauty/ (generiert)
pitches/<slug>/index.html   je Fassung: beauty, ariel61, yelizkoc (generiert, alles eingebettet, offline-fähig)
build.py                    baut alle Fassungen aus src/ + data/ + assets/
tools/extract.py            liest eine SingleFile-Speicherung des Shops aus
src/                        template.html, style.css, app.js, icons.svg
data/                       catalog.json, deals.json, brands.json, selection.json, pitches.json, pitches/ (Logos)
assets/                     products/, deals/, logos/, ui/ (INCENT-Logos, Zahlungsarten, Kategorie-Hintergrund), fonts/ (Barlow Semi Condensed, Inter – beide SIL OFL)
screenshots/                Vorschaubilder
.github/workflows/pages.yml baut und veröffentlicht auf GitHub Pages
```

## Hinweise zu den Zahlen

- Preise, Vergleichspreise („Regulär“) und Rabatte sind eine Momentaufnahme vom 01.11.2026 aus dem INCENT-Vorteilsportal, Kategorie Health & Beauty.
- „80+ Marken“, „250+ Produkte“, „bis 71 %“, „46 Partner-Deals“ und „Ø 27 %“ sind aus diesen Daten berechnet. „4.400 Unternehmen“, „450+ Markenpartner“, „3.000+ Markenprodukte“ und „70+ Partnergutscheine“ stammen von incent.de.
- Die Beteiligung beträgt 70 % vom Gewinn. Alle Verdienst-Beträge rechnen mit rund 25 % Durchschnittsmarge (70 % davon = 17,5 % vom Verkaufspreis). Reichweiten- und Umsatzwerte im Rechner sowie das Diagramm sind als Beispiel bzw. schematisch gekennzeichnet.
