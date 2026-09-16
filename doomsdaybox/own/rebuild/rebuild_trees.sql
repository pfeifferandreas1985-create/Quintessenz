-- rebuild_trees.sql – Technologie-Abhängigkeitsbäume (Modul Zivilisationsneustart)
-- Aufbau:  sqlite3 rebuild_trees.db < rebuild_trees.sql
-- Kategorie = Dartnell-Kapitel. xref = Verweise auf andere Module (mech:, med:, surv:, mil:).
-- Alle Einträge sind eigene Zusammenfassungen; Quellen im Feld source.

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS tech (
  id               TEXT PRIMARY KEY,
  name             TEXT NOT NULL,
  category         TEXT NOT NULL,          -- Dartnell-Kapitel
  description_md   TEXT,
  min_viable_scale TEXT NOT NULL CHECK (min_viable_scale IN
                     ('Haushalt','Dorf','Region','Salvage')),  -- Salvage = nicht rekonstruierbar, nur bergen
  era_equivalent   TEXT,                   -- Jahr, ab dem der Stand der Technik beherrschbar war
  salvage_lifetime TEXT,                   -- wie lange geborgene Exemplare nutzbar bleiben
  xref             TEXT,                   -- z. B. 'mech:motor-rewinding; med:...'
  source           TEXT
);

CREATE TABLE IF NOT EXISTS tech_input (
  tech_id       TEXT NOT NULL REFERENCES tech(id),
  input_id      TEXT NOT NULL REFERENCES tech(id),
  role          TEXT,                      -- Funktion des Eingangs im Produkt
  quantity_note TEXT,
  substitute    TEXT,                      -- Ersatz auf niedrigerer Stufe
  PRIMARY KEY (tech_id, input_id)
);

CREATE TABLE IF NOT EXISTS process (
  id            TEXT PRIMARY KEY,
  name          TEXT NOT NULL,
  produces      TEXT NOT NULL REFERENCES tech(id),
  inputs        TEXT,
  tools         TEXT,
  temperature_c TEXT,
  scale         TEXT CHECK (scale IN ('Haushalt','Dorf','Region','Salvage')),
  hazards       TEXT,
  steps_md      TEXT,
  source        TEXT
);

CREATE VIRTUAL TABLE IF NOT EXISTS tech_fts USING fts5(id, name, description_md, content='tech', content_rowid='rowid');
CREATE VIRTUAL TABLE IF NOT EXISTS process_fts USING fts5(id, name, steps_md, hazards, content='process', content_rowid='rowid');

-- ============================================================
-- Rohstoffe und Grundstoffe (Blätter des Baums)
-- ============================================================
INSERT INTO tech VALUES
('raw-copper-scrap','Kupferschrott (Kabel, Rohre, Wicklungen)','Schonfrist/Salvage','Wichtigste Kupferquelle nach dem Kollaps: Erdkabel, Hausinstallation, Transformatoren, Motoren. Erz-Verhüttung ist Regionsniveau, Schrott ist Dorfniveau.','Haushalt','vor 1800','unbegrenzt, korrodiert kaum','surv:salvage-priorities','Dartnell Kap. 1'),
('raw-iron-scrap','Eisen-/Stahlschrott','Schonfrist/Salvage','Blattfedern (Federstahl), Achsen (Vergütungsstahl), Bleche, Armierungsstahl. Kohlenstoffgehalt am Funkenbild erkennen.','Haushalt','vor 1800','Jahrzehnte, Rost oberflächlich','mech:werkstoffe-stahl-erkennen','Dartnell Kap. 4; Gingery Bd. 1'),
('raw-lead','Blei (Akkus, Dachblei, Gewichte)','Stoffe & Materialien','Aus Altakkus (Platten, Pasten) oder Baublei. Schmelzpunkt 327 °C, mit Holzfeuer erreichbar.','Haushalt','Antike','unbegrenzt','med:bleivergiftung','Wikipedia Blei'),
('raw-sulfur','Schwefel','Chemie','Vulkanisch, aus Pyrit durch Rösten, oder aus Gips über Reduktion. In Mitteleuropa knapp; Salvage: Schwefelsäure aus Altakkus zurückgewinnen.','Region','Antike','unbegrenzt','—','Rogers, Industrial Chemistry'),
('raw-wood','Holz (Brenn-, Bau-, Hartholz)','Energie','Buche/Eiche für Holzkohle, Pockholz/Weißbuche für Gleitlager, Esche für Werkzeugstiele.','Haushalt','—','—','surv:feuer','—'),
('raw-clay','Ton/Lehm','Stoffe & Materialien','Für Tiegel, Ofenauskleidung, Keramikisolatoren. Feuerfest durch Schamottezusatz (gebrannter, gemahlener Ton).','Haushalt','Steinzeit','—','—','Dartnell Kap. 4'),
('raw-sand-quartz','Quarzsand','Stoffe & Materialien','Formsand für Guss (mit Ton/Bentonit gebunden), Rohstoff für Glas.','Haushalt','Antike','—','—','Gingery Bd. 1'),
('raw-limestone','Kalkstein','Stoffe & Materialien','Brennen zu Branntkalk (900 °C) für Mörtel, Flussmittel im Schmelzofen, Natronlauge über Kaustifizierung von Soda.','Dorf','Antike','—','—','Practical Action Lime Burning'),
('raw-salt','Steinsalz/Meersalz','Chemie','Ausgang für Soda (Solvay), Salzsäure, Chlor. Konservierung.','Haushalt','Antike','—','surv:konservierung','—'),
('raw-fiber','Fasern (Flachs, Hanf, Wolle, Baumwolle)','Nahrung & Kleidung','Für Isolation (Baumwollumspinnung), Seile, Textil.','Haushalt','Steinzeit','—','—','Hooper, Hand-Loom Weaving'),
('raw-resin-shellac','Harze, Schellack, Leinöl','Stoffe & Materialien','Natürliche Isolierlacke: Schellack (Lackschildlaus, Import) oder Leinöl-Kopal-Lack (heimisch). Ersatz: Bienenwachs, Kolophonium.','Dorf','1800','Lackvorräte 10–20 Jahre','mech:isolationsklassen','Hawkins Bd. 1'),
('raw-mica-glass','Glimmer/Glas (Isolatoren)','Stoffe & Materialien','Glimmer als Kommutator-Isolation; Glas für Röhren, Gefäße, Isolatoren.','Dorf','Antike (Glas)','—','—','—'),
('raw-magnetite','Magnetit/Permanentmagnete','Stoffe & Materialien','Moderne Magnete (NdFeB, Ferrit) sind nicht rekonstruierbar. Salvage aus Festplatten, Motoren, Lautsprechern. Ersatz: Elektromagnet (fremderregt).','Salvage','—','NdFeB: Jahrzehnte, verliert bei >80 °C','mech:motor-typen','Dartnell Kap. 6'),
('raw-tungsten-nickel','Wolfram, Nickel (Röhren-Elektroden)','Kommunikation','Aus Glühlampen, Heizdrähten, Münzen. Röhrenbau ist Dorf-Grenzfall.','Salvage','1910','—','—','—');

