# ÜBERGABE an den Download-Agenten – DoomsdayBox, Szenario „Voll“

Stand: 2026-09-15. Autor: Planungs-Session DoomsdayBox. Empfänger: Agent, der aktuell Laufwerk D: (Intenso 3,7 TB, extern, USB 3.0) beschreibt.

## 0. Kontext in fünf Sätzen

Auf D: entstehen zwei Archive. `D:\AI-ARK` ist das Modell- und Laufzeitarchiv für PC/Workstation (deine bisherige Aufgabe). `D:\DoomsdayBox` ist das **Wissensarchiv für einen Raspberry Pi 5 (16 GB RAM, 1 TB NVMe)**: Kiwix-ZIMs, PDF-Bibliothek, Offline-Karten, kleine Modelle, eigenes Material. Beide teilen sich die Platte, nichts wird doppelt geladen. Diese Anweisung sagt dir exakt, was in `D:\DoomsdayBox` hinein muss, in welcher Reihenfolge, und was nicht.

## 1. Vorbedingungen – vor dem ersten Byte prüfen

1. **Dateisystem von D:** muss exFAT oder NTFS sein. Prüfen: `Get-Volume -DriveLetter D | Select FileSystem`. Steht dort FAT32: **nichts laden**, die 4-GB-Grenze zerstört jede ZIM-Datei. Neuformatierung macht der Benutzer, alter Inhalt liegt in `C:\D-Sicherung` (418 GB). Nach der Formatierung `C:\D-Sicherung\*` zurückkopieren, dann weiter.
2. **Freier Platz:** Voll braucht ca. 330 GB, mit Optionen bis 480 GB. Zusätzlich zu AI-ARK (ca. 565–625 GB). Beides passt auf 3,7 TB.
3. **HDD-Regeln:** D: ist eine 2,5-Zoll-Festplatte (vermutlich SMR). Große Dateien sequentiell mit **einer** Verbindung direkt auf D: laden, oder auf `C:\stage` laden und danach verschieben. Sammlungen aus vielen kleinen Dateien (PDFs, Git-Klone, pip-Wheels, Beckhoff InfoSys) **immer** auf C: aufbauen und als Ganzes nach D: kopieren.
4. **Werkzeuge:** aria2c oder wget, curl, sha256sum, `zimcheck` (zim-tools), `kiwix-manage` (kiwix-tools, liegt in `D:\AI-ARK\00_RUNTIME\ui\kiwix`), `hf` (huggingface_hub CLI), `pmtiles`-CLI, Python 3, Ghostscript, optional Docker.
5. **Skripte** liegen fertig in `D:\DoomsdayBox\tools\` (Bash, für WSL oder Git-Bash). Du kannst sie benutzen oder die Listen unten manuell abarbeiten. Beide Download-Skripte brechen auf FAT32 selbst ab.

## 2. Zielstruktur (nicht ändern)

```
D:\DoomsdayBox\
  zim\        ZIM-Dateien + library.xml + MANIFEST.sha256
  pdf\        PDFs nach Modul: mech, prog, med, surv, energie, komm, mil, rebuild
  maps\       PMTiles, Basemap-Assets, PBF, Routing
  models\     Modelle für den Pi (GGUF/GGML/ONNX)
  src\        Software für den Pi: llama.cpp arm64, kiwix-tools aarch64, pip-Wheels, Firmware, Quellcode
  db\         bleibt leer (wird auf dem Pi gefüllt)
  own\        eigenes Material (mech, med, surv, mil, rebuild) – nicht anfassen, enthält rebuild_trees.db
  doku\       Spezifikation
  tools\      Skripte, zim_manifest.tsv, pdf_sources.csv
