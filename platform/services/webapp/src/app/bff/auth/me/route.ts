import { AUTH_MODE, getAccessToken } from "@/lib/upstream";

function decodeClaims(token: string): Record<string, unknown> {
  try {
    const payload = token.split(".")[1];
    return JSON.parse(Buffer.from(payload, "base64url").toString("utf-8"));
  } catch {
    return {};
  }
}

// Session-Status für die UI (Anzeige only – Autorität bleibt bei der API).
export async function GET() {
  if (AUTH_MODE !== "oidc") {
    return Response.json({
      authenticated: true,
      mode: "dev",
      username: process.env.DEV_USER ?? "dev",
    });
  }
  const token = await getAccessToken();
  if (!token) return Response.json({ authenticated: false, mode: "oidc" });
  const claims = decodeClaims(token);
  return Response.json({
    authenticated: true,
    mode: "oidc",
    username: claims.preferred_username ?? claims.sub ?? "angemeldet",
  });
}
