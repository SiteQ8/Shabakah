"""Unit tests for the Shabakah guide: bilingual completeness, Arabic house
rules, counted nouns, flags, and the version. Run from the repo root with
python3 -m unittest discover -s tests"""

import contextlib
import hashlib
import importlib.machinery
import importlib.util
import io
import os
import re
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import lint_lessons  # noqa: E402

AR = re.compile(r"[؀-ۿ]")
MID_STOP = re.compile(r"\.\s+(?=[؀-ۿ])")
BANNED_CHARS = ["–", "—", "·", "→", "•"]
BANNED_AR = ["حاوية", "الحاوية", "حاويات", "الخليج الفارسي"]


def load_guide(home):
    os.environ["HOME"] = home
    os.environ["SHABAKAH_LESSONS"] = os.path.join(ROOT, "lab", "lessons")
    os.environ["NO_COLOR"] = "1"
    path = os.path.join(ROOT, "lab", "bin", "netsec")
    loader = importlib.machinery.SourceFileLoader("netsec_under_test", path)
    spec = importlib.util.spec_from_loader("netsec_under_test", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def arabic_ok(testcase, label, text):
    testcase.assertTrue(AR.search(text), "%s has no Arabic: %r" % (label, text))
    testcase.assertFalse(MID_STOP.search(text), "%s has a full stop mid sentence: %r" % (label, text))
    for ch in BANNED_CHARS:
        testcase.assertNotIn(ch, text, "%s has a banned character" % label)
    for w in BANNED_AR:
        testcase.assertNotIn(w, text, "%s uses the banned word %s" % (label, w))


class GuideStrings(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.g = load_guide(cls.tmp.name)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_every_key_in_both_languages(self):
        en, ar = set(self.g.STR["en"]), set(self.g.STR["ar"])
        self.assertEqual(sorted(en - ar), [], "keys missing from Arabic")
        self.assertEqual(sorted(ar - en), [], "keys missing from English")

    def test_format_placeholders_match(self):
        for key, en in self.g.STR["en"].items():
            ar = self.g.STR["ar"][key]
            self.assertEqual(en.count("%d"), ar.count("%d"), key)
            self.assertEqual(en.count("%s"), ar.count("%s"), key)

    def test_arabic_strings_follow_house_rules(self):
        exempt = {"next_cmd"}
        for key, text in self.g.STR["ar"].items():
            if key not in exempt:
                arabic_ok(self, "STR[ar][%s]" % key, text)

    def test_tables_are_bilingual(self):
        for row in self.g.CHEAT:
            arabic_ok(self, "cheat label", row[1])
        for row in self.g.HELP:
            arabic_ok(self, "help line", row[2])
        for row in self.g.TARGETS:
            arabic_ok(self, "target note", row[3])
        for a in self.g._ach_defs():
            arabic_ok(self, "achievement", a["ar"])
            arabic_ok(self, "achievement description", a["desc_ar"])
        for f in self.g.FLAGS:
            arabic_ok(self, "flag title", f["title_ar"])
            arabic_ok(self, "flag hint", f["where_ar"])

    def test_counted_nouns(self):
        cn = self.g.count_noun
        self.assertEqual(cn(1, "lesson", "ar"), "درس واحد")
        self.assertEqual(cn(2, "lesson", "ar"), "درسان")
        self.assertEqual(cn(3, "lesson", "ar"), "3 دروس")
        self.assertEqual(cn(10, "lesson", "ar"), "10 دروس")
        self.assertEqual(cn(11, "lesson", "ar"), "11 درسا")
        self.assertEqual(cn(17, "lesson", "ar"), "17 درسا")
        self.assertEqual(cn(100, "lesson", "ar"), "100 درس")
        self.assertEqual(cn(10, "point", "ar"), "10 نقاط")
        self.assertEqual(cn(20, "point", "ar"), "20 نقطة")
        self.assertEqual(cn(110, "point", "ar"), "110 نقاط")
        self.assertEqual(cn(6, "flag", "ar"), "6 رموز سرية")
        self.assertEqual(cn(1, "point", "en"), "1 point")
        self.assertEqual(cn(17, "lesson", "en"), "17 lessons")

    def test_answers_accept_arabic_digits(self):
        self.assertEqual(self.g.norm_answer("٣"), "3")
        self.assertEqual(self.g._parse_number("ثلاثة"), 3)
        self.assertEqual(self.g._parse_number("6 ports"), 6)


class Flags(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.g = load_guide(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_every_planted_flag_has_a_digest(self):
        sources = ""
        for rel in ("lab/targets/targets.py", "entrypoint.sh"):
            with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
                sources += fh.read()
        planted = set(re.findall(r"flag\{[a-z_]+\}", sources))
        digests = {f["sha256"] for f in self.g.FLAGS}
        self.assertEqual(len(planted), len(self.g.FLAGS))
        for flag in planted:
            self.assertIn(hashlib.sha256(flag.encode()).hexdigest(), digests, flag)

    def test_no_plaintext_flag_in_guide(self):
        with open(os.path.join(ROOT, "lab", "bin", "netsec"), encoding="utf-8") as fh:
            self.assertNotRegex(fh.read(), r"flag\{shabakah_[a-z_]+\}")

    def test_submission(self):
        self.assertEqual(self.g.submit_flag("recon")[0], "unknown")
        self.assertEqual(self.g.submit_flag("flag{shabakah_http_recon_ok}")[0], "new")
        self.assertEqual(self.g.submit_flag(" flag{shabakah_http_recon_ok} ")[0], "already")
        self.assertEqual(self.g.submit_flag("flag{nope}")[0], "unknown")

    def test_arabic_submit_prints_score(self):
        self.g.set_lang("ar")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = self.g.cmd_submit(["flag{shabakah_cert_metadata}"])
        self.assertEqual(code, 0)
        self.assertIn("نقاطك: 20 من", buf.getvalue())
        self.assertIn("(+20 نقطة)", buf.getvalue())


class Views(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.g = load_guide(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def render(self, fn, *args):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            fn(*args)
        return buf.getvalue()

    def test_arabic_views_have_no_english_interface(self):
        self.g.set_lang("ar")
        self.g.mark_complete("01")
        out = "".join(self.render(v) for v in (
            self.g.banner, self.g.show_progress, self.g.targets_status,
            self.g.ctf_board, self.g.achievements_view, self.g.show_lessons_list))
        for leak in ("Welcome back", "lessons", " pts", "Next up", "not found",
                     "found", "Points:", "Achievements", "the door", "UP", "DOWN"):
            self.assertNotIn(leak, out, "English leaked: %s" % leak)

    def test_certificate_locked_until_everything_is_done(self):
        self.assertEqual(self.render(self.g.cmd_certificate, []).count("flags left"), 1)


class Release(unittest.TestCase):
    def test_versions_agree(self):
        with open(os.path.join(ROOT, "VERSION"), encoding="utf-8") as fh:
            version = fh.read().strip()
        with open(os.path.join(ROOT, "lab", "bin", "netsec"), encoding="utf-8") as fh:
            self.assertIn('VERSION = "%s"' % version, fh.read())
        with open(os.path.join(ROOT, "Dockerfile"), encoding="utf-8") as fh:
            self.assertIn('org.opencontainers.image.version="%s"' % version, fh.read())
        with open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8") as fh:
            self.assertIn("## %s" % version, fh.read())
        notes = os.path.join(ROOT, ".github", "release-notes", "v%s.md" % version)
        self.assertTrue(os.path.exists(notes), "release notes missing for v%s" % version)


class Lessons(unittest.TestCase):
    def test_lessons_lint_clean(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = lint_lessons.main([])
        self.assertEqual(code, 0, buf.getvalue())


if __name__ == "__main__":
    unittest.main()
