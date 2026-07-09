import type { Metadata } from "next";
import { Container } from "@/components/Container";
import { PageHero } from "@/components/PageHero";
import { SectionHeading } from "@/components/SectionHeading";
import { CtaButton } from "@/components/CtaButton";
import { IconCheckCircle, IconArrowRight } from "@/components/icons";

export const metadata: Metadata = {
  title: "Anwendungsfälle – OnLumis in Ihren Fachbereichen",
  description:
    "Konkrete Anwendungsfälle einer lokalen Unternehmens-KI: von Vertrieb und Kundenservice über HR und IT bis zu Recht, Produktion und Geschäftsführung.",
  alternates: { canonical: "/anwendungsfaelle" },
};

const departments = [
  {
    title: "Geschäftsführung & Strategie",
    intro: "Schneller Überblick über verteiltes Wissen – als Entscheidungsgrundlage.",
    cases: [
      "Zusammenfassung interner Berichte, Protokolle und Strategiepapiere auf Nachfrage.",
      "Schnelle Beantwortung von Fragen zu internen Richtlinien und Prozessen ohne Rückfrage bei Fachabteilungen.",
      "Grundlage für strukturiertes Wissensmanagement bei Nachfolge- oder Wachstumsplanung.",
    ],
  },
  {
    title: "Vertrieb & Kundenservice",
    intro: "Schnellere, konsistente Antworten – intern wie im Kundenkontakt.",
    cases: [
      "Sofortiger Zugriff auf Produktdetails, Konditionen und Vertragsklauseln während des Kundengesprächs.",
      "Unterstützung bei der Angebotserstellung durch Vorlagen- und Referenztexte aus früheren Projekten.",
      "Schnellere Bearbeitung wiederkehrender Kundenanfragen im Support, gestützt auf interne FAQ und Wissensdatenbanken.",
    ],
  },
  {
    title: "HR & Personalwesen",
    intro: "Onboarding und interne Fragen effizienter beantworten.",
    cases: [
      "Neue Mitarbeitende erhalten Antworten zu Prozessen, Benefits und internen Richtlinien, ohne HR direkt zu kontaktieren.",
      "Schnellere Beantwortung wiederkehrender Fragen zu Urlaub, Reisekosten oder internen Abläufen.",
      "Zentrale, aktuelle Wissensbasis für alle Standorte und Teams.",
    ],
  },
  {
    title: "IT & Technik",
    intro: "Internes technisches Wissen sichtbar und nutzbar machen.",
    cases: [
      "Dokumentation zu Systemen, Konfigurationen und wiederkehrenden Störungen wird durchsuchbar statt in Tickets verloren zu gehen.",
      "Unterstützung des internen IT-Supports bei der Diagnose bekannter Probleme.",
      "Wissenssicherung bei Personalwechsel in technischen Rollen.",
    ],
  },
  {
    title: "Recht, Qualität & Compliance",
    intro: "Schneller Zugriff auf Richtlinien, ohne Vertraulichkeit zu gefährden.",
    cases: [
      "Beantwortung von Fragen zu internen Compliance-Vorgaben und Qualitätsrichtlinien.",
      "Unterstützung bei der Recherche in Verträgen und Vertragsanhängen.",
      "Nachvollziehbare, quellenbasierte Antworten für Audits und Zertifizierungen – ohne dass vertrauliche Inhalte das Haus verlassen.",
    ],
  },
  {
    title: "Produktion & Qualitätssicherung",
    intro: "Erfahrungswissen sichern und für alle Schichten verfügbar machen.",
    cases: [
      "Zugriff auf Arbeitsanweisungen, Maschinenhandbücher und Wartungsprotokolle direkt an der Linie.",
      "Schnellere Einarbeitung neuer Mitarbeitender in Produktionsprozesse.",
      "Sicherung von Erfahrungswissen langjähriger Mitarbeitender für den Ruhestand oder Personalwechsel.",
    ],
  },
];

