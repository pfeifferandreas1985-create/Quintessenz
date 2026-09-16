"""Datenmodell einer AKTE - das gemeinsame Format aller Quellen.

Der Kern der Anwendung ist, dass jede Quelle (ZIM-Artikel, Stack-Exchange-
Thread, PDF-Kapitel, eigene SQLite-Tabelle, Markdown-Datei) in EIN Format
uebersetzt wird. Das Papier-Template kennt nur dieses Format und sonst nichts.
Dadurch sieht jede Seite gleich aus, egal woher sie kommt.

Ein Adapter hat genau eine Aufgabe: Rohquelle -> Akte.
Er erzeugt kein Darstellungs-HTML; das macht allein das Frontend.

BLOCKTYPEN (Akte.inhalt)
------------------------
ueberschrift  ebene 2..4, text, anker
absatz        html  (erlaubt: em strong code sub sup br a[data-akte] a[data-anker])
liste         geordnet: bool, punkte: [html]
tabelle       titel, kopf: [str], zeilen: [[str]], ausrichtung: [l|r|c], fussnote
bild          quelle (URL), alt, bildunterschrift, herkunft, breite: schmal|normal|breit
seitenbild    wie bild, aber als "eingeklebte Kopie" gerahmt (PDF-Seite, Zeichnung)
code          sprache, text, titel          -> Lochstreifen-Kasten
formel        tex, text (Klartextfassung fuer Screenreader und Notfall)
warnung       stufe: gefahr|achtung|hinweis, titel, text
infokasten    titel, zeilen: [[label, wert]] -> gestempeltes Formular
zitat         text, autor
fall_frage    autor, datum, stimmen, blocks: [Block]
fall_antwort  autor, datum, stimmen, akzeptiert: bool, blocks: [Block]
trenner       -

TIEFE-STEMPEL: REFERENZ | LEHRBUCH | PRAXIS | FALL
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import asdict, dataclass, field
from typing import Any

TIEFEN = ("REFERENZ", "LEHRBUCH", "PRAXIS", "FALL")
QUELLTYPEN = ("zim", "se", "pdf", "eigen", "demo")

_UMLAUTE = {
    "ä": "ae", "ö": "oe", "ü": "ue",
    "Ä": "ae", "Ö": "oe", "Ü": "ue", "ß": "ss",
}


def anker(text: str) -> str:
    """Stabiler Sprungmarken-Name aus einer Ueberschrift."""
    for k, v in _UMLAUTE.items():
        text = text.replace(k, v)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return re.sub(r"-{2,}", "-", text)[:60]


@dataclass
class Quelle:
    """Der Aktenstempel: woher der Inhalt stammt. Immer sichtbar."""

    typ: str                      # zim | se | pdf | eigen | demo
    name: str                     # "Wikipedia DE", "Electrical Engineering SE"
    datei: str = ""               # wikipedia_de_all_maxi_2026-01.zim / neets_mod07.pdf
    kennung: str = ""             # Artikelname, Fragen-ID, Kapitelnummer
    seite: str = ""               # "S. 4-12 bis 4-19"
    lizenz: str = ""              # "CC BY-SA 4.0", "Public Domain (US Navy)"
    stand: str = ""               # Datum des Quellstandes, ISO
    autor: str = ""
    nur_lokal: bool = False       # aus zim/eigene/privat/ -> Stempel "NUR LOKAL"
    original_url: str = ""        # interne Route fuer "Original einsehen", nie extern


@dataclass
class Akte:
    id: str
    titel: str
    bereich_id: str
    thema_id: str
    tiefe: str                    # einer von TIEFEN
    sprache: str                  # "DE" | "EN"
    quelle: Quelle
    inhalt: list[dict[str, Any]] = field(default_factory=list)
    untertitel: str = ""
    verwandt: list[dict[str, str]] = field(default_factory=list)
    stempel: list[str] = field(default_factory=list)   # z.B. ["DEMO", "NUR LOKAL"]
    demo: bool = False

    def inhaltsverzeichnis(self) -> list[dict[str, Any]]:
        return [
            {
                "ebene": b.get("ebene", 2),
                "text": b["text"],
                "anker": b.get("anker") or anker(b["text"]),
            }
            for b in self.inhalt
            if b.get("typ") == "ueberschrift"
        ]

    def volltext(self) -> str:
        """Flacher Text fuer FTS5 und die Demo-Suche."""
        teile: list[str] = [self.titel, self.untertitel]

        def lauf(blocks: list[dict[str, Any]]) -> None:
            for b in blocks:
                t = b.get("typ")
                if t in ("ueberschrift", "zitat"):
                    teile.append(b.get("text", ""))
                elif t == "absatz":
                    teile.append(b.get("html", ""))
                elif t == "liste":
                    teile.extend(b.get("punkte", []))
                elif t == "tabelle":
                    teile.extend(b.get("kopf", []))
                    for z in b.get("zeilen", []):
                        teile.extend(str(c) for c in z)
                elif t in ("bild", "seitenbild"):
                    teile.append(b.get("bildunterschrift", ""))
                elif t in ("code", "formel"):
                    teile.append(b.get("text", ""))
                elif t == "warnung":
                    teile.append(b.get("titel", ""))
                    teile.append(b.get("text", ""))
                elif t == "infokasten":
                    for zeile in b.get("zeilen", []):
                        teile.extend(str(c) for c in zeile)
                elif t in ("fall_frage", "fall_antwort"):
                    lauf(b.get("blocks", []))

        lauf(self.inhalt)
        return re.sub(r"<[^>]+>", " ", " ".join(x for x in teile if x))

    def kurzfassung(self, zeichen: int = 220) -> str:
        def ersterAbsatz(blocks: list[dict[str, Any]]) -> str:
            for b in blocks:
                if b.get("typ") == "absatz":
                    txt = re.sub(r"<[^>]+>", "", b.get("html", "")).strip()
                    if len(txt) > 40:
                        return txt
                if b.get("typ") in ("fall_frage", "fall_antwort"):
                    treffer = ersterAbsatz(b.get("blocks", []))
                    if treffer:
                        return treffer
            return ""

        txt = ersterAbsatz(self.inhalt)
        return txt[:zeichen] + ("…" if len(txt) > zeichen else "")

    def als_dict(self, mit_inhalt: bool = True) -> dict[str, Any]:
        d = asdict(self)
        d["toc"] = self.inhaltsverzeichnis()
        d["kurzfassung"] = self.kurzfassung()
        if not mit_inhalt:
            d.pop("inhalt")
        return d


# --- Bequeme Konstruktoren, damit Adapter kurz bleiben -----------------------


def h(text: str, ebene: int = 2) -> dict[str, Any]:
    return {"typ": "ueberschrift", "ebene": ebene, "text": text, "anker": anker(text)}


def p(html: str) -> dict[str, Any]:
    return {"typ": "absatz", "html": html}


def ul(*punkte: str, geordnet: bool = False) -> dict[str, Any]:
    return {"typ": "liste", "geordnet": geordnet, "punkte": list(punkte)}


def tab(kopf: list[str], zeilen: list[list[str]], titel: str = "",
        ausrichtung: list[str] | None = None, fussnote: str = "") -> dict[str, Any]:
    return {"typ": "tabelle", "titel": titel, "kopf": kopf, "zeilen": zeilen,
            "ausrichtung": ausrichtung or ["l"] * len(kopf), "fussnote": fussnote}


def bild(quelle: str, bildunterschrift: str = "", herkunft: str = "",
         breite: str = "normal", alt: str = "") -> dict[str, Any]:
    return {"typ": "bild", "quelle": quelle, "alt": alt or bildunterschrift,
            "bildunterschrift": bildunterschrift, "herkunft": herkunft, "breite": breite}


def seitenbild(quelle: str, bildunterschrift: str = "", herkunft: str = "",
               alt: str = "") -> dict[str, Any]:
    return {"typ": "seitenbild", "quelle": quelle, "alt": alt or bildunterschrift,
            "bildunterschrift": bildunterschrift, "herkunft": herkunft, "breite": "breit"}


def code(text: str, sprache: str = "", titel: str = "") -> dict[str, Any]:
    return {"typ": "code", "sprache": sprache, "text": text, "titel": titel}


def formel(tex: str, text: str = "") -> dict[str, Any]:
    return {"typ": "formel", "tex": tex, "text": text}


def warnung(titel: str, text: str, stufe: str = "achtung") -> dict[str, Any]:
    return {"typ": "warnung", "stufe": stufe, "titel": titel, "text": text}


def infokasten(titel: str, zeilen: list[list[str]]) -> dict[str, Any]:
    return {"typ": "infokasten", "titel": titel, "zeilen": zeilen}


def zitat(text: str, autor: str = "") -> dict[str, Any]:
    return {"typ": "zitat", "text": text, "autor": autor}


def trenner() -> dict[str, Any]:
    return {"typ": "trenner"}


def fall_frage(autor: str, datum: str, stimmen: int,
               blocks: list[dict[str, Any]]) -> dict[str, Any]:
    return {"typ": "fall_frage", "autor": autor, "datum": datum,
            "stimmen": stimmen, "blocks": blocks}


def fall_antwort(autor: str, datum: str, stimmen: int, blocks: list[dict[str, Any]],
                 akzeptiert: bool = False) -> dict[str, Any]:
    return {"typ": "fall_antwort", "autor": autor, "datum": datum, "stimmen": stimmen,
            "akzeptiert": akzeptiert, "blocks": blocks}
