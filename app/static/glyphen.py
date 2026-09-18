# -*- coding: utf-8 -*-
"""
Symbolbibliothek fuer QUINTESSENZ V2.

Jedes Symbol ist eine Strichzeichnung im Feld 0 0 100 100, gleiche Strichstaerke, keine
Flaechen, keine Perspektive. Damit sehen alle Ebenen gleich aus, vom Hauptbereich bis zum
einzelnen Thema. Die Ringe drumherum setzt der Erzeuger, hier steht nur das Motiv.

    from glyphen import GLYPHEN, svg
    svg("blitz")     ->  <svg ...>...</svg>
"""

# Motive: Kennung -> SVG-Innenleben (Feld 0 0 100 100)
GLYPHEN = {
    # ---- Hauptbereiche -------------------------------------------------------
    "technik":   '<path d="M22 78 L52 48"/>'
                 '<path d="M46 42 a13 13 0 1 0 12 -12 L48 40 L40 32 L50 22 a13 13 0 0 0 -4 20 Z"/>'
                 '<path d="M74 22 L58 38 L62 42 L78 26 Z"/><path d="M78 26 L86 18"/>'
                 '<circle cx="24" cy="76" r="4"/>',
    "survival":  '<path d="M20 78 L50 22 L80 78 Z"/><path d="M34 78 L50 50 L66 78"/>'
                 '<path d="M12 86 H88"/>',
    "medizin":   '<path d="M42 16 H58 V42 H84 V58 H58 V84 H42 V58 H16 V42 H42 Z"/>',
    "archiv":    '<path d="M16 30 C30 22 44 24 50 30 L50 80 C44 74 30 72 16 80 Z"/>'
                 '<path d="M84 30 C70 22 56 24 50 30 L50 80 C56 74 70 72 84 80 Z"/>',
    "assistent": '<rect x="18" y="26" width="64" height="40" rx="4"/>'
                 '<path d="M30 38 v16 M42 38 v16 M54 38 v16 M66 38 v16"/>'
                 '<path d="M34 78 h32 M28 66 v12 M72 66 v12"/>',

    # ---- Elektrotechnik ------------------------------------------------------
    "blitz":      '<path d="M56 12 L32 52 L48 52 L42 88 L70 44 L52 44 L62 12 Z"/>',
    "bauteil":    '<path d="M10 50 H26 L32 36 L44 64 L56 36 L68 64 L74 50 H90"/>',
    "analog":     '<path d="M10 50 C22 18 34 82 46 50 C58 18 70 82 82 50 H90"/>',
    "digital":    '<path d="M10 66 H26 V34 H42 V66 H58 V34 H74 V66 H90"/>',
    "leistung":   '<path d="M50 20 V38 M50 62 V80"/><path d="M34 38 H66 L50 62 Z"/>'
                  '<path d="M34 62 H66"/>',
    "motor":      '<circle cx="46" cy="50" r="26"/><path d="M36 60 L46 38 L56 60 M40 52 H52"/>'
                  '<path d="M72 50 H90 M82 42 v16"/>',
    "regler":     '<path d="M14 34 H86 M14 66 H86"/><circle cx="38" cy="34" r="8"/>'
                  '<circle cx="66" cy="66" r="8"/>',
    "sensor":     '<path d="M14 50 H34"/><circle cx="50" cy="50" r="16"/>'
                  '<path d="M66 34 L86 22 M66 50 H86 M66 66 L86 78"/>',
    "relais":     '<rect x="16" y="32" width="26" height="36" rx="2"/>'
                  '<path d="M20 38 L38 56 M20 48 L38 66 M20 58 L34 68"/>'
                  '<circle cx="54" cy="40" r="3"/><path d="M54 40 L86 52"/>'
                  '<path d="M84 30 h-8 M84 66 h-8"/>',
    "messen":     '<path d="M20 68 A30 30 0 0 1 80 68"/><path d="M50 68 L66 40"/>'
                  '<circle cx="50" cy="68" r="4"/><path d="M24 78 H76"/>',
    "hochspannung": '<path d="M30 16 L30 84 M70 16 L70 84"/>'
                    '<path d="M30 40 L44 50 L30 60 M70 40 L56 50 L70 60"/>'
                    '<path d="M46 44 L54 50 L46 56"/>',
    "antenne":     '<path d="M50 84 V34"/><path d="M34 84 L50 52 L66 84 Z"/>'
                   '<circle cx="50" cy="28" r="4"/>'
                   '<path d="M36 22 A20 20 0 0 1 64 22"/><path d="M26 14 A34 34 0 0 1 74 14"/>',

    # ---- Mechanik ------------------------------------------------------------
    "zahnrad":  '<path d="M50.0 20.0 L57.2 10.7 L69.8 15.2 L69.3 27.0 L69.3 27.0 L80.8 24.5 L87.5 36.1 L79.5 44.8 L79.5 44.8 L90.0 50.3 L87.7 63.4 L76.0 65.0 L76.0 65.0 L80.5 75.9 L70.2 84.5 L60.3 78.2 L60.3 78.2 L56.7 89.4 L43.3 89.4 L39.7 78.2 L39.7 78.2 L29.8 84.5 L19.5 75.9 L24.0 65.0 L24.0 65.0 L12.3 63.4 L10.0 50.3 L20.5 44.8 L20.5 44.8 L12.5 36.1 L19.2 24.5 L30.7 27.0 L30.7 27.0 L30.2 15.2 L42.8 10.7 L50.0 20.0 Z"/>'
                '<circle cx="50" cy="50" r="13"/>',
    "traeger":  '<path d="M18 22 H82 M18 78 H82 M42 22 V78 M58 22 V78"/>'
                '<path d="M50 8 v8 M50 84 v8 M44 14 l6 -6 l6 6 M44 86 l6 6 l6 -6"/>',
    "lager":    '<circle cx="50" cy="50" r="30"/><circle cx="50" cy="50" r="13"/>'
                '<circle cx="50" cy="28" r="5"/><circle cx="50" cy="72" r="5"/>'
                '<circle cx="28" cy="50" r="5"/><circle cx="72" cy="50" r="5"/>'
                '<circle cx="66" cy="34" r="5"/><circle cx="34" cy="66" r="5"/>',
    "werkstoff": '<path d="M16 34 L50 18 L84 34 L50 50 Z"/><path d="M16 50 L50 66 L84 50"/>'
                 '<path d="M16 66 L50 82 L84 66"/><path d="M16 34 V66 M84 34 V66"/>',
    "schweissen": '<path d="M18 78 L46 44"/><path d="M40 36 L58 54 L48 64 L30 46 Z"/>'
                  '<path d="M62 44 c8 -10 6 -18 2 -24 c12 6 18 16 12 26 c6 -2 8 -8 8 -12'
                  ' c6 10 2 22 -10 24 c-8 2 -14 -4 -12 -14 Z"/>',
    "hydraulik": '<rect x="14" y="36" width="44" height="28" rx="2"/>'
                 '<path d="M36 36 V64"/><path d="M58 50 H86"/><path d="M80 44 v12"/>'
                 '<path d="M22 30 v-8 M46 30 v-8"/>',
    "fahrzeug":  '<path d="M16 62 V50 L28 34 H62 L76 50 H84 V62"/>'
                 '<circle cx="32" cy="66" r="8"/><circle cx="68" cy="66" r="8"/>'
                 '<path d="M40 62 H60 M34 50 H66"/>',

    # ---- Programmierung ------------------------------------------------------
    "code":      '<path d="M34 28 C22 28 26 44 16 50 C26 56 22 72 34 72"/>'
                 '<path d="M66 28 C78 28 74 44 84 50 C74 56 78 72 66 72"/>'
                 '<path d="M56 26 L44 74"/>',
    "schlange":  '<path d="M30 30 C30 18 70 18 70 30 V44 C70 52 30 48 30 58 V70'
                 ' C30 82 70 82 70 70"/><circle cx="40" cy="26" r="3"/>'
                 '<circle cx="60" cy="74" r="3"/>',
    "terminal":  '<rect x="14" y="24" width="72" height="52" rx="4"/>'
                 '<path d="M14 38 H86"/><path d="M26 52 L36 60 L26 68 M44 68 H64"/>',
    "chip":      '<rect x="30" y="30" width="40" height="40" rx="3"/>'
                 '<path d="M38 30 V18 M50 30 V18 M62 30 V18 M38 70 V82 M50 70 V82 M62 70 V82'
                 ' M30 38 H18 M30 50 H18 M30 62 H18 M70 38 H82 M70 50 H82 M70 62 H82"/>',
    "netzwerk":  '<circle cx="50" cy="22" r="8"/><circle cx="22" cy="72" r="8"/>'
                 '<circle cx="78" cy="72" r="8"/><circle cx="50" cy="50" r="8"/>'
                 '<path d="M50 30 V42 M44 56 L28 66 M56 56 L72 66 M30 72 H70"/>',

    # ---- Versorgung ----------------------------------------------------------
    "glas":      '<path d="M32 28 H68 V78 a6 6 0 0 1 -6 6 H38 a6 6 0 0 1 -6 -6 Z"/>'
                 '<path d="M28 22 H72"/><path d="M38 44 H62 M38 58 H62"/>',
    "pflanze":   '<path d="M50 84 V44"/><path d="M50 56 C34 56 26 46 26 32 C42 32 50 42 50 56 Z"/>'
                 '<path d="M50 48 C66 48 74 38 74 24 C58 24 50 34 50 48 Z"/>',
    "feuer":     '<path d="M50 84 C30 84 22 70 28 56 c4 8 8 8 10 4 c4 -12 -4 -20 2 -32'
                 ' c2 14 14 14 14 26 c4 -6 4 -12 2 -16 c14 10 18 24 12 36 c-2 6 -10 10 -18 10 Z"/>',
    "acker":     '<path d="M12 70 C28 62 44 78 60 70 C72 64 80 68 88 70"/>'
                 '<path d="M12 82 C28 74 44 90 60 82 C72 76 80 80 88 82"/>'
                 '<path d="M50 58 V26"/><path d="M50 40 C38 40 34 32 34 22 C46 22 50 30 50 40 Z"/>',
    "haus":      '<path d="M18 50 L50 22 L82 50"/><path d="M26 46 V80 H74 V46"/>'
                 '<path d="M42 80 V60 H58 V80"/>',
    "anleitung": '<rect x="24" y="16" width="52" height="68" rx="3"/>'
                 '<path d="M34 34 l6 6 l10 -12 M56 36 H68 M34 54 l6 6 l10 -12 M56 56 H68'
                 ' M34 72 h6 M56 72 H68"/>',
    "topf":      '<path d="M22 40 H78 V66 a10 10 0 0 1 -10 10 H32 a10 10 0 0 1 -10 -10 Z"/>'
                 '<path d="M14 46 H22 M78 46 H86"/>'
                 '<path d="M38 30 c0 -8 6 -8 6 -14 M54 30 c0 -8 6 -8 6 -14"/>',

    # ---- Neustart ------------------------------------------------------------
    "amboss":   '<path d="M20 46 H80 V58 H62 L66 74 H34 L38 58 H20 Z"/>'
                '<path d="M20 46 L10 40 L16 30 L28 46"/><path d="M34 82 H66"/>',
    "ofen":     '<path d="M26 84 V44 a24 24 0 0 1 48 0 V84 Z"/>'
                '<path d="M40 84 V64 h20 v20"/><path d="M50 20 v-8 M36 26 l-6 -6 M64 26 l6 -6"/>',
    "chemie":   '<path d="M42 16 V40 L22 76 a6 6 0 0 0 5 9 H73 a6 6 0 0 0 5 -9 L58 40 V16 Z"/>'
                '<path d="M36 16 H64"/><path d="M32 62 H68"/>',
    "faden":    '<ellipse cx="50" cy="26" rx="20" ry="8"/>'
                '<path d="M30 26 V74 M70 26 V74"/><ellipse cx="50" cy="74" rx="20" ry="8"/>'
                '<path d="M30 42 H70 M30 58 H70"/>',
    "gluehbirne": '<path d="M38 66 a20 20 0 1 1 24 0 v8 H38 Z"/>'
                  '<path d="M40 78 H60 M42 86 H58"/><path d="M44 62 l6 -14 l6 14"/>',
    "gemeinschaft": '<circle cx="28" cy="34" r="9"/><circle cx="72" cy="34" r="9"/>'
                    '<circle cx="50" cy="28" r="11"/>'
                    '<path d="M14 72 c0 -12 10 -18 14 -18 M86 72 c0 -12 -10 -18 -14 -18"/>'
                    '<path d="M32 80 c0 -16 10 -24 18 -24 s18 8 18 24"/>',

    # ---- Sicherung -----------------------------------------------------------
    "auge":     '<path d="M14 50 C28 30 72 30 86 50 C72 70 28 70 14 50 Z"/>'
                '<circle cx="50" cy="50" r="12"/><circle cx="50" cy="50" r="4"/>',
    "schild":   '<path d="M50 14 L82 26 C82 54 70 74 50 86 C30 74 18 54 18 26 Z"/>'
                '<path d="M38 50 l8 10 l18 -22"/>',
    "maske":    '<path d="M24 38 C24 26 76 26 76 38 V52 C76 72 62 82 50 82 S24 72 24 52 Z"/>'
                '<circle cx="38" cy="46" r="4"/><circle cx="62" cy="46" r="4"/>'
                '<path d="M34 64 h32 M30 34 l-14 -8 M70 34 l14 -8"/>',
    "strahlung": '<circle cx="50" cy="50" r="7"/>'
                 '<path d="M50 20 A30 30 0 0 1 76 65 L62 57 A14 14 0 0 0 50 36 Z"/>'
                 '<path d="M24 65 A30 30 0 0 1 50 20 V36 A14 14 0 0 0 38 57 Z"/>'
                 '<path d="M76 65 A30 30 0 0 1 24 65 L38 57 A14 14 0 0 0 62 57 Z"/>',
    "seuche":   '<circle cx="50" cy="50" r="18"/>'
                '<path d="M50 32 V16 M50 68 V84 M32 50 H16 M68 50 H84'
                ' M37 37 L26 26 M63 63 L74 74 M63 37 L74 26 M37 63 L26 74"/>'
                '<circle cx="44" cy="46" r="3"/><circle cx="56" cy="54" r="3"/>',
    "kompass":  '<circle cx="50" cy="50" r="32"/>'
                '<path d="M62 38 L44 44 L38 62 L56 56 Z"/>'
                '<path d="M50 10 v8 M50 82 v8 M10 50 h8 M82 50 h8"/>',
    "waage":    '<path d="M50 18 V80 M30 80 H70"/><path d="M22 34 H78"/>'
                '<path d="M22 34 L12 56 a12 12 0 0 0 20 0 Z"/>'
                '<path d="M78 34 L68 56 a12 12 0 0 0 20 0 Z"/><circle cx="50" cy="28" r="5"/>',

    # ---- Energie -------------------------------------------------------------
    "sonne":     '<circle cx="50" cy="50" r="18"/>'
                 '<path d="M50 14 v10 M50 76 v10 M14 50 h10 M76 50 h10'
                 ' M23 23 l7 7 M70 70 l7 7 M77 23 l-7 7 M30 70 l-7 7"/>',
    "generator": '<circle cx="50" cy="50" r="26"/>'
                 '<path d="M36 58 C44 40 56 60 64 42"/>'
                 '<path d="M50 24 V12 M50 76 v12 M24 50 H12 M76 50 h12"/>',
    "gas":       '<path d="M30 84 V52 a20 20 0 0 1 40 0 V84 Z"/>'
                 '<path d="M50 32 c-6 -8 0 -14 4 -18 c-2 10 8 10 6 18"/>'
                 '<path d="M38 84 V66 h24 v18"/>',
    "wasserrad": '<circle cx="50" cy="46" r="26"/><circle cx="50" cy="46" r="6"/>'
                 '<path d="M50 20 V72 M24 46 H76 M32 28 L68 64 M68 28 L32 64"/>'
                 '<path d="M12 84 C28 76 44 92 60 84 C72 78 80 82 88 84"/>',
    "pumpe":     '<circle cx="42" cy="54" r="20"/><path d="M42 34 V54 H62"/>'
                 '<path d="M62 44 H80 V64 H62"/><path d="M42 74 V86 M28 86 H56"/>',

    # ---- Medizin -------------------------------------------------------------
    "herz":      '<path d="M50 82 C26 64 16 52 16 38 a16 16 0 0 1 34 -8 a16 16 0 0 1 34 8'
                 ' c0 14 -10 26 -34 44 Z"/><path d="M22 48 H38 l6 -10 l8 20 l6 -10 H78"/>',
    "kreuz":     '<path d="M42 16 H58 V42 H84 V58 H58 V84 H42 V58 H16 V42 H42 Z"/>',
    "pille":     '<rect x="14" y="38" width="72" height="24" rx="12" transform="rotate(-20 50 50)"/>'
                 '<path d="M38 62 L62 38"/>',
    "spritze":   '<path d="M20 80 L38 62"/><path d="M34 52 L48 66 L70 44 L56 30 Z"/>'
                 '<path d="M62 24 L76 38"/><path d="M52 34 l8 8 M44 42 l8 8"/>',
    "stethoskop": '<path d="M26 16 V42 a14 14 0 0 0 28 0 V16"/>'
                  '<path d="M40 56 V66 a14 14 0 0 0 28 0 V58"/><circle cx="68" cy="50" r="9"/>'
                  '<circle cx="22" cy="16" r="4"/><circle cx="58" cy="16" r="4"/>',
    "baby":      '<circle cx="50" cy="38" r="20"/><circle cx="43" cy="36" r="3"/>'
                 '<circle cx="57" cy="36" r="3"/><path d="M42 46 c4 4 12 4 16 0"/>'
                 '<path d="M30 60 C30 78 70 78 70 60"/><path d="M38 20 c6 -8 18 -8 24 0"/>',
    "skalpell":  '<path d="M18 82 L44 56"/><path d="M40 52 L60 32 a14 14 0 0 1 20 20 L60 72 Z"/>'
                 '<path d="M52 44 L68 60"/>',
    "zahn":      '<path d="M28 30 C28 18 44 16 50 22 C56 16 72 18 72 30 C72 46 66 52 64 68'
                 ' C62 80 54 82 52 68 L50 56 L48 68 C46 82 38 80 36 68 C34 52 28 46 28 30 Z"/>',
    "tropfen":   '<path d="M50 14 C34 38 26 50 26 60 a24 24 0 0 0 48 0 c0 -10 -8 -22 -24 -46 Z"/>'
                 '<path d="M38 62 a12 12 0 0 0 12 12"/>',
    "mikrobe":   '<circle cx="50" cy="50" r="22"/><circle cx="42" cy="44" r="4"/>'
                 '<circle cx="58" cy="52" r="5"/><circle cx="48" cy="60" r="3"/>'
                 '<path d="M50 28 v-10 M50 72 v10 M28 50 h-10 M72 50 h10'
                 ' M34 34 l-7 -7 M66 66 l7 7 M66 34 l7 -7 M34 66 l-7 7"/>',

    # ---- Archiv und Karten ---------------------------------------------------
    "buch":      '<path d="M16 30 C30 22 44 24 50 30 L50 80 C44 74 30 72 16 80 Z"/>'
                 '<path d="M84 30 C70 22 56 24 50 30 L50 80 C56 74 70 72 84 80 Z"/>',
    "globus":    '<circle cx="50" cy="50" r="32"/><ellipse cx="50" cy="50" rx="13" ry="32"/>'
                 '<path d="M18 50 H82 M24 32 C38 40 62 40 76 32 M24 68 C38 60 62 60 76 68"/>',
    "woerter":   '<rect x="18" y="20" width="64" height="60" rx="4"/>'
                 '<path d="M30 62 L40 34 L50 62 M33 54 H47"/>'
                 '<path d="M58 34 H72 L58 62 H72"/>',
    "forum":     '<path d="M14 24 H62 V56 H34 L22 68 V56 H14 Z"/>'
                 '<path d="M70 40 H86 V72 H78 V84 L66 72 H46"/>'
                 '<path d="M24 34 H52 M24 44 H44"/>',
    "karte":     '<path d="M16 28 L38 20 L62 30 L84 22 V72 L62 80 L38 70 L16 78 Z"/>'
                 '<path d="M38 20 V70 M62 30 V80"/>',
    "route":     '<path d="M26 78 C26 58 74 62 74 40" stroke-dasharray="6 6"/>'
                 '<path d="M26 78 a8 8 0 1 0 0 -16 a8 8 0 0 0 0 16 Z"/>'
                 '<path d="M74 14 c-9 0 -14 7 -14 14 c0 11 14 22 14 22 s14 -11 14 -22'
                 ' c0 -7 -5 -14 -14 -14 Z"/><circle cx="74" cy="28" r="5"/>',
    "ort":       '<path d="M50 12 c-14 0 -22 10 -22 22 c0 16 22 40 22 40 s22 -24 22 -40'
                 ' c0 -12 -8 -22 -22 -22 Z"/><circle cx="50" cy="34" r="8"/>'
                 '<path d="M26 84 H74"/>',
    "hoehe":     '<path d="M14 74 C30 62 44 78 58 66 C70 56 80 62 88 58"/>'
                 '<path d="M14 58 C30 46 44 62 58 50 C70 40 80 46 88 42"/>'
                 '<path d="M14 42 C30 30 44 46 58 34 C70 24 80 30 88 26"/>',
    # ---- KI-Funktionen -------------------------------------------------------
    "fragen":    '<path d="M14 24 H86 V64 H46 L28 80 V64 H14 Z"/>'
                 '<path d="M40 38 a10 10 0 1 1 10 12 v4"/><circle cx="50" cy="58" r="2.5"/>',
    "arbeiten":  '<path d="M18 26 H70 V58 H40 L26 70 V58 H18 Z"/>'
                 '<path d="M30 40 h28 M30 48 h18"/>'
                 '<circle cx="70" cy="70" r="13"/><circle cx="70" cy="70" r="4"/>'
                 '<path d="M70 52 v6 M70 82 v6 M52 70 h6 M82 70 h6"/>',
    "quellen":   '<path d="M22 20 H62 L74 32 V70 H22 Z"/><path d="M62 20 V32 H74"/>'
                 '<path d="M32 44 H64 M32 54 H64 M32 62 H52"/>'
                 '<path d="M30 78 H82 V36"/>',
    "drucken":   '<path d="M30 34 V16 H70 V34"/>'
                 '<path d="M18 34 H82 V62 H70 V50 H30 V62 H18 Z"/>'
                 '<path d="M30 50 H70 V84 H30 Z"/><path d="M38 60 H62 M38 70 H62"/>'
                 '<circle cx="72" cy="42" r="3"/>',
    "lehrblatt": '<rect x="20" y="14" width="60" height="72" rx="3"/>'
                 '<rect x="30" y="26" width="40" height="24" rx="2"/>'
                 '<path d="M34 46 L44 34 L52 42 L58 36 L66 46"/>'
                 '<path d="M30 60 H70 M30 68 H70 M30 76 H54"/>',
    "foto":      '<path d="M14 34 H32 L38 24 H62 L68 34 H86 V78 H14 Z"/>'
                 '<circle cx="50" cy="54" r="16"/><circle cx="50" cy="54" r="7"/>'
                 '<circle cx="76" cy="42" r="3"/>',
    "vorlesen":  '<path d="M20 40 H34 L52 24 V76 L34 60 H20 Z"/>'
                 '<path d="M62 38 a16 16 0 0 1 0 24"/><path d="M72 28 a30 30 0 0 1 0 44"/>',
    "zurueck":   '<circle cx="50" cy="50" r="30" stroke-dasharray="6 6"/>'
                 '<path d="M60 34 L42 50 L60 66"/>',
}


def svg(kennung, klasse="motiv"):
    """Motiv als SVG-Gruppe. Unbekannte Kennung ergibt einen Punkt, nie einen Absturz."""
    inhalt = GLYPHEN.get(kennung) or '<circle cx="50" cy="50" r="8"/>'
    return f'<g class="{klasse}">{inhalt}</g>'
