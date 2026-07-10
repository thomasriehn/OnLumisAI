import { API_BASE_URL, upstreamHeaders } from "@/lib/upstream";

// Streaming-Proxy: reicht den SSE-Stream des Orchestrators 1:1 an den
// Browser weiter (Route Handler, nicht gecacht – POST ist immer dynamisch).
export async function POST(request: Request) {
  const body = await request.json();
  const upstream = await fetch(`${API_BASE_URL}/v1/chat/completions`, {
    method: "POST",
    headers: upstreamHeaders(request),
    body: JSON.stringify({ ...body, stream: true }),
  });

  if (!upstream.ok || !upstream.body) {
    const detail = await upstream.text().catch(() => "");
    return Response.json(
      { error: detail || `Upstream-Fehler (${upstream.status})` },
      { status: upstream.status || 502 },
    );
  }

  return new Response(upstream.body, {
    headers: {
      "content-type": "text/event-stream",
      "cache-control": "no-cache",
    },
  });
}
