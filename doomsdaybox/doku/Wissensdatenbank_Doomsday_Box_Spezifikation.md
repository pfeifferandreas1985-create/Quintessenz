# Spezifikation Wissensdatenbank – Offline-Wissens- und KI-Box (Mechatronik-Fokus)

Zielplattform: Raspberry Pi 5, 16 GB RAM, 1 TB NVMe. Betrieb ohne Internet, Stromnetz und externe Infrastruktur.
Stand: September 2026. Alle Größenangaben sind Schätzwerte auf Basis der Kiwix-Bibliothek und typischer Dateigrößen; vor dem Download im Katalog (library.kiwix.org) prüfen, Werte ändern sich mit jedem Monatsbuild.

---

## 0. Betriebsarchitektur (Kurzfassung)

| Schicht | Komponente | Zweck |
|---|---|---|
| Speicher | ext4 auf NVMe, Verzeichnisbaum `/srv/box/{zim,pdf,db,maps,models,src,own}`; `own/` untergliedert nach Modulen (`mech`, `med`, `surv`, `mil`, `rebuild`) | ein Wurzelpfad, damit Spiegelung per `rsync` trivial bleibt |
| Browsing | kiwix-serve (ARM64) mit `library.xml` | ZIM-Volltextsuche (Xapian) für alle ZIM-Quellen |
| PDF | Web-Verzeichnis + pdf.js, Index in SQLite FTS5 (Text per `pdftotext`/PyMuPDF extrahiert) | Handbücher durchsuchbar ohne Öffnen |
| Eigenes Wissen | SQLite mit FTS5 + sqlite-vec; Markdown-Quellen im Git-Repo | Tabellenbuch, Formeln, Normen-Zusammenfassungen, Diagnosebäume |
| Karten | PMTiles + MapLibre GL JS (lokal), optional GraphHopper für Routing | Offline-Navigation im Browser |
| KI | llama.cpp (llama-server) mit GGUF-Modellen; Embeddings via bge-m3 | RAG über eigenes Wissen, PDF-Index und ZIM-Treffer |
| Zugriff | WLAN-Access-Point (hostapd + dnsmasq), Weboberfläche | jedes Smartphone/Laptop im Umkreis kann lesen |

RAG-Hinweis: Eine Vektor-Indexierung der gesamten Wikipedia ist auf dem Pi nicht sinnvoll (Millionen Artikel, Wochen Rechenzeit). Empfohlen ist ein hybrider Ansatz: Vektor-Index nur für Priorität 1–2 (eigenes Tabellenbuch, PDF-Bibliothek, WikiMed, Elektronik-Quellen, ca. 5–10 GB Text), lexikalische Suche (Xapian in libzim) für Wikipedia und Stack Exchange. Embeddings werden vorab auf einem PC mit GPU berechnet und als SQLite-Datei auf die Box kopiert. Prompt-Verarbeitung auf dem Pi ist langsam (ca. 20–50 Token/s bei 8B), daher RAG-Kontext auf 2.000–3.000 Token begrenzen.

---

## 1. Quellentabelle

Spalten: Wissensbereich | Konkrete Quelle (Name, Herausgeber, Lizenz) | Format | Geschätzte Größe | Priorität | Beschaffungsweg | Besonderheiten

Beschaffungsweg: **frei** = frei lizenziert oder Public Domain, weiterverteilbar (ggf. mit NC-Einschränkung) · **frei (Herst.)** = kostenloser Download, urheberrechtlich geschützt, Eigennutzung · **frei (Privatkopie)** = öffentliche Website, Offline-Kopie nur für Eigengebrauch (§ 53 UrhG), keine Weitergabe · **kommerziell** = kaufen · **eigen** = selbst erstellen

### 1.1 Mechatronik-Kern (Priorität 1)

| Wissensbereich | Konkrete Quelle | Format | Größe | Prio | Beschaffung | Besonderheiten |
|---|---|---|---|---|---|---|
| Elektrotechnik: Grundlagen, Kirchhoff, Drehstrom, Formelsammlung | Wikibooks DE „Elektrotechnik“, „Formelsammlung Elektrotechnik“, „Digitale Schaltungstechnik“, „Regelungstechnik“ (Wikimedia, CC BY-SA 4.0) | ZIM `wikibooks_de_all_maxi` | 1,3 GB | 1 | frei | ein ZIM deckt mehrere Bereiche ab; Qualität artikelweise unterschiedlich |
| Elektrotechnik/Elektronik, Lehrbuchreihe (EN) | „Lessons in Electric Circuits“ Bd. 1–6, T. Kuphaldt (Design Science License) | PDF + HTML→ZIM | 60 MB | 1 | frei | DC, AC, Halbleiter, Digital, Referenz, Experimente; ideal als RAG-Korpus |
| Elektronik, Messtechnik, Motoren, Antennen (EN) | NEETS „Navy Electricity and Electronics Training Series“, Module 1–24 (US Navy, Public Domain) | PDF | 250 MB | 1 | frei | älter, aber grundlagensicher; Module 5/15 Motoren/Generatoren, 10 Antennen, 16 Messtechnik |
| Elektronik, Praxiswissen (DE) | Elektronik-Kompendium.de (P. Schnabel, urheberrechtlich geschützt) | ZIM via zimit | 0,5–1 GB | 1 | frei (Privatkopie) | Konvertierung mit zimit auf x86-PC (Docker); keine Weitergabe |
| Elektronik, Fragen/Antworten | Electrical Engineering Stack Exchange (Stack Exchange Inc., CC BY-SA 4.0) | ZIM `electronics.stackexchange.com_en_all` | 2 GB | 1 | frei | Fehlersuche, Bauteilwahl, Schaltungsreview |
| Operationsverstärker, Analogtechnik, Filter | TI „Op Amps for Everyone“, TI „Analog Engineer's Pocket Reference“, ADI „Linear Circuit Design Handbook“, ADI „Op Amp Applications Handbook“ | PDF | 100 MB | 1 | frei (Herst.) | Registrierung teils nötig; Filterentwurf-Tabellen enthalten |
| Halbleiter, Transistoren, Thyristoren, Leistungselektronik | Datenblätter und Application Notes (Infineon, ST, TI, onsemi, Microchip, Nexperia, Vishay) | PDF | 1–5 GB | 1 | frei (Herst.) | eigene Auswahl: alle in eigenen Projekten verbaute Teile plus ca. 200 Standardtypen (1N4007, BC547, IRFZ44N, LM358, NE555, TL431, ATmega328P …); Dateiname = Typbezeichnung |
| Schaltzeichen (DIN EN 60617 / IEC 60617) | Wikipedia „Schaltzeichen“, „Liste der Schaltzeichen“; Wikimedia Commons „Category:Electrical symbols“ (CC BY-SA / PD); KiCad-Symbolbibliothek (CC0) | ZIM (in Wikipedia) + SVG + MD | 200 MB | 1 | frei | Norm nicht kopieren; eigene Übersichtstafel als Markdown/SVG aus Commons-Symbolen; KiCad-Libs als IEC-nahe Referenz |
| Schutzmaßnahmen, Arbeiten an elektrischen Anlagen | DGUV Vorschrift 3, DGUV Information 203-xxx, DGUV Regel 103-011, TRBS 1201/1203, BG ETEM Lernmedien (frei abrufbar) | PDF | 200 MB | 1 | frei | fünf Sicherheitsregeln, Prüffristen, Schutzklassen, Schutzarten; ersetzt VDE 0100/0105 nicht, deckt aber die Praxis |
| Leitungsdimensionierung, Installation (IEC-60364-Systematik) | ABB „Electrical Installation Handbook“ Vol. 1+2; Schneider Electric „Electrical Installation Guide“; Lapp/Helukabel „Technische Tabellen“ (Strombelastbarkeit, Verlegearten) | PDF | 150 MB | 1 | frei (Herst.) | IEC-60364-Inhalte sind inhaltlich weitgehend deckungsgleich mit VDE 0100-430/-520; Spannungsfall, Kurzschlussstrom, Selektivität |
| Tabellenbuch Elektrotechnik/Mechatronik | Europa-Lehrmittel „Tabellenbuch Elektrotechnik“, „Tabellenbuch Mechatronik“; Westermann „Friedrich Tabellenbuch“ | PDF (E-Book) | 100 MB | 1 | kommerziell | nur als gekauftes E-Book; DRM verhindert oft die Ablage als PDF → eigenes Tabellenbuch (Zeile unten) ist der Plan A |
| Mechanik: Statik, Festigkeit | OpenStax „University Physics“ Bd. 1 (CC BY 4.0); Wikibooks DE „Technische Mechanik“; Wikipedia | PDF + ZIM | 100 MB | 1 | frei | Roloff/Matek, Dubbel, Hütte nur kommerziell (Springer E-Book, DRM-frei als PDF erhältlich) |
| Maschinenelemente: Lager, Getriebe, Gewinde, Toleranzen | SKF „Wälzlager-Hauptkatalog“, Schaeffler „Wälzlager HR1“; Wikipedia „ISO-Toleranz“, „Metrisches ISO-Gewinde“, „Passung“; eigene SQLite-Tabellen | PDF + SQLite | 500 MB | 1 | frei (Herst.) + eigen | ISO-286-Toleranzfelder und Gewindetabellen selbst berechnen (Formeln sind öffentlich), nicht aus Normen abschreiben |
| Materialkennwerte | Werkstoffdatenblätter (thyssenkrupp, Deutsche Edelstahlwerke, Ensinger für Kunststoffe, Aluminium-Verband); Wikipedia; eigene Werkstofftabelle | PDF + SQLite | 200 MB | 1 | frei (Herst.) + eigen | eigene Tabelle mit ca. 150 Werkstoffen (E, Rm, Re, Dichte, α, λ, Härte, Bearbeitbarkeit, Schweißeignung) |
| Antriebstechnik: Auslegung, Getriebemotoren, Frequenzumrichter | SEW-Eurodrive „Praxis der Antriebsauslegung“ + Handbuchreihe „Antriebstechnik in der Praxis“; Danfoss „Facts Worth Knowing about Frequency Converters“; Siemens SINAMICS G120/V20 Betriebsanleitungen | PDF | 500 MB | 1 | frei (Herst.) | Parameterlisten und Fehlercode-Tabellen der eigenen FU-Typen unbedingt ablegen |
| Motoren: DC, Schrittmotor, Servo, BLDC | Microchip AN885 (BLDC), AN907 (Stepper); TI DRV8xxx-Datenblätter; Trinamic TMC-Datenblätter; NEETS Modul 5/15 | PDF | 300 MB | 1 | frei (Herst.) | Kommutierung, Mikroschritt, Encoder-Auswertung |
| Regelungstechnik, PID | Åström/Murray „Feedback Systems“ 2. Aufl. (Princeton, PDF frei); Wikibooks DE „Regelungstechnik“; Wikipedia | PDF + ZIM | 30 MB | 1 | frei | Einstellregeln (Ziegler-Nichols, CHR, Lambda-Tuning) zusätzlich als eigene Markdown-Karte |
| Sensorik: 4–20 mA, Thermoelemente, RTD, Näherungsschalter, Encoder | WIKA „Handbuch Druck- und Temperaturmesstechnik“; ifm, Pepperl+Fuchs, SICK, Balluff Grundlagenbroschüren; NIST ITS-90 Thermoelement-Tabellen (Public Domain); Pt100/Pt1000-Tabelle selbst berechnet (Callendar-Van-Dusen) | PDF + SQLite | 300 MB | 1 | frei (Herst.) + eigen | TC- und RTD-Tabellen als SQLite, damit das LLM sie per Abfrage nutzen kann |
| Pneumatik/Hydraulik | US Navy NAVEDTRA 14105 „Fluid Power“ (Public Domain); Festo/SMC/Bosch Rexroth Grundlagenbroschüren (frei); Festo Didactic Lehrbücher (kommerziell); Wikipedia; eigene Symboltafel ISO 1219 | PDF + MD | 200 MB | 1 | frei / kommerziell | ISO-1219-Symbole als eigene SVG-Tafel aus Commons-Symbolen |
| SPS: IEC 61131-3 (AWL, KOP, FUP, ST), PLCopen | PLCopen „Coding Guidelines“ (frei, Registrierung); OSCAT Basic/Building/Network Doku + Quellcode (frei); Beckhoff InfoSys Offline-Installation (frei); Siemens S7-1200/1500 Systemhandbücher, STEP 7 Handbücher (frei); CODESYS Online-Hilfe (frei) | PDF + HTML→ZIM + Quellcode | 3–6 GB (InfoSys groß) | 1 | frei (Herst.) | Norm IEC 61131-3 selbst nur kommerziell; OSCAT liefert über 500 ST-Bausteine als Beispielcode → RAG-Korpus für ST |
| Mess- und Prüftechnik, Fehlersuche | Tektronix „XYZs of Oscilloscopes“; Rohde & Schwarz „Oscilloscope Fundamentals“; Fluke Grundlagenbroschüren (Multimeter, Isolationsmessung, Wärmebild); eigene Diagnosebäume | PDF + MD | 100 MB | 1 | frei (Herst.) + eigen | Diagnosebäume als Markdown mit Ja/Nein-Struktur: Motor läuft nicht, FU-Fehler, Sensor 0 mA/>20 mA, SPS geht nicht in RUN, Netzteil schaltet ab |
| Eigenes Tabellenbuch und Formelsammlung | eigene strukturierte Zusammenfassung: Formeln, Einheiten, Werkstoffe, Normen-Kernaussagen mit Quellenangabe, Anschlussbelegungen, Farbcodes, Schutzarten | SQLite (FTS5 + sqlite-vec) + Markdown | 50–200 MB | 1 | eigen | Kernstück der RAG-Pipeline; Normen nur als eigene Zusammenfassung in eigenen Worten |
| Embedded-Community (DE) | mikrocontroller.net Artikelsammlung (Wiki-Teil, urheberrechtlich geschützt) | ZIM via zimit | 300 MB | 2 | frei (Privatkopie) | nur Artikel, nicht das Forum |
| Arduino, Raspberry Pi | Arduino SE, Raspberry Pi SE (CC BY-SA 4.0); Raspberry Pi Documentation (CC BY-SA 4.0); RP2040/RP2350-Datenblätter; ESP32 Technical Reference | ZIM + PDF | 800 MB | 2 | frei | Pi-Doku als Git-Klon oder zimit |
| Reparatur allgemein | iFixit (iFixit, CC BY-NC-SA 3.0) | ZIM `ifixit_de_all`, optional `ifixit_en_all` | 2 GB (DE), 3,5 GB (EN) | 2 | frei | NC-Lizenz: keine kommerzielle Weitergabe |

