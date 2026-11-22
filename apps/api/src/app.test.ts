import { PGlite } from "@electric-sql/pglite";
import { drizzle } from "drizzle-orm/pglite";
import { beforeAll, describe, expect, it } from "vitest";
import { createApp } from "./app";
import type { Database } from "./db/connection";
import * as schema from "./db/schema";

// Real Postgres in memory: same SQL dialect as Neon, no server, no Docker.
const pg = new PGlite();
const db = drizzle(pg, { schema }) as unknown as Database;
const app = createApp(() => db);
const env = { DATABASE_URL: "", ALLOWED_ORIGIN: "http://localhost:4321" };

const post = (body: unknown) =>
  app.request(
    "/api/contact",
    { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) },
    env,
  );

beforeAll(async () => {
  await pg.exec(`create table messages (
    id integer generated always as identity primary key,
    name text not null, email text not null, message text not null,
    received_at timestamptz not null default now())`);
});

describe("API", () => {
  it("meldet Gesundheit", async () => {
    const res = await app.request("/api/health", {}, env);
    expect(res.status).toBe(200);
    expect(await res.json()).toEqual({ ok: true });
  });

  it("speichert eine gültige Kontaktanfrage", async () => {
    const res = await post({
      name: "Vale",
      email: "vale@example.org",
      message: "Hallo, ich habe eine Frage.",
    });
    expect(res.status).toBe(201);
    expect(((await res.json()) as { ok: boolean }).ok).toBe(true);
    const rows = await pg.query("select count(*)::int as n from messages");
    expect(rows.rows[0]).toEqual({ n: 1 });
  });

  it("lehnt ungültige Anfragen mit 400 ab", async () => {
    const res = await post({ name: "V" });
    expect(res.status).toBe(400);
  });
});
