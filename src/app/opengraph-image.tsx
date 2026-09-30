import { ImageResponse } from "next/og";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";
export default function OpengraphImage() {
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
        <span style={{ fontSize: 36, fontWeight: 700 }}>OnLumisAI</span>
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
    size,
  );
}
