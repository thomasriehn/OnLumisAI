import type { Metadata } from "next";
import Link from "next/link";
import { Container } from "@/components/Container";
import { SectionHeading } from "@/components/SectionHeading";
import { FeatureCard } from "@/components/FeatureCard";
import { CtaButton } from "@/components/CtaButton";
import { FaqSection } from "@/components/FaqSection";
import {
  IconShield,
  IconServer,
  IconDatabase,
  IconEuro,
  IconUsers,
  IconCheckCircle,
  IconArrowRight,
  IconPlug,
  IconSearch,
  IconChat,
  IconLayers,
} from "@/components/icons";

export const metadata: Metadata = {
  title: "Lokale KI für Ihr Unternehmen – DSGVO-konform & On-Premise",
  description:
    "OnLumis bettet das Wissen Ihres Unternehmens in ein lokal betriebenes KI-System ein. DSGVO-konform, ohne Cloud-Zwang, förderfähig – entwickelt von der JULITH GmbH für den deutschen Mittelstand.",
  alternates: { canonical: "/" },
};

const trustBadges = [
  "100 % On-Premise",
  "DSGVO-konform von Grund auf",
  "Ihre Daten verlassen nie das Haus",
  "Förderfähig, z. B. über Digitalbonus Hessen",
];

const process = [
  {
    step: "01",
    title: "Analyse & Zielbild",
    description:
      "Gemeinsam analysieren wir Ihre Wissensquellen – von Dateiservern über DMS bis Ticketsysteme – und definieren, welche Fragen OnLumis für welche Teams beantworten soll.",
  },
  {
    step: "02",
    title: "Einbettung Ihres Wissens",
    description:
      "Ihre Dokumente, Handbücher, E-Mails und internen Wikis werden strukturiert aufbereitet, in Vektor-Embeddings überführt und in die lokale Wissensbasis eingebunden – ohne dass Inhalte an Dritte übertragen werden.",
  },
  {
    step: "03",
    title: "Installation vor Ort",
    description:
      "OnLumis wird auf einem Server in Ihrem Rechenzentrum, Serverraum oder in einer deutschen/EU-Private-Cloud-Umgebung installiert – abgeschottet von öffentlichen KI-Diensten.",
  },
  {
    step: "04",
    title: "Betrieb, Zugriff & Pflege",
    description:
      "Ihre Mitarbeitenden greifen über Chat, Suche oder Integrationen (z. B. Intranet, Teams) auf das System zu. JULITH GmbH übernimmt Updates, Modellpflege und technischen Support.",
  },
];

const advantages = [
  {
    icon: <IconShield />,
    title: "DSGVO-konform per Architektur",
    text: "Da alle Daten und Modelle lokal betrieben werden, entfällt die Übermittlung personenbezogener oder geschäftskritischer Daten an außereuropäische Cloud-Anbieter.",
  },
  {
    icon: <IconServer />,
    title: "Volle Datenhoheit",
    text: "Sie behalten die vollständige Kontrolle über Ihre Daten, Zugriffsrechte und Speicherorte – auditierbar und jederzeit nachvollziehbar.",
  },
  {
    icon: <IconDatabase />,
    title: "Nur Ihr Wissen, keine Fremddaten",
    text: "OnLumis antwortet ausschließlich auf Basis Ihrer eingebetteten Unternehmensdaten – das reduziert Falschantworten (Halluzinationen) erheblich.",
  },
  {
    icon: <IconEuro />,
    title: "Planbare Kosten statt Cloud-Abrechnung",
    text: "Keine unvorhersehbaren Kosten pro Anfrage oder Token. Sie investieren einmalig in Infrastruktur und Betrieb – förderfähig über Digitalisierungsprogramme.",
  },
  {
    icon: <IconUsers />,
    title: "Für Ihr ganzes Team nutzbar",
    text: "Vom Vertrieb über die Buchhaltung bis zur Geschäftsführung: Rollenbasierte Zugriffe sorgen dafür, dass jede Abteilung nur die für sie relevanten Informationen sieht.",
  },
  {
    icon: <IconPlug />,
    title: "Integriert sich in Ihre IT",
    text: "Anbindung an bestehende Systeme wie Fileserver, SharePoint, ERP oder Ticketsysteme – ohne Ihre bestehende IT-Landschaft zu ersetzen.",
  },
];