### 1.2 Programmierung (Priorität 1–2)

| Wissensbereich | Konkrete Quelle | Format | Größe | Prio | Beschaffung | Besonderheiten |
|---|---|---|---|---|---|---|
| C (Embedded) | „Modern C“ (J. Gustedt, CC BY-NC-ND); „Beej's Guide to C Programming“ (frei); cppreference Offline-Archiv (CC BY-SA 3.0); avr-libc-Doku; GCC-Handbuch (GFDL); Barr Group „Embedded C Coding Standard“ (frei, Registrierung) | PDF + HTML→ZIM | 300 MB | 1 | frei | K&R und MISRA C nur kommerziell |
| C, C++, Python, Bash Referenz | DevDocs-ZIMs `devdocs_en_c`, `devdocs_en_cpp`, `devdocs_en_python`, `devdocs_en_bash` (Kiwix/DevDocs, jeweilige Dokulizenz) | ZIM | 300 MB | 1 | frei | kompakt, saubere Struktur, sehr gut für RAG |
| Python | offizielle Python-3-Dokumentation (PSF-Lizenz, HTML/PDF-Download); „Automate the Boring Stuff“ (CC BY-NC-SA); „Think Python“ (CC BY-NC-SA); Wikibooks DE „Python-Programmierung“ | ZIM + PDF | 200 MB | 1 | frei | — |
| Python-Pakete für RAG und Automatisierung | Offline-Wheels für ARM64 + Doku: numpy, sqlite-vec, llama-cpp-python, python-libzim, PyMuPDF, paho-mqtt, pyserial, pymodbus, flask/fastapi | Wheels + HTML | 1–2 GB | 1 | frei | lokaler pip-Index per `pip download --platform manylinux2014_aarch64`; ohne das ist keine Neuinstallation möglich |
| Structured Text / SPS | siehe OSCAT, PLCopen, Beckhoff InfoSys, CODESYS (Abschnitt 1.1) | — | — | 1 | frei | — |
| Linux: Shell, systemd, Netzwerk | „The Debian Administrator's Handbook“ (GPL-2+/CC BY-SA); „The Linux Command Line“ (W. Shotts, CC BY-NC-ND); ArchWiki `archlinux_en_all` (GFDL); Unix & Linux SE, Ask Ubuntu SE (CC BY-SA 4.0); man-pages lokal installiert | PDF + ZIM | 3–6 GB (SE-Sites groß) | 2 | frei | Debian/Raspberry-Pi-OS APT-Teilspiegel (apt-mirror, nur main/arm64) optional 20+ GB |
| Stack Overflow | `stackoverflow.com_en_all` (CC BY-SA 4.0) | ZIM | 75–80 GB | 3 | frei | nur Szenario Voll; für den Alltag reichen die kleineren SE-Sites |

### 1.3 Medizin (Priorität 1)

