---
name: interview
description: Phase 1 der Bauhütte (Grill Me). Fragt Vale gründlich zu einer neuen Webseite oder einem großen Vorhaben aus, bis alle Entscheidungen geklärt sind, und hält Anforderung und Fachbegriffe fest. Nutzen bei "/interview", "grill me", einer neuen Projektidee oder unklaren Anforderungen.
argument-hint: "[Thema oder Link zur alten Seite]"
---

# Interview (Grill Me)

Ziel: gemeinsames Verständnis, bevor irgendetwas gebaut wird. Jede offene Entscheidung wird geklärt.

## Ablauf
1. `python3 -m parlier status` lesen. Gibt es schon `docs/projekt/anf.md`, daran anknüpfen statt neu anzufangen.
   Phasen-Issue: gibt es kein offenes "Phase 1: Interview", anlegen mit
   `python3 -m parlier issues neu --titel "Phase 1: Interview" --label prd --label mensch --zweig`.
   Nach jeder beantworteten Frage ein kurzer Kommentar ins Issue (`parlier issue <nr> kommentar "..."`):
   Frage, Antwort, Entscheidung.
2. Material sichten, das Vale nennt (alte Seite, Dateien in `eingang/`). Was du selbst nachlesen kannst, fragst du nicht.
3. **Eine Frage pro Nachricht.** Zu jeder Frage deine Empfehlung mit kurzem Grund, damit Vale nur zustimmen muss.
4. Gehe den Entscheidungsbaum Ast für Ast durch, bis jeder Ast entschieden oder bewusst offen ist:
   - Zweck und Zielgruppe, Erfolg in einem Jahr
   - Seiten und Inhalte, wer pflegt was, wie oft (Redaktion nötig?)
   - Funktionen (Formulare, Termine, Suche, Login, Zahlungen), was ausdrücklich **nicht**
   - Gestaltung: Vorlagen, Marke, Bilder, Barrierefreiheit
   - Betrieb: Domain, Hosting (SFTP-Server oder Cloud), Profil statisch oder fullstack, Budget
   - Recht: Impressum, Datenschutz, Bildrechte, Einwilligungen
   - Termine und Abhängigkeiten
5. Widerspricht sich etwas, sprich es sofort an.

## Festhalten (laufend, nicht erst am Ende)
- `docs/projekt/anf.md`: Frontmatter `titel`, `typ: anforderung`, `erstellt`, `tags`, `status: entwurf`.
  Abschnitte: Ziel, Zielgruppe, Seiten und Inhalte, Funktionen, Nicht-Ziele, Gestaltung, Betrieb, Recht,
  Offene Fragen, Entscheidungen (je Zeile: Entscheidung, Grund).
- `docs/technik/glossar.md`: jeder Fachbegriff, der fällt, mit einer Zeile Bedeutung. Gleiche Wörter für
  gleiche Dinge in Code, Doku und Gespräch.

## Ende
Wenn keine Frage mehr offen ist: kurze Zusammenfassung (höchstens 10 Zeilen) und Vorschlag: weiter mit `/prd`.
Vale bestätigt, dann `status: freigegeben` in `anf.md` setzen und mit `python3 -m parlier commit` sichern.
