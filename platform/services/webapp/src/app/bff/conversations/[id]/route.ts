import { NextRequest } from "next/server";
import { forward } from "@/lib/upstream";

async function proxy(
  request: NextRequest,
  ctx: { params: Promise<{ id: string }> },
) {
  const { id } = await ctx.params;
  return forward(request, `/v1/conversations/${id}`);
}

export { proxy as GET, proxy as DELETE };
