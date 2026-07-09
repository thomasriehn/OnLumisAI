import type { Metadata } from "next";
import { Container } from "@/components/Container";
import { PageHero } from "@/components/PageHero";
import { SectionHeading } from "@/components/SectionHeading";
import { FeatureCard } from "@/components/FeatureCard";
import { CtaButton } from "@/components/CtaButton";
import {
  IconLayers,
  IconDatabase,
  IconCpu,
  IconLock,
  IconServer,
  IconPlug,
  IconCheckCircle,
  IconArrowRight,
  IconChat,
  IconSearch,
} from "@/components/icons";

export const metadata: Metadata = {
  title: "Produkt – Wie OnLumis Ihre lokale Unternehmens-KI aufbaut",
  description:
    "Architektur, Datenintegration, KI-Modelle, Sicherheit und Betrieb von OnLumis im Detail: So entsteht aus Ihrem Unternehmenswissen eine On-Premise-KI ohne Cloud-Zwang.",
  alternates: { canonical: "/produkt" },
};

const architectureLayers = [
  {
    icon: <IconDatabase />,
    title: "Datenquellen",
    text: "Fileserver/NAS, DMS-Systeme, SharePoint, Confluence/Wikis, E-Mail-Postfächer, ERP-/CRM-Exporte, PDF, Word, Excel und gescannte Dokumente (OCR).",
  },
  {
    icon: <IconLayers />,
    title: "Aufbereitung & Embedding",
    text: "Dokumente werden bereinigt, in sinnvolle Abschnitte zerlegt und als Vektor-Embeddings in einer lokalen Vektordatenbank abgelegt – die technische Grundlage für präzises Wiederfinden von Wissen (Retrieval-Augmented Generation, RAG).",
  },
  {
    icon: <IconCpu />,
    title: "Lokales Sprachmodell",
    text: "Ein leistungsfähiges, quelloffenes Sprachmodell läuft vollständig auf Ihrer Infrastruktur und formuliert Antworten – ausschließlich gestützt auf die von Ihnen freigegebenen Inhalte.",
  },
  {
    icon: <IconPlug />,
    title: "Zugriffsschicht",
    text: "Chat-Oberfläche, interne Suche, Microsoft-Teams-Anbindung oder eigene API – Ihre Teams greifen dort auf OnLumis zu, wo sie ohnehin arbeiten.",
  },
];

const dataSources = [
  "Datei- und NAS-Server (SMB/NFS)",
  "Dokumentenmanagementsysteme (z. B. ELO, d.velop, DATEV-Umfelder)",
  "SharePoint, OneDrive, Google Workspace",
  "Confluence, Wikis und interne Handbücher",
  "E-Mail-Postfächer und Ticketsysteme (nach expliziter Freigabe)",
  "ERP- und CRM-Exporte, strukturierte Tabellen",
  "PDF, Word, Excel, PowerPoint sowie gescannte Dokumente per OCR",
];

const security = [
  {
    icon: <IconLock />,
    title: "Verschlüsselung durchgängig",
    text: "Daten werden verschlüsselt gespeichert (at rest) und verschlüsselt übertragen (in transit) – auch innerhalb Ihres Netzwerks.",
  },
  {
    icon: <IconServer />,
    title: "Rollen- und Rechtekonzept",
    text: "Anbindung an Active Directory / LDAP / SSO. Nutzer sehen nur Informationen, für die sie berechtigt sind – bis auf Dokumentenebene steuerbar.",
  },
  {
    icon: <IconCheckCircle />,
    title: "Protokollierung & Nachvollziehbarkeit",
    text: "Zugriffe und Antworten werden protokolliert, damit IT-Sicherheit und Datenschutzbeauftragte jederzeit nachvollziehen können, wer worauf zugegriffen hat.",
  },
  {
    icon: <IconLayers />,
    title: "Netzwerkisolation möglich",
    text: "Auf Wunsch vollständig vom Internet getrennter Betrieb (air-gapped) für besonders schutzbedürftige Umgebungen, z. B. in der Fertigung oder im Gesundheitswesen.",
  },
];

const deploymentOptions = [
  {
    title: "On-Premise im eigenen Haus",
    text: "OnLumis läuft auf einem Server in Ihrem eigenen Serverraum oder Rechenzentrum. Maximale Kontrolle, keine Abhängigkeit von externen Anbietern.",
  },
  {
    title: "Exklusive Private Cloud in Deutschland/EU",
    text: "Für Unternehmen ohne eigene Serverinfrastruktur betreiben wir OnLumis in einem zertifizierten deutschen oder europäischen Rechenzentrum – exklusiv für Sie, nicht als geteilter Cloud-Dienst.",
  },
  {
    title: "Hybrid",
    text: "Sensible Daten bleiben on-premise, weniger kritische Anwendungsfälle laufen in der Private Cloud – abgestimmt auf Ihre Sicherheitsanforderungen.",
  },
];

