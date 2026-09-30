import Link from "next/link";
import { Arrow } from "@/components/BrandIcons";
export default function NotFound() {
  return (
    <section className="shell section">
      <p className="eyebrow">404 / HIER GEHT ES NICHT WEITER</p>
      <h1 className="mt-6 mb-6 text-5xl">
        Diese Seite haben wir nicht gefunden.
      </h1>
      <p className="mb-8 text-muted">
        Die Startseite oder unser Demo-Studio helfen Ihnen weiter.
      </p>
      <div className="button-row">
        <Link href="/" className="btn btn-dark">
          Zur Startseite <Arrow />
        </Link>
        <Link href="/demo" className="text-link">
          Demo-Studio öffnen <Arrow />
        </Link>
      </div>
    </section>
  );
}