```

Jeder Unterordner bekommt eine `MANIFEST.sha256` (Format `sha256sum`-kompatibel: `<hash>  <dateiname>`). Nach jedem Download eintragen.

## 3. Phase A – ZIM-Dateien (ca. 220 GB, wichtigster Block)

Quelle: `https://download.kiwix.org/zim/<kategorie>/<prefix>_YYYY-MM.zim`, Spiegel `https://ftp.fau.de/kiwix/zim/`. Immer die **neueste** Ausgabe (höchstes Datum im Dateinamen) nehmen. Neueste URL per Katalog: `https://library.kiwix.org/catalog/v2/entries?name=<prefix>&count=1` (Link auf `.meta4`, Endung abschneiden). Nach dem Download `zimcheck -C <datei>` ausführen; schlägt es fehl, Datei löschen und neu laden. Falls Kiwix eine `<datei>.sha256` anbietet, zusätzlich vergleichen.

Skript: `tools/download_zim.sh /d/DoomsdayBox/zim <MAX_PRIO> [/c/stage]` – liest `tools/zim_manifest.tsv`, ist wiederaufnehmbar, baut `library.xml`.

Reihenfolge: erst alle Prio 1, dann 2, dann 3.

### Prio 1 (ca. 65 GB)

| Prefix | Kategorie | ca. GB | Zweck |
|---|---|---|---|
| wikipedia_de_all_maxi | wikipedia | 45 | Wikipedia DE mit Bildern |
| wikipedia_en_medicine_maxi | wikipedia | 1,7 | WikiMed EN |
| wikipedia_de_medicine_maxi | wikipedia | 1 | WikiMed DE – **falls im Katalog vorhanden**, sonst überspringen und melden |
| wikibooks_de_all_maxi | wikibooks | 1,3 | Lehrbücher DE |
| electronics.stackexchange.com_en_all | stack_exchange | 2 | Elektronik Q&A |
| devdocs_en_c | devdocs | 0,02 | C-Referenz |
| devdocs_en_cpp | devdocs | 0,1 | C++-Referenz |
| devdocs_en_python | devdocs | 0,1 | Python-Referenz |
| devdocs_en_bash | devdocs | 0,01 | Bash-Referenz |
| zimgit-post-disaster_en | other | 0,6 | Katastrophen-Sammlung |
| zimgit-water_en | other | 0,05 | Wasser |
| zimgit-food-preparation_en | other | 0,2 | Nahrung |
| zimgit-medicine_en | other | 0,07 | Medizin |

### Prio 2 (ca. 25 GB)

| Prefix | Kategorie | ca. GB |
|---|---|---|
| wikibooks_en_all_maxi | wikibooks | 4 |
| arduino.stackexchange.com_en_all | stack_exchange | 0,4 |
| raspberrypi.stackexchange.com_en_all | stack_exchange | 0,3 |
| engineering.stackexchange.com_en_all | stack_exchange | 0,2 |
| unix.stackexchange.com_en_all | stack_exchange | 2,5 |
| askubuntu.com_en_all | stack_exchange | 3,5 |
| diy.stackexchange.com_en_all | stack_exchange | 1 |
| mechanics.stackexchange.com_en_all | stack_exchange | 0,3 |
| gardening.stackexchange.com_en_all | stack_exchange | 0,2 |
| outdoors.stackexchange.com_en_all | stack_exchange | 0,15 |
| ham.stackexchange.com_en_all | stack_exchange | 0,1 |
| ifixit_de_all | ifixit | 2 |
| wikihow_de_maxi | wikihow | 3 |
| appropedia_en_all_maxi | other | 2 |
| lowtechmagazine.com_en_all | other | 0,3 |
| energypedia_en_all_maxi | other | 0,3 |
| archlinux_en_all_maxi | other | 0,2 |

### Prio 3 (ca. 135 GB)

| Prefix | Kategorie | ca. GB |
|---|---|---|
| wikipedia_en_all_nopic | wikipedia | 55 |
| gutenberg_en_all | gutenberg | 65 |
| gutenberg_de_all | gutenberg | 2,5 |
| ifixit_en_all | ifixit | 3,5 |
| superuser.com_en_all | stack_exchange | 4 |
| physics.stackexchange.com_en_all | stack_exchange | 3 |
| woodworking.stackexchange.com_en_all | stack_exchange | 0,1 |
| medicalsciences.stackexchange.com_en_all | stack_exchange | 0,1 |
| wiktionary_de_all_maxi | wiktionary | 1 |
| wikiversity_de_all_maxi | wikiversity | 0,5 |

