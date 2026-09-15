"""Die Schnittstelle, die jeder Quelladapter erfuellen muss.

Dieses Modul enthaelt absichtlich keine Logik. Es haelt den Vertrag fest,
damit die noch fehlenden Adapter (zim, se, pdf) spaeter eingehaengt werden
koennen, ohne dass Server oder Frontend angefasst werden muessen.

Ein Adapter hat zwei Aufgaben:

  liste()           -> welche Akten kann ich liefern? (nur Kopfdaten)
  hole(akte_id)     -> die vollstaendige Akte mit Inhaltsbloecken

Wer live aus der Quelle liest (ZIM ueber python-libzim), implementiert beide
zur Laufzeit. Wer vorverarbeitet (PDF ueber den Ingest auf dem PC), liest
beide aus db/index.sqlite. Das Frontend merkt keinen Unterschied.

Grenzen, die jeder Adapter einhalten muss
-----------------------------------------
* Er erzeugt Bloecke nach akte.py, niemals Darstellungs-HTML.
* Absatz-HTML enthaelt nur: em strong code sub sup br a[data-akte]
  Alles andere wird HIER entfernt, nicht erst im Browser.
* Interne Verweise zeigen auf andere Akten (a[data-akte]), nie auf kiwix
  oder eine externe Adresse.
* Bilder liefern eine anwendungseigene URL (/api/bild/...), nie eine
  fremde. Wer keine hat, liefert keinen Bildblock - lieber gar kein Bild
  als ein erfundenes.
* Jede Akte traegt eine vollstaendige Quelle (Datei, Kennung, Lizenz, Stand).
  Eine Akte ohne Quellenangabe wird verworfen.
"""
from __future__ import annotations

from typing import Iterable, Protocol

from akte import Akte


class Adapter(Protocol):
    """Was ein Quelladapter koennen muss."""

    #: Kurzname, taucht im Aktenstempel und in der Konfiguration auf.
    typ: str

    def verfuegbar(self) -> bool:
        """Liegen die noetigen Dateien/Dienste vor?

        Wird beim Start einmal gefragt. Ein nicht verfuegbarer Adapter wird
        uebersprungen; die Anwendung startet trotzdem und zeigt die
        betroffenen Themen als 'wartet auf Beschaffung'.
        """
        ...

    def liste(self) -> Iterable[Akte]:
        """Alle lieferbaren Akten, OHNE Inhaltsbloecke (inhalt=[]).

        Muss billig sein: wird beim Start und nach jedem Ingest aufgerufen.
        Bei grossen Quellen eine SQL-Abfrage, kein Durchlauf der ZIM.
        """
        ...

    def hole(self, akte_id: str) -> Akte | None:
        """Die vollstaendige Akte. None, wenn unbekannt."""
        ...

    def original(self, akte_id: str) -> tuple[str, str] | None:
        """Rohdarstellung fuer 'Original einsehen' als (medientyp, inhalt).

        ZIM: das bereinigte Quell-HTML. PDF: die gerenderte Seite als PNG.
        Eigenes Material: die Rohzeilen der Tabelle.
        """
        ...


def pruefe(a: Akte) -> list[str]:
    """Mindestpruefung einer Akte, bevor sie ins Register darf.

    Liefert die Liste der Maengel; leer heisst in Ordnung. Der Server
    verwirft Akten mit Maengeln und schreibt sie ins Log, statt sie
    stillschweigend anzuzeigen.
    """
    maengel: list[str] = []
    if not a.id or " " in a.id:
        maengel.append("id fehlt oder enthaelt Leerzeichen")
    if not a.titel.strip():
        maengel.append("titel leer")
    if a.tiefe not in ("REFERENZ", "LEHRBUCH", "PRAXIS", "FALL"):
        maengel.append(f"tiefe unbekannt: {a.tiefe!r}")
    if not a.quelle or not a.quelle.name:
        maengel.append("quelle.name fehlt - Akten ohne Quellenangabe sind unzulaessig")
    if not a.quelle.lizenz:
        maengel.append("quelle.lizenz fehlt")
    if not a.bereich_id or not a.thema_id:
        maengel.append("bereich_id/thema_id fehlt")
    return maengel
