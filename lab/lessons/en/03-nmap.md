---
id: 03
title: Port scanning with nmap
objective: Discover which ports are open on a host and reason about scan types.
est_min: 12
challenge_type: dynamic
challenge_check: open_ports
challenge_prompt: Scan localhost and list the open application ports of the lab, separated by commas.
challenge_hint: A TCP connect scan of all ports works without extra privilege. Try nmap -sT -p- 127.0.0.1 and read the open ports.
---

# Port scanning with nmap

A port scan answers the second question of any assessment. Given a host, which
doors are open. nmap is the standard tool and it rewards understanding rather
than memorising flags.

## Scan types worth knowing

- **Connect scan** `-sT` completes the full TCP handshake. It needs no special
  privilege and always works, but it is louder and slower.
- **SYN scan** `-sS` sends a SYN and never finishes the handshake. It is faster
  and quieter, but it needs raw socket privilege, so run it with sudo.
- **UDP scan** `-sU` probes UDP ports. UDP gives no clean open signal, so it is
  slow and needs care.

## Choosing what to scan

- `-p 22,80,443` scans a list, `-p 1-1024` scans a range, `-p-` scans all
  65535 ports.
- `-sV` asks nmap to talk to each open port and guess the service and version.
- `-A` turns on version detection, default scripts and more. It is thorough and
  noisy.
- `-T4` speeds up timing on a fast, local network like this lab.

## Why a defender cares

You should scan your own estate before someone else does. The output is your
inventory of exposure. When a scan shows a port you did not expect, you have
found either a service you forgot or something you did not put there.

## Try it

Start with a plain connect scan of every port on the loopback address.

```
nmap -sT -p- 127.0.0.1
```

Then ask what is actually running on the open ports.

```
nmap -sV -p 8080,8443,9000 127.0.0.1
```

If you want to feel the difference, compare a SYN scan, which needs sudo.

```
sudo nmap -sS -p- 127.0.0.1
```

## What you should notice

Ignore port 22 and the DNS resolver for this challenge. List the open ports that
belong to the practice application services. The version scan in the second
command names each one.
