# Changelog

Alle nennenswerten Änderungen an diesem Projekt. Format nach
[keepachangelog.com](https://keepachangelog.com/de/1.1.0/), Versionen nach [semver.org](https://semver.org/lang/de/).

## [Unreleased]

### Hinzugefügt
- `parlier profil statisch|fullstack` legt das Profil in Phase 3 fest, statisch entfernt `apps/api`.

- `parlier issues neu` legt ein einzelnes Issue an, mit `--zweig` gleich den Arbeitszweig dazu.

### Geändert
- Ohne Issue keine Arbeit: Hüttenordnung und Skills beginnen jede Phase mit einem Issue, `parlier zweig` und `parlier commit` lehnen Arbeit ohne Issue-Nummer ab.
- `parlier pr` weicht auf die REST-API aus, wenn GraphQL gesperrt ist (Cloud-Sitzungen). Labels und Kommentare laufen immer über REST.

### Behoben
- `parlier issue <nr> label -name` entfernt Labels wieder, vorher hielt die Befehlszeile das Minus für eine Option.
- `parlier einrichten` lässt das Profil offen und beginnt ein frisches CHANGELOG für das neue Projekt.
- Namensschema für Projekte: `web-<projekt>`, die Vorlage heißt jetzt `web-bauhuette`.

## [0.1.0] - 2026-11-22

### Hinzugefügt
- Bauhütte als Vorlage: Hüttenordnung, sieben Rollen als Subagenten, elf Skills von Eingang bis Release.
- Werkzeug parlier (Python): Zweige, Commits, Pull Requests, Issues aus Entwürfen, Kontext für Subagenten,
  Prüfen mit kurzer Fehlerausgabe, Doku-Pflicht, Linkprüfung, Ralph für AFK, Releases, Vorschau, Überwachung.
- Hooks für Claude Code: Lagebericht beim Start, Formatieren nach jeder Änderung, schnelle Prüfung vor Abschluss.
- Webseite mit Astro, Vertrag mit zod, API mit Hono und Neon für das Profil fullstack.
- Hilfe-Wiki mit Quartz: Suche, Inhaltsverzeichnis, Links auf diese Seite, Kategorien, Bearbeiten,
  Versionsgeschichte und Diskussion je Seite.
- Workflows: Prüfung je Pull Request, Testseite je Zweig, Livegang per SFTP, Release aus dem CHANGELOG,
  Label fertig bei develop, Claude in Issues, Überwachung der Live-Seite, Labels, Dependabot.
- Sandbox-Container für Ralph.

### Behoben
- Testseiten werden wieder veröffentlicht: Bauen und Veröffentlichen laufen in zwei Jobs. (#2)
- parlier commit setzt die Issue-Nummer in die erste Zeile statt ans Ende mehrzeiliger Nachrichten. (#2)
- Hilfe-Wiki: Absätze brechen nicht mehr mitten im Satz um, toter Link auf die Kategorie Redaktion entfernt. (#2)
