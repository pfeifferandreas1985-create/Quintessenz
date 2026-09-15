# 01 — Konzept

## Zielbild

Eine Kiste von der Größe eines Taschenbuchs. Einschalten, 60 Sekunden warten,
mit dem Handy auf `http://quintessenz.local` gehen, Frage stellen. Die Antwort kommt aus
einer lokalen Wissensbasis, formuliert von einem lokalen Sprachmodell, mit
Quellenangabe auf den Abschnitt, aus dem sie stammt. Kein Internet, kein Konto,
kein Abo. Läuft vier Stunden an einer 100-Wh-Powerbank oder unbegrenzt an einem
kleinen Solarpaneel.

## Für wen und wann

| Szenario | Was die Box leisten muss |
|---|---|
| **Werkstatt ohne Netz** | Reparaturanleitung finden, Datenblatt nachschlagen, Schaltung erklären lassen |
| **Stromausfall / Netzausfall über Tage** | Erste Hilfe, Wasseraufbereitung, Kommunikationsmittel — lesbar auf jedem Handy im WLAN der Box |
| **Unterwegs, Auto, Camping** | Karten, Pflanzenbestimmung, medizinische Grundfragen |
| **Internet vorhanden, aber unbrauchbar** | Verlässliche Referenz ohne generierten Müll, Bezahlschranken und Filter |
| **Weitergabe** | Die Box muss von jemandem bedienbar sein, der sie nicht gebaut hat |

Das letzte Szenario prägt die Gestaltung am stärksten: **eine Oberfläche, ein
Eingabefeld, keine Konfiguration.**

## Grundsätze

1. **Die Wissensbasis ist das Produkt, das Modell ist der Vorleser.** Ein 2-B-Modell
   erfindet Fakten. Es darf deshalb ausschließlich aus gefundenen Textstellen
   antworten und muss diese zeigen. Ohne Treffer sagt es "nicht in der Wissensbasis".
2. **Alles muss ohne die Box lesbar bleiben.** ZIM-Dateien öffnen sich mit jedem
   Kiwix-Reader, PDFs mit jedem PDF-Reader. Wenn der Pi stirbt, stirbt nicht das Wissen.
3. **Zwei Kopien von allem.** SSD im Pi + externe Kopie. SSD-Ausfall = Totalverlust
   ist nicht akzeptabel.
4. **Strom ist die knappste Ressource.** Jede Komponente wird nach Watt beurteilt.
5. **Erst nachbauen, was es gibt.** Potato OS, Kiwix, Project NOMAD lösen 80 %.
   Eigenentwicklung nur für die RAG-Verknüpfung und die Oberfläche.

## Architektur

```
 Handy / Laptop im WLAN der Box
          │  http://quintessenz.local
          ▼
 ┌─────────────────────────────────────────────────────┐
 │  Weboberfläche (ein Eingabefeld, Quellen, Verlauf)  │
 ├──────────────┬──────────────────┬───────────────────┤
 │  RAG-Dienst  │  Kiwix-Server    │  Kartenserver     │
 │  (Python)    │  :8888           │  (PMTiles)        │
 │  ┌─────────┐ │                  │                   │
 │  │Embedding│ │  ZIM-Dateien:    │  OSM-Region       │
 │  │ 300 M   │ │  Wikipedia, Med, │  Höhenlinien      │
 │  ├─────────┤ │  iFixit, StackEx │                   │
 │  │Vektor-DB│ │                  │                   │
 │  ├─────────┤ │                  │                   │
 │  │  LLM    │ │                  │                   │
 │  │ 2–3 B   │ │                  │                   │
 │  └─────────┘ │                  │                   │
 ├──────────────┴──────────────────┴───────────────────┤
 │  llama.cpp-Server (OpenAI-API, :8080)               │
 ├─────────────────────────────────────────────────────┤
 │  Raspberry Pi OS 64-bit · Pi 5 16 GB · NVMe 1–2 TB  │
 └─────────────────────────────────────────────────────┘
```

**Datenfluss einer Frage:**
Frage → Embedding → Vektorsuche (Top 8) → optional Reranking → Textstellen +
Frage an LLM → Antwort mit Verweisen → Klick auf Verweis öffnet den Kiwix-Artikel.

## Phasenplan

| Phase | Ziel | Ergebnis | Aufwand |
|---|---|---|---|
| **0 — Konzept** *(jetzt)* | Entscheidungen treffen, offene Fragen klären | Dieses Repo | 1 Abend |
| **1 — Trockenlauf** | Stack auf dem vorhandenen PC nachbauen, bevor Hardware gekauft wird | RAG über 3 ZIMs funktioniert, Latenz gemessen | 1 Wochenende |
| **2 — Hardware** | Pi 5 16 GB + NVMe + Kühler beschaffen, Potato OS oder Pi OS flashen | Pi antwortet im Browser | 1 Abend + Lieferzeit |
| **3 — Wissensbasis** | ZIMs, PDFs, Karten laden; Embedding-Index aufbauen | Alle Prioritäts-Hoch-Quellen durchsuchbar | 1–2 Wochenenden (Indexierung läuft nachts) |
| **4 — Oberfläche** | Ein-Feld-UI mit Quellenanzeige, mDNS `quintessenz.local`, WLAN-Hotspot-Modus | Bedienbar ohne Anleitung | 1 Wochenende |
| **5 — Härtung** | Read-only-Root, Watchdog, Backup-Skript, Gehäuse, Powerbank-Test | 72-h-Dauertest bestanden | 1 Wochenende |
| **6 — Weitergabe** | Image-Datei + Kurzanleitung, die jemand anderes flashen kann | `Quintessenz.img.xz` + 1 Seite PDF | 1 Abend |

**Phase 1 ist der wichtigste Schritt:** Er kostet nichts und beantwortet die
Frage, ob ein 2-B-Modell mit RAG für die eigenen Anwendungsfälle tatsächlich
ausreicht — bevor 250 € für Hardware ausgegeben werden.

## Was die Box bewusst nicht ist

- Kein Ersatz für Fachwissen. Sie findet die Anleitung, sie repariert nicht.
- Kein Coding-Assistent — dafür ist AI-ARK mit den großen Modellen da.
- Kein Chatbot zum Plaudern. Jede Antwort soll auf eine Quelle zeigen.
- Kein Internet-Gateway. Sie hängt in keinem fremden Netz.

## Erfolgskriterien

Die Box gilt als fertig, wenn:
- [ ] eine fremde Person ohne Einweisung in unter 2 Minuten eine Antwort erhält
- [ ] 10 von 10 Testfragen aus dem Fachbereich mit korrekter Quelle beantwortet werden
- [ ] eine mittellange Antwort in unter 45 Sekunden steht
- [ ] 72 Stunden Dauerbetrieb ohne Eingriff überstanden sind
- [ ] 4 Stunden Betrieb an einer 100-Wh-Powerbank gemessen sind
- [ ] die Wissensbasis auf einem zweiten Medium liegt und dort geöffnet wurde
