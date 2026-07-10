#!/usr/bin/env bash
# Air-Gap-Export (AP 6.3): erstellt auf einer ONLINE-Maschine ein vollständiges
# Offline-Bundle (Images + Modell-Cache + Code) für die luftgetrennte Spark.
#
#   OUT=/mnt/stick/onlumis-bundle ./export-bundle.sh
#
# Vorher auf der Online-Maschine ausführen:
#   docker compose --profile models build
#   docker compose --profile models pull
#   ./models/download.sh <alle Modelle laut .env>
set -euo pipefail

PLATFORM_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="${OUT:-./onlumis-bundle}"
mkdir -p "$OUT"
cd "$PLATFORM_DIR"

echo "1/3 Docker-Images exportieren ..."
IMAGES=$(POSTGRES_PASSWORD=x KEYCLOAK_DB_PASSWORD=x KEYCLOAK_ADMIN_PASSWORD=x \
  docker compose -f compose.yml --profile models --profile monitoring config --images | sort -u)
echo "$IMAGES" > "$OUT/images.txt"
# shellcheck disable=SC2086
docker save $IMAGES | gzip > "$OUT/images.tar.gz"

echo "2/3 Modell-Cache exportieren (hf-cache-Volume) ..."
docker run --rm -v onlumis_hf-cache:/cache:ro -v "$(cd "$OUT" && pwd)":/out alpine \
  tar czf /out/hf-cache.tgz -C /cache .

echo "3/3 Code & Konfiguration ..."
git -C "$PLATFORM_DIR/.." archive --format=tar.gz -o "$OUT/onlumis-src.tar.gz" HEAD platform

echo "OK: Bundle unter $OUT"
du -sh "$OUT"/*
