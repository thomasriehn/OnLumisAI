import Link from "next/link";

const TABS = [
  { key: "chat", href: "/", label: "Chat" },
  { key: "suche", href: "/suche", label: "Suche" },
  { key: "admin", href: "/admin", label: "Verwaltung" },
] as const;

export function TopBar({ active }: { active: (typeof TABS)[number]["key"] }) {
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
      </nav>
    </header>
  );
}
