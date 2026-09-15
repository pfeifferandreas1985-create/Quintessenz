"""Misst die Kontrastverhaeltnisse des Designsystems (WCAG 2.1).

Die Vorgabe lautet: Papier mindestens 7:1 (Stufe AAA fuer Fliesstext).
Das Terminal ist Bedienoberflaeche mit kurzen Blicken, dort gilt 4,5:1
als Untergrenze fuer alles, was man lesen koennen muss.

Die Werte werden aus app/static/css/tokens.css gelesen, nicht hier
wiederholt - so kann die Messung nicht veralten.

Aufruf:  python tools/kontrast.py
Rueckgabe 1, wenn eine geforderte Paarung reisst.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

CSS = Path(__file__).resolve().parent.parent / "app" / "static" / "css"
TOKENS = CSS / "tokens.css"
THEMEN = CSS / "themen.css"

# (Vordergrund, Hintergrund, Beschreibung, Mindestwert)
PAARE = [
    ("--tinte",          "--pap-dunkel",   "Papier: Fliesstext auf dunkelster Stelle", 7.0),
    ("--tinte",          "--pap-hell",     "Papier: Fliesstext auf hellster Stelle",   7.0),
    ("--tinte-mittel",   "--pap-dunkel",   "Papier: Untertitel, Tabellenhinweis",      4.5),
    ("--tinte-schwach",  "--pap-dunkel",   "Papier: Quellenlabel, Bildherkunft",       3.0),
    ("--stempel",        "--pap-dunkel",   "Papier: Stempel und Verweise",             4.5),
    ("--warn-schwarz",   "--warn-gelb",    "Papier: Warnband",                         7.0),
    ("--phos",           "--term-bg",      "Terminal: Haupttext",                      4.5),
    ("--phos-hell",      "--term-bg",      "Terminal: Schilder",                       4.5),
]

# Zusaetzlich im Modus "hoher Kontrast"
PAARE_HOCH = [
    ("--tinte", "--pap-dunkel", "Hoher Kontrast: Fliesstext", 7.0),
]


def lese_block(datei: Path, block: str) -> dict[str, str]:
    text = datei.read_text(encoding="utf-8")
    start = text.index(block) + len(block)
    ende = text.index("}", start)
    werte: dict[str, str] = {}
    for name, wert in re.findall(r"(--[a-z0-9-]+)\s*:\s*([^;]+);", text[start:ende]):
        werte[name] = wert.strip()
    return werte


def lese_tokens(block: str = ":root {") -> dict[str, str]:
    return lese_block(TOKENS, block)


def themen_ids() -> list[str]:
    """Alle in themen.css definierten Geraete, in Reihenfolge der Datei."""
    text = THEMEN.read_text(encoding="utf-8")
    return re.findall(r':root\[data-thema="([a-z]+)"\]\s*\{', text)


def rgb(wert: str) -> tuple[float, float, float]:
    wert = wert.strip()
    m = re.match(r"#([0-9a-fA-F]{6})$", wert)
    if m:
        h = m.group(1)
        return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]
    m = re.match(r"rgba?\(([^)]+)\)", wert)
    if m:
        teile = [t.strip() for t in m.group(1).split(",")]
        return tuple(float(t) / 255 for t in teile[:3])             # type: ignore[return-value]
    raise ValueError(f"Farbe nicht lesbar: {wert!r}")


def leuchtdichte(farbe: tuple[float, float, float]) -> float:
    def k(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (k(x) for x in farbe)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def kontrast(a: str, b: str) -> float:
    la, lb = leuchtdichte(rgb(a)), leuchtdichte(rgb(b))
    hell, dunkel = max(la, lb), min(la, lb)
    return (hell + 0.05) / (dunkel + 0.05)


def mische(a: str, b: str, anteil: float = 0.5) -> str:
    """Mittelwert zweier Farben - fuer den Verlauf des Papiers."""
    ra, rb = rgb(a), rgb(b)
    m = tuple(round(255 * (x * (1 - anteil) + y * anteil)) for x, y in zip(ra, rb))
    return "#%02X%02X%02X" % m


def pruefe_thema(name: str, werte: dict[str, str], ausfuehrlich: bool) -> int:
    """Prueft ein Geraet. Liefert die Zahl der gerissenen Paarungen."""
    mitte = mische(werte["--pap-hell"], werte["--pap-dunkel"])
    fehler = 0
    zeilen: list[str] = []

    for vg, hg, bez, soll in PAARE:
        ist = kontrast(werte[vg], werte[hg])
        ok = ist >= soll
        fehler += not ok
        zeilen.append(f"  {bez:50s} {ist:6.2f}:1 {soll:5.1f}  "
                      f"{'ok' if ok else 'REISST'}")

    ist = kontrast(werte["--tinte"], mitte)
    ok = ist >= 7
    fehler += not ok
    zeilen.append(f"  {'Papier: Fliesstext auf Mittelwert ' + mitte:50s} "
                  f"{ist:6.2f}:1 {7.0:5.1f}  {'ok' if ok else 'REISST'}")

    kopf = f"{name.upper():16s} Papier {ist:5.2f}:1   Schirm " \
           f"{kontrast(werte['--phos'], werte['--term-bg']):5.2f}:1"
    print(kopf + ("" if not fehler else f"   <-- {fehler} REISST"))
    if ausfuehrlich or fehler:
        print("\n".join(zeilen))
    return fehler


def main() -> int:
    ausfuehrlich = "--alles" in sys.argv
    grund = lese_tokens(":root {")
    fehler = 0

    print("Geraete (themen.css) - Papier >= 7:1, Schirm >= 4,5:1\n")
    for tid in themen_ids():
        werte = {**grund, **lese_block(THEMEN, f':root[data-thema="{tid}"] {{')}
        fehler += pruefe_thema(tid, werte, ausfuehrlich)

    print()
    hoch = lese_tokens(':root[data-kontrast="hoch"] {')
    for vg, hg, bez, soll in PAARE_HOCH:
        werte = {**grund, **hoch}
        mitte = mische(werte["--pap-hell"], werte["--pap-dunkel"])
        ist = kontrast(werte[vg], mitte)
        ok = ist >= soll
        fehler += not ok
        print(f"{'HOHER KONTRAST':16s} Papier {ist:5.2f}:1 (auf {mitte})"
              f"{'' if ok else '   <-- REISST'}")

    print()
    print(f"{fehler} Paarung(en) reissen." if fehler
          else "Alle Geraete erfuellen die Vorgaben.")
    if not ausfuehrlich and not fehler:
        print("Einzelwerte:  python tools/kontrast.py --alles")
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
