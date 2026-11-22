import { z } from "zod";

/** Example API contract (profile fullstack): contact form. */
export const ContactRequestSchema = z.object({
  name: z.string().trim().min(2).max(100),
  email: z.email(),
  message: z.string().trim().min(10).max(5000),
  /** Honeypot against spam: must stay empty. */
  website: z.string().max(0).optional(),
});

export const ContactResponseSchema = z.object({
  ok: z.literal(true),
  id: z.number().int().positive(),
});

export type ContactRequest = z.infer<typeof ContactRequestSchema>;
export type ContactResponse = z.infer<typeof ContactResponseSchema>;