-- ============================================================
-- Zwischenprodukte
-- ============================================================
INSERT INTO tech VALUES
('charcoal','Holzkohle','Energie','Universalbrennstoff für 1000–1300 °C mit Blasebalg. Meiler oder Retorte (Fass-in-Fass). Ausbeute 20–25 % der Holzmasse.','Haushalt','Steinzeit','—','surv:feuer','FAO Forestry Paper 41; Dartnell Kap. 4'),
('crucible','Schmelztiegel (Ton-Graphit oder Schamotte)','Stoffe & Materialien','Für Kupfer, Bronze, Aluminium. Graphit aus Batterien/Elektroden beimischen. Rissgefahr: langsam vorheizen.','Dorf','Bronzezeit','—','—','Gingery Bd. 1'),
('furnace-charcoal','Holzkohle-Schmelzofen mit Gebläse','Stoffe & Materialien','Ofenrohr aus Blech, Schamotteauskleidung, Gebläse aus Haartrockner-Motor, Handkurbel oder Blasebalg. 1100–1200 °C.','Dorf','Bronzezeit','—','mech:luefter-antrieb','Gingery Bd. 1 (Charcoal Foundry)'),
('copper-ingot','Kupferbarren/-stange','Stoffe & Materialien','Schrott im Tiegel schmelzen (1085 °C), Schlacke abziehen, in Sand- oder Grafitform als Stange gießen.','Dorf','Bronzezeit','—','—','Gingery Bd. 1'),
('draw-plate','Ziehstein / Ziehplatte aus gehärtetem Stahl','Stoffe & Materialien','Stahlplatte mit konischen Löchern abgestufter Durchmesser, gehärtet und poliert. Engpassbauteil für alle Drahtherstellung.','Dorf','1300','—','mech:haerten-anlassen','Hawkins Bd. 1; Wikipedia Drahtziehen'),
('wire-copper','Kupferdraht, blank','Stoffe & Materialien','Stange auf Kantendurchmesser hämmern, dann durch Ziehstein ziehen, alle 3–4 Züge weichglühen (500–600 °C). Handzugbank oder Winde.','Dorf','1300','Salvage-Draht: unbegrenzt','mech:leitungsdimensionierung','Hawkins Bd. 1'),
('wire-insulated','Isolierter Wickeldraht','Stoffe & Materialien','Blankdraht mit Baumwolle/Seide umspinnen und in Schellack/Leinöllack tauchen, trocknen. Lackdraht nur mit Ofen.','Dorf','1850','—','mech:isolationsklassen','Hawkins Bd. 1'),
('iron-bloom','Luppe / Schmiedeeisen aus Rennofen','Stoffe & Materialien','Nur nötig, wenn kein Schrott. Rennofen aus Lehm, Erz + Holzkohle, Ausbeute gering, Nachbearbeitung durch Ausschmieden.','Region','Eisenzeit','—','—','Dartnell Kap. 4'),
('steel-carbon','Kohlenstoffstahl (schmiedbar, härtbar)','Stoffe & Materialien','Aus Schrott (Federn, Feilen) oder durch Aufkohlen von Schmiedeeisen in Holzkohle-Kiste (900 °C, Stunden).','Dorf','Antike','—','mech:werkstoffe-stahl-erkennen','Drew, Farm Blacksmithing'),
('heat-treatment','Härten und Anlassen','Stoffe & Materialien','Auf Kirschrot (ca. 800 °C, nicht magnetisch) erhitzen, in Wasser/Öl abschrecken, anlassen nach Anlassfarbe (strohgelb 220 °C Schneidwerkzeug, blau 300 °C Federn).','Haushalt','Antike','—','mech:waermebehandlung','Drew; Wikipedia Anlassfarben'),
('iron-sheet-soft','Weicheisenblech, geglüht (Blechpaket)','Stoffe & Materialien','Trafoblech aus Salvage (Trafos, Motoren) oder Weißblech/Dachblech, entzinnt, geglüht und mit Lack/Papier isoliert geschichtet. Wirbelstromverluste ohne Silizium höher, aber brauchbar.','Dorf','1880','Salvage-Blechpakete unbegrenzt','mech:transformator-berechnung','Hawkins Bd. 2'),
('bronze','Bronze / Messing (Lagerwerkstoff)','Stoffe & Materialien','Kupfer + 10 % Zinn (Bronze) oder + 30 % Zink (Messing). Zinn aus Lötzinn, Zink aus Batteriehülsen, Dachrinnen.','Dorf','Bronzezeit','—','mech:gleitlager-auslegung','Gingery Bd. 1'),
('bearing-plain','Gleitlager (Bronze oder Pockholz)','Transport','Gegossene Bronzebuchse oder gedrehtes Hartholz, geschmiert mit Talg, Pflanzenöl, Graphit. Ersatz für Wälzlager bis mittlere Drehzahl.','Dorf','Antike','—','mech:lager-schmierung','Dartnell Kap. 7'),
('lathe-scrap','Drehbank aus Schrott (Gingery-Typ)','Stoffe & Materialien','Bett aus Aluminium- oder Zinkguss auf Stahlprofil, Spindel mit Bronzelagern, Antrieb über Riemen von Motor, Tretkurbel oder Wasserrad. Schlüsselwerkzeug für alles Weitere.','Dorf','1800','—','mech:zerspanung-grundlagen','Gingery Bd. 2'),
('sulfuric-acid','Schwefelsäure','Chemie','Historisch: Bleikammerverfahren (SO2 + NO2 + Wasser). Dorfnah: Rückgewinnung aus Altakkus, Aufkonzentrieren durch Eindampfen (Bleigefäß, Abzug). Kontaktverfahren braucht Katalysator (V2O5/Platin).','Region','1750','Akkusäure: Jahrzehnte im Glas','med:saeureverletzung','Rogers; Wikipedia Bleikammerverfahren'),
('lead-plate','Bleiplatten / Bleigitter','Energie','Blei gießen in Sandform mit Gitterstruktur, Paste aus Bleioxid (Bleimennige/Bleiglätte) + verdünnter Schwefelsäure einstreichen, formieren durch Laden.','Dorf','1860','—','mech:akku-lade-kennlinie','Hawkins Bd. 4; Wikipedia Bleiakkumulator'),
('glass-vessel','Glas- oder Keramikgefäß, säurefest','Stoffe & Materialien','Salvage (Einmachgläser!) oder Töpferware mit Bleiglasur (nicht für Lebensmittel). Glasherstellung: Sand + Soda + Kalk, 1400 °C, Regionsniveau.','Haushalt','Antike','Salvage-Gläser unbegrenzt; Neuherstellung ist Regionsniveau','—','Dartnell Kap. 4'),
('vacuum-tube','Elektronenröhre (Triode)','Kommunikation','Glaskolben, Wolfram-Glühfaden, Nickel-Anode, Vakuum über Pumpe + Getter. Handwerklich möglich (Amateur-Röhrenbauer belegen es), aber Dorf-Grenzfall. Salvage bevorzugen.','Region','1910','Lagerröhren 50+ Jahre','—','Wikipedia Elektronenröhre; ARRL Handbook 1928'),
('capacitor-inductor','Kondensator und Spule (selbstgebaut)','Kommunikation','Kondensator: Alufolie + gewachstes Papier oder Glasplatten. Spule: Draht auf Pappe/Holz. Beide Haushaltsniveau, Werte per Formel.','Haushalt','1850','—','mech:schwingkreis-berechnung','ARRL Handbook 1928'),
('crystal-detector','Detektor (Bleiglanz/Pyrit mit Kontaktspitze) oder Salvage-Diode','Kommunikation','Halbleiter-Gleichrichter auf Mineralbasis; genügt für Empfang starker Sender ohne Stromquelle.','Haushalt','1906','Salvage-Dioden unbegrenzt','—','Wikipedia Detektorempfänger'),
('spring-steel','Federstahl (Kontaktfedern)','Stoffe & Materialien','Aus Uhrfedern, Blattfedern, Klaviersaiten; anlassen blau für Federwirkung.','Haushalt','Antike','—','—','Drew'),
('insulator-ceramic-wood','Isolator (Keramik, Glas, trockenes Hartholz, Schellackpapier)','Stoffe & Materialien','Für Schalter- und Relaisgrundplatten, Klemmen, Isolatoren an Freileitungen.','Haushalt','Antike','—','—','—'),
('relay-coil','Elektromagnet / Relaisspule','Kommunikation','Weicheisenkern (Nagel, Schraube), isolierter Draht, Anker aus Weicheisenblech, Rückstellfeder.','Haushalt','1830','—','mech:relaislogik','Hawkins Bd. 1'),
('prime-mover','Antriebsmaschine (Wasserrad, Windrad, Holzgasmotor, Dampfmaschine)','Energie','Wasserrad oberschlächtig 60–70 % Wirkungsgrad, Dorfniveau. Holzgas-Generator für geborgene Ottomotoren: FEMA-Anleitung. Dampfmaschine: Region (Kesselbau, Druck!).','Dorf','1780','Verbrennungsmotoren: 20–40 Jahre mit Wartung','mech:generator-drehzahl; surv:wasserkraft','FEMA Wood Gas 1989; Practical Action Micro-Hydro'),
('commutator','Kommutator (Gleichstrom)','Energie','Kupfersegmente auf isolierter Nabe (Glimmer oder Schellackpapier), Kohlebürsten aus Batteriekohle oder Graphit. Alternative: Schleifringe + externer Gleichrichter (Salvage).','Dorf','1870','—','mech:gleichstrommaschine','Hawkins Bd. 2'),
('shaft-machined','Welle, gedreht','Transport','Rundstahl (Salvage-Achse) auf Drehbank auf Lagersitz gedreht; ohne Drehbank: gefeilt und geschliffen in Lehre.','Dorf','1800','—','mech:passungen','Gingery Bd. 2'),
('steel-balls-races','Kugeln und Laufringe, gehärtet und geschliffen','Transport','Kugeln: Stahlstücke in Kugelmühle zwischen Platten rund geschliffen, gehärtet, poliert. Laufringe: gedreht, gehärtet, geschliffen. Toleranzen im µm-Bereich nur mit Läppen. Realistisch: Salvage.','Region','1880','Salvage-Lager: unbegrenzt gefettet und trocken','mech:lager-toleranzen','Dartnell Kap. 7'),
('bimetal-bourdon','Bimetallstreifen / Bourdon-Rohr / Schwimmer','Zeit & Ort','Bimetall: Stahl + Messing vernietet, Ausschlag über Temperatur. Bourdon: flachgedrücktes gebogenes Messingrohr streckt sich unter Druck. Schwimmer: Blechdose an Hebel.','Haushalt','1820','—','mech:sensorik-mechanisch','Wikipedia Bimetall, Rohrfeder'),
('thermocouple-wire','Thermoelement aus zwei ungleichen Drähten','Zeit & Ort','Eisen + Kupfer-Nickel (Konstantan aus Widerstandsdraht/Heizdraht) ergibt Typ J-ähnlich; Kupfer + Konstantan Typ T. Kalibrieren an Eis (0 °C) und siedendem Wasser (100 °C). Ablesen mit Salvage-Multimeter oder Drehspulinstrument.','Haushalt','1830','—','mech:thermoelement-tabellen','NIST ITS-90; Wikipedia Thermoelement');

