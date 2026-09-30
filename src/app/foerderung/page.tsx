import type { Metadata } from "next";
import { EditorialPage } from "@/components/EditorialPage";
export const metadata: Metadata = {
  title: "Projektplanung & Förderung",
  description:
    "Ein OnLumisAI-Pilot mit klarem Ziel, transparentem Aufwand und einer projektspezifischen Prüfung möglicher Förderangebote.",
  alternates: { canonical: "/foerderung" },
};
export default function Funding() {
  return (
    <EditorialPage
      eyebrow="Projektplanung & Förderung"
      title="Ein guter Start braucht einen klaren Plan."
      intro="Wir grenzen Ihr Vorhaben gemeinsam ein: vom ersten Anwendungsfall über die Datenbasis bis zum Betrieb. Mögliche Förderangebote prüfen wir passend zu Ihrem Standort und Projekt."
      sections={[
        {
          title: "Den Nutzen konkret machen",
          text: "Welche Fragen kosten Ihr Team heute Zeit? Welche Unterlagen werden gebraucht? Aus diesen Antworten entsteht ein überschaubarer Pilot mit nachvollziehbaren Erfolgskriterien.",
        },
        {
          title: "Den Aufwand sichtbar machen",
          text: "Wir betrachten Datenaufbereitung, vorhandene Hardware, Integrationen, Berechtigungen und den späteren Betrieb. Das Angebot beschreibt die vorgesehenen Leistungen und ihre Voraussetzungen.",
        },
        {
          title: "Fördermöglichkeiten prüfen",
          text: "Ob eine Förderung infrage kommt, hängt unter anderem von Standort, Unternehmensgröße, Projektinhalt und den aktuell geltenden Programmbedingungen ab. Eine pauschale Förderzusage lässt sich daraus nicht ableiten.",
          detail:
            "Programmverfügbarkeit und Förderfähigkeit müssen vor einer Entscheidung mit der zuständigen Förderstelle geklärt werden. Eine erste Übersicht bietet die Förderdatenbank des Bundes.",
        },
        {
          title: "Geordnet umsetzen",
          text: "Zeitplan, Verantwortlichkeiten und Testfälle werden vor dem Start vereinbart. Nach der Pilotbewertung entscheiden Sie über den weiteren Ausbau.",
        },
      ]}
    >
      <p className="official-link">
        <a
          href="https://www.foerderdatenbank.de/"
          target="_blank"
          rel="noopener noreferrer"
        >
          Zur offiziellen Förderdatenbank des Bundes ↗
        </a>
      </p>
    </EditorialPage>
  );
}
