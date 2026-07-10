"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

const TABS = [
  { key: "chat", href: "/", label: "Chat" },
  { key: "suche", href: "/suche", label: "Suche" },
  { key: "admin", href: "/admin", label: "Verwaltung" },
] as const;

type Session = { authenticated: boolean; mode: "dev" | "oidc"; username?: string };

export function TopBar({ active }: { active: (typeof TABS)[number]["key"] }) {
  const [session, setSession] = useState<Session | null>(null);

  useEffect(() => {
    fetch("/bff/auth/me")
      .then((r) => r.json())
      .then(setSession)
      .catch(() => setSession(null));
  }, []);

  return (
    <header className="topbar">
      <div className="logo-dot" aria-hidden />
      <strong>OnLumis</strong>
      <nav className="tabs">
        {TABS.map((tab) => (
          <Link
            key={tab.key}
            href={tab.href}
            className={tab.key === active ? "tab active" : "tab"}
          >
            {tab.label}
          </Link>
        ))}
        {session?.authenticated ? (
          <span className="session">
            {session.username}
            {session.mode === "oidc" && (
              <a className="tab" href="/bff/auth/logout">
                Abmelden
              </a>
            )}
          </span>
        ) : session ? (
          <a className="tab active" href="/bff/auth/login" data-testid="login">
            Anmelden
          </a>
        ) : null}
      </nav>
    </header>
  );
}