const onboarding = [
  {
    title: "Kickoff-Workshop",
    text: "Wir erfassen Ihre wichtigsten Wissensquellen, Zielgruppen im Unternehmen und die relevantesten Anwendungsfälle.",
  },
  {
    title: "Datenaufnahme & Klassifizierung",
    text: "Gemeinsam legen wir fest, welche Dokumente und Systeme eingebunden werden und wer worauf Zugriff erhalten soll.",
  },
  {
    title: "Aufbau der Wissensbasis",
    text: "Ihre Daten werden aufbereitet, eingebettet und mit dem lokalen Sprachmodell verbunden. Erste Tests erfolgen in einer geschützten Umgebung.",
  },
  {
    title: "Pilotphase mit ausgewähltem Team",
    text: "Eine Pilotgruppe testet OnLumis im Alltag. Feedback fließt direkt in Feinjustierung von Antwortqualität und Berechtigungen ein.",
  },
  {
    title: "Go-Live & unternehmensweiter Rollout",
    text: "Nach erfolgreicher Pilotphase wird OnLumis für weitere Teams freigeschaltet – schrittweise oder unternehmensweit.",
  },
  {
    title: "Laufender Betrieb & Pflege",
    text: "JULITH GmbH übernimmt technischen Support, Modellpflege, Sicherheitsupdates und die Erweiterung um neue Wissensquellen.",
  },
];

