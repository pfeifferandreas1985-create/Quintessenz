"""Adapter fuer eigenes Material: own/fahrzeuge und own/rebuild.

Das sind die einzigen Quellen, die HEUTE schon vollstaendig vorliegen. Sie
liefern echte Akten, keine Demo-Daten - daran laesst sich pruefen, ob das
Papier-Template mit echten, unsortierten Daten zurechtkommt.

  fahrzeuge.db  -> je Fahrzeug 5 Akten (Kenndaten, Teile, Schwachstellen,
                   Wartungsplan, Dokumente)
  rebuild_trees.db -> je Technologie 1 Akte, je Prozess 1 Akte

Das Feld verified=0 bedeutet: der Wert stammt aus dem Gedaechtnis und ist
nicht gegen das Handbuch geprueft. Das wird als Stempel PRUEFEN sichtbar
gemacht, nicht verschwiegen.
"""
from __future__ import annotations

import re
import sqlite3
from typing import Any

import pfade
from akte import (
    Akte, Quelle, code, h, infokasten, p, tab, ul, warnung,
)

BEREICH_FZ = "eigene-fahrzeuge"
BEREICH_RB = "zivilisationsneustart"

# Fahrzeug-ID -> Themen-Slug aus bereiche.yaml
THEMA_FZ = {
    "defender": "land-rover-defender-110-td5",
    "mini": "rover-mini-cooper-1-3i",
    "vespa": "vespa-v50-n-v5a1t-1963",
}
THEMA_RB_TECH = "abhaengigkeitsbaeume"
# tech.category -> Themen-Slug; alles Uebrige landet bei den Abhaengigkeitsbaeumen
THEMA_RB_KATEGORIE = {
    "Metallurgie": "metallurgie",
    "Chemie": "chemie",
    "Textil": "textil-leder-papier-druck",
    "Elektrotechnik": "fruehe-elektrotechnik-von-grund-auf",
    "Schonfrist/Salvage": "was-nach-dem-kollaps-wie",
}

SKALA_ERKLAERT = {
    "Haushalt": "eine Person mit Handwerkzeug",
    "Dorf": "Werkstatt, Schmiede, einige Helfer",
    "Region": "arbeitsteilige Produktion, Hunderte Menschen",
    "Salvage": "nicht neu herstellbar – nur bergen und erhalten",
}


