import Link from "next/link";

export function Logo({ className = "" }: { className?: string }) {
  return (
    <Link
      href="/"
      className={`inline-flex items-center gap-2.5 font-display text-lg font-semibold tracking-tight text-ink dark:text-white ${className}`}
      aria-label="OnLumis – Startseite"
    >
      <span
        className="relative flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary"
        aria-hidden="true"
      >
        <span className="absolute inset-[3px] rounded-full border border-accent/70" />
        <span className="h-2 w-2 rounded-full bg-accent" />
      </span>
      <span>
        On<span className="text-accent-strong">Lumis</span>
      </span>
    </Link>
  );
}
