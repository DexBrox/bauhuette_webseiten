---
name: prd
description: Phase 2 der Bauhütte. Macht aus Interview und Anforderung ein PRD (Produktanforderung) in docs/projekt/prd.md und holt Vales Freigabe. Nutzen bei "/prd", "schreib das PRD" oder nach abgeschlossenem Interview.
---

# PRD schreiben

Voraussetzung: `docs/projekt/anf.md` mit `status: freigegeben`. Sonst zuerst `/interview`.

0. Phasen-Issue: `python3 -m parlier issues neu --titel "Phase 2: PRD" --label prd --zweig`, falls keins offen ist.
1. `anf.md` und `docs/technik/glossar.md` lesen. Kein neues Interview: nur nachfragen, was für das PRD fehlt.
2. Vorlage `.claude/skills/prd/vorlage.md` nach `docs/projekt/prd.md` übernehmen und füllen.
   - User Stories als nummerierte Liste ("Als ... möchte ich ..., damit ..."), jede mit prüfbaren Akzeptanzkriterien.
   - Jede Story bekommt eine Überschrift `### S<n> Kurzname`. Die Zerlegung verweist auf diese Abschnitte.
   - Nicht-Ziele ausdrücklich nennen. Sie schützen vor wucherndem Umfang.
   - Begriffe nur aus dem Glossar.
3. Den **Advocatus Diaboli** auf das PRD ansetzen (Subagent `advocatus-diaboli`, Auftrag: Lücken, Widersprüche,
   unrealistischer Umfang). Kritische Befunde mit Vale klären, Ergebnis im Abschnitt "Gegenrede" festhalten.
4. Vale das PRD in höchstens 10 Zeilen zusammenfassen und um Freigabe bitten.
5. Erst nach ausdrücklicher Freigabe `status: freigegeben` setzen, `python3 -m parlier commit "PRD freigegeben"`.
   Weiter mit `/architektur`.
