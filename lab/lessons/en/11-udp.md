---
id: 11
title: UDP services and why they hide
objective: Scan and talk to a UDP service, and understand why UDP is easy to miss.
est_min: 10
challenge_type: dynamic
challenge_check: udp_banner
challenge_prompt: Send the word PING to the lab UDP service on port 9001 and read what it answers. What one word comes back?
challenge_hint: UDP needs netcat in UDP mode. Try printf 'PING' | nc -u -w1 127.0.0.1 9001 and read the reply.
---

# UDP services and why they hide

Most of what you have scanned so far speaks TCP, which announces itself with a
handshake. UDP does not. It is connectionless, so a port can be wide open and
still answer a scanner with complete silence. That silence is the whole lesson.

## Why UDP is awkward to scan

- There is no handshake, so an open UDP port that chooses not to reply looks the
  same as a filtered one.
- A closed UDP port is only revealed indirectly, when the host sends back an
  ICMP port unreachable message, and hosts often rate limit those.
- So UDP scans are slow and need care. You confirm a service by speaking its
  protocol, not by watching for a handshake.

## Scanning UDP with nmap

```
sudo nmap -sU -p 9001 127.0.0.1
sudo nmap -sU -sV -p 9001 127.0.0.1
```

The version probe matters here, because it makes nmap send real payloads and
wait for a real answer instead of guessing from silence.

## Talking to it by hand

netcat speaks UDP with the -u flag. Send a probe and read the reply.

```
printf 'PING' | nc -u -w1 127.0.0.1 9001
printf 'TIME' | nc -u -w1 127.0.0.1 9001
printf 'hello' | nc -u -w1 127.0.0.1 9001
```

The service understands PING and TIME, and answers anything else with its
banner.

## Why a defender cares

UDP carries DNS, NTP, SNMP, syslog, and plenty of other services that attackers
love and defenders forget. Because UDP hides from a careless scan, a forgotten
UDP service can sit exposed for a long time. Scan UDP on your own hosts on
purpose, and remember that no reply is not the same as no service.

## Try it

Send PING to port 9001 with netcat in UDP mode and read the single word it
sends back.
