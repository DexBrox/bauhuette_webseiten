import { integer, pgTable, text, timestamp } from "drizzle-orm/pg-core";

/** Example table. The Baumeister replaces it with the real data model in phase 3. */
export const messages = pgTable("messages", {
  id: integer("id").primaryKey().generatedAlwaysAsIdentity(),
  name: text("name").notNull(),
  email: text("email").notNull(),
  message: text("message").notNull(),
  receivedAt: timestamp("received_at", { withTimezone: true }).notNull().defaultNow(),
});
