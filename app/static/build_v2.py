# -*- coding: utf-8 -*-
"""
Baut QUINTESSENZ V2: Startanimation und Navigation in einer Datei (v2.html)

Aufbau
    Ebene 1   fuenf Hauptgruppen auf einem Kreis (Technik, Survival, Medicine, Archive, Assistent)
    Ebene 2   beim Ueberfahren poppen die Untergruppen als Blasen um die Hauptgruppe auf
    Ebene 3   beim Ueberfahren einer Untergruppe deren Themen als kleine Blasen im zweiten Ring
    Panel     nach dem Anklicken eines Bereichs erscheinen die KI-Funktionen dazu

Nur HTML, CSS und etwas JavaScript, keine externen Dateien. Die Symbole kommen aus
icons/build_icons.py und werden eingebettet.

    python build_v2.py     ->  v2.html
"""
import json
import re
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER / "icons"))
from build_icons import ICONS, svg_text  # noqa: E402

# ---------------------------------------------------------------- Gliederung
# (Kuerzel, Beschriftung, Farbe beim Ueberfahren, Symbol aus dem Satz, Kinder)
BAUM = [
    ("TEC", "TECHNIK", "#FFB000", "ME", [
        ("EL", "ELECTRICS", "#FFB000", "EL", [
            "Grundlagen und Bauteile", "Analog und Digital", "Leistungselektronik",
            "Antriebe und Umrichter", "Regelung und Sensorik", "Steuerungen und Relaislogik",
            "Messen und Fehlersuche", "Hochspannung", "Funk und Antennen"]),
        ("ME", "MECHANICS", "#FF6A00", "ME", [
            "Statik und Festigkeit", "Maschinenelemente", "Werkstoffe",
            "Fertigung und Schweissen", "Pneumatik und Hydraulik", "Fahrzeuge"]),
        ("PR", "PROGRAMMING", "#33FF66", "PR", [
            "C", "Python", "Bash und Linux", "Mikrocontroller", "Netzwerk"]),
    ]),
    ("SUR", "SURVIVAL", "#FFA76B", "SV", [
        ("SV", "SUPPLY", "#FFA76B", "SV", [
            "Nahrung haltbar machen", "Pflanzen und Pilze", "Feuer und Unterschlupf",
            "Landwirtschaft", "Bauen und Holz", "Alltagsanleitungen", "Kochrezepte"]),
        ("NS", "RESTART", "#E07A3F", "NS", [
            "Abhaengigkeitsbaeume", "Metallurgie", "Chemie", "Textil und Papier",
            "Fruehe Elektrotechnik", "Gemeinschaft organisieren"]),
        ("SI", "SECURITY", "#E6E6E6", "SI", [
            "Wache und Beobachtung", "Objektschutz", "ABC-Schutz", "Strahlenschutz",
            "Quarantaene", "Orientierung und Marsch", "Recht und Fuehrung"]),
        ("EN", "ENERGY", "#FFD447", "EN", [
            "Solar und Inselanlagen", "Generatoren und Motoren", "Holzgas und Biogas",
            "Wasserkraft und Wind", "Pumpen und Sanitaer"]),
    ]),
    ("MED", "MEDICINE", "#FF4FA3", "MD", [
        ("M1", "ERSTE HILFE", "#FF4FA3", "MD", [
            "Reanimation", "Blutungskontrolle", "Wunden und Frakturen", "Schock"]),
        ("M2", "KRANKHEITEN", "#FF7AC0", "MD", [
            "Symptome und Diagnose", "Medikamente und Dosierung", "Infektionen", "Anatomie"]),
        ("M3", "OHNE ARZT", "#FFA8D6", "MD", [
            "Untersuchung", "Geburt", "Chirurgie mit einfachen Mitteln", "Zaehne",
            "Versorgung ueber Tage"]),
        ("M4", "HYGIENE", "#FFC7E4", "MD", [
            "Wasseraufbereitung", "Wasserqualitaet", "Seuchenschutz"]),
    ]),
    ("ARC", "ARCHIVE", "#FFF1B8", "AW", [
        ("AW", "WISSEN", "#FFF1B8", "AW", [
            "Wikipedia", "Buecher und Literatur", "Lehrbuecher und Kurse",
            "Woerterbuch", "Fachforen"]),
        ("KN", "MAPS", "#2EF2C0", "KN", [
            "Weltkarte", "Europa und DACH", "Deutschland", "Routing",
            "Orte in der Naehe", "Hoehenlinien"]),
    ]),
    ("ASS", "ASSISTENT", "#FF3DF5", "KI", []),
]

