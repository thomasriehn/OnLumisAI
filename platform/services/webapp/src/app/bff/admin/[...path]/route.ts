import { NextRequest } from "next/server";
import { forward } from "@/lib/upstream";

// Generischer Proxy für /v1/admin/* – Rollenprüfung macht der Orchestrator.
async function proxy(
  request: NextRequest,
  ctx: { params: Promise<{ path: string[] }> },
) {
  const { path } = await ctx.params;
  return forward(
    request,
    `/v1/admin/${path.join("/")}${request.nextUrl.search}`,
    { raw: path.includes("export") },
  );
}

export { proxy as GET, proxy as POST, proxy as PATCH, proxy as DELETE };
