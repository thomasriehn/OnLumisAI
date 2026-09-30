import type { Metadata } from "next";
import { PageHero } from "@/components/PageHero";
import { UseCases } from "@/components/UseCases";
import Link from "next/link";
import { Arrow } from "@/components/BrandIcons";
export const metadata: Metadata = {
  title: "Anwendungsfälle",
  description:
    "OnLumisAI im Service, Vertrieb, Support und Onboarding: konkrete Fragen an das Wissen Ihres Unternehmens.",
  alternates: { canonical: "/anwendungsfaelle" },
};
export default function Cases() {
  return (
    <>
      <PageHero
        eyebrow="Anwendungsfälle"
        title="Die richtige Frage verändert, wie Ihr Team arbeitet."
        description="Beginnen Sie dort, wo Wissen täglich gebraucht wird. Die folgenden Beispiele zeigen, wie sich Dokumente, Erfahrung und konkrete Aufgaben verbinden lassen."
      />
      <section className="section shell">
        <UseCases />
      </section>
      <section className="shell editorial-page">
        <div className="question-grid">
          {[
            [
              "Onboarding",
              "Wie beantrage ich Urlaub – und wer muss zustimmen?",
              "Interne Richtlinien, Prozesse und Ansprechpartner leichter kennenlernen.",
            ],
            [
              "Qualitätsmanagement",
              "Welche Schritte sieht unsere Reklamationsbearbeitung vor?",
              "Arbeitsanweisungen, Formulare und Zuständigkeiten gemeinsam erschließen.",
            ],
            [
              "Projektarbeit",
              "Welche Informationen liegen zu diesem Kunden vor?",
              "Projektberichte, Protokolle und Vereinbarungen gezielt durchsuchen.",
            ],
            [
              "Wissensmanagement",
              "Wo haben wir dieses Problem schon einmal gelöst?",
              "Erfahrungen aus dokumentierten Fällen für neue Aufgaben verfügbar machen.",
            ],
          ].map(([t, q, p]) => (
            <div key={t}>
              <p className="eyebrow">{t}</p>
              <h2>„{q}“</h2>
              <p>{p}</p>
            </div>
          ))}
        </div>
        <div className="editorial-cta">
          <div>
            <p className="eyebrow">ECHTE FRAGEN. VOLLSTÄNDIGE DURCHLÄUFE.</p>
            <h2>Entdecken Sie die Playbooks.</h2>
          </div>
          <Link href="/demo" className="btn btn-dark">
            Ins Demo-Studio <Arrow />
          </Link>
        </div>
      </section>
    </>
  );
}
