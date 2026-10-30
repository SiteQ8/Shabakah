#!/usr/bin/env python3
# Renders the terminal screenshots shown on the website and in the README.
# Author: Ali AlEnezi (SiteQ8)
#
# Runs the real guide under a pseudo terminal against the real practice
# services, with a learner part way through (five lessons done, three flags
# found), turns its colour output into HTML with the site's terminal palette,
# and photographs each screen with a headless browser.
#
# Writes docs/screenshots/<view>.png (English) and docs/screenshots/ar/<view>.png
# (Arabic). Needs python3, openssl and the playwright package with Chromium.
# Usage: python3 tools/screenshots.py

import html
import json
import os
import pty
import re
import select
import shutil
import struct
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "screenshots")

VIEWS = [
    ("menu", [], b"9\n"),
    ("lesson", ["lesson", "03"], b""),
    ("ctf", ["ctf"], b""),
    ("achievements", ["achievements"], b""),
    ("targets", ["targets"], b""),
    ("cheat", ["cheat"], b""),
]
TITLES = {
    "en": {"menu": "The guide when you SSH in", "lesson": "A lesson",
           "ctf": "Capture the flag", "achievements": "Achievements",
           "targets": "Practice services", "cheat": "Cheat sheet"},
    "ar": {"menu": "المرشد عند الدخول", "lesson": "درس",
           "ctf": "التحديات", "achievements": "الإنجازات",
           "targets": "خدمات التدريب", "cheat": "الأوامر السريعة"},
}
PALETTE = {"31": "#ff8a80", "32": "#7ce0b3", "33": "#f2c14e", "34": "#7aa2f7",
           "35": "#c792ea", "36": "#5FD3C6"}

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans+Arabic:wght@400;600&display=swap" rel="stylesheet">
<style>
body{margin:0;padding:24px;background:#0E1428;display:inline-block}
.term{background:#080C18;color:#D9E6E0;border:1px solid #2E3E5C;border-radius:14px;overflow:hidden;
      font-family:'IBM Plex Mono','IBM Plex Sans Arabic',monospace;font-size:14px;line-height:1.55;width:780px}
.bar{display:flex;align-items:center;gap:8px;padding:10px 14px;background:rgba(255,255,255,.03);
     border-bottom:1px solid #233149;color:#6E8791;font-size:12px}
.bar i{width:11px;height:11px;border-radius:50%;display:inline-block;margin-right:6px}
pre{margin:0;padding:16px 18px;white-space:pre-wrap;word-break:break-word;font:inherit}
</style></head><body><div class="term"><div class="bar"><span><i style="background:#ff5f57"></i>
<i style="background:#febc2e"></i><i style="background:#28c840"></i></span><span>learner@shabakah: TITLE</span></div>
<pre>BODY</pre></div></body></html>"""


def ansi_to_html(text):
    text = text.replace("\r\n", "\n").replace("\r", "")
    text = re.sub(r"\x1b\[\?[0-9;]*[a-zA-Z]", "", text)
    text = re.sub(r"\x1b\][^\x07]*\x07", "", text)
    text = re.sub(r"\x1b\[[0-9;]*[A-HJKfX]", "", text)
    out, style, opened = [], {"b": False, "d": False, "c": None}, False
    for m in re.finditer(r"\x1b\[([0-9;]*)m|([^\x1b]+)", text):
        codes, chunk = m.group(1), m.group(2)
        if codes is not None:
            if opened:
                out.append("</span>")
                opened = False
            for code in codes.split(";"):
                if code in ("", "0"):
                    style = {"b": False, "d": False, "c": None}
                elif code == "1":
                    style["b"] = True
                elif code == "2":
                    style["d"] = True
                elif code in PALETTE:
                    style["c"] = PALETTE[code]
            css = []
            if style["b"]:
                css.append("font-weight:600")
            if style["d"]:
                css.append("opacity:.6")
            if style["c"]:
                css.append("color:" + style["c"])
            if css:
                out.append('<span style="%s">' % ";".join(css))
                opened = True
        elif chunk:
            out.append(html.escape(chunk))
    if opened:
        out.append("</span>")
    return "".join(out).strip("\n")


def capture(env, args, feed):
    pid, fd = pty.fork()
    if pid == 0:
        os.chdir(ROOT)
        os.execvpe(sys.executable, [sys.executable, os.path.join(ROOT, "lab", "bin", "netsec")] + args, env)
    import fcntl
    import termios
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", 48, 92, 0, 0))
    if feed:
        time.sleep(0.4)
        os.write(fd, feed)
    data = b""
    while True:
        try:
            ready, _, _ = select.select([fd], [], [], 2.0)
        except OSError:
            break
        if not ready:
            break
        try:
            chunk = os.read(fd, 65536)
        except OSError:
            break
        if not chunk:
            break
        data += chunk
    try:
        os.close(fd)
        os.waitpid(pid, 0)
    except OSError:
        pass
    return data.decode("utf-8", "replace")


def main():
    from playwright.sync_api import sync_playwright
    work = tempfile.mkdtemp(prefix="shabakah-shots-")
    cert, key = os.path.join(work, "lab.crt"), os.path.join(work, "lab.key")
    subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-keyout", key,
                    "-out", cert, "-days", "3650", "-subj",
                    "/C=KW/O=Shabakah Lab/OU=flag{shabakah_cert_metadata}/CN=shabakah.lab",
                    "-addext", "subjectAltName=DNS:shabakah.lab"],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    env = dict(os.environ, SHABAKAH_CERT=cert, SHABAKAH_KEY=key, TERM="xterm-256color",
               SHABAKAH_LESSONS=os.path.join(ROOT, "lab", "lessons"), SHABAKAH_NOPAGER="1",
               COLUMNS="92", LINES="48", HOME=os.path.join(work, "home"))
    env.pop("NO_COLOR", None)
    os.makedirs(os.path.join(env["HOME"], ".shabakah"))
    targets = subprocess.Popen([sys.executable, os.path.join(ROOT, "lab", "targets", "targets.py")],
                               env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    with open(os.path.join(env["HOME"], ".shabakah", "progress.json"), "w") as fh:
        json.dump({"completed": ["01", "02", "03", "04", "05"], "flags": ["recon", "html", "debug"]}, fh)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--no-sandbox"])
            for lang in ("en", "ar"):
                with open(os.path.join(env["HOME"], ".shabakah", "config.json"), "w") as fh:
                    json.dump({"lang": lang}, fh)
                folder = OUT if lang == "en" else os.path.join(OUT, "ar")
                os.makedirs(folder, exist_ok=True)
                for name, args, feed in VIEWS:
                    body = ansi_to_html(capture(env, args, feed))
                    page_html = PAGE.replace("TITLE", html.escape(TITLES[lang][name])).replace("BODY", body)
                    if lang == "ar":
                        page_html = page_html.replace('<html>', '<html lang="ar">')
                    page = browser.new_page(device_scale_factor=2)
                    page.set_content(page_html, wait_until="networkidle")
                    page.wait_for_timeout(300)
                    page.query_selector(".term").screenshot(path=os.path.join(folder, name + ".png"))
                    page.close()
                    print("wrote", os.path.relpath(os.path.join(folder, name + ".png"), ROOT))
            browser.close()
    finally:
        targets.terminate()
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
