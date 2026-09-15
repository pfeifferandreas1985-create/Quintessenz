# ingest/ — Vorverarbeitung auf dem PC

**Noch nicht gebaut.** Dieser Ordner ist die zweite Stufe. Die Schnittstelle,
die er bedienen muss, steht bereits fest: `app/adapters/basis.py`.

## Warum getrennt vom Server

Der Index wird auf dem PC gebaut, nicht auf dem Pi — Stunden statt Tage, und
die Embeddings brauchen eine GPU. Ergebnis sind drei Dinge unter `db/`, die
danach auf die Box kopiert werden:

| | |
|---|---|
| `db/index.sqlite` | Akten + FTS5-Volltextindex |
| `db/vectors.sqlite` | Embeddings (sqlite-vec, Qwen3-Embedding-0.6B) |
| `db/images/` | aus ZIM und PDF extrahierte Abbildungen |

## Geplanter Aufruf

```bash
python -m ingest --daten D:\DoomsdayBox --nur pdf        # nur PDFs
python -m ingest --daten D:\DoomsdayBox --thema medizin/erste-hilfe-reanimation-aktuelle-erc
python -m ingest --daten D:\DoomsdayBox --fortsetzen     # nach Abbruch
python -m ingest --daten D:\DoomsdayBox --embeddings     # zweiter Durchgang, GPU
```

Wiederaufnehmbar und inkrementell: jede Quelldatei bekommt einen Eintrag mit
SHA-256 und Änderungszeit. Unveränderte Dateien werden übersprungen.

## Was die drei Adapter leisten müssen

**ZIM** — `python-libzim`. HTML bereinigen: Navigationsleisten, Bearbeiten-Links,
Fußzeilen und das Wikipedia-Infobox-Layout entfernen; Überschriften, Absätze,
Listen, Tabellen, Bilder und Formeln behalten. Interne Verweise auf
`a[data-akte]` umschreiben, nie auf kiwix. Bilder nach `db/images/` auslagern.

**Stack Exchange** — Frage plus akzeptierte oder bestbewertete Antwort als
`fall_frage` / `fall_antwort`. Weitere Antworten als `fall_antwort` ohne
`akzeptiert` — das Papier klappt sie ein.

**PDF** — `pymupdf`. Überschriften über Schriftgröße erkennen, eingebettete
Bilder extrahieren. Layoutlastige Seiten (Zeichnungen, komplexe Tabellen) nicht
nachbauen, sondern als `seitenbild` rendern und einkleben. Kapitelgrenzen
kommen aus `quellen.yaml`.

## Regeln

Die Grenzen für jeden Adapter stehen in `app/adapters/basis.py` im
Modul-Docstring. Die wichtigste: **eine Akte ohne vollständige Quellenangabe
wird verworfen.** `pruefe()` setzt das durch.
