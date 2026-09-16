# Wissensübersicht – Was das lokale Internet kann (Szenario Voll)

Stand 2026-09-15. Status: **geplant**, Beschaffung läuft noch nicht (D: ist FAT32, Downloads gesperrt). Zahlen sind Größenordnungen.

## 1. Auf einen Blick

| Kennzahl | Wert |
|---|---|
| Enzyklopädie-Artikel | ca. 2,9 Mio. deutsch (mit Bildern) + 6,9 Mio. englisch (Text) |
| Fragen/Antworten aus Fachforen (Stack Exchange) | ca. 3–4 Mio. Fragen mit Antworten, 16 Fachbereiche |
| Lehrbücher (Wikibooks DE/EN) | ca. 5.000 Bücher/Kurse |
| Reparaturanleitungen (iFixit DE/EN) | ca. 100.000 Anleitungen |
| Bücher Project Gutenberg | ca. 75.000 englisch, 3.500 deutsch |
| Praxisanleitungen (wikiHow DE, Appropedia) | ca. 30.000 + 10.000 |
| Medizin (WikiMed) | ca. 50.000 Artikel EN, ca. 10.000 DE, mit Bildern |
| PDF-Handbücher, Kataloge, Datenblätter | ca. 500–1.500 Dokumente |
| Karten | Europa vollständig (Straßen, Wege, Gebäude, Gewässer), Deutschland mit Routing und POI |
| KI-Modelle | 3 Sprachmodelle (0,8–9 B), 1 multimodal (Bild, Audio), Embedding, Sprache→Text, Text→Sprache |
| Sprachen | Deutsch und Englisch; Modelle übersetzen live |
| Gesamt | ca. 300 GB |

Zugriff: Browser im lokalen WLAN der Box. Volltextsuche über alle ZIMs (Kiwix), Suche über PDFs (SQLite), Chat mit dem Sprachmodell, das in den Quellen nachschlägt (RAG), Karte im Browser.

## 2. Wissensbereiche im Detail

Legende Tiefe: **Referenz** = Nachschlagen (Werte, Tabellen, Definitionen) · **Lehrbuch** = systematisches Lernen · **Praxis** = Schritt-für-Schritt-Anleitungen · **Q&A** = konkrete Problemfälle mit Lösungen

### 2.1 Elektrotechnik und Elektronik

| Was du nachschlagen kannst | Quelle | Tiefe | Sprache |
|---|---|---|---|
| Grundlagen: Ohm, Kirchhoff, Wechselstrom, Drehstrom, Leistung, Blindleistung | Wikibooks Elektrotechnik, Lessons in Electric Circuits Bd. 1–2, Wikipedia | Lehrbuch | DE/EN |
| Formelsammlung Elektrotechnik | Wikibooks, eigenes Tabellenbuch (SQLite) | Referenz | DE |
| Schaltzeichen nach IEC 60617 | Wikipedia, Commons-Symboltafel, KiCad-Bibliothek | Referenz | DE |
| Leitungsdimensionierung, Strombelastbarkeit, Spannungsfall, Kurzschluss, Selektivität (IEC-60364-Systematik) | ABB Installation Handbook, Schneider Installation Guide, Lapp/Helukabel-Tabellen | Referenz | EN/DE |
| Schutzmaßnahmen, fünf Sicherheitsregeln, Prüffristen, Schutzklassen, Schutzarten IP | DGUV Vorschrift 3, DGUV 203-xxx, TRBS | Referenz | DE |
| Halbleiter, Dioden, Transistoren, MOSFET, Thyristor, Triac, IGBT | Lessons Bd. 3, NEETS Mod. 7, Elektronik-Kompendium, Datenblätter | Lehrbuch + Referenz | DE/EN |
| Operationsverstärker, Filter, Regler, Analogtechnik | TI Op Amps for Everyone, ADI Linear Circuit Design, Pocket Reference | Lehrbuch + Referenz | EN |
| Digitaltechnik: Gatter, Flipflops, Zähler, Zahlensysteme | Lessons Bd. 4, Wikibooks Digitale Schaltungstechnik, NEETS Mod. 13 | Lehrbuch | DE/EN |
| Datenblätter ca. 200 Standardbauteile + eigene Projektteile | Herstellerdatenblätter | Referenz | EN |
| Konkrete Schaltungsprobleme („warum schwingt mein Regler“, „MOSFET wird heiß“) | Electrical Engineering Stack Exchange (ca. 180.000 Fragen) | Q&A | EN |
| Netzteile, Batterien, Laderegler, Inverter | Victron-Handbücher, NEETS, Wikipedia | Praxis | EN/DE |

