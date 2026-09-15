# 06 — Auftrag: „QUINTESSENZ TERMINAL"

> Offline-Wissensbibliothek im Atompunk-Stil für die DoomsdayBox.
> Dieses Dokument ist der vollständige Arbeitsauftrag für die Sitzung, die die Anwendung baut.
> Stand: 2026-09-15. Vorgängerfassung (Tron-Stil) verworfen zugunsten der Zwei-Welten-Idee Terminal/Papier.

## Die Idee in drei Sätzen

Eine Webanwendung auf der Box, die sich anfühlt wie ein Wissensterminal aus einer Welt, in der die
1950er nie aufgehört haben — und inhaltlich eine Enzyklopädie ist. Der Nutzer geht von 16 Bereichen
über Themen zu einzelnen Einträgen und liest sie **in der Anwendung**, einheitlich gesetzt, mit
Bildern aus den Originalquellen. Es öffnet sich nie ein fremdes Dokument: Das Terminal ist die
Navigation, das vergilbte Papierblatt ist die Lesefläche, die ZIMs und PDFs sind das Regal, das
niemand sieht.

---

## Der Prompt

```text
# Auftrag: „QUINTESSENZ TERMINAL“ – Offline-Wissensbibliothek im Atompunk-Stil für die DoomsdayBox

## Ausgangslage
Auf einem Raspberry Pi 5 (16 GB RAM, 1 TB NVMe, Raspberry Pi OS Lite 64-bit) liegt unter /srv/box
ein Offline-Wissensarchiv, aufgebaut nach D:\DoomsdayBox (Spiegel auf dem PC):
  zim/      ca. 40 Kiwix-ZIM-Dateien (Wikipedia DE/EN, WikiMed, Wikibooks, 16 Stack-Exchange-Bereiche,
            iFixit, Gutenberg, Appropedia, DevDocs, zimgit-Sammlungen …) + library.xml
  pdf/      ca. 100–150 PDFs nach Modul: mech, prog, med, surv, energie, komm, mil, rebuild, fahrzeuge
  own/      eigenes Material: rebuild_trees.db (Technologie-Abhängigkeitsbäume, SQLite),
            fahrzeuge.db (drei Fahrzeuge: Defender TD5, Mini MPi, Vespa V50), Fahrzeugakten (Markdown)
  maps/     PMTiles (Europa/DACH/Deutschland), MapLibre GL JS + Assets, poi.sqlite, GraphHopper
  models/   GGUF: Qwen3.5-9B, Gemma 4 E4B (+mmproj), Qwen3-Embedding-0.6B, whisper, Piper
  db/       leer, wird von der Anwendung befüllt (Volltextindex, Embeddings via sqlite-vec)
Dienste auf der Box: kiwix-serve :8888 (liefert ZIM-Inhalte als HTML, hat eine Suche-API),
llama-server :8080 (OpenAI-kompatible API), optional zweiter llama-server :8081 (Embeddings).
Die Wissensbereiche und ihre Quellen stehen in doku/WISSENSUEBERSICHT.md (16 Bereiche:
Elektrotechnik, Mechanik, Antriebe/Regelung/Sensorik, SPS, Messtechnik, Programmierung/Linux, Medizin,
Survival, Energie, Kommunikation, Militär defensiv, Zivilisationsneustart, Allgemeinwissen, Karten,
KI-Fähigkeiten, Eigene Fahrzeuge). Diese 16 Bereiche sind die oberste Navigationsebene.

## Ziel
Eine Webanwendung im lokalen WLAN der Box (http://quintessenz.local), die sich anfühlt wie ein
Wissensterminal aus einer Welt, in der die 1950er nie aufgehört haben – Atompunk, Retro-Futurismus,
die Ästhetik der Fallout-Spiele als Inspiration. Inhaltlich ist sie eine Enzyklopädie: Der Nutzer geht
von den 16 Bereichen über Themen zu einzelnen Einträgen und liest dort den Inhalt IN DER ANWENDUNG,
einheitlich gesetzt. Es wird niemals ein Original-PDF, ein Kiwix-Fenster oder ein fremder Tab geöffnet.
Die Anwendung liest die Quellen aus und rendert sie im eigenen Stil neu.

## Kernprinzipien (nicht verhandelbar)
1. Einheitlicher Stil: Jede Seite – ob aus Wikipedia, einem Stack-Exchange-Thread, einem PDF-Handbuch
   oder einer eigenen Fahrzeugakte – sieht aus, als wäre sie für dieses Terminal geschrieben und
   auf demselben Papier gedruckt. Gleiche Typografie, Abstände, Bild- und Tabellenrahmen, Infoboxen.
2. Bilder aus den Originalen: Abbildungen aus ZIM-Artikeln und PDFs werden extrahiert und eingebettet
   (Bildunterschrift + Quellenangabe). Keine Stockfotos, keine generierten Bilder.
3. Quelle immer sichtbar: Jeder Eintrag zeigt wie ein Aktenstempel, aus welcher Quelle (Datei,
   Artikel, Seite) er stammt, mit Datum. „Original einsehen“ öffnet die Rohdarstellung als Overlay –
   nur auf Wunsch.
4. Vollständig offline: keine externen Fonts, CDNs, Analytics, Web-Requests. Alle Assets lokal.
5. Läuft auf dem Pi 5: Serverseite leichtgewichtig (Python 3.12 + FastAPI oder Go), Rendering im
   Browser des Nutzers (Handy, Tablet, Laptop, 7-Zoll-Display). Ziel: Seite < 1 s, Suche < 2 s.
6. Bedienbar ohne Anleitung: Eine fremde Person muss in unter zwei Minuten eine Antwort finden.
7. Stil-Inspiration, keine Kopie: Keine geschützten Namen, Logos, Figuren oder Grafiken aus Fallout
   (kein Vault Boy, kein Vault-Tec, kein RobCo, kein Pip-Boy, keine Spielschriften). Eigene Namen,
   eigene Grafiken, frei lizenzierte Schriften.

## Zwei Welten: TERMINAL und PAPIER
Das ist die zentrale Gestaltungsidee und löst das Lesbarkeitsproblem retro-futuristischer Oberflächen:
- TERMINAL (Navigation, Suche, Chat, Karte): monochromer Röhrenmonitor. Phosphorgrün auf Schwarz,
  wahlweise Amber. Menüs als Listen mit Cursor „>“ und Klammern „[ ]“, Tastatur- UND Touch-bedienbar.
  Kurze Boot-Sequenz beim ersten Aufruf (überspringbar, < 2 s). Scanlines, leichtes Bloom und
  Flackern als CSS-Effekt – abschaltbar, standardmäßig aus auf Displays < 8 Zoll.
- PAPIER (Lesen): Sobald ein Eintrag geöffnet wird, „druckt“ das Terminal ihn: Die Seite erscheint als
  vergilbtes Papierblatt (Creme/Ocker, leichte Papierstruktur, dunkle Tinte), Schreibmaschinen-
  oder Buchschrift, Bilder als eingeklebte Fotos/Zeichnungen mit Rahmen, Tabellen als gestempelte
  Formulare. Ruhig, kontrastreich, lang lesbar. Kein Glow, keine Scanlines auf Papier.
  Aktenkopf oben: Bereich › Thema › Titel, Quelle, Datum, Tiefe-Stempel (REFERENZ / LEHRBUCH /
  PRAXIS / FALL). Sicherheits- und Medizinhinweise als schwarz-gelb gestreifte Warnkästen.
- Übergang: Terminal-Ansicht und Papierblatt gleichzeitig sichtbar auf großen Displays (Terminal
  links als schmale Spalte, Papier rechts), gestapelt auf Handy.

## Designsprache im Detail (Atompunk)
- Farben TERMINAL: Hintergrund #0B0F0A, Phosphor #33FF66 (Grün) / #FFB000 (Amber), gedimmt für
  Sekundärtext. Farben PAPIER: Papier #E8DCC0 bis #D9CBA3 (leichter Verlauf/Struktur), Tinte #1E1A14,
  Stempelrot #8B2E1F, Warnstreifen Schwarz/#E3B505.
- Formen: abgerundete Bildschirmkanten (Röhrenbezel), Bakelit-Anmutung an Rahmen und Knöpfen,
  Chromkanten sparsam, Atomsymbol als Ladeanzeige, Zeigerinstrumente (Gauges) für Kennzahlen
  (Archivgröße, Suchtreffer, Modellauslastung), gestanzte Metallschilder für Bereichsnamen.
- Schriften (alle lokal, OFL-lizenziert): Terminal in einer runden Monospace (z. B. VT323 oder
  Share Tech Mono), Überschriften/Schilder in einer geometrischen 50er-Sans (z. B. Jost, League
  Spartan), Papier-Fließtext in einer Buch-/Schreibmaschinenschrift mit hoher Lesbarkeit (z. B.
  Courier Prime für Akten, Libre Baskerville für lange Lehrbuchtexte). Code in Monospace auf Papier
  als „Lochstreifen“-Kasten.
- Ikonografie: eigene Piktogramme im Stil von 50er-Sicherheitspostern (Strich, zwei Farben),
  kein Vault Boy. Bereichs-Piktogramme: Blitz, Zahnrad, Regler, Relais, Messgerät, Lochkarte,
  Kreuz, Zelt, Atom, Antenne, Schild, Amboss, Buch, Kompass, Gehirn, Schraubenschlüssel.
- Ton: optionale Terminal-Klicks und Relais-Geräusche, standardmäßig aus.
- Sprache der Oberfläche: knapp, technisch, leicht behördlich („AKTE ÖFFNEN“, „SUCHE AUSFÜHREN“,
  „ARCHIVBESTAND“), Deutsch, Englisch umschaltbar. Keine Ironie, kein Spielzitat.
- Modellantworten (RAG) erscheinen im Terminal, nie auf Papier – so ist immer klar, was aus den
  Quellen gedruckt wurde und was die Maschine formuliert hat.
- Druckansicht: das Papierblatt ohne Effekte, Schwarz auf Weiß.

## Navigation (Menüführung)
- EINGANG: Terminal-Startbildschirm mit den 16 Bereichen als Menü (Piktogramm + Schildname +
  Bestandsanzeige „412 Akten“), darüber ein einziges Suchfeld mit blinkendem Cursor. Nichts anderes.
- BEREICH → THEMEN: Themenliste (aus WISSENSUEBERSICHT.md: „Was du nachschlagen kannst“) mit
  Tiefe-Stempel und Quellenzahl.
- THEMA → AKTEN: Kuratierte Einstiegsakten (aus einer Konfigurationsdatei je Thema) plus Suchtreffer
  aus den zugeordneten Quellen. Reihenfolge: Referenz zuerst, Fälle (Q&A) zuletzt.
- AKTE: Das Papierblatt. Randleiste im Terminal: Inhaltsverzeichnis, verwandte Akten (aus Links im
  Original), „Original einsehen“, „Vorlesen“ (Piper), „Nachfragen“ (RAG-Chat mit dieser Akte als
  Kontext), „Merken“ (Lesezeichen).
- Pfadanzeige immer sichtbar: EINGANG › BEREICH › THEMA › AKTE. Zurück mit Escape oder Wischgeste.
- Globale Suche jederzeit per „/“. Treffer nach Bereich gruppiert, Trefferzahl als Zeigerinstrument.
- Sonderräume: KARTENTISCH (MapLibre mit PMTiles, POI-Suche, Routing) und WERKSTATT (Rechner:
  Leitungsquerschnitt, Ohmsches Gesetz, Drehmoment, Einheiten, Thermoelement-Tabellen – aus own/).
- Verlauf und Lesezeichen lokal im Browser (localStorage).

## Inhaltspipeline (das Herz der Anwendung)
- ZIM: Artikel per python-libzim oder kiwix-serve-API lesen → HTML bereinigen (Navigationsleisten,
  Bearbeiten-Links, Fußzeilen, Wikipedia-Infobox-Layout entfernen; Überschriften, Absätze, Listen,
  Tabellen, Bilder, Formeln behalten) → in das Papier-Template gießen. Bilder aus der ZIM ausliefern
  (Cache auf NVMe). Interne Links auf andere Artikel zeigen auf die Anwendung, nicht auf Kiwix.
- Stack Exchange: Frage + akzeptierte/bestbewertete Antwort als „Fall“ rendern (Frage-Block,
  Lösungs-Block, weitere Antworten einklappbar). Code mit Syntaxhervorhebung.
- PDF: mit pymupdf Text mit Struktur (Überschriften über Schriftgröße erkennen), eingebettete Bilder
  und Seitenausschnitte für Tabellen/Zeichnungen extrahieren → als Kapitelakten rendern.
  Layout-lastige Seiten (Zeichnungen, komplexe Tabellen): Seite als „eingeklebte Kopie“ im Rahmen.
  Einmalige Vorverarbeitung auf dem PC („Ingest“), Ergebnis als SQLite + Bildordner nach db/.
- Eigenes Material (Markdown, SQLite): direkt rendern; Fahrzeugakten als Werkstatt-Karteikarten,
  Abhängigkeitsbäume als interaktive Schalttafel-Grafik, Stücklisten als Formulartabellen mit Filter.
- Volltextsuche: SQLite FTS5 über alle ingestierten Texte + Weiterleitung an die Kiwix-Suche für
  Wikipedia-große Quellen. Optional semantische Suche via sqlite-vec + Qwen3-Embedding.
- RAG-Chat: Frage → Treffer aus FTS/Vektor → Kontext an llama-server → Antwort im Terminal mit
  nummerierten Quellen, die auf Akten verlinken. Modell darf nur aus Quellen antworten.

## Technische Leitplanken
- Backend: Python 3.12, FastAPI + Uvicorn, python-libzim, pymupdf, sqlite3 (FTS5, sqlite-vec),
  httpx für llama-server. Keine Datenbank-Server, keine Docker-Container auf dem Pi.
- Frontend: statisches HTML/CSS/JS ohne Build-Schritt (Vanilla oder ein winziges Framework als eine
  lokale Datei). CRT-Effekte rein in CSS. MapLibre GL JS lokal. Kein Node auf dem Pi nötig.
- Ingest-Werkzeug separat (läuft auf dem PC mit GPU für Embeddings): quintessenz-ingest, erzeugt
  db/index.sqlite, db/vectors.sqlite, db/images/. Wiederaufnehmbar, inkrementell.
- Konfiguration in YAML: Bereiche → Themen → Quellen (ZIM-Name, PDF-Pfad, Kategorie-Filter,
  kuratierte Einstiegsakten). WISSENSUEBERSICHT.md ist die Vorlage dafür.
- systemd-Unit, Start in < 10 s nach Boot, Watchdog, Logs nach RAM.
- Lizenzhinweise-Seite: alle Quellen mit Lizenz (CC BY-SA, Public Domain, Herstellerdoku,
  Privatkopie). Inhalte aus zim/eigene/privat/ sind als „NUR LOKAL“ gestempelt.
- Barrierefreiheit: alle Effekte abschaltbar, Kontrast im Papier-Modus ≥ 7:1, Schriftgröße
  skalierbar, vollständige Tastaturbedienung, Screenreader-taugliche Struktur.

## Was NICHT gebaut werden soll
- Kein Nutzerkonto, kein Login, keine Cloud, kein Update-Mechanismus über das Netz.
- Keine Bearbeitungsfunktion für Quellinhalte (eigenes Material wird außerhalb gepflegt).
- Kein Versuch, PDF-Layouts pixelgenau nachzubauen – wo es nicht geht, Seite als Bild im Rahmen.
- Keine generierten Bilder, keine Illustrationen, die nicht aus den Quellen stammen.
- Kein Spielzitat, keine Bethesda-Marken, kein Humor in Sicherheits- und Medizininhalten.

## Arbeitsweise und Lieferung
1. Zuerst ein klickbarer Prototyp mit DREI Bereichen (Elektrotechnik, Medizin, Eigene Fahrzeuge),
   je einem Thema, je drei Akten aus drei Quelltypen (ZIM-Artikel, Stack-Exchange-Fall, PDF-Kapitel),
   Startbildschirm, Terminal- und Papier-Ansicht – um Stil, Lesbarkeit und Menüführung zu prüfen,
   bevor die Pipeline vollständig gebaut wird. Prototyp auf einem 7-Zoll-Display UND einem Handy testen.
2. Dann die Ingest-Pipeline für alle Quelltypen, dann Suche, dann RAG, dann Kartentisch und Werkstatt.
3. Jeder Schritt lauffähig auf dem PC (mit D:\DoomsdayBox als Datenpfad) UND auf dem Pi.
4. Dokumentation: README (Start in 5 Minuten), CONFIG.md (Bereiche/Themen pflegen),
   DESIGN.md (Designsystem: Farbwerte, Schriften, Abstände, Komponenten, Effekte und ihre Schalter).
5. Code ins Repo github.com/pfeifferandreas1985-create/Quintessenz, Ordner app/ und ingest/.
Stelle Rückfragen, bevor du Annahmen über Bereichszuordnungen oder Designentscheidungen triffst,
die sich später schwer ändern lassen. Erkläre bei jedem Schritt, was auf dem Pi 5 wie schnell läuft.
```

