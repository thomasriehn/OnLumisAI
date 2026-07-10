import { NextRequest } from "next/server";
import { cookies } from "next/headers";
import {
  OIDC_CLIENT_ID,
  OIDC_INTERNAL_URL,
  requestOrigin,
  storeTokens,
} from "@/lib/upstream";

// Tauscht den Authorization Code serverseitig gegen Tokens (PKCE).
export async function GET(request: NextRequest) {
  const code = request.nextUrl.searchParams.get("code");
  const state = request.nextUrl.searchParams.get("state");
  const store = await cookies();
  const verifier = store.get("onlumis_pkce")?.value;
  const expectedState = store.get("onlumis_state")?.value;
  store.delete("onlumis_pkce");
  store.delete("onlumis_state");

  if (!code || !verifier || !state || state !== expectedState) {
    return new Response("Login fehlgeschlagen (State/PKCE)", { status: 400 });
  }

  const response = await fetch(
    `${OIDC_INTERNAL_URL}/protocol/openid-connect/token`,
    {
      method: "POST",
      headers: { "content-type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "authorization_code",
        client_id: OIDC_CLIENT_ID,
        code,
        redirect_uri: `${requestOrigin(request)}/bff/auth/callback`,
        code_verifier: verifier,
      }),
    },
  );
  if (!response.ok) {
    return new Response(`Token-Austausch fehlgeschlagen (${response.status})`, {
      status: 502,
    });
  }
  await storeTokens(await response.json());
  return Response.redirect(new URL("/", requestOrigin(request)));
}
