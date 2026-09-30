import Link from "next/link";
import { ReactNode } from "react";

type Variant = "primary" | "secondary" | "ghost";

const variantClasses: Record<Variant, string> = {
  primary:
    "bg-accent-strong text-[#05251b] hover:bg-accent shadow-sm shadow-accent-strong/20",
  secondary: "bg-primary text-white hover:bg-primary-soft",
  ghost:
    "border border-border text-ink hover:border-accent-strong hover:text-accent-strong dark:text-white",
};

export function CtaButton({
  href,
  children,
  variant = "primary",
  className = "",
}: {
  href: string;
  children: ReactNode;
  variant?: Variant;
  className?: string;
}) {
  return (
    <Link
      href={href}
      className={`inline-flex items-center justify-center gap-2 rounded-full px-6 py-3 text-sm font-semibold transition-colors duration-150 ${variantClasses[variant]} ${className}`}
    >
      {children}
    </Link>
  );
}
