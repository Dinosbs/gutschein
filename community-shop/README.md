# Community-Shop – Pitch

Eine scroll-gesteuerte Präsentation, mit der wir Influencerinnen und Influencern und ihrem Management im Meeting den INCENT-Community-Shop vorstellen. Danach bekommen sie den Link mit.

- **Allgemein:** https://dinosbs.github.io/pitch/ – das ganze Portal: 15 Welten, 450+ Marken, große Top-Deals. Unisex, nicht auf eine Zielgruppe zugeschnitten (Thema `allgemein`).
- **Beauty:** https://dinosbs.github.io/pitch/beauty/ – die Fassung für Health & Beauty (Thema `beauty`).
- **Ariel61:** https://dinosbs.github.io/pitch/ariel61/ (Beauty) – Shop vorgebaut mit eigenem Logo (`data/pitches/ariel61-logo.png`), eigenem Hintergrundbild (`data/pitches/ariel61-hintergrund.jpg`, dunkel → helle Überschrift), Creme-Leiste, Buttons in #790b0a, Rechner startet mit 410.000 Followern
- **Yeliz Koc:** https://dinosbs.github.io/pitch/yelizkoc/ (Beauty) – eigenes Logo (`data/pitches/yelizkoc-logo.png`), eigenes Hintergrundbild im Shop (`data/pitches/yelizkoc-hintergrund.jpg`), überwiegend weiß mit schwarzen Akzenten, Rechner startet mit 875.000 Followern

Persönliche Fassungen sollen nicht „vom Band“ aussehen. Deshalb wird je Fassung beim Build gewürfelt, mit festem Startwert, sodass jeder Build gleich aussieht:

- **Vorschau-Angebote:** Portal, Shop-Handy und Instagram-Shop zeigen eigene Beauty-Deals und Produkte. Keine zwei Fassungen teilen sich ein Angebot (`preview_sets`).
- **Reihenfolgen:** Partner-Deals im Laufband, Reiter und Produkte der Edits, Luxusmarken, Logo-Laufband und die Produkte bei „Zwei Gewinner“.
- **Einzelwerte:** Story-Produkt und Story-Text, Feed-Post, Startzeit am iPhone und die Start-Zielgruppe bei „Mehr als Beauty“. Zwei Fassungen bekommen hier nie denselben Wert (`pick_one`).

Die Fassungen ohne Namen (Startseite und `/beauty/`) behalten die kuratierte Auswahl und Reihenfolge.

**Verdienst:** 70 % vom Gewinn jeder Bestellung. Alle Beträge rechnen mit 25 % Durchschnittsmarge (also 17,5 % vom Verkaufspreis). Auf den Folien steht dazu als Kleingedrucktes „*Durchschnittsmarge ist rund 25 %“.

Jeder Push auf `main` baut alle Fassungen neu und veröffentlicht sie über GitHub Pages (`.github/workflows/pages.yml`). Die Seiten sind mit `noindex, nofollow` markiert und erscheinen nicht in Suchmaschinen. Wer den Link hat, kann sie aber öffnen.

## Zwei Themen: allgemein und beauty

Beide Themen nutzen dieselbe Vorlage, dieselben Animationen und denselben Ablauf. Das Thema bestimmt Texte, Daten und einige Folien:

| | `allgemein` (Startseite) | `beauty` |
| --- | --- | --- |
| Titel | „Dein eigener Vorteils-Shop“ · Community-Shop · 15 Welten · 450+ Marken | „Dein eigener Beauty-Shop“ · Health & Beauty |
| Daten | `data/general/` (sechs Kategorien), Bilder in `assets/general/` | `data/` (Health & Beauty), Bilder in `assets/` |
| Folie 05 | **15 Welten:** alle Kategorien des Portals mit Unterkategorien und „bis X %“; man wählt eine Zielgruppe, die passenden Welten leuchten auf | Markenvielfalt (Beauty-Luxusmarken) |
| Folie 06 | **Top-Deals:** vier große Deal-Karten, die reihum wechseln (Rabatt zählt hoch), darunter zwei Laufbänder mit 28 Deals | Partner-Deals (Laufbänder) |
| Folie 07 | Markenvielfalt: Apple bis Sixt, „Top-Rabatt je Welt“, zwei Logo-Laufbänder | Deine Edits |
| Folie 08 | Deine Edits: Technik, Home & Living, Reisen & Gepäck, Sport & Fitness, Mobilität, Health & Beauty | Mehr als Beauty |

