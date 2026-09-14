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
[ "$EN" -ge 10 ] || fail "expected at least 10 lessons, found $EN"
pass "en and ar both have $EN lessons"

echo "== certificate =="
openssl req -x509 -newkey rsa:2048 -nodes \
    -keyout "$SHABAKAH_KEY" -out "$SHABAKAH_CERT" \
    -days 3650 -subj "/C=KW/O=Shabakah Lab/CN=shabakah.lab" \
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
reject 02 WRONG
reject 07 example.com

echo
echo "ALL SMOKE TESTS PASSED"
