import { API_BASE_URL, upstreamHeaders } from "@/lib/upstream";

export async function POST(request: Request) {
  const body = await request.json();
  const upstream = await fetch(`${API_BASE_URL}/v1/feedback`, {
    method: "POST",
    headers: upstreamHeaders(request),
    body: JSON.stringify(body),
  });
  if (!upstream.ok) {
    const detail = await upstream.text().catch(() => "");
    return Response.json(
      { error: detail || `Upstream-Fehler (${upstream.status})` },
      { status: upstream.status },
    );
  }
  return new Response(null, { status: 204 });
}
