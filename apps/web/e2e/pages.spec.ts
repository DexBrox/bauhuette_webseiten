import { existsSync } from "node:fs";
import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

// Jede neue Seite hier eintragen. Der Tester-Agent hält die Liste aktuell.
const PAGES = ["/", "/impressum/", "/datenschutz/"];

for (const path of PAGES) {
  test.describe(`Seite ${path}`, () => {
    test("lädt mit genau einer Hauptüberschrift", async ({ page }) => {
      const antwort = await page.goto(path);
      expect(antwort?.status()).toBe(200);
      await expect(page.locator("h1")).toHaveCount(1);
      await expect(page).toHaveTitle(/.+/);
    });

    test("ist barrierearm (axe, WCAG 2.1 AA)", async ({ page }) => {
      await page.goto(path);
      const ergebnis = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze();
      const ernst = ergebnis.violations.filter((v) => v.impact === "serious" || v.impact === "critical");
      expect(ernst.map((v) => `${v.id}: ${v.help}`)).toEqual([]);
    });

    test("sieht aus wie die Referenz @bild", async ({ page }, info) => {
      const name = `${path.replace(/\//g, "_") || "_"}.png`;
      test.skip(
        !existsSync(info.snapshotPath(name)) && !info.config.updateSnapshots.includes("all"),
        "Noch keine Referenz",
      );
      await page.goto(path);
      await expect(page).toHaveScreenshot(name, { fullPage: true });
    });
  });
}

test("Sprunglink führt zum Inhalt", async ({ page }) => {
  await page.goto("/");
  await page.keyboard.press("Tab");
  await expect(page.locator(".sprunglink")).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("#inhalt")).toBeFocused();
});

test("unbekannte Seite zeigt die 404-Seite", async ({ page }) => {
  const antwort = await page.goto("/gibt-es-nicht/");
  expect(antwort?.status()).toBe(404);
});
