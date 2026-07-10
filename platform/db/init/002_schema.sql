-- OnLumis-Schema v1 (Architektur §8).
-- Migrationsstrategie: bis v1.0 additive Änderungen als neue Init-Skripte;
-- ab erstem produktiven Kundenbestand Umstieg auf versionierte Migrationen.

CREATE SCHEMA IF NOT EXISTS knowledge;  -- Wissensbasis (Ingestion schreibt, API liest)
CREATE SCHEMA IF NOT EXISTS app;        -- Konversationen, Feedback
CREATE SCHEMA IF NOT EXISTS audit;      -- append-only Protokoll (A7)

-- ---------------------------------------------------------------- knowledge

CREATE TABLE knowledge.sources (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  kind         text NOT NULL CHECK (kind IN ('filesystem', 'sharepoint', 'confluence', 'imap')),
  name         text NOT NULL UNIQUE,
  config       jsonb NOT NULL DEFAULT '{}',   -- z. B. {"root_path": "/data/sources/handbuecher"}
  default_acl  text[] NOT NULL DEFAULT '{}',  -- AD-/Keycloak-Gruppen (A5)
  enabled      boolean NOT NULL DEFAULT true,
  last_sync_at timestamptz,
  last_sync_status text,                      -- 'ok' | 'error: ...'
  created_at   timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE knowledge.documents (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id    uuid NOT NULL REFERENCES knowledge.sources(id) ON DELETE CASCADE,
  external_id  text NOT NULL,                 -- Pfad/Item-ID innerhalb der Quelle
  uri          text NOT NULL,                 -- klickbare Quellenangabe (A1)
  title        text,
  mime_type    text,
  content_hash text NOT NULL,                 -- SHA-256, Change Detection & Dedup
  acl_groups   text[] NOT NULL DEFAULT '{}',
  meta         jsonb NOT NULL DEFAULT '{}',   -- z. B. {"mtime": ..., "size": ...}
  updated_at   timestamptz NOT NULL DEFAULT now(),
  deleted_at   timestamptz,                   -- Tombstone: Chunks entfernt, Zeile bleibt (Audit)
  UNIQUE (source_id, external_id)
);
CREATE INDEX documents_acl_idx ON knowledge.documents USING gin (acl_groups);
CREATE INDEX documents_alive_idx ON knowledge.documents (source_id) WHERE deleted_at IS NULL;

CREATE TABLE knowledge.chunks (
  id           bigserial PRIMARY KEY,
  document_id  uuid NOT NULL REFERENCES knowledge.documents(id) ON DELETE CASCADE,
  chunk_index  int  NOT NULL,
  content      text NOT NULL,
  heading_path text,                          -- "Handbuch › Kap. 3 › Wartung" (Zitate)
  page         int,
  embedding    vector(1024) NOT NULL,         -- BGE-M3; Modellwechsel = Re-Indexierung
  tsv          tsvector GENERATED ALWAYS AS (to_tsvector('german', content)) STORED,
  UNIQUE (document_id, chunk_index)
);
CREATE INDEX chunks_embedding_idx ON knowledge.chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX chunks_tsv_idx ON knowledge.chunks USING gin (tsv);

-- ---------------------------------------------------------------------- app

CREATE TABLE app.conversations (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  username   text NOT NULL,
  title      text,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX conversations_user_idx ON app.conversations (username, created_at DESC);

CREATE TABLE app.messages (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id uuid NOT NULL REFERENCES app.conversations(id) ON DELETE CASCADE,
  role            text NOT NULL CHECK (role IN ('user', 'assistant')),
  content         text NOT NULL,
  citations       jsonb,                      -- [{n, title, uri, page, heading_path, ...}]
  chunk_ids       bigint[],                   -- Rückführbarkeit Antwort -> Chunks
  model           text,                       -- Modell + ggf. LoRA-Adapter der Antwort
  created_at      timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX messages_conversation_idx ON app.messages (conversation_id, created_at);

CREATE TABLE app.feedback (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  message_id uuid NOT NULL REFERENCES app.messages(id) ON DELETE CASCADE,
  rating     text NOT NULL CHECK (rating IN ('up', 'down')),
  comment    text,
  username   text NOT NULL,
  reviewed   boolean NOT NULL DEFAULT false,  -- Kuratierungs-Workflow (Phase 5)
  created_at timestamptz NOT NULL DEFAULT now()
);

-- -------------------------------------------------------------------- audit

-- Append-only; bewusst ohne Fremdschlüssel, damit Einträge Dokument-/
-- Konversations-Löschungen überleben. Fragen als Klartext ODER Hash,
-- gesteuert durch AUDIT_LOG_QUESTIONS (Datenschutz-Default: nur Hash).
CREATE TABLE audit.events (
  id              bigserial PRIMARY KEY,
  ts              timestamptz NOT NULL DEFAULT now(),
  actor           text NOT NULL,
  action          text NOT NULL,              -- 'chat' | 'search' | 'admin:source_created' | ...
  question        text,
  question_hash   text,
  document_ids    uuid[],
  chunk_ids       bigint[],
  conversation_id uuid,
  model           text,
  meta            jsonb NOT NULL DEFAULT '{}'
);
CREATE INDEX events_ts_idx ON audit.events (ts);
CREATE INDEX events_actor_idx ON audit.events (actor, ts);

REVOKE UPDATE, DELETE ON audit.events FROM PUBLIC;
