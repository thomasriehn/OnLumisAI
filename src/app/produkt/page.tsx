import type { Metadata } from "next";
import { EditorialPage } from "@/components/EditorialPage";
export const metadata: Metadata = {
  title: "Produkt & Architektur",
  description:
    "Wie OnLumisAI aus Dokumenten nutzbares Unternehmenswissen macht: Aufbereitung, Suche, KI-Antworten, Quellen und Zugriffsrechte.",
  alternates: { canonical: "/produkt" },
};
export default function Product() {
  return (
    <EditorialPage
      eyebrow="Produkt & Architektur"
      title="Ihre Dokumente. Ein Gespräch. Ein neuer Zugang zu Wissen."
      intro="OnLumisAI verbindet eine durchsuchbare Wissensbasis mit einem Sprachmodell. Das System läuft in Ihrer gewählten Umgebung und macht freigegebene Informationen im Dialog zugänglich."
      sections={[
        {
          title: "Wissen anbinden",
          text: "Dateisysteme, SharePoint und strukturierte Exporte bilden den Ausgangspunkt. Dokumente werden eingelesen, aufbereitet und in Textabschnitte zerlegt.",
          detail:
            "Welche Quellsysteme direkt angebunden werden und wo ein Export sinnvoll ist, klären wir anhand Ihrer bestehenden IT. Die Datenqualität und Lesbarkeit der Dokumente werden im Pilot geprüft.",
        },
        {
          title: "Gezielt wiederfinden",
          text: "Die Suche berücksichtigt Begriffe und inhaltliche Ähnlichkeit. Relevante Treffer werden ausgewählt und nachsortiert, bevor sie als Kontext für die Antwort dienen.",
          detail:
            "Bei Folgefragen kann der Gesprächskontext in die Suche einfließen. So lässt sich ein Thema Schritt für Schritt vertiefen.",
        },
        {
          title: "Mit Belegen antworten",
          text: "Das Sprachmodell formuliert aus den ausgewählten Fundstellen eine Antwort. Die Quellen bleiben erreichbar, damit Ihr Team Aussagen am Ursprungsdokument prüfen kann.",
          detail:
            "Fehlende, widersprüchliche oder veraltete Inhalte können die Antwortqualität begrenzen. Deshalb gehören fachliche Prüfung und repräsentative Testfragen zur Einführung.",
        },
        {
          title: "Zugriff steuern",
          text: "Quellen und Dokumente werden Nutzergruppen zugeordnet. Die Recherche erfolgt innerhalb der für den jeweiligen Benutzer zugänglichen Wissensbasis.",
          detail:
            "Identitätsverwaltung, Rechteübernahme und Ihr Datenschutzkonzept werden gemeinsam eingerichtet und mit konkreten Benutzerrollen getestet.",
        },
        {
          title: "Passend betreiben",
          text: "Das Modell kann auf Ihrer Infrastruktur oder in einer vereinbarten Private Cloud laufen. Datenmenge, gleichzeitige Nutzer und gewünschte Antwortzeiten bestimmen die Auslegung.",
          detail:
            "Updates, Backup, Monitoring und Verantwortlichkeiten werden Teil des Betriebskonzepts. Verbindungen zu externen Diensten werden bewusst konfiguriert.",
        },
      ]}
    />
  );
}
