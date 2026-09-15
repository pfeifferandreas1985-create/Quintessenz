# CONFIG.md — Bereiche, Themen und Quellen pflegen

Zwei Dateien steuern, was im Terminal erscheint. Sie sind bewusst getrennt:

| Datei | Beantwortet | Gepflegt |
|---|---|---|
| `app/config/bereiche.yaml` | **Was** gibt es? 16 Bereiche, 104 Themen | erzeugt aus `doku/WISSENSUEBERSICHT.md` |
| `app/config/quellen.yaml` | **Woraus** werden die Akten eines Themas gemacht? | von Hand |

Der Generator überschreibt `bereiche.yaml` vollständig. `quellen.yaml` fasst er
nie an — dort steht die Handarbeit.

---

## 1. Bereiche und Themen

### Woher sie kommen

`doku/WISSENSUEBERSICHT.md` ist die Quelle. Jeder Abschnitt `### 2.x` wird ein
Bereich, **jede Tabellenzeile darin wird ein Thema**. Zeilen, deren erste Zelle
mit „Nicht enthalten" beginnt, landen unter `ausschluss` und erscheinen am Fuß
der Bereichsseite.

```bash
python tools/gen_bereiche.py
# oder mit anderem Pfad:
python tools/gen_bereiche.py /srv/box/doku/WISSENSUEBERSICHT.md
```

Ausgabe:

```
app/config/bereiche.yaml: 16 Bereiche, 104 Themen
  2.1  Elektrotechnik und Elektronik      11 Themen
  2.2  Mechanik und Maschinenelemente      7 Themen
  ...
```

### Aufbau

```yaml
bereiche:
  - id: elektrotechnik-und-elektronik   # URL-Name, aus dem Titel abgeleitet
    nr: 1                               # Abschnittsnummer der Übersicht
    titel: "Elektrotechnik und Elektronik"
    schild: "ELEKTROTECHNIK"            # Metallschild, max. ~18 Zeichen
    piktogramm: blitz                   # Symbol-ID aus piktogramme.svg
    themen:
      - id: grundlagen
        titel: "Grundlagen: Ohm, Kirchhoff, Wechselstrom, ..."
        tiefe: [LEHRBUCH]               # REFERENZ | LEHRBUCH | PRAXIS | FALL
        sprache: "DE/EN"
        quellen_text: "Wikibooks Elektrotechnik, Lessons in Electric Circuits, ..."
    ausschluss:
      - "Stack Overflow (80 GB, optional), IDE-Doku, kommerzielle Bücher"
```

### Themen-IDs

Der Generator kürzt den Titel auf die ersten fünf Wörter vor dem ersten
Doppelpunkt, höchstens 42 Zeichen, und bricht nie mitten im Wort ab. Kollisionen
innerhalb eines Bereichs bekommen `-2`, `-3` angehängt.

```
"Grundlagen: Ohm, Kirchhoff, Wechselstrom, Drehstrom, ..."  →  grundlagen
"Leitungsdimensionierung, Strombelastbarkeit, ..."          →  leitungsdimensionierung-strombelastbarkeit
```

**Eine Themen-ID ist eine Adresse.** Sie steht in Lesezeichen, im Verlauf und in
`quellen.yaml`. Wer einen Titel in der Übersicht ändert, ändert damit die ID —
und bricht die Lesezeichen. Bei einer Titeländerung entweder die alte ID in
`bereiche.yaml` von Hand wiederherstellen, oder bewusst in Kauf nehmen.

### Schilder und Piktogramme ändern

