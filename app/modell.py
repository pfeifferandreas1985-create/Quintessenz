# -*- coding: utf-8 -*-
"""
Modellanbindung mit Umschalter: lokal oder online.

Warum es diese Schicht gibt
    Die Box ist dafuer gebaut, ohne Netz zu antworten. Ein Online-Modell ist schneller und
    staerker, aber es ist Komfort, nicht Rueckfallebene. Beides soll nebeneinander moeglich
    sein, ohne dass man Dateien aendert.

Was NIE nach aussen geht
    Die Suche bleibt lokal: Index, Einbettungen, Auswahl der Fundstellen. Online geht nur der
    letzte Schritt, das Formulieren der Antwort, und dafuer nur die Frage und die wenigen
    Absaetze, die zur Frage gehoeren. Das Archiv verlaesst das Geraet nicht.

Anbieter
    lokal      Ollama auf 127.0.0.1:11434 (Vorgabe)
    openai     alles, was die OpenAI-Schnittstelle spricht: OpenAI, Mistral, Groq,
               OpenRouter, LM Studio, llama.cpp-Server
    anthropic  Claude

Schluessel
    Nur aus der Umgebung, nie aus einer Datei im Repo:
        setx QUINTESSENZ_API_KEY "..."      (Windows)
        export QUINTESSENZ_API_KEY=...      (Linux)

Gebrauch
    from modell import antwort, verfuegbar
    text, woher = antwort("Wie dimensioniere ich ...", fundstellen, modus="auto")
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

try:
    import yaml
except ImportError:                                    # pragma: no cover
    yaml = None

HIER = Path(__file__).resolve().parent
KONFIGDATEI = HIER / "config" / "modell.yaml"
SCHLUESSEL_VAR = "QUINTESSENZ_API_KEY"

SYSTEMSATZ = (
    "Du beantwortest Fragen ausschliesslich aus den mitgelieferten Quellen. "
    "Steht die Antwort nicht darin, sage das klar und rate nicht. "
    "Nenne hinter jeder Aussage die Fundstelle in eckigen Klammern, "
    "zum Beispiel [Werkstatthandbuch, S. 214]. "
    "Antworte knapp, in ganzen Saetzen, auf Deutsch."
)


# --------------------------------------------------------------------------- Konfiguration
@dataclass
class Einstellung:
    """Was fuer einen Anbieter gebraucht wird."""
    anbieter: str = "lokal"
    adresse: str = "http://127.0.0.1:11434"
    modell: str = "qwen3.5-9b"
    einbettungsmodell: str = "qwen3-embedding-0.6b"
    zeitlimit: int = 300
    temperatur: float = 0.2
    max_zeichen: int = 4000            # so viel Quelltext geht hoechstens in den Prompt


@dataclass
class Konfiguration:
    modus: str = "lokal"               # lokal | online | auto
    lokal: Einstellung = field(default_factory=Einstellung)
    online: Einstellung = field(default_factory=lambda: Einstellung(
        anbieter="anthropic",
        adresse="https://api.anthropic.com",
        modell="claude-sonnet-5",
        einbettungsmodell="",          # Einbettungen bleiben grundsaetzlich lokal
    ))

    @classmethod
    def laden(cls) -> "Konfiguration":
        k = cls()
        if yaml and KONFIGDATEI.exists():
            roh = yaml.safe_load(KONFIGDATEI.read_text(encoding="utf-8")) or {}
            k.modus = roh.get("modus", k.modus)
            for name in ("lokal", "online"):
                teil = roh.get(name) or {}
                ziel = getattr(k, name)
                for feld, wert in teil.items():
                    if hasattr(ziel, feld):
                        setattr(ziel, feld, wert)
        k.modus = os.environ.get("QUINTESSENZ_MODUS", k.modus)
        return k


KONFIG = Konfiguration.laden()


def schluessel() -> str:
    return os.environ.get(SCHLUESSEL_VAR, "").strip()


# --------------------------------------------------------------------------- Hilfsmittel
def _post(url: str, daten: dict[str, Any], kopf: dict[str, str], zeitlimit: int) -> dict[str, Any]:
    anfrage = urllib.request.Request(
        url, data=json.dumps(daten).encode("utf-8"),
        headers={"Content-Type": "application/json", **kopf})
    with urllib.request.urlopen(anfrage, timeout=zeitlimit) as r:
        return json.loads(r.read().decode("utf-8"))


def verfuegbar(modus: str) -> tuple[bool, str]:
    """Kann in diesem Modus geantwortet werden? Gibt (ja, Begruendung) zurueck."""
    if modus == "lokal":
        e = KONFIG.lokal
        try:
            with urllib.request.urlopen(e.adresse + "/api/tags", timeout=3) as r:
                namen = [m["name"] for m in json.loads(r.read())["models"]]
            if not namen:
                return False, "Ollama laeuft, aber kein Modell geladen"
            return True, f"{len(namen)} Modelle lokal"
        except Exception as fehler:
            return False, f"Ollama nicht erreichbar ({type(fehler).__name__})"
    if not schluessel():
        return False, f"kein Schluessel in {SCHLUESSEL_VAR}"
    return True, f"Schluessel gesetzt, Anbieter {KONFIG.online.anbieter}"


def _quellenblock(fundstellen: list[dict[str, Any]], grenze: int) -> str:
    """Fundstellen in einen Textblock giessen, gekuerzt auf die Zeichengrenze."""
    teile, laenge = [], 0
    for i, f in enumerate(fundstellen, 1):
        kopf = f.get("titel") or f.get("quelle") or f"Fundstelle {i}"
        seite = f.get("seite")
        marke = f"[{kopf}{', S. ' + str(seite) if seite else ''}]"
        text = (f.get("text") or "").strip()
        stueck = f"{marke}\n{text}\n"
        if laenge + len(stueck) > grenze:
            stueck = stueck[: max(0, grenze - laenge)]
            if stueck:
                teile.append(stueck)
            break
        teile.append(stueck)
        laenge += len(stueck)
    return "\n".join(teile)


# --------------------------------------------------------------------------- Anbieter
def _ollama(e: Einstellung, system: str, frage: str, strom: bool):
    daten = {"model": e.modell, "stream": strom,
             "options": {"temperature": e.temperatur},
             "messages": [{"role": "system", "content": system},
                          {"role": "user", "content": frage}]}
    if not strom:
        return _post(e.adresse + "/api/chat", daten, {}, e.zeitlimit)["message"]["content"]

    def lauf() -> Iterator[str]:
        anfrage = urllib.request.Request(
            e.adresse + "/api/chat", data=json.dumps(daten).encode("utf-8"),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(anfrage, timeout=e.zeitlimit) as r:
            for zeile in r:
                if not zeile.strip():
                    continue
                stueck = json.loads(zeile)
                if stueck.get("message", {}).get("content"):
                    yield stueck["message"]["content"]
    return lauf()


def _openai(e: Einstellung, system: str, frage: str, strom: bool):
    kopf = {"Authorization": "Bearer " + schluessel()}
    daten = {"model": e.modell, "temperature": e.temperatur, "stream": False,
             "messages": [{"role": "system", "content": system},
                          {"role": "user", "content": frage}]}
    antwort_roh = _post(e.adresse.rstrip("/") + "/v1/chat/completions", daten, kopf, e.zeitlimit)
    text = antwort_roh["choices"][0]["message"]["content"]
    return iter([text]) if strom else text


def _anthropic(e: Einstellung, system: str, frage: str, strom: bool):
    kopf = {"x-api-key": schluessel(), "anthropic-version": "2023-06-01"}
    daten = {"model": e.modell, "max_tokens": 2000, "temperature": e.temperatur,
             "system": system, "messages": [{"role": "user", "content": frage}]}
    antwort_roh = _post(e.adresse.rstrip("/") + "/v1/messages", daten, kopf, e.zeitlimit)
    text = "".join(t.get("text", "") for t in antwort_roh.get("content", []))
    return iter([text]) if strom else text


ANBIETER = {"lokal": _ollama, "ollama": _ollama, "openai": _openai, "anthropic": _anthropic}


# --------------------------------------------------------------------------- Hauptweg
def antwort(frage: str, fundstellen: list[dict[str, Any]], modus: str | None = None,
            strom: bool = False) -> tuple[Any, str]:
    """Antwort auf eine Frage, gestuetzt auf die uebergebenen Fundstellen.

    modus: "lokal", "online", "auto" oder None (dann aus der Konfiguration).
    "auto" nimmt das lokale Modell und weicht nur aus, wenn es nicht laeuft.

    Gibt (Text oder Generator, Herkunft) zurueck. Herkunft ist "lokal" oder
    "online: <Anbieter>/<Modell>" und gehoert sichtbar in die Oberflaeche.
    """
    modus = modus or KONFIG.modus
    if modus == "auto":
        modus = "lokal" if verfuegbar("lokal")[0] else "online"

    e = KONFIG.lokal if modus == "lokal" else KONFIG.online
    ok, grund = verfuegbar(modus)
    if not ok:
        raise RuntimeError(f"Modus {modus} nicht nutzbar: {grund}")

    block = _quellenblock(fundstellen, e.max_zeichen)
    text = (f"QUELLEN\n{block}\n\nFRAGE\n{frage}\n\n"
            "Antworte nur aus den Quellen und nenne die Fundstelle.")

    ruf = ANBIETER.get(e.anbieter)
    if not ruf:
        raise RuntimeError(f"Unbekannter Anbieter: {e.anbieter}")
    ergebnis = ruf(e, SYSTEMSATZ, text, strom)
    herkunft = "lokal" if modus == "lokal" else f"online: {e.anbieter}/{e.modell}"
    return ergebnis, herkunft


def einbetten(texte: list[str]) -> list[list[float]]:
    """Einbettungen, immer lokal.

    Den gesamten Bestand ueber eine Schnittstelle einzubetten waere langsam und teuer,
    und beim Nachruesten neuer Quellen waere man wieder auf Netz angewiesen. Deshalb
    gibt es hier bewusst keinen Online-Weg.
    """
    e = KONFIG.lokal
    antwort_roh = _post(e.adresse + "/api/embed",
                        {"model": e.einbettungsmodell, "input": texte}, {}, e.zeitlimit)
    return antwort_roh["embeddings"]


def bericht() -> str:
    """Einzeiler fuer die Statusanzeige."""
    zeilen = []
    for m in ("lokal", "online"):
        ok, grund = verfuegbar(m)
        e = KONFIG.lokal if m == "lokal" else KONFIG.online
        zeilen.append(f"{m:7s} {'ja ' if ok else 'nein'}  {e.anbieter}/{e.modell or '-'}  ({grund})")
    return f"Modus: {KONFIG.modus}\n" + "\n".join(zeilen)


if __name__ == "__main__":
    print(bericht())
