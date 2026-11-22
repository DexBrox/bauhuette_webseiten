---
name: rechtspruefung
description: Prüft eine Webseite vor dem ersten Release und nach größeren Änderungen auf Impressum, Datenschutz, Cookies, Verbindungen zu Dritten, Bildrechte, Einwilligungen und Barrierefreiheit und schreibt ein Prüfprotokoll. Nutzen bei "/rechtspruefung", vor dem Go-live.
---

# Rechtsprüfung

Wichtig: Das ist eine sorgfältige Prüfung nach öffentlichen Quellen, **keine Rechtsberatung**. Das steht
auch oben im Protokoll. Verantwortlich bleibt der Betreiber der Seite.

1. `pnpm build`, dann die gebaute Seite in `_site/` prüfen, nicht nur den Quellcode.
2. Die Punkte in `checkliste.md` der Reihe nach abarbeiten. Aktuelle Rechtslage im Web nachsehen
   (z. B. DDG statt TMG, aktuelle Urteile zu Google Fonts), nicht aus dem Gedächtnis.
3. Verbindungen zu Dritten technisch prüfen: `grep -rEo 'https?://[^"'"'"' )]+' _site | sort -u` und jede
   fremde Domain bewerten.
4. Protokoll nach `docs/technik/rechtspruefung.md` (Frontmatter `typ: protokoll`, `vertraulich: ja`, wenn
   personenbezogene Daten vorkommen): Tabelle "Ergebnis auf einen Blick", dann je Bereich Befund und Maßnahme.
5. Für jeden Handlungsbedarf beim Betreiber ein Issue mit Label `recht` und `mensch`.
   Für technischen Handlungsbedarf ein Issue mit Label `recht` und `technik`.
6. Ergebnis an Vale: höchstens 10 Zeilen, was bestanden ist und was der Betreiber tun muss.