-- ============================================================
-- Die zehn Kerntechnologien
-- ============================================================
INSERT INTO tech VALUES
('electric-motor','Elektromotor','Energie',
'**Ziel:** Gleichstrom- oder Wechselstrommaschine, fremderregt (kein Permanentmagnet nötig).
**Warum Dorfniveau:** Alle Teile sind mit Tiegelofen, Ziehstein, Drehbank und Handwickeln herstellbar. Der Engpass ist isolierter Kupferdraht.
**Salvage-Strategie:** Zuerst geborgene Motoren neu wickeln (mech:motor-rewinding), erst danach Neubau. Ein Mechatroniker kann Wicklungsschemata berechnen; die Box hält Hawkins Bd. 2 und die eigenen Wicklungstabellen.
**Vereinfachung:** Universalmotor mit Reihenschlusswicklung läuft an Gleich- und Wechselstrom, keine Anlaufhilfe nötig.',
'Dorf','1880','Salvage-Motoren 30–50 Jahre, Wicklungen neu isolierbar','mech:motor-rewinding; mech:motor-typen; mech:isolationsklassen','Hawkins Bd. 2; Dartnell Kap. 6'),
('generator','Generator','Energie',
'**Ziel:** Gleichstrom-Nebenschlussgenerator (selbsterregend über Restmagnetismus) oder Wechselstrommaschine mit Schleifringen.
**Baugleich mit dem Motor;** jede Gleichstrommaschine läuft in beiden Richtungen. Der eigentliche Aufwand liegt in der Antriebsmaschine und der Drehzahlregelung (Fliehkraftregler, Wasserzulauf).
**Salvage:** Kfz-Lichtmaschine (mit Regler) + Wasserrad ist die schnellste Lösung; Erregung braucht 12 V Startbatterie.',
'Dorf','1870','Lichtmaschinen 20+ Jahre; Dioden sind Schwachpunkt','mech:generator-drehzahl; mech:gleichstrommaschine; surv:wasserkraft','Hawkins Bd. 2; FEMA Wood Gas; Practical Action'),
('transformer','Transformator','Energie',
'**Ziel:** Netz- oder Übertragungstrafo für Wechselspannung, um Leitungsverluste bei Dorfnetzen zu senken.
**Kern:** Geschichtetes Weicheisenblech (Salvage-Trafoblech ist deutlich besser als selbst geglühtes Blech). Ohne Siliziumstahl höhere Verluste, mit größerem Kern kompensierbar.
**Berechnung:** Windungszahl pro Volt ≈ 1/(4,44·f·B·A). Formel und B-Werte im Tabellenbuch (mech:transformator-berechnung).
**Öl:** Pflanzenöl (Rapsöl) als Isolier- und Kühlmedium ist historisch belegt.',
'Dorf','1885','Salvage-Trafos unbegrenzt, Öl prüfen','mech:transformator-berechnung; mech:isolationsklassen','Hawkins Bd. 3; Dartnell Kap. 6'),
('copper-wire-insulated','Isolierter Kupferdraht (Wickel- und Leitungsdraht)','Stoffe & Materialien',
'**Der Engpass der gesamten Elektrotechnik.** Ohne Draht kein Motor, Generator, Trafo, Relais, Funk.
**Kette:** Kupferschrott → Tiegelschmelze → Stange → Hämmern → Ziehstein (10–20 Züge mit Zwischenglühen) → Umspinnen mit Baumwolle → Schellack/Leinöllack.
**Salvage-Priorität 1:** Erdkabel und Trafowicklungen bergen, sortiert nach Durchmesser lagern, trocken. Lackdraht bleibt Jahrzehnte nutzbar.
**Realistische Rate:** Ein Zwei-Personen-Betrieb zieht wenige kg pro Tag.',
'Dorf','1300 (Draht), 1850 (Lackdraht)','unbegrenzt bei trockener Lagerung','mech:leitungsdimensionierung; mech:isolationsklassen','Hawkins Bd. 1; Wikipedia Drahtziehen'),
('ball-bearing','Kugellager','Transport',
'**Ziel:** Wälzlager für hohe Drehzahlen (Generatoren, Drehbankspindeln).
**Warum Regionsniveau:** Kugeln und Ringe brauchen gehärteten Stahl mit µm-Toleranzen und Schleif-/Läppprozesse; ohne Präzisionsmaschinen wird das Lager schlechter als ein gutes Gleitlager.
**Dorf-Alternative:** Bronze- oder Pockholz-Gleitlager, geschmiert. Für Wasserräder, langsame Getriebe, Handwerkzeug völlig ausreichend.
**Salvage:** Lager aus Fahrrädern, Motoren, Kfz. Gefettet, verpackt, trocken: unbegrenzt haltbar. Größte Lagerhaltungs-Priorität nach Draht.',
'Region','1880','unbegrenzt gefettet','mech:lager-toleranzen; mech:lager-schmierung; mech:gleitlager-auslegung','Dartnell Kap. 7'),
('battery-lead-acid','Blei-Akkumulator','Energie',
'**Ziel:** Speicher für Gleichstromnetz, Erregung des Generators, Funk.
**Kette:** Blei gießen → Gitter → Paste aus Bleioxid → formieren mit Schwefelsäure (1,28 g/cm³) → säurefestes Gefäß.
**Chemie-Engpass:** Schwefelsäure. Dorfnah nur durch Rückgewinnung aus Altakkus; Neuherstellung (Bleikammer) ist Regionsniveau und braucht Schwefel.
**Salvage:** Altakkus mit sulfatierten Platten sind reparierbar (Platten neu gießen, Säure filtern). LiFePO4-Zellen sind nicht rekonstruierbar, aber 10–20 Jahre nutzbar.
**Gefahren:** Bleidämpfe, Säure, Wasserstoff beim Laden (Explosion).',
'Dorf','1860','Blei-Akkus 5–10 Jahre; LiFePO4 10–20 Jahre','mech:akku-lade-kennlinie; med:bleivergiftung; med:saeureverletzung','Wikipedia Bleiakkumulator; Rogers'),
('radio-transceiver','Funksender/-empfänger','Kommunikation',
'**Empfang (Haushalt):** Detektorempfänger aus Spule, Drehkondensator (Alufolie/Papier), Bleiglanz-Detektor, Kopfhörer (Salvage) – braucht keinen Strom.
**Senden (Dorf, mit Röhre oder Salvage-Transistor):** Einröhren-Oszillator, Morsetaste, Drahtantenne. Reichweite auf Kurzwelle mit wenigen Watt: hunderte km.
**Halbleiter:** nicht rekonstruierbar. Transistoren, Dioden, ICs bergen, ESD-geschützt lagern. Röhrenbau ist handwerklich möglich, aber Grenzfall.
**Vorschrift:** Frequenzen und Betriebsverfahren im Modul Kommunikation (Bandplan, Notfunk).',
'Dorf','1920','Lagerröhren 50 Jahre; Halbleiter Jahrzehnte trocken','mech:schwingkreis-berechnung; mil:funkdisziplin; surv:notfunk','ARRL Handbook 1928; NEETS Modul 17/18'),
('switch-relay','Schalter und Relais','Energie',
'**Haushaltsniveau.** Kupferkontakte (aus Draht gehämmert), Federstahl, Isolatorgrundplatte (Hartholz, Keramik). Relais: Spule auf Weicheisenkern zieht Anker an.
**Bedeutung:** Relais sind die Logikelemente der SPS-Alternative. Kontaktabbrand mit Silberkontakten (Salvage: alte Relais, Besteck) verringern.
**Salvage:** Schütze, Relais, Schalter sind massenhaft vorhanden und praktisch unbegrenzt haltbar.',
'Haushalt','1830','unbegrenzt','mech:relaislogik; mech:schaltzeichen','Hawkins Bd. 1'),
('plc-equivalent','SPS-Äquivalent (Relais-, Nocken-, Pneumatiklogik)','Energie',
'**Kern-Erkenntnis:** Mikroelektronik ist nicht rekonstruierbar (Lithografie, Reinstchemie, Reinraum). SPS, Mikrocontroller, Frequenzumrichter sind reine Salvage-Güter.
**Strategie:** 1) SPS-Ersatzteile, Netzteile, I/O-Karten und Programmiergeräte einlagern, Programme und Backups in der Box (mech:sps-backup). 2) Jede Steuerung zusätzlich als Relaislogik dokumentieren (Stromlaufplan mit Selbsthaltung, Verriegelung, Zeitrelais). 3) Ablaufsteuerungen mechanisch: Nockenwelle mit Schaltnocken (Waschmaschinen-Prinzip). 4) Pneumatische Logik (UND/ODER/Speicher-Ventile) für explosionsgefährdete Bereiche.
**Zeitglieder:** Bimetall, RC-Glied mit Salvage-Bauteilen, Pneumatik-Drossel, Uhrwerk.',
'Dorf','1900 (Relais), 1950 (Pneumatiklogik)','SPS-Hardware 20–30 Jahre; Elkos sind Schwachpunkt','mech:relaislogik; mech:sps-backup; mech:pneumatik-logik; mech:iec61131-strukturierter-text','Wikipedia Relaislogik; Festo Pneumatik-Grundlagen'),
('sensor-basic','Sensoren (Temperatur, Druck, Füllstand, Drehzahl)','Zeit & Ort',
'**Haushalt bis Dorf.** Thermoelement aus zwei ungleichen Drähten; Bimetallthermostat; Bourdon-Rohr-Manometer; Schwimmerschalter; Fliehkraftregler für Drehzahl; Quecksilber-/Alkoholthermometer (Glasbläserei).
**Halbleitersensoren, Pt100, Hall-Sensoren, Encoder:** Salvage. Encoder-Alternative: Lochscheibe mit Lampe und Fotowiderstand (Salvage) oder mechanischer Kontakt.
**Kalibrierung ohne Referenzgeräte:** Eispunkt 0 °C, Siedepunkt 100 °C (druckkorrigiert), Wassersäule für Druck (1 m = 98 mbar), Pendel für Zeit.',
'Haushalt','1830','Salvage-Sensoren 10–30 Jahre','mech:sensorik-mechanisch; mech:thermoelement-tabellen; mech:kalibrierung-ohne-referenz','NIST ITS-90; WIKA Handbuch; Wikipedia');

