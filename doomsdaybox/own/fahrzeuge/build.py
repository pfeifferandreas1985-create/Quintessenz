#!/usr/bin/env python3
"""build.py – baut fahrzeuge.db aus fahrzeuge.sql und erzeugt je Fahrzeug eine Fahrzeugakte_<id>.md.
Aufruf im Ordner own/fahrzeuge:  python build.py
"""
import pathlib, sqlite3, datetime

HERE = pathlib.Path(__file__).parent
SQL = (HERE / "fahrzeuge.sql").read_text(encoding="utf-8")
DB = HERE / "fahrzeuge.db"

if DB.exists():
    DB.unlink()
con = sqlite3.connect(DB)
con.executescript(SQL)
con.commit()
con.execute("PRAGMA journal_mode=DELETE")
con.row_factory = sqlite3.Row

def flag(v):
    return "" if v else " ⚠ prüfen"

def table(rows, cols, headers):
    if not rows:
        return "_keine Einträge_\n"
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for r in rows:
        out.append("| " + " | ".join(str(r[c]) if r[c] is not None else "" for c in cols) + " |")
    return "\n".join(out) + "\n"

stamp = datetime.date.today().isoformat()
for v in con.execute("SELECT * FROM vehicle ORDER BY id"):
    vid = v["id"]
    md = [f"# Fahrzeugakte – {v['name']}", "",
          f"Stand {stamp}. Quelle: `fahrzeuge.db` (Tabelle `vehicle` = `{vid}`). "
          "Zeilen mit **⚠ prüfen** sind aus dem Gedächtnis eingetragen und gegen Werkstatthandbuch/Teilekatalog zu verifizieren.", "",
          "| Feld | Wert |", "|---|---|",
          f"| Modellcode | {v['model_code']} |", f"| Baujahr | {v['year']} |", f"| Motor | {v['engine']} |",
          f"| Fahrgestellnummer | {v['vin'] or '_eintragen_'} |", f"| Motornummer | {v['engine_no'] or '_eintragen_'} |",
          f"| Kennzeichen | {v['plate'] or '_eintragen_'} |", f"| Hinweise | {v['notes']} |", ""]

    md += ["## Kenndaten, Füllmengen, Drehmomente, Einstellwerte", ""]
    rows = con.execute("SELECT category, key, value, unit, source, verified FROM spec WHERE vehicle_id=? ORDER BY category, key", (vid,)).fetchall()
    md.append("| Kategorie | Größe | Wert | Einheit | Quelle/Hinweis | Status |")
    md.append("|---|---|---|---|---|---|")
    for r in rows:
        md.append(f"| {r['category']} | {r['key']} | {r['value']} | {r['unit'] or ''} | {r['source'] or ''} | {'✓' if r['verified'] else '⚠ prüfen'} |")
    md.append("")

    md += ["## Stückliste Verschleiß- und Ersatzteile", "",
           "Teilenummern immer mit Fahrgestellnummer im Katalog gegenprüfen. Spalte *Lager* = Anzahl im eigenen Bestand.", ""]
    rows = con.execute("SELECT grp, name, oem_no, alt_no, qty, interval, supplier, stock, verified FROM part WHERE vehicle_id=? ORDER BY grp, name", (vid,)).fetchall()
    md.append("| Gruppe | Teil | OEM-Nr. | Alternativ | Menge | Intervall | Bezug | Lager | Status |")
    md.append("|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        md.append(f"| {r['grp']} | {r['name']} | {r['oem_no'] or ''} | {r['alt_no'] or ''} | {r['qty'] or ''} | {r['interval'] or ''} | {r['supplier'] or ''} | {r['stock']} | {'✓' if r['verified'] else '⚠ prüfen'} |")
    md.append("")

    md += ["## Bekannte Schwachstellen und Fehlerbilder", ""]
    rows = con.execute("SELECT symptom, cause, fix, severity FROM issue WHERE vehicle_id=? ORDER BY CASE severity WHEN 'hoch' THEN 0 WHEN 'mittel' THEN 1 ELSE 2 END", (vid,)).fetchall()
    md.append(table(rows, ["symptom", "cause", "fix", "severity"], ["Symptom", "Ursache", "Abhilfe", "Schwere"]))

    md += ["## Wartungsplan", ""]
    rows = con.execute("SELECT task, interval_km, interval_time, notes, verified FROM maintenance WHERE vehicle_id=?", (vid,)).fetchall()
    md.append("| Arbeit | km | Zeit | Hinweis | Status |")
    md.append("|---|---|---|---|---|")
    for r in rows:
        md.append(f"| {r['task']} | {r['interval_km'] or ''} | {r['interval_time'] or ''} | {r['notes'] or ''} | {'✓' if r['verified'] else '⚠ prüfen'} |")
    md.append("")

    md += ["## Dokumente: Werkstatthandbuch, Ersatzteilkatalog, Explosionszeichnungen", ""]
    rows = con.execute("SELECT title, kind, publisher, license, where_to_get, local_path, priority FROM doc WHERE vehicle_id=? ORDER BY priority", (vid,)).fetchall()
    md.append(table(rows, ["priority", "title", "kind", "publisher", "license", "where_to_get", "local_path"],
                    ["Prio", "Titel", "Art", "Herausgeber", "Lizenz/Bezug", "Wo", "Ablage"]))

    md += ["## Logbuch", ""]
    rows = con.execute("SELECT date, km, work, parts_used, cost_eur, notes FROM logbook WHERE vehicle_id=? ORDER BY date", (vid,)).fetchall()
    md.append(table(rows, ["date", "km", "work", "parts_used", "cost_eur", "notes"], ["Datum", "km", "Arbeit", "Teile", "€", "Notiz"]))

    (HERE / f"Fahrzeugakte_{vid}.md").write_text("\n".join(md), encoding="utf-8")
    print(f"Fahrzeugakte_{vid}.md geschrieben")

n = {t: con.execute(f"SELECT count(*) FROM {t}").fetchone()[0] for t in ("vehicle", "spec", "part", "issue", "doc", "maintenance")}
print("fahrzeuge.db:", n)
con.close()
