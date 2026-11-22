"""Hooks für Claude Code (eingetragen in .claude/settings.json).

  start        SessionStart: kurzer Lagebericht statt teurer Erkundung
  formatieren  PostToolUse nach Edit/Write: Datei mit Biome formatieren, still
  abschluss    Stop: schnelle Prüfung, wenn sich Code geändert hat. Exit 2 schickt Claude zurück an die Arbeit
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from .basis import git, wurzel
from .pruefen import pruefen

FORMAT_ENDUNGEN = {".ts", ".tsx", ".js", ".mjs", ".jsx", ".json", ".css", ".astro"}
CODE_ORDNER = ("apps/", "packages/")


def _eingabe() -> dict:
    try:
        roh = sys.stdin.read()
        return json.loads(roh) if roh.strip() else {}
    except (json.JSONDecodeError, OSError):
        return {}


def formatieren() -> int:
    daten = _eingabe()
    pfad = (daten.get("tool_input") or {}).get("file_path")
    biome = wurzel() / "node_modules" / ".bin" / "biome"
    if not pfad or Path(pfad).suffix not in FORMAT_ENDUNGEN or not biome.exists():
        return 0
    import subprocess

    subprocess.run([str(biome), "format", "--write", pfad], capture_output=True, cwd=wurzel())
    return 0


def _code_stand() -> str | None:
    """Fingerabdruck der geänderten Code-Dateien. None, wenn kein Code geändert ist."""
    zeilen = [z for z in git("status", "--porcelain", pruefen=False).splitlines() if z[3:].startswith(CODE_ORDNER)]
    if not zeilen:
        return None
    h = hashlib.sha1()
    for zeile in sorted(zeilen):
        datei = wurzel() / zeile[3:].strip().strip('"')
        h.update(zeile.encode())
        if datei.is_file():
            h.update(datei.read_bytes())
    return h.hexdigest()


def abschluss() -> int:
    daten = _eingabe()
    if daten.get("stop_hook_active"):
        return 0
    stand = _code_stand()
    if stand is None or not (wurzel() / "node_modules").exists():
        return 0
    merker = wurzel() / ".bauhuette" / "letzte-pruefung"
    if merker.exists() and merker.read_text().strip() == stand:
        return 0
    ok, bericht = pruefen("schnell", leise=True)
    if ok:
        merker.parent.mkdir(parents=True, exist_ok=True)
        merker.write_text(stand)
        return 0
    print("Die schnelle Prüfung schlägt fehl. Bitte beheben oder kurz begründen, warum nicht:\n" + bericht, file=sys.stderr)
    return 2


def start() -> int:
    from .status import lagebericht

    print(lagebericht(kurz=True))
    return 0
