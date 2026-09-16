"""DEMO-Akten fuer den Prototyp.

Solange zim/ und pdf/ leer sind, liefert dieses Modul Akten in exakt dem
Format, das spaeter die echten Adapter (adapters/zim.py, adapters/pdf.py,
adapters/se.py) erzeugen. Wenn die Beschaffung durch ist, wird hier nichts
umgebaut - die Demo-Quelle wird in config/quellen.yaml abgeschaltet und die
echten Adapter liefern dieselben Blocktypen.

JEDE Akte hier traegt demo=True und den Stempel "DEMO". Das Papier zeigt das
als Randvermerk. Nichts davon darf mit echtem Archivinhalt verwechselt werden.

Abbildungen: es gibt noch keine Originalbilder. Statt erfundener Grafiken
stehen ehrliche Platzhalterrahmen (/api/platzhalter.svg), die sagen, welches
Bild aus welcher Quelle spaeter an dieser Stelle steht.
"""
from __future__ import annotations

from urllib.parse import quote

from akte import (
    Akte, Quelle, bild, code, fall_antwort, fall_frage, formel, h, infokasten,
    p, seitenbild, tab, trenner, ul, warnung, zitat,
)


def ph(text: str, w: int = 640, h_: int = 380, art: str = "abbildung") -> str:
    """URL eines Platzhalterrahmens - kein erfundenes Bild, nur ein Hinweis."""
    return f"/api/platzhalter.svg?w={w}&h={h_}&art={art}&text={quote(text)}"


# ---------------------------------------------------------------------------
# 1  ELEKTROTECHNIK - ZIM-Artikel (Wikipedia DE)
# ---------------------------------------------------------------------------

OHM = Akte(
    id="et-ohmsches-gesetz",
    titel="Ohmsches Gesetz",
    untertitel="Zusammenhang von Spannung, Stromstärke und Widerstand",
    bereich_id="elektrotechnik-und-elektronik",
    thema_id="grundlagen",
    tiefe="LEHRBUCH",
    sprache="DE",
    demo=True,
    stempel=["DEMO"],
    quelle=Quelle(
        typ="zim", name="Wikipedia (Deutsch)",
        datei="wikipedia_de_all_maxi_2026-01.zim",
        kennung="A/Ohmsches_Gesetz", lizenz="CC BY-SA 4.0",
        stand="2026-01-04", autor="Wikipedia-Autoren",
        original_url="/api/akte/et-ohmsches-gesetz/original",
    ),
    verwandt=[
        {"id": "et-leitungsquerschnitt", "titel": "Strombelastbarkeit und Spannungsfall"},
        {"id": "et-mosfet-heiss", "titel": "MOSFET wird heiß, obwohl R_DS(on) klein ist"},
    ],
    inhalt=[
        p("Das <strong>ohmsche Gesetz</strong> besagt, dass die Stromstärke durch einen "
          "elektrischen Leiter proportional zur angelegten Spannung ist, solange Temperatur "
          "und übrige physikalische Bedingungen konstant bleiben. Der Proportionalitätsfaktor "
          "ist der elektrische Widerstand."),
        formel("U = R \\cdot I", "Spannung gleich Widerstand mal Stromstärke"),
        p("Dabei ist <em>U</em> die Spannung in Volt (V), <em>I</em> die Stromstärke in "
          "Ampere (A) und <em>R</em> der Widerstand in Ohm (Ω). Umgestellt ergibt sich "
          "<code>I = U / R</code> und <code>R = U / I</code>."),
        h("Geltungsbereich"),
        p("Das Gesetz ist kein Naturgesetz im strengen Sinn, sondern eine "
          "<strong>Materialeigenschaft</strong>. Bauelemente, bei denen es gilt, heißen "
          "<em>ohmsche</em> oder <em>lineare</em> Widerstände. Ihre Strom-Spannungs-Kennlinie "
          "ist eine Gerade durch den Ursprung."),
        p("Nicht ohmsch verhalten sich unter anderem:"),
        ul(
            "<strong>Halbleiterdioden</strong> – exponentielle Kennlinie, Durchlassspannung "
            "etwa 0,7 V bei Silizium",
            "<strong>Glühlampen</strong> – der Kaltwiderstand beträgt nur etwa ein Zehntel "
            "des Betriebswiderstands",
            "<strong>Heiz- und Kaltleiter</strong> (NTC, PTC) – stark temperaturabhängig",
            "<strong>Gasentladungsstrecken</strong> – abschnittsweise negativer differentieller "
            "Widerstand",
        ),
        bild(
            ph("Kennlinienfeld: ohmscher Widerstand (Gerade) gegen Diode und Glühlampe", 660, 400,
               "diagramm"),
            bildunterschrift="Strom-Spannungs-Kennlinien: der ohmsche Widerstand als Gerade, "
                             "Diode und Glühlampe als gekrümmte Kurven.",
            herkunft="Wikipedia DE, Datei: Kennlinie_Ohm.svg – CC BY-SA 4.0",
        ),
        h("Temperaturabhängigkeit"),
        p("Auch bei metallischen Leitern gilt das Gesetz nur bei konstanter Temperatur. "
          "Der Widerstand ändert sich näherungsweise linear mit der Temperatur:"),
        formel("R(\\vartheta) = R_{20} \\cdot \\left[1 + \\alpha \\cdot (\\vartheta - 20\\,^\\circ\\mathrm{C})\\right]",
               "R bei Temperatur theta gleich R bei 20 Grad mal Klammer auf 1 plus alpha mal "
               "Temperaturdifferenz zu 20 Grad Klammer zu"),
        tab(
            kopf=["Werkstoff", "α in 1/K", "Widerstand bei 80 °C (bezogen auf 20 °C)"],
            zeilen=[
                ["Kupfer", "0,00393", "+23,6 %"],
                ["Aluminium", "0,00377", "+22,6 %"],
                ["Eisen", "0,00650", "+39,0 %"],
                ["Konstantan", "0,00002", "+0,1 %"],
                ["Kohle", "−0,00050", "−3,0 %"],
            ],
            titel="Temperaturkoeffizient α gängiger Leiterwerkstoffe",
            ausrichtung=["l", "r", "r"],
            fussnote="Richtwerte für reine Werkstoffe. Legierungen weichen ab.",
        ),
        warnung(
            "Erwärmung bei der Messung beachten",
            "Eine Widerstandsmessung mit hohem Messstrom erwärmt das Bauteil und verfälscht "
            "das Ergebnis. Bei Wicklungen und Präzisionswiderständen mit kleinem Messstrom "
            "arbeiten oder den Wert auf 20 °C zurückrechnen.",
            stufe="hinweis",
        ),
        h("Leistung"),
        p("Aus dem ohmschen Gesetz folgt unmittelbar die in Wärme umgesetzte Leistung:"),
        formel("P = U \\cdot I = I^2 \\cdot R = \\frac{U^2}{R}",
               "P gleich U mal I gleich I Quadrat mal R gleich U Quadrat durch R"),
        p("Die mittlere Form <code>P = I²·R</code> erklärt, warum Leitungsverluste mit dem "
          "<em>Quadrat</em> des Stromes wachsen – und warum Energieübertragung bei hoher "
          "Spannung und kleinem Strom erfolgt."),
        h("Rechenbeispiel"),
        p("Ein Heizwiderstand von 48 Ω liegt an 230 V."),
        ul(
            "Strom: <code>I = 230 V / 48 Ω = 4,79 A</code>",
            "Leistung: <code>P = 230 V · 4,79 A = 1102 W</code>",
            "Absicherung: nächstgrößere Norm-Sicherung 6 A, Leitung mindestens 0,75 mm²",
            geordnet=True,
        ),
    ],
)


