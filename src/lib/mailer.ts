import nodemailer from "nodemailer";
import type { ContactFormValues } from "@/lib/validation";

function getTransport() {
  const host = process.env.SMTP_HOST || "localhost";
  const port = Number(process.env.SMTP_PORT || 25);
  const secure = process.env.SMTP_SECURE === "true";
  const user = process.env.SMTP_USER;
  const pass = process.env.SMTP_PASS;

  return nodemailer.createTransport({
    host,
    port,
    secure,
    auth: user && pass ? { user, pass } : undefined,
  });
}

function escapeHtml(value: string) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

export async function sendContactMail(data: ContactFormValues) {
  const mailFrom = process.env.MAIL_FROM || "OnLumis Website <no-reply@onlumis.ai>";
  const mailTo = process.env.MAIL_TO || "info@onlumis.ai";

  const transport = getTransport();

  const text = [
    `Neue Kontaktanfrage über onlumis.ai`,
    ``,
    `Name: ${data.name}`,
    `Unternehmen: ${data.company}`,
    `E-Mail: ${data.email}`,
    data.phone ? `Telefon: ${data.phone}` : null,
    data.companySize ? `Unternehmensgröße: ${data.companySize}` : null,
    ``,
    `Nachricht:`,
    data.message,
  ]
    .filter((line) => line !== null)
    .join("\n");

  const html = `
    <h2>Neue Kontaktanfrage über onlumis.ai</h2>
    <p><strong>Name:</strong> ${escapeHtml(data.name)}</p>
    <p><strong>Unternehmen:</strong> ${escapeHtml(data.company)}</p>
    <p><strong>E-Mail:</strong> ${escapeHtml(data.email)}</p>
    ${data.phone ? `<p><strong>Telefon:</strong> ${escapeHtml(data.phone)}</p>` : ""}
    ${data.companySize ? `<p><strong>Unternehmensgröße:</strong> ${escapeHtml(data.companySize)}</p>` : ""}
    <p><strong>Nachricht:</strong></p>
    <p>${escapeHtml(data.message).replace(/\n/g, "<br />")}</p>
  `;

  await transport.sendMail({
    from: mailFrom,
    to: mailTo,
    replyTo: `${data.name} <${data.email}>`,
    subject: `Neue Kontaktanfrage: ${data.company}`,
    text,
    html,
  });
}
