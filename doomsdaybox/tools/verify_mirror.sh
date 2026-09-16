#!/usr/bin/env bash
# verify_mirror.sh – Integritätsprüfung und Paritätsdateien für alle Kopien (NVMe, USB-SSD, externe Platte).
# Aufruf:  ./verify_mirror.sh /srv/box            # prüft alle MANIFEST.sha256, erzeugt fehlende par2-Dateien
#          ./verify_mirror.sh /mnt/usb-ssd check  # nur prüfen, nichts erzeugen
# Voraussetzungen: sha256sum, par2 (par2cmdline), zimcheck optional
# Halbjährlich auf jeder Kopie laufen lassen; externe Platten dabei mindestens 1 h bestromt lassen.

set -euo pipefail
ROOT="${1:-/srv/box}"
MODE="${2:-full}"
REPORT="$ROOT/verify_$(date +%F).log"

echo "Prüfung $ROOT am $(date)" | tee "$REPORT"
fail=0

# 1) Prüfsummen-Manifeste aller Unterordner
find "$ROOT" -name MANIFEST.sha256 | while read -r m; do
  d="$(dirname "$m")"
  echo "== $d" | tee -a "$REPORT"
  ( cd "$d" && sha256sum -c MANIFEST.sha256 2>&1 | grep -v ': OK$' || true ) | tee -a "$REPORT"
done

# 2) ZIM-Eigenprüfsummen (langsam, nur bei Verdacht oder jährlich)
if command -v zimcheck >/dev/null 2>&1 && [ "$MODE" = "full" ]; then
  for z in "$ROOT"/zim/*.zim; do
    zimcheck -C "$z" >/dev/null 2>&1 || { echo "ZIM DEFEKT: $z" | tee -a "$REPORT"; fail=1; }
  done
fi

# 3) par2-Parität (10 %) für PDF, SQLite, eigenes Material – ZIM und PMTiles sind zu groß, dort genügt der Spiegel
if command -v par2 >/dev/null 2>&1; then
  for dir in pdf db own; do
    [ -d "$ROOT/$dir" ] || continue
    find "$ROOT/$dir" -type f \( -name '*.pdf' -o -name '*.db' -o -name '*.sqlite' -o -name '*.md' \) ! -name '*.par2' | while read -r f; do
      if [ -f "$f.par2" ]; then
        par2 verify -q "$f.par2" >/dev/null 2>&1 || { echo "PAR2-FEHLER (reparierbar mit: par2 repair '$f.par2'): $f" | tee -a "$REPORT"; }
      elif [ "$MODE" = "full" ]; then
        par2 create -q -r10 -n1 "$f.par2" "$f" >/dev/null 2>&1 || echo "par2 create fehlgeschlagen: $f" | tee -a "$REPORT"
      fi
    done
  done
fi

# 4) Manifest für eigenes Material aktualisieren (ändert sich am häufigsten)
if [ "$MODE" = "full" ]; then
  ( cd "$ROOT/own" && find . -type f ! -name MANIFEST.sha256 ! -name '*.par2' -print0 | xargs -0 sha256sum > MANIFEST.sha256 )
fi

echo "Belegung:" | tee -a "$REPORT"
du -sh "$ROOT"/* 2>/dev/null | tee -a "$REPORT"
echo "Bericht: $REPORT"

# Spiegeln auf USB-SSD (exFAT verträgt keine Rechte/Symlinks, daher -rlt statt -a):
#   rsync -rlt --delete --info=progress2 /srv/box/ /mnt/usb-ssd/box/
#   ./verify_mirror.sh /mnt/usb-ssd/box check