# ---------------------------------------------------------------------------
# 2  ELEKTROTECHNIK - Stack-Exchange-Fall
# ---------------------------------------------------------------------------

MOSFET = Akte(
    id="et-mosfet-heiss",
    titel="MOSFET wird heiß, obwohl R_DS(on) klein ist",
    untertitel="Electrical Engineering Stack Exchange – Frage 273891",
    bereich_id="elektrotechnik-und-elektronik",
    thema_id="konkrete-schaltungsprobleme-warum-schwingt",
    tiefe="FALL",
    sprache="EN",
    demo=True,
    stempel=["DEMO"],
    quelle=Quelle(
        typ="se", name="Electrical Engineering Stack Exchange",
        datei="stackexchange_electronics_en_all_2026-01.zim",
        kennung="questions/273891", lizenz="CC BY-SA 4.0",
        stand="2026-01-11", autor="Stack-Exchange-Beitragende",
        original_url="/api/akte/et-mosfet-heiss/original",
    ),
    verwandt=[{"id": "et-ohmsches-gesetz", "titel": "Ohmsches Gesetz"}],
    inhalt=[
        fall_frage(
            autor="mriley_", datum="2026-01-11", stimmen=34,
            blocks=[
                p("I am switching a 12&nbsp;V / 8&nbsp;A motor load with an IRLZ44N "
                  "(R<sub>DS(on)</sub> = 22&nbsp;mΩ). By my calculation the MOSFET should "
                  "dissipate <code>I² · R = 64 · 0.022 = 1.4&nbsp;W</code>, which the "
                  "TO-220 package handles easily. In practice it reaches over 120&nbsp;°C "
                  "within a minute and eventually fails."),
                p("The gate is driven directly from an Arduino pin at 5&nbsp;V through a "
                  "220&nbsp;Ω resistor. PWM frequency is 20&nbsp;kHz. What am I missing?"),
                code(
                    "analogWriteFrequency(9, 20000);\n"
                    "analogWrite(9, 180);   // ca. 70 % Tastverhältnis",
                    sprache="c", titel="Ansteuerung",
                ),
            ],
        ),
        fall_antwort(
            autor="Spehro P.", datum="2026-01-11", stimmen=58, akzeptiert=True,
            blocks=[
                p("Your calculation only covers the <strong>conduction loss</strong>. At "
                  "20&nbsp;kHz the <strong>switching loss</strong> dominates, and your gate "
                  "drive is far too weak."),
                h("1. Gate charge versus drive current", 3),
                p("The IRLZ44N needs roughly 48&nbsp;nC of gate charge. Through a 220&nbsp;Ω "
                  "resistor from a 5&nbsp;V pin the peak gate current is only about 23&nbsp;mA, "
                  "so the transition takes on the order of 2&nbsp;µs. During each transition "
                  "the device sits in its linear region with both high voltage and high current "
                  "across it."),
                formel(
                    "P_{sw} = \\tfrac{1}{2} \\cdot U_{DS} \\cdot I_D \\cdot (t_{on} + t_{off}) \\cdot f",
                    "P switching gleich ein halb mal U_DS mal I_D mal Summe der Schaltzeiten "
                    "mal Schaltfrequenz",
                ),
                tab(
                    kopf=["Beitrag", "Rechnung", "Verlust"],
                    zeilen=[
                        ["Durchlassverlust", "8 A² · 22 mΩ · 0,7", "0,99 W"],
                        ["Schaltverlust", "½ · 12 V · 8 A · 4 µs · 20 kHz", "3,84 W"],
                        ["Summe", "", "4,8 W"],
                    ],
                    titel="Verlustaufteilung im vorliegenden Fall",
                    ausrichtung=["l", "l", "r"],
                ),
                p("Nearly four times what you expected – and a bare TO-220 without a heatsink "
                  "has a thermal resistance of about 62&nbsp;K/W to ambient. 4.8&nbsp;W means a "
                  "rise of roughly 300&nbsp;K. That is your failure."),
                h("2. The logic level is marginal", 3),
                p("The IRLZ44N is a logic-level part, but its R<sub>DS(on)</sub> of 22&nbsp;mΩ "
                  "is specified at V<sub>GS</sub>&nbsp;=&nbsp;10&nbsp;V. At 4.5&nbsp;V it is closer "
                  "to 28&nbsp;mΩ, and an Arduino pin under load does not reach a clean 5&nbsp;V."),
                h("3. Remedy", 3),
                ul(
                    "Use a proper gate driver (TC4420, UCC27517 or similar) with 1–2&nbsp;A "
                    "peak output, supplied from 10–12&nbsp;V.",
                    "Reduce the gate resistor to 10–22&nbsp;Ω – just enough to damp ringing.",
                    "Lower the PWM frequency to 1–2&nbsp;kHz if a driver is not an option. "
                    "Switching loss scales linearly with frequency.",
                    "Add a heatsink regardless. Even 1&nbsp;W in a TO-220 raises the junction "
                    "noticeably.",
                    "Fit a freewheeling diode across the motor if you have not already.",
                    geordnet=True,
                ),
                warnung(
                    "Freilaufdiode nicht vergessen",
                    "Eine induktive Last ohne Freilaufdiode erzeugt beim Abschalten "
                    "Spannungsspitzen weit über der Drain-Source-Sperrspannung. Der MOSFET "
                    "stirbt dann unabhängig von der Erwärmung.",
                    stufe="achtung",
                ),
            ],
        ),
        fall_antwort(
            autor="jonk", datum="2026-01-12", stimmen=12,
            blocks=[
                p("To add a measurement you can do yourself: put a scope on the gate and look "
                  "at the <em>Miller plateau</em>. If the flat section in the middle of the rising "
                  "edge lasts longer than about 200&nbsp;ns at 20&nbsp;kHz, your drive is too weak. "
                  "That plateau is precisely the time the device spends in its linear region."),
            ],
        ),
    ],
)


