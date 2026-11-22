---
titel: Betrieb
typ: dokumentation
erstellt: 2026-11-22
tags: [technik, betrieb]
---

# Betrieb

Hier stehen nur Namen von Secrets, nie Werte.

## GitHub einrichten (einmal pro Projekt)

1. **Settings, Pages, Build and deployment, Source: GitHub Actions.**
2. **Settings, Environments, github-pages:** neben `main` auch `develop`, `feature/*` und `fix/*` erlauben,
   sonst bricht die Vorschau ab.
3. **Settings, General:** "Template repository" nur in der Vorlage selbst anhaken.
4. Labels: `python3 -m parlier labels` (oder Workflow "Labels abgleichen" von Hand starten).

## Secrets (Settings, Secrets and variables, Actions)

| Name | Wofür | Pflicht |
|---|---|---|
| `SFTP_HOST`, `SFTP_USER`, `SFTP_PASSWORD`, `SFTP_PFAD` | Livegang auf den vorhandenen Server | für den Livegang |
| `SFTP_PORT` | wenn nicht 22 | nein |
| `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID` | API auf Workers (Profil fullstack) | nur fullstack |
| `CLAUDE_CODE_OAUTH_TOKEN` | Claude in Issues (`claude setup-token`) | nein |

Variable `SERVER_ABGLEICH = ja`: Der Upload löscht Dateien, die nicht mehr zur Seite gehören. Ohne sie zeigt
ein Trockenlauf in der Zusammenfassung, was gelöscht würde. `.well-known`, `cgi-bin` und Dateien des
Hosters bleiben immer.

## Profil fullstack: Cloudflare und Neon

1. Neon: Projekt anlegen (Region Frankfurt), Verbindung mit `-pooler` kopieren.
2. Datenbank anlegen: `DATABASE_URL=... pnpm --filter api exec drizzle-kit migrate`.
3. Cloudflare: API-Token mit Recht "Workers Scripts: Edit". In GitHub als Secret eintragen.
4. `pnpm --filter api exec wrangler secret put DATABASE_URL`, in `apps/api/wrangler.toml` `ALLOWED_ORIGIN`
   auf die Live-Domain setzen.
5. Neon und Cloudflare sind Auftragsverarbeiter: in die Datenschutzerklärung (Skill `/rechtspruefung`).

## Überwachung

Alle 6 Stunden prüft der Workflow "Überwachung" die Seiten aus `bauhuette.toml` (`[ueberwachung]`) und das
Zertifikat. Bei Störung entsteht ein Issue mit Label `betrieb`, es schließt sich selbst, wenn alles wieder geht.

## Kosten

| Posten | Kosten |
|---|---|
| GitHub (privates Repo, Actions, Pages) | im Konto enthalten, Actions-Minuten beachten |
| SFTP-Server | vorhanden |
| Cloudflare Workers, Neon | Free-Tarif reicht für kleine Projekte |
| Claude | Abo, Ralph und GitHub Action zählen zur Nutzung |

## Verbunden

- [[zusammenarbeit]]
