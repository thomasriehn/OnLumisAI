-- Phase 2/5: API-Keys (AP 4.1) und Eval-Harness (AP 5.1).

-- API-Keys für Service-zu-Service-Zugriff (A4). Der Klartext-Key wird nur
-- einmal bei der Erstellung angezeigt; gespeichert wird ausschließlich der
-- SHA-256-Hash. "groups" bestimmt die ACL-Sicht des Keys, "scopes" die
-- erlaubten Endpunkte ('chat' | 'search'). Admin-Endpunkte sind für Keys
-- grundsätzlich gesperrt.
CREATE TABLE app.api_keys (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name         text NOT NULL UNIQUE,
  key_prefix   text NOT NULL,               -- erste Zeichen zur Identifikation
  key_hash     text NOT NULL UNIQUE,        -- SHA-256(hex) des vollen Keys
  scopes       text[] NOT NULL DEFAULT '{chat,search}',
  groups       text[] NOT NULL DEFAULT '{}',
  enabled      boolean NOT NULL DEFAULT true,
  created_by   text NOT NULL,
  created_at   timestamptz NOT NULL DEFAULT now(),
  last_used_at timestamptz
);

-- Goldene Fragen (Eval-Gate vor Modell-/Adapter-/Prompt-Rollouts, §6.7).
CREATE SCHEMA IF NOT EXISTS eval;

CREATE TABLE eval.questions (
  id                     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  question               text NOT NULL,
  expected_uri_substring text,              -- Retrieval-Hit: Zitat-URI enthält ...
  expected_keywords      text[] NOT NULL DEFAULT '{}',  -- müssen in Antwort vorkommen
  groups                 text[] NOT NULL DEFAULT '{all-users}',  -- ACL-Sicht des Laufs
  enabled                boolean NOT NULL DEFAULT true,
  created_at             timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE eval.runs (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  started_at  timestamptz NOT NULL DEFAULT now(),
  finished_at timestamptz,
  model       text NOT NULL,
  notes       text,
  stats       jsonb                          -- {total, retrieval_hits, keyword_hits, ...}
);

CREATE TABLE eval.results (
  id            bigserial PRIMARY KEY,
  run_id        uuid NOT NULL REFERENCES eval.runs(id) ON DELETE CASCADE,
  question_id   uuid NOT NULL REFERENCES eval.questions(id) ON DELETE CASCADE,
  retrieval_hit boolean NOT NULL,
  keywords_hit  boolean NOT NULL,
  judge_score   double precision,            -- optionaler LLM-Judge (0..1)
  answer        text NOT NULL,
  citations     jsonb,
  latency_ms    int
);
CREATE INDEX results_run_idx ON eval.results (run_id);
