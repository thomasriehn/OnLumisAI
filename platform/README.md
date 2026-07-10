# OnLumis-Plattform

Implementierung der lokalen Unternehmens-KI aus dem
[Architekturmodell](../docs/architektur.md) und dem
[Implementierungsplan](../docs/implementierungsplan.md): RAG mit Quellenangaben
auf Basis von **vLLM** (DGX Spark), **PostgreSQL + pgvector** (dockerisiert),
FastAPI-Orchestrator und Next.js-Chat-UI.

> Dieses Verzeichnis ist als eigenständiges Monorepo geschnitten (Plan §5) und
> kann später per `git subtree split` in das Repo `onlumis-platform` ausgelagert
> werden.

## Dienste

| Dienst | Technologie | Aufgabe |
|---|---|---|
| `proxy` | Caddy | TLS-Terminierung, einziger exponierter Port (443) |
| `webapp` | Next.js 16 | **OIDC-Login (PKCE, httpOnly-Cookies)**, Chat mit Konversations-Sidebar, Spracheingabe (Mikrofon), klickbaren Quellen; Intranet-Suche (`/suche`); Admin-Portal (`/admin`: Quellen, Upload, Feedback, Evals, Wissenslücken). BFF-Routen unter `/bff/*` |
| `api` | FastAPI | RAG-Orchestrator: Auth (OIDC/API-Keys), Hybrid-Retrieval (RRF) + Reranking mit **Konfidenz-Schwelle**, Query-Rewriting, **Prompt-Profile je Gruppe**, Zitate, Quellen-Viewer, Audit + **Retention**, Rate-Limit, Eval-Harness, **Wissenslücken-Report**, Transkription, **MCP-Server** (`/api/mcp`: search, answer, draft) |
| `ingestion` | Python-Worker | Konnektoren (Dateisystem, Confluence, SharePoint, IMAP, **Jira, WebDAV/DMS, Google Drive**), Parsing (simple/**Docling**, OCR-Fallback), **Audio-Transkription**, Chunking, Embeddings, Delta-Sync + Tombstones |
| `postgres` | pgvector/pg17 | Wissensbasis (Chunks, Embeddings, ACLs), App-Daten, Audit-Log, Eval-Daten |
| `keycloak` | Keycloak 26 | OIDC mit Realm-Import (`deploy/keycloak/`); AD/LDAP-Federation im Realm konfigurierbar |
| `vllm-chat/-embed/-rerank/-whisper` | NGC vLLM | Modell-Serving auf der Spark (`--profile models`) |
| `redis` | Redis 7 | Queue/Cache (Jobqueue-Ausbau bei Parallel-Syncs) |
| `prometheus`/`grafana` | – | Monitoring (`--profile monitoring`) |

## Quickstart auf der DGX Spark

```bash
cp .env.example .env        # Passwörter setzen!
./models/download.sh Qwen/Qwen3-32B-FP8      # Modelle vorab laden
./models/download.sh BAAI/bge-m3
./models/download.sh BAAI/bge-reranker-v2-m3

docker compose --profile models up -d --build

# Wissensquelle registrieren (Pfad liegt unter SOURCES_PATH aus .env,
# im Container unter /data/sources):
docker compose exec ingestion python -m worker.main add-source \
  --name handbuecher --root /data/sources/beispiel --acl all-users
docker compose exec ingestion python -m worker.main once   # Erst-Sync sofort
```

Danach: `https://<ONLUMIS_DOMAIN>/` (Chat), `/suche` (Intranet-Suche),
`/admin` (Verwaltung), `/api/docs` (OpenAPI), `/api/mcp` (MCP-Endpoint für
Agenten), `/auth` (Keycloak). Die Beispieldokumente unter
`data/sources/beispiel/` machen das System sofort befragbar.

**Keycloak:** Beim Erststart wird das Realm `onlumis` importiert
(`deploy/keycloak/realm-onlumis.json`) – inkl. Gruppen (`all-users`,
`onlumis-admin`, `onlumis-auditor`, …), Groups-Claim-Mapper und einem
Demo-Nutzer `demo`/`demo`. **Vor Produktivbetrieb:** Demo-Nutzer entfernen,
AD/LDAP-Federation im Realm einrichten (Keycloak-Admin → User Federation) und
`AUTH_MODE=oidc` setzen.

## Entwicklung ohne GPU

```bash
docker compose -f compose.yml -f compose.dev.yml up -d --build
```

Embeddings laufen dabei auf CPU (TEI, gleiches BGE-M3-Modell), als Chat-LLM
dient ein beliebiger OpenAI-kompatibler Endpoint auf dem Host (z. B. Ollama,
`DEV_CHAT_BASE_URL`). Auth steht auf `dev` (X-Dev-Header, setzt der
Webapp-Server serverseitig).

## Tests

```bash
python3 -m venv .venv
.venv/bin/pip install -e "./services/api[test]" -e "./services/ingestion[test]"

# Integrationstests erwarten eine pgvector-Instanz (sonst: skip):
docker run -d --name onlumis-test-pg \
  -e POSTGRES_DB=onlumis -e POSTGRES_USER=onlumis -e POSTGRES_PASSWORD=test \
  -e KEYCLOAK_DB_PASSWORD=test -p 127.0.0.1:55432:5432 pgvector/pgvector:pg17

.venv/bin/python -m pytest
```

Die Integrationstests decken den Kernpfad ab: Ingestion → pgvector →
Hybrid-Suche (Vektor + Volltext + RRF) → **ACL-Negativtests** → Tombstones.

## Umsetzungsstand (Referenz: Implementierungsplan)

| Bereich | Stand |
|---|---|
| **Phase 0** Compose-Stack, Netze, TLS-Proxy, Secrets-Schema, Modell-Manifeste | ✅ umgesetzt |
| **Phase 1** DB-Schema, Dateisystem-Konnektor, Parsing, Chunking, Sync-Runner, RAG-API, Chat-UI | ✅ umgesetzt + getestet (Ende-zu-Ende inkl. Browser-Test) |
| Hybrid-Suche (pgvector-HNSW + tsvector-`german` + RRF) & Reranker | ✅ umgesetzt + getestet |
| **Phase 2** Dokument-ACLs (SQL-seitig) + Pfadregel-ACLs, ACL-Testsuite (HTTP-Ebene) | ✅ umgesetzt + Negativtests |
| Phase 2 OIDC: Keycloak-Realm-Import (Groups-Mapper), JWKS-Validierung | ✅ E2E gegen echtes Keycloak verifiziert; AD-Federation = Realm-Konfiguration beim Kunden |
| Phase 2 API-Keys (gehasht, Scopes, ACL-Gruppen), Rate-Limit, Audit-Export (JSON/CSV, Auditor-Rolle) | ✅ umgesetzt + getestet |
| Phase 2 DSGVO-Paket (AVV/TOMs-Dokumente) | ⬜ juristische Vorlagen, kein Code |
| **Phase 3** Konnektor-Framework (Version/ETag-Engine) + Confluence, SharePoint (Graph), IMAP | ✅ umgesetzt + Mock-/Integrationstests; Test gegen echte Systeme beim Piloten |
| Phase 3 Query-Rewriting aus Konversationskontext | ✅ umgesetzt + getestet (abschaltbar) |
| **Phase 4** MCP-Server (`search_knowledge`, `answer_with_sources`) | ✅ Roundtrip mit offiziellem MCP-Client inkl. ACL-Negativtest |
| Phase 4 Admin-Portal (Quellen, Stats, Feedback-Queue, Evals) + Such-Seite | ✅ umgesetzt, Browser-getestet |
| Phase 4 Teams-Bot | ⬜ bewusst offen: Hybrid-Feature, erfordert Azure-Bot-Registrierung des Kunden |
| **Phase 5** Eval-Harness (goldene Fragen, Runs, Gate-Endpoint) | ✅ umgesetzt + getestet |
| Phase 5 Feedback-Kuratierung + JSONL-Export | ✅ umgesetzt + getestet |
| Phase 5 LoRA-Pipeline (`finetune/`: Dataset-Builder, QLoRA-Training, Synth-QA, Rollout mit Eval-Gate) | ✅ Skripte + getesteter Dataset-Builder; Trainingslauf braucht Spark-GPU |
| OCR-Fallback für Scans (Tesseract, Build-Arg `WITH_OCR=1`) | ✅ Wiring + Tests; Tesseract-Lauf auf Zielsystem |
| **Login** OIDC in der Webapp (PKCE, httpOnly-Cookies, Refresh, Logout) | ✅ E2E im Browser gegen echtes Keycloak verifiziert |
| **Quick Wins** Konversations-Sidebar (+Löschen), Quellen-Viewer (ACL + Traversal-Schutz), Upload-Portal, Retention-Job | ✅ umgesetzt + getestet (HTTP + Browser) |
| **Qualität** Konfidenz-Schwelle/No-Hit-Kurzschluss, Prompt-Profile je Gruppe, Docling-Backend (`PARSING_BACKEND=docling`, `.[docling]`) | ✅ umgesetzt + getestet |
| **Abdeckung** Jira-, WebDAV-(DMS)-, Google-Drive-Konnektor; Whisper-Service, Audio-Ingestion | ✅ Mock-/Integrationstests; echte Systeme beim Piloten |
| **Spracheingabe** Mikrofon in Chat/Suche → lokales Whisper (`/v1/transcriptions`) | ✅ UI + Endpoint getestet; Whisper-Modell läuft auf der Spark |
| **Strategisch** Wissenslücken-Report (Zero-Hit-Fragen, pseudonymisiert) + MCP-Tool `draft_text` | ✅ umgesetzt + getestet |
| **Phase 6** Backup/Restore (`deploy/backup/`, systemd-Timer) | ✅ Skripte + Roundtrip gegen echtes Postgres verifiziert |
| Phase 6 Air-Gap-Bundle (`deploy/airgap/`, `compose.airgap.yml`) | ✅ Export/Import-Tooling, Compose-Override validiert |
| Phase 6 Lasttest-Tool (`deploy/bench/loadtest.py`, TTFT/Durchsatz/429) | ✅ live gegen Dev-Stack verifiziert; Messung auf der Spark = AP 1.9 |
| Phase 6 Betriebs-/Nutzerdoku: `deploy/RUNBOOK.md`, `docs/admin-handbuch.md`, DSGVO-Paket (`docs/dsgvo/`), Eval-Seed (`db/seed/`) | ✅ erstellt (DSGVO: Vorlagen mit juristischem Prüfvorbehalt) |
| Phase 6 Ausführung auf Ziel-Hardware: PoC-Messung, Restore-Übung, Pentest, Pilotbetrieb | ⬜ Deployment (Runbook §§2–5 führen durch) |

## Struktur

```
platform/
  compose.yml / .dev.yml / .airgap.yml   Stack (Spark, Dev ohne GPU, offline)
  .env.example                    Konfiguration
  db/init/  db/seed/              Schema + goldene Starterfragen
  deploy/                         Caddy, Keycloak-Realm, Monitoring,
                                  backup/, airgap/, bench/, systemd/, RUNBOOK.md
  models/                         Modell-Manifeste + Download (Air-Gap-fähig)
  services/api/                   FastAPI RAG-Orchestrator + MCP-Server
  services/ingestion/             Konnektoren, Parsing/OCR, Chunking, Indexer
  services/webapp/                Next.js: Chat, Suche, Admin-Portal
  finetune/                       LoRA-Pipeline (Dataset, Training, Rollout-Gate)
  data/sources/beispiel/          Demo-Korpus für den Quickstart
  tests/                          Ende-zu-Ende- und HTTP-Integrationstests
```
