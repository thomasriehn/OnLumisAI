"use client";
import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Logo } from "./Logo";
import { Arrow, Lock } from "./BrandIcons";
const links = [
  ["Produkt", "/produkt"],
  ["Anwendungsfälle", "/anwendungsfaelle"],
  ["Vorteile", "/vorteile"],
];
export function Header() {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();
  return (
    <header className="site-header">
      <div className="shell header-inner">
        <Logo />
        <nav className="desktop-nav" aria-label="Hauptnavigation">
          {links.map(([t, h]) => (
            <Link
              key={h}
              href={h}
              aria-current={pathname === h ? "page" : undefined}
            >
              {t}
            </Link>
          ))}
        </nav>
        <div className="header-actions">
          <Link href="/demo" className="studio-link">
            <Lock />
            Demo-Studio
          </Link>
          <Link href="/kontakt" className="btn btn-dark btn-small">
            Kontakt <Arrow />
          </Link>
        </div>
        <button
          className="menu-toggle"
          aria-label={open ? "Menü schließen" : "Menü öffnen"}
          aria-expanded={open}
          aria-controls="mobile-menu"
          onClick={() => setOpen(!open)}
        >
          {open ? "✕" : "☰"}
        </button>
      </div>
      {open && (
        <nav
          id="mobile-menu"
          className="mobile-nav"
          aria-label="Mobile Hauptnavigation"
        >
          {[...links, ["Demo-Studio", "/demo"], ["Kontakt", "/kontakt"]].map(
            ([t, h]) => (
              <Link key={h} href={h} onClick={() => setOpen(false)}>
                {t}
                <Arrow />
              </Link>
            ),
          )}
        </nav>
      )}
    </header>
  );
}
