import type { MetadataRoute } from "next";
import { siteConfig } from "@/lib/site";

const routes = [
  { path: "", priority: 1, changeFrequency: "monthly" as const },
  { path: "/produkt", priority: 0.9, changeFrequency: "monthly" as const },
  { path: "/vorteile", priority: 0.8, changeFrequency: "monthly" as const },
  {
    path: "/anwendungsfaelle",
    priority: 0.8,
    changeFrequency: "monthly" as const,
  },
  { path: "/foerderung", priority: 0.8, changeFrequency: "monthly" as const },
  { path: "/kontakt", priority: 0.7, changeFrequency: "yearly" as const },
  { path: "/datenschutz", priority: 0.3, changeFrequency: "yearly" as const },
  { path: "/impressum", priority: 0.3, changeFrequency: "yearly" as const },
];

export default function sitemap(): MetadataRoute.Sitemap {
  return routes.map((route) => ({
    url: `${siteConfig.url}${route.path}`,
    lastModified: new Date(),
    changeFrequency: route.changeFrequency,
    priority: route.priority,
  }));
}
