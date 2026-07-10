import { NextRequest } from "next/server";
import { AUTH_MODE, OIDC_CLIENT_ID, OIDC_ISSUER_URL, clearTokens, requestOrigin } from "@/lib/upstream";

export async function GET(request: NextRequest) {
  await clearTokens();
  if (AUTH_MODE !== "oidc") return Response.redirect(new URL("/", requestOrigin(request)));
  const endSession = new URL(`${OIDC_ISSUER_URL}/protocol/openid-connect/logout`);
  endSession.search = new URLSearchParams({
    client_id: OIDC_CLIENT_ID,
    post_logout_redirect_uri: requestOrigin(request),
  }).toString();
  return Response.redirect(endSession);
}
