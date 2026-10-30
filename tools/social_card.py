#!/usr/bin/env python3
# Renders docs/og.png, the 1200 x 630 card shown when the site is shared.
# Author: Ali AlEnezi (SiteQ8)
#
# The numbers on the card come from the lab itself (via build_site.counts), so
# rerun this after adding lessons, flags or practice services.
# Needs the playwright package with Chromium. Usage: python3 tools/social_card.py

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import build_site  # noqa: E402

CARD = """<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans+Arabic:wght@400;600;700&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box}
body{margin:0;width:1200px;height:630px;overflow:hidden;font-family:'IBM Plex Sans Arabic',sans-serif;color:#EAEFF7;
  background:#0A0E1A;background-image:radial-gradient(900px 520px at 85% -10%,rgba(0,51,160,.55),transparent 62%),
  radial-gradient(700px 420px at 0% 110%,rgba(0,51,160,.28),transparent 60%)}
.wrap{position:absolute;inset:0;padding:64px 72px;display:grid;grid-template-columns:1fr 470px;gap:48px;align-items:center}
.brand{display:flex;align-items:center;gap:16px;font-size:30px;font-weight:700}
.brand svg{width:54px;height:54px}
.brand span{color:#9DAEC8;font-weight:600}
h1{font-size:58px;line-height:1.08;margin:30px 0 14px;letter-spacing:-.01em}
.ar{font-size:36px;font-weight:700;color:#C9D5EA;margin:0 0 34px;direction:rtl;text-align:left}
.facts{display:flex;gap:14px}
.fact{background:#121A2E;border:1px solid #2E3E5C;border-radius:14px;padding:14px 18px;min-width:118px}
.fact b{display:block;font-size:34px;color:#4F8BFF;line-height:1}
.fact span{display:block;font-size:15px;color:#9DAEC8;margin-top:6px}
.term{background:#080C18;border:1px solid #2E3E5C;border-radius:16px;overflow:hidden;box-shadow:0 30px 60px rgba(0,0,0,.45);
  font-family:'IBM Plex Mono',monospace;font-size:15px;line-height:1.6}
.bar{padding:12px 16px;border-bottom:1px solid #233149;color:#6E8791;font-size:13px}
.bar i{display:inline-block;width:11px;height:11px;border-radius:50%;margin-right:6px;vertical-align:-1px}
pre{margin:0;padding:16px 18px;color:#D9E6E0;font:inherit;white-space:pre}
.c{color:#5FD3C6}.g{color:#7ce0b3}.u{color:#f2c14e}.d{opacity:.6}
.url{position:absolute;left:72px;bottom:40px;font-size:18px;color:#9DAEC8;font-family:'IBM Plex Mono',monospace}
</style></head><body><div class="wrap"><div>
<div class="brand"><svg viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#121A2E"/><path d="M16 44 L32 20 L48 44 M16 44 L48 44" stroke="#4F8BFF" stroke-width="3" fill="none" stroke-linejoin="round"/><circle cx="16" cy="44" r="5" fill="#F2C14E"/><circle cx="32" cy="20" r="5" fill="#F2C14E"/><circle cx="48" cy="44" r="5" fill="#F2C14E"/></svg>Shabakah <span>شبكة</span></div>
<h1>A network security lab you SSH into.</h1>
<p class="ar">مختبر لأمن الشبكات في جهازك!</p>
<div class="facts">
<div class="fact"><b>LESSONS</b><span>hands on lessons</span></div>
<div class="fact"><b>TARGETS</b><span>live targets</span></div>
<div class="fact"><b>FLAGS</b><span>secret flags</span></div>
<div class="fact"><b>2</b><span>languages</span></div>
</div></div>
<div class="term"><div class="bar"><i style="background:#ff5f57"></i><i style="background:#febc2e"></i><i style="background:#28c840"></i>learner@shabakah: ~</div>
<pre><span>$ ssh -p 2222 learner@localhost</span>
<span class="d">Connecting to shabakah.lab</span> <span class="g">[ok]</span>
<span class="c">====================================</span>
<span class="c">  SHABAKAH</span>  <span class="d">|</span>  شبكة
<span class="c">====================================</span>
<span class="d">  Welcome back.</span>  <span class="g">5/LESSONS</span> <span class="d">lessons</span>  <span class="u">40/POINTS</span> <span class="d">pts</span>

  MAIN MENU
  1)  Browse lessons
  5)  Capture the flag
  6)  Achievements
  Choose a number: <span style="background:#5FD3C6">&nbsp;</span></pre></div>
</div><div class="url">shabakah.3li.info</div></body></html>"""


def main():
    from playwright.sync_api import sync_playwright
    c = build_site.counts()
    page_html = (CARD.replace("LESSONS", str(c["lessons"])).replace("TARGETS", str(c["targets"]))
                 .replace("FLAGS", str(c["flags"])).replace("POINTS", str(c["points"])))
    out = os.path.join(ROOT, "docs", "og.png")
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1200, "height": 630})
        page.set_content(page_html, wait_until="networkidle")
        page.wait_for_timeout(400)
        page.screenshot(path=out)
        browser.close()
    print("wrote docs/og.png")


if __name__ == "__main__":
    main()
