/* ===========================================================================
   QUINTESSENZ TERMINAL - Frontend
   Reines ES-Modul, kein Build-Schritt, keine Abhaengigkeit, kein Netzzugriff
   ausser zum eigenen Server.

   Zwei Welten, eine Zustandsmaschine:
     TERMINAL  #bildschirminhalt  - Navigation, Suche, Aktenwerkzeuge
     PAPIER    #papierblatt       - der gelesene Inhalt

   Adressen (Hash-Router, damit Lesezeichen und Zurueck funktionieren):
     #/                        Eingang
     #/b/<bereich>             Themenliste
     #/b/<bereich>/<thema>     Aktenliste
     #/a/<akte>                Akte
     #/suche/<begriff>         Trefferliste
   =========================================================================== */

import { setze as texSetzen } from './formel.js';

const $  = (s, w = document) => w.querySelector(s);
const $$ = (s, w = document) => [...w.querySelectorAll(s)];

const PIKTO = (name) =>
  `<svg class="pikto" aria-hidden="true"><use href="/static/img/piktogramme.svg#p-${name}"></use></svg>`;

const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

/* Absatz-HTML stammt im Prototyp ausschliesslich aus eigenen Adaptern.
   Sobald ZIM-Inhalte dazukommen, wird serverseitig gereinigt (bleach o.ae.)
   und hier zusaetzlich auf eine Merkliste erlaubter Tags gefiltert. */