### 2.2 Mechanik und Maschinenelemente

| Was | Quelle | Tiefe | Sprache |
|---|---|---|---|
| Statik, Festigkeitslehre, Kinematik, Dynamik | OpenStax University Physics, Wikibooks Technische Mechanik, Wikipedia | Lehrbuch | EN/DE |
| Wälzlager: Auswahl, Lebensdauer, Passungen, Schmierung | SKF-Hauptkatalog, Schaeffler HR1 | Referenz | DE |
| Toleranzen (ISO 286), Passungen, Gewinde (ISO metrisch, Rohr, Trapez) | Wikipedia, eigene berechnete Tabellen | Referenz | DE |
| Werkstoffkennwerte Stahl, Edelstahl, Aluminium, Kunststoffe | Hersteller-Datenblätter, eigene Werkstofftabelle (ca. 150 Werkstoffe) | Referenz | DE |
| Getriebe, Zahnräder, Riemen, Kupplungen, Antriebsauslegung | SEW Praxis der Antriebsauslegung, Wikipedia, Machinery's Handbook (alt) | Lehrbuch + Referenz | DE/EN |
| Zerspanung, Schweißen, Härten, Schmieden | Wikipedia, Wikibooks Werkstoffkunde, Farm Blacksmithing, Gingery (gekauft) | Praxis | DE/EN |
| Fahrzeug- und Motorreparatur | Motor Vehicle Maintenance SE, TM 9-8000, iFixit | Q&A + Praxis | EN/DE |

### 2.3 Antriebstechnik, Regelung, Sensorik

| Was | Quelle | Tiefe | Sprache |
|---|---|---|---|
| DC-, Schritt-, Servo-, BLDC-, Asynchronmotoren: Aufbau, Kennlinien, Ansteuerung | NEETS Mod. 5/15, Microchip AN885/AN907, Trinamic, Hawkins (alt) | Lehrbuch + Referenz | EN |
| Frequenzumrichter: Funktion, Parametrierung, Fehlercodes (Siemens G120/V20, Danfoss) | Danfoss Facts Worth Knowing, Siemens-Handbücher | Referenz | DE/EN |
| Regelungstechnik, PID, Einstellregeln, Stabilität | Åström/Murray Feedback Systems, Wikibooks Regelungstechnik, eigene Karte | Lehrbuch + Referenz | EN/DE |
| 4–20 mA, Thermoelemente (Typ J/K/T-Tabellen), Pt100/Pt1000-Tabellen, Näherungsschalter, Encoder | WIKA-Handbuch, NIST ITS-90, ifm/P+F-Broschüren, eigene SQLite-Tabellen | Referenz | DE/EN |
| Pneumatik, Hydraulik: Symbole, Ventile, Zylinder, Schaltpläne | NAVEDTRA 14105 Fluid Power, Festo/SMC-Broschüren, eigene ISO-1219-Tafel | Lehrbuch | EN/DE |

### 2.4 SPS und Automatisierung

