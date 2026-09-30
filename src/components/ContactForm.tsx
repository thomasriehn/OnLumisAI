"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { companySizeOptions } from "@/lib/validation";

type Status = "idle" | "loading" | "success" | "error";

export function ContactForm() {
  const [status, setStatus] = useState<Status>("idle");
  const [errorMessage, setErrorMessage] = useState<string>("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus("loading");
    setErrorMessage("");

    const form = event.currentTarget;
    const formData = new FormData(form);

    const payload = {
      name: String(formData.get("name") || ""),
      company: String(formData.get("company") || ""),
      email: String(formData.get("email") || ""),
      phone: String(formData.get("phone") || ""),
      companySize: String(formData.get("companySize") || ""),
      message: String(formData.get("message") || ""),
      consent: formData.get("consent") === "on",
      website: String(formData.get("website") || ""),
    };

    try {
      const response = await fetch("/api/kontakt", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();

      if (!response.ok || !data.ok) {
        setStatus("error");
        setErrorMessage(
          data.message ||
            "Es ist ein Fehler aufgetreten. Bitte versuchen Sie es erneut.",
        );
        return;
      }

      setStatus("success");
      form.reset();
    } catch {
      setStatus("error");
      setErrorMessage(
        "Es ist ein Fehler aufgetreten. Bitte versuchen Sie es erneut.",
      );
    }
  }

  if (status === "success") {
    return (
      <div
        role="status"
        className="rounded-2xl border border-accent-strong/30 bg-accent-strong/5 p-8 text-center"
      >
        <h3 className="font-display text-lg font-semibold text-ink dark:text-white">
          Vielen Dank für Ihre Nachricht!
        </h3>
        <p className="mt-2 text-sm text-muted">
          Wir haben Ihre Anfrage erhalten und melden uns in der Regel innerhalb
          von 1–2 Werktagen bei Ihnen.
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} noValidate className="space-y-5">
      <div className="grid gap-5 sm:grid-cols-2">
        <div>
          <label
            htmlFor="name"
            className="text-sm font-medium text-ink dark:text-white"
          >
            Name *
          </label>
          <input
            id="name"
            name="name"
            type="text"
            required
            minLength={2}
            autoComplete="name"
            className="mt-1.5 w-full rounded-lg border border-border bg-surface px-3.5 py-2.5 text-sm text-ink outline-none focus:border-accent-strong focus:ring-1 focus:ring-accent-strong dark:text-white"
          />
        </div>
        <div>
          <label
            htmlFor="company"
            className="text-sm font-medium text-ink dark:text-white"
          >
            Unternehmen *
          </label>
          <input
            id="company"
            name="company"
            type="text"
            required
            minLength={2}
            autoComplete="organization"
            className="mt-1.5 w-full rounded-lg border border-border bg-surface px-3.5 py-2.5 text-sm text-ink outline-none focus:border-accent-strong focus:ring-1 focus:ring-accent-strong dark:text-white"
          />
        </div>
      </div>

      <div className="grid gap-5 sm:grid-cols-2">
        <div>
          <label
            htmlFor="email"
            className="text-sm font-medium text-ink dark:text-white"
          >
            E-Mail-Adresse *
          </label>
          <input
            id="email"
            name="email"
            type="email"
            required
            autoComplete="email"
            className="mt-1.5 w-full rounded-lg border border-border bg-surface px-3.5 py-2.5 text-sm text-ink outline-none focus:border-accent-strong focus:ring-1 focus:ring-accent-strong dark:text-white"
          />
        </div>
        <div>
          <label
            htmlFor="phone"
            className="text-sm font-medium text-ink dark:text-white"
          >
            Telefon (optional)
          </label>
          <input
            id="phone"
            name="phone"
            type="tel"
            autoComplete="tel"
            className="mt-1.5 w-full rounded-lg border border-border bg-surface px-3.5 py-2.5 text-sm text-ink outline-none focus:border-accent-strong focus:ring-1 focus:ring-accent-strong dark:text-white"
          />
        </div>
      </div>

      <div>
        <label
          htmlFor="companySize"
          className="text-sm font-medium text-ink dark:text-white"
        >
          Unternehmensgröße (optional)
        </label>
        <select
          id="companySize"
          name="companySize"
          defaultValue=""
          className="mt-1.5 w-full rounded-lg border border-border bg-surface px-3.5 py-2.5 text-sm text-ink outline-none focus:border-accent-strong focus:ring-1 focus:ring-accent-strong dark:text-white"
        >
          <option value="">Bitte wählen</option>
          {companySizeOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label
          htmlFor="message"
          className="text-sm font-medium text-ink dark:text-white"
        >
          Ihre Nachricht *
        </label>
        <textarea
          id="message"
          name="message"
          required
          minLength={10}
          rows={5}
          placeholder="Erzählen Sie uns kurz von Ihrem Vorhaben – z. B. welche Wissensquellen Sie einbinden möchten oder welche Herausforderungen Sie lösen wollen."
          className="mt-1.5 w-full rounded-lg border border-border bg-surface px-3.5 py-2.5 text-sm text-ink outline-none focus:border-accent-strong focus:ring-1 focus:ring-accent-strong dark:text-white"
        />
      </div>

      {/* Honeypot: hidden from real users, catches simple bots. */}
      <div className="absolute left-[-9999px] top-auto" aria-hidden="true">
        <label htmlFor="website">Website</label>
        <input
          id="website"
          name="website"
          type="text"
          tabIndex={-1}
          autoComplete="off"
        />
      </div>

      <div className="flex items-start gap-3">
        <input
          id="consent"
          name="consent"
          type="checkbox"
          required
          className="mt-1 h-4 w-4 shrink-0 rounded border-border text-accent-strong focus:ring-accent-strong"
        />
        <label htmlFor="consent" className="text-sm text-muted">
          Ich stimme zu, dass meine Angaben aus dem Kontaktformular zur
          Bearbeitung meiner Anfrage gespeichert und verarbeitet werden. Weitere
          Informationen finden Sie in unserer{" "}
          <Link
            href="/datenschutz"
            className="text-accent-strong underline underline-offset-2"
          >
            Datenschutzerklärung
          </Link>
          . *
        </label>
      </div>

      {status === "error" && (
        <p
          role="alert"
          className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700 dark:bg-red-950/40 dark:text-red-300"
        >
          {errorMessage}
        </p>
      )}

      <button
        type="submit"
        disabled={status === "loading"}
        className="inline-flex w-full items-center justify-center gap-2 rounded-full bg-accent-strong px-6 py-3 text-sm font-semibold text-white transition-colors hover:bg-accent disabled:cursor-not-allowed disabled:opacity-60 sm:w-auto"
      >
        {status === "loading" ? "Wird gesendet…" : "Nachricht absenden"}
      </button>
      <p className="text-xs text-muted">* Pflichtfeld</p>
    </form>
  );
}
