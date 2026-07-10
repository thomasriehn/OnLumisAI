#!/bin/bash
# Legt beim Erststart des Postgres-Containers die Keycloak-Datenbank an.
# Läuft nur bei leerem Datenverzeichnis (docker-entrypoint-initdb.d).
set -euo pipefail

psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d postgres <<-EOSQL
	CREATE ROLE keycloak LOGIN PASSWORD '${KEYCLOAK_DB_PASSWORD}';
	CREATE DATABASE keycloak OWNER keycloak;
EOSQL