| Wissensbereich | Konkrete Quelle | Format | Größe | Prio | Beschaffung | Besonderheiten |
|---|---|---|---|---|---|---|
| Medizin, Enzyklopädie (EN) | WikiMed / Medical Wikipedia (Wiki Project Med Foundation, CC BY-SA 4.0) | ZIM `wikipedia_en_medicine_maxi` | 1,7 GB | 1 | frei | mit Bildern, ca. 50.000 Artikel, Medikamente enthalten |
| Medizin, Enzyklopädie (DE) | WikiMed DE, falls im Kiwix-Katalog vorhanden; sonst eigenes ZIM per mwoffliner aus Kategorie „Medizin“ der deutschen Wikipedia (CC BY-SA 4.0) | ZIM | 0,7–1,5 GB | 1 | frei | Verfügbarkeit prüfen; mwoffliner mit `--articleList` |
| Basisversorgung ohne Arzt | Hesperian: „Where There Is No Doctor“ (Aufl. 2021), „Where There Is No Dentist“, „Where Women Have No Doctor“, „A Book for Midwives“; deutsche Ausgabe „Wo es keinen Arzt gibt“ (Hesperian Health Guides, CC BY-NC-SA 4.0) | PDF | 200 MB | 1 | frei | NC-Lizenz; deutsche Ausgabe älterer Stand |
| Erste Hilfe | Wikibooks DE „Erste Hilfe“ (CC BY-SA); ERC-Leitlinien 2021 in deutscher Übersetzung (GRC, frei); DGUV Information 204-006 „Anleitung zur Ersten Hilfe“ (frei); DRK/ASB-Merkblätter (frei abrufbar, urheberrechtlich) | ZIM + PDF | 100 MB | 1 | frei | DRK-Lehrbücher sind kommerziell; Wundversorgung, Frakturen, Reanimation abgedeckt |
| Notfall-, Kriegs- und Katastrophenmedizin | „Emergency War Surgery“ (US Army, Public Domain); TCCC-Guidelines (Public Domain); WHO „Surgical Care at the District Hospital“ (frei); WHO „Pocket Book of Hospital Care for Children“ (frei) | PDF | 300 MB | 1 | frei | englisch; für Situationen ohne Klinik |
| Pharmakologie, Dosierungen | WHO Model Formulary 2008 + WHO Essential Medicines List (WHO, CC BY-NC-SA 3.0 IGO); MSF „Essential Drugs“ und „Clinical Guidelines“ (frei); OpenStax „Pharmacology for Nurses“ (CC BY 4.0); Fachinformationen der eigenen Hausapotheke (PDF vom Hersteller) | PDF + SQLite | 300 MB | 1 | frei | Dosistabellen (Erwachsene/Kinder, kg-bezogen) zusätzlich in eigener SQLite; MSD Manual nur als Privatkopie |
| Anatomie, Physiologie | OpenStax „Anatomy and Physiology 2e“ (CC BY 4.0) | PDF | 150 MB | 2 | frei | Bilder wichtig: nicht unter 150 DPI komprimieren |
| Hygiene, Infektionen, Wasser | WHO „Guidelines for Drinking-water Quality“ (frei); CDC „Household Water Treatment“ (Public Domain); zimgit-medicine | PDF + ZIM | 150 MB | 1 | frei | — |

### 1.4 Survival und Grundversorgung (Priorität 1–2)

| Wissensbereich | Konkrete Quelle | Format | Größe | Prio | Beschaffung | Besonderheiten |
|---|---|---|---|---|---|---|
| Überleben allgemein | US Army FM 21-76 / FM 3-05.70 „Survival“ (Public Domain); Kiwix-Sammlung `zimgit-post-disaster` | PDF + ZIM | 700 MB | 1 | frei | Feuer, Unterschlupf, Orientierung, Signale enthalten |
| Wasser | `zimgit-water`; SODIS-Handbuch (Eawag, frei); CAWST Biosand-Filter-Handbuch (CC BY-NC-SA); WHO Trinkwasser-Leitlinien | ZIM + PDF | 200 MB | 1 | frei | Chemie (Chlor, Dosierung) in eigener Markdown-Karte zusammenfassen |
| Nahrung: Konservierung, Fermentation, Trocknung | USDA „Complete Guide to Home Canning“ (Public Domain); National Center for Home Food Preservation (frei); `zimgit-food-preparation`; BZfE-Merkblätter (frei) | PDF + ZIM | 300 MB | 1 | frei | Einkochzeiten/Drucktabellen zusätzlich in SQLite |
| Pflanzen- und Pilzerkennung | Wikipedia Bildvariante; eigenes mwoffliner-ZIM „Pilze Mitteleuropas“ und „Essbare Wildpflanzen“ mit Bildern; Wikimedia Commons Bildersätze | ZIM | 1–3 GB | 1 | frei | Nur-Text-Wikipedia ist hier unbrauchbar; Bestimmungsbücher (Kosmos) nur kommerziell |
| Praktisches Alltagswissen | wikiHow DE (CC BY-NC-SA 3.0; 22.272 Artikel, eigener zimit-Crawl, da bei Kiwix eingestellt); Appropedia (CC BY-SA 4.0); Low-tech Magazine (CC BY-NC-SA) | ZIM | 3 GB + 2 GB + 0,3 GB | 2 | frei | Appropedia stark bei Appropriate Technology, Wasser, Landwirtschaft |
| Landwirtschaft, Kleintierhaltung | FAO-Publikationen (CC BY-NC-SA 3.0 IGO bzw. CC BY 4.0): „Rural structures in the tropics“, Small-scale poultry/rabbit production, Bodenfruchtbarkeit; Gardening SE (CC BY-SA); Wikibooks | PDF + ZIM | 1 GB | 2 | frei | — |
| Bauen, Reparieren | Home Improvement SE, Woodworking SE, Motor Vehicle Maintenance SE (CC BY-SA 4.0); US Army TM 5-704 „Construction Print Reading“ (Public Domain) | ZIM + PDF | 2 GB | 2 | frei | — |
| Outdoor, Orientierung | Outdoors SE (CC BY-SA 4.0); in FM 21-76 enthalten | ZIM | 150 MB | 2 | frei | — |

### 1.5 Energie und Infrastruktur (Priorität 1–2)

| Wissensbereich | Konkrete Quelle | Format | Größe | Prio | Beschaffung | Besonderheiten |
|---|---|---|---|---|---|---|
| PV-Auslegung | Sandia „Stand-Alone Photovoltaic Systems: A Handbook of Recommended Design Practices“ (Public Domain); NREL-Publikationen (Public Domain); energypedia `energypedia_en_all` (CC BY-SA) | PDF + ZIM | 300 MB | 1 | frei | — |
| Laderegler, Inverter, LiFePO4 | Victron Energy Handbücher + „Wiring Unlimited“ (frei); Zellendatenblätter (EVE, CATL); BMS-Handbücher (JK, JBD, Daly); Battery University (Privatkopie) | PDF + ZIM | 500 MB | 1 | frei (Herst.) | eigene Anlage vollständig dokumentieren: Schaltplan, Parameter, Zellzuordnung → eigenes Material |
| Generatoren, Verbrennungsmotoren | US Army TM 9-8000 „Principles of Automotive Vehicles“ (Public Domain); TM 5-6115-xxx Generatorsätze (Public Domain); Werkstatthandbücher eigener Geräte (Honda GX, Briggs & Stratton) | PDF | 500 MB | 2 | frei / kommerziell | — |
| Pumpen, technische Wasseraufbereitung | Grundfos „Pump Handbook“ (frei); KSB „Kreiselpumpen-Lexikon“ (Privatkopie); Akvopedia (CC BY-SA) | PDF + ZIM | 300 MB | 2 | frei | — |
| Sanitär, Abwasser, Kompostierung | Eawag „Compendium of Sanitation Systems and Technologies“ (frei); „The Humanure Handbook“ (J. Jenkins, PDF frei); NRAES „On-Farm Composting Handbook“ (frei) | PDF | 150 MB | 2 | frei | — |

### 1.6 Kommunikation (Priorität 1–3)

| Wissensbereich | Konkrete Quelle | Format | Größe | Prio | Beschaffung | Besonderheiten |
|---|---|---|---|---|---|---|
| Frequenzen, Bandpläne, Notfunk | BNetzA Frequenzplan (amtlich, frei); IARU-Region-1- und DARC-Bandpläne (frei); eigene Tabelle: PMR446, Freenet, CB, 2 m/70 cm-Relais, Marine, Flugfunk, Wetterfunk, Notfrequenzen | PDF + MD | 50 MB | 1 | frei + eigen | — |
| Amateurfunk Theorie, Prüfung | BNetzA Fragenkataloge Klasse N/E/A (amtlich, frei); DARC Online-Lehrgang (E. Moltrecht, Privatkopie); Amateur Radio SE (CC BY-SA 4.0); Wikibooks | PDF + ZIM | 200 MB | 2 | frei | ARRL Handbook, Rothammel Antennenbuch nur kommerziell |
| Antennenbau | NEETS Modul 10; Wikipedia; eigene Rechenkarten (Dipol, Groundplane, J-Pole, SWR) | PDF + MD | in NEETS | 2 | frei + eigen | — |
| Morse | Wikipedia; eigene Tabelle mit Q-Gruppen und Abkürzungen | MD | < 1 MB | 3 | frei | — |
| Mesh-Netze | Meshtastic-Dokumentation (GPL-3.0) als zimit-ZIM + Firmware-Binaries + Flash-Tool; Reticulum Manual (PDF) + Quellcode (Reticulum-Lizenz); LoRa-Datenblätter Semtech SX127x/SX126x | ZIM + PDF + Binaries | 300 MB | 2 | frei | ohne Firmware und Flasher ist die Doku wertlos |
| Lokale Netze ohne Internet | Debian Handbook (Netzwerkkapitel); eigene HowTos: hostapd, dnsmasq, mDNS, Kiwix-Serve-Freigabe, Meshtastic-Gateway | MD | 10 MB | 2 | frei + eigen | — |

### 1.7 Referenz, Allgemeinwissen, Karten (Priorität 1–3)

