"""Holt die Bildschirmschriften nach app/static/fonts/.

Alle vier Familien stehen unter der SIL Open Font License 1.1 und duerfen
mitgeliefert und weitergegeben werden. Sie werden ins Repo eingecheckt, damit
die Box ohne Internet startet - das ist der ganze Sinn der Uebung.

Quelle: github.com/google/fonts (Rohdateien ueber raw.githubusercontent.com).
Die TTF werden lokal nach woff2 gewandelt, wenn das Paket 'fonttools[woff]'
verfuegbar ist; sonst wird die TTF abgelegt und tokens.css nutzt sie direkt.

Aufruf:  python tools/fetch_fonts.py
         python tools/fetch_fonts.py --pruefen     (nur Bestand zeigen)
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import urllib.request
from pathlib import Path

ROH = "https://raw.githubusercontent.com/google/fonts/main"

# (Zielname ohne Endung, Pfad im google/fonts-Repo)
SCHRIFTEN = [
    # Jost und Libre Baskerville liegen bei Google Fonts nur noch als
    # Variable Font vor (eine Datei, Gewichtsachse). tokens.css deklariert
    # dafuer font-weight als Bereich.
    ("VT323-Regular",                    f"{ROH}/ofl/vt323/VT323-Regular.ttf"),
    ("Jost-Variable",                    f"{ROH}/ofl/jost/Jost%5Bwght%5D.ttf"),
    ("CourierPrime-Regular",             f"{ROH}/ofl/courierprime/CourierPrime-Regular.ttf"),
    ("CourierPrime-Bold",                f"{ROH}/ofl/courierprime/CourierPrime-Bold.ttf"),
    ("CourierPrime-Italic",              f"{ROH}/ofl/courierprime/CourierPrime-Italic.ttf"),
    ("LibreBaskerville-Variable",        f"{ROH}/ofl/librebaskerville/LibreBaskerville%5Bwght%5D.ttf"),
    ("LibreBaskerville-Italic-Variable", f"{ROH}/ofl/librebaskerville/LibreBaskerville-Italic%5Bwght%5D.ttf"),
]

LIZENZEN = [
    ("OFL-VT323.txt",            f"{ROH}/ofl/vt323/OFL.txt"),
    ("OFL-Jost.txt",             f"{ROH}/ofl/jost/OFL.txt"),
    ("OFL-CourierPrime.txt",     f"{ROH}/ofl/courierprime/OFL.txt"),
    ("OFL-LibreBaskerville.txt", f"{ROH}/ofl/librebaskerville/OFL.txt"),
]

ZIEL = Path(__file__).resolve().parent.parent / "app" / "static" / "fonts"


def laden(url: str) -> bytes:
    anfrage = urllib.request.Request(url, headers={"User-Agent": "quintessenz-fetch-fonts"})
    with urllib.request.urlopen(anfrage, timeout=60) as antwort:
        return antwort.read()


def nach_woff2(ttf: bytes, ziel: Path) -> bool:
    try:
        from fontTools.ttLib import TTFont
    except ImportError:
        return False
    import io
    f = TTFont(io.BytesIO(ttf))
    f.flavor = "woff2"
    try:
        f.save(ziel)
    except Exception as e:                      # brotli fehlt o. ae.
        print(f"    woff2 nicht moeglich ({e}); TTF wird abgelegt")
        return False
    return True


def bestand() -> None:
    if not ZIEL.is_dir():
        print(f"{ZIEL} fehlt")
        return
    dateien = sorted(ZIEL.glob("*"))
    if not dateien:
        print(f"{ZIEL} ist leer - System-Fallbacks greifen")
        return
    for f in dateien:
        print(f"  {f.name:34s} {f.stat().st_size/1024:8.1f} kB  "
              f"{hashlib.sha256(f.read_bytes()).hexdigest()[:16]}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pruefen", action="store_true", help="nur Bestand anzeigen")
    args = ap.parse_args()

    if args.pruefen:
        bestand()
        return 0

    ZIEL.mkdir(parents=True, exist_ok=True)
    fehler = 0

    for name, url in SCHRIFTEN:
        woff2 = ZIEL / f"{name}.woff2"
        if woff2.is_file():
            print(f"  {name}: schon da")
            continue
        print(f"  {name}: lade ...")
        try:
            roh = laden(url)
        except Exception as e:
            print(f"    FEHLER: {e}")
            fehler += 1
            continue
        if not nach_woff2(roh, woff2):
            (ZIEL / f"{name}.ttf").write_bytes(roh)
            print(f"    als TTF abgelegt ({len(roh)/1024:.0f} kB)")
        else:
            print(f"    woff2 {woff2.stat().st_size/1024:.0f} kB")

    for name, url in LIZENZEN:
        ziel = ZIEL / name
        if ziel.is_file():
            continue
        try:
            ziel.write_bytes(laden(url))
            print(f"  {name}: abgelegt")
        except Exception as e:
            print(f"  {name}: FEHLER {e}")
            fehler += 1

    print()
    bestand()
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
