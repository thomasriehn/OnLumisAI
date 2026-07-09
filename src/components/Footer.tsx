import Link from "next/link";
import { Container } from "@/components/Container";
import { Logo } from "@/components/Logo";
import { navigation, legalNavigation, siteConfig } from "@/lib/site";

export function Footer() {
  return (
    <footer className="border-t border-border bg-primary text-white/80">
      <Container className="grid gap-10 py-14 md:grid-cols-4">
        <div className="md:col-span-2">
          <div className="[&_a]:text-white [&_span]:text-white">
            <Logo />
          </div>
          <p className="mt-4 max-w-sm text-sm leading-relaxed text-white/70">
            {siteConfig.tagline} OnLumis wird entwickelt und betrieben von der{" "}
            <a
              href={siteConfig.company.url}
              className="underline decoration-white/30 underline-offset-2 hover:text-white"
              target="_blank"
              rel="noopener noreferrer"
            >
              {siteConfig.company.legalName}
            </a>
            .
          </p>
        </div>

        <div>
          <h3 className="text-sm font-semibold text-white">Produkt</h3>
          <ul className="mt-4 space-y-3 text-sm">
            {navigation.map((item) => (
              <li key={item.href}>
                <Link href={item.href} className="text-white/70 hover:text-white">
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h3 className="text-sm font-semibold text-white">Rechtliches</h3>
          <ul className="mt-4 space-y-3 text-sm">
            {legalNavigation.map((item) => (
              <li key={item.href}>
                <Link href={item.href} className="text-white/70 hover:text-white">
                  {item.label}
                </Link>
              </li>
            ))}
            <li>
              <a
                href={`mailto:${siteConfig.company.contactEmail}`}
                className="text-white/70 hover:text-white"
              >
                {siteConfig.company.contactEmail}
              </a>
            </li>
          </ul>
        </div>
      </Container>

      <div className="border-t border-white/10">
        <Container className="flex flex-col gap-2 py-6 text-xs text-white/60 sm:flex-row sm:items-center sm:justify-between">
          <p>
            © {new Date().getFullYear()} {siteConfig.company.legalName} · {siteConfig.name}
          </p>
          <p>Ein Schweizer Unternehmen · Für den deutschen Mittelstand entwickelt</p>
        </Container>
      </div>
    </footer>
  );
}
