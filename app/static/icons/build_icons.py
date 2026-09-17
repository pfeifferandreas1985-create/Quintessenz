# -*- coding: utf-8 -*-
"""
Erzeugt die 16 animierten Bereichslogos des Quintessenz-Terminals als eigenständige SVG-Dateien
(Tron-Blau, transparenter Hintergrund, ruhige Dauerbewegung, bei Hover schneller und heller)
sowie eine Demo-Seite mit allen 16.

    python build_icons.py            # schreibt <KUERZEL>_<name>.svg + demo_icons.html

Nur SVG + CSS, kein JavaScript. Einbinden als Inline-SVG oder <object>; per <img> laufen die
Animationen, aber der Hover-Zustand nicht. Farben über CSS-Variablen am SVG-Wurzelelement
umstellbar (--p Grundfarbe, --h Hover-Farbe, --a Akzent). Alle Bewegungen respektieren
prefers-reduced-motion.
"""
import math
from pathlib import Path

HIER = Path(__file__).resolve().parent

FARBEN = {"p": "#3FC8FF", "h": "#CFF7FF", "a": "#FF8A00"}   # Tron: Cyan, Weiß-Cyan, Orange

STIL = """
    svg { --f: 1; }
    svg:hover { --f: .22; }
    .linie { fill: none; stroke: var(--p); stroke-linecap: round; stroke-linejoin: round; stroke-width: 2.4; }
    .fuell { fill: var(--p); stroke: none; }
    .duenn { stroke-width: 1.4; }
    .dick  { stroke-width: 3.4; }
    .motiv { filter: url(#glow); }
    svg:hover .motiv { filter: url(#glow-stark); }
    svg:hover .linie { stroke: var(--h); }
    svg:hover .fuell { fill: var(--h); }
    svg:hover .akzent { stroke: var(--a); }
    svg:hover .akzent-fuell { fill: var(--a); }
    .ring-aussen { stroke-width: 2; stroke-dasharray: 34 10 4 10; --t: 24s; --o: 100px 96px; }
    .ring-innen  { stroke-width: 1; stroke-dasharray: 2 6; opacity: .7; --t: 16s; --o: 100px 96px; }
    .ring-marke  { stroke-width: 3; stroke-dasharray: 6 214; --t: 6s; --o: 100px 96px; }
    svg:hover .ring-marke { stroke: var(--a); }
    .anim-drehen   { animation: drehen calc(var(--t) * var(--f)) linear infinite; transform-origin: var(--o); }
    .anim-drehen-r { animation: drehen calc(var(--t) * var(--f)) linear infinite reverse; transform-origin: var(--o); }
    .anim-pendeln  { animation: pendeln calc(var(--t) * var(--f)) ease-in-out infinite alternate; transform-origin: var(--o); }
    .anim-fliessen { stroke-dasharray: var(--d, 5 7); animation: fliessen calc(var(--t) * var(--f)) linear infinite; }
    .anim-atmen    { animation: atmen calc(var(--t) * var(--f)) ease-in-out infinite; }
    .anim-blinken  { animation: blinken calc(var(--t) * var(--f)) steps(1) infinite; }
    .anim-pulsieren{ animation: pulsieren calc(var(--t) * var(--f)) ease-out infinite; transform-origin: var(--o); }
    .anim-blicken  { animation: blicken calc(var(--t) * var(--f)) ease-in-out infinite; }
    .anim-wippen   { animation: wippen calc(var(--t) * var(--f)) ease-in-out infinite alternate; }
    svg:hover .hover-flackern { animation: flackern .9s steps(1) infinite; }
    .funke { opacity: 0; transform-origin: 100px 96px; stroke-width: 2; }
    svg:hover .funke { animation: funkeln 1.1s ease-out infinite; stroke: var(--a); }
    .schild { fill: var(--p); font: 700 13px/1 "Jost", "League Spartan", "Futura", "Century Gothic", sans-serif;
              letter-spacing: 3.5px; text-anchor: middle; }
    svg:hover .schild { fill: var(--h); }
    @keyframes drehen    { to { transform: rotate(360deg); } }
    @keyframes pendeln   { from { transform: rotate(calc(-1 * var(--w, 12deg))); } to { transform: rotate(var(--w, 12deg)); } }
    @keyframes fliessen  { to { stroke-dashoffset: var(--v, -24); } }
    @keyframes atmen     { 0%, 100% { opacity: .35; } 50% { opacity: 1; } }
    @keyframes blinken   { 0%, 49% { opacity: 1; } 50%, 100% { opacity: .15; } }
    @keyframes pulsieren { 0% { transform: scale(.92); opacity: .8; } 60% { transform: scale(1.06); opacity: 1; } 100% { transform: scale(.92); opacity: .8; } }
    @keyframes blicken   { 0%, 20% { transform: translateX(-6px); } 45%, 65% { transform: translateX(6px); } 85%, 100% { transform: translateX(-6px); } }
    @keyframes wippen    { from { transform: translateY(-1.5px); } to { transform: translateY(1.5px); } }
    @keyframes flackern  { 0% { opacity: 1; } 12% { opacity: .35; } 20% { opacity: 1; } 47% { opacity: .9; }
                           55% { opacity: .2; } 62% { opacity: 1; } 81% { opacity: .6; } 88% { opacity: 1; } 100% { opacity: 1; } }
    @keyframes funkeln   { 0% { opacity: 0; transform: scale(.6); } 15% { opacity: 1; } 100% { opacity: 0; transform: scale(1.25); } }
    @media (prefers-reduced-motion: reduce) { * { animation: none !important; } }
"""

