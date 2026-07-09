export const siteConfig = {
  name: "OnLumis",
  tagline: "Ihre Firma. Ihre KI.",
  domain: "onlumis.ai",
  url: "https://onlumis.ai",
  description:
    "OnLumis ist die lokale KI-Lösung der JULITH GmbH für kleine und mittlere Unternehmen: Ihr Unternehmenswissen wird in ein On-Premise-KI-System eingebettet – DSGVO-konform, ohne Cloud-Zwang und vollständig unter eigener Kontrolle.",
  locale: "de_DE",
  company: {
    legalName: "JULITH GmbH",
    url: "https://julith.gmbh",
    contactEmail: "info@onlumis.ai",
    legalEmail: "info@julith.gmbh",
    address: {
      street: "Erlengasse 3",
      zip: "8240",
      city: "Thayngen",
      country: "Schweiz",
    },
    registerNumber: "CHE-164.714.634",
    managingDirector: "Thomas Riehn",
  },
} as const;

export const navigation = [
  { label: "Produkt", href: "/produkt" },
  { label: "Vorteile", href: "/vorteile" },
  { label: "Anwendungsfälle", href: "/anwendungsfaelle" },
  { label: "Förderung", href: "/foerderung" },
  { label: "Kontakt", href: "/kontakt" },
] as const;

export const legalNavigation = [
  { label: "Impressum", href: "/impressum" },
  { label: "Datenschutz", href: "/datenschutz" },
] as const;