Beides steht in `tools/gen_bereiche.py` in den Tabellen `SCHILD` und
`PIKTOGRAMME` (Reihenfolge = Abschnitte 2.1 bis 2.16). Ein neues Piktogramm
braucht ein `<symbol id="p-name">` in `app/static/img/piktogramme.svg` — Aufbau
und Regeln stehen in [DESIGN.md](DESIGN.md#piktogramme).

### Bereich hinzufügen

Einen Abschnitt `### 2.17 Neuer Bereich` samt Tabelle in
`WISSENSUEBERSICHT.md` ergänzen, in `gen_bereiche.py` bei `SCHILD` und
`PIKTOGRAMME` je einen Eintrag anhängen, Generator laufen lassen. Die
Navigation nimmt beliebig viele Bereiche.

---

## 2. Quellen

`app/config/quellen.yaml` verbindet ein Thema mit den Dateien, aus denen seine
Akten entstehen. Schlüssel ist `<bereich-id>/<thema-id>`.

```yaml
themen:
  elektrotechnik-und-elektronik/grundlagen:
    einstieg: [et-ohmsches-gesetz]        # steht oben auf der Themenseite
    quellen:
      - typ: zim
        datei: wikipedia_de_all_maxi.zim
        artikel: [Ohmsches_Gesetz, Kirchhoffsche_Regeln, Wechselstrom]
```

### Quelltypen

**`zim`** — Kiwix-Archiv

| Feld | Bedeutung |
|---|---|
| `datei` | Dateiname in `zim/`, ohne Pfad |
| `praefix` | Namensraum, meist `A/` |
| `artikel` | Liste konkreter Artikel (für kuratierte Einstiegsakten) |
| `kategorie` | Kategoriename; `"*"` nimmt alles |
| `suche` | Suchbegriffe; Treffer werden verlinkt, aber **nicht** ingestiert |
| `max` | Obergrenze aufgenommener Artikel |

**`se`** — Stack Exchange

| Feld | Bedeutung |
|---|---|
| `datei` | Stack-Exchange-ZIM |
| `tags` | nur Fragen mit diesen Tags |
| `min_score` | Mindestpunktzahl |
| `nur_beantwortet` | `true` → nur Fragen mit akzeptierter Antwort |

**`pdf`** — Handbuch, Katalog, Leitlinie

| Feld | Bedeutung |
|---|---|
| `datei` | Pfad unterhalb von `pdf/` |
| `kapitel` | Seitenbereiche, die je eine Akte werden: `{von, bis, titel}` |
| `seitenbild` | Seiten, die als Kopie eingeklebt statt neu gesetzt werden |
| `tiefe` | überschreibt die Tiefe des Themas |

**`eigen`** — eigenes Material

| Feld | Bedeutung |
|---|---|
| `modul` | `fahrzeuge` \| `rebuild` \| `tabellen` |

### Große Quellen nicht ingestieren

Wikipedia DE maxi hat 2,9 Mio. Artikel. Ein eigener Volltextindex darüber wäre
30–40 GB groß und würde Tage rechnen. Solche Archive gehören unter
`nur_durchsuchen`:

```yaml
nur_durchsuchen:
  - wikipedia_de_all_maxi.zim
  - wikipedia_en_all_nopic.zim
  - gutenberg_en_all.zim
```

Die Suche geht dann an `kiwix-serve` auf `:8888`; der Artikel wird beim Öffnen
live aus der ZIM gelesen, bereinigt und ins Papier-Template gegossen. Auf dem
Pi 5 kostet das etwa 80–200 ms je Artikel — nicht spürbar.

Alles Übrige (WikiMed, Wikibooks, Stack Exchange, iFixit, PDFs, eigenes
Material) ist klein genug für FTS5 und Embeddings.

### NUR LOKAL

```yaml
nur_lokal:
  - zim/eigene/privat/
  - pdf/fahrzeuge/
  - own/
```

Akten aus diesen Pfaden bekommen den Stempel **NUR LOKAL** und bleiben bei einer
Weitergabe der Box außen vor. Kommerzielle Werkstatthandbücher und eigene
Unterlagen gehören hierher.

---

## 3. Reihenfolge auf der Themenseite

1. die unter `einstieg` genannten Akten, in der dort angegebenen Reihenfolge
2. alles Weitere nach Tiefe: **REFERENZ → LEHRBUCH → PRAXIS → FALL**, innerhalb
   einer Stufe alphabetisch

Die Rangfolge steht in `app/server.py`, `TIEFE_RANG`.

---

## 4. Prüfen

```bash
python tools/gen_bereiche.py           # Bereiche neu erzeugen
python tools/kontrast.py               # Farbkontraste gegen die Vorgaben
curl -s localhost:8000/api/status      # was der Server sieht
curl -s localhost:8000/api/eingang | python -m json.tool | head -40
```

`/api/status` zeigt unter `datenpfad`, welchen Ordner die Anwendung tatsächlich
gewählt hat — die häufigste Ursache für „meine Akten fehlen".

Eine Akte ohne vollständige Quellenangabe wird verworfen und ins Log
geschrieben, nicht stillschweigend angezeigt. Die Prüfung steht in
`app/adapters/basis.py`, `pruefe()`.