VORLAGE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200" role="img" aria-label="Bereich {schild}">
  <title>{schild}</title>
  <!-- Bereichslogo {kuerzel} · {schild} · Quintessenz-Terminal · erzeugt von build_icons.py -->
  <defs>
    <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="2" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="glow-stark" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="4.5" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <style>
    :root {{ --p: {p}; --h: {h}; --a: {a}; }}{stil}
  </style>
  <rect width="200" height="200" fill="transparent"/>
  <circle class="linie ring-aussen anim-drehen"   cx="100" cy="96" r="80"/>
  <circle class="linie ring-innen  anim-drehen-r" cx="100" cy="96" r="71"/>
  <circle class="linie ring-marke  anim-drehen"   cx="100" cy="96" r="80"/>
  <g class="motiv">
{motiv}
  </g>
  <text class="schild" x="100" y="195">{schild}</text>
</svg>
"""


def zahnrad(cx, cy, r_aussen, r_innen, zaehne, breite=0.5):
    """Pfad eines Zahnrads (Polygon)."""
    pts = []
    for i in range(zaehne):
        a0 = 2 * math.pi * i / zaehne
        a1 = a0 + 2 * math.pi / zaehne * breite * 0.5
        a2 = a0 + 2 * math.pi / zaehne * (0.5 + breite * 0.5)
        a3 = a0 + 2 * math.pi / zaehne * 0.5
        for a, r in ((a0, r_innen), (a1, r_aussen), (a2, r_aussen), (a3, r_innen)):
            pts.append(f"{cx + r * math.cos(a):.1f} {cy + r * math.sin(a):.1f}")
    return "M" + " L".join(pts) + " Z"


def stern(cx, cy, r1, r2, zacken):
    pts = []
    for i in range(zacken * 2):
        a = math.pi * i / zacken - math.pi / 2
        r = r1 if i % 2 == 0 else r2
        pts.append(f"{cx + r * math.cos(a):.1f} {cy + r * math.sin(a):.1f}")
    return "M" + " L".join(pts) + " Z"


def rad(cx, cy, r, t="6s"):
    """Rad mit zwei Speichen, dreht sich."""
    return (f'<g class="anim-drehen" style="--t:{t};--o:{cx}px {cy}px">'
            f'<circle class="linie" cx="{cx}" cy="{cy}" r="{r}"/>'
            f'<path class="linie duenn" d="M{cx - r} {cy} L{cx + r} {cy} M{cx} {cy - r} L{cx} {cy + r}"/></g>')


ICONS = {}

ICONS["EL"] = ("elektrik", "ELEKTRIK", f"""
    <path class="linie dick anim-atmen hover-flackern" style="--t:3.2s" d="M111 36 L85 88 L103 88 L89 130 L123 78 L105 78 L117 36 Z"/>
    <path class="linie duenn hover-flackern" style="stroke:#EAFBFF;opacity:.55" d="M109 42 L91 84 L105 84 L95 121 L117 80 L101 80 L111 42"/>
    <path class="linie funke" d="M123 76 l9 -6 M125 82 l10 2"/>
    <path class="linie funke" style="animation-delay:-.4s" d="M85 90 l-10 -3 M83 84 l-8 -7"/>
    <path class="linie funke" style="animation-delay:-.75s" d="M89 130 l-6 9 M93 132 l2 11"/>
    <path class="linie anim-fliessen" style="--t:2.4s" d="M58 150 C65 136 75 136 79 150 C83 164 93 164 100 150"/>
    <path class="linie anim-fliessen" style="--t:2.4s;animation-delay:-1.2s" d="M100 150 C107 136 117 136 121 150 C125 164 135 164 142 150"/>
