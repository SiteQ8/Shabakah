---
id: 17
title: Scripted scanning with nmap
tag: scripting
objective: Use the Nmap Scripting Engine to pull titles, certificates and banners in one pass, and know which scripts are safe to run.
est_min: 15
challenge_type: dynamic
challenge_check: http_title
challenge_prompt: Run nmap's http-title script against port 8080. What page title does it report?
challenge_hint: Try nmap -sT -p 8080 --script http-title 127.0.0.1 and read the line under the port.
---

# Scripted scanning with nmap

Lesson three taught nmap to answer which ports are open. The Nmap Scripting
Engine, NSE for short, lets the same scan answer what is behind them. Each
script is a small program that runs against an open port and reports what it
finds, from a web page title to the details of a certificate.

## Running a single script

```
nmap -sT -p 8080 --script http-title 127.0.0.1
```

The result appears under the port, prefixed with the name of the script.

## Running the default set

```
nmap -sT -sC -p 8080,8443 127.0.0.1
```

`-sC` runs the scripts in the default category, which are chosen to be fast and
safe. Against port 8080 they also read robots.txt and list the paths it tries
to hide.

## Pulling more detail

```
nmap -sT -p 8443 --script ssl-cert -v 127.0.0.1
nmap -sT -p 2323,9000 --script banner 127.0.0.1
```

The `ssl-cert` script prints the certificate subject, issuer and validity
dates, and with `-v` it shows every field of the subject. The `banner` script
reads the first line each service sends, which is enumeration done for you.

## Know your categories

Scripts are grouped into categories such as default, safe, discovery, version,
intrusive, brute and vuln. The first few only read. Intrusive, brute and vuln
scripts send heavy or risky traffic and can crash a fragile service or lock an
account, so run them only against systems you own or are authorised to test,
and read what a script does before you run it.

```
nmap --script-help http-title
```

## Why a defender cares

Attackers run these exact scripts in the first minutes of an assessment.
Running them against your own services first shows you what a stranger learns
for free: titles that name products, certificates that leak internal names,
banners that announce versions. Fix what they reveal before someone else reads
it.

## Try it

Run the http-title script against port 8080 and submit the title it reports.
While you are there, run ssl-cert with -v against port 8443 and look closely at
the subject.
