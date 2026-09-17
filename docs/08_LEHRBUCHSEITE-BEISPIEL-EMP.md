# Beispiel: Lehrbuchseite „Elektromagnetischer Puls" für Claude Design

Ausgefüllte Fassung der Vorlage aus [07_LEHRBUCHSEITE-PROMPT.md](07_LEHRBUCHSEITE-PROMPT.md),
angepasst an Claude Design: Grafiken werden als **Inline-SVG** direkt erzeugt statt als Prompt
für einen Bildgenerator. Thema aus der Hochspannungsbibliothek (`own/hvkb`), Ausrichtung
**Verstehen und Schützen**. Bauanleitungen für Pulsquellen sind bewusst ausgeschlossen
(§ 148 TKG, siehe `own/hvkb/QUELLEN.md`).

Ein Faktenblatt ist eingebaut, damit die Seite nicht frei fantasiert. Alle Werte dort sind
Größenordnungen aus IEC 61000-2-9 / 61000-5-x und der Fachliteratur; die Seite soll sie als
Richtwerte kennzeichnen.

---

```text
THEMA: „Der elektromagnetische Puls (EMP): Entstehung, Wirkung auf Elektronik, Schutz"
Kapitelkürzel: HV-07 (Reihe Hochspannungs- und Impulstechnik)

Erstelle zu diesem Thema eine Lehrbuch-Doppelseite (2 × DIN A4, Hochformat) als eine einzelne
HTML-Datei mit eingebettetem CSS und Inline-SVG-Grafiken, im Stil eines technischen Lehrbuchs
aus einer Welt, in der die 1950er nie aufgehört haben: Atompunk, Retro-Futurismus,
Atomzeitalter-Optimismus, Schulwandtafel-Ästhetik. Ernsthaftes Lehrmittel, kein Spiel-Look.

== RAHMEN ==
- Sprache Deutsch, Niveau interessierter Praktiker (Elektriker, Funkamateur, Werkstatt).
- Ziel der Seite: Der Leser versteht, wie ein EMP entsteht und in Geräte einkoppelt, und kann
  seine Elektronik mit einfachen Mitteln schützen und nach einem Ereignis prüfen.
- Ausdrücklich NICHT enthalten: Aufbau, Dimensionierung oder Betrieb von Geräten, die
  elektromagnetische Impulse erzeugen (Marx-Generator, Flusskompression, Vircator o. ä.).
  Wenn Quellen erwähnt werden, dann nur als Naturereignis oder historisches Ereignis.
- Kein erfundenes Wissen. Zahlen nur aus dem Faktenblatt unten oder als „Richtwert" markiert.

== FAKTENBLATT (verwenden, nicht erweitern) ==
- Drei natürliche/technische Quellen: Blitz (LEMP, lokal, µs-Bereich); Sonnensturm /
  geomagnetischer Sturm (langsame Erdströme in langen Leitungen, Minuten bis Stunden; Beispiele:
  Carrington-Ereignis 1859, Québec-Netzausfall 13. März 1989, 9 Stunden); nuklearer Höhen-EMP
  (NEMP/HEMP, historisch Starfish Prime 9. Juli 1962, Störungen an Straßenbeleuchtung auf Hawaii).
- HEMP nach IEC 61000-2-9 in drei Phasen: E1 schnell (Anstieg ca. 2–5 ns, Dauer bis ca. 1 µs,
  Feldstärke bis ca. 50 kV/m), E2 mittel (1 µs bis 1 s, blitzähnlich), E3 langsam (1 s bis
  Minuten, wirkt wie geomagnetischer Sturm auf lange Leitungen).
- Einkopplung: Feld → Leiter wirkt als Antenne. Je länger der Leiter, desto mehr Spannung
  (Netzleitungen, Antennen, lange Kabel sind die Hauptpfade). Kurze, geräteinterne Leiterbahnen
  sind bei E1 kritisch, lange Leitungen bei E2/E3.
- Empfindlichkeit: Halbleiter (MOSFET-Gates, Mikrocontroller, Funkempfänger-Eingangsstufen)
  sterben ab wenigen Volt über Nennspannung; Elektromechanik (Relais, Motoren, Glühlampen,
  Röhren) ist erheblich robuster.
- Schutzprinzipien (IEC 61000-5-Reihe): 1. Abschirmen (Faraday-Käfig: leitfähige Hülle ohne
  Schlitze länger als ca. 1/20 der Wellenlänge, Deckel überlappend, keine durchgeführten Kabel;
  Richtwert für gute Kisten 40–60 dB Dämpfung), 2. Trennen (Gerät ist nicht angeschlossen, Stecker
  raus, Antennen ab), 3. Ableiten (Überspannungsschutz mit Gasableiter + Varistor + Suppressordiode
  gestaffelt, kurze Erdverbindung), 4. Filtern (Netzfilter, Ferrite), 5. Vorrat (Ersatzgeräte
  geschützt lagern: Funkgerät, Ladegerät, Solarregler, Zündmodul).
- Metallkiste/Munitionskiste mit leitfähig gereinigter Dichtfläche ist ein brauchbarer Käfig;
  Alufolie mehrlagig um Karton um das Gerät ebenfalls (Gerät darf die Hülle nicht berühren).
- Prüfmethode ohne Messgerät: Mobiltelefon oder UKW-Radio in die geschlossene Kiste, anrufen
  bzw. Empfang prüfen; kein Empfang = grob dicht (Richtwert, kein Messwert).
- Nach einem Ereignis: erst sichtbare Schäden, dann Sicherungen, dann Netzteile, dann
  Halbleiter prüfen; geschützte Ersatzgeräte erst nach 24 h einsetzen (Folgeereignisse).
- Rechtlicher Hinweis für die Fußzeile: Betrieb störender Sender/Impulsquellen ist in
  Deutschland verboten (§ 148 TKG), Schutzmaßnahmen sind frei.

== AUFBAU DER DOPPELSEITE ==
  1. Kopfband: „HV-07 · Der elektromagnetische Puls", Untertitel: „Warum ein Blitz am Himmel
     Geräte im Keller tötet, und was eine Blechkiste dagegen kann."
  2. Einstieg „Warum das wichtig ist" (3–5 Sätze, Beispiel Québec 1989).
  3. Abschnitte: „Drei Quellen, ein Prinzip" · „E1, E2, E3: schnell, mittel, langsam" ·
     „Wie der Puls ins Gerät kommt" · „Fünf Schutzprinzipien" · „Nach dem Ereignis".
     Je 80–150 Wörter, erklärend.
  4. Merksatz-Kasten: „Nicht das Gerät, die Leitung ist die Antenne. Trennen schlägt Abschirmen,
     Abschirmen schlägt Hoffen."  Zahlenwerte-Kasten: E1/E2/E3 mit Dauer und typischem Pfad.
  5. Schritt-für-Schritt (6–8 Schritte): „Eine EMP-Schutzkiste aus einer Metallkiste bauen und
     prüfen" (nur Schutz, keine Quelle).
  6. Gefahr-Kasten: Überspannungsschutz nie ohne Erdung; keine Geräte mit Akku in luftdichter
     Kiste ohne Kontrolle; nach Sonnensturm Trafostationen meiden.
  7. Fehlertabelle „Symptom → Ursache → Abhilfe" (Kiste dämpft nicht: Dichtfläche lackiert /
     Kabel durchgeführt / Deckel verzogen …).
  8. Randspalte: Glossar (Feldstärke kV/m, Dämpfung dB, Faraday-Käfig, Varistor, geomagnetisch
     induzierter Strom), historische Notiz (Carrington 1859: Telegrafenlinien funkten, Papier
     brannte), Siehe auch: HV-03 Blitzschutz, HV-05 Überspannungsschutz.
  9. Fußzeile „Quellen und weiterführend": IEC 61000-2-9 (HEMP-Umgebung), IEC 61000-5-3 bis 5-7
     (HEMP-Schutzkonzepte), Kronjäger „Experimente mit Hochspannung" (Franzis, 2. Aufl. 2002) als
     Grundlagenwerk zu Impuls und Feld, Wahl „Neue Experimente mit EMPs, Tesla- und Mikrowellen"
     (Franzis 2005, nur Lesestoff), NASA/NOAA Space Weather Prediction Center. Plus der
     Rechtshinweis.
- Umfang 900–1.300 Wörter, kurze Sätze, Fachbegriff beim ersten Auftreten erklärt.

== GRAFIKEN (genau 3, als Inline-SVG im HTML) ==
  Abb. 1  Hauptillustration, halbe Seite: Schnitt durch ein Wohnhaus mit Keller. Von oben trifft
          eine stilisierte Wellenfront ein; nummerierte Bezugslinien (1) Freileitung als Antenne,
          (2) Hausanschluss/Zählerkasten, (3) Steckdose mit Gerät, (4) Antennenkabel vom Dach,
          (5) Metallkiste im Keller mit Ersatzgerät, (6) Erdungsschiene. Legende rechts unten.
  Abb. 2  Tafelgrafik: Zeitachse logarithmisch von 1 ns bis 1 h, darüber die drei Balken E1/E2/E3
          mit Beschriftung „SCHNELL · MITTEL · LANGSAM" und darunter der jeweils gefährdete Pfad
          („Geräteintern", „Hausinstallation", „Netz/Fernleitung").
  Abb. 3  Sicherheitsplakat im 50er-Arbeitsschutzstil: eine Hand zieht einen Stecker, dahinter
          ein stilisiertes Gewitter oder eine Sonne mit Strahlenkranz. Text maximal 6 Wörter,
          z. B. „STECKER RAUS. KISTE ZU. RUHE BEWAHREN."
Stil aller SVGs: Strichzeichnung wie Lithografie, zweifarbiger Druck (Tinte #1E1A14 auf Papier
#E8DCC0, Akzent Rostrot #8B2E1F, Zweitakzent Senf #E3B505), Halbton-Schraffur als Muster,
Beschriftungen in Versalien in einer geometrischen Sans, leichte Passer-Ungenauigkeit, keine
Verläufe, kein Leuchten, kein Chrom, keine Videospiel-Anleihen, keine Waffen.

== GESTALTUNG ==
- Papier #E8DCC0 → #D9CBA3 mit feiner Struktur, Tinte #1E1A14, Stempelrot #8B2E1F für
  Kapitelnummer, Merksatz-Rahmen, Randmarken; Gefahr-Kasten mit Schwarz/#E3B505-Warnstreifen.
- Schriften mit lokalem @font-face und System-Fallback: Überschriften geometrische 50er-Sans
  (Jost / League Spartan, Versalien, gesperrt), Fließtext Courier Prime oder IBM Plex Serif,
  Tabellen Monospace. Kontrast ≥ 7:1, Lesbarkeit vor Effekt.
- Zweispaltig mit schmaler Randspalte außen, Abbildungen mit Doppelrahmen und „Abb. N"-Etikett,
  Tabellen wie gestempelte Formulare, Fußzeile mit Seitenzahl und „HV-07".
- Druck-CSS mit @page A4, Seitenumbruch zwischen den beiden Seiten, keine externen Ressourcen.

== AUSGABE ==
1. Die fertige HTML-Datei (beide Seiten, SVGs eingebettet).
2. Danach eine kurze Liste „Bitte prüfen" mit allen Zahlen, die über das Faktenblatt hinausgehen.
```

---

## Nach dem Test

- Ergebnis als PDF drucken → `D:\DoomsdayBox\own\lehrbuch\HV-07_EMP.pdf`, im Kopf „KI-erzeugt,
  geprüft am …" ergänzen, dann in `own/hvkb/data/raw/` legen, damit die RAG-Pipeline sie mit
  indiziert.
- Wenn das Layout überzeugt: dieselbe Vorlage für HV-03 Blitzschutz und HV-05
  Überspannungsschutz, dann ergibt sich eine kleine Reihe mit funktionierenden Querverweisen.
