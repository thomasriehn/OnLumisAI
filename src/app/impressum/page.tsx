import type { Metadata } from "next";
import { Container } from "@/components/Container";
import { siteConfig } from "@/lib/site";

export const metadata: Metadata = {
  title: "Impressum",
  description: "Impressum von OnLumis, ein Produkt der JULITH GmbH, Schweiz.",
  alternates: { canonical: "/impressum" },
  robots: { index: true, follow: true },
};

export default function ImpressumPage() {
  const { address } = siteConfig.company;

  return (
    <section className="py-16 sm:py-20">
      <Container className="max-w-3xl">
        <h1 className="font-display text-3xl font-semibold text-ink dark:text-white">
          Impressum
        </h1>

        <div className="mt-10 space-y-8 text-sm leading-relaxed text-muted">
          <div>
            <h2 className="text-lg font-semibold text-ink dark:text-white">
              Anbieterkennzeichnung
            </h2>
            <p className="mt-3">
              {siteConfig.company.legalName}
              <br />
              {address.street}
              <br />
              {address.zip} {address.city}
              <br />
              {address.country}
            </p>
          </div>

          <div>
            <h2 className="text-lg font-semibold text-ink dark:text-white">Vertreten durch</h2>
            <p className="mt-3">Geschäftsführer: {siteConfig.company.managingDirector}</p>
          </div>

          <div>
            <h2 className="text-lg font-semibold text-ink dark:text-white">Kontakt</h2>
            <p className="mt-3">
              E-Mail:{" "}
              <a
                href={`mailto:${siteConfig.company.legalEmail}`}
                className="text-accent-strong underline underline-offset-2"
              >
                {siteConfig.company.legalEmail}
              </a>
              <br />
              Website:{" "}
              <a
                href={siteConfig.company.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-accent-strong underline underline-offset-2"
              >
                {siteConfig.company.url}
              </a>
            </p>
          </div>

          <div>
            <h2 className="text-lg font-semibold text-ink dark:text-white">
              Handelsregister / UID
            </h2>
            <p className="mt-3">
              Handelsregister-Nr. / Unternehmens-Identifikationsnummer (UID):
              <br />
              {siteConfig.company.registerNumber}
            </p>
          </div>

          <div>
            <h2 className="text-lg font-semibold text-ink dark:text-white">
              Hinweis zum Angebot
            </h2>
            <p className="mt-3">
              {siteConfig.company.legalName} hat ihren Sitz in der Schweiz. OnLumis (
              {siteConfig.url}) ist ein Produkt der {siteConfig.company.legalName} und richtet
              sich als B2B-Angebot auch an Unternehmenskundinnen und -kunden in Deutschland und
              der übrigen EU. Es liegt kein Verbraucherangebot im Sinne der
              Verbraucherstreitbeilegung vor.
            </p>
          </div>

          <div>
            <h2 className="text-lg font-semibold text-ink dark:text-white">Haftungsausschluss</h2>
            <p className="mt-3">
              Die Inhalte dieser Website werden mit grösster Sorgfalt erstellt. Für die
              Richtigkeit, Vollständigkeit und Aktualität der Inhalte übernehmen wir jedoch keine
              Gewähr. Als Anbieterin sind wir für eigene Inhalte auf dieser Website nach den
              allgemeinen gesetzlichen Bestimmungen verantwortlich.
            </p>
            <p className="mt-3">
              Diese Website kann Links zu externen Websites Dritter enthalten, auf deren Inhalte
              wir keinen Einfluss haben. Für diese fremden Inhalte übernehmen wir daher keine
              Gewähr; verantwortlich ist stets die jeweilige Anbieterin oder der jeweilige
              Betreiber der verlinkten Seite. Bei Bekanntwerden von Rechtsverletzungen werden
              entsprechende Links umgehend entfernt.
            </p>
          </div>

          <div>
            <h2 className="text-lg font-semibold text-ink dark:text-white">Urheberrecht</h2>
            <p className="mt-3">
              Die durch die Seitenbetreiberin erstellten Inhalte und Werke auf dieser Website
              unterliegen dem Urheberrecht. Die Vervielfältigung, Bearbeitung, Verbreitung und
              jede Art der Verwertung ausserhalb der Grenzen des Urheberrechts bedürfen der
              schriftlichen Zustimmung der {siteConfig.company.legalName}.
            </p>
          </div>
        </div>
      </Container>
    </section>
  );
}
