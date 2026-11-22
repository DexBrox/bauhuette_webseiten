---
titel: "ADR 0001: Grundentscheidungen der Vorlage"
typ: adr
erstellt: 2026-11-22
tags: [technik, adr]
status: freigegeben
---

# ADR 0001: Grundentscheidungen der Vorlage

## Kontext
Die Vorlage soll Webseiten mit Frontend und optionalem Backend tragen, auf vorhandenen SFTP-Servern oder in der
Cloud laufen (nicht lokal) und so arbeiten, dass Claude möglichst wenig Tokens für Handarbeit braucht.

## Entscheidung
TypeScript durchgehend, Astro für die Webseite, zod-Vertrag in `packages/shared`, Hono auf Cloudflare Workers
mit Neon-Postgres nur bei Bedarf, Quartz für das Hilfe-Wiki, Python-Werkzeug `parlier` für alle Handarbeit.

## Alternativen
| Option | Dafür | Dagegen |
|---|---|---|
| **Astro** (gewählt) | statisches HTML je Seite, gut für Suchmaschinen, läuft per SFTP, React-Teile möglich | eigenes Dateiformat `.astro` |
| React mit Vite (SPA) | vertraut aus der Fitness-App | Seiten entstehen erst im Browser, schlechter für Suchmaschinen, braucht Umleitungen auf dem Server |
| Next.js | alles in einem | vermischt Frontend und Backend, zielt auf eigene Hosting-Plattform |
| **Hono auf Workers** (gewählt) | kostenlos, kein Server, läuft auch lokal und in Tests | 10 ms CPU je Anfrage im Free-Tarif |
| Node auf VPS | keine Grenzen | Wartung, Updates, Kosten |
| Backend auf dem SFTP-Server | vorhanden | dort läuft meist nur PHP |
| **Neon-Postgres** (gewählt), Tests mit PGlite | echtes Postgres, gleicher Dialekt in Tests ohne Server | 0,5 GB im Free-Tarif |
| Cloudflare D1 (SQLite) | direkt im Worker | anderer Dialekt, weniger Werkzeuge |
| **Quartz** (gewählt) | Wikilinks wie Obsidian, Backlinks, Suche, Kategorien, statisch | wird als Ordner geholt, nicht als Paket |
| MediaWiki, DokuWiki | echtes Bearbeiten im Browser | Inhalte außerhalb des Repos, Agenten kommen schlecht ran |
| Starlight | sauber im Monorepo | eher Handbuch als Wiki |
| **Python für parlier** (gewählt) | Vale pflegt es selbst, unabhängig vom Projekt-Stack, nur Standardbibliothek | zweite Laufzeit |
| Node-Skripte | eine Laufzeit | bindet das Werkzeug an den Stack |

## Folgen
- Profil `statisch` braucht nur einen SFTP-Server, `fullstack` zusätzlich Cloudflare und Neon.
- Jede weitere Abhängigkeit braucht ein eigenes ADR.
- Inhalte, Redaktion und API teilen dieselben Schemas, Fehler fallen beim Bauen auf.

## Gegenrede
Astro weicht von der ursprünglich besprochenen React-Variante ab. Vale hat Astro am 22.11.2026 freigegeben,
weil fertiges HTML pro Seite für Suchmaschinen und SFTP-Server besser passt.

## Verbunden
- [[zusammenarbeit]]
- [[betrieb]]
