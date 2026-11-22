"""Lint, Typen, Tests, Build. Gibt nur die wichtigen Fehlerzeilen zurück, nicht ganze Logs.
Außerdem die Doku-Pflicht für Pull Requests."""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path

from .basis import git, konfig, lauf, melde, wurzel

MUSTER = re.compile(
    r"(error|fehler|fail|✗|×|✘|assert|expected|received|cannot|not found|unexpected|TS\d{3,5}|ERR!|panic)",
    re.IGNORECASE,
)
STOERUNG = re.compile(r"^\s*(at |node:internal|\u001b\[2m|npm notice)")


@dataclass
class Ergebnis:
    befehl: str
    ok: bool
    sekunden: float
    auszug: str


def auszug(ausgabe: str, max_zeilen: int = 25) -> str:
    """Wählt die aussagekräftigen Zeilen: Fehlerzeilen plus etwas Umgebung, dann das Ende."""
    zeilen = [z.rstrip() for z in re.sub(r"\x1b\[[0-9;]*m", "", ausgabe).splitlines() if z.strip()]
    wichtig: list[str] = []
    for i, zeile in enumerate(zeilen):
        if MUSTER.search(zeile) and not STOERUNG.match(zeile):
            for z in zeilen[max(0, i - 1) : i + 3]:
                if z not in wichtig:
                    wichtig.append(z)
        if len(wichtig) >= max_zeilen:
            break
    if not wichtig:
        wichtig = zeilen[-max_zeilen:]
    return "\n".join(wichtig[:max_zeilen])


def pruefen(stufe: str = "voll", stopp: bool = False, als_json: bool = False, leise: bool = False) -> tuple[bool, str]:
    """Führt die Prüfschritte aus. Gibt (alles_ok, kurzer_bericht) zurück."""
    befehle = konfig()["pruefen"].get(stufe) or []
    if not (wurzel() / "node_modules").exists() and any(b.startswith("pnpm") for b in befehle):
        bericht = "Hinweis: node_modules fehlt, zuerst 'pnpm install' ausführen."
        if not leise:
            melde(bericht)
        return False, bericht
    ergebnisse: list[Ergebnis] = []
    for befehl in befehle:
        start = time.monotonic()
        r = lauf(befehl, pruefen=False)
        dauer = time.monotonic() - start
        ok = r.returncode == 0
        ergebnisse.append(Ergebnis(befehl, ok, dauer, "" if ok else auszug(r.stdout + "\n" + r.stderr)))
        if stopp and not ok:
            break
    zeilen = []
    for e in ergebnisse:
        zeichen = "ok" if e.ok else "FEHLER"
        zeilen.append(f"{zeichen:6} {e.befehl} ({e.sekunden:.1f} s)")
        if not e.ok:
            zeilen += ["       " + z for z in e.auszug.splitlines()]
    fehler = sum(not e.ok for e in ergebnisse)
    zeilen.append(f"Prüfung {stufe}: {len(ergebnisse) - fehler} ok, {fehler} Fehler")
    bericht = "\n".join(zeilen)
    if als_json:
        melde(json.dumps([e.__dict__ for e in ergebnisse], ensure_ascii=False))
    elif not leise:
        melde(bericht)
    return fehler == 0, bericht


# ---------------------------------------------------------------- Links der gebauten Seite

RE_LINK = re.compile(r'(?:href|src)="([^"#?]*)')
EXTERN = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//)", re.IGNORECASE)


def kaputte_links(ordner: Path, basis: str = "/", ohne: tuple[str, ...] = ("hilfe",)) -> list[str]:
    """Findet interne Links und Bilder in _site, deren Ziel fehlt. Das Wiki prüft Quartz selbst."""
    basis = "/" + basis.strip("/") + "/" if basis.strip("/") else "/"
    fehler = set()
    for datei in ordner.rglob("*.html"):
        relativ = datei.relative_to(ordner)
        if relativ.parts and relativ.parts[0] in ohne:
            continue
        for ziel in RE_LINK.findall(datei.read_text(encoding="utf-8", errors="replace")):
            if not ziel or EXTERN.match(ziel):
                continue
            if ziel.startswith("/"):
                rest = ziel[len(basis):] if ziel.startswith(basis) else ziel.lstrip("/")
                pfad = ordner / rest
            else:
                pfad = datei.parent / ziel
            pfad = Path(os.path.normpath(pfad))
            teile = pfad.relative_to(ordner).parts if pfad.is_relative_to(ordner) else ()
            if teile and teile[0] in ohne:
                continue
            kandidaten = [pfad, pfad / "index.html", pfad.with_suffix(".html")]
            if not any(k.is_file() for k in kandidaten):
                fehler.add(f"{relativ.as_posix()}: {ziel}")
    return sorted(fehler)


def links(ordner: str = "_site", basis: str | None = None, auch_wiki: bool = False) -> bool:
    ziel = wurzel() / ordner
    if not ziel.exists():
        melde(f"{ordner} fehlt, erst bauen (pnpm build).")
        return False
    gefunden = kaputte_links(ziel, basis if basis is not None else os.environ.get("BASE_PATH", "/"), () if auch_wiki else ("hilfe",))
    if gefunden:
        melde(f"{len(gefunden)} kaputte Links:\n" + "\n".join(f"  {f}" for f in gefunden[:30]))
        return False
    melde(f"Links in {ordner} in Ordnung.")
    return True


# ---------------------------------------------------------------- Doku-Pflicht

CODE = ("apps/", "packages/", "parlier/", ".github/workflows/", ".claude/")
DOKU = ("CHANGELOG.md", "docs/")


def doku_fehlt(dateien: list[str], labels: list[str]) -> str | None:
    """Gibt eine Meldung zurück, wenn Code geändert wurde, aber weder CHANGELOG noch docs/."""
    if "keine-doku" in labels:
        return None
    code = [d for d in dateien if d.startswith(CODE)]
    doku = [d for d in dateien if d.startswith(DOKU)]
    if code and not doku:
        beispiele = ", ".join(code[:3])
        return (
            f"Code geändert ({beispiele}{' ...' if len(code) > 3 else ''}), aber kein Eintrag in CHANGELOG.md "
            "oder docs/. Chronist beauftragen oder Label 'keine-doku' setzen."
        )
    return None


def doku_check(basis: str | None = None) -> bool:
    basis = basis or f"origin/{konfig()['zweige']['sammel']}"
    dateien = git("diff", "--name-only", f"{basis}...HEAD").splitlines()
    roh = os.environ.get("PR_LABELS", "")
    try:
        labels = [l if isinstance(l, str) else l.get("name", "") for l in json.loads(roh)] if roh.startswith("[") else roh.split(",")
    except json.JSONDecodeError:
        labels = []
    meldung = doku_fehlt(dateien, [l.strip() for l in labels])
    if meldung:
        melde(meldung)
        return False
    melde(f"Doku-Pflicht erfüllt ({len(dateien)} Dateien geändert).")
    return True
