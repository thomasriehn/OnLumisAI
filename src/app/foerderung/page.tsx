import type { Metadata } from "next";
import { Container } from "@/components/Container";
import { PageHero } from "@/components/PageHero";
import { SectionHeading } from "@/components/SectionHeading";
import { CtaButton } from "@/components/CtaButton";
import { IconCheckCircle, IconArrowRight, IconEuro } from "@/components/icons";

export const metadata: Metadata = {
  title: "Förderung – Digitalbonus Hessen & Co. für Ihre KI-Investition nutzen",
  description:
    "Wie Sie OnLumis über Digitalisierungsförderprogramme wie den Digitalbonus Hessen bezuschussen lassen können – inklusive Unterstützung bei der Antragstellung durch JULITH GmbH.",
  alternates: { canonical: "/foerderung" },
};

const eligibleCosts = [
  "Beratungsleistungen zur Analyse und Konzeption Ihrer Wissens-KI",
  "Implementierung, Einrichtung und Konfiguration von OnLumis",
  "Einbettung und Aufbereitung Ihrer Unternehmensdaten (Embedding-Prozess)",
  "Schulung und Einweisung Ihrer Mitarbeitenden",
  "In vielen Programmen anteilig: benötigte Hardware/Infrastruktur",
];

const otherPrograms = [
  {
    title: "go-digital (Bund)",
    text: "Förderprogramm des Bundesministeriums für Wirtschaft und Klimaschutz für kleine und mittlere Unternehmen, u. a. für die Module „Digitalisierte Geschäftsprozesse&quot; und „IT-Sicherheit&quot;.",
  },
  {
    title: "Digitalbonus / Digitalisierungsprogramme anderer Bundesländer",
    text: "Neben Hessen bieten u. a. Bayern, Nordrhein-Westfalen, Baden-Württemberg und weitere Länder eigene Digitalisierungsförderungen für KMU mit teils unterschiedlichen Schwerpunkten und Konditionen.",
  },
  {
    title: "Deutschland- und EU-Programme",
    text: "Ergänzend gibt es bundesweite und europäische Förderinstrumente für digitale Transformation und Innovationsvorhaben, deren Passung im Einzelfall geprüft werden sollte.",
  },
];

const steps = [
  {
    title: "Kostenlose Ersteinschätzung",
    text: "Wir prüfen gemeinsam mit Ihnen, ob und über welches Programm Ihr OnLumis-Projekt grundsätzlich förderfähig sein könnte.",
  },
  {
    title: "Angebot & Projektbeschreibung",
    text: "Sie erhalten ein detailliertes, förderkonformes Angebot inklusive der für die Antragstellung benötigten Projektbeschreibung.",
  },
  {
    title: "Begleitung bei der Antragstellung",
    text: "Wir unterstützen Sie bei der Zusammenstellung der Unterlagen für den Förderantrag bei der zuständigen Stelle (z. B. der WIBank in Hessen).",
  },
  {
    title: "Umsetzung & Verwendungsnachweis",
    text: "Nach Bewilligung setzen wir Ihr OnLumis-Projekt um und unterstützen Sie bei der Dokumentation für den Verwendungsnachweis.",
  },
];

