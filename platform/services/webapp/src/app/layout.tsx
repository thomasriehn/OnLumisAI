import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "OnLumis – Ihr Unternehmenswissen",
  description:
    "Interner Wissensassistent: Antworten aus Ihren eigenen Dokumenten, mit Quellenangabe – vollständig lokal betrieben.",
  robots: { index: false, follow: false },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="de">
      <body>{children}</body>
    </html>
  );
}
