#!/usr/bin/env bash
# Air-Gap-Import (AP 6.3): spielt ein export-bundle.sh-Bundle auf der
# OFFLINE-Spark ein.
#
#   ./import-bundle.sh /mnt/stick/onlumis-bundle
#
# Danach: .env pflegen (HF_HUB_OFFLINE=1 setzen!) und starten mit
#   docker compose -f compose.yml -f compose.airgap.yml --profile models up -d
set -euo pipefail

BUNDLE="${1:?Nutzung: ./import-bundle.sh <bundle-verzeichnis>}"

echo "1/3 Quellcode entpacken (falls noch nicht vorhanden) ..."
if [ -f "$BUNDLE/onlumis-src.tar.gz" ] && [ ! -f compose.yml ] && [ ! -d platform ]; then
  tar xzf "$BUNDLE/onlumis-src.tar.gz"
  echo "    -> ./platform entpackt; Skript künftig aus platform/deploy/airgap ausführen"
fi

echo "2/3 Docker-Images laden ..."
gunzip -c "$BUNDLE/images.tar.gz" | docker load

echo "3/3 Modell-Cache in Volume onlumis_hf-cache einspielen ..."
docker volume create onlumis_hf-cache >/dev/null
docker run --rm -v onlumis_hf-cache:/cache -v "$(cd "$BUNDLE" && pwd)":/in:ro alpine \
  sh -c "tar xzf /in/hf-cache.tgz -C /cache"

echo "OK. Nächste Schritte:"
echo "  1) cd platform && cp .env.example .env  (Passwörter setzen, HF_HUB_OFFLINE=1)"
echo "  2) docker compose -f compose.yml -f compose.airgap.yml --profile models up -d"
