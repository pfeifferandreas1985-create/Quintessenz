# -*- coding: utf-8 -*-
"""
Baut den Ladebildschirm des Quintessenz-Terminals als eine eigenständige HTML-Datei:

  1. Bildröhre schaltet ein: weißer Strich geht auf, Flackern, Raster kommt hoch
  2. Countdown 3 · 2 · 1 mit ablaufendem Ring, dann „WORLD RESTART INITIATED"
  3. Systemcheck als Boot-Text wie auf einem alten Rechner (Schreibmaschine)
  4. Die Zeichen des Boot-Texts fliegen auseinander und werden zu den 16 animierten Logos
  5. Menü: 16 Kacheln, Englisch, jede mit eigener Hover-Farbe, verlinkt in die Anwendung

Die 16 SVGs (englische Schilder aus icons/en/) werden direkt eingebettet, damit Hover-Zustand
und Farbvariablen ohne Server funktionieren. Kein Netz, keine externen Schriften.

    python build_intro.py     ->  intro.html      (Server liefert sie unter /intro)
"""
import re
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER / "icons"))
from build_icons import ICONS, SCHILD_EN, svg_text  # noqa: E402

# Reihenfolge im Menü: Kürzel, englischer Untertitel, Hover-Farbe, Bereichs-ID aus
# app/config/bereiche.yaml (die Kachel führt auf "/#/b/<ID>" in die Anwendung)
MENUE = [
    ("EL", "Electrical engineering",              "#FFB000", "elektrotechnik-und-elektronik"),
    ("ME", "Mechanics & machine elements",        "#FF6A00", "mechanik-und-maschinenelemente"),
    ("AN", "Drives, control & sensors",           "#B4FF3A", "antriebstechnik-regelung-sensorik"),
    ("AU", "Relay logic & PLC basics",            "#FFE733", "sps-und-automatisierung"),
    ("MP", "Test equipment & troubleshooting",    "#FF3B3B", "mess-und-prueftechnik-fehlersuche"),
    ("PR", "Programming & Linux",                 "#33FF66", "programmierung-und-linux"),
    ("MD", "Medicine & first aid",                "#FF4FA3", "medizin"),
    ("SV", "Survival & basic supply",             "#FFA76B", "survival-und-grundversorgung"),
    ("EN", "Energy & infrastructure",             "#FFD447", "energie-und-infrastruktur"),
    ("KO", "Radio & communication",               "#B26BFF", "kommunikation"),
    ("SI", "Defensive basics",                    "#E6E6E6", "militaerische-grundlagen-defensiv"),
    ("NS", "Rebuilding civilization",             "#E07A3F", "zivilisationsneustart"),
    ("AW", "General knowledge & literature",      "#FFF1B8", "allgemeinwissen-sprache-literatur"),
    ("KN", "Maps & navigation",                   "#2EF2C0", "karten-und-navigation"),
    ("KI", "AI capabilities, offline",            "#FF3DF5", "ki-faehigkeiten"),
    ("FZ", "Own vehicles: Defender, Mini, Vespa", "#FF5E5E", "eigene-fahrzeuge"),
]

BOOT = [
    "QUINTESSENZ TERMINAL  //  BIOS 1.0  //  ATOMIC AGE EDITION",
    "",
    "CPU ........ ARM CORTEX-A76 x4 @ 2.4 GHZ .......... OK",
    "MEMORY ..... 16384 MB ............................ OK",
    "STORAGE .... /srv/box  595 GB, READ-ONLY ......... OK",
    "KIWIX ...... 38 ARCHIVES, 2 LANGUAGES ............ OK",
    "MAPS ....... WORLD / EUROPE / DACH / GERMANY ..... OK",
    "MODELS ..... 9 LOADED, NO CLOUD .................. OK",
    "NETWORK .... NONE (BY DESIGN) .................... OK",
    "",
    "SCANNING KNOWLEDGE DOMAINS ....................... 16 FOUND",
    "INITIALIZING INTERFACE",
]


def inline_svg(kuerzel):
    """SVG so einbetten, dass es in HTML sauber liegt: Wurzel ohne feste Größe."""
    s = svg_text(kuerzel, SCHILD_EN[kuerzel])
    s = re.sub(r'\s+width="200" height="200"', "", s, count=1)
    return s.strip()


