#!/bin/sh
# Shabakah entrypoint. Brings the lab up, then hands control to sshd.
set -e

LEARNER_PASSWORD="${LEARNER_PASSWORD:-shabakah}"
SSH_PORT_HINT="${SSH_PORT_HINT:-2222}"

# 1. SSH host keys (generated on first run, never baked into the image).
if [ ! -f /etc/ssh/ssh_host_ed25519_key ]; then
    ssh-keygen -A >/dev/null 2>&1
fi
mkdir -p /run/sshd

# 2. Set the learner account password.
echo "learner:${LEARNER_PASSWORD}" | chpasswd

# 3. Optional public key login, if the operator passes one in.
if [ -n "$SSH_PUBKEY" ]; then
    install -d -m 700 -o learner -g learner /home/learner/.ssh
    printf '%s\n' "$SSH_PUBKEY" > /home/learner/.ssh/authorized_keys
    chmod 600 /home/learner/.ssh/authorized_keys
    chown learner:learner /home/learner/.ssh/authorized_keys
fi

# 4. Self signed certificate for the HTTPS practice target.
if [ ! -f /opt/shabakah/tls/lab.crt ]; then
    mkdir -p /opt/shabakah/tls
    openssl req -x509 -newkey rsa:2048 -nodes \
        -keyout /opt/shabakah/tls/lab.key \
        -out /opt/shabakah/tls/lab.crt \
        -days 3650 \
        -subj "/C=KW/O=Shabakah Lab/CN=shabakah.lab" \
        -addext "subjectAltName=DNS:shabakah.lab" >/dev/null 2>&1 || true
    chmod 644 /opt/shabakah/tls/lab.crt 2>/dev/null || true
    chmod 640 /opt/shabakah/tls/lab.key 2>/dev/null || true
fi

# 5. Lab DNS resolver (loopback only, no forwarding).
if command -v dnsmasq >/dev/null 2>&1; then
    rm -f /run/dnsmasq-shabakah.pid
    dnsmasq --conf-file=/etc/shabakah/dnsmasq.conf \
            --pid-file=/run/dnsmasq-shabakah.pid \
            >/var/log/shabakah-dns.log 2>&1 || \
        echo "shabakah: DNS resolver did not start, the DNS lesson may be limited"
fi

# 6. Practice targets (HTTP, HTTPS, raw TCP banner).
python3 /opt/shabakah/targets/targets.py >/var/log/shabakah-targets.log 2>&1 &

echo "==================================================================="
echo " Shabakah lab is ready."
if [ "$LEARNER_PASSWORD" = "shabakah" ]; then
    echo " SSH in:  ssh -p ${SSH_PORT_HINT} learner@localhost   password: shabakah"
else
    echo " SSH in:  ssh -p ${SSH_PORT_HINT} learner@localhost   password: (LEARNER_PASSWORD)"
fi
echo " The guide starts automatically. Type 'netsec' any time to reopen it."
echo "==================================================================="

# 7. Hand off to sshd in the foreground so it owns signals.
exec /usr/sbin/sshd -D -e
