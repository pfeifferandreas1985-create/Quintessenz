/* ===========================================================================
   Kleiner TeX-Setzer fuer das Papier.

   Warum kein KaTeX/MathJax: die Anwendung muss vollstaendig offline laufen und
   soll auf einem Pi 5 in unter einer Sekunde eine Seite liefern. KaTeX kostet
   ~280 kB plus Schriften fuer eine Handvoll Formeln je Akte. Die Teilmenge,
   die in technischen Handbuechern und Wikipedia-Artikeln tatsaechlich vorkommt,
   laesst sich mit <sup>, <sub> und einem gestapelten Bruch sauber setzen.

   Unterstuetzt: \frac \tfrac \dfrac, ^ _ (auch mit {}), \sqrt, \cdot \times \pm
   \le \ge \ne \approx \to \infty \partial, griechische Buchstaben, \mathrm
   \mathbf \text, \left( \right), Abstaende \, \; \quad, Funktionsnamen
   (\sin \cos \tan \log \ln \exp ...).

   Alles andere wird unveraendert und escaped ausgegeben - sichtbar, aber nie
   als Rohbefehl mit Backslash. Wenn eine Akte etwas zeigt, das hier fehlt,
   steht es in der Klartextzeile darunter (Feld 'text' des Formelblocks).
   =========================================================================== */

const GRIECHISCH = {
  alpha: 'α', beta: 'β', gamma: 'γ', delta: 'δ',
  epsilon: 'ε', varepsilon: 'ε', zeta: 'ζ', eta: 'η',
  theta: 'θ', vartheta: 'ϑ', iota: 'ι', kappa: 'κ',
  lambda: 'λ', mu: 'μ', nu: 'ν', xi: 'ξ',
  pi: 'π', rho: 'ρ', sigma: 'σ', tau: 'τ',
  upsilon: 'υ', phi: 'φ', varphi: 'φ', chi: 'χ',
  psi: 'ψ', omega: 'ω',
  Gamma: 'Γ', Delta: 'Δ', Theta: 'Θ', Lambda: 'Λ',
  Xi: 'Ξ', Pi: 'Π', Sigma: 'Σ', Phi: 'Φ',
  Psi: 'Ψ', Omega: 'Ω',
};

const ZEICHEN = {
  cdot: '·', times: '×', div: '÷', pm: '±', mp: '∓',
  le: '≤', leq: '≤', ge: '≥', geq: '≥',
  ne: '≠', neq: '≠', approx: '≈', equiv: '≡',
  propto: '∝', infty: '∞', partial: '∂', nabla: '∇',
  to: '→', rightarrow: '→', leftarrow: '←',
  Rightarrow: '⇒', leftrightarrow: '↔',
  sum: '∑', prod: '∏', int: '∫',
  circ: '°', degree: '°', deg: '°',
  ohm: 'Ω', Omega_: 'Ω', ldots: '…', dots: '…',
  angle: '∠', perp: '⊥', parallel: '∥',
};

const FUNKTIONEN = new Set([
  'sin', 'cos', 'tan', 'cot', 'sec', 'csc', 'arcsin', 'arccos', 'arctan',
  'sinh', 'cosh', 'tanh', 'log', 'ln', 'lg', 'exp', 'lim', 'max', 'min',
  'det', 'dim', 'mod',
]);

const ABSTAND = { ',': '.16em', ';': '.28em', ':': '.22em', ' ': '.3em', quad: '1em', qquad: '2em' };

