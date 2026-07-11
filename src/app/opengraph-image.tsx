import { ImageResponse } from "next/og";
import { siteConfig } from "@/lib/site";

export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OpengraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: 72,
          background: "linear-gradient(135deg, #0b1220 0%, #0f2a43 60%, #0b7e64 130%)",
          color: "white",
          fontFamily: "sans-serif",
        }}
      >
        {/* Bild- und Wortmarke analog zu components/Logo.tsx */}
        <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
          <div
            style={{
              width: 64,
              height: 64,
              borderRadius: "50%",
              background: "#17436a",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <div
              style={{
                width: 52,
                height: 52,
                borderRadius: "50%",
                border: "2px solid rgba(14,159,126,0.7)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <div
                style={{
                  width: 16,
                  height: 16,
                  borderRadius: "50%",
                  background: "#0e9f7e",
                }}
              />
            </div>
          </div>
          <div style={{ fontSize: 40, fontWeight: 700, display: "flex" }}>
            On<span style={{ color: "#3ddbb0" }}>Lumis</span>
          </div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 20, maxWidth: 980 }}>
          <div style={{ fontSize: 60, fontWeight: 700, lineHeight: 1.15, display: "flex" }}>
            Ihre Firma.
          </div>
          <div style={{ fontSize: 60, fontWeight: 700, lineHeight: 1.15, color: "#3ddbb0", display: "flex" }}>
            Ihre KI.
          </div>
          <div style={{ fontSize: 26, color: "rgba(255,255,255,0.75)", display: "flex" }}>
            On-Premise-KI für den deutschen Mittelstand · {siteConfig.company.legalName}
          </div>
        </div>
      </div>
    ),
    { ...size }
  );
}
