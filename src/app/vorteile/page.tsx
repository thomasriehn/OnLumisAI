import type { Metadata } from "next";
import { Container } from "@/components/Container";
import { PageHero } from "@/components/PageHero";
import { SectionHeading } from "@/components/SectionHeading";
import { FeatureCard } from "@/components/FeatureCard";
import { CtaButton } from "@/components/CtaButton";
import {
  IconShield,
  IconEuro,
  IconUsers,
  IconServer,
  IconDatabase,
  IconCpu,
  IconCheckCircle,
  IconArrowRight,
} from "@/components/icons";

export const metadata: Metadata = {
  title: "Vorteile – Was eine lokale KI Ihrem Unternehmen bringt",
  description:
    "Datenschutz, Wirtschaftlichkeit und Wettbewerbsfähigkeit im Vergleich: die konkreten Vorteile einer On-Premise-KI mit OnLumis gegenüber klassischen Cloud-KI-Diensten.",
  alternates: { canonical: "/vorteile" },
};

const comparison = [
  {
    aspect: "Speicherort der Daten",
    cloud: "Server außereuropäischer Anbieter, oft intransparent",
    kern: "Ihr Serverraum oder ein Rechenzentrum in Deutschland/EU",
  },
  {
    aspect: "DSGVO-Konformität",
    cloud: "Zusätzliche Verträge (SCC, AVV) und Restrisiken nötig",
    kern: "Von der Architektur her eingebaut, keine Datenübermittlung an Dritte",
  },
  {
    aspect: "Kostenmodell",
    cloud: "Laufende, nutzungsabhängige Gebühren pro Anfrage/Token",
    kern: "Einmalige Investition in Infrastruktur & Einrichtung, planbarer Betrieb",
  },
  {
    aspect: "Datengrundlage der Antworten",
    cloud: "Allgemeines Internet-Wissen, oft ohne Quellenbezug",
    kern: "Ausschließlich Ihr freigegebenes Unternehmenswissen, mit Quellenangabe",
  },
  {
    aspect: "Verfügbarkeit & Kontrolle",
    cloud: "Abhängig vom Anbieter, dessen Preisänderungen und Abschaltungen",
    kern: "Sie entscheiden über Betrieb, Updates und Weiterentwicklung",
  },
  {
    aspect: "Förderfähigkeit",
    cloud: "Reine Software-Abonnements meist nicht förderfähig",
    kern: "Als Digitalisierungsprojekt förderfähig, z. B. über Digitalisierungsprogramme der Länder",
  },
];

const categories = [
  {
    icon: <IconShield />,
    title: "Datenschutz & Compliance",
    intro:
      "Für viele Unternehmen ist der Schutz sensibler Daten kein „Nice-to-have&quot;, sondern Voraussetzung für den Einsatz von KI überhaupt.",
    points: [
      "Keine Übermittlung personenbezogener oder geschäftskritischer Daten an außereuropäische Cloud-Anbieter.",
      "Datenverarbeitung im Rahmen eines klar geregelten Auftragsverarbeitungsvertrags (Art. 28 DSGVO).",
      "Vollständige Nachvollziehbarkeit für Datenschutzbeauftragte, Betriebsrat und IT-Sicherheit.",
      "Reduziertes Risiko im Vergleich zu Schatten-KI, bei der Mitarbeitende eigenmächtig öffentliche KI-Tools mit Firmendaten nutzen.",
    ],
  },
  {
    icon: <IconEuro />,
    title: "Wirtschaftlichkeit",
    intro:
      "On-Premise-KI verschiebt die Kostenstruktur von laufenden, schwer kalkulierbaren Ausgaben hin zu einer klar planbaren Investition.",
    points: [
      "Keine Kosten pro Anfrage oder pro verarbeitetem Token wie bei vielen Cloud-KI-Abonnements.",
      "Investitionskosten sind häufig über Digitalisierungsförderungen der Bundesländer bezuschussbar.",
      "Zeitersparnis durch schnelleren Zugriff auf internes Wissen zahlt sich unmittelbar in Produktivität aus.",
      "Ein System für viele Anwendungsfälle statt vieler einzelner Tool-Abonnements.",
    ],
  },
  {
    icon: <IconUsers />,
    title: "Effizienz & Wettbewerbsfähigkeit",
    intro:
      "Wissen, das sonst nur in Köpfen oder unstrukturierten Ordnern liegt, wird für das gesamte Unternehmen nutzbar.",
    points: [
      "Schnellerer Zugriff auf Richtlinien, Produktwissen und Vertragsdetails für alle Abteilungen.",
      "Kürzere Einarbeitungszeiten für neue Mitarbeitende.",
      "Entlastung von erfahrenen Fachkräften, die nicht mehr jede Rückfrage einzeln beantworten müssen.",
      "Konsistente, aktuelle Antworten statt veralteter oder widersprüchlicher Informationen.",
    ],
  },
  {
    icon: <IconServer />,
    title: "Unabhängigkeit & Zukunftssicherheit",
    intro:
      "Sie bleiben Herr der Lage – technologisch wie wirtschaftlich.",
    points: [
      "Keine Abhängigkeit von Preismodellen, Nutzungsbedingungen oder Abschaltungen einzelner Cloud-Anbieter.",
      "Freie Wahl und Austauschbarkeit der eingesetzten KI-Modelle, je nach technologischem Fortschritt.",
      "Investition bleibt auch bei Anbieterwechseln im Markt für Sie nutzbar, da Infrastruktur und Daten Ihnen gehören.",
      "Skalierbar von einzelnen Abteilungen bis zum unternehmensweiten Einsatz.",
    ],
  },
];

