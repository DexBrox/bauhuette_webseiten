---
name: zerlegen
description: Phase 4 der Bauhütte. Zerlegt freigegebenes PRD und Architektur in vertikale Slices (Tracer Bullets) und legt sie mit parlier als GitHub-Issues mit Abhängigkeiten an. Nutzen bei "/zerlegen", "mach Issues daraus" oder nach freigegebener Architektur.
---

# Zerlegen in Issues

Voraussetzung: `prd.md` und `architektur.md` mit `status: freigegeben`.

## Regeln für Slices
- **Vertikal:** Jedes Issue ist ein dünner Durchstich durch alle Schichten (Inhalt, Seite, ggf. API, Test),
  nach dem man etwas sehen oder benutzen kann. Kein "erst alle Schemas, dann alle Seiten".
- Das erste Issue ist das Gerüst, das alles andere trägt (Layout, Navigation, Deploy). Klein halten.
- Ein Issue ist in einer Sitzung machbar: höchstens etwa 5 Akzeptanzkriterien.
- **AFK oder HITL:** `"afk": true`, wenn ein Agent es allein umsetzen kann. `false`, wenn Vale entscheiden
  oder liefern muss (Texte, Bilder, Zugänge, Design-Abnahme). HITL-Issues bekommen das Label `mensch`.
- Jedes Issue verweist auf seine Story (`prd_abschnitt`, z. B. "S3"), ADRs und betroffene Dateien.
- Abhängigkeiten nur, wo wirklich nötig. Unabhängige Issues kann Ralph in beliebiger Reihenfolge abarbeiten.

## Ablauf
1. Entwurf als JSON nach `.bauhuette/zerlegung.json` schreiben, Format in `issue-format.md`.
2. `python3 -m parlier issues anlegen .bauhuette/zerlegung.json --trocken` zeigt Reihenfolge und Abhängigkeiten.
3. Vale die Liste zeigen (Nummer, Titel, AFK/HITL, hängt ab von). Anpassungen einarbeiten.
4. `python3 -m parlier issues anlegen .bauhuette/zerlegung.json` legt Sammel-Issue und Issues an und schreibt
   `docs/projekt/issues.md`.
5. `python3 -m parlier commit "Zerlegung angelegt"`. Weiter mit `/umsetzen <nr>` oder AFK: `python3 -m parlier ralph`.