| Was | Quelle | Tiefe | Sprache |
|---|---|---|---|
| IEC 61131-3: ST, KOP, FUP, AWL, Ablaufsprache | PLCopen Coding Guidelines, Beckhoff InfoSys, CODESYS-Hilfe, Siemens STEP 7 | Lehrbuch + Referenz | DE/EN |
| Über 500 fertige ST-Bausteine mit Quellcode (Regler, Zeit, Mathematik, Gebäude, Netzwerk) | OSCAT Basic/Building/Network | Referenz + Code | DE/EN |
| Siemens S7-1200/1500: Systemhandbuch, Befehle, Kommunikation | Siemens-Handbücher | Referenz | DE |
| Beckhoff TwinCAT komplett | InfoSys offline (3–6 GB) | Referenz | DE/EN |
| Relaislogik als SPS-Ersatz, Selbsthaltung, Verriegelung | eigenes Material, Wikipedia | Praxis | DE |

### 2.5 Mess- und Prüftechnik, Fehlersuche

| Was | Quelle | Tiefe | Sprache |
|---|---|---|---|
| Oszilloskop-Grundlagen, Tastköpfe, Triggern | Tektronix XYZs, R&S Fundamentals | Lehrbuch | EN |
| Multimeter, Isolationsmessung, Wärmebild | Fluke-Broschüren | Praxis | DE |
| Diagnosebäume: Motor läuft nicht, FU-Fehler, Sensor liefert Unsinn, SPS nicht in RUN, Netzteil schaltet ab | eigenes Material | Praxis | DE |
| Kalibrieren ohne Referenzgeräte (Eispunkt, Siedepunkt, Wassersäule) | eigenes Material, rebuild_trees.db | Praxis | DE |

### 2.6 Programmierung und Linux

| Was | Quelle | Tiefe | Sprache |
|---|---|---|---|
| C: Sprache, Standardbibliothek, Embedded-Stil | Modern C, Beej's Guide, cppreference, DevDocs C/C++, Barr Coding Standard, avr-libc | Lehrbuch + Referenz | EN |
| Python 3 komplett + Automatisierung | Offizielle Doku, DevDocs Python, Automate the Boring Stuff, Wikibooks | Lehrbuch + Referenz | EN/DE |
| Bash, Shell, systemd, Netzwerk, Debian/Raspberry Pi OS | Debian Handbook, The Linux Command Line, ArchWiki, DevDocs Bash, man-pages | Lehrbuch + Referenz | EN |
| Konkrete Fehler und Konfigurationsfragen | Unix & Linux SE, Ask Ubuntu, Super User, Raspberry Pi SE, Arduino SE | Q&A | EN |
| Arduino, Raspberry Pi, ESP32, RP2040 | Pi-Dokumentation, Datenblätter, Arduino SE | Referenz + Q&A | EN |
| Installierbare Software für den Pi ohne Internet | pip-Wheels, .deb-Pakete, llama.cpp, kiwix-tools, Quellcode | – | – |
| Nicht enthalten | Stack Overflow (80 GB, optional), IDE-Doku, kommerzielle Bücher | | |

### 2.7 Medizin

| Was | Quelle | Tiefe | Sprache |
|---|---|---|---|
| Krankheiten, Symptome, Medikamente, Anatomie: ca. 50.000 Artikel mit Bildern | WikiMed EN (+ DE, falls verfügbar) | Referenz | EN/DE |
| Behandlung ohne Arzt: Untersuchung, häufige Krankheiten, Geburt, Kinder, Zähne | Hesperian Where There Is No Doctor / Dentist / Women / Midwives, dt. Ausgabe | Praxis | EN/DE |
| Erste Hilfe, Reanimation (aktuelle ERC-Leitlinien), Wundversorgung, Frakturen | ERC 2021 deutsch, DGUV 204-006, Wikibooks Erste Hilfe | Praxis | DE |
| Blutungskontrolle, Tourniquet, Thorax, Schock (taktisch und zivil) | TCCC, TECC, Stop the Bleed, FM 21-11 / TC 4-02.1 | Praxis | EN |
| Chirurgie ohne Klinik, Anästhesie mit einfachen Mitteln | Emergency War Surgery, WHO Surgical Care, WHO Anaesthesia, Primary Surgery | Lehrbuch + Praxis | EN |
| Medikamente, Dosierungen Erwachsene/Kinder, Wechselwirkungen | WHO Model Formulary, Essential Medicines List, MSF Essential Drugs, OpenStax Pharmacology, eigene Dosistabelle | Referenz | EN/DE |
| Infektionskrankheiten, Hygiene, Wasserqualität, Quarantäne | WHO Drinking-water, CDC, RKI, zimgit-medicine | Referenz | EN/DE |
| Anatomie und Physiologie vollständig | OpenStax A&P 2e | Lehrbuch | EN |
| Verlängerte Versorgung über Tage ohne Abtransport | Prolonged Field Care | Praxis | EN |
| Nicht enthalten | Fachinformationen einzelner Präparate (nur die der eigenen Hausapotheke), Labormedizin, Bildgebung | | |

