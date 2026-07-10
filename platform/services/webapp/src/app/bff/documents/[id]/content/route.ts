import { NextRequest } from "next/server";
import { forward } from "@/lib/upstream";

// Quellen-Viewer: streamt das Ursprungsdokument (ACL-geprüft im Orchestrator).
export async function GET(
  request: NextRequest,
  ctx: { params: Promise<{ id: string }> },
) {
  const { id } = await ctx.params;
  return forward(request, `/v1/documents/${id}/content`, { raw: true });
}
