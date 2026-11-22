---
name: kurzweg
description: Kleiner Weg für Fehlerbehebungen und kleine Änderungen ohne Interview, PRD, Architektur und Zerlegung. Nutzen bei "/kurzweg", Tippfehlern, kaputten Links, kleinen Fehlern, die in einer Stunde erledigt sind.
argument-hint: "<was zu tun ist oder issue-nummer>"
---

# Kurzweg

Für alles, was klein ist: ein Fehler, ein Text, ein Link, eine Farbe. Der volle Ablauf wäre hier zu teuer.

**Nicht der Kurzweg**, sondern volles Verfahren, wenn: neue Seite oder Funktion, neue Abhängigkeit,
Änderung an Datenmodell, API oder Redaktion, mehr als etwa fünf Dateien. Dann Vale vorschlagen: `/interview`
oder Issue mit `/zerlegen`.

1. Gibt es kein Issue: `python3 -m parlier issues neu --titel "..." --label fehler --text "..." --zweig --fix`.
2. Gibt es eins: `python3 -m parlier zweig <nr> --fix`
3. Fehler zuerst mit einem Test nachstellen, der rot ist. Dann beheben. (Bei reinen Texten entfällt der Test.)
4. Subagent `pruefer`, nur Stufe 1 und Stufe 2 in Kurzform.
5. CHANGELOG-Eintrag unter `### Behoben` selbst schreiben (eine Zeile mit Issue-Nummer).
6. `python3 -m parlier pruefen voll`, `python3 -m parlier commit "..."`, `python3 -m parlier pr --was "..."`.

Notfall (Live-Seite kaputt): Zweig von `main` statt `develop` (`git switch -c fix/<nr>-x origin/main`),
`python3 -m parlier pr --basis main --was "..."`, Vale sofort Bescheid geben. Nach dem Zusammenführen holt
Vale `main` nach `develop` (`git switch develop && git merge origin/main && git push`).
