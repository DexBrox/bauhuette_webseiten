"""Kommandozeile: python3 -m parlier <befehl>. Jeder Befehl gibt nur wenige Zeilen aus."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .basis import Abbruch, warne

HILFE = """Parlier: die Handarbeit der Bauhütte, damit Claude keine Tokens dafür braucht.

Arbeit an Issues:
  zweig <nr> [--fix]          Arbeitszweig feature/<nr>-titel von develop anlegen
  commit "Nachricht"          alles committen, Issue-Nummer aus dem Zweig anhängen
  push                        Arbeitszweig pushen
  pr [--titel T] [--was W]    pushen und Pull Request nach develop öffnen
  aktualisieren               develop in den Arbeitszweig holen
  kontext <nr>                Kontext für einen Subagenten zusammenstellen
  issues anlegen <datei.json> Issues aus einem Zerlegungs-Entwurf anlegen [--trocken]
  issues naechstes            das nächste umsetzbare Issue zeigen
  issue <nr> label +a -b      Labels ändern
  issue <nr> kommentar "Text" Kommentar schreiben
  ralph [--max N] [--trocken] Issues AFK abarbeiten (nur im Sandbox-Container)

Prüfen und Doku:
  pruefen [schnell|voll]      Lint, Typen, Tests, Build mit kurzer Fehlerausgabe
  doku-check [--basis REF]    Doku-Pflicht für Pull Requests
  links [_site] [--basis /x/] kaputte interne Links und Bilder in der gebauten Seite
  wiki [--nur-vorbereiten]    Hilfe-Wiki mit Quartz bauen
  status                      Lagebericht und nächster Schritt

Betrieb (Vale):
  einrichten --name --repo --profil --domain   neues Projekt aus der Vorlage
  labels                      Labels aus bauhuette.toml auf GitHub anlegen
  release X.Y.Z [--abschliessen] [--titel T]   Release vorbereiten bzw. abschließen
  release-notiz X.Y.Z [datei] Release-Text aus dem CHANGELOG
  vorschau kennzeichnen <ordner> <zweig>
  vorschau einsetzen|entfernen <zweig> <ablage> [--quelle _site]
  ueberwachen [--issue]       Live-Seite und Zertifikat prüfen
  hook start|formatieren|abschluss   (für Claude Code)
