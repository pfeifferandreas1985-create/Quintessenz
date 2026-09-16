#!/usr/bin/env python3
"""
fahrzeuge_abschluss.py - Phase F abschliessen: Stage -> D:, Manifeste, Bericht.

  python fahrzeuge_abschluss.py --stage C:/stage --root D:/DoomsdayBox

Kopiert aus <stage>/fahrzeuge/:
  defender/*.pdf, mini/*.pdf, vespa/*.pdf          -> <root>/pdf/fahrzeuge/<fahrzeug>/
  <fahrzeug>/forenwissen, gsf-wiki, landypedia, schaltplaene  -> <root>/own/fahrzeuge/<fahrzeug>_<quelle>/
(Explosionszeichnungen und Teilelisten-CSV hat fahrzeuge_fetch.py bereits direkt nach D: geschrieben.)
Schreibt MANIFEST.sha256 in pdf/fahrzeuge und own/fahrzeuge, ergaenzt LOGBUCH.md, erzeugt doku/BERICHT_Phase-F_Fahrzeuge.md.
"""
import argparse, csv, hashlib, re, shutil
from datetime import date
from pathlib import Path

HEUTE = date.today().isoformat()
KAUFEN = {
    "defender": ["Brooklands: Defender Workshop Manual TD5 (LRL0410/LRL0097) - Nachdruck, falls gedruckte Ausgabe gewuenscht",
                 "Brooklands: Defender Parts Catalogue 1987-2006 (STC9021CC) - gedruckt; digital durch Rimmer-Katalog gedeckt",
                 "Haynes 3017 Land Rover Defender Diesel 1983-2007"],
    "mini": ["Brooklands/Rover: Mini Workshop Manual 1992-2000 inkl. MPi (RCL0193) - Nachdruck, falls gedruckt gewuenscht",
             "Mini Parts Catalogue 1990-2000 (British Motor Heritage) - gedruckt; digital durch Minispares-Katalog gedeckt",
             "Haynes 0646 Mini 1969-2001"],
    "vespa": ["Bucheli Reparaturanleitung Vespa 50/90/125 Smallframe", "Vespa Technica Bd. Smallframe"],
}
NICHT_ERREICHBAR = [
    "lrcat.com - Zeitueberschreitung von diesem Anschluss (Land-Rover-Explosionszeichnungen stattdessen aus dem Rimmer-Teilekatalog 1983-2006)",
    "sip-scootershop.com - HTTP 403 fuer Skripte, Browser durch Organisationsrichtlinie gesperrt (Piaggio-Tafeln stattdessen von scooter-center.com)",
    "minimania.com - HTTP 522 (Server nicht erreichbar) am 16.09.2026, Tech-Artikel spaeter nachholen",
    "britpart.com - keine oeffentlichen Explosionszeichnungen im Katalog gefunden",
    "paddockspares.com - nur Produktlisten, keine Explosionszeichnungen",
]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(8 << 20), b""):
            h.update(b)
    return h.hexdigest()


