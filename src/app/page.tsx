import type { Metadata } from "next";
import Link from "next/link";
import { KnowledgeVisual } from "@/components/KnowledgeVisual";
import { UseCases } from "@/components/UseCases";
import { ProductVideo } from "@/components/ProductVideo";
import { Reveal } from "@/components/Reveal";
import { Arrow, Lock, Check } from "@/components/BrandIcons";
export const metadata: Metadata = {
  title: "OnLumisAI – Ihr Wissen. Ihre Infrastruktur. Ihre KI.",
  description:
    "Machen Sie Ihr Unternehmenswissen nutzbar. OnLumisAI verbindet Dokumente, Suche und KI auf Ihrer Infrastruktur – mit Quellen und kontrolliertem Zugriff.",
  alternates: { canonical: "/" },
};
export default function Home() {
  return (
    <>
      <section className="hero shell">
        <div className="hero-copy">
          <div className="eyebrow">
            <span className="live-dot" /> UNTERNEHMENSWISSEN. IN IHRER HAND.
          </div>
          <h1>
            Ihre Firma weiß viel.
            <br />
            Machen Sie es
            <br />
            <em>ansprechbar.</em>
          </h1>
          <p className="hero-lead">
            Die Antwort steckt in Ihren Dokumenten. OnLumisAI bringt sie ins
            Gespräch – mit Quellen, im richtigen Kontext und auf Ihrer
            Infrastruktur.
          </p>
          <div className="button-row">
            <Link href="/kontakt" className="btn btn-dark">
              OnLumis kennenlernen <Arrow />
            </Link>
            <a href="#erleben" className="text-link">
              <span className="play-small">▶</span> In Aktion ansehen
            </a>
          </div>
          <div className="hero-proof">
            <span>
              <Check /> Lokal betreibbar
            </span>
            <span>
              <Check /> Quellen im Blick
            </span>
            <span>
              <Check /> Zugriff nach Berechtigung
            </span>
          </div>
        </div>
        <KnowledgeVisual />
        <div className="hero-foot">
          <span>ENTWICKELT VON JULITH GMBH</span>
          <span>Für den Mittelstand. Für den Arbeitsalltag.</span>
          <a href="#wissen">
            WEITER ENTDECKEN <span>↓</span>
          </a>
        </div>
      </section>
      <section id="wissen" className="section shell">
        <Reveal>
          <div className="section-heading split-heading">
            <div>
              <p className="eyebrow">01 / WISSEN, DAS WEITERHILFT</p>
              <h2>
                Weniger suchen.
                <br />
                <span className="muted-heading">
                  Mehr wissen, was zu tun ist.
                </span>
              </h2>
            </div>
            <p>
              Handbücher im Dateiserver. Verträge in SharePoint. Erfahrungen im
              Servicebericht. OnLumis verbindet diese Perspektiven zu Antworten,
              mit denen Ihre Teams arbeiten können.
            </p>
          </div>
        </Reveal>
        <Reveal>
          <div className="value-grid">
            {[
              [
                "Eine Frage.",
                "Ihre Wissensquellen.",
                "Stellen Sie Fragen in Ihrer Sprache. Das System sucht in den freigegebenen Inhalten Ihres Unternehmens.",
              ],
              [
                "Antworten.",
                "Mit Fundstelle.",
                "Öffnen Sie die verwendeten Quellen. So können Sie Aussagen nachvollziehen und fachlich prüfen.",
              ],
              [
                "Ihre Infrastruktur.",
                "Ihre Entscheidung.",
                "Betreiben Sie die KI vor Ort oder in einer vereinbarten Private Cloud. Sie bestimmen Datenhaltung und Zugriff.",
              ],
            ].map(([a, b, c], i) => (
              <div key={a}>
                <span className="value-number">0{i + 1}</span>
                <h3>
                  {a}
                  <br />
                  {b}
                </h3>
                <p>{c}</p>
              </div>
            ))}
          </div>
        </Reveal>
      </section>
      <section id="erleben" className="demo-section">
        <div className="shell">
          <Reveal>
            <div className="section-heading split-heading">
              <div>
                <p className="eyebrow">02 / NICHT NUR ERKLÄREN. ZEIGEN.</p>
                <h2>
                  Ein Fehlercode.
                  <br />
                  Ein guter nächster Schritt.
                </h2>
              </div>
              <p>
                Begleiten Sie einen Servicetechniker: vom Fehlerbild über
                passende Dokumente bis zum Bericht. Eine echte Aufnahme mit
                fiktiven Unternehmensdaten.
              </p>
            </div>
          </Reveal>
          <ProductVideo />
          <div className="demo-caption">
            <span>
              <span className="live-dot" /> Originalaufnahme · Mit Sprecherin
              erklärt
            </span>
            <span>
              Fiktive Demodaten ·{" "}
              <a
                href="/media/service-transkript.txt"
                target="_blank"
                rel="noopener"
              >
                Sprechertext lesen ↗
              </a>
            </span>
          </div>
        </div>
      </section>
      <section className="section shell">
        <Reveal>
          <div className="section-heading">
            <p className="eyebrow">03 / NAH AN IHRER ARBEIT</p>
            <h2>
              Gutes Wissen kennt
              <br />
              <span className="muted-heading">keine Abteilungsgrenzen.</span>
            </h2>
          </div>
        </Reveal>
        <UseCases />
      </section>
      <section className="architecture-section" id="architektur">
        <div className="shell">
          <Reveal>
            <div className="section-heading split-heading">
              <div>
                <p className="eyebrow">04 / DIE INTELLIGENZ DAHINTER</p>
                <h2>
                  Eine klare Verbindung.
                  <br />
                  <span>Von der Quelle zur Antwort.</span>
                </h2>
              </div>
              <p>
                OnLumis verbindet die Suche in Ihren Daten mit einem
                Sprachmodell. Berechtigungen und relevante Fundstellen
                bestimmen, welches Wissen in die Antwort einfließt.
              </p>
            </div>
          </Reveal>
          <Reveal>
            <div className="architecture-flow">
              {[
                [
                  "Ihr Wissen",
                  "Dokumente, Dateiserver, SharePoint und strukturierte Exporte.",
                ],
                [
                  "Die passende Fundstelle",
                  "Aufbereitung, Suche und Auswahl relevanter Textabschnitte.",
                ],
                [
                  "Ihre Antwort",
                  "Eine verständliche Antwort aus dem ausgewählten Kontext.",
                ],
                [
                  "Der nachvollziehbare Beleg",
                  "Quellen öffnen, Aussagen prüfen und im Dialog vertiefen.",
                ],
              ].map(([t, d], i) => (
                <div className="flow-step" key={t}>
                  <span className="flow-index">0{i + 1}</span>
                  <h3>{t}</h3>
                  <p>{d}</p>
                  <span className="flow-arrow" aria-hidden="true">
                    →
                  </span>
                </div>
              ))}
            </div>
          </Reveal>
          <div className="architecture-bottom">
            <span>
              <Lock /> Innerhalb Ihrer gewählten Betriebsumgebung
            </span>
            <Link href="/produkt">
              Die Architektur kennenlernen <Arrow />
            </Link>
          </div>
        </div>
      </section>
      <section className="section shell control-section">
        <Reveal>
          <div>
            <p className="eyebrow">05 / SOUVERÄN BLEIBEN</p>
            <h2>
              KI im Unternehmen.
              <br />
              <span className="muted-heading">Unter Ihrer Kontrolle.</span>
            </h2>
            <p className="section-lead">
              Eine gute KI-Lösung passt zu Ihrer IT. Und zu dem Vertrauen, das
              Ihre Kunden in Sie setzen.
            </p>
            <Link href="/vorteile" className="text-link">
              Was das für Sie bedeutet <Arrow />
            </Link>
          </div>
        </Reveal>
        <div className="control-list">
          {[
            [
              "Betrieb, den Sie bestimmen",
              "On-Premise oder Private Cloud: Infrastruktur und Modell werden passend zu Ihrem Vorhaben ausgewählt.",
            ],
            [
              "Wissen, das Sie freigeben",
              "Nutzer- und Gruppenrechte begrenzen den Zugriff auf Quellen und Dokumente.",
            ],
            [
              "Ein Partner, der bleibt",
              "JULITH begleitet Analyse, Pilot, Einführung und Betrieb – mit persönlichen Ansprechpartnern.",
            ],
          ].map(([t, p], i) => (
            <Reveal key={t}>
              <div>
                <span>0{i + 1}</span>
                <section>
                  <h3>{t}</h3>
                  <p>{p}</p>
                </section>
                <Check />
              </div>
            </Reveal>
          ))}
        </div>
      </section>
      <section className="library-teaser shell">
        <div className="library-count" aria-hidden="true">
          27<span>WALKTHROUGHS</span>
        </div>
        <div>
          <p className="eyebrow">DAS DEMO-STUDIO</p>
          <h2>
            Sehen. Nachfragen.
            <br />
            Selbst einordnen.
          </h2>
          <p>
            Alle Walkthroughs, die drei Playbooks und die Originalfragen –
            gesammelt im geschützten Bereich. Auch mit den Grenzen, die in den
            Aufnahmen sichtbar werden.
          </p>
          <Link href="/demo" className="btn btn-dark">
            <Lock /> Demo-Studio öffnen <Arrow />
          </Link>
        </div>
        <div className="library-stripes" aria-hidden="true">
          <span>
            V1 <b>Grundlagen</b>
          </span>
          <span>
            V2 <b>Vertiefung</b>
          </span>
          <span>
            V3 <b>Enterprise</b>
          </span>
        </div>
      </section>
      <section className="section shell journey">
        <Reveal>
          <div className="section-heading split-heading">
            <div>
              <p className="eyebrow">06 / KLEIN STARTEN. GEZIELT WACHSEN.</p>
              <h2>
                Ihr Wissen ist schon da.
                <br />
                <span className="muted-heading">
                  Der nächste Schritt ist ein Gespräch.
                </span>
              </h2>
            </div>
            <Link href="/kontakt" className="btn btn-dark">
              Pilotprojekt besprechen <Arrow />
            </Link>
          </div>
        </Reveal>
        <div className="journey-steps">
          {[
            [
              "Verstehen",
              "Wir wählen einen konkreten Anwendungsfall und die passenden Wissensquellen.",
            ],
            [
              "Erproben",
              "Ihr Team prüft Antworten, Quellen und Berechtigungen in einem abgegrenzten Pilot.",
            ],
            [
              "Einführen",
              "Nach der gemeinsamen Bewertung erweitern wir Datenbasis, Integrationen und Nutzerkreis.",
            ],
          ].map(([t, p], i) => (
            <div key={t}>
              <span>0{i + 1}</span>
              <h3>{t}</h3>
              <p>{p}</p>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}