**Nicht laden** (nur auf ausdrückliche Anweisung): `stackoverflow.com_en_all` (80 GB), `wikipedia_en_all_maxi` (110 GB). `wikipedia_de_all_mini` liegt bei AI-ARK, nicht doppelt.

Wenn ein Prefix im Katalog nicht existiert: nicht raten, sondern im Bericht als „nicht gefunden“ listen. Namen können sich geändert haben (z. B. Suffix `_maxi`/`_all` vertauscht); Suche im Katalog mit dem Stamm (`appropedia`, `lowtech`) ist erlaubt.

Abschluss Phase A: `kiwix-manage D:\DoomsdayBox\zim\library.xml add <jede .zim>`.

## 4. Phase B – Modelle für den Pi 5 (ca. 15 GB)

Ziel: `D:\DoomsdayBox\models\<Repo-Name>\`. **Zuerst in `D:\AI-ARK\01_MODELS` nachsehen**; liegt die Datei dort vollständig (keine `.incomplete`, nicht in `.cache`), kopieren statt laden. Repos stammen aus `D:\AI-ARK\01_INVENTAR.md` (am 15.09.2026 gegen die HF-API geprüft).

Skript: `tools/download_models.sh /d/DoomsdayBox/models 3 /d/AI-ARK/01_MODELS`

| Prio | Repo | Datei-Muster | ca. GB | Zweck |
|---|---|---|---|---|
| 1 | unsloth/Qwen3.5-9B-GGUF | `*Q4_K_M*.gguf` | 6 | Hauptmodell Text |
| 1 | unsloth/gemma-4-E4B-it-GGUF | `*Q4_K_M*.gguf` + `mmproj*` | 4,5 | schnelles Modell, Bild + Audio |
| 1 | Qwen/Qwen3-Embedding-0.6B-GGUF | `*Q8_0*.gguf` | 0,6 | Embedding für RAG |
| 2 | unsloth/gemma-4-E2B-it-GGUF | `*Q4_K_M*.gguf` + `mmproj*` | 3 | Notmodell |
| 2 | unsloth/Qwen3.5-0.8B-GGUF | `*Q8_0*.gguf` | 0,8 | Kleinstmodell |
| 2 | nomic-ai/nomic-embed-text-v1.5-GGUF | `*Q8_0*.gguf` | 0,3 | Embedding-Notnagel |
| 2 | ggerganov/whisper.cpp | `ggml-medium.bin`, `ggml-small.bin` | 2 | Sprache → Text |
| 3 | unsloth/granite-4.0-h-1b-GGUF | `*Q8_0*.gguf` | 1,1 | Kleinstmodell |
| 3 | rhasspy/piper-voices | `de/de_DE/thorsten/medium/*` | 0,1 | Text → Sprache DE |
| 3 | GGUF-Fassung von bge-reranker-v2-m3 | per `hf search "bge-reranker-v2-m3 gguf"` suchen | 0,6 | Reranker; Repo im Bericht nennen |

Nicht laden: alles aus `AI-ARK/01_MODELS/mid` und `small` (passt nicht in 16 GB RAM des Pi).

## 5. Phase C – Karten (ca. 42 GB)

Ziel: `D:\DoomsdayBox\maps\`. Skript: `tools/maps.sh /d/DoomsdayBox/maps`. Manuell:

1. Neuesten Protomaps-Build ermitteln: `https://build.protomaps.com/builds.json` → höchster Key `YYYYMMDD.pmtiles`.
2. Extrakte (`pmtiles extract <URL> <ziel> --bbox=W,S,O,N`):
   - `europa.pmtiles` bbox `-25,34,45,72` (ca. 30 GB)
   - `dach.pmtiles` bbox `5.8,45.8,17.2,55.1` (ca. 6 GB)
   - `deutschland.pmtiles` bbox `5.8,47.2,15.1,55.1` (ca. 4 GB)
3. `git clone --depth 1 https://github.com/protomaps/basemaps-assets` nach `maps\assets\` (Schriften, Sprites).
4. MapLibre GL JS + CSS (`https://unpkg.com/maplibre-gl@5/dist/`) und `https://unpkg.com/pmtiles@4/dist/pmtiles.js` nach `maps\assets\`.
5. `https://download.geofabrik.de/europe/germany-latest.osm.pbf` (ca. 4 GB) + `.md5` prüfen.
6. GraphHopper: `graphhopper-web-10.0.jar` von Maven Central + `config-example.yml` nach `maps\routing\`. Import (`java -Xmx8g -jar ... import config.yml`) nur, wenn Zeit ist; sonst im Bericht als offen vermerken.

## 6. Phase D – Software für den Pi (ca. 3 GB, auf C: sammeln, dann nach `src\`)

- llama.cpp: `llama-b109xx-bin-ubuntu-arm64.tar.gz` – liegt in `D:\AI-ARK\00_RUNTIME\llamacpp\`, kopieren.
- kiwix-tools `linux-aarch64` – liegt in `D:\AI-ARK\00_RUNTIME\ui\kiwix\`, kopieren.
- Raspberry Pi OS Lite 64-bit Image (aktuell) + `SHA256` von raspberrypi.com.
- pip-Wheels für aarch64/manylinux2014, Python 3.11–3.13: `numpy sqlite-vec llama-cpp-python python-libzim pymupdf paho-mqtt pyserial pymodbus fastapi uvicorn huggingface_hub` → `pip download --platform manylinux2014_aarch64 --only-binary=:all: --python-version 3.12 -d src\wheels <pakete>`.
- Debian-Pakete für den Pi (arm64 .deb): `kiwix-tools`, `zim-tools`, `par2`, `aria2`, `hostapd`, `dnsmasq`, `openjdk-17-jre-headless`, `ocrmypdf`, `tesseract-ocr-deu` → via `apt-get download` auf einem arm64-System oder aus deb.debian.org; alternativ im Bericht als offen markieren.
- Meshtastic-Firmware-Release (zip) + Web-Flasher-Quellen von github.com/meshtastic/firmware/releases.
- Quellcode als Tarball: llama.cpp, kiwix-tools, libzim, sqlite-vec, MapLibre GL JS (jeweils GitHub „Source code“).

## 7. Phase E – PDF-Bibliothek (ca. 15 GB, Handarbeit, auf C: sammeln)

Vollständige Liste mit Lizenz, Startseite und Zielordner: `tools/pdf_sources.csv` (90 Zeilen, Trennzeichen `;`). Abarbeiten nach Spalte `prio`. **Prio 1 zuerst**, das sind unter anderem:

- Lessons in Electric Circuits Bd. 1–6 (allaboutcircuits.com / ibiblio.org)
- NEETS Module 1–24 (archive.org, Suchbegriff „NEETS module“)
- TI: Op Amps for Everyone (ti.com/lit/slod006), Analog Engineer's Pocket Reference; ADI: Linear Circuit Design Handbook
- DGUV Vorschrift 3, DGUV Information 203-xxx, DGUV Regel 103-011 (publikationen.dguv.de); TRBS 1201/1203 (baua.de)
- ABB Electrical Installation Handbook Vol. 1+2; Schneider Electrical Installation Guide
- SKF Wälzlager-Hauptkatalog; Schaeffler HR1
- SEW „Praxis der Antriebsauslegung“; Danfoss „Facts Worth Knowing about Frequency Converters“; Siemens SINAMICS G120/V20, S7-1200 Systemhandbuch
- Åström/Murray „Feedback Systems“ (fbsbook.org); WIKA Handbuch Druck-/Temperaturmesstechnik
- NAVEDTRA 14105 Fluid Power; PLCopen Coding Guidelines; OSCAT-Doku + Bibliotheken (oscat.de)
- Tektronix XYZs of Oscilloscopes; R&S Oscilloscope Fundamentals; Fluke-Grundlagen
- Modern C (Gustedt); Beej's Guide to C; cppreference-Offline-Archiv; Python-3-Doku HTML; Barr Embedded C Coding Standard
- Hesperian: Where There Is No Doctor, No Dentist, Where Women Have No Doctor, A Book for Midwives, „Wo es keinen Arzt gibt“ (hesperian.org)
- ERC-Leitlinien 2021 deutsch (grc-org.de); DGUV 204-006
- Emergency War Surgery (medcoe.army.mil); TCCC Guidelines + Quick Reference (deployedmedicine.com); TECC Guidelines (c-tecc.org); Stop the Bleed
- WHO: Surgical Care at the District Hospital, Pocket Book Hospital Care for Children, Anaesthesia at the District Hospital, Drinking-water Quality, Model Formulary 2008, Essential Medicines List; MSF Essential Drugs + Clinical Guidelines
- OpenStax: Pharmacology for Nurses, Anatomy and Physiology 2e; CDC Household Water Treatment; Primary Surgery Bd. 1+2 (primary-surgery.org)
- FM 21-76 / FM 3-05.70 / ATP 3-50.21 Survival; USDA Complete Guide to Home Canning; SODIS Manual; CAWST Biosand Filter Manual
- Sandia SAND87-7023 Stand-Alone PV Handbook (osti.gov); Victron Wiring Unlimited; FEMA Wood Gas Generator (1989)
- BNetzA Frequenzplan + Fragenkataloge Amateurfunk
- FM 21-11 First Aid for Soldiers + TC 4-02.1 First Aid; Prolonged Field Care Guidelines
- Public-Domain-Klassiker (archive.org/gutenberg.org): Farm Blacksmithing (1901), Hawkins Electrical Guide Bd. 1–10 (1917), Machinery's Handbook ≤1928, Henley's Formulas (1914), Rogers Industrial Chemistry, Hand-Loom Weaving (1910), Farmers of Forty Centuries (1911), King's American Dispensatory (1898), Radio Amateur's Handbook 1926–1928
- Beckhoff Information System Offline-Installer (infosys.beckhoff.com, 3–6 GB) → `src\beckhoff-infosys\`

Regeln: Nur Ausgaben mit dem Vermerk „Approved for public release; distribution is unlimited“ bei US-Militärdokumenten. Nach dem Download Ghostscript `-dPDFSETTINGS=/ebook` (150 DPI) auf Text-PDFs; Scans von Zeichnungen unverändert lassen. Dateiname: `<Herausgeber>_<Titel>_<Jahr>.pdf`, keine Leerzeichen. Kommerzielle Titel (Dartnell, Gingery, THE BOOK, Tabellenbücher, Reibert) **nicht** laden, die kauft der Benutzer.

## 7a. Phase F – Eigene Fahrzeuge (ca. 2 GB, Handarbeit, auf C: sammeln)

Fahrzeuge des Benutzers: **Land Rover Defender 110 TD5** (1998–2006), **Rover Mini Cooper 1.3i MPi „British Open Classic“** (1999), **Vespa V50 N, V5A1T** (1963). Zielordner `pdf\fahrzeuge\<defender|mini|vespa>\`, Explosionszeichnungen in den Unterordner `explosionszeichnungen\`. Quellen mit Lizenz in `tools/pdf_sources.csv`, Modul `fahrzeuge` (16 Zeilen). Die Fahrzeugakten (`own\fahrzeuge\fahrzeuge.db`, `Fahrzeugakte_*.md`) **nicht** verändern.

| Fahrzeug | Frei beschaffbar (jetzt laden) | Kaufen (Benutzer entscheidet, im Bericht listen) |
|---|---|---|
| Defender TD5 | Nanocom-Evolution-Handbuch (nanocom-diagnostics.com); Online-Teilekataloge mit Explosionszeichnungen: lrcat.com, britpart.com, paddockspares.com, rimmerbros.com – **jede Baugruppe** (Motor, Kraftstoff, Kühlung, Getriebe R380, Verteilergetriebe LT230, Achsen, Bremsen, Lenkung, Elektrik, Karosserie, Rahmen) als PDF drucken, Dateiname `Defender-TD5_<Baugruppe>_<Quelle>.pdf` | Defender Workshop Manual TD5 + Electrical Library (Brooklands), Parts Catalogue STC9021CC (Brooklands), Haynes 3017 |
| Mini MPi 1999 | minispares.com: alle Baugruppen für Mini MPi 1997–2000 als PDF (Motor, Einspritzung MEMS, Kühlung, Getriebe, Antriebswellen, Bremsen, Fahrwerk, Karosserie, Elektrik); Mini-Mania-Tech-Artikel zu MPi/MEMS 2J; MPi-Schaltplan aus Foren (theminiforum.co.uk, mini-forum.de) | Rover Mini Workshop Manual 1992–2000 inkl. MPi (Brooklands), Mini Parts Catalogue 1990–2000, Haynes 0646 |
| Vespa V50 1963 | scooterhelp.com: Werkstatthandbuch „Vespa 50“, Ersatzteilkatalog „Vespa 50 V5A1T“, Bedienungsanleitung 1963 (Scans, Privatkopie); sip-scootershop.com und scooter-center.com: Explosionszeichnungen Modell **V50 N (V5A1T)** je Baugruppe mit aktuellen Teilenummern als PDF; GSF-Wiki-Artikel (germanscooterforum.de): Zündung einstellen, Motor teilen, Falschluft suchen | Bucheli Reparaturanleitung Smallframe, Vespa Technica Smallframe |

Regeln: Online-Kataloge nur für den Eigengebrauch speichern (Privatkopie), nicht weitergeben. Bei Land Rover die Fahrgestellnummer eingeben, sobald der Benutzer sie liefert, sonst Bauzeitraum 1999–2006 wählen. Keine Raubkopien von Brooklands/Haynes/Bucheli. Foren nicht spiegeln, nur die genannten Artikel.

## 8. Ausschlüsse – auf keinen Fall

- DIN/VDE/IEC-Normen als Datei (auch nicht von Drittseiten).
- Bundeswehr-Vorschriften (ZDv, Zentralrichtlinien, Taschenkarten), Reibert-Scans.
- Bauanleitungen für Sprengmittel, Waffen, Sprengfallen; FM 5-31 nur, wenn ausdrücklich angefordert, und dann mit Vermerk „nur Erkennungskapitel“.
- US-Dokumente mit „FOUO“, „Distribution restricted“ oder Einstufung.
- Raubkopien kommerzieller Bücher (libgen, z-lib o. ä.).
- Modelle aus `AI-ARK/mid` und `small` in die DoomsdayBox kopieren.

## 9. Bericht nach jeder Phase

Format wie `D:\AI-ARK\LOGBUCH.md`: `| Datum | Aktion | Ergebnis |`, Datei `D:\DoomsdayBox\LOGBUCH.md`. Pro Phase: Anzahl Dateien, GB, Prüfsummen OK/fehlgeschlagen, Liste „nicht gefunden“, Liste „offen“. Am Ende `tools/verify_mirror.sh /d/DoomsdayBox` ausführen und den Bericht anhängen. Solange D: nicht neu formatiert ist: alle kleinen Änderungen zusätzlich nach `C:\D-Sicherung\DoomsdayBox` spiegeln.

## 10. Zusammenfassung der Größen

| Phase | Inhalt | ca. GB |
|---|---|---|
| A | ZIM Prio 1 / 2 / 3 | 65 / 25 / 135 |
| B | Modelle Pi | 15 |
| C | Karten | 42 |
| D | Software Pi | 3 |
| E | PDF + Beckhoff | 15 |
| **Summe** | | **ca. 300 GB** |

Reihenfolge, wenn die Zeit knapp ist: A-Prio 1 → B-Prio 1 → C deutschland.pmtiles + Assets → E-Prio 1 → A-Prio 2 → Rest.