### 2.8 Survival und Grundversorgung

| Was | Quelle | Tiefe | Sprache |
|---|---|---|---|
| Wasser finden, filtern, entkeimen (Chlor, SODIS, Biosand, Abkochen) | zimgit-water, SODIS, CAWST, WHO | Praxis | EN |
| Nahrung: Einkochen, Trocknen, Fermentieren, Räuchern, Haltbarkeit | USDA Home Canning, NCHFP, zimgit-food, BZfE | Praxis | EN/DE |
| Pflanzen und Pilze erkennen (mit Bildern) | Wikipedia DE maxi, eigene Themen-ZIMs | Referenz | DE |
| Feuer, Unterschlupf, Orientierung, Signale, Klima | FM 21-76/ATP 3-50.21, zimgit-post-disaster, Outdoors SE | Praxis | EN |
| Landwirtschaft: Boden, Saatgut, Fruchtfolge, Kleintiere, Zugtiere | FAO-Publikationen, Gardening SE, Farmers of Forty Centuries, Wikibooks | Lehrbuch + Q&A | EN |
| Bauen, Holz, Haus reparieren | Home Improvement SE, Woodworking SE, TM 5-704, wikiHow | Q&A + Praxis | EN/DE |
| Alltagsanleitungen aller Art (ca. 30.000) | wikiHow DE | Praxis | DE |
| Angepasste Technik für einfache Mittel (Öfen, Pumpen, Solar, Sanitär) | Appropedia, Low-tech Magazine, VITA Village Technology | Praxis | EN |

### 2.9 Energie und Infrastruktur

| Was | Quelle | Tiefe | Sprache |
|---|---|---|---|
| PV-Anlagen auslegen, Inselsysteme, Batterien, LiFePO4, BMS | Sandia Handbook, Victron Wiring Unlimited, energypedia, Zellen-Datenblätter | Lehrbuch + Referenz | EN |
| Generatoren, Verbrennungsmotoren, Lichtmaschinen | TM 9-8000, TM 5-6115, Hawkins | Lehrbuch | EN |
| Holzgas, Biogas, Wasserkraft, Windkraft | FEMA Wood Gas, Sasse Biogas, Practical Action Micro-Hydro | Praxis | EN |
| Pumpen, Wasserversorgung, Sanitär, Kompost-Toilette, Abwasser | Grundfos Pump Handbook, Eawag Compendium, Humanure Handbook, Akvopedia | Lehrbuch + Praxis | EN |

### 2.10 Kommunikation

| Was | Quelle | Tiefe | Sprache |
|---|---|---|---|
| Amateurfunk-Theorie, Prüfungsfragen N/E/A, Bandpläne, Frequenzplan | BNetzA, DARC, Amateur Radio SE | Lehrbuch + Referenz | DE/EN |
| Antennenbau, Wellenausbreitung | NEETS Mod. 10, Wikipedia, eigene Rechenkarten | Lehrbuch | EN/DE |
| Notfunk-Frequenzen (PMR, CB, Marine, Flug, Wetter), Morse, Buchstabiertafel | eigene Tabellen, Wikipedia | Referenz | DE |
| Meshtastic, Reticulum, LoRa: Doku, Firmware, Flasher | Meshtastic Docs, Reticulum Manual, Semtech-Datenblätter | Referenz + Software | EN |
| Lokales Netz ohne Internet aufbauen (WLAN-AP, DNS, Kiwix freigeben) | Debian Handbook, eigene HowTos | Praxis | DE/EN |
| Funkdisziplin, Meldeschemata (SITREP, MEDEVAC) | FM 24-18, FM 6-99, eigene Karten | Referenz | EN/DE |

