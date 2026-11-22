"""Ralph: arbeitet offene Issues ab, während niemand zuschaut (AFK).

Die Schleife selbst kostet keine Tokens, sie ist Python. Pro Issue:
  1. nächstes Issue mit Label 'bereit' und erledigten Abhängigkeiten holen
  2. Zweig anlegen, Label 'in-arbeit', Kontext zusammenstellen
  3. Claude headless mit dem Skill 'umsetzen' starten
  4. volle Prüfung; bei Fehlern eine Nachbesserungsrunde in derselben Sitzung
  5. grün: Commit, Push, Pull Request nach develop. Rot: Label 'braucht-hilfe', Zwischenstand pushen
Läuft nur im Sandbox-Container mit allen Rechten (BAUHUETTE_SANDBOX=1), sonst mit acceptEdits.
"""

from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path

from . import issues as iss
from .basis import Abbruch, git, hat_programm, konfig, kuerzen, lauf, melde, warne, wurzel
from .kontext import zusammenstellen
from .pruefen import pruefen
from .zweig import commit, hat_aenderungen, pull_request, push, zweig_anlegen

AUFTRAG = """Du arbeitest als Parlier der Bauhütte im AFK-Modus. Niemand kann Rückfragen beantworten.
Setze Issue #{nummer} mit dem Skill "umsetzen" vollständig um (TDD, Prüfer, Chronist).
Du bist bereits auf dem Zweig {zweig}. Committe mit `python3 -m parlier commit "..."`.
Pushen und den Pull Request erledigt die Schleife danach, das machst du nicht selbst.
Wenn das Issue ohne Entscheidung von Vale nicht lösbar ist: schreibe die offene Frage mit
`python3 -m parlier issue {nummer} kommentar "..."`, setze nichts Halbes um und beende die Arbeit.

Kontext:

{kontext}
"""

NACHBESSERN = """Die volle Prüfung nach deiner Umsetzung ist fehlgeschlagen:

{fehler}

Behebe die Ursache (nicht die Tests abschwächen) und committe erneut mit parlier."""


def _claude(auftrag: str, k: dict, sitzung: str | None = None) -> dict:
    r = k["ralph"]
    befehl = [r["befehl"], "-p", auftrag, "--model", r["modell"], "--max-turns", str(r["max_runden"]), "--output-format", "json"]
    if sitzung:
        befehl += ["--resume", sitzung]
    if os.environ.get("BAUHUETTE_SANDBOX") == "1":
        befehl.append("--dangerously-skip-permissions")
    else:
        befehl += ["--permission-mode", "acceptEdits"]
    ergebnis = lauf(befehl, pruefen=False, zeitlimit=r["zeitlimit_min"] * 60)
    try:
        daten = json.loads(ergebnis.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError):
        daten = {"is_error": True, "result": kuerzen(ergebnis.stdout + ergebnis.stderr, 20)}
    return daten


def _protokoll(eintrag: dict) -> None:
    ordner = wurzel() / ".bauhuette" / "protokoll"
    ordner.mkdir(parents=True, exist_ok=True)
    datei = ordner / f"ralph-{dt.date.today().isoformat()}.jsonl"
    with datei.open("a", encoding="utf-8") as f:
        f.write(json.dumps(eintrag, ensure_ascii=False) + "\n")


def ralph(max_issues: int | None = None, trocken: bool = False) -> None:
    k = konfig()
    for programm in ("gh", k["ralph"]["befehl"]):
        if not hat_programm(programm) and not trocken:
            raise Abbruch(f"{programm} fehlt. Ralph läuft im Sandbox-Container, siehe docs/technik/zusammenarbeit.md")
    if hat_aenderungen():
        raise Abbruch("Arbeitsbaum ist nicht sauber. Erst committen oder verwerfen.")
    sammel = k["zweige"]["sammel"]
    anzahl = max_issues or k["ralph"]["max_issues"]
    bilanz = []

    for _ in range(anzahl):
        issue = iss.naechstes(k["ralph"]["label"])
        if not issue:
            melde("Kein umsetzbares Issue mehr.")
            break
        nummer, titel = issue["number"], issue["title"]
        melde(f"-> #{nummer} {titel}")
        if trocken:
            bilanz.append((nummer, "trocken"))
            break
        iss.labels_aendern(nummer, hinzu=["in-arbeit"], weg=[k["ralph"]["label"]])
        git("switch", "-q", sammel)
        zweig = zweig_anlegen(nummer, titel)
        start = dt.datetime.now()
        daten = _claude(AUFTRAG.format(nummer=nummer, zweig=zweig, kontext=zusammenstellen(nummer)), k)
        kosten = float(daten.get("total_cost_usd") or 0)
        ok, bericht = pruefen("voll")
        if not ok and daten.get("session_id"):
            nach = _claude(NACHBESSERN.format(fehler=kuerzen(bericht, 40)), k, sitzung=daten["session_id"])
            kosten += float(nach.get("total_cost_usd") or 0)
            ok, bericht = pruefen("voll")
        if hat_aenderungen():
            commit("Zwischenstand aus Ralph" if not ok else f"Issue #{nummer} umgesetzt", nummer)
        hat_commits = bool(git("log", "--oneline", f"origin/{sammel}..HEAD", pruefen=False))
        dauer = int((dt.datetime.now() - start).total_seconds() / 60)
        zusammenfassung = kuerzen(str(daten.get("result", "")).strip(), 25)
        if ok and hat_commits:
            url = pull_request(titel=titel, was=zusammenfassung, issue=nummer)
            iss.kommentieren(nummer, f"Ralph: umgesetzt in {dauer} min, Kosten ca. {kosten:.2f} USD. PR: {url}")
            status = "pr"
        else:
            if hat_commits:
                push()
            iss.labels_aendern(nummer, hinzu=["braucht-hilfe"], weg=["in-arbeit"])
            iss.kommentieren(nummer, f"Ralph kommt nicht weiter (Prüfung {'grün' if ok else 'rot'}, "
                                     f"Commits: {'ja' if hat_commits else 'nein'}). Zweig: `{zweig}`\n\n{zusammenfassung}")
            status = "braucht-hilfe"
        _protokoll({"issue": nummer, "zweig": zweig, "status": status, "minuten": dauer, "kosten_usd": round(kosten, 3)})
        bilanz.append((nummer, status))
        git("switch", "-q", sammel)

    if bilanz:
        melde("Bilanz: " + ", ".join(f"#{n} {s}" for n, s in bilanz))
    else:
        warne("Nichts umgesetzt.")
