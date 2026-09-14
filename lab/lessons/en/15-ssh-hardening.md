---
id: 15
title: Harden the door you came in through
objective: Understand the settings that make an SSH server hard to attack, and see them in place.
est_min: 12
challenge_type: static
challenge_answer: (PermitRootLogin)
challenge_match: regex
challenge_prompt: You want to stop anyone from logging in directly as root over SSH. Which sshd_config directive controls that? Name the directive.
challenge_hint: It is one setting whose name says exactly what it does. Look through the sshd config in the box with sshd -T and find the one about the root account logging in.
---

# Harden the door you came in through

You reached this lab over SSH, which makes SSH worth understanding from the other
side. A default SSH server is reasonable, but a hardened one closes the doors
that attacks lean on most. This lesson walks the settings that matter and shows
you the ones already in force here.

## See the running configuration

sshd can print its full effective configuration, every setting resolved to the
value it is actually using.

```
sudo sshd -T | sort | less
```

You can also read the file that Shabakah ships.

```
cat /etc/ssh/sshd_config.d/shabakah.conf
```

## The settings that matter most

A few directives carry most of the weight.

The root account should never log in directly over the network. If an attack has
to guess a normal username first, and root can only be reached through sudo after
that, you have removed the single most attacked target. The directive is
`PermitRootLogin`, set to `no`.

Passwords are guessable and get reused, so strong deployments prefer keys. Public
key authentication uses a private key the attacker does not have, which defeats
guessing entirely. The directives are `PubkeyAuthentication yes` and, once every
user has a key, `PasswordAuthentication no`.

Limit who may log in at all. `AllowUsers` names the accounts permitted to
connect, so even a correct password for any other account is refused.

Cut idle and forwarded sessions you do not need. `ClientAliveInterval` reaps
sessions that have gone away, and `X11Forwarding no` removes a feature most
servers never use and attackers sometimes do.

## Why a defender cares

SSH is often the most exposed service a host runs, so it is the one most worth
hardening. Most SSH attacks are not clever, they are patient: guess a common
username and password, over and over. Turning off root login, preferring keys,
and naming who may connect turns that patient guessing into wasted effort. The
best part is that none of it is exotic. It is a short list of settings you can
read back with one command.

## Try it

Name the sshd_config directive that stops root from logging in directly over
SSH. Submit the directive name.
