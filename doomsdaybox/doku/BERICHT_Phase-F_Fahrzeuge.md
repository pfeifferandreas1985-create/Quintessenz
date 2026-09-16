# Bericht Phase F - Eigene Fahrzeuge

Stand 2026-09-16. Alle Dateien sind Privatkopien fuer den Eigengebrauch; Quelle und Abrufdatum stehen in jedem PDF.


## Land Rover Defender 110 TD5 (1998-2006)

| Bereich | Dateien | MB | Ablage |
|---|---|---|---|
| Handbuecher, Kataloge, Schaltplaene (PDF) | 17 | 149 | pdf/fahrzeuge/defender/ |
| forenwissen (Artikel/Threads als PDF) | 9 | 19 | own/fahrzeuge/defender_forenwissen/ |
| landypedia (Artikel/Threads als PDF) | 182 | 181 | own/fahrzeuge/defender_landypedia/ |

**Kaufempfehlung (nicht geladen):**
- Brooklands: Defender Workshop Manual TD5 (LRL0410/LRL0097) - Nachdruck, falls gedruckte Ausgabe gewuenscht
- Brooklands: Defender Parts Catalogue 1987-2006 (STC9021CC) - gedruckt; digital durch Rimmer-Katalog gedeckt
- Haynes 3017 Land Rover Defender Diesel 1983-2007

## Rover Mini Cooper 1.3i MPi (1999)

| Bereich | Dateien | MB | Ablage |
|---|---|---|---|
| Handbuecher, Kataloge, Schaltplaene (PDF) | 3 | 79 | pdf/fahrzeuge/mini/ |
| Explosionszeichnungen, einheitlich gesetzt | 22 | 38 | pdf/fahrzeuge/mini/explosionszeichnungen/ |
| forenwissen (Artikel/Threads als PDF) | 7 | 38 | own/fahrzeuge/mini_forenwissen/ |
| Teileliste (CSV, 6411 Positionen) | 1 | 0.7 | own/fahrzeuge/minispares_teileliste.csv |

**Kaufempfehlung (nicht geladen):**
- Brooklands/Rover: Mini Workshop Manual 1992-2000 inkl. MPi (RCL0193) - Nachdruck, falls gedruckt gewuenscht
- Mini Parts Catalogue 1990-2000 (British Motor Heritage) - gedruckt; digital durch Minispares-Katalog gedeckt

**Nachtrag 16.09.2026:** Mini Sport Catalogue 2019/20 (Mini Sport Ltd, Padiham; 196 S., Teile, Restaurierung, Tuning, Zubehoer; mit Textebene) vom Nutzer geliefert - ergaenzt den Minispares-Katalog um einen zweiten Haendlerkatalog mit Bildern und Artikelnummern.
- Haynes 0646 Mini 1969-2001

## Vespa V50 N, V5A1T (1963)

| Bereich | Dateien | MB | Ablage |
|---|---|---|---|
| Handbuecher, Kataloge, Schaltplaene (PDF) | 3 | 31 | pdf/fahrzeuge/vespa/ |
| Explosionszeichnungen, einheitlich gesetzt | 8 | 26 | pdf/fahrzeuge/vespa/explosionszeichnungen/ |
| forenwissen (Artikel/Threads als PDF) | 19 | 156 | own/fahrzeuge/vespa_forenwissen/ |
| gsf-wiki (Artikel/Threads als PDF) | 204 | 1327 | own/fahrzeuge/vespa_gsf-wiki/ |
| schaltplaene (Artikel/Threads als PDF) | 5 | 9 | own/fahrzeuge/vespa_schaltplaene/ |
| Teileliste (CSV, 4618 Positionen) | 1 | 0.7 | own/fahrzeuge/scootercenter_teileliste.csv |

**Kaufempfehlung (nicht geladen):**
- Bucheli Reparaturanleitung Vespa 50/90/125 Smallframe
- Vespa Technica Bd. Smallframe

## Nicht erreichbar / offen

- lrcat.com - Zeitueberschreitung von diesem Anschluss (Land-Rover-Explosionszeichnungen stattdessen aus dem Rimmer-Teilekatalog 1983-2006)
- sip-scootershop.com - HTTP 403 fuer Skripte, Browser durch Organisationsrichtlinie gesperrt (Piaggio-Tafeln stattdessen von scooter-center.com)
- minimania.com - HTTP 522 (Server nicht erreichbar) am 16.09.2026, Tech-Artikel spaeter nachholen
- britpart.com - keine oeffentlichen Explosionszeichnungen im Katalog gefunden
- paddockspares.com - nur Produktlisten, keine Explosionszeichnungen

## Werkzeuge

- `tools/fahrzeuge_fetch.py` - Kataloge spiegeln (Minispares, Scooter Center), PDF je Kapitel/Modell + CSV
- `tools/seiten_zu_pdf.py` - Wiki-Artikel (MediaWiki-API), Forenthreads, Fachseiten als PDF
- `tools/fahrzeuge_abschluss.py` - dieses Skript: Stage -> D:, Manifeste, Bericht

Erneuter Lauf laedt nur Fehlendes nach (Cache unter C:/stage/fahrzeuge/_cache).
