#!/usr/bin/env python3
# Shabakah practice targets.
# Author: Ali AlEnezi (SiteQ8)
#
# Small, deliberately simple services that give the learner something real to
# scan, capture, and inspect. Everything binds locally inside the container and
# nothing here reaches the outside world. Several services model bad habits on
# purpose (a cleartext credential, a chatty banner, an undocumented debug
# command, a reused password) so that the lessons have real findings to uncover
# and the capture the flag board has something to hunt.

import os
import ssl
import sys
import json
import time
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HTTP_PORT = int(os.environ.get("SHABAKAH_HTTP_PORT", "8080"))
HTTPS_PORT = int(os.environ.get("SHABAKAH_HTTPS_PORT", "8443"))
ENUM_PORT = int(os.environ.get("SHABAKAH_ENUM_PORT", "9000"))
UDP_PORT = int(os.environ.get("SHABAKAH_UDP_PORT", "9001"))
CONSOLE_PORT = int(os.environ.get("SHABAKAH_CONSOLE_PORT", "2323"))
CERT = os.environ.get("SHABAKAH_CERT", "/opt/shabakah/tls/lab.crt")
KEY = os.environ.get("SHABAKAH_KEY", "/opt/shabakah/tls/lab.key")

SERVER_BANNER = "Shabakah-Web/1.0"
LAB_TOKEN = "SHBK-7788"
LAB_USER = "admin"
LAB_PASS = "lab-P@ss"
CONSOLE_HOSTNAME = "netadmin-console-01"

