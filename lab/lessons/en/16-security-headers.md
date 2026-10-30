---
id: 16
title: Reading security headers
tag: headers
objective: Read the HTTP response headers that tell a browser how to protect its users, and spot the ones that are missing.
est_min: 12
challenge_type: dynamic
challenge_check: missing_security_headers
challenge_prompt: On the HTTPS target at port 8443, how many of these four headers are missing from the response: Strict-Transport-Security, Content-Security-Policy, X-Content-Type-Options, X-Frame-Options? Answer with a number.
challenge_hint: Run curl -skI https://127.0.0.1:8443/ and compare the headers it prints with the list of four.
---

# Reading security headers

A web server tells a browser more than the page itself. Response headers
carry instructions about how the browser should treat that page, and a handful
of them exist only to protect the people visiting. When they are missing, the
browser falls back to permissive defaults and nobody notices.

## The four headers that matter most

- `Strict-Transport-Security` tells the browser to use HTTPS for this site from now on, which stops anyone quietly downgrading a visitor to plain HTTP.
- `Content-Security-Policy` lists where scripts, styles and images may load from, which turns many cross site scripting bugs into dead ends.
- `X-Content-Type-Options: nosniff` stops the browser guessing a file's type, so an uploaded text file cannot be run as a script.
- `X-Frame-Options` stops other sites from showing yours inside a frame, the trick behind clickjacking.

## Reading them

```
curl -sI http://127.0.0.1:8080/
curl -skI https://127.0.0.1:8443/
```

`-I` asks for the headers only, and `-k` accepts the lab's self signed
certificate. Compare the two answers line by line: the HTTPS service sends one
protective header that the plain web service does not.

## Why a defender cares

Missing headers break nothing, which is exactly why they go unnoticed. They
cost a line of configuration each, they appear in almost every external web
assessment report, and each one closes off a whole class of attack. When you
review a web service, read its headers before you read its code.

## Try it

Fetch the headers from the HTTPS target, count how many of the four are absent,
and submit that number.