In `src/template.html` stehen themenabhängige Teile in `<!--@if allgemein-->…<!--@end-->` bzw. `<!--@if beauty-->…<!--@end-->`, kurze Texte als `<!--@t:schlüssel-->` (Werte in `THEMES` in `build.py`). Das `<html>`-Element trägt `data-thema`, damit `style.css` Feinheiten je Thema setzen kann.

**Auswahl der allgemeinen Fassung** (`data/general/selection.json`): bekannte Marken mit hohem Rabatt, quer durch alle Welten und bewusst unisex – nichts, was nur Frauen oder nur Männer anspricht (keine Damen-/Herrenmode, Rasierer oder Make-up in den Hauptplätzen). Spielzeug und reine Kinderartikel bleiben draußen, ebenso Logos, die auf weißem Grund schlecht lesbar sind.

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

## Folien (allgemeine Fassung)

| # | Kapitel | Folie | Inhalt |
| --- | --- | --- | --- |
| 01 | Dein Shop | Titel | „Dein eigener Vorteils-Shop“: über 450 Marken in 15 Welten. Unten ragt schon das Portal ins Bild. |
| 02 | Dein Shop | Dein Shop | Das vorteile.net-Portal richtet sich in 3D auf. Bestellungen laufen ein, der Tageszähler steigt. |
| 03 | Dein Shop | Dein Look | Der Gestalter fährt ein: Logo, Name, Button- und Leistenfarbe und Hintergrund. Ohne Klick probiert eine Live-Demo selbst Looks durch. Ohne eigene Wahl kehrt beim Weiterschalten der Ausgangslook zurück. |
| 04 | Deine Community | Die Idee | Vorteilspreise, die sonst nur Mitarbeitende bekommen, dazu drei Schritte und Kennzahlen (450+ Markenpartner, 3.000+ Produkte, bis 83 %, 15 Welten). |
| 05 | Deine Community | 15 Welten | „Ein Shop. 15 Welten.“ Alle Kategorien mit Unterkategorien und Top-Rabatt. Links wählt man die Zielgruppe (Tech & Gaming, Sport & Outdoor, Familie & Zuhause, Reisen & Lifestyle, Beauty & Wellness), rechts leuchten die passenden Welten auf. |
| 06 | Deine Community | Top-Deals | „Deals, die es sonst nirgends gibt.“ Vier große Karten (z. B. Bitdefender 60 %, P&G bis 66 %, FINN bis 3.033 €, Sony bis 45 %) wechseln reihum, der Rabatt zählt hoch. Darunter zwei gegenläufige Laufbänder und „150+ exklusive Partner-Deals“. |
| 07 | Deine Community | Markenvielfalt | Apple, Samsung, Sony, Dyson, Nintendo, Bose, adidas, Nike, Puma, Bosch, Sixt und „+ 440 weitere“. Darunter „Top-Rabatt je Welt“ und zwei Logo-Laufbänder. |
| 08 | Deine Community | Deine Edits | Sortimente in Reitern mit „+ X € für Dich“. Die Reiter wechseln von selbst, bis jemand klickt. |
| 09 | Dein Verdienst | Ein Verkauf, zwei Gewinner | Echte Produkte von unter 10 € bis über 100 € wechseln sich ab, immer reihum aus vier Preisbereichen. Jeweils zu sehen: regulär → im Shop → Community spart → Du verdienst (70 % vom Gewinn bei rund 25 % Durchschnittsmarge). Darunter zählen Verkäufe und Verdienst mit: „… und das ohne einen Handgriff.“ |
| 10 | Dein Verdienst | Dein Potenzial | Rechner mit Reichweite, Kaufquote und Warenkorb. Die Beteiligung steht fest auf 70 % vom Gewinn, gerechnet mit rund 25 % Durchschnittsmarge. |
| 11 | Dein Verdienst | Null Aufwand | „Ihr müsst nichts tun.“ Aufgaben werden durchgestrichen und an INCENT übergeben. Der Aufwand zählt von 40 auf 0 Stunden. |
| 12 | Dein Verdienst | Passives Einkommen | iPhone-Sperrbildschirm im iOS-Stil. Unten ist eine Live-Aktivität angeheftet, die den Gewinn der Nacht mitzählt („Heute Nacht verdient“ mit dem letzten Betrag in Grün). Darüber schieben sich Bestellungen von unten ein, die Uhr läuft durch die Nacht. Als iOS-Schrift dient San Francisco, wo vorhanden, sonst das eingebettete Inter. |
| 13 | Dein Start | Reichweite & Bindung | Ein Handy mit Instagram, als 24-Sekunden-Schleife. Der Ablauf steht unter der Tabelle. |
| 14 | Dein Start | Dein Start | „Innerhalb einer Woche zur eigenen Plattform“, mit Tag 1 bis Live. Schritt 1 heißt: Sortiment aus 15 Welten auf die Zielgruppe zuschneiden. |
| 15 | Dein Start | Auf einen Blick | Zusammenfassung zum Mitnehmen (Dein Look · 70 % vom Gewinn · Null Aufwand · 15 Welten) und Link zum Wiederöffnen. |

