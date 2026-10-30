#!/bin/sh
# Shabakah end to end test. Starts the built image and works through the lab
# the way a learner would: every challenge is answered and every flag is found
# over the network with the tools inside the lab, then submitted.
# Needs: docker and an image. Usage: sh tests/e2e.sh [image]
set -eu

IMAGE="${1:-shabakah:latest}"
NAME="shabakah-e2e-$$"
PASSED=0

fail() { echo "FAIL: $1"; docker logs "$NAME" 2>&1 | tail -20 || true; cleanup; exit 1; }
pass() { echo "ok: $1"; PASSED=$((PASSED + 1)); }
cleanup() { docker rm -f "$NAME" >/dev/null 2>&1 || true; }
trap cleanup EXIT

# run a command inside the lab as the learner, with a login like environment
lab() { docker exec -u learner -e HOME=/home/learner -e NO_COLOR=1 "$NAME" sh -c "$1"; }
root() { docker exec "$NAME" sh -c "$1"; }

echo "== start $IMAGE =="
docker run -d --name "$NAME" --cap-add NET_ADMIN "$IMAGE" >/dev/null
i=0
until lab "nc -z 127.0.0.1 8080 && nc -z 127.0.0.1 8443 && nc -z 127.0.0.1 2323" 2>/dev/null; do
    i=$((i + 1)); [ "$i" -lt 60 ] || fail "practice services did not come up"; sleep 1
done
pass "lab is up"

echo "== hardening =="
root "ss -H -ltn" | grep -E ':(8080|8443|9000|2323) ' | grep -v '127.0.0.1' && fail "a practice service listens beyond loopback" || pass "practice services listen on loopback only"
[ "$(root "ps -o user= -C python3 | sort -u | tr -d ' '")" = "shabakah" ] && pass "practice services run as the shabakah account" || fail "practice services are not running as shabakah"
lab "cat /opt/shabakah/targets/targets.py" >/dev/null 2>&1 && fail "the learner can read the target source" || pass "target source is not readable by the learner"
lab "grep -q 'flag{shabakah' /usr/local/bin/netsec" && fail "the guide holds plaintext flags" || pass "the guide holds no plaintext flags"
[ "$(lab 'netsec version')" = "shabakah $(cat "$(dirname "$0")/../VERSION")" ] && pass "guide reports the release version" || fail "guide version differs from VERSION"

echo "== every lesson, answered with the lab tools =="
answer() {
    # $1 lesson id, $2 shell that prints the answer inside the lab
    ans="$(lab "$2" | head -1 | tr -d '\r')"
    [ -n "$ans" ] || fail "lesson $1: could not derive an answer"
    if lab "netsec check $1 \"$ans\"" >/dev/null; then pass "lesson $1 solved ($ans)"; else fail "lesson $1 rejected '$ans'"; fi
}
answer 01 "ss -H -ltn | awk '{print \$4}' | sed 's/.*://' | sort -u | wc -l"
answer 02 "curl -sI http://127.0.0.1:8080 | sed -n 's/^X-Lab-Token: *//p'"
answer 03 "nmap -sT -p- --open 127.0.0.1 -oG - | grep -o '[0-9]*/open' | cut -d/ -f1 | grep -vx 22 | grep -vx 5353 | paste -sd, -"
answer 04 "printf 'QUIT\n' | nc -w2 127.0.0.1 9000 | grep -o 'v[0-9][0-9.]*' | head -1"
answer 05 "curl -s http://127.0.0.1:8080/login | grep -o 'password=[^ <]*' | cut -d= -f2"
answer 06 "dig +short @127.0.0.1 -p 5353 web.shabakah.lab A"
answer 07 "echo | openssl s_client -connect 127.0.0.1:8443 2>/dev/null | openssl x509 -noout -subject | sed 's/.*CN *= *//'"
answer 08 "echo DROP"
answer 09 "echo port scan"
answer 10 "echo least privilege"
answer 11 "printf PING | nc -u -w1 127.0.0.1 9001"
answer 12 "printf 'admin\nlab-P@ss\nHOSTNAME\nLOGOUT\n' | nc -w3 127.0.0.1 2323 | grep -o 'netadmin-console-[0-9]*' | head -1"
answer 13 "tcpdump -nr \"\$SHABAKAH_DATA/pcaps/incident.pcap\" 'tcp[tcpflags] == tcp-syn' 2>/dev/null | awk '{print \$3}' | cut -d. -f1-4 | sort | uniq -c | sort -rn | awk 'NR==1{print \$2}'"
answer 14 "grep 'Failed password' \"\$SHABAKAH_DATA/logs/auth.log\" | grep -o 'from [0-9.]*' | sort | uniq -c | sort -rn | awk 'NR==1{print \$3}'"
answer 15 "echo PermitRootLogin"
answer 16 "h=\$(curl -skI https://127.0.0.1:8443/); n=0; for x in Strict-Transport-Security Content-Security-Policy X-Content-Type-Options X-Frame-Options; do echo \"\$h\" | grep -qi \"^\$x:\" || n=\$((n+1)); done; echo \$n"
answer 17 "nmap -sT -p 8080 --script http-title 127.0.0.1 | sed -n 's/.*http-title: *//p'"
lab "netsec check 03 8080,8443,9000" >/dev/null && fail "lesson 03 accepted a scan that missed the console" || pass "lesson 03 rejects an incomplete scan"
lab "netsec check 16 4" >/dev/null && fail "lesson 16 accepted a wrong count" || pass "lesson 16 rejects a wrong count"