def main():
    kacheln = []
    for i, (k, untertitel, farbe, bereich_id) in enumerate(MENUE):
        kacheln.append(f"""
      <a class="tile" href="/#/b/{bereich_id}" data-domain="{k}" style="--h:{farbe};--a:#FFFFFF;--i:{i}">
        {inline_svg(k)}
        <span class="tile-code">{k}</span>
        <span class="tile-sub">{untertitel}</span>
      </a>""")
    boot_js = ",\n      ".join(repr(z) for z in BOOT).replace("'", '"')

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>QUINTESSENZ · KNOWLEDGE TERMINAL</title>
<style>
  :root {{ --p: #3FC8FF; --h: #CFF7FF; --a: #FF8A00; --bg: #05080b; --dim: #1a5f78; }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; height: 100%; background: #000; color: var(--p); overflow: hidden;
               font: 15px/1.45 "IBM Plex Mono", "Courier Prime", "Consolas", monospace; }}
  /* Ruhezustand ist "aus". body.on setzt "an" als festen Zustand und spielt das Einschalten ab;
     kein animation-fill-mode, sonst wuerde eine spaetere Animation (Ruettler) den Endzustand
     mitnehmen und der Schirm fiele auf schwarz zurueck. */
  #stage {{ position: relative; width: 100%; height: 100%; background: var(--bg);
            transform: scaleY(0); opacity: 0; }}
  body.on #stage {{ transform: none; opacity: 1; animation: crt-on .85s cubic-bezier(.2,.9,.2,1); }}
  body.on #stage::after {{ content: ""; position: absolute; inset: 0; background: #fff; opacity: 0;
                           pointer-events: none; z-index: 40; animation: crt-flicker 1.5s steps(1) .3s; }}
  body::before {{ /* feine Scanlines über allem */
    content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 50; opacity: .18;
    background: repeating-linear-gradient(0deg, transparent 0 2px, rgba(0,0,0,.6) 2px 3px); }}
  section {{ position: absolute; inset: 0; display: grid; place-items: center; opacity: 0;
             pointer-events: none; transition: opacity .45s; }}
  section.on {{ opacity: 1; pointer-events: auto; }}

  /* ---- 1/2 · Countdown ------------------------------------------------------ */
  #s-count {{ text-align: center; }}
  #count {{ position: relative; width: min(46vmin, 320px); aspect-ratio: 1; display: grid; place-items: center;
            opacity: 0; transition: opacity .3s; }}
  #count.on {{ opacity: 1; }}
  #count svg {{ position: absolute; inset: 0; width: 100%; height: 100%; overflow: visible; }}
  #count circle {{ fill: none; transform: rotate(-90deg); transform-origin: 100px 100px; }}
  .ring-bg {{ stroke: var(--dim); stroke-width: 1.5; stroke-dasharray: 3 7; }}
  .ring-go {{ stroke: var(--p); stroke-width: 3.5; stroke-linecap: round;
              stroke-dasharray: 540.35; stroke-dashoffset: 540.35; filter: drop-shadow(0 0 8px var(--p)); }}
  .ring-go.go {{ animation: ring-run 1s linear forwards; }}
  .ring-in {{ stroke: var(--p); stroke-width: 1; opacity: .35; }}
  .ring-in.go {{ animation: ring-pulse 1s ease-out; }}
  #count-num {{ position: relative; font-size: min(22vmin, 150px); font-weight: 700; line-height: 1;
                color: var(--h); text-shadow: 0 0 30px var(--p), 0 0 60px rgba(63,200,255,.5); }}
  #count-num.beat {{ animation: num-in .95s cubic-bezier(.2,.8,.2,1); }}
  #count-cap {{ position: absolute; bottom: -8%; left: 0; right: 0; font-size: 12px; letter-spacing: .45em;
                text-indent: .45em; opacity: .65; }}
  /* Vorspann vor dem Countdown */
  #preface {{ position: absolute; text-align: center; opacity: 0; }}
  #preface.on {{ opacity: 1; animation: pre-out .5s ease-in 1.9s forwards; }}
  #preface .wort {{ font-size: clamp(24px, 6vw, 68px); font-weight: 700; letter-spacing: .3em;
                    text-indent: .3em; color: var(--h); text-shadow: 0 0 30px var(--p), 0 0 70px rgba(63,200,255,.45);
                    white-space: nowrap; }}
  #preface .wort span {{ display: inline-block; opacity: 0; }}
  #preface.on .wort span {{ animation: pre-letter .55s cubic-bezier(.2,.9,.2,1) forwards;
                            animation-delay: calc(var(--i) * 65ms); }}
  #preface .strich {{ height: 2px; margin: 18px auto 0; width: 0; background: var(--p);
                      box-shadow: 0 0 14px var(--p); }}
  #preface.on .strich {{ animation: pre-line .9s cubic-bezier(.2,.9,.2,1) .55s forwards; }}
  #preface .unter {{ margin-top: 14px; font-size: 11px; letter-spacing: .5em; text-indent: .5em;
                     opacity: 0; }}
  #preface.on .unter {{ animation: pre-sub .6s ease-out 1.1s forwards; }}

  /* ---- Glitch statt Schriftzug ---------------------------------------------- */
  #glitch {{ position: absolute; inset: 0; z-index: 35; pointer-events: none; opacity: 0; overflow: hidden; }}
  #glitch.on {{ opacity: 1; }}
  #glitch i {{ position: absolute; left: -10%; right: -10%; display: block; background: var(--c);
               opacity: .34; mix-blend-mode: screen; transform: translateX(var(--dx));
               animation: g-slice var(--t) steps(2) infinite alternate; }}
  #glitch b {{ position: absolute; left: 0; right: 0; height: 2px; background: var(--h); opacity: .75;
               box-shadow: 0 0 24px var(--h); animation: g-sweep .5s linear infinite; }}
  #glitch::after {{ content: ""; position: absolute; inset: -20%; opacity: .1; mix-blend-mode: screen;
                    background: repeating-linear-gradient(0deg, rgba(255,255,255,.9) 0 1px, transparent 1px 5px);
                    animation: g-noise .08s steps(2) infinite; }}
  body.glitching #stage {{ animation: g-shake .09s steps(2) infinite; }}
  .skip {{ position: fixed; right: 18px; bottom: 14px; font-size: 12px; letter-spacing: .2em; opacity: .5;
           z-index: 60; color: var(--p); border: 1px solid var(--dim); padding: 6px 10px; cursor: pointer;
           background: none; font-family: inherit; }}
  .skip:hover {{ opacity: 1; border-color: var(--p); }}

  /* ---- 3 · Systemcheck ------------------------------------------------------ */
  #s-boot {{ place-items: start; padding: 6vh 6vw; }}
  #boot {{ margin: 0; white-space: pre-wrap; font-size: clamp(12px, 1.6vw, 18px); line-height: 1.7;
           color: var(--p); text-shadow: 0 0 8px rgba(63,200,255,.6); }}
  #boot .ok {{ color: #6CFF9A; }}
  #boot .warn {{ color: var(--a); }}
  #boot .cur {{ display: inline-block; width: .6em; height: 1.1em; background: var(--p);
                vertical-align: -.2em; animation: blink .8s steps(1) infinite; }}
  #boot span.g {{ display: inline-block; will-change: transform, opacity; }}

  /* ---- 4/5 · Menü ----------------------------------------------------------- */
  #s-menu {{ grid-template-rows: auto 1fr auto; padding: 3vh 4vw; }}
  #s-menu header {{ letter-spacing: .4em; text-indent: .4em; font-size: 13px; opacity: .8; text-align: center; }}
  #s-menu header b {{ color: var(--h); font-weight: 700; }}
  /* Breites Band statt mittigem Quadrat: 8 x 2 auf breiten Schirmen, keine Kästchen */
  .grid {{ display: grid; grid-template-columns: repeat(8, minmax(0, 1fr)); gap: clamp(6px, 1.1vw, 20px);
           width: 96vw; align-self: center; }}
  @media (max-width: 1100px) {{ .grid {{ grid-template-columns: repeat(4, 1fr); }} }}
  @media (max-width: 620px) {{ .grid {{ grid-template-columns: repeat(2, 1fr); }} #s-menu.on {{ overflow-y: auto; }} }}
  .tile {{ position: relative; display: block; padding: 0 0 34px; border: 0; background: none;
           color: var(--p); text-decoration: none; opacity: 0; transform: scale(.4); }}
  .tile.in {{ animation: tile-in .7s cubic-bezier(.2,.9,.3,1.2) forwards; animation-delay: calc(var(--i) * 45ms); }}
  /* kein border-radius auf dem SVG: das beschneidet den Schildnamen unter dem Ring */
  .tile svg {{ width: 100%; height: auto; display: block; transition: filter .25s; }}
  .tile:hover svg {{ filter: drop-shadow(0 0 16px color-mix(in srgb, var(--h) 60%, transparent)); }}
  .tile-code {{ position: absolute; left: 50%; top: 2%; transform: translateX(-50%); font-size: 10px;
                letter-spacing: .3em; text-indent: .3em; opacity: .35; }}
  .tile-sub {{ position: absolute; left: 0; right: 0; bottom: 10px; text-align: center;
               font-size: clamp(9px, .85vw, 12px); letter-spacing: .04em; opacity: 0; padding: 0 4px;
               white-space: nowrap; overflow: hidden; text-overflow: ellipsis; transition: opacity .25s; }}
  .tile:hover .tile-sub {{ opacity: .85; color: var(--h); }}
  .tile:hover .tile-code {{ opacity: .9; color: var(--h); }}
  #s-menu footer {{ font-size: 11px; letter-spacing: .25em; opacity: .5; text-align: center; }}

  @keyframes crt-on {{ 0% {{ transform: scaleY(.004) scaleX(.6); opacity: 0; }}
                       18% {{ transform: scaleY(.004) scaleX(1); opacity: 1; }}
                       100% {{ transform: scaleY(1) scaleX(1); opacity: 1; }} }}
  @keyframes crt-flicker {{ 0%, 6%, 12%, 100% {{ opacity: 0; }} 3% {{ opacity: .5; }} 9% {{ opacity: .18; }} }}
  @keyframes ring-run {{ from {{ stroke-dashoffset: 540.35; }} to {{ stroke-dashoffset: 0; }} }}
  @keyframes ring-pulse {{ 0% {{ transform: rotate(-90deg) scale(1); opacity: .45; }}
                           100% {{ transform: rotate(-90deg) scale(1.25); opacity: 0; }} }}
  @keyframes num-in {{ 0% {{ opacity: 0; transform: scale(1.7); filter: blur(6px); }}
                       22% {{ opacity: 1; transform: scale(1); filter: blur(0); }}
                       80% {{ opacity: 1; }} 100% {{ opacity: .15; transform: scale(.94); }} }}
  @keyframes pre-letter {{ 0% {{ opacity: 0; transform: translateY(14px) scale(1.25); filter: blur(7px); }}
                           100% {{ opacity: 1; transform: none; filter: blur(0); }} }}
  @keyframes pre-line {{ to {{ width: min(62vw, 520px); }} }}
  @keyframes pre-sub {{ to {{ opacity: .6; }} }}
  @keyframes pre-out {{ to {{ opacity: 0; transform: scale(1.06); filter: blur(3px); }} }}
  @keyframes g-slice {{ from {{ transform: translateX(var(--dx)); }} to {{ transform: translateX(calc(var(--dx) * -.7)); }} }}
  @keyframes g-sweep {{ from {{ top: -4%; }} to {{ top: 104%; }} }}
  @keyframes g-noise {{ 0% {{ transform: translateY(0); }} 100% {{ transform: translateY(3px); }} }}
  @keyframes g-shake {{ 0% {{ transform: translate(0,0); }} 33% {{ transform: translate(-6px, 2px) skewX(.6deg); }}
                        66% {{ transform: translate(5px,-2px) skewX(-.5deg); }} 100% {{ transform: translate(0,0); }} }}
  @keyframes blink {{ 0%, 49% {{ opacity: 1; }} 50%, 100% {{ opacity: .15; }} }}
  @keyframes tile-in {{ to {{ opacity: 1; transform: scale(1); }} }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation-duration: .001s !important; }} }}
