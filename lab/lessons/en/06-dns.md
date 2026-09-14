---
id: 06
title: DNS reconnaissance
objective: Query different record types and understand what DNS reveals.
est_min: 10
challenge_type: dynamic
challenge_check: dns_web_ip
challenge_prompt: Using the lab DNS resolver, what IP address does web.shabakah.lab resolve to?
challenge_hint: Query the lab resolver directly with dig at port 5353. Try dig @127.0.0.1 -p 5353 web.shabakah.lab A and read the answer.
---

# DNS reconnaissance

DNS is the map of a network. Before touching a host, an assessor learns the
names, the addresses behind them, and the roles those names hint at. The lab
runs a small resolver so you can practise offline.

## The tools

- **dig** is the precise query tool. It shows you exactly what the server
  answered.
- **nslookup** is simpler and interactive.
- **host** is the quickest one liner.

## Record types worth knowing

- **A** maps a name to an IPv4 address, **AAAA** to IPv6.
- **MX** names the mail servers for a domain.
- **TXT** holds free text, and often carries policy such as SPF and DKIM.
- **NS** names the authoritative servers, **PTR** maps an address back to a name.

## Querying the lab resolver

The lab resolver listens on the loopback at port 5353, so you must point dig at
it directly.

```
dig @127.0.0.1 -p 5353 web.shabakah.lab A
dig @127.0.0.1 -p 5353 shabakah.lab MX
dig @127.0.0.1 -p 5353 shabakah.lab TXT
```

Use +short when you only want the answer.

```
dig +short @127.0.0.1 -p 5353 web.shabakah.lab
```

## Why a defender cares

DNS records describe your estate to anyone who asks. Names such as vpn, mail and
db tell a story about what matters. TXT records can leak internal detail. Knowing
what your own DNS exposes, and keeping it tidy, is part of shrinking your
footprint.

## Try it

Resolve web.shabakah.lab against the lab resolver and read the IPv4 address it
returns. While you are there, look at the MX and TXT records to see how much a
zone can say about an organisation.