| Wissensbereich | Konkrete Quelle | Format | Größe | Prio | Beschaffung | Besonderheiten |
|---|---|---|---|---|---|---|
| Wikipedia DE, Textversion | `wikipedia_de_all_nopic` (Wikimedia, CC BY-SA 4.0) | ZIM | 11 GB | 1 | frei | `mini` 2,8 GB für Minimal; `maxi` mit Bildern 45 GB für Voll |
| Wikipedia EN | `wikipedia_en_all_nopic` / `wikipedia_en_all_maxi` | ZIM | 55 GB / 110 GB | 3 | frei | nur Voll |
| Wikibooks | `wikibooks_de_all_maxi`, `wikibooks_en_all_maxi` | ZIM | 1,3 GB / 4 GB | 1 | frei | DE in Abschnitt 1.1 bereits enthalten |
| Wiktionary, Wikiversity DE | `wiktionary_de_all_maxi`, `wikiversity_de_all_maxi` | ZIM | 1 GB / 0,5 GB | 3 | frei | optional |
| Project Gutenberg | `gutenberg_de_all` (Public Domain), `gutenberg_en_all` | ZIM | 2,5 GB / 65 GB | 3 | frei | die 75.000+ Bücher sind nur in der EN-Volldatei |
| Offline-Karten | Protomaps Planet-Build (OSM, ODbL) → `pmtiles extract` mit Bounding-Box; Basemap-Style, Glyphs, Sprites lokal | PMTiles + JS | DE 4 GB, DACH 6 GB, Europa 30 GB | 1 | frei | benötigt lokalen Viewer (MapLibre GL JS); Höhenlinien/Hillshade optional (+3–10 GB) |
| Routing, POI-Datenbank | Geofabrik PBF Deutschland (ODbL) + GraphHopper- oder Valhalla-Graph; Extrakt Wasserstellen, Apotheken, Krankenhäuser, Tankstellen, Baumärkte als SQLite | PBF + Graph + SQLite | 7 GB | 2 | frei | POI-Tabelle direkt vom LLM abfragbar („nächste Apotheke“) |
| Topografische Karten | OpenTopoMap-Kacheln regional (CC BY-SA) | PMTiles/MBTiles | 2–10 GB | 3 | frei | — |

### 1.8 KI-Modelle (GGUF, Priorität 1–3)

> **Aktualisierung 15.09.2026:** Die Modellnamen in dieser Tabelle (Qwen3, Gemma 3) sind der Stand meines Wissens; das parallel angelegte Archiv `D:\AI-ARK` (01_INVENTAR.md) hat am selben Tag aktuellere Repos gegen die Hugging-Face-API geprüft: Qwen3.5-9B, Gemma 4 E4B/E2B (Bild + Audio), Qwen3.5-0.8B, Granite 4.0 Nano, Qwen3-Embedding-0.6B, bge-reranker-v2-m3, nomic-embed-text-v1.5. Für den Pi 5 mit 16 GB gilt daher: Qwen3.5-9B Q4_K_M als Hauptmodell (~6 GB), Gemma 4 E4B als schnelles multimodales Modell (~4,5 GB), Qwen3-Embedding-0.6B für RAG. `tools/download_models.sh` verwendet diese Liste.


| Zweck | Modell (Lizenz) | Format | Größe | Prio | Beschaffung | Besonderheiten (Pi 5, CPU, 16 GB) |
|---|---|---|---|---|---|---|
| Hauptmodell Chat/RAG | Qwen3-8B Instruct, Q4_K_M (Apache 2.0) | GGUF | 5 GB | 1 | frei | ca. 3 Token/s; gutes Deutsch; Thinking-Modus abschaltbar |
| Schnelles Modell für RAG | Qwen3-4B Q4_K_M (Apache 2.0) oder Gemma 3 4B Q4_K_M (Gemma-Lizenz) | GGUF | 2,5–3 GB | 1 | frei | ca. 6–8 Token/s; Gemma 3 4B versteht Bilder (Typenschild-Foto, Schaltplan-Ausschnitt) |
| Code (C, Python, ST) | Qwen2.5-Coder-7B-Instruct Q4_K_M (Apache 2.0) | GGUF | 4,7 GB | 2 | frei | — |
| Großes Modell | Qwen3-14B Q4_K_M oder Gemma 3 12B Q4_K_M | GGUF | 9 GB | 3 | frei | 1,5–2 Token/s, nur bei Zeit; belegt 10 GB RAM |
| Deutschzentriert | Teuken-7B-instruct (OpenGPT-X, Apache 2.0) Q5_K_M | GGUF | 5,5 GB | 3 | frei | Alternative mit europäischem Trainingsfokus |
| Embedding | bge-m3 Q8_0 oder f16 (MIT) | GGUF | 0,6–1,2 GB | 1 | frei | mehrsprachig, 8k Kontext; Embeddings vorab am PC erzeugen |
| Reranker | bge-reranker-v2-m3 (MIT) | GGUF | 0,6 GB | 2 | frei | verbessert RAG-Treffer spürbar |
| Sprache → Text | whisper.cpp ggml-small / ggml-medium (MIT) | GGML | 0,5 / 1,5 GB | 2 | frei | Diktat mit öligen Händen an der Maschine |
| Text → Sprache | Piper de_DE-thorsten (MIT) | ONNX | 0,1 GB | 3 | frei | — |
| OCR | tesseract deu + eng traineddata (Apache 2.0) | traineddata | 50 MB | 2 | frei | eigene Scans durchsuchbar machen (ocrmypdf) |

### 1.9 Militärische Grundlagen – defensiv (Priorität 1–3)

Abgrenzung: Nur Verwundetenversorgung, Sicherung, ABC-Abwehr, Feldüberleben, Notwehrrecht, Melde- und Führungswesen. Keine Waffen- oder Schießausbildung, keine Bauanleitungen, keine Verschlusssachen. US-Publikationen nur in Ausgaben mit dem Vermerk „Approved for public release; distribution is unlimited“ verwenden. Bundeswehr-Vorschriften (ZDv, Zentralrichtlinien) sind nicht öffentlich und gehen nur als eigene Zusammenfassung ein.

