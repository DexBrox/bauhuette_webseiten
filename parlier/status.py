"""Lagebericht: wo steht das Projekt, was ist der nächste Schritt."""

from __future__ import annotations

from .basis import Abbruch, frontmatter, gh, git, hat_programm, konfig, wurzel

PHASEN = [
    ("docs/projekt/anf.md", "1 Interview", "/interview"),
    ("docs/projekt/prd.md", "2 PRD", "/prd"),
    ("docs/technik/architektur.md", "3 Architektur", "/architektur"),
]


def dokument_status(pfad: str) -> str:
    datei = wurzel() / pfad
    if not datei.exists():
        return "fehlt"
    werte, _ = frontmatter(datei.read_text(encoding="utf-8"))
    return werte.get("status", "entwurf")


def phase() -> tuple[str, str]:
    """Gibt (Phase, nächster Befehl) zurück. Ein Dokument gilt erst mit status: freigegeben als erledigt."""
    for pfad, name, befehl in PHASEN:
        status = dokument_status(pfad)
        if status != "freigegeben":
            hinweis = f"{befehl} ({pfad}: {status})"
            if status == "entwurf" and pfad != "docs/projekt/anf.md":
                hinweis += ", wartet auf deine Freigabe"
            return name, hinweis
    if not (wurzel() / "docs" / "projekt" / "issues.md").exists():
        return "4 Zerlegung", "/zerlegen"
    return "5 Umsetzung und Review", "/umsetzen <nr> oder python3 -m parlier ralph"


def _issue_zahlen() -> str | None:
    if not hat_programm("gh"):
        return None
    try:
        offen = gh("issue", "list", "--state", "open", "--limit", "300", "--json", "labels", als_json=True)
    except Abbruch:
        return None
    zaehler = {"bereit": 0, "in-arbeit": 0, "in-review": 0, "braucht-hilfe": 0, "mensch": 0, "fertig": 0}
    for issue in offen:
        for label in issue.get("labels", []):
            if label["name"] in zaehler:
                zaehler[label["name"]] += 1
    teile = [f"{n} {name}" for name, n in zaehler.items() if n]
    return f"Issues offen: {len(offen)}" + (f" ({', '.join(teile)})" if teile else "")


def lagebericht(kurz: bool = False) -> str:
    k = konfig()
    zweig = git("rev-parse", "--abbrev-ref", "HEAD", pruefen=False) or "?"
    geaendert = len(git("status", "--porcelain", pruefen=False).splitlines())
    name, naechster = phase()
    zeilen = [
        f"Bauhütte: {k['projekt']['name']} (Profil {k['projekt']['profil']})",
        f"Zweig: {zweig}, {geaendert} geänderte Dateien",
        f"Phase: {name}. Nächster Schritt: {naechster}",
    ]
    if not kurz:
        if zahlen := _issue_zahlen():
            zeilen.append(zahlen)
        if hat_programm("gh"):
            try:
                laeufe = gh("run", "list", "--limit", "3", "--json", "name,conclusion,headBranch", als_json=True)
                for l in laeufe:
                    zeilen.append(f"Lauf: {l['name']} auf {l['headBranch']}: {l.get('conclusion') or 'läuft'}")
            except Abbruch:
                pass
    return "\n".join(zeilen)
