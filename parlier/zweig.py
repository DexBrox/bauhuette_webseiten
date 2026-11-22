"""Git-Arbeit: Zweige, Commits, Push, Pull Requests. Setzt die Git-Regel technisch durch:
Agenten arbeiten nur auf feature/... und fix/..., nie direkt auf main oder develop."""

from __future__ import annotations

import re

from .basis import Abbruch, gh, git, hat_programm, konfig, kurzname, lauf, melde

GESPERRT_IMMER = {"vorschau-ablage"}


def aktueller_zweig() -> str:
    return git("rev-parse", "--abbrev-ref", "HEAD")


def geschuetzte_zweige() -> set[str]:
    z = konfig()["zweige"]
    return {z["haupt"], z["sammel"], *GESPERRT_IMMER}


def pruefe_arbeitszweig(zweig: str | None = None) -> str:
    zweig = zweig or aktueller_zweig()
    if zweig in geschuetzte_zweige():
        raise Abbruch(
            f"Auf '{zweig}' wird nicht direkt gearbeitet. Erst einen Arbeitszweig anlegen: "
            "python3 -m parlier zweig <issue-nummer>"
        )
    return zweig


def issue_aus_zweig(zweig: str | None = None) -> int | None:
    m = re.search(r"(?:^|/)(\d+)-", zweig or aktueller_zweig())
    return int(m.group(1)) if m else None


def hat_remote() -> bool:
    return bool(git("remote", pruefen=False))


OHNE_ISSUE = "Ohne Issue keine Arbeit. Erst anlegen: python3 -m parlier issues neu --titel \"...\" --zweig"


def zweig_anlegen(nummer: int | None, titel: str | None = None, art: str = "feature") -> str:
    if nummer is None:
        raise Abbruch(OHNE_ISSUE)
    k = konfig()["zweige"]
    praefix = k["fix"] if art == "fix" else k["feature"]
    if titel is None and hat_programm("gh"):
        try:
            titel = gh("issue", "view", str(nummer), "--json", "title", "--jq", ".title")
        except Abbruch:
            titel = None
    teile = [str(nummer)] + ([kurzname(titel)] if titel else [])
    name = praefix + "-".join(teile)
    basis = k["sammel"]
    if hat_remote():
        git("fetch", "-q", "origin", basis, pruefen=False)
        start = f"origin/{basis}" if git("rev-parse", "--verify", "-q", f"origin/{basis}", pruefen=False) else basis
    else:
        start = basis
    vorhanden = git("rev-parse", "--verify", "-q", name, pruefen=False)
    if vorhanden:
        git("switch", "-q", name)
        melde(f"Zweig {name} (vorhanden)")
    else:
        git("switch", "-q", "-c", name, start)
        melde(f"Zweig {name} angelegt von {start}")
    return name


def hat_aenderungen() -> bool:
    return bool(git("status", "--porcelain"))


def commit(nachricht: str, issue: int | None = None) -> str | None:
    zweig = pruefe_arbeitszweig()
    if not hat_aenderungen():
        melde("Nichts zu committen.")
        return None
    issue = issue or issue_aus_zweig(zweig)
    k = konfig()["zweige"]
    if not issue and zweig.startswith((k["feature"], k["fix"])):
        raise Abbruch(OHNE_ISSUE)
    betreff, _, rest = nachricht.partition("\n")
    if issue and f"#{issue}" not in betreff:
        nachricht = f"{betreff} (#{issue})" + (f"\n{rest}" if rest else "")
    git("add", "-A")
    git("commit", "-q", "-m", nachricht)
    kurz = git("rev-parse", "--short", "HEAD")
    melde(f"Commit {kurz} auf {zweig}: {nachricht.splitlines()[0]}")
    return kurz


def push() -> str:
    zweig = pruefe_arbeitszweig()
    if not hat_remote():
        raise Abbruch("Kein Remote eingerichtet (git remote add origin ...).")
    lauf(["git", "-c", "push.negotiate=true", "push", "-q", "-u", "origin", zweig])
    melde(f"Gepusht: {zweig}")
    return zweig


def aktualisieren() -> None:
    """Holt den neuesten Stand von develop in den Arbeitszweig."""
    zweig = pruefe_arbeitszweig()
    basis = konfig()["zweige"]["sammel"]
    git("fetch", "-q", "origin", basis)
    ergebnis = lauf(["git", "merge", "--no-edit", "-q", f"origin/{basis}"], pruefen=False)
    if ergebnis.returncode != 0:
        konflikte = git("diff", "--name-only", "--diff-filter=U", pruefen=False)
        raise Abbruch(f"Konflikt beim Aktualisieren von {zweig}. Betroffene Dateien:\n{konflikte}")
    melde(f"{zweig} ist auf dem Stand von {basis}.")


PR_TEXT = """## Was ändert sich

{was}

{bezug}

## Prüfen

- [ ] Testseite angesehen (Link kommt als Kommentar vom Vorschau-Workflow)
- [ ] Am Handy angesehen (schmales Fenster reicht)
- [ ] CHANGELOG und Wiki angepasst (der Prüf-Workflow kontrolliert das)
"""


def pr_anlegen(basis: str, zweig: str, titel: str, text: str, entwurf: bool) -> str:
    """Öffnet den PR mit gh pr create. Ist GraphQL gesperrt (Cloud-Sitzungen), über die REST-API."""
    argumente = ["pr", "create", "--base", basis, "--head", zweig, "--title", titel, "--body-file", "-"]
    if entwurf:
        argumente.append("--draft")
    try:
        return gh(*argumente, eingabe=text)
    except Abbruch as fehler:
        if "GraphQL" not in str(fehler):
            raise
    rest = ["api", f"repos/{konfig()['projekt']['repo']}/pulls", "-f", f"title={titel}", "-f", f"head={zweig}",
            "-f", f"base={basis}", "-F", "body=@-", "--jq", ".html_url"]
    if entwurf:
        rest += ["-F", "draft=true"]
    return gh(*rest, eingabe=text)


def pull_request(
    titel: str | None = None, was: str = "", issue: int | None = None, entwurf: bool = False, basis: str | None = None
) -> str:
    """Pusht und öffnet einen PR nach develop. basis=main nur für Notfälle (Kurzweg)."""
    zweig = pruefe_arbeitszweig()
    issue = issue or issue_aus_zweig(zweig)
    push()
    if titel is None:
        titel = git("log", "-1", "--format=%s")
    bezug = f"Closes #{issue}" if issue else ""
    text = PR_TEXT.format(was=was or "Siehe Commits.", bezug=bezug)
    url = pr_anlegen(basis or konfig()["zweige"]["sammel"], zweig, titel, text, entwurf)
    if issue:
        from .issues import labels_aendern

        labels_aendern(issue, hinzu=["in-review"], weg=["in-arbeit"])
    melde(f"Pull Request: {url}")
    return url