In der **Beauty-Fassung** sind die Folien 05–08: Markenvielfalt (Luxusmarken, „+ 70 weitere“, Kategorien, „Und weit mehr als Beauty“), Partner-Deals (30 echte Deals in zwei Laufbändern, „46 exklusive Partner-Deals allein in Health & Beauty“), Deine Edits und „Mehr als Beauty“ („Beauty ist erst der Anfang.“: Zielgruppe wählen, die passenden Welten leuchten auf). Titel und Zusammenfassung sprechen von „Beauty & weit mehr“.

Ablauf der Instagram-Schleife auf Folie 13:

1. Story antippen.
2. Link antippen.
3. Der Webshop öffnet sich. Ein Produkt kommt in den Warenkorb („Zum Warenkorb hinzugefügt“, das Symbol zeigt 1).
4. Durch die Deals scrollen.
5. Warenkorb öffnen, „Zur Kasse“ antippen. Es erscheint „Bestellung abgeschlossen“ und neben dem Handy „+X € für Dich“.
6. Den Shop schließen. Zurück geht es zur Story, nach einer kurzen Pause zum Feed, und die Schleife beginnt von vorn.

Der Warenkorb ist im Stil von vorteile.net nachempfunden, die echte Warenkorb-Seite war nicht in der Shop-Speicherung enthalten.

Vorschaubilder liegen in `screenshots/` (`allgemein-*.png` für die Startseite, die übrigen für die Beauty-Fassung).

## Sublinks je Influencerin oder Influencer

Für jeden Pitch kommt ein Eintrag in `data/pitches.json` unter `pitches`:

