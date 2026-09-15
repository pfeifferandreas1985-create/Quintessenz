"""QUINTESSENZ TERMINAL - Serverseite.

Leichtgewichtig: FastAPI + Uvicorn, kein Datenbankserver, kein Build-Schritt,
keine externe Anfrage. Alles, was der Browser braucht, liegt unter static/.

Im Prototyp haelt der Server alle Akten im Speicher (75 Stueck, wenige MB).
Sobald der Ingest laeuft, wird REGISTER durch eine SQLite-FTS5-Abfrage
ersetzt - die Routen und das JSON-Format bleiben unveraendert.

Start:  python -m uvicorn server:app --host 0.0.0.0 --port 8000 --app-dir app
"""
from __future__ import annotations

import html as html_mod
import re
import sys
import time
from pathlib import Path
from typing import Any

import yaml
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

APP_DIR = Path(__file__).resolve().parent
for p in (APP_DIR, APP_DIR / "adapters", APP_DIR / "demo"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import pfade                                   # noqa: E402
from akte import Akte                          # noqa: E402
import eigene                                  # noqa: E402
import fixtures                                # noqa: E402

VERSION = "0.1.0-prototyp"
START = time.time()

app = FastAPI(title="QUINTESSENZ TERMINAL", version=VERSION, docs_url=None, redoc_url=None)


# --- Bestand laden ----------------------------------------------------------

def _lade_konfig() -> dict[str, Any]:
    with open(APP_DIR / "config" / "bereiche.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


_KONFIG = _lade_konfig()
BEREICHE: list[dict[str, Any]] = _KONFIG["bereiche"]
BEREICH_NACH_ID = {b["id"]: b for b in BEREICHE}
# Gruppen sind nur Zwischenueberschriften am Eingang, keine Navigationsebene.
# Es gibt deshalb bewusst KEINE Route /api/gruppe/<id>.
GRUPPEN: list[dict[str, Any]] = _KONFIG.get("gruppen", [])
GRUPPEN_RANG = {b: (gi, bi) for gi, g in enumerate(GRUPPEN)
                for bi, b in enumerate(g["bereiche"])}

REGISTER: dict[str, Akte] = {}
VOLLTEXT: dict[str, str] = {}


def _register_aufbauen() -> None:
    REGISTER.clear()
    VOLLTEXT.clear()
    for a in list(eigene.alle()) + list(fixtures.DEMO_AKTEN):
        REGISTER[a.id] = a
        VOLLTEXT[a.id] = a.volltext().lower()


_register_aufbauen()


def _akten_im_bereich(bereich_id: str) -> list[Akte]:
    return [a for a in REGISTER.values() if a.bereich_id == bereich_id]


def _akten_im_thema(bereich_id: str, thema_id: str) -> list[Akte]:
    return [a for a in REGISTER.values()
            if a.bereich_id == bereich_id and a.thema_id == thema_id]


# Reihenfolge auf Themenseiten: Referenz zuerst, Faelle zuletzt.
TIEFE_RANG = {"REFERENZ": 0, "LEHRBUCH": 1, "PRAXIS": 2, "FALL": 3}


def _sortiert(akten: list[Akte]) -> list[Akte]:
    return sorted(akten, key=lambda a: (TIEFE_RANG.get(a.tiefe, 9), a.titel))


# --- Navigationsrouten ------------------------------------------------------

@app.get("/api/eingang")
def eingang() -> dict[str, Any]:
    """Startbildschirm: 16 Bereiche, nach Gruppen geordnet, plus Kennzahlen."""
    nach_id: dict[str, dict[str, Any]] = {}
    for b in BEREICHE:
        akten = _akten_im_bereich(b["id"])
        belegte = {a.thema_id for a in akten}
        nach_id[b["id"]] = {
            "id": b["id"], "nr": b["nr"], "titel": b["titel"],
            "schild": b["schild"], "piktogramm": b["piktogramm"],
            "gruppe": b.get("gruppe", ""),
            "themen": len(b["themen"]),
            "themen_belegt": len(belegte),
            "akten": len(akten),
        }

    gruppen = []
    for g in GRUPPEN:
        mitglieder = [nach_id[i] for i in g["bereiche"] if i in nach_id]
        gruppen.append({
            "id": g["id"], "schild": g["schild"],
            "themen": sum(m["themen"] for m in mitglieder),
            "akten": sum(m["akten"] for m in mitglieder),
            "bereiche": mitglieder,
        })
    # Bereiche, die keiner Gruppe zugeordnet sind, gehen nicht verloren.
    zugeordnet = {m["id"] for g in gruppen for m in g["bereiche"]}
    uebrig = [b for i, b in nach_id.items() if i not in zugeordnet]
    if uebrig:
        gruppen.append({"id": "sonstige", "schild": "SONSTIGE",
                        "themen": sum(b["themen"] for b in uebrig),
                        "akten": sum(b["akten"] for b in uebrig),
                        "bereiche": uebrig})

    bereiche = [m for g in gruppen for m in g["bereiche"]]
    best = pfade.bestand()
    return {
        "gruppen": gruppen,
        "bereiche": bereiche,
        "kennzahlen": {
            "akten_gesamt": len(REGISTER),
            "akten_demo": sum(1 for a in REGISTER.values() if a.demo),
            "themen_gesamt": sum(len(b["themen"]) for b in BEREICHE),
            "bereiche_gesamt": len(BEREICHE),
            "gruppen_gesamt": len(GRUPPEN),
            "archiv_bytes": sum(int(v["bytes"]) for v in best.values()),
            "archiv_dateien": sum(int(v["dateien"]) for v in best.values()),
        },
        "bestand": best,
        "datenpfad": str(pfade.DATEN),
        "version": VERSION,
    }


@app.get("/api/bereich/{bereich_id}")
def bereich(bereich_id: str) -> dict[str, Any]:
    b = BEREICH_NACH_ID.get(bereich_id)
    if not b:
        raise HTTPException(404, "Bereich nicht gefunden")
    akten = _akten_im_bereich(bereich_id)
    themen = []
    for t in b["themen"]:
        im_thema = [a for a in akten if a.thema_id == t["id"]]
        themen.append({
            **{k: v for k, v in t.items() if k != "beschreibung"},
            "akten": len(im_thema),
            "quellen": sorted({a.quelle.typ for a in im_thema}),
        })
    g = next((x for x in GRUPPEN if b["id"] in x["bereiche"]), None)
    return {
        "id": b["id"], "nr": b["nr"], "titel": b["titel"], "schild": b["schild"],
        "piktogramm": b["piktogramm"], "ausschluss": b.get("ausschluss", []),
        "gruppe": {"id": g["id"], "schild": g["schild"]} if g else None,
        "akten_gesamt": len(akten), "themen": themen,
    }


@app.get("/api/thema/{bereich_id}/{thema_id}")
def thema(bereich_id: str, thema_id: str) -> dict[str, Any]:
    b = BEREICH_NACH_ID.get(bereich_id)
    if not b:
        raise HTTPException(404, "Bereich nicht gefunden")
    t = next((x for x in b["themen"] if x["id"] == thema_id), None)
    if not t:
        raise HTTPException(404, "Thema nicht gefunden")
    akten = _sortiert(_akten_im_thema(bereich_id, thema_id))
    return {
        "bereich": {"id": b["id"], "titel": b["titel"], "schild": b["schild"],
                    "piktogramm": b["piktogramm"]},
        "thema": t,
        "akten": [a.als_dict(mit_inhalt=False) for a in akten],
    }


@app.get("/api/akte/{akte_id}")
def akte(akte_id: str) -> dict[str, Any]:
    a = REGISTER.get(akte_id)
    if not a:
        raise HTTPException(404, "Akte nicht gefunden")
    b = BEREICH_NACH_ID.get(a.bereich_id, {})
    t = next((x for x in b.get("themen", []) if x["id"] == a.thema_id), {})
    d = a.als_dict()
    d["pfad"] = {
        "bereich": {"id": a.bereich_id, "titel": b.get("titel", a.bereich_id),
                    "schild": b.get("schild", ""), "piktogramm": b.get("piktogramm", "buch")},
        "thema": {"id": a.thema_id, "titel": t.get("titel", a.thema_id)},
    }
    return d


@app.get("/api/akte/{akte_id}/original", response_class=HTMLResponse)
def original(akte_id: str) -> HTMLResponse:
    """Rohdarstellung fuer das Overlay 'Original einsehen'.

    Im Prototyp die unveraenderte Blockstruktur. Sobald die echten Adapter
    laufen, liefert diese Route das bereinigte Quell-HTML aus der ZIM bzw.
    die gerenderte PDF-Seite.
    """
    a = REGISTER.get(akte_id)
    if not a:
        raise HTTPException(404, "Akte nicht gefunden")
    import json
    roh = json.dumps([b for b in a.inhalt], ensure_ascii=False, indent=2)
    q = a.quelle
    strich = "—"
    kopf = "\n".join([
        f"Quelle:  {q.name}",
        f"Datei:   {q.datei or strich}",
        f"Kennung: {q.kennung or strich}",
        f"Seite:   {q.seite or strich}",
        f"Lizenz:  {q.lizenz or strich}",
        f"Stand:   {q.stand or strich}",
    ]) + "\n"
    return HTMLResponse(
        "<!doctype html><meta charset='utf-8'>"
        "<style>body{background:#0B0F0A;color:#33FF66;font:13px/1.5 ui-monospace,monospace;"
        "padding:1.2rem;margin:0}h1{font-size:1rem;letter-spacing:.1em}"
        "pre{white-space:pre-wrap;word-break:break-word}hr{border:0;border-top:1px dashed #33FF6655}</style>"
        f"<h1>ROHDATEN · {html_mod.escape(a.titel)}</h1>"
        f"<pre>{html_mod.escape(kopf)}</pre><hr>"
        f"<pre>{html_mod.escape(roh)}</pre>"
    )


# --- Suche ------------------------------------------------------------------

def _schnipsel(text: str, begriffe: list[str], laenge: int = 190) -> str:
    tief = text.lower()
    pos = min((tief.find(b) for b in begriffe if tief.find(b) >= 0), default=-1)
    if pos < 0:
        return text[:laenge].strip()
    start = max(0, pos - laenge // 3)
    aus = text[start:start + laenge].strip()
    return ("…" if start > 0 else "") + aus + ("…" if start + laenge < len(text) else "")


@app.get("/api/suche")
def suche(q: str = Query("", min_length=0), grenze: int = 60) -> dict[str, Any]:
    """Demo-Suche ueber den Speicher.

    Gleiches Antwortformat wie die spaetere FTS5-Suche, damit das Frontend
    beim Umbau unveraendert bleibt.
    """
    begriffe = [w for w in re.split(r"\s+", q.strip().lower()) if len(w) > 1]
    if not begriffe:
        return {"anfrage": q, "treffer": 0, "dauer_ms": 0, "gruppen": []}

    t0 = time.perf_counter()
    bewertet: list[tuple[float, Akte]] = []
    for aid, a in REGISTER.items():
        titel = (a.titel + " " + a.untertitel).lower()
        text = VOLLTEXT[aid]
        punkte = 0.0
        for begriff in begriffe:
            if begriff in titel:
                punkte += 12
            treffer = text.count(begriff)
            if treffer:
                punkte += 1 + min(treffer, 8) * 0.5
        if punkte and all(b in titel or b in text for b in begriffe):
            punkte -= TIEFE_RANG.get(a.tiefe, 0) * 0.4      # Referenz zuerst
            bewertet.append((punkte, a))

    bewertet.sort(key=lambda x: (-x[0], x[1].titel))
    bewertet = bewertet[:grenze]

    gruppen: dict[str, dict[str, Any]] = {}
    for punkte, a in bewertet:
        b = BEREICH_NACH_ID.get(a.bereich_id, {})
        g = gruppen.setdefault(a.bereich_id, {
            "bereich_id": a.bereich_id,
            "titel": b.get("titel", a.bereich_id),
            "schild": b.get("schild", ""),
            "piktogramm": b.get("piktogramm", "buch"),
            "treffer": [],
        })
        d = a.als_dict(mit_inhalt=False)
        d["punkte"] = round(punkte, 1)
        d["schnipsel"] = _schnipsel(a.volltext(), begriffe)
        g["treffer"].append(d)

    dauer = (time.perf_counter() - t0) * 1000
    # Gleiche Reihenfolge wie am Eingang - wer die Gruppen kennt, findet
    # die Treffer an derselben Stelle wieder.
    return {
        "anfrage": q,
        "treffer": len(bewertet),
        "dauer_ms": round(dauer, 1),
        "gruppen": sorted(gruppen.values(),
                          key=lambda g: GRUPPEN_RANG.get(g["bereich_id"], (99, 99))),
    }


# --- Platzhalterrahmen ------------------------------------------------------

ART_TEXT = {
    "abbildung": "ABBILDUNG", "diagramm": "DIAGRAMM", "foto": "LICHTBILD",
    "zeichnung": "ZEICHNUNG", "seite": "SEITENKOPIE",
}


@app.get("/api/platzhalter.svg")
def platzhalter(w: int = 640, h: int = 400, text: str = "", art: str = "abbildung") -> Response:
    """Ehrlicher Platzhalter statt erfundenem Bild.

    Sagt, welche Abbildung aus welcher Quelle hier spaeter steht. Wird
    ueberfluessig, sobald der Ingest Bilder nach db/images/ extrahiert.
    """
    w, h = max(80, min(w, 1600)), max(60, min(h, 1600))
    marke = ART_TEXT.get(art, "ABBILDUNG")
    zeilen, zeile = [], ""
    grenze = max(18, int(w / 9.2))
    for wort in text.split():
        if len(zeile) + len(wort) + 1 > grenze:
            zeilen.append(zeile)
            zeile = wort
        else:
            zeile = f"{zeile} {wort}".strip()
    if zeile:
        zeilen.append(zeile)
    zeilen = zeilen[:4]

    y0 = h / 2 - (len(zeilen) - 1) * 11 + 6
    text_svg = "".join(
        f'<text x="{w/2:.0f}" y="{y0 + i*22:.0f}" text-anchor="middle" '
        f'font-family="Courier New, monospace" font-size="14" fill="#5E5344">'
        f'{html_mod.escape(z)}</text>'
        for i, z in enumerate(zeilen)
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">
<defs><pattern id="s" width="12" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
<line x1="0" y1="0" x2="0" y2="12" stroke="#1E1A14" stroke-width="1" opacity=".07"/></pattern></defs>
<rect width="{w}" height="{h}" fill="#DED2B6"/><rect width="{w}" height="{h}" fill="url(#s)"/>
<rect x="6" y="6" width="{w-12}" height="{h-12}" fill="none" stroke="#8B2E1F" stroke-width="2"
      stroke-dasharray="9 6" opacity=".55"/>
<text x="{w/2:.0f}" y="{y0-34:.0f}" text-anchor="middle" font-family="Jost, Arial, sans-serif"
      font-size="12" letter-spacing="3" fill="#8B2E1F">{marke} FOLGT</text>
{text_svg}
<text x="{w/2:.0f}" y="{h-16}" text-anchor="middle" font-family="Courier New, monospace"
      font-size="10" letter-spacing="1.5" fill="#8B2E1F" opacity=".8">PLATZHALTER – KEIN QUELLBILD VORHANDEN</text>
</svg>'''
    return Response(svg, media_type="image/svg+xml",
                    headers={"Cache-Control": "public, max-age=86400"})


# --- Betrieb ----------------------------------------------------------------

@app.get("/api/status")
def status() -> dict[str, Any]:
    return {
        "version": VERSION,
        "laufzeit_s": round(time.time() - START, 1),
        "akten": len(REGISTER),
        "datenpfad": str(pfade.DATEN),
        "kiwix": pfade.KIWIX_URL,
        "llama": pfade.LLAMA_URL,
        "modus": "prototyp",
    }


STATIC = APP_DIR / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")


def _fassung() -> str:
    """Kennung der ausgelieferten Oberflaeche.

    Haengt an den Verweisen auf CSS und JS. Ohne sie zeigt ein Browser nach
    einem Update der Box weiter die alte Fassung aus seinem Zwischenspeicher -
    beim Entwickeln genauso wie im Betrieb. Der juengste Zeitstempel unter
    static/ aendert sich bei jeder Aenderung und sonst nie.
    """
    neueste = max((f.stat().st_mtime for f in STATIC.rglob("*") if f.is_file()),
                  default=0.0)
    return f"{VERSION}-{int(neueste)}"


@app.get("/", response_class=HTMLResponse)
def wurzel() -> HTMLResponse:
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(
        html.replace("__FASSUNG__", _fassung()),
        headers={"Cache-Control": "no-cache"},
    )


@app.exception_handler(404)
async def nicht_gefunden(request, exc):  # type: ignore[no-untyped-def]
    if request.url.path.startswith("/api/"):
        return JSONResponse({"fehler": "nicht gefunden"}, status_code=404)
    return wurzel()
