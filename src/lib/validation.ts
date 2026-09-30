import { z } from "zod";

export const companySizeOptions = [
  { value: "1-9", label: "1–9 Mitarbeitende" },
  { value: "10-49", label: "10–49 Mitarbeitende" },
  { value: "50-249", label: "50–249 Mitarbeitende" },
  { value: "250+", label: "250+ Mitarbeitende" },
] as const;

export const contactFormSchema = z.object({
  name: z.string().trim().min(2, "Bitte geben Sie Ihren Namen an.").max(120),
  company: z
    .string()
    .trim()
    .min(2, "Bitte geben Sie Ihr Unternehmen an.")
    .max(160),
  email: z
    .string()
    .trim()
    .email("Bitte geben Sie eine gültige E-Mail-Adresse an.")
    .max(200),
  phone: z.string().trim().max(40).optional().or(z.literal("")),
  companySize: z
    .enum(["1-9", "10-49", "50-249", "250+"])
    .optional()
    .or(z.literal("")),
  message: z
    .string()
    .trim()
    .min(10, "Bitte beschreiben Sie Ihr Anliegen etwas ausführlicher.")
    .max(5000),
  consent: z.literal(true, {
    message: "Bitte stimmen Sie der Verarbeitung Ihrer Daten zu.",
  }),
  // Honeypot field: left empty by real users, deliberately unvalidated here so a
  // filled-in value still parses successfully and can be handled as spam by the caller.
  website: z.string().optional().or(z.literal("")),
});

export type ContactFormValues = z.infer<typeof contactFormSchema>;
