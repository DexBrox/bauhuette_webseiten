"""Prüft die Live-Seite: Seiten erreichbar, Zertifikat gültig. Optional als Issue melden."""

from __future__ import annotations

import datetime as dt
import socket
import ssl
import urllib.error
import urllib.request

from .basis import Abbruch, gh, konfig, melde

TITEL = "Störung: Live-Seite"


def zertifikat_tage(host: str) -> int:
    kontext = ssl.create_default_context()
    with socket.create_connection((host, 443), timeout=15) as roh:
        with kontext.wrap_socket(roh, server_hostname=host) as s:
            ablauf = dt.datetime.strptime(s.getpeercert()["notAfter"], "%b %d %H:%M:%S %Y %Z")
    return (ablauf.replace(tzinfo=dt.timezone.utc) - dt.datetime.now(dt.timezone.utc)).days


def pruefen_live() -> list[str]:
    k = konfig()
    domain = k["projekt"].get("domain")
    if not domain:
        raise Abbruch("In bauhuette.toml ist keine domain eingetragen.")
    probleme = []
    for pfad in k["ueberwachung"]["seiten"]:
        url = f"https://{domain}{pfad}"
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "bauhuette-ueberwachung"}), timeout=20) as r:
                if r.status != 200:
                    probleme.append(f"{url}: Status {r.status}")
        except urllib.error.HTTPError as fehler:
            probleme.append(f"{url}: Status {fehler.code}")
        except (urllib.error.URLError, TimeoutError) as fehler:
            probleme.append(f"{url}: nicht erreichbar ({fehler})")
    try:
        tage = zertifikat_tage(domain)
        if tage < k["ueberwachung"]["zertifikat_tage"]:
            probleme.append(f"Zertifikat läuft in {tage} Tagen ab")
    except (OSError, ssl.SSLError) as fehler:
        probleme.append(f"Zertifikat nicht prüfbar: {fehler}")
    return probleme


def ueberwachen(als_issue: bool = False) -> bool:
    probleme = pruefen_live()
    offen = []
    if als_issue:
        offen = gh("issue", "list", "--state", "open", "--search", f'"{TITEL}" in:title', "--json", "number", als_json=True)
    if probleme:
        text = "Gefunden bei der automatischen Prüfung:\n\n" + "\n".join(f"- {p}" for p in probleme)
        melde(text)
        if als_issue:
            if offen:
                gh("issue", "comment", str(offen[0]["number"]), "--body-file", "-", eingabe=text)
            else:
                gh("issue", "create", "--title", TITEL, "--label", "betrieb", "--body-file", "-", eingabe=text)
        return False
    melde("Live-Seite in Ordnung.")
    for issue in offen:
        gh("issue", "close", str(issue["number"]), "--comment", "Wieder alles erreichbar.")
    return True
