"""Releases in zwei Befehlen statt sechs Handgriffen. Nur für Vale: Claude darf das nicht
ausführen (gesperrt in .claude/settings.json), weil ein Release live geht.

  python3 -m parlier release 1.4.0              CHANGELOG versionieren, Release-PR develop -> main
  (PR auf GitHub mit "Create a merge commit" zusammenführen)
  python3 -m parlier release 1.4.0 --abschliessen   Tag setzen, Release anlegen, develop nachziehen
"""

from __future__ import annotations

import datetime as dt
import re
from pathlib import Path

from .basis import Abbruch, gh, git, konfig, lauf, melde, wurzel

RE_VERSION = re.compile(r"^\d+\.\d+\.\d+$")
RE_ABSCHNITT = re.compile(r"^## \[([^\]]+)\][^\n]*\n", re.MULTILINE)


def pruefe_version(version: str) -> str:
    version = version.removeprefix("v")
    if not RE_VERSION.match(version):
        raise Abbruch("Version im Format X.Y.Z angeben, z. B. 1.4.0")
    return version


def abschnitt(text: str, version: str) -> str | None:
    text = text.replace("\r\n", "\n")
    treffer = list(RE_ABSCHNITT.finditer(text))
    for i, m in enumerate(treffer):
        if m.group(1) == version:
            ende = treffer[i + 1].start() if i + 1 < len(treffer) else len(text)
            return text[m.end() : ende].strip()
    return None


def versionieren(text: str, version: str, datum: str) -> str:
    """Macht aus [Unreleased] den Abschnitt der Version und setzt ein leeres [Unreleased] darüber."""
    if abschnitt(text, version) is not None:
        raise Abbruch(f"Version {version} steht schon im CHANGELOG.")
    inhalt = abschnitt(text, "Unreleased")
    if inhalt is None:
        raise Abbruch("Im CHANGELOG fehlt '## [Unreleased]'.")
    if not inhalt.strip():
        raise Abbruch("Unter [Unreleased] steht nichts. Ohne Änderungen kein Release.")
    return text.replace("## [Unreleased]\n", f"## [Unreleased]\n\n## [{version}] - {datum}\n", 1)


def notiz(text: str, version: str, repo: str = "") -> str:
    inhalt = abschnitt(text, version)
    if inhalt is None:
        raise Abbruch(f'Im CHANGELOG fehlt der Abschnitt "## [{version}]".')
    inhalt = re.sub(r"\n(?!\n|- |#{2,} )\s+", " ", inhalt)
    versionen = [m.group(1) for m in RE_ABSCHNITT.finditer(text) if RE_VERSION.match(m.group(1))]
    if repo and version in versionen:
        i = versionen.index(version)
        if i + 1 < len(versionen):
            inhalt += f"\n\nAlle Änderungen: https://github.com/{repo}/compare/v{versionen[i + 1]}...v{version}"
    return inhalt + "\n"


def _changelog() -> Path:
    return wurzel() / "CHANGELOG.md"


def vorbereiten(version: str) -> None:
    version = pruefe_version(version)
    z = konfig()["zweige"]
    if git("rev-parse", "--abbrev-ref", "HEAD") != z["sammel"]:
        raise Abbruch(f"Release nur von '{z['sammel']}' aus: git switch {z['sammel']}")
    if git("status", "--porcelain"):
        raise Abbruch("Es gibt nicht committete Änderungen.")
    git("pull", "-q", "--ff-only")
    datei = _changelog()
    datei.write_text(versionieren(datei.read_text(encoding="utf-8"), version, dt.date.today().isoformat()), encoding="utf-8")
    git("add", "CHANGELOG.md")
    git("commit", "-q", "-m", f"Release {version}")
    lauf(["git", "push", "-q", "origin", z["sammel"]])
    fertige = gh("issue", "list", "--state", "open", "--label", "fertig", "--limit", "200", "--json", "number,title", als_json=True)
    zeilen = "\n".join(f"Closes #{i['number']}" for i in sorted(fertige, key=lambda i: i["number"]))
    text = (
        f"Release {version}. Zusammenführen mit **Create a merge commit** (nicht Squash), "
        f"danach `python3 -m parlier release {version} --abschliessen`.\n\n{zeilen}\n"
    )
    url = gh("pr", "create", "--base", z["haupt"], "--head", z["sammel"], "--title", f"Release {version}", "--body-file", "-", eingabe=text)
    melde(f"Release-PR: {url}\n{len(fertige)} Issues werden beim Zusammenführen geschlossen.")


def abschliessen(version: str, titel: str = "") -> None:
    version = pruefe_version(version)
    z = konfig()["zweige"]
    git("fetch", "-q", "origin", z["haupt"], z["sammel"])
    log = git("log", "--format=%s", "-n", "30", f"origin/{z['haupt']}")
    if f"Release {version}" not in log:
        raise Abbruch(f"'Release {version}' ist noch nicht auf {z['haupt']}. Erst den Release-PR zusammenführen.")
    nachricht = f"{version}: {titel}" if titel else version
    git("tag", "-a", f"v{version}", "-m", nachricht, f"origin/{z['haupt']}")
    lauf(["git", "push", "-q", "origin", f"v{version}"])
    git("switch", "-q", z["sammel"])
    git("pull", "-q", "--ff-only")
    git("merge", "-q", "--no-edit", f"origin/{z['haupt']}")
    lauf(["git", "push", "-q", "origin", z["sammel"]])
    melde(f"v{version} getaggt. Der Release-Workflow legt das GitHub-Release an. {z['sammel']} ist nachgezogen.")
