# 03 — Software

## Zwei Wege — Entscheidung in Phase 1

| | **Weg A: Potato OS** | **Weg B: Raspberry Pi OS + eigener Stack** |
|---|---|---|
| Aufwand bis zum ersten Chat | 20 Minuten | 2–3 Stunden |
| LLM-Laufzeit | ik_llama.cpp (Pi-optimiert), llama.cpp | llama.cpp oder Ollama |
| Web-UI | vorhanden, `http://potato.local` | selbst wählen (Open WebUI zu schwer für Pi → eigene leichte UI) |
| OpenAI-API | ja, :8080 | ja |
| Kiwix integriert | nein, nachrüsten | nein, nachrüsten |
| RAG integriert | nein, nachrüsten | nein, nachrüsten |
| Kontrolle / Härtung | eingeschränkt (fremdes Image) | vollständig |
| Wartbarkeit in 5 Jahren | abhängig vom Projekt | abhängig von dir |

**Vorschlag:** Phase 1–2 mit **Potato OS** (schnell sehen, ob es trägt), dann
entscheiden, ob Kiwix + RAG **auf** Potato OS aufgesetzt werden (Debian-Basis,
sollte gehen) oder ob Phase 4–6 auf ein eigenes Pi-OS-Image wechseln. Für die
Weitergabe (Phase 6) ist ein eigenes Image vermutlich sauberer.

## Komponenten

### Betriebssystem
- Raspberry Pi OS Lite 64-bit (Debian 13 "Trixie"), ohne Desktop
- Boot von NVMe (Bootloader-Reihenfolge per `rpi-eeprom-config`)
- PCIe Gen 3 aktivieren (`dtparam=pciex1_gen=3`) — inoffiziell, aber verbreitet;
  bei Instabilität zurück auf Gen 2
- Read-only-Root mit Overlay-FS ab Phase 5 (Schutz gegen Stromabriss)
- mDNS: `quintessenz.local` via avahi
- WLAN-Hotspot-Modus (hostapd/NetworkManager), falls kein Router vorhanden:
  Handy verbindet sich direkt mit der Box

### Inferenz
- **llama.cpp** (`llama-server`), kompiliert mit ARM-NEON-Optimierungen
  → OpenAI-kompatible API auf :8080
- Modelle (aus AI-ARK `01_MODELS/minimal/`):

| Rolle | Modell | Größe | Warum |
|---|---|---|---|
| Hauptmodell | **Qwen3.5-2B** (Q4_K_M) | ~1,5 GB | Potato-Standard, ~8 tok/s, Vision-Encoder |
| Alternative | Gemma 4 E2B (Q4) | ~3 GB | Bild + Audio-Eingabe, 140 Sprachen |
| Größer, wenn RAM reicht | Gemma 4 E4B (Q4) | ~4,5 GB | Merkbar besseres Textverständnis |
| Notfall | Qwen3.5-0.8B | ~0,6 GB | Läuft, wenn sonst nichts läuft |
| Embedding | **Qwen3-Embedding-0.6B** (Q8) oder EmbeddingGemma-300M | 0,3–0,6 GB | Mehrsprachig, klein |
| Reranker | bge-reranker-v2-m3 | ~1,2 GB | Optional; auf dem Pi ~2 s pro Frage extra — messen |

Qwen3-30B-A3B mit SSD-Offload: als Experiment interessant, für die Box
ungeeignet — SSD-Verschleiß, Ladezeiten, Speicherdruck. Nicht einplanen.

### Wissensbasis-Server
- **kiwix-serve** auf :8888, alle ZIMs aus einem Verzeichnis (`--library`)
- Volltextsuche ist in Kiwix eingebaut (Xapian-Index in der ZIM)
- **Karten:** PMTiles einer OSM-Region + kleiner Tile-Server (`pmtiles serve`
  oder `martin`), Frontend MapLibre GL — komplett offline

### RAG-Dienst (Eigenentwicklung, Python)

