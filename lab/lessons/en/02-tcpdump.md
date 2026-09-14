---
id: 02
title: Reading the wire with tcpdump
objective: Capture live traffic, apply a filter, and read what a request and reply contain.
est_min: 12
challenge_type: dynamic
challenge_check: http_lab_token
challenge_prompt: Capture the HTTP traffic to the web target while you request it, then read the value of the X-Lab-Token response header. What is that value?
challenge_hint: In one shell run sudo tcpdump on the loopback for port 8080 with -A, in another shell run curl against http://127.0.0.1:8080, then read the header from the capture.
---

# Reading the wire with tcpdump

If you can read packets you can answer questions that logs cannot. tcpdump is
the tool that is on almost every machine, so it is worth knowing well.

## The shape of a command

```
sudo tcpdump -i <interface> -n <filter>
```

- `-i lo` captures on the loopback interface, which is where our local targets
  live. Use `-i any` to watch every interface.
- `-n` stops tcpdump from turning addresses and ports into names, which keeps
  the output honest and fast.
- The **filter** at the end is a BPF expression. It decides what you keep.

## Useful flags

- `-A` prints packet payloads as text, which is perfect for cleartext protocols.
- `-x` prints them as hex, `-X` prints hex and text side by side.
- `-c 20` stops after twenty packets.
- `-w capture.pcap` writes raw packets to a file, and `-r capture.pcap` reads
  them back later.

## Filters you will reuse

```
sudo tcpdump -i lo -n port 8080
sudo tcpdump -i lo -n tcp and port 8080
sudo tcpdump -i lo -n host 127.0.0.1 and port 8443
sudo tcpdump -i lo -n -A port 8080
```

## Why a defender cares

Capture is how you confirm what really left the machine, not what you hoped
left it. It is how you find cleartext credentials, odd destinations and beacons.
A saved pcap is evidence you can hand to someone else and replay.

## Try it

Open two shells into the lab. In the first, start a capture with payloads
shown.

```
sudo tcpdump -i lo -n -A port 8080
```

In the second, make a request so there is something to see.

```
curl -s http://127.0.0.1:8080/ >/dev/null
```

Watch the first shell. You will see the request line, then the server reply with
its headers. One of those response headers is named X-Lab-Token. Read its value.

> The same value shows up with `curl -sI http://127.0.0.1:8080`, but the point
> of this lesson is to see it on the wire, not just in the client.
