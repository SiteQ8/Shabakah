---
id: 05
title: HTTP recon and cleartext exposure
objective: Inspect an HTTP service and see why cleartext protocols are dangerous.
est_min: 10
challenge_type: dynamic
challenge_check: http_cleartext_cred
challenge_prompt: The legacy login page on the web target sends a credential in the clear. What is the password value it exposes?
challenge_hint: Request http://127.0.0.1:8080/login and read the response body, or capture the traffic with tcpdump -A and read it off the wire.
---

# HTTP recon and cleartext exposure

HTTP without TLS sends everything as readable text. That makes it a perfect
teacher. Anything the client and server say to each other can be read by anyone
on the path.

## Reading an HTTP service

```
curl -s http://127.0.0.1:8080/
curl -sI http://127.0.0.1:8080/
curl -s http://127.0.0.1:8080/login
```

- `-s` is silent, without the progress meter.
- `-I` requests only the headers.
- `-v` shows the full exchange, request and response, which is the most useful
  view when you are learning.

```
curl -v http://127.0.0.1:8080/login
```

## The point of the lesson

The lab runs a deliberately careless login page. It transmits a username and a
password as plain text. Fetch it and the secret is simply there in the body. Now
capture the same request on the wire and see that the network path sees it too.

```
sudo tcpdump -i lo -n -A port 8080
```

Then in another shell request the page and watch the capture.

```
curl -s http://127.0.0.1:8080/login >/dev/null
```

## Why a defender cares

This is the single clearest argument for TLS everywhere. Credentials, tokens,
session cookies and personal data all travel in the open on plain HTTP. On a
shared network that is a gift to anyone capturing traffic. When you audit a
system, cleartext transport of anything sensitive is a finding on its own.

## Try it

Find the password that the login page leaks, either from the response body or
from your capture. Then compare with the next lesson, where the same kind of
service is protected by TLS.
