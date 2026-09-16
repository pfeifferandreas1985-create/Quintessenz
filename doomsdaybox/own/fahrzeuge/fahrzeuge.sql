-- fahrzeuge.sql – Fahrzeugakten für die DoomsdayBox
-- Fahrzeuge: Land Rover Defender 110 TD5 · Rover Mini Cooper 1.3i MPi „British Open Classic“ (1999) · Vespa V50 (1963, V5A1T)
-- Aufbau: python build.py   (erzeugt fahrzeuge.db und Fahrzeugakte_*.md)
--
-- WICHTIG: verified = 0 bedeutet „aus dem Gedächtnis eingetragen, gegen Werkstatthandbuch / Teilekatalog prüfen“.
--          Erst nach Prüfung am Fahrzeug bzw. im Originalhandbuch auf 1 setzen und Quelle eintragen.
--          Teilenummern immer mit Fahrgestellnummer im Katalog gegenprüfen (Bauzeitraum-Abhängigkeit).

PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS vehicle (
  id TEXT PRIMARY KEY, name TEXT, model_code TEXT, year TEXT, engine TEXT,
  vin TEXT, engine_no TEXT, plate TEXT, notes TEXT
);
CREATE TABLE IF NOT EXISTS spec (          -- Kenndaten, Füllmengen, Drehmomente, Einstellwerte
  vehicle_id TEXT REFERENCES vehicle(id), category TEXT, key TEXT, value TEXT, unit TEXT,
  source TEXT, verified INTEGER DEFAULT 0, PRIMARY KEY (vehicle_id, category, key)
);
CREATE TABLE IF NOT EXISTS part (          -- Stückliste Verschleiß- und Ersatzteile
  vehicle_id TEXT REFERENCES vehicle(id), grp TEXT, name TEXT, oem_no TEXT, alt_no TEXT,
  qty TEXT, interval TEXT, supplier TEXT, stock INTEGER DEFAULT 0, source TEXT, verified INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS issue (         -- bekannte Schwachstellen und Fehlerbilder
  vehicle_id TEXT REFERENCES vehicle(id), symptom TEXT, cause TEXT, fix TEXT, severity TEXT, source TEXT
);
CREATE TABLE IF NOT EXISTS doc (           -- Dokumente: Handbücher, Kataloge, Zeichnungen
  vehicle_id TEXT REFERENCES vehicle(id), title TEXT, kind TEXT, publisher TEXT, license TEXT,
  where_to_get TEXT, local_path TEXT, priority INTEGER
);
CREATE TABLE IF NOT EXISTS maintenance (   -- Wartungsplan
  vehicle_id TEXT REFERENCES vehicle(id), task TEXT, interval_km TEXT, interval_time TEXT, notes TEXT, source TEXT, verified INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS logbook (       -- eigene Historie
  vehicle_id TEXT REFERENCES vehicle(id), date TEXT, km INTEGER, work TEXT, parts_used TEXT, cost_eur REAL, notes TEXT
);

-- ============================================================ Fahrzeuge
INSERT OR REPLACE INTO vehicle VALUES
('defender','Land Rover Defender 110 TD5','L316 (Defender 110), Motor 10P (bis MJ 2001) / 15P (ab MJ 2002)','1998–2006','2,5 l Fünfzylinder Turbodiesel, Direkteinspritzung, elektronisch (Motorsteuergerät), 90 kW / 122 PS, 300 Nm',NULL,NULL,NULL,'Fahrgestellnummer eintragen; 10P oder 15P am Motor prüfen (15P: Motorsteuergerät MSB, geändertes Ladeluft-/AGR-System). Getriebe R380, Verteilergetriebe LT230, Hinterachse Salisbury (110 bis ca. 2002) oder Land-Rover-Achse.'),
('mini','Rover Mini Cooper 1.3i MPi „British Open Classic“','Rover Mini (ADO20), Sondermodell British Open Classic 1998/99, Twin-Point-Einspritzung (MEMS 2J)','1999','A-Serie 1275 cm³, Mehrpunkt-Einspritzung, ca. 46 kW / 63 PS, Motor und Getriebe mit gemeinsamem Ölhaushalt',NULL,NULL,NULL,'Sondermodell mit elektrischem Faltschiebedach über die volle Länge, British Racing Green. Rahmennummer (SAXX…) und Motornummer eintragen. Bauzeit exakt festhalten, Teilekataloge unterscheiden SPi (1991–96) und MPi (1997–2000).'),
('vespa','Vespa V50 (V50 N)','V5A1T (Rahmen), V5A1M (Motor)','1963','49,8 cm³ Einzylinder-Zweitakter, Bohrung 38,4 mm, Hub 43 mm, ca. 1,5 PS, 3-Gang-Handschaltung, 6-V-Magnetzündung mit Unterbrecher',NULL,NULL,NULL,'Erstes Baujahr der V50. Rahmennummer V5A1T* und Motornummer V5A1M* eintragen; Vergaser- und Zündungsvarianten der ersten Serien im Ersatzteilkatalog prüfen. Wahrscheinlich im Laufe der Jahre Teile späterer Baujahre verbaut.');

-- ============================================================ Kenndaten (verified=0: prüfen!)
INSERT OR REPLACE INTO spec VALUES
-- Defender
('defender','Füllmenge','Motoröl mit Filter','ca. 7,2','l','Werkstatthandbuch TD5; Spezifikation ACEA B3/A3, 5W-40 oder 10W-40 teilsynthetisch',0),
('defender','Füllmenge','Kühlmittel','ca. 11','l','Werkstatthandbuch; OAT-Kühlmittel (orange), nicht mit blauem mischen',0),
('defender','Füllmenge','Schaltgetriebe R380','ca. 2,4','l','MTF 94 (Texaco) oder gleichwertig; kein normales GL5-Getriebeöl',0),
('defender','Füllmenge','Verteilergetriebe LT230','ca. 2,3','l','EP 80W-90 GL4/GL5',0),
('defender','Füllmenge','Vorderachse','ca. 1,7','l','EP 90 GL5',0),
('defender','Füllmenge','Hinterachse Salisbury','ca. 2,3','l','EP 90 GL5; Land-Rover-Achse ca. 1,7 l',0),
('defender','Füllmenge','Schwenklager (Achsschenkel) je Seite','ca. 0,33','l','One-Shot-Fett (Halbflüssigfett) bei Schwenklagern ab 1994, sonst EP 90',0),
('defender','Füllmenge','Servolenkung','ca. 2,9','l','ATF Dexron II/III',0),
('defender','Füllmenge','Kraftstofftank','ca. 75','l','110 Station Wagon; Reserveanzeige ab ca. 9 l',0),
('defender','Drehmoment','Radmuttern','130','Nm','Werkstatthandbuch; Alu- und Stahlfelgen unterschiedlich, prüfen',0),
('defender','Drehmoment','Ölablassschraube Motor','ca. 35','Nm','',0),
('defender','Reifen','Dimension Standard','235/85 R16 oder 7.50 R16','','Reifendruck laut Türaufkleber, grob 1,9 vorn / 2,6 hinten bei Beladung; leer 1,9/2,0',0),
('defender','Elektrik','Bordspannung / Batterie','12 V, ca. 90–110 Ah, Pluspol-Trennung beachten','','',0),
('defender','Elektrik','Diagnose','OBD-Stecker im Fußraum Beifahrer/Fahrer; TD5 braucht Land-Rover-spezifisches Gerät (Nanocom Evolution, Hawkeye) für Fehlerspeicher und Injektor-Codes','','Nach Injektortausch müssen die 5 Injektor-Codes eingelesen werden',0),
('defender','Motor','Ventilspiel','hydraulisch, keine Einstellung','','',1),
('defender','Motor','Zündfolge / Zylinder','1-2-4-5-3','','Fünfzylinder, Zylinder 1 vorn',0),
('defender','Motor','Kraftstoffdruck','ca. 4 bar (Vorförderpumpe im Tank, Druckregler am Zylinderkopf)','bar','Fehlerbild niedriger Druck = Leistungsverlust warm',0),
-- Mini
('mini','Füllmenge','Motor-/Getriebeöl mit Filter','ca. 4,8','l','Gemeinsamer Ölsumpf. 20W-50 mineralisch (klassische A-Serie) mit ZDDP-Anteil; kein Leichtlauföl',0),
('mini','Füllmenge','Kühlmittel','ca. 3,5','l','Frontkühler mit Elektrolüfter (MPi), Glykol 50 %',0),
('mini','Füllmenge','Kraftstofftank','ca. 34','l','',0),
('mini','Füllmenge','Bremsflüssigkeit','DOT 4','','Bremse vorn Scheibe, hinten Trommel; Wechsel alle 2 Jahre',1),
('mini','Drehmoment','Radmuttern','ca. 60','Nm','Werkstatthandbuch prüfen (Angabe je nach Felge 42–48 lbf·ft)',0),
('mini','Drehmoment','Antriebswellenmutter (Nabe)','ca. 200','Nm','Werkstatthandbuch prüfen; neue Splinte',0),
('mini','Drehmoment','Ölablassschraube','ca. 35','Nm','',0),
('mini','Zündung','Zündkerzen','NGK BPR6ES oder Champion RN9YC, Abstand 0,9 mm','','MPi: elektronische Zündung ohne Verteiler, Zündzeitpunkt wird vom Steuergerät geregelt, nicht einstellbar',0),
('mini','Reifen','Dimension','145/70 R12 (Standard) oder 175/50 R13 (Sportpack)','','Druck ca. 1,9 bar rundum, Türaufkleber prüfen',0),
('mini','Fahrwerk','Federung','Gummikonusfedern (trocken), einstellbare Federbeine (Hi-Lo) nachrüstbar','','Bodenfreiheit / Höhe hinten und vorn messen, Konen setzen sich',1),
('mini','Fahrwerk','Spur vorn','ca. 1,5 mm Nachspur (toe-out)','mm','Werkstatthandbuch prüfen',0),
('mini','Elektrik','Diagnose','MEMS 2J Steuergerät; Diagnose über Rover-Testbook oder MEMS-Reader (z. B. „Mini MEMS Diag“-Kabel); Blinkcode nicht vorhanden','','',0),
-- Vespa
('vespa','Füllmenge','Getriebeöl','ca. 250','ml','SAE 30 Einbereichsöl oder 80W GL4; Ablass unten am Motor, Einfüll-/Kontrollschraube seitlich',0),
('vespa','Füllmenge','Kraftstoff','Gemisch 1:50 mit modernem Zweitaktöl (JASO FC/FD); original 2 %','','Tank ca. 5,2 l inkl. Reserve, Reservehahn',0),
('vespa','Zündung','Zündkerze','Bosch W5AC oder NGK B7HS, Elektrodenabstand 0,5–0,6 mm','','',0),
('vespa','Zündung','Unterbrecherabstand','0,35–0,45','mm','Zündzeitpunkt ca. 27° vor OT (bei Unterbrecherzündung), Markierung am Polrad / Gehäuse prüfen; Kondensator häufigste Fehlerquelle',0),
('vespa','Zündung','Bordnetz','6 V Wechselstrom, Magnetzündung, kein Akku','','Glühlampen 6 V; Lichtmaschine ca. 20–30 W',0),
('vespa','Vergaser','Typ','Dell''Orto SHB 16/10 (V50 N)','','Hauptdüse ca. 50–55, Leerlaufdüse ca. 38; Leerlaufluftschraube ca. 2 Umdrehungen offen; Werte prüfen',0),
('vespa','Reifen','Dimension','2.75-9 (1963), spätere Modelle 3.00-10','','Druck ca. 1,25 bar vorn / 1,75 bar hinten (Solo)',0),
('vespa','Motor','Kolbenspiel / Verdichtung','Zylinder Grauguss, Kolben mit 2 Ringen; Kompression ca. 8–9 bar','','Bohrung 38,4 mm, Übermaßkolben 38,6 / 38,8 / 39,0 erhältlich',0),
('vespa','Drehmoment','Polradmutter','ca. 40','Nm','Werkstatthandbuch prüfen',0),
('vespa','Drehmoment','Kupplungsmutter','ca. 45','Nm','Werkstatthandbuch prüfen; Sicherungsblech',0),
('vespa','Drehmoment','Radmuttern','ca. 25','Nm','Geteilte Felge: Reifen nur bei entlüftetem Schlauch trennen',0);

-- ============================================================ Stückliste / Verschleißteile (verified=0: Teilenummer im Katalog mit Fahrgestellnummer prüfen)
INSERT INTO part (vehicle_id,grp,name,oem_no,alt_no,qty,interval,supplier,source,verified) VALUES
-- Defender TD5
('defender','Motor','Ölfilter','LPX100590','Mann W 930/26','1','12.000 km / 12 Monate','Britpart, Bearmach, Paddock, Famous Four','Katalog prüfen',0),
('defender','Motor','Zentrifugal-Ölfilterrotor','ERR6299','','1','36.000 km','','Katalog prüfen',0),
('defender','Motor','Kraftstofffilter','ESR4686','','1','24.000 km / 24 Monate','','Katalog prüfen',0),
('defender','Motor','Luftfilter','ESR4238','','1','24.000 km, staubig öfter','','Katalog prüfen',0),
('defender','Motor','Injektor-Kabelbaum (Ölmigration)','AMR6103','','1','bei Öl im Steuergerätestecker','','Katalog prüfen',0),
('defender','Motor','Injektor-Dichtscheiben Kupfer','ERR7004','','5','bei jedem Injektor-Ausbau','','Katalog prüfen',0),
('defender','Motor','Kurbelwellen-Positionssensor','ERR7354','','1','bei Bedarf (Motor geht warm aus)','','Katalog prüfen',0),
('defender','Motor','Keilrippenriemen','ERR6896','','1','60.000 km','','Katalog prüfen',0),
('defender','Motor','Thermostat','PEL500110','','1','bei Bedarf','','Katalog prüfen',0),
('defender','Kühlung','Kühlmittel OAT','STC50529 (Texaco XLC)','','11 l','5 Jahre','','',0),
('defender','Bremse','Bremsbeläge vorn','SFP500190','','1 Satz','Verschleiß','','Katalog prüfen, abhängig von Bremssattel-Typ',0),
('defender','Bremse','Bremsbeläge hinten','SFP500200','','1 Satz','Verschleiß','','Katalog prüfen',0),
('defender','Bremse','Bremsscheibe vorn belüftet','FTC1381','','2','Verschleiß','','Katalog prüfen',0),
('defender','Fahrwerk','Radlager vorn Satz','RTC3429','','2','bei Spiel; einstellbar','','Katalog prüfen',0),
('defender','Fahrwerk','Schwenklager-Dichtung (Achsschenkel)','FTC3401','','2','bei Ölaustritt','','Katalog prüfen',0),
('defender','Fahrwerk','Achsschenkel-Kugel (Swivel Ball)','FTC3179 / FTC3180','','2','bei Korrosionsnarben','','Katalog prüfen',0),
('defender','Antrieb','Kupplungssatz','STC8358','','1','Verschleiß','','Katalog prüfen',0),
('defender','Antrieb','Kupplungsnehmerzylinder','FTC5072','','1','bei Bedarf (häufig)','','Katalog prüfen',0),
('defender','Antrieb','Kreuzgelenk Kardanwelle','RTC3346','','4','Schmieren alle 12.000 km, Wechsel bei Spiel','','Katalog prüfen',0),
('defender','Elektrik','Glühkerzen','ERR6066','','5','bei Kaltstartproblemen','','Katalog prüfen',0),
('defender','Elektrik','Luftmassenmesser','MHK100620','','1','bei Bedarf (Ruckeln, Rauch)','','Katalog prüfen',0),
('defender','Karosserie','Hinterer Querträger (Rahmen)','','diverse Anbieter (Marsland, Richards)','1','bei Durchrostung','','',0),
-- Mini MPi
('mini','Motor','Ölfilter','GFE443','Mann W 920/21 (prüfen)','1','5.000–10.000 km / 12 Monate','Mini Spares, Mini Sport, Somerford, Rimmer Bros','Katalog prüfen',0),
('mini','Motor','Luftfiltereinsatz MPi','WJN101780','','1','20.000 km','','Katalog prüfen',0),
('mini','Motor','Kraftstofffilter (Leitung)','WJN101190','','1','20.000 km','','Katalog prüfen',0),
('mini','Motor','Zündkerzen','NGK BPR6ES','Champion RN9YC','4','10.000 km','','',0),
('mini','Motor','Zündkabel-Satz MPi','NGC10054','','1','bei Bedarf','','Katalog prüfen',0),
('mini','Motor','Kurbelwellensensor MPi','NSC100760','','1','bei Bedarf (Motor geht aus)','','Katalog prüfen',0),
('mini','Motor','Leerlaufsteller (Schrittmotor)','MHB000010','','1','bei Bedarf','','Katalog prüfen',0),
('mini','Motor','Lambdasonde','MHK100840','','1','bei Bedarf','','Katalog prüfen',0),
('mini','Motor','Wasserpumpe','GWP134','','1','bei Bedarf','','Katalog prüfen',0),
('mini','Motor','Keilriemen','GCB10813','','1','40.000 km','','Katalog prüfen',0),
('mini','Motor','Thermostat 88 °C','GTS102','','1','bei Bedarf','','Katalog prüfen',0),
('mini','Motor','Ventildeckeldichtung','12A1139','','1','bei Ölverlust','','Katalog prüfen',0),
('mini','Antrieb','Kupplungssatz (Verto)','GCK151AF','','1','Verschleiß','','Katalog prüfen',0),
('mini','Antrieb','Antriebswellengelenk innen (Pot Joint)','GCV1105','','2','bei Spiel','','Katalog prüfen',0),
('mini','Antrieb','Antriebswellengelenk außen (CV)','GCV1104','','2','bei Knacken','','Katalog prüfen',0),
('mini','Antrieb','Faltenbalg Antriebswelle','GCV1110','','2','bei Riss','','Katalog prüfen',0),
('mini','Bremse','Bremsbeläge vorn 8,4 Zoll','GBP281','','1 Satz','Verschleiß','','Katalog prüfen',0),
('mini','Bremse','Bremsbacken hinten','GBS834','','1 Satz','Verschleiß','','Katalog prüfen',0),
('mini','Bremse','Bremsscheibe vorn 8,4 Zoll','GBD139','','2','Verschleiß','','Katalog prüfen',0),
('mini','Fahrwerk','Gummikonusfeder','FAM3968','','4','bei Setzen (Höhe)','','Katalog prüfen',0),
('mini','Fahrwerk','Kugelgelenk-Satz oben/unten','GSJ166','','2','bei Spiel; einstellbar mit Passscheiben','','Katalog prüfen',0),
('mini','Fahrwerk','Radlagersatz vorn','GHK1548','','2','bei Spiel','','Katalog prüfen',0),
('mini','Karosserie','Schweller außen','14A7194','','2','bei Durchrostung','','Katalog prüfen',0),
('mini','Karosserie','Hinterer Hilfsrahmen','KGB10021','','1','bei Durchrostung; Sicherheitsrelevant','','Katalog prüfen',0),
-- Vespa V50
('vespa','Motor','Zündkerze','Bosch W5AC','NGK B7HS','1','5.000 km','SIP, Scooter Center, Vespa-Händler','',0),
('vespa','Motor','Unterbrecher','','SIP/Piaggio-Nachbau','1','10.000 km','','Katalog prüfen (Zündungsausführung 1963)',0),
('vespa','Motor','Kondensator','','','1','bei Zündaussetzern','','Katalog prüfen',0),
('vespa','Motor','Kolben Standard 38,4 mm mit Ringen','','Übermaß 38,6 / 38,8 / 39,0','1','bei Verschleiß','','Katalog prüfen',0),
('vespa','Motor','Kolbenringe','','','2','bei Kompressionsverlust','','',0),
('vespa','Motor','Dichtsatz Motor komplett','','','1','bei Motorrevision','','',0),
('vespa','Motor','Simmerring Kurbelwelle kupplungsseitig','','','1','bei Ölaustritt','','Katalog prüfen',0),
('vespa','Motor','Simmerring Kurbelwelle lichtmaschinenseitig','','','1','bei Falschluft / Zündungsöl','','Katalog prüfen',0),
('vespa','Motor','Kurbelwellenlager','','','2','bei Motorrevision','','',0),
('vespa','Motor','Ansaugstutzen-Dichtung','','','1','bei Falschluft','','',0),
('vespa','Vergaser','Hauptdüse / Leerlaufdüse SHB 16/10','','Dell''Orto Original','je 1','bei Bedarf','','Bedüsung prüfen',0),
('vespa','Vergaser','Vergaserdichtsatz SHB','','','1','bei Revision','','',0),
('vespa','Antrieb','Kupplungsbeläge (Kork) 3 Scheiben','','','1 Satz','bei Rutschen','','Ausführung 1963 prüfen',0),
('vespa','Antrieb','Schaltkreuz','','','1','bei Gangspringen','','',0),
('vespa','Antrieb','Kupplungszug / Schaltzüge / Gaszug / Bremszug','','Satz Bowdenzüge komplett','1 Satz','bei Bedarf; Reserve mitführen','','',0),
('vespa','Fahrwerk','Reifen 2.75-9 (oder 3.00-10 mit Felge)','','','2 + Ersatzrad','Verschleiß / Alter > 6 Jahre','','',0),
('vespa','Fahrwerk','Schlauch 2.75-9','','','2','','','',0),
('vespa','Fahrwerk','Bremsbacken vorn / hinten','','','je 1 Satz','Verschleiß','','Trommeldurchmesser prüfen',0),
('vespa','Fahrwerk','Lenkkopflager Satz','','','1','bei Spiel','','',0),
('vespa','Fahrwerk','Schwingenlager (Silentblöcke) Motor','','','1 Satz','bei Riss','','',0),
('vespa','Elektrik','Glühlampen 6 V (Scheinwerfer, Rücklicht, Tacho)','','','Satz','Reserve mitführen','','Sockel prüfen',0),
('vespa','Elektrik','Kabelbaum komplett','','','1','bei Brüchen','','Nachfertigung für V50 N erhältlich',0);

-- ============================================================ Bekannte Schwachstellen
INSERT INTO issue VALUES
('defender','Motor geht warm aus / startet nicht mehr, Fehler Kurbelwellensensor','Kurbelwellen-Positionssensor defekt oder Öl im Motorkabelbaum','Sensor tauschen; roten Steuergerätestecker auf Öl prüfen, Kabelbaum AMR6103 tauschen, Steuergerätestecker reinigen','hoch','TD5-Foren, Werkstattpraxis'),
('defender','Leistungsverlust warm, Ruckeln, Rauch','Kraftstoffdruckregler, Luftmassenmesser, Ladeluftschlauch, verstopfter Kraftstofffilter','Kraftstoffdruck messen (Regler am Kopf), Luftmassenmesser abstecken zum Test, Schläuche prüfen','mittel',''),
('defender','Diesel im Motoröl (Ölstand steigt, riecht nach Diesel)','Injektor-Kupferdichtscheiben undicht','Injektoren aus- und mit neuen Scheiben einbauen, Codes einlesen','hoch',''),
('defender','Kühlmittelverlust ohne sichtbares Leck, weißer Rauch','Zylinderkopfriss zwischen Ventilen (Überhitzung), Kopfdichtung','Kopf prüfen; Ursache Kühlung (Viskolüfter, Thermostat, Kühler) beheben','hoch',''),
('defender','Ölpumpenschraube löst sich, Öldruck weg','Bekannte TD5-Schwachstelle: Schraube Ölpumpen-Antriebsrad','Vorsorglich Schraube mit Schraubensicherung erneuern (Stirndeckel ab)','hoch','TD5-Foren'),
('defender','Kupplung lässt sich nicht trennen','Kupplungsnehmerzylinder undicht','Zylinder tauschen, entlüften','mittel',''),
('defender','Rost: Rahmen hinten (Querträger, Ausleger), Stirnwand Fußräume, Türböden, Schweller','Konstruktion, Alu-Stahl-Kontaktkorrosion','Regelmäßig reinigen, Hohlraumkonservierung, Querträger schweißen lassen','hoch',''),
('defender','Lenkung schwammig, Radlager Spiel','Radlager einstellbar, Schwenklager Vorspannung, Panhardstab-Buchsen','Radlager nach Handbuch einstellen (Vorspannung), Buchsen erneuern','mittel',''),
('defender','Ölaustritt Achsschenkel','Schwenklagerdichtung, Kugeloberfläche narbig','Dichtung erneuern, bei Narben Kugel tauschen','niedrig',''),
('mini','Motor geht aus / startet nicht, kein Fehlerbild','Kurbelwellensensor, MEMS-Steuergerät, Masseverbindungen','Sensor prüfen, Massepunkte reinigen, Steuergerät auf Feuchtigkeit prüfen','hoch',''),
('mini','Unruhiger Leerlauf, geht im Stand aus','Leerlaufsteller (Schrittmotor), Drosselklappenpoti, Falschluft','Steller reinigen/tauschen, Schläuche prüfen','mittel',''),
('mini','Ölverlust an Kupplungsgehäuse / Primärantrieb','Simmerring Primärantrieb, Kupplungsgehäusedichtung','Gehäuse ab, Simmerring erneuern','mittel',''),
('mini','Klacken beim Einlenken unter Last','Äußeres Antriebswellengelenk','Gelenk tauschen','mittel',''),
('mini','Fahrzeug hängt hinten/vorn tief, hart','Gummikonusfedern gesetzt','Konen tauschen oder Hi-Lo-Federbeine','niedrig',''),
('mini','Rost: Schweller, A-Säulen, Kofferraumboden, Türunterkanten, Frontschürze, hinterer Hilfsrahmen','Konstruktion, Feuchtigkeit','Hilfsrahmen ist sicherheitsrelevant (TÜV), rechtzeitig tauschen; Hohlraumschutz','hoch',''),
('mini','Kühlerlüfter läuft nicht, Motor wird heiß','Lüfterthermoschalter, Relais, Lüftermotor (Frontkühler MPi)','Schalter brücken zum Test, Relais tauschen','hoch',''),
('mini','Kugelgelenke Spiel, Lenkung schlägt','Kugelgelenke oben/unten verschlissen','Tauschen und mit Passscheiben einstellen (Handbuch)','mittel',''),
('vespa','Springt schlecht an, Zündaussetzer warm','Kondensator, Unterbrecher, Zündspule, Polradmagnet schwach','Kondensator tauschen (erste Maßnahme), Unterbrecherabstand, Zündzeitpunkt prüfen','hoch',''),
('vespa','Dreht im Leerlauf hoch, geht aus, Kolben frisst','Falschluft (Ansaugstutzen, Simmerring lichtmaschinenseitig, Vergaserflansch), zu magere Bedüsung','Dichtungen erneuern, Bedüsung prüfen, Startgas-Test mit Bremsenreiniger','hoch',''),
('vespa','Öl am Motor unten, Getriebeöl schwindet','Simmerring Kurbelwelle kupplungsseitig, Ablassschraube','Simmerring erneuern','mittel',''),
('vespa','Gang springt raus, lässt sich schwer schalten','Schaltkreuz verschlissen, Schaltzüge verstellt','Züge einstellen, Schaltkreuz tauschen (Motor teilen)','mittel',''),
('vespa','Kupplung rutscht oder trennt nicht','Korkbeläge verschlissen, Öl falsch, Zug','Beläge tauschen, SAE 30, Zug einstellen','mittel',''),
('vespa','Licht flackert / Lampen brennen durch','6-V-Wechselstromnetz, Masse, Spannungsregler fehlt (original nicht vorhanden)','Massepunkte, Kabelbaum prüfen; Lampen mit korrekter Wattzahl','niedrig',''),
('vespa','Rost: Trittbrett, Beinschild unten, Unterboden, Rahmentunnel','Alter','Rahmen innen mit Wachs konservieren, Ablauflöcher frei halten','mittel',''),
('vespa','Lenkung hakt, Spiel','Lenkkopflager, Schwinge','Lager tauschen, fetten','mittel','');

-- ============================================================ Dokumente (Beschaffung)
INSERT INTO doc VALUES
('defender','Defender Workshop Manual TD5 (MJ 1999–2006, LRL0410 / LRL0097) + Electrical Library','Werkstatthandbuch + Schaltpläne','Land Rover / Brooklands Books (Nachdruck)','kommerziell (ca. 40–60 €); Original-PDFs urheberrechtlich, nur gekauft oder Privatkopie','Brooklands Books, Amazon, Land-Rover-Teilehändler','pdf/fahrzeuge/defender/',1),
('defender','Defender Parts Catalogue 1987–2006 (STC9021CC) mit Explosionszeichnungen','Ersatzteilkatalog','Land Rover / Brooklands Books','kommerziell (ca. 50 €)','Brooklands Books','pdf/fahrzeuge/defender/',1),
('defender','Online-Teilekatalog mit Explosionszeichnungen (lrcat.com, Britpart, Bearmach, Paddock Spares, Famous Four, Rimmer Bros)','Explosionszeichnungen online','diverse Händler','frei einsehbar, Speicherung nur Privatkopie','Websites; relevante Baugruppen als PDF drucken oder per zimit sichern','pdf/fahrzeuge/defender/explosionszeichnungen/',1),
('defender','Haynes 3017 Land Rover Defender Diesel 1983–2007','Reparaturanleitung','Haynes','kommerziell (ca. 30 €)','Buchhandel','pdf/fahrzeuge/defender/',2),
('defender','Nanocom Evolution Handbuch TD5','Diagnosegerät-Doku','Blackbox Solutions','frei (Herst.)','nanocom-diagnostics.com','pdf/fahrzeuge/defender/',1),
('defender','TD5-Wissen aus Foren (landyzone.co.uk, lr4x4.com, defender-forum.de, landyforum.de)','Praxiswissen','Community','urheberrechtlich, Privatkopie einzelner Threads','gezielt Threads zu Ölpumpenschraube, Injektorkabelbaum, Kopfriss sichern','own/fahrzeuge/defender_forenwissen.md',2),
('mini','Rover Mini Workshop Manual 1992–2000 inkl. MPi-Nachtrag (RCL 0193 / AKM 7169)','Werkstatthandbuch + Schaltpläne','Rover / Brooklands Books (Nachdruck)','kommerziell (ca. 40–60 €)','Brooklands Books, Mini Spares','pdf/fahrzeuge/mini/',1),
('mini','Mini Parts Catalogue 1990–2000 (Rover, mit Explosionszeichnungen)','Ersatzteilkatalog','Rover / British Motor Heritage','kommerziell / Nachdruck','Mini Spares, Somerford Mini, BMIHT-Archiv','pdf/fahrzeuge/mini/',1),
('mini','Mini Spares Online-Katalog (minispares.com) mit Explosionszeichnungen je Baugruppe und Teilenummern','Explosionszeichnungen online','Mini Spares Centre','frei einsehbar, Speicherung nur Privatkopie','Website, Baugruppen als PDF sichern','pdf/fahrzeuge/mini/explosionszeichnungen/',1),
('mini','Haynes 0646 Mini 1969–2001','Reparaturanleitung','Haynes','kommerziell (ca. 30 €)','Buchhandel','pdf/fahrzeuge/mini/',2),
('mini','MPi-spezifisches Wissen: MEMS 2J, Schaltplan MPi 1997–2000','Praxiswissen, Schaltplan','Community (theminiforum.co.uk, mini-forum.de, minimania.com Tech Articles)','urheberrechtlich, Privatkopie','gezielt sichern','own/fahrzeuge/mini_forenwissen.md',2),
('vespa','Vespa 50 (V5A1T) – Anleitung für die Werkstatt / Officina (Piaggio, 1960er)','Werkstatthandbuch','Piaggio','urheberrechtlich, Scans frei zugänglich (scooterhelp.com) – Privatkopie','scooterhelp.com „Manuals“, vespa-archiv','pdf/fahrzeuge/vespa/',1),
('vespa','Catalogo parti di ricambio Vespa 50 V5A1T (Original-Ersatzteilkatalog mit Explosionszeichnungen und Piaggio-Nummern)','Ersatzteilkatalog','Piaggio','wie oben','scooterhelp.com „Parts Books“','pdf/fahrzeuge/vespa/',1),
('vespa','SIP Scootershop / Scooter Center: Explosionszeichnungen Vespa V50 N je Baugruppe mit aktuellen Teilenummern','Explosionszeichnungen online','SIP, Scooter Center','frei einsehbar, Speicherung nur Privatkopie','sip-scootershop.com, scooter-center.com; jede Baugruppe als PDF sichern','pdf/fahrzeuge/vespa/explosionszeichnungen/',1),
('vespa','Bedienungsanleitung Vespa 50 (1963)','Betriebsanleitung','Piaggio','Scan frei zugänglich, Privatkopie','scooterhelp.com','pdf/fahrzeuge/vespa/',2),
('vespa','Bucheli Reparaturanleitung Vespa 50/90/125 Smallframe','Reparaturanleitung','Bucheli Verlag','kommerziell (ca. 30 €)','Buchhandel','pdf/fahrzeuge/vespa/',2),
('vespa','Vespa Technica Bd. 3 (Smallframe) ','Referenz, Restaurierung','Vespa Technica','kommerziell','Buchhandel','pdf/fahrzeuge/vespa/',3),
('vespa','GSF-Wiki (germanscooterforum.de), vespaforum.de, Smallframe-Wissen','Praxiswissen','Community','urheberrechtlich, Privatkopie einzelner Artikel','gezielt sichern: Zündung einstellen, Motor teilen, Falschluft','own/fahrzeuge/vespa_forenwissen.md',2);

-- ============================================================ Wartungsplan (verified=0: Intervalle mit Handbuch abgleichen)
INSERT INTO maintenance VALUES
('defender','Motoröl + Filter wechseln','12.000','12 Monate','ACEA B3 5W-40/10W-40; Zentrifugalrotor alle 3. Wechsel','Handbuch prüfen',0),
('defender','Kraftstofffilter wechseln','24.000','24 Monate','Wasser ablassen jährlich','',0),
('defender','Luftfilter wechseln','24.000','','staubig: jährlich','',0),
('defender','Getriebe-, Verteilergetriebe-, Achsöle wechseln','60.000','','R380 nur MTF 94','',0),
('defender','Kardanwellen-Kreuzgelenke abschmieren','12.000','12 Monate','auch Schiebestücke','',1),
('defender','Bremsflüssigkeit wechseln','','24 Monate','DOT 4','',1),
('defender','Kühlmittel wechseln','','5 Jahre','OAT','',0),
('defender','Ölpumpenschraube kontrollieren/sichern','einmalig','','Stirndeckel ab','TD5-Foren',0),
('defender','Rahmen und Stirnwand auf Rost prüfen, Hohlraumkonservierung','','12 Monate','Herbst','',1),
('mini','Motor-/Getriebeöl + Filter wechseln','5.000–10.000','12 Monate','20W-50','Handbuch prüfen',0),
('mini','Zündkerzen wechseln','10.000','','','',0),
('mini','Luft- und Kraftstofffilter wechseln','20.000','','','',0),
('mini','Kugelgelenke prüfen/einstellen, Radlager prüfen','10.000','12 Monate','','',0),
('mini','Bremsflüssigkeit wechseln','','24 Monate','','',1),
('mini','Hilfsrahmen hinten, Schweller, A-Säulen auf Rost prüfen','','12 Monate','TÜV-relevant','',1),
('mini','Kühlmittel wechseln','','3 Jahre','','',0),
('vespa','Getriebeöl wechseln','3.000','12 Monate','SAE 30, 250 ml','Handbuch prüfen',0),
('vespa','Zündkerze prüfen/wechseln','3.000–5.000','','Kerzenbild lesen (Gemisch)','',0),
('vespa','Unterbrecher, Kondensator, Zündzeitpunkt prüfen','5.000','12 Monate','','',0),
('vespa','Bowdenzüge ölen, Spiel einstellen','1.000','6 Monate','Kupplung 2–3 mm Spiel am Hebel','',0),
('vespa','Vergaser reinigen, Filter','5.000','12 Monate','Ethanol-Kraftstoff: Dichtungen prüfen','',0),
('vespa','Reifen Alter/Druck, Radmuttern','','vor jeder Fahrt / 6 Monate','','',1),
('vespa','Lenkkopflager, Schwinge, Stoßdämpfer prüfen','','12 Monate','','',1),
('vespa','Rahmen konservieren, Ablauflöcher','','12 Monate','','',1);
