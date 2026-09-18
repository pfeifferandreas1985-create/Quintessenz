# Quintessenz — Offline-Wissensassistent auf dem Raspberry Pi

> *Quintessenz* — das Wesentliche, auf das sich alles reduzieren lässt. Hier: das Wissen, das bleibt, wenn alles andere wegfällt.

> Eine Box, die ohne Internet Fragen beantwortet — mit einem lokalen Sprachmodell,
> das in einer Offline-Wissensbasis nachschlägt statt zu raten.
> Tragbar, stromsparend, redundant. Der kleine Bruder von AI-ARK.

**Status:** Konzept steht, die Oberfläche läuft als Prototyp.
`app/` enthält das QUINTESSENZ TERMINAL — die Weboberfläche, die alle Quellen
in einem einheitlichen Stil darstellt. Die Wissensbasis selbst wird gerade
beschafft; `ingest/` ist noch leer.

---

## Was hier entsteht

Ein Kasten, der weiterhilft, wenn das Netz weg ist. Nicht als Endzeitspielerei, sondern
weil Wissen, das nur in der Leitung hängt, kein Wissen ist, über das man verfügt.

Drei Teile greifen ineinander:

1. **Ein Wissensspeicher.** Rund 740 GB: Wikipedia in zwei Sprachen, 75.000 Bücher,
   Lehrbücher, 16 Fachforen mit beantworteten Praxisfragen, Medizin von Erster Hilfe bis
   Chirurgie ohne Klinik, Karten der ganzen Welt mit 1,15 Mio. Orten, Reparaturanleitungen,
   und das vollständige Werkstattwissen zu drei konkreten Fahrzeugen.
2. **Ein Sprachmodell, das nachschlägt statt zu raten.** Es antwortet aus diesen Quellen
   und nennt die Fundstelle. Läuft lokal, ohne Netz, ohne Konto, ohne Abo.
3. **Eine Oberfläche, die man ohne Anleitung bedient.** Das QUINTESSENZ TERMINAL in `app/`,
   gestaltet wie ein Gerät aus einer Welt, in der die Fünfziger nie aufgehört haben.

Zielgerät ist ein Raspberry Pi 5 mit einer NVMe-Platte, Stromaufnahme im einstelligen
Wattbereich. Auf einem PC läuft dasselbe schneller und mit größeren Modellen.

### Alles herunterladen, ein Befehl

```powershell
git clone https://github.com/pfeifferandreas1985-create/Quintessenz.git
cd Quintessenz\doomsdaybox\tools
.\alles_holen.ps1 -Ziel D:\DoomsdayBox
```

Auf Linux und dem Pi:

```bash
git clone https://github.com/pfeifferandreas1985-create/Quintessenz.git
cd Quintessenz/doomsdaybox/tools && chmod +x alles_holen.sh
ZIEL=/srv/box ./alles_holen.sh
```

Der Befehl lädt Archive, Karten, Modelle und Software nacheinander, prüft jede Datei gegen
die offizielle Prüfsumme und schreibt ein Logbuch. Abbrechen ist gefahrlos: beim nächsten
Aufruf geht es an der Abbruchstelle weiter. Mit `-Prio 1` beziehungsweise `PRIO=1` holt man
zuerst nur das Wichtigste, rund 80 GB.

**Platzbedarf:** etwa 740 GB. Das Ziellaufwerk darf nicht FAT32 sein, sonst scheitern alle
Dateien über 4 GB. Das Skript prüft das vorab.

---

## Start in fünf Minuten

Voraussetzung: Python 3.11 oder neuer. Sonst nichts — kein Node, kein Docker,
keine Datenbank.

```bash
git clone https://github.com/pfeifferandreas1985-create/Quintessenz.git
cd Quintessenz
python -m venv .venv && . .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python tools/fetch_fonts.py                        # einmalig, 287 kB, OFL
python -m uvicorn server:app --app-dir app --host 0.0.0.0 --port 8000
```

Dann `http://localhost:8000` aufrufen. Von einem anderen Gerät im WLAN:
`http://<IP-des-Rechners>:8000`.

### Wo liegen die Daten?

`app/pfade.py` sucht in dieser Reihenfolge und nimmt den ersten Ordner, der
tatsächlich Inhalt hat:

1. `$QUINTESSENZ_DATEN`
2. `/srv/box` — auf dem Pi
3. `D:\DoomsdayBox` — auf dem PC
4. `C:\D-Sicherung\DoomsdayBox` — Sicherungskopie

Ein anderer Pfad:

```bash
QUINTESSENZ_DATEN=/pfad/zur/box python -m uvicorn server:app --app-dir app
```

Findet sich nichts, startet die Anwendung trotzdem — sie zeigt dann nur die
Demo-Akten und markiert alle Themen als „wartet auf Beschaffung".

### Was der Prototyp heute kann

