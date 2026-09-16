# Wissensdatenbank Hochspannungs- und HF-Technik

Lokales RAG über eigene Buchscans und offene Online-Quellen. Läuft vollständig
offline auf dem Rechner — keine Cloud, keine Uploads.

## Architektur

```
PDF (Scan oder digital)
   │  01_ingest.py    pypdfium2 rendert Seiten, Tesseract erkennt Text
   ▼                  (digitale PDFs: vorhandene Textebene wird genutzt)
data/text/*.json      Seitentext          data/pages/<doc>/0001.png   Seitenbild
   │  02_index.py     Chunking (seitentreu) → Embeddings über Ollama
   ▼
data/kb.sqlite        Metadaten + FTS5-Volltextindex (BM25)
data/vectors.npy      Embedding-Matrix, float32, L2-normalisiert
   │  03_ask.py       Hybride Suche: BM25 + Kosinus, fusioniert per RRF
   ▼                  → lokales LLM formuliert Antwort mit Seitenangabe
Antwort + [Kurztitel, S. N] + Original-Seitenbild auf Wunsch
```

**Warum kein Vektor-DBMS.** Bei ~10 Büchern entstehen grob 4.000–8.000 Chunks.
Eine Matrixmultiplikation über 8.000 × 1024 float32 (32 MB) dauert unter 20 ms.
Ein Vektorindex (LanceDB, Chroma, Qdrant) bringt in dieser Größenordnung keinen
messbaren Vorteil, kostet aber eine Abhängigkeit, die auf gesperrten
Firmenrechnern gern scheitert. SQLite und NumPy reichen bis etwa 200.000 Chunks.

**Warum hybrid.** Rein semantische Suche verfehlt exakte Fachbegriffe und
Bauteilbezeichnungen ("Greinacher-Kaskade", "BU508", "1N4007"). BM25 findet die,
versagt aber bei Umschreibungen. Reciprocal Rank Fusion kombiniert beide, ohne
dass Scores kalibriert werden müssen.

## Installation (Windows 11)

```powershell
winget install UB-Mannheim.TesseractOCR
winget install Ollama.Ollama
```

Deutsches Sprachpaket für Tesseract: im Installer unter *Additional language
data* → **German** mitauswählen. Nachträglich prüfen mit:

```powershell
tesseract --list-langs     # muss "deu" enthalten
```

Findet Python `tesseract` nicht, in `config.py` den absoluten Pfad eintragen:
`TESSERACT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"`

Modelle und Python-Pakete:

```powershell
ollama pull bge-m3          # Embeddings, ~1,2 GB
ollama pull qwen3:8b        # Antwortmodell, ~5 GB — mit `ollama list` prüfen
pip install pypdfium2 numpy requests
```

Ohne dedizierte GPU laufen 8B-Modelle bei etwa 4–8 Token/s. Das ist für
Rückfragen brauchbar, aber spürbar zäh. Alternativen: `qwen3:4b` (schneller,
schwächer) oder die Antwortgenerierung weglassen und mit `--quellen` arbeiten —
die Fundstellen sind ohnehin der eigentliche Nutzen.

## Ablauf

```powershell
# 1. Scans nach data\raw\ legen (ein PDF je Buch)
python 01_ingest.py                    # OCR, dauert ~1-2 s je Seite
python 02_index.py                     # Index bauen
python 03_ask.py "Wie dimensioniert man die Ladewiderstände im Marx-Generator?"
```

Weitere Aufrufe:

| Befehl | Wirkung |
|---|---|
| `python 01_ingest.py --force` | alles neu einlesen |
| `python 02_index.py --no-embed` | nur BM25, ohne Ollama |
| `python 03_ask.py --quellen "..."` | nur Fundstellen, kein LLM |
| `python 03_ask.py --oeffnen "..."` | beste Originalseite im Bildbetrachter öffnen |
| `python 03_ask.py -k 15 "..."` | mehr Fundstellen berücksichtigen |

`catalog.csv` ordnet jeder `doc_id` (= bereinigter Dateiname) Titel, Autor, Jahr
und ISBN zu. Ohne Eintrag erscheint die `doc_id` als Titel.

## Scan-Workflow

Gebrauchte Franzis-Bände kosten antiquarisch meist 5–20 €. Die schnellste
Methode: zweites Exemplar kaufen, Buchrücken beim Copyshop abschneiden lassen,
durch den Einzugsscanner ziehen.

- **400 dpi, Graustufen** — 300 dpi reicht für Fließtext, aber nicht für
  Bauteilbeschriftungen in Schaltplänen.
- **Nicht entrastern, nicht schärfen.** Beides zerstört feine Linien in
  Schaltplänen.
- Ausgabe als **PDF ohne Kompression oder mit verlustarmem JPEG (Qualität ≥ 85)**.
  Aggressive Kompression frisst dünne Leiterbahnen.
- Kein Duplex-Versatz: Vorder- und Rückseite müssen dieselbe Seitenzahl-Reihenfolge
  behalten, sonst stimmen die Seitenverweise nicht.

## Bekannte Grenze

Der Kern dieser Bücher sind **Schaltpläne, Wickeldaten und Bauteiltabellen**.
Schaltpläne sind Bilder — OCR liefert dort bestenfalls verstreute Bauteilnummern,
oft gar nichts. Das System findet deshalb zuverlässig *die richtige Seite* und
den umgebenden Fließtext, kann aber Schaltungen nicht "lesen". Genau darum wird
jedes Seitenbild abgelegt und `--oeffnen` mitgeliefert: die Antwort verweist,
das Auge liest.

Wer das ändern will, braucht ein Vision-Modell über die Seitenbilder
(z. B. `ollama pull qwen2.5vl:7b`) und einen zusätzlichen Schritt, der je Seite
eine Bildbeschreibung erzeugt und mitindiziert. Das kostet viel Rechenzeit und
liefert bei Schaltplänen erfahrungsgemäß mäßige Ergebnisse — erst sinnvoll, wenn
die Textsuche steht und sich als unzureichend erweist.