</style>
</head>
<body>
<svg width="0" height="0" style="position:absolute">
  <defs>
    <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="glow-stark" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="4.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
</svg>

<div id="stage">

  <!-- 1/2 · Einschalten und Countdown -->
  <section id="s-count" class="on">
    <div id="preface">
      <div class="wort"></div>
      <div class="strich"></div>
      <div class="unter">STAND BY</div>
    </div>
    <div id="count">
      <svg viewBox="0 0 200 200" aria-hidden="true">
        <circle class="ring-bg" cx="100" cy="100" r="86"/>
        <circle class="ring-in" cx="100" cy="100" r="70"/>
        <circle class="ring-go" cx="100" cy="100" r="86"/>
      </svg>
      <div id="count-num" aria-live="polite">3</div>
      <div id="count-cap">RESET SEQUENCE</div>
    </div>
  </section>
  <div id="glitch" aria-hidden="true"></div>

  <!-- 3 · Systemcheck -->
  <section id="s-boot"><pre id="boot"></pre></section>

  <!-- 4/5 · Menü -->
  <section id="s-menu">
    <header>QUINTESSENZ · <b>KNOWLEDGE TERMINAL</b> · OFFLINE · 16 DOMAINS</header>
    <div class="grid">{''.join(kacheln)}
    </div>
    <footer>SELECT A DOMAIN · NO NETWORK REQUIRED · ALL SOURCES LOCAL</footer>
  </section>
