---
id: 09
title: Traffic analysis and spotting attacks
objective: Recognise the shape of common activity, including a scan, in captured traffic.
est_min: 12
challenge_type: static
challenge_answer: (scan|فحص|مسح)
challenge_match: regex
challenge_prompt: In a capture you see one host sending SYN packets to many different ports with almost no completed handshakes. What activity does that pattern indicate?
challenge_hint: A completed TCP handshake is SYN then SYN ACK then ACK. Many SYNs to many ports with no completions is the signature of one specific reconnaissance activity.
---

# Traffic analysis and spotting attacks

Capturing traffic is half the skill. The other half is reading it and knowing
what normal and abnormal look like. You already have tcpdump. Now learn to see
patterns rather than single packets.

## The TCP handshake, and what breaks it

A healthy TCP connection begins with three packets.

1. The client sends **SYN**.
2. The server replies **SYN ACK**.
3. The client sends **ACK**, and data flows.

Read the flags in tcpdump output and you can tell a real connection from a probe.

```
sudo tcpdump -i lo -n 'tcp[tcpflags] & tcp-syn != 0'
```

## Shapes worth recognising

- **A port scan** shows one source touching many destination ports quickly, with
  many connections that never complete the handshake.
- **A sweep** shows one source touching the same port across many hosts.
- **Cleartext credentials** show a readable username and password in payload,
  which you saw in the HTTP lesson.
- **Odd destinations** show a host talking to an address or port it has no reason
  to, which can be a beacon.

## Make a pattern to study

Generate a small burst of connections against the lab and watch it.

```
sudo tcpdump -i lo -n -c 40 port 9000 &
for p in 9000 9001 9002 9003 9004; do nc -w1 127.0.0.1 $p </dev/null; done
```

You will see connection attempts land on the open port and get refused on the
closed ones. That contrast, accept here and reset there, is exactly what a
scanner reads to map a host.

## Why a defender cares

Detection lives here. Signatures and anomaly rules are just encoded versions of
these shapes. If you can spot a scan or a cleartext secret by eye in a capture,
you can reason about why a sensor fired, and whether it missed something.

## Try it

Answer what the many SYNs to many ports pattern means. Then, for your own
practice, capture the burst above and pick out the refused connections from the
accepted one.
