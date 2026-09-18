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
            k("el1", "Fundamentals", "bauteil"),
            k("el2", "Analog", "analog"),
            k("el3", "Digital", "digital"),
            k("el4", "Power", "leistung"),
            k("el5", "Drives", "motor"),
            k("el6", "Control", "regler"),
            k("el7", "Sensors", "sensor"),
            k("el8", "Relay Logic", "relais"),
            k("el9", "Measurement", "messen"),
            k("el10", "High Voltage", "hochspannung"),
            k("el11", "Radio", "antenne"),
        ]),
        k("ME", "MECHANICS", "zahnrad", "#FF6A00", [
            k("me1", "Statics", "traeger"),
            k("me2", "Machine Parts", "lager"),
            k("me3", "Materials", "werkstoff"),
            k("me4", "Manufacturing", "schweissen"),
            k("me5", "Fluid Power", "hydraulik"),
            k("me6", "Vehicles", "fahrzeug"),
        ]),
        k("PR", "PROGRAMMING", "terminal", "#33FF66", [
            k("pr1", "C", "code"),
            k("pr2", "Python", "schlange"),
            k("pr3", "Linux", "terminal"),
            k("pr4", "Embedded", "chip"),
            k("pr5", "Network", "netzwerk"),
        ]),
    ]),
    k("SUR", "SURVIVAL", "survival", "#FFA76B", [
        k("SV", "SUPPLY", "glas", "#FFA76B", [
            k("sv1", "Preserving", "glas"),
            k("sv2", "Plants", "pflanze"),
            k("sv3", "Fire & Shelter", "feuer"),
            k("sv4", "Farming", "acker"),
            k("sv5", "Building", "haus"),
            k("sv6", "How-To", "anleitung"),
            k("sv7", "Recipes", "topf"),
        ]),
        k("NS", "RESTART", "amboss", "#E07A3F", [
            k("ns1", "Tech Trees", "netzwerk"),
            k("ns2", "Metallurgy", "ofen"),
            k("ns3", "Chemistry", "chemie"),
            k("ns4", "Textiles", "faden"),
            k("ns5", "Early Power", "gluehbirne"),
            k("ns6", "Community", "gemeinschaft"),
        ]),
        k("SI", "SECURITY", "schild", "#E6E6E6", [
            k("si1", "Watch", "auge"),
            k("si2", "Perimeter", "schild"),
            k("si3", "CBRN", "maske"),
            k("si4", "Radiation", "strahlung"),
            k("si5", "Quarantine", "seuche"),
            k("si6", "Navigation", "kompass"),
            k("si7", "Law", "waage"),
        ]),
        k("EN", "ENERGY", "sonne", "#FFD447", [
            k("en1", "Solar", "sonne"),
            k("en2", "Generators", "generator"),
            k("en3", "Wood Gas", "gas"),
            k("en4", "Hydro & Wind", "wasserrad"),
            k("en5", "Pumps", "pumpe"),
        ]),
    ]),
    k("MED", "MEDICINE", "medizin", "#FF4FA3", [
        k("M1", "FIRST AID", "herz", "#FF4FA3", [
            k("m11", "CPR", "herz"),
            k("m12", "Bleeding", "kreuz"),
            k("m13", "Wounds", "skalpell"),
            k("m14", "Shock", "stethoskop"),
        ]),
        k("M2", "DISEASES", "mikrobe", "#FF7AC0", [
            k("m21", "Diagnosis", "stethoskop"),
            k("m22", "Medication", "pille"),
            k("m23", "Infections", "mikrobe"),
            k("m24", "Anatomy", "herz"),
        ]),
        k("M3", "NO DOCTOR", "skalpell", "#FFA8D6", [
            k("m31", "Examination", "stethoskop"),
            k("m32", "Childbirth", "baby"),
            k("m33", "Field Surgery", "skalpell"),
            k("m34", "Dental", "zahn"),
            k("m35", "Long-Term Care", "spritze"),
        ]),
        k("M4", "HYGIENE", "tropfen", "#FFC7E4", [
            k("m41", "Treatment", "tropfen"),
            k("m42", "Quality", "mikrobe"),
            k("m43", "Epidemics", "seuche"),
        ]),
    ]),
    k("ARC", "ARCHIVE", "archiv", "#FFF1B8", [
        k("AW", "KNOWLEDGE", "buch", "#FFF1B8", [
            k("aw1", "Wikipedia", "globus"),
            k("aw2", "Books", "buch"),
            k("aw3", "Textbooks", "lehrblatt"),
            k("aw4", "Dictionary", "woerter"),
            k("aw5", "Q&A", "forum"),
        ]),
        k("KN", "MAPS", "karte", "#2EF2C0", [
            k("kn1", "World Map", "globus"),
            k("kn2", "Europe", "karte"),
            k("kn3", "Germany", "karte"),
            k("kn4", "Routing", "route"),
            k("kn5", "Places", "ort"),
            k("kn6", "Contours", "hoehe"),
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
    {"id": "f3", "name": "SOURCES", "glyph": "quellen",
     "text": "Archive und Dokumente des Bereichs im Original lesen"},
    {"id": "f4", "name": "PRINT", "glyph": "drucken",
     "text": "Seiten als PDF sammeln und drucken, fuer den Fall ohne Geraet"},
    {"id": "f5", "name": "HANDOUT", "glyph": "lehrblatt",
     "text": "Doppelseite setzen: Text, Schnittzeichnung, Warnungen, Fehlertabelle"},
    {"id": "f6", "name": "PHOTO", "glyph": "foto",
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