export default function FoerderungPage() {
  return (
    <>
      <PageHero
        eyebrow="Förderung"
        title="Ihre OnLumis-Investition öffentlich fördern lassen"
        description="Digitalisierungsförderprogramme der Bundesländer und des Bundes unterstützen kleine und mittlere Unternehmen gezielt bei Investitionen in digitale Technologien – dazu zählt auch der Aufbau einer eigenen, lokalen Unternehmens-KI."
      >
        <CtaButton href="/kontakt">Förderfähigkeit unverbindlich prüfen lassen</CtaButton>
      </PageHero>

      <section className="py-20 sm:py-28">
        <Container className="max-w-3xl">
          <SectionHeading align="left" eyebrow="Im Fokus" title="Digitalbonus Hessen" />
          <div className="prose-content mt-6 space-y-5 text-muted">
            <p>
              Der <strong>Digitalbonus Hessen</strong> ist ein Zuschussprogramm des Landes Hessen,
              das über die Wirtschafts- und Infrastrukturbank Hessen (WIBank) kleine und mittlere
              Unternehmen bei Investitionen in die digitale Transformation unterstützt. Gefördert
              werden typischerweise Beratungs- und Umsetzungsleistungen für digitale Vorhaben –
              der Aufbau einer lokal betriebenen KI-Lösung wie OnLumis kann grundsätzlich in
              den Anwendungsbereich solcher Digitalisierungsprojekte fallen.
            </p>
            <p>
              Da sich Förderquoten, Höchstbeträge, Antragsfristen und Voraussetzungen bei
              Landesförderprogrammen regelmäßig ändern können, geben wir an dieser Stelle bewusst
              keine konkreten Prozentsätze oder Fördersummen an. Wir prüfen die aktuell gültigen
              Bedingungen gemeinsam mit Ihnen im Rahmen der Ersteinschätzung und verweisen für
              verbindliche Auskünfte an die offiziellen Stellen des Landes Hessen.
            </p>
          </div>
        </Container>
      </section>

      <section className="bg-surface-alt py-20 sm:py-28">
        <Container className="grid gap-10 lg:grid-cols-2">
          <div>
            <SectionHeading
              align="left"
              eyebrow="Förderfähige Kosten"
              title="Was im Rahmen von OnLumis typischerweise förderfähig sein kann"
            />
            <ul className="mt-8 space-y-3">
              {eligibleCosts.map((cost) => (
                <li key={cost} className="flex items-start gap-3 text-sm text-muted">
                  <IconCheckCircle className="mt-0.5 h-5 w-5 shrink-0 text-accent-strong" />
                  {cost}
                </li>
              ))}
            </ul>
          </div>
          <div className="rounded-2xl border border-gold/40 bg-surface p-8">
            <div className="inline-flex h-11 w-11 items-center justify-center rounded-xl bg-gold/10 text-gold">
              <IconEuro />
            </div>
            <h3 className="mt-4 font-display text-lg font-semibold text-ink dark:text-white">
              Wichtiger Hinweis
            </h3>
            <p className="mt-3 text-sm leading-relaxed text-muted">
              Alle Angaben auf dieser Seite dienen der ersten Orientierung und stellen keine
              rechtsverbindliche Förder- oder Rechtsberatung dar. Ob und in welcher Höhe eine
              Förderung tatsächlich möglich ist, hängt von den zum Zeitpunkt der Antragstellung
              geltenden Richtlinien, der Verfügbarkeit von Fördermitteln und der individuellen
              Prüfung durch die zuständige Förderstelle ab. Verbindliche Auskünfte erteilen
              ausschließlich die jeweiligen Förderinstitutionen, für Hessen insbesondere die
              WIBank.
            </p>
          </div>
        </Container>
      </section>

      <section className="py-20 sm:py-28">
        <Container>
          <SectionHeading
            eyebrow="Über Hessen hinaus"
            title="Weitere Förderprogramme für Ihr Bundesland"
            description="Auch außerhalb Hessens gibt es vergleichbare Programme – wir prüfen, welches für Ihren Unternehmenssitz infrage kommt."
          />
          <div className="mt-14 grid gap-6 lg:grid-cols-3">
            {otherPrograms.map((program) => (
              <div key={program.title} className="rounded-2xl border border-border bg-surface p-6">
                <h3 className="font-display text-lg font-semibold text-ink dark:text-white">
                  {program.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-muted">{program.text}</p>
              </div>
            ))}
          </div>
        </Container>
      </section>

      <section className="bg-surface-alt py-20 sm:py-28">
        <Container>
          <SectionHeading eyebrow="Ablauf" title="So unterstützen wir Sie bei der Förderung" />
          <ol className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {steps.map((step, index) => (
              <li key={step.title} className="rounded-2xl border border-border bg-surface p-6">
                <span className="font-display text-sm font-semibold text-accent-strong">
                  Schritt {index + 1}
                </span>
                <h3 className="mt-2 font-display text-lg font-semibold text-ink dark:text-white">
                  {step.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-muted">{step.text}</p>
              </li>
            ))}
          </ol>
        </Container>
      </section>

      <section className="bg-primary py-20 text-white sm:py-24">
        <Container className="flex flex-col items-center gap-6 text-center">
          <h2 className="font-display text-3xl font-semibold sm:text-4xl">
            Lassen Sie uns Ihre Förderoptionen klären
          </h2>
          <p className="max-w-xl text-white/75">
            Nennen Sie uns Ihren Unternehmenssitz und Ihr Vorhaben – wir sagen Ihnen, welche
            Förderprogramme für Ihre OnLumis-Einführung infrage kommen können.
          </p>
          <CtaButton href="/kontakt">
            Jetzt anfragen <IconArrowRight />
          </CtaButton>
        </Container>
      </section>
    </>
  );
}
