# OnLumisAI Website

## Betrieb

Die Website läuft als Next.js-Standalone-Dienst auf dem vorhandenen Webserver.

- Dienst: `onlumis.service`, Port 3000 hinter dem vorhandenen HTTPS-Proxy
- Release: `/home/claude/onlumis-site/releases/20260930-redesign-final`
- Laufzeitkonfiguration: `/home/claude/onlumis-site/shared/.env` (0600)
- Geschützte Videos und PDFs: `/home/claude/onlumis-site/shared/demo`
- Öffentliche Medien: `/home/claude/onlumis-site/shared/media`
- Sicherung des ursprünglichen Dienstes: `/home/claude/onlumis-site/backups/onlumis.service.before-redesign`
- Das ursprüngliche Checkout `/home/claude/OnLumisAI` bleibt unverändert erhalten.

`APP_ORIGIN` muss der öffentlichen HTTPS-Adresse entsprechen. Der vorgeschaltete Proxy darf die privaten Antworten unter `/demo` und `/api/demo` nicht zwischenspeichern. Keine zusätzliche öffentliche Alias-Auslieferung des privaten Medienverzeichnisses einrichten.

## Demo-Passwort ändern

In der Laufzeitkonfiguration `DEMO_PASSWORD` ändern (mindestens 16 Zeichen), dann `sudo systemctl restart onlumis`. Bestehende Sitzungen werden ungültig. `DEMO_SESSION_SECRET` ist ein unabhängiges zufälliges Geheimnis mit mindestens 32 Zeichen. Keine dieser Angaben gehört ins Repository.

Die Anmeldung gilt acht Stunden. HTML, Videos, Vorschaubilder und PDFs prüfen dieselbe signierte Sitzung. Videos unterstützen Byte-Ranges zum Vorspulen. Nach der Abmeldung kann der Browser die Dateien nicht erneut anfordern. Bereits heruntergeladene Dateien können nicht zurückgerufen werden.

Login-Versuche werden im einzelnen Serverprozess begrenzt (zehn pro Adresse und 150 insgesamt je zehn Minuten). Bei mehreren Instanzen ist dafür ein gemeinsamer Speicher erforderlich. Ein Proxy sollte `X-Real-IP` selbst setzen und vom Client gelieferte Werte überschreiben.

## Lokale Entwicklung und Prüfung

Node.js >= 20.9, `npm ci`, `.env.local` anhand von `.env.example` anlegen. Für lokale Produktionsprüfungen `APP_ORIGIN=http://localhost:3100` verwenden; nur für localhost wird das Secure-Cookie ausgenommen.

```
npm run lint
npm run build
npm run start -- --port 3100
npx playwright install chromium
npm run test:browser
npm run test:access
```

Die Tests benötigen die vorbereiteten Medien. `python3 scripts/import-demo.py /Pfad/zum/OnLumisAI-Arbeitsordner` importiert die vorhandenen Aufnahmen, PDFs, Vorschaubilder und Beobachtungen. Diese großen bzw. geschützten Dateien sind bewusst nicht in Git. Die Video-Inhalte werden nicht verändert.

`TEST_BASE_URL`, `TEST_ENV_FILE` (Zugriffstest) und `PLAYWRIGHT_MODULE` (optional) erlauben andere Testumgebungen. Keine echten Kontaktmails werden von den Tests verschickt. Prüfergebnisse und Screenshots liegen im ignorierten Verzeichnis `qa`.

## Neues Release

1. Separates Release-Verzeichnis anlegen und Quellcode übertragen, ohne lokale `.env`, `.git`, `node_modules` oder `.next`.
2. Dort `npm ci && npm run build` ausführen. Der Build verwendet Webpack.
3. `.next/static` nach `.next/standalone/.next/static` und `public` nach `.next/standalone/public` kopieren. Das öffentliche Erklärvideo ergänzen. Private Medien bleiben ausschließlich im konfigurierten `DEMO_ASSET_DIR`.
4. Mit eigener Portnummer zunächst lokal auf dem Server prüfen. Dabei dieselbe Runtime-Konfiguration verwenden; für HTTP-Tests kann ein Testclient den Cookie explizit mitsenden. Die Browseranmeldung erfolgt ausschließlich über HTTPS.
5. Den Dienst auf das geprüfte Release umstellen, neu starten und die öffentliche Seite einschließlich direkter geschützter Dateien überprüfen.

## Rückkehr zur früheren Website

```
sudo cp /home/claude/onlumis-site/backups/onlumis.service.before-redesign /etc/systemd/system/onlumis.service
sudo systemctl daemon-reload
sudo systemctl restart onlumis
```

Die neue Demo-Bibliothek gehört zur neuen Version. Die Rückkehr zum ursprünglichen Dienst stellt dessen alten Funktionsumfang wieder her.
