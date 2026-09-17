# Prompt: Lehrbuchseite im Atompunk-Stil zu einem beliebigen Thema

Vorlage für ein KI-Werkzeug mit Text- **und** Bildausgabe (oder Text-Modell plus separater
Bildgenerator). Nur die Zeile `THEMA:` ausfüllen, Rest unverändert einfügen. Die Farb- und
Schriftwerte sind dieselben wie im [Quintessenz-Terminal](06_TERMINAL-AUFTRAG.md), damit die
Seiten später als PDF in die DoomsdayBox passen.

---

```text
THEMA: [hier eintragen, z. B. „Der Bleiakkumulator: Aufbau, Laden, Pflege"]

Erstelle zu diesem Thema eine Lehrbuch-Doppelseite (2 × DIN A4, Hochformat) im Stil eines
technischen Lehrbuchs aus einer Welt, in der die 1950er nie aufgehört haben: Atompunk,
Retro-Futurismus, Atomzeitalter-Optimismus, Schulwandtafel-Ästhetik. Kein Fantasy-Gimmick,
sondern ein ernsthaftes Lehrmittel, das man in einer Werkstatt aufhängen könnte.

== INHALT (Priorität 1: fachlich richtig) ==
- Sprache Deutsch, Niveau: interessierter Praktiker ohne Vorwissen im Thema (Berufsschule / Gesellenbrief).
- Kein erfundenes Wissen. Zahlenwerte, Formeln, Grenzwerte und Sicherheitsangaben nur, wenn du
  dir sicher bist; sonst als „Richtwert, im Datenblatt prüfen" kennzeichnen. Keine Markennamen.
- Aufbau der Doppelseite:
  1. Kopfband: Kapitelnummer, Titel, Untertitel (ein Satz, was man danach kann).
  2. Einstieg „Warum das wichtig ist" (3–5 Sätze, ein konkretes Alltags- oder Notfallbeispiel).
  3. Drei bis fünf Abschnitte mit Zwischenüberschrift, je 80–150 Wörter. Erklären, nicht aufzählen.
  4. Ein „Merksatz"-Kasten (max. 2 Sätze, fett) und ein „Faustregel / Zahlenwerte"-Kasten (Tabelle, max. 6 Zeilen).
  5. Eine nummerierte Schritt-für-Schritt-Anleitung (5–8 Schritte) für die wichtigste praktische Handlung.
  6. Ein „Gefahr"-Kasten mit Warnstreifen: was kann verletzen oder zerstören, was tut man dann.
  7. Eine „Fehler und ihre Ursachen"-Tabelle (Symptom → Ursache → Abhilfe, 4–6 Zeilen).
  8. Randspalte: 3–5 Begriffe erklärt (Glossar), 1 historische Notiz (2 Sätze), 1 Querverweis „Siehe auch".
  9. Fußzeile: „Quellen und weiterführend" mit 3–5 echten, überprüfbaren Werken oder Normen
     (Titel, Urheber, Jahr; keine URLs erfinden).
- Umfang gesamt 900–1.300 Wörter. Kurze Sätze. Fachbegriff beim ersten Auftreten erklärt.

== GRAFIKEN UND ILLUSTRATIONEN (genau 3) ==
Plane drei Abbildungen und liefere für jede: Bildnummer, Bildunterschrift (1–2 Sätze, sagt, was
zu sehen ist und worauf zu achten ist) und einen eigenständigen Bildprompt in Englisch für einen
Bildgenerator. Die drei Bildtypen sind fest:
  Abb. 1  Hauptillustration (halbe Seite): Schnittzeichnung oder Explosionsdarstellung des zentralen
          Gegenstands mit 5–8 nummerierten Bezugslinien und Legende.
  Abb. 2  Vorgangsdiagramm: Ablauf, Kreislauf oder Kennlinie als Tafelgrafik mit beschrifteten Achsen
          bzw. Pfeilen.
  Abb. 3  Sicherheits- oder Piktogrammtafel im Stil eines 50er-Arbeitsschutzplakats: eine Figur oder
          ein Symbol, eine Botschaft, maximal 6 Wörter Text.
Jeder Bildprompt enthält wörtlich diesen Stilblock:
  „1950s atompunk technical textbook illustration, mid-century schoolbook lithograph, clean ink
  linework, two-color spot printing (ink #1E1A14 on aged paper #E8DCC0, accent rust red #8B2E1F,
  second accent mustard #E3B505), halftone shading, slightly misregistered print, numbered callout
  lines with a legend box, geometric 1950s sans-serif labels, optimistic atomic-age poster mood,
  no photorealism, no modern UI, no glow effects, no chrome, no video-game references, no
  trademarked mascots or logos, no gore, no weapons."
Ergänze je Bild konkret, was dargestellt ist, welche Teile beschriftet sind und aus welcher
Perspektive. Beschriftungen im Bild auf Deutsch, kurz, in Großbuchstaben. Die Nummern in Abb. 1
müssen zur Legende im Text passen.

== GESTALTUNG DER SEITE ==
- Papier: Farbverlauf #E8DCC0 → #D9CBA3, leichte Faserstruktur. Tinte #1E1A14. Stempelrot #8B2E1F
  für Kapitelnummer, Merksatz-Rahmen und Randmarken. Gefahr-Kasten mit Schwarz/#E3B505-Warnstreifen.
- Schriften (frei lizenziert): Überschriften geometrische 50er-Sans (z. B. Jost oder League Spartan,
  Versalien, gesperrt), Fließtext eine gut lesbare Buch- oder Schreibmaschinenschrift
  (z. B. Special Elite, Courier Prime oder IBM Plex Serif), Tabellen in Monospace.
- Zweispaltiger Satz mit schmaler Randspalte außen. Abbildungen mit dünnem Doppelrahmen und
  „Abb. N"-Etikett wie eingeklebt. Tabellen wie gestempelte Formulare. Seitenzahl und
  Kapitelkürzel in der Fußzeile. Alle Effekte dezent; Lesbarkeit geht vor Stil (Kontrast ≥ 7:1).
- Keine Marken, Figuren oder Schriften aus Videospielen. Eigene Namen, eigene Piktogramme.

== AUSGABEFORMAT ==
1. Zuerst der komplette Seitentext in Markdown mit den Kästen, Tabellen und Bildplatzhaltern
   „[Abb. 1 hier]" an den richtigen Stellen.
2. Dann die drei Bildprompts, klar getrennt, jeweils mit Bildunterschrift.
3. Dann eine einzelne HTML-Datei (DIN A4, CSS für Druck mit @page, alle Stile inline, keine
   externen Ressourcen, Schriften als lokale @font-face-Verweise mit Fallback), die den Text im
   beschriebenen Layout setzt und die Bilder unter „abb1.png", „abb2.png", „abb3.png" einbindet.
4. Zum Schluss eine Liste „Bitte prüfen": alle Zahlenwerte und Sicherheitsangaben, die du nicht
   sicher belegen kannst.
Falls du selbst Bilder erzeugen kannst: erzeuge die drei Bilder zusätzlich direkt nach den
Bildprompts. Falls nicht: gib nur die Prompts aus.
```

