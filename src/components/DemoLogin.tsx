/* eslint-disable @next/next/no-location-assign-relative-destination -- Full navigation clears authenticated router state after login/logout. */
"use client";
import { FormEvent, useState } from "react";
import { Arrow } from "./BrandIcons";
export function DemoLogin() {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    setBusy(true);
    const form = e.currentTarget;
    try {
      const response = await fetch("/api/demo/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password: new FormData(form).get("password") }),
      });
      const body = await response.json();
      if (!response.ok) {
        setError(body.message);
        setBusy(false);
        return;
      }
      form.reset();
      window.location.assign("/demo/bibliothek");
    } catch {
      setError(
        "Die Verbindung ist fehlgeschlagen. Bitte versuchen Sie es erneut.",
      );
      setBusy(false);
    }
  }
  return (
    <form onSubmit={submit}>
      <label htmlFor="demo-password">Passwort</label>
      <input
        id="demo-password"
        name="password"
        type="password"
        autoComplete="current-password"
        required
        maxLength={256}
        aria-describedby={error ? "login-error" : undefined}
      />
      {error && (
        <p id="login-error" role="alert" className="form-error">
          {error}
        </p>
      )}
      <button className="btn btn-dark" disabled={busy}>
        {busy ? "Wird geöffnet …" : "Studio öffnen"}
        <Arrow />
      </button>
      <p className="login-session">
        Ihr Zugang bleibt bis zu acht Stunden aktiv.
      </p>
    </form>
  );
}
