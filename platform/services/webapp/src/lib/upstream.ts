/**
 * Server-seitige Anbindung an den RAG-Orchestrator (BFF-Muster).
 *
 * OIDC-Betrieb: Tokens liegen ausschließlich in httpOnly-Cookies; der
 * Browser sieht sie nie. Vor jedem Upstream-Call wird das Access-Token bei
 * Bedarf über das Refresh-Token erneuert (Rotation via Cookie-Update).
 * Dev-Betrieb: Der Server setzt die X-Dev-*-Header selbst.
 */

import { cookies } from "next/headers";

export const API_BASE_URL = process.env.API_BASE_URL ?? "http://localhost:8000";
export const AUTH_MODE = process.env.AUTH_MODE ?? "dev";
export const OIDC_ISSUER_URL = (process.env.OIDC_ISSUER_URL ?? "").replace(/\/$/, "");
export const OIDC_INTERNAL_URL = (
  process.env.OIDC_INTERNAL_URL || OIDC_ISSUER_URL
).replace(/\/$/, "");
export const OIDC_CLIENT_ID = process.env.OIDC_CLIENT_ID ?? "onlumis-webapp";

/** Öffentlicher Origin des Requests (berücksichtigt Reverse-Proxy-Header). */
export function requestOrigin(request: Request): string {
  const proto = request.headers.get("x-forwarded-proto") ?? "http";
  const host =
    request.headers.get("x-forwarded-host") ??
    request.headers.get("host") ??
    "localhost";
  return `${proto}://${host}`;
}

const AT_COOKIE = "onlumis_at";
const RT_COOKIE = "onlumis_rt";
const EXP_COOKIE = "onlumis_exp";

const cookieOpts = {
  httpOnly: true,
  sameSite: "lax" as const,
  secure: process.env.NODE_ENV === "production" && !process.env.ALLOW_INSECURE_COOKIES,
  path: "/",
};

export type TokenSet = {
  access_token: string;
  refresh_token?: string;
  expires_in?: number;
  id_token?: string;
};

export async function storeTokens(tokens: TokenSet) {
  const store = await cookies();
  store.set(AT_COOKIE, tokens.access_token, cookieOpts);
  if (tokens.refresh_token) store.set(RT_COOKIE, tokens.refresh_token, cookieOpts);
  const expiresAt = Date.now() + (tokens.expires_in ?? 300) * 1000;
  store.set(EXP_COOKIE, String(expiresAt), cookieOpts);
}

export async function clearTokens() {
  const store = await cookies();
  for (const name of [AT_COOKIE, RT_COOKIE, EXP_COOKIE]) store.delete(name);
}

async function refreshTokens(refreshToken: string): Promise<TokenSet | null> {
  const response = await fetch(
    `${OIDC_INTERNAL_URL}/protocol/openid-connect/token`,
    {
      method: "POST",
      headers: { "content-type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "refresh_token",
        client_id: OIDC_CLIENT_ID,
        refresh_token: refreshToken,
      }),
    },
  );
  return response.ok ? response.json() : null;
}

/** Gültiges Access-Token aus der Session; erneuert es bei Bedarf. */
export async function getAccessToken(): Promise<string | null> {
  const store = await cookies();
  const token = store.get(AT_COOKIE)?.value;
  const expiresAt = Number(store.get(EXP_COOKIE)?.value ?? 0);
  if (token && Date.now() < expiresAt - 30_000) return token;

  const refreshToken = store.get(RT_COOKIE)?.value;
  if (!refreshToken) return token ?? null;
  const refreshed = await refreshTokens(refreshToken);
  if (!refreshed) {
    await clearTokens();
    return null;
  }
  await storeTokens(refreshed);
  return refreshed.access_token;
}

export async function upstreamHeaders(): Promise<Record<string, string>> {
  const headers: Record<string, string> = { "content-type": "application/json" };
  if (AUTH_MODE !== "oidc") {
    headers["x-dev-user"] = process.env.DEV_USER ?? "dev";
    headers["x-dev-groups"] = process.env.DEV_GROUPS ?? "all-users";
    return headers;
  }
  const token = await getAccessToken();
  if (token) headers.authorization = `Bearer ${token}`;
  return headers;
}

/** Generischer Proxy zum Orchestrator (JSON; raw für Binär-/Streaming-Inhalte). */
export async function forward(
  request: Request,
  path: string,
  opts: { raw?: boolean } = {},
): Promise<Response> {
  const headers = await upstreamHeaders();
  const init: RequestInit & { duplex?: "half" } = {
    method: request.method,
    headers,
  };
  const contentType = request.headers.get("content-type") ?? "";
  if (!["GET", "HEAD", "DELETE"].includes(request.method)) {
    if (contentType.startsWith("multipart/")) {
      headers["content-type"] = contentType;
      init.body = request.body;
      init.duplex = "half";
    } else {
      init.body = await request.text();
    }
  }
  const upstream = await fetch(`${API_BASE_URL}${path}`, init);
  const responseHeaders: Record<string, string> = {
    "content-type": upstream.headers.get("content-type") ?? "application/json",
  };
  const disposition = upstream.headers.get("content-disposition");
  if (disposition) responseHeaders["content-disposition"] = disposition;
  if (opts.raw) {
    return new Response(upstream.body, { status: upstream.status, headers: responseHeaders });
  }
  const body = await upstream.text();
  return new Response(body, { status: upstream.status, headers: responseHeaders });
}