const industries = [
  {
    title: "Industrie & produzierendes Gewerbe",
    text: "Maschinen- und Prozessdokumentation, Qualitätsrichtlinien und Erfahrungswissen zentral verfügbar machen.",
  },
  {
    title: "Handwerk & technische Dienstleister",
    text: "Schneller Zugriff auf technische Datenblätter, Montageanleitungen und Kundenprojekte im Außendienst.",
  },
  {
    title: "Kanzleien & Beratungsunternehmen",
    text: "Vertrauliche Mandats- und Vertragsdaten bleiben vollständig im Haus, während Recherchezeiten sinken.",
  },
  {
    title: "Gesundheitswesen & Pflege",
    text: "Interne Richtlinien, Hygienevorschriften und Abläufe sind für besonders sensible Umgebungen ausschließlich lokal verfügbar.",
  },
  {
    title: "Handel & Großhandel",
    text: "Produktinformationen, Lieferantenverträge und interne Prozesse für Einkauf und Vertrieb schnell zugänglich.",
  },
  {
    title: "Öffentliche Einrichtungen & Verbände",
    text: "Nachvollziehbare, DSGVO-konforme Wissensvermittlung ohne Abhängigkeit von US-Cloud-Diensten.",
  },
];

export default function AnwendungsfaellePage() {
  return (
    <>
      <PageHero
        eyebrow="Anwendungsfälle"
        title="OnLumis im Alltag Ihrer Fachbereiche"
        description="Ob Vertrieb, HR, IT oder Produktion: OnLumis macht das vorhandene Wissen Ihres Unternehmens für jede Abteilung nutzbar – zugeschnitten auf die jeweiligen Berechtigungen."
      >
        <CtaButton href="/kontakt">Passenden Anwendungsfall besprechen</CtaButton>
      </PageHero>

      <section className="py-20 sm:py-28">
        <Container>
          <SectionHeading eyebrow="Nach Fachbereich" title="Konkreter Nutzen in jeder Abteilung" />
          <div className="mt-14 grid gap-6 lg:grid-cols-2">
            {departments.map((dept) => (
              <div key={dept.title} className="rounded-2xl border border-border bg-surface p-7">
                <h3 className="font-display text-lg font-semibold text-ink dark:text-white">
                  {dept.title}
                </h3>
                <p className="mt-2 text-sm text-muted">{dept.intro}</p>
                <ul className="mt-4 space-y-2.5">
                  {dept.cases.map((c) => (
                    <li key={c} className="flex items-start gap-2.5 text-sm text-muted">
                      <IconCheckCircle className="mt-0.5 h-4 w-4 shrink-0 text-accent-strong" />
                      {c}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </Container>
      </section>

      <section className="bg-surface-alt py-20 sm:py-28">
        <Container>
          <SectionHeading eyebrow="Nach Branche" title="Besonders gefragt in diesen Branchen" />
          <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {industries.map((industry) => (
              <div key={industry.title} className="rounded-2xl border border-border bg-surface p-6">
                <h3 className="font-display text-base font-semibold text-ink dark:text-white">
                  {industry.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-muted">{industry.text}</p>
              </div>
            ))}
          </div>
        </Container>
      </section>

      <section className="bg-primary py-20 text-white sm:py-24">
        <Container className="flex flex-col items-center gap-6 text-center">
          <h2 className="font-display text-3xl font-semibold sm:text-4xl">
            Welcher Anwendungsfall passt zu Ihnen?
          </h2>
          <p className="max-w-xl text-white/75">
            Erzählen Sie uns von Ihrer Situation – wir zeigen Ihnen, wie OnLumis in Ihrem
            konkreten Umfeld eingesetzt werden kann.
          </p>
          <CtaButton href="/kontakt">
            Jetzt Kontakt aufnehmen <IconArrowRight />
          </CtaButton>
        </Container>
      </section>
    </>
  );
}
