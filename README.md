# Hinweis „Nicht mit Select-Einkaufsgutschein kaufbar“

> **Neu:** `community-shop/` enthält den Pitch-One-Pager „Dein eigener Beauty-Shop“ für den INCENT-Community-Shop (Health & Beauty) im Design des incent.de-Relaunchs, mit Shop-Mockups im vorteile.net-Look. Details in [`community-shop/README.md`](community-shop/README.md).

Dieses Repo enthält einen Design-Prototyp für die INCENT-Gutscheinwelt. Er markiert Gutscheine, die nicht mit dem Select-Einkaufsgutschein gekauft werden können, und zwar an drei Stellen:

| Seite | Was passiert |
| --- | --- |
| **Gutscheinwelt** (`mockups/gutscheinwelt.html`) | Ein orangefarbenes Icon sitzt oben links auf dem Produktbild. Beim Hovern, Fokussieren oder Antippen erscheint ein Tooltip mit dem Hinweis. Eine kleine Legende im Filterbereich erklärt das Icon. |
| **Warenkorb** (`mockups/warenkorb.html`) | Am Artikel stehen das gleiche Icon und ein dauerhaft sichtbarer Hinweis. Über dem Checkout-Button fasst ein Kasten zusammen, welche Artikel betroffen sind. |
| **Details prüfen** (`mockups/details-pruefen.html`) | Die Artikel tragen dieselben Hinweise wie im Warenkorb. Unter dem Gutscheincode-Feld steht eine kompakte Warnung. Sobald jemand einen Code eingeben will, klappt sie auf und zeigt die betroffenen Artikel. Zusätzlich werden diese Artikel links orange hervorgehoben. Ein Klick auf „Einlösen“ lässt die Warnung kurz wackeln. |

Zum Ansehen die Dateien in `mockups/` im Browser öffnen. Vorschaubilder liegen in `screenshots/`.

## Aufbau

```
original/   unveränderte SingleFile-Speicherungen der drei Seiten
src/        select-hinweis.css + select-hinweis.js (der eigentliche Baustein)
mockups/    Original + eingebettetes CSS/JS (generiert)
build.py    erzeugt mockups/ aus original/ + src/
```

Nach Änderungen in `src/` die Mockups neu bauen:

```
python3 build.py
```

## Welche Gutscheine markiert sind

Für den Prototyp sind diese Marken markiert: FlixBus, Circle K DE und Wellcard. Die Liste steht oben in `src/select-hinweis.js`:

```js
const EXCLUDED_BRANDS = ['flixbus', 'circle k de', 'wellcard'];
```

Im echten Shop sollte das ein Flag pro Produkt aus der API sein (z. B. `selectVoucherExcluded: true`), keine Namensliste.

## Design-Entscheidungen

- **Farbe:** Orange ist die Komplementärfarbe zum INCENT-Blau (`#1C87B8`). Dadurch fällt der Hinweis deutlich auf und passt trotzdem zur Seite. Text auf Orange erreicht mindestens 4,5:1 Kontrast (WCAG AA).
- **Icon:** Ein Gutschein-Ticket mit ✕, also „Gutschein nicht einlösbar“. Das Icon ist überall gleich: auf der Karte, am Artikel, in der Zusammenfassung und am Code-Feld. So erkennt man es auf jeder Seite wieder.
- **Aufmerksamkeit:** Das Icon hat einen dezenten Puls in Intervallen. Bei `prefers-reduced-motion` ist er abgeschaltet.
- **Tooltip:** Er hängt am `<body>` und wird deshalb nicht von `overflow: hidden` der Karten abgeschnitten. Er bleibt immer im Viewport und klappt nach oben, wenn unten kein Platz ist.
- **Bedienung:** Der Tooltip funktioniert mit Maus, Tastatur und Touch. Esc schließt ihn. Ein Klick aufs Icon öffnet nicht die Produktseite.
- **Responsiv:** Unter 1200 px rutscht der Artikel-Hinweis unter den Artikel, weil die Spalte neben dem Bild dort zu schmal ist.
- **Barrierefreiheit:** Screenreader lesen den Hinweis vor, wenn die Gutscheincode-Felder fokussiert werden (über `aria-describedby`).
