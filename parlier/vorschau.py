"""Testseiten je Zweig auf GitHub Pages (übernommen aus Kulturland Hohenlohe).

  /                 develop
  /zweig/<name>/    jeder andere Zweig, z. B. /zweig/feature-12-karte/
  /zweig/           Übersicht aller Testseiten
"""

from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import shutil
from pathlib import Path

from .basis import konfig, melde

INFO = "_vorschau.json"
UNTER = "zweig"

STIL = (
    "position:fixed;left:12px;bottom:12px;z-index:2147483647;pointer-events:none;"
    "background:#9c2f1f;color:#fff;font:600 13px/1.4 system-ui,sans-serif;padding:7px 12px;"
    "border-radius:8px;box-shadow:0 4px 14px rgba(0,0,0,.25);max-width:min(90vw,420px)"
)


def kurzname(zweig: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", zweig.lower()).strip("-")[:60] or "zweig"


def pfad_fuer(zweig: str) -> str:
    return "" if zweig == konfig()["zweige"]["sammel"] else f"{UNTER}/{kurzname(zweig)}/"


def kennzeichnen(ordner: Path, zweig: str) -> int:
    """Sperrt Suchmaschinen und setzt ein Schild 'Vorschau' auf jede Seite."""
    zweig = re.sub(r'[<>&"]', "", zweig)
    domain = konfig()["projekt"].get("domain") or "der echten Adresse"
    meta = '<meta name="robots" content="noindex, nofollow">'
    anzahl = 0
    for datei in ordner.rglob("*.html"):
        text = datei.read_text(encoding="utf-8", errors="replace")
        ist_redaktion = "admin" in datei.relative_to(ordner).parts
        hinweis = (
            f"Vorschau (Zweig {zweig}). In dieser Redaktion nichts veröffentlichen."
            if ist_redaktion
            else f"Vorschau (Zweig {zweig}). Die echte Website liegt unter {domain}."
        )
        if 'name="robots"' not in text:
            text = re.sub(r"<head([^>]*)>", lambda m: m.group(0) + meta, text, count=1, flags=re.IGNORECASE)
        schild = f'<div id="vorschau-schild" style="{STIL}">{html.escape(hinweis)}</div>'
        if re.search(r"</body>", text, re.IGNORECASE):
            text = re.sub(r"</body>", schild + "</body>", text, count=1, flags=re.IGNORECASE)
        else:
            text += schild
        datei.write_text(text, encoding="utf-8")
        anzahl += 1
    (ordner / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    for name in (".htaccess", "sitemap.xml"):
        (ordner / name).unlink(missing_ok=True)
    melde(f"Vorschau gekennzeichnet: {anzahl} Seiten, Zweig {zweig}")
    return anzahl


def _leeren(ordner: Path, behalten: set[str]) -> None:
    if not ordner.exists():
        return
    for eintrag in ordner.iterdir():
        if eintrag.name in behalten:
            continue
        if eintrag.is_dir():
            shutil.rmtree(eintrag)
        else:
            eintrag.unlink()


def ablage(aktion: str, zweig: str, ablage_ordner: Path, quelle: Path) -> None:
    haupt = konfig()["zweige"]["sammel"]
    ist_haupt = zweig == haupt
    ziel = ablage_ordner if ist_haupt else ablage_ordner / UNTER / kurzname(zweig)
    ablage_ordner.mkdir(parents=True, exist_ok=True)
    if aktion == "einsetzen":
        _leeren(ziel, {".git", UNTER} if ist_haupt else set())
        shutil.copytree(quelle, ziel, dirs_exist_ok=True)
        (ziel / INFO).write_text(json.dumps({
            "zweig": zweig,
            "stand": dt.datetime.now(dt.timezone.utc).isoformat(),
            "commit": os.environ.get("GITHUB_SHA", "")[:7],
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        melde(f"Testseite für {zweig} eingesetzt: /{pfad_fuer(zweig)}")
    elif ist_haupt:
        melde(f"{haupt} wird nicht entfernt.")
    else:
        shutil.rmtree(ziel, ignore_errors=True)
        melde(f"Testseite für {zweig} entfernt.")
    uebersicht(ablage_ordner, haupt)


def _lesen(ordner: Path) -> dict | None:
    try:
        return json.loads((ordner / INFO).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def uebersicht(ablage_ordner: Path, haupt: str) -> None:
    eintraege = []
    if info := _lesen(ablage_ordner):
        eintraege.append({**info, "link": "../"})
    unter = ablage_ordner / UNTER
    if unter.exists():
        for ordner in sorted(p for p in unter.iterdir() if p.is_dir()):
            if info := _lesen(ordner):
                eintraege.append({**info, "link": f"{ordner.name}/"})
    rest = sorted((e for e in eintraege if e["zweig"] != haupt), key=lambda e: e["stand"], reverse=True)
    eintraege = [e for e in eintraege if e["zweig"] == haupt] + rest
    zeilen = "\n".join(
        f'<tr><td><a href="{html.escape(e["link"])}">{html.escape(e["zweig"])}</a></td>'
        f'<td>{html.escape(e["stand"][:16].replace("T", " "))} UTC</td><td><code>{html.escape(e["commit"])}</code></td></tr>'
        for e in eintraege
    )
    name = html.escape(konfig()["projekt"]["name"])
    unter.mkdir(parents=True, exist_ok=True)
    (unter / "index.html").write_text(f"""<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow"><title>Testseiten {name}</title>
<style>body{{font:16px/1.5 system-ui,sans-serif;margin:0;padding:24px 16px;color:#222;background:#f6f6f3}}
main{{max-width:720px;margin:0 auto}}table{{width:100%;border-collapse:collapse;background:#fff}}
th,td{{text-align:left;padding:10px 12px;border-bottom:1px solid #e3e3dc}}a{{font-weight:600}}</style></head>
<body><main><h1>Testseiten {name}</h1><p>Eine Testseite je Zweig.</p>
<table><thead><tr><th>Zweig</th><th>Stand</th><th>Commit</th></tr></thead><tbody>
{zeilen or '<tr><td colspan="3">Noch keine Testseite.</td></tr>'}
</tbody></table></main></body></html>
""", encoding="utf-8")
    melde(f"Übersicht: {len(eintraege)} Testseiten")
