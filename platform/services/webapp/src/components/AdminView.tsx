"use client";

import { useCallback, useEffect, useState } from "react";
import { TopBar } from "@/components/TopBar";

type Stats = { documents: number; chunks: number; conversations: number; feedback_open: number };
type Source = {
  id: string; name: string; kind: string; enabled: boolean;
  document_count: number; last_sync_at: string | null; last_sync_status: string | null;
};
type FeedbackEntry = {
  id: string; rating: string; comment: string | null; username: string;
  question: string | null; answer: string;
};
type EvalRun = {
  id: string; started_at: string; finished_at: string | null; model: string;
  stats: { total: number; retrieval_rate: number | null; keyword_rate: number | null } | null;
};
type GapReport = {
  total: number;
  gaps: { question: string; occurrences: number; distinct_users: number; last_seen: string }[];
};

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/bff/admin/${path}`, {
    headers: { "content-type": "application/json" },
    ...init,
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => null);
    throw new Error(detail?.detail ?? `Fehler ${response.status}`);
  }
  return response.status === 204 ? (undefined as T) : response.json();
}

export function AdminView() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [sources, setSources] = useState<Source[]>([]);
  const [feedback, setFeedback] = useState<FeedbackEntry[]>([]);
  const [runs, setRuns] = useState<EvalRun[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [uploadInfo, setUploadInfo] = useState<string | null>(null);
  const [gaps, setGaps] = useState<GapReport | null>(null);

  const reload = useCallback(async () => {
    try {
      setError(null);
      const [s, src, fb, ev, gapsReport] = await Promise.all([
        api<Stats>("stats"),
        api<Source[]>("sources"),
        api<FeedbackEntry[]>("feedback?reviewed=false"),
        api<EvalRun[]>("evals/runs"),
        api<GapReport>("reports/knowledge-gaps?days=30"),
      ]);
      setStats(s);
      setSources(src);
      setFeedback(fb);
      setRuns(ev);
      setGaps(gapsReport);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unbekannter Fehler");
    }
  }, []);

  useEffect(() => {
    void reload();
  }, [reload]);

  async function addSource(formData: FormData) {
    setBusy(true);
    try {
      const kind = String(formData.get("kind"));
      const config =
        kind === "filesystem"
          ? { root_path: String(formData.get("root_path")) }
          : JSON.parse(String(formData.get("config") || "{}"));
      await api("sources", {
        method: "POST",
        body: JSON.stringify({
          name: String(formData.get("name")),
          kind,
          config,
          default_acl: String(formData.get("acl") || "all-users")
            .split(",")
            .map((g) => g.trim())
            .filter(Boolean),
        }),
      });
      await reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Quelle konnte nicht angelegt werden");
    } finally {
      setBusy(false);
    }
  }

  async function reviewFeedback(id: string) {
    await api(`feedback/${id}`, { method: "PATCH" });
    setFeedback((prev) => prev.filter((f) => f.id !== id));
  }

  async function runEval() {
    setBusy(true);
    try {
      await api("evals/run?wait=true", { method: "POST" });
      await reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Eval fehlgeschlagen");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="shell">
      <TopBar active="admin" />
      <div className="messages admin">
        {error && <div className="error">⚠ {error}</div>}

        {stats && (
          <section className="stat-row">
            <Stat label="Dokumente" value={stats.documents} />
            <Stat label="Chunks" value={stats.chunks} />
            <Stat label="Konversationen" value={stats.conversations} />
            <Stat label="Offenes Feedback" value={stats.feedback_open} />
          </section>
        )}

        <section className="card">
          <h2>Wissensquellen</h2>
          <table>
            <thead>
              <tr><th>Name</th><th>Typ</th><th>Dokumente</th><th>Letzter Sync</th></tr>
            </thead>
            <tbody>
              {sources.map((source) => (
                <tr key={source.id}>
                  <td>{source.name}</td>
                  <td>{source.kind}</td>
                  <td>{source.document_count}</td>
                  <td title={source.last_sync_status ?? ""}>
                    {source.last_sync_at
                      ? `${new Date(source.last_sync_at).toLocaleString("de-DE")} · ${
                          source.last_sync_status?.split(" ")[0] ?? ""
                        }`
                      : "ausstehend"}
                  </td>
                </tr>
              ))}
              {sources.length === 0 && (
                <tr><td colSpan={4}>Noch keine Quelle angebunden.</td></tr>
              )}
            </tbody>
          </table>

          <form
            className="source-form"
            onSubmit={(event) => {
              event.preventDefault();
              void addSource(new FormData(event.currentTarget));
              event.currentTarget.reset();
            }}
          >
            <input name="name" placeholder="Name" required />
            <select name="kind" defaultValue="filesystem">
              <option value="filesystem">Dateisystem</option>
              <option value="confluence">Confluence</option>
              <option value="sharepoint">SharePoint</option>
              <option value="imap">IMAP-Postfach</option>
            </select>
            <input name="root_path" placeholder="Pfad (Dateisystem), z. B. /data/sources/hr" />
            <input name="config" placeholder='Config-JSON (andere Typen)' />
            <input name="acl" placeholder="Gruppen (Komma), z. B. hr,all-users" />
            <button type="submit" disabled={busy}>Quelle anlegen</button>
          </form>
          <p className="muted">
            Der nächste Sync-Lauf indexiert die Quelle automatisch (Intervall
            siehe SYNC_INTERVAL_SECONDS); Berechtigungen wirken ab dem ersten Sync.
          </p>
        </section>

        <section className="card">
          <h2>Dokumente hochladen</h2>
          <p className="muted">
            Für Dokumente ohne Quellsystem – sie landen in der Quelle
            „uploads" (Sichtbarkeit gemäß deren ACL) und werden beim nächsten
            Sync indexiert.
          </p>
          <form
            className="source-form"
            onSubmit={async (event) => {
              event.preventDefault();
              const form = event.currentTarget;
              const input = form.querySelector<HTMLInputElement>("input[type=file]");
              if (!input?.files?.length) return;
              const data = new FormData();
              for (const file of input.files) data.append("files", file);
              setBusy(true);
              try {
                const response = await fetch("/bff/admin/uploads", {
                  method: "POST",
                  body: data,
                });
                if (!response.ok) throw new Error(`Fehler ${response.status}`);
                setUploadInfo((await response.json()).saved.join(", "));
                form.reset();
                await reload();
              } catch (err) {
                setError(err instanceof Error ? err.message : "Upload fehlgeschlagen");
              } finally {
                setBusy(false);
              }
            }}
          >
            <input type="file" multiple accept=".pdf,.docx,.md,.txt,.html" />
            <button type="submit" disabled={busy}>Hochladen</button>
          </form>
          {uploadInfo && <p className="muted">Gespeichert: {uploadInfo}</p>}
        </section>

        <section className="card">
          <h2>Feedback-Kuratierung ({feedback.length} offen)</h2>
          {feedback.map((entry) => (
            <div className="citation" key={entry.id} style={{ maxWidth: "100%" }}>
              <span className="n">{entry.rating === "up" ? "👍" : "👎"}</span>
              <strong>{entry.question ?? "(ohne Frage)"}</strong>
              <p style={{ margin: "6px 0" }}>{entry.answer.slice(0, 300)}</p>
              {entry.comment && <p className="muted">Kommentar: {entry.comment}</p>}
              <button className="small" onClick={() => void reviewFeedback(entry.id)}>
                Geprüft & freigeben
              </button>
            </div>
          ))}
          {feedback.length === 0 && <p className="muted">Keine offenen Einträge.</p>}
        </section>

        <section className="card">
          <h2>
            Wissenslücken – gefragte, aber unbeantwortete Themen
            {gaps ? ` (${gaps.total} in 30 Tagen)` : ""}
          </h2>
          <p className="muted">
            Fragen ohne belastbare Quelle (Nutzer pseudonymisiert). Diese Themen
            lohnt es zu dokumentieren oder als Quelle anzubinden.
          </p>
          <table>
            <thead>
              <tr><th>Frage</th><th>Häufigkeit</th><th>Nutzer</th><th>Zuletzt</th></tr>
            </thead>
            <tbody>
              {gaps?.gaps.map((gap) => (
                <tr key={gap.question}>
                  <td>{gap.question}</td>
                  <td>{gap.occurrences}</td>
                  <td>{gap.distinct_users}</td>
                  <td>{new Date(gap.last_seen).toLocaleDateString("de-DE")}</td>
                </tr>
              ))}
              {(!gaps || gaps.gaps.length === 0) && (
                <tr><td colSpan={4}>Keine offenen Wissenslücken – gut dokumentiert.</td></tr>
              )}
            </tbody>
          </table>
        </section>

        <section className="card">
          <h2>Qualität (goldene Fragen)</h2>
          <button className="small" onClick={() => void runEval()} disabled={busy}>
            {busy ? "läuft …" : "Eval-Lauf starten"}
          </button>
          <table>
            <thead>
              <tr><th>Start</th><th>Modell</th><th>Fragen</th><th>Retrieval</th><th>Keywords</th></tr>
            </thead>
            <tbody>
              {runs.map((run) => (
                <tr key={run.id}>
                  <td>{new Date(run.started_at).toLocaleString("de-DE")}</td>
                  <td>{run.model}</td>
                  <td>{run.stats?.total ?? "–"}</td>
                  <td>{formatRate(run.stats?.retrieval_rate)}</td>
                  <td>{formatRate(run.stats?.keyword_rate)}</td>
                </tr>
              ))}
              {runs.length === 0 && <tr><td colSpan={5}>Noch kein Lauf.</td></tr>}
            </tbody>
          </table>
        </section>
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="stat">
      <span className="stat-value">{value.toLocaleString("de-DE")}</span>
      <span className="stat-label">{label}</span>
    </div>
  );
}

function formatRate(rate: number | null | undefined) {
  return rate == null ? "–" : `${Math.round(rate * 100)} %`;
}
