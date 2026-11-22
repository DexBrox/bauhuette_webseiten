"""Ein neues Projekt aus der Vorlage einrichten und die Labels auf GitHub pflegen."""

from __future__ import annotations

import re
import shutil

from .basis import Abbruch, gh, git, hat_programm, konfig, lauf, melde, wurzel


def _setze(text: str, abschnitt: str, schluessel: str, wert: str) -> str:
    muster = re.compile(rf"(\[{abschnitt}\][^\[]*?^{schluessel}\s*=\s*)\"[^\"]*\"", re.MULTILINE | re.DOTALL)
    if not muster.search(text):
        raise Abbruch(f"In bauhuette.toml fehlt {abschnitt}.{schluessel}")
    return muster.sub(lambda m: m.group(1) + '"' + wert.replace('"', "") + '"', text, count=1)


def labels() -> int:
    eintraege = konfig().get("label", [])
    for l in eintraege:
        gh("label", "create", l["name"], "--color", l.get("farbe", "ededed"), "--description", l.get("text", ""), "--force")
    melde(f"{len(eintraege)} Labels angelegt oder aktualisiert.")
    return len(eintraege)


PROFILE = {"statisch", "fullstack"}

CHANGELOG_NEU = """# Changelog

Alle nennenswerten Änderungen an {name}. Format nach
[keepachangelog.com](https://keepachangelog.com/de/1.1.0/), Versionen nach [semver.org](https://semver.org/lang/de/).

## [Unreleased]

### Hinzugefügt
- Projekt aus der Vorlage Bauhütte angelegt.
"""


def profil(wert: str) -> None:
    """Legt das Profil fest (Phase 3, Architektur). Bei statisch fällt apps/api weg."""
    if wert not in PROFILE:
        raise Abbruch("Profil ist 'statisch' oder 'fullstack'.")
    datei = wurzel() / "bauhuette.toml"
    datei.write_text(_setze(datei.read_text(encoding="utf-8"), "projekt", "profil", wert), encoding="utf-8")
    api = wurzel() / "apps" / "api"
    if wert == "statisch" and api.exists():
        shutil.rmtree(api)
        melde("Profil statisch: apps/api entfernt (kommt bei Bedarf aus der Vorlage zurück). Danach pnpm install.")
    else:
        melde(f"Profil {wert} eingetragen.")


def einrichten(
    name: str | None,
    repo: str | None,
    profil_wert: str | None,
    domain: str | None,
    mit_labels: bool = True,
    installieren: bool = True,
) -> None:
    """Richtet ein neues Projekt ein. Das Profil bleibt offen, es gehört in die Architektur (parlier profil)."""
    datei = wurzel() / "bauhuette.toml"
    text = datei.read_text(encoding="utf-8")
    for schluessel, wert in (("name", name), ("repo", repo), ("domain", domain)):
        if wert is not None:
            text = _setze(text, "projekt", schluessel, wert)
    datei.write_text(text, encoding="utf-8")
    if profil_wert:
        profil(profil_wert)
    k = konfig()

    changelog = wurzel() / "CHANGELOG.md"
    if name and changelog.exists() and re.search(r"^## \[\d+\.\d+\.\d+\]", changelog.read_text(encoding="utf-8"), re.MULTILINE):
        changelog.write_text(CHANGELOG_NEU.format(name=name), encoding="utf-8")
        melde("CHANGELOG neu begonnen.")

    wiki = wurzel() / k["wiki"]["konfig"]
    if wiki.exists():
        w = wiki.read_text(encoding="utf-8")
        w = re.sub(r"^(  pageTitle:).*$", rf'\1 "Hilfe {k["projekt"]["name"]}"', w, count=1, flags=re.MULTILINE)
        if k["projekt"]["domain"]:
            w = re.sub(r"^(  baseUrl:).*$", rf"\1 {k['projekt']['domain']}/hilfe", w, count=1, flags=re.MULTILINE)
        wiki.write_text(w, encoding="utf-8")

    if mit_labels and hat_programm("gh"):
        labels()
    if not git("rev-parse", "--verify", "-q", k["zweige"]["sammel"], pruefen=False):
        git("branch", k["zweige"]["sammel"])
        melde(f"Zweig {k['zweige']['sammel']} angelegt.")
    if installieren and hat_programm("pnpm"):
        lauf(["pnpm", "install", "--silent"], pruefen=False)
    melde(
        "Eingerichtet. Jetzt sichern: git add -A && git commit -m \"Projekt eingerichtet\" && git push "
        f"&& git push -u origin {k['zweige']['sammel']}\n"
        "Noch von Hand auf GitHub: Settings, Pages, Source: GitHub Actions; "
        "Secrets SFTP_HOST, SFTP_USER, SFTP_PASSWORD, SFTP_PFAD; optional CLAUDE_CODE_OAUTH_TOKEN. "
        "Details: docs/technik/betrieb.md"
    )
