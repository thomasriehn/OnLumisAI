import { NextRequest } from "next/server";
import { API_BASE_URL, upstreamHeaders } from "@/lib/upstream";

// Generischer Proxy für alle Admin-Endpunkte (/v1/admin/*). Die Rollenprüfung
// (onlumis-admin) übernimmt der RAG-Orchestrator.
async function proxy(
  request: NextRequest,
  ctx: { params: Promise<{ path: string[] }> },
) {
  const { path } = await ctx.params;
  const url = `${API_BASE_URL}/v1/admin/${path.join("/")}${request.nextUrl.search}`;
  const init: RequestInit = {
    method: request.method,
    headers: upstreamHeaders(request),
  };
  if (!["GET", "DELETE"].includes(request.method)) {
    init.body = await request.text();
  }
  const upstream = await fetch(url, init);
  const body = await upstream.text();
  return new Response(body, {
    status: upstream.status,
    headers: {
      "content-type": upstream.headers.get("content-type") ?? "application/json",
    },
  });
}

export { proxy as GET, proxy as POST, proxy as PATCH, proxy as DELETE };
