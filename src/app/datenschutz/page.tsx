import type { Metadata } from "next";
import { Container } from "@/components/Container";
import { siteConfig } from "@/lib/site";

export const metadata: Metadata = {
  title: "Datenschutzerklärung",
  description:
    "Datenschutzerklärung von OnLumis gemäß Schweizer Datenschutzgesetz (DSG) und, soweit anwendbar, der DSGVO.",
  alternates: { canonical: "/datenschutz" },
  robots: { index: true, follow: true },
};

export default function DatenschutzPage() {
  const { address } = siteConfig.company;

  return (
    <section className="py-16 sm:py-20">
      <Container className="max-w-3xl">
        <h1 className="font-display text-3xl font-semibold text-ink dark:text-white">
          Datenschutzerklärung
        </h1>
        <p className="mt-2 text-sm text-muted">Stand: Juli 2026</p>

        <div className="prose-content mt-10 space-y-10 text-sm leading-relaxed text-muted [&_h2]:mt-0 [&_h2]:text-xl [&_h2]:font-semibold [&_h2]:text-ink dark:[&_h2]:text-white [&_h3]:font-semibold [&_h3]:text-ink dark:[&_h3]:text-white [&_p]:mt-3 [&_ul]:mt-3 [&_ul]:list-disc [&_ul]:pl-5 [&_li]:mt-1">
          <div>
            <h2>1. Verantwortliche Stelle</h2>
            <p>Verantwortlich für die Datenbearbeitung/-verarbeitung auf dieser Website ist:</p>
            <p>
              {siteConfig.company.legalName}
              <br />
              {address.street}
              <br />
              {address.zip} {address.city}
              <br />
              {address.country}
              <br />
              E-Mail:{" "}
              <a
                href={`mailto:${siteConfig.company.legalEmail}`}
                className="text-accent-strong underline underline-offset-2"
              >
                {siteConfig.company.legalEmail}
              </a>
            </p>
            <p>
              Weitere Angaben zum Verantwortlichen finden Sie in unserem{" "}
              <a href="/impressum" className="text-accent-strong underline underline-offset-2">
                Impressum
              </a>
              .
            </p>
          </div>

          <div>
            <h2>2. Anwendbares Recht und Grundsätze der Datenbearbeitung</h2>
            <p>
              {siteConfig.company.legalName} hat ihren Sitz in der Schweiz. Diese
              Datenschutzerklärung richtet sich in erster Linie nach dem Schweizerischen
              Bundesgesetz über den Datenschutz (DSG). Da sich das Angebot von OnLumis auch
              an Unternehmen in Deutschland und der übrigen EU richtet und dabei personenbezogene
              Daten von Personen in der EU/dem EWR bearbeitet werden können, beachten wir
              ergänzend, soweit anwendbar, die Vorgaben der europäischen
              Datenschutz-Grundverordnung (DSGVO).
            </p>
            <p>
              Wir bearbeiten personenbezogene Daten unserer Nutzerinnen und Nutzer grundsätzlich
              nur, soweit dies zur Bereitstellung einer funktionsfähigen Website sowie unserer
              Inhalte und Leistungen erforderlich ist. Die Bearbeitung erfolgt regelmäßig nur mit
              Einwilligung, zur Erfüllung vertraglicher bzw. vorvertraglicher Pflichten oder auf
              Grundlage berechtigter Interessen (entsprechend Art. 6 Abs. 1 DSGVO bzw. Art. 6 DSG).
            </p>
          </div>

          <div>
            <h2>3. Hosting und Bereitstellung der Website (Server-Logfiles)</h2>
            <p>
              Beim Aufruf dieser Website erhebt der von uns eingesetzte Hosting-Anbieter
              automatisch Informationen in sogenannten Server-Logfiles, die Ihr Browser
              automatisch übermittelt. Dies sind insbesondere:
            </p>
            <ul>
              <li>Browsertyp und Browserversion</li>
              <li>verwendetes Betriebssystem</li>
              <li>Referrer-URL</li>
              <li>Uhrzeit der Serveranfrage</li>
              <li>IP-Adresse (anonymisiert bzw. gekürzt)</li>
            </ul>
            <p>
              Diese Daten sind nicht bestimmten Personen zuordenbar, werden nicht mit anderen
              Datenquellen zusammengeführt und dienen ausschließlich der technisch
              fehlerfreien Bereitstellung und Absicherung der Website (berechtigtes Interesse
              entsprechend Art. 6 Abs. 1 lit. f DSGVO bzw. Art. 6 Abs. 1 DSG). Server-Logfiles
              werden automatisiert nach spätestens 14 Tagen gelöscht.
            </p>
            <p>
              Wir wählen unseren Hosting-Anbieter sorgfältig aus und achten auf ein angemessenes
              Datenschutzniveau. Sollten im Rahmen des Hostings Daten in Länder außerhalb der
              Schweiz oder des EWR übermittelt werden, stellen wir ein angemessenes
              Schutzniveau sicher, etwa durch Standardvertragsklauseln oder vergleichbare
              Garantien.
            </p>
          </div>

          <div>
            <h2>4. Keine Nutzung von Analyse- oder Tracking-Cookies</h2>
            <p>
              Diese Website verzichtet bewusst auf den Einsatz von Analyse-Tools,
              Werbe-Trackern und nicht technisch notwendigen Cookies Dritter. Es findet keine
              Erstellung von Nutzerprofilen und kein Tracking über mehrere Websites hinweg
              statt. Auch eingebundene Schriftarten werden lokal ausgeliefert; es besteht keine
              Verbindung zu externen Diensten wie Google Fonts. Sollte sich dies zukünftig
              ändern, werden wir Sie vorab um Ihre ausdrückliche Einwilligung bitten und diese
              Erklärung entsprechend anpassen.
            </p>
          </div>

          <div>
            <h2>5. Kontaktformular</h2>
            <p>
              Wenn Sie uns über das Kontaktformular Anfragen zukommen lassen, werden Ihre
              Angaben aus dem Formular – Name, Unternehmen, E-Mail-Adresse, optional Telefonnummer
              und Unternehmensgröße sowie Ihre Nachricht – zwecks Bearbeitung der Anfrage und für
              den Fall von Anschlussfragen bei uns gespeichert.
            </p>
            <p>
              Die Bearbeitung dieser Daten erfolgt auf Grundlage Ihrer Einwilligung sowie, sofern
              Ihre Anfrage mit der Anbahnung oder Erfüllung eines Vertrags zusammenhängt, zur
              Durchführung vorvertraglicher Maßnahmen (entsprechend Art. 6 Abs. 1 lit. a und b
              DSGVO bzw. Art. 6 DSG). In allen übrigen Fällen beruht die Bearbeitung auf unserem
              berechtigten Interesse an der Beantwortung Ihrer Anfrage.
            </p>
            <p>
              Die über das Kontaktformular übermittelten Daten werden per E-Mail an unser
              Postfach zugestellt. Der Versand erfolgt über einen Mailserver, den wir bzw. unser
              Hosting-Auftragsbearbeiter betreibt. Die Daten verbleiben bei uns, bis Sie uns zur
              Löschung auffordern, Ihre Einwilligung widerrufen oder der Zweck für die
              Speicherung entfällt – in der Regel nach abgeschlossener Bearbeitung Ihrer Anfrage.
              Besteht ausnahmsweise eine handelsrechtliche Aufbewahrungspflicht (in der Schweiz
              grundsätzlich bis zu 10 Jahre, Art. 958f OR), bleibt diese unberührt.
            </p>
            <p>
              Zum Schutz vor missbräuchlicher automatisierter Nutzung des Formulars (Spam) setzen
              wir ein verstecktes Formularfeld (sogenanntes „Honeypot&quot;) sowie eine technische
              Begrenzung der Anzahl an Anfragen pro Absender-IP-Adresse in einem kurzen Zeitraum
              ein. Hierbei werden keine zusätzlichen personenbezogenen Daten dauerhaft
              gespeichert.
            </p>
          </div>

          <div>
            <h2>6. Empfänger und Auftragsbearbeitung</h2>
            <p>
              Für den Betrieb dieser Website und den Versand von E-Mails setzen wir
              gegebenenfalls technische Dienstleister (z. B. Hosting- und
              E-Mail-Infrastrukturanbieter) ein, die in unserem Auftrag und ausschließlich nach
              unserer Weisung tätig werden. Mit diesen Dienstleistern schließen wir, soweit
              erforderlich, Verträge zur Auftragsbearbeitung bzw. Auftragsverarbeitung gemäß DSG
              bzw. Art. 28 DSGVO ab.
            </p>
          </div>

          <div>
            <h2>7. Hinweis zum Produkt OnLumis</h2>
            <p>
              Diese Datenschutzerklärung betrifft ausschließlich den Betrieb dieser Website
              (onlumis.ai). Setzen Sie das Produkt OnLumis in Ihrem eigenen Unternehmen
              ein, sind Sie als Kunde grundsätzlich selbst datenschutzrechtlich Verantwortlicher
              für die durch Sie in das System eingebrachten Unternehmensdaten. Im Rahmen einer
              Beauftragung schließen wir mit Ihnen einen gesonderten Vertrag zur
              Auftragsbearbeitung bzw. Auftragsverarbeitung (je nach anwendbarem Recht DSG bzw.
              Art. 28 DSGVO) für die Einrichtungs- und ggf. Betriebsleistungen ab, die wir als{" "}
              {siteConfig.company.legalName} für Sie erbringen.
            </p>
          </div>

          <div>
            <h2>8. Ihre Rechte als betroffene Person</h2>
            <p>
              Ihnen stehen nach dem Schweizer DSG und, soweit die DSGVO anwendbar ist, nach der
              DSGVO insbesondere folgende Rechte zu:
            </p>
            <ul>
              <li>Recht auf Auskunft über die bearbeiteten Daten (Art. 25 DSG / Art. 15 DSGVO)</li>
              <li>Recht auf Berichtigung unrichtiger Daten (Art. 32 DSG / Art. 16 DSGVO)</li>
              <li>Recht auf Löschung (Art. 32 DSG / Art. 17 DSGVO)</li>
              <li>Recht auf Einschränkung der Bearbeitung (Art. 32 DSG / Art. 18 DSGVO)</li>
              <li>Recht auf Datenherausgabe/-übertragbarkeit (Art. 28 DSG / Art. 20 DSGVO)</li>
              <li>Widerspruchsrecht gegen die Bearbeitung (Art. 30 DSG / Art. 21 DSGVO)</li>
              <li>Recht auf Widerruf erteilter Einwilligungen mit Wirkung für die Zukunft</li>
            </ul>
            <p>
              Zur Ausübung Ihrer Rechte wenden Sie sich bitte an die oben unter Ziffer 1
              genannten Kontaktdaten.
            </p>
          </div>

          <div>
            <h2>9. Beschwerderecht bei einer Aufsichtsbehörde</h2>
            <p>
              Für Anliegen im Zusammenhang mit dem Schweizer Datenschutzrecht ist der
              Eidgenössische Datenschutz- und Öffentlichkeitsbeauftragte (EDÖB), Feldeggweg 1,
              3003 Bern, Schweiz, zuständige Aufsichtsbehörde.
            </p>
            <p>
              Sofern die DSGVO anwendbar ist, haben Sie zusätzlich das Recht auf Beschwerde bei
              einer Datenschutz-Aufsichtsbehörde in der EU, insbesondere in dem Mitgliedstaat
              Ihres Aufenthaltsorts, Ihres Arbeitsplatzes oder des Orts des mutmaßlichen
              Verstoßes, wenn Sie der Ansicht sind, dass die Bearbeitung der Sie betreffenden
              personenbezogenen Daten gegen geltendes Datenschutzrecht verstößt.
            </p>
          </div>

          <div>
            <h2>10. Aktualität und Änderung dieser Datenschutzerklärung</h2>
            <p>
              Diese Datenschutzerklärung wird bei Bedarf angepasst, um sie an geänderte
              Rechtslagen oder bei Änderungen des Angebots bzw. der Datenbearbeitung anzupassen.
              Es gilt jeweils die zuletzt veröffentlichte Fassung.
            </p>
          </div>
        </div>
      </Container>
    </section>
  );
}
