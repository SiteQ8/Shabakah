#!/usr/bin/env python3
# Renders the parts of the website and the README that must follow the lab.
# Author: Ali AlEnezi (SiteQ8)
#
# The lesson files and the guide are the single source of truth. This script
# writes the curriculum lists, every count (lessons, flags, points, practice
# services) and the Arabic phrases that must agree with those counts into
# docs/index.html and README.md, between markers:
#
#   <!--lessons:en--> ... <!--/lessons-->     curriculum rows on the site
#   <!--table:en--> ... <!--/table-->         curriculum table in the README
#   <!--n:lessons-->17<!--/n-->               a bare number
#   <!--ar:lesson:lessons-->17 درسا<!--/ar-->  number and agreeing Arabic noun
#   <!--arnoun:lesson:lessons-->درسا<!--/arnoun-->  the agreeing noun alone
#
# Usage: python3 tools/build_site.py          rewrite the files
#        python3 tools/build_site.py --check  exit 1 if anything is stale

import html
import importlib.machinery
import importlib.util
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "docs", "index.html")
README = os.path.join(ROOT, "README.md")
LESSONS = os.path.join(ROOT, "lab", "lessons")
REPO_BLOB = "https://github.com/SiteQ8/Shabakah/blob/main/lab/lessons"

# Arabic noun phrases by the agreement class a number takes: "few" for 3 to
# 10, "many" for 11 to 99, "hundred" for round hundreds (and 0, 101, 102).
AR_FORMS = {
    "lesson":         {"few": "دروس", "many": "درسا", "hundred": "درس"},
    "lesson_applied": {"few": "دروس تطبيقية", "many": "درسا تطبيقيا", "hundred": "درس تطبيقي"},
    "code":           {"few": "رموز سرية", "many": "رمزا سريا", "hundred": "رمز سري"},
    "code_hidden":    {"few": "تحديات مخفية", "many": "تحديا مخفيا", "hundred": "تحد مخفي"},
    "challenge":      {"few": "تحديات", "many": "تحديا", "hundred": "تحد"},
    "point":          {"few": "نقاط", "many": "نقطة", "hundred": "نقطة"},
    "target":         {"few": "أهداف للتدريب", "many": "هدفا للتدريب", "hundred": "هدف للتدريب"},
    "service_real":   {"few": "خدمات حقيقية", "many": "خدمة حقيقية", "hundred": "خدمة حقيقية"},
    "service_train":  {"few": "خدمات للتدريب", "many": "خدمة للتدريب", "hundred": "خدمة للتدريب"},
}


def ar_form(n, noun):
    r = n % 100
    if 3 <= r <= 10:
        return AR_FORMS[noun]["few"]
    if 11 <= r <= 99:
        return AR_FORMS[noun]["many"]
    if n in (1, 2):
        raise ValueError("write 1 and 2 by hand, they take a singular or a dual")
    return AR_FORMS[noun]["hundred"]


