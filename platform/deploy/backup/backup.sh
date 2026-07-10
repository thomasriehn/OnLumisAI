#!/usr/bin/env bash
# OnLumis-Backup (AP 6.2): Datenbanken (inkl. Keycloak), Uploads, Konfiguration,
# LoRA-Adapter. Läuft auf dem Host neben dem Compose-Stack.
#
#   BACKUP_DIR=/mnt/nas/onlumis KEEP=14 ./backup.sh
#
# Wiederherstellung: ./restore.sh <backup-verzeichnis>   (siehe RUNBOOK.md)
set -euo pipefail

PLATFORM_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/onlumis}"
KEEP="${KEEP:-14}"
COMPOSE="docker compose --project-directory $PLATFORM_DIR"

STAMP="$(date +%Y%m%d-%H%M%S)"
TARGET="$BACKUP_DIR/$STAMP"
mkdir -p "$TARGET"

echo "1/4 Datenbank-Dump (alle DBs inkl. keycloak) ..."
$COMPOSE exec -T postgres pg_dumpall -U onlumis | gzip > "$TARGET/postgres.sql.gz"

echo "2/4 Uploads-Volume ..."
docker run --rm -v onlumis_uploads:/data:ro -v "$TARGET":/backup alpine \
  tar czf /backup/uploads.tgz -C /data .

echo "3/4 Konfiguration & Adapter ..."
[ -f "$PLATFORM_DIR/.env" ] && cp "$PLATFORM_DIR/.env" "$TARGET/env.backup"
if [ -d "$PLATFORM_DIR/finetune/out" ]; then
  tar czf "$TARGET/adapters.tgz" -C "$PLATFORM_DIR/finetune" out
fi

echo "4/4 Rotation (behalte $KEEP) ..."
# shellcheck disable=SC2012
ls -1dt "$BACKUP_DIR"/*/ 2>/dev/null | tail -n +"$((KEEP + 1))" | xargs -r rm -rf

echo "OK: $TARGET"
du -sh "$TARGET"
