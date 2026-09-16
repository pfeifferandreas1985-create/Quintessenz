#!/usr/bin/env bash
# download_zim.sh – lädt die neueste Ausgabe jeder ZIM-Datei aus zim_manifest.tsv,
# prüft SHA-256 (falls Kiwix eine .sha256-Datei anbietet) und zusätzlich mit zimcheck
# (eingebaute Prüfsumme), schreibt MANIFEST.sha256 fort.
#
# Aufruf:  ./download_zim.sh [ZIELVERZEICHNIS] [MAX_PRIO]
#          ./download_zim.sh /srv/box/zim 3        # Voll: alles
#          ./download_zim.sh /srv/box/zim 1        # nur Prioritaet 1
# Voraussetzungen: bash, curl, aria2c (oder wget), sha256sum, zimcheck (zim-tools), xmllint (libxml2)
# Laufzeit fuer Voll: mehrere Tage, ca. 220 GB. Skript ist wiederaufnehmbar (aria2c -c).

set -euo pipefail

DEST="${1:-/srv/box/zim}"
MAX_PRIO="${2:-3}"
STAGE="${3:-}"            # optional: Zwischenspeicher auf interner SSD (z. B. /c/stage); Download dorthin, danach Verschieben.
                          # Sinnvoll bei externen HDDs (SMR) – aria2 schreibt segmentiert, das mag eine HDD nicht.
MANIFEST="$(dirname "$0")/zim_manifest.tsv"

# Dateisystem-Sperre: FAT32 kann keine Datei >4 GB speichern; fast jede ZIM-Datei ist größer.
fs_check() {
  local fs
  fs="$(df -T "$1" 2>/dev/null | awk 'NR==2{print tolower($2)}')"
  case "$fs" in
    vfat|fat32|msdos|fat) echo "ABBRUCH: $1 liegt auf FAT32 ($fs). 4-GB-Dateigrenze. Platte auf exFAT oder NTFS formatieren."; exit 2 ;;
    "") echo "WARNUNG: Dateisystem von $1 nicht erkennbar – FAT32 wäre fatal, bitte manuell prüfen." ;;
    *) echo "Dateisystem $1: $fs" ;;
  esac
}
CATALOG="https://library.kiwix.org/catalog/v2/entries"
MIRROR="https://download.kiwix.org/zim"
LOG="$DEST/download_zim.log"

mkdir -p "$DEST"
fs_check "$DEST"
if [ -n "$STAGE" ]; then mkdir -p "$STAGE"; fs_check "$STAGE"; fi
touch "$DEST/MANIFEST.sha256"

log() { printf '%s %s\n' "$(date '+%F %T')" "$*" | tee -a "$LOG"; }

need() { command -v "$1" >/dev/null 2>&1 || { echo "fehlt: $1"; exit 1; }; }
need curl; need sha256sum
DL=""
if command -v aria2c >/dev/null 2>&1; then DL="aria2"; elif command -v wget >/dev/null 2>&1; then DL="wget"; else echo "aria2c oder wget fehlt"; exit 1; fi
HAVE_ZIMCHECK=0; command -v zimcheck >/dev/null 2>&1 && HAVE_ZIMCHECK=1
HAVE_XMLLINT=0; command -v xmllint >/dev/null 2>&1 && HAVE_XMLLINT=1

# 1) Neueste Datei-URL ueber den OPDS-Katalog (name=...) ermitteln
resolve_catalog() {
  local prefix="$1"
  [ "$HAVE_XMLLINT" -eq 1 ] || return 1
  local xml
  xml="$(curl -fsSL "$CATALOG?name=$prefix&count=1" 2>/dev/null)" || return 1
  # Link auf .meta4 -> .zim
  printf '%s' "$xml" | xmllint --xpath 'string(//*[local-name()="link"][@type="application/x-zim"]/@href)' - 2>/dev/null \
    | sed 's/\.meta4$//' | grep -E '\.zim$' || return 1
}

# 2) Fallback: Verzeichnisliste des Spiegels nach Prefix durchsuchen, juengstes Datum nehmen
resolve_listing() {
  local prefix="$1" category="$2"
  local list
  for cat in "$category" wikipedia wikibooks wiktionary wikiversity stack_exchange ifixit gutenberg wikihow devdocs other; do
    list="$(curl -fsSL "$MIRROR/$cat/" 2>/dev/null | grep -oE "href=\"${prefix}_[0-9]{4}-[0-9]{2}\.zim\"" | sed 's/href="//; s/"$//' | sort | tail -n1)" || true
    if [ -n "$list" ]; then printf '%s/%s/%s\n' "$MIRROR" "$cat" "$list"; return 0; fi
  done
  return 1
}

