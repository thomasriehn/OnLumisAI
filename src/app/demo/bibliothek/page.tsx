import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { hasDemoSession } from "@/lib/demo-auth";
import { DemoLibrary } from "@/components/DemoLibrary";
import catalogue from "@/data/demo-catalogue.json";
export const dynamic = "force-dynamic";
export const metadata: Metadata = {
  title: "Ihre Demo-Bibliothek",
  robots: { index: false, follow: false },
  alternates: { canonical: "/demo/bibliothek" },
};
export default async function LibraryPage() {
  if (!(await hasDemoSession())) redirect("/demo");
  return <DemoLibrary items={catalogue} />;
}