const useCasePreview = [
  {
    icon: <IconChat />,
    title: "Interner Wissens-Chat",
    text: "Mitarbeitende stellen Fragen in natürlicher Sprache und erhalten Antworten direkt aus Handbüchern, Richtlinien und internen Dokumenten.",
  },
  {
    icon: <IconSearch />,
    title: "Intelligente Dokumentensuche",
    text: "Statt Ordnerstrukturen zu durchsuchen, findet OnLumis die richtige Information in Sekunden – inklusive Quellenangabe.",
  },
  {
    icon: <IconUsers />,
    title: "Onboarding neuer Mitarbeitender",
    text: "Neue Kolleginnen und Kollegen erschließen sich Prozesse und Produktwissen selbstständig, statt Kolleg:innen ständig zu unterbrechen.",
  },
  {
    icon: <IconLayers />,
    title: "Support & Kundenservice",
    text: "Ihr Service-Team beantwortet Kundenanfragen schneller, gestützt auf firmeneigenes Produkt- und Vertragswissen.",
  },
];

const faqItems = [
  {
    question: "Ist meine KI dann wirklich komplett von der Cloud getrennt?",
    answer:
      "Ja. OnLumis wird als On-Premise-System auf Ihrer eigenen Infrastruktur oder in einem deutschen/EU-Rechenzentrum Ihrer Wahl betrieben. Es besteht keine zwingende Verbindung zu Cloud-KI-Anbietern wie OpenAI, Microsoft oder Google – Ihre Daten verlassen Ihr Unternehmen nicht.",
  },
  {
    question: "Welche Hardware benötige ich für OnLumis?",
    answer:
      "Der Bedarf hängt von Datenmenge, Nutzerzahl und gewünschter Antwortgeschwindigkeit ab. Für viele KMU reicht ein moderner Server mit ausreichend Arbeitsspeicher und einer GPU für die KI-Berechnung. Im Rahmen der Analysephase erstellen wir Ihnen eine konkrete Hardware- und Betriebsempfehlung, inklusive Optionen für gehostete Private-Cloud-Umgebungen in Deutschland.",
  },
  {
    question: "Wie lange dauert die Einführung von OnLumis?",
    answer:
      "Ein typisches Projekt – von der Analyse über die Einbettung Ihrer Daten bis zum produktiven Betrieb – dauert je nach Datenmenge und Integrationstiefe wenige Wochen. Wir starten häufig mit einem klar abgegrenzten Pilotbereich, um schnell echten Mehrwert sichtbar zu machen.",
  },
  {
    question: "Können wir Fördermittel wie den Digitalbonus Hessen nutzen?",
    answer:
      "In vielen Fällen ja. Digitalisierungsförderprogramme der Bundesländer – etwa der Digitalbonus Hessen – unterstützen KMU bei Investitionen in digitale Technologien wie OnLumis. Wir helfen Ihnen bei der Einschätzung der Förderfähigkeit und der Aufbereitung der notwendigen Unterlagen. Details finden Sie auf unserer Förderseite.",
  },
  {
    question: "Was passiert mit meinen Daten während der Einrichtung?",
    answer:
      "Ihre Dokumente werden ausschließlich innerhalb der vereinbarten, abgesicherten Umgebung verarbeitet. JULITH GmbH verarbeitet Daten im Rahmen eines Auftragsverarbeitungsvertrags (Art. 28 DSGVO) und ausschließlich zweckgebunden für die Einrichtung und den Betrieb Ihres OnLumis-Systems.",
  },
];

