import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";
import { hasDemoSession } from "@/lib/demo-auth";
import { DemoLogin } from "@/components/DemoLogin";
import { Lock } from "@/components/BrandIcons";
export const metadata: Metadata = {
  title: "Demo-Studio",
  robots: { index: false, follow: false },
  alternates: { canonical: "/demo" },
};
export const dynamic = "force-dynamic";
export default async function DemoPage() {
  if (await hasDemoSession()) redirect("/demo/bibliothek");
  return (
    <section className="studio-entry shell">
      <div>
        <p className="eyebrow">
          <Lock /> WILLKOMMEN IM DEMO-STUDIO
        </p>
        <h1>
          Ein genauerer Blick.
          <br />
          <em>Viel zu entdecken.</em>
        </h1>
        <p>
          Sehen Sie, wie OnLumis mit Unternehmenswissen arbeitet. An echten
          Fragen, in vollständigen Gesprächen und mit nachvollziehbaren Quellen.
        </p>
        <div className="studio-facts">
          <span>
            <b>27</b>Walkthroughs
          </span>
          <span>
            <b>3</b>Playbooks
          </span>
          <span>
            <b>1</b>Fiktives Unternehmen
          </span>
        </div>
        <p className="studio-disclaimer">
          Die Aufnahmen zeigen reale Ergebnisse einschließlich erkennbarer
          Grenzen. Grundlage sind ausschließlich fiktive Demodaten.
        </p>
      </div>
      <div className="login-card">
        <div className="login-icon">
          <Lock />
        </div>
        <h2>
          Ihr Zugang zum
          <br />
          Demo-Studio.
        </h2>
        <p>Geben Sie das Passwort ein, das Sie von uns erhalten haben.</p>
        <DemoLogin />
        <div className="login-contact">
          Noch keinen Zugang?{" "}
          <Link href="/kontakt">Demo-Zugang anfragen ↗</Link>
        </div>
      </div>
    </section>
  );
}
