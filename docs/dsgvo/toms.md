# Technisch-organisatorische Maßnahmen (TOMs) – OnLumis

Stand: Produktversion 0.x · Vorlage, je Installation zu konkretisieren.
Besonderheit: Die Kernmaßnahme ist die Architektur selbst – **Daten und
KI-Modelle verlassen die Infrastruktur des Verantwortlichen nicht** (A10/A8).

## 1. Vertraulichkeit

- **Zutritt:** Betrieb im Serverraum/RZ des Verantwortlichen (bzw.
  zertifiziertes DE/EU-RZ in der Private-Cloud-Variante); physische
  Zutrittsregelung des Standorts.
- **Zugang:** Anmeldung ausschließlich über zentrales IAM (Keycloak mit
  AD/LDAP-Federation, OIDC); Passwort-/MFA-Richtlinien des Unternehmens
  greifen durch. Dienstzugriffe über einzeln widerrufbare API-Keys
  (SHA-256-gehasht gespeichert, Scopes, eigene ACL-Gruppen).
- **Zugriff:** Dokumenten-Berechtigungen (ACLs) werden bei **jeder** Suche/
  Antwort auf Datenbankebene durchgesetzt – vor dem Sprachmodell. Rollen
  `admin`/`auditor` getrennt. Fine-Tuning trainiert grundsätzlich kein
  vertrauliches Wissen in Modellgewichte (ADR-9).
- **Trennung:** getrennte Datenbankschemata (Wissen/Anwendung/Audit/Eval);
  getrennte Docker-Netze (edge/app/data/ml); Modelle und Datenbank sind von
  außen nicht erreichbar (einziger exponierter Port: 443).

## 2. Integrität

- Transportverschlüsselung überall (TLS am Proxy, interne Netztrennung);
  Speicherverschlüsselung at rest (LUKS auf der NVMe der Spark).
- Append-only-Audit-Protokoll (wer, wann, welche Dokumente, welches Modell);
  UPDATE/DELETE auf Audit-Einträge entzogen, Löschung nur über das
  dokumentierte Aufbewahrungskonzept.
- Eingaben aus Dokumenten werden als Daten, nicht als Instruktionen
  verarbeitet (Schutz vor indirekter Prompt-Injection); Antworten sind über
  Zitate auf Quelldokumente rückführbar.

## 3. Verfügbarkeit & Belastbarkeit

- Tägliche automatisierte Backups (Datenbanken, Uploads, Konfiguration,
  Adapter) mit Rotation auf getrenntem Speicher (NAS); dokumentierte und
  geübte Wiederherstellung (Runbook §5).
- Monitoring/Alerting (Prometheus/Grafana), Healthchecks, Rate-Limiting
  gegen Überlast; Restart-Policies aller Dienste.

## 4. Pseudonymisierung & Datenminimierung

- Audit-Log speichert Frageinhalte standardmäßig **nur als SHA-256-Hash**
  (`AUDIT_LOG_QUESTIONS=false`).
- Wissenslücken-Report speichert Fragen ohne Personenbezug zum Fragenden
  (Nutzer nur als Hash).
- Konfigurierbare Aufbewahrungsfristen mit automatischer Löschung für
  Konversationen und Audit-Daten (`RETENTION_DAYS_*`).
- Spracheingaben werden lokal transkribiert und nicht gespeichert
  (nur Größe im Audit).

## 5. Auftragskontrolle & Organisation

- Fernwartung durch JULITH nur nach Freigabe und AVV; Zugriffe laufen über
  dieselben auditierten Kanäle.
- Air-Gap-Betriebsmodus für besonders schutzbedürftige Umgebungen
  (vollständig offline, signierte Update-Bundles per Datenträger).
- Dokumentierte Update-/Rollback-Prozesse mit Qualitäts-Gate (goldene
  Fragen) vor jedem Modellwechsel.
