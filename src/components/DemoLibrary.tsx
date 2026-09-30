/* eslint-disable @next/next/no-location-assign-relative-destination -- Full navigation clears authenticated router state after login/logout. */
"use client";
import { useState } from "react";
import { Arrow, Lock } from "./BrandIcons";
export type DemoItem = {
  id: string;
  version: string;
  title: string;
  file: string;
  poster: string;
  duration: string;
  questions: string[];
  closing: string;
  note: string;
  retake: boolean;
  pdf: string;
};
const fileUrl = (name: string) =>
  "/demo/dateien/" + name.split("/").map(encodeURIComponent).join("/");
export function DemoLibrary({ items }: { items: DemoItem[] }) {
  const [version, setVersion] = useState("Alle");
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");
  const visible = items.filter(
    (i) =>
      (version === "Alle" || i.version === version) &&
      `${i.title} ${i.id} ${i.questions.join(" ")}`
        .toLocaleLowerCase("de")
        .includes(search.toLocaleLowerCase("de")),
  );
  async function logout() {
    try {
      const r = await fetch("/api/demo/logout", { method: "POST" });
      if (!r.ok) throw Error();
      window.location.assign("/demo");
    } catch {
      setError("Abmelden fehlgeschlagen. Bitte versuchen Sie es erneut.");
    }
  }
  return (
    <section className="shell library-page">
      <div className="library-heading">
        <div>
          <p className="eyebrow">
            <Lock /> IHR GESCHÜTZTER DEMO-BEREICH
          </p>
          <h1>Wissen in Aktion.</h1>
          <p>
            27 Walkthroughs. Drei Playbooks. Nehmen Sie sich die Zeit für einen
            genaueren Blick.
          </p>
        </div>
        <button className="text-link" onClick={logout}>
          Abmelden ↗
        </button>
      </div>
      {error && (
        <p role="alert" className="form-error">
          {error}
        </p>
      )}
      <div className="playbook-downloads">
        {[
          ["V1", "Grundlagen", "Sieben typische Aufgaben"],
          ["V2", "Advanced", "Vertiefung und Folgefragen"],
          ["V3", "Enterprise", "Elf anspruchsvolle Szenarien"],
        ].map(([v, t, d]) => (
          <a
            key={v}
            href={fileUrl(
              "playbooks/" + items.find((i) => i.version === v)!.pdf,
            )}
            target="_blank"
            rel="noopener"
          >
            <span>{v} / PDF</span>
            <h2>{t}</h2>
            <p>{d}</p>
            <b>
              Playbook öffnen <Arrow />
            </b>
          </a>
        ))}
      </div>
      <div className="library-toolbar">
        <div role="group" aria-label="Playbook-Version filtern">
          {["Alle", "V1", "V2", "V3"].map((v) => (
            <button
              key={v}
              onClick={() => setVersion(v)}
              aria-pressed={v === version}
            >
              {v}
            </button>
          ))}
        </div>
        <label>
          <span className="sr-only">Videos und Fragen durchsuchen</span>
          <input
            type="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Video, Thema oder Frage suchen …"
          />
        </label>
        <span aria-live="polite">{visible.length} Videos</span>
      </div>
      <div className="library-grid">
        {visible.map((i) => (
          <article key={i.id}>
            <video
              controls
              preload="none"
              playsInline
              poster={fileUrl(i.poster)}
              aria-label={i.title}
            >
              <source src={fileUrl(i.file)} type="video/mp4" />
            </video>
            <div className="library-card-body">
              <div className="library-meta">
                <span>{i.id}</span>
                <span>{i.duration} · Reasoning aus</span>
              </div>
              <h2>{i.title}</h2>
              {i.retake && (
                <p className="retake-tag">Neu aufgenommen · 30.09.2026</p>
              )}
              {i.note && <p className="library-note">{i.note}</p>}
              <details>
                <summary>Fragen & Abschluss</summary>
                <ol>
                  {i.questions.map((q) => (
                    <li key={q}>{q}</li>
                  ))}
                </ol>
                <p>
                  <strong>Zum Gesprächsabschluss:</strong> {i.closing}
                </p>
              </details>
              <a className="text-link" href={fileUrl(i.file)} download>
                MP4 herunterladen <Arrow />
              </a>
            </div>
          </article>
        ))}
      </div>
      {visible.length === 0 && (
        <div className="empty-state">
          <h2>Kein passendes Video gefunden.</h2>
          <p>
            Probieren Sie einen anderen Suchbegriff oder wählen Sie alle
            Versionen.
          </p>
          <button
            onClick={() => {
              setVersion("Alle");
              setSearch("");
            }}
            className="btn btn-dark"
          >
            Alle Videos anzeigen
          </button>
        </div>
      )}
      <aside className="library-footer">
        <p>
          Originalaufnahmen mit fiktiven Unternehmensdaten. Die Hinweise an den
          Videos dokumentieren bekannte Einschränkungen. Die Aufnahmen zur
          Zugriffssteuerung wurden mit dem vorhandenen Benutzer „mueller“
          erstellt.
        </p>
        <div>
          <a href="/demo/video.html" target="_blank" rel="noopener">
            Klassische video.html ↗
          </a>
          <a href={fileUrl("BEOBACHTUNGEN.md")}>Beobachtungen & Grenzen ↗</a>
          <a href={fileUrl("PRUEFPROTOKOLL.md")}>Technische Prüfung ↗</a>
        </div>
      </aside>
    </section>
  );
}
