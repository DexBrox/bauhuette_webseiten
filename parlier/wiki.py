"""Baut das Hilfe-Wiki aus docs/hilfe mit Quartz (https://quartz.jzhao.xyz).

Vorbereiten: Die Seiten werden in einen Arbeitsordner kopiert. Dabei
  - wird das Frontmatter der Vault-Konvention (titel, erstellt) auf Quartz übersetzt (title, created),
  - bekommt jede Seite das Änderungsdatum aus Git (modified),
  - bekommt jede Seite unten die Wikipedia-Werkzeuge: Seite bearbeiten, Versionsgeschichte, Diskussion.
Bauen: Quartz wird in der eingestellten Version nach .cache/quartz geholt und baut nach _site/hilfe.
"""

from __future__ import annotations

import os
import re
import shutil
from pathlib import Path
from urllib.parse import quote

from .basis import Abbruch, frontmatter, git, hat_programm, konfig, kuerzen, lauf, melde, wurzel

ARBEIT = ".cache/wiki-inhalt"
QUARTZ = ".cache/quartz"
QUARTZ_REPO = "https://github.com/jackyzha0/quartz.git"


def werkzeugleiste(repo: str, zweig: str, quellpfad: str, titel: str) -> str:
    basis = f"https://github.com/{repo}"
    thema = quote(f"[Wiki] {titel}")
    return (
        "\n\n---\n\n<div class=\"seitenwerkzeuge\">\n\n"
        f"[Seite bearbeiten]({basis}/edit/{zweig}/{quellpfad}) · "
        f"[Versionsgeschichte]({basis}/commits/{zweig}/{quellpfad}) · "
        f"[Diskussion]({basis}/issues/new?template=wiki.yml&title={thema})"
        "\n\n</div>\n"
    )


def seite_umschreiben(text: str, quellpfad: str, repo: str, zweig: str, geaendert: str | None) -> str:
    werte, rumpf = frontmatter(text)
    titel = werte.get("title") or werte.get("titel") or Path(quellpfad).stem.replace("-", " ").capitalize()
    zusatz = []
    if "title" not in werte:
        zusatz.append(f'title: "{titel}"')
    if "created" not in werte and werte.get("erstellt"):
        zusatz.append(f"created: {werte['erstellt']}")
    if "modified" not in werte and geaendert:
        zusatz.append(f"modified: {geaendert}")
    if text.startswith("---\n"):
        ende = text.find("\n---", 4)
        kopf = text[4:ende].rstrip("\n")
        neu = "---\n" + kopf + ("\n" + "\n".join(zusatz) if zusatz else "") + "\n---\n\n" + rumpf
    else:
        neu = "---\n" + "\n".join(zusatz) + "\n---\n\n" + text
    if repo:
        neu = neu.rstrip() + werkzeugleiste(repo, zweig, quellpfad, titel)
    return neu


def vorbereiten(zweig: str | None = None) -> Path:
    k = konfig()
    quelle = wurzel() / k["wiki"]["quelle"]
    if not quelle.exists():
        raise Abbruch(f"Wiki-Quelle fehlt: {quelle}")
    ziel = wurzel() / ARBEIT
    shutil.rmtree(ziel, ignore_errors=True)
    repo = k["projekt"].get("repo", "")
    zweig = zweig or os.environ.get("GITHUB_REF_NAME") or k["zweige"]["sammel"]
    anzahl = 0
    for datei in quelle.rglob("*"):
        if datei.is_dir():
            continue
        relativ = datei.relative_to(quelle)
        neu = ziel / relativ
        neu.parent.mkdir(parents=True, exist_ok=True)
        if datei.suffix != ".md":
            shutil.copy2(datei, neu)
            continue
        quellpfad = datei.relative_to(wurzel()).as_posix()
        geaendert = git("log", "-1", "--format=%cs", "--", quellpfad, pruefen=False) or None
        neu.write_text(seite_umschreiben(datei.read_text(encoding="utf-8"), quellpfad, repo, zweig, geaendert), encoding="utf-8")
        anzahl += 1
    melde(f"Wiki vorbereitet: {anzahl} Seiten in {ARBEIT}")
    return ziel


def quartz_holen(version: str) -> Path:
    ordner = wurzel() / QUARTZ
    marke = ordner / ".bauhuette-version"
    if not (marke.exists() and marke.read_text().strip() == version):
        shutil.rmtree(ordner, ignore_errors=True)
        ordner.parent.mkdir(parents=True, exist_ok=True)
        lauf(["git", "clone", "-q", "--depth", "1", "--branch", version, QUARTZ_REPO, str(ordner)])
        lauf(["npm", "ci", "--no-audit", "--no-fund", "--loglevel=error"], ordner=ordner)
        marke.write_text(version)
        melde(f"Quartz {version} geholt")
    return ordner


def bauen(zweig: str | None = None) -> Path:
    if not hat_programm("npm"):
        raise Abbruch("npm fehlt (Node 22 installieren).")
    k = konfig()
    inhalt = vorbereiten(zweig)
    quartz = quartz_holen(k["wiki"]["quartz"])
    konfig_text = (wurzel() / k["wiki"]["konfig"]).read_text(encoding="utf-8")
    if domain := k["projekt"].get("domain"):
        konfig_text = konfig_text.replace("      links: {}", f"      links:\n        Zur Webseite: https://{domain}/", 1)
    (quartz / "quartz.config.yaml").write_text(konfig_text, encoding="utf-8")
    stil = wurzel() / k["wiki"]["stil"]
    if stil.exists():
        shutil.copy2(stil, quartz / "quartz" / "styles" / "custom.scss")
    ziel = wurzel() / k["wiki"]["ziel"]
    shutil.rmtree(ziel, ignore_errors=True)
    lauf(["npx", "quartz", "plugin", "install", "--from-config"], ordner=quartz)
    ergebnis = lauf(["npx", "quartz", "build", "-d", str(inhalt), "-o", str(ziel)], ordner=quartz)
    ausgabe = re.sub(r"\x1b\[[0-9;]*m", "", ergebnis.stdout + ergebnis.stderr)
    erwartet = len(list(inhalt.rglob("*.md")))
    seiten = len(list(ziel.rglob("*.html"))) if ziel.exists() else 0
    if seiten < erwartet:
        raise Abbruch(f"Wiki unvollständig: {seiten} HTML-Seiten für {erwartet} Markdown-Seiten. Quartz meldet:\n{kuerzen(ausgabe, 40)}")
    melde(f"Wiki gebaut: {seiten} HTML-Seiten aus {erwartet} Markdown-Seiten in {ziel.relative_to(wurzel())}")
    return ziel
