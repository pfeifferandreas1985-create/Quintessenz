#!/usr/bin/env bash
# download_models.sh – Modelle für die Pi-5-Box (16 GB RAM, CPU) laden.
# Aufruf:   ./download_models.sh [ZIEL] [MAX_PRIO] [AI-ARK-MODELLORDNER]
#           ./download_models.sh /d/DoomsdayBox/models 3 /d/AI-ARK/01_MODELS
# Voraussetzung: pip install -U "huggingface_hub[cli]"   (Befehl: hf  oder  huggingface-cli)
#
# Modellauswahl: identisch mit dem Bereich "minimal" + "embedding" des AI-ARK-Archivs (D:\AI-ARK\01_INVENTAR.md),
# dessen 15 Repo-Namen am 15.09.2026 gegen die Hugging-Face-API geprüft wurden. Liegt eine Datei dort schon,
# wird sie kopiert statt erneut geladen (dritter Parameter).
# Dateinamen werden über Muster (--include) gewählt, damit Umbenennungen der Anbieter nicht sofort brechen.

set -euo pipefail
DEST="${1:-/srv/box/models}"
MAX_PRIO="${2:-3}"
ARK="${3:-}"
mkdir -p "$DEST"

fs="$(df -T "$DEST" 2>/dev/null | awk 'NR==2{print tolower($2)}')"
case "$fs" in vfat|fat32|msdos|fat) echo "ABBRUCH: $DEST ist FAT32 (4-GB-Grenze). exFAT oder NTFS nötig."; exit 2;; esac

HF=""; command -v hf >/dev/null 2>&1 && HF="hf"; [ -z "$HF" ] && command -v huggingface-cli >/dev/null 2>&1 && HF="huggingface-cli"
[ -n "$HF" ] || { echo "hf / huggingface-cli fehlt: pip install -U 'huggingface_hub[cli]'"; exit 1; }

# prio | repo | include-Muster | Zweck auf dem Pi 5 (16 GB)
MODELS=$(cat <<'EOF'
1|unsloth/Qwen3.5-9B-GGUF|*Q4_K_M*.gguf|Hauptmodell Text (~6 GB, ~2-3 tok/s, 262k Kontext)
1|unsloth/gemma-4-E4B-it-GGUF|*Q4_K_M*.gguf|Schnelles Modell mit Bild + Audio (~4,5 GB, Typenschild-Fotos)
1|unsloth/gemma-4-E4B-it-GGUF|mmproj*|Vision-/Audio-Projektor zu Gemma 4 E4B
1|Qwen/Qwen3-Embedding-0.6B-GGUF|*Q8_0*.gguf|Embedding für RAG (~0,6 GB, mehrsprachig)
2|unsloth/gemma-4-E2B-it-GGUF|*Q4_K_M*.gguf|Notmodell, läuft auch auf 4-GB-Geräten (~3 GB)
2|unsloth/gemma-4-E2B-it-GGUF|mmproj*|Projektor zu Gemma 4 E2B
2|unsloth/Qwen3.5-0.8B-GGUF|*Q8_0*.gguf|Kleinstmodell für Klassifikation/Zusammenfassung (~0,8 GB)
2|nomic-ai/nomic-embed-text-v1.5-GGUF|*Q8_0*.gguf|Embedding-Notnagel (~0,3 GB)
2|ggerganov/whisper.cpp|ggml-medium.bin|Sprache→Text (1,5 GB)
2|ggerganov/whisper.cpp|ggml-small.bin|Sprache→Text schnell (0,5 GB)
3|unsloth/granite-4.0-h-1b-GGUF|*Q8_0*.gguf|Kleinstmodell, dokumentierte Trainingsdaten
3|rhasspy/piper-voices|de/de_DE/thorsten/medium/*|Text→Sprache Deutsch
EOF
)
# Reranker: BAAI/bge-reranker-v2-m3 liegt in AI-ARK als safetensors; für llama.cpp eine GGUF-Fassung suchen:
#   hf search "bge-reranker-v2-m3 gguf"   (z. B. gpustack/bge-reranker-v2-m3-GGUF)  – manuell prüfen und ergänzen.

echo "$MODELS" | while IFS='|' read -r prio repo pattern purpose; do
  [ -z "$prio" ] && continue
  [ "$prio" -le "$MAX_PRIO" ] || continue
  sub="$DEST/$(basename "$repo")"
  if [ -d "$sub" ] && find "$sub" -type f -name "${pattern##*/}" | grep -q .; then echo "vorhanden: $repo ($pattern)"; continue; fi

  # 1) Aus AI-ARK übernehmen, falls dort schon geladen (vollständige Dateien, keine .incomplete)
  if [ -n "$ARK" ] && [ -d "$ARK" ]; then
    hit="$(find "$ARK" -type f -path "*$(basename "$repo")*" -name "${pattern##*/}" ! -name '*.incomplete' ! -path '*/.cache/*' | head -n1 || true)"
    if [ -n "$hit" ]; then mkdir -p "$sub"; echo "übernehme aus AI-ARK: $hit"; cp "$hit" "$sub/"; continue; fi
  fi

  # 2) Laden
  echo "lade (Prio $prio): $repo  $pattern  – $purpose"
  if $HF download "$repo" --include "$pattern" --local-dir "$sub" >/dev/null; then
    rm -rf "$sub/.cache"
  else
    echo "   FEHLER: $repo (Lizenz nicht akzeptiert? Muster ohne Treffer? -> hf search / Repo-Seite prüfen)"
  fi
done

# Prüfsummen: Hugging Face liefert SHA-256 in den LFS-Metadaten der Repo-Seite (Klick auf die Datei).
# Lokales Manifest für Spiegelprüfung:
( cd "$DEST" && find . -type f -name '*.gguf' -o -name '*.bin' -o -name '*.onnx' | xargs -d '\n' sha256sum > MANIFEST.sha256 2>/dev/null || true )
echo "Fertig: $(du -sh "$DEST" | cut -f1) in $DEST"

# Schnelltest auf dem Pi (llama.cpp aus D:\AI-ARK\00_RUNTIME\llamacpp\llama-*-bin-ubuntu-arm64.tar.gz):
#   llama-cli -m models/Qwen3.5-9B-GGUF/*Q4_K_M*.gguf -p "Nenne die fünf Sicherheitsregeln." -n 200
#   llama-server -m models/gemma-4-E4B-it-GGUF/*Q4_K_M*.gguf --mmproj models/gemma-4-E4B-it-GGUF/mmproj*.gguf -c 8192 --port 8080
#   llama-server -m models/Qwen3-Embedding-0.6B-GGUF/*Q8_0*.gguf --embedding --port 8081
