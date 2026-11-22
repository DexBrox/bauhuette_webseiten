import { defineConfig, devices } from "@playwright/test";

// Prüft die gebaute Seite (astro preview). Screenshot-Vergleiche (@bild) laufen erst, wenn es
// Referenzbilder gibt. Anlegen im Sandbox-Container (Linux, wie die CI): pnpm --filter web e2e:bilder
export default defineConfig({
  testDir: "e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [["list"], ["html", { open: "never" }]] : "list",
  use: {
    baseURL: "http://localhost:4321",
    trace: "retain-on-failure",
  },
  expect: {
    toHaveScreenshot: { maxDiffPixelRatio: 0.01 },
  },
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"] } },
    { name: "handy", use: { ...devices["Pixel 7"] } },
  ],
  webServer: {
    command: "pnpm preview",
    url: "http://localhost:4321",
    reuseExistingServer: !process.env.CI,
  },
});
