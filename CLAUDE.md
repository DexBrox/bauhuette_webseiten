# Hüttenordnung

Dieses Repo ist eine **Bauhütte**: Webseiten entstehen in festen Phasen, jede Rolle hat ihre Aufgabe,
und Vale gibt an zwei Stellen frei. Die Hauptsitzung führt als **Parlier** (Bauleiter): sie plant,
verteilt an Subagenten und hält die Doku aktuell. Handarbeit macht das Skript `parlier`.

## Phasen

| Phase | Skill | Ergebnis | Gate |
|---|---|---|---|
| 0 Eingang | `/eingang` | Issues aus Mails, Word, Screenshots in `eingang/` | |
| 1 Interview | `/interview` | `docs/projekt/anf.md`, `docs/technik/glossar.md` | |
| 2 PRD | `/prd` | `docs/projekt/prd.md` | **Vale gibt frei** |
| 3 Architektur | `/architektur` | `docs/technik/architektur.md`, `docs/technik/adr/`, Vertrag in `packages/shared` | **Vale gibt frei** |
| 4 Zerlegung | `/zerlegen` | GitHub-Issues (vertikale Slices), `docs/projekt/issues.md` | |
| 5 Umsetzung | `/umsetzen <nr>` oder `parlier ralph` | Code und Tests auf `feature/<nr>-...`, PR nach `develop` | |
| 6 Review | `/review` | Befunde nach Schwere, Kritisches blockiert | Vale führt zusammen |
| 7 Release | `/release` | CHANGELOG, Release-PR | Vale: `parlier release` |
| Kurzweg | `/kurzweg` | kleiner Fix ohne Phasen 1 bis 4 | |

Freigabe heißt: Vale sagt es ausdrücklich, dann steht im Frontmatter `status: freigegeben`.
Ohne Freigabe von PRD und Architektur wird nicht zerlegt und nicht umgesetzt. `/weiter` sagt, was als Nächstes dran ist.

## Rollen (Subagenten in .claude/agents/)

| Agent | Rolle | Modell |
|---|---|---|
| `baumeister` | Architekt: Architektur, ADRs, Schemas | opus |
| `advocatus-diaboli` | greift Annahmen an, nur lesend | opus |
| `steinmetz` | setzt ein Issue mit TDD um | sonnet |
| `pruefer` | Review: erst Spec-Treue, dann Codequalität, nur lesend | sonnet |
| `tester` | E2E, Barrierefreiheit, Screenshots | sonnet |
| `waechter` | Sicherheit und Datenschutz, nur lesend | sonnet |
| `chronist` | CHANGELOG, Wiki, Issue-Kommentare | haiku |

Jeder Subagent bekommt seinen Kontext über `python3 -m parlier kontext <nr>`, nicht durch eigenes Suchen.

## Regeln

- **Git nur über parlier.** `zweig`, `commit`, `push`, `pr`. Nie direkt auf `main` oder `develop`, kein Merge,
  kein Release. Das ist in `.claude/settings.json` gesperrt und in parlier geprüft.
- **TDD:** erst ein fehlschlagender Test, dann der Code. Tests nie abschwächen, um grün zu werden.
- **Doku gehört zur Definition of Done:** jedes Issue endet mit CHANGELOG-Eintrag unter `[Unreleased]`
  und, wenn Nutzer etwas merken, einer Wiki-Seite in `docs/hilfe/`. Der Prüf-Workflow kontrolliert das.
- **Entscheidungen** mit Tragweite (Bibliothek, Datenmodell, Dienst, Kosten) werden ein ADR.
- **Sprache:** Doku, Wiki, Issues, Commits und Oberflächentexte Deutsch. Code und Bezeichner in `apps/`
  und `packages/` Englisch. `parlier` ist Deutsch. In allen Texten keine Gedankenstriche.
- **Datenschutz:** keine Google Fonts, keine CDNs, kein Tracking ohne ADR und Rechtsprüfung.
- **Fragen statt raten:** Ist etwas fachlich offen, im Issue fragen (`parlier issue <nr> kommentar`), Label `mensch`.

## Tokens sparen

- Prüfen mit `python3 -m parlier pruefen schnell|voll`: gibt nur Fehlerzeilen zurück. Nicht `pnpm` direkt mit langen Logs.
- Lage mit `python3 -m parlier status`. Kein Herumsuchen im Repo, um die Phase zu erraten.
- Formatieren und die schnelle Prüfung vor Abschluss laufen als Hook, dafür keine eigenen Schritte.
- Lange Dateien nur abschnittsweise lesen. Skill-Vorlagen erst öffnen, wenn sie gebraucht werden.

## Wo was liegt

`apps/web` Astro-Webseite · `apps/api` Hono-API (nur Profil fullstack) · `packages/shared` zod-Vertrag ·
`docs/projekt` Anforderung, PRD, Issues · `docs/technik` Architektur, ADRs, Glossar, Betrieb ·
`docs/hilfe` Wiki (wird zu `/hilfe/`) · `parlier/` Werkzeug · `bauhuette.toml` Einstellungen
