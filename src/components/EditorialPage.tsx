import Link from "next/link";
import { PageHero } from "./PageHero";
import { Arrow } from "./BrandIcons";
export function EditorialPage({
  eyebrow,
  title,
  intro,
  sections,
  children,
}: {
  eyebrow: string;
  title: string;
  intro: string;
  sections: { title: string; text: string; detail?: string }[];
  children?: React.ReactNode;
}) {
  return (
    <>
      <PageHero eyebrow={eyebrow} title={title} description={intro} />
      <div className="shell editorial-page">
        {sections.map((s, i) => (
          <section key={s.title} className="editorial-row">
            <span>0{i + 1}</span>
            <h2>{s.title}</h2>
            <div>
              <p>{s.text}</p>
              {s.detail && <p className="editorial-detail">{s.detail}</p>}
            </div>
          </section>
        ))}
        {children}
        <div className="editorial-cta">
          <div>
            <p className="eyebrow">IHR ANWENDUNGSFALL ZÄHLT.</p>
            <h2>
              Was möchten Sie
              <br />
              Ihr Unternehmen fragen?
            </h2>
          </div>
          <Link href="/kontakt" className="btn btn-dark">
            Gemeinsam herausfinden <Arrow />
          </Link>
        </div>
      </div>
    </>
  );
}
