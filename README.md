# OnLumis

Marketing-Website für **OnLumis** – die lokale, DSGVO-konforme
Unternehmens-KI der [JULITH GmbH](https://julith.gmbh). Produktiv unter
[onlumis.ai](https://onlumis.ai).

Gebaut mit Next.js (App Router) + TypeScript + Tailwind CSS. Statisch
generierte Seiten für Produkt, Vorteile, Anwendungsfälle, Förderung,
Datenschutz und Impressum sowie ein serverseitiges Kontaktformular, das
Mails über einen Postfix-MTA versendet.

## Voraussetzungen

- Node.js 20+
- Ein erreichbarer SMTP-/Postfix-Server für den Mailversand (siehe unten)

## Lokale Entwicklung

```bash
npm install
npm run dev
```

Die Seite ist danach unter [http://localhost:3000](http://localhost:3000)
erreichbar.

```bash
npm run build   # Produktions-Build
npm run start   # Produktions-Server starten
npm run lint    # ESLint
```

## Umgebungsvariablen (Kontaktformular)

Das Kontaktformular unter `/kontakt` sendet POST-Requests an die Route
`src/app/api/kontakt/route.ts`, die per [nodemailer](https://nodemailer.com/)
eine E-Mail über SMTP verschickt. Kopieren Sie `.env.example` zu `.env.local`
und tragen Sie Ihre Zugangsdaten ein:

```bash
cp .env.example .env.local
```

| Variable      | Beschreibung                                                                 | Default |
| -------------- | ----------------------------------------------------------------------------- | ------- |
| `SMTP_HOST`    | Hostname des SMTP-Servers/Postfix-MTA                                         | `localhost` |
| `SMTP_PORT`    | Port des SMTP-Servers (25 = lokales Relay, 587 = Submission mit STARTTLS)      | `25` |
| `SMTP_SECURE`  | `"true"` für implizites TLS (z. B. Port 465), sonst `"false"`                 | `false` |
| `SMTP_USER`    | Optional: Benutzername, falls der Server/Postfix-Relay Auth verlangt          | leer |
| `SMTP_PASS`    | Optional: Passwort, falls der Server/Postfix-Relay Auth verlangt              | leer |
| `MAIL_FROM`    | Absenderadresse der versendeten Mails                                        | `OnLumis Website <no-reply@onlumis.ai>` |
| `MAIL_TO`      | Empfängeradresse für eingehende Kontaktanfragen                              | `info@onlumis.ai` |

`.env*`-Dateien sind über `.gitignore` von der Versionskontrolle
ausgeschlossen – Zugangsdaten landen also nicht im Repository.

### Postfix als lokaler Mailversand (Standardfall)

Läuft die Anwendung auf demselben Server wie Postfix (z. B. auf einem
Linux-Server/VM), reicht in der Regel die Standardkonfiguration:

```
SMTP_HOST=localhost
SMTP_PORT=25
SMTP_SECURE=false
SMTP_USER=
SMTP_PASS=
```

Postfix muss dafür ausgehende Mails zustellen bzw. an einen Smarthost
weiterleiten können. Minimalanforderungen an die Postfix-Konfiguration
(`/etc/postfix/main.cf`):

```
myhostname = mail.onlumis.ai
myorigin = $myhostname
inet_interfaces = loopback-only   # Postfix lauscht nur lokal, kein offenes Relay
mydestination =
relayhost =                       # leer lassen, wenn Postfix direkt zustellen soll
```

Damit Mails nicht im Spam landen, sollten für die Absenderdomain **SPF**,
**DKIM** (z. B. via `opendkim`) und idealerweise **DMARC** eingerichtet sein.

### Postfix als Relay zu einem Smarthost (empfohlen für Zustellbarkeit)

Alternativ kann Postfix ausgehende Mails über einen externen SMTP-Anbieter
(Smarthost) mit Authentifizierung versenden. Dazu in `main.cf`:

```
relayhost = [smtp.ihr-anbieter.de]:587
smtp_sasl_auth_enable = yes
smtp_sasl_password_maps = hash:/etc/postfix/sasl_passwd
smtp_sasl_security_options = noanonymous
smtp_tls_security_level = encrypt
```

und in `/etc/postfix/sasl_passwd` die Zugangsdaten hinterlegen (danach
`postmap /etc/postfix/sasl_passwd` ausführen). Die Anwendung selbst spricht
in diesem Fall weiterhin nur mit dem lokalen Postfix auf `localhost:25` –
`SMTP_USER`/`SMTP_PASS` in der `.env` bleiben leer, da die Authentifizierung
beim Smarthost von Postfix übernommen wird.

### Test des Mailversands

```bash
# Postfix-Warteschlange prüfen
mailq

# Testmail über den lokalen MTA verschicken
echo "Testinhalt" | mail -s "Testbetreff" ihre-adresse@example.com

# Logs prüfen
journalctl -u postfix -f
# bzw.
tail -f /var/log/mail.log
```

## SEO & Rechtliches

- `src/app/sitemap.ts` und `src/app/robots.ts` erzeugen automatisch
  `sitemap.xml` und `robots.txt`.
- `src/app/opengraph-image.tsx` und `src/app/icon.tsx` erzeugen Open-Graph-Bild
  und Favicon serverseitig, ohne externe Assets.
- Strukturierte Daten (JSON-LD) für `Organization`, `SoftwareApplication` und
  `FAQPage` sind in `src/app/layout.tsx` bzw. `src/components/FaqSection.tsx`
  eingebunden.
- **Wichtig:** `src/app/impressum/page.tsx` enthält Platzhalter in eckigen
  Klammern (Anschrift, Geschäftsführung, Registergericht, HRB-Nummer,
  USt-IdNr.) für die JULITH GmbH. Diese müssen vor Veröffentlichung durch die
  echten Angaben ersetzt werden – ein unvollständiges Impressum ist
  abmahnfähig.
- `src/app/datenschutz/page.tsx` enthält ebenfalls Platzhalter für Anschrift
  in Ziffer 1 (Verantwortlicher).

## Projektstruktur

```
src/
  app/                Seiten (App Router), API-Route, Sitemap/Robots
  components/          Wiederverwendbare UI-Komponenten
  lib/                 Site-Konfiguration, Validierung, Mailer, Rate-Limit
```

## Deployment

Die Seite ist als reguläre Next.js-Anwendung deploybar (z. B. per `next
build && next start` auf einem eigenen/gemieteten Server, Docker-Container
oder Node-Hosting). Für den DSGVO-konformen Betrieb wird ein Hosting-Standort
in Deutschland bzw. der EU empfohlen.
