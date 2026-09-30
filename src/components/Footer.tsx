import Link from "next/link";
import { Logo } from "./Logo";
import { Arrow } from "./BrandIcons";
export function Footer() {
  return (
    <footer className="site-footer">
      <div className="shell">
        <div className="footer-top">
          <div>
            <p className="eyebrow">DAS WISSEN IST IHRES.</p>
            <p className="footer-statement">
              Die Möglichkeiten
              <br />
              beginnen hier.
            </p>
            <a href="mailto:info@onlumis.ai">
              info@onlumis.ai <Arrow />
            </a>
          </div>
          <div className="footer-links">
            <div>
              <span>ENTDECKEN</span>
              <Link href="/produkt">Produkt & Architektur</Link>
              <Link href="/anwendungsfaelle">Anwendungsfälle</Link>
              <Link href="/vorteile">Ihre Vorteile</Link>
              <Link href="/foerderung">Projekt & Förderung</Link>
            </div>
            <div>
              <span>INS GESPRÄCH KOMMEN</span>
              <Link href="/kontakt">Kontakt aufnehmen</Link>
              <Link href="/demo">Demo-Studio</Link>
              <a
                href="https://julith.gmbh"
                target="_blank"
                rel="noopener noreferrer"
              >
                JULITH GmbH ↗
              </a>
            </div>
          </div>
        </div>
        <div className="footer-bottom">
          <Logo />
          <p>
            © {new Date().getFullYear()} JULITH GmbH · Entwickelt für den
            Mittelstand.
          </p>
          <div>
            <Link href="/impressum">Impressum</Link>
            <Link href="/datenschutz">Datenschutz</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
