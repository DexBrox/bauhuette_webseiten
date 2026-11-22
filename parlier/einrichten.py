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


def einrichten(name: str | None, repo: str | None, profil: str | None, domain: str | None, mit_labels: bool = True) -> None:
    datei = wurzel() / "bauhuette.toml"
    text = datei.read_text(encoding="utf-8")
    if profil and profil not in {"statisch", "fullstack"}:
        raise Abbruch("Profil ist 'statisch' oder 'fullstack'.")
    for schluessel, wert in (("name", name), ("repo", repo), ("profil", profil), ("domain", domain)):
        if wert is not None:
            text = _setze(text, "projekt", schluessel, wert)
    datei.write_text(text, encoding="utf-8")
    k = konfig()

    wiki = wurzel() / k["wiki"]["konfig"]
    if wiki.exists():
        w = wiki.read_text(encoding="utf-8")
        w = re.sub(r"^(  pageTitle:).*$", rf'\1 "Hilfe {k["projekt"]["name"]}"', w, count=1, flags=re.MULTILINE)
        if k["projekt"]["domain"]:
            w = re.sub(r"^(  baseUrl:).*$", rf"\1 {k['projekt']['domain']}/hilfe", w, count=1, flags=re.MULTILINE)
        wiki.write_text(w, encoding="utf-8")

    if k["projekt"]["profil"] == "statisch" and (wurzel() / "apps" / "api").exists():
        shutil.rmtree(wurzel() / "apps" / "api")
        melde("Profil statisch: apps/api entfernt (kommt bei Bedarf aus der Vorlage zurück).")

    if mit_labels and hat_programm("gh"):
        labels()
    if not git("rev-parse", "--verify", "-q", k["zweige"]["sammel"], pruefen=False):
        git("branch", k["zweige"]["sammel"])
        melde(f"Zweig {k['zweige']['sammel']} angelegt.")
    if hat_programm("pnpm"):
        lauf(["pnpm", "install", "--silent"], pruefen=False)
    melde(
        "Eingerichtet. Jetzt sichern: git add -A && git commit -m \"Projekt eingerichtet\" && git push "
        f"&& git push -u origin {k['zweige']['sammel']}\n"
        "Noch von Hand auf GitHub: Settings, Pages, Source: GitHub Actions; "
        "Secrets SFTP_HOST, SFTP_USER, SFTP_PASSWORD, SFTP_PFAD; optional CLAUDE_CODE_OAUTH_TOKEN. "
        "Details: docs/technik/betrieb.md"
    )
