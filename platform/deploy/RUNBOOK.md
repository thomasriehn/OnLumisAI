# OnLumis Betriebs-Runbook (DGX Spark)

Zielgruppe: Technik/IT beim Kunden bzw. JULITH-Betrieb. Alle Kommandos laufen
im Verzeichnis `platform/` (empfohlen: `/opt/onlumis/platform`).

## 1. Erstinstallation auf der Spark

**Empfohlener Weg – Setup-Skript** (erledigt Schritte 3–5 und 7–9 automatisch,
inkl. NVFP4-Chatmodell, Beispielkorpus, goldener Fragen und Smoke-Test):

```bash
# Voraussetzungen: DGX OS mit LUKS, NGC-Login (docker login nvcr.io)
git clone <repo> /opt/onlumis && cd /opt/onlumis/platform
./deploy/setup-spark.sh --check-only                       # Vorprüfung
./deploy/setup-spark.sh --domain onlumis.firma.local \
    --model standard --with-monitoring --install-systemd
```

Modell-Presets (NVIDIA-NVFP4): `standard` (Qwen3.6-35B-A3B, schnell),
`qualitaet` (Nemotron-3-Super-120B), `klassisch` (Qwen3-32B), `kompakt`
(Llama-3.1-8B) – oder eine beliebige HF-ID. `--help` zeigt alle Optionen.

**Manuelle Schritte danach (macht kein Skript):**

6. **Keycloak anbinden:** `https://<domain>/auth` → Realm `onlumis` →
   *User Federation* → AD/LDAP konfigurieren; **Demo-Nutzer `demo` löschen**;
   in `.env` `AUTH_MODE=oidc` setzen und `docker compose up -d api webapp`.
7. **Echte Quellen anbinden:** über `https://<domain>/admin`
   (Admin-Handbuch §3); goldene Fragen kundenspezifisch ersetzen.

<details><summary>Manuelle Installation ohne Skript (Referenz)</summary>

1. `cp .env.example .env` – Pflichtwerte setzen (`POSTGRES_PASSWORD`,
   `KEYCLOAK_DB_PASSWORD`, `KEYCLOAK_ADMIN_PASSWORD`, `ONLUMIS_DOMAIN`).
2. Modelle laden: `./models/download.sh <CHAT_MODEL_ID aus .env>`, dazu
   `BAAI/bge-m3`, `BAAI/bge-reranker-v2-m3`, `openai/whisper-large-v3-turbo`.
3. `docker compose --profile models up -d --build`
4. Beispielquelle: `docker compose exec ingestion python -m worker.main
   add-source --name beispiel --root /data/sources/beispiel --acl all-users`
   und `… worker.main once`; goldene Fragen: `docker compose exec -T postgres
   psql -U onlumis -d onlumis < db/seed/eval-beispiel.sql`.
5. systemd-Units aus `deploy/systemd/` installieren (Pfade anpassen).

</details>

## 2. Smoke-Checks (nach Installation/Update/Restore)

```bash
curl -k https://localhost/api/readyz          # {"status":"ok","database":"ok"}
docker compose ps                             # alle Dienste "running"
docker compose logs --since 5m api | grep -i error || echo ok
# Fachlicher Check: im Chat eine bekannte Frage stellen -> Antwort MIT Quelle
# Eval-Gate: Verwaltung -> "Eval-Lauf starten" -> Raten mit Vorlauf vergleichen
```

## 3. PoC-/Lastmessung (AP 1.9 / 6.1)

```bash
.venv/bin/python deploy/bench/loadtest.py \
  --base-url https://<domain>/api --api-key olk_... --insecure \
  --users 10 --duration 120
```
Zielwerte: TTFT p50 < 2 s, p95 < 6 s. Bei Verfehlung: kleineres/stärker
quantisiertes Chatmodell (`CHAT_MODEL_ID`), `CHAT_MAX_MODEL_LEN` senken oder
zweite Spark (Architektur §11).

## 4. Updates (monatliches Wartungsfenster)

```bash
cd /opt/onlumis && git pull                   # bzw. neues Bundle einspielen
cd platform
docker compose --profile models build
docker compose --profile models up -d         # rollt geänderte Dienste neu
# danach Smoke-Checks (§2) + Eval-Lauf als Regressionsgate
```
Modell-/Adapterwechsel: Manifest ergänzen, Modell laden, `.env` anpassen,
Eval-Gate (`finetune/rollout.py` für Adapter), Wartungsfenster.

## 5. Backup & Restore (AP 6.2)

- Nächtlich automatisch via `onlumis-backup.timer` → `deploy/backup/backup.sh`
  (Postgres inkl. Keycloak, Uploads, `.env`, Adapter; Rotation `KEEP=14`).
  `BACKUP_DIR` auf ein NAS legen!
- Manuell: `BACKUP_DIR=/mnt/nas/onlumis deploy/backup/backup.sh`
- Restore: `deploy/backup/restore.sh <backup-verzeichnis>` → Smoke-Checks.
- Halbjährliche Restore-Übung durchführen und protokollieren.

## 6. Air-Gap-Betrieb (A8)

Auf einer Online-Maschine: Images bauen/pullen, Modelle laden, dann
`deploy/airgap/export-bundle.sh`. Auf der Offline-Spark:
`deploy/airgap/import-bundle.sh <bundle>` → `.env` mit `HF_HUB_OFFLINE=1` →
`docker compose -f compose.yml -f compose.airgap.yml --profile models up -d`.
Updates laufen als neues Bundle über denselben Weg.

## 7. Störungsdiagnose

| Symptom | Diagnose | Behebung |
|---|---|---|
| Chat: „Upstream-Fehler" / 502 | `docker compose logs vllm-chat` | Modell lädt noch (Erststart dauert Minuten) oder OOM → `CHAT_GPU_MEM_FRACTION`/`CHAT_MAX_MODEL_LEN` senken |
| Antworten ohne Quellen bei bekannten Docs | Verwaltung → Quelle → letzter Sync | Sync-Fehler beheben; `docker compose logs ingestion` |
| 401 nach Login | Uhrzeit/NTP der Spark, `OIDC_ISSUER_URL` erreichbar? | Zeit synchronisieren; Issuer-URL muss der öffentlichen Domain entsprechen |
| „keine belastbare Quelle" häufig | Verwaltung → Wissenslücken | fehlende Inhalte anbinden; ggf. `MIN_RERANK_SCORE` senken |
| Suche langsam | `docker compose exec postgres psql … -c 'ANALYZE knowledge.chunks;'` | nach Groß-Importen ANALYZE/REINDEX; Grafana-Dashboards prüfen |
| Diskfüllstand | `docker system df`, Backups, hf-cache | alte Images `docker image prune`, Backup-Rotation prüfen |
| Rate-Limit-Beschwerden | Audit/Nutzung prüfen | `RATE_LIMIT_PER_MINUTE` anpassen (0 = aus) |

## 8. Dienste & Ports (intern)

proxy :443 (einziger exponierter Port) · webapp :3000 · api :8000 ·
keycloak :8080 · postgres :5432 · redis :6379 · vllm-chat :8001 ·
vllm-embed :8002 · vllm-rerank :8003 · vllm-whisper :8005 ·
prometheus :9090 · grafana :3001 (Pfad `/grafana`).