download() {
  local url="$1" out="$2"
  local tmp="$out"
  [ -n "$STAGE" ] && tmp="$STAGE/$(basename "$out")"
  case "$DL" in
    # Ohne STAGE (Ziel = HDD): eine Verbindung, sequentielles Schreiben. Mit STAGE (SSD): 4 Segmente.
    aria2) if [ -n "$STAGE" ]; then
             aria2c -c -x 4 -s 4 --file-allocation=none --console-log-level=warn -d "$(dirname "$tmp")" -o "$(basename "$tmp")" "$url"
           else
             aria2c -c -x 1 -s 1 --file-allocation=none --console-log-level=warn -d "$(dirname "$tmp")" -o "$(basename "$tmp")" "$url"
           fi ;;
    wget)  wget -c -q --show-progress -O "$tmp" "$url" ;;
  esac
  if [ -n "$STAGE" ]; then
    log "  verschiebe nach $DEST"
    mv -f "$tmp" "$out"            # geräteübergreifend = Kopie + Löschen, sequentiell, HDD-freundlich
  fi
}

verify() {
  local url="$1" file="$2" ok=0
  # a) offizielle .sha256, falls vorhanden
  local remote
  if remote="$(curl -fsSL "$url.sha256" 2>/dev/null)"; then
    local want have
    want="$(printf '%s' "$remote" | awk '{print $1}')"
    have="$(sha256sum "$file" | awk '{print $1}')"
    if [ "$want" = "$have" ]; then log "  SHA-256 OK (offiziell)"; ok=1; else log "  SHA-256 FEHLER: $file"; return 1; fi
  fi
  # b) eingebaute ZIM-Pruefsumme
  if [ "$HAVE_ZIMCHECK" -eq 1 ]; then
    if zimcheck -C "$file" >/dev/null 2>&1; then log "  zimcheck OK"; ok=1; else log "  zimcheck FEHLER: $file"; return 1; fi
  fi
  [ "$ok" -eq 1 ] || log "  WARNUNG: keine Pruefsumme verfuegbar (weder .sha256 noch zimcheck)"
  # c) in lokales Manifest eintragen (fuer spaetere Spiegel-Pruefung mit sha256sum -c)
  grep -q " $(basename "$file")\$" "$DEST/MANIFEST.sha256" || sha256sum "$file" | sed "s# .*/# #" >> "$DEST/MANIFEST.sha256"
  return 0
}

log "Start, Ziel=$DEST, max. Prioritaet=$MAX_PRIO, Downloader=$DL"
tail -n +2 "$MANIFEST" | while IFS=$'\t' read -r prefix category prio size note; do
  [ -z "$prefix" ] && continue
  [ "$prio" -le "$MAX_PRIO" ] || { log "skip (Prio $prio): $prefix"; continue; }

  # bereits vorhandene Ausgabe?
  existing="$(ls -1 "$DEST"/"${prefix}"_????-??.zim 2>/dev/null | sort | tail -n1 || true)"

  url="$(resolve_catalog "$prefix" || true)"
  [ -n "$url" ] || url="$(resolve_listing "$prefix" "$category" || true)"
  if [ -z "$url" ]; then log "NICHT GEFUNDEN: $prefix ($note) – Name im Katalog pruefen"; continue; fi

  fname="$(basename "$url")"
  target="$DEST/$fname"
  if [ -n "$existing" ] && [ "$(basename "$existing")" = "$fname" ] && [ ! -f "$target.aria2" ]; then
    log "aktuell: $fname"; continue
  fi

  log "lade ($size GB, Prio $prio): $fname – $note"
  if download "$url" "$target"; then
    if verify "$url" "$target"; then
      # alte Ausgabe erst nach erfolgreicher Pruefung entfernen
      if [ -n "$existing" ] && [ "$existing" != "$target" ]; then
        log "  entferne alte Ausgabe $(basename "$existing")"; rm -f "$existing"
        sed -i "\# $(basename "$existing")\$#d" "$DEST/MANIFEST.sha256"
      fi
    else
      log "  Pruefung fehlgeschlagen, Datei wird umbenannt"; mv "$target" "$target.BAD"
    fi
  else
    log "  Download abgebrochen: $fname (Wiederaufnahme beim naechsten Lauf)"
  fi
done

# Kiwix-Bibliothek neu aufbauen
if command -v kiwix-manage >/dev/null 2>&1; then
  rm -f "$DEST/library.xml"
  for z in "$DEST"/*.zim; do kiwix-manage "$DEST/library.xml" add "$z" >/dev/null; done
  log "library.xml aktualisiert ($(ls -1 "$DEST"/*.zim | wc -l) ZIM-Dateien)"
fi
log "Fertig. Gesamt: $(du -sh "$DEST" | cut -f1)"