---

## Hinweise zur Nutzung

- **Für Bild-Werkzeuge ohne Textverständnis** (Midjourney, Stable Diffusion, Flux): nur die drei
  Bildprompts übernehmen. Die Bildbeschriftungen in Großbuchstaben werden dort oft falsch
  geschrieben; entweder nachträglich in einem Bildeditor setzen oder im Prompt „no text" ergänzen
  und die Legende ausschließlich im Seitentext führen.
- **Für die DoomsdayBox:** die HTML-Datei mit `tools/seiten_zu_pdf.py` oder dem Browser als PDF
  drucken und unter `D:\DoomsdayBox\own\lehrbuch\<Thema>.pdf` ablegen. Im Dateikopf Datum und
  Hinweis „KI-erzeugt, Angaben geprüft am …" eintragen, sonst ist es keine Quelle, sondern ein
  Entwurf.
- **Serien:** Gleiche Kapitelnummerierung durchziehen (z. B. E-01 Elektrik, M-01 Mechanik, S-01
  Sanitär), dann lassen sich die Seiten später zu einem Band binden.
- **Warum drei feste Bildtypen:** Schnitt, Ablauf, Warnung decken 90 % der Lehrmittelbedarfe ab
  und zwingen das Modell, das Thema aus drei Richtungen zu denken. Für rein theoretische Themen
  Abb. 1 durch ein Schema ersetzen (im Prompt die Zeile anpassen).
