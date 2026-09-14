---
id: 07
title: TLS and certificates
objective: Inspect a TLS service, read its certificate, and judge its trust.
est_min: 12
challenge_type: dynamic
challenge_check: tls_cn
challenge_prompt: Inspect the certificate on the HTTPS target on port 8443. What is the common name (CN) in the certificate subject?
challenge_hint: Use openssl s_client to connect, then read the subject. Try echo | openssl s_client -connect 127.0.0.1:8443 then pipe into openssl x509 -noout -subject.
---

# TLS and certificates

TLS is what turns cleartext HTTP into HTTPS. It gives you encryption in transit,
integrity, and a way to check you are talking to who you think. The certificate
is the heart of that last part.

## What a certificate claims

A certificate binds a public key to an identity. The pieces you inspect most
are the **subject** (who it is for, including the common name and any subject
alternative names), the **issuer** (who vouched for it), and the **validity**
dates. A self signed certificate, like the one in this lab, vouches for itself,
so a client cannot trust it automatically.

## Inspecting with openssl

Connect and see the handshake and the chain.

```
echo | openssl s_client -connect 127.0.0.1:8443
```

Pull out just the subject, issuer and dates.

```
echo | openssl s_client -connect 127.0.0.1:8443 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates
```

See the full certificate in readable form.

```
echo | openssl s_client -connect 127.0.0.1:8443 2>/dev/null \
  | openssl x509 -noout -text
```

Check which protocol versions and ciphers are on offer.

```
openssl s_client -connect 127.0.0.1:8443 -tls1_2 </dev/null 2>/dev/null | head
nmap --script ssl-enum-ciphers -p 8443 127.0.0.1
```

## Why a defender cares

Weak TLS is a common finding. Expired certificates break trust and training.
Old protocol versions and weak ciphers can be attacked. A certificate whose name
does not match the host it serves is either a mistake or a warning. Reading
certificates by hand is how you verify what a scanner reported.

## Try it

Connect to port 8443 and read the certificate subject. Note the common name.
Compare the issuer with the subject and confirm for yourself that this is a self
signed certificate, which is exactly why your browser would complain about it.
