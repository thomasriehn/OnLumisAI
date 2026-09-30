import assert from "node:assert/strict";
import { readFileSync, mkdirSync, writeFileSync } from "node:fs";
import { parseEnv } from "node:util";
import { createHmac } from "node:crypto";
const env = parseEnv(
  readFileSync(process.env.TEST_ENV_FILE || ".env.local", "utf8"),
);
const base = process.env.TEST_BASE_URL || "http://localhost:3100";
const origin = env.APP_ORIGIN;
const items = JSON.parse(readFileSync("src/data/demo-catalogue.json", "utf8"));
const file = "/demo/dateien/" + items[0].file;
const checks = [];
const get = (url, headers = {}, method = "GET") =>
  fetch(base + url, {
    method,
    headers,
    redirect: "manual",
    signal: AbortSignal.timeout(15000),
  });
const login = (password, originHeader = origin) =>
  fetch(base + "/api/demo/login", {
    method: "POST",
    headers: { Origin: originHeader, "Content-Type": "application/json" },
    body: JSON.stringify({ password }),
    signal: AbortSignal.timeout(15000),
  });
for (const p of [
  file,
  "/demo/dateien/playbooks/" + items[0].pdf,
  "/demo/dateien/VIDEOS.html",
  "/demo/video.html",
]) {
  const r = await get(p);
  assert.equal(r.status, 401);
  assert.match(r.headers.get("cache-control"), /no-store/);
}
assert.equal((await get("/demo/bibliothek")).status, 307);
checks.push("Anonymous pages, video, PDF and legacy HTML are protected");
assert.equal(
  (await login(env.DEMO_PASSWORD, "https://other.example")).status,
  403,
);
assert.equal((await login("wrong")).status, 401);
const r = await login(env.DEMO_PASSWORD);
assert.equal(r.status, 200);
const setCookie = r.headers.get("set-cookie");
assert(/HttpOnly/i.test(setCookie), "Session cookie must be HttpOnly");
assert(
  /SameSite=strict/i.test(setCookie),
  "Session cookie must be SameSite=strict",
);
if (origin.startsWith("https:"))
  assert(/Secure/i.test(setCookie), "HTTPS session cookie must be Secure");
const cookie = setCookie.split(";")[0];
checks.push("Same-origin login, password validation and protected cookie");
// A streamed Next.js response can be HTTP 200 even if server rendering fails.
// Verify the authenticated HTML, not only the status or the separate file API.
const library = await get("/demo/bibliothek", { Cookie: cookie });
assert.equal(library.status, 200);
const libraryHtml = await library.text();
assert(libraryHtml.includes("Wissen in Aktion."), "Library heading missing");
assert(libraryHtml.includes('class="library-grid"'), "Library grid missing");
assert.equal((libraryHtml.match(/<article[\s>]/g) || []).length, items.length);
assert(
  !libraryHtml.includes("This page couldn’t load"),
  "Library server error",
);
assert.equal((await get("/demo", { Cookie: cookie })).status, 307);
checks.push("Authenticated library renders its heading and all video cards");
const og = await get("/opengraph-image");
assert.equal(og.status, 200);
assert.match(og.headers.get("content-type"), /^image\/png/);
const ogBytes = Buffer.from(await og.arrayBuffer());
assert.equal(ogBytes.subarray(0, 8).toString("hex"), "89504e470d0a1a0a");
checks.push("Open Graph image is a valid PNG alongside authenticated metadata");
const full = await get(file, { Cookie: cookie }, "HEAD");
assert.equal(full.status, 200);
const size = Number(full.headers.get("content-length"));
assert(size > 1000);
for (const range of ["bytes=0-15", "bytes=-16"]) {
  const part = await get(file, { Cookie: cookie, Range: range });
  assert.equal(part.status, 206);
  assert.equal((await part.arrayBuffer()).byteLength, 16);
}
assert.equal(
  (await get(file, { Cookie: cookie, Range: "bytes=" + size + "-" })).status,
  416,
);
checks.push("Authenticated HEAD, seeking, suffix range and invalid range");
for (const item of items) {
  assert.equal(
    (await get("/demo/dateien/" + item.file, { Cookie: cookie }, "HEAD"))
      .status,
    200,
  );
  assert.equal(
    (await get("/demo/dateien/" + item.poster, { Cookie: cookie }, "HEAD"))
      .status,
    200,
  );
}
for (const pdf of new Set(items.map((i) => i.pdf))) {
  const r = await get("/demo/dateien/playbooks/" + pdf, {
    Cookie: cookie,
    Range: "bytes=0-4",
  });
  assert.equal(r.status, 206);
  assert.equal(await r.text(), "%PDF-");
}
checks.push("All 27 videos, 27 posters and three PDFs exist behind login");
const legacy = await get("/demo/video.html", { Cookie: cookie });
assert.equal(legacy.status, 200);
assert.match(await legacy.text(), /<base href="\/demo\/dateien\/">/);
assert.equal(
  (await get("/demo/dateien/reports/secret.json", { Cookie: cookie })).status,
  404,
);
assert.equal((await get("/private/demo/" + items[0].file)).status, 404);
assert.equal(
  (
    await get("/demo/dateien/assets/%2e%2e%2f%2e%2e%2f.env.local", {
      Cookie: cookie,
    })
  ).status,
  404,
);
checks.push(
  "Legacy page stays protected; non-allowlisted and traversal paths fail",
);
assert.equal(
  (await get(file, { Cookie: cookie.slice(0, -1) + "!" })).status,
  401,
);
const payload = Buffer.from(
  JSON.stringify({
    exp: Math.floor(Date.now() / 1000) - 1,
    nonce: "x".repeat(32),
  }),
).toString("base64url");
const key = createHmac("sha256", env.DEMO_SESSION_SECRET)
  .update(env.DEMO_PASSWORD)
  .digest();
const sig = createHmac("sha256", key).update(payload).digest("base64url");
assert.equal(
  (await get(file, { Cookie: "onlumis_demo=" + payload + "." + sig })).status,
  401,
);
checks.push("Tampered and expired sessions rejected");
const logout = await fetch(base + "/api/demo/logout", {
  method: "POST",
  headers: { Cookie: cookie, Origin: origin },
});
assert.equal(logout.status, 200);
assert.match(logout.headers.get("set-cookie"), /Max-Age=0/);
assert.equal((await get(file)).status, 401);
checks.push("Logout clears browser session");
mkdirSync("qa", { recursive: true });
writeFileSync("qa/access-check.json", JSON.stringify({ checks }, null, 2));
console.log(JSON.stringify({ passed: checks.length, checks }));
