import { NextRequest } from "next/server";
import { cookies } from "next/headers";
import { AUTH_MODE, OIDC_CLIENT_ID, OIDC_ISSUER_URL, requestOrigin } from "@/lib/upstream";

function base64url(bytes: Uint8Array): string {
  return Buffer.from(bytes).toString("base64url");
}

// Startet den Authorization-Code-Flow mit PKCE (S256).
export async function GET(request: NextRequest) {
  if (AUTH_MODE !== "oidc") return Response.redirect(new URL("/", requestOrigin(request)));

  const verifier = base64url(crypto.getRandomValues(new Uint8Array(32)));
  const state = base64url(crypto.getRandomValues(new Uint8Array(16)));
  const challenge = base64url(
    new Uint8Array(
      await crypto.subtle.digest("SHA-256", new TextEncoder().encode(verifier)),
    ),
  );

  const store = await cookies();
  const opts = { httpOnly: true, sameSite: "lax" as const, path: "/", maxAge: 600 };
  store.set("onlumis_pkce", verifier, opts);
  store.set("onlumis_state", state, opts);

  const redirectUri = `${requestOrigin(request)}/bff/auth/callback`;
  const authorize = new URL(`${OIDC_ISSUER_URL}/protocol/openid-connect/auth`);
  authorize.search = new URLSearchParams({
    client_id: OIDC_CLIENT_ID,
    response_type: "code",
    // Nur "openid": Username/Gruppen kommen über Client-Level-Mapper des
    // Realms (Import bindet Built-in-Scopes wie profile/email nicht zuverlässig).
    scope: "openid",
    redirect_uri: redirectUri,
    state,
    code_challenge: challenge,
    code_challenge_method: "S256",
  }).toString();
  return Response.redirect(authorize);
}
