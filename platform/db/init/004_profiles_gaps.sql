-- Abteilungs-Prompt-Profile: zusätzliche Antwortvorgaben je AD-Gruppe
-- (z. B. Angebots-Textbausteine für 'vertrieb', Schritt-für-Schritt für
-- 'produktion'). Mehrere zutreffende Profile werden kombiniert.
CREATE TABLE app.prompt_profiles (
  group_name   text PRIMARY KEY,
  instructions text NOT NULL,
  updated_at   timestamptz NOT NULL DEFAULT now()
);

-- Wissenslücken-Report: Fragen ohne belastbare Quelle (Zero-Hit). Nutzer
-- pseudonymisiert (Hash) – der Inhalt der Frage ist das Arbeitsmaterial für
-- das Wissensmanagement, nicht die Person.
CREATE TABLE app.knowledge_gaps (
  id            bigserial PRIMARY KEY,
  question      text NOT NULL,
  username_hash text NOT NULL,
  groups        text[] NOT NULL DEFAULT '{}',
  created_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX knowledge_gaps_created_idx ON app.knowledge_gaps (created_at DESC);