# ---------------------------------------------------------------------------
# 3  ELEKTROTECHNIK - PDF-Kapitel
# ---------------------------------------------------------------------------

LEITUNG = Akte(
    id="et-leitungsquerschnitt",
    titel="Strombelastbarkeit und Spannungsfall",
    untertitel="Leitungsdimensionierung nach IEC-60364-Systematik",
    bereich_id="elektrotechnik-und-elektronik",
    thema_id="leitungsdimensionierung-strombelastbarkeit",
    tiefe="REFERENZ",
    sprache="DE",
    demo=True,
    stempel=["DEMO"],
    quelle=Quelle(
        typ="pdf", name="ABB Electrical Installation Handbook, 7. Auflage",
        datei="pdf/energie/abb_installation_handbook_7ed.pdf",
        kennung="Kapitel 3.2", seite="S. 3-14 bis 3-21",
        lizenz="Herstellerdokumentation, Einzelkopie", stand="2022-03-01",
        original_url="/api/akte/et-leitungsquerschnitt/original",
    ),
    verwandt=[{"id": "et-ohmsches-gesetz", "titel": "Ohmsches Gesetz"}],
    inhalt=[
        p("Der Querschnitt einer Leitung wird von <strong>drei</strong> Bedingungen bestimmt. "
          "Maßgebend ist immer die ungünstigste."),
        ul(
            "<strong>Strombelastbarkeit</strong> – die Leitung darf sich nicht über ihre "
            "zulässige Betriebstemperatur erwärmen (PVC 70 °C, VPE 90 °C).",
            "<strong>Spannungsfall</strong> – üblich maximal 3 % für Beleuchtung, 5 % für "
            "sonstige Verbraucher, gerechnet ab Übergabepunkt.",
            "<strong>Abschaltbedingung</strong> – im Kurzschlussfall muss die Schutzeinrichtung "
            "innerhalb der geforderten Zeit auslösen.",
            geordnet=True,
        ),
        h("Verlegearten"),
        p("Die Belastbarkeit hängt entscheidend davon ab, wie gut die Wärme abgeführt wird. "
          "Die Referenz-Verlegearten fassen die Praxisfälle zusammen:"),
        tab(
            kopf=["Art", "Beschreibung", "Beispiel"],
            zeilen=[
                ["A1", "Aderleitungen im wärmegedämmten Rohr in der Wand",
                 "Neubau, Installationsrohr im Dämmstoff"],
                ["A2", "Mehraderleitung im wärmegedämmten Rohr", "NYM im Rohr im Dämmstoff"],
                ["B1", "Aderleitungen im Rohr auf der Wand", "Aufputzrohr"],
                ["B2", "Mehraderleitung im Rohr auf der Wand", "NYM im Aufputzrohr"],
                ["C", "Mehraderleitung direkt auf der Wand", "NYM auf Putz, Kabelschelle"],
                ["E", "Mehraderleitung frei in Luft", "Kabelpritsche mit Abstand"],
            ],
            titel="Referenz-Verlegearten",
        ),
        tab(
            kopf=["Querschnitt", "A2", "B2", "C", "E"],
            zeilen=[
                ["1,5 mm²", "13 A", "15 A", "17,5 A", "19,5 A"],
                ["2,5 mm²", "17,5 A", "20 A", "24 A", "27 A"],
                ["4 mm²", "23 A", "27 A", "32 A", "36 A"],
                ["6 mm²", "29 A", "34 A", "41 A", "46 A"],
                ["10 mm²", "39 A", "46 A", "57 A", "63 A"],
                ["16 mm²", "52 A", "62 A", "76 A", "85 A"],
            ],
            titel="Belastbarkeit Kupfer, PVC-isoliert, zwei belastete Adern, 30 °C Umgebung",
            ausrichtung=["l", "r", "r", "r", "r"],
            fussnote="Werte zur Orientierung. Maßgebend ist die Tabelle der jeweils "
                     "geltenden Errichtungsbestimmung.",
        ),
        h("Umrechnungsfaktoren"),
        p("Die Tabellenwerte gelten für 30 °C Umgebungstemperatur und eine einzeln "
          "verlegte Leitung. Abweichungen werden multiplikativ berücksichtigt:"),
        tab(
            kopf=["Einfluss", "Bedingung", "Faktor"],
            zeilen=[
                ["Umgebungstemperatur", "40 °C statt 30 °C (PVC)", "0,87"],
                ["Umgebungstemperatur", "50 °C statt 30 °C (PVC)", "0,71"],
                ["Häufung", "3 Stromkreise gebündelt", "0,70"],
                ["Häufung", "6 Stromkreise gebündelt", "0,57"],
                ["Erdverlegung", "Bodentemperatur 20 °C", "1,00"],
            ],
            ausrichtung=["l", "l", "r"],
        ),
        h("Spannungsfall"),
        p("Für Wechselstrom im Einphasennetz – Hin- und Rückleiter, daher Faktor 2:"),
        formel(
            "\\Delta U = \\frac{2 \\cdot L \\cdot I \\cdot \\cos\\varphi}{\\kappa \\cdot A}",
            "Delta U gleich zwei mal Laenge mal Strom mal Kosinus phi, geteilt durch "
            "Leitwert mal Querschnitt",
        ),
        p("Im Drehstromnetz tritt an die Stelle der 2 der Faktor √3. Der Leitwert κ beträgt "
          "für Kupfer 56 m/(Ω·mm²), für Aluminium 35 m/(Ω·mm²)."),
        seitenbild(
            ph("Nomogramm Spannungsfall – Seite 3-19 des Handbuchs", 760, 520, "seite"),
            bildunterschrift="Nomogramm zur Überschlagsrechnung des Spannungsfalls. "
                             "Die Seite ist layoutgebunden und wird als Kopie eingeklebt.",
            herkunft="ABB Electrical Installation Handbook, S. 3-19",
        ),
        h("Rechenbeispiel"),
        infokasten("Vorgabe", [
            ["Verbraucher", "Drehstrommotor 5,5 kW"],
            ["Netz", "400 V, 50 Hz"],
            ["Nennstrom", "11,1 A"],
            ["cos φ", "0,84"],
            ["Leitungslänge", "40 m"],
            ["Verlegeart", "C (auf der Wand)"],
            ["Zul. Spannungsfall", "5 % = 20 V"],
        ]),
        ul(
            "Nach Belastbarkeit genügt 1,5 mm² (17,5 A bei Verlegeart C).",
            "Spannungsfall bei 1,5 mm²: ΔU = (√3 · 40 · 11,1 · 0,84) / (56 · 1,5) "
            "= 7,7 V → 1,9 %. Zulässig.",
            "Maßgebend ist hier die Abschaltbedingung und die Motorschutz-Auslegung, "
            "nicht die Erwärmung. In der Praxis wird 2,5 mm² gewählt.",
            geordnet=True,
        ),
        warnung(
            "Diese Tabellen ersetzen keine Errichtungsbestimmung",
            "Die Werte stammen aus einer Herstellerdokumentation und dienen der Orientierung. "
            "Für Arbeiten an ortsfesten Anlagen gelten die jeweils geltenden nationalen "
            "Errichtungsbestimmungen und die fünf Sicherheitsregeln.",
            stufe="gefahr",
        ),
    ],
)


