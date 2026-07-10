# OnLumis Admin-Handbuch

Für Administratoren und Kuratoren (Rollen `onlumis-admin` / `curator`).
Technischer Betrieb: siehe [`platform/deploy/RUNBOOK.md`](../platform/deploy/RUNBOOK.md).

## 1. Anmeldung & Rollen

Anmeldung über den Firmen-Login (Keycloak/AD). Rollen werden über AD-Gruppen
gesteuert: `onlumis-admin` (Verwaltung), `onlumis-auditor` (Audit-Einsicht),
alle übrigen Gruppen wirken als **Berechtigungen auf Dokumente** (ACLs).

## 2. Nutzung (alle Mitarbeitenden)

- **Chat:** Fragen in natürlicher Sprache; Antworten ausschließlich aus
  freigegebenen Dokumenten, jede Aussage mit Quellen-Link (`[1]` anklicken
  öffnet das Originaldokument). Verläufe links in der Seitenleiste;
  Folgefragen („und dort?") funktionieren, 👍/👎 verbessert das System.
- **Spracheingabe:** Mikrofon-Symbol neben dem Eingabefeld (Chat und Suche);
  die Aufnahme wird lokal auf dem Firmenserver transkribiert.
- **Suche:** `/suche` liefert Fundstellen mit Abschnitt und Original-Link,
  ohne generierte Antwort.
- Findet das System keine belastbare Quelle, sagt es das offen – solche
  Fragen erscheinen im Wissenslücken-Report (anonymisiert).

## 3. Verwaltung (`/admin`)

### Wissensquellen
„Quelle anlegen" mit Typ und Konfiguration; der nächste Sync-Lauf indexiert
automatisch. Konfigurationsbeispiele (`Config-JSON`):

| Typ | Beispiel-Config |
|---|---|
| Dateisystem | Pfad-Feld, z. B. `/data/sources/hr`; optional `{"acl_rules": [{"pattern": "geheim/*", "groups": ["geschaeftsfuehrung"]}]}` |
| Confluence | `{"base_url": "https://firma.atlassian.net/wiki", "space_keys": ["DOCS"], "email": "bot@firma.de", "api_token_env": "CONFLUENCE_TOKEN"}` |
| SharePoint | `{"tenant_id": "…", "client_id": "…", "client_secret_env": "GRAPH_SECRET", "drive_id": "b!…"}` |
| IMAP | `{"host": "mail.firma.de", "username": "wissen@firma.de", "password_env": "IMAP_PASSWORD", "folders": ["INBOX"]}` |
| Jira | `{"base_url": "https://firma.atlassian.net", "jql": "project = SUP AND resolution = Done", "email": "bot@firma.de", "api_token_env": "JIRA_TOKEN"}` |
| WebDAV (DMS/Nextcloud) | `{"base_url": "https://dms.firma.de/webdav", "root_path": "Richtlinien", "username": "bot", "password_env": "WEBDAV_PASSWORD"}` |
| Google Drive | `{"service_account_json_env": "GDRIVE_SA", "folder_id": "1AbC…"}` |

`*_env`-Felder verweisen auf Umgebungsvariablen des Ingestion-Containers –
Zugangsdaten stehen so nie in der Datenbank. **Gruppen (ACL)** der Quelle
bestimmen, wer die Inhalte sieht; Default restriktiv wählen. Audio-Dateien
(mp3/wav/…) in Dateisystem-Quellen werden automatisch transkribiert.

### Dokumente hochladen
Für Einzeldokumente ohne Quellsystem; landen in der Quelle „uploads"
(Sichtbarkeit = deren ACL).

### Antwortprofile je Gruppe
Stil-/Formatvorgaben pro AD-Gruppe (z. B. `vertrieb`: „Formuliere als
Angebots-Textbaustein"). Wirken zusätzlich zum Systemprompt, nie auf Fakten.

### API-Keys
Für Integrationen (Intranet-Suche, Skripte, Agenten via MCP). Scopes `chat`/
`search`; die **Gruppen des Keys bestimmen seine Dokumentensicht**. Der Key
wird nur einmal angezeigt. Deaktivieren statt löschen erhält Nachvollziehbarkeit.

### Feedback-Kuratierung
👎-Einträge zeigen Schwachstellen; geprüfte 👍-Beispiele („Geprüft &
freigeben") speisen den Fine-Tuning-Datensatz (`finetune/`). Nur Inhalte
freigeben, die alle sehen dürfen.

### Qualität (goldene Fragen)
Referenzfragen mit erwarteter Quelle/Schlüsselbegriffen; „Eval-Lauf starten"
misst Retrieval- und Antwortqualität. Vor/nach jedem Modell- oder
Adapterwechsel laufen lassen (Regressionsgate). Startfragen:
`platform/db/seed/eval-beispiel.sql`.

### Wissenslücken
Meistgestellte Fragen ohne belastbare Quelle (Personen pseudonymisiert) –
die Arbeitsliste fürs Wissensmanagement: dokumentieren oder Quelle anbinden.

## 4. Audit & Datenschutz

- Auditoren (`onlumis-auditor`) exportieren das Zugriffsprotokoll über
  `GET /api/v1/audit/events?format=csv` (wer, wann, welche Dokumente;
  Fragen standardmäßig nur als Hash).
- Aufbewahrung: `RETENTION_DAYS_CONVERSATIONS`/`RETENTION_DAYS_AUDIT`
  löschen automatisch (0 = unbegrenzt). Details: [`dsgvo/`](dsgvo/).

## 5. Schnittstellen für Fachanwendungen

- REST: `https://<domain>/api/docs` (OpenAPI); Auth per API-Key.
- MCP (Agenten/IDE-Assistenten): `https://<domain>/api/mcp` mit Tools
  `search_knowledge`, `answer_with_sources`, `draft_text`.
