import { ReactNode } from "react";
export function PageHero({
  eyebrow,
  title,
  description,
  children,
}: {
  eyebrow: string;
  title: string;
  description: string;
  children?: ReactNode;
}) {
  return (
    <section className="inner-hero">
      <div className="shell">
        <p className="eyebrow">ONLUMISAI / {eyebrow.toLocaleUpperCase("de")}</p>
        <h1>{title}</h1>
        <p className="inner-hero-lead">{description}</p>
        {children && <div className="button-row">{children}</div>}
        <span className="inner-hero-orbit" aria-hidden="true" />
      </div>
    </section>
  );
}
