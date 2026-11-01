# Community-Shop – Pitch Health & Beauty

Ein One-Pager im Präsentationsstil, mit dem wir Creatorinnen aus Health & Beauty den INCENT-Community-Shop vorstellen.

- **Design:** wie der INCENT-Relaunch ([Dinosbs/incentde](https://github.com/Dinosbs/incentde)) mit Barlow Semi Condensed, blauem CI-Verlauf, hellen Flächen, Eyebrow-Pills und Buttons mit Leuchteffekt. Die Du-Ansprache und die Inhalte stimmen mit der Creator-Welt der Website überein.
- **Shop-Mockups:** Sie sind dem echten Vorteilsportal (vorteile.net) nachgebaut, genauso wie die Live-Demo der Website. Es gibt eine Desktop- und eine Handy-Ansicht mit Kategorie-Pills, „Best of Health & Beauty“, Angebotskacheln und Produktkarten. Der Hintergrund ist das echte Bild der Kategorie Health & Beauty. So wird der Shop am Ende aussehen.
- **Inhalte:** Produkte, Preise, Deals und Logos stammen aus einer Speicherung der Kategorie „Health & Beauty“ im INCENT-Shop vom 01.11.2026.

**Ansehen:** `index.html` im Browser öffnen. Die Datei ist komplett eigenständig (Bilder und Schriften eingebettet, ca. 3,3 MB) und funktioniert offline.

## Folien

| # | Folie | Inhalt |
| --- | --- | --- |
| – | Start | „Dein eigener Beauty-Shop“ mit großem vorteile.net-Portal in 3D. Es neigt sich zum Cursor und richtet sich beim Scrollen auf. Dazu laufende Bestellungen („Neue Bestellung · +10,60 €“), der Zähler „heute für Dich“ und Kennzahlen. |
| 01 | Die Idee | Vorteilspreise, die sonst nur Mitarbeitende bekommen. Drei Schritte und ein Rechenbeispiel an einer echten Produktkarte. |
| 02 | Dein Design | Live-Demo: Logo hochladen, Namen eintippen, Button- und Navigationsfarbe sowie Hintergrund wählen. Alle Portal-Mockups der Seite (Desktop, Handy, Story) übernehmen das sofort, die Adresse wird zu `name.vorteile.net`. |
| 03 | Verdienst | Sechs echte Produktkarten mit Ersparnis und Verdienst pro Verkauf. Der Regler „Deine Beteiligung“ rechnet alle Beträge auf der Seite um. |
| 04 | Rechner | Reichweite, Kaufquote, Ø Warenkorb und Beteiligung ergeben den Verdienst pro Monat und Jahr. Dazu die Profile Micro, Mid und Macro. |
| 05 | Marken | Luxusmarken als Logo-Kacheln, Produktzahlen je Kategorie und ein Laufband mit allen weiteren Marken. |
| 06 | Edits | Fünf Sortimente mit vorteile.net-Produktkarten, jeweils mit „+ X € für Dich“. |
| 07 | Partner-Deals | Zwölf Angebotskacheln im vorteile.net-Look (Shiseido, NARS, ghd, Rituals …). |
| 08 | Reichweite | Story → Link → Shop auf dem Handy, dazu vier Vorteile. |
| 09 | Service | „Du machst Content. Wir den Rest.“ mit Aufgabenteilung und einer Beispiel-Auswertung, die die Werte aus dem Rechner übernimmt. |
| 10 | Ablauf | „Innerhalb einer Woche zur eigenen Plattform“ in vier Schritten, danach „Shop anfragen“. |

**Präsentieren:** Mit den Pfeiltasten ↑ ↓ oder Bild↑/Bild↓ (also auch mit einem Presenter) springt man von Folie zu Folie. Bei langen Folien wird erst innerhalb der Folie weitergeblättert.

## Für eine bestimmte Creatorin personalisieren

Die Seite bleibt allgemein. Über die Adresse lässt sie sich aber vorbelegen, ohne neu zu bauen:

```
index.html?name=Lena&farbe=rose&nav=schwarz&hintergrund=verlauf&provision=12
```

| Parameter | Wirkung |
| --- | --- |
| `name` | Schriftzug im Portal-Header, Shop-Name, Adresse `lena.vorteile.net`, Story-Handle, „Exklusiv für Lena“ im Hero, Seitentitel |
| `farbe` | Buttonfarbe des Portals: `blau`, `rose`, `beere`, `nude`, `salbei`, `lavendel`, `schwarz` oder ein Hex-Wert (`c0746a`) |
| `nav` | Farbe der Navigationsleiste, gleiche Werte wie `farbe` (z. B. `schwarz` oder `ffffff`) |
| `hintergrund` | `bild` (Standard, Health-&-Beauty-Motiv), `einfarbig` oder `verlauf` |
| `provision` | Startwert der Beteiligung in Prozent (5–20) |
| `reichweite` | Startwert der Reichweite im Rechner |

Ein eigenes Logo lässt sich im Gestalter hochladen. Es bleibt im Browser und wird nicht gespeichert.

## Anpassen

- **Beteiligung beim Öffnen, Kontaktadresse, Preisstand, Farben im Gestalter:** oben in `build.py` (`DEFAULT_RATE`, `CONTACT_MAIL`, `SNAPSHOT_DATE`, `BTN_COLORS`, `NAV_COLORS`). Ist `CONTACT_MAIL` leer, öffnet „Shop anfragen“ eine Mail ohne Empfänger.
- **Welche Produkte und Deals gezeigt werden:** `data/selection.json` (Marke + exakter Titel aus `data/catalog.json`).
- **Texte und Aufbau:** `src/template.html`. Design: `src/style.css`. Interaktion: `src/app.js`. Icons: `src/icons.svg`.

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

`extract.py` schreibt `data/catalog.json` (alle Produkte), `data/deals.json` und `data/brands.json`. Die Bilder legt es unter `assets/` ab, also Produkte, Deals, Logos, Zahlungsarten und den Kategorie-Hintergrund. Produktbilder werden nur für Produkte aus `data/selection.json` exportiert.

## Aufbau

```
index.html            fertige Seite (generiert, alles eingebettet)
build.py              baut index.html aus src/ + data/ + assets/
tools/extract.py      liest eine SingleFile-Speicherung des Shops aus
src/                  template.html, style.css, app.js, icons.svg
data/                 catalog.json, deals.json, brands.json, selection.json
assets/products/      Produktbilder        assets/deals/   Bilder der Partner-Deals
assets/logos/         Marken-Logos         assets/ui/      INCENT-Logos, Favicon, Zahlungsarten, Kategorie-Hintergrund
assets/fonts/         Barlow Semi Condensed (SIL OFL, aus dem incent.de-Relaunch)
screenshots/          Vorschaubilder
```

## Hinweise zu den Zahlen

- Preise, Vergleichspreise („Regulär“) und Rabatte sind eine Momentaufnahme vom 01.11.2026.
- „80+ Marken“, „250+ Produkte“, „bis 71 %“, „46 Partner-Deals“ und „Ø 27 %“ sind direkt aus den Shop-Daten berechnet. „Über 4.400 Unternehmen“ stammt von der incent.de-Website.
- Die Beteiligung (Standard 10 %), die Kaufquote und der Warenkorb sind **Beispielwerte**. Die Seite kennzeichnet sie als Beispielrechnung. Vor dem Pitch die echten Konditionen prüfen und gegebenenfalls `DEFAULT_RATE` anpassen.
