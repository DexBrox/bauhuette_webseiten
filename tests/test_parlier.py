"""Tests für parlier. Ausführen: python3 -m unittest discover -s tests"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from parlier import basis, issues, kontext, pruefen, release, vorschau, wiki, zweig

VORLAGE = Path(__file__).resolve().parent.parent


class ImOrdner:
    """Wechselt für einen Test in einen frischen Ordner mit bauhuette.toml."""

    def __init__(self, git_init: bool = False):
        self.git_init = git_init

    def __enter__(self) -> Path:
        self.alt = Path.cwd()
        self.tmp = tempfile.TemporaryDirectory()
        ort = Path(self.tmp.name)
        (ort / "bauhuette.toml").write_text((VORLAGE / "bauhuette.toml").read_text(encoding="utf-8"), encoding="utf-8")
        os.chdir(ort)
        if self.git_init:
            for befehl in (["git", "init", "-q", "-b", "develop"], ["git", "config", "user.email", "t@t"], ["git", "config", "user.name", "T"],
                           ["git", "add", "-A"], ["git", "commit", "-q", "-m", "start"]):
                subprocess.run(befehl, check=True, capture_output=True)
        return ort

    def __exit__(self, *fehler):
        os.chdir(self.alt)
        self.tmp.cleanup()


class Basis(unittest.TestCase):
    def test_kurzname(self):
        self.assertEqual(basis.kurzname("Größe der Bilder ändern!"), "groesse-der-bilder-aendern")
        self.assertEqual(basis.kurzname("???"), "ohne-titel")

    def test_frontmatter(self):
        werte, rumpf = basis.frontmatter("---\ntitel: Hallo\nstatus: freigegeben\n---\n\n# Text\n")
        self.assertEqual(werte["titel"], "Hallo")
        self.assertEqual(werte["status"], "freigegeben")
        self.assertTrue(rumpf.startswith("# Text"))

    def test_konfig_mischt_standard(self):
        with ImOrdner():
            k = basis.konfig()
            self.assertEqual(k["zweige"]["sammel"], "develop")
            self.assertTrue(k["label"])


class Issues(unittest.TestCase):
    ENTWURF = {
        "prd": "docs/projekt/prd.md",
        "issues": [
            {"id": "B", "titel": "Liste", "text": "x", "akzeptanz": ["a"], "abhaengig_von": ["A"]},
            {"id": "A", "titel": "Grundgerüst", "text": "y", "akzeptanz": ["b"], "afk": False, "adr": ["0002"]},
        ],
    }

    def test_reihenfolge(self):
        self.assertEqual([e["id"] for e in issues.reihenfolge(self.ENTWURF["issues"])], ["A", "B"])

    def test_kreis_wird_erkannt(self):
        kreis = [{"id": "A", "titel": "t", "text": "t", "akzeptanz": ["a"], "abhaengig_von": ["B"]},
                 {"id": "B", "titel": "t", "text": "t", "akzeptanz": ["a"], "abhaengig_von": ["A"]}]
        with self.assertRaises(basis.Abbruch):
            issues.pruefe_entwurf({"issues": kreis})

    def test_unbekannte_abhaengigkeit(self):
        with self.assertRaises(basis.Abbruch):
            issues.pruefe_entwurf({"issues": [{"id": "A", "titel": "t", "text": "t", "akzeptanz": ["a"], "abhaengig_von": ["X"]}]})

    def test_text_und_labels(self):
        text = issues.issue_text(self.ENTWURF["issues"][0], {"A": 7}, "docs/projekt/prd.md", 3)
        self.assertIn("Blockiert von: #7", text)
        self.assertIn("Teil von: #3", text)
        self.assertEqual(issues.blockiert_von(text), [7])
        self.assertEqual(issues.labels_fuer(self.ENTWURF["issues"][1]), ["mensch"])
        self.assertIn("ADR: 0002", issues.issue_text(self.ENTWURF["issues"][1], {}, None, None))

    def test_trockenlauf_ohne_github(self):
        with ImOrdner() as ort:
            datei = ort / "entwurf.json"
            datei.write_text(json.dumps(self.ENTWURF), encoding="utf-8")
            nummern = issues.anlegen(datei, trocken=True)
            self.assertEqual(set(nummern), {"A", "B"})
            self.assertFalse((ort / "docs" / "projekt" / "issues.md").exists())


class Kontext(unittest.TestCase):
    def test_prd_abschnitt(self):
        prd = "# PRD\n\n## Abstimmung\n\nText\n\n### Regeln\n\nmehr\n\n## Anderes\n\nnicht"
        stueck = kontext.prd_abschnitt(prd, "Abstimmung")
        self.assertIn("### Regeln", stueck)
        self.assertNotIn("Anderes", stueck)

    def test_bezug(self):
        self.assertEqual(kontext.bezug("PRD: docs/x.md\nADR: 0001, 0003", "ADR"), "0001, 0003")


class Pruefen(unittest.TestCase):
    def test_auszug_findet_fehler(self):
        log = "\n".join(["ok"] * 50 + ["src/a.ts(3,1): error TS2322: Type 'x'", "  detail"] + ["fertig"] * 50)
        self.assertIn("TS2322", pruefen.auszug(log))
        self.assertLessEqual(len(pruefen.auszug(log).splitlines()), 25)

    def test_kaputte_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp)
            (site / "impressum").mkdir()
            (site / "impressum" / "index.html").write_text('<a href="/">Start</a>')
            (site / "index.html").write_text(
                '<a href="/repo/impressum/">i</a><a href="/repo/fehlt/">f</a><img src="bild.jpg">'
                '<a href="https://example.org">e</a><a href="mailto:a@b">m</a><a href="#x">s</a>'
            )
            self.assertEqual(pruefen.kaputte_links(site, "/repo/"), ["index.html: /repo/fehlt/", "index.html: bild.jpg"])

    def test_doku_pflicht(self):
        self.assertIsNotNone(pruefen.doku_fehlt(["apps/web/src/a.ts"], []))
        self.assertIsNone(pruefen.doku_fehlt(["apps/web/src/a.ts", "CHANGELOG.md"], []))
        self.assertIsNone(pruefen.doku_fehlt(["apps/web/src/a.ts"], ["keine-doku"]))
        self.assertIsNone(pruefen.doku_fehlt(["README.md"], []))


class Release(unittest.TestCase):
    LOG = "# Changelog\n\n## [Unreleased]\n\n### Hinzugefügt\n- Neu\n  mit Fortsetzung\n\n## [1.0.0] - 2026-01-01\n\n- Start\n"

    def test_versionieren(self):
        neu = release.versionieren(self.LOG, "1.1.0", "2026-11-22")
        self.assertIn("## [Unreleased]\n\n## [1.1.0] - 2026-11-22", neu)
        self.assertEqual(release.abschnitt(neu, "Unreleased"), "")
        self.assertIn("- Neu", release.abschnitt(neu, "1.1.0"))

    def test_leeres_unreleased(self):
        with self.assertRaises(basis.Abbruch):
            release.versionieren("## [Unreleased]\n\n## [1.0.0] - x\n", "1.1.0", "d")

    def test_notiz(self):
        neu = release.versionieren(self.LOG, "1.1.0", "2026-11-22")
        text = release.notiz(neu, "1.1.0", "DexBrox/x")
        self.assertIn("- Neu mit Fortsetzung", text)
        self.assertIn("compare/v1.0.0...v1.1.0", text)

    def test_version(self):
        self.assertEqual(release.pruefe_version("v2.0.1"), "2.0.1")
        with self.assertRaises(basis.Abbruch):
            release.pruefe_version("2.0")


class Wiki(unittest.TestCase):
    def test_seite_umschreiben(self):
        text = "---\ntitel: Erste Schritte\nerstellt: 2026-11-22\ntags: [hilfe]\n---\n\n# Erste Schritte\n"
        neu = wiki.seite_umschreiben(text, "docs/hilfe/erste-schritte.md", "DexBrox/x", "develop", "2026-11-23")
        self.assertIn('title: "Erste Schritte"', neu)
        self.assertIn("created: 2026-11-22", neu)
        self.assertIn("modified: 2026-11-23", neu)
        self.assertIn("/edit/develop/docs/hilfe/erste-schritte.md", neu)
        self.assertIn("template=wiki.yml", neu)
        self.assertEqual(neu.count("---\n"), 3)

    def test_ohne_frontmatter_und_repo(self):
        neu = wiki.seite_umschreiben("# Hallo\n", "docs/hilfe/hallo-welt.md", "", "develop", None)
        self.assertIn('title: "Hallo welt"', neu)
        self.assertNotIn("Seite bearbeiten", neu)


class Vorschau(unittest.TestCase):
    def test_kennzeichnen_und_ablage(self):
        with ImOrdner() as ort:
            site = ort / "_site"
            site.mkdir()
            (site / "index.html").write_text("<html><head></head><body>Hi</body></html>", encoding="utf-8")
            (site / "sitemap.xml").write_text("x")
            self.assertEqual(vorschau.kennzeichnen(site, "feature/12-x"), 1)
            html = (site / "index.html").read_text(encoding="utf-8")
            self.assertIn("noindex", html)
            self.assertIn("vorschau-schild", html)
            self.assertFalse((site / "sitemap.xml").exists())
            ablage = ort / "ablage"
            vorschau.ablage("einsetzen", "develop", ablage, site)
            vorschau.ablage("einsetzen", "feature/12-x", ablage, site)
            self.assertTrue((ablage / "zweig" / "feature-12-x" / "index.html").exists())
            self.assertIn("feature/12-x", (ablage / "zweig" / "index.html").read_text(encoding="utf-8"))
            vorschau.ablage("entfernen", "feature/12-x", ablage, site)
            self.assertFalse((ablage / "zweig" / "feature-12-x").exists())
            self.assertTrue((ablage / "index.html").exists())


class Zweige(unittest.TestCase):
    def test_kein_commit_auf_develop(self):
        with ImOrdner(git_init=True) as ort:
            (ort / "a.txt").write_text("x")
            with self.assertRaises(basis.Abbruch):
                zweig.commit("Test")

    def test_commit_auf_featurezweig(self):
        with ImOrdner(git_init=True) as ort:
            name = zweig.zweig_anlegen(12, "Neue Seite")
            self.assertEqual(name, "feature/12-neue-seite")
            (ort / "a.txt").write_text("x")
            zweig.commit("Seite angelegt")
            self.assertEqual(basis.git("log", "-1", "--format=%s"), "Seite angelegt (#12)")
            self.assertEqual(zweig.issue_aus_zweig(), 12)

    def test_issue_nummer_in_erster_zeile(self):
        with ImOrdner(git_init=True) as ort:
            zweig.zweig_anlegen(7, "Mehrzeilig")
            (ort / "b.txt").write_text("x")
            zweig.commit("Betreff\n\nText\n\nCo-Authored-By: X <x@y>")
            nachricht = basis.git("log", "-1", "--format=%B")
            self.assertTrue(nachricht.startswith("Betreff (#7)\n"))
            self.assertTrue(nachricht.rstrip().endswith("Co-Authored-By: X <x@y>"))


if __name__ == "__main__":
    unittest.main()
