import { defineConfig } from "astro/config";

// SITE_URL und BASE_PATH setzen die Workflows: live die Domain, in der Vorschau der Pfad auf GitHub Pages.
export default defineConfig({
  site: process.env.SITE_URL || "http://localhost:4321",
  base: process.env.BASE_PATH || "/",
  trailingSlash: "always",
  outDir: "../../_site",
  build: { format: "directory" },
});