export default function VorteilePage() {
  return (
    <>
      <PageHero
        eyebrow="Vorteile"
        title="Warum sich eine lokale Unternehmens-KI für Sie auszahlt"
        description="OnLumis verbindet die Leistungsfähigkeit moderner KI mit den Anforderungen an Datenschutz, Kostenkontrolle und Unabhängigkeit, die für den deutschen Mittelstand zählen."
      >
        <CtaButton href="/kontakt">Individuelles Nutzenpotenzial ermitteln</CtaButton>
      </PageHero>

      <section className="py-20 sm:py-28">
        <Container>
          <SectionHeading
            eyebrow="Im Vergleich"
            title="OnLumis vs. klassische Cloud-KI"
            description="Ein direkter Blick auf die wichtigsten Unterschiede."
          />
          <div className="mt-12 overflow-x-auto rounded-2xl border border-border">
            <table className="w-full min-w-[640px] border-collapse text-left text-sm">
              <thead>
                <tr className="bg-surface-alt">
                  <th className="p-4 font-semibold text-ink dark:text-white">Kriterium</th>
                  <th className="p-4 font-semibold text-ink dark:text-white">Klassische Cloud-KI</th>
                  <th className="p-4 font-semibold text-accent-strong">OnLumis (On-Premise)</th>
                </tr>
              </thead>
              <tbody>
                {comparison.map((row, index) => (
                  <tr
                    key={row.aspect}
                    className={index % 2 === 0 ? "bg-surface" : "bg-surface-alt/50"}
                  >
                    <td className="p-4 font-medium text-ink dark:text-white">{row.aspect}</td>
                    <td className="p-4 text-muted">{row.cloud}</td>
                    <td className="p-4 text-muted">{row.kern}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Container>
      </section>

      {categories.map((category, index) => (
        <section
          key={category.title}
          className={index % 2 === 0 ? "bg-surface-alt py-20 sm:py-24" : "py-20 sm:py-24"}
        >
          <Container className="grid gap-10 lg:grid-cols-3 lg:items-start">
            <div className="lg:col-span-1">
              <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-accent-strong/10 text-accent-strong">
                {category.icon}
              </div>
              <h2 className="mt-4 font-display text-2xl font-semibold text-ink dark:text-white">
                {category.title}
              </h2>
              <p className="mt-3 text-muted">{category.intro}</p>
            </div>
            <ul className="grid gap-4 lg:col-span-2 sm:grid-cols-2">
              {category.points.map((point) => (
                <li
                  key={point}
                  className="flex items-start gap-3 rounded-xl border border-border bg-surface p-4 text-sm text-muted"
                >
                  <IconCheckCircle className="mt-0.5 h-5 w-5 shrink-0 text-accent-strong" />
                  {point}
                </li>
              ))}
            </ul>
          </Container>
        </section>
      ))}

      <section className="py-20 sm:py-28">
        <Container>
          <SectionHeading eyebrow="Für wen geeignet" title="OnLumis passt zu Unternehmen, die..." />
          <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <FeatureCard icon={<IconDatabase />} title="viel wertvolles Wissen besitzen">
              Handbücher, Richtlinien, Verträge oder Erfahrungswissen sind vorhanden, aber schwer
              auffindbar oder an einzelne Personen gebunden.
            </FeatureCard>
            <FeatureCard icon={<IconShield />} title="hohe Anforderungen an Datenschutz haben">
              Etwa in der Industrie, im Gesundheitswesen, bei Kanzleien oder im
              öffentlichkeitsnahen Umfeld.
            </FeatureCard>
            <FeatureCard icon={<IconCpu />} title="KI produktiv nutzen wollen, ohne Kontrolle abzugeben">
              Sie möchten die Vorteile moderner KI nutzen, aber nicht auf Kosten von Datenhoheit
              und Unabhängigkeit.
            </FeatureCard>
          </div>
        </Container>
      </section>

      <section className="bg-primary py-20 text-white sm:py-24">
        <Container className="flex flex-col items-center gap-6 text-center">
          <h2 className="font-display text-3xl font-semibold sm:text-4xl">
            Lassen Sie uns Ihr konkretes Einsparpotenzial ermitteln
          </h2>
          <p className="max-w-xl text-white/75">
            In einem kostenlosen Erstgespräch schauen wir gemeinsam auf Ihre Ausgangslage und
            zeigen auf, welchen Mehrwert OnLumis für Ihr Unternehmen konkret bietet.
          </p>
          <CtaButton href="/kontakt">
            Erstgespräch vereinbaren <IconArrowRight />
          </CtaButton>
        </Container>
      </section>
    </>
  );
}