| Wissensbereich | Konkrete Quelle | Format | Größe | Prio | Beschaffung | Besonderheiten |
|---|---|---|---|---|---|---|
| Taktische Verwundetenversorgung (TCCC) | CoTCCC „TCCC Guidelines“ aktuelle Ausgabe + „Quick Reference Guide“ (US DoD/Deployed Medicine, Public Domain); C-TECC „TECC Guidelines“ (zivile Ableitung, frei); „Stop the Bleed“ (American College of Surgeons, frei) | PDF | 30 MB | 1 | frei | MARCH-Algorithmus, Tourniquet, Wundtamponade, Thoraxentlastung, Hypothermie; TECC ist die zivile Fassung für Lagen ohne Gefecht |
| Einsatzersthelfer A/B | Bundeswehr-Lehrgangsunterlagen nicht öffentlich → eigene Zusammenfassung aus Lehrgang/Kurs mit Quellenangabe; ergänzend „Wehrmedizinische Monatsschrift“ (frei online, Fachartikel) | MD + eigenes ZIM | 20 MB | 1 | eigen / kommerziell (Kurs) | Inhalte decken sich weitgehend mit TCCC/TECC; legaler Weg: zivile Kurse „Taktische Notfallmedizin“ der Hilfsorganisationen |
| Erste Hilfe militärisch (US) | FM 21-11 „First Aid for Soldiers“ (1988) und Nachfolger FM 4-25.11 / TC 4-02.1 „First Aid“ (US Army, Public Domain) | PDF | 40 MB | 1 | frei | neue Ausgabe als Standard, alte für improvisierte Verfahren (Schienen, Transportgriffe) |
| Verlängerte Versorgung ohne Klinik | SOMA „Prolonged Field Care“-Leitlinien (frei); „Emergency War Surgery“ und Hesperian (Abschnitt 1.3) | PDF | 100 MB | 1 | frei | für Lagen, in denen Abtransport tage- oder wochenlang unmöglich ist |
| Improvisation Sanität | eigene Markdown-Karten: Tourniquet aus Gürtel/Stoff + Knebel, Schienen aus Holz/Metall, Wundreinigung ohne Pharmaka (abgekochtes Wasser, Salzlösung, Druckspülung, Honig), Transportgriffe; Quellen FM 21-11, Hesperian, TCCC | MD | 5 MB | 1 | eigen | Bilder aus Public-Domain-Quellen übernehmen |
| Wach- und Sicherungsdienst | FM 22-6 „Guard Duty“ (US Army, Public Domain); FM 21-75 „Combat Skills of the Soldier“ (Beobachtung, Deckung, Meldungen; Public Domain); eigene Zusammenfassung des Reibert-Kapitels Wachdienst | PDF + MD | 30 MB | 2 | frei + eigen | Postenablösung, Sichtmeldung, Alarmierung, Streifengänge |
| Perimeter- und Objektschutz | FM 3-19.30 / ATP 3-39.32 „Physical Security“ (Public Domain); FEMA 426/427 „Reference Manual to Mitigate Potential Terrorist Attacks Against Buildings“ (Public Domain) | PDF | 60 MB | 2 | frei | Sichtfelder, Zugangskontrolle, Beleuchtung ohne Netz, Alarmketten ohne Elektronik |
| IED-/Sprengfallen-Erkennung | DHS/FEMA „IED Awareness“-Material (frei); UNMAS „IED Lexicon“ (frei); FM 3-34.119 „IED Defeat“ nur Fassung „approved for public release“; FM 5-31 „Boobytraps“ (1965, Public Domain) | PDF | 40 MB | 2–3 | frei | nur Erkennen, Abstand halten, Melden; FM 5-31 enthält Bauprinzipien → nur Erkennungskapitel exzerpieren, Rest nicht in den RAG-Index aufnehmen |
| Städtische Verteidigung | FM 3-06 „Urban Operations“ (2006) / ATP 3-06 (2017); FM 90-10 „MOUT“ (1979) und FM 90-10-1 (1993) (US Army, Public Domain) | PDF | 60 MB | 2 | frei | Doktrindokumente; für Zivilisten relevant: Gebäudesicherung, Bewegung, Deckung; Angriffskapitel weglassen |
| ABC-Abwehr Grundlagen | FM 3-11 „CBRN Operations“, FM 3-11.4 „NBC Protection“, FM 3-11.5 „CBRN Decontamination“ (Public Domain); BBK „Ratgeber für Notfallvorsorge“, BBK/BfS-Merkblätter Strahlenunfall (amtlich, frei); SSK-Empfehlungen (frei) | PDF | 100 MB | 2 | frei | improvisierter Atemschutz, Abdichten von Räumen, Personen-/Geräte-/Flächendekon ohne Spezialgerät |
| Strahlenschutz, improvisiertes Dosimeter | C. Kearny „Nuclear War Survival Skills“ (Oak Ridge National Laboratory, Public Domain): Kearny Fallout Meter, Abschirmung, Schutzraumlüftung, Evakuierungsentscheidung | PDF | 30 MB | 2 | frei | KFM ist ein Messgerät aus Alltagsmaterial, ideales Mechatroniker-Projekt |
| Biologische Gefahren, Quarantäne, Umgang mit Toten | RKI-Rahmenkonzepte Epidemie/Pandemie (frei); WHO/PAHO „Management of Dead Bodies after Disasters“ (frei); Sphere Handbook 2018, Kapitel WASH/Gesundheit (CC BY-SA) | PDF | 50 MB | 2 | frei | — |
| Überleben im Feld | FM 21-76 (1992) / FM 3-05.70 (2002) / ATP 3-50.21 (2018) „Survival“ (Public Domain), siehe Abschnitt 1.4 | PDF | 30 MB | 2 | frei | Navigation, Wasser, Nahrung, Feuer, Unterschlupf, Signalgebung |
| Tarnung, Beobachtung | FM 21-75 (s. o.); FM 20-3 „Camouflage, Concealment, and Decoys“ (Public Domain) | PDF | 30 MB | 2 | frei | Sichtschutz, Geräusch, Wärmesignatur |
| Orientierung ohne GPS | FM 3-25.26 / TC 3-25.26 „Map Reading and Land Navigation“ (Public Domain); Wikipedia Astronavigation; eigene Karte Sonnenstand/Polarstern/Uhrmethode | PDF + MD | 40 MB | 2 | frei | Ausdruckfähigkeit der PMTiles-Karten (Druckerbetrieb an Solar) vorsehen |
| Marschvorbereitung, Fußpflege | FM 21-18 „Foot Marches“ (Public Domain); FM 21-20 „Physical Fitness Training“ (Public Domain) | PDF | 30 MB | 2 | frei | Gepäckorganisation, Belastungsgrenzen |
| Notwehr, Rechtsgrundlagen | StGB §§ 32–35, BGB §§ 227–231, WaffG-Auszüge über gesetze-im-internet.de (amtlich, frei); eigene Zusammenfassung Verhältnismäßigkeit | HTML + MD | 5 MB | 3 | frei + eigen | Rechtsstand mit Datum vermerken |
| Selbstverteidigung, Befreiungsgriffe | eigene Zusammenfassung aus besuchten Kursen; kommerzielle Lehrbücher als gekauftes E-Book | MD + PDF | 50 MB | 3 | eigen / kommerziell | Bewegungsabläufe sind als Text schwach: kurze eigene Übungsclips (< 500 MB) erwägen |
| Funkdisziplin, Meldewesen | FM 24-18 „Tactical Single-Channel Radio Communications“ (Buchstabiertafel, Prowords, Frequenzwechsel); FM 6-99 „Report and Message Formats“ (SALUTE, SITREP, MEDEVAC 9-Line) (Public Domain); eigene deutsche Schemata Lage-, Feind-, Verwundetenmeldung | PDF + MD | 30 MB | 3 | frei + eigen | Einseitige Funkerkarten laminieren |
| Gruppenführung, Auftragstaktik | ADP 6-0 „Mission Command“, ADP 6-22 „Army Leadership“ (Public Domain); Reibert-Zusammenfassung (Führungsgrundsätze, Befehlsschema, Entscheidung unter Stress) | PDF + MD | 30 MB | 3 | frei + eigen | — |
| Reibert | „Der Reibert – Das Handbuch für den deutschen Soldaten“ (Mittler Verlag, ca. 30–40 €, urheberrechtlich geschützt) | eigenes ZIM/MD (Zusammenfassung) | 5 MB | 2 | kommerziell | nur eigene Zusammenfassung mit Quellenangabe; gedrucktes Exemplar in die Box legen |
| Survival-Kampfbuch | kommerziell, laut Vorgabe | eigenes ZIM/MD (Zusammenfassung) | 5 MB | 3 | kommerziell | bibliografische Daten vor Kauf prüfen |

Größe gesamt: Minimal ca. 50 MB (TCCC, FM 21-11, FM 21-76), Standard ca. 200 MB, Voll ca. 500 MB.

### 1.10 Zivilisationsneustart und Grundlagentechnologie (Priorität 1–3)

Taxonomie: Die Kapitelstruktur von Dartnell (Schonfrist/Salvage, Landwirtschaft, Nahrung & Kleidung, Stoffe & Materialien, Medizin, Energie, Transport, Kommunikation, Chemie, Zeit & Ort, wissenschaftliche Methode) ist das Ordnungsschema für Verzeichnisse, Tags und die SQLite-Kategorie. Querverweisregel: Jeder Eintrag verlinkt per `xref` auf die zugehörigen Einträge in Mechatronik (Wie reparieren?), Medizin (Wie behandeln?) und Survival (Wie kurzfristig überleben?). Ausschluss: keine Waffen-, Sprengstoff-, Kerntechnik-, Drogen- oder ABC-Offensivinhalte; Schwarzpulver nur als Geschichtsabsatz.

| Wissensbereich | Konkrete Quelle | Format | Größe | Prio | Beschaffung | Besonderheiten |
|---|---|---|---|---|---|---|
| Kernreferenz | L. Dartnell „The Knowledge“ / „Das Handbuch für den Neustart der Welt“ (Hanser, ca. 15–20 €, urheberrechtlich); Begleitseite the-knowledge.org (frei) | PDF (gekauftes E-Book, 120 DPI) + MD-Kapitelextrakt | 20 MB | 1 | kommerziell | Kapitelstruktur = Taxonomie des Moduls; Extrakt in eigenen Worten |
| Visuelle Referenz | „THE BOOK: The Ultimate Guide to Rebuilding a Civilization“ (Hungry Minds 2024, 410 S., ca. 110 €) | PDF (Eigen-Scan oder E-Book) | 0,3–1 GB | 2 | kommerziell | Eigen-Scan des gekauften Exemplars ist Privatkopie; Illustrationen bei 150 DPI, nicht darunter |
| Weitere kommerzielle Titel | „Survive the Collapse“ (2025); „The Ascent Begins: Sovereignty in the Age of Collapse“ (2025) | PDF | 50 MB | 3 | kommerziell | bibliografische Angaben konnte ich nicht verifizieren, vor Kauf prüfen |
| Technologie-Abhängigkeitsbäume | eigenes Modul (Schema und Startliste unten) | SQLite + MD | 10–50 MB | 1 | eigen | wichtigstes Eigenartefakt; zehn Kerntechnologien zuerst |
| Metallurgie: Holzkohle, Rennofen, Tiegelstahl, Buntmetall, Drahtziehen, Wärmebehandlung, Schmieden, Gießen | D. Gingery „Build Your Own Metal Working Shop from Scrap“ Bd. 1–7 (kommerziell, ca. 60 €); „Farm Blacksmithing“ (J. Drew 1901, Public Domain); „Hawkins Electrical Guide“ Bd. 1–10 (1917, Public Domain); FAO „Simple Technologies for Charcoal Making“ (Forestry Paper 41, frei); „Machinery's Handbook“ Ausgaben bis 1928 (Public Domain); Wikipedia | PDF + ZIM | 500 MB | 1 | frei / kommerziell | Gingery: Holzkohle-Schmelzofen, Aluminiumguss, Drehbank aus Schrott; Hawkins: Generator- und Motorbau der Frühzeit |
| Chemie: Schwefel-, Salpeter-, Salzsäure, Soda, Natronlauge, Seife, Glas, Keramik, Kalk, Zement | „Henley's Twentieth Century Book of Formulas, Processes and Trade Secrets“ (1914, Public Domain); A. Rogers „Manual of Industrial Chemistry“ (1920er, Public Domain); Thorpe „Dictionary of Applied Chemistry“ (Public Domain); Practical Action „Small-scale Lime Burning“ (frei); Wikipedia (Bleikammerverfahren, Solvay-Verfahren, Glasherstellung) | PDF + ZIM | 1 GB | 1 | frei | historische Verfahren; eigene Sicherheitskarten (Säuren, Laugen, CO, Quecksilber vermeiden) |
| Textil, Leder | L. Hooper „Hand-Loom Weaving“ (1910, Public Domain); USDA Farmers' Bulletins zu Gerben und Wolle (Public Domain); Wikipedia | PDF + ZIM | 100 MB | 2 | frei | — |
| Energie: Wasserrad, Windmühle, Dampf, Holzgas, Biogas | FEMA „Construction of a Simplified Wood Gas Generator for Fueling Internal Combustion Engines“ (1989, Public Domain); Practical Action „Micro-Hydro Power“ (frei); VITA „Village Technology Handbook“ (frei); L. Sasse „Biogas Plants“ (GTZ, frei); Hawkins Bd. 1–3; Wikipedia | PDF + ZIM | 300 MB | 1 | frei | Holzgas-Generatorbetrieb verknüpft mit Abschnitt 1.5 |
| Landwirtschaft: Boden, Saatgut, Fruchtfolge, Zugtiere, Bewässerung | F. H. King „Farmers of Forty Centuries“ (1911, Public Domain); USDA Farmers' Bulletins, Auswahl (Public Domain); FAO „Draught Animal Power Manual“ (frei); Wikipedia (Leguminosen, Saatgutgewinnung, Kompost) | PDF + ZIM | 500 MB | 1 | frei | „Seed to Seed“ nur kommerziell |
| Medizinherstellung, Chirurgie, Anästhesie | M. King „Primary Surgery“ Bd. 1+2 (frei online); WHO „Anaesthesia at the District Hospital“ (frei, Draw-over-Verfahren Äther/Ketamin); „King's American Dispensatory“ (1898, Public Domain); WHO-Monographien Heilpflanzen (frei); Wikipedia (Destillation, Sterilisation, Penicillin-Geschichte) | PDF + ZIM | 400 MB | 1 | frei | Penicillin-Eigenkultur nur mit Warnkarte: minimale Ausbeute, Reinheit nicht prüfbar, Toxinrisiko fremder Schimmel; Äther: Explosionsgefahr, Peroxidbildung |
| Kommunikation & Information: Telegraf, Detektorempfänger, Röhre, Papier, Druck | ARRL „Radio Amateur's Handbook“ Ausgaben 1926–1928 (Public Domain); Practical Action „Papermaking“ (frei); Wikipedia (Morsetelegraf, Erdrückleitung, Buchdruck, Buchbinden); eigene Karten | PDF + ZIM + MD | 200 MB | 2 | frei | — |
| Soziale Organisation, öffentliche Gesundheit | Sphere Handbook 2018 (CC BY-SA); UNHCR Emergency Handbook (frei); Wikipedia (Genossenschaft, Allmende, Ostrom-Prinzipien, Warengeld); eigene Karten Konfliktlösung, Ressourcenverteilung, Tauschsystem | PDF + MD | 100 MB | 2 | frei + eigen | E. Ostrom „Governing the Commons“ nur kommerziell |
| Bildung: Lesen, Rechnen, Technik lehren | UNESCO Alphabetisierungsmaterial (frei); Wikibooks DE Schulstoff Mathematik/Physik; OpenStax Prealgebra bis College Physics (CC BY 4.0) | ZIM + PDF | 500 MB | 2 | frei | — |
| Historische Fallstudien | Wikipedia (Spätantike, Karolingische Renaissance, Meiji-Restauration, Industrialisierung); eigene Zusammenfassungen; kommerzielle Titel s. o. | ZIM + MD | 20 MB | 3 | frei | Muster erkennen, keine Handlungsanleitung |
| Sammelbestand Appropriate Technology | CD3WD-Sammlung (A. Weir, ca. 13 GB, gemischte freie Lizenzen); Appropedia (Abschnitt 1.4) | HTML/PDF | 13 GB | 3 | frei | nur Voll; Lizenz je Dokument prüfen |

