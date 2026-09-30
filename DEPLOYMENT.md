# OnLumisAI Website

## Betrieb

Die Website läuft als Next.js-Standalone-Dienst auf dem vorhandenen Webserver.

- Dienst: `onlumis.service`, Port 3000 hinter dem vorhandenen HTTPS-Proxy
- Release: `/home/claude/onlumis-site/releases/20260930-demo-fix`
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
3. `RELEASE_DIR=/absoluter/Pfad scripts/prepare-release.sh` prüft die im Standalone-Paket enthaltenen OG-Schriften, ergänzt statische Dateien und öffentliche Medien und startet eine Vorschau auf Port 3100. Private Medien bleiben ausschließlich im konfigurierten `DEMO_ASSET_DIR`. Die Logo-Schriften werden durch `outputFileTracingIncludes` ausdrücklich mitgeliefert; ihr Lesen erfolgt erst beim Erzeugen des OG-Bildes, nicht beim Import der Seitenmetadaten.
4. Die Vorschau aus ihrem tatsächlichen `.next/standalone`-Verzeichnis mit derselben Runtime-Konfiguration prüfen. `next start` im Quellverzeichnis genügt nicht als Paketprüfung. Für HTTP-Tests kann ein Testclient den Cookie explizit mitsenden; die Browseranmeldung erfolgt ausschließlich über HTTPS.
5. `RELEASE_DIR=/absoluter/Pfad scripts/activate-release.sh` verlangt vor der Umstellung erfolgreiche Zugriffsprüfungen einschließlich Anmeldung, gerenderter Bibliothek mit allen Videokarten, geschützten Dateien und OG-Bild. Die Prüfung wird nach dem Neustart wiederholt; bei einem Fehler wird der vorherige Dienst wiederhergestellt. Ein HTTP-200-Status allein genügt nicht, da auch eine fehlerhafte gestreamte Next.js-Seite diesen Status liefern kann.
6. Anschließend die Browserprüfung über die öffentliche HTTPS-Adresse ausführen, einschließlich Anmeldung, Videowiedergabe, PDF und Abmeldung.

## Rückkehr zur früheren Website

```
sudo cp /home/claude/onlumis-site/backups/onlumis.service.before-redesign /etc/systemd/system/onlumis.service
sudo systemctl daemon-reload
sudo systemctl restart onlumis
```

Die neue Demo-Bibliothek gehört zur neuen Version. Die Rückkehr zum ursprünglichen Dienst stellt dessen alten Funktionsumfang wieder her.
