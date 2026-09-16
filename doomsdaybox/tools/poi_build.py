# -*- coding: utf-8 -*-
"""
POI-Datenbank fuer die DoomsdayBox aus einer OSM-PBF-Datei bauen.

Liest Punkte UND Flaechen (Wege), damit Krankenhaeuser, Feuerwehren, Supermaerkte
usw. auch dann gefunden werden, wenn sie als Gebaeude gezeichnet sind. Flaechen
bekommen den Mittelwert ihrer Stuetzpunkte als Lage. Multipolygon-Relationen
werden nicht aufgeloest (selten, meist grosse Klinikgelaende, deren Gebaeude
ohnehin einzeln erfasst sind).

Zwei Durchlaeufe ueber die PBF, gefiltert in C++ (pyosmium >= 4.0), Speicherbedarf
unter 1 GB. Laufzeit fuer germany-latest.osm.pbf (4,8 GB): etwa 10-30 Minuten.

    python poi_build.py D:/DoomsdayBox/maps/germany-latest.osm.pbf D:/DoomsdayBox/maps/poi.sqlite

Schema:  poi(id, otype 'n'|'w', lat, lon, key, kind, name, tags JSON)
         poi_fts  FTS5 ueber name (fuer die Suche im Terminal)
"""
import json
import os
import sqlite3
import sys
import time

import osmium
from osmium.filter import IdFilter, KeyFilter

# Was gesucht wird: Schluessel -> erlaubte Werte. Auswahl nach Nutzen im Notfall:
# Versorgung, Wasser, Medizin, Sicherheit, Werkstatt/Material, Unterkunft, Energie.
KEYS = {
    "amenity": {
        "hospital", "clinic", "doctors", "dentist", "veterinary", "pharmacy",
        "drinking_water", "water_point", "fuel", "charging_station",
        "fire_station", "police", "shelter", "toilets", "place_of_worship",
        "townhall", "school", "community_centre", "social_facility",
    },
    "shop": {
        "hardware", "doityourself", "electronics", "agrarian", "farm",
        "supermarket", "chemist", "medical_supply", "outdoor", "hunting", "gas",
        "car_repair", "car_parts", "motorcycle", "motorcycle_repair", "bicycle",
        "trade", "garden_centre",
    },
    "craft": {
        "electrician", "metal_construction", "blacksmith", "welder", "plumber",
        "carpenter", "sawmill", "electronics_repair", "agricultural_engines",
    },
    "man_made": {"water_well", "water_tower", "windmill", "watermill", "reservoir_covered"},
    "natural": {"spring"},
    "emergency": {"defibrillator", "water_tank", "assembly_point", "siren"},
    "tourism": {"camp_site", "alpine_hut", "wilderness_hut"},
    "power": {"plant", "substation", "generator"},
}


def treffer(tags):
    """Erstes passendes (key, value) oder None."""
    for k, vals in KEYS.items():
        v = tags.get(k)
        if v in vals:
            return k, v
    return None


def main(pbf, ziel):
    t0 = time.time()
    tmp = ziel + ".neu"
    if os.path.exists(tmp):
        os.remove(tmp)
    con = sqlite3.connect(tmp)
    con.execute("PRAGMA journal_mode=OFF")
    con.execute("PRAGMA synchronous=OFF")
    con.execute("CREATE TABLE poi(id INTEGER, otype TEXT, lat REAL, lon REAL, key TEXT, kind TEXT, "
                "name TEXT, tags TEXT, PRIMARY KEY(otype, id))")

    keyfilter = KeyFilter(*KEYS.keys())

    # ---- Durchlauf 1: Punkte direkt schreiben, Wege vormerken --------------------------
    wege = {}          # way_id -> (key, kind, name, tags_json, [node_refs])
    knoten_noetig = set()
    n_pt = 0
    fp = osmium.FileProcessor(pbf, osmium.osm.NODE | osmium.osm.WAY).with_filter(keyfilter)
    for o in fp:
        tags = dict(o.tags)
        tr = treffer(tags)
        if not tr:
            continue
        k, v = tr
        if o.is_node():
            con.execute("INSERT OR IGNORE INTO poi VALUES(?,?,?,?,?,?,?,?)",
                        (o.id, "n", o.location.lat, o.location.lon, k, v, tags.get("name"),
                         json.dumps(tags, ensure_ascii=False)))
            n_pt += 1
        else:
            refs = [n.ref for n in o.nodes]
            if not refs:
                continue
            wege[o.id] = (k, v, tags.get("name"), json.dumps(tags, ensure_ascii=False), refs)
            knoten_noetig.update(refs)
    con.commit()
    print(f"Durchlauf 1: {n_pt} Punkte, {len(wege)} Flaechen, {len(knoten_noetig)} Stuetzpunkte noetig "
          f"({time.time() - t0:.0f} s)", flush=True)

    # ---- Durchlauf 2: Koordinaten der Stuetzpunkte holen ------------------------------
    koord = {}
    fp2 = osmium.FileProcessor(pbf, osmium.osm.NODE).with_filter(IdFilter(knoten_noetig))
    for n in fp2:
        if n.location.valid():
            koord[n.id] = (n.location.lat, n.location.lon)
    print(f"Durchlauf 2: {len(koord)} Koordinaten ({time.time() - t0:.0f} s)", flush=True)

    n_fl = 0
    for wid, (k, v, name, tj, refs) in wege.items():
        pts = [koord[r] for r in refs if r in koord]
        if not pts:
            continue
        # geschlossener Ring: letzten Punkt nicht doppelt zaehlen
        if len(pts) > 1 and refs[0] == refs[-1]:
            pts = pts[:-1]
        lat = sum(p[0] for p in pts) / len(pts)
        lon = sum(p[1] for p in pts) / len(pts)
        con.execute("INSERT OR IGNORE INTO poi VALUES(?,?,?,?,?,?,?,?)",
                    (wid, "w", lat, lon, k, v, name, tj))
        n_fl += 1
    con.commit()

    con.execute("CREATE INDEX idx_kind ON poi(kind)")
    con.execute("CREATE INDEX idx_pos ON poi(lat, lon)")
    con.execute("CREATE VIRTUAL TABLE poi_fts USING fts5(name, kind, content='poi', content_rowid='rowid')")
    con.execute("INSERT INTO poi_fts(rowid, name, kind) SELECT rowid, name, kind FROM poi")
    con.execute("CREATE TABLE meta(k TEXT PRIMARY KEY, v TEXT)")
    con.execute("INSERT INTO meta VALUES('quelle', ?)", (os.path.basename(pbf),))
    con.execute("INSERT INTO meta VALUES('erstellt', ?)", (time.strftime("%Y-%m-%d"),))
    con.execute("INSERT INTO meta VALUES('lizenz', 'OpenStreetMap-Mitwirkende, ODbL 1.0')")
    con.commit()
    gesamt = con.execute("SELECT count(*) FROM poi").fetchone()[0]
    stat = con.execute("SELECT kind, count(*) FROM poi GROUP BY kind ORDER BY 2 DESC").fetchall()
    con.execute("VACUUM")
    con.close()

    os.replace(tmp, ziel)
    print(f"fertig: {gesamt} Eintraege ({n_pt} Punkte + {n_fl} Flaechen) -> {ziel} "
          f"({os.path.getsize(ziel) / 1e6:.0f} MB, {time.time() - t0:.0f} s)")
    for kind, n in stat:
        print(f"  {kind:22s} {n:7d}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
