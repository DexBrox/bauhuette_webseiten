# Bauhütte Webseiten

Vorlage für Webseiten, die mit Claude Code in einer festen Bauhütte entstehen: Interview, PRD,
Architektur mit Gegenrede, vertikale Issues, Umsetzung mit TDD (auch AFK), Review, Release.
Handarbeit wie Commits, Issues, Prüfen und Releases erledigt das Python-Werkzeug `parlier`,
damit Claude dafür keine Tokens braucht.

## Neues Projekt anlegen

1. Auf GitHub **Use this template**, neues privates Repo anlegen, klonen.
2. Einmal einrichten:
   ```bash
   pnpm install
   python3 -m parlier einrichten --name "Kulturland Hohenlohe" --repo DexBrox/kulturland --profil statisch --domain kulturland-hohenlohe.de
   git add -A && git commit -m "Projekt eingerichtet" && git push && git push -u origin develop
   ```
   `einrichten` passt `bauhuette.toml` und das Wiki an, entfernt bei `statisch` die API und aktualisiert
   `pnpm-lock.yaml`. Deshalb danach einmal committen.
3. Auf GitHub: **Settings, Pages, Source: GitHub Actions**, Secrets für den Server eintragen
   ([docs/technik/betrieb.md](docs/technik/betrieb.md)).
4. Claude Code im Ordner starten und `/interview` eingeben.

## Ablauf

| Phase | Befehl in Claude Code | Wer gibt frei |
|---|---|---|
| 0 Eingang | `/eingang` | |
| 1 Interview (Grill Me) | `/interview` | |
| 2 PRD | `/prd` | Vale |
| 3 Architektur und Gegenrede | `/architektur` | Vale |
| 4 Zerlegung in Issues | `/zerlegen` | |
| 5 Umsetzung | `/umsetzen 12` oder AFK `python3 -m parlier ralph` | |
| 6 Review | `/review 14` | Vale führt zusammen |
| 7 Release | `/release`, dann `python3 -m parlier release 1.2.0` | Vale |
| Klein | `/kurzweg` | |
| Orientierung | `/weiter` | |

Rollen, Regeln und Sprachregeln stehen in der Hüttenordnung [CLAUDE.md](CLAUDE.md).

## parlier

```bash
python3 -m parlier status            # wo stehen wir, was ist dran
python3 -m parlier pruefen schnell   # Lint, Typen, Tests, nur Fehlerzeilen
python3 -m parlier zweig 12          # feature/12-titel von develop
python3 -m parlier commit "Termine als Liste"
python3 -m parlier pr --was "Termine erscheinen jetzt als Liste."
python3 -m parlier ralph --max 3     # AFK im Sandbox-Container
python3 -m parlier --help            # alle Befehle
```

Nur Python-Standardbibliothek, dazu `git` und `gh`. Tests: `python3 -m unittest discover -s tests`.

## Stack

| Teil | Technik | Warum |
|---|---|---|
| Webseite | Astro, statisches HTML | schnell, gut für Suchmaschinen, läuft auf jedem SFTP-Server |
| Vertrag | zod in `packages/shared` | ein Schema für Seite, Redaktion und API |
| API (nur fullstack) | Hono auf Cloudflare Workers, Neon-Postgres | kein Server zu pflegen, kostenlos für kleine Projekte |
| Tests | Vitest, PGlite, Playwright mit axe | echtes Postgres ohne Server, Barrierefreiheit geprüft |
| Hilfe-Wiki | Quartz aus `docs/hilfe` | Wikilinks wie in Obsidian, Suche, Backlinks, Kategorien |
| Werkzeug | Python (`parlier`) | spart Tokens, setzt die Git-Regeln durch |

Begründungen und verworfene Alternativen: [ADR 0001](docs/technik/adr/0001-grundentscheidungen.md).

## Aufbau

```
.
├── CLAUDE.md                  Hüttenordnung: Phasen, Rollen, Regeln
├── bauhuette.toml             Einstellungen: Projekt, Zweige, Prüfschritte, Ralph, Wiki, Labels
├── .claude/
│   ├── agents/                baumeister, advocatus-diaboli, steinmetz, pruefer, tester, waechter, chronist
│   ├── skills/                interview, prd, architektur, zerlegen, umsetzen, review, release, kurzweg, eingang, rechtspruefung, weiter
│   └── settings.json          Rechte (Git nur über parlier) und Hooks (Lagebericht, Formatieren, Prüfen)
├── parlier/                   Python-Werkzeug, Tests in tests/
├── apps/web/                  Astro-Webseite, E2E-Tests in e2e/
├── apps/api/                  Hono-API (Profil fullstack)
├── packages/shared/           zod-Schemas
├── docs/
│   ├── projekt/               anf.md, prd.md, issues.md entstehen in den Phasen 1, 2, 4
│   ├── technik/               Architektur, ADRs, Glossar, Zusammenarbeit, Betrieb
│   └── hilfe/                 Wiki, wird zu /hilfe/
├── wiki/                      Quartz-Konfiguration und Stil
├── sandbox/Dockerfile         Container für Ralph
├── eingang/                   Material von außen, bleibt lokal
└── .github/                   Prüfung, Vorschau je Zweig, Live per SFTP, Release, Claude, Überwachung
```

## Weiter lesen

- [Zusammenarbeit, Zweige, Ralph, Releases](docs/technik/zusammenarbeit.md)
- [Betrieb: Server, Secrets, Cloudflare, Neon](docs/technik/betrieb.md)
- [Glossar](docs/technik/glossar.md)
