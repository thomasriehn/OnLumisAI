import { ImageResponse } from "next/og";

export const size = { width: 64, height: 64 };
export const contentType = "image/png";

export default function Icon() {
  return new ImageResponse(
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "#0b1713",
        borderRadius: "50%",
      }}
    >
      <div
        style={{
          width: 34,
          height: 34,
          borderRadius: "50%",
          border: "3px solid rgba(14,159,126,0.8)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <div
          style={{
            width: 12,
            height: 12,
            borderRadius: "50%",
            background: "#12b395",
          }}
        />
      </div>
    </div>,
    { ...size },
  );
}