""")

ICONS["ME"] = ("mechanik", "MECHANIK", f"""
    <path class="linie anim-drehen" style="--t:30s;--o:100px 96px" d="{zahnrad(100, 96, 46, 38, 12)}"/>
    <circle class="linie duenn" cx="100" cy="96" r="30"/>
    <circle class="linie" cx="100" cy="96" r="11"/>
    <g class="anim-drehen-r" style="--t:12s;--o:100px 96px">
      {''.join(f'<circle class="fuell" cx="{100 + 20.5 * math.cos(2 * math.pi * i / 8):.1f}" cy="{96 + 20.5 * math.sin(2 * math.pi * i / 8):.1f}" r="3.2"/>' for i in range(8))}
    </g>
    <path class="linie funke" d="M146 60 l8 -8 M150 70 l10 -2"/>
    <path class="linie funke" style="animation-delay:-.5s" d="M54 130 l-8 8 M50 120 l-10 2"/>
""")

ICONS["AN"] = ("antrieb", "ANTRIEB", """
    <rect class="linie" x="54" y="92" width="58" height="34" rx="4"/>
    <path class="linie duenn" d="M66 98 v22 M76 98 v22 M86 98 v22 M96 98 v22"/>
    <path class="linie dick akzent" d="M112 109 L140 109"/>
    <g class="anim-drehen" style="--t:2s;--o:140px 109px"><path class="linie duenn" d="M140 101 v16 M132 109 h16"/></g>
    <path class="linie duenn" d="M54 80 L54 40 M54 80 L150 80"/>
    <path class="linie anim-fliessen" style="--t:3s;--d:60 200;--v:-260" d="M56 78 C80 76 96 50 148 44"/>
    <g class="anim-pendeln" style="--t:2.2s;--w:35deg;--o:70px 146px">
      <circle class="linie" cx="70" cy="146" r="11"/><path class="linie akzent" d="M70 146 L70 137"/>
    </g>
    <path class="linie duenn" d="M96 140 h50 M96 152 h36" />
    <path class="linie funke" d="M144 100 l8 -6 M146 118 l10 4"/>
""")

ICONS["AU"] = ("automation", "AUTOMATION", """
    <rect class="linie" x="56" y="84" width="34" height="46" rx="3"/>
    <path class="linie duenn anim-fliessen" style="--t:2.6s;--d:4 4" d="M60 90 L86 116 M60 100 L86 126 M60 110 L80 130 M66 88 L86 108 M76 88 L86 98"/>
    <path class="linie" d="M73 84 V64 M73 130 V150"/>
    <circle class="fuell" cx="112" cy="90" r="3.5"/>
    <g class="anim-pendeln" style="--t:1.6s;--w:7deg;--o:112px 90px">
      <path class="linie dick akzent" d="M112 90 L150 90"/>
    </g>
    <path class="linie" d="M150 74 h-8 M150 106 h-8"/>
    <circle class="fuell" cx="150" cy="80" r="2.5"/><circle class="fuell" cx="150" cy="100" r="2.5"/>
    <path class="linie duenn" d="M112 90 V150 M150 80 H166 V150 M150 100 H160 V150"/>
    <path class="linie funke" d="M150 92 l8 -4 M154 84 l6 -6"/>
