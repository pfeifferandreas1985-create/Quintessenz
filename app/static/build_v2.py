# -*- coding: utf-8 -*-
"""
Baut QUINTESSENZ V2: Startanimation und Navigation in einer Datei (v2.html).

Navigation
    Ein Ring um eine Mitte. Was man anwaehlt, rueckt in die Mitte, alles Uebrige
    verschwindet nach innen; darum herum poppen die Unterpunkte auf. Das gilt auf jeder
    Ebene, bis hinunter zu den KI-Funktionen. Kein Seitenmenue, alles sind Symbole.

Symbole
    Aus glyphen.py, alle im gleichen Strich. Jeder Knoten hat eins, auch die Themen und
    die KI-Funktionen.

    python build_v2.py     ->  v2.html
"""
import json
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
from glyphen import GLYPHEN  # noqa: E402


def k(kennung, titel, glyph, farbe=None, kinder=()):
    return {"id": kennung, "name": titel, "glyph": glyph, "farbe": farbe,
            "kinder": list(kinder)}


# ---------------------------------------------------------------- Gliederung
BAUM = [
    k("TEC", "TECHNOLOGY", "technik", "#FFB000", [
        k("EL", "ELECTRICS", "blitz", "#FFB000", [
            k("el1", "Fundamentals & Components", "bauteil"),
            k("el2", "Analog Circuits", "analog"),
            k("el3", "Digital Circuits", "digital"),
            k("el4", "Power Electronics", "leistung"),
            k("el5", "Drives & Inverters", "motor"),
            k("el6", "Control Systems", "regler"),
            k("el7", "Sensors", "sensor"),
            k("el8", "Relay Logic & PLC", "relais"),
            k("el9", "Measurement & Diagnostics", "messen"),
            k("el10", "High Voltage", "hochspannung"),
            k("el11", "Radio & Antennas", "antenne"),
        ]),
        k("ME", "MECHANICS", "zahnrad", "#FF6A00", [
            k("me1", "Statics & Strength", "traeger"),
            k("me2", "Machine Elements", "lager"),
            k("me3", "Materials", "werkstoff"),
            k("me4", "Manufacturing & Welding", "schweissen"),
            k("me5", "Pneumatics & Hydraulics", "hydraulik"),
            k("me6", "Vehicles", "fahrzeug"),
        ]),
        k("PR", "PROGRAMMING", "terminal", "#33FF66", [
            k("pr1", "C", "code"),
            k("pr2", "Python", "schlange"),
            k("pr3", "Bash & Linux", "terminal"),
            k("pr4", "Microcontrollers", "chip"),
            k("pr5", "Networking", "netzwerk"),
        ]),
    ]),
    k("SUR", "SURVIVAL", "survival", "#FFA76B", [
        k("SV", "SUPPLY", "glas", "#FFA76B", [
            k("sv1", "Food Preservation", "glas"),
            k("sv2", "Plants & Fungi", "pflanze"),
            k("sv3", "Fire & Shelter", "feuer"),
            k("sv4", "Farming", "acker"),
            k("sv5", "Building & Timber", "haus"),
            k("sv6", "Everyday How-To", "anleitung"),
            k("sv7", "Recipes", "topf"),
        ]),
        k("NS", "RESTART", "amboss", "#E07A3F", [
            k("ns1", "Dependency Trees", "netzwerk"),
            k("ns2", "Metallurgy", "ofen"),
            k("ns3", "Chemistry", "chemie"),
            k("ns4", "Textiles & Paper", "faden"),
            k("ns5", "Early Electrics", "gluehbirne"),
            k("ns6", "Community", "gemeinschaft"),
        ]),
        k("SI", "SECURITY", "schild", "#E6E6E6", [
            k("si1", "Watch & Observation", "auge"),
            k("si2", "Site Protection", "schild"),
            k("si3", "CBRN Protection", "maske"),
            k("si4", "Radiation Safety", "strahlung"),
            k("si5", "Quarantine", "seuche"),
            k("si6", "Navigation & March", "kompass"),
            k("si7", "Law & Leadership", "waage"),
        ]),
        k("EN", "ENERGY", "sonne", "#FFD447", [
            k("en1", "Solar & Off-Grid", "sonne"),
            k("en2", "Generators & Engines", "generator"),
            k("en3", "Wood Gas & Biogas", "gas"),
            k("en4", "Hydro & Wind", "wasserrad"),
            k("en5", "Pumps & Sanitation", "pumpe"),
        ]),
    ]),
    k("MED", "MEDICINE", "medizin", "#FF4FA3", [
        k("M1", "FIRST AID", "herz", "#FF4FA3", [
            k("m11", "Resuscitation", "herz"),
            k("m12", "Bleeding Control", "kreuz"),
            k("m13", "Wounds & Fractures", "skalpell"),
            k("m14", "Shock", "stethoskop"),
        ]),
        k("M2", "DISEASES", "mikrobe", "#FF7AC0", [
            k("m21", "Symptoms & Diagnosis", "stethoskop"),
            k("m22", "Medication", "pille"),
            k("m23", "Infections", "mikrobe"),
            k("m24", "Anatomy", "herz"),
        ]),
        k("M3", "WITHOUT A DOCTOR", "skalpell", "#FFA8D6", [
            k("m31", "Examination", "stethoskop"),
            k("m32", "Childbirth", "baby"),
            k("m33", "Field Surgery", "skalpell"),
            k("m34", "Dental", "zahn"),
            k("m35", "Prolonged Care", "spritze"),
        ]),
        k("M4", "HYGIENE", "tropfen", "#FFC7E4", [
            k("m41", "Water Treatment", "tropfen"),
            k("m42", "Water Quality", "mikrobe"),
            k("m43", "Epidemic Control", "seuche"),
        ]),
    ]),
    k("ARC", "ARCHIVE", "archiv", "#FFF1B8", [
        k("AW", "KNOWLEDGE", "buch", "#FFF1B8", [
            k("aw1", "Wikipedia", "globus"),
            k("aw2", "Books", "buch"),
            k("aw3", "Textbooks & Courses", "lehrblatt"),
            k("aw4", "Dictionary", "woerter"),
            k("aw5", "Q&A Archives", "forum"),
        ]),
        k("KN", "MAPS", "karte", "#2EF2C0", [
            k("kn1", "World Map", "globus"),
            k("kn2", "Europe & DACH", "karte"),
            k("kn3", "Germany", "karte"),
            k("kn4", "Routing", "route"),
            k("kn5", "Places Nearby", "ort"),
            k("kn6", "Contour Lines", "hoehe"),
        ]),
    ]),
    k("ASS", "ASSISTANT", "assistent", "#FF3DF5", []),
]