PAGE_HOME = """<!doctype html>
<html><head><meta charset="utf-8"><title>Shabakah lab web</title></head>
<body>
<h1>Shabakah practice web service</h1>
<p>This service exists so you can practise. Try /login and /flag.</p>
<!-- TODO remove before go live: flag{shabakah_hidden_in_html} -->
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

PAGE_ROBOTS = """User-agent: *
Disallow: /admin-notes
Disallow: /backup/
"""

PAGE_ADMIN_NOTES = """<!doctype html>
<html><head><meta charset="utf-8"><title>admin notes</title></head>
<body>
<h1>Ops notes (internal)</h1>
<ul>
<li>The netadmin console still listens on tcp/2323. Same password as the legacy login, we never rotated it.</li>
<li>Backups of the old config live under /backup/ until the migration finishes.</li>
<li>Lab resolver: 127.0.0.1 port 5353, zone shabakah.lab.</li>
</ul>
</body></html>
"""

PAGE_BACKUP_INDEX = """<!doctype html>
<html><head><meta charset="utf-8"><title>Index of /backup/</title></head>
<body><h1>Index of /backup/</h1><pre>
<a href="/backup/config.bak">config.bak</a>          2026-08-30  412
</pre></body></html>
"""

PAGE_CONFIG_BAK = """# legacy app config (backup)
db_host = 10.13.37.30
db_user = app
db_password = Summer2026!
api_key = SHBK-INTERNAL-9c1f
debug = true
# note left by a tired admin: flag{shabakah_forgotten_backup}
"""

API_STATUS = {"service": "shabakah-web", "version": "1.0", "debug": False,
              "endpoints": ["/", "/login", "/flag", "/robots.txt", "/api/status"]}


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
        elif path == "/robots.txt":
            self._send(PAGE_ROBOTS, ctype="text/plain; charset=utf-8")
        elif path == "/admin-notes":
            self._send(PAGE_ADMIN_NOTES)
        elif path in ("/backup", "/backup/"):
            self._send(PAGE_BACKUP_INDEX)
        elif path == "/backup/config.bak":
            self._send(PAGE_CONFIG_BAK, ctype="text/plain; charset=utf-8")
        elif path == "/api/status":
            self._send(json.dumps(API_STATUS, indent=2) + "\n", ctype="application/json")
        else:
            self._send("<h1>404 not found</h1>", status=404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length).decode("utf-8", "replace") if length else ""
        path = self.path.split("?", 1)[0]
        if path == "/login":
            if "password=" + LAB_PASS in body and "user=" + LAB_USER in body:
                self._send("<h1>Welcome admin</h1>")
            else:
                self._send("<h1>Login failed</h1>", status=401)
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


# --- Raw TCP enumeration service (port 9000) --------------------------------

def _handle_enum_client(conn, addr):
    try:
        conn.sendall(b"SHABAKAH-ENUM SERVICE v2 ready\r\n")
        conn.sendall(b"type HELP for a list of commands\r\n")
        conn.settimeout(60)
        buf = ""
        while True:
            data = conn.recv(256)
            if not data:
                break
            buf += data.decode("latin-1", "replace")
            # Process every complete line, so both interactive and piped input work.
            while "\n" in buf:
                raw, buf = buf.split("\n", 1)
                line = raw.strip()
                if not line:
                    continue
                low = line.lower()
                if low in ("quit", "exit", "bye"):
                    conn.sendall(b"bye\r\n")
                    return
                elif low == "help":
                    conn.sendall(b"commands: HELP VERSION WHOAMI TIME QUIT\r\n")
                elif low == "version":
                    conn.sendall(b"SHABAKAH-ENUM v2 build 20260914 (debug commands enabled)\r\n")
                elif low == "whoami":
                    conn.sendall(b"service-account: enumsvc\r\n")
                elif low == "time":
                    conn.sendall((time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()) + "\r\n").encode())
                elif low == "debug":
                    # Undocumented. Exactly the kind of thing enumeration is meant to find.
                    conn.sendall(b"DEBUG dump:\r\n"
                                 b"  build=20260914 pid=%d\r\n"
                                 b"  env=lab role=enumsvc\r\n"
                                 b"  FLAG=flag{shabakah_undocumented_debug}\r\n" % os.getpid())
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


# --- Cleartext admin console (port 2323) -------------------------------------
# Models a forgotten telnet style console that shares a password with the web
# login. Credentials cross the wire in the clear and the password is reused.

def _readline(conn, limit=128):
    buf = b""
    while len(buf) < limit:
        ch = conn.recv(1)
        if not ch:
            return None
        if ch in (b"\n",):
            break
        if ch == b"\r":
            continue
        buf += ch
    return buf.decode("latin-1", "replace").strip()


def _handle_console_client(conn, addr):
    try:
        conn.settimeout(90)
        conn.sendall(b"\r\nnetadmin console (cleartext) \r\n")
        for attempt in range(3):
            conn.sendall(b"login: ")
            user = _readline(conn)
            if user is None:
                return
            conn.sendall(b"Password: ")
            pw = _readline(conn)
            if pw is None:
                return
            if user == LAB_USER and pw == LAB_PASS:
                conn.sendall(b"\r\nWelcome admin. Last login from 10.13.37.5\r\n"
                             b"MOTD: password reuse is how one leak becomes three. flag{shabakah_reused_password}\r\n"
                             b"commands: HELP HOSTNAME UPTIME USERS LOGOUT\r\n")
                break
            conn.sendall(b"Login incorrect\r\n")
        else:
            conn.sendall(b"too many failures\r\n")
            return
        start = time.time()
        while True:
            conn.sendall(b"admin@console> ")
            line = _readline(conn)
            if line is None:
                return
            low = line.lower()
            if low in ("logout", "exit", "quit"):
                conn.sendall(b"bye\r\n")
                return
            elif low == "help":
                conn.sendall(b"commands: HELP HOSTNAME UPTIME USERS LOGOUT\r\n")
            elif low == "hostname":
                conn.sendall((CONSOLE_HOSTNAME + "\r\n").encode())
            elif low == "uptime":
                conn.sendall(("up %d seconds this session\r\n" % int(time.time() - start)).encode())
            elif low == "users":
                conn.sendall(b"admin operator backup\r\n")
            else:
                conn.sendall(b"unknown command, try HELP\r\n")
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass


def serve_console():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", CONSOLE_PORT))
    srv.listen(16)
    while True:
        try:
            conn, addr = srv.accept()
        except Exception:
            continue
        threading.Thread(target=_handle_console_client, args=(conn, addr), daemon=True).start()


# --- UDP banner service (port 9001) ------------------------------------------
# UDP gives a scanner nothing back unless the service chooses to answer, which
# is the whole lesson. This one answers.

def serve_udp():
    srv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", UDP_PORT))
    while True:
        try:
            data, addr = srv.recvfrom(512)
        except Exception:
            continue
        msg = data.strip().decode("latin-1", "replace").lower()
        if msg == "ping":
            reply = b"PONG\n"
        elif msg == "time":
            reply = (time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()) + "\n").encode()
        else:
            reply = b"SHABAKAH-UDP v1 ready (commands: PING TIME)\n"
        try:
            srv.sendto(reply, addr)
        except Exception:
            pass


def main():
    threads = [
        threading.Thread(target=serve_http, daemon=True),
        threading.Thread(target=serve_https, daemon=True),
        threading.Thread(target=serve_enum, daemon=True),
        threading.Thread(target=serve_console, daemon=True),
        threading.Thread(target=serve_udp, daemon=True),
    ]
    for th in threads:
        th.start()
    sys.stdout.write(
        "shabakah targets up: http :%d, https :%d, enum :%d, console :%d, udp :%d\n"
        % (HTTP_PORT, HTTPS_PORT, ENUM_PORT, CONSOLE_PORT, UDP_PORT))
    sys.stdout.flush()
    for th in threads:
        th.join()


if __name__ == "__main__":
    main()
