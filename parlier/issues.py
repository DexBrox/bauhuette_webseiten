"""Issues anlegen, verknüpfen und das nächste umsetzbare finden.

Der Agent schreibt einen Entwurf als JSON (Format: .claude/skills/zerlegen/issue-format.md),
parlier legt daraus die GitHub-Issues in Abhängigkeitsreihenfolge an und schreibt
docs/projekt/issues.md als Übersicht.
"""

from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path
from typing import Any

from .basis import Abbruch, gh, hat_programm, konfig, melde, warne, wurzel

SPERR_LABELS = {"in-arbeit", "in-review", "braucht-hilfe", "mensch", "fertig"}
RE_BLOCKIERT = re.compile(r"^Blockiert von:\s*(.+)$", re.MULTILINE | re.IGNORECASE)


# ---------------------------------------------------------------- Entwurf prüfen


def entwurf_laden(pfad: Path) -> dict[str, Any]:
    try:
        daten = json.loads(pfad.read_text(encoding="utf-8"))
    except FileNotFoundError as fehler:
        raise Abbruch(f"Entwurf nicht gefunden: {pfad}") from fehler
    except json.JSONDecodeError as fehler:
        raise Abbruch(f"Entwurf ist kein gültiges JSON: {fehler}") from fehler
    pruefe_entwurf(daten)
    return daten


def pruefe_entwurf(daten: dict[str, Any]) -> None:
    eintraege = daten.get("issues")
    if not isinstance(eintraege, list) or not eintraege:
        raise Abbruch("Der Entwurf braucht eine nicht leere Liste 'issues'.")
    ids = [e.get("id") for e in eintraege]
    if any(not i for i in ids):
        raise Abbruch("Jedes Issue braucht eine 'id' (z. B. \"A\").")
    doppelt = {i for i in ids if ids.count(i) > 1}
    if doppelt:
        raise Abbruch(f"Doppelte ids: {', '.join(sorted(doppelt))}")
    for e in eintraege:
        for pflicht in ("titel", "text", "akzeptanz"):
            if not e.get(pflicht):
                raise Abbruch(f"Issue {e['id']}: Feld '{pflicht}' fehlt.")
        for abh in e.get("abhaengig_von", []):
            if abh not in ids:
                raise Abbruch(f"Issue {e['id']}: hängt von unbekannter id '{abh}' ab.")
    reihenfolge(eintraege)  # wirft bei Kreisen


