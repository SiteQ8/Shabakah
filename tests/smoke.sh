#!/bin/sh
# Shabakah smoke test. Validates the guide and the live challenge checks that
# rely only on Python sockets and openssl, so it runs without Docker.
# Needs: python3, openssl. Run from the repo root: sh tests/smoke.sh
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export SHABAKAH_LESSONS="$ROOT/lab/lessons"
export NO_COLOR=1

WORK="$(mktemp -d)"
export HOME="$WORK"
export SHABAKAH_CERT="$WORK/lab.crt"
export SHABAKAH_KEY="$WORK/lab.key"

fail() { echo "FAIL: $1"; cleanup; exit 1; }
pass() { echo "ok: $1"; }

TPID=""
cleanup() {
    [ -n "$TPID" ] && kill "$TPID" 2>/dev/null || true
    rm -rf "$WORK"
}
trap cleanup EXIT

echo "== syntax =="
python3 -m py_compile "$ROOT/lab/bin/netsec" || fail "netsec does not compile"
python3 -m py_compile "$ROOT/lab/targets/targets.py" || fail "targets.py does not compile"
pass "python compiles"

echo "== lesson parity =="
EN=$(ls "$ROOT"/lab/lessons/en/*.md | wc -l | tr -d ' ')
AR=$(ls "$ROOT"/lab/lessons/ar/*.md | wc -l | tr -d ' ')
[ "$EN" = "$AR" ] || fail "lesson count mismatch en=$EN ar=$AR"
[ "$EN" -ge 15 ] || fail "expected at least 15 lessons, found $EN"
pass "en and ar both have $EN lessons"

echo "== every dynamic check referenced by a lesson exists in the guide =="
MISSING=$(python3 - "$ROOT" <<'PYEOF'
import os, re, sys
root = sys.argv[1]
src = open(os.path.join(root, "lab/bin/netsec"), encoding="utf-8").read()
known = set(re.findall(r'"([a-z_]+)":\s*check_', src))
missing = []
for d in ("en", "ar"):
    for fn in os.listdir(os.path.join(root, "lab/lessons", d)):
        text = open(os.path.join(root, "lab/lessons", d, fn), encoding="utf-8").read()
        m = re.search(r"challenge_type:\s*dynamic", text)
        c = re.search(r"challenge_check:\s*(\S+)", text)
        if m and c and c.group(1) not in known:
            missing.append(d + "/" + fn + " -> " + c.group(1))
print("\n".join(missing))
PYEOF
)
[ -z "$MISSING" ] || fail "dynamic checks missing from guide: $MISSING"
pass "all dynamic checks resolve"

echo "== certificate =="
openssl req -x509 -newkey rsa:2048 -nodes \
    -keyout "$SHABAKAH_KEY" -out "$SHABAKAH_CERT" \
    -days 3650 -subj "/C=KW/O=Shabakah Lab/OU=flag{shabakah_cert_metadata}/CN=shabakah.lab" \
    -addext "subjectAltName=DNS:shabakah.lab" >/dev/null 2>&1 || fail "cert generation failed"
pass "self signed cert generated"

echo "== start targets =="
python3 "$ROOT/lab/targets/targets.py" >"$WORK/targets.log" 2>&1 &
TPID=$!
sleep 2
grep -q "targets up" "$WORK/targets.log" || fail "targets did not start"
pass "targets are up"

echo "== live challenge checks =="
check() {
    if python3 "$ROOT/lab/bin/netsec" check "$1" "$2" >/dev/null 2>&1; then
        pass "check $1 passes"
    else
        fail "check $1 '$2' did not pass"
    fi
}
reject() {
    if python3 "$ROOT/lab/bin/netsec" check "$1" "$2" >/dev/null 2>&1; then
        fail "check $1 '$2' should have failed"
    else
        pass "check $1 rejects a wrong answer"
    fi
}

check 02 SHBK-7788
check 03 "8080,8443,9000"
check 04 v2
check 05 "lab-P@ss"
check 07 shabakah.lab
check 08 DROP
check 09 "port scan"
check 10 "least privilege"
check 11 PONG
check 12 netadmin-console-01
check 13 10.13.37.66
check 14 203.0.113.77
check 15 PermitRootLogin
reject 02 WRONG
reject 07 example.com
reject 11 NOPE

echo "== sample data files present and readable =="
[ -s "$ROOT/lab/data/pcaps/incident.pcap" ] && pass "incident.pcap present" || fail "incident.pcap missing"
[ -s "$ROOT/lab/data/logs/auth.log" ] && pass "auth.log present" || fail "auth.log missing"
python3 -c "
import struct,sys
d=open('$ROOT/lab/data/pcaps/incident.pcap','rb').read()
magic=struct.unpack('<I', d[:4])[0]
sys.exit(0 if magic==0xA1B2C3D4 else 1)
" && pass "incident.pcap has a valid pcap header" || fail "incident.pcap header invalid"
grep -q "203.0.113.77" "$ROOT/lab/data/logs/auth.log" && pass "auth.log contains the attacker address" || fail "auth.log missing attacker"

echo "== capture the flag flow =="
flag() {
    if python3 "$ROOT/lab/bin/netsec" submit "$1" >/dev/null 2>&1; then
        pass "flag accepted: $1"
    else
        fail "flag rejected: $1"
    fi
}
# every flag must be reachable from the running targets and accepted on submit
for f in \
    "flag{shabakah_http_recon_ok}" \
    "flag{shabakah_hidden_in_html}" \
    "flag{shabakah_forgotten_backup}" \
    "flag{shabakah_undocumented_debug}" \
    "flag{shabakah_reused_password}" \
    "flag{shabakah_cert_metadata}"; do
    flag "$f"
done
if python3 "$ROOT/lab/bin/netsec" submit "flag{not_real}" >/dev/null 2>&1; then
    fail "a fake flag was accepted"
else
    pass "fake flag rejected"
fi
# after all six, the score line should read 110 of 110
python3 "$ROOT/lab/bin/netsec" progress | grep -q "110 of 110" && pass "full score reached" || fail "score not 110 of 110"

echo "== flags are actually reachable on the wire =="
reachable() {
    echo "$2" | grep -q "$1" && pass "reachable: $1" || fail "not reachable: $1"
}
reachable "flag{shabakah_http_recon_ok}"      "$(curl -s http://127.0.0.1:8080/flag)"
reachable "flag{shabakah_hidden_in_html}"     "$(curl -s http://127.0.0.1:8080/)"
reachable "flag{shabakah_forgotten_backup}"   "$(curl -s http://127.0.0.1:8080/backup/config.bak)"
reachable "flag{shabakah_cert_metadata}"      "$(echo | openssl s_client -connect 127.0.0.1:8443 2>/dev/null | openssl x509 -noout -subject 2>/dev/null)"

echo
echo "ALL SMOKE TESTS PASSED"
