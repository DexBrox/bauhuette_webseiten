import { z } from "zod";

/** One section of a page, as the editor (Redaktion) will later edit it. */
export const SectionSchema = z.object({
  id: z.string().regex(/^[a-z0-9-]+$/, "nur Kleinbuchstaben, Ziffern und Bindestriche"),
  heading: z.string().min(1).max(120),
  text: z.string().min(1),
  image: z
    .object({
      src: z.string().min(1),
      alt: z.string().min(1, "Bildbeschreibung fehlt (Barrierefreiheit)"),
    })
    .optional(),
});

/** Content of a page: stored as JSON in apps/web/src/content/ and validated at build time. */
export const PageSchema = z.object({
  title: z.string().min(1).max(70),
  description: z.string().min(1).max(160),
  sections: z.array(SectionSchema).min(1),
});

export type Section = z.infer<typeof SectionSchema>;
export type Page = z.infer<typeof PageSchema>;

/** Parses and validates page content. Throws a readable (German) message so the build says what is missing. */
export function parsePage(data: unknown, source: string): Page {
  const result = PageSchema.safeParse(data);
  if (!result.success) {
    const problems = result.error.issues
      .map((i) => `${i.path.join(".") || "(Wurzel)"}: ${i.message}`)
      .join("; ");
    throw new Error(`Inhalt ${source} ist ungültig: ${problems}`);
  }
  return result.data;
}
