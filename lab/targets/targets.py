#!/usr/bin/env python3
# Shabakah practice targets.
# Author: Ali AlEnezi (SiteQ8)
#
# Small, deliberately simple services that give the learner something real to
# scan, capture, and inspect. Everything binds locally inside the container and
# nothing here reaches the outside world. A couple of the services model bad
# habits on purpose (a cleartext credential, a chatty banner) so that the
# lessons on capture and enumeration have a real finding to uncover.

import os
import ssl
import sys
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HTTP_PORT = int(os.environ.get("SHABAKAH_HTTP_PORT", "8080"))
HTTPS_PORT = int(os.environ.get("SHABAKAH_HTTPS_PORT", "8443"))
ENUM_PORT = int(os.environ.get("SHABAKAH_ENUM_PORT", "9000"))
CERT = os.environ.get("SHABAKAH_CERT", "/opt/shabakah/tls/lab.crt")
KEY = os.environ.get("SHABAKAH_KEY", "/opt/shabakah/tls/lab.key")

SERVER_BANNER = "Shabakah-Web/1.0"
LAB_TOKEN = "SHBK-7788"

PAGE_HOME = """<!doctype html>
<html><head><meta charset="utf-8"><title>Shabakah lab web</title></head>
<body>
<h1>Shabakah practice web service</h1>
<p>This service exists so you can practise. Try /login and /flag.</p>
</body></html>
"""

PAGE_LOGIN = """<!doctype html>
<html><head><meta charset="utf-8"><title>login</title></head>
<body>
<h1>Legacy login</h1>
<p>This page sends its credentials over plain HTTP, which is exactly the
mistake you are here to learn to spot.</p>
<pre>auth: user=admin password=lab-P@ss role=operator</pre>
</body></html>
"""

PAGE_FLAG = """<!doctype html>
<html><head><meta charset="utf-8"><title>flag</title></head>
<body><pre>flag{shabakah_http_recon_ok}</pre></body></html>
"""


class LabHandler(BaseHTTPRequestHandler):
    server_version = SERVER_BANNER
    sys_version = ""

    def _send(self, body, status=200, ctype="text/html; charset=utf-8"):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Lab-Token", LAB_TOKEN)
        self.end_headers()
        try:
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/":
            self._send(PAGE_HOME)
        elif path == "/login":
            self._send(PAGE_LOGIN)
        elif path == "/flag":
            self._send(PAGE_FLAG)
        else:
            self._send("<h1>404 not found</h1>", status=404)

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("X-Lab-Token", LAB_TOKEN)
        self.end_headers()

    def log_message(self, fmt, *args):
        # Keep the console quiet. Real traffic is meant to be seen with tcpdump.
        return


def serve_http():
    httpd = ThreadingHTTPServer(("0.0.0.0", HTTP_PORT), LabHandler)
    httpd.serve_forever()


def serve_https():
    if not (os.path.exists(CERT) and os.path.exists(KEY)):
        sys.stderr.write("shabakah: TLS cert missing, HTTPS target disabled\n")
        return
    httpd = ThreadingHTTPServer(("0.0.0.0", HTTPS_PORT), LabHandler)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(certfile=CERT, keyfile=KEY)
    httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)
    httpd.serve_forever()


def _handle_enum_client(conn, addr):
    try:
        conn.sendall(b"SHABAKAH-ENUM SERVICE v2 ready\r\n")
        conn.sendall(b"type HELP for a list of commands\r\n")
        conn.settimeout(60)
        while True:
            data = conn.recv(256)
            if not data:
                break
            line = data.strip().decode("latin-1", "replace")
            low = line.lower()
            if low in ("quit", "exit", "bye"):
                conn.sendall(b"bye\r\n")
                break
            elif low == "help":
                conn.sendall(b"commands: HELP VERSION WHOAMI QUIT\r\n")
            elif low == "version":
                conn.sendall(b"SHABAKAH-ENUM v2 build 20260914\r\n")
            elif low == "whoami":
                conn.sendall(b"service-account: enumsvc\r\n")
            else:
                conn.sendall(("echo: " + line + "\r\n").encode("latin-1", "replace"))
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass


def serve_enum():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", ENUM_PORT))
    srv.listen(16)
    while True:
        try:
            conn, addr = srv.accept()
        except Exception:
            continue
        threading.Thread(target=_handle_enum_client, args=(conn, addr), daemon=True).start()


def main():
    threads = [
        threading.Thread(target=serve_http, daemon=True),
        threading.Thread(target=serve_https, daemon=True),
        threading.Thread(target=serve_enum, daemon=True),
    ]
    for th in threads:
        th.start()
    sys.stdout.write(
        "shabakah targets up: http :%d, https :%d, enum :%d\n"
        % (HTTP_PORT, HTTPS_PORT, ENUM_PORT))
    sys.stdout.flush()
    # Block forever.
    for th in threads:
        th.join()


if __name__ == "__main__":
    main()
