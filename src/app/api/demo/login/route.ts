import { NextResponse } from "next/server";
import { allowLogin } from "@/lib/demo-limit";
import {
  createSession,
  demoConfigured,
  passwordMatches,
  PRIVATE_HEADERS,
  sameOrigin,
  SESSION_COOKIE,
  sessionOptions,
} from "@/lib/demo-auth";
export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export async function POST(request: Request) {
  const reply = (message: string, status: number) =>
    NextResponse.json(
      { ok: false, message },
      { status, headers: PRIVATE_HEADERS },
    );
  if (!sameOrigin(request))
    return reply("Diese Anfrage ist nicht erlaubt.", 403);
  if (!allowLogin(request))
    return reply("Zu viele Versuche. Bitte warten Sie zehn Minuten.", 429);
  if (!demoConfigured())
    return reply(
      "Der Demo-Zugang wird gerade vorbereitet. Bitte kontaktieren Sie uns.",
      503,
    );
  if (!request.headers.get("content-type")?.startsWith("application/json"))
    return reply("Ungültige Anfrage.", 400);
  let password: unknown;
  try {
    const reader = request.body?.getReader();
    if (!reader) return reply("Ungültige Anfrage.", 400);
    let body = "";
    let size = 0;
    const decoder = new TextDecoder();
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > 2048) {
        await reader.cancel();
        return reply("Ungültige Anfrage.", 413);
      }
      body += decoder.decode(value, { stream: true });
    }
    body += decoder.decode();
    password = JSON.parse(body).password;
  } catch {
    return reply("Ungültige Anfrage.", 400);
  }
  if (
    typeof password !== "string" ||
    password.length > 256 ||
    !passwordMatches(password)
  )
    return reply(
      "Das Passwort stimmt nicht. Bitte versuchen Sie es erneut.",
      401,
    );
  const response = NextResponse.json(
    { ok: true },
    { headers: PRIVATE_HEADERS },
  );
  response.cookies.set(SESSION_COOKIE, createSession(), sessionOptions());
  return response;
}