### 2.11 Militärische Grundlagen (defensiv)

| Was | Quelle | Tiefe | Sprache |
|---|---|---|---|
| Wachdienst, Beobachtung, Deckung, Tarnung, Meldungen | FM 22-6, FM 21-75, FM 20-3, Reibert-Zusammenfassung | Praxis | EN/DE |
| Objektschutz, Zugangskontrolle, Gebäudesicherung | ATP 3-39.32, FEMA 426/427, FM 3-06, FM 90-10 | Lehrbuch | EN |
| IED und Sprengfallen erkennen, Abstand, Melden | DHS/FEMA IED Awareness, UNMAS Lexicon, FM 5-31 Erkennungskapitel | Referenz | EN |
| ABC-Schutz: Atemschutz improvisieren, Räume abdichten, Dekontamination | FM 3-11.x, BBK, BfS, SSK | Praxis | EN/DE |
| Strahlenschutz, improvisiertes Dosimeter (Kearny Fallout Meter), Schutzraum | Nuclear War Survival Skills | Praxis | EN |
| Quarantäne, Epidemie, Umgang mit Toten | RKI, WHO/PAHO, Sphere Handbook | Referenz | DE/EN |
| Karte, Kompass, Sternnavigation, Marsch, Fußpflege | TC 3-25.26, FM 21-18 | Lehrbuch | EN |
| Notwehrrecht (StGB, BGB), Verhältnismäßigkeit | gesetze-im-internet.de, eigene Zusammenfassung | Referenz | DE |
| Führung, Auftragstaktik, Entscheidung unter Stress | ADP 6-0, ADP 6-22, Reibert-Zusammenfassung | Lehrbuch | EN/DE |
| Nicht enthalten | Waffen, Schießausbildung, Angriffstaktik, Bauanleitungen, Bundeswehr-Vorschriften im Original | | |

### 2.12 Zivilisationsneustart

| Was | Quelle | Tiefe | Sprache |
|---|---|---|---|
| Was nach dem Kollaps wie lange nutzbar bleibt, Neustart-Reihenfolge | Dartnell The Knowledge (gekauft), THE BOOK (gekauft) | Lehrbuch | DE/EN |
| **Abhängigkeitsbäume**: 10 Kerntechnologien (Motor, Generator, Trafo, Draht, Lager, Akku, Funk, Schalter, SPS-Ersatz, Sensoren) bis zum Rohstoff, mit minimaler Produktionsgröße und 9 Prozessanleitungen | rebuild_trees.db (eigenes Material, **bereits vorhanden**) | Referenz + Praxis | DE |
| Metallurgie: Holzkohle, Schmelzofen, Guss, Schmieden, Härten, Drahtziehen, Drehbank aus Schrott | Gingery (gekauft), Farm Blacksmithing, Hawkins, FAO Charcoal, Machinery's Handbook alt | Praxis | EN |
| Chemie: Säuren, Laugen, Soda, Seife, Glas, Kalk, Zement | Henley's Formulas, Rogers Industrial Chemistry, Thorpe, Practical Action | Referenz | EN |
| Textil, Leder, Papier, Druck | Hand-Loom Weaving, USDA Bulletins, Practical Action Papermaking | Praxis | EN |
| Frühe Elektrotechnik von Grund auf (Generatoren, Motoren, Telegraf, Röhrenfunk um 1917–1928) | Hawkins Electrical Guide, Radio Amateur's Handbook 1926–28 | Lehrbuch | EN |
| Arzneimittel, Anästhesie, Chirurgie mit einfachen Mitteln | WHO Anaesthesia, Primary Surgery, King's Dispensatory | Lehrbuch | EN |
| Gemeinschaft organisieren, Hygiene-Mindeststandards, Bildung | Sphere Handbook, UNHCR Handbook, UNESCO, OpenStax | Referenz | EN |
| Nicht enthalten | Waffen-, Sprengstoff-, Kerntechnik, Drogensynthese | | |

