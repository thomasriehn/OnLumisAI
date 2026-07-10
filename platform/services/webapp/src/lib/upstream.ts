/**
 * Server-seitige Weiterleitung an den RAG-Orchestrator.
 *
 * Auth: Im OIDC-Betrieb wird das Authorization-Header des Clients
 * durchgereicht. Im Dev-Modus setzt der Server die X-Dev-*-Header selbst –
 * der Browser kann sich also keine fremden Gruppen geben.
 */
export const API_BASE_URL = process.env.API_BASE_URL ?? "http://localhost:8000";

export function upstreamHeaders(request: Request): Record<string, string> {
  const headers: Record<string, string> = { "content-type": "application/json" };
  const auth = request.headers.get("authorization");
  if (auth) headers.authorization = auth;
  if (process.env.AUTH_MODE !== "oidc") {
    headers["x-dev-user"] = process.env.DEV_USER ?? "dev";
    headers["x-dev-groups"] = process.env.DEV_GROUPS ?? "all-users";
  }
  return headers;
}
