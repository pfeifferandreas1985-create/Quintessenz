#!/usr/bin/env bash
# Holt den gesamten Wissensbestand der DoomsdayBox aus dem Netz. Ein Befehl, vier Phasen.
#
#   1. zim       Kiwix-Archive (Wikipedia, Fachforen, Lehrbuecher, Gutenberg)  ~360 GB
#   2. maps      Karten, Ortsdatenbank, Routing-Rohdaten                       ~210 GB
#   3. models    Sprachmodelle fuer den Pi                                      ~27 GB
#   4. software  ARM64-Programme, Pi OS, Python-Pakete                           ~1 GB
#
# Jede Phase ist fortsetzbar: abbrechen, neu aufrufen, es geht an der Abbruchstelle weiter.
# Jede Datei wird gegen die offizielle Pruefsumme geprueft und ins Manifest eingetragen.
#
#   ./alles_holen.sh                      # nach /srv/box, alles
#   ZIEL=/mnt/platte/box ./alles_holen.sh # anderes Ziel
#   PHASEN="zim maps" PRIO=2 ./alles_holen.sh
set -u

ZIEL="${ZIEL:-/srv/box}"
ARK="${ARK:-$ZIEL/../AI-ARK}"
PHASEN="${PHASEN:-zim maps models software}"
PRIO="${PRIO:-3}"
WERKZEUGE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

command -v python3 >/dev/null || { echo "python3 fehlt: sudo apt install python3" >&2; exit 1; }
mkdir -p "$ZIEL"

# Dateisystem pruefen: auf FAT32 sind Dateien ueber 4 GB unmoeglich, Wikipedia allein ist groesser.
fs="$(df -T "$ZIEL" | awk 'NR==2{print $2}')"
case "$fs" in
  vfat|msdos) echo "FEHLER: $ZIEL liegt auf $fs. Dateien ueber 4 GB sind dort unmoeglich." >&2; exit 1;;
esac

echo "DoomsdayBox: Wissensbestand holen"
echo "  Ziel   $ZIEL   ($fs)"
echo "  Phasen $PHASEN   Prioritaet bis $PRIO"
echo

start=$(date +%s)
for phase in $PHASEN; do
  echo "== Phase $phase =============================="
  python3 "$WERKZEUGE/ddbox_fetch.py" "$phase" --root "$ZIEL" --ark "$ARK" --max-prio "$PRIO" \
    || echo "Phase $phase abgebrochen. Befehl spaeter erneut aufrufen, es wird fortgesetzt."
done

dauer=$(( ($(date +%s) - start) / 3600 ))
echo
echo "Fertig nach ${dauer} h. Bestand: $(du -sh "$ZIEL" | cut -f1) in $ZIEL"
echo "Pruefen:  python3 \"$WERKZEUGE/ddbox_fetch.py\" verify --root \"$ZIEL\""
echo "Logbuch:  $ZIEL/LOGBUCH.md"
