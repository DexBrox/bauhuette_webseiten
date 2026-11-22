import { ContactRequestSchema, type ContactResponse } from "@bauhuette/shared";
import { Hono } from "hono";
import { cors } from "hono/cors";
import type { Database } from "./db/connection";
import { messages } from "./db/schema";

export type AppEnv = {
  Bindings: { DATABASE_URL: string; ALLOWED_ORIGIN: string };
  Variables: { db: Database };
};

/**
 * Builds the app. The database is passed in: Neon in the worker, PGlite in tests.
 * That keeps the logic testable without a server.
 */
export function createApp(getDatabase: (env: AppEnv["Bindings"]) => Database) {
  const app = new Hono<AppEnv>().basePath("/api");

  app.use("*", async (c, next) => {
    const origin = c.env?.ALLOWED_ORIGIN ?? "http://localhost:4321";
    return cors({ origin, allowMethods: ["GET", "POST"] })(c, next);
  });

  app.use("*", async (c, next) => {
    c.set("db", getDatabase(c.env));
    await next();
  });

  app.get("/health", (c) => c.json({ ok: true }));

  app.post("/contact", async (c) => {
    const body = await c.req.json().catch(() => null);
    const request = ContactRequestSchema.safeParse(body);
    if (!request.success) {
      return c.json({ ok: false, fields: request.error.issues.map((i) => i.path.join(".")) }, 400);
    }
    const { name, email, message } = request.data;
    const [row] = await c.var.db
      .insert(messages)
      .values({ name, email, message })
      .returning({ id: messages.id });
    if (!row) {
      return c.json({ ok: false, fields: [] }, 500);
    }
    const response: ContactResponse = { ok: true, id: row.id };
    return c.json(response, 201);
  });

  return app;
}
