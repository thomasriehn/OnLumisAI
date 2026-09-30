import { ImageResponse } from "next/og";
import { readFile } from "node:fs/promises";
import { join } from "node:path";

export const size = { width: 1200, height: 630 };
export const contentType = "image/png";
export default async function OpengraphImage() {
  // Page metadata imports this module too: only read fonts when rendering the image.
  const [bodyFont, logoStrong, logoLight] = await Promise.all([
    readFile(
      join(
        process.cwd(),
        "node_modules/next/dist/compiled/@vercel/og/Geist-Regular.ttf",
      ),
    ),
    readFile(join(process.cwd(), "src/assets/fonts/OnLumisLogoStrong.ttf")),
    readFile(join(process.cwd(), "src/assets/fonts/OnLumisLogoLight.ttf")),
  ]);
  return new ImageResponse(
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        width: "100%",
        height: "100%",
        padding: 68,
        background: "#0b1713",
        color: "#edf6f2",
        fontFamily: "sans-serif",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 15 }}>
          <div
            style={{
              width: 18,
              height: 18,
              borderRadius: "50%",
              background: "#32c5a1",
              boxShadow: "0 0 21px #32c5a170",
              flexShrink: 0,
            }}
          />
          <div
            style={{
              display: "flex",
              alignItems: "baseline",
              fontSize: 36,
              letterSpacing: -1.8,
            }}
          >
            <span style={{ fontFamily: "OnLumisLogoStrong", fontWeight: 700 }}>
              OnLumis
            </span>
            <span
              style={{
                fontFamily: "OnLumisLogoLight",
                fontWeight: 400,
                color: "#32d1af",
              }}
            >
              AI
            </span>
          </div>
        </div>
        <span style={{ fontSize: 16, color: "#a3b9b0" }}>
          IHR WISSEN. IHRE INFRASTRUKTUR. IHRE KI.
        </span>
      </div>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          fontSize: 70,
          fontWeight: 600,
          lineHeight: 1.07,
          letterSpacing: -3,
        }}
      >
        <span>Ihre Firma weiß viel.</span>
        <span>Machen Sie es</span>
        <span style={{ color: "#12b395" }}>ansprechbar.</span>
      </div>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          fontSize: 19,
          color: "#a3b9b0",
        }}
      >
        <span>Lokale KI für den Mittelstand</span>
        <span>onlumis.ai · JULITH GmbH</span>
      </div>
    </div>,
    {
      ...size,
      fonts: [
        { name: "sans serif", data: bodyFont, weight: 700, style: "normal" },
        {
          name: "OnLumisLogoStrong",
          data: logoStrong,
          weight: 700,
          style: "normal",
        },
        {
          name: "OnLumisLogoLight",
          data: logoLight,
          weight: 400,
          style: "normal",
        },
      ],
    },
  );
}