Größe gesamt: Minimal ca. 50 MB (Dartnell + Bäume), Standard ca. 1 GB, Voll ca. 3 GB (plus 13 GB CD3WD optional).

**Schema Technologie-Abhängigkeitsbäume (SQLite)**

```sql
CREATE TABLE tech(
  id TEXT PRIMARY KEY, name TEXT, category TEXT,          -- category = Dartnell-Kapitel
  description_md TEXT,
  min_viable_scale TEXT,   -- 'Haushalt' | 'Dorf (50–500 Pers.)' | 'Region (>5000)' | 'nicht rekonstruierbar (nur Salvage)'
  era_equivalent TEXT,     -- z. B. '1880' = Stand der Technik, ab dem es beherrschbar war
  salvage_lifetime TEXT,   -- wie lange geborgene Exemplare nutzbar bleiben
  xref TEXT                -- Links: mech:motor-rewinding, med:..., surv:...
);
CREATE TABLE tech_input(tech_id TEXT, input_id TEXT, role TEXT, quantity_note TEXT, substitute TEXT,
  PRIMARY KEY(tech_id, input_id));
CREATE TABLE process(id TEXT PRIMARY KEY, name TEXT, inputs TEXT, outputs TEXT, tools TEXT,
  temperature_c TEXT, hazards TEXT, source TEXT);
CREATE VIRTUAL TABLE tech_fts USING fts5(name, description_md, content='tech', content_rowid='rowid');
```

**Startliste: zehn Kerntechnologien und minimale Produktionsgröße**

| Produkt | Direkte Eingänge | Vorgelagerte Kette | Min. Größe | Bemerkung |
|---|---|---|---|---|
| Elektromotor | Kupferdraht, Blechpaket, Welle, Lager, Isolation | Kupferschrott → Tiegelschmelze (1085 °C, Holzkohle) → Gießen → Drahtziehen; Weicheisenblech → Glühen; Isolation aus Schellack, Baumwolle, geöltem Papier | Dorf | Permanentmagnete nur Salvage → fremderregte Maschine bauen |
| Generator | wie Motor + Antriebsmaschine | Wasserrad, Windrad, Holzgasmotor, Dampfmaschine | Dorf | Gleichstrom mit Kommutator ist einfacher zu regeln als Drehstrom |
| Transformator | geglühtes Eisenblech, Draht, Isolation, Öl | wie oben | Dorf | Blechschnitt von Hand, Verluste akzeptieren |
| Kupferdraht | Kupferbarren, Ziehstein | Ziehstein aus gehärtetem Stahl mit konischer Bohrung; Zugbank | Dorf | Engpass für alle Elektrotechnik; Salvage-Priorität Nr. 1 |
| Kugellager | Kugeln, Laufringe, Käfig | Kohlenstoffstahl → Härten/Anlassen → Präzisionsschleifen | Region | Dorf-Alternative: Gleitlager aus Bronze oder Pockholz |
| Blei-Akku | Bleiplatten, Schwefelsäure, Gefäß | Bleischmelze (327 °C); Säure über Bleikammer- oder Kontaktverfahren; Gefäß Glas/Keramik | Dorf | Bleivergiftung, Säureunfälle → Sicherheitskarte |
| Funksender/-empfänger | Röhre oder Transistor, Kondensator, Spule, Antenne | Röhre: Glasbläserei, Vakuum, Wolfram/Nickel; Transistor: nicht rekonstruierbar | Dorf (Röhre, Funkenstrecke) / Salvage (Halbleiter) | Detektorempfänger mit Bleiglanz ist Haushaltsniveau |
| Schalter/Relais | Kupferkontakte, Feder, Isolator, Spule | Kupfer, Federstahl, Holz/Keramik | Haushalt | Basis der SPS-Alternative |
| SPS-Äquivalent | Relaislogik, Nockensteuerung, pneumatische Logik | Schalter, Relais, Pneumatik | Dorf | Halbleiterfertigung nicht rekonstruierbar → SPS-Ersatzteilvorrat sichern, Relaislogik dokumentieren |
| Sensoren | Thermoelement (zwei ungleiche Drähte), Bimetall, Bourdon-Rohr, Schwimmer, Manometer | Draht, Blech, Glas | Haushalt bis Dorf | Pt100 und Halbleitersensoren nur Salvage |

### 1.11 Eigene Fahrzeuge (Priorität 1)

Fahrzeuge: **Land Rover Defender 110 TD5** (1998–2006), **Rover Mini Cooper 1.3i MPi „British Open Classic“** (1999), **Vespa V50 N, V5A1T** (1963). Je Fahrzeug: Werkstatthandbuch mit Schaltplänen, Original-Ersatzteilkatalog mit Explosionszeichnungen und Teilenummern, Reparaturanleitung, Foren-Praxiswissen, eigene Fahrzeugakte. Die Fahrzeugakten liegen als SQLite (`own/fahrzeuge/fahrzeuge.db`, Quelle `fahrzeuge.sql`) und generiertes Markdown vor: Kenndaten, Füllmengen, Drehmomente, Einstellwerte, Stückliste der Verschleißteile mit OEM-Nummern, bekannte Schwachstellen, Wartungsplan, Logbuch. Alle aus dem Gedächtnis eingetragenen Werte sind mit `verified = 0` markiert und gegen das Handbuch zu prüfen.

