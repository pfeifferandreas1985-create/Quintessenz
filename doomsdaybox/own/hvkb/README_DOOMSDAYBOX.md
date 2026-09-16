# hvkb in der DoomsdayBox — Einbindung

Stand 2026-09-16. Die Pipeline (`01_ingest.py`, `02_index.py`, `03_ask.py`, `config.py`) ist
unverändert aus dem Chat übernommen; dieses Blatt beschreibt nur, wie sie **offline mit dem
vorhandenen Archiv** läuft. Originalanleitung: `README.md`, Bibliografie und Rechtliches: `QUELLEN.md`.

## Wo was liegt

```
D:\DoomsdayBox\own\hvkb\          diese Pipeline (Skripte, Katalog, Doku)
   data\raw\                      HIER eigene Scan-PDFs ablegen (ein PDF je Buch, 400 dpi Graustufen)
   data\raw\quellen_online\       frei zugängliche Quellen (Hochschulskripte, Kronjaeger-Begleitseite) — vorbelegt
   data\text\ pages\ kb.sqlite vectors.npy   entstehen beim Lauf
D:\AI-ARK\00_RUNTIME\ollama\      Ollama-Installer (Windows/Linux/macOS)
D:\AI-ARK\01_MODELS\              Modelle als GGUF — kein `ollama pull` nötig
D:\AI-ARK\02_META\modelfiles\     fertige Modelfiles zum Einbinden
```

## Modelle ohne Internet einbinden

Statt `ollama pull bge-m3` / `qwen3:8b` (Netz nötig) die Archiv-Modelle registrieren:

```powershell
ollama create qwen3-embedding-0.6b -f D:\AI-ARK\02_META\modelfiles\Qwen3-Embedding-0.6B.Modelfile
ollama create qwen3.5-9b           -f D:\AI-ARK\02_META\modelfiles\Qwen3.5-9B.Modelfile
```

Dann in `config.py`:

```python
EMBED_MODEL = "qwen3-embedding-0.6b"   # 1024 Dimensionen, wie bge-m3 -> EMBED_DIM bleibt 1024
CHAT_MODEL  = "qwen3.5-9b"
```

Auf dem Ryzen-Rechner (RTX 3060) statt 9B besser `gemma-4-26B-A4B-it-qat` oder `Qwen3.5-35B-A3B`
(Modelfiles liegen bei) — deutlich stärkere Antworten bei gleicher Geschwindigkeit.

## Werkzeuge

- Python-Pakete: `pip install pypdfium2 numpy requests` (auf diesem Rechner installiert;
  für den Pi liegen Wheels in `D:\DoomsdayBox\src\wheels\`, pypdfium2 dort nachlegen)
- **Tesseract OCR** mit Sprachpaket `deu`: Installer siehe `D:\AI-ARK\00_RUNTIME\tools\`
  (falls vorhanden) oder `winget install UB-Mannheim.TesseractOCR`. Pfad in `config.py` eintragen:
  `TESSERACT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"`. Nur nötig für Scans ohne Textebene;
  digitale PDFs (Hochschulskripte) brauchen kein OCR.

## Ablauf

```powershell
cd D:\DoomsdayBox\own\hvkb
python 01_ingest.py            # liest data\raw\**  (auch quellen_online)
python 02_index.py             # BM25 + Embeddings (Ollama muss laufen)
python 03_ask.py "Wie dimensioniert man die Ladewiderstände im Marx-Generator?"
```

Hinweis: `01_ingest.py` liest nur `data\raw\*.pdf` (keine Unterordner). Entweder die Online-Quellen
direkt nach `data\raw\` legen oder in `config.py` `RAW.glob("*.pdf")` durch `RAW.rglob("*.pdf")`
ersetzen (eine Zeile in `01_ingest.py`, `main()`).

## Bewusst nicht enthalten

Die Minispione-Bände (Wahl) — siehe `QUELLEN.md`, Abschnitt „hier steige ich aus" (§ 90 TKG).
EMP-Kapitel nur als Lesestoff (§ 148 TKG). Eigene Scans sind Privatkopien nach § 53 UrhG:
nicht weitergeben, nicht auf Firmen-Shares.

## Bezug zur Box

Für das QUINTESSENZ-Terminal ist `kb.sqlite` (FTS5) + `vectors.npy` direkt nutzbar — gleiches
Schema-Prinzip wie der geplante Ingest (SQLite-Volltext + Vektoren, Seitenbild je Treffer).
Bereich in der Wissensübersicht: 2.1 Elektrotechnik (Hochspannung) bzw. eigener Unterpunkt.
