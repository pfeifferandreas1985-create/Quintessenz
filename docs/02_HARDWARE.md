# 02 — Hardware

## Stückliste (Grundkonfiguration)

Preise sind grobe Schätzungen (Stand 2026, Deutschland) — vor Bestellung prüfen.

| # | Komponente | Empfehlung | ca. Preis | Begründung |
|---|---|---|---|---|
| 1 | Rechner | **Raspberry Pi 5, 16 GB** | 120–130 € | 8 GB reichen für 2-B-Modelle; 16 GB geben Luft für Embedding-Modell + Vektor-DB + Kiwix gleichzeitig im RAM |
| 2 | Speicher | **NVMe-SSD 2 TB, M.2 2230/2242** | 120–160 € | Wissensbasis 200–500 GB + Modelle + Index + Platz für Wachstum. Zweite Kopie einplanen |
| 3 | SSD-Anschluss | **NVMe-HAT (M.2 HAT+ oder Pimoroni NVMe Base)** | 15–25 € | PCIe Gen 2 ×1 offiziell, Gen 3 per Konfiguration — für Modell-Ladezeiten und ZIM-Suche relevant |
| 4 | Kühlung | **Offizieller Active Cooler** | 6 € | Inferenz ist Dauerlast; ohne Lüfter drosselt der Pi nach Minuten |
| 5 | Netzteil | **Offizielles 27-W-USB-C** | 13 € | Unterversorgte Pis produzieren Fehler, die wie Softwarebugs aussehen |
| 6 | Boot-Medium | microSD 32 GB (nur zum Erststart) | 8 € | Danach Boot direkt von NVMe |
| 7 | Gehäuse | Argon NEO 5 M.2 NVMe oder Pironman 5 | 30–60 € | Muss HAT + Lüfter aufnehmen; Metall hilft passiv |
| | **Summe Grundausbau** | | **~320–410 €** | |

### Optional / Ausbau

| Komponente | Empfehlung | ca. Preis | Wann |
|---|---|---|---|
| Zweite SSD (extern, USB) | 2 TB, gleiche Größe | 120–160 € | **Nicht optional** für die Redundanz-Regel — spätestens Phase 5 |
| Powerbank | 100 Wh (27.000 mAh), USB-C PD 30 W+ | 60–100 € | Mobilbetrieb, 4–5 h |
| USV-HAT | Waveshare UPS HAT (E) oder PiJuice | 40–70 € | Stationär bei unsicherem Netz; sauberes Herunterfahren |
| Solar | 60–100 W Panel + Laderegler + 12-V-Akku | 150–300 € | Autarker Dauerbetrieb |
| Display | 7" Touch oder E-Paper | 60–100 € | Bedienung ohne zweites Gerät |
| RTC-Batterie | CR2032 für Pi 5 RTC | 2 € | Zeitstempel ohne NTP |
| GPS-Modul | USB-GPS | 15–25 € | Kartenfunktion mit Standort |

## Strombudget

| Zustand | Pi 5 + NVMe + Lüfter | Anmerkung |
|---|---|---|
| Leerlauf | 4–6 W | Kiwix + Server bereit |
| Suche (Embedding + Vektor) | 8–12 W | wenige Sekunden |
| LLM-Inferenz | 12–15 W | 30–60 s pro Antwort |
| Spitze (Indexaufbau) | 15–18 W | einmalig, Stunden |

**Rechnung Powerbank 100 Wh:** bei gemischter Nutzung (~10 W Mittel) ≈ 8 h reine
Laufzeit, realistisch **4–6 h** nach Wandlungsverlusten. Entspricht deiner
Schätzung.

## Die NPU-Frage: AI HAT+ 2 (Hailo-10H)

**Empfehlung: Nein, nicht für diese Box.** Aber aus anderen Gründen als "zu langsam".

Die Quellen widersprechen sich bei der LLM-Geschwindigkeit:
- Einige Tests (CNX Software, Hackster, 01/2026) sehen den HAT **10–25× schneller**
  als die Pi-CPU bei denselben Modellen
- Andere Berichte sehen **keinen Vorteil**, weil die PCIe-Gen-2-×1-Anbindung
  (~400–500 MB/s) limitiert

Das ist nicht entscheidbar, ohne selbst zu messen → **05_OFFENE-FRAGEN.md, Frage 3.**

Was **unabhängig davon** gegen den HAT spricht:

| Argument | Gewicht |
|---|---|
| Belegt den einzigen PCIe-Slot → keine NVMe ohne zusätzlichen PCIe-Switch-HAT (Kosten, Höhe, Stromverbrauch, Komplexität) | **Entscheidend** |
| Eigener 8-GB-Speicher, aber nur Modelle bis ~1,5 B praktikabel — der Speicher nützt dem größeren Modell nichts | Hoch |
| Eigene Toolchain (Hailo-Modellformat), nicht GGUF — jedes neue Modell muss konvertiert werden, Konvertierung braucht Internet und x86-Rechner | Hoch |
| Zusätzliche 3–5 W | Mittel |
| Für RAG ist Geschwindigkeit sekundär: die Wissensbasis liefert die Fakten, das Modell muss nur lesbar formulieren | Mittel |

**Wo der HAT sinnvoll wäre:** ein zweiter Pi als Kamera-Box (Pflanzenerkennung,
Schädlinge, Objekterkennung) — das ist echte Edge-AI und genau das, wofür Hailo
gebaut ist. Als **Ausbaustufe** notieren, nicht als Teil der Wissensbox.

## Alternative: gebrauchter Mini-PC

| | Pi 5 16 GB | Mini-PC (Ryzen 7 5800H, 32–64 GB, gebraucht) |
|---|---|---|
| Preis komplett | ~350 € | 250–400 € |
| Leistung LLM | 2–3 B bei 7–8 tok/s | 7–9 B bei 10–15 tok/s, 27 B möglich |
| Leerlauf | 5 W | 10–15 W |
| Last | 15 W | 45–65 W |
| Powerbank 100 Wh | 4–6 h | 1,5–2 h |
| Robustheit | keine bewegten Teile außer Lüfter, 5 V | Lüfter, 19 V, mehr Elektronik |
| Ausfallrisiko | gering, Ersatz 130 € | mittel, gebraucht |
| Modellklasse | Formulieren | Denken (Qwen3.5-9B, Gemma 4 E4B) |

**Empfehlung:** Erst den Pi bauen — er erfüllt die Kernanforderung (tragbar,
sparsam, weitergebbar). Wenn sich in Phase 1 zeigt, dass 2 B mit RAG **nicht**
reicht, ist der Mini-PC die stationäre Ergänzung, nicht der Ersatz. Beide teilen
sich dieselbe Wissensbasis und dasselbe Software-Image.

## Was aus dem Bestand genutzt werden kann

- **AI-ARK auf D:** liefert die Modelle (Qwen3.5-0.8B, Gemma 4 E2B/E4B, Granite Nano,
  Embedding-Modelle) und die ZIM-Dateien → nichts doppelt herunterladen
- Ein vorhandener PC für Phase 1 (Trockenlauf)