| Wissensbereich | Konkrete Quelle | Format | Größe | Prio | Beschaffung | Besonderheiten |
|---|---|---|---|---|---|---|
| Defender TD5: Werkstatthandbuch, Schaltpläne | „Defender Workshop Manual“ MJ 1999–2006 (LRL0410/LRL0097) + „Electrical Library“ (Land Rover; Nachdruck Brooklands Books) | PDF | 300 MB | 1 | kommerziell (40–60 €) | Original-PDF urheberrechtlich; kursierende Kopien nur als Privatkopie |
| Defender: Ersatzteilkatalog mit Explosionszeichnungen | „Defender Parts Catalogue 1987–2006“ STC9021CC (Land Rover/Brooklands); Online: lrcat.com, Britpart, Bearmach, Paddock Spares, Famous Four, Rimmer Bros | PDF + gesicherte Webseiten | 500 MB | 1 | kommerziell + frei einsehbar (Privatkopie) | Online-Kataloge zeigen Explosionszeichnung je Baugruppe mit Nummern; per Fahrgestellnummer filtern, als PDF drucken |
| Defender: Diagnose | Nanocom Evolution Handbuch (frei); Haynes 3017 (kommerziell) | PDF | 50 MB | 1 | frei (Herst.) / kommerziell | TD5 braucht LR-spezifisches Diagnosegerät; Injektor-Codes |
| Mini MPi: Werkstatthandbuch, Schaltpläne | „Rover Mini Workshop Manual 1992–2000“ inkl. MPi-Nachtrag (RCL 0193 / AKM 7169, Brooklands-Nachdruck); Haynes 0646 | PDF | 200 MB | 1 | kommerziell | MPi-Schaltplan 1997–2000 separat sichern |
| Mini: Ersatzteilkatalog mit Explosionszeichnungen | Rover „Mini Parts Catalogue 1990–2000“ (BMIHT/Nachdruck); Online: minispares.com (jede Baugruppe mit Zeichnung und Nummern), Somerford Mini, Mini Sport | PDF + gesicherte Webseiten | 400 MB | 1 | kommerziell + frei einsehbar (Privatkopie) | SPi/MPi-Unterschiede beachten |
| Vespa V50 N 1963: Werkstatthandbuch, Bedienungsanleitung | Piaggio „Vespa 50 – Anleitung für die Werkstatt“ (1960er), Bedienungsanleitung 1963; Bucheli Reparaturanleitung Smallframe; Vespa Technica | PDF | 100 MB | 1 | Scans frei zugänglich (scooterhelp.com, Privatkopie) / kommerziell | Piaggio-Urheberrecht formal fortbestehend |
| Vespa: Ersatzteilkatalog mit Explosionszeichnungen | Piaggio „Catalogo parti di ricambio Vespa 50 V5A1T“ (scooterhelp.com); Online: SIP Scootershop und Scooter Center, Explosionszeichnung je Baugruppe mit aktuellen Nummern | PDF + gesicherte Webseiten | 300 MB | 1 | frei einsehbar (Privatkopie) | Modell V50 N / V5A1T auswählen; Bauzeit-Varianten der ersten Serie |
| Foren-Praxiswissen | landyzone.co.uk, lr4x4.com, defender-forum.de; theminiforum.co.uk, mini-forum.de, minimania.com; germanscooterforum.de (GSF-Wiki), vespaforum.de | Markdown-Exzerpte | 50 MB | 2 | frei (Privatkopie) | gezielt Threads zu bekannten Schwachstellen sichern, nicht die Foren spiegeln |
| Eigene Fahrzeugakten | `own/fahrzeuge/fahrzeuge.db` + `Fahrzeugakte_*.md`; Fotos eigener Umbauten, Typenschilder, Rechnungen | SQLite + MD + JPG | 200 MB | 1 | eigen | Fahrgestell-/Motornummern eintragen, `verified` nach Prüfung setzen |
| Allgemein Kfz | Motor Vehicle Maintenance SE, TM 9-8000, iFixit (bereits enthalten) | ZIM + PDF | – | 2 | frei | — |

Größe gesamt: ca. 2 GB. Rechtlich: Werkstatthandbücher und Kataloge sind urheberrechtlich geschützt (Jaguar Land Rover, Rover-Nachfolge über BMIHT, Piaggio). Brooklands Books und Haynes sind lizenzierte Nachdrucke, deren Kauf der saubere Weg ist. Frei einsehbare Online-Kataloge der Teilehändler dürfen für den Eigengebrauch gespeichert werden, nicht weitergegeben.

---

## 2. Gesamtgrößen für drei Szenarien

### Minimal – Notfallkern, ca. 5 GB (passt auf USB-Stick oder microSD, auch mit Kiwix am Smartphone lesbar)

| Inhalt | Größe |
|---|---|
| WikiMed DE (oder EN 1,7 GB) | 0,8 GB |
| Hesperian, 4 Bücher | 0,2 GB |
| Erste Hilfe, ERC, Notfallmedizin, WHO Formulary | 0,3 GB |
| Lessons in Electric Circuits + NEETS-Auswahl + TI/ADI Analog-Handbücher | 0,2 GB |
| Eigenes Tabellenbuch (SQLite + Markdown), Diagnosebäume, Notfunk-Tabelle | 0,1 GB |
| FM 21-76, USDA Canning, zimgit-water | 0,2 GB |
| DevDocs C/Python/Bash | 0,3 GB |
| Wikipedia DE `mini` | 2,8 GB |
| PMTiles Heimatregion (ein Bundesland) | 0,5 GB |
| Militär: TCCC, FM 21-11, FM 21-76, Kearny | 0,05 GB |
| Neustart: Dartnell-PDF + Abhängigkeitsbäume | 0,05 GB |
| Fahrzeuge: Fahrzeugakten + Werkstatthandbuch-Kernkapitel | 0,1 GB |
| **Summe** | **5,5 GB** |

Kein LLM enthalten. Mit Qwen3-4B und bge-m3 kommen 3,1 GB dazu (ca. 8,5 GB).

### Standard – Alltagsbox, ca. 30 GB

| Inhalt | Größe |
|---|---|
| Wikipedia DE `nopic` | 11 GB |
| WikiMed EN + DE | 2,5 GB |
| Wikibooks DE | 1,3 GB |
| Electronics SE, Arduino SE, Raspberry Pi SE, Engineering SE | 3 GB |
| iFixit DE | 2 GB |
| DevDocs, ArchWiki, Elektronik-Kompendium (zimit) | 1,2 GB |
| PDF-Bibliothek: Handbücher, Datenblätter, Kataloge, Medizin, Survival, Energie, SPS (ohne Beckhoff InfoSys) | 4 GB |
| Eigenes Material | 0,2 GB |
| PMTiles Deutschland | 4 GB |
| Militär: alle FMs Prio 1–2, ABC-Abwehr, Reibert-Zusammenfassung | 0,2 GB |
| Neustart: Dartnell, THE BOOK, PD-Klassiker, Materialhandbuch-ZIM | 1 GB |
| Fahrzeuge: Handbücher und Kataloge der drei eigenen Fahrzeuge | 2 GB |
| **Zwischensumme Daten** | **30,4 GB** |
| Modelle: Qwen3-8B, Qwen3-4B, bge-m3, whisper small | 8,6 GB |
| **Summe** | **ca. 39 GB** |

Wer bei 30 GB bleiben will, nimmt nur Qwen3-4B und bge-m3 (3,1 GB) und lässt iFixit und Gutenberg weg.

### Voll – 1 TB NVMe, realistisch 300–450 GB

| Inhalt | Größe |
|---|---|
| Wikipedia DE `maxi` (mit Bildern) | 45 GB |
| Wikipedia EN `nopic` | 55 GB |
| WikiMed EN + DE | 2,5 GB |
| Wikibooks DE + EN, Wiktionary DE | 6,5 GB |
| wikiHow DE, Appropedia, Low-tech Magazine, energypedia | 5,6 GB |
| Stack-Exchange-Paket: Electronics, Arduino, RPi, Engineering, Unix, Ask Ubuntu, Super User, Physics, DIY, Mechanics, Gardening, Outdoors, Ham, Woodworking | 20 GB |
| iFixit DE + EN | 5,5 GB |
| Gutenberg DE + EN | 68 GB |
| zimgit-Sammlungen | 1 GB |
| PDF-Bibliothek erweitert inkl. Beckhoff InfoSys, alle Datenblätter, Kataloge | 15 GB |
| Karten: PMTiles Europa, PBF + Routing-Graph DE, OpenTopoMap DACH | 42 GB |
| Software-Spiegel: APT-Teilspiegel arm64, pip-Wheels, Firmware, Quellcode Kiwix/llama.cpp/MapLibre, OS-Images | 25 GB |
| Modelle: Qwen3-8B, Qwen3-14B, Qwen2.5-Coder-7B, Gemma 3 12B, Qwen3-4B, bge-m3, Reranker, whisper medium, Piper | 33 GB |
| Eigenes Material inkl. Scans | 0,5 GB |
| Militär: alle FMs inkl. FM 5-31 (Erkennungskapitel), eigene Clips | 0,5 GB |
| Neustart: alle Module, Chemie erweitert, Fallstudien | 3 GB |
| Fahrzeuge: Handbücher, Kataloge, Explosionszeichnungen, Fahrzeugakten | 2 GB |
| **Summe** | **ca. 330 GB** |

Optional: Stack Overflow (+80 GB), Wikipedia EN `maxi` statt `nopic` (+55 GB), CD3WD (+13 GB) → ca. 480 GB. Die restlichen 500 GB der NVMe bleiben frei für eigene Scans, Fotos von Typenschildern und Backups der SD-Karten.

---

## 3. Redundanz

Grundregel 3-2-1: drei Kopien, zwei Medientypen, eine räumlich getrennt. Dazu kommt Software-Redundanz, denn ohne lauffähiges System ist die Datenkopie wertlos.

| Ebene | Medium | Inhalt | Dateisystem | Aktualisierung |
|---|---|---|---|---|
| 1 Betrieb | NVMe 1 TB im Pi 5 | Voll | ext4 | laufend |
| 2 Spiegel | USB-SSD 1–2 TB | 1:1-Kopie von `/srv/box` per `rsync -a --checksum` | exFAT (auf Windows/Android lesbar) | nach jeder Änderung, mindestens monatlich |
| 3 Extern | zweite USB-SSD an anderem Ort, in Metallbox oder antistatischem Faraday-Beutel | Voll oder Standard | exFAT | vierteljährlich tauschen (Rotation zweier Platten) |
| 4 Taschenkopie | microSD 64 GB oder USB-Stick | Minimal + Kiwix-APK für Android | exFAT | jährlich |
| 5 System | zwei identische microSD-Karten mit fertigem OS-Image (Raspberry Pi OS, kiwix-serve, llama.cpp, MapLibre, Skripte, `library.xml`) | bootfähiges Image | ext4 | nach jeder Systemänderung neu ziehen (`dd` oder rpi-clone) |

