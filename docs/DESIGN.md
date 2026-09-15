# DESIGN.md — Designsystem QUINTESSENZ TERMINAL

Die Anwendung hat **zwei Welten**. Das ist keine Spielerei, sondern die Lösung
für das Grundproblem retro-futuristischer Oberflächen: Phosphorgrün auf Schwarz
sieht großartig aus und ist nach zehn Minuten Lesen unerträglich.

| | TERMINAL | PAPIER |
|---|---|---|
| Wofür | Navigation, Suche, Chat, Werkzeuge | Lesen |
| Datei | `app/static/css/terminal.css` | `app/static/css/papier.css` |
| Grund | kurze Blicke, Bedienung | lange Lesezeit |
| Glow, Scanlines, Flackern | erlaubt | **verboten** |
| Modellantworten (RAG) | hier | **nie hier** |

Wer einen neuen Baustein baut, entscheidet zuerst: Terminal oder Papier. Es
gibt nichts dazwischen.

---

## 1. Farben

Alle Werte stehen in `app/static/css/tokens.css`. Nichts wird woanders
hartkodiert.

> **Die Farbwerte unten sind die Grundeinstellung (Gerät PHOSPHOR).**
> Jedes der zehn Geräte in `themen.css` überschreibt sie — siehe
> [Abschnitt 10](#10-die-zehn-geräte). Die *Rollen* der Token ändern sich nie,
> nur ihre Werte.

### Terminal

| Token | Wert | Verwendung |
|---|---|---|
| `--term-bg` | `#0B0F0A` | Schirm |
| `--term-bg-tief` | `#070A06` | Schirmrand (Vignette) |
| `--term-gehaeuse` | `#191612` | Bakelit |
| `--term-gehaeuse-h` | `#2A2621` | Bakelit-Lichtkante |
| `--phos` | `#33FF66` | Phosphor, Haupttext |
| `--phos-hell` | `#9DFFC0` | Schilder, Hervorhebung |
| `--phos-dim` | `rgba(51,255,102,.58)` | Sekundärtext |
| `--phos-schwach` | `rgba(51,255,102,.28)` | Linien, Rahmen |
| `--phos-hauch` | `rgba(51,255,102,.10)` | Hintergrund bei Auswahl |
| `--phos-glut` | `rgba(51,255,102,.34)` | Bloom (`text-shadow`) |

Ein Gerätewechsel tauscht genau diese Token aus — kein Baustein kennt eine
Farbe unmittelbar. Deshalb kostet ein neues Gerät nur einen CSS-Block.

### Papier

| Token | Wert | Verwendung |
|---|---|---|
| `--pap-hell` | `#E8DCC0` | Papier oben links |
| `--pap-dunkel` | `#D9CBA3` | Papier unten rechts |
| `--pap-kante` | `#C4B48C` | Linien, Bildrahmen, Fußnoten |
| `--tinte` | `#1E1A14` | Fließtext, Überschriften |
| `--tinte-mittel` | `#433B2E` | Untertitel, Tabellenhinweise |
| `--tinte-schwach` | `#6B6151` | Quellenlabel, Bildherkunft |
| `--stempel` | `#8B2E1F` | Stempel, Verweise, Akzent |
| `--warn-gelb` | `#E3B505` | Warnstreifen |
| `--warn-schwarz` | `#171310` | Warnstreifen |

**Kontrast Tinte auf Papier: 11,65:1** (`#1E1A14` auf dem mittleren Papierwert
`#E0D3B2`; 10,73:1 an der dunkelsten, 12,72:1 an der hellsten Stelle des
Verlaufs). Gefordert waren ≥ 7:1. Der Modus *hoher Kontrast*
(`:root[data-kontrast="hoch"]`) hebt auf 16,29:1 (`#100D09` auf `#F1EBDB`).

Gemessen mit `python tools/kontrast.py` — das Skript liest die Werte aus
`tokens.css`, prüft neun Paarungen gegen ihre Mindestwerte und gibt 1 zurück,
wenn eine reißt. Stand zuletzt: alle erfüllt.

---

## 2. Schriften

Alle vier Familien liegen lokal unter `app/static/fonts/` (SIL OFL 1.1,
Weitergabe erlaubt, Lizenztexte liegen daneben). Geholt mit
`python tools/fetch_fonts.py`. **Kein CDN, kein `@import` aus dem Netz.**

| Token | Familie | Wofür |
|---|---|---|
| `--f-term` | VT323 | alles im Terminal |
| `--f-schild` | Jost (Variable, 100–900) | Überschriften, Metallschilder, Stempel, Tabellenköpfe |
| `--f-akte` | Courier Prime | Aktenzeichen, Tabellenzellen, Bildunterschriften, Warnkästen |
| `--f-buch` | Libre Baskerville | Fließtext auf dem Papier |
| `--f-code` | Courier Prime | Lochstreifen-Kasten |

Jeder Stack endet in Systemschriften. Fehlt eine Datei, bleibt die Anwendung
vollständig benutzbar — sie sieht nur generischer aus.

**Zusammen 287 kB** für sieben woff2-Dateien. Beim ersten Aufruf einmal geladen,
danach aus dem Browser-Cache.

### Größen

`--skala` (Vorgabe 1) multipliziert jede Schriftgröße. Der Knopf `A+` schaltet
1 → 1,12 → 1,26 → 1,42 → 0,9 durch und speichert die Wahl lokal.

| Token | Wert | |
|---|---|---|
| `--t-klein` | 0,78 rem | Terminal-Sekundärtext, Fußzeile |
| `--t-normal` | 0,95 rem | Terminal-Menüeinträge |
| `--t-gross` | 1,15 rem | Suchfeld |
| `--pap-text` | 1,02 rem | Papier-Fließtext |
| `--pap-zeile` | 1,72 | Zeilenabstand Papier |
| `--pap-breite` | 38 rem | Satzspiegel ≈ 72 Zeichen |

---

## 3. Abstände

4-px-Raster, `--a0` bis `--a8` (2, 4, 8, 12, 16, 24, 32, 48, 64 px). Andere
Werte kommen nicht vor. Wer einen braucht, erweitert das Raster in `tokens.css`,
statt eine Ausnahme zu schreiben.

---

## 4. Bausteine

### Terminal

| Klasse | Was |
|---|---|
| `#geraet` | Bakelitgehäuse mit Chromkante |
| `#schirm` | Röhre: Rundung, Vignette, Scanlines, Glaswölbung |
| `.eintrag` | Menüzeile: Cursor `>`, Piktogramm, Name, Bestandszahl |
| `.schild` | gestanztes Metallschild für Bereichsnamen |
| `.tiefe` | kleiner Rahmen mit REFERENZ / LEHRBUCH / PRAXIS / FALL |
| `.klammer` | setzt `[ … ]` um einen Aktennamen |
| `.abschnitt` | Abschnittsüberschrift mit auslaufender Linie |
| `.gruppenkopf` | Gruppenschild am Eingang mit Bestandszahl — **kein Klickziel** |
| `.gauge` | Zeigerinstrument (Archivgröße, Treffer, Bereiche) |
| `.werkzeug` | Aktenwerkzeug in der Randleiste, mit Tastenkürzel |
| `.knopf` | Bakelitknopf unter dem Schirm |
| `.maschine` | Modellantwort (RAG) — **ausschließlich im Terminal** |

### Papier

| Klasse | Was |
|---|---|
| `.aktenkopf` | Laufweg, Titel, Untertitel, Stempelreihe, Aktenzeichen |
| `.stempel` | schräg gestellter Stempel; `.demo`, `.nurlokal`, `.pruefen`, `.sprache` |
| `.aktenzeichen` | Quellenangabe als Formularzeile (`dl`) |
| `.formular` | Tabelle mit Titel und Fußnote |
| `.infokasten` | Label/Wert-Formular, roter Kopf |
| `.warnung` | Warnkasten; `.gefahr`, `.achtung`, `.hinweis` |
| `figure` / `figure.seitenkopie` | eingeklebtes Bild / eingeklebte Seitenkopie |
| `.lochstreifen` | Code-Kasten mit gestanztem Kopfband |
| `.formel` | freigestellte Formel mit Klartextzeile darunter |
| `.fall` | Frage-/Antwortblock eines Stack-Exchange-Falls |
| `.demo-vermerk` | Randvermerk auf Demo-Akten |

### Piktogramme

`app/static/img/piktogramme.svg`, 16 Bereichszeichen plus 7 Hilfszeichen,
alle 24×24, Strichzeichnung im Stil von Sicherheitspostern der 1950er.

Blitz · Zahnrad · Regler · Relais · Messgerät · Lochkarte · Kreuz · Zelt ·
Atom · Antenne · Schild · Amboss · Buch · Kompass · Knotennetz · Schraubenschlüssel

Farben und Strichstärken stehen als **Präsentationsattribute** an den Elementen,
nicht in einem `<style>`-Block: bei externem `<use href="datei.svg#id">`
übernehmen Browser die Stylesheets des referenzierten Dokuments nicht
zuverlässig, Attribute dagegen schon. Wer ein Symbol animieren will, muss es
inline setzen (siehe Atom im Leerzustand des Papiers) — Shadow-DOM eines `<use>`
ist von außen nicht formatierbar.

`.pikto` setzt immer Breite und Höhe. Ein `<svg>` ohne Größenangabe rendert
sonst mit 300×150.

---

## 5. Effekte und ihre Schalter

| Effekt | Umsetzung | Schalter |
|---|---|---|
| Scanlines | `#schirm::before`, `repeating-linear-gradient` | `--scanline-deckkraft` |
| Bloom | `text-shadow` auf `#schirmtext` | `--bloom-staerke` |
| Flackern | `@keyframes flackern`, 9 s | `--flacker` |
| Vignette + Glaswölbung | `#schirm::after` | immer an, kostet nichts |
| Cursor-Blinken | `@keyframes blinken` | langsamer bei Effekte aus |
| Atom-Rotation | `@keyframes kreisen` | aus bei Effekte aus |

`:root[data-effekte="aus"]` setzt alle drei auf 0. **Vorgabe auf Displays unter
8 Zoll ist AUS** — `app.js` prüft `min(screen.width, screen.height) < 800` oder
`(pointer: coarse)`. Der Knopf *Effekte* überschreibt das dauerhaft.

`@media (prefers-reduced-motion: reduce)` schaltet Flackern und Übergänge
unabhängig davon ab.

---

## 6. Umbruchpunkte

| Breite | Aufbau | Terminal |
|---|---|---|
| ≥ 1200 px | nebeneinander | 452 px |
| 900–1199 px | nebeneinander, kompakter (7-Zoll-Klasse, 1024×600) | 352 px |
| < 900 px | gestapelt: Papier verdrängt das Terminal, sobald eine Akte offen ist | volle Breite |
| < 560 px | Bestandszahl rutscht unter den Namen, Grundschrift 17 px | volle Breite |

Zurück zum Terminal auf dem Handy: `Esc`, der Knopf *Zurück zum Terminal*, oder
vom linken Rand nach rechts wischen.

---

## 7. Druckansicht

`@media print` in `papier.css`: Schwarz auf Weiß, Terminal und Overlay
ausgeblendet, Stempel entfärbt, Warnbänder als schwarze Balken, alle Antworten
eines Falls aufgeklappt, `break-inside: avoid` für Tabellen, Bilder, Warn- und
Infokästen. Seitenrand 18 mm oben/unten, 16 mm seitlich.

---

## 8. Formelsatz

`app/static/js/formel.js`, ~180 Zeilen, kein KaTeX.

KaTeX kostet 280 kB plus eigene Schriften. Die Teilmenge, die in
Handbüchern und Wikipedia-Artikeln tatsächlich vorkommt, lässt sich mit
`<sup>`, `<sub>` und einem gestapelten Bruch (`.tex-bruch`) sauber setzen.

Unterstützt: `\frac \tfrac \dfrac`, `^ _`, `\sqrt`, `\cdot \times \pm \le \ge
\ne \approx \to \infty \partial`, alle griechischen Buchstaben, `\mathrm
\mathbf \text`, `\left( \right)`, Abstände `\, \; \quad`, Funktionsnamen
(`\sin \cos \log \ln …`).

Variablen werden kursiv gesetzt, Ziffern und Operatoren aufrecht — so setzt man
Formeln. Unbekannte Befehle erscheinen lesbar ohne Backslash, nie als Rohbefehl.
Jeder Formelblock trägt zusätzlich eine **Klartextzeile** (`b.text`) für
Screenreader und für den Fall, dass der Satz misslingt.

---

## 10. Die zehn Geräte

Ein *Gerät* ist ein vollständiges Thema: es stellt **beide Welten** um. Andere
Röhre, anderes Gehäuse, anderes Schirmraster, anderer Kantenradius — und
dazu passend ein anderer Papierbogen mit eigener Tinte, eigenem Stempelton
und eigener Leseschrift. Die Vorstellung dahinter: eine andere Maschine aus
einer anderen Welt, die auf ihrem eigenen Papier druckt.

Alle Definitionen stehen in `app/static/css/themen.css`, ausgewählt über
`:root[data-thema="…"]`. Die Bedienung ist in allen zehn identisch.

| Gerät | Requisite | Schirm | Raster | Papier | Leseschrift |
|---|---|---|---|---|---|
| **Phosphor** | Aktenterminal einer Behörde, Röhre 1958 | Grün `#33FF66` auf `#0B0F0A`, Bakelit | Zeilensprung | vergilbte Akte | Libre Baskerville |
| **Bernstein** | Leitstand einer Anlage | Amber `#FFB000` | Zeilensprung, weich | Durchschlagpapier | Libre Baskerville |
| **Gitternetz** | Rechnerraum, in dem Licht die Wege zeichnet | Cyan `#6FE9FF` auf `#03070C`, Anthrazit, Radius 3 px | Gitter 22 px | kaltweißes Diagrammblatt | Jost |
| **Regenschauer** | Serverkeller, fallende Zeichen | kaltes Grün `#22E96A` auf `#010502` | senkrechte Bahnen 9 px | blassgrünes Endlospapier mit Leitzeilen | Courier Prime |
| **Reaktorkern** | Helmanzeige eines gepanzerten Fluganzugs | Gold `#FFC24A`, Zweitfarbe Hologrammblau `#59E6FF` | feine Linien 5 px | technisches Datenblatt | Jost |
| **Flugleitung** | Cockpit einer Propellermaschine der 1930er | Radiumweiß `#CFE3D2`, Nussholz + Messing, Radius 30 px | weich, starke Glaswölbung | Leinenpapier, Sepiatinte | Libre Baskerville |
| **Logbuch** | Kartentisch unter Deck bei Öllampe | Laternengelb `#F0C070`, dunkles Holz | grob, starke Vignette | vergilbtes Pergament | Libre Baskerville |
| **Seekarte** | Navigationspult eines Abenteurerschiffs | Gold `#FFD23F` auf lackiertem Blau `#10222E` | senkrecht 28 px | helles Seekartenpapier, schwere Tusche | Libre Baskerville |
| **Springfield** | Kraftwerks-Leitstand in Zeichentrickfarben | Gelb `#FFD90F` auf Tiefblau `#07222F`, Radius 30 px | **keins** (flächig) | Weiß mit schwarzer Kontur, Rahmen 2 px | Jost |
| **Klemmbaustein** | Anzeige an einer Bauanleitung aus Kunststoffsteinen | Weiß auf ABS-Blaugrau, Akzent Gelb `#F2CD37` | Noppen-Punktraster 16 px | reinweißes Anleitungspapier, harte Kontur | Jost |

### Warum eigene Namen

Dieselbe Regel wie beim Fallout-Verbot im Auftrag: gestaltet wird die
**Anmutung eines Geräts**, nicht eine Marke. Keine Logos, keine Figuren, keine
Filmschriften, keine geschützten Titel im Code oder in der Oberfläche. Wer ein
Gerät wiedererkennt, erkennt es an Farbe, Form und Raster — nicht an einem
Emblem. Die vier Schriften bleiben in allen zehn dieselben OFL-Familien.

### Bedienung

| | |
|---|---|
| Knopf **Gerät** | öffnet die Klappe mit allen zehn, zwei Plättchen zeigen Röhre und Bogen |
| Taste `G` | Klappe auf/zu |
| Taste `T` | nächstes Gerät |
| gespeichert | `localStorage`, Schlüssel `quintessenz.thema` |

Die Wahl setzt zusätzlich `<meta name="theme-color">`, damit auch die
Adressleiste des Handys mitzieht.

### Ein Gerät hinzufügen

1. Block `:root[data-thema="name"]` in `themen.css` anlegen. **Alle** Token
   setzen, die PHOSPHOR setzt — sonst erbt das Gerät Reste des vorigen.
2. Eintrag in `GERAETE` in `app/static/js/app.js` (Id, Name, Kurzbeschreibung,
   zwei Vorschaufarben).
3. `python tools/kontrast.py` — das Skript findet neue Geräte selbst und prüft
   jedes gegen Papier ≥ 7:1 und Schirm ≥ 4,5:1. Es gibt 1 zurück, wenn eine
   Paarung reißt.

Stand zuletzt: alle zehn erfüllen die Vorgaben. Papier 10,59:1 (Logbuch, der
niedrigste) bis 16,87:1 (Springfield); Schirm 10,64:1 bis 16,59:1.

---

## 11. Was verboten ist

- Farbwerte außerhalb von `tokens.css` und `themen.css`.
- Ein Gerät, das nur die Röhre umstellt und das Papier vergisst.
- Ein Gerät, das `tools/kontrast.py` nicht besteht.
- Abstände außerhalb des 4-px-Rasters.
- Glow, Scanlines oder Leuchtfarben auf dem Papier.
- Modellantworten auf dem Papier.
- Eine Schrift, ein Skript oder ein Bild aus dem Netz.
- Ein `<svg>` ohne Breiten- und Höhenangabe.
- Ein Bild, das nicht aus einer Quelle stammt. Wo keins vorliegt, steht ein
  ehrlicher Platzhalterrahmen (`/api/platzhalter.svg`), der sagt, welche
  Abbildung dort später hingehört.
- Eine Akte ohne vollständige Quellenangabe (`adapters/basis.py`, `pruefe()`).
