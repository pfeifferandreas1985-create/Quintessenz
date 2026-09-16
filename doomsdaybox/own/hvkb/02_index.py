# -*- coding: utf-8 -*-
"""Schritt 2: Seitentexte -> Chunks -> Embeddings -> SQLite(FTS5) + vectors.npy

Aufruf:
    python 02_index.py            # Index komplett neu aufbauen
    python 02_index.py --no-embed # nur Volltextindex (BM25), ohne Ollama
"""
import argparse
import csv
import json
import sqlite3
import sys

import numpy as np
import requests

import config as cfg

SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS docs(
    doc_id TEXT PRIMARY KEY, title TEXT, author TEXT,
    year TEXT, isbn TEXT, file TEXT, n_pages INTEGER);
CREATE TABLE IF NOT EXISTS chunks(
    chunk_id INTEGER PRIMARY KEY,
    doc_id TEXT NOT NULL, page_start INTEGER, page_end INTEGER,
    text TEXT NOT NULL, vec_row INTEGER);
CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
    text, content='chunks', content_rowid='chunk_id',
    tokenize="unicode61 remove_diacritics 2");
"""


# --------------------------------------------------------------------------- #
def load_catalog() -> dict:
    """catalog.csv: doc_id,title,author,year,isbn  (optional)"""
    meta = {}
    if cfg.CATALOG.exists():
        with cfg.CATALOG.open(encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                if row.get("doc_id"):
                    meta[row["doc_id"].strip()] = row
    return meta


def split_page(text: str) -> list:
    """Absatzweise in ~CHUNK_CHARS grosse Stuecke mit Ueberlappung teilen."""
    text = text.strip()
    if not text:
        return []
    if len(text) <= cfg.CHUNK_CHARS:
        return [text]

    parts, buf = [], ""
    for para in text.split("\n\n"):
        if len(buf) + len(para) + 2 <= cfg.CHUNK_CHARS:
            buf = f"{buf}\n\n{para}" if buf else para
        else:
            if buf:
                parts.append(buf)
            # Absatz selbst zu gross -> hart schneiden
            while len(para) > cfg.CHUNK_CHARS:
                cut = para.rfind(" ", 0, cfg.CHUNK_CHARS)
                cut = cut if cut > cfg.CHUNK_CHARS // 2 else cfg.CHUNK_CHARS
                parts.append(para[:cut])
                para = para[max(0, cut - cfg.CHUNK_OVERLAP):]
            buf = para
    if buf:
        parts.append(buf)

    # Ueberlappung zwischen den Stuecken herstellen
    out = []
    for i, p in enumerate(parts):
        if i and cfg.CHUNK_OVERLAP:
            p = parts[i - 1][-cfg.CHUNK_OVERLAP:] + " " + p
        out.append(p.strip())
    return out


def build_chunks() -> list:
    """Alle Seiten-JSONs zu Chunks verarbeiten; kurze Seiten werden verschmolzen."""
    chunks = []
    for jf in sorted(cfg.TEXT.glob("*.json")):
        doc = json.loads(jf.read_text(encoding="utf-8"))
        did = doc["doc_id"]
        carry, carry_start = "", None
        for pg in doc["pages"]:
            txt = (carry + "\n\n" + pg["text"]).strip() if carry else pg["text"].strip()
            start = carry_start if carry_start else pg["page"]
            if len(txt) < cfg.SHORT_PAGE_CHARS:
                carry, carry_start = txt, start   # mit naechster Seite zusammenlegen
                continue
            for c in split_page(txt):
                chunks.append({"doc_id": did, "page_start": start,
                               "page_end": pg["page"], "text": c})
            carry, carry_start = "", None
        if carry.strip():
            for c in split_page(carry):
                chunks.append({"doc_id": did, "page_start": carry_start,
                               "page_end": doc["n_pages"], "text": c})
    return chunks


def embed(texts: list) -> np.ndarray:
    """Embeddings ueber die lokale Ollama-Instanz, L2-normalisiert."""
    vecs = []
    for i in range(0, len(texts), cfg.EMBED_BATCH):
        batch = texts[i:i + cfg.EMBED_BATCH]
        try:
            r = requests.post(f"{cfg.OLLAMA_URL}/api/embed",
                              json={"model": cfg.EMBED_MODEL, "input": batch},
                              timeout=600)
            r.raise_for_status()
        except requests.RequestException as e:
            sys.exit(f"Ollama nicht erreichbar ({e}). Laeuft `ollama serve` und "
                     f"ist `ollama pull {cfg.EMBED_MODEL}` erfolgt?")
        vecs.extend(r.json()["embeddings"])
        print(f"    eingebettet {min(i + cfg.EMBED_BATCH, len(texts))}/{len(texts)}",
              end="\r", flush=True)
    print()
    a = np.asarray(vecs, dtype=np.float32)
    a /= np.linalg.norm(a, axis=1, keepdims=True) + 1e-12
    return a


# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-embed", action="store_true",
                    help="nur Stichwortindex aufbauen (ohne Ollama)")
    args = ap.parse_args()

    chunks = build_chunks()
    if not chunks:
        sys.exit("Keine Chunks gefunden - erst 01_ingest.py laufen lassen.")
    print(f"{len(chunks)} Chunks aus {len(list(cfg.TEXT.glob('*.json')))} Dokument(en)")

    if cfg.DB_PATH.exists():
        cfg.DB_PATH.unlink()
    for suf in ("-wal", "-shm"):
        p = cfg.DB_PATH.with_name(cfg.DB_PATH.name + suf)
        if p.exists():
            p.unlink()

    con = sqlite3.connect(cfg.DB_PATH)
    con.executescript(SCHEMA)

    meta = load_catalog()
    for jf in sorted(cfg.TEXT.glob("*.json")):
        d = json.loads(jf.read_text(encoding="utf-8"))
        m = meta.get(d["doc_id"], {})
        con.execute("INSERT OR REPLACE INTO docs VALUES (?,?,?,?,?,?,?)",
                    (d["doc_id"], m.get("title") or d["doc_id"], m.get("author", ""),
                     m.get("year", ""), m.get("isbn", ""), d["file"], d["n_pages"]))

    rows = [(i + 1, c["doc_id"], c["page_start"], c["page_end"], c["text"], i)
            for i, c in enumerate(chunks)]
    con.executemany("INSERT INTO chunks VALUES (?,?,?,?,?,?)", rows)
    con.execute("INSERT INTO chunks_fts(chunks_fts) VALUES('rebuild')")
    con.commit()
    print(f"Volltextindex (BM25) aufgebaut -> {cfg.DB_PATH.name}")

    if args.no_embed:
        print("Embeddings uebersprungen (--no-embed). Semantische Suche steht noch nicht.")
    else:
        print(f"Embeddings mit '{cfg.EMBED_MODEL}' ...")
        vecs = embed([c["text"] for c in chunks])
        np.save(cfg.VEC_PATH, vecs)
        print(f"Vektoren gespeichert -> {cfg.VEC_PATH.name}  {vecs.shape}")

    con.close()
    print("Index fertig. Weiter mit: python 03_ask.py \"Ihre Frage\"")


if __name__ == "__main__":
    main()
