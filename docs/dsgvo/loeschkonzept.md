# Löschkonzept – OnLumis

Vorlage; Fristen sind je Installation vom Verantwortlichen festzulegen.

## 1. Datenkategorien, Fristen, Mechanismen

| Kategorie | Inhalt | Löschmechanismus | Frist (Empfehlung) |
|---|---|---|---|
| Wissensbasis (Chunks/Embeddings) | Kopien freigegebener Firmendokumente | **automatisch**: Löschung/Entzug in der Quelle → nächster Delta-Sync entfernt Chunks (Tombstone; Dokumentzeile bleibt ohne Inhalt für die Nachvollziehbarkeit) | ≤ Sync-Intervall (Std.) |
| Konversationen | Fragen/Antworten der Nutzenden | Nutzer: Löschen einzelner Verläufe in der Sidebar; System: `RETENTION_DAYS_CONVERSATIONS` (täglicher Job) | 90–365 Tage |
| Audit-Protokoll | Zugriffe (Fragen als Hash) | `RETENTION_DAYS_AUDIT` (täglicher Job) | 365 Tage bzw. gem. Vorgabe DSB |
| Wissenslücken | Fragen ohne Quelle, Nutzer pseudonymisiert | mit Audit-Frist mitlöschen bzw. nach Bearbeitung | 180 Tage |
| Feedback/Trainingsdaten | kuratierte Q/A-Paare | Kuratierungsprozess entfernt Personenbezug; Datensätze versioniert, Löschung auf Anforderung | bis Widerruf |
| Uploads | manuell hochgeladene Dokumente | Datei im Upload-Verzeichnis löschen → Sync-Tombstone | wie Wissensbasis |
| Backups | Gesamtsicherungen | automatische Rotation (`KEEP`, Standard 14 Generationen) | 14–30 Tage |
| Modell-Adapter (LoRA) | trainiertes Verhalten, keine Personendaten (ADR-9) | Adapter-Registry, Löschung + Rollback möglich | bis Ablösung |

## 2. Betroffenenrechte (Art. 15–17 DSGVO)

- **Auskunft:** Audit-Export je Nutzerkennung (`/v1/audit/events?actor=…`);
  Konversationen des Nutzers über die Anwendung einsehbar.
- **Löschung:** (1) Konversationen des Betroffenen löschen (UI oder SQL),
  (2) Dokumente mit Personenbezug in der **Quelle** löschen/korrigieren –
  der Sync übernimmt dies in die Wissensbasis, (3) Backup-Rotation abwarten
  oder anlassbezogen bereinigen; Frist dokumentieren.
- **Berichtigung:** Korrektur im Quellsystem; Re-Sync aktualisiert die
  Wissensbasis automatisch (Versions-/Hash-Erkennung).

## 3. Vertragsende / Außerbetriebnahme

1. Stack stoppen (`docker compose down`).
2. Docker-Volumes löschen (`docker volume rm onlumis_pgdata onlumis_uploads
   onlumis_hf-cache …`) bzw. LUKS-Datenträger kryptografisch löschen.
3. Backups auf dem NAS entfernen; Löschung protokollieren.
4. Bei JULITH-Betrieb (Private Cloud): Löschbestätigung gemäß AVV §7.
