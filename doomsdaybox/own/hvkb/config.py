# -*- coding: utf-8 -*-
"""Zentrale Konfiguration der Wissensdatenbank."""
from pathlib import Path

# --- Verzeichnisse ----------------------------------------------------------
ROOT      = Path(__file__).resolve().parent
DATA      = ROOT / "data"
RAW       = DATA / "raw"        # Original-Scans / heruntergeladene PDFs
PAGES     = DATA / "pages"      # Seitenbilder (PNG) fuer den Blick aufs Original
TEXT      = DATA / "text"       # Seitentexte als JSON
DB_PATH   = DATA / "kb.sqlite"  # Metadaten + Volltextindex (FTS5)
VEC_PATH  = DATA / "vectors.npy"  # Embedding-Matrix, Zeilenindex == chunks.vec_row
CATALOG   = ROOT / "catalog.csv"  # Dateiname -> bibliografische Metadaten

# --- OCR --------------------------------------------------------------------
TESSERACT   = "tesseract"   # unter Windows ggf. absoluter Pfad, s. README
OCR_LANG    = "deu"
OCR_DPI     = 300           # Aufloesung fuer die Texterkennung
VIEW_DPI    = 150           # Aufloesung der abgelegten Seitenbilder
# Wenn die PDF-Seite bereits mehr als so viele Zeichen Textebene hat,
# wird nicht OCR-t, sondern die vorhandene Textebene benutzt.
TEXTLAYER_MIN_CHARS = 200

# --- Chunking ---------------------------------------------------------------
CHUNK_CHARS   = 1200
CHUNK_OVERLAP = 200
# Seiten mit weniger Zeichen werden mit der Folgeseite zusammengefasst
SHORT_PAGE_CHARS = 400

# --- Ollama -----------------------------------------------------------------
OLLAMA_URL   = "http://localhost:11434"
EMBED_MODEL  = "bge-m3"          # mehrsprachig, gut auf Deutsch, 1024 Dim
CHAT_MODEL   = "qwen3:8b"        # mit `ollama list` pruefen und ggf. anpassen
EMBED_DIM    = 1024
EMBED_BATCH  = 16

# --- Retrieval --------------------------------------------------------------
TOP_K_VECTOR = 40   # Kandidaten aus der semantischen Suche
TOP_K_FTS    = 40   # Kandidaten aus der Stichwortsuche (BM25)
RRF_K        = 60   # Daempfung der Reciprocal-Rank-Fusion
TOP_K_FINAL  = 8    # so viele Chunks gehen in den Prompt

for _d in (RAW, PAGES, TEXT):
    _d.mkdir(parents=True, exist_ok=True)