# ---------------------------------------------------------------------------
# 4  MEDIZIN - ZIM-Artikel (WikiMed)
# ---------------------------------------------------------------------------

ANAPHYLAXIE = Akte(
    id="med-anaphylaxie",
    titel="Anaphylaxie",
    untertitel="Akute, lebensbedrohliche allergische Allgemeinreaktion",
    bereich_id="medizin",
    thema_id="krankheiten-symptome-medikamente-anatomie",
    tiefe="REFERENZ",
    sprache="DE",
    demo=True,
    stempel=["DEMO"],
    quelle=Quelle(
        typ="zim", name="WikiMed Medical Encyclopedia (Deutsch)",
        datei="wikimed_de_all_maxi_2025-11.zim",
        kennung="A/Anaphylaxie", lizenz="CC BY-SA 4.0",
        stand="2025-11-18", autor="Wikipedia-/WikiProjectMed-Autoren",
        original_url="/api/akte/med-anaphylaxie/original",
    ),
    verwandt=[
        {"id": "med-reanimation", "titel": "Reanimation des Erwachsenen"},
    ],
    inhalt=[
        warnung(
            "Notfall – sofortiges Handeln erforderlich",
            "Bei Verdacht auf Anaphylaxie zählt jede Minute. Adrenalin intramuskulär ist die "
            "einzige Maßnahme, die den Verlauf sicher durchbricht. Antihistaminika und "
            "Kortison wirken zu langsam und ersetzen es nicht.",
            stufe="gefahr",
        ),
        p("Die <strong>Anaphylaxie</strong> ist eine akute, potenziell tödliche Überreaktion "
          "des Immunsystems, die innerhalb von Minuten mehrere Organsysteme erfasst. Sie "
          "entsteht durch massive Freisetzung von Histamin und anderen Mediatoren aus "
          "Mastzellen und basophilen Granulozyten."),
        h("Auslöser"),
        tab(
            kopf=["Gruppe", "Häufige Auslöser", "Anteil bei Erwachsenen"],
            zeilen=[
                ["Insektengift", "Biene, Wespe, Hornisse", "ca. 50 %"],
                ["Arzneimittel", "Penicilline, NSAR, Kontrastmittel, Muskelrelaxanzien", "ca. 25 %"],
                ["Nahrungsmittel", "Erdnuss, Baumnüsse, Schalentiere, Sellerie", "ca. 20 %"],
                ["Sonstige", "Latex, körperliche Anstrengung, idiopathisch", "ca. 5 %"],
            ],
            titel="Auslöser nach Häufigkeit",
            ausrichtung=["l", "l", "r"],
            fussnote="Bei Kindern überwiegen Nahrungsmittel deutlich.",
        ),
        h("Schweregrade"),
        tab(
            kopf=["Grad", "Haut", "Bauch", "Atemwege", "Kreislauf"],
            zeilen=[
                ["I", "Juckreiz, Rötung, Quaddeln", "–", "–", "–"],
                ["II", "wie I", "Übelkeit, Krampf", "Heiserkeit, Luftnot", "Herzrasen, Blutdruckabfall"],
                ["III", "wie I", "Erbrechen, Durchfall", "Kehlkopfödem, Bronchospasmus", "Schock"],
                ["IV", "wie I", "–", "Atemstillstand", "Kreislaufstillstand"],
            ],
            titel="Einteilung nach Ring und Meßmer",
            fussnote="Die Grade müssen nicht der Reihe nach durchlaufen werden. Ein Verlauf "
                     "kann direkt mit Grad III beginnen.",
        ),
        bild(
            ph("Quaddelbildung (Urtikaria) am Unterarm", 520, 340, "foto"),
            bildunterschrift="Urtikaria als häufigstes Frühzeichen. Fehlende Hautsymptome "
                             "schließen eine Anaphylaxie jedoch nicht aus – bei etwa 10 % der "
                             "Fälle fehlen sie.",
            herkunft="WikiMed, Datei: Urticaria_forearm.jpg – CC BY-SA 3.0",
            breite="schmal",
        ),
        h("Sofortmaßnahmen"),
        ul(
            "Zufuhr des Auslösers stoppen (Infusion abstellen, Stachel entfernen).",
            "Notruf absetzen.",
            "<strong>Adrenalin intramuskulär</strong> in die Außenseite des Oberschenkels – "
            "Erwachsene 0,5 mg, Kinder 0,01 mg je kg Körpergewicht, maximal 0,5 mg. "
            "Wiederholung nach 5–10 Minuten möglich.",
            "Lagerung: bei Kreislaufproblemen flach mit erhöhten Beinen, bei Luftnot sitzend. "
            "<em>Nicht</em> plötzlich aufsetzen oder aufstehen lassen.",
            "Sauerstoff hochdosiert, sofern verfügbar.",
            "Erst danach: Antihistaminikum und Glukokortikoid.",
            geordnet=True,
        ),
        infokasten("Adrenalin intramuskulär – Dosis", [
            ["Erwachsene und Kinder ab 12 Jahren", "0,5 mg (0,5 ml der Lösung 1 mg/ml)"],
            ["Kinder 6–12 Jahre", "0,3 mg"],
            ["Kinder unter 6 Jahren", "0,15 mg"],
            ["Ort", "Musculus vastus lateralis, Oberschenkelaußenseite"],
            ["Wiederholung", "nach 5–10 Minuten bei ausbleibender Besserung"],
        ]),
        warnung(
            "Biphasischer Verlauf",
            "Bei bis zu 20 % der Fälle tritt nach scheinbarer Erholung eine zweite Reaktion "
            "auf, typischerweise nach 4–12 Stunden. Betroffene müssen deshalb auch nach "
            "erfolgreicher Behandlung mindestens 12 Stunden überwacht werden.",
            stufe="achtung",
        ),
        h("Nach dem Ereignis"),
        p("Wer eine Anaphylaxie überstanden hat, benötigt ein <strong>Notfallset</strong> mit "
          "Adrenalin-Autoinjektor, Antihistaminikum und Kortikoid sowie eine Einweisung in "
          "dessen Anwendung. Ein Allergiepass hält den Auslöser fest."),
    ],
)


