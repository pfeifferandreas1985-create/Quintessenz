# ark-pi — Offline-Wissensassistent auf dem Raspberry Pi

> Eine Box, die ohne Internet Fragen beantwortet — mit einem lokalen Sprachmodell,
> das in einer Offline-Wissensbasis nachschlägt statt zu raten.
> Tragbar, stromsparend, redundant. Der kleine Bruder von AI-ARK.

**Status:** Konzeptphase — nichts gebaut, nichts bestellt. Dieses Repo sammelt
die Idee, die Entscheidungen und die offenen Fragen, bevor Geld fließt.

---

## Die Idee in drei Sätzen

Ein Raspberry Pi 5 mit NVMe-SSD trägt ein kleines Sprachmodell (2–3 B) und eine
durchsuchbare Wissensbasis: Wikipedia, WikiMed, Reparaturanleitungen, Fachbücher,
Karten, eigene Dokumente. Eine RAG-Pipeline verbindet beides — das Modell
formuliert, die Wissensbasis liefert die Fakten. Das Ganze läuft an einer
Powerbank, im Auto oder am Solarpaneel und ist über jedes Gerät im lokalen
Netz per Browser erreichbar.

## Warum nicht einfach AI-ARK?

| | AI-ARK | ark-pi |
|---|---|---|
| Rolle | Vollarchiv, 500 GB Modelle, Workstation-Klasse | Tragbare Notfallbox, ein Modell, ein Zweck |
| Hardware | Beliebiger PC mit viel RAM/GPU | Pi 5, 16 GB, ~15 W |
| Strom | 100–500 W | 10–25 W, Powerbank-tauglich |
| Stärke | Die besten offenen Modelle, Coding, Analyse | Immer an, überall, fast umsonst im Betrieb |
| Schwäche | Braucht einen Rechner, der im Ernstfall vielleicht nicht läuft | 2-B-Modell — formuliert gut, denkt wenig |

Beide teilen sich die Wissensbasis (ZIM-Dateien, Dokumente). ark-pi ist das,
was man in die Tasche steckt, wenn die Workstation nicht mitkommt.

## Dokumente

| Datei | Inhalt |
|---|---|
| [docs/01_KONZEPT.md](docs/01_KONZEPT.md) | Zielbild, Nutzungsszenarien, Architektur, Phasenplan |
| [docs/02_HARDWARE.md](docs/02_HARDWARE.md) | Stückliste, Entscheidung Pi vs. Mini-PC, die NPU-Frage |
| [docs/03_SOFTWARE.md](docs/03_SOFTWARE.md) | OS, Inferenz, Kiwix, RAG-Pipeline, Oberfläche |
| [docs/04_WISSENSBASIS.md](docs/04_WISSENSBASIS.md) | Was rein muss, priorisiert nach Bereich, mit Quellen |
| [docs/05_OFFENE-FRAGEN.md](docs/05_OFFENE-FRAGEN.md) | Was vor dem Kauf geklärt werden muss |

## Verwandt

- **AI-ARK** — das große Offline-Archiv (500 GB Modelle, Handbuch, Skripte), lokal unter `D:\AI-ARK`
- [Potato OS](https://github.com/potato-os/core) — fertiges Pi-Image mit LLM + Web-UI
- [Kiwix](https://kiwix.org) — Offline-Reader für ZIM-Archive
- [Project NOMAD](https://github.com/geoffwhittington/project-nomad) — Docker-Stack für Offline-Wissen + KI (x86, als Architekturvorlage)
- [Hesperian Foundation](https://hesperian.org) — *Where There Is No Doctor* und weitere Handbücher, frei als PDF