Integrität:
- SHA-256-Manifest über alle Dateien (`sha256sum -c`), Prüflauf halbjährlich auf allen Kopien.
- ZIM-Dateien zusätzlich mit `zimcheck` prüfen (eingebaute Prüfsummen).
- Für PDF- und SQLite-Bestände par2-Paritätsdateien mit 10 % Redundanz erzeugen, damit Bitfehler reparierbar bleiben.
- SSDs unbestromt verlieren Daten nach 1–2 Jahren bei Wärme. Externe Platten jährlich mindestens einmal anstecken und Prüfsumme laufen lassen.
- Hardware: zweites Pi-5-Board oder mindestens Netzteil, NVMe-Adapter und SD-Karten doppelt vorhalten.
- Papier: die 50–100 wichtigsten Seiten (Sicherheitsregeln, Erste-Hilfe-Ablauf, Dosierungstabelle, Wasserdesinfektion, Formelkern, Notfunkfrequenzen) ausgedruckt in der Box. Das ist der einzige Bestand, der ohne Strom funktioniert.

---

## 4. Rechtliche Grenzen (keine Rechtsberatung)

- **DIN/VDE/IEC-Normen** sind urheberrechtlich geschützt (DIN Media, VDE Verlag). Kopieren, Scannen oder Weitergeben ist unzulässig. Zulässig: gekaufte Norm-PDFs (Einzelplatzlizenz, Wasserzeichen) auf der eigenen Box ablegen, nicht weitergeben. Zulässig: eigene Zusammenfassung der Anforderungen in eigenen Worten mit Quellenangabe („nach DIN VDE 0100-410:2018, Abschnitt 411“). Nicht zulässig: Tabellen 1:1 übernehmen, auch nicht „abgetippt“. Fakten selbst (physikalische Werte, Formeln) sind frei; berechnete Tabellen aus öffentlichen Formeln (Toleranzfelder, Gewindemaße, Pt100-Kennlinie) darf man selbst erzeugen.
- **Harmonisierte EN-Normen**: Der EuGH hat 2024 (C-588/21) entschieden, dass harmonisierte Normen zugänglich sein müssen. Praktisch ist der freie Zugang weiterhin eingeschränkt; kein Freifahrtschein für Kopien.
- **Kommerzielle Tabellenbücher** (Europa, Westermann, Roloff/Matek, Dubbel): nur als gekauftes E-Book. Kopierschutz darf nach § 95a UrhG nicht umgangen werden, auch nicht für Privatkopien. Springer-E-Books sind meist DRM-frei und damit unproblematisch ablegbar.
- **Hersteller-Dokumente** (Datenblätter, Handbücher, Kataloge) sind urheberrechtlich geschützt, der Download ist kostenlos und die Eigennutzung erlaubt. Keine Weitergabe der Sammlung.
- **Website-Kopien per zimit** (Elektronik-Kompendium, mikrocontroller.net, MSD Manual, Battery University, DARC-Lehrgang) fallen unter Privatkopie (§ 53 UrhG): nur eigener Gebrauch, keine Weitergabe, keine Bereitstellung im Netz außerhalb des Haushalts.
- **NC-Lizenzen** (iFixit, Hesperian, wikiHow, Low-tech Magazine, WHO, FAO älter) verbieten kommerzielle Nutzung. Weitergabe an Nachbarn ist erlaubt, Verkauf der Box mit Inhalt nicht.
- **CC BY-SA** (Wikipedia, Stack Exchange, Appropedia, Wikibooks) verlangt Namensnennung und Weitergabe unter gleicher Lizenz; für eigene Zusammenfassungen daraus die Quelle nennen.
- **Public Domain** (US-Regierung: NEETS, Army FM/TM, USDA, NIST, Sandia, NREL) ist uneingeschränkt nutzbar.
- **Software**: GPL-Software (Kiwix, Meshtastic) mit Quellcode ablegen, dann ist auch die Weitergabe sauber.
- **US-Militärhandbücher** (FM, TC, ATP, ADP) sind als Werke der US-Regierung gemeinfrei und frei kopier- und weitergebbar. Nur Ausgaben mit „Approved for public release; distribution is unlimited“ verwenden; „FOUO“- oder „Distribution restricted“-Fassungen nicht beschaffen. Quellen: Army Publishing Directorate, GlobalSecurity.org, Internet Archive.
- **Bundeswehr-Vorschriften** (ZDv, Zentralrichtlinien, Taschenkarten) sind nicht öffentlich und teils eingestuft; nur eigene Zusammenfassungen aus legal besuchten Lehrgängen. Der Reibert (Mittler Verlag) ist urheberrechtlich geschützt: gedrucktes Exemplar in die Box, digital nur eigene Zusammenfassung mit Quellenangabe.
- **Sprengfallen-/IED-Literatur**: Erkennungswissen ist legal; Bauanleitungen für Sprengvorrichtungen fallen unter § 52 WaffG / SprengG und gehören nicht in die Sammlung. FM 5-31 daher nur auszugsweise (Erkennungskapitel) übernehmen.
- **Dartnell, THE BOOK, weitere Neustart-Titel**: kommerziell; als gekauftes E-Book oder Eigen-Scan (Privatkopie) ablegen, Weitergabe ausgeschlossen. Kapitelextrakte in eigenen Worten mit Quellenangabe sind eigenes Werk.
- **Historische Fachliteratur vor 1929** (Hawkins, Henley's, Machinery's Handbook alte Ausgaben, King, Drew, Hooper) ist in den USA gemeinfrei; in Deutschland gilt 70 Jahre nach Tod des Autors, bei allen genannten Titeln erfüllt.
- **Chemie- und Medizinherstellung**: Historische Verfahren zu Säuren, Laugen, Anästhetika und Antibiotika sind frei dokumentierbar. Nicht in die Sammlung: Synthesewege für Sprengstoffe, Kampfstoffe oder Betäubungsmittel im Sinne des BtMG, auch nicht als „historischer Kontext“ mit Mengenangaben.

---

## 5. Beschaffungs- und Konvertierungsworkflow (auf einem PC, vor dem Einsatz)

1. ZIM-Dateien aus dem Kiwix-Katalog laden (HTTPS oder Torrent), `zimcheck` ausführen, `library.xml` mit `kiwix-manage` erzeugen.
2. Eigene Website-Kopien mit zimit (Docker, x86) erzeugen; eigene HTML-Sammlungen mit `zimwriterfs`.
3. Themen-ZIMs mit Bildern (Pilze, Wildpflanzen, Medizin DE, Elektrotechnik-Kategorie) mit mwoffliner und Artikelliste erzeugen.
4. PDFs komprimieren: Ghostscript `-dPDFSETTINGS=/ebook` (150 DPI) für Textdokumente; gescannte Schaltpläne und Zeichnungen bei 200 DPI belassen, sonst werden Bezeichner unlesbar; Vektor-PDFs nicht rastern. Scans mit ocrmypdf durchsuchbar machen.
5. PDF-Text extrahieren (PyMuPDF), in SQLite FTS5 indexieren, Chunks (500–800 Token) mit bge-m3 einbetten, in sqlite-vec speichern.
6. Karten: `pmtiles extract` aus dem Protomaps-Build mit Bounding-Box; Basemap-Assets (Style, Glyphs, Sprites) lokal ablegen; GraphHopper-Graph aus Geofabrik-PBF bauen.
7. Modelle laden, mit llama.cpp auf dem Pi testen (Token/s messen, Kontextgröße 4k–8k festlegen).
8. SHA-256-Manifest und par2 erzeugen, dann auf Ebene 2–5 spiegeln.

### Schema-Skizze für das eigene Tabellenbuch (SQLite)

```sql
CREATE TABLE notes(id INTEGER PRIMARY KEY, title TEXT, body_md TEXT, area TEXT, tags TEXT, source TEXT, checked_on TEXT);
CREATE TABLE formulas(id INTEGER PRIMARY KEY, name TEXT, latex TEXT, variables TEXT, units TEXT, area TEXT, source TEXT);
CREATE TABLE materials(name TEXT PRIMARY KEY, e_modul_gpa REAL, rm_mpa REAL, re_mpa REAL, density_kgm3 REAL, alpha_1e6k REAL, lambda_wmk REAL, notes TEXT, source TEXT);
CREATE TABLE standards_summary(norm_id TEXT PRIMARY KEY, title TEXT, scope TEXT, key_points_md TEXT, edition TEXT, source_ref TEXT, checked_on TEXT);
CREATE TABLE diag_trees(id INTEGER PRIMARY KEY, symptom TEXT, tree_md TEXT, area TEXT);
CREATE TABLE tc_table(type TEXT, temp_c REAL, emf_mv REAL);          -- aus NIST ITS-90
CREATE TABLE rtd_table(sensor TEXT, temp_c REAL, r_ohm REAL);        -- Callendar-Van-Dusen, selbst berechnet
CREATE VIRTUAL TABLE notes_fts USING fts5(title, body_md, tags, content='notes', content_rowid='id');
-- Vektoren: CREATE VIRTUAL TABLE notes_vec USING vec0(id INTEGER PRIMARY KEY, embedding float[1024]);
```
