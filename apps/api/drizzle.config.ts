import { defineConfig } from "drizzle-kit";

// Migrationen erzeugen: pnpm --filter api exec drizzle-kit generate
// Anwenden auf Neon:    DATABASE_URL=... pnpm --filter api exec drizzle-kit migrate
export default defineConfig({
  schema: "./src/db/schema.ts",
  out: "./drizzle",
  dialect: "postgresql",
  dbCredentials: { url: process.env.DATABASE_URL ?? "" },
});
