"""Wo liegen die Daten? Eine Stelle, damit PC und Pi denselben Code fahren.

Reihenfolge:
  1. Umgebungsvariable QUINTESSENZ_DATEN
  2. /srv/box                          (Pi)
  3. D:\\DoomsdayBox                    (PC, Arbeitslaufwerk)
  4. C:\\D-Sicherung\\DoomsdayBox        (PC, Sicherungskopie)

"Belegt" hei\u00dft: der Ordner existiert UND enth\u00e4lt mindestens ein Modul mit
Inhalt. Ein leerer Ordner z\u00e4hlt nicht, sonst gewinnt auf dem PC das leere
D:\\DoomsdayBox gegen die gef\u00fcllte Sicherung.
"""
from __future__ import annotations

import os
from pathlib import Path

MODULE = ("zim", "pdf", "own", "maps", "models", "db", "doku")

KANDIDATEN = [
    Path("/srv/box"),
    Path("D:/DoomsdayBox"),
    Path("C:/D-Sicherung/DoomsdayBox"),
]


def _belegt(wurzel: Path) -> bool:
    if not wurzel.is_dir():
        return False
    return any(
        (wurzel / m).is_dir() and any((wurzel / m).iterdir())
        for m in MODULE
    )


def finde_daten() -> Path:
    gesetzt = os.environ.get("QUINTESSENZ_DATEN")
    if gesetzt:
        return Path(gesetzt)
    for k in KANDIDATEN:
        if _belegt(k):
            return k
    for k in KANDIDATEN:
        if k.is_dir():
            return k
    return Path.cwd() / "daten"


APP = Path(__file__).resolve().parent
WURZEL = APP.parent
DATEN = finde_daten()

ZIM = DATEN / "zim"
PDF = DATEN / "pdf"
OWN = DATEN / "own"
MAPS = DATEN / "maps"
MODELS = DATEN / "models"
DB = DATEN / "db"
DOKU = DATEN / "doku"

FAHRZEUGE_DB = OWN / "fahrzeuge" / "fahrzeuge.db"
REBUILD_DB = OWN / "rebuild" / "rebuild_trees.db"
INDEX_DB = DB / "index.sqlite"
VEKTOR_DB = DB / "vectors.sqlite"
BILDER = DB / "images"

# Dienste auf der Box. Auf dem PC zeigen sie ins Leere; die Anwendung
# erkennt das und blendet die betroffenen Funktionen aus.
KIWIX_URL = os.environ.get("QUINTESSENZ_KIWIX", "http://127.0.0.1:8888")
LLAMA_URL = os.environ.get("QUINTESSENZ_LLAMA", "http://127.0.0.1:8080")
EMBED_URL = os.environ.get("QUINTESSENZ_EMBED", "http://127.0.0.1:8081")


def bestand() -> dict[str, dict[str, object]]:
    """Was ist tats\u00e4chlich da? Speist die Zeigerinstrumente im Eingang."""
    out: dict[str, dict[str, object]] = {}
    for m in MODULE:
        pfad = DATEN / m
        if not pfad.is_dir():
            out[m] = {"da": False, "dateien": 0, "bytes": 0}
            continue
        dateien = [f for f in pfad.rglob("*") if f.is_file()]
        out[m] = {
            "da": True,
            "dateien": len(dateien),
            "bytes": sum(f.stat().st_size for f in dateien),
        }
    return out
