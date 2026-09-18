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
    k("TEC", "TECHNIK", "technik", "#FFB000", [
        k("EL", "ELECTRICS", "blitz", "#FFB000", [
            k("el1", "Grundlagen und Bauteile", "bauteil"),
            k("el2", "Analogtechnik", "analog"),
            k("el3", "Digitaltechnik", "digital"),
            k("el4", "Leistungselektronik", "leistung"),
            k("el5", "Antriebe und Umrichter", "motor"),
            k("el6", "Regelung", "regler"),
            k("el7", "Sensorik", "sensor"),
            k("el8", "Steuerungen und Relais", "relais"),
            k("el9", "Messen und Fehlersuche", "messen"),
            k("el10", "Hochspannung", "hochspannung"),
            k("el11", "Funk und Antennen", "antenne"),
        ]),
        k("ME", "MECHANICS", "zahnrad", "#FF6A00", [
            k("me1", "Statik und Festigkeit", "traeger"),
            k("me2", "Maschinenelemente", "lager"),
            k("me3", "Werkstoffe", "werkstoff"),
            k("me4", "Fertigung und Schweissen", "schweissen"),
            k("me5", "Pneumatik und Hydraulik", "hydraulik"),
            k("me6", "Fahrzeuge", "fahrzeug"),
        ]),
        k("PR", "PROGRAMMING", "terminal", "#33FF66", [
            k("pr1", "C", "code"),
            k("pr2", "Python", "schlange"),
            k("pr3", "Bash und Linux", "terminal"),
            k("pr4", "Mikrocontroller", "chip"),
            k("pr5", "Netzwerk", "netzwerk"),
        ]),
    ]),
    k("SUR", "SURVIVAL", "survival", "#FFA76B", [
        k("SV", "SUPPLY", "glas", "#FFA76B", [
            k("sv1", "Haltbar machen", "glas"),
            k("sv2", "Pflanzen und Pilze", "pflanze"),
            k("sv3", "Feuer und Unterschlupf", "feuer"),
            k("sv4", "Landwirtschaft", "acker"),
            k("sv5", "Bauen und Holz", "haus"),
            k("sv6", "Alltagsanleitungen", "anleitung"),
            k("sv7", "Kochrezepte", "topf"),
        ]),
        k("NS", "RESTART", "amboss", "#E07A3F", [
            k("ns1", "Abhaengigkeitsbaeume", "netzwerk"),
            k("ns2", "Metallurgie", "ofen"),
            k("ns3", "Chemie", "chemie"),
            k("ns4", "Textil und Papier", "faden"),
            k("ns5", "Fruehe Elektrotechnik", "gluehbirne"),
            k("ns6", "Gemeinschaft", "gemeinschaft"),
        ]),
        k("SI", "SECURITY", "schild", "#E6E6E6", [
            k("si1", "Wache und Beobachtung", "auge"),
            k("si2", "Objektschutz", "schild"),
            k("si3", "ABC-Schutz", "maske"),
            k("si4", "Strahlenschutz", "strahlung"),
            k("si5", "Quarantaene", "seuche"),
            k("si6", "Orientierung und Marsch", "kompass"),
            k("si7", "Recht und Fuehrung", "waage"),
        ]),
        k("EN", "ENERGY", "sonne", "#FFD447", [
            k("en1", "Solar und Inselanlagen", "sonne"),
            k("en2", "Generatoren und Motoren", "generator"),
            k("en3", "Holzgas und Biogas", "gas"),
            k("en4", "Wasserkraft und Wind", "wasserrad"),
            k("en5", "Pumpen und Sanitaer", "pumpe"),
        ]),
    ]),
    k("MED", "MEDICINE", "medizin", "#FF4FA3", [
        k("M1", "ERSTE HILFE", "herz", "#FF4FA3", [
            k("m11", "Reanimation", "herz"),
            k("m12", "Blutungskontrolle", "kreuz"),
            k("m13", "Wunden und Frakturen", "skalpell"),
            k("m14", "Schock", "stethoskop"),
        ]),
        k("M2", "KRANKHEITEN", "mikrobe", "#FF7AC0", [
            k("m21", "Symptome und Diagnose", "stethoskop"),
            k("m22", "Medikamente", "pille"),
            k("m23", "Infektionen", "mikrobe"),
            k("m24", "Anatomie", "herz"),
        ]),
        k("M3", "OHNE ARZT", "skalpell", "#FFA8D6", [
            k("m31", "Untersuchung", "stethoskop"),
            k("m32", "Geburt", "baby"),
            k("m33", "Chirurgie einfach", "skalpell"),
            k("m34", "Zaehne", "zahn"),
            k("m35", "Versorgung ueber Tage", "spritze"),
        ]),
        k("M4", "HYGIENE", "tropfen", "#FFC7E4", [
            k("m41", "Wasseraufbereitung", "tropfen"),
            k("m42", "Wasserqualitaet", "mikrobe"),
            k("m43", "Seuchenschutz", "seuche"),
        ]),
    ]),
    k("ARC", "ARCHIVE", "archiv", "#FFF1B8", [
        k("AW", "WISSEN", "buch", "#FFF1B8", [
            k("aw1", "Wikipedia", "globus"),
            k("aw2", "Buecher", "buch"),
            k("aw3", "Lehrbuecher und Kurse", "lehrblatt"),
            k("aw4", "Woerterbuch", "woerter"),
            k("aw5", "Fachforen", "forum"),
        ]),
        k("KN", "MAPS", "karte", "#2EF2C0", [
            k("kn1", "Weltkarte", "globus"),
            k("kn2", "Europa und DACH", "karte"),
            k("kn3", "Deutschland", "karte"),
            k("kn4", "Routing", "route"),
            k("kn5", "Orte in der Naehe", "ort"),
            k("kn6", "Hoehenlinien", "hoehe"),
        ]),
    ]),
    k("ASS", "ASSISTENT", "assistent", "#FF3DF5", []),
]

# KI-Funktionen: haengen unter jedem Knoten, der keine eigenen Unterpunkte hat
FUNKTIONEN = [
    {"id": "f1", "name": "MIT KI SPRECHEN", "glyph": "fragen",
     "text": "Frage stellen, Antwort aus den Quellen des Bereichs mit Fundstelle"},
    {"id": "f2", "name": "MIT KI ARBEITEN", "glyph": "arbeiten",
     "text": "Rechnen, uebersetzen, zusammenfassen, Schritt fuer Schritt anleiten"},
    {"id": "f3", "name": "QUELLEN EINSEHEN", "glyph": "quellen",
     "text": "Archive und Dokumente des Bereichs im Original lesen"},
    {"id": "f4", "name": "QUELLEN DRUCKEN", "glyph": "drucken",
     "text": "Seiten als PDF sammeln und drucken, fuer den Fall ohne Geraet"},
    {"id": "f5", "name": "LEHRBLATT ERZEUGEN", "glyph": "lehrblatt",
     "text": "Doppelseite setzen: Text, Schnittzeichnung, Warnungen, Fehlertabelle"},
    {"id": "f6", "name": "FOTO ERKLAEREN", "glyph": "foto",
     "text": "Typenschild oder Bauteil fotografieren und im Bereich deuten"},
    {"id": "f7", "name": "VORLESEN", "glyph": "vorlesen",
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