""")

ICONS["MP"] = ("messen", "MESSEN", """
    <path class="linie" d="M52 112 A50 50 0 0 1 148 112"/>
    <path class="linie dick akzent" style="stroke:var(--a);opacity:.85" d="M129 74 A50 50 0 0 1 148 112"/>
    <path class="linie duenn" d="M56 100 l7 2 M64 82 l6 4 M78 68 l4 6 M100 62 v7 M122 68 l-4 6"/>
    <g class="anim-pendeln" style="--t:3.4s;--w:38deg;--o:100px 118px">
      <path class="linie dick" d="M100 118 L100 70"/>
      <path class="linie duenn akzent" d="M100 70 l-3 8 h6 z"/>
    </g>
    <circle class="fuell" cx="100" cy="118" r="4"/>
    <path class="linie" d="M60 120 H140"/>
    <path class="linie akzent" d="M64 158 L82 132"/><path class="linie" d="M136 158 L118 132"/>
    <circle class="fuell" cx="62" cy="161" r="2.5"/><circle class="fuell" cx="138" cy="161" r="2.5"/>
    <path class="linie funke" d="M140 100 l8 -3 M142 90 l8 -6"/>
""")

_loecher = []
for reihe in range(4):
    for spalte in range(7):
        x, y, n = 64 + spalte * 11, 76 + reihe * 13, reihe * 7 + spalte
        if (n * 7 + reihe) % 3 != 1:
            _loecher.append(f'<rect class="fuell anim-blinken" style="--t:{2.2 + (n % 5) * 0.4:.1f}s;animation-delay:-{(n * 0.37) % 2.2:.2f}s" x="{x}" y="{y}" width="4" height="7"/>')
ICONS["PR"] = ("programm", "PROGRAMM", f"""
    <path class="linie" d="M54 60 L136 60 L150 74 L150 138 L54 138 Z"/>
    <path class="linie duenn" d="M136 60 V74 H150"/>
    {''.join(_loecher)}
    <rect class="fuell akzent-fuell anim-blinken" style="--t:1s" x="62" y="128" width="9" height="5"/>
    <path class="linie duenn" d="M76 130 h30"/>
    <path class="linie funke" d="M152 70 l8 -6 M154 82 l10 0"/>
""")

ICONS["MD"] = ("medizin", "MEDIZIN", """
    <path class="linie dick" d="M92 48 h16 v22 h22 v16 h-22 v22 h-16 v-22 h-22 v-16 h22 z"/>
    <path class="linie duenn" d="M100 56 V126"/>
    <path class="linie anim-fliessen" style="--t:3s;--d:4 3" d="M92 62 C112 70 88 82 108 92 C90 102 110 114 96 124"/>
    <circle class="fuell" cx="100" cy="52" r="2.5"/>
    <path class="linie akzent anim-fliessen" style="--t:2.8s;--d:70 130;--v:-200" d="M44 152 L70 152 L78 140 L86 166 L94 146 L100 152 L156 152"/>
    <path class="linie funke" d="M132 60 l8 -6 M134 70 l10 0"/>
""")

ICONS["SV"] = ("versorgung", "VERSORGUNG", """
    <path class="linie" d="M46 74 Q100 26 154 74"/>
    <path class="linie duenn" d="M58 64 l-6 -8 M70 56 l-4 -9 M84 50 l-2 -10 M100 48 v-10 M116 50 l2 -10 M130 56 l4 -9 M142 64 l6 -8"/>
    <rect class="linie" x="58" y="88" width="40" height="52" rx="6"/>
    <rect class="linie" x="55" y="80" width="46" height="9" rx="2"/>
    <path class="linie duenn" d="M66 104 h24 M66 116 h24 M66 128 h14"/>
    <g class="anim-pulsieren hover-flackern" style="--t:1.6s;--o:126px 140px">
      <path class="linie akzent" d="M126 140 C106 122 120 110 122 92 C128 104 140 108 134 122 C142 114 148 122 146 132 C144 138 136 140 126 140 Z"/>
      <path class="linie duenn" d="M126 134 C118 124 126 116 128 108 C134 118 136 126 126 134 Z"/>
    </g>
    <path class="linie funke" d="M148 100 l8 -6 M150 112 l10 0"/>