"""


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="parlier", description=HILFE, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="befehl")

    z = s.add_parser("zweig")
    z.add_argument("nummer", type=int, nargs="?")
    z.add_argument("--titel")
    z.add_argument("--fix", action="store_true")

    c = s.add_parser("commit")
    c.add_argument("nachricht")
    c.add_argument("--issue", type=int)

    s.add_parser("push")
    s.add_parser("aktualisieren")

    pr = s.add_parser("pr")
    pr.add_argument("--titel")
    pr.add_argument("--was", default="")
    pr.add_argument("--issue", type=int)
    pr.add_argument("--entwurf", action="store_true")
    pr.add_argument("--basis", help="Ziel des PR, Standard develop. main nur im Notfall")

    k = s.add_parser("kontext")
    k.add_argument("nummer", type=int)

    i = s.add_parser("issues")
    i.add_argument("aktion", choices=["anlegen", "naechstes"])
    i.add_argument("datei", nargs="?")
    i.add_argument("--trocken", action="store_true")

    e = s.add_parser("issue")
    e.add_argument("nummer", type=int)
    e.add_argument("aktion", choices=["label", "kommentar"])
    e.add_argument("werte", nargs="+")

    r = s.add_parser("ralph")
    r.add_argument("--max", type=int)
    r.add_argument("--trocken", action="store_true")

    pf = s.add_parser("pruefen")
    pf.add_argument("stufe", nargs="?", default="voll", choices=["schnell", "voll"])
    pf.add_argument("--stopp", action="store_true")
    pf.add_argument("--json", action="store_true")

    d = s.add_parser("doku-check")
    d.add_argument("--basis")

    lk = s.add_parser("links")
    lk.add_argument("ordner", nargs="?", default="_site")
    lk.add_argument("--basis", help="Basispfad der Seite, Standard BASE_PATH oder /")
    lk.add_argument("--auch-wiki", action="store_true")

    w = s.add_parser("wiki")
    w.add_argument("--nur-vorbereiten", action="store_true")
    w.add_argument("--zweig")

    s.add_parser("status")
    s.add_parser("labels")

    ei = s.add_parser("einrichten")
    ei.add_argument("--name")
    ei.add_argument("--repo")
    ei.add_argument("--profil", choices=["statisch", "fullstack"])
    ei.add_argument("--domain")
    ei.add_argument("--ohne-labels", action="store_true")

    rl = s.add_parser("release")
    rl.add_argument("version")
    rl.add_argument("--abschliessen", action="store_true")
    rl.add_argument("--titel", default="")

    rn = s.add_parser("release-notiz")
    rn.add_argument("version")
    rn.add_argument("datei", nargs="?")

    v = s.add_parser("vorschau")
    v.add_argument("aktion", choices=["kennzeichnen", "einsetzen", "entfernen"])
    v.add_argument("argumente", nargs="+")
    v.add_argument("--quelle", default="_site")

    u = s.add_parser("ueberwachen")
    u.add_argument("--issue", action="store_true")

    h = s.add_parser("hook")
    h.add_argument("art", choices=["start", "formatieren", "abschluss"])
    return p


def ausfuehren(a: argparse.Namespace) -> int:
    if a.befehl == "zweig":
        from .zweig import zweig_anlegen

        zweig_anlegen(a.nummer, a.titel, "fix" if a.fix else "feature")
    elif a.befehl == "commit":
        from .zweig import commit

        commit(a.nachricht, a.issue)
    elif a.befehl == "push":
        from .zweig import push

        push()
    elif a.befehl == "aktualisieren":
        from .zweig import aktualisieren

        aktualisieren()
    elif a.befehl == "pr":
        from .zweig import pull_request

        pull_request(a.titel, a.was, a.issue, a.entwurf, a.basis)
    elif a.befehl == "kontext":
        from .kontext import zusammenstellen

        print(zusammenstellen(a.nummer))
    elif a.befehl == "issues":
        from . import issues

        if a.aktion == "anlegen":
            if not a.datei:
                raise Abbruch("Bitte die Entwurfsdatei angeben.")
            issues.anlegen(Path(a.datei), a.trocken)
        else:
            naechstes = issues.naechstes()
            print(f"#{naechstes['number']} {naechstes['title']}" if naechstes else "Kein umsetzbares Issue.")
    elif a.befehl == "issue":
        from . import issues

        if a.aktion == "kommentar":
            issues.kommentieren(a.nummer, " ".join(a.werte))
        else:
            hinzu = [w[1:] for w in a.werte if w.startswith("+")]
            weg = [w[1:] for w in a.werte if w.startswith("-")]
            issues.labels_aendern(a.nummer, hinzu, weg)
    elif a.befehl == "ralph":
        from .ralph import ralph

        ralph(a.max, a.trocken)
    elif a.befehl == "pruefen":
        from .pruefen import pruefen

        return 0 if pruefen(a.stufe, a.stopp, a.json)[0] else 1
    elif a.befehl == "doku-check":
        from .pruefen import doku_check

        return 0 if doku_check(a.basis) else 1
    elif a.befehl == "links":
        from .pruefen import links

        return 0 if links(a.ordner, a.basis, a.auch_wiki) else 1
    elif a.befehl == "wiki":
        from . import wiki

        wiki.vorbereiten(a.zweig) if a.nur_vorbereiten else wiki.bauen(a.zweig)
    elif a.befehl == "status":
        from .status import lagebericht

        print(lagebericht())
    elif a.befehl == "labels":
        from .einrichten import labels

        labels()
    elif a.befehl == "einrichten":
        from .einrichten import einrichten

        einrichten(a.name, a.repo, a.profil, a.domain, not a.ohne_labels)
    elif a.befehl == "release":
        from . import release

        release.abschliessen(a.version, a.titel) if a.abschliessen else release.vorbereiten(a.version)
    elif a.befehl == "release-notiz":
        from .basis import konfig, wurzel
        from .release import notiz, pruefe_version

        text = notiz((wurzel() / "CHANGELOG.md").read_text(encoding="utf-8"), pruefe_version(a.version), konfig()["projekt"]["repo"])
        if a.datei:
            Path(a.datei).write_text(text, encoding="utf-8")
        else:
            print(text, end="")
    elif a.befehl == "vorschau":
        from . import vorschau

        if a.aktion == "kennzeichnen":
            if len(a.argumente) != 2:
                raise Abbruch("vorschau kennzeichnen <ordner> <zweig>")
            vorschau.kennzeichnen(Path(a.argumente[0]), a.argumente[1])
        else:
            if len(a.argumente) != 2:
                raise Abbruch(f"vorschau {a.aktion} <zweig> <ablage>")
            vorschau.ablage(a.aktion, a.argumente[0], Path(a.argumente[1]), Path(a.quelle))
    elif a.befehl == "ueberwachen":
        from .ueberwachung import ueberwachen

        return 0 if ueberwachen(a.issue) else 1
    elif a.befehl == "hook":
        from . import hooks

        return {"start": hooks.start, "formatieren": hooks.formatieren, "abschluss": hooks.abschluss}[a.art]()
    else:
        print(HILFE)
    return 0


def main(argv: list[str] | None = None) -> int:
    argumente = _parser().parse_args(argv)
    try:
        return ausfuehren(argumente)
    except Abbruch as fehler:
        warne(f"parlier: {fehler}")
        return 1
    except KeyboardInterrupt:
        warne("abgebrochen")
        return 130


if __name__ == "__main__":
    sys.exit(main())
