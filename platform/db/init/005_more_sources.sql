-- Wissensabdeckung: weitere Konnektor-Typen (Jira, WebDAV/DMS, Google Drive)
ALTER TABLE knowledge.sources DROP CONSTRAINT sources_kind_check;
ALTER TABLE knowledge.sources ADD CONSTRAINT sources_kind_check
  CHECK (kind IN ('filesystem', 'sharepoint', 'confluence', 'imap',
                  'jira', 'webdav', 'gdrive'));
