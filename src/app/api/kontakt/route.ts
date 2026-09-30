import { NextRequest, NextResponse } from "next/server";
import { contactFormSchema } from "@/lib/validation";
import { sendContactMail } from "@/lib/mailer";
import { isRateLimited } from "@/lib/rateLimit";

export const dynamic = "force-dynamic";

export async function POST(request: NextRequest) {
  const ip =
    request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || "unknown";

  if (isRateLimited(ip)) {
    return NextResponse.json(
      {
        ok: false,
        message: "Zu viele Anfragen. Bitte versuchen Sie es später erneut.",
      },
      { status: 429 },
    );
  }

  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json(
      { ok: false, message: "Ungültige Anfrage." },
      { status: 400 },
    );
  }

  const parsed = contactFormSchema.safeParse(body);
  if (!parsed.success) {
    const firstIssue = parsed.error.issues[0];
    return NextResponse.json(
      {
        ok: false,
        message: firstIssue?.message || "Bitte überprüfen Sie Ihre Eingaben.",
      },
      { status: 400 },
    );
  }

  if (parsed.data.website) {
    // Honeypot field filled in -> treat as spam, but report success to not tip off bots.
    return NextResponse.json({ ok: true });
  }

  try {
    await sendContactMail(parsed.data);
  } catch (error) {
    console.error("Kontaktformular: Versand fehlgeschlagen", error);
    return NextResponse.json(
      {
        ok: false,
        message:
          "Ihre Nachricht konnte nicht versendet werden. Bitte versuchen Sie es später erneut oder schreiben Sie uns direkt per E-Mail.",
      },
      { status: 502 },
    );
  }

  return NextResponse.json({ ok: true });
}
