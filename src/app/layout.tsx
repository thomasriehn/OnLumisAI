import type { Metadata } from "next";
import "@fontsource-variable/inter";
import "@fontsource-variable/manrope";
import Script from "next/script";
import "./globals.css";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { siteConfig } from "@/lib/site";

export const metadata: Metadata = {
  metadataBase: new URL(siteConfig.url),
  title: {
    default: `${siteConfig.name} – Lokale KI für Ihr Unternehmenswissen`,
    template: `%s | ${siteConfig.name}`,
  },
  description: siteConfig.description,
  keywords: [
    "lokale KI Unternehmen",
    "On-Premise KI",
    "DSGVO-konforme KI",
    "KI für den Mittelstand",
    "Unternehmens-KI ohne Cloud",
    "eigene KI Wissensdatenbank",
    "KI Assistent Firma",
  ],
  authors: [
    { name: siteConfig.company.legalName, url: siteConfig.company.url },
  ],
  creator: siteConfig.company.legalName,
  publisher: siteConfig.company.legalName,
  alternates: {
    canonical: "/",
  },
  openGraph: {
    type: "website",
    locale: siteConfig.locale,
    url: siteConfig.url,
    siteName: siteConfig.name,
    title: `${siteConfig.name} – ${siteConfig.tagline}`,
    description: siteConfig.description,
  },
  twitter: {
    card: "summary_large_image",
    title: `${siteConfig.name} – ${siteConfig.tagline}`,
    description: siteConfig.description,
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
    },
  },
};

const organizationJsonLd = {
  "@context": "https://schema.org",
  "@type": "Organization",
  name: siteConfig.company.legalName,
  url: siteConfig.company.url,
  brand: {
    "@type": "Brand",
    name: siteConfig.name,
    url: siteConfig.url,
  },
  contactPoint: [
    {
      "@type": "ContactPoint",
      contactType: "sales",
      email: siteConfig.company.contactEmail,
      areaServed: "DE",
      availableLanguage: ["de"],
    },
  ],
};

const softwareJsonLd = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  name: siteConfig.name,
  applicationCategory: "BusinessApplication",
  operatingSystem: "On-Premise / Linux",
  description: siteConfig.description,
  url: siteConfig.url,
  offers: {
    "@type": "Offer",
    availability: "https://schema.org/InStock",
    areaServed: "DE",
  },
  provider: {
    "@type": "Organization",
    name: siteConfig.company.legalName,
    url: siteConfig.company.url,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="de" className="h-full antialiased">
      <body className="flex min-h-full flex-col bg-background text-foreground">
        <Script
          id="ld-organization"
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify(organizationJsonLd),
          }}
        />
        <Script
          id="ld-software"
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(softwareJsonLd) }}
        />
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[100] focus:rounded-md focus:bg-accent-strong focus:px-4 focus:py-2 focus:text-white"
        >
          Zum Inhalt springen
        </a>
        <Header />
        <main id="main-content" className="flex-1">
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
}
