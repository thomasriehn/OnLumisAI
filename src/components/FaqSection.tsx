import Script from "next/script";
import { SectionHeading } from "@/components/SectionHeading";

export type FaqItem = {
  question: string;
  answer: string;
};

export function FaqSection({
  items,
  title = "Häufig gestellte Fragen",
  eyebrow = "FAQ",
  id = "faq",
}: {
  items: FaqItem[];
  title?: string;
  eyebrow?: string;
  id?: string;
}) {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: items.map((item) => ({
      "@type": "Question",
      name: item.question,
      acceptedAnswer: {
        "@type": "Answer",
        text: item.answer,
      },
    })),
  };

  return (
    <section id={id} className="py-20 sm:py-28">
      <div className="mx-auto w-full max-w-3xl px-6 lg:px-8">
        <SectionHeading eyebrow={eyebrow} title={title} />
        <dl className="mt-10 space-y-3">
          {items.map((item) => (
            <details
              key={item.question}
              className="group rounded-xl border border-border bg-surface p-5 open:shadow-sm"
            >
              <summary className="flex cursor-pointer list-none items-center justify-between gap-4 font-medium text-ink marker:content-none dark:text-white">
                <span>{item.question}</span>
                <span
                  className="shrink-0 text-accent-strong transition-transform group-open:rotate-45"
                  aria-hidden="true"
                >
                  +
                </span>
              </summary>
              <p className="mt-3 text-sm leading-relaxed text-muted">
                {item.answer}
              </p>
            </details>
          ))}
        </dl>
      </div>
      <Script
        id={`ld-faq-${id}`}
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
    </section>
  );
}
