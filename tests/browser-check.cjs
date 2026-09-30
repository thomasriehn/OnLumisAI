const { chromium } = require(
  process.env.PLAYWRIGHT_MODULE || "@playwright/test",
);
const fs = require("fs");
const path = require("path");
const assert = require("assert/strict");
const ROOT = path.resolve(__dirname, "..");
const base = process.env.TEST_BASE_URL || "http://localhost:3100";
const env = Object.fromEntries(
  fs
    .readFileSync(
      process.env.TEST_ENV_FILE || path.join(ROOT, ".env.local"),
      "utf8",
    )
    .split("\n")
    .filter((x) => x.includes("="))
    .map((x) => {
      const i = x.indexOf("=");
      return [x.slice(0, i), x.slice(i + 1)];
    }),
);
(async () => {
  const browser = await chromium.launch({ headless: true });
  const qa = path.join(ROOT, "qa");
  fs.mkdirSync(qa, { recursive: true });
  const checks = [];
  try {
    const page = await browser.newPage({
      viewport: { width: 1440, height: 1000 },
    });
    const errors = [];
    const external = [];
    page.on("pageerror", (e) => errors.push(e.message));
    page.on("request", (r) => {
      if (!r.url().startsWith(base) && !r.url().startsWith("data:"))
        external.push(r.url());
    });
    await page.goto(base, { waitUntil: "networkidle" });
    await page.screenshot({ path: path.join(qa, "home-desktop-top.png") });
    assert(
      (await page
        .getByRole("heading", {
          name: "Ihre Firma weiß viel.Machen Sie esansprechbar.",
        })
        .count()) || (await page.locator("h1").count()),
    );
    await page
      .locator(".visual-tabs")
      .getByRole("button", { name: "Vertrieb", exact: true })
      .click();
    await page
      .getByText("Welche Konditionen gelten für dieses Projekt?", {
        exact: true,
      })
      .waitFor();
    checks.push("Interactive knowledge diagram");
    await page.getByRole("tab", { name: /Vertrieb/ }).click();
    await page
      .locator(".case-panel")
      .getByText("Was wurde vereinbart? Die Fundstelle ist entscheidend.")
      .waitFor();
    checks.push("Use-case tabs");
    for (
      let y = 0;
      y < (await page.locator("body").evaluate((x) => x.scrollHeight));
      y += 750
    ) {
      await page.evaluate((v) => window.scrollTo(0, v), y);
      await page.waitForTimeout(70);
    }
    await page.waitForTimeout(650);
    await page.screenshot({
      path: path.join(qa, "home-desktop-full.png"),
      fullPage: true,
    });
    await page
      .getByRole("button", { name: "Service-Erklärvideo abspielen" })
      .click();
    await page.waitForTimeout(1200);
    const media = await page.locator(".product-video video").evaluate((v) => ({
      error: v.error?.message,
      time: v.currentTime,
      paused: v.paused,
      duration: v.duration,
    }));
    assert(!media.error && !media.paused && media.time > 0);
    await page.locator("video").evaluate((v) => v.pause());
    checks.push("Public explainer plays");
    for (const route of [
      "/produkt",
      "/vorteile",
      "/anwendungsfaelle",
      "/foerderung",
      "/kontakt",
      "/impressum",
      "/datenschutz",
    ]) {
      const response = await page.goto(base + route, {
        waitUntil: "networkidle",
      });
      assert.equal(response.status(), 200);
      assert.equal(await page.locator("h1").count(), 1);
      checks.push("Page " + route);
    }
    await page.goto(base + "/demo", { waitUntil: "networkidle" });
    await page
      .getByLabel("Passwort", { exact: true })
      .fill("incorrect-password");
    await page.getByRole("button", { name: "Studio öffnen" }).click();
    await page
      .getByText("Das Passwort stimmt nicht. Bitte versuchen Sie es erneut.")
      .waitFor();
    await page.getByLabel("Passwort", { exact: true }).fill(env.DEMO_PASSWORD);
    await page.getByRole("button", { name: "Studio öffnen" }).click();
    await page.waitForURL("**/demo/bibliothek");
    await page.waitForLoadState("networkidle");
    assert.equal(await page.locator(".library-grid article").count(), 27);
    checks.push("Login and 27 protected videos");
    await page.getByRole("button", { name: "V3", exact: true }).click();
    assert.equal(await page.locator(".library-grid article").count(), 11);
    await page.getByRole("searchbox").fill("Preis und Lager");
    assert.equal(await page.locator(".library-grid article").count(), 1);
    await page.screenshot({
      path: path.join(qa, "library-filtered.png"),
      fullPage: true,
    });
    const v = page.locator(".library-grid video");
    await v.evaluate((x) => x.play());
    await page.waitForTimeout(800);
    assert(await v.evaluate((x) => !x.paused && x.currentTime > 0 && !x.error));
    await v.evaluate((x) => x.pause());
    checks.push("Protected MP4 playback and search");
    const pdf = await page
      .locator(".playbook-downloads a")
      .first()
      .getAttribute("href");
    const pdfResponse = await page.request.get(base + pdf, {
      headers: { Range: "bytes=0-15" },
    });
    assert.equal(pdfResponse.status(), 206);
    assert((await pdfResponse.body()).toString().startsWith("%PDF"));
    checks.push("Protected PDF");
    await page.getByRole("button", { name: "Abmelden" }).click();
    await page.waitForURL("**/demo");
    assert.equal((await page.request.get(base + pdf)).status(), 401);
    checks.push("Logout protects direct URLs again");
    await page.screenshot({
      path: path.join(qa, "login-desktop.png"),
      fullPage: true,
    });
    for (const width of [390, 768]) {
      await page.setViewportSize({ width, height: 844 });
      await page.goto(base, { waitUntil: "networkidle" });
      assert(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= window.innerWidth,
        ),
        "Horizontal overflow at " + width,
      );
      await page.screenshot({ path: path.join(qa, "home-" + width + ".png") });
      await page.getByRole("button", { name: "Menü öffnen" }).click();
      await page
        .locator(".mobile-nav")
        .getByRole("link", { name: "Demo-Studio" })
        .click();
      await page.waitForURL("**/demo");
      assert(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= window.innerWidth,
        ),
      );
      checks.push("Mobile layout " + width);
    }
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.goto(base);
    assert.equal(
      await page
        .locator(".flow-pulse")
        .evaluate((x) => getComputedStyle(x).animationName),
      "none",
    );
    checks.push("Reduced motion respected");
    assert.deepEqual(errors, []);
    assert.deepEqual(external, []);
    checks.push("No browser errors or third-party requests");
    fs.writeFileSync(
      path.join(qa, "browser-check.json"),
      JSON.stringify({ checks }, null, 2),
    );
    console.log(JSON.stringify({ passed: checks.length, checks }));
  } finally {
    await browser.close();
  }
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
