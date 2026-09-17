# -*- coding: utf-8 -*-
"""
Baut den Ladebildschirm des Quintessenz-Terminals als eine eigenständige HTML-Datei:

  1. Versorgungskiste („DOOMSDAY BOX") mittig, Tron-Blau, leises Summen
  2. Detonation: Blitz, Druckwelle, Splitter (Canvas), Pilzwolke
  3. Boot-Text wie ein alter Rechner (Schreibmaschine, Monospace)
  4. Die Zeichen des Boot-Texts fliegen auseinander und werden zu den 16 animierten Logos
  5. Menü: 16 Kacheln, Englisch, jede mit eigener Hover-Farbe

Die 16 SVGs (englische Schilder aus icons/en/) werden direkt in die Seite eingebettet, damit
Hover-Zustand und Farbvariablen ohne Server funktionieren.

    python build_intro.py     ->  intro.html
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
    """SVG so einbetten, dass es in HTML sauber liegt: ohne XML-Kopf, Wurzel ohne feste Größe."""
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
<title>QUINTESSENZ · DOOMSDAY BOX</title>
<style>
  :root {{ --p: #3FC8FF; --h: #CFF7FF; --a: #FF8A00; --bg: #05080b; --dim: #1a5f78; }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; height: 100%; background: var(--bg); color: var(--p); overflow: hidden;
               font: 15px/1.45 "IBM Plex Mono", "Courier Prime", "Consolas", monospace; }}
  body::before {{ /* feine Scanlines */
    content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 50; opacity: .18;
    background: repeating-linear-gradient(0deg, transparent 0 2px, rgba(0,0,0,.6) 2px 3px); }}
  #stage {{ position: relative; width: 100%; height: 100%; }}
  section {{ position: absolute; inset: 0; display: grid; place-items: center; opacity: 0; pointer-events: none;
             transition: opacity .5s; }}
  section.on {{ opacity: 1; pointer-events: auto; }}

  /* ---- 1 Kiste ---- */
  #s-crate {{ grid-template-rows: 1fr auto 1fr; }}
  #crate {{ width: min(48vw, 420px); filter: url(#glow); align-self: end; }}
  #crate .lamp {{ animation: blinken 1.2s steps(1) infinite; }}
  #crate .scan {{ animation: scan 2.8s linear infinite; }}
  .title {{ text-align: center; letter-spacing: .5em; text-indent: .5em; margin-top: 26px; }}
  .title h1 {{ font-size: clamp(22px, 4vw, 44px); font-weight: 700; margin: 0; color: var(--h); text-shadow: 0 0 18px var(--p); }}
  .title p {{ margin: 10px 0 0; opacity: .7; font-size: 13px; letter-spacing: .3em; animation: atmen 2.2s ease-in-out infinite; }}
  .skip {{ position: fixed; right: 18px; bottom: 14px; font-size: 12px; letter-spacing: .2em; opacity: .55; z-index: 60;
           color: var(--p); text-decoration: none; border: 1px solid var(--dim); padding: 6px 10px; cursor: pointer; background: none; }}
  .skip:hover {{ opacity: 1; border-color: var(--p); }}

  /* ---- 2 Detonation ---- */
  #fx {{ position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; z-index: 10; }}
  #flash {{ position: absolute; inset: 0; background: #fff; opacity: 0; pointer-events: none; z-index: 20; }}
  #shock {{ position: absolute; left: 50%; top: 50%; width: 40px; height: 40px; border-radius: 50%; pointer-events: none;
            border: 3px solid var(--h); box-shadow: 0 0 40px var(--p), inset 0 0 30px var(--p); opacity: 0; z-index: 12;
            transform: translate(-50%, -50%) scale(0); }}
  #cloud {{ position: absolute; left: 50%; top: 50%; width: min(60vw, 520px); transform: translate(-50%, -50%); opacity: 0;
            pointer-events: none; z-index: 11; filter: url(#glow); }}
  .boom #flash {{ animation: flash 1.1s ease-out forwards; }}
  .boom #shock {{ animation: shock 1.4s cubic-bezier(.1,.8,.2,1) forwards; }}
  .boom #cloud {{ animation: cloud 2.6s ease-out forwards; }}
  .boom #crate {{ animation: crate-gone .35s ease-in forwards; }}
  .boom .title {{ animation: title-gone .3s ease-in forwards; }}

  /* ---- 3 Boot ---- */
  #s-boot {{ place-items: start; padding: 6vh 6vw; }}
  #boot {{ margin: 0; white-space: pre-wrap; font-size: clamp(12px, 1.6vw, 18px); line-height: 1.7; color: var(--p);
           text-shadow: 0 0 8px rgba(63,200,255,.6); }}
  #boot .ok {{ color: #6CFF9A; }}
  #boot .warn {{ color: var(--a); }}
  #boot .cur {{ display: inline-block; width: .6em; height: 1.1em; background: var(--p); vertical-align: -0.2em; animation: blinken .8s steps(1) infinite; }}
  #boot span.g {{ display: inline-block; will-change: transform, opacity; }}

  /* ---- 4/5 Menü ---- */
  #s-menu {{ grid-template-rows: auto 1fr auto; padding: 3vh 4vw; }}
  #s-menu header {{ letter-spacing: .4em; text-indent: .4em; font-size: 13px; opacity: .8; text-align: center; }}
  #s-menu header b {{ color: var(--h); font-weight: 700; }}
  /* 4 x 4 muss ohne Scrollen in die Höhe passen: Kachel ist ca. 1,12-mal so hoch wie breit */
  .grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px;
           width: min(92vw, calc((100vh - 152px) / 1.12 + 42px)); align-self: center; }}
  @media (max-aspect-ratio: 4/5) {{ .grid {{ grid-template-columns: repeat(2, 1fr); width: 92vw; }} #s-menu.on {{ overflow-y: auto; }} }}
  .tile {{ position: relative; display: block; padding: 6px 6px 26px; border: 1px solid var(--dim); border-radius: 6px;
           color: var(--p); text-decoration: none; opacity: 0; transform: scale(.4);
           background: radial-gradient(circle at 50% 40%, #0a1a22 0, transparent 70%); }}
  .tile.in {{ animation: tile-in .7s cubic-bezier(.2,.9,.3,1.2) forwards; animation-delay: calc(var(--i) * 45ms); }}
  .tile svg {{ width: 100%; height: auto; display: block; }}
  .tile:hover {{ border-color: var(--h); box-shadow: 0 0 22px color-mix(in srgb, var(--h) 45%, transparent); }}
  .tile-code {{ position: absolute; left: 10px; top: 8px; font-size: 11px; letter-spacing: .2em; opacity: .6; }}
  .tile-sub {{ position: absolute; left: 0; right: 0; bottom: 7px; text-align: center; font-size: clamp(9px, .9vw, 12px);
               letter-spacing: .04em; opacity: .55; padding: 0 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .tile:hover .tile-sub, .tile:hover .tile-code {{ opacity: 1; color: var(--h); }}
  #s-menu footer {{ font-size: 11px; letter-spacing: .25em; opacity: .5; text-align: center; }}

  @keyframes blinken {{ 0%, 49% {{ opacity: 1; }} 50%, 100% {{ opacity: .15; }} }}
  @keyframes atmen {{ 0%, 100% {{ opacity: .35; }} 50% {{ opacity: .9; }} }}
  @keyframes scan {{ from {{ transform: translateY(0); }} to {{ transform: translateY(150px); }} }}
  @keyframes flash {{ 0% {{ opacity: 0; }} 6% {{ opacity: 1; }} 100% {{ opacity: 0; }} }}
  @keyframes shock {{ 0% {{ opacity: 1; transform: translate(-50%,-50%) scale(0); }} 100% {{ opacity: 0; transform: translate(-50%,-50%) scale(60); }} }}
  @keyframes cloud {{ 0% {{ opacity: 0; transform: translate(-50%,-30%) scale(.3); }} 25% {{ opacity: 1; }}
                      100% {{ opacity: 0; transform: translate(-50%,-70%) scale(1.15); }} }}
  @keyframes crate-gone {{ to {{ opacity: 0; transform: scale(1.6); filter: blur(6px); }} }}
  @keyframes title-gone {{ to {{ opacity: 0; transform: translateY(20px); }} }}
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

  <!-- 1 · Kiste -->
  <section id="s-crate" class="on">
    <div></div>
    <div style="display:grid;place-items:center">
      <svg id="crate" viewBox="0 0 320 200" aria-label="Supply crate">
        <g fill="none" stroke="var(--p)" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round">
          <!-- Körper -->
          <path d="M28 70 H292 V186 H28 Z"/>
          <path d="M28 70 L60 40 H260 L292 70"/>
          <path d="M60 40 V70 M260 40 V70"/>
          <path d="M28 96 H292" stroke-width="1.4"/>
          <!-- Eckbeschläge -->
          <path d="M28 70 h22 v10 h-12 v14 h-10 M292 70 h-22 v10 h12 v14 h10 M28 186 v-24 h10 v14 h12 v10 M292 186 v-24 h-10 v14 h-12 v10"/>
          <!-- Verschlüsse -->
          <path d="M96 96 v22 h16 v-22 M104 118 v10 M208 96 v22 h16 v-22 M216 118 v10"/>
          <!-- Griffe -->
          <path d="M14 120 q-10 20 0 40 M306 120 q10 20 0 40" stroke-width="3"/>
          <!-- Stern und Stempel -->
          <path d="M160 108 l6 14 h15 l-12 9 5 15 -14 -9 -14 9 5 -15 -12 -9 h15 z" stroke-width="1.8"/>
          <path d="M70 168 h50 M200 168 h50" stroke-width="1.4" opacity=".6"/>
          <text x="160" y="176" fill="var(--p)" stroke="none" font-size="10" text-anchor="middle" letter-spacing="3" font-family="inherit" font-weight="700">SUPPLY CRATE · NO. 16 · KEEP DRY</text>
          <text x="160" y="60" fill="var(--p)" stroke="none" font-size="9" text-anchor="middle" letter-spacing="4" font-family="inherit" opacity=".7">THIS SIDE UP</text>
          <!-- Kontrolllampe -->
          <circle class="lamp" cx="276" cy="84" r="4" fill="var(--a)" stroke="none"/>
          <!-- Scanlinie -->
          <path class="scan" d="M30 42 H290" stroke="var(--h)" stroke-width="1" opacity=".5"/>
        </g>
      </svg>
      <div class="title">
        <h1>DOOMSDAY BOX</h1>
        <p>PRESS ANY KEY · OR WAIT</p>
      </div>
    </div>
    <div></div>
  </section>

  <!-- 2 · Detonation -->
  <canvas id="fx"></canvas>
  <div id="shock"></div>
  <svg id="cloud" viewBox="0 0 400 400" aria-hidden="true">
    <g fill="none" stroke="var(--h)" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round">
      <path d="M170 380 C176 320 168 260 182 210 M230 380 C224 320 232 260 218 210"/>
      <path d="M182 210 C110 214 60 170 84 118 C40 100 70 40 130 52 C150 10 250 10 270 52 C330 40 360 100 316 118 C340 170 290 214 218 210"/>
      <path d="M120 150 C150 175 250 175 280 150" opacity=".6"/>
      <path d="M96 118 C130 140 270 140 304 118" opacity=".4"/>
      <ellipse cx="200" cy="380" rx="150" ry="16" stroke-dasharray="6 8" opacity=".7"/>
      <ellipse cx="200" cy="380" rx="90" ry="9" stroke-dasharray="3 6" opacity=".5"/>
    </g>
  </svg>
  <div id="flash"></div>

  <!-- 3 · Boot -->
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
  const wait = ms => new Promise(r => setTimeout(r, ms));
  let phase = 'crate', skipped = false;

  // ---- Splitter auf Canvas -------------------------------------------------
  const cv = $('#fx'), cx = cv.getContext('2d');
  function fit() {{ const d = devicePixelRatio || 1; cv.width = innerWidth * d; cv.height = innerHeight * d; cx.setTransform(d, 0, 0, d, 0, 0); }}
  addEventListener('resize', fit); fit();
  function shards(n = 320) {{
    const ox = innerWidth / 2, oy = innerHeight / 2, t0 = performance.now(), P = [];
    for (let i = 0; i < n; i++) {{
      const a = Math.random() * Math.PI * 2, v = 220 + Math.random() * 640;
      P.push({{ x: ox, y: oy, vx: Math.cos(a) * v, vy: Math.sin(a) * v - 120, len: 6 + Math.random() * 26,
               rot: a, spin: (Math.random() - .5) * 12, life: 1.3 + Math.random() * 1.2 }});
    }}
    return new Promise(res => {{
      let last = t0;
      (function frame(now) {{
        const dt = Math.min(.05, (now - last) / 1000); last = now;
        const age = (now - t0) / 1000;
        cx.clearRect(0, 0, innerWidth, innerHeight);
        cx.lineCap = 'round'; cx.shadowColor = '#3FC8FF'; cx.shadowBlur = 12;
        let alive = 0;
        for (const p of P) {{
          const k = age / p.life; if (k >= 1) continue; alive++;
          p.vy += 380 * dt; p.vx *= (1 - 1.1 * dt); p.vy *= (1 - .6 * dt);
          p.x += p.vx * dt; p.y += p.vy * dt; p.rot += p.spin * dt;
          cx.globalAlpha = 1 - k; cx.strokeStyle = k < .15 ? '#FFFFFF' : '#3FC8FF'; cx.lineWidth = 2.2 - k;
          cx.beginPath(); cx.moveTo(p.x, p.y); cx.lineTo(p.x + Math.cos(p.rot) * p.len, p.y + Math.sin(p.rot) * p.len); cx.stroke();
        }}
        cx.globalAlpha = 1;
        if (alive && !skipped) requestAnimationFrame(frame); else {{ cx.clearRect(0, 0, innerWidth, innerHeight); res(); }}
      }})(t0);
    }});
  }}

  // ---- Boot-Text ----------------------------------------------------------------
  const LINES = [
      {boot_js}
  ];
  async function boot() {{
    const pre = $('#boot'); pre.innerHTML = '';
    const cur = document.createElement('span'); cur.className = 'cur'; pre.appendChild(cur);
    for (const line of LINES) {{
      if (skipped) return;
      const row = document.createDocumentFragment();
      for (const ch of line) {{
        const s = document.createElement('span'); s.className = 'g'; s.textContent = ch;
        pre.insertBefore(s, cur);
        if (line.length > 40 && !reduced) await wait(9 + Math.random() * 10);
      }}
      if (line.endsWith(' OK')) [...pre.querySelectorAll('span.g')].slice(-2).forEach(s => s.classList.add('ok'));
      if (line.endsWith('FOUND')) [...pre.querySelectorAll('span.g')].slice(-8).forEach(s => s.classList.add('warn'));
      pre.insertBefore(document.createTextNode('\\n'), cur);
      await wait(reduced ? 0 : (line === '' ? 120 : 220 + Math.random() * 160));
    }}
    // Fortschrittsbalken
    for (let i = 0; i < 24 && !skipped; i++) {{
      const s = document.createElement('span'); s.className = 'g'; s.textContent = '█'; pre.insertBefore(s, cur); await wait(reduced ? 0 : 55);
    }}
    await wait(reduced ? 0 : 500);
  }}

  // ---- Zeichen -> Logos -------------------------------------------------------
  async function morph() {{
    const menu = $('#s-menu'), tiles = [...menu.querySelectorAll('.tile')];
    menu.style.opacity = '0'; menu.classList.add('on');          // sichtbar für Messung, aber unsichtbar
    const targets = tiles.map(t => {{ const r = t.getBoundingClientRect(); return {{ x: r.left + r.width / 2, y: r.top + r.height / 2 }}; }});
    const glyphs = [...document.querySelectorAll('#boot span.g')];
    $('#boot .cur')?.remove();
    const anims = glyphs.map((g, i) => {{
      const r = g.getBoundingClientRect(), t = targets[i % 16];
      const dx = t.x - (r.left + r.width / 2) + (Math.random() - .5) * 40, dy = t.y - (r.top + r.height / 2) + (Math.random() - .5) * 40;
      return g.animate([
        {{ transform: 'translate(0,0) scale(1)', opacity: 1 }},
        {{ transform: `translate(${{dx * .35}}px, ${{dy * .35 - 60}}px) scale(1.4)`, opacity: 1, offset: .35 }},
        {{ transform: `translate(${{dx}}px, ${{dy}}px) scale(.2)`, opacity: 0 }}
      ], {{ duration: 900 + Math.random() * 500, delay: Math.random() * 350, easing: 'cubic-bezier(.3,.7,.2,1)', fill: 'forwards' }}).finished;
    }});
    await wait(650);
    menu.style.opacity = '';
    tiles.forEach(t => t.classList.add('in'));
    $('#s-boot').classList.remove('on');
    await Promise.allSettled(anims);
    phase = 'menu';
  }}

  // ---- Ablauf ------------------------------------------------------------------
  async function detonate() {{
    if (phase !== 'crate') return; phase = 'boom';
    document.body.classList.add('boom');
    const s = shards(); await wait(1500);
    $('#s-crate').classList.remove('on');
    $('#s-boot').classList.add('on');
    await boot();
    await morph();
    await s;
    $('#skip').remove();
  }}
  function skipAll() {{
    skipped = true; phase = 'menu';
    document.body.classList.remove('boom');
    ['#s-crate', '#s-boot'].forEach(s => $(s).classList.remove('on'));
    const menu = $('#s-menu'); menu.classList.add('on'); menu.style.opacity = '';
    menu.querySelectorAll('.tile').forEach(t => {{ t.style.opacity = 1; t.style.transform = 'none'; }});
    $('#skip')?.remove();
  }}
  $('#skip').addEventListener('click', skipAll);
  addEventListener('keydown', e => {{ if (e.key === 'Escape') skipAll(); else detonate(); }}, {{ once: false }});
  $('#s-crate').addEventListener('click', detonate);
  if (reduced) skipAll(); else setTimeout(detonate, 3200);
}})();
</script>
</body>
</html>
"""
    (HIER / "intro.html").write_text(html, encoding="utf-8", newline="\n")
    print("intro.html geschrieben:", HIER / "intro.html", f"({len(html) // 1024} KB)")


if __name__ == "__main__":
    main()