```json
{
  "slug": "lena",
  "name": "Lena",
  "thema": "beauty",
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
| `name` | erscheint überall: „Exklusiv für Lena“, Schriftzug im Portal, `lena.vorteile.net`, „Für Lena“ in der Leiste, „Lenas Shop“ auf dem iPhone, „Lenas Beauty-Shop.“ bzw. „Lenas Vorteils-Shop.“ – leer lassen für eine Fassung ohne Namen |
| `thema` | `beauty` (Standard) oder `allgemein` |
| `farbe`, `nav` | Button- und Leistenfarbe: `blau`, `rose`, `beere`, `nude`, `salbei`, `lavendel`, `schwarz`, `weiss`, `puder`, `creme` oder ein Hex-Wert |
| `hintergrund` | `image` (Kategorie-Motiv: Health & Beauty bzw. Technik), `solid` oder `gradient` |
| `logo` | optional: Logo-Datei in `data/pitches/`. Sie ersetzt den Schriftzug in allen Mockups. |
| `hintergrundfarbe` | optional: Hex-Wert für den einfarbigen Hintergrund (sonst aus der Buttonfarbe abgeleitet) |
| `hintergrundbild` | optional: Bilddatei in `data/pitches/` für den Bild-Hintergrund im Shop (sonst das Kategorie-Motiv); am besten 16:9, Personen am linken und rechten Rand |
| `hintergrundton` | optional: `dunkel` bei dunklem Hintergrundbild – Überschrift im Shop wird hell, das Bild läuft vor der Produktreihe ins Weiß aus |
| `reichweite` | optional: Startwert „Deine Reichweite“ im Rechner (Follower, 5.000–1.000.000), Standard 100.000 |
| `beteiligung` | optional, Standard 70 (Prozent vom Gewinn) |
| `marge` | optional, Standard 25 (Durchschnittsmarge pro Produkt in Prozent) |

`startseite` in `data/pitches.json` beschreibt die Seite unter https://dinosbs.github.io/pitch/ (dieselben Felder ohne `slug`, derzeit Thema `allgemein` ohne Namen).

Danach `python3 build.py` ausführen (das erzeugt `index.html` und `pitches/<slug>/index.html`) und auf `main` pushen. Der Workflow veröffentlicht die Seite unter `/<slug>/`.

Für schnelle Tests geht es auch ohne neuen Build: `pitches/beauty/index.html?name=Lena&farbe=rose&nav=schwarz&hintergrund=verlauf` (genauso mit `index.html?name=…` für die allgemeine Fassung)

## Anpassen

- **Beteiligung, Beispiel-Marge, Preisstand, Farben im Gestalter:** oben in `build.py` (`SHARE`, `MARGIN` = Durchschnittsmarge, `SNAPSHOT_DATE` für Beauty, `SNAPSHOT_GEN` für allgemein, `BTN_COLORS`, `NAV_COLORS`)
- **Texte je Thema:** `THEMES` in `build.py`
- **Produkte und Deals der Beauty-Fassung:** `data/selection.json` (Marke + exakter Titel aus `data/catalog.json`). Die ersten 30 Deals füllen die zwei Laufbänder (`DEAL_ROW` in `build.py`), `cycle` legt die Produkte je Preisklasse fest. Die Bilder holt `tools/extract.py`.
- **Auswahl der allgemeinen Fassung:** `data/general/selection.json` (Produkte als [Marke, exakter Titel] aus `data/general/catalog.json`, Deals über ihren Titel aus `data/general/deals.json`, Marken über ihren Namen aus `data/general/brands.json`):

  | Schlüssel | Wofür |
  | --- | --- |
  | `preview` | Portal und Shop-Handy (`deals`, `products`), Instagram (`post`, `story`, `story_text`, `caption`) |
  | `zielgruppen` | die Buttons links auf „15 Welten“ (`id`, `label`, `sub`, `icon`) |
  | `welten` | je Kategorie das Icon, `gruppen` (welche Zielgruppen sie aufleuchten lassen) und für Kategorien ohne Unterkategorien einen `text` |
  | `spotlight` | 8 Deals für die vier großen Karten auf „Top-Deals“ (je Platz zwei, sie wechseln sich ab) |
  | `wall` | die Deals der zwei Laufbänder darunter |
  | `lux` | die 11 großen Marken-Kacheln |
  | `logos` | zwei Reihen für die Logo-Laufbänder |
  | `edits` | Reiter (`id`, `name`, `claim`, `items`) |
  | `cycle` | „Zwei Gewinner“: Produkte je Preisklasse `a` < 10 €, `b` < 50 €, `c` < 100 €, `d` ab 100 € |
  | `products`, `deals`, `brands` | alles, wofür `tools/extract_all.py` Bilder speichert – neue Einträge oben auch hier ergänzen |
  | `dlogo_marke` | Deal → Markenlogo, wenn ein Deal in der Speicherung kein eigenes Logo hat |

- **Texte und Folien:** `src/template.html`. Design: `src/style.css`. Ablauf und Animationen: `src/app.js`. Icons: `src/icons.svg`.
- **Neue Folie:** `<section class="slide" data-act="…" data-snap data-label="…">` mit `.shell > .bg + .frame > .frame__in > .content`. Legende, Zähler und Kapitelbalken übernehmen sie automatisch. Inhalte werden in Canvas-Pixeln (1600 × 900) gestaltet. Passt eine Folie nicht ganz, verkleinert app.js nur ihren Inhalt.

```
python3 build.py
```

## Daten aus neuen Shop-Speicherungen holen

Seite im INCENT-Shop komplett aufklappen und mit SingleFile speichern, dann:

```
pip install pillow
```

Beauty-Fassung (eine Kategorie):

```
python3 tools/extract.py "/pfad/zu/Health & Beauty - incent.html"
```

Allgemeine Fassung (beliebig viele Kategorien; liest zusätzlich alle 15 Welten mit Unterkategorien aus der Portal-Navigation):

```
python3 tools/extract_all.py "/pfad/Technik.html" "/pfad/Home_und_Living.html" "/pfad/Sport.html"
```

Danach `python3 build.py`.

## Aufbau

```
index.html                  allgemeine Fassung (Startseite, generiert)
pitches/<slug>/index.html   je Fassung: beauty, ariel61, yelizkoc (generiert, alles eingebettet, offline-fähig)
build.py                    baut alle Fassungen aus src/ + data/ + assets/
tools/extract.py            liest eine SingleFile-Speicherung einer Kategorie aus (Beauty)
tools/extract_all.py        liest mehrere Kategorie-Speicherungen aus (allgemein)
src/                        template.html, style.css, app.js, icons.svg
data/                       catalog.json, deals.json, brands.json, selection.json (Beauty), pitches.json, pitches/ (Logos, Hintergrundbilder)
data/general/               kategorien.json, catalog.json, deals.json, brands.json, selection.json (allgemein)
assets/                     products/, deals/, logos/, ui/ (INCENT-Logos, Zahlungsarten, Kategorie-Hintergrund), fonts/ (Barlow Semi Condensed, Inter – beide SIL OFL)
assets/general/             products/, deals/, dlogos/ (Logos in Deals), logos/, ui/ (Kategorie-Hintergründe)
screenshots/                Vorschaubilder
.github/workflows/pages.yml baut und veröffentlicht auf GitHub Pages
```

## Hinweise zu den Zahlen

- Preise, Vergleichspreise („Regulär“) und Rabatte sind Momentaufnahmen aus dem INCENT-Vorteilsportal: Beauty vom 01.11.2026 (Kategorie Health & Beauty), allgemein vom 04.11.2026 (Technik, Home & Living, Mobilität, Mode & Accessoires, Sport, Health & Beauty).
- Beauty: „80+ Marken“, „250+ Produkte“, „bis 71 %“, „46 Partner-Deals“ und „Ø 27 %“ sind aus diesen Daten berechnet.
- Allgemein: „15 Welten“ und „über 50 Unterkategorien“ stammen aus der Portal-Navigation. „bis 83 %“, „Top-Rabatt je Welt“, „150+ exklusive Partner-Deals“ (154 verschiedene Deals in den sechs gespeicherten Kategorien) und „Ø 31 %“ sind aus den Speicherungen berechnet. Die übrigen neun Welten erscheinen mit Namen und Unterkategorien, ohne Rabattangabe.
- „4.400 Unternehmen“, „450+ Markenpartner“, „3.000+ Markenprodukte“ und „70+ Partnergutscheine“ stammen von incent.de.
- Die Beteiligung beträgt 70 % vom Gewinn. Alle Verdienst-Beträge rechnen mit rund 25 % Durchschnittsmarge (70 % davon = 17,5 % vom Verkaufspreis). Reichweiten- und Umsatzwerte im Rechner sowie das Diagramm sind als Beispiel bzw. schematisch gekennzeichnet.
