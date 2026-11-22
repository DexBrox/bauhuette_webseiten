"""Stellt für einen Subagenten genau den Kontext zusammen, den er für ein Issue braucht.
Spart Tokens: Der Agent muss nicht selbst suchen, welche PRD-Stelle und welche ADRs gelten."""

from __future__ import annotations

import re
from pathlib import Path

from .basis import gh, kuerzen, wurzel

MAX_ADR_ZEILEN = 60
MAX_GLOSSAR_ZEILEN = 50
MAX_ABSCHNITT_ZEILEN = 80


def bezug(text: str, schluessel: str) -> str | None:
    m = re.search(rf"^{schluessel}:\s*(.+)$", text or "", re.MULTILINE | re.IGNORECASE)
    return m.group(1).strip() if m else None


def prd_abschnitt(prd_text: str, ueberschrift: str) -> str | None:
    """Schneidet den Abschnitt mit dieser Überschrift (beliebige Ebene) bis zur nächsten gleich hohen aus."""
    zeilen = prd_text.splitlines()
    for i, zeile in enumerate(zeilen):
        m = re.match(r"^(#+)\s+(.*)$", zeile)
        if m and ueberschrift.lower() in m.group(2).lower():
            ebene = len(m.group(1))
            ende = len(zeilen)
            for j in range(i + 1, len(zeilen)):
                n = re.match(r"^(#+)\s", zeilen[j])
                if n and len(n.group(1)) <= ebene:
                    ende = j
                    break
            return "\n".join(zeilen[i:ende]).strip()
    return None


def adr_dateien(kennungen: str) -> list[Path]:
    ordner = wurzel() / "docs" / "technik" / "adr"
    gefunden = []
    for nummer in re.findall(r"\d{1,4}", kennungen):
        gefunden += sorted(ordner.glob(f"{int(nummer):04d}-*.md"))
    return gefunden


def zusammenstellen(nummer: int) -> str:
    issue = gh("issue", "view", str(nummer), "--json", "number,title,body,labels,comments", als_json=True)
    text = issue.get("body") or ""
    teile = [f"# Issue #{issue['number']}: {issue['title']}", "", text.strip()]

    kommentare = issue.get("comments") or []
    if kommentare:
        teile += ["", "## Letzte Kommentare"]
        for k in kommentare[-3:]:
            autor = (k.get("author") or {}).get("login", "?")
            teile += ["", f"**{autor}:** " + kuerzen(k.get("body", "").strip(), 12)]

    prd = bezug(text, "PRD")
    if prd:
        m = re.match(r'([^,]+?)(?:,\s*Abschnitt\s+"([^"]+)")?$', prd)
        datei = wurzel() / (m.group(1).strip() if m else "docs/projekt/prd.md")
        abschnitt = m.group(2) if m else None
        if datei.exists() and abschnitt:
            stueck = prd_abschnitt(datei.read_text(encoding="utf-8"), abschnitt)
            if stueck:
                teile += ["", f"## PRD-Abschnitt ({datei.name})", "", kuerzen(stueck, MAX_ABSCHNITT_ZEILEN)]

    adr = bezug(text, "ADR")
    if adr:
        for datei in adr_dateien(adr):
            teile += ["", f"## {datei.stem}", "", kuerzen(datei.read_text(encoding="utf-8").strip(), MAX_ADR_ZEILEN)]

    glossar = wurzel() / "docs" / "technik" / "glossar.md"
    if glossar.exists():
        teile += ["", "## Glossar", "", kuerzen(glossar.read_text(encoding="utf-8").strip(), MAX_GLOSSAR_ZEILEN)]

    dateien = bezug(text, "Dateien")
    if dateien:
        teile += ["", "## Betroffene Dateien"]
        for pfad in [p.strip() for p in dateien.split(",") if p.strip()]:
            status = "vorhanden" if (wurzel() / pfad).exists() else "neu"
            teile.append(f"- {pfad} ({status})")

    return "\n".join(teile).strip() + "\n"
