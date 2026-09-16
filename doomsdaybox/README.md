# DoomsdayBox – Beschaffungspaket Szenario „Voll“

Ziel-Hardware: Raspberry Pi 5 (16 GB), NVMe 1 TB. Dieser Ordner auf D: ist die **Sammel- und Spiegelstation** auf dem PC.
Nach der Beschaffung wird der Ordner 1:1 auf die NVMe des Pi kopiert (Zielpfad `/srv/box`) und auf USB-SSDs gespiegelt.
Erwartete Größe Voll: ca. 330 GB (ohne Optionen), bis 480 GB mit Stack Overflow, Wikipedia EN maxi und CD3WD.

## Ordnerstruktur

| Ordner | Inhalt | Skript |
|---|---|---|
| `zim/` | Kiwix-ZIM-Dateien + `library.xml` + `MANIFEST.sha256` | `tools/download_zim.sh` |
| `pdf/` | Handbücher, Datenblätter, Public-Domain-Klassiker, nach Modul sortiert | `tools/pdf_sources.csv` (manuell) |
| `db/` | SQLite: PDF-Volltextindex, Embeddings (sqlite-vec), POI-Datenbank | eigene RAG-Pipeline |
| `maps/` | PMTiles Europa/DACH/Deutschland, Basemap-Assets, PBF, Routing-Graph | `tools/maps.sh` |
| `models/` | GGUF/GGML/ONNX-Modelle | `tools/download_models.sh` |
| `src/` | Software-Spiegel: pip-Wheels, APT-Teilspiegel, Firmware, Quellcode, Beckhoff InfoSys | manuell |
| `own/` | eigenes Material je Modul: `mech`, `med`, `surv`, `mil`, `rebuild`, `fahrzeuge` | Git-Repo empfohlen |
| `own/fahrzeuge/fahrzeuge.db` | **Fahrzeugakten** Defender 110 TD5, Mini Cooper MPi 1999, Vespa V50 1963: Kenndaten, Stücklisten mit OEM-Nummern, Schwachstellen, Wartung, Dokumente | `fahrzeuge.sql`, `build.py` |
| `own/rebuild/rebuild_trees.db` | **Technologie-Abhängigkeitsbäume** (10 Kerntechnologien, 53 Knoten, 78 Kanten, 9 Prozesse) | `rebuild_trees.sql` |
| `doku/` | Spezifikation der Wissensdatenbank | — |
| `tools/` | alle Skripte und Manifeste | — |

## Reihenfolge der Beschaffung (auf dem PC, Linux/WSL/Git-Bash)

1. Werkzeuge installieren: `aria2`, `curl`, `libxml2-utils` (xmllint), `zim-tools` (zimcheck, zimwriterfs), `kiwix-tools` (kiwix-manage, kiwix-serve), `par2`, `python3`, `pip install huggingface_hub[cli] osmium`, `pmtiles`-CLI, Java 17 (Routing), Docker (zimit, mwoffliner).
2. ZIM-Dateien: `tools/download_zim.sh D:/DoomsdayBox/zim 3` – läuft Tage, ist wiederaufnehmbar. Erst Priorität 1 (`... 1`), dann Rest.
3. Modelle: `tools/download_models.sh D:/DoomsdayBox/models 3` – vorher Gemma-Lizenz auf huggingface.co annehmen und `hf auth login`.
4. Karten: `tools/maps.sh D:/DoomsdayBox/maps` – Europa-Extrakt ca. 30 GB; GraphHopper-Import anschließend von Hand starten (Befehl wird ausgegeben).
5. PDFs: `tools/pdf_sources.csv` abarbeiten. Spalte `zielordner` gibt den Ablageort vor. Komprimieren:
   `gs -sDEVICE=pdfwrite -dPDFSETTINGS=/ebook -dNOPAUSE -dBATCH -sOutputFile=out.pdf in.pdf` (150 DPI; Zeichnungs-Scans bei 200 DPI belassen).
   Scans durchsuchbar machen: `ocrmypdf -l deu+eng in.pdf out.pdf`.
6. Eigene Website-Kopien (Elektronik-Kompendium, mikrocontroller.net, DARC-Lehrgang, Meshtastic-Doku) mit zimit im Docker erzeugen → `zim/`.
7. Themen-ZIMs mit Bildern (Pilze, Wildpflanzen, Medizin DE, Elektrotechnik) mit mwoffliner und Artikelliste → `zim/`.
8. Eigenes Material in `own/` schreiben; `rebuild_trees.sql` erweitern und neu bauen (siehe unten).
9. Prüfsummen und Parität: `tools/verify_mirror.sh D:/DoomsdayBox`.
10. Auf den Pi: `rsync -a --info=progress2 D:/DoomsdayBox/ pi:/srv/box/`, dann `kiwix-serve --library /srv/box/zim/library.xml --port 8080`.

## Abhängigkeitsbäume benutzen

Neu bauen nach Änderungen an der SQL-Datei:

```bash
python3 -c "import sqlite3,pathlib; c=sqlite3.connect('own/rebuild/rebuild_trees.db'); c.executescript(pathlib.Path('own/rebuild/rebuild_trees.sql').read_text(encoding='utf-8'))"
```

Nützliche Abfragen (sqlite3-Shell oder Python):