# ---------------------------------------------------------------------------
# 5  MEDIZIN - PDF-Kapitel (Leitlinie)
# ---------------------------------------------------------------------------

REANIMATION = Akte(
    id="med-reanimation",
    titel="Reanimation des Erwachsenen",
    untertitel="Basismaßnahmen (BLS) und Verwendung eines AED",
    bereich_id="medizin",
    thema_id="erste-hilfe-reanimation-aktuelle-erc",
    tiefe="PRAXIS",
    sprache="DE",
    demo=True,
    stempel=["DEMO"],
    quelle=Quelle(
        typ="pdf", name="ERC-Leitlinien 2021, deutsche Fassung",
        datei="pdf/med/erc_leitlinien_2021_de.pdf",
        kennung="Kapitel 2 – Basismaßnahmen", seite="S. 41 bis 56",
        lizenz="CC BY-NC-ND 4.0", stand="2021-03-25",
        autor="European Resuscitation Council / GRC",
        original_url="/api/akte/med-reanimation/original",
    ),
    verwandt=[{"id": "med-anaphylaxie", "titel": "Anaphylaxie"}],
    inhalt=[
        warnung(
            "Diese Akte ersetzt keinen Kurs",
            "Reanimation ist eine körperliche Fertigkeit. Der Ablauf lässt sich nachlesen, "
            "die Drucktiefe und die Frequenz nicht. Ein Auffrischungskurs alle zwei Jahre "
            "ist durch nichts zu ersetzen.",
            stufe="hinweis",
        ),
        h("Ablauf in fünf Schritten"),
        ul(
            "<strong>Prüfen:</strong> Ansprechen, rütteln an den Schultern. Keine Reaktion → "
            "Atemwege freimachen (Kopf überstrecken, Kinn anheben), höchstens 10 Sekunden "
            "auf normale Atmung prüfen. Schnappatmung gilt als <em>keine</em> Atmung.",
            "<strong>Rufen:</strong> Notruf 112, Lautsprecher einschalten, jemanden nach einem "
            "AED schicken.",
            "<strong>Drücken:</strong> Handballen auf die Mitte des Brustkorbs, 30 Kompressionen.",
            "<strong>Beatmen:</strong> 2 Beatmungen, je etwa 1 Sekunde. Wer das nicht kann oder "
            "will, drückt ohne Unterbrechung weiter.",
            "<strong>AED:</strong> sobald verfügbar einschalten und den Ansagen folgen.",
            geordnet=True,
        ),
        infokasten("Kennzahlen der Herzdruckmassage", [
            ["Verhältnis", "30 : 2"],
            ["Frequenz", "100 bis 120 pro Minute"],
            ["Drucktiefe Erwachsener", "5 bis 6 cm"],
            ["Entlastung", "vollständig, Brustkorb zurückfedern lassen"],
            ["Unterbrechung", "höchstens 10 Sekunden"],
            ["Helferwechsel", "alle 2 Minuten"],
        ]),
        seitenbild(
            ph("Algorithmus Basismaßnahmen Erwachsene – Seite 43", 700, 900, "seite"),
            bildunterschrift="Der Algorithmus als Flussdiagramm. Layoutgebundene Seite, "
                             "deshalb als Kopie eingeklebt statt neu gesetzt.",
            herkunft="ERC-Leitlinien 2021, deutsche Fassung, S. 43",
        ),
        h("Automatisierter externer Defibrillator"),
        p("Der AED analysiert selbstständig und gibt nur dann einen Schock frei, wenn der "
          "Rhythmus schockbar ist. Er kann bei korrekter Anwendung niemanden schaden, der "
          "keinen Schock braucht."),
        ul(
            "Gerät einschalten, Anweisungen befolgen.",
            "Elektroden auf den entkleideten, trockenen Brustkorb: eine rechts unterhalb des "
            "Schlüsselbeins, eine links seitlich unterhalb der Achsel.",
            "Während der Analyse niemand berührt die Person.",
            "Nach dem Schock <strong>sofort</strong> weiter drücken, ohne Pulskontrolle.",
            geordnet=True,
        ),
        warnung(
            "Umgebung vor dem Schock prüfen",
            "Vor der Schockabgabe laut ansagen und sicherstellen, dass niemand die Person "
            "oder eine leitende Verbindung dazu berührt. Bei nässer Umgebung die Person "
            "zuvor auf eine trockene Unterlage ziehen.",
            stufe="gefahr",
        ),
        h("Abweichungen bei Kindern"),
        tab(
            kopf=["", "Erwachsener", "Kind (1 Jahr bis Pubertät)", "Säugling"],
            zeilen=[
                ["Beginn", "30 Kompressionen", "5 Initialbeatmungen", "5 Initialbeatmungen"],
                ["Verhältnis (Laien)", "30 : 2", "30 : 2", "30 : 2"],
                ["Verhältnis (Profi)", "30 : 2", "15 : 2", "15 : 2"],
                ["Drucktiefe", "5–6 cm", "ca. 1/3 des Brustkorbs", "ca. 1/3, ca. 4 cm"],
                ["Technik", "zwei Hände", "ein oder zwei Hände", "zwei Finger / zwei Daumen"],
            ],
            titel="Basismaßnahmen nach Altersgruppe",
        ),
        zitat(
            "Jede Reanimation ist besser als keine. Die häufigste Fehlerquelle ist nicht die "
            "falsche Technik, sondern das Zögern.",
            "ERC-Leitlinien 2021, Kapitel 2",
        ),
    ],
)