""")

ICONS["EN"] = ("energie", "ENERGIE", """
    <circle class="linie" cx="74" cy="72" r="14"/>
    <g class="anim-drehen" style="--t:20s;--o:74px 72px">
      <path class="linie duenn" d="M74 50 v-8 M74 94 v8 M52 72 h-8 M96 72 h8 M58.4 56.4 l-5.6 -5.6 M89.6 87.6 l5.6 5.6 M58.4 87.6 l-5.6 5.6 M89.6 56.4 l5.6 -5.6"/>
    </g>
    <rect class="linie" x="106" y="60" width="44" height="24" rx="3"/><rect class="fuell" x="150" y="67" width="5" height="10"/>
    <rect class="fuell anim-blinken" style="--t:3.2s;animation-delay:-0s" x="111" y="65" width="7" height="14"/>
    <rect class="fuell anim-blinken" style="--t:3.2s;animation-delay:-.8s" x="120" y="65" width="7" height="14"/>
    <rect class="fuell anim-blinken" style="--t:3.2s;animation-delay:-1.6s" x="129" y="65" width="7" height="14"/>
    <rect class="fuell akzent-fuell anim-blinken" style="--t:3.2s;animation-delay:-2.4s" x="138" y="65" width="7" height="14"/>
    <g class="anim-drehen" style="--t:9s;--o:100px 128px">
      <circle class="linie" cx="100" cy="128" r="20"/>
      <path class="linie duenn" d="M100 108 V148 M80 128 H120 M85.9 113.9 L114.1 142.1 M114.1 113.9 L85.9 142.1"/>
    </g>
    <path class="linie duenn anim-fliessen" style="--t:2s;--d:6 6" d="M56 156 Q66 150 76 156 T96 156 T116 156 T136 156 T146 156"/>
    <path class="linie funke" d="M150 100 l8 -6 M152 112 l10 0"/>
""")

ICONS["KO"] = ("funk", "FUNK", """
    <path class="linie" d="M100 142 V66"/>
    <path class="linie" d="M84 142 L100 100 L116 142 Z"/>
    <path class="linie duenn" d="M92 122 h16 M88 132 h24"/>
    <circle class="fuell akzent-fuell" cx="100" cy="62" r="3.5"/>
    <path class="linie anim-atmen" style="--t:2.4s" d="M86 52 A16 16 0 0 1 114 52"/>
    <path class="linie anim-atmen" style="--t:2.4s;animation-delay:-.8s" d="M76 44 A28 28 0 0 1 124 44"/>
    <path class="linie anim-atmen" style="--t:2.4s;animation-delay:-1.6s" d="M66 36 A40 40 0 0 1 134 36"/>
    <g class="anim-blinken" style="--t:1.4s"><circle class="fuell" cx="60" cy="158" r="2.6"/><rect class="fuell" x="70" y="156" width="10" height="4"/></g>
    <g class="anim-blinken" style="--t:1.4s;animation-delay:-.7s"><circle class="fuell" cx="90" cy="158" r="2.6"/><circle class="fuell" cx="100" cy="158" r="2.6"/><rect class="fuell" x="110" y="156" width="10" height="4"/></g>
    <g class="anim-blinken" style="--t:1.4s;animation-delay:-.35s"><rect class="fuell" x="126" y="156" width="10" height="4"/><circle class="fuell" cx="142" cy="158" r="2.6"/></g>
    <path class="linie funke" d="M130 60 l8 -6 M132 72 l10 0"/>
""")

ICONS["SI"] = ("sicherung", "SICHERUNG", """
    <path class="linie dick" d="M100 44 L148 60 C148 100 130 130 100 148 C70 130 52 100 52 60 Z"/>
    <path class="linie duenn" d="M100 54 L138 66 C138 98 124 122 100 136 C76 122 62 98 62 66 Z"/>
    <path class="linie" d="M70 96 Q100 70 130 96 Q100 122 70 96 Z"/>
    <g class="anim-blicken" style="--t:6s">
      <circle class="linie" cx="100" cy="96" r="9"/>
      <circle class="fuell akzent-fuell" cx="100" cy="96" r="3.5"/>
    </g>
    <path class="linie funke" d="M146 56 l8 -6 M148 68 l10 0"/>
""")

ICONS["NS"] = ("neustart", "NEUSTART", """
    <path class="linie duenn anim-fliessen" style="--t:12s;--d:8 6;--v:-14" d="M42 122 A58 58 0 0 1 158 122"/>
    <path class="linie" d="M62 112 H138 V124 H112 L116 138 H84 L88 124 H62 Z"/>
    <path class="linie" d="M62 112 L44 108 L50 98 L70 112"/>
    <path class="linie duenn" d="M78 138 H122 V146 H78 Z"/>
    <g class="anim-pendeln" style="--t:1.1s;--w:16deg;--o:96px 118px">
      <path class="linie" d="M96 118 L136 74"/>
      <rect class="linie akzent" x="126" y="58" width="24" height="14" rx="2" transform="rotate(-45 138 65)"/>
    </g>
    <path class="linie funke" d="M104 112 l-6 -8 M110 110 l2 -10 M116 114 l8 -6"/>