export default function ProduktPage() {
  return (
    <>
      <PageHero
        eyebrow="Das Produkt"
        title="OnLumis: Eine KI, die ausschließlich mit Ihrem Wissen arbeitet"
        description="OnLumis verbindet ein leistungsfähiges, lokal betriebenes Sprachmodell mit den Dokumenten, Prozessen und dem Erfahrungswissen Ihres Unternehmens – installiert und betrieben dort, wo Ihre Daten hingehören: bei Ihnen."
      >
        <CtaButton href="/kontakt">Persönliche Beratung anfragen</CtaButton>
      </PageHero>

      <section className="py-20 sm:py-28">
        <Container className="max-w-3xl">
          <SectionHeading align="left" eyebrow="Überblick" title="Was OnLumis konkret leistet" />
          <div className="prose-content mt-8 space-y-5 text-muted">
            <p>
              Große Sprachmodelle wie sie aus öffentlichen Cloud-Diensten bekannt sind, kennen
              „die Welt&quot; – aber nicht Ihr Unternehmen. OnLumis schließt genau diese Lücke:
              Statt auf allgemeinem Internet-Wissen zu basieren, wird ein leistungsfähiges
              KI-Modell mit den tatsächlichen Inhalten Ihres Unternehmens verbunden – Ihren
              Handbüchern, Richtlinien, Verträgen, Produktinformationen, internen Wikis und
              Erfahrungswerten.
            </p>
            <p>
              Technisch nutzt OnLumis dafür ein Verfahren namens{" "}
              <strong>Retrieval-Augmented Generation (RAG)</strong>: Ihre Dokumente werden in
              durchsuchbare Wissenseinheiten zerlegt und in einer lokalen Vektordatenbank
              abgelegt. Stellt ein Mitarbeitender eine Frage, sucht das System zunächst die
              relevantesten Inhalte aus Ihrer eigenen Wissensbasis heraus und lässt das
              Sprachmodell darauf basierend eine präzise, nachvollziehbare Antwort formulieren –
              inklusive Quellenangabe zum Ursprungsdokument.
            </p>
            <p>
              Das Ergebnis: deutlich weniger falsche oder erfundene Antworten
              („Halluzinationen&quot;), maximale Kontrolle über die verwendeten Daten und ein
              System, das mit jedem neuen Dokument klüger wird – ohne dass eine einzige Information
              Ihr Unternehmen verlässt.
            </p>
          </div>
        </Container>
      </section>

      <section className="bg-surface-alt py-20 sm:py-28">
        <Container>
          <SectionHeading
            eyebrow="Architektur"
            title="So ist OnLumis aufgebaut"
            description="Vier zusammenspielende Ebenen sorgen dafür, dass aus Ihren Rohdaten verlässliches, abrufbares Unternehmenswissen wird."
          />
          <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {architectureLayers.map((layer) => (
              <FeatureCard key={layer.title} icon={layer.icon} title={layer.title}>
                {layer.text}
              </FeatureCard>
            ))}
          </div>
        </Container>
      </section>

      <section className="py-20 sm:py-28">
        <Container className="grid gap-12 lg:grid-cols-2 lg:items-start">
          <div>
            <SectionHeading align="left" eyebrow="Datenintegration" title="Welche Wissensquellen OnLumis einbindet" />
            <ul className="mt-8 space-y-3">
              {dataSources.map((source) => (
                <li key={source} className="flex items-start gap-3 text-sm text-muted">
                  <IconCheckCircle className="mt-0.5 h-5 w-5 shrink-0 text-accent-strong" />
                  {source}
                </li>
              ))}
            </ul>
          </div>
          <div className="rounded-2xl border border-border bg-surface-alt p-8">
            <h3 className="font-display text-xl font-semibold text-ink dark:text-white">
              KI-Modelle & Technologie
            </h3>
            <p className="mt-4 text-sm leading-relaxed text-muted">
              OnLumis setzt auf ausgewählte, quelloffene Sprachmodelle (z. B. aus den
              Modellfamilien Llama, Mistral oder vergleichbare, für den deutschsprachigen Einsatz
              geeignete Modelle), die vollständig lokal betrieben werden. Es besteht keine
              Abhängigkeit von einer laufenden Verbindung zu OpenAI, Microsoft, Google oder
              anderen Cloud-KI-Anbietern.
            </p>
            <p className="mt-4 text-sm leading-relaxed text-muted">
              Die Modellauswahl richtet sich nach Ihrem Anwendungsfall, der verfügbaren Hardware
              und den Anforderungen an Antwortqualität und Geschwindigkeit. Updates und
              Modellwechsel werden von JULITH GmbH geprüft und kontrolliert eingespielt, bevor sie
              produktiv genutzt werden.
            </p>
          </div>
        </Container>
      </section>

      <section className="bg-surface-alt py-20 sm:py-28">
        <Container>
          <SectionHeading
            eyebrow="Sicherheit"
            title="Sicherheits- und Zugriffskonzept"
            description="OnLumis ist für den Einsatz in schutzbedürftigen Unternehmensumgebungen konzipiert."
          />
          <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {security.map((item) => (
              <FeatureCard key={item.title} icon={item.icon} title={item.title}>
                {item.text}
              </FeatureCard>
            ))}
          </div>
        </Container>
      </section>

      <section className="py-20 sm:py-28">
        <Container>
          <SectionHeading eyebrow="Betriebsmodelle" title="Wie und wo OnLumis betrieben wird" />
          <div className="mt-14 grid gap-6 lg:grid-cols-3">
            {deploymentOptions.map((option) => (
              <div key={option.title} className="rounded-2xl border border-border bg-surface p-6">
                <h3 className="font-display text-lg font-semibold text-ink dark:text-white">
                  {option.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-muted">{option.text}</p>
              </div>
            ))}
          </div>
        </Container>
      </section>

      <section className="bg-surface-alt py-20 sm:py-28">
        <Container>
          <SectionHeading eyebrow="Zugriff im Alltag" title="Nahtlos dort nutzbar, wo Ihre Teams arbeiten" />
          <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <FeatureCard icon={<IconChat />} title="Chat-Oberfläche">
              Eine einfache, im Corporate Design anpassbare Weboberfläche für natürlichsprachliche
              Fragen an Ihr Unternehmenswissen.
            </FeatureCard>
            <FeatureCard icon={<IconSearch />} title="Intelligente Suche">
              Integration in bestehende Intranet- oder Portallösungen als intelligente
              Volltextsuche mit Quellenangabe.
            </FeatureCard>
            <FeatureCard icon={<IconPlug />} title="Teams- & API-Anbindung">
              Anbindung an Microsoft Teams sowie eine dokumentierte API-Schnittstelle für die
              Integration in eigene Anwendungen.
            </FeatureCard>
          </div>
        </Container>
      </section>

      <section className="py-20 sm:py-28">
        <Container>
          <SectionHeading
            eyebrow="Einführung"
            title="Von der ersten Analyse bis zum laufenden Betrieb"
            description="Ein strukturierter, gemeinsam mit Ihnen abgestimmter Prozess sorgt für einen reibungslosen Einstieg."
          />
          <ol className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {onboarding.map((step, index) => (
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
            Bereit für Ihre eigene Unternehmens-KI?
          </h2>
          <p className="max-w-xl text-white/75">
            Vereinbaren Sie ein unverbindliches Gespräch – wir analysieren gemeinsam Ihre
            Ausgangslage und zeigen konkrete nächste Schritte auf.
          </p>
          <CtaButton href="/kontakt">
            Kontakt aufnehmen <IconArrowRight />
          </CtaButton>
        </Container>
      </section>
    </>
  );
}
