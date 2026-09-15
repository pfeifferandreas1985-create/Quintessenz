# 05 — Offene Fragen

Vor Phase 2 (Hardwarekauf) sollten 1, 2, 4 und 5 beantwortet sein. Der Rest
kann während des Aufbaus geklärt werden.

| # | Frage | Warum es zählt | Wie klären | Status |
|---|---|---|---|---|
| 1 | **Reicht ein 2-B-Modell mit RAG für die Fachfragen?** | Wenn nein, ist der Pi die falsche Plattform | Phase 1: Qwen3.5-2B + Kiwix-Suche auf dem PC, 20 echte Fragen aus Werkstatt/Medizin/Survival, Antworten bewerten | offen |
| 2 | **Pi 5 16 GB oder Mini-PC?** | 350 € vs. 300 €, 15 W vs. 50 W, 2 B vs. 9 B | Hängt an Frage 1. Wenn 2 B reicht → Pi. Wenn nicht → beides, Pi als mobile Leseeinheit | offen |
| 3 | **AI HAT+ 2: wirklich schneller?** | Quellen widersprechen sich (10–25× vs. kein Vorteil) | Nicht selbst kaufen zum Testen. Zwei unabhängige Benchmarks mit Qwen-2B lesen; PCIe-Switch-Preis prüfen. Vorläufige Antwort: **nein**, siehe 02_HARDWARE | vorläufig nein |
| 4 | **Potato OS oder eigenes Image?** | Zeit bis zum ersten Erfolg vs. Kontrolle | Phase 1 mit Potato OS. Prüfen: lässt sich Kiwix + Python-Dienst sauber daneben installieren? Wie aktiv ist das Projekt in 12 Monaten? | offen |
| 5 | **Wikipedia semantisch indexieren oder Kiwix-Volltextsuche als Retriever?** | 30–40 GB Index + Tage Rechenzeit vs. BM25 sofort verfügbar | Beides testen in Phase 1 mit 30 Fragen. Vermutung: **Hybrid** — Kiwix-BM25 für Wikipedia, Embedding nur für PDFs und kleine Fach-ZIMs | offen |
| 6 | **sqlite-vec oder Qdrant?** | Einfachheit vs. Skalierung | Erst sqlite-vec. Wechsel, wenn Abfragen > 2 s | vorläufig sqlite-vec |
| 7 | **Reranker auf dem Pi tragbar?** | +1–3 s pro Frage, aber deutlich bessere Treffer | Messen in Phase 3. Abschaltbar machen | offen |
| 8 | **WLAN-Hotspot oder Anschluss an vorhandenen Router?** | Hotspot = autark, aber kein Internet parallel für andere Geräte | Beides vorsehen, Umschalter in der UI. Standard: Hotspot | beides |
| 9 | **PCIe Gen 3 stabil?** | Doppelte SSD-Geschwindigkeit, inoffiziell | Ausprobieren, bei Fehlern in `dmesg` zurück auf Gen 2 | offen |
| 10 | **Wie wird das Image weitergegeben?** | Phase 6 — 100 GB+ Image ist unhandlich | Image ohne Wissensbasis (~10 GB) + separater Ordner ZIMs. Oder: Anleitung "SSD klonen" | offen |
| 11 | **Lizenzfragen bei Weitergabe** | Wikipedia CC BY-SA: ok. Tabellenbuch, SAS-Handbuch: nicht ok | Trennung: `knowledge/frei/` (weitergebbar) und `knowledge/privat/` (nur eigene Kopie) | Struktur festlegen |
| 12 | **Gehäuse: Metall (Kühlung) oder Kunststoff (WLAN)?** | Metallgehäuse dämpfen das Pi-WLAN spürbar | Argon-Gehäuse mit externem WLAN-Fenster, oder USB-WLAN-Stick mit Antenne | offen |
| 13 | **Zweite Box für die Familie / Werkstatt?** | Redundanz durch Duplikation ist einfacher als Backup | Wenn Phase 6 sauber, ist die zweite Box ein Nachmittag | später |

## Entscheidungen, die schon gefallen sind

| Entscheidung | Begründung |
|---|---|
| Kein AI HAT+ 2 in der Wissensbox | PCIe-Slot für NVMe, GGUF-Kompatibilität, Strom — unabhängig von der Geschwindigkeitsfrage |
| Kein Qwen3-30B-A3B mit SSD-Offload | SSD-Verschleiß, Speicherdruck, kein Nutzen für RAG |
| Kein Docker auf dem Pi | Overhead, Komplexität; systemd reicht |
| Kein Open WebUI auf dem Pi | Zu schwer (Node + Python + DB); eigene Ein-Seiten-UI |
| Modell antwortet nur aus Quellen | Grundsatz 1 — ein 2-B-Modell ohne Leine erfindet |
| Wissensbasis wird mit AI-ARK geteilt | Einmal laden, zweimal nutzen |
| Index wird auf dem PC gebaut, nicht auf dem Pi | Tage vs. Stunden |