# KI-Funktionen: haengen unter jedem Knoten, der keine eigenen Unterpunkte hat
FUNKTIONEN = [
    {"id": "f1", "name": "ASK THE AI", "glyph": "fragen",
     "text": "Frage stellen, Antwort aus den Quellen des Bereichs mit Fundstelle"},
    {"id": "f2", "name": "WORK WITH AI", "glyph": "arbeiten",
     "text": "Rechnen, uebersetzen, zusammenfassen, Schritt fuer Schritt anleiten"},
    {"id": "f3", "name": "BROWSE SOURCES", "glyph": "quellen",
     "text": "Archive und Dokumente des Bereichs im Original lesen"},
    {"id": "f4", "name": "PRINT SOURCES", "glyph": "drucken",
     "text": "Seiten als PDF sammeln und drucken, fuer den Fall ohne Geraet"},
    {"id": "f5", "name": "MAKE A HANDOUT", "glyph": "lehrblatt",
     "text": "Doppelseite setzen: Text, Schnittzeichnung, Warnungen, Fehlertabelle"},
    {"id": "f6", "name": "EXPLAIN A PHOTO", "glyph": "foto",
     "text": "Typenschild oder Bauteil fotografieren und im Bereich deuten"},
    {"id": "f7", "name": "READ ALOUD", "glyph": "vorlesen",
     "text": "Antwort laut ausgeben, fuer die Bedienung mit schmutzigen Haenden"},
]

BOOT = [
    "QUINTESSENZ TERMINAL  //  BIOS 2.0  //  ATOMIC AGE EDITION",
    "",
    "CPU ........ ARM CORTEX-A76 x4 @ 2.4 GHZ .......... OK",
    "MEMORY ..... 16384 MB ............................ OK",
    "STORAGE .... /srv/box  740 GB, READ-ONLY ......... OK",
    "KIWIX ...... 39 ARCHIVES, 2 LANGUAGES ............ OK",
    "MAPS ....... WORLD / EUROPE / DACH / GERMANY ..... OK",
    "MODELS ..... 9 LOADED, NO CLOUD .................. OK",
    "NETWORK .... NONE (BY DESIGN) .................... OK",
    "",
    "SCANNING KNOWLEDGE GROUPS ........................ 5 FOUND",
    "INITIALIZING INTERFACE",
]


def main():
    fehlend = set()

    def pruefe(knoten):
        for x in knoten:
            if x["glyph"] not in GLYPHEN:
                fehlend.add(x["glyph"])
            pruefe(x["kinder"])

    pruefe(BAUM)
    for f in FUNKTIONEN:
        if f["glyph"] not in GLYPHEN:
            fehlend.add(f["glyph"])
    if fehlend:
        print("WARNUNG, Symbole fehlen:", ", ".join(sorted(fehlend)))

    # Als echte SVG-Definitionen ausgeben, nicht als <template>. In einer HTML-Vorlage
    # landen <path> und Co. im HTML-Namensraum und werden nie gezeichnet.
    motive = ('<svg width="0" height="0" aria-hidden="true" style="position:absolute"><defs>'
              + "".join(f'<g id="g-{name}">{inhalt}</g>'
                         for name, inhalt in sorted(GLYPHEN.items()))
              + '</defs></svg>')
    vorlage = (HIER / "v2_vorlage.html").read_text(encoding="utf-8")
    html = (vorlage
            .replace("/*BAUM*/", json.dumps(BAUM, ensure_ascii=False))
            .replace("/*FUNKTIONEN*/", json.dumps(FUNKTIONEN, ensure_ascii=False))
            .replace("/*BOOT*/", json.dumps(BOOT, ensure_ascii=False))
            .replace("<!--SYMBOLE-->", motive))
    (HIER / "v2.html").write_text(html, encoding="utf-8", newline="\n")
    print(f"v2.html geschrieben: {HIER / 'v2.html'} "
          f"({len(html)//1024} KB, {len(GLYPHEN)} Symbole)")


if __name__ == "__main__":
    main()