""")

ICONS["AW"] = ("archiv", "ARCHIV", """
    <g class="anim-drehen" style="--t:24s;--o:100px 60px">
      <circle class="linie" cx="100" cy="60" r="20"/>
    </g>
    <ellipse class="linie duenn anim-fliessen" style="--t:4s;--d:4 4" cx="100" cy="60" rx="20" ry="7"/>
    <ellipse class="linie duenn" cx="100" cy="60" rx="8" ry="20"/>
    <path class="linie duenn" d="M80 60 H120"/>
    <path class="linie" d="M54 96 C70 88 88 90 100 98 L100 146 C88 138 70 136 54 144 Z"/>
    <path class="linie" d="M146 96 C130 88 112 90 100 98 L100 146 C112 138 130 136 146 144 Z"/>
    <path class="linie duenn anim-fliessen" style="--t:3s;--d:30 8;--v:-38" d="M62 104 C74 99 86 100 94 105 M62 114 C74 109 86 110 94 115 M62 124 C74 119 86 120 94 125"/>
    <path class="linie duenn anim-fliessen" style="--t:3s;--d:30 8;--v:-38;animation-delay:-1.5s" d="M138 104 C126 99 114 100 106 105 M138 114 C126 109 114 110 106 115 M138 124 C126 119 114 120 106 125"/>
    <path class="linie funke" d="M128 44 l8 -6 M130 56 l10 0"/>
""")

ICONS["KN"] = ("karten", "KARTEN", f"""
    <path class="linie" d="M46 128 L72 116 L98 128 L124 116 L150 128 L150 156 L124 168 L98 156 L72 168 L46 156 Z"/>
    <path class="linie duenn" d="M72 116 V168 M98 128 V156 M124 116 V168"/>
    <path class="linie duenn anim-fliessen" style="--t:3s;--d:6 4" d="M50 140 C60 134 66 146 78 140 M104 150 C112 142 120 152 132 146 M128 134 C136 128 142 138 148 134"/>
    <path class="linie" d="{stern(100, 82, 34, 12, 8)}"/>
    <g class="anim-pendeln" style="--t:4s;--w:24deg;--o:100px 82px">
      <path class="linie dick akzent" d="M100 82 L100 54"/>
      <path class="linie dick" d="M100 82 L100 110"/>
    </g>
    <circle class="fuell" cx="100" cy="82" r="3.5"/>
    <path class="linie funke" d="M136 54 l8 -6 M138 66 l10 0"/>
""")

ICONS["KI"] = ("assistent", "ASSISTENT", """
    <rect class="linie" x="50" y="60" width="98" height="64" rx="4"/>
    <rect class="linie anim-atmen" style="--t:2.6s" x="60" y="70" width="9" height="24" rx="4"/>
    <rect class="linie anim-atmen" style="--t:2.6s;animation-delay:-.6s" x="76" y="70" width="9" height="24" rx="4"/>
    <rect class="linie anim-atmen" style="--t:2.6s;animation-delay:-1.2s" x="92" y="70" width="9" height="24" rx="4"/>
    <rect class="linie anim-atmen" style="--t:2.6s;animation-delay:-1.8s" x="108" y="70" width="9" height="24" rx="4"/>
    <circle class="linie duenn" cx="132" cy="80" r="7"/><path class="linie duenn akzent" d="M132 80 L136 75"/>
    <path class="linie duenn" d="M60 106 h20 M88 106 h20 M116 106 h22"/>
    <rect class="fuell anim-blinken" style="--t:.9s" x="60" y="112" width="6" height="4"/>
    <path class="linie anim-fliessen" style="--t:2.2s;--d:3 5" d="M56 136 C72 128 88 146 104 138 C118 131 132 143 148 136"/>
    <path class="linie duenn" d="M56 132 C72 124 88 142 104 134 C118 127 132 139 148 132 M56 140 C72 132 88 150 104 142 C118 135 132 147 148 140"/>
    <g class="anim-wippen" style="--t:1.6s">
      <path class="linie" d="M118 34 H158 Q164 34 164 40 V52 Q164 58 158 58 H134 L126 66 V58 H118 Q112 58 112 52 V40 Q112 34 118 34 Z"/>
      <circle class="fuell anim-blinken" style="--t:1.2s" cx="128" cy="46" r="2.2"/>
      <circle class="fuell anim-blinken" style="--t:1.2s;animation-delay:-.4s" cx="138" cy="46" r="2.2"/>
      <circle class="fuell anim-blinken akzent-fuell" style="--t:1.2s;animation-delay:-.8s" cx="148" cy="46" r="2.2"/>
    </g>
    <path class="linie funke" d="M46 56 l-8 -6 M44 68 l-10 0"/>
