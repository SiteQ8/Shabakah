#!/usr/bin/env python3
# Lesson linter for Shabakah.
# Author: Ali AlEnezi (SiteQ8)
#
# Checks that every lesson exists in both languages, that the Arabic file
# keeps the same challenge and the same commands as the English one, and that
# the Arabic prose follows the house rules: no banned characters or words, and
# no full stop in the middle of a paragraph (clauses are joined with
# conjunctions, the full stop closes the paragraph).
#
# Usage: python3 tools/lint_lessons.py [lesson.md ...]
# With no arguments every lesson under lab/lessons is checked.
# Exits 1 when anything is wrong.

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LESSONS = os.path.join(ROOT, "lab", "lessons")

# Values the Arabic file must copy from the English file, byte for byte.
LOCKED = ["id", "est_min", "challenge_type", "challenge_check",
          "challenge_answer", "challenge_match"]
REQUIRED = ["id", "title", "tag", "objective", "est_min", "challenge_type",
            "challenge_prompt", "challenge_hint"]
TEXT_FIELDS = ["title", "tag", "objective", "challenge_prompt", "challenge_hint"]

BANNED_CHARS = {
    "–": "en dash", "—": "em dash", "·": "middle dot",
    "→": "arrow", "•": "bullet symbol",
}
BANNED_WORDS_AR = ["حاوية", "الحاوية", "حاويات", "حاويته", "الخليج الفارسي"]
BANNED_WORDS_ANY = ["claude", "anthropic", "nbk"]

AR_LETTER = re.compile(r"[؀-ۿ]")
# A full stop followed by space and more Arabic text inside one paragraph.
MID_STOP = re.compile(r"\.\s+(?=[؀-ۿ])")


def split_lesson(path):
    with open(path, "r", encoding="utf-8") as fh:
        raw = fh.read()
    lines = raw.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, raw
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            meta = {}
            for line in lines[1:i]:
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
            return meta, "\n".join(lines[i + 1:])
    return None, raw


def code_blocks(body):
    return re.findall(r"```[^\n]*\n(.*?)```", body, re.S)


def prose_paragraphs(body):
    """Yield prose paragraphs: no code, no headings, each list item alone."""
    body = re.sub(r"```.*?```", "\n\n", body, flags=re.S)
    para = []
    for line in body.splitlines():
        s = line.strip()
        is_item = bool(re.match(r"^([-*]|\d+\.)\s+", s))
        if not s or s.startswith("#") or is_item:
            if para:
                yield " ".join(para)
                para = []
            if is_item:
                yield re.sub(r"^([-*]|\d+\.)\s+", "", s)
            continue
        if s.startswith(">"):
            s = s.lstrip("> ").strip()
        para.append(s)
    if para:
        yield " ".join(para)


def strip_inline_code(text):
    return re.sub(r"`[^`]*`", "CODE", text)


def lint_pair(en_path, ar_path):
    errors = []
    rel = os.path.relpath(ar_path, ROOT)
    if not os.path.exists(en_path):
        return ["%s: no English counterpart" % rel]
    me, be = split_lesson(en_path)
    ma, ba = split_lesson(ar_path)
    if me is None or ma is None:
        return ["%s: missing front matter" % rel]
    for k in REQUIRED:
        if not ma.get(k):
            errors.append("%s: front matter key '%s' is missing or empty" % (rel, k))
        if not me.get(k):
            errors.append("%s: front matter key '%s' is missing or empty"
                          % (os.path.relpath(en_path, ROOT), k))
    for k in LOCKED:
        if me.get(k, "") != ma.get(k, ""):
            errors.append("%s: '%s' differs from the English file (%r vs %r)"
                          % (rel, k, ma.get(k, ""), me.get(k, "")))
    if code_blocks(be) != code_blocks(ba):
        errors.append("%s: code blocks differ from the English file" % rel)
    for k in TEXT_FIELDS:
        v = ma.get(k, "")
        if v and not AR_LETTER.search(v):
            errors.append("%s: '%s' has no Arabic text" % (rel, k))
        if MID_STOP.search(strip_inline_code(v)):
            errors.append("%s: '%s' has a full stop in the middle: %s" % (rel, k, v[:90]))
    for para in prose_paragraphs(ba):
        clean = strip_inline_code(para)
        if MID_STOP.search(clean):
            errors.append("%s: full stop in the middle of a paragraph: %s" % (rel, para[:110]))
    with open(ar_path, "r", encoding="utf-8") as fh:
        raw_ar = fh.read()
    with open(en_path, "r", encoding="utf-8") as fh:
        raw_en = fh.read()
    for name, raw in ((rel, raw_ar), (os.path.relpath(en_path, ROOT), raw_en)):
        for ch, label in BANNED_CHARS.items():
            if ch in raw:
                errors.append("%s: contains a banned %s" % (name, label))
        low = raw.lower()
        for w in BANNED_WORDS_ANY:
            if re.search(r"\b%s\b" % w, low):
                errors.append("%s: contains the banned word '%s'" % (name, w))
    for w in BANNED_WORDS_AR:
        if w in raw_ar:
            errors.append("%s: contains the banned word '%s'" % (rel, w))
    return errors


def main(argv):
    if argv:
        pairs = []
        for p in argv:
            p = os.path.abspath(p)
            name = os.path.basename(p)
            pairs.append((os.path.join(LESSONS, "en", name), os.path.join(LESSONS, "ar", name)))
    else:
        en = sorted(f for f in os.listdir(os.path.join(LESSONS, "en")) if f.endswith(".md"))
        ar = sorted(f for f in os.listdir(os.path.join(LESSONS, "ar")) if f.endswith(".md"))
        problems = []
        if en != ar:
            problems.append("lesson files differ between en and ar: %s"
                            % sorted(set(en) ^ set(ar)))
        pairs = [(os.path.join(LESSONS, "en", f), os.path.join(LESSONS, "ar", f)) for f in en]
    errors = []
    if not argv:
        errors.extend(problems)
    for e, a in pairs:
        errors.extend(lint_pair(e, a))
    for line in errors:
        print("FAIL " + line)
    if not errors:
        print("ok: %d lesson pair(s) clean" % len(pairs))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
