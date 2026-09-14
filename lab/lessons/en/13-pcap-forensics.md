---
id: 13
title: Read a capture like an investigator
objective: Open a saved packet capture and reconstruct what happened from the packets alone.
est_min: 15
challenge_type: static
challenge_answer: (10\.13\.37\.66)
challenge_match: regex
challenge_prompt: Open the saved capture at /opt/shabakah/data/pcaps/incident.pcap and find the host that scanned the server. What is its IP address?
challenge_hint: One source sends a SYN to many different ports in a short window with almost no completed handshakes. Read the capture with tcpdump -nr and watch the source addresses.
---

# Read a capture like an investigator

A packet capture is a recording of what actually crossed the wire, and it does
not lie. When something looks wrong, a saved capture lets you replay the event
and reconstruct it packet by packet. This lesson hands you a real capture of a
small incident and asks you to work out what happened.

## Open the capture

The file is saved in the box. Read it without touching the network.

```
tcpdump -nr /opt/shabakah/data/pcaps/incident.pcap
```

The `-n` keeps addresses and ports numeric so nothing is hidden behind names,
and `-r` reads from the file instead of a live interface. Scroll through it once
to get a feel for the shape before you go looking for detail.

## Follow the three threads

There are three separate things happening in this capture, and untangling them
is the whole exercise.

First, one host is scanning. Look for a single source address sending a SYN to
many different destination ports in a very short time, with most of them
answered by a reset. That is the fingerprint of a port scan, and the source of
those packets is the scanner.

```
tcpdump -nr /opt/shabakah/data/pcaps/incident.pcap 'tcp[tcpflags] & tcp-syn != 0'
```

Second, a client logs in to a web app over plain HTTP. Filter for port 80 and
read the request body. Because it is cleartext, the credentials are right there
in the packets.

```
tcpdump -nAr /opt/shabakah/data/pcaps/incident.pcap port 80 | less
```

Third, the same client asks the lab resolver to look up a name. Filter for port
53 and you will see the query and the answer.

```
tcpdump -nr /opt/shabakah/data/pcaps/incident.pcap port 53
```

## Why a defender cares

The capture is the ground truth of an incident. Logs can be incomplete or
tampered with, but a capture shows the packets as they were. Learning to read
one, to separate the noise from the story and name the actors by their behaviour,
is one of the most useful skills in an investigation. When you can point at a
source address and say what it did and when, you have turned a pile of packets
into an account of an event.

## Try it

Open the capture and identify the host that ran the port scan against the
server. Submit its IP address.
