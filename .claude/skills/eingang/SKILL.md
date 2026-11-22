---
name: eingang
description: Phase 0 der Bauhütte. Verarbeitet Material in eingang/ (Mails, Word, PDFs, Screenshots, alte Webseiten) zu Issues oder zu Stoff für das Interview. Nutzen bei "/eingang", "schau in den Eingang", wenn Vale Wünsche vom Auftraggeber weitergibt.
---

# Eingang verarbeiten

1. Dateien in `eingang/` auflisten (außer `LIESMICH.md`). Leer: Vale fragen, ob er etwas hineinlegen will.
2. Jede Datei lesen (Word und PDF mit den passenden Werkzeugen, Bilder ansehen).
3. Einordnen:
   | Art | Was passiert |
   |---|---|
   | Inhalt (Text, Bild, Termin) | Issue mit Label `inhalt`: Redaktion reicht, kein Code |
   | Kleiner Fehler oder Wunsch | Issue mit Label `fehler` oder `wunsch`, Hinweis auf `/kurzweg` |
   | Größerer Wunsch | Issue mit Label `wunsch`, Vorschlag: `/interview` dazu |
   | Material für ein neues Projekt | Zusammenfassung als Startpunkt für `/interview` |
   | Rechtliches (Impressum, Einwilligung) | Issue mit Label `recht` |
4. Issues anlegen mit `python3 -m parlier issues neu --titel "[Wunsch] ..." --label <label> --text "..."`. Text: was gewünscht
   ist, von wem, Datum, Dateiname aus dem Eingang. Keine personenbezogenen Daten, die nicht nötig sind.
5. Vale eine Tabelle zeigen: Datei, was daraus wurde (Issue-Nummer), was unklar blieb.
6. Verarbeitete Dateien nach `eingang/erledigt/` verschieben (bleiben lokal, nicht im Repo).
