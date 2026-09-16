# -*- coding: utf-8 -*-
"""Schritt 1: PDF -> Seitentext (Textebene oder OCR) + Seitenbild.

Aufruf:
    python 01_ingest.py                 # alle neuen PDFs in data/raw
    python 01_ingest.py --force         # alles neu einlesen
    python 01_ingest.py datei.pdf       # nur eine Datei
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pypdfium2 as pdfium

import config as cfg


def doc_id_from(path: Path) -> str:
    """Stabile, dateisystemtaugliche ID aus dem Dateinamen."""
    s = re.sub(r"[^A-Za-z0-9]+", "_", path.stem).strip("_").lower()
    return s or "doc"


def ocr_image(png_path: Path) -> str:
    """Tesseract auf ein Seitenbild anwenden."""
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "out"
        try:
            subprocess.run(
                [cfg.TESSERACT, str(png_path), str(out),
                 "-l", cfg.OCR_LANG, "--psm", "3"],
                check=True, capture_output=True,
            )
        except FileNotFoundError:
            sys.exit(f"Tesseract nicht gefunden unter '{cfg.TESSERACT}'. "
                     f"Pfad in config.py anpassen.")
        except subprocess.CalledProcessError as e:
            print(f"    ! OCR-Fehler: {e.stderr.decode('utf-8', 'replace')[:200]}")
            return ""
        txt = out.with_suffix(".txt")
        return txt.read_text(encoding="utf-8", errors="replace") if txt.exists() else ""


def clean(text: str) -> str:
    """Typische OCR-Artefakte deutscher Fachbuch-Scans entschaerfen."""
    # Am Zeilenende getrennte Woerter wieder zusammenziehen
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    # Einzelne Zeilenumbrueche innerhalb eines Absatzes zu Leerzeichen
    text = re.sub(r"(?<![\n.:;!?])\n(?![\n\s•\-–])", " ", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def ingest_pdf(pdf_path: Path, force: bool = False) -> None:
    did = doc_id_from(pdf_path)
    out_json = cfg.TEXT / f"{did}.json"
    if out_json.exists() and not force:
        print(f"  uebersprungen (bereits eingelesen): {pdf_path.name}")
        return

    page_dir = cfg.PAGES / did
    page_dir.mkdir(parents=True, exist_ok=True)

    pdf = pdfium.PdfDocument(str(pdf_path))
    n = len(pdf)
    print(f"  {pdf_path.name}: {n} Seiten")

    pages, n_ocr = [], 0
    for i in range(n):
        page = pdf[i]

        # 1) Vorhandene Textebene bevorzugen (digitale PDFs, z.B. Uni-Skripte)
        raw = page.get_textpage().get_text_range() or ""
        source = "textlayer"

        # 2) Seitenbild fuer die Anzeige immer erzeugen
        view_png = page_dir / f"{i + 1:04d}.png"
        if not view_png.exists() or force:
            page.render(scale=cfg.VIEW_DPI / 72).to_pil().save(view_png)

        # 3) Bei zu wenig Text: OCR auf hoeher aufgeloestem Rendering
        if len(raw.strip()) < cfg.TEXTLAYER_MIN_CHARS:
            with tempfile.TemporaryDirectory() as td:
                big = Path(td) / "page.png"
                page.render(scale=cfg.OCR_DPI / 72).to_pil().save(big)
                raw = ocr_image(big)
            source = "ocr"
            n_ocr += 1

        pages.append({"page": i + 1, "source": source, "text": clean(raw)})
        if (i + 1) % 25 == 0:
            print(f"    ... Seite {i + 1}/{n}")

    pdf.close()
    out_json.write_text(
        json.dumps({"doc_id": did, "file": pdf_path.name,
                    "n_pages": n, "pages": pages},
                   ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    print(f"  fertig: {did}  ({n_ocr} Seiten per OCR, {n - n_ocr} aus Textebene)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", nargs="?", help="einzelne PDF-Datei (optional)")
    ap.add_argument("--force", action="store_true", help="bereits Eingelesenes neu verarbeiten")
    args = ap.parse_args()

    targets = [Path(args.pdf)] if args.pdf else sorted(cfg.RAW.glob("*.pdf"))
    if not targets:
        sys.exit(f"Keine PDFs in {cfg.RAW} gefunden.")
    print(f"{len(targets)} Datei(en) zu verarbeiten")
    for p in targets:
        ingest_pdf(p, force=args.force)


if __name__ == "__main__":
    main()
