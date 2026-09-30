"use client";
import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { Arrow } from "./BrandIcons";
const cases = [
  {
    title: "Service & Technik",
    tag: "VOM FEHLERBILD ZUM NÄCHSTEN SCHRITT",
    heading: "Erfahrung abrufen. Auch wenn der Kollege unterwegs ist.",
    copy: "Prüfanweisungen, frühere Einsätze und Produktdokumentation zusammen betrachten. Folgefragen bleiben im Gespräch – und Quellen sind direkt erreichbar.",
    image: "/media/service-screen.png",
    alt: "Originalaufnahme: OnLumis beantwortet eine Frage zum Fehlercode E37 mit Prüfschritten und Quellen.",
    question: "„MX-400 zeigt E37. Was soll ich zuerst prüfen?“",
  },
  {
    title: "Vertrieb & Projekte",
    tag: "VORBEREITET INS NÄCHSTE GESPRÄCH",
    heading: "Was wurde vereinbart? Die Fundstelle ist entscheidend.",
    copy: "Kundenanfragen, Vertragsunterlagen und Projektberichte gezielt erschließen. Die Quellen helfen, allgemeine Regeln von projektspezifischen Vereinbarungen zu unterscheiden.",
    image: "/media/vertrieb-screen.png",
    alt: "Originalaufnahme eines OnLumis-Walkthroughs zur Angebotsvorbereitung.",
    question: "„Welche Sonderkonditionen gelten für das Projekt?“",
  },
  {
    title: "Support & Wissen",
    tag: "WISSEN IM ALLTAG NUTZBAR MACHEN",
    heading: "Weniger Weiterleiten. Mehr selbst herausfinden.",
    copy: "Mitarbeitende finden Produktwissen, interne Abläufe und relevante Ansprechpartner. Das entlastet erfahrene Kollegen und erleichtert den Einstieg in neue Aufgaben.",
    image: "/media/support-screen.png",
    alt: "Originalaufnahme: eine Supportfrage in OnLumis mit Quellenbelegen.",
    question: "„Welche Schritte empfiehlt unsere Dokumentation?“",
  },
];
export function UseCases() {
  const [active, setActive] = useState(0);
  const c = cases[active];
  return (
    <div className="use-cases">
      <div className="case-tabs" role="tablist" aria-label="Einsatzbereiche">
        {cases.map((c, i) => (
          <button
            key={c.title}
            role="tab"
            id={`case-tab-${i}`}
            aria-controls={`case-panel-${i}`}
            aria-selected={active === i}
            tabIndex={active === i ? 0 : -1}
            onKeyDown={(e) => {
              if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
                e.preventDefault();
                const next =
                  (active + (e.key === "ArrowRight" ? 1 : cases.length - 1)) %
                  cases.length;
                setActive(next);
                document.getElementById(`case-tab-${next}`)?.focus();
              }
            }}
            onClick={() => setActive(i)}
          >
            <span>0{i + 1}</span>
            {c.title}
            <Arrow />
          </button>
        ))}
      </div>
      <div
        className="case-panel"
        role="tabpanel"
        id={`case-panel-${active}`}
        aria-labelledby={`case-tab-${active}`}
      >
        <div className="case-copy">
          <p className="eyebrow">{c.tag}</p>
          <h3>{c.heading}</h3>
          <p>{c.copy}</p>
          <blockquote>{c.question}</blockquote>
          <Link href="/anwendungsfaelle" className="text-link">
            Einsatzmöglichkeiten entdecken <Arrow />
          </Link>
        </div>
        <div className="case-image">
          <div className="window-bar">
            <i />
            <i />
            <i />
            <span>OnLumisAI · Originalaufnahme</span>
          </div>
          <Image
            src={c.image}
            alt={c.alt}
            width={1600}
            height={900}
            sizes="(max-width: 800px) 100vw, 55vw"
          />
          <p>Fiktive Demodaten · Aufnahme vom September 2026</p>
        </div>
      </div>
    </div>
  );
}