-- ============================================================
-- Abhängigkeiten (Kanten)
-- ============================================================
INSERT INTO tech_input VALUES
-- Elektromotor
('electric-motor','copper-wire-insulated','Wicklungen Anker und Feld','einige kg je kW','Salvage-Lackdraht'),
('electric-motor','iron-sheet-soft','Blechpaket Stator/Rotor','—','Salvage-Motorblechpaket'),
('electric-motor','shaft-machined','Welle','—','Salvage-Achse, gefeilt'),
('electric-motor','bearing-plain','Lagerung','2 Stück','Salvage-Kugellager'),
('electric-motor','commutator','Stromwender (bei Gleichstrom)','—','Schleifringe + Salvage-Gleichrichter'),
('electric-motor','raw-resin-shellac','Wicklungsimprägnierung','—','Bienenwachs, Leinöl'),
('electric-motor','raw-magnetite','Permanentmagnet (optional)','—','Fremderregung mit Feldwicklung'),
-- Generator
('generator','electric-motor','Maschine selbst (baugleich)','—','Kfz-Lichtmaschine'),
('generator','prime-mover','Antrieb','—','Handkurbel/Tretantrieb (100–200 W)'),
('generator','switch-relay','Regelung, Abschaltung','—','—'),
('generator','battery-lead-acid','Erregung / Puffer','—','Restmagnetismus bei Nebenschlussmaschine'),
-- Transformator
('transformer','copper-wire-insulated','Primär-/Sekundärwicklung','—','—'),
('transformer','iron-sheet-soft','Kern','—','Salvage-Trafokern'),
('transformer','insulator-ceramic-wood','Spulenkörper, Klemmen','—','—'),
('transformer','raw-resin-shellac','Imprägnierung; Rapsöl als Kühlmedium','—','—'),
-- Draht
('copper-wire-insulated','wire-copper','Blankdraht','—','Salvage-Draht abisolieren'),
('copper-wire-insulated','raw-fiber','Umspinnung','—','Papierstreifen'),
('copper-wire-insulated','raw-resin-shellac','Lack','—','Leinöl-Kopal, Bienenwachs'),
('wire-copper','copper-ingot','Ausgangsstange','—','—'),
('wire-copper','draw-plate','Ziehwerkzeug','1 Satz','—'),
('wire-copper','charcoal','Zwischenglühen','—','—'),
('copper-ingot','raw-copper-scrap','Rohstoff','—','Kupfererz (Region)'),
('copper-ingot','crucible','Schmelzgefäß','—','—'),
('copper-ingot','furnace-charcoal','Ofen','—','—'),
('furnace-charcoal','charcoal','Brennstoff','—','Koks, Holzgas'),
('furnace-charcoal','raw-clay','Auskleidung','—','—'),
('crucible','raw-clay','Grundstoff','—','Salvage-Graphittiegel'),
('draw-plate','steel-carbon','Werkstoff','—','—'),
('draw-plate','heat-treatment','Härten','—','—'),
('charcoal','raw-wood','Rohstoff','4–5 kg Holz je kg Holzkohle','—'),
-- Kugellager
('ball-bearing','steel-balls-races','Kugeln, Ringe','—','Gleitlager (bearing-plain)'),
('ball-bearing','lathe-scrap','Fertigung Ringe','—','—'),
('steel-balls-races','steel-carbon','Werkstoff','—','—'),
('steel-balls-races','heat-treatment','Härten/Anlassen','—','—'),
('bearing-plain','bronze','Buchse','—','Pockholz, Weißbuche'),
('bronze','copper-ingot','Kupferanteil','90 %','—'),
('lathe-scrap','bearing-plain','Spindellager','—','—'),
('lathe-scrap','steel-carbon','Bett, Spindel, Werkzeuge','—','Salvage-Profile'),
('lathe-scrap','prime-mover','Antrieb','—','Tretkurbel'),
('steel-carbon','raw-iron-scrap','Rohstoff','—','Luppe aufkohlen (Region)'),
('steel-carbon','charcoal','Schmiedefeuer, Aufkohlen','—','—'),
('shaft-machined','steel-carbon','Werkstoff','—','—'),
('shaft-machined','lathe-scrap','Bearbeitung','—','Feile + Lehre'),
-- Blei-Akku
('battery-lead-acid','lead-plate','Elektroden','—','Salvage-Platten'),
('battery-lead-acid','sulfuric-acid','Elektrolyt','1,28 g/cm³, ca. 1 l je 100 Ah-Zelle','Rückgewinnung aus Altakkus'),
('battery-lead-acid','glass-vessel','Gehäuse','—','Salvage-Kunststoffgehäuse'),
('lead-plate','raw-lead','Rohstoff','—','—'),
('sulfuric-acid','raw-sulfur','Rohstoff (Neuherstellung)','—','Altakkusäure'),
('sulfuric-acid','raw-lead','Bleikammer / Eindampfgefäß','—','—'),
-- Funk
('radio-transceiver','capacitor-inductor','Schwingkreis','—','—'),
('radio-transceiver','crystal-detector','Demodulator (Empfang)','—','Salvage-Diode'),
('radio-transceiver','vacuum-tube','Verstärker/Oszillator (Senden)','1–3 Stück','Salvage-Transistor'),
('radio-transceiver','wire-copper','Antenne, Erde','20–40 m','Salvage-Draht, Zaun'),
('radio-transceiver','battery-lead-acid','Stromversorgung Sender','—','Generator, Handkurbel'),
('radio-transceiver','switch-relay','Morsetaste, Sende-Empfangs-Umschaltung','—','—'),
('vacuum-tube','raw-mica-glass','Kolben','—','Salvage-Röhren'),
('vacuum-tube','raw-tungsten-nickel','Faden, Anode','—','Salvage'),
('capacitor-inductor','wire-copper','Spule','—','—'),
('capacitor-inductor','raw-mica-glass','Dielektrikum','—','gewachstes Papier'),
-- Schalter/Relais
('switch-relay','wire-copper','Kontakte (gehämmert)','—','Salvage-Silberkontakte'),
('switch-relay','spring-steel','Kontaktfedern','—','Messingblech'),
('switch-relay','insulator-ceramic-wood','Grundplatte','—','—'),
('switch-relay','relay-coil','Antrieb (Relais)','—','Handbetätigung'),
('relay-coil','copper-wire-insulated','Spule','—','—'),
('relay-coil','raw-iron-scrap','Kern, Anker','—','—'),
('spring-steel','heat-treatment','Anlassen blau','—','—'),
-- SPS-Äquivalent
('plc-equivalent','switch-relay','Logikelemente','10–100 Relais je Anlage','—'),
('plc-equivalent','shaft-machined','Nockenwelle (Ablaufsteuerung)','—','Holzwelle'),
('plc-equivalent','prime-mover','Antrieb Nockenwelle','—','Uhrwerk, Synchronmotor'),
('plc-equivalent','sensor-basic','Eingänge','—','—'),
('plc-equivalent','battery-lead-acid','Steuerspannung 12/24 V','—','—'),
-- Sensoren
('sensor-basic','thermocouple-wire','Temperatur','—','Bimetall, Flüssigkeitsthermometer'),
('sensor-basic','bimetal-bourdon','Temperatur, Druck, Füllstand','—','—'),
('sensor-basic','switch-relay','Grenzwertkontakte','—','—'),
('thermocouple-wire','wire-copper','Kupferschenkel','—','—'),
('thermocouple-wire','raw-iron-scrap','Eisenschenkel','—','Konstantan aus Heizdraht'),
('bimetal-bourdon','bronze','Messingrohr/-streifen','—','Salvage-Manometer'),
('bimetal-bourdon','spring-steel','Stahlstreifen','—','—');

