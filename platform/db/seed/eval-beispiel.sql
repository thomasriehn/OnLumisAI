-- Goldene Starterfragen für den Beispielkorpus (data/sources/beispiel).
-- Idempotent; Einspielen z. B. mit:
--   docker compose exec -T postgres psql -U onlumis -d onlumis < db/seed/eval-beispiel.sql
-- Beim Piloten durch kundenspezifische Fragen ersetzen/ergänzen (50-200 Stück).

INSERT INTO eval.questions (question, expected_uri_substring, expected_keywords, groups)
SELECT * FROM (VALUES
  ('Wie viel Sonderurlaub gibt es bei der eigenen Hochzeit?',
   'urlaubsrichtlinie', ARRAY['Sonderurlaub', '1 Tag'], ARRAY['all-users']),
  ('Wie viele Urlaubstage haben Vollzeit-Mitarbeitende pro Jahr?',
   'urlaubsrichtlinie', ARRAY['30'], ARRAY['all-users']),
  ('Bis wann kann Resturlaub ins Folgejahr übertragen werden?',
   'urlaubsrichtlinie', ARRAY['31. März'], ARRAY['all-users']),
  ('Was ist zu prüfen, wenn die Presse P-300 keinen Druck aufbaut?',
   'wartung-presse', ARRAY['Saugfilter'], ARRAY['all-users']),
  ('Welcher Öldruck ist bei der wöchentlichen Wartung der P-300 korrekt?',
   'wartung-presse', ARRAY['185'], ARRAY['all-users']),
  ('Welches Fett wird für die Führungsschienen der P-300 verwendet?',
   'wartung-presse', ARRAY['KP2K-30'], ARRAY['all-users'])
) AS neu(question, expected_uri_substring, expected_keywords, groups)
WHERE NOT EXISTS (
  SELECT 1 FROM eval.questions q WHERE q.question = neu.question
);
