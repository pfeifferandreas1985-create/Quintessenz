"""Erzeugt app/config/bereiche.yaml aus doku/WISSENSUEBERSICHT.md.

Jede Tabellenzeile eines Abschnitts 2.x wird ein Thema (Entscheidung vom
2026-09-15). Zeilen "Nicht enthalten" landen als Ausschluss im Bereich.
Aufruf:  python tools/gen_bereiche.py <pfad/WISSENSUEBERSICHT.md>
"""
import re
import sys
import unicodedata
from pathlib import Path

# Reihenfolge = Reihenfolge der Abschnitte 2.1 .. 2.16 in der Uebersicht.
PIKTOGRAMME = [
    "blitz", "zahnrad", "regler", "relais", "messgeraet", "lochkarte",
    "kreuz", "zelt", "atom", "antenne", "schild", "amboss",
    "buch", "kompass", "gehirn", "schraubenschluessel",
]
# Kurzname fuer das gestanzte Metallschild im Terminal (max. ~18 Zeichen).
SCHILD = {
    1: "ELEKTROTECHNIK", 2: "MECHANIK", 3: "ANTRIEBE", 4: "SPS",
    5: "MESSTECHNIK", 6: "PROGRAMMIERUNG", 7: "MEDIZIN", 8: "SURVIVAL",
    9: "ENERGIE", 10: "KOMMUNIKATION", 11: "SCHUTZ", 12: "NEUSTART",
    13: "ALLGEMEIN", 14: "KARTEN", 15: "MASCHINE", 16: "FAHRZEUGE",
}
# Gruppen der obersten Navigationsebene (Entscheidung vom 15.09.2026).
# Die 16 Bereiche bleiben einen Klick entfernt; die Gruppe ist nur eine
# Zwischenueberschrift am Eingang, kein eigener Schritt. Die Reihenfolge
# hier ist die Reihenfolge auf dem Schirm - innerhalb wie aussen.
GRUPPEN = [
    ("engineering", "ENGINEERING", [1, 2, 3, 4, 5]),
    ("rechner",     "RECHNER",     [6, 15]),
    ("ueberleben",  "\u00dcBERLEBEN",   [7, 8, 11]),
    ("versorgung",  "VERSORGUNG",  [9, 10, 14]),
    ("wissen",      "WISSEN",      [13, 12]),
    ("eigenes",     "EIGENES",     [16]),
]

TIEFE_MAP = {
    "referenz": "REFERENZ", "lehrbuch": "LEHRBUCH",
    "praxis": "PRAXIS", "q&a": "FALL", "code": "REFERENZ",
}


def slug(text: str, max_woerter: int = 5, max_len: int = 42) -> str:
    """Kurzer, sprechender URL-Name. Bricht nie mitten im Wort ab.

    Themenzeilen der Uebersicht sind oft Aufzaehlungen ("Grundlagen: Ohm,
    Kirchhoff, Wechselstrom, ..."). Fuer die URL zaehlt nur der Kopf davon.
    """
    text = text.split(":")[0]
    for a, b in (("–", "-"), ("—", "-"), ("ä", "ae"), ("ö", "oe"),
                 ("ü", "ue"), ("Ä", "ae"), ("Ö", "oe"), ("Ü", "ue"),
                 ("ß", "ss")):
        text = text.replace(a, b)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    woerter = [w for w in re.split(r"[^a-zA-Z0-9]+", text.lower()) if w]
    out: list[str] = []
    for w in woerter[:max_woerter]:
        if out and len("-".join(out)) + 1 + len(w) > max_len:
            break
        out.append(w)
    return "-".join(out) or "thema"


def eindeutig(kandidat: str, vergeben: set[str]) -> str:
    name, n = kandidat, 2
    while name in vergeben:
        name, n = f"{kandidat}-{n}", n + 1
    vergeben.add(name)
    return name