### 2.13 Allgemeinwissen, Sprache, Literatur

| Was | Quelle | Umfang |
|---|---|---|
| Deutsche Wikipedia komplett mit Bildern | wikipedia_de_all_maxi | 2,9 Mio. Artikel |
| Englische Wikipedia komplett, ohne Bilder | wikipedia_en_all_nopic | 6,9 Mio. Artikel |
| Wörterbuch Deutsch (Bedeutung, Übersetzung, Grammatik) | Wiktionary DE | 1 Mio. Einträge |
| Lehrbücher und Kurse aller Fächer | Wikibooks DE/EN, Wikiversity DE | 5.000 |
| Weltliteratur gemeinfrei (bis ca. 1929) | Gutenberg EN/DE | 75.000 + 3.500 Bücher |
| Physik-Fragen | Physics SE | 250.000 Fragen |

### 2.14 Karten und Navigation

| Was | Quelle | Umfang |
|---|---|---|
| Straßen, Wege, Gebäude, Gewässer, Landnutzung, Ortsnamen, alle Zoomstufen | PMTiles Europa, DACH, Deutschland | Europa komplett |
| Routing Auto/Rad/Fuß offline | GraphHopper mit Deutschland-Graph | Deutschland |
| Suchbare Orte: Trinkwasser, Brunnen, Quellen, Apotheken, Krankenhäuser, Tankstellen, Baumärkte, Feuerwehr, Notunterkünfte, Elektriker, Schmiede | POI-SQLite aus OSM | Deutschland |
| Höhenlinien, Relief | optional OpenTopoMap | DACH |
| Nicht enthalten | Satellitenbilder, Luftbilder, Live-Daten | |

### 2.15 KI-Fähigkeiten

| Fähigkeit | Modell | Was es bedeutet |
|---|---|---|
| Fragen beantworten mit Quellenbezug (RAG) | Qwen3.5-9B + Qwen3-Embedding | „Wie lege ich einen 5,5-kW-Motor an 400 V ab, Leitungslänge 40 m?“ → Antwort mit Verweis auf Tabelle |
| Deutsch/Englisch übersetzen und zusammenfassen | Qwen3.5-9B, Gemma 4 E4B | englische Handbücher auf Deutsch lesen |
| Fotos verstehen | Gemma 4 E4B | Typenschild fotografieren → Motordaten; Schaltplanausschnitt erklären |
| Sprache eingeben / vorlesen | whisper.cpp, Piper | Bedienung mit schmutzigen Händen |
| Code schreiben und erklären | Qwen3.5-9B | C, Python, Structured Text, Bash |
| Scans durchsuchbar machen | tesseract deu/eng | eigene Papierunterlagen einlesen |
| Grenzen | | ca. 2–3 Token/s beim 9B-Modell auf dem Pi; kein Internet-Faktenabgleich; Modell kann irren, deshalb immer Quelle anzeigen |

### 2.16 Eigene Fahrzeuge

