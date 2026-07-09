import type { Metadata } from "next";
import { Container } from "@/components/Container";
import { PageHero } from "@/components/PageHero";
import { ContactForm } from "@/components/ContactForm";
import { IconCheckCircle } from "@/components/icons";
import { siteConfig } from "@/lib/site";

export const metadata: Metadata = {
  title: "Kontakt – Unverbindliches Erstgespräch zu OnLumis",
  description:
    "Nehmen Sie Kontakt zu JULITH GmbH auf und erfahren Sie, wie OnLumis als lokale, DSGVO-konforme KI-Lösung in Ihrem Unternehmen eingeführt werden kann.",
  alternates: { canonical: "/kontakt" },
};

const points = [
  "Antwort in der Regel innerhalb von 1–2 Werktagen",
  "Unverbindliches Erstgespräch, keine versteckten Kosten",
  "Persönliche Beratung durch die JULITH GmbH",
  "Auf Wunsch inklusive Einschätzung zu Fördermöglichkeiten",
];

export default function KontaktPage() {
  return (
    <>
      <PageHero
        eyebrow="Kontakt"
        title="Lassen Sie uns über Ihre Unternehmens-KI sprechen"
        description="Egal ob Sie schon eine konkrete Vorstellung haben oder OnLumis erst kennenlernen möchten – wir freuen uns auf Ihre Nachricht."
      />

      <section className="py-20 sm:py-28">
        <Container className="grid gap-12 lg:grid-cols-3">
          <div className="lg:col-span-1">
            <h2 className="font-display text-xl font-semibold text-ink dark:text-white">
              Was Sie erwarten können
            </h2>
            <ul className="mt-5 space-y-3">
              {points.map((point) => (
                <li key={point} className="flex items-start gap-3 text-sm text-muted">
                  <IconCheckCircle className="mt-0.5 h-5 w-5 shrink-0 text-accent-strong" />
                  {point}
                </li>
              ))}
            </ul>

            <div className="mt-10 rounded-2xl border border-border bg-surface-alt p-6">
              <h3 className="font-display text-base font-semibold text-ink dark:text-white">
                Direkter Kontakt
              </h3>
              <p className="mt-2 text-sm text-muted">
                <a
                  href={`mailto:${siteConfig.company.contactEmail}`}
                  className="font-medium text-accent-strong hover:underline"
                >
                  {siteConfig.company.contactEmail}
                </a>
              </p>
              <p className="mt-3 text-sm text-muted">
                Ein Angebot der {siteConfig.company.legalName}
                <br />
                <a
                  href={siteConfig.company.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-accent-strong hover:underline"
                >
                  julith.gmbh
                </a>
              </p>
            </div>
          </div>

          <div className="rounded-2xl border border-border bg-surface p-6 sm:p-8 lg:col-span-2">
            <ContactForm />
          </div>
        </Container>
      </section>
    </>
  );
}
