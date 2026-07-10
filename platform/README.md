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
| `webapp` | Next.js 16 | Chat-UI mit Streaming, Quellen-Panel, Feedback |
| `api` | FastAPI | RAG-Orchestrator: Auth, Hybrid-Retrieval (RRF) + Reranking, Zitate, Audit |
| `ingestion` | Python-Worker | Dateisystem-Konnektor, Parsing (MD/TXT/HTML/PDF/DOCX), Chunking, Embeddings, Delta-Sync + Tombstones |
| `postgres` | pgvector/pg17 | Wissensbasis (Chunks, Embeddings, ACLs), App-Daten, Audit-Log |
| `keycloak` | Keycloak 26 | OIDC; AD/LDAP-Federation folgt in Phase 2 |
| `vllm-chat/-embed/-rerank` | NGC vLLM | Modell-Serving auf der Spark (`--profile models`) |
| `redis` | Redis 7 | Queue/Cache (Jobqueue-Ausbau in Phase 3) |
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

Danach: `https://<ONLUMIS_DOMAIN>/` (Chat), `/api/docs` (OpenAPI),
`/auth` (Keycloak-Admin). Die mitgelieferten Beispieldokumente unter
`data/sources/beispiel/` machen das System sofort befragbar.

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
| P0 Compose-Stack, Netze, TLS-Proxy, Secrets-Schema, Modell-Manifeste | ✅ umgesetzt |
| AP 1.1 DB-Schema (knowledge/app/audit, HNSW+GIN, ACL-Arrays) | ✅ umgesetzt + getestet |
| AP 1.2 Dateisystem-Konnektor (Change Detection 2-stufig, Tombstones) | ✅ umgesetzt + getestet |
| AP 1.3 Parsing MD/TXT/HTML/PDF/DOCX | ✅ v1 (Docling/OCR-Backend folgt an gleicher Schnittstelle) |
| AP 1.4 Chunking (Überschriften-Pfade, Seiten, Überlappung) | ✅ umgesetzt + getestet |
| AP 1.5 Sync-Runner (`once`/`loop`, Status je Quelle) | ✅ v1 (Redis-Jobqueue folgt Phase 3) |
| AP 1.6 RAG-API: /v1/answers, /v1/chat/completions (SSE), /v1/search, Feedback, Admin, Audit | ✅ umgesetzt + Smoke-Test Ende-zu-Ende |
| AP 1.7 Chat-UI (Streaming, Quellen, Feedback, Verlauf clientseitig) | ✅ v1, `next build` verifiziert |
| Reranker-Anbindung (vLLM /v1/rerank, abschaltbar) | ✅ umgesetzt (Wirkungs-A/B: AP 3.6) |
| Hybrid-Suche (pgvector-HNSW + tsvector-`german` + RRF in einem SQL) | ✅ umgesetzt + getestet |
| Dokument-ACLs im Retrieval (SQL-seitig) | ✅ umgesetzt + Negativtests |
| OIDC-Validierung (Keycloak JWKS) | ✅ Code vorhanden; Realm-Setup + AD-Federation = Phase 2 |
| OCR für Scans, weitere Konnektoren, MCP-Server, Teams, Eval-Harness, LoRA | ⬜ gemäß Plan Phase 2–5 |

## Struktur

```
platform/
  compose.yml / compose.dev.yml   Stack (Spark bzw. Dev ohne GPU)
  .env.example                    Konfiguration
  db/init/                        Schema (pgvector, knowledge/app/audit)
  deploy/                         Caddy, Prometheus, Grafana
  models/                         Modell-Manifeste + Download (Air-Gap-fähig)
  services/api/                   FastAPI RAG-Orchestrator
  services/ingestion/             Konnektoren, Parsing, Chunking, Indexer
  services/webapp/                Next.js-Chat (Streaming + Quellen)
  data/sources/beispiel/          Demo-Korpus für den Quickstart
  tests/                          Ende-zu-Ende-Integrationstests
```
