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
<link href="https://fonts.googleapis.com/css2?family=Readex+Pro:wght@300..700&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box}
body{margin:0;width:1200px;height:630px;overflow:hidden;font-family:'Readex Pro',sans-serif;color:#0A1F4D;background:#EEF2F8}
.wrap{position:absolute;inset:0;padding:60px 72px;display:grid;grid-template-columns:1fr 440px;gap:56px;align-items:center}
.brand{display:flex;align-items:center;gap:14px;font-size:28px;font-weight:600}
.brand svg{width:44px;height:44px}
.brand span{color:#56668F;font-weight:400}
h1{font-size:62px;line-height:1.04;margin:34px 0 14px;letter-spacing:-.03em;font-weight:600}
.ar{font-size:34px;font-weight:500;color:#34477A;margin:0;direction:rtl;text-align:left}
.box{background:#fff;border:2px solid #0A1F4D;border-radius:20px;padding:24px}
.box b{display:block;font-size:20px;font-weight:600;margin-bottom:16px}
.ports{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.port{display:flex;align-items:center;gap:10px;background:#EEF2F8;border:1px solid #CCD6EA;border-radius:12px;padding:12px 14px;font-family:Menlo,monospace;font-weight:700;font-size:20px}
.port.on{background:#0033A0;border-color:#0033A0;color:#fff}
.port i{width:11px;height:11px;border-radius:50%;background:#12B76A}
.plate{margin-top:18px;display:flex;justify-content:space-between;border-top:1px dashed #CCD6EA;padding-top:16px;font-size:16px;color:#34477A}
.plate em{font-style:normal;font-weight:600;color:#0033A0;font-size:24px;margin-inline-end:6px}
.url{position:absolute;left:72px;bottom:44px;font-size:18px;color:#56668F}
</style></head><body><div class="wrap"><div>
<div class="brand"><svg viewBox="0 0 32 32"><rect width="32" height="32" rx="7" fill="#0033A0"/><path d="M7 8.5h18v12h-4.5V24h-9v-3.5H7z" fill="#fff"/><rect x="10.6" y="10.5" width="2.2" height="5" rx=".6" fill="#0033A0"/><rect x="14.9" y="10.5" width="2.2" height="5" rx=".6" fill="#0033A0"/><rect x="19.2" y="10.5" width="2.2" height="5" rx=".6" fill="#0033A0"/></svg>Shabakah <span>شبكة</span></div>
<h1>A network security lab you SSH into.</h1>
<p class="ar">مختبر لأمن الشبكات في جهازك!</p>
</div>
<div class="box"><b>Shabakah lab</b>
<div class="ports"><div class="port on"><i></i>8080</div><div class="port"><i></i>8443</div><div class="port"><i></i>9000</div><div class="port"><i></i>2323</div><div class="port"><i></i>5353</div><div class="port"><i></i>9001</div></div>
<div class="plate"><span><em>LESSONS</em>lessons</span><span><em>FLAGS</em>flags</span><span><em>POINTS</em>points</span></div>
</div></div>
<div class="url">shabakah.3li.info</div>
</body></html>"""


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
