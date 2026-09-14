---
id: 04
title: Service enumeration and banners
objective: Talk to a service by hand and pull useful detail out of its responses.
est_min: 10
challenge_type: dynamic
challenge_check: enum_banner
challenge_prompt: Connect to the raw TCP service on port 9000 and read its banner. Which version does it report?
challenge_hint: Use netcat. Run nc 127.0.0.1 9000 and read the first lines it sends, then look for the version token.
---

# Service enumeration and banners

Finding an open port is the start. Enumeration is the work of getting the
service to tell you what it is, what version it runs, and what it lets you do.
Much of this is just a careful conversation.

## The Swiss army knives

- **netcat** (`nc`) opens a raw TCP connection so you can read a banner or type
  a protocol by hand.
- **socat** does the same with more power, including TLS wrapped connections.
- **curl** speaks HTTP properly and shows you headers.

## Banner grabbing

Many services greet you the moment you connect. That greeting, the **banner**,
often leaks the product and version.

```
nc 127.0.0.1 9000
```

Type a command once you are connected. This service understands a few.

```
HELP
VERSION
WHOAMI
QUIT
```

For HTTP, the banner lives in the response headers rather than a greeting.

```
curl -sI http://127.0.0.1:8080
```

## Why a defender cares

Attackers enumerate to plan. If a banner hands out an exact version, it hands
out a shortlist of known weaknesses. Trimming or masking banners will not stop a
determined tester, but it slows the casual one and it is basic hygiene. More
importantly, you should enumerate your own services so you know what they reveal.

## Try it

Connect to port 9000 with netcat and read what it sends before you type
anything. Then ask it for its version and read the reply. The version token
looks like a small letter v followed by a number.