---

## Warum so — zwei bewusste Entscheidungen

**Der Prototyp zuerst.** Drei Bereiche, neun Akten, klickbar — bevor jemand eine Pipeline für
40 ZIMs und 150 PDFs baut. Retro-Ästhetik ist Geschmackssache, und bei „futuristisch" wird gern
die Lesbarkeit geopfert. Das will man an neun Seiten sehen, nicht an neuntausend.

**Der Ingest läuft auf dem PC, nicht auf dem Pi.** Text aus 150 PDFs ziehen, Bilder extrahieren,
Embeddings rechnen — das dauert auf dem Pi Tage, auf dem Ryzen mit der RTX 3060 Stunden. Die
Anwendung selbst ist dann auf dem Pi schnell, weil sie nur noch fertig aufbereitete Daten liest.

## Verhältnis zu den anderen Dokumenten

| Dokument | Rolle |
|---|---|
| `01_KONZEPT.md` | Zielbild und Phasenplan der Box — das Terminal ist Phase 4 („Oberfläche") in ausgebauter Form |
| `03_SOFTWARE.md` | Dienste, auf die das Terminal aufsetzt (kiwix-serve, llama-server, sqlite-vec) |
| `04_WISSENSBASIS.md` und DoomsdayBox `doku/WISSENSUEBERSICHT.md` | Die 16 Bereiche und ihre Quellen — Vorlage für die YAML-Konfiguration |
| DoomsdayBox `UEBERGABE_Download-Agent.md` | Die Beschaffung der Inhalte, die das Terminal später anzeigt |