def reihenfolge(eintraege: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sortiert so, dass jedes Issue nach seinen Abhängigkeiten kommt (stabil)."""
    nach_id = {e["id"]: e for e in eintraege}
    fertig: list[dict[str, Any]] = []
    gesehen: set[str] = set()
    pfad: set[str] = set()

    def besuchen(i: str) -> None:
        if i in gesehen:
            return
        if i in pfad:
            raise Abbruch(f"Abhängigkeiten bilden einen Kreis bei '{i}'.")
        pfad.add(i)
        for abh in nach_id[i].get("abhaengig_von", []):
            besuchen(abh)
        pfad.discard(i)
        gesehen.add(i)
        fertig.append(nach_id[i])

    for e in eintraege:
        besuchen(e["id"])
    return fertig


def issue_text(e: dict[str, Any], nummern: dict[str, int], prd: str | None, eltern: int | None) -> str:
    teile = ["## Worum es geht", "", e["text"].strip(), "", "## Akzeptanzkriterien", ""]
    teile += [f"- [ ] {a}" for a in e["akzeptanz"]]
    bezuege = []
    if prd or e.get("prd_abschnitt"):
        abschnitt = f', Abschnitt "{e["prd_abschnitt"]}"' if e.get("prd_abschnitt") else ""
        bezuege.append(f"PRD: {prd or 'docs/projekt/prd.md'}{abschnitt}")
    if e.get("adr"):
        bezuege.append("ADR: " + ", ".join(e["adr"]))
    if e.get("dateien"):
        bezuege.append("Dateien: " + ", ".join(e["dateien"]))
    if eltern:
        bezuege.append(f"Teil von: #{eltern}")
    if bezuege:
        teile += ["", "## Bezüge", "", *bezuege]
    abh = [f"#{nummern[a]}" for a in e.get("abhaengig_von", []) if a in nummern]
    teile += ["", "## Abhängigkeiten", "", f"Blockiert von: {', '.join(abh) if abh else 'nichts'}"]
    art = "AFK (Agent darf allein umsetzen)" if e.get("afk", True) else "HITL (braucht Vale)"
    teile += ["", f"Art: {art}"]
    return "\n".join(teile) + "\n"


def labels_fuer(e: dict[str, Any]) -> list[str]:
    labels = list(dict.fromkeys(e.get("labels", [])))
    labels.append("bereit" if e.get("afk", True) else "mensch")
    return labels


# ---------------------------------------------------------------- Anlegen


def anlegen(pfad: Path, trocken: bool = False) -> dict[str, int]:
    daten = entwurf_laden(pfad)
    eintraege = reihenfolge(daten["issues"])
    prd = daten.get("prd")
    online = not trocken and hat_programm("gh")
    if not trocken and not online:
        warne("gh fehlt: Issues werden nur in docs/projekt/issues.md eingetragen, nicht auf GitHub.")
    nummern: dict[str, int] = {}
    links: dict[str, str] = {}

    eltern_nr = None
    eltern = daten.get("eltern")
    if eltern and online:
        url = gh("issue", "create", "--title", eltern["titel"], "--label", "prd", "--body-file", "-",
                 eingabe=eltern.get("text", "") + "\n\n(Liste der Teile folgt.)\n")
        eltern_nr = nummer_aus_url(url)
        melde(f"#{eltern_nr} {eltern['titel']} (PRD)")

    for zaehler, e in enumerate(eintraege, start=1):
        text = issue_text(e, nummern, prd, eltern_nr)
        if online:
            argumente = ["issue", "create", "--title", e["titel"], "--body-file", "-"]
            for label in labels_fuer(e):
                argumente += ["--label", label]
            url = gh(*argumente, eingabe=text)
            nummern[e["id"]] = nummer_aus_url(url)
            links[e["id"]] = url
        else:
            nummern[e["id"]] = -zaehler  # Platzhalter
        abh = ", ".join(e.get("abhaengig_von", [])) or "-"
        nr = f"#{nummern[e['id']]}" if nummern[e["id"]] > 0 else e["id"]
        melde(f"{nr} {e['titel']}  (hängt ab von: {abh})")

    if eltern_nr and online:
        liste = "\n".join(f"- [ ] #{nummern[e['id']]} {e['titel']}" for e in eintraege)
        gh("issue", "edit", str(eltern_nr), "--body-file", "-", eingabe=eltern.get("text", "") + "\n\n## Teile\n\n" + liste + "\n")

    if not trocken:
        uebersicht_schreiben(daten, eintraege, nummern, links, eltern_nr)
    return nummern


def nummer_aus_url(url: str) -> int:
    m = re.search(r"/issues/(\d+)", url)
    if not m:
        raise Abbruch(f"Konnte keine Issue-Nummer lesen aus: {url}")
    return int(m.group(1))


def uebersicht_schreiben(daten, eintraege, nummern, links, eltern_nr) -> Path:
    ziel = wurzel() / "docs" / "projekt" / "issues.md"
    heute = dt.date.today().isoformat()
    titel = (daten.get("eltern") or {}).get("titel", "Zerlegung")
    zeilen = []
    if not ziel.exists():
        zeilen += ["---", "titel: Issues", "typ: uebersicht", f"erstellt: {heute}", "tags: [projekt, issues]", "---", "",
                   "# Issues", "", "Erzeugt von `parlier issues anlegen`. Nicht von Hand pflegen, GitHub ist die Quelle.", ""]
    kopf = f"## {titel} ({heute})"
    if eltern_nr:
        kopf += f", Sammel-Issue #{eltern_nr}"
    zeilen += [kopf, "", "| Nr | Titel | Hängt ab von | Art |", "|---|---|---|---|"]
    for e in eintraege:
        nr = nummern[e["id"]]
        nr_text = f"[#{nr}]({links[e['id']]})" if e["id"] in links else e["id"]
        abh = ", ".join(f"#{nummern[a]}" if nummern[a] > 0 else a for a in e.get("abhaengig_von", [])) or "-"
        art = "AFK" if e.get("afk", True) else "HITL"
        zeilen.append(f"| {nr_text} | {e['titel']} | {abh} | {art} |")
    ziel.parent.mkdir(parents=True, exist_ok=True)
    alt = ziel.read_text(encoding="utf-8").rstrip() + "\n\n" if ziel.exists() else ""
    ziel.write_text(alt + "\n".join(zeilen) + "\n", encoding="utf-8")
    melde(f"Übersicht: {ziel.relative_to(wurzel())}")
    return ziel


# ---------------------------------------------------------------- Lesen und ändern


def blockiert_von(text: str) -> list[int]:
    m = RE_BLOCKIERT.search(text or "")
    if not m:
        return []
    return [int(n) for n in re.findall(r"#(\d+)", m.group(1))]


def _labels(issue: dict[str, Any]) -> set[str]:
    return {l["name"] for l in issue.get("labels", [])}


def erledigt(nummer: int, zwischenspeicher: dict[int, bool]) -> bool:
    if nummer not in zwischenspeicher:
        daten = gh("issue", "view", str(nummer), "--json", "state,labels", als_json=True)
        zwischenspeicher[nummer] = daten["state"] == "CLOSED" or "fertig" in _labels(daten)
    return zwischenspeicher[nummer]


def naechstes(label: str = "bereit") -> dict[str, Any] | None:
    """Das älteste offene Issue mit Label 'bereit', dessen Abhängigkeiten erledigt sind."""
    kandidaten = gh("issue", "list", "--state", "open", "--label", label, "--limit", "200",
                    "--json", "number,title,body,labels", als_json=True)
    zwischenspeicher: dict[int, bool] = {}
    for issue in sorted(kandidaten, key=lambda i: i["number"]):
        if _labels(issue) & SPERR_LABELS:
            continue
        if all(erledigt(n, zwischenspeicher) for n in blockiert_von(issue.get("body", ""))):
            return issue
    return None


def neu(titel: str, labels: list[str] = (), text: str = "") -> int:
    """Legt ein einzelnes Issue über die REST-API an (klappt auch, wo GraphQL gesperrt ist)."""
    argumente = ["api", f"repos/{konfig()['projekt']['repo']}/issues", "-f", f"title={titel}"]
    for label in labels:
        argumente += ["-f", f"labels[]={label}"]
    argumente += ["-F", "body=@-", "--jq", ".number"]
    nummer = int(gh(*argumente, eingabe=text))
    melde(f"Issue #{nummer}: {titel}")
    return nummer


def labels_aendern(nummer: int, hinzu: list[str] = (), weg: list[str] = ()) -> None:
    """Über die REST-API, damit es auch klappt, wo GraphQL gesperrt ist."""
    from urllib.parse import quote

    pfad = f"repos/{konfig()['projekt']['repo']}/issues/{nummer}/labels"
    if hinzu:
        argumente = ["api", "-X", "POST", pfad]
        for l in hinzu:
            argumente += ["-f", f"labels[]={l}"]
        try:
            gh(*argumente)
        except Abbruch as fehler:
            warne(f"Labels an #{nummer} nicht gesetzt: {fehler}")
    for l in weg:
        try:
            gh("api", "-X", "DELETE", f"{pfad}/{quote(l)}")
        except Abbruch:
            pass  # Label war nicht gesetzt


def kommentieren(nummer: int, text: str) -> None:
    try:
        gh("api", f"repos/{konfig()['projekt']['repo']}/issues/{nummer}/comments", "-F", "body=@-", "--silent", eingabe=text)
    except Abbruch as fehler:
        warne(f"Kommentar an #{nummer} fehlgeschlagen: {fehler}")
