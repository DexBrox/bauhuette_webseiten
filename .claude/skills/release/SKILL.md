---
name: release
description: Phase 7 der Bauhütte. Bereitet ein Release vor (CHANGELOG prüfen, Version vorschlagen, letzte Prüfung) und sagt Vale den einen Befehl, der es live bringt. Nutzen bei "/release", "Release bitte".
---

# Release vorbereiten

Ein Release bringt alles von `develop` gesammelt live. Ausführen darf es nur Vale.

1. `git fetch -q origin` und `git log --oneline origin/main..origin/develop` (Was kommt mit?).
2. CHANGELOG unter `[Unreleased]` gegen die Liste prüfen. Fehlt etwas, Chronist beauftragen und auf einem
   Zweig `fix/changelog-<datum>` mit PR nachtragen.
3. Version vorschlagen nach diesen Regeln und begründen:
   | Version | Wann |
   |---|---|
   | `X.0.0` | Neuaufbau oder grundlegend anderes Aussehen |
   | `x.Y.0` | mindestens eine neue Funktion oder Seite |
   | `x.y.Z` | nur Fehlerbehebungen und kleine Korrekturen |
4. Subagent `waechter` über alles seit dem letzten Release. Kritische Befunde stoppen das Release.
5. Vor dem **ersten** Release: `/rechtspruefung`, falls noch nicht geschehen.
6. Vale diese Befehle geben:
   ```
   git switch develop && git pull
   python3 -m parlier release <version>
   ```
   Danach auf GitHub den Release-PR mit **Create a merge commit** zusammenführen, dann:
   ```
   python3 -m parlier release <version> --abschliessen --titel "<kurzer Titel>"
   ```
7. Kurzen Text "Was ist neu" für den Auftraggeber vorschlagen (höchstens 5 Zeilen, ohne Technik).
