---
id: 12
title: Chaining findings into access
objective: Follow a trail from one small leak to real access, the way a real assessment runs.
est_min: 15
challenge_type: dynamic
challenge_check: console_hostname
challenge_prompt: Follow the trail to the cleartext console on port 2323, log in, and run HOSTNAME. What hostname does it report?
challenge_hint: The web login leaks a password in the clear, and robots.txt plus the admin notes point at a console on 2323 that reuses it. Log in with that user and password, then run HOSTNAME.
---

# Chaining findings into access

Single findings rarely matter on their own. Real assessments are about the
chain, where a small leak leads to a document, which leads to a credential,
which opens a door. This lesson walks one full chain using only what the earlier
lessons taught you, and it doubles as the guided path through several of the lab
flags.

## The mindset

Every finding is a question about the next step. A cleartext password is not the
prize, it is a key looking for a lock. A hidden path is not the prize, it is a
map to where the keys are kept. You keep pulling the thread.

## Walk the chain

Start at the web service and read what it does not mean to show.

```
curl -s http://127.0.0.1:8080/robots.txt
```

robots.txt names paths that are meant to stay private, which is exactly why it
is worth reading. Follow them.

```
curl -s http://127.0.0.1:8080/admin-notes
curl -s http://127.0.0.1:8080/backup/config.bak
```

The notes mention a console that was never locked down, and the backup leaks
secrets that should never sit in a web root. Now recall lesson five, where the
legacy login sent a password in the clear.

```
curl -s http://127.0.0.1:8080/login
```

That same password is reused on the console on port 2323. Reuse is how one leak
becomes three. Connect and log in.

```
nc 127.0.0.1 2323
```

Once you are in, look around with the commands it offers.

```
HELP
HOSTNAME
USERS
LOGOUT
```

## Why a defender cares

Defenders often dismiss a finding because on its own it seems minor. Attackers
do not think in single findings, they think in chains. A cleartext password, a
forgotten backup, a reused credential, none of them alarming alone, together
become full access. When you triage findings, ask what each one unlocks next.

## Try it

Follow the trail to the console on port 2323, log in with the credential you
found in the clear, and run HOSTNAME. Submit the hostname it prints. Along the
way you will pass several flags, so run `netsec ctf` to see the board.