</div>
<button class="skip" id="skip" type="button">SKIP INTRO ▸</button>

<script>
(() => {{
  const $ = s => document.querySelector(s);
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let skipped = false;

  // Warten und Tippen haengen am Bildtakt, nicht an setTimeout: Browser drosseln Timer
  // (Hintergrundfenster, Stromsparen, Vorschaufenster) teils um den Faktor 40, dann
  // kroeche der Vorspann. requestAnimationFrame laeuft mit der Bildwiederholung.
  // Bildtakt als Taktgeber, setTimeout als Notnagel. Browser halten requestAnimationFrame
  // an, sobald das Fenster nicht sichtbar ist; ohne den Notnagel bliebe der Vorspann dann
  // fuer immer am Anfang stehen. setTimeout laeuft auch im Hintergrund, nur gedrosselt.
  const wait = ms => new Promise(res => {{
    if (reduced || ms <= 0) return res();
    let fertig = false;
    const ende = () => {{ if (!fertig) {{ fertig = true; res(); }} }};
    const t0 = performance.now();
    (function f(now) {{ if (fertig) return; (now - t0 >= ms || skipped) ? ende() : requestAnimationFrame(f); }})(t0);
    setTimeout(ende, ms + 40);
  }});

  /** Zeile zeichenweise setzen, Tempo in Zeichen je Sekunde. */
  function tippen(pre, cur, line, cps) {{
    return new Promise(res => {{
      if (reduced || skipped) {{
        for (const ch of line) {{ const s = document.createElement('span'); s.className = 'g';
                                 s.textContent = ch; pre.insertBefore(s, cur); }}
        return res();
      }}
      let i = 0, fertig = false;
      const t0 = performance.now();
      const setze = bis => {{
        while (i < bis) {{
          const s = document.createElement('span'); s.className = 'g'; s.textContent = line[i++];
          pre.insertBefore(s, cur);
        }}
      }};
      const ende = () => {{ if (!fertig) {{ fertig = true; setze(line.length); res(); }} }};
      (function f(now) {{
        if (fertig) return;
        setze(Math.min(line.length, Math.floor((now - t0) / 1000 * cps)));
        (i >= line.length || skipped) ? ende() : requestAnimationFrame(f);
      }})(t0);
      setTimeout(ende, (line.length / cps) * 1000 + 600);   // Notnagel, s. wait()
    }});
  }}

  // ---- Systemcheck tippen -------------------------------------------------------
  const LINES = [
      {boot_js}
  ];
  async function boot() {{
    const pre = $('#boot'); pre.innerHTML = '';
    const cur = document.createElement('span'); cur.className = 'cur'; pre.appendChild(cur);
    for (const line of LINES) {{
      if (skipped) return;
      await tippen(pre, cur, line, 90);
      if (line.endsWith(' OK')) [...pre.querySelectorAll('span.g')].slice(-2).forEach(s => s.classList.add('ok'));
      if (line.endsWith('FOUND')) [...pre.querySelectorAll('span.g')].slice(-8).forEach(s => s.classList.add('warn'));
      pre.insertBefore(document.createTextNode('\\n'), cur);
      await wait(line === '' ? 90 : 150 + Math.random() * 120);
    }}
    await tippen(pre, cur, '████████████████████████', 26);
    await wait(420);
  }}

  // ---- Zeichen werden zu Logos --------------------------------------------------
  async function morph() {{
    const menu = $('#s-menu'), tiles = [...menu.querySelectorAll('.tile')];
    menu.style.opacity = '0'; menu.classList.add('on');       // messbar, aber noch unsichtbar
    const targets = tiles.map(t => {{ const r = t.getBoundingClientRect();
                                     return {{ x: r.left + r.width / 2, y: r.top + r.height / 2 }}; }});
    const glyphs = [...document.querySelectorAll('#boot span.g')];
    $('#boot .cur')?.remove();
    const anims = glyphs.map((g, i) => {{
      const r = g.getBoundingClientRect(), t = targets[i % 16];
      const dx = t.x - (r.left + r.width / 2) + (Math.random() - .5) * 40;
      const dy = t.y - (r.top + r.height / 2) + (Math.random() - .5) * 40;
      return g.animate([
        {{ transform: 'translate(0,0) scale(1)', opacity: 1 }},
        {{ transform: `translate(${{dx * .35}}px, ${{dy * .35 - 60}}px) scale(1.4)`, opacity: 1, offset: .35 }},
        {{ transform: `translate(${{dx}}px, ${{dy}}px) scale(.2)`, opacity: 0 }}
      ], {{ duration: 900 + Math.random() * 500, delay: Math.random() * 350,
           easing: 'cubic-bezier(.3,.7,.2,1)', fill: 'forwards' }}).finished;
    }});
    await wait(650);
    menu.style.opacity = '';
    tiles.forEach(t => t.classList.add('in'));
    $('#s-boot').classList.remove('on');
    await Promise.allSettled(anims);
  }}

  // ---- Bildstoerung: versetzte Streifen, Suchlauf, Rauschen, Ruettler ------------
  async function stoerung(ms) {{
    if (reduced) return;
    const g = $('#glitch');
    g.innerHTML = '';
    for (let i = 0; i < 9; i++) {{
      const b = document.createElement('i');
      b.style.cssText = `top:${{(Math.random() * 100).toFixed(1)}}%;height:${{(.5 + Math.random() * 3).toFixed(1)}}%;`
        + `--dx:${{((Math.random() - .5) * 18).toFixed(1)}}vw;--t:${{(70 + Math.random() * 90).toFixed(0)}}ms;`
        + `--c:${{Math.random() < .4 ? '#FF3DF5' : (Math.random() < .5 ? '#3FC8FF' : '#CFF7FF')}}`;
      g.appendChild(b);
    }}
    g.appendChild(document.createElement('b'));
    g.classList.add('on'); document.body.classList.add('glitching');
    await wait(ms);
    g.classList.remove('on'); document.body.classList.remove('glitching');
    g.innerHTML = '';
  }}

  // ---- Ablauf -------------------------------------------------------------------
  function neu(el) {{ el.classList.remove('go'); void el.offsetWidth; el.classList.add('go'); }}

  async function lauf() {{
    document.body.classList.add('on');                       // Bildroehre schaltet ein
    await wait(620);
    if (skipped) return;
    await stoerung(900);                                     // Bildstoerung zuerst
    if (skipped) return;

    const vor = $('#preface');                               // dann der Vorspann: WORLD RESET
    vor.querySelector('.wort').innerHTML = [...'WORLD RESET']
      .map((c, i) => `<span style="--i:${{i}}">${{c === ' ' ? '&nbsp;' : c}}</span>`).join('');
    vor.classList.add('on');
    await wait(2400);
    vor.classList.remove('on');
    if (skipped) return;

    const box = $('#count'), num = $('#count-num');
    box.classList.add('on');
    for (const n of ['3', '2', '1']) {{
      if (skipped) return;
      num.textContent = n;
      num.classList.remove('beat'); void num.offsetWidth; num.classList.add('beat');
      neu($('.ring-go')); neu($('.ring-in'));
      await wait(reduced ? 0 : 1000);
    }}
    box.classList.remove('on');
    $('#s-count').classList.remove('on');
    await stoerung(340);                                     // kurzer Schnitt zum Systemcheck
    if (skipped) return;
    $('#s-boot').classList.add('on');
    await boot();
    if (skipped) return;
    await morph();
    $('#skip')?.remove();
  }}

  function skipAll() {{
    skipped = true;
    document.body.classList.add('on');
    $('#stage').style.animation = 'none'; $('#stage').style.transform = 'none'; $('#stage').style.opacity = '1';
    ['#s-count', '#s-boot'].forEach(s => $(s).classList.remove('on'));
    const menu = $('#s-menu'); menu.classList.add('on'); menu.style.opacity = '';
    menu.querySelectorAll('.tile').forEach(t => {{ t.style.opacity = 1; t.style.transform = 'none'; }});
    $('#skip')?.remove();
  }}

  $('#skip').addEventListener('click', skipAll);
  addEventListener('keydown', e => {{ if (e.key === 'Escape' || e.key === ' ') skipAll(); }});
  if (reduced) skipAll(); else lauf();
}})();
</script>
</body>
</html>
"""
    (HIER / "intro.html").write_text(html, encoding="utf-8", newline="\n")
    print("intro.html geschrieben:", HIER / "intro.html", f"({len(html) // 1024} KB)")


if __name__ == "__main__":
    main()
