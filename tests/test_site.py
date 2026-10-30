"""Checks that the website and README follow the lab and the house rules.
Run from the repo root with python3 -m unittest discover -s tests"""

import contextlib
import html
import io
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import build_site  # noqa: E402

SITE = os.path.join(ROOT, "docs", "index.html")
README = os.path.join(ROOT, "README.md")
MID_STOP = re.compile(r"\.\s+(?=[؀-ۿ])")
NUMBER_WORDS = re.compile(
    r"\b(eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|"
    r"a hundred and ten)\b|خمسة عشر|اثنا عشر|اثني عشر|سبعة عشر|ستة عشر|مئة وعشر", re.I)


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def visible(fragment):
    fragment = re.sub(r"<!--.*?-->", "", fragment, flags=re.S)
    fragment = re.sub(r"<code>.*?</code>", "CODE", fragment, flags=re.S)
    fragment = re.sub(r"<[^>]+>", "", fragment)
    return html.unescape(fragment)


class SiteMatchesLab(unittest.TestCase):
    def test_generated_parts_are_current(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = build_site.main(["--check"])
        self.assertEqual(code, 0, buf.getvalue())

    def test_no_hand_written_counts(self):
        for path in (SITE, README):
            text = re.sub(r"<!--.*?-->", "", read(path), flags=re.S)
            m = NUMBER_WORDS.search(text)
            self.assertIsNone(m, "%s spells out a count by hand: %r" % (path, m and m.group(0)))

    def test_every_lesson_listed_in_both_languages(self):
        site = read(SITE)
        for lang in ("en", "ar"):
            block = re.search(r"<!--lessons:%s-->(.*?)<!--/lessons-->" % lang, site, re.S).group(1)
            ids = re.findall(r'<span class="lid">(\d+)</span>', block)
            expected = [m["id"] for m in build_site.lessons(lang)]
            self.assertEqual(ids, expected, lang)

    def test_screenshots_exist(self):
        site = read(SITE)
        for rel in set(re.findall(r'screenshots/[a-z/]+\.png', site)):
            self.assertTrue(os.path.exists(os.path.join(ROOT, "docs", rel)), rel)
        for name in re.findall(r'data-shot="([a-z]+)"', site):
            for folder in ("screenshots", "screenshots/ar"):
                self.assertTrue(os.path.exists(os.path.join(ROOT, "docs", folder, name + ".png")),
                                "%s/%s.png" % (folder, name))


class HouseRules(unittest.TestCase):
    def test_banned_characters_and_words(self):
        for path in (SITE, README):
            text = read(path)
            for ch in ("–", "—", "·", "→", "•"):
                self.assertNotIn(ch, text, "%s has a banned character" % path)
            for word in ("حاوية", "الحاوية", "الخليج الفارسي"):
                self.assertNotIn(word, text, "%s uses %s" % (path, word))
            for word in ("claude", "anthropic", "nbk"):
                self.assertNotRegex(text.lower(), r"\b%s\b" % word, path)

    def test_arabic_site_has_no_mid_sentence_full_stop(self):
        ar = re.search(r'<main lang="ar".*?</main>', read(SITE), re.S).group(0)
        for tag in ("p", "h1", "h2", "h3", "summary", "div"):
            for frag in re.findall(r"<%s[^>]*>(.*?)</%s>" % (tag, tag), ar, re.S):
                if "<div" in frag or "<p" in frag:
                    continue
                text = visible(frag).strip()
                self.assertIsNone(MID_STOP.search(text), "full stop mid sentence: %s" % text[:100])

    def test_arabic_readme_has_no_mid_sentence_full_stop(self):
        text = read(README).split("## عن شبكة", 1)[1]
        text = re.sub(r"```.*?```", "", text, flags=re.S)
        for para in re.split(r"\n\s*\n", text):
            if para.lstrip().startswith(("#", "|", "<!--table")):
                continue
            self.assertIsNone(MID_STOP.search(visible(para)), "full stop mid sentence: %s" % para[:100])


if __name__ == "__main__":
    unittest.main()