""")

ICONS["FZ"] = ("fahrzeuge", "FAHRZEUGE", f"""
    <g class="anim-wippen" style="--t:1.3s">
      <path class="linie" d="M60 84 V66 H74 L82 54 H122 L130 66 H140 V84 Z"/>
      <path class="linie duenn" d="M86 66 H118 M84 66 L88 56 M118 56 L120 66"/>
      {rad(76, 86, 7, "3s")}{rad(124, 86, 7, "3s")}
    </g>
    <g class="anim-wippen" style="--t:1.3s;animation-delay:-.4s">
      <path class="linie" d="M66 122 L70 108 L82 98 H116 L128 108 L134 122 Z"/>
      <path class="linie duenn" d="M84 108 H114 M86 108 L90 99 M112 99 L114 108"/>
      {rad(80, 123, 6, "2.6s")}{rad(120, 123, 6, "2.6s")}
    </g>
    <g class="anim-wippen" style="--t:1.3s;animation-delay:-.8s">
      <path class="linie" d="M94 132 L88 156 H124 C124 142 138 140 142 156"/>
      <path class="linie duenn" d="M94 132 L104 126 M76 156 H88 M116 148 H122"/>
      {rad(74, 157, 7, "2.2s")}{rad(140, 157, 7, "2.2s")}
    </g>
    <path class="linie akzent" d="M46 66 L58 54 M46 66 l-6 -2 l2 -6 l6 2"/>
    <path class="linie funke" d="M150 60 l8 -6 M152 72 l10 0"/>
""")


def main():
    stil = STIL
    for kuerzel, (name, schild, motiv) in ICONS.items():
        svg = VORLAGE.format(kuerzel=kuerzel, schild=schild, motiv=motiv.rstrip(), stil=stil, **FARBEN)
        (HIER / f"{kuerzel}_{name}.svg").write_text(svg, encoding="utf-8", newline="\n")
    kacheln = "\n".join(
        f'  <a class="kachel" href="{k}_{n}.svg" title="{k} · {s}"><object type="image/svg+xml" data="{k}_{n}.svg" aria-label="{s}"></object></a>'
        for k, (n, s, _) in ICONS.items())
    demo = f"""<!doctype html>
<html lang="de"><head><meta charset="utf-8"><title>Quintessenz · 16 Bereichslogos</title>
<style>
  body {{ margin: 0; background: #06090c; color: {FARBEN['p']}; font: 14px/1.4 "Courier Prime", "IBM Plex Mono", monospace; }}
  h1 {{ text-align: center; font-weight: 400; letter-spacing: 4px; margin: 28px 0 8px; }}
  p {{ text-align: center; opacity: .7; margin: 0 0 20px; }}
  main {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 18px; padding: 0 28px 40px; max-width: 1200px; margin: 0 auto; }}
  .kachel {{ display: block; padding: 8px; border: 1px solid #12333d; border-radius: 6px; background: radial-gradient(circle at 50% 40%, #0a1a22 0, #06090c 70%); }}
  .kachel:hover {{ border-color: {FARBEN['p']}; box-shadow: 0 0 18px {FARBEN['p']}44; }}
  .kachel object {{ width: 100%; aspect-ratio: 1; display: block; }}
</style></head><body>
<h1>EINGANG · 16 BEREICHE</h1>
<p>Maus über ein Schild: schneller, heller, Funken. Hintergrund der SVGs ist transparent.</p>
<main>
{kacheln}
</main></body></html>
"""
    (HIER / "demo_icons.html").write_text(demo, encoding="utf-8", newline="\n")
    print(f"{len(ICONS)} SVGs + demo_icons.html geschrieben nach {HIER}")


if __name__ == "__main__":
    main()