echo "== every flag, found on the wire and submitted =="
found() {
    flag="$(lab "$2" | grep -o 'flag{[a-z_]*}' | head -1)"
    [ -n "$flag" ] || fail "flag $1 not found on the wire"
    lab "netsec submit '$flag'" >/dev/null || fail "flag $1 was rejected"
    pass "flag $1 found and accepted"
}
found recon  "curl -s http://127.0.0.1:8080/flag"
found html   "curl -s http://127.0.0.1:8080/"
found backup "curl -s http://127.0.0.1:8080/robots.txt >/dev/null; curl -s http://127.0.0.1:8080/backup/config.bak"
found debug  "printf 'DEBUG\nQUIT\n' | nc -w2 127.0.0.1 9000"
found reuse  "printf 'admin\nlab-P@ss\nLOGOUT\n' | nc -w3 127.0.0.1 2323"
found cert   "nmap -sT -p 8443 --script ssl-cert -v 127.0.0.1"
lab "netsec submit recon" >/dev/null && fail "a flag id was accepted as a flag" || pass "flag ids are not accepted as flags"
lab "netsec progress" | grep -q "Points: 110 of 110" && pass "full score" || fail "score is not complete"

echo "== certificate, Arabic screens, reset =="
lab "netsec certificate 'E2E Learner'" | grep -q "E2E Learner" && pass "certificate printed" || fail "certificate missing"
lab "test -s ~/shabakah-certificate.txt" && pass "certificate saved" || fail "certificate file missing"
lab "netsec lang ar >/dev/null; for v in lessons targets cheat ctf achievements progress help; do netsec \$v; done; netsec submit 'flag{not_real}'; printf '9\n' | netsec" >/tmp/shabakah-ar-$$.txt 2>&1 || true
grep -q Traceback /tmp/shabakah-ar-$$.txt && fail "an Arabic screen crashed" || pass "every Arabic screen renders"
grep -q "يعمل" /tmp/shabakah-ar-$$.txt && pass "Arabic target status shown" || fail "Arabic target status missing"
rm -f /tmp/shabakah-ar-$$.txt
lab "netsec lang en >/dev/null; netsec reset --yes" >/dev/null && pass "reset works" || fail "reset failed"
lab "netsec progress" | grep -q "Lessons completed: 0 of" && pass "progress cleared" || fail "progress not cleared"

echo
echo "ALL E2E TESTS PASSED ($PASSED checks)"