def manifest(ordner):
    lines = []
    for f in sorted(Path(ordner).rglob("*")):
        if f.is_file() and f.name != "MANIFEST.sha256" and not f.name.endswith(".part"):
            lines.append(f"{sha(f)}  {f.relative_to(ordner).as_posix()}")
    (Path(ordner) / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(lines)


def kopiere(src, dst):
    n = 0
    if not Path(src).exists():
        return 0
    Path(dst).mkdir(parents=True, exist_ok=True)
    for f in Path(src).iterdir():
        if f.is_file() and f.suffix.lower() in (".pdf", ".md", ".csv"):
            z = Path(dst) / f.name
            if not z.exists() or z.stat().st_size != f.stat().st_size:
                shutil.copy2(f, z)
            n += 1
    return n


def groesse(ordner, muster="*.pdf"):
    fs = list(Path(ordner).rglob(muster)) if Path(ordner).exists() else []
    return len(fs), sum(f.stat().st_size for f in fs) / 1048576


def main(a):
    stage = Path(a.stage) / "fahrzeuge"
    root = Path(a.root)
    bericht = [f"# Bericht Phase F - Eigene Fahrzeuge\n\nStand {HEUTE}. Alle Dateien sind Privatkopien fuer den Eigengebrauch; "
               f"Quelle und Abrufdatum stehen in jedem PDF.\n"]
    for fz, name in (("defender", "Land Rover Defender 110 TD5 (1998-2006)"),
                     ("mini", "Rover Mini Cooper 1.3i MPi (1999)"),
                     ("vespa", "Vespa V50 N, V5A1T (1963)")):
        pdfziel = root / "pdf" / "fahrzeuge" / fz
        n1 = kopiere(stage / fz, pdfziel)
        zeilen = [f"\n## {name}\n", "| Bereich | Dateien | MB | Ablage |", "|---|---|---|---|"]
        n, mb = groesse(pdfziel, "*.pdf")
        ex_n, ex_mb = groesse(pdfziel / "explosionszeichnungen", "*.pdf")
        zeilen.append(f"| Handbuecher, Kataloge, Schaltplaene (PDF) | {n - ex_n} | {mb - ex_mb:.0f} | pdf/fahrzeuge/{fz}/ |")
        if ex_n:
            zeilen.append(f"| Explosionszeichnungen, einheitlich gesetzt | {ex_n} | {ex_mb:.0f} | pdf/fahrzeuge/{fz}/explosionszeichnungen/ |")
        for quelle in ("forenwissen", "gsf-wiki", "landypedia", "schaltplaene"):
            q = stage / fz / quelle
            if q.exists():
                dst = root / "own" / "fahrzeuge" / f"{fz}_{quelle}"
                kopiere(q, dst)
                qn, qmb = groesse(dst, "*.pdf")
                zeilen.append(f"| {quelle} (Artikel/Threads als PDF) | {qn} | {qmb:.0f} | own/fahrzeuge/{fz}_{quelle}/ |")
        for csvf in (root / "own" / "fahrzeuge").glob("*teileliste.csv"):
            if (fz == "mini" and "minispares" in csvf.name) or (fz == "vespa" and "scootercenter" in csvf.name):
                with open(csvf, encoding="utf-8") as f:
                    k = sum(1 for _ in f) - 1
                zeilen.append(f"| Teileliste (CSV, {k} Positionen) | 1 | {csvf.stat().st_size / 1048576:.1f} | own/fahrzeuge/{csvf.name} |")
        zeilen.append("\n**Kaufempfehlung (nicht geladen):**")
        zeilen += [f"- {k}" for k in KAUFEN[fz]]
        bericht += zeilen
    bericht += ["\n## Nicht erreichbar / offen\n"] + [f"- {x}" for x in NICHT_ERREICHBAR]
    bericht += ["\n## Werkzeuge\n", "- `tools/fahrzeuge_fetch.py` - Kataloge spiegeln (Minispares, Scooter Center), PDF je Kapitel/Modell + CSV",
                "- `tools/seiten_zu_pdf.py` - Wiki-Artikel (MediaWiki-API), Forenthreads, Fachseiten als PDF",
                "- `tools/fahrzeuge_abschluss.py` - dieses Skript: Stage -> D:, Manifeste, Bericht",
                "\nErneuter Lauf laedt nur Fehlendes nach (Cache unter C:/stage/fahrzeuge/_cache)."]
    (root / "doku").mkdir(exist_ok=True)
    (root / "doku" / "BERICHT_Phase-F_Fahrzeuge.md").write_text("\n".join(bericht) + "\n", encoding="utf-8")
    m1 = manifest(root / "pdf" / "fahrzeuge")
    m2 = manifest(root / "own" / "fahrzeuge")
    n_pdf, mb = groesse(root / "pdf" / "fahrzeuge")
    n_own, mb2 = groesse(root / "own" / "fahrzeuge")
    with open(root / "LOGBUCH.md", "a", encoding="utf-8") as f:
        f.write(f"| {HEUTE} | Phase F Fahrzeuge abgeschlossen | pdf/fahrzeuge: {n_pdf} PDFs ({mb:.0f} MB), own/fahrzeuge: {n_own} PDFs ({mb2:.0f} MB) + CSV/DB; "
                f"Manifeste {m1}+{m2} Eintraege; Bericht doku/BERICHT_Phase-F_Fahrzeuge.md |\n")
    print(f"pdf/fahrzeuge: {n_pdf} PDFs, {mb:.0f} MB | own/fahrzeuge: {n_own} PDFs, {mb2:.0f} MB | Manifeste: {m1} + {m2} | Bericht geschrieben")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", default="C:/stage")
    ap.add_argument("--root", default="D:/DoomsdayBox")
    main(ap.parse_args())