| Fahrzeug | Was du nachschlagen kannst | Quelle | Tiefe |
|---|---|---|---|
| **Land Rover Defender 110 TD5** (1998–2006) | Werkstatthandbuch komplett mit Schaltplänen, Ersatzteilkatalog mit Explosionszeichnungen und Teilenummern je Baugruppe, Diagnose (Nanocom), Füllmengen, Drehmomente, Wartungsplan, bekannte Schwachstellen (Öl im Steuergerätestecker, Injektordichtungen, Ölpumpenschraube, Kopfriss, Rahmenrost) | Workshop Manual + Electrical Library (Brooklands), Parts Catalogue STC9021CC, lrcat/Britpart/Paddock-Zeichnungen, Haynes 3017, Fahrzeugakte | Referenz + Praxis |
| **Rover Mini Cooper 1.3i MPi „British Open Classic“** (1999) | Werkstatthandbuch inkl. MPi-Nachtrag, MEMS-2J-Schaltplan, Explosionszeichnungen aller Baugruppen mit Nummern, Fahrwerkseinstellung (Gummikonen, Kugelgelenke), Rostschwerpunkte (Schweller, A-Säulen, hinterer Hilfsrahmen) | Rover Workshop Manual (Brooklands), Mini Parts Catalogue, minispares.com-Zeichnungen, Haynes 0646, Fahrzeugakte | Referenz + Praxis |
| **Vespa V50 N, V5A1T** (1963) | Piaggio-Werkstatthandbuch, Original-Ersatzteilkatalog mit Explosionszeichnungen, Bedienungsanleitung 1963, aktuelle Teilenummern (SIP, Scooter Center), Zündung einstellen, Vergaser SHB 16/10 bedüsen, Motor teilen, Falschluft suchen | scooterhelp.com-Scans, SIP/Scooter-Center-Zeichnungen, Bucheli, GSF-Wiki, Fahrzeugakte | Referenz + Praxis |
| Alle drei: **Fahrzeugakten** (bereits vorhanden) | Kenndaten, Füllmengen, Drehmomente, Einstellwerte (40), Stückliste Verschleißteile mit OEM-Nummern (68), Schwachstellen mit Abhilfe (25), Wartungsplan (24), Dokumentenliste (18), Logbuch | `own/fahrzeuge/fahrzeuge.db` + `Fahrzeugakte_*.md`; Werte aus dem Gedächtnis sind als „prüfen“ markiert | Referenz |
| Allgemein Kfz | Motor-, Getriebe-, Bremsen-, Elektrikreparatur, Fehlersuche | Motor Vehicle Maintenance SE, TM 9-8000, iFixit | Q&A + Lehrbuch |

## 3. Was bewusst fehlt

- DIN/VDE/IEC-Normen im Original (nur eigene Zusammenfassungen und IEC-nahe Herstellerhandbücher).
- Kommerzielle Tabellenbücher und Standardwerke (Europa, Roloff/Matek, Dubbel, Reibert, Dartnell, Gingery): nur, wenn du sie kaufst und selbst ablegst.
- Stack Overflow (80 GB), Wikipedia EN mit Bildern (110 GB): optional, nicht im Standardumfang.
- Videos, Kurse, Podcasts jeglicher Art.
- Aktuelle Nachrichten, Wetterdaten, Preise, alles Zeitkritische.
- Fachinformationen zu Medikamenten außer denen der eigenen Hausapotheke.
- Waffen, Sprengstoff, Kerntechnik, Angriffstaktik, Drogensynthese.

## 4. Was heute schon da ist

| Bestand | Ort | Status |
|---|---|---|
| Abhängigkeitsbäume (53 Technologien, 78 Kanten, 9 Prozesse) | `D:\DoomsdayBox\own\rebuild\rebuild_trees.db` | vorhanden |
| Fahrzeugakten Defender 110 TD5, Mini Cooper MPi 1999, Vespa V50 1963 (40 Kenndaten, 68 Teile, 25 Schwachstellen, 24 Wartungspunkte, 18 Dokumente) | `D:\DoomsdayBox\own\fahrzeuge\` | vorhanden |
| Spezifikation, Übergabe, Skripte, Quellenlisten | `D:\DoomsdayBox\doku`, `tools` | vorhanden |
| llama.cpp (Win/Linux/ARM64), Ollama, kiwix-tools (Win/Linux/aarch64), kiwix-desktop | `D:\AI-ARK\00_RUNTIME` | vorhanden |
| Modelle | `D:\AI-ARK\01_MODELS` | 15 GB Fragmente, durch FAT32 abgebrochen |
| ZIMs, PDFs, Karten, Pi-Modelle | – | **0 %, wartet auf Neuformatierung von D:** |
