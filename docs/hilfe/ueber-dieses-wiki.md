---
titel: Über dieses Wiki
typ: wiki
erstellt: 2026-11-22
tags: [hilfe, wiki]
---

Dieses Wiki ist aufgebaut wie Wikipedia: jede Seite ein Thema, Seiten verlinken sich gegenseitig, Kategorien
bündeln Seiten. Geschrieben wird es in Markdown im Ordner `docs/hilfe/` des Projekts. Beim Bauen der Webseite
entsteht daraus diese Hilfe unter `/hilfe/`.

> [!infobox] Wikipedia-Funktionen
> - **Suche:** oben links
> - **Inhaltsverzeichnis:** rechts
> - **Links auf diese Seite:** rechts unten
> - **Kategorien:** unter dem Titel
> - **Bearbeiten, Versionsgeschichte, Diskussion:** unten auf jeder Seite

## Eine Seite schreiben

```markdown
---
titel: Bilder austauschen
typ: wiki
erstellt: 2026-12-01
tags: [hilfe, redaktion]
---

Text mit Link auf eine andere Seite: [[wunsch-melden]].

## Verbunden

- [[erste-schritte]]
```

- **Links** auf andere Seiten mit `[[dateiname]]` oder `[[dateiname|anderer Text]]`.
- **Kategorien** sind die `tags`. Jede Kategorie hat automatisch eine Übersichtsseite.
- **Infokasten** rechts neben dem Text: `> [!infobox] Titel`, darunter Zeilen mit `> `.
- **Hinweise:** `> [!note]`, `> [!warning]`, `> [!tip]`.

Neue Seiten und Änderungen schreibt meist der Chronist-Agent mit, sobald sich an der Webseite etwas ändert.
Von Hand geht es über **Seite bearbeiten** unten auf jeder Seite.

## Verbunden

- [[index|Hauptseite]]