```sql
-- Kompletter Baum einer Kerntechnologie
SELECT depth, path, min_viable_scale FROM v_tree WHERE root='electric-motor' ORDER BY path;

-- Engpässe: welche Vorprodukte brauchen die meisten Kerntechnologien?
SELECT * FROM v_bottlenecks;

-- Alles, was nur geborgen werden kann (Lagerhaltungs-Prioritäten)
SELECT * FROM v_salvage_only;

-- Prozesse mit Sicherheitshinweisen
SELECT name, scale, hazards FROM process;

-- Volltextsuche
SELECT id, name FROM tech_fts WHERE tech_fts MATCH 'Schellack OR Isolation';
```

Ergebnis des ersten Durchlaufs: Alle zehn Kerntechnologien laufen auf dieselben neun Vorprodukte zurück: Kupferschrott, Eisenschrott, Holz, Ton, Holzkohle, Schmelzofen, Tiegel, Kohlenstoffstahl und Härten/Anlassen. Nur zwei Knoten sind reine Salvage-Güter: Permanentmagnete und Röhren-Elektrodenmetalle. Kugellager sind die einzige Kerntechnologie auf Regionsniveau, alle anderen sind mit Dorfmitteln erreichbar.

## Redundanz

| Kopie | Medium | Dateisystem | Takt |
|---|---|---|---|
| Betrieb | NVMe im Pi | ext4 | laufend |
| Sammelstation | D: (dieser Ordner, externe HDD) | exFAT (nach Neuformatierung) | Quelle aller Kopien |
| Spiegel 1 | USB-SSD 1–2 TB | exFAT | nach jeder Änderung, `rsync -rlt --delete` |
| Spiegel 2 | USB-SSD extern gelagert, Metallbox | exFAT | vierteljährlich rotieren |
| System | 2 microSD mit bootfähigem Pi-Image | ext4 | nach jeder Systemänderung |
| Papier | 50–100 Seiten Notfallkern | — | jährlich |

Prüfung halbjährlich mit `tools/verify_mirror.sh <Pfad> check` auf jeder Kopie.

## Rechtliches (Kurzform)

Frei weitergebbar: Wikipedia, Stack Exchange, Wikibooks, Appropedia (CC BY-SA), US-Regierungswerke (Public Domain), Klassiker vor 1929.
Nur Eigennutzung: Hersteller-Handbücher, Website-Kopien per zimit (Privatkopie), gekaufte E-Books (Dartnell, Gingery, THE BOOK, Tabellenbücher).
Nicht kommerziell weitergeben: iFixit, Hesperian, wikiHow, WHO, FAO (NC-Lizenzen).
Nicht in die Sammlung: DIN/VDE-Normen als Kopie, Bundeswehr-Vorschriften, Bauanleitungen für Sprengmittel oder Waffen, FM 5-31 außer Erkennungskapitel.
Details: `doku/Wissensdatenbank_Doomsday_Box_Spezifikation.md`, Abschnitt 4.

## Externe Platte D: – Stand 15.09.2026

- D: ist eine **Intenso External USB 3.0, 3,7 TB, 2,5 Zoll** (mit hoher Wahrscheinlichkeit SMR-HDD, ca. 100 MB/s sequentiell, sehr langsam bei vielen kleinen Dateien).
- D: war **FAT32**: keine Datei über 4 GB möglich. Fast jede ZIM-Datei und jedes Modell ist größer. Die Sicherung des alten Inhalts liegt in `C:\D-Sicherung` (418 GB, inkl. `AI-ARK` und `DoomsdayBox`).
- Neuformatierung durch den Benutzer: **exFAT** (Windows, Linux/Pi, Android, macOS lesen es), Clustergröße 1 MB. NTFS nur, wenn ausschließlich Windows + Pi genutzt wird. Danach `C:\D-Sicherung\*` zurückkopieren.
- Beide Download-Skripte brechen jetzt auf FAT32 mit Fehlermeldung ab.
- HDD-Regeln: ZIM-Downloads mit einer Verbindung direkt auf D: (sequentiell), oder mit drittem Parameter `STAGE` auf die interne SSD laden und verschieben lassen (`./download_zim.sh /d/DoomsdayBox/zim 3 /c/stage`). Sammlungen mit vielen kleinen Dateien (PDF-Bibliothek, Beckhoff InfoSys, pip-Wheels, CD3WD, Git-Klone) auf C: aufbauen und als Ganzes per `rsync`/`robocopy` nach D: schieben. par2 nur für `pdf/`, `db/`, `own/`.
- Verhältnis zu `D:\AI-ARK`: AI-ARK ist das Modell- und Laufzeitarchiv (Ziel 2-TB-NVMe, große Modelle für PC/Workstation). DoomsdayBox ist das Wissensarchiv für den Pi 5. Überschneidungen vermeiden: Modelle für den Pi kommen aus `AI-ARK/01_MODELS/minimal` und `embedding` (Skript `download_models.sh` übernimmt vorhandene Dateien mit drittem Parameter `/d/AI-ARK/01_MODELS`), Laufzeit (llama.cpp ARM64, kiwix-tools aarch64) aus `AI-ARK/00_RUNTIME`. Die ZIM-Sammlung wird nur einmal gehalten: hier in `DoomsdayBox/zim`, `AI-ARK/03_KNOWLEDGE/zim` verweist darauf.