const esc = (s) => String(s).replace(/[&<>"]/g, (c) =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

/* --- Zerteilen -------------------------------------------------------------
   Liefert eine flache Folge von Marken. Gruppen {...} bleiben als Rohtext
   erhalten und werden beim Setzen rekursiv verarbeitet.                     */

function gruppeLesen(s, i) {
  // s[i] === '{' ; liefert [inhalt, naechsterIndex]
  let tiefe = 0, start = i + 1;
  for (let j = i; j < s.length; j++) {
    if (s[j] === '{' && s[j - 1] !== '\\') tiefe++;
    else if (s[j] === '}' && s[j - 1] !== '\\') {
      tiefe--;
      if (tiefe === 0) return [s.slice(start, j), j + 1];
    }
  }
  return [s.slice(start), s.length];
}

/* Liest das naechste Argument: entweder {Gruppe} oder ein einzelnes Zeichen
   bzw. ein \befehl. Fuer ^2 und _{20} gleichermassen. */
function argumentLesen(s, i) {
  while (s[i] === ' ') i++;
  if (s[i] === '{') return gruppeLesen(s, i);
  if (s[i] === '\\') {
    const m = /^\\([a-zA-Z]+)/.exec(s.slice(i));
    if (m) return [m[0], i + m[0].length];
    return [s.slice(i, i + 2), i + 2];
  }
  return [s[i] ?? '', i + 1];
}

function bruch(zaehler, nenner, klein) {
  return `<span class="tex-bruch${klein ? ' klein' : ''}">` +
         `<span class="z">${setze(zaehler)}</span>` +
         `<span class="n">${setze(nenner)}</span></span>`;
}

export function setze(tex) {
  let out = '';
  const s = String(tex ?? '');
  let i = 0;

  while (i < s.length) {
    const c = s[i];

    if (c === '{') { const [g, j] = gruppeLesen(s, i); out += setze(g); i = j; continue; }
    if (c === '}') { i++; continue; }

    if (c === '^' || c === '_') {
      const [arg, j] = argumentLesen(s, i + 1);
      const tag = c === '^' ? 'sup' : 'sub';
      out += `<${tag}>${setze(arg)}</${tag}>`;
      i = j; continue;
    }

    if (c === '\\') {
      const m = /^\\([a-zA-Z]+)/.exec(s.slice(i));
      if (!m) {                                   // \, \; \{ \} \% ...
        const naechstes = s[i + 1] ?? '';
        if (ABSTAND[naechstes] !== undefined) {
          out += `<span style="display:inline-block;width:${ABSTAND[naechstes]}"></span>`;
        } else {
          out += esc(naechstes);
        }
        i += 2; continue;
      }
      const befehl = m[1];
      i += m[0].length;

      if (befehl === 'frac' || befehl === 'dfrac' || befehl === 'tfrac') {
        const [z, i1] = argumentLesen(s, i);
        const [n, i2] = argumentLesen(s, i1);
        out += bruch(z, n, befehl === 'tfrac');
        i = i2; continue;
      }
      if (befehl === 'sqrt') {
        const [a, j] = argumentLesen(s, i);
        out += `√<span class="tex-wurzel">${setze(a)}</span>`;
        i = j; continue;
      }
      if (befehl === 'mathrm' || befehl === 'text' || befehl === 'operatorname') {
        const [a, j] = argumentLesen(s, i);
        out += `<span class="tex-aufrecht">${setze(a)}</span>`;
        i = j; continue;
      }
      if (befehl === 'mathbf') {
        const [a, j] = argumentLesen(s, i);
        out += `<b class="tex-aufrecht">${setze(a)}</b>`;
        i = j; continue;
      }
      if (befehl === 'left' || befehl === 'right') { continue; }  // Klammer folgt
      if (befehl === 'quad' || befehl === 'qquad') {
        out += `<span style="display:inline-block;width:${ABSTAND[befehl]}"></span>`;
        continue;
      }
      if (FUNKTIONEN.has(befehl)) {
        out += `<span class="tex-aufrecht">${befehl}</span> `;
        continue;
      }
      if (GRIECHISCH[befehl] !== undefined) { out += GRIECHISCH[befehl]; continue; }
      if (ZEICHEN[befehl] !== undefined) { out += ZEICHEN[befehl]; continue; }

      out += esc(befehl);                         // unbekannt: lesbar, ohne Backslash
      continue;
    }

    if (c === ' ') { out += ' '; i++; continue; }

    /* Variablen kursiv, Ziffern und Operatoren aufrecht - so setzt man Formeln. */
    if (/[A-Za-z]/.test(c)) { out += `<i>${esc(c)}</i>`; i++; continue; }
    out += esc(c); i++;
  }
  return out;
}

export default setze;