# ---------------------------------------------------------------------------
# 6  MEDIZIN - PDF-Kapitel (taktisch)
# ---------------------------------------------------------------------------

TOURNIQUET = Akte(
    id="med-tourniquet",
    titel="Tourniquet bei lebensbedrohlicher Extremitätenblutung",
    untertitel="Anlage, Kontrolle, Dokumentation",
    bereich_id="medizin",
    thema_id="blutungskontrolle-tourniquet-thorax-schock",
    tiefe="PRAXIS",
    sprache="DE",
    demo=True,
    stempel=["DEMO"],
    quelle=Quelle(
        typ="pdf", name="TCCC Guidelines for Medical Personnel",
        datei="pdf/med/tccc_guidelines_2025-01.pdf",
        kennung="Abschnitt 2 – Massive Hemorrhage", seite="S. 8 bis 14",
        lizenz="Public Domain (US DoD, approved for public release)",
        stand="2025-01-15",
        original_url="/api/akte/med-tourniquet/original",
    ),
    verwandt=[{"id": "med-reanimation", "titel": "Reanimation des Erwachsenen"}],
    inhalt=[
        warnung(
            "Nur bei lebensbedrohlicher Blutung",
            "Ein Tourniquet ist kein Mittel gegen jede Blutung. Es gehört an eine Extremität, "
            "deren Blutung mit Druckverband und direktem Druck nicht zu stoppen ist – "
            "typischerweise spritzende arterielle Blutung, Amputation oder ein Verletzter, "
            "bei dem mehrere Verletzungen gleichzeitig zu versorgen sind.",
            stufe="gefahr",
        ),
        h("Anlage"),
        ul(
            "<strong>Hoch und fest</strong> – im Notfall so weit proximal wie möglich, "
            "über der Kleidung. Später, wenn Zeit ist, auf 5–7 cm oberhalb der Wunde "
            "umsetzen, nie über einem Gelenk.",
            "Band durchfädeln, festziehen, bis kein Spiel mehr bleibt.",
            "Knüppel drehen, bis die Blutung steht <em>und</em> der periphere Puls "
            "nicht mehr tastbar ist.",
            "Knüppel in der Halterung sichern.",
            "<strong>Uhrzeit</strong> auf das Band schreiben – nicht auf die Haut, nicht "
            "auf die Kleidung.",
            geordnet=True,
        ),
        bild(
            ph("Anlage eines Tourniquets am Oberschenkel, Schrittfolge", 640, 420, "zeichnung"),
            bildunterschrift="Schrittfolge der Anlage. Der Knüppel wird gedreht, bis die "
                             "Blutung steht, dann in der Halterung gesichert.",
            herkunft="TCCC Guidelines, Abbildung 2-3",
        ),
        infokasten("Kontrollpunkte nach der Anlage", [
            ["Blutung", "steht vollständig"],
            ["Peripherer Puls", "nicht mehr tastbar"],
            ["Uhrzeit", "auf dem Band vermerkt"],
            ["Sichtbarkeit", "Tourniquet nicht zudecken"],
            ["Nachkontrolle", "alle 10–15 Minuten, ob es sich gelockert hat"],
        ]),
        warnung(
            "Ein angelegtes Tourniquet wird nicht gelockert",
            "Kurzzeitiges Lösen zum „Durchbluten“ ist schaedlich: es führt zu erneutem "
            "Blutverlust und schwemmt saure Stoffwechselprodukte ein. Die Entscheidung "
            "über das Lösen trifft erst die weiterbehandelnde Stelle.",
            stufe="gefahr",
        ),
        h("Zeitgrenzen"),
        tab(
            kopf=["Liegedauer", "Erwartung", "Vorgehen"],
            zeilen=[
                ["bis 2 h", "Extremität in aller Regel zu erhalten", "belassen"],
                ["2–6 h", "Schädigung wahrscheinlich, Erhalt meist möglich", "belassen, dringlich verlegen"],
                ["über 6 h", "schwere Schädigung, Reperfusionssyndrom",
                 "nur unter Überwachung lösen"],
            ],
            fussnote="Der Extremitätenverlust durch ein Tourniquet ist selten. Der Tod durch "
                     "eine nicht gestillte Blutung ist es nicht.",
        ),
        h("Wenn kein Tourniquet verfügbar ist"),
        p("Ein improvisiertes Tourniquet ist deutlich schlechter als ein gefertigtes, aber "
          "besser als nichts. Es braucht <strong>zwingend</strong> einen Knüppel zum Verdrehen – "
          "ein bloß zugezogener Gurt erreicht den nötigen Druck nicht."),
        ul(
            "Breites Band verwenden, mindestens 4 cm – Dreiecktuch, Gurtband, kein Draht, "
            "keine Schnur.",
            "Stabiler Stab als Knüppel, etwa 15–20 cm.",
            "Nach dem Verdrehen den Knüppel mit einem zweiten Band fixieren.",
        ),
    ],
)


