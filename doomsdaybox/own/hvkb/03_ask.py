# -*- coding: utf-8 -*-
"""Schritt 3: Frage stellen. Hybride Suche (BM25 + Vektor, RRF) -> lokales LLM.

Aufruf:
    python 03_ask.py "Wie dimensioniert man den Stosskondensator im Marx-Generator?"
    python 03_ask.py --quellen "Loeschfunkenstrecke"   # nur Fundstellen, kein LLM
    python 03_ask.py --oeffnen "Marx-Generator"        # beste Originalseite anzeigen
"""
import argparse
import os
import re
import sqlite3
import subprocess
import sys

import numpy as np
import requests

import config as cfg

SYSTEM = (
    "Du bist ein praeziser technischer Assistent fuer Hochspannungs- und "
    "Hochfrequenztechnik. Antworte ausschliesslich auf Basis der bereitgestellten "
    "Auszuege. Nenne hinter jeder Aussage die Fundstelle im Format [Kurztitel, S. N]. "
    "Wenn die Auszuege die Frage nicht abdecken, sage das klar und rate nicht. "
    "Schaltplaene und Bauteilwerte stehen oft als Abbildung im Buch und nicht im "
    "erkannten Text - weise in dem Fall auf die Seite hin, statt Werte zu erfinden. "
    "Antworte auf Deutsch."
)


# --------------------------------------------------------------------------- #
def fts_query(con, q: str, k: int) -> list:
    """BM25-Suche. Anfrage wird zu einer ODER-Verknuepfung der Terme entschaerft."""
    terms = [t for t in re.findall(r"\w{3,}", q, flags=re.UNICODE)]
    if not terms:
        return []
    match = " OR ".join(f'"{t}"' for t in terms)
    try:
        cur = con.execute(
            "SELECT c.chunk_id FROM chunks_fts f JOIN chunks c ON c.chunk_id=f.rowid "
            "WHERE chunks_fts MATCH ? ORDER BY bm25(chunks_fts) LIMIT ?", (match, k))
        return [r[0] for r in cur.fetchall()]
    except sqlite3.OperationalError:
        return []


def vector_query(q: str, k: int) -> list:
    if not cfg.VEC_PATH.exists():
        return []
    try:
        r = requests.post(f"{cfg.OLLAMA_URL}/api/embed",
                          json={"model": cfg.EMBED_MODEL, "input": [q]}, timeout=120)
        r.raise_for_status()
    except requests.RequestException:
        print("  (Hinweis: Ollama nicht erreichbar - nur Stichwortsuche)", file=sys.stderr)
        return []
    qv = np.asarray(r.json()["embeddings"][0], dtype=np.float32)
    qv /= np.linalg.norm(qv) + 1e-12
    mat = np.load(cfg.VEC_PATH, mmap_mode="r")
    sims = np.asarray(mat) @ qv
    top = np.argsort(-sims)[:k]
    return [int(i) + 1 for i in top]      # vec_row -> chunk_id (1-basiert)


def rrf(*ranked_lists) -> list:
    """Reciprocal Rank Fusion ueber mehrere Trefferlisten."""
    score = {}
    for lst in ranked_lists:
        for rank, cid in enumerate(lst):
            score[cid] = score.get(cid, 0.0) + 1.0 / (cfg.RRF_K + rank + 1)
    return sorted(score, key=score.get, reverse=True)


def fetch(con, chunk_ids: list) -> list:
    if not chunk_ids:
        return []
    qs = ",".join("?" * len(chunk_ids))
    cur = con.execute(
        f"SELECT c.chunk_id, d.title, d.doc_id, c.page_start, c.page_end, c.text "
        f"FROM chunks c JOIN docs d ON d.doc_id=c.doc_id WHERE c.chunk_id IN ({qs})",
        chunk_ids)
    by_id = {r[0]: r for r in cur.fetchall()}
    return [by_id[i] for i in chunk_ids if i in by_id]


def short(title: str) -> str:
    return (title[:40] + "...") if len(title) > 43 else title


def page_ref(row) -> str:
    _, title, _, ps, pe, _ = row
    seite = f"S. {ps}" if ps == pe else f"S. {ps}-{pe}"
    return f"[{short(title)}, {seite}]"


def ask_llm(question: str, rows: list) -> str:
    ctx = "\n\n".join(f"--- {page_ref(r)} ---\n{r[5]}" for r in rows)
    try:
        r = requests.post(
            f"{cfg.OLLAMA_URL}/api/chat",
            json={"model": cfg.CHAT_MODEL, "stream": False,
                  "options": {"temperature": 0.2},
                  "messages": [
                      {"role": "system", "content": SYSTEM},
                      {"role": "user",
                       "content": f"Auszuege:\n\n{ctx}\n\nFrage: {question}"}]},
            timeout=900)
        r.raise_for_status()
    except requests.RequestException as e:
        return f"(LLM nicht erreichbar: {e})"
    return r.json()["message"]["content"]


def open_page(row) -> None:
    _, _, did, ps, _, _ = row
    png = cfg.PAGES / did / f"{ps:04d}.png"
    if not png.exists():
        print(f"  Seitenbild fehlt: {png}")
        return
    print(f"  oeffne {png}")
    if sys.platform.startswith("win"):
        os.startfile(png)                                   # noqa: S606
    else:
        subprocess.run(["xdg-open", str(png)], check=False)


# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("frage", help="Ihre Frage bzw. Suchbegriff")
    ap.add_argument("--quellen", action="store_true", help="nur Fundstellen, kein LLM")
    ap.add_argument("--oeffnen", action="store_true", help="beste Originalseite oeffnen")
    ap.add_argument("-k", type=int, default=cfg.TOP_K_FINAL, help="Anzahl Fundstellen")
    args = ap.parse_args()

    if not cfg.DB_PATH.exists():
        sys.exit("Kein Index vorhanden - erst 01_ingest.py und 02_index.py laufen lassen.")
    con = sqlite3.connect(cfg.DB_PATH)

    ids = rrf(vector_query(args.frage, cfg.TOP_K_VECTOR),
              fts_query(con, args.frage, cfg.TOP_K_FTS))[:args.k]
    rows = fetch(con, ids)
    if not rows:
        sys.exit("Keine Treffer.")

    print(f"\n{len(rows)} Fundstellen:")
    for r in rows:
        print(f"  {page_ref(r)}  {r[5][:110].replace(chr(10), ' ')}...")

    if args.oeffnen:
        open_page(rows[0])

    if not args.quellen:
        print("\n--- Antwort -------------------------------------------------")
        print(ask_llm(args.frage, rows))
    con.close()


if __name__ == "__main__":
    main()
