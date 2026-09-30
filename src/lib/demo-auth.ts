import {
  createHash,
  createHmac,
  randomBytes,
  timingSafeEqual,
} from "node:crypto";
import { cookies } from "next/headers";
export const SESSION_COOKIE = "onlumis_demo";
export const SESSION_SECONDS = 8 * 60 * 60;
export const PRIVATE_HEADERS = {
  "Cache-Control": "private, no-store, max-age=0",
  "X-Robots-Tag": "noindex, nofollow, noarchive",
  Vary: "Cookie",
  "X-Content-Type-Options": "nosniff",
};
function configuration() {
  const password = process.env.DEMO_PASSWORD ?? "";
  const secret = process.env.DEMO_SESSION_SECRET ?? "";
  if (password.length < 16 || secret.length < 32) return null;
  return { password, secret };
}
export function demoConfigured() {
  return configuration() !== null;
}
function digest(value: string) {
  return createHash("sha256").update(value).digest();
}
export function passwordMatches(input: string) {
  const config = configuration();
  return !!config && timingSafeEqual(digest(input), digest(config.password));
}
function sign(payload: string) {
  const config = configuration();
  if (!config) throw Error("Demo access is not configured");
  const key = createHmac("sha256", config.secret)
    .update(config.password)
    .digest();
  return createHmac("sha256", key).update(payload).digest("base64url");
}
export function createSession(now = Date.now()) {
  const payload = Buffer.from(
    JSON.stringify({
      exp: Math.floor(now / 1000) + SESSION_SECONDS,
      nonce: randomBytes(24).toString("base64url"),
    }),
  ).toString("base64url");
  return `${payload}.${sign(payload)}`;
}
export function validSession(token: string | undefined, now = Date.now()) {
  if (!configuration() || !token || token.length > 512) return false;
  try {
    const parts = token.split(".");
    if (parts.length !== 2) return false;
    const [payload, sig] = parts;
    const expected = sign(payload);
    if (
      !/^[a-zA-Z0-9_-]{43}$/.test(sig) ||
      !timingSafeEqual(Buffer.from(sig), Buffer.from(expected))
    )
      return false;
    const data = JSON.parse(Buffer.from(payload, "base64url").toString("utf8"));
    const seconds = Math.floor(now / 1000);
    return (
      Number.isSafeInteger(data.exp) &&
      data.exp > seconds &&
      data.exp <= seconds + SESSION_SECONDS &&
      typeof data.nonce === "string" &&
      data.nonce.length === 32
    );
  } catch {
    return false;
  }
}
export async function hasDemoSession() {
  return validSession((await cookies()).get(SESSION_COOKIE)?.value);
}
export function sessionOptions() {
  return {
    httpOnly: true,
    secure:
      process.env.NODE_ENV === "production" &&
      !process.env.APP_ORIGIN?.startsWith("http://localhost:"),
    sameSite: "strict" as const,
    path: "/",
    maxAge: SESSION_SECONDS,
  };
}
export function sameOrigin(request: Request) {
  const expected = process.env.APP_ORIGIN ?? "https://onlumis.ai";
  return request.headers.get("origin") === new URL(expected).origin;
}
