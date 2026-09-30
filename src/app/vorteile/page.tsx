import type { Metadata } from "next";
import { EditorialPage } from "@/components/EditorialPage";
export const metadata: Metadata = {
  title: "Ihre Vorteile",
  description:
    "Unternehmenswissen nutzbar machen, Quellen nachvollziehen und den Betrieb selbst bestimmen. Die Vorteile von OnLumisAI.",
  alternates: { canonical: "/vorteile" },
};
export default function Benefits() {
  return (
    <EditorialPage
      eyebrow="Ihre Vorteile"
      title="Wissen wird wertvoll, wenn Menschen damit arbeiten können."
      intro="OnLumisAI schafft einen gemeinsamen Zugang zu verteilten Informationen. Der Nutzen zeigt sich an den Aufgaben Ihres Teams – und wird im Pilot konkret überprüft."
      sections={[
        {
          title: "Informationen schneller erschließen",
          text: "Eine Frage kann mehrere Dokumente zusammenbringen. Ihr Team erhält einen Einstieg in komplexe Unterlagen und kann relevante Quellen unmittelbar weiterverfolgen.",
          detail:
            "Mögliche Einsatzfelder sind wiederkehrende Servicefragen, Vertragsrecherche, Prozesswissen und die Vorbereitung von Kundengesprächen.",
        },
        {
          title: "Erfahrung zugänglich halten",
          text: "Dokumentierte Servicefälle, Übergaben und Projektberichte bleiben auch dann nutzbar, wenn die erfahrene Kollegin gerade nicht erreichbar ist.",
          detail:
            "Der Wert entsteht aus Ihrer Dokumentation. Implizites Wissen wird durch die Einführung nicht automatisch erfasst; wir identifizieren gemeinsam die nötigen Inhalte.",
        },
        {
          title: "Kontrolle behalten",
          text: "Sie entscheiden, welche Inhalte aufgenommen werden, wer sie nutzen darf und in welcher Infrastruktur sie verarbeitet werden.",
          detail:
            "Der lokale Betrieb unterstützt Ihr Datenschutzkonzept. Organisatorische Maßnahmen, Berechtigungen und vereinbarte Betriebsprozesse gehören ebenfalls dazu.",
        },
        {
          title: "Ergebnisse nachvollziehen",
          text: "Quellenbelege machen die Herkunft von Aussagen sichtbar. Teams können prüfen, vertiefen und erkennen, wo Rückfragen nötig sind.",
          detail:
            "Die geschützte Demo-Bibliothek zeigt echte Durchläufe mit fiktiven Daten – einschließlich der Grenzen, die bei anspruchsvollen Fragen auftreten.",
        },
        {
          title: "Mit einem klaren Pilot starten",
          text: "Statt sofort das gesamte Unternehmen einzubeziehen, wählen wir einen abgegrenzten Anwendungsfall. Sie bewerten Qualität und Nutzen gemeinsam mit den späteren Anwendern.",
          detail:
            "Infrastruktur, Einrichtung, Integrationen und laufender Betrieb werden im Angebot getrennt beschrieben. So entsteht eine nachvollziehbare Entscheidungsgrundlage.",
        },
      ]}
    />
  );
}