def strip_md(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    return text.replace("„", '"').replace("“", '"').strip()


def parse_tiefe(cell: str) -> list[str]:
    low = cell.lower()
    out = [v for k, v in TIEFE_MAP.items() if k in low]
    seen = []
    for v in out:
        if v not in seen:
            seen.append(v)
    return seen or ["REFERENZ"]


def split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def yaml_str(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main(src: Path, dst: Path) -> None:
    lines = src.read_text(encoding="utf-8").splitlines()
    bereiche, cur = [], None
    header: list[str] = []

    for line in lines:
        m = re.match(r"^###\s+2\.(\d+)\s+(.+?)\s*$", line)
        if m:
            nr = int(m.group(1))
            cur = {
                "nr": nr, "titel": strip_md(m.group(2)),
                "schild": SCHILD.get(nr, strip_md(m.group(2)).upper()[:18]),
                "piktogramm": PIKTOGRAMME[nr - 1] if nr <= len(PIKTOGRAMME) else "buch",
                "themen": [], "ausschluss": [], "_ids": set(),
            }
            bereiche.append(cur)
            header = []
            continue
        if line.startswith("#"):     # jede andere Ueberschrift beendet den Bereich
            cur = None
            continue
        if cur is None or not line.startswith("|"):
            continue
        cells = split_row(line)
        if set("".join(cells)) <= set("-: "):       # Trennzeile
            continue
        if not header:                              # Kopfzeile
            header = [c.lower() for c in cells]
            continue

        titel = strip_md(cells[0])
        if not titel:
            continue
        if titel.lower().startswith("nicht enthalten"):
            cur["ausschluss"].append(strip_md(cells[1]) if len(cells) > 1 else "")
            continue

        def col(*names, default=""):
            for n in names:
                for i, h in enumerate(header):
                    if n in h and i < len(cells):
                        return strip_md(cells[i])
            return default

        # 2.16 hat die Spalten Fahrzeug | Was du nachschlagen kannst | Quelle | Tiefe
        if cur["nr"] == 16 and len(cells) >= 4:
            beschreibung = strip_md(cells[1])
            quelle, tiefe = strip_md(cells[2]), strip_md(cells[3])
        else:
            beschreibung = ""
            quelle = col("quelle", "modell", default="")
            tiefe = col("tiefe", default="")

        cur["themen"].append({
            "id": eindeutig(slug(titel), cur["_ids"]),
            "titel": titel,
            "beschreibung": beschreibung,
            "quellen_text": quelle,
            "tiefe": parse_tiefe(tiefe or col("umfang", "was es bedeutet")),
            "sprache": col("sprache", default="DE"),
            "umfang": col("umfang", "was es bedeutet", default=""),
        })

    gruppe_von = {nr: gid for gid, _, nrs in GRUPPEN for nr in nrs}
    nach_nr = {b["nr"]: b for b in bereiche}
    fehlend = [b["nr"] for b in bereiche if b["nr"] not in gruppe_von]
    if fehlend:
        print(f"  WARNUNG: Bereiche ohne Gruppe: {fehlend} -> 'wissen'")

    out = [
        "# bereiche.yaml - Navigationsebene 1 und 2 des QUINTESSENZ TERMINALs.",
        "#",
        "# ERZEUGT von tools/gen_bereiche.py aus doku/WISSENSUEBERSICHT.md.",
        "# Haendische Aenderungen an Titeln/Themen sind erlaubt, gehen aber bei einem",
        "# erneuten Lauf des Generators verloren. Kuratierte Einstiegsakten und die",
        "# Quellenzuordnung stehen in quellen.yaml und bleiben davon unberuehrt.",
        "#",
        f"# Quelle: {src.name}",
        "",
        "# Gruppen: nur Zwischenueberschriften am Eingang, KEINE eigene",
        "# Navigationsebene. Jeder Bereich bleibt einen Klick entfernt und",
        "# behaelt seine Adresse #/b/<id>. Gepflegt in tools/gen_bereiche.py.",
        "gruppen:",
    ]
    for gid, schild, nrs in GRUPPEN:
        mitglieder = [nach_nr[n] for n in nrs if n in nach_nr]
        themen = sum(len(b["themen"]) for b in mitglieder)
        out += [
            f"  - id: {gid}",
            f"    schild: {yaml_str(schild)}",
            f"    themen: {themen}",
            "    bereiche: [" + ", ".join(
                slug(b["titel"], max_woerter=4, max_len=34) for b in mitglieder) + "]",
        ]
    out += [
        "",
        "bereiche:",
    ]
    for b in bereiche:
        b.pop("_ids", None)
        out += [
            f"  - id: {slug(b['titel'], max_woerter=4, max_len=34)}",
            f"    nr: {b['nr']}",
            f"    titel: {yaml_str(b['titel'])}",
            f"    schild: {yaml_str(b['schild'])}",
            f"    piktogramm: {b['piktogramm']}",
            f"    gruppe: {gruppe_von.get(b['nr'], 'wissen')}",
            "    themen:",
        ]
        for t in b["themen"]:
            out += [
                f"      - id: {t['id']}",
                f"        titel: {yaml_str(t['titel'])}",
                f"        tiefe: [{', '.join(t['tiefe'])}]",
                f"        sprache: {yaml_str(t['sprache'] or 'DE')}",
            ]
            if t["beschreibung"]:
                out.append(f"        beschreibung: {yaml_str(t['beschreibung'])}")
            if t["quellen_text"]:
                out.append(f"        quellen_text: {yaml_str(t['quellen_text'])}")
            if t["umfang"]:
                out.append(f"        umfang: {yaml_str(t['umfang'])}")
        if b["ausschluss"]:
            out.append("    ausschluss:")
            out += [f"      - {yaml_str(a)}" for a in b["ausschluss"] if a]
        out.append("")

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("\n".join(out), encoding="utf-8")
    ges = sum(len(b["themen"]) for b in bereiche)
    print(f"{dst}: {len(GRUPPEN)} Gruppen, {len(bereiche)} Bereiche, {ges} Themen")
    for gid, schild, nrs in GRUPPEN:
        mitglieder = [nach_nr[n] for n in nrs if n in nach_nr]
        themen = sum(len(b["themen"]) for b in mitglieder)
        print(f"\n  {schild:<14s} {themen:>3} Themen")
        for b in mitglieder:
            print(f"    2.{b['nr']:<2} {b['titel'][:42]:42s} {len(b['themen']):>3}")


if __name__ == "__main__":
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        r"C:\D-Sicherung\DoomsdayBox\doku\WISSENSUEBERSICHT.md")
    dst = Path(__file__).resolve().parent.parent / "app" / "config" / "bereiche.yaml"
    main(src, dst)
