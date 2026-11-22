# Format des Zerlegungs-Entwurfs

```json
{
  "prd": "docs/projekt/prd.md",
  "eltern": {
    "titel": "PRD: Vereinsseite Kulturland",
    "text": "Sammel-Issue für alle Teile aus docs/projekt/prd.md."
  },
  "issues": [
    {
      "id": "A",
      "titel": "Gerüst: Layout, Navigation, Deploy auf die Testseite",
      "text": "Was gebaut wird und warum, in zwei bis fünf Sätzen.",
      "akzeptanz": [
        "Startseite zeigt Kopf, Menü und Fuß mit Impressum und Datenschutz",
        "Push auf develop baut die Testseite"
      ],
      "prd_abschnitt": "S1",
      "adr": ["0001"],
      "dateien": ["apps/web/src/layouts/BaseLayout.astro"],
      "labels": ["technik"],
      "afk": true,
      "abhaengig_von": []
    },
    {
      "id": "B",
      "titel": "Termine: Liste der kommenden Termine",
      "text": "...",
      "akzeptanz": ["..."],
      "prd_abschnitt": "S3",
      "labels": ["technik"],
      "afk": true,
      "abhaengig_von": ["A"]
    }
  ]
}
```

| Feld | Pflicht | Bedeutung |
|---|---|---|
| `id` | ja | Kurzname nur im Entwurf, wird zur Issue-Nummer |
| `titel`, `text`, `akzeptanz` | ja | Kriterien prüfbar und aus Nutzersicht |
| `prd_abschnitt` | nein | Überschrift oder Story-Kürzel im PRD, parlier kontext schneidet sie aus |
| `adr` | nein | Nummern der ADRs, die gelten |
| `dateien` | nein | voraussichtlich betroffene Dateien |
| `labels` | nein | aus bauhuette.toml (`technik`, `design`, `inhalt`, `recht`, ...) |
| `afk` | nein | Standard `true`. `false` gibt Label `mensch` statt `bereit` |
| `abhaengig_von` | nein | ids, die vorher erledigt sein müssen. Kreise werden abgelehnt |
