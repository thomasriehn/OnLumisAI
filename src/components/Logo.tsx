import Link from "next/link";
export function Logo({ className = "" }: { className?: string }) {
  return (
    <Link
      href="/"
      className={`brand ${className}`}
      aria-label="OnLumisAI – Startseite"
    >
      <span className="brand-symbol" aria-hidden="true" />
      <span>
        OnLumis<span className="brand-ai">AI</span>
      </span>
    </Link>
  );
}
