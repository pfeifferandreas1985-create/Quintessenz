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
| `--pap-breite` | 58 ch | Satzspiegel, gemessen 72–75 Zeichen |

### Bogenbreite und Satzspiegel sind zwei verschiedene Dinge

Das war anfangs vermischt, mit dem Ergebnis: auf einem 1100 px breiten Brett
lag ein 684 px schmaler Bogen mit 208 px Rand je Seite — und die Zeile lief
trotzdem auf 98 Zeichen.

| | |
|---|---|
| **Bogen** | `width: min(100%, max(40rem, 88cqi))`, höchstens `64rem`. `#papierblatt` ist `container-type: inline-size`, der Bogen misst sich also am **Brett**, nicht am Fenster. Ergebnis: 85 % der Brettbreite, ~84 px Rand je Seite. |
| **Satzspiegel** | `max-width: var(--pap-breite)` auf `p h2 h3 h4 ul ol blockquote .formel`. Tabellen, Bilder, Info- und Warnkästen nutzen den **ganzen** Bogen — wie auf einer technischen Zeichnung. |

Die Zeilenlänge steht in **`ch`**, nicht in `rem`: `1ch` ist die Breite der
Ziffer 0 in der gerade geltenden Schrift, die Zeile passt sich also der
Leseschrift des Geräts an. Gemessen bei `58ch`: 72 Zeichen (Libre
Baskerville), 75 (Jost). Bei einer Schreibmaschinenschrift ist `1ch` exakt
ein Zeichen — **Regenschauer** setzt deshalb `72ch`.

Nachmessen im Browser:

```js
const p = [...document.querySelectorAll('.blatt > p')]
  .find(x => !x.classList.contains('demo-vermerk') && x.textContent.length > 90);
const s = document.createElement('span');
s.style.cssText = 'position:absolute;visibility:hidden;white-space:pre';
s.textContent = 'abcdefghijklmnopqrstuvwxyz ';
p.appendChild(s);
const proZeichen = s.getBoundingClientRect().width / 27; s.remove();
Math.round(p.getBoundingClientRect().width / proZeichen);   // Zeichen je Zeile
```

### Fassungsnummer an CSS und JS

`server.py` ersetzt beim Ausliefern von `index.html` den Platzhalter
`__FASSUNG__` durch `<version>-<jüngster Zeitstempel unter static/>`. Ohne das
zeigt ein Browser nach einem Update der Box weiter die alte Oberfläche aus
seinem Zwischenspeicher — beim Entwickeln genauso wie im Betrieb. Die HTML
selbst geht mit `Cache-Control: no-cache` raus.

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

### Drei Ebenen statt einer Fläche

Die Leseseite besteht aus **Brett**, **Bogen** und **Rahmen** — nicht aus einer
Papierfläche:

| Ebene | Element | Was |
|---|---|---|
| **Brett** | `#papierblatt` | Reißbrett: Belag, Zeichenschiene quer über den Kopf, Maßstab am linken Rand. Scrollt **nicht** mit — nur der Bogen wandert darüber. |
| **Bogen** | `.blatt` | Das Blatt: eigene Kante, Schattenwurf, Raster und Heftlochung als Hintergrundlagen. Zwei Klammern (`::before`) halten es oben. |
| **Rahmen** | `.blatt::after` | Zeichnungsrahmen, links breiter als Heftrand. |

Der Aktenkopf ist ein **Schriftfeld** (`.aktenzeichen`): harte Zellen,
kräftiger Außenrahmen, keine Rundungen — der Titelblock einer technischen
Zeichnung. Das erfüllt die Forderung „Quelle immer sichtbar wie ein
Aktenstempel" ohne zusätzliche Bauteile.

### Was ein Gerät alles umstellt

Ein Thema tauscht **nicht nur die Palette**. Diese Token stehen jedem Gerät
offen (Vorgaben in `tokens.css`, Werte in `themen.css`):

