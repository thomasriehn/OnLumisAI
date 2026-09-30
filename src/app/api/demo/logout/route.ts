import { NextResponse } from "next/server";
import {
  PRIVATE_HEADERS,
  sameOrigin,
  SESSION_COOKIE,
  sessionOptions,
} from "@/lib/demo-auth";
export async function POST(request: Request) {
  if (!sameOrigin(request))
    return NextResponse.json(
      { ok: false },
      { status: 403, headers: PRIVATE_HEADERS },
    );
  const response = NextResponse.json(
    { ok: true },
    { headers: PRIVATE_HEADERS },
  );
  response.cookies.set(SESSION_COOKIE, "", { ...sessionOptions(), maxAge: 0 });
  return response;
}