# KI-Funktionen im Panel: (Kennung, Beschriftung, Erklaerung, ob im Assistenten-Bereich)
FUNKTIONEN = [
    ("fragen", "FRAGE STELLEN",
     "Frage in normaler Sprache. Die Antwort kommt aus den Quellen dieses Bereichs und nennt die Fundstelle."),
    ("arbeiten", "MIT KI ARBEITEN",
     "Laengeres Gespraech im Bereich: rechnen lassen, uebersetzen, zusammenfassen, Schritt fuer Schritt anleiten."),
    ("quellen", "QUELLEN EINSEHEN",
     "Alle Archive, Handbuecher und Dokumente dieses Bereichs durchblaettern und im Original lesen."),
    ("drucken", "QUELLEN DRUCKEN",
     "Ausgewaehlte Seiten als PDF sammeln und drucken, fuer den Fall, dass kein Geraet mehr laeuft."),
    ("lehrblatt", "LEHRBLATT ERZEUGEN",
     "Eine Doppelseite zum Thema setzen: Text, Schnittzeichnung, Warnhinweise, Fehlertabelle."),
    ("foto", "FOTO ERKLAEREN",
     "Typenschild, Schaltplanausschnitt oder Bauteil fotografieren und im Zusammenhang dieses Bereichs deuten."),
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


def inline_svg(kuerzel, groesse):
    s = svg_text(kuerzel)
    s = re.sub(r'\s+width="200" height="200"', "", s, count=1)
    s = s.replace("<title>", f'<title data-size="{groesse}">', 1)
    # Schildnamen im Symbol weglassen, die Beschriftung steht in der Blase
    s = re.sub(r'<text class="schild".*?</text>', "", s, flags=re.S)
    return s.strip()


def main():
    # Baum als JSON fuer das Skript, Symbole getrennt als HTML-Schnipsel
    gebraucht = set()
    baum = []
    for k, name, farbe, sym, kinder in BAUM:
        gebraucht.add(sym)
        kk = []
        for k2, name2, farbe2, sym2, themen in kinder:
            gebraucht.add(sym2)
            kk.append({"id": k2, "name": name2, "farbe": farbe2, "sym": sym2, "themen": themen})
        baum.append({"id": k, "name": name, "farbe": farbe, "sym": sym, "kinder": kk})

    symbole = "\n".join(
        f'<template id="sym-{k}">{inline_svg(k, 200)}</template>' for k in sorted(gebraucht))

    vorlage = (HIER / "v2_vorlage.html").read_text(encoding="utf-8")
    html = (vorlage
            .replace("/*BAUM*/", json.dumps(baum, ensure_ascii=False))
            .replace("/*FUNKTIONEN*/", json.dumps(
                [{"id": a, "name": b, "text": c} for a, b, c in FUNKTIONEN], ensure_ascii=False))
            .replace("/*BOOT*/", json.dumps(BOOT, ensure_ascii=False))
            .replace("<!--SYMBOLE-->", symbole))
    (HIER / "v2.html").write_text(html, encoding="utf-8", newline="\n")
    print("v2.html geschrieben:", HIER / "v2.html", f"({len(html)//1024} KB)")


if __name__ == "__main__":
    main()