export default function HomePage() {
  return (
    <>
      <section className="relative overflow-hidden bg-primary text-white">
        <div
          className="pointer-events-none absolute inset-0 opacity-40"
          style={{
            background:
              "radial-gradient(60% 60% at 80% 10%, rgba(14,159,126,0.35) 0%, rgba(14,159,126,0) 70%)",
          }}
          aria-hidden="true"
        />
        <Container className="relative py-24 sm:py-32">
          <div className="max-w-3xl">
            <p className="inline-flex items-center rounded-full border border-white/20 bg-white/5 px-4 py-1.5 text-sm font-medium text-white/80">
              On-Premise-KI für den deutschen Mittelstand
            </p>
            <h1 className="mt-6 font-display text-4xl font-semibold leading-tight tracking-tight sm:text-5xl lg:text-6xl">
              Ihre Firma. <span className="text-accent">Ihre KI.</span>
            </h1>
            <p className="mt-4 text-xl font-medium text-white/85">
              Das Gehirn Ihres Unternehmens – lokal betrieben und nur mit Ihrem Wissen.
            </p>
            <p className="mt-6 max-w-2xl text-lg leading-relaxed text-white/75">
              OnLumis von JULITH GmbH verwandelt Ihr internes Unternehmenswissen in eine
              eigene, lokal gehostete KI – ohne dass Ihre Daten jemals in eine fremde Cloud
              wandern. Volle Kontrolle, volle DSGVO-Konformität, volle Wertschöpfung im eigenen
              Haus.
            </p>
            <div className="mt-10 flex flex-col gap-4 sm:flex-row">
              <CtaButton href="/kontakt">
                Kostenloses Erstgespräch vereinbaren <IconArrowRight />
              </CtaButton>
              <CtaButton href="/produkt" variant="ghost" className="border-white/25 text-white hover:border-accent hover:text-accent">
                So funktioniert OnLumis
              </CtaButton>
            </div>
            <ul className="mt-12 flex flex-wrap gap-x-8 gap-y-3 text-sm text-white/70">
              {trustBadges.map((badge) => (
                <li key={badge} className="flex items-center gap-2">
                  <IconCheckCircle className="h-4 w-4 text-accent" />
                  {badge}
                </li>
              ))}
            </ul>
          </div>
        </Container>
      </section>

      <section className="py-20 sm:py-28">
        <Container>
          <SectionHeading
            eyebrow="Die Ausgangslage"
            title="Cloud-KI bringt viele Unternehmen in ein Dilemma"
            description="Öffentliche KI-Dienste sind leistungsfähig – doch sensible Vertrags-, Kunden- und Prozessdaten in eine fremde Cloud zu geben, ist für viele Unternehmen in Deutschland kein gangbarer Weg."
          />
          <div className="mt-14 grid gap-6 lg:grid-cols-2">
            <div className="rounded-2xl border border-border bg-surface-alt p-8">
              <h3 className="font-display text-xl font-semibold text-ink dark:text-white">
                Das Problem mit klassischer Cloud-KI
              </h3>
              <ul className="mt-5 space-y-3 text-sm leading-relaxed text-muted">
                <li>– Unternehmensdaten verlassen Deutschland/die EU und liegen auf fremden Servern.</li>
                <li>– Unklare Verwendung von Eingaben zu Trainingszwecken durch den Anbieter.</li>
                <li>– Laufende, schwer planbare Kosten pro Nutzer oder Anfrage.</li>
                <li>– Abhängigkeit von der Verfügbarkeit und den Preismodellen einzelner Konzerne.</li>
                <li>– Datenschutzbeauftragte und Betriebsrat müssen aufwendig eingebunden werden.</li>
              </ul>
            </div>
            <div className="rounded-2xl border border-accent-strong/30 bg-surface p-8">
              <h3 className="font-display text-xl font-semibold text-ink dark:text-white">
                Die Antwort: OnLumis
              </h3>
              <ul className="mt-5 space-y-3 text-sm leading-relaxed text-muted">
                <li>– Betrieb vollständig On-Premise oder in einer deutschen/EU-Private-Cloud.</li>
                <li>– Ausschließlich Ihr eigenes, freigegebenes Unternehmenswissen als Grundlage.</li>
                <li>– Einmalige Investition statt unkalkulierbarer Cloud-Gebühren.</li>
                <li>– Unabhängig von externen KI-Anbietern und deren Änderungen an Preis oder Zugriff.</li>
                <li>– DSGVO-Konformität ist Teil der Architektur, nicht nachträglich aufgesetzt.</li>
              </ul>
            </div>
          </div>
        </Container>
      </section>

      <section className="bg-surface-alt py-20 sm:py-28">
        <Container>
          <SectionHeading
            eyebrow="So funktioniert es"
            title="In vier Schritten zur eigenen Unternehmens-KI"
            description="Von der ersten Analyse bis zum produktiven Betrieb begleitet Sie JULITH GmbH persönlich – als Partner, nicht als anonymer Software-Anbieter."
          />
          <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {process.map((item) => (
              <div key={item.step} className="rounded-2xl border border-border bg-surface p-6">
                <span className="font-display text-3xl font-semibold text-accent-strong/40">
                  {item.step}
                </span>
                <h3 className="mt-3 font-display text-lg font-semibold text-ink dark:text-white">
                  {item.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-muted">{item.description}</p>
              </div>
            ))}
          </div>
        </Container>
      </section>

      <section className="py-20 sm:py-28">
        <Container>
          <SectionHeading
            eyebrow="Ihre Vorteile"
            title="Was OnLumis für Ihr Unternehmen bedeutet"
            description="Datenschutz, Kontrolle und Wirtschaftlichkeit müssen sich nicht widersprechen."
          />
          <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {advantages.map((item) => (
              <FeatureCard key={item.title} icon={item.icon} title={item.title}>
                {item.text}
              </FeatureCard>
            ))}
          </div>
          <div className="mt-10 text-center">
            <Link
              href="/vorteile"
              className="inline-flex items-center gap-1.5 text-sm font-semibold text-accent-strong hover:underline"
            >
              Alle Vorteile im Detail ansehen <IconArrowRight />
            </Link>
          </div>
        </Container>
      </section>

      <section className="bg-surface-alt py-20 sm:py-28">
        <Container>
          <SectionHeading
            eyebrow="Anwendungsfälle"
            title="Wo OnLumis in Ihrem Unternehmen sofort wirkt"
          />
          <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {useCasePreview.map((item) => (
              <FeatureCard key={item.title} icon={item.icon} title={item.title}>
                {item.text}
              </FeatureCard>
            ))}
          </div>
          <div className="mt-10 text-center">
            <Link
              href="/anwendungsfaelle"
              className="inline-flex items-center gap-1.5 text-sm font-semibold text-accent-strong hover:underline"
            >
              Weitere Anwendungsfälle entdecken <IconArrowRight />
            </Link>
          </div>
        </Container>
      </section>

      <section className="py-20 sm:py-28">
        <Container>
          <div className="grid items-center gap-10 rounded-3xl border border-gold/30 bg-surface p-10 lg:grid-cols-3 lg:p-14">
            <div className="lg:col-span-2">
              <p className="text-sm font-semibold uppercase tracking-wide text-gold">
                Förderung nutzen
              </p>
              <h2 className="mt-3 font-display text-2xl font-semibold text-ink sm:text-3xl dark:text-white">
                Investieren Sie mit Unterstützung, z. B. über den Digitalbonus Hessen
              </h2>
              <p className="mt-4 max-w-2xl text-muted">
                Viele Bundesländer fördern die digitale Transformation von KMU – darunter der
                Digitalbonus Hessen. OnLumis kann als förderfähiges Digitalisierungsprojekt
                eingebracht werden. Wir unterstützen Sie bei der Einschätzung und Antragstellung.
              </p>
            </div>
            <div className="flex lg:justify-end">
              <CtaButton href="/foerderung" variant="secondary">
                Förderung prüfen <IconArrowRight />
              </CtaButton>
            </div>
          </div>
        </Container>
      </section>

      <FaqSection items={faqItems} />

      <section className="bg-primary py-20 text-white sm:py-24">
        <Container className="flex flex-col items-center gap-6 text-center">
          <h2 className="font-display text-3xl font-semibold sm:text-4xl">
            Lernen Sie OnLumis in einem unverbindlichen Gespräch kennen
          </h2>
          <p className="max-w-xl text-white/75">
            Wir zeigen Ihnen, wie eine lokale KI auf Basis Ihres eigenen Wissens konkret für Ihr
            Unternehmen aussehen kann – inklusive Einschätzung zu Aufwand, Hardware und
            Fördermöglichkeiten.
          </p>
          <CtaButton href="/kontakt">
            Jetzt Kontakt aufnehmen <IconArrowRight />
          </CtaButton>
        </Container>
      </section>
    </>
  );
}
