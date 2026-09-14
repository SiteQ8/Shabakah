# Shabakah - interactive network security lab you SSH into.
# Author: Ali AlEnezi (SiteQ8)
FROM debian:bookworm-slim

LABEL org.opencontainers.image.title="Shabakah" \
      org.opencontainers.image.description="Interactive network security lab you SSH into to learn by doing" \
      org.opencontainers.image.authors="Ali AlEnezi (SiteQ8)" \
      org.opencontainers.image.source="https://github.com/SiteQ8/Shabakah" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.version="1.1.0"

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# Toolset for hands on network security practice, plus sshd for access.
RUN apt-get update && apt-get install -y --no-install-recommends \
        openssh-server \
        sudo \
        bash \
        ca-certificates \
        python3 \
        openssl \
        nmap \
        tcpdump \
        ngrep \
        netcat-openbsd \
        socat \
        curl \
        wget \
        dnsutils \
        dnsmasq \
        whois \
        iproute2 \
        net-tools \
        iputils-ping \
        traceroute \
        mtr-tiny \
        nftables \
        iptables \
        hping3 \
        jq \
        less \
        nano \
        man-db \
        manpages \
        procps \
        tini \
    && rm -rf /var/lib/apt/lists/*

# Unprivileged learner account.
RUN useradd -m -s /bin/bash learner \
    && adduser learner sudo \
    && install -d -m 755 /opt/shabakah /etc/shabakah

# Lab content and tooling.
COPY lab/bin/netsec /usr/local/bin/netsec
COPY lab/targets/targets.py /opt/shabakah/targets/targets.py
COPY lab/targets/dnsmasq.conf /etc/shabakah/dnsmasq.conf
COPY lab/lessons /opt/shabakah/lessons
COPY lab/data /opt/shabakah/data
COPY lab/sshd_shabakah.conf /etc/ssh/sshd_config.d/shabakah.conf
COPY lab/profile-shabakah.sh /etc/profile.d/shabakah.sh
COPY lab/motd /etc/motd
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

RUN chmod +x /usr/local/bin/netsec /usr/local/bin/entrypoint.sh \
    && chmod 644 /etc/profile.d/shabakah.sh

ENV SHABAKAH_LESSONS=/opt/shabakah/lessons \
    SHABAKAH_DATA=/opt/shabakah/data

EXPOSE 22 8080 8443 9000 9001 2323 5353

ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]