| Token | Wirkung |
|---|---|
| `--f-term`, `--term-groesse`, `--term-spur`, `--term-vers` | Terminalschrift, Größe, Laufweite, Versalien |
| `--zeiger` | Cursorzeichen vor dem gewählten Eintrag |
| `--gauge-art` | Bauart der Instrumente: `nadel` · `ring` · `balken` · `saeule` |
| `--r-bezel`, `--knopf-radius`, `--schild-radius`, `--schild-rahmen` | Form von Gehäuse, Knöpfen, Schildern |
| `--eintrag-trenn`, `--eintrag-marke` | Trennlinien und Auswahlbalken |
| `--raster` | Muster der Schirmoberfläche |
| `--brett`, `--schiene`, `--klammer`, `--brett-deko` | Reißbrett und seine Ausstattung |
| `--blatt-textur`, `--blatt-rand`, `--rahmen-staerke`, `--h2-linie`, `--stempel-dreh` | Bogen: Lagen, Randstreifen, Linien |
| `#geraet::after` | Dekoration: Noppen, Messingschrauben, Nagelköpfe, HUD-Winkel |

### Die zehn im Einzelnen

| Gerät | Requisite | Schirm | Schrift · Zeichen · Instrument | Form | Brett + Bogen |
|---|---|---|---|---|---|
| **Phosphor** | Aktenterminal einer Behörde, Röhre 1958 | Grün `#33FF66` auf `#0B0F0A` | VT323 · `>` · Nadel | Bakelit, Radius 22 px, Zeilensprung | dunkelolives Brett · vergilbter Zeichnungsbogen |
| **Bernstein** | Leitstand einer Anlage | Amber `#FFB000` | VT323 · `»` · Nadel | geriffeltes Bakelit, punktierte Trennlinien | Brett in Nussbraun · Durchschlag mit **Heftlochung** |
| **Gitternetz** | Rechnerraum aus Licht | Cyan `#6FE9FF` auf `#03070C` | Jost **Versalien** · `▸` · **Balken** | kein Gehäuse, **Lichtkante + Eckwinkel**, Radius 2 px, Gitterraster | Lichttisch, **cyan leuchtende Klammern** · **echte Blaupause**: helle Linien auf Preußischblau |
| **Regenschauer** | Serverkeller, fallende Zeichen | kaltes Grün `#22E96A` auf `#010502` | **Courier Prime** · `▌` · **Säule** | Gehäuse fast weg, senkrechte Bahnen | schwarzes Brett · **Endlospapier mit Transportlochung beidseitig** |
| **Reaktorkern** | Helmanzeige eines Fluganzugs | Gold `#FFC24A`, Zweitfarbe `#59E6FF` | Jost Versalien · `◆` · **Ring** | **geschnittene Ecken** (clip-path), **schräge Schilder** | Brett in Metallbraun · Datenblatt mit **Passkreuzen** |
| **Flugleitung** | Cockpit der 1930er | Radiumweiß `#CFE3D2` | VT323 · `▴` · Nadel | Nussholz, **Messingschrauben in den Ecken**, Radius 34 px, graviertes Messingschild | Holzbrett, Messingschiene · Leinenpapier mit **doppelter Zierlinie** |
| **Logbuch** | Kartentisch bei Öllampe | Laternengelb `#F0C070` | VT323 · `❖` · Nadel | dunkles Holz, **Nagelköpfe**, gestrichelte Trennlinien | Brett in Dunkelbraun · **Pergament mit angesengtem Rand**, kein Raster |
| **Seekarte** | Navigationspult | Gold `#FFD23F` auf lackiertem Blau | Jost Versalien · `✦` · Nadel | goldene Innenkante, Radius 10 px | marineblaues Brett, Goldschiene · **Rhumbenlinien**, 3-px-Tusche unter Überschriften |
| **Springfield** | Kraftwerk in Zeichentrickfarben | Gelb `#FFD90F` auf Tiefblau | Jost · `▶` · **Balken** | **kein Raster**, Radius 30 px, **3-px-Kontur** um Gehäuse und Schirm | Türkisbrett, **schwarze Schiene, gelbe Klammern**, kein Maßstab · Weiß mit harter Kontur |
| **Klemmbaustein** | Bauanleitung aus Kunststoffsteinen | Weiß auf **Stein-Blau `#0055BF`** | Jost · `●` · **Balken** | **Noppenreihe** über dem Schirm, gelbe Steinplatten als Schilder, Rot `#C91A09` als Signal | **Grundplatte mit Noppen**, **rote Klammern** · weißes Anleitungspapier, blau-roter Kopfstreifen, blaue Schrittnummern |

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
