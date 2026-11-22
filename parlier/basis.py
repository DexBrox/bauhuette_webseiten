"""Gemeinsame Helfer: Konfiguration, Befehle ausführen, kurze Ausgaben."""

from __future__ import annotations

import copy
import json
import os
import re
import shutil
import subprocess
import sys
import tomllib
import unicodedata
from pathlib import Path
from typing import Any

KONFIG_DATEI = "bauhuette.toml"

STANDARD: dict[str, Any] = {
    "projekt": {"name": "Webseite", "repo": "", "profil": "statisch", "domain": ""},
    "zweige": {"haupt": "main", "sammel": "develop", "feature": "feature/", "fix": "fix/"},
    "pruefen": {
        "schnell": ["pnpm lint", "pnpm typecheck", "pnpm test"],
        "voll": ["pnpm lint", "pnpm typecheck", "pnpm test", "pnpm build"],
    },
    "ralph": {
        "befehl": "claude",
        "modell": "sonnet",
        "max_issues": 5,
        "max_runden": 80,
        "zeitlimit_min": 45,
        "label": "bereit",
    },
    "wiki": {
        "quelle": "docs/hilfe",
        "ziel": "_site/hilfe",
        "quartz": "v5.2.0",
        "konfig": "wiki/quartz.config.yaml",
        "stil": "wiki/custom.scss",
    },
    "ueberwachung": {"seiten": ["/"], "zertifikat_tage": 14},
    "label": [],
}


class Abbruch(Exception):
    """Fehler mit verständlicher Meldung. Wird in cli.main als kurze Zeile ausgegeben."""


def wurzel(start: Path | None = None) -> Path:
    """Projektwurzel: der nächste Ordner nach oben, der bauhuette.toml enthält."""
    ort = (start or Path.cwd()).resolve()
    for kandidat in [ort, *ort.parents]:
        if (kandidat / KONFIG_DATEI).exists():
            return kandidat
    return ort


def _mischen(basis: dict[str, Any], eigen: dict[str, Any]) -> dict[str, Any]:
    ergebnis = copy.deepcopy(basis)
    for schluessel, wert in eigen.items():
        if isinstance(wert, dict) and isinstance(ergebnis.get(schluessel), dict):
            ergebnis[schluessel] = _mischen(ergebnis[schluessel], wert)
        else:
            ergebnis[schluessel] = wert
    return ergebnis


def konfig(start: Path | None = None) -> dict[str, Any]:
    datei = wurzel(start) / KONFIG_DATEI
    if not datei.exists():
        return copy.deepcopy(STANDARD)
    with datei.open("rb") as f:
        return _mischen(STANDARD, tomllib.load(f))


def lauf(
    befehl: list[str] | str,
    *,
    pruefen: bool = True,
    eingabe: str | None = None,
    umgebung: dict[str, str] | None = None,
    ordner: Path | None = None,
    zeitlimit: float | None = None,
) -> subprocess.CompletedProcess[str]:
    """Führt einen Befehl aus und fängt die Ausgabe ab."""
    env = {**os.environ, **(umgebung or {})}
    try:
        ergebnis = subprocess.run(
            befehl,
            shell=isinstance(befehl, str),
            input=eingabe,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            cwd=ordner or wurzel(),
            timeout=zeitlimit,
        )
    except FileNotFoundError as fehler:
        name = befehl if isinstance(befehl, str) else befehl[0]
        raise Abbruch(f"Programm nicht gefunden: {name}") from fehler
    if pruefen and ergebnis.returncode != 0:
        name = befehl if isinstance(befehl, str) else " ".join(befehl[:3])
        text = (ergebnis.stderr or ergebnis.stdout).strip()
        raise Abbruch(f"{name} fehlgeschlagen:\n{kuerzen(text, 15)}")
    return ergebnis


def git(*argumente: str, pruefen: bool = True) -> str:
    return lauf(["git", *argumente], pruefen=pruefen).stdout.strip()


def hat_programm(name: str) -> bool:
    return shutil.which(name) is not None


def gh(*argumente: str, eingabe: str | None = None, als_json: bool = False) -> Any:
    """Ruft die GitHub-CLI auf. Mit als_json wird die Ausgabe als JSON gelesen."""
    if not hat_programm("gh"):
        raise Abbruch("Die GitHub-CLI (gh) fehlt. Installieren und mit 'gh auth login' anmelden.")
    ausgabe = lauf(["gh", *argumente], eingabe=eingabe).stdout
    if als_json:
        return json.loads(ausgabe or "null")
    return ausgabe.strip()


def kuerzen(text: str, max_zeilen: int = 30) -> str:
    zeilen = text.splitlines()
    if len(zeilen) <= max_zeilen:
        return text
    rest = len(zeilen) - max_zeilen
    return "\n".join(zeilen[:max_zeilen]) + f"\n... ({rest} weitere Zeilen)"


_UMLAUTE = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "Ä": "ae", "Ö": "oe", "Ü": "ue", "ß": "ss"})


def kurzname(text: str, laenge: int = 40) -> str:
    """Macht aus einem Titel einen Zweig- oder Dateinamen: 'Größe ändern' -> 'groesse-aendern'."""
    text = text.translate(_UMLAUTE)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text[:laenge].rstrip("-") or "ohne-titel"


def frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Liest einfaches Frontmatter (schluessel: wert). Listen bleiben als Text erhalten."""
    if not text.startswith("---\n"):
        return {}, text
    ende = text.find("\n---", 4)
    if ende < 0:
        return {}, text
    kopf = text[4:ende]
    rumpf = text[ende + 4 :].lstrip("\n")
    werte: dict[str, str] = {}
    for zeile in kopf.splitlines():
        m = re.match(r"^([A-Za-zÄÖÜäöü_][\w-]*):\s*(.*)$", zeile)
        if m:
            werte[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return werte, rumpf


def melde(text: str) -> None:
    print(text, flush=True)


def warne(text: str) -> None:
    print(text, file=sys.stderr, flush=True)
