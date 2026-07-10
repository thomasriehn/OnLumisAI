"use client";

import { useState } from "react";
import { TopBar } from "@/components/TopBar";

type Result = {
  title: string | null;
  uri: string;
  page: number | null;
  heading_path: string | null;
  snippet: string;
  score: number;
};

export function SearchView() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Result[] | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function search(event: React.FormEvent) {
    event.preventDefault();
    if (!query.trim() || busy) return;
    setBusy(true);
    setError(null);
    try {
      const response = await fetch("/api/search", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ query: query.trim(), top_k: 10 }),
      });
      if (!response.ok) throw new Error(`Fehler ${response.status}`);
      setResults((await response.json()).results);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unbekannter Fehler");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="shell">
      <TopBar active="suche" />
      <div className="messages">
        <form className="composer" onSubmit={search} style={{ borderTop: "none" }}>
          <textarea
            rows={1}
            value={query}
            placeholder="Dokumente durchsuchen …"
            onChange={(event) => setQuery(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                search(event);
              }
            }}
          />
          <button type="submit" disabled={busy || !query.trim()}>
            Suchen
          </button>
        </form>
        {error && <div className="error">⚠ {error}</div>}
        {results !== null && results.length === 0 && (
          <div className="empty">
            <p>Keine Treffer in den für Sie freigegebenen Dokumenten.</p>
          </div>
        )}
        {results?.map((result, index) => (
          <div className="citation" key={index} style={{ maxWidth: "100%" }}>
            <span className="n">{index + 1}.</span>
            <strong>{result.title ?? result.uri}</strong>
            {result.page != null && ` · Seite ${result.page}`}
            {result.heading_path && ` · ${result.heading_path}`}
            <p style={{ margin: "6px 0" }}>{result.snippet}…</p>
            <span className="path">{result.uri}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