-- ============================================================
-- Prozesse (Beispieleinträge)
-- ============================================================
INSERT INTO process(id,name,produces,inputs,tools,temperature_c,hazards,steps_md,source) VALUES
('p-charcoal-retort','Holzkohle in der Fass-Retorte','charcoal','trockenes Hartholz, 200-l-Fass, kleineres Fass, Rohr','Fass, Blech, Schaufel','400–500 °C','CO-Vergiftung im Freien gering; Brandgefahr; Teerdämpfe',
'1. Kleines Fass mit Holz füllen, Deckel mit Loch, kopfüber in großes Fass.
2. Zwischenraum mit Brennholz füllen, anzünden, Gasaustritt aus dem Loch entzündet sich nach 20–30 min.
3. Wenn die Flamme am Loch erlischt (2–4 h), alles luftdicht abdecken, 12 h abkühlen.
4. Ausbeute 20–25 % Masse, Qualität an klarem Klang der Stücke erkennbar.','FAO Forestry Paper 41'),
('p-copper-melt','Kupfer schmelzen und gießen','copper-ingot','Kupferschrott (entzinnt, ohne Isolierung), Tiegel, Holzkohle, Borax oder Glasbruch als Abdeckung','Schmelzofen, Gebläse, Tiegelzange, Kokille aus Grafit oder gebranntem Sand','1100–1200 °C','Zinkdämpfe bei Messing (Metallrauchfieber), Spritzer, Feuchtigkeit in der Form = Explosion',
'1. Schrott sortenrein trennen, PVC-Isolierung vorher abziehen (Dioxine!).
2. Tiegel langsam vorwärmen, Kupfer zugeben, mit Holzkohle/Glas abdecken gegen Oxidation.
3. Schlacke abziehen, in vorgewärmte, absolut trockene Form gießen.
4. Stange langsam abkühlen lassen, Gussfehler durch Hämmern schließen.','Gingery Bd. 1'),
('p-wire-draw','Kupferdraht ziehen','wire-copper','Kupferstange 8–10 mm, Ziehplatte, Fett/Talg','Zugbank mit Winde oder Hebelzug, Zange, Glühfeuer','Glühen 500–600 °C','Reißen des Drahts unter Zug, Quetschungen',
'1. Stangenende anspitzen, durch das nächstkleinere Loch stecken, mit Zange fassen und ziehen.
2. Je Zug ca. 10–15 % Querschnittsabnahme; Draht wird hart.
3. Nach 3–4 Zügen weichglühen (Kirschrot dunkel, in Wasser abschrecken macht Kupfer weich, nicht hart).
4. Fetten, weiter bis Zieldurchmesser. Kontrolle mit Schieblehre oder Lehre.','Hawkins Bd. 1; Wikipedia Drahtziehen'),
('p-harden-temper','Stahl härten und anlassen','heat-treatment','Kohlenstoffstahl (Funkenprobe: viele verzweigte Funken), Wasser oder Öl','Schmiedefeuer, Zange, Magnet','Härten ca. 780–830 °C (nicht magnetisch), Anlassen 200–320 °C','Verzug, Rissbildung, Ölbrand beim Abschrecken',
'1. Werkstück gleichmäßig erhitzen, bis der Magnet nicht mehr haftet, kurz halten.
2. Senkrecht in Wasser (einfache Stähle) oder Öl (legierte, rissgefährdete) tauchen, bewegen.
3. Blank schleifen, langsam erwärmen und Anlassfarbe beobachten: strohgelb 220 °C Schneidwerkzeug, braun 260 °C Bohrer, violett 280 °C Meißel, blau 300 °C Federn.
4. Bei Farbe sofort abschrecken.','Drew, Farm Blacksmithing; Wikipedia Anlassfarben'),
('p-motor-rewind','Motor neu wickeln (Salvage)','electric-motor','defekter Motor, Lackdraht gleichen Durchmessers, Isolierpapier/Schellack','Wickelschablone, Zähler, Isolationsprüfer oder Glühlampen-Prüfschaltung','Imprägnierung trocknen 80–120 °C','Isolationsfehler = Brand/Stromschlag; Prüfung vor Inbetriebnahme Pflicht',
'1. Alte Wicklung vermessen: Windungszahl je Spule, Drahtdurchmesser, Schaltung (Stern/Dreieck, Polzahl), Nutbelegung skizzieren.
2. Alte Wicklung ausbrennen oder herausschneiden, Nuten reinigen, neu isolieren.
3. Spulen auf Schablone wickeln, einlegen, verschalten nach Skizze.
4. Widerstand aller Stränge gleich? Isolation gegen Gehäuse prüfen. Tränken, trocknen. Probelauf mit Strommessung.','Hawkins Bd. 2; eigenes mech:motor-rewinding'),
('p-lead-acid-cell','Blei-Akku-Zelle aufbauen','battery-lead-acid','Bleigitter, Bleioxid-Paste, Schwefelsäure 1,28 g/cm³, Separator (Holzfurnier, Glasfaser), Gefäß','Gießform, Ladequelle (Generator), Säureheber','Blei gießen 350–400 °C','Blei (nicht essen, waschen, Dämpfe), Säure (Schutzbrille, Sodalösung bereit), Knallgas beim Laden (Lüftung, kein Funken)',
'1. Gitter gießen, Paste (Bleioxid + verdünnte Säure + Wasser) einstreichen, trocknen.
2. Platten wechselweise plus/minus mit Separatoren stapeln, Pole verlöten (Blei-Zinn).
3. Säure einfüllen, 24 h stehen lassen, dann mit kleinem Strom (C/20) 24–48 h formieren.
4. Zellspannung 2,1 V geladen; Säuredichte als Ladeanzeige nutzen.','Wikipedia Bleiakkumulator; Hawkins Bd. 4'),
('p-crystal-radio','Detektorempfänger bauen','radio-transceiver','Spule (60–100 Windungen auf Papprohr), Drehko oder Schiebekontakt, Detektor (Bleiglanz + Nadel oder Germaniumdiode), hochohmiger Kopfhörer, 20–40 m Antennendraht, Erdung','Messer, Lötkolben (optional, Klemmen reichen)','—','Antenne bei Gewitter erden/abklemmen',
'1. Antenne möglichst hoch und lang, Erdung an Wasserrohr oder Erdspieß.
2. Spule mit Abgriffen, Schwingkreis mit Kondensator abstimmen.
3. Detektor in Reihe mit Kopfhörer parallel zum Schwingkreis.
4. Kontaktspitze auf dem Kristall suchen, bis Empfang. Kein Strom nötig.','ARRL Handbook 1928; Wikipedia Detektorempfänger'),
('p-relay-logic','Steuerung als Relaislogik dokumentieren','plc-equivalent','vorhandenes SPS-Programm, Schütze/Relais, Taster, Zeitrelais','Stromlaufplan-Vorlage (mech:schaltzeichen), Klemmenplan','—','Fehlende Verriegelung = Maschinenschaden oder Personengefahr; Not-Halt immer hardwareseitig',
'1. Jeden SPS-Ausgang einem Schütz zuordnen, jeden Eingang einem Kontakt.
2. Programmlogik in Reihenschaltung (UND), Parallelschaltung (ODER), Selbsthaltung (SR), Öffner (NICHT) übersetzen.
3. Zeitfunktionen mit Zeitrelais oder RC-Glied, Zähler mit Schrittschaltwerk.
4. Verriegelungen (Rechts-/Linkslauf, Endlagen) zwingend mit Öffnerkontakten realisieren.
5. Plan ausdrucken und an der Anlage hinterlegen.','Wikipedia Relaislogik; eigenes mech:relaislogik'),
('p-thermocouple','Thermoelement herstellen und kalibrieren','sensor-basic','Eisendraht, Konstantandraht (Heizdraht) oder Kupferdraht, Salvage-Multimeter (mV) oder Drehspulinstrument','Zange, Lötlampe oder Schmiedefeuer zum Verschweißen','Verschweißen der Messstelle > 1000 °C','—',
'1. Zwei Drähte an einem Ende verdrillen und im Feuer/mit Lichtbogen (12-V-Batterie, Kohlestift) verschweißen.
2. Freie Enden an Messgerät; Vergleichsstelle bei bekannter Temperatur.
3. Kalibrieren: Eiswasser 0 °C, siedendes Wasser 100 °C (bei Normaldruck), ggf. Schmelzpunkt Blei 327 °C.
4. Kennlinie in SQLite-Tabelle rtd_table/tc_table eintragen; Typ-J-Tabelle aus NIST als Vergleich.','NIST ITS-90; Wikipedia Thermoelement');

-- Prozess-Skala aus der erzeugten Technologie übernehmen
UPDATE process SET scale = (SELECT min_viable_scale FROM tech WHERE tech.id = process.produces);

-- FTS-Indizes füllen
INSERT INTO tech_fts(tech_fts) VALUES('rebuild');
INSERT INTO process_fts(process_fts) VALUES('rebuild');

-- ============================================================
-- Nützliche Sichten
-- ============================================================
-- Vollständiger Baum (rekursiv) für eine Technologie:
--   SELECT * FROM v_tree WHERE root='electric-motor';
CREATE VIEW IF NOT EXISTS v_tree AS
WITH RECURSIVE tree(root, tech_id, input_id, depth, path) AS (
  SELECT t.id, t.id, ti.input_id, 1, t.id || ' > ' || ti.input_id
    FROM tech t JOIN tech_input ti ON ti.tech_id = t.id
  UNION ALL
  SELECT tree.root, ti.tech_id, ti.input_id, tree.depth + 1, tree.path || ' > ' || ti.input_id
    FROM tree JOIN tech_input ti ON ti.tech_id = tree.input_id
   WHERE tree.depth < 12 AND instr(tree.path, ti.input_id) = 0
)
SELECT tree.root, tree.depth, tree.input_id, tree.path, i.name AS input_name, i.min_viable_scale, i.category
  FROM tree JOIN tech i ON i.id = tree.input_id;

-- Engpässe: welche Eingänge werden von den meisten Kerntechnologien gebraucht?
CREATE VIEW IF NOT EXISTS v_bottlenecks AS
SELECT input_id, i.name, i.min_viable_scale, COUNT(DISTINCT root) AS used_by_roots
  FROM v_tree JOIN tech i ON i.id = v_tree.input_id
 WHERE root IN ('electric-motor','generator','transformer','copper-wire-insulated','ball-bearing',
                'battery-lead-acid','radio-transceiver','switch-relay','plc-equivalent','sensor-basic')
 GROUP BY input_id ORDER BY used_by_roots DESC, i.min_viable_scale;

-- Alles, was nur Salvage ist (Lagerhaltungs-Prioritäten):
CREATE VIEW IF NOT EXISTS v_salvage_only AS
SELECT id, name, category, salvage_lifetime, xref FROM tech WHERE min_viable_scale = 'Salvage';
