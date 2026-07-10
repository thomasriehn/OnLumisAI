"use client";

import { useEffect, useRef, useState } from "react";

type Citation = {
  n: number;
  title: string | null;
  uri: string;
  page: number | null;
  heading_path: string | null;
  snippet: string;
  used: boolean;
};

type Message = {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  messageId?: string;
  feedback?: "up" | "down";
  pending?: boolean;
};

const EXAMPLES = [
  "Wie viele Urlaubstage habe ich pro Jahr?",
  "Was tun, wenn die Presse P-300 keinen Druck aufbaut?",
  "Wie beantrage ich Sonderurlaub für einen Umzug?",
];

/** Parst den SSE-Stream des Orchestrators (OpenAI-Chunks + onlumis.citations). */
async function readStream(
  response: Response,
  onDelta: (text: string) => void,
  onFinal: (data: { citations?: Citation[]; conversation_id?: string; message_id?: string }) => void,
) {
  const reader = response.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split("\n\n");
    buffer = events.pop() ?? "";
    for (const event of events) {
      for (const line of event.split("\n")) {
        if (!line.startsWith("data: ")) continue;
        const data = line.slice(6).trim();
        if (data === "[DONE]") return;
        try {
          const parsed = JSON.parse(data);
          if (parsed.object === "chat.completion.chunk") {
            const delta = parsed.choices?.[0]?.delta?.content;
            if (delta) onDelta(delta);
          } else if (parsed.object === "onlumis.citations") {
            onFinal(parsed);
          }
        } catch {
          // unvollständige/fremde Events ignorieren
        }
      }
    }
  }
}

export function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const conversationId = useRef<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [messages]);

  async function send(question: string) {
    const trimmed = question.trim();
    if (!trimmed || busy) return;
    setError(null);
    setBusy(true);
    setInput("");

    const history = messages.map((m) => ({ role: m.role, content: m.content }));
    setMessages((prev) => [
      ...prev,
      { role: "user", content: trimmed },
      { role: "assistant", content: "", pending: true },
    ]);

    const updateLast = (patch: Partial<Message> | ((m: Message) => Partial<Message>)) =>
      setMessages((prev) => {
        const next = [...prev];
        const last = next[next.length - 1];
        next[next.length - 1] = {
          ...last,
          ...(typeof patch === "function" ? patch(last) : patch),
        };
        return next;
      });

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          messages: [...history, { role: "user", content: trimmed }],
          metadata: { persist: true, conversation_id: conversationId.current },
        }),
      });
      if (!response.ok || !response.body) {
        const detail = await response.json().catch(() => null);
        throw new Error(detail?.error ?? `Fehler ${response.status}`);
      }
      await readStream(
        response,
        (delta) => updateLast((m) => ({ content: m.content + delta })),
        (final) => {
          if (final.conversation_id) conversationId.current = final.conversation_id;
          updateLast({
            citations: (final.citations ?? []).filter((c) => c.used),
            messageId: final.message_id,
          });
        },
      );
      updateLast({ pending: false });
    } catch (err) {
      setMessages((prev) => prev.filter((m) => !(m.pending && !m.content)));
      setError(err instanceof Error ? err.message : "Unbekannter Fehler");
    } finally {
      setBusy(false);
    }
  }

  async function sendFeedback(index: number, rating: "up" | "down") {
    const message = messages[index];
    if (!message.messageId || message.feedback) return;
    setMessages((prev) =>
      prev.map((m, i) => (i === index ? { ...m, feedback: rating } : m)),
    );
    await fetch("/api/feedback", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ message_id: message.messageId, rating }),
    }).catch(() => undefined);
  }

  return (
    <div className="shell">
      <header className="topbar">
        <div className="logo-dot" aria-hidden />
        <strong>OnLumis</strong>
        <span>Ihr Unternehmenswissen. Lokal. Mit Quellen.</span>
      </header>

      <div className="messages" ref={scrollRef}>
        {messages.length === 0 ? (
          <div className="empty">
            <h1>Fragen Sie Ihr Unternehmenswissen</h1>
            <p>
              Antworten kommen ausschließlich aus den freigegebenen internen
              Dokumenten – mit Quellenangabe zum Ursprungsdokument.
            </p>
            <div className="examples">
              {EXAMPLES.map((example) => (
                <button key={example} onClick={() => send(example)} disabled={busy}>
                  {example}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((message, index) => (
            <MessageView
              key={index}
              message={message}
              onFeedback={(rating) => sendFeedback(index, rating)}
            />
          ))
        )}
        {error && <div className="error">⚠ {error}</div>}
      </div>

      <form
        className="composer"
        onSubmit={(event) => {
          event.preventDefault();
          send(input);
        }}
      >
        <textarea
          value={input}
          placeholder="Frage an das Unternehmenswissen …"
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              send(input);
            }
          }}
          rows={2}
        />
        <button type="submit" disabled={busy || !input.trim()}>
          Senden
        </button>
      </form>
      <div className="hint">
        Antworten basieren auf indexierten Unternehmensdokumenten und können
        unvollständig sein – Quellen prüfen.
      </div>
    </div>
  );
}

function MessageView({
  message,
  onFeedback,
}: {
  message: Message;
  onFeedback: (rating: "up" | "down") => void;
}) {
  if (message.role === "user") {
    return <div className="msg user">{message.content}</div>;
  }
  const citations = message.citations ?? [];
  return (
    <>
      <div className={`msg assistant${message.pending ? " pending" : ""}`}>
        {message.content || (message.pending ? "" : "(keine Antwort)")}
      </div>
      {citations.length > 0 && (
        <details className="citations" open={citations.length <= 3}>
          <summary>
            {citations.length} Quelle{citations.length > 1 ? "n" : ""}
          </summary>
          {citations.map((citation) => (
            <div className="citation" key={citation.n}>
              <span className="n">[{citation.n}]</span>
              {citation.title ?? citation.uri}
              {citation.page != null && ` · Seite ${citation.page}`}
              {citation.heading_path && ` · ${citation.heading_path}`}
              <span className="path">{citation.uri}</span>
            </div>
          ))}
        </details>
      )}
      {message.messageId && !message.pending && (
        <div className="actions">
          <button
            className={message.feedback === "up" ? "active" : ""}
            onClick={() => onFeedback("up")}
            aria-label="Antwort war hilfreich"
          >
            👍
          </button>
          <button
            className={message.feedback === "down" ? "active" : ""}
            onClick={() => onFeedback("down")}
            aria-label="Antwort war nicht hilfreich"
          >
            👎
          </button>
        </div>
      )}
    </>
  );
}
