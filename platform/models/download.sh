#!/usr/bin/env sh
# Lädt ein Hugging-Face-Modell in das geteilte hf-cache-Volume der Plattform.
# Nutzung: ./download.sh <hf-repo> [revision]
set -eu

REPO="${1:?Nutzung: ./download.sh <hf-repo> [revision]}"
REVISION="${2:-main}"
IMAGE="${VLLM_IMAGE:-nvcr.io/nvidia/vllm:latest}"

docker run --rm \
  -v onlumis_hf-cache:/root/.cache/huggingface \
  -e HF_HUB_ENABLE_HF_TRANSFER=1 \
  "$IMAGE" \
  huggingface-cli download "$REPO" --revision "$REVISION"

echo "OK: $REPO@$REVISION im Volume onlumis_hf-cache"