| | |
|---|---|
| 16 Bereiche in 6 Gruppen, 104 Themen | aus `doku/WISSENSUEBERSICHT.md` abgeleitet (`tools/gen_bereiche.py`); Gruppen sind Überschriften, keine Ebene |
| 68 echte Akten | aus `own/fahrzeuge/fahrzeuge.db` und `own/rebuild/rebuild_trees.db` |
| 7 Demo-Akten | ZIM-Artikel, Stack-Exchange-Fall, PDF-Kapitel — auf dem Papier als DEMO gestempelt |
| Volltextsuche | über den Speicher, ~2 ms bei 75 Akten; wird später FTS5 |
| Terminal- und Papieransicht | nebeneinander ab 900 px, gestapelt darunter |
| 10 Geräte (Themes) | jedes stellt Röhre **und** Papier um; Knopf *Gerät*, Taste `G` oder `T` |
| Tastatur, Touch, Druckansicht | vollständig |

Noch **nicht** angeschlossen: ZIM-, PDF- und Stack-Exchange-Adapter, RAG-Chat,
Vorlesen, Kartentisch, Werkstatt. Die Schnittstelle dafür steht in
`app/adapters/basis.py`.

### Auf dem Pi

```bash
sudo cp deploy/quintessenz.service /etc/systemd/system/
sudo systemctl enable --now quintessenz
```

### Dokumentation

| Datei | Inhalt |
|---|---|
| [docs/CONFIG.md](docs/CONFIG.md) | Bereiche, Themen und Quellen pflegen |
| [docs/DESIGN.md](docs/DESIGN.md) | Designsystem: Farben, Schriften, Abstände, Bausteine, Effekte |
| [docs/05_OFFENE-FRAGEN.md](docs/05_OFFENE-FRAGEN.md) | was noch zu entscheiden ist |

---

## Die Idee in drei Sätzen

Ein Raspberry Pi 5 mit NVMe-SSD trägt ein kleines Sprachmodell (2–3 B) und eine
durchsuchbare Wissensbasis: Wikipedia, WikiMed, Reparaturanleitungen, Fachbücher,
Karten, eigene Dokumente. Eine RAG-Pipeline verbindet beides — das Modell
formuliert, die Wissensbasis liefert die Fakten. Das Ganze läuft an einer
Powerbank, im Auto oder am Solarpaneel und ist über jedes Gerät im lokalen
Netz per Browser erreichbar.

## Warum nicht einfach AI-ARK?

| | AI-ARK | Quintessenz |
|---|---|---|
| Rolle | Vollarchiv, 500 GB Modelle, Workstation-Klasse | Tragbare Notfallbox, ein Modell, ein Zweck |
| Hardware | Beliebiger PC mit viel RAM/GPU | Pi 5, 16 GB, ~15 W |
| Strom | 100–500 W | 10–25 W, Powerbank-tauglich |
| Stärke | Die besten offenen Modelle, Coding, Analyse | Immer an, überall, fast umsonst im Betrieb |
| Schwäche | Braucht einen Rechner, der im Ernstfall vielleicht nicht läuft | 2-B-Modell — formuliert gut, denkt wenig |

Beide teilen sich die Wissensbasis (ZIM-Dateien, Dokumente). Quintessenz ist das,
was man in die Tasche steckt, wenn die Workstation nicht mitkommt.

## Dokumente

| Datei | Inhalt |
|---|---|
| [docs/01_KONZEPT.md](docs/01_KONZEPT.md) | Zielbild, Nutzungsszenarien, Architektur, Phasenplan |
| [docs/02_HARDWARE.md](docs/02_HARDWARE.md) | Stückliste, Entscheidung Pi vs. Mini-PC, die NPU-Frage |
| [docs/03_SOFTWARE.md](docs/03_SOFTWARE.md) | OS, Inferenz, Kiwix, RAG-Pipeline, Oberfläche |
| [docs/04_WISSENSBASIS.md](docs/04_WISSENSBASIS.md) | Was rein muss, priorisiert nach Bereich, mit Quellen |
| [docs/05_OFFENE-FRAGEN.md](docs/05_OFFENE-FRAGEN.md) | Was vor dem Kauf geklärt werden muss |
| [docs/06_TERMINAL-AUFTRAG.md](docs/06_TERMINAL-AUFTRAG.md) | Arbeitsauftrag für die Oberfläche: Offline-Wissensbibliothek im Atompunk-Stil (Terminal + Papier) |

## Verwandt

- **AI-ARK** — das große Offline-Archiv (500 GB Modelle, Handbuch, Skripte), lokal unter `D:\AI-ARK`
- [Potato OS](https://github.com/potato-os/core) — fertiges Pi-Image mit LLM + Web-UI
- [Kiwix](https://kiwix.org) — Offline-Reader für ZIM-Archive
- [Project NOMAD](https://github.com/geoffwhittington/project-nomad) — Docker-Stack für Offline-Wissen + KI (x86, als Architekturvorlage)
- [Hesperian Foundation](https://hesperian.org) — *Where There Is No Doctor* und weitere Handbücher, frei als PDF
