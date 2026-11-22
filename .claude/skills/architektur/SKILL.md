---
name: architektur
description: Phase 3 der Bauhütte. Baumeister entwirft Architektur, Datenmodell und Vertrag aus dem freigegebenen PRD, der Advocatus Diaboli greift den Entwurf an, danach gibt Vale frei. Nutzen bei "/architektur" oder nach freigegebenem PRD.
---

# Architektur

Voraussetzung: `docs/projekt/prd.md` mit `status: freigegeben`.

1. **Entwurf:** Subagent `baumeister` beauftragen. Er liest PRD, Glossar, `bauhuette.toml` und schreibt
   `docs/technik/architektur.md` (Vorlage `architektur-vorlage.md`), ADRs (Vorlage `adr-vorlage.md`) und die
   Schemas in `packages/shared/src/`.
2. **Gegenrede:** Subagent `advocatus-diaboli` auf `architektur.md` und die neuen ADRs ansetzen,
   mit der Annahmenliste des Baumeisters als Startpunkt.
3. **Überarbeiten:** Kritische und wichtige Befunde an den Baumeister zurück. Höchstens zwei Runden.
   Was strittig bleibt, wird eine Frage an Vale, nicht stillschweigend entschieden.
4. Gegenrede und Umgang damit in den Abschnitt "Gegenrede" von `architektur.md` und in die betroffenen ADRs.
5. `python3 -m parlier pruefen schnell` (die Schemas müssen kompilieren).
6. Vale in höchstens 12 Zeilen vorstellen: Bausteine, wichtigste Entscheidungen mit Grund, offene Risiken.
   Erst nach ausdrücklicher Freigabe `status: freigegeben` in `architektur.md` und den ADRs setzen.
7. Profil festlegen, wie freigegeben: `python3 -m parlier profil statisch` (entfernt `apps/api`) oder
   `python3 -m parlier profil fullstack`, danach `pnpm install`, damit `pnpm-lock.yaml` passt.
8. `python3 -m parlier commit "Architektur freigegeben"`. Weiter mit `/zerlegen`.

Bei Profil `statisch` braucht es kein Datenmodell für eine Datenbank, wohl aber Schemas für die Inhalte,
weil die Redaktion daraus ihre Felder baut.
