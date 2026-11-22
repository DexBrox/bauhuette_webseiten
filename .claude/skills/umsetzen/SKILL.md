---
name: umsetzen
description: Phase 5 der Bauhütte. Setzt ein Issue um: frischer Steinmetz mit TDD, zweistufiger Prüfer, bei Seiten der Tester, am Ende der Chronist, dann Pull Request nach develop. Nutzen bei "/umsetzen <nr>", "setz Issue 12 um" und von Ralph im AFK-Modus.
argument-hint: "<issue-nummer>"
---

# Ein Issue umsetzen

Du bist der Parlier. Du schreibst selbst keinen Anwendungscode, du verteilst und prüfst.

1. **Vorbereiten:** `python3 -m parlier zweig <nr>` (überspringen, wenn Ralph den Zweig schon angelegt hat),
   `python3 -m parlier issue <nr> label +in-arbeit -bereit`, dann `python3 -m parlier kontext <nr>`.
   Fehlt etwas Fachliches, im Issue fragen, Label `mensch`, abbrechen.
2. **Umsetzen:** Subagent `steinmetz` mit dem Kontext beauftragen. Er arbeitet TDD und committet selbst.
3. **Prüfen Stufe 1 und 2:** Subagent `pruefer` mit Issue-Nummer und `git diff origin/develop...HEAD`.
   Bei `Urteil: nachbessern` die Befunde an einen **neuen** Steinmetz geben. Höchstens zwei Runden,
   danach Label `braucht-hilfe` und Zusammenfassung im Issue.
4. **Seiten oder Abläufe geändert?** Subagent `tester` für E2E und Barrierefreiheit.
   **Formulare, API, Dritte, neue Pakete?** Subagent `waechter`.
5. **Doku:** Subagent `chronist`: CHANGELOG unter `[Unreleased]`, Wiki in `docs/hilfe/` falls Nutzer etwas merken.
6. `python3 -m parlier pruefen voll`. Muss grün sein.
7. Im AFK-Modus endet die Arbeit hier, Ralph öffnet den PR. Sonst:
   `python3 -m parlier pr --was "<2 bis 4 Sätze, für Laien verständlich>"`.
8. Ergebnis an Vale in höchstens 6 Zeilen: was geht jetzt, Link zum PR, was offen ist.