const ERLAUBT = /^(em|strong|code|sub|sup|br|a|span)$/i;
function saeubern(html) {
  const topf = document.createElement('div');
  topf.innerHTML = html ?? '';
  for (const el of [...topf.querySelectorAll('*')]) {
    if (!ERLAUBT.test(el.tagName)) { el.replaceWith(...el.childNodes); continue; }
    for (const attr of [...el.attributes]) {
      const ok = (el.tagName === 'A' && ['href', 'data-akte', 'data-anker'].includes(attr.name));
      if (!ok) el.removeAttribute(attr.name);
    }
    if (el.tagName === 'A' && el.getAttribute('href')?.match(/^(?!\/|#)/)) el.removeAttribute('href');
  }
  return topf.innerHTML;
}

const holen = async (pfad) => {
  const a = await fetch(pfad, { headers: { Accept: 'application/json' } });
  if (!a.ok) throw new Error(`${a.status} ${pfad}`);
  return a.json();
};

const groesse = (b) => {
  if (!b) return '0 B';
  const e = ['B', 'kB', 'MB', 'GB', 'TB'];
  const i = Math.min(e.length - 1, Math.floor(Math.log(b) / Math.log(1024)));
  return `${(b / 1024 ** i).toFixed(i ? 1 : 0).replace('.', ',')} ${e[i]}`;
};

/* =============================  Geraete  ================================== *
 * Zehn Themen. Jedes stellt BEIDE Welten um: die Roehre und das Papier.
 * Die Farbwerte stehen in css/themen.css - hier nur Name, Kurzbeschreibung
 * und die zwei Farben fuer das Vorschauplaettchen.
 * Eigennamen, keine Marken: gestaltet ist die Anmutung eines Geraets, nicht
 * ein Logo. Woher die Anregung stammt, steht in docs/DESIGN.md.            */

const GERAETE = [
  // id · Name · was es darstellt · t Phosphor · g Gehaeuse · w Signalfarbe
  // · b Bogen · z Cursorzeichen
  { id: 'phosphor',      name: 'Phosphor',      was: 'Aktenterminal, R\u00f6hre 1958',
    t: '#33FF66', g: '#191612', w: '#FFB000', b: '#E1D5B8', z: '>' },
  { id: 'bernstein',     name: 'Bernstein',     was: 'Leitstand, Bernsteinr\u00f6hre',
    t: '#FFB000', g: '#1C1712', w: '#9DFFC0', b: '#E5DAC6', z: '\u00bb' },
  { id: 'gitternetz',    name: 'Gitternetz',    was: 'Lichtgitter \u00b7 Blaupause',
    t: '#6FE9FF', g: '#05090E', w: '#FF7A18', b: '#0F4C81', z: '\u25b8' },
  { id: 'regenschauer',  name: 'Regenschauer',  was: 'Serverkeller \u00b7 Endlospapier',
    t: '#22E96A', g: '#050806', w: '#E8FFEE', b: '#DCE7DA', z: '\u2595' },
  { id: 'reaktorkern',   name: 'Reaktorkern',   was: 'Helmanzeige, Gold + Blau',
    t: '#FFC24A', g: '#1A1210', w: '#59E6FF', b: '#EBE7E0', z: '\u25c6' },
  { id: 'flugleitung',   name: 'Flugleitung',   was: 'Cockpit 1930er, Messing',
    t: '#CFE3D2', g: '#2E2314', w: '#E8C24A', b: '#E9DEC7', z: '\u25b4' },
  { id: 'logbuch',       name: 'Logbuch',       was: 'Kartentisch, \u00d6llampe',
    t: '#F0C070', g: '#33230F', w: '#E07A4E', b: '#E1CEA5', z: '\u2756' },
  { id: 'seekarte',      name: 'Seekarte',      was: 'Navigationspult, Gold auf Blau',
    t: '#FFD23F', g: '#123246', w: '#FF6F55', b: '#EDDFBD', z: '\u2726' },
  { id: 'springfield',   name: 'Springfield',   was: 'Zeichentrick, harte Kontur',
    t: '#FFD90F', g: '#2A9FD6', w: '#6FD0F0', b: '#F8F3E2', z: '\u25b6' },
  { id: 'klemmbaustein', name: 'Klemmbaustein', was: 'Bauanleitung, Noppen',
    t: '#FFFFFF', g: '#0055BF', w: '#C91A09', b: '#FFFFFF', z: '\u25cf' },
];

/* ===========================  Einstellungen  ============================== */

const EIN = {
  thema: 'phosphor', effekte: null, skala: 1, kontrast: 'normal',
  gebootet: false, lesezeichen: [], verlauf: [],
};

function einstellungenLaden() {
  try { Object.assign(EIN, JSON.parse(localStorage.getItem('quintessenz') || '{}')); }
  catch { /* beschaedigt -> Vorgaben */ }
  /* Effekte: Standard AUS auf Displays unter 8 Zoll (Faustregel: kurze Kante
     < 800 CSS-px oder Touch ohne Maus). Grosse Schirme starten mit Effekt. */
  if (EIN.effekte === null || EIN.effekte === undefined) {
    const kurz = Math.min(screen.width, screen.height);
    EIN.effekte = !(kurz < 800 || matchMedia('(pointer: coarse)').matches);
  }
  anwenden();
}
function einstellungenSichern() {
  EIN.verlauf = EIN.verlauf.slice(0, 40);
  localStorage.setItem('quintessenz', JSON.stringify(EIN));
}
function anwenden() {
  const w = document.documentElement;
  if (!GERAETE.some((g) => g.id === EIN.thema)) EIN.thema = 'phosphor';
  w.dataset.thema = EIN.thema;
  w.dataset.effekte = EIN.effekte ? 'an' : 'aus';
  w.dataset.kontrast = EIN.kontrast;
  w.style.setProperty('--skala', EIN.skala);
  $('#k-effekte').setAttribute('aria-pressed', String(!!EIN.effekte));
  $('#k-kontrast').setAttribute('aria-pressed', EIN.kontrast === 'hoch');
  $('#k-schrift').textContent = EIN.skala === 1 ? 'A+' : `A ${EIN.skala.toFixed(2)}`;
  const g = GERAETE.find((x) => x.id === EIN.thema);
  $('#k-thema').lastChild.textContent = g.name;
  $$('.geraet-wahl').forEach((b) =>
    b.setAttribute('aria-current', String(b.dataset.thema === EIN.thema)));
  /* Adressleistenfarbe des Handys mitziehen. */
  let m = document.querySelector('meta[name="theme-color"]');
  if (!m) { m = document.createElement('meta'); m.name = 'theme-color'; document.head.append(m); }
  m.content = getComputedStyle(w).getPropertyValue('--term-gehaeuse').trim();
}

function geraetewahlZeichnen() {
  $('#themenwahl').innerHTML = GERAETE.map((g) => `
    <button class="geraet-wahl" type="button" role="option" data-thema="${g.id}"
            aria-current="${g.id === EIN.thema}">
      <span class="geraet-probe" aria-hidden="true">
        <i style="background:${g.g};color:${g.t}">${g.z}</i>
        <i style="background:${g.w}"></i>
        <i style="background:${g.b}"></i>
      </span>
      <span class="bez">${esc(g.name)}<small>${esc(g.was)}</small></span>
    </button>`).join('');
}

function geraetSetzen(id) {
  EIN.thema = id;
  anwenden();
  einstellungenSichern();
  /* Die Instrumente werden als SVG gezeichnet, nicht per CSS - nach einem
     Geraetewechsel muss die Ansicht deshalb neu aufgebaut werden. */
  route();
}

function geraeteklappe(auf) {
  const k = $('#themenwahl');
  const offen = auf ?? !k.hasAttribute('open');
  k.toggleAttribute('open', offen);
  $('#k-thema').setAttribute('aria-expanded', String(offen));
  if (offen) $('.geraet-wahl[aria-current="true"]')?.focus();
}

/* ============================  Bootsequenz  =============================== */

const BOOTZEILEN = [
  ['QUINTESSENZ TERMINAL  MOD. 5  – STARTVORGANG', 0],
  ['KERNSPEICHER .................. 16384 MB   ', 140, 'OK'],
  ['ARCHIVTRÄGER .................. NVMe 1 TB  ', 260, 'OK'],
  ['AKTENVERZEICHNIS .............. WIRD GELESEN', 400, 'OK'],
  ['RECHENWERK .................... BEREIT     ', 560, 'OK'],
  ['NETZ .......................... LOKAL      ', 700, 'OK'],
  ['', 820],
  ['ARCHIV FREIGEGEBEN. GUTEN TAG.', 900],
];

function booten() {
  const kasten = $('#boot');
  const ziel = $('#bootzeilen');
  if (EIN.gebootet) return Promise.resolve();
  kasten.hidden = false;
  let fertig;
  const versprechen = new Promise((r) => { fertig = r; });
  const uhren = [];
  const ende = () => {
    uhren.forEach(clearTimeout);
    kasten.hidden = true;
    removeEventListener('keydown', ende);
    removeEventListener('pointerdown', ende);
    EIN.gebootet = true; einstellungenSichern();
    fertig();
  };
  BOOTZEILEN.forEach(([text, ms, ok]) => {
    uhren.push(setTimeout(() => {
      const d = document.createElement('div');
      d.className = 'zeile';
      d.innerHTML = esc(text) + (ok ? ` <span class="ok">[${esc(ok)}]</span>` : '&nbsp;');
      ziel.append(d);
    }, ms));
  });
  uhren.push(setTimeout(ende, 1500));
  addEventListener('keydown', ende, { once: true });
  addEventListener('pointerdown', ende, { once: true });
  return versprechen;
}

/* ==========================  Zeigerinstrument  ============================ */

/* Vier Instrumentenbauarten. Welche gilt, sagt das Geraet ueber --gauge-art:

     nadel   Zeigerinstrument mit Teilstrichen   (Phosphor, Bernstein,
                                                  Flugleitung, Logbuch, Seekarte)
     ring    geschlossener Ring                  (Reaktorkern)
     balken  grobe Segmente                      (Gitternetz, Springfield,
                                                  Klemmbaustein)
     saeule  Saeulen wie ein Aussteuerungsmesser (Regenschauer)

   Alle zeichnen in dieselbe Flaeche 68x44, damit der Kopf des Eingangs in
   jedem Geraet gleich hoch bleibt. */
function bauart() {
  return (getComputedStyle(document.documentElement)
    .getPropertyValue('--gauge-art') || 'nadel').trim();
}

function gaugeSvg(a, art) {
  const auf = (n) => n.toFixed(1);
  if (art === 'ring') {
    const u = 2 * Math.PI * 16;
    return `<circle cx="34" cy="24" r="16" stroke-width="3" opacity=".22"/>
      <circle cx="34" cy="24" r="16" stroke-width="3" stroke-linecap="butt"
              stroke-dasharray="${auf(a * u)} ${auf(u)}"
              transform="rotate(-90 34 24)"/>
      <circle cx="34" cy="24" r="2" fill="currentColor" stroke="none" opacity=".7"/>`;
  }
  if (art === 'balken') {
    const n = 8, voll = Math.round(a * n);
    return Array.from({ length: n }, (_, i) =>
      `<rect x="${6 + i * 7.3}" y="14" width="5.4" height="17" rx="1"
             fill="currentColor" stroke="none"
             opacity="${i < voll ? 1 : 0.18}"/>`).join('');
  }
  if (art === 'saeule') {
    const n = 11;
    return Array.from({ length: n }, (_, i) => {
      const t = (i + 1) / n;
      const h = Math.max(3, Math.min(1, a / t) * 24 * (0.45 + 0.55 * t));
      return `<rect x="${5 + i * 5.4}" y="${34 - h}" width="3.4" height="${auf(h)}"
              fill="currentColor" stroke="none"
              opacity="${t <= a + 0.06 ? 1 : 0.18}"/>`;
    }).join('');
  }
  // nadel
  const winkel = -120 + a * 240;
  const rad = (winkel - 90) * Math.PI / 180;
  const x = 34 + 24 * Math.cos(rad), y = 34 + 24 * Math.sin(rad);
  const striche = Array.from({ length: 7 }, (_, i) => {
    const w = (-120 + (i / 6) * 240 - 90) * Math.PI / 180;
    const c = Math.cos(w), sn = Math.sin(w);
    return `<line x1="${auf(34 + 26 * c)}" y1="${auf(36 + 26 * sn)}"
                  x2="${auf(34 + 30 * c)}" y2="${auf(36 + 30 * sn)}"
                  stroke-width="1.2" opacity=".45"/>`;
  }).join('');
  return `${striche}
    <path d="M8 36a26 26 0 0 1 52 0" stroke-width="1.4" opacity=".28"/>
    <path d="M8 36a26 26 0 0 1 52 0" stroke-width="2.4"
          stroke-dasharray="${auf(a * 81.7)} 200"/>
    <line x1="34" y1="36" x2="${auf(x)}" y2="${auf(y)}" stroke-width="1.6"/>
    <circle cx="34" cy="36" r="2.2" fill="currentColor" stroke="none"/>`;
}

function gauge(marke, wert, anteil) {
  const a = Math.max(0, Math.min(1, anteil));
  return `<div class="gauge">
    <svg width="68" height="44" viewBox="0 0 68 44" aria-hidden="true" fill="none"
         stroke="currentColor" stroke-linecap="round">${gaugeSvg(a, bauart())}</svg>
    <span class="wert">${esc(wert)}</span>
    <span class="marke">${esc(marke)}</span>
  </div>`;
}

/* =============================  Zustand  ================================== */

const Z = { ansicht: 'eingang', bereich: null, thema: null, akte: null, frage: '', eintraege: [], zeiger: 0 };

function pfadZeichnen(teile) {
  $('#pfad').innerHTML = teile.map((t, i) => {
    const letzte = i === teile.length - 1;
    /* still: eine Stufe, die nur beschriftet - die Gruppe hat keine eigene
       Seite, also darf sie auch nicht wie ein Knopf aussehen. */
    const inhalt = (letzte || t.still || !t.ziel)
      ? `<span class="${letzte ? 'jetzt' : 'still'}">${esc(t.text)}</span>`
      : `<button data-ziel="${esc(t.ziel)}">${esc(t.text)}</button>`;
    return (i ? '<span class="teiler">›</span>' : '') + inhalt;
  }).join('');
}

/* =========================  Terminal-Ansichten  =========================== */

async function zeigeEingang() {
  const d = await holen('/api/eingang');
  Z.ansicht = 'eingang'; Z.bereich = Z.thema = Z.akte = null;
  document.body.dataset.ansicht = 'eingang';
  pfadZeichnen([{ text: 'Eingang' }]);

  const k = d.kennzahlen;
  const belegt = d.bereiche.filter((b) => b.akten > 0).length;

  /* Die Gruppen sind Zwischenueberschriften, keine Navigationsebene:
     jeder Bereich bleibt einen Klick entfernt und behaelt seine Adresse.
     Sie ordnen nur den Eingang - und die Trefferliste der Suche, damit
     beides an derselben Stelle steht. */
  const gruppeHtml = (g) => `
    <div class="gruppenkopf">
      <span class="schild">${esc(g.schild)}</span>
      <span class="zahl">${g.akten ? `${g.akten} Akten · ` : ''}${g.themen} Themen</span>
    </div>
    <ul class="liste" role="group" aria-label="${esc(g.schild)}">
      ${g.bereiche.map((b) => `
        <li class="eintrag${b.akten ? '' : ' leer'}" role="option" aria-selected="false"
            data-ziel="#/b/${b.id}" data-leer="${b.akten ? 0 : 1}">
          <span class="zeiger" aria-hidden="true"></span>
          ${PIKTO(b.piktogramm)}
          <span class="name"><span class="schild">${esc(b.schild)}</span>
            <br>${esc(b.titel)}</span>
          <span class="zahl">${b.akten ? `${b.akten} Akten` : '—'}<br>
            ${b.themen} Themen</span>
        </li>`).join('')}
    </ul>`;

  const html = `
    <div class="instrumente">
      ${gauge('Akten', k.akten_gesamt, k.akten_gesamt / 500)}
      ${gauge('Bereiche belegt', `${belegt}/${k.bereiche_gesamt}`, belegt / k.bereiche_gesamt)}
      ${gauge('Archiv', groesse(k.archiv_bytes), Math.log10(1 + k.archiv_bytes) / 12)}
    </div>
    ${k.akten_demo ? `<p class="hinweis">
       <b>Prototyp.</b> ${k.akten_gesamt - k.akten_demo} Akten stammen aus echtem eigenem
       Material, ${k.akten_demo} sind Demo-Akten und auf dem Papier als solche gestempelt.
       Datenpfad: ${esc(d.datenpfad)}</p>` : ''}
    <div class="abschnitt">Archivbestand – ${k.bereiche_gesamt} Bereiche
      in ${d.gruppen.length} Gruppen</div>
    <div role="listbox" aria-label="Bereiche">
      ${d.gruppen.map(gruppeHtml).join('')}
    </div>`;
  setzeInhalt(html);
}

async function zeigeBereich(id) {
  const d = await holen(`/api/bereich/${encodeURIComponent(id)}`);
  Z.ansicht = 'bereich'; Z.bereich = id; Z.thema = Z.akte = null;
  document.body.dataset.ansicht = 'bereich';
  pfadZeichnen([
    { text: 'Eingang', ziel: '#/' },
    ...(d.gruppe ? [{ text: d.gruppe.schild, still: true }] : []),
    { text: d.schild },
  ]);

  const html = `
    <div class="abschnitt">${PIKTO(d.piktogramm)} ${esc(d.titel)}</div>
    <p class="hinweis">${d.themen.length} Themen, ${d.akten_gesamt} Akten im Bestand.</p>
    <ul class="liste" role="listbox" aria-label="Themen">
      ${d.themen.map((t) => `
        <li class="eintrag${t.akten ? '' : ' leer'}" role="option" aria-selected="false"
            data-ziel="#/b/${d.id}/${t.id}" data-leer="${t.akten ? 0 : 1}">
          <span class="zeiger" aria-hidden="true"></span>
          <span></span>
          <span class="name">${esc(t.titel)}
            <br><span class="tiefe">${t.tiefe.join(' · ')}</span>
            ${t.sprache ? `<span class="tiefe">${esc(t.sprache)}</span>` : ''}</span>
          <span class="zahl">${t.akten ? `${t.akten} Akten` : 'wartet auf<br>Beschaffung'}</span>
        </li>`).join('')}
    </ul>
    ${d.ausschluss?.length ? `<div class="abschnitt">Bewusst nicht enthalten</div>
      <p class="hinweis">${d.ausschluss.map(esc).join(' · ')}</p>` : ''}`;
  setzeInhalt(html);
}

const QUELLZEICHEN = { zim: 'ENZYKLOPÄDIE', se: 'FACHFORUM', pdf: 'HANDBUCH', eigen: 'EIGEN', demo: 'DEMO' };

async function zeigeThema(bereichId, themaId) {
  const d = await holen(`/api/thema/${encodeURIComponent(bereichId)}/${encodeURIComponent(themaId)}`);
  Z.ansicht = 'thema'; Z.bereich = bereichId; Z.thema = themaId; Z.akte = null;
  document.body.dataset.ansicht = 'thema';
  pfadZeichnen([
    { text: 'Eingang', ziel: '#/' },
    { text: d.bereich.schild, ziel: `#/b/${d.bereich.id}` },
    { text: d.thema.titel.slice(0, 34) },
  ]);

  const html = `
    <div class="abschnitt">${PIKTO(d.bereich.piktogramm)} ${esc(d.thema.titel)}</div>
    ${d.thema.quellen_text ? `<p class="hinweis">Quellen laut Übersicht:
       ${esc(d.thema.quellen_text)}</p>` : ''}
    ${d.akten.length ? `
      <ul class="liste" role="listbox" aria-label="Akten">
        ${d.akten.map((a) => `
          <li class="eintrag" role="option" aria-selected="false" data-ziel="#/a/${a.id}">
            <span class="zeiger" aria-hidden="true"></span>
            <span></span>
            <span class="name klammer">${esc(a.titel)}
              <br><span class="tiefe">${esc(a.tiefe)}</span>
              <span class="tiefe">${esc(QUELLZEICHEN[a.quelle.typ] || a.quelle.typ)}</span>
              ${a.demo ? '<span class="tiefe">DEMO</span>' : ''}</span>
            <span class="zahl">${esc(a.sprache)}</span>
          </li>`).join('')}
      </ul>`
    : `<p class="hinweis">Noch keine Akten. Die Quellen dieses Themas sind
         beschafft, aber noch nicht ingestiert – oder die Beschaffung läuft noch.</p>`}`;
  setzeInhalt(html);
}

async function zeigeAkte(id) {
  const a = await holen(`/api/akte/${encodeURIComponent(id)}`);
  Z.ansicht = 'akte'; Z.akte = a; Z.bereich = a.bereich_id; Z.thema = a.thema_id;
  document.body.dataset.ansicht = 'akte';
  pfadZeichnen([
    { text: 'Eingang', ziel: '#/' },
    { text: a.pfad.bereich.schild, ziel: `#/b/${a.bereich_id}` },
    { text: a.pfad.thema.titel.slice(0, 22), ziel: `#/b/${a.bereich_id}/${a.thema_id}` },
    { text: a.titel.slice(0, 26) },
  ]);

  const gemerkt = EIN.lesezeichen.includes(a.id);
  const html = `
    <div class="abschnitt">Akte geöffnet</div>
    <div class="werkzeuge">
      <button class="werkzeug" data-tat="original">${PIKTO('lupe')} Original einsehen
        <span class="taste">O</span></button>
      <button class="werkzeug" data-tat="vorlesen">${PIKTO('lautsprecher')} Vorlesen
        <span class="taste">V</span></button>
      <button class="werkzeug" data-tat="nachfragen">${PIKTO('frage')} Nachfragen
        <span class="taste">N</span></button>
      <button class="werkzeug" data-tat="merken" aria-pressed="${gemerkt}">
        ${PIKTO('lesezeichen')} ${gemerkt ? 'Gemerkt' : 'Merken'}<span class="taste">M</span></button>
      <button class="werkzeug" data-tat="drucken">${PIKTO('drucker')} Drucken
        <span class="taste">D</span></button>
      <button class="werkzeug" id="zurueck-terminal" data-tat="zurueck">
        &#8592; Zur&uuml;ck zum Terminal</button>
    </div>
    ${a.toc.length ? `<div class="abschnitt">Inhalt</div>
      <ul class="toc">${a.toc.map((t) => `
        <li class="e${t.ebene}"><a href="#${esc(t.anker)}" data-anker="${esc(t.anker)}">${esc(t.text)}</a></li>`).join('')}
      </ul>` : ''}
    ${a.verwandt.length ? `<div class="abschnitt">Verwandte Akten</div>
      <ul class="liste">${a.verwandt.map((v) => `
        <li class="eintrag" data-ziel="#/a/${v.id}">
          <span class="zeiger" aria-hidden="true"></span><span></span>
          <span class="name">${esc(v.titel)}</span><span class="zahl"></span>
        </li>`).join('')}</ul>` : ''}
    <div id="chat"></div>`;
  setzeInhalt(html);
  drucke(a);

  EIN.verlauf = [{ id: a.id, titel: a.titel, zeit: Date.now() },
    ...EIN.verlauf.filter((v) => v.id !== a.id)];
  einstellungenSichern();
}

async function zeigeSuche(frage) {
  const d = await holen(`/api/suche?q=${encodeURIComponent(frage)}`);
  Z.ansicht = 'suche'; Z.frage = frage; Z.akte = null;
  document.body.dataset.ansicht = 'suche';
  pfadZeichnen([{ text: 'Eingang', ziel: '#/' }, { text: `Suche: ${frage}` }]);
  $('#suche').value = frage;

  const html = `
    <div class="instrumente">
      ${gauge('Treffer', d.treffer, d.treffer / 40)}
      ${gauge('Bereiche', d.gruppen.length, d.gruppen.length / 16)}
      ${gauge('Dauer', `${d.dauer_ms} ms`, Math.min(1, d.dauer_ms / 2000))}
    </div>
    ${d.treffer === 0
      ? `<p class="hinweis">Kein Treffer für „${esc(frage)}“.
           Der Bestand umfasst im Prototyp nur eigenes Material und Demo-Akten.</p>`
      : d.gruppen.map((g) => `
          <div class="abschnitt">${PIKTO(g.piktogramm)}
            <span class="schild">${esc(g.schild)}</span> ${g.treffer.length}</div>
          <ul class="liste" role="listbox">
            ${g.treffer.map((t) => `
              <li class="eintrag" role="option" aria-selected="false" data-ziel="#/a/${t.id}">
                <span class="zeiger" aria-hidden="true"></span><span></span>
                <span class="name klammer">${esc(t.titel)}
                  <br><span class="hinweis">${esc(t.schnipsel)}</span></span>
                <span class="zahl"><span class="tiefe">${esc(t.tiefe)}</span></span>
              </li>`).join('')}
          </ul>`).join('')}`;
  setzeInhalt(html);
}

/* ====================  Auswahlcursor im Terminal  ========================= */

function setzeInhalt(html) {
  const ziel = $('#bildschirminhalt');
  ziel.innerHTML = html;
  ziel.scrollTop = 0;
  Z.eintraege = $$('.eintrag[data-ziel]:not(.leer)', ziel);
  Z.zeiger = 0;
  markiere();
}
function markiere() {
  Z.eintraege.forEach((e, i) => e.setAttribute('aria-selected', String(i === Z.zeiger)));
  Z.eintraege[Z.zeiger]?.scrollIntoView({ block: 'nearest' });
}
function bewege(schritt) {
  if (!Z.eintraege.length) return;
  Z.zeiger = (Z.zeiger + schritt + Z.eintraege.length) % Z.eintraege.length;
  markiere();
}

/* =============================  PAPIER  =================================== */

const WARNMARKE = { gefahr: 'Gefahr', achtung: 'Achtung', hinweis: 'Hinweis' };

const ART_MARKE = {
  abbildung: 'Abbildung', diagramm: 'Diagramm', foto: 'Lichtbild',
  zeichnung: 'Zeichnung', seite: 'Seitenkopie',
};

/* Solange das Archiv beschafft wird, gibt es zu vielen Akten noch kein
   Quellbild. Statt etwas zu erfinden steht ein Rahmen da, der sagt, welche
   Abbildung dort hingehoert.

   Der Rahmen wird INLINE gezeichnet, nicht als <img> vom Server geholt:
   nur so erbt er ueber currentColor die Tinte des gerade gewaehlten Geraets.
   Ein <img> haette in jedem der zehn Geraete dieselbe Farbe - und in neun
   davon die falsche. Die Route /api/platzhalter.svg bleibt fuer Aufrufer
   ausserhalb des Browsers bestehen. */
function platzhalterHtml(url, alt) {
  const q = new URLSearchParams(url.split('?')[1] || '');
  const w = Math.max(80, Math.min(+q.get('w') || 640, 1600));
  const h = Math.max(60, Math.min(+q.get('h') || 400, 1600));
  const marke = ART_MARKE[q.get('art')] || 'Abbildung';
  const text = q.get('text') || '';

  const grenze = Math.max(20, Math.round(w / 8.6));
  const zeilen = [];
  let zeile = '';
  for (const wort of text.split(/\s+/).filter(Boolean)) {
    if ((zeile + ' ' + wort).trim().length > grenze) { zeilen.push(zeile); zeile = wort; }
    else zeile = (zeile + ' ' + wort).trim();
  }
  if (zeile) zeilen.push(zeile);
  const sichtbar = zeilen.slice(0, 4);
  const y0 = h / 2 - (sichtbar.length - 1) * 11 + 5;

  return `<svg class="platzhalter" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}"
       role="img" aria-label="${esc(alt || marke + ' folgt')}" preserveAspectRatio="xMidYMid meet">
    <rect x="5" y="5" width="${w - 10}" height="${h - 10}" fill="none"
          stroke="currentColor" stroke-width="2" stroke-dasharray="9 6" opacity=".5"/>
    <text x="${w / 2}" y="${y0 - 34}" text-anchor="middle" class="ph-marke"
          opacity=".8">${esc(marke.toUpperCase())} FOLGT</text>
    ${sichtbar.map((z, i) => `<text x="${w / 2}" y="${y0 + i * 22}" text-anchor="middle"
          class="ph-text" opacity=".72">${esc(z)}</text>`).join('')}
    <text x="${w / 2}" y="${h - 15}" text-anchor="middle" class="ph-fuss"
          opacity=".6">PLATZHALTER \u2013 KEIN QUELLBILD VORHANDEN</text>
  </svg>`;
}

function bildHtml(b) {
  const url = String(b.quelle || '');
  if (url.startsWith('/api/platzhalter.svg')) return platzhalterHtml(url, b.alt);
  return `<img src="${esc(url)}" alt="${esc(b.alt || '')}" loading="lazy">`;
}

function blockHtml(b) {
  switch (b.typ) {
    case 'ueberschrift': {
      const e = Math.min(4, Math.max(2, b.ebene || 2));
      return `<h${e} id="${esc(b.anker || '')}">${esc(b.text)}</h${e}>`;
    }
    case 'absatz':
      return `<p>${saeubern(b.html)}</p>`;
    case 'liste': {
      const t = b.geordnet ? 'ol' : 'ul';
      return `<${t}>${b.punkte.map((x) => `<li>${saeubern(x)}</li>`).join('')}</${t}>`;
    }
    case 'tabelle': {
      const a = b.ausrichtung || [];
      return `<div class="formular">
        ${b.titel ? `<div class="titel">${esc(b.titel)}</div>` : ''}
        <div class="rollbar"><table>
          <thead><tr>${b.kopf.map((k, i) =>
            `<th class="${a[i] === 'r' ? 'r' : a[i] === 'c' ? 'c' : ''}">${esc(k)}</th>`).join('')}</tr></thead>
          <tbody>${b.zeilen.map((z) => `<tr>${z.map((c, i) =>
            `<td class="${a[i] === 'r' ? 'r' : a[i] === 'c' ? 'c' : ''}">${saeubern(c)}</td>`).join('')}</tr>`).join('')}
          </tbody></table></div>
        ${b.fussnote ? `<div class="fussnote">${esc(b.fussnote)}</div>` : ''}
      </div>`;
    }
    case 'bild':
    case 'seitenbild':
      return `<figure class="${b.typ === 'seitenbild' ? 'seitenkopie breit' : esc(b.breite || 'normal')}">
        <div class="rahmen">${bildHtml(b)}</div>
        <figcaption>${esc(b.bildunterschrift || '')}
          ${b.herkunft ? `<span class="herkunft">Quelle: ${esc(b.herkunft)}</span>` : ''}
        </figcaption></figure>`;
    case 'code':
      return `<div class="lochstreifen">
        <div class="kopf"><span>${esc(b.titel || 'Quelltext')}</span>
          <span>${esc((b.sprache || '').toUpperCase())}</span></div>
        <pre><code>${esc(b.text)}</code></pre></div>`;
    case 'formel':
      return `<div class="formel"><span class="tex">${texSetzen(b.tex)}</span>
        ${b.text ? `<span class="klartext">${esc(b.text)}</span>` : ''}</div>`;
    case 'warnung':
      return `<aside class="warnung ${esc(b.stufe || 'achtung')}" role="note">
        <div class="band"><span>${esc(WARNMARKE[b.stufe] || 'Achtung')}</span>${esc(b.titel)}</div>
        <div class="text">${saeubern(b.text)}</div></aside>`;
    case 'infokasten':
      return `<div class="infokasten">
        ${b.titel ? `<div class="titel">${esc(b.titel)}</div>` : ''}
        <dl>${b.zeilen.map(([k, v]) =>
          `<dt>${esc(k)}</dt><dd>${saeubern(String(v))}</dd>`).join('')}</dl></div>`;
    case 'zitat':
      return `<blockquote>${esc(b.text)}
        ${b.autor ? `<cite>${esc(b.autor)}</cite>` : ''}</blockquote>`;
    case 'trenner':
      return '<hr class="trenner">';
    case 'fall_frage':
    case 'fall_antwort': {
      const frage = b.typ === 'fall_frage';
      const rolle = frage ? 'Frage' : (b.akzeptiert ? 'Gelöst' : 'Antwort');
      const klassen = [
        'fall', frage ? 'frage' : 'antwort',
        b.akzeptiert ? 'akzeptiert' : '',
        (!frage && !b.akzeptiert) ? 'weitere' : '',
      ].filter(Boolean).join(' ');
      return `<section class="${klassen}">
        <div class="kopf"><span class="rolle">${esc(rolle)}</span>
          <span>${esc(b.autor || '')}</span><span>${esc(b.datum || '')}</span>
          <span class="stimmen">${b.stimmen ?? 0} Stimmen</span></div>
        ${b.blocks.map(blockHtml).join('')}</section>`;
    }
    default:
      return '';
  }
}

function drucke(a) {
  const q = a.quelle;
  const weitere = a.inhalt.filter((b) => b.typ === 'fall_antwort' && !b.akzeptiert).length;
  const stempel = [
    `<span class="stempel tiefe-${esc(a.tiefe)}">${esc(a.tiefe)}</span>`,
    `<span class="stempel sprache">${esc(a.sprache)}</span>`,
    ...a.stempel.map((s) => {
      const k = s === 'DEMO' ? 'demo' : s === 'NUR LOKAL' ? 'nurlokal'
        : s === 'PRÜFEN' ? 'pruefen' : '';
      return `<span class="stempel ${k}">${esc(s)}</span>`;
    }),
  ].join('');

  const zeile = (k, v) => (v ? `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>` : '');

  $('#papierblatt').innerHTML = `<article class="blatt" data-weitere="zu">
    <header class="aktenkopf">
      <div class="laufweg">${esc(a.pfad.bereich.titel)} › ${esc(a.pfad.thema.titel)}</div>
      <h1>${esc(a.titel)}</h1>
      ${a.untertitel ? `<div class="untertitel">${esc(a.untertitel)}</div>` : ''}
      <div class="stempelreihe">${stempel}</div>
      <div class="aktenzeichen"><dl>
        ${zeile('Quelle', q.name)}
        ${zeile('Datei', q.datei)}
        ${zeile('Kennung', q.kennung)}
        ${zeile('Seite', q.seite)}
        ${zeile('Verfasser', q.autor)}
        ${zeile('Lizenz', q.lizenz)}
        ${zeile('Stand', q.stand)}
      </dl></div>
    </header>

    ${a.demo ? `<p class="demo-vermerk"><strong>Demo-Akte.</strong> Dieser Text dient der
      Gestaltungsprüfung, solange das Archiv noch beschafft wird. Er ist inhaltlich
      plausibel, aber nicht aus der genannten Quelle ausgelesen. Sobald der Ingest
      läuft, wird diese Akte durch den echten Quelltext ersetzt.</p>` : ''}

    ${a.inhalt.map(blockHtml).join('')}

    ${weitere ? `<button class="fall-aufklappen" type="button">
      ${weitere} weitere Antwort${weitere > 1 ? 'en' : ''} anzeigen</button>` : ''}

    <footer class="blattfuss">
      <span>Akte ${esc(a.id)}</span>
      <span>${esc(q.lizenz || '')}</span>
      <span>Gedruckt am ${new Date().toLocaleDateString('de-DE')}</span>
    </footer>
  </article>`;
  $('#papierblatt').scrollTop = 0;
}

/* =========================  Aktenwerkzeuge  =============================== */

function werkzeug(tat) {
  const a = Z.akte;
  if (!a) return;
  switch (tat) {
    case 'original': {
      $('#overlay-titel').textContent = `ORIGINAL · ${a.quelle.name}`;
      $('#overlay-rahmen').src = a.quelle.original_url || `/api/akte/${a.id}/original`;
      $('#overlay').setAttribute('open', '');
      $('#overlay-zu').focus();
      break;
    }
    case 'merken': {
      const i = EIN.lesezeichen.indexOf(a.id);
      if (i < 0) EIN.lesezeichen.push(a.id); else EIN.lesezeichen.splice(i, 1);
      einstellungenSichern();
      const b = $('.werkzeug[data-tat="merken"]');
      const jetzt = EIN.lesezeichen.includes(a.id);
      b.setAttribute('aria-pressed', String(jetzt));
      b.lastChild.textContent = jetzt ? 'Gemerkt' : 'Merken';
      break;
    }
    case 'drucken': print(); break;
    case 'zurueck': location.hash = `#/b/${a.bereich_id}/${a.thema_id}`; break;
    case 'vorlesen': nochNicht('Vorlesen', 'Piper läuft auf der Box, nicht auf dem PC.'); break;
    case 'nachfragen': nochNicht('Nachfragen',
      'Der RAG-Chat kommt, sobald llama-server erreichbar ist und der Index steht.'); break;
  }
}

function nochNicht(name, warum) {
  $('#chat').innerHTML = `<div class="maschine">
    <div class="kopf">Maschine · noch nicht verfügbar</div>
    <b>${esc(name)}</b> ist im Prototyp noch nicht angeschlossen. ${esc(warum)}</div>`;
  $('#chat').scrollIntoView({ block: 'nearest', behavior: 'smooth' });
}

/* ==============================  Router  ================================== */

async function route() {
  const teile = decodeURIComponent(location.hash.replace(/^#\/?/, '')).split('/').filter(Boolean);
  try {
    if (!teile.length) return await zeigeEingang();
    if (teile[0] === 'b' && teile.length === 2) return await zeigeBereich(teile[1]);
    if (teile[0] === 'b' && teile.length >= 3) return await zeigeThema(teile[1], teile[2]);
    if (teile[0] === 'a') return await zeigeAkte(teile.slice(1).join('/'));
    if (teile[0] === 'suche') return await zeigeSuche(teile.slice(1).join('/'));
    await zeigeEingang();
  } catch (e) {
    setzeInhalt(`<p class="hinweis">Störung: ${esc(e.message)}.
      <button class="werkzeug" onclick="location.hash='#/'">Zum Eingang</button></p>`);
  }
}

function zurueck() {
  if ($('#overlay').hasAttribute('open')) { overlayZu(); return; }
  if ($('#themenwahl').hasAttribute('open')) { geraeteklappe(false); return; }
  if (Z.ansicht === 'akte' && Z.bereich) location.hash = `#/b/${Z.bereich}/${Z.thema}`;
  else if (Z.ansicht === 'thema') location.hash = `#/b/${Z.bereich}`;
  else if (Z.ansicht === 'bereich' || Z.ansicht === 'suche') location.hash = '#/';
}

const overlayZu = () => {
  $('#overlay').removeAttribute('open');
  $('#overlay-rahmen').src = 'about:blank';
};

/* ===========================  Ereignisse  ================================= */

function verdrahten() {
  $('#suchfeld').addEventListener('submit', (e) => {
    e.preventDefault();
    const q = $('#suche').value.trim();
    if (q) location.hash = `#/suche/${encodeURIComponent(q)}`;
  });
  $('#suche').addEventListener('input', () => {
    $('#suchcursor').style.visibility = $('#suche').value ? 'hidden' : '';
  });

  document.addEventListener('click', (e) => {
    const pfadKnopf = e.target.closest('#pfad button[data-ziel]');
    if (pfadKnopf) { location.hash = pfadKnopf.dataset.ziel; return; }
    const eintrag = e.target.closest('.eintrag[data-ziel]:not(.leer)');
    if (eintrag) { location.hash = eintrag.dataset.ziel; return; }
    const wz = e.target.closest('.werkzeug[data-tat]');
    if (wz) { werkzeug(wz.dataset.tat); return; }
    const auf = e.target.closest('.fall-aufklappen');
    if (auf) { $('.blatt').dataset.weitere = 'offen'; auf.remove(); return; }
    const anker = e.target.closest('.toc a[data-anker]');
    if (anker) {
      e.preventDefault();
      $('#papierblatt').querySelector(`#${CSS.escape(anker.dataset.anker)}`)
        ?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });

  /* Interner Verweis von einer Akte auf eine andere */
  $('#papierblatt').addEventListener('click', (e) => {
    const a = e.target.closest('a[data-akte]');
    if (a) { e.preventDefault(); location.hash = `#/a/${a.dataset.akte}`; }
  });

  $('#overlay-zu').addEventListener('click', overlayZu);

  geraetewahlZeichnen();
  $('#k-thema').addEventListener('click', () => geraeteklappe());
  $('#themenwahl').addEventListener('click', (e) => {
    const b = e.target.closest('.geraet-wahl');
    if (b) { geraetSetzen(b.dataset.thema); geraeteklappe(false); $('#k-thema').focus(); }
  });
  $('#k-effekte').addEventListener('click', () => {
    EIN.effekte = !EIN.effekte; anwenden(); einstellungenSichern();
  });
  $('#k-kontrast').addEventListener('click', () => {
    EIN.kontrast = EIN.kontrast === 'hoch' ? 'normal' : 'hoch';
    anwenden(); einstellungenSichern();
  });
  $('#k-schrift').addEventListener('click', () => {
    const stufen = [1, 1.12, 1.26, 1.42, 0.9];
    EIN.skala = stufen[(stufen.indexOf(EIN.skala) + 1) % stufen.length] ?? 1;
    anwenden(); einstellungenSichern();
  });

  addEventListener('keydown', (e) => {
    const imFeld = e.target.matches('input, textarea');
    if (e.key === 'Escape') {
      if (imFeld) { e.target.blur(); return; }
      zurueck(); return;
    }
    if (imFeld) return;
    switch (e.key) {
      case 'ArrowDown': case 'j': e.preventDefault(); bewege(1); break;
      case 'ArrowUp':   case 'k': e.preventDefault(); bewege(-1); break;
      case 'Enter': {
        const ziel = Z.eintraege[Z.zeiger]?.dataset.ziel;
        if (ziel) { e.preventDefault(); location.hash = ziel; }
        break;
      }
      case '/': e.preventDefault(); $('#suche').focus(); $('#suche').select(); break;
      case 'o': werkzeug('original'); break;
      case 'm': werkzeug('merken'); break;
      case 'd': werkzeug('drucken'); break;
      case 'v': werkzeug('vorlesen'); break;
      case 'n': werkzeug('nachfragen'); break;
      case 't': {
        const i = GERAETE.findIndex((g) => g.id === EIN.thema);
        geraetSetzen(GERAETE[(i + 1) % GERAETE.length].id);
        break;
      }
      case 'g': geraeteklappe(); break;
      case '?': hilfe(); break;
    }
  });

  addEventListener('hashchange', route);

  /* Wischgeste zurueck auf dem Handy */
  let x0 = null;
  addEventListener('touchstart', (e) => { x0 = e.touches[0].clientX; }, { passive: true });
  addEventListener('touchend', (e) => {
    if (x0 !== null && e.changedTouches[0].clientX - x0 > 90 && x0 < 60) zurueck();
    x0 = null;
  }, { passive: true });

  setInterval(() => {
    $('#uhr').textContent = new Date().toLocaleTimeString('de-DE',
      { hour: '2-digit', minute: '2-digit' });
  }, 1000);
  $('#uhr').textContent = new Date().toLocaleTimeString('de-DE',
    { hour: '2-digit', minute: '2-digit' });
}

function hilfe() {
  setzeInhalt(`
    <div class="abschnitt">Bedienung</div>
    <p class="hinweis">
      <b>Pfeiltasten</b> oder <b>J/K</b> wählen einen Eintrag, <b>Eingabe</b> öffnet ihn,
      <b>Esc</b> geht eine Ebene zurück. <b>/</b> springt ins Suchfeld.
      In einer geöffneten Akte: <b>O</b> Original, <b>M</b> merken, <b>D</b> drucken,
      <b>V</b> vorlesen, <b>N</b> nachfragen.<br><br>
      Auf dem Handy: tippen zum Öffnen, vom linken Rand nach rechts wischen für
      zurück.<br><br>
      <b>G</b> öffnet die Gerätewahl, <b>T</b> schaltet zum nächsten Gerät.
      Es gibt zehn; jedes stellt Röhre <em>und</em> Papier um.<br><br>
      Die vier Knöpfe unter dem Schirm schalten Gerät, Bildschirmeffekte,
      Schriftgröße und hohen Kontrast – alles wird lokal gespeichert.
    </p>
    <div class="abschnitt">Zuletzt gelesen</div>
    <ul class="liste">${EIN.verlauf.slice(0, 8).map((v) => `
      <li class="eintrag" data-ziel="#/a/${v.id}">
        <span class="zeiger" aria-hidden="true"></span><span></span>
        <span class="name">${esc(v.titel)}</span><span class="zahl"></span></li>`).join('')
      || '<li class="eintrag leer"><span></span><span></span><span class="name">—</span><span></span></li>'}
    </ul>`);
}

/* ==============================  Start  =================================== */

einstellungenLaden();
verdrahten();
booten().then(route);
