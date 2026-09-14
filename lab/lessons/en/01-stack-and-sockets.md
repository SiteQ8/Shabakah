---
id: 01
title: The network stack and sockets
objective: See how your host talks to the network and how to read what is listening.
est_min: 10
challenge_type: dynamic
challenge_check: listening_tcp_count
challenge_prompt: How many unique TCP ports are in the LISTEN state on this host? Answer with a plain number.
challenge_hint: Use ss with the listening, tcp and numeric flags, then count the distinct local ports.
---

# The network stack and sockets

Every network conversation on this host rides on a small set of ideas. Get
these straight and the rest of the lessons fall into place.

## The layers you will actually touch

- The **link** layer moves frames on the local segment and uses MAC addresses.
- The **network** layer (IP) moves packets between hosts and uses IP addresses.
- The **transport** layer (TCP and UDP) moves data between programs and uses
  **ports**. TCP is connection based and ordered, UDP is fire and forget.
- The **application** layer is the protocol the program speaks, such as HTTP,
  DNS or SSH.

A **socket** is the endpoint a program binds to. It is the pair of an IP
address and a port, plus the protocol. When a service is waiting for clients it
is said to be **listening** on its port.

## Why a defender cares

The first question in any assessment is simple. What is running, and what is
exposed. A host that listens on fewer ports has a smaller attack surface. If you
cannot list what is listening, you cannot defend it.

## Try it

Look at your own interfaces and routing first.

```
ip addr
ip route
```

Now list every socket that is listening for TCP connections.

```
ss -ltnp
```

The columns that matter are the state, the local address and port, and the
process. Compare that with the older tool if you like.

```
netstat -ltnp
```

Add UDP into the picture, since not every service uses TCP.

```
ss -lunp
```

## What you should notice

The lab is listening on a handful of ports on purpose. You came in through SSH
on port 22, and there are a few practice services waiting for you. The next
lessons put each of them to work.

> Tip: run `netsec targets` to see the practice services and their ports.