def _verbinde(pfad) -> sqlite3.Connection | None:
    if not pfad.is_file():
        return None
    con = sqlite3.connect(f"file:{pfad}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def _md_zu_bloecken(text: str) -> list[dict[str, Any]]:
    """Sehr kleiner Markdown-Leser: nummerierte Schritte und Absaetze."""
    if not text:
        return []
    bloecke: list[dict[str, Any]] = []
    schritte: list[str] = []
    for zeile in (z.strip() for z in text.split("\n")):
        if not zeile:
            continue
        m = re.match(r"^\d+\.\s*(.+)$", zeile)
        if m:
            schritte.append(m.group(1))
            continue
        if schritte:
            bloecke.append(ul(*schritte, geordnet=True))
            schritte = []
        bloecke.append(p(zeile))
    if schritte:
        bloecke.append(ul(*schritte, geordnet=True))
    return bloecke


# --- Fahrzeuge --------------------------------------------------------------

def _fz_quelle(kennung: str, tabelle: str) -> Quelle:
    return Quelle(
        typ="eigen", name="Eigene Fahrzeugakte",
        datei="own/fahrzeuge/fahrzeuge.db", kennung=f"{kennung} · Tabelle {tabelle}",
        lizenz="Eigenes Material", nur_lokal=True,
        original_url=f"/api/akte/{kennung}/original",
    )


def _stempel(ungeprueft: int) -> list[str]:
    return ["NUR LOKAL"] + (["PRÜFEN"] if ungeprueft else [])


def fahrzeug_akten() -> list[Akte]:
    con = _verbinde(pfade.FAHRZEUGE_DB)
    if con is None:
        return []
    akten: list[Akte] = []
    fahrzeuge = con.execute("SELECT * FROM vehicle ORDER BY id").fetchall()

    for fz in fahrzeuge:
        vid = fz["id"]
        thema = THEMA_FZ.get(vid, "alle-drei")
        andere = [
            {"id": f"fz-{a['id']}-kenndaten", "titel": f"{a['name']} – Kenndaten"}
            for a in fahrzeuge if a["id"] != vid
        ]

        # --- Kenndaten -----------------------------------------------------
        specs = con.execute(
            "SELECT * FROM spec WHERE vehicle_id=? ORDER BY category, key", (vid,)
        ).fetchall()
        ungeprueft = sum(1 for s in specs if not s["verified"])
        inhalt: list[dict[str, Any]] = [
            infokasten("Fahrzeug", [
                ["Bezeichnung", fz["name"] or ""],
                ["Typschlüssel", fz["model_code"] or ""],
                ["Baujahr", fz["year"] or ""],
                ["Motor", fz["engine"] or ""],
                ["Fahrgestellnummer", fz["vin"] or "— nicht eingetragen"],
                ["Motornummer", fz["engine_no"] or "— nicht eingetragen"],
                ["Kennzeichen", fz["plate"] or "—"],
            ]),
        ]
        if fz["notes"]:
            inhalt += [h("Anmerkungen"), p(fz["notes"])]
        if ungeprueft:
            inhalt.append(warnung(
                "Nicht alle Werte sind geprüft",
                f"{ungeprueft} von {len(specs)} Kenndaten stammen aus dem Gedächtnis und "
                "sind nicht gegen das Werkstatthandbuch abgeglichen. Sie sind in der "
                "Spalte „Geprüft“ mit — gekennzeichnet. Vor Arbeiten am Fahrzeug "
                "gegen das Handbuch prüfen.",
                stufe="achtung",
            ))
        for kategorie in dict.fromkeys(s["category"] for s in specs):
            zeilen = [
                [s["key"], f"{s['value']} {s['unit'] or ''}".strip(),
                 s["source"] or "", "✓" if s["verified"] else "—"]
                for s in specs if s["category"] == kategorie
            ]
            inhalt += [
                h(str(kategorie)),
                tab(["Größe", "Wert", "Herkunft", "Geprüft"], zeilen,
                    ausrichtung=["l", "r", "l", "c"]),
            ]
        akten.append(Akte(
            id=f"fz-{vid}-kenndaten", titel=f"{fz['name']} – Kenndaten",
            untertitel="Füllmengen, Drehmomente, Einstellwerte",
            bereich_id=BEREICH_FZ, thema_id=thema, tiefe="REFERENZ", sprache="DE",
            quelle=_fz_quelle(f"fz-{vid}-kenndaten", "vehicle + spec"),
            stempel=_stempel(ungeprueft), inhalt=inhalt, verwandt=andere,
        ))

        # --- Verschleissteile ----------------------------------------------
        teile = con.execute(
            "SELECT * FROM part WHERE vehicle_id=? ORDER BY grp, name", (vid,)
        ).fetchall()
        if teile:
            inhalt = [p(
                f"Stückliste der Verschleiß- und Ersatzteile für {fz['name']}. "
                f"{len(teile)} Positionen in "
                f"{len(set(t['grp'] for t in teile))} Baugruppen. Die Spalte Lager zählt, "
                "was tatsächlich vorrätig ist."
            )]
            for grp in dict.fromkeys(t["grp"] for t in teile):
                zeilen = [
                    [t["name"], t["oem_no"] or "", t["alt_no"] or "", t["qty"] or "",
                     t["interval"] or "", str(t["stock"] or 0)]
                    for t in teile if t["grp"] == grp
                ]
                inhalt += [
                    h(str(grp)),
                    tab(["Teil", "OEM-Nummer", "Alternative", "Anz.", "Intervall", "Lager"],
                        zeilen, ausrichtung=["l", "l", "l", "r", "l", "r"]),
                ]
            akten.append(Akte(
                id=f"fz-{vid}-teile", titel=f"{fz['name']} – Verschleißteile",
                untertitel="Stückliste mit OEM-Nummern und Lagerbestand",
                bereich_id=BEREICH_FZ, thema_id=thema, tiefe="REFERENZ", sprache="DE",
                quelle=_fz_quelle(f"fz-{vid}-teile", "part"),
                stempel=_stempel(sum(1 for t in teile if not t["verified"])),
                inhalt=inhalt, verwandt=andere,
            ))

        # --- Schwachstellen -------------------------------------------------
        probleme = con.execute(
            "SELECT * FROM issue WHERE vehicle_id=? "
            "ORDER BY CASE severity WHEN 'hoch' THEN 0 WHEN 'mittel' THEN 1 ELSE 2 END",
            (vid,),
        ).fetchall()
        if probleme:
            inhalt = [p(
                f"Bekannte Schwachstellen und typische Fehlerbilder des {fz['name']}, "
                "nach Schwere sortiert. Jeder Eintrag nennt Symptom, Ursache und Abhilfe."
            )]
            for prob in probleme:
                schwere = (prob["severity"] or "").lower()
                inhalt.append(h(prob["symptom"] or "Ohne Bezeichnung", 3))
                inhalt.append(infokasten("", [
                    ["Ursache", prob["cause"] or "—"],
                    ["Abhilfe", prob["fix"] or "—"],
                    ["Schwere", prob["severity"] or "—"],
                    ["Herkunft", prob["source"] or "eigene Aufzeichnung"],
                ]))
                if schwere == "hoch":
                    inhalt.append(warnung(
                        "Liegenbleiber", "Dieser Fehler führt typischerweise zum Ausfall "
                        "unterwegs. Ersatzteil und Werkzeug gehören auf längeren Fahrten "
                        "mitgeführt.", stufe="achtung",
                    ))
            akten.append(Akte(
                id=f"fz-{vid}-schwachstellen", titel=f"{fz['name']} – Schwachstellen",
                untertitel="Symptom, Ursache, Abhilfe",
                bereich_id=BEREICH_FZ, thema_id=thema, tiefe="PRAXIS", sprache="DE",
                quelle=_fz_quelle(f"fz-{vid}-schwachstellen", "issue"),
                stempel=["NUR LOKAL"], inhalt=inhalt, verwandt=andere,
            ))

        # --- Wartungsplan ---------------------------------------------------
        wartung = con.execute(
            "SELECT * FROM maintenance WHERE vehicle_id=? ORDER BY rowid", (vid,)
        ).fetchall()
        if wartung:
            zeilen = [
                [w["task"], w["interval_km"] or "—", w["interval_time"] or "—",
                 w["notes"] or "", "✓" if w["verified"] else "—"]
                for w in wartung
            ]
            akten.append(Akte(
                id=f"fz-{vid}-wartung", titel=f"{fz['name']} – Wartungsplan",
                untertitel=f"{len(wartung)} Positionen",
                bereich_id=BEREICH_FZ, thema_id=thema, tiefe="PRAXIS", sprache="DE",
                quelle=_fz_quelle(f"fz-{vid}-wartung", "maintenance"),
                stempel=_stempel(sum(1 for w in wartung if not w["verified"])),
                verwandt=andere,
                inhalt=[
                    p("Wartungsplan. Maßgebend ist immer das zuerst erreichte Intervall – "
                      "Kilometerstand oder Zeit."),
                    tab(["Arbeit", "km", "Zeit", "Hinweis", "Geprüft"], zeilen,
                        ausrichtung=["l", "r", "l", "l", "c"]),
                ],
            ))

        # --- Dokumente ------------------------------------------------------
        docs = con.execute(
            "SELECT * FROM doc WHERE vehicle_id=? ORDER BY priority, title", (vid,)
        ).fetchall()
        if docs:
            inhalt = [p(
                "Welche Unterlagen zu diesem Fahrzeug gehören, woher sie stammen und "
                "unter welcher Lizenz sie stehen. Kommerzielle Werke werden nicht "
                "weitergegeben."
            )]
            for d in docs:
                inhalt.append(h(d["title"] or "", 3))
                inhalt.append(infokasten("", [
                    ["Art", d["kind"] or "—"],
                    ["Herausgeber", d["publisher"] or "—"],
                    ["Lizenz", d["license"] or "—"],
                    ["Bezug", d["where_to_get"] or "—"],
                    ["Ablage", d["local_path"] or "—"],
                ]))
            akten.append(Akte(
                id=f"fz-{vid}-dokumente", titel=f"{fz['name']} – Dokumente",
                untertitel="Handbücher, Kataloge, Zeichnungen",
                bereich_id=BEREICH_FZ, thema_id=thema, tiefe="REFERENZ", sprache="DE",
                quelle=_fz_quelle(f"fz-{vid}-dokumente", "doc"),
                stempel=["NUR LOKAL"], inhalt=inhalt, verwandt=andere,
            ))

    con.close()
    return akten


# --- Zivilisationsneustart ---------------------------------------------------

def rebuild_akten() -> list[Akte]:
    con = _verbinde(pfade.REBUILD_DB)
    if con is None:
        return []
    akten: list[Akte] = []

    techs = {r["id"]: r for r in con.execute("SELECT * FROM tech ORDER BY name")}
    eingaenge: dict[str, list[sqlite3.Row]] = {}
    verwendet: dict[str, list[str]] = {}
    for r in con.execute("SELECT * FROM tech_input"):
        eingaenge.setdefault(r["tech_id"], []).append(r)
        verwendet.setdefault(r["input_id"], []).append(r["tech_id"])
    prozesse: dict[str, list[sqlite3.Row]] = {}
    for r in con.execute("SELECT * FROM process ORDER BY name"):
        prozesse.setdefault(r["produces"], []).append(r)

    def quelle(kennung: str, tabelle: str, src: str) -> Quelle:
        return Quelle(
            typ="eigen", name="Abhängigkeitsbäume (eigenes Material)",
            datei="own/rebuild/rebuild_trees.db",
            kennung=f"{kennung} · Tabelle {tabelle}",
            lizenz="Eigenes Material", autor=src or "", nur_lokal=True,
            original_url=f"/api/akte/{kennung}/original",
        )

    for tid, t in techs.items():
        thema = THEMA_RB_KATEGORIE.get(t["category"] or "", THEMA_RB_TECH)
        inhalt: list[dict[str, Any]] = [
            infokasten("Einordnung", [
                ["Kategorie", t["category"] or "—"],
                ["Kleinste tragfähige Stufe",
                 f"{t['min_viable_scale']} – {SKALA_ERKLAERT.get(t['min_viable_scale'], '')}"],
                ["Technikstand", t["era_equivalent"] or "—"],
                ["Haltbarkeit geborgener Stücke", t["salvage_lifetime"] or "—"],
            ]),
        ]
        if t["description_md"]:
            inhalt += _md_zu_bloecken(t["description_md"])

        if t["min_viable_scale"] == "Salvage":
            inhalt.append(warnung(
                "Nicht rekonstruierbar",
                "Diese Technologie lässt sich mit den Mitteln einer Region nicht neu "
                "herstellen. Vorhandene Exemplare sind zu bergen und so lange wie "
                "möglich zu erhalten. Ersatz durch eine einfachere Stufe planen.",
                stufe="achtung",
            ))

        eing = eingaenge.get(tid, [])
        if eing:
            inhalt += [
                h("Was hineingeht"),
                tab(["Vorstufe", "Funktion", "Menge", "Ersatz"],
                    [[techs.get(e["input_id"], {"name": e["input_id"]})["name"],
                      e["role"] or "", e["quantity_note"] or "", e["substitute"] or "—"]
                     for e in eing]),
            ]
        wird_gebraucht = verwendet.get(tid, [])
        if wird_gebraucht:
            inhalt += [
                h("Wo es gebraucht wird"),
                ul(*[techs.get(w, {"name": w})["name"] for w in wird_gebraucht]),
            ]
        for pr in prozesse.get(tid, []):
            inhalt.append(h(f"Herstellung: {pr['name']}"))
            inhalt.append(infokasten("", [
                ["Eingangsstoffe", pr["inputs"] or "—"],
                ["Werkzeug", pr["tools"] or "—"],
                ["Temperatur", pr["temperature_c"] or "—"],
                ["Stufe", pr["scale"] or "—"],
            ]))
            if pr["hazards"]:
                inhalt.append(warnung("Gefahren", pr["hazards"], stufe="gefahr"))
            inhalt += _md_zu_bloecken(pr["steps_md"] or "")

        akten.append(Akte(
            id=f"rb-{tid}", titel=t["name"],
            untertitel=t["category"] or "",
            bereich_id=BEREICH_RB, thema_id=thema,
            tiefe="PRAXIS" if prozesse.get(tid) else "REFERENZ", sprache="DE",
            quelle=quelle(f"rb-{tid}", "tech", t["source"] or ""),
            stempel=["NUR LOKAL"], inhalt=inhalt,
            verwandt=[
                {"id": f"rb-{e['input_id']}",
                 "titel": techs.get(e["input_id"], {"name": e["input_id"]})["name"]}
                for e in eing if e["input_id"] in techs
            ][:8],
        ))

    con.close()
    return akten


def alle() -> list[Akte]:
    return fahrzeug_akten() + rebuild_akten()