# ---------------------------------------------------------------------------
# 7  EIGENE FAHRZEUGE - PDF-Kapitel (Werkstatthandbuch)
# ---------------------------------------------------------------------------

VESPA_ZUENDUNG = Akte(
    id="fz-vespa-zuendung",
    titel="Vespa V50: Zündung einstellen",
    untertitel="Unterbrecherkontakt, Zündzeitpunkt, Falschluftsuche",
    bereich_id="eigene-fahrzeuge",
    thema_id="vespa-v50-n-v5a1t-1963",
    tiefe="PRAXIS",
    sprache="DE",
    demo=True,
    stempel=["DEMO", "NUR LOKAL"],
    quelle=Quelle(
        typ="pdf", name="Piaggio Werkstatthandbuch Vespa 50 (V5A1T)",
        datei="pdf/fahrzeuge/vespa/piaggio_wsh_v50_scan.pdf",
        kennung="Abschnitt 5 – Impianto elettrico", seite="S. 5-2 bis 5-9",
        lizenz="Privatkopie, nicht weitergeben", stand="1963-01-01",
        nur_lokal=True,
        original_url="/api/akte/fz-vespa-zuendung/original",
    ),
    verwandt=[
        {"id": "fz-defender-kenndaten", "titel": "Defender 110 TD5 – Kenndaten"},
    ],
    inhalt=[
        warnung(
            "Werte gegen das Original prüfen",
            "Diese Akte ist Demo-Inhalt. Einstellwerte an einem 60 Jahre alten Fahrzeug "
            "gehören vor der Anwendung gegen das Original-Werkstatthandbuch und den "
            "tatsächlichen Motorstand geprüft.",
            stufe="achtung",
        ),
        infokasten("Einstellwerte", [
            ["Motor", "V5A1M, 49,77 cm³, Zweitakt"],
            ["Zündanlage", "Schwungradmagnetzünder, Unterbrecher"],
            ["Unterbrecherabstand", "0,35 bis 0,45 mm"],
            ["Zündzeitpunkt", "23° ± 1° vor OT"],
            ["Zündkerze", "W5AC / B7HS, Elektrodenabstand 0,5–0,6 mm"],
            ["Vergaser", "Dell'Orto SHB 16/10"],
        ]),
        h("Vorbereitung"),
        ul(
            "Zündkerze herausdrehen, Kerzenbild beurteilen und notieren.",
            "Backe links öffnen, Polrad freilegen.",
            "Kraftstoffhahn schließen.",
            geordnet=True,
        ),
        h("Unterbrecherabstand"),
        ul(
            "Polrad drehen, bis der Unterbrecher seine größte Öffnung erreicht – der "
            "Gleitschuh steht dann auf der Spitze des Nockens.",
            "Mit der Fühlerlehre messen. Sollwert 0,4 mm, zulässig 0,35 bis 0,45 mm.",
            "Klemmschraube lösen, Grundplatte des festen Kontakts verschieben, Schraube "
            "wieder anziehen, nachmessen.",
            "Kontaktflächen prüfen: Krater oder Kegel bedeuten neuer Unterbrecher und "
            "meist auch neuer Kondensator.",
            geordnet=True,
        ),
        seitenbild(
            ph("Schnittzeichnung Zündgrundplatte mit Markierungen – Seite 5-4", 720, 560, "seite"),
            bildunterschrift="Zündgrundplatte mit Unterbrecher, Kondensator und den Marken "
                             "für den Zündzeitpunkt.",
            herkunft="Piaggio Werkstatthandbuch V5A1T, S. 5-4",
        ),
        h("Zündzeitpunkt"),
        p("Der Zündzeitpunkt wird über das Verdrehen der gesamten Grundplatte eingestellt. "
          "Ohne Gradscheibe lässt er sich mit einer Messuhr über die Kerzenbohrung "
          "bestimmen: 23° vor OT entsprechen bei diesem Motor etwa 1,3 mm Kolbenweg "
          "vor dem oberen Totpunkt."),
        ul(
            "Messuhr in die Kerzenbohrung setzen, oberen Totpunkt suchen, Uhr nullen.",
            "Polrad entgegen der Drehrichtung zurückdrehen, bis 1,3 mm angezeigt werden.",
            "Prüflampe zwischen Unterbrecherklemme und Masse. Grundplatte verdrehen, bis "
            "die Lampe genau in diesem Moment umschaltet – der Kontakt öffnet.",
            "Grundplatte festziehen, Einstellung zweimal nachprüfen.",
            geordnet=True,
        ),
        h("Falschluft suchen"),
        p("Ein Zweitakter mit Falschluft läuft zu mager, dreht im Leerlauf hoch und nimmt "
          "schlecht Gas an. Typische Stellen in der Reihenfolge der Häufigkeit:"),
        tab(
            kopf=["Stelle", "Anzeichen", "Abhilfe"],
            zeilen=[
                ["Wellendichtring lichtmaschinenseitig", "Drehzahl hängt nach dem Gaswegnehmen",
                 "Simmerring erneuern"],
                ["Wellendichtring kupplungsseitig", "Getriebeöl wird weniger, blauer Rauch",
                 "Simmerring erneuern"],
                ["Zylinderfußdichtung", "Ölspur am Fuß", "Dichtung und Auflagefläche prüfen"],
                ["Vergaserflansch", "Leerlauf nicht einstellbar", "Flansch planen, Dichtung neu"],
                ["Ansaugstutzen", "Risse im Gummi", "Stutzen ersetzen"],
            ],
        ),
        p("Prüfmethode ohne Spezialwerkzeug: Motor im Leerlauf laufen lassen und die "
          "Verdachtsstellen kurz mit Bremsenreiniger oder Startpilot ansäubern. Ändert "
          "sich die Drehzahl, ist die Stelle undicht."),
        warnung(
            "Brandgefahr bei der Falschluftsuche",
            "Bremsenreiniger und Startpilot sind leicht entzündlich und werden hier an einem "
            "laufenden, heißen Motor eingesetzt. Nur im Freien, nur sparsam, Feuerlöscher "
            "in Reichweite, nicht in die Nähe des Auspuffs sprühen.",
            stufe="gefahr",
        ),
    ],
)


DEMO_AKTEN: list[Akte] = [
    OHM, MOSFET, LEITUNG, ANAPHYLAXIE, REANIMATION, TOURNIQUET, VESPA_ZUENDUNG,
]