```
┌─────────────────────────────────────────────────────────┐
│ Indexierung (einmalig, läuft nachts)                    │
│  ZIM → libzim → Artikel → Chunks (800 Token, 150 Überl.)│
│  PDF → pymupdf → Text → Chunks                          │
│  Chunk → Embedding → Vektor-DB (+ Quelle, Titel, URL)   │
├─────────────────────────────────────────────────────────┤
│ Abfrage (pro Frage)                                     │
│  Frage → Embedding → Top-20 aus Vektor-DB               │
│  → optional Reranker → Top-5                            │
│  → Prompt: "Antworte NUR aus diesen Abschnitten,        │
│     nenne die Nummer der Quelle, sonst: 'nicht in der   │
│     Wissensbasis'" → LLM                                │
│  → Antwort + klickbare Quellen (→ kiwix-serve-URL)      │
└─────────────────────────────────────────────────────────┘
```

**Vektor-Datenbank — Wahl für den Pi:**

| Option | Für | Gegen |
|---|---|---|
| **sqlite-vec** | Eine Datei, kein Dienst, winzig, ARM-fähig | Jung, weniger Tooling |
| ChromaDB | Einfach, Python-nativ | Speicherhungrig bei >1 M Chunks |
| Qdrant | Schnell, robust, in NOMAD bewährt | Eigener Dienst, Rust-Binary, mehr RAM |
| LanceDB | Datei-basiert, schnell | Weniger verbreitet |

**Vorschlag: sqlite-vec.** Passt zum Grundsatz "alles muss ohne die Box lesbar
bleiben" — der Index ist eine SQLite-Datei. Bei Skalierungsproblemen → Qdrant.

**Größenabschätzung Index:** Wikipedia DE ≈ 2,9 M Artikel ≈ 15–20 M Chunks.
Bei 1024-dim float16 ≈ 2 KB je Chunk → **30–40 GB Index**. Machbar, aber die
Indexierung auf dem Pi dauert **Tage**. → Auf dem PC indexieren (AI-ARK-Rechner,
GPU), fertigen Index auf die SSD kopieren. Das gehört in den Phasenplan.

Alternative für Wikipedia: **Kiwix-Volltextsuche als Retriever nutzen** (BM25
statt Embedding) und nur die Fach-PDFs und kleinen ZIMs semantisch indexieren.
Hybrid — vermutlich der pragmatische Weg. → 05_OFFENE-FRAGEN.md, Frage 5.

### Oberfläche
- Eine HTML-Seite, kein Framework-Build: Eingabefeld, Antwort, Quellenliste,
  Link "Im Artikel lesen" → kiwix-serve
- Läuft auf dem Handy im Querformat und auf einem 7"-Display
- Kein Login. Die Box ist das Vertrauensgebiet.
- Zusätzlich: Direktlinks zu Kiwix-Suche und Karte für die, die lieber selbst suchen

### Betrieb & Härtung (Phase 5)
- systemd-Units für llama-server, kiwix-serve, rag, tiles — mit `Restart=always`
- Hardware-Watchdog (`bcm2835_wdt`) aktivieren
- Log nach RAM (`journald` volatile), SSD schonen
- Temperatur-/Throttling-Überwachung (`vcgencmd get_throttled`) in der UI anzeigen
- Backup-Skript: `rsync` der Wissensbasis + Index auf externe SSD, mit Prüfsummen
- Image bauen: `rpi-image-gen` oder `pi-gen` für reproduzierbares `Quintessenz.img.xz`

## Was aus Project NOMAD übernommen werden kann

NOMAD (x86, Docker, Ryzen 7 / 32 GB Minimum) ist zu schwer für den Pi, aber die
**Architektur** ist genau richtig: Kiwix + Kolibri + Ollama + Qdrant + Upload-UI.
Übernehmen: Aufteilung der Dienste, Ideen der Oberfläche, die Liste der
Wissensquellen. Nicht übernehmen: Docker (Overhead auf Pi), Qdrant (RAM), Kolibri
(riesig — nur, wenn Bildungsinhalte Priorität bekommen).
