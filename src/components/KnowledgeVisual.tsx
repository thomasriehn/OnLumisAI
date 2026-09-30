"use client";
import { useState } from "react";
import { Check, Lock } from "./BrandIcons";
const examples = [
  {
    label: "Service",
    question: "Was sollte ich bei Fehler E37 zuerst prüfen?",
    answer:
      "Die aktuelle Prüfanweisung und passende Servicefälle gemeinsam betrachten.",
    sources: ["Prüfanweisung · Revision 3", "Servicebericht · MX-400"],
  },
  {
    label: "Vertrieb",
    question: "Welche Konditionen gelten für dieses Projekt?",
    answer:
      "Leistungsbeschreibung und projektspezifische Nachträge zusammenführen.",
    sources: ["Leistungsbeschreibung", "Vertragsnachtrag"],
  },
  {
    label: "Wissen",
    question: "Wie läuft die Reklamationsbearbeitung ab?",
    answer:
      "Den dokumentierten Ablauf mit den zuständigen Ansprechpartnern finden.",
    sources: ["Arbeitsanweisung", "Organigramm"],
  },
];
export function KnowledgeVisual() {
  const [active, setActive] = useState(0);
  const ex = examples[active];
  return (
    <div className="knowledge-visual">
      <div className="visual-grid" aria-hidden="true" />
      <div className="visual-topline">
        <span className="live-dot" /> IHR WISSEN, VERBUNDEN <Lock />
      </div>
      <div className="source-stack" aria-hidden="true">
        <div>
          <span>PDF</span>
          <b>Handbücher</b>
          <i>Technik & Service</i>
        </div>
        <div>
          <span>DOC</span>
          <b>Verträge</b>
          <i>Projekte & Zusagen</i>
        </div>
        <div>
          <span>DATA</span>
          <b>Erfahrungswissen</b>
          <i>Berichte & Prozesse</i>
        </div>
      </div>
      <svg
        className="connection-lines"
        viewBox="0 0 560 180"
        fill="none"
        aria-hidden="true"
      >
        <path
          d="M105 8v38q0 16 18 16h130q27 0 27 26v82M280 8v162M455 8v38q0 16-18 16H307q-27 0-27 26"
          stroke="currentColor"
        />
        <path
          className="flow-pulse"
          d="M105 8v38q0 16 18 16h130q27 0 27 26v82M280 8v162M455 8v38q0 16-18 16H307q-27 0-27 26"
          stroke="currentColor"
          strokeWidth="2"
        />
      </svg>
      <div className="knowledge-core">
        <span className="core-mark" aria-hidden="true">
          ◉
        </span>
        <div>
          <b>
            OnLumis<span>AI</span>
          </b>
          <small>Finden. Verbinden. Verstehen.</small>
        </div>
        <span className="core-status">
          <Check />
        </span>
      </div>
      <div className="visual-answer" key={active}>
        <div className="visual-question">{ex.question}</div>
        <div className="visual-response">
          <span className="response-star">✳</span>
          <p>{ex.answer}</p>
        </div>
        <div className="visual-sources">
          {ex.sources.map((s, i) => (
            <span key={s}>
              <b>{i + 1}</b>
              {s}
            </span>
          ))}
        </div>
      </div>
      <div
        className="visual-tabs"
        role="group"
        aria-label="Anwendungsbeispiel wählen"
      >
        {examples.map((e, i) => (
          <button
            key={e.label}
            onClick={() => setActive(i)}
            aria-pressed={active === i}
          >
            {e.label}
          </button>
        ))}
        <span>Illustratives Beispiel</span>
      </div>
    </div>
  );
}
