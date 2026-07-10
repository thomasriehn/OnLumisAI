import { API_BASE_URL, upstreamHeaders } from "@/lib/upstream";

export async function POST(request: Request) {
  const body = await request.json();
  const upstream = await fetch(`${API_BASE_URL}/v1/search`, {
    method: "POST",
    headers: upstreamHeaders(request),
    body: JSON.stringify(body),
  });
  const payload = await upstream.text();
  return new Response(payload, {
    status: upstream.status,
    headers: { "content-type": "application/json" },
  });
}
