import { neon } from "@neondatabase/serverless";
import { drizzle } from "drizzle-orm/neon-http";
import type { PgDatabase, PgQueryResultHKT } from "drizzle-orm/pg-core";
import * as schema from "./schema";

/** Common type for Neon (worker) and PGlite (tests). */
export type Database = PgDatabase<PgQueryResultHKT, typeof schema>;

export function connectNeon(url: string): Database {
  return drizzle(neon(url), { schema }) as unknown as Database;
}
