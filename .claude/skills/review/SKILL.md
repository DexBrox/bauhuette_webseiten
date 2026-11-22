---
name: review
description: Phase 6 der Bauhütte. Prüft einen Pull Request oder Zweig parallel mit Prüfer, Tester und Wächter und fasst die Befunde nach Schwere zusammen. Nutzen bei "/review", "schau dir PR 14 an" oder vor dem Zusammenführen.
argument-hint: "[pr-nummer oder zweig]"
---

# Review

1. Ziel bestimmen: PR-Nummer (`gh pr view <nr> --json headRefName,body`) oder aktueller Zweig.
   Zugehöriges Issue aus "Closes #" lesen, `python3 -m parlier kontext <issue>`.
2. **Parallel** starten: `pruefer` (Spec-Treue, Qualität), `tester` (E2E, Barrierefreiheit),
   `waechter` (Sicherheit, Datenschutz). Jeder bekommt Kontext und Diff gegen `origin/develop`.
3. Bei Änderungen an Architektur oder neuen Abhängigkeiten zusätzlich `advocatus-diaboli`.
4. Zusammenführen: doppelte Befunde streichen, nach Schwere sortieren.
5. Ausgabe an Vale, höchstens 20 Zeilen:
   - Tabelle `Schwere | Befund | Fundstelle | Wer behebt`
   - Urteil: **zusammenführen** (keine kritischen Befunde), **nachbessern** oder **verwerfen**
6. Bei nachbessern: Befunde als Kommentar in den PR (`gh pr comment <nr> --body-file -`) und, wenn Vale will,
   `/umsetzen <issue>` erneut mit den Befunden.

Zusammenführen tut nur Vale.