def load_guide():
    path = os.path.join(ROOT, "lab", "bin", "netsec")
    loader = importlib.machinery.SourceFileLoader("netsec_guide", path)
    spec = importlib.util.spec_from_loader("netsec_guide", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def front_matter(path):
    with open(path, "r", encoding="utf-8") as fh:
        raw = fh.read()
    meta = {}
    lines = raw.splitlines()
    if lines and lines[0].strip() == "---":
        for line in lines[1:]:
            if line.strip() == "---":
                break
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    return meta


def lessons(lang):
    out = []
    folder = os.path.join(LESSONS, lang)
    for name in sorted(os.listdir(folder)):
        if name.endswith(".md"):
            meta = front_matter(os.path.join(folder, name))
            meta["_file"] = name
            out.append(meta)
    return out


def counts():
    guide = load_guide()
    n_lessons = len(lessons("en"))
    if n_lessons != len(lessons("ar")):
        raise SystemExit("lesson count differs between en and ar")
    return {
        "lessons": n_lessons,
        "flags": len(guide.FLAGS),
        "points": sum(f["points"] for f in guide.FLAGS),
        # every practice service, the SSH door itself excluded
        "targets": sum(1 for t in guide.TARGETS if t[4] != 22),
    }


def site_rows(lang):
    rows = []
    for m in lessons(lang):
        rows.append(
            '    <div class="lrow"><span class="lid">%s</span><span class="lt">%s'
            '<span class="ld">%s</span></span><span class="lmeta">%s</span></div>'
            % (html.escape(m["id"]), html.escape(m["title"]),
               html.escape(m.get("objective", "")), html.escape(m.get("tag", ""))))
    return "\n" + "\n".join(rows) + "\n    "


def readme_table(lang):
    if lang == "ar":
        head = "| الدرس | العنوان | الهدف |\n|---|---|---|"
    else:
        head = "| # | Lesson | Objective |\n|---|---|---|"
    rows = []
    for m in lessons(lang):
        title = m["title"].replace("|", "\\|")
        link = "[%s](%s/%s/%s)" % (title, REPO_BLOB, lang, m["_file"])
        rows.append("| %s | %s | %s |" % (m["id"], link, m.get("objective", "").replace("|", "\\|")))
    return "\n" + head + "\n" + "\n".join(rows) + "\n"


def render(text, c, is_site):
    def number(m):
        return "<!--n:%s-->%d<!--/n-->" % (m.group(1), c[m.group(1)])
    text = re.sub(r"<!--n:(\w+)-->.*?<!--/n-->", number, text, flags=re.S)

    def phrase(m):
        noun, key = m.group(1), m.group(2)
        return "<!--ar:%s:%s-->%d %s<!--/ar-->" % (noun, key, c[key], ar_form(c[key], noun))
    text = re.sub(r"<!--ar:(\w+):(\w+)-->.*?<!--/ar-->", phrase, text, flags=re.S)

    def noun_only(m):
        noun, key = m.group(1), m.group(2)
        return "<!--arnoun:%s:%s-->%s<!--/arnoun-->" % (noun, key, ar_form(c[key], noun))
    text = re.sub(r"<!--arnoun:(\w+):(\w+)-->.*?<!--/arnoun-->", noun_only, text, flags=re.S)

    for lang in ("en", "ar"):
        if is_site:
            text = re.sub(r"(<!--lessons:%s-->).*?(<!--/lessons-->)" % lang,
                          lambda m: m.group(1) + site_rows(lang) + m.group(2), text, flags=re.S)
        else:
            text = re.sub(r"(<!--table:%s-->).*?(<!--/table-->)" % lang,
                          lambda m: m.group(1) + readme_table(lang) + m.group(2), text, flags=re.S)

    if is_site:
        desc = ("Shabakah is an isolated Docker lab you SSH into to learn network security "
                "by doing: %d hands on lessons, %d live practice services, a %d flag capture "
                "the flag hunt, achievements, and a guide that checks your answers. "
                "English and Arabic." % (c["lessons"], c["targets"], c["flags"]))
        text = re.sub(r'(<meta name="description" content=")[^"]*(")',
                      lambda m: m.group(1) + desc + m.group(2), text)
        og = ("%d lessons, %d live practice services, a capture the flag hunt, and a guide "
              "that checks your work. English and Arabic." % (c["lessons"], c["targets"]))
        text = re.sub(r'(<meta (?:property="og:description"|name="twitter:description") content=")[^"]*(")',
                      lambda m: m.group(1) + og + m.group(2), text)
        with open(os.path.join(ROOT, "VERSION"), encoding="utf-8") as fh:
            version = fh.read().strip()
        text = re.sub(r"v\d+\.\d+\.\d+(  \|  github\.com/SiteQ8/Shabakah)", lambda m: "v" + version + m.group(1), text)
        text = re.sub(r'("softwareVersion":")[^"]*(")', lambda m: m.group(1) + version + m.group(2), text)
        # The hero terminal mirrors the guide banner: 5 lessons done, 40 points.
        text = re.sub(r'(\{t:"5/)\d+( ",cls:"g"\})', lambda m: "%s%d%s" % (m.group(1), c["lessons"], m.group(2)), text)
        text = re.sub(r'(\{t:"40/)\d+( ",cls:"u"\})', lambda m: "%s%d%s" % (m.group(1), c["points"], m.group(2)), text)
    return text


def main(argv):
    check = "--check" in argv
    c = counts()
    stale = []
    for path, is_site in ((SITE, True), (README, False)):
        with open(path, "r", encoding="utf-8") as fh:
            before = fh.read()
        after = render(before, c, is_site)
        if after != before:
            stale.append(os.path.relpath(path, ROOT))
            if not check:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(after)
    if check:
        if stale:
            print("stale: %s (run python3 tools/build_site.py)" % ", ".join(stale))
            return 1
        print("ok: site and README match the lab (%s)" % ", ".join("%s=%d" % kv for kv in sorted(c.items())))
        return 0
    print("rendered: %s" % (", ".join(stale) if stale else "nothing changed"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
