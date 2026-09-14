---
id: 08
title: Host firewalling
objective: Read and reason about firewall rules and the default deny idea.
est_min: 12
challenge_type: static
challenge_answer: drop|deny|منع|رفض|إسقاط|اسقاط
challenge_match: contains
challenge_prompt: A firewall that blocks everything unless a rule explicitly allows it is using which default policy for its input chain? Answer with the one word action.
challenge_hint: Think about the two ways a packet can be handled when no rule matches. One accepts, the safer one refuses. Name the refusing action.
---

# Host firewalling

A firewall decides which packets are allowed near a host. On Linux the kernel
does the filtering, and you shape it with rules. The tools are nftables, the
modern one, and iptables, the classic one that many guides still use.

## The two mindsets

- **Default allow** lets everything through except what you block. It is easy to
  break and easy to forget a hole.
- **Default deny** blocks everything except what you allow. It is the safer base
  because a service you forgot stays closed rather than open.

The safest posture sets the input policy to drop, then adds narrow rules for the
few things that must be reachable.

## Reading rules with iptables

```
sudo iptables -L -n -v
sudo iptables -L INPUT -n -v --line-numbers
```

- `-L` lists, `-n` keeps addresses numeric, `-v` shows counters.
- Each chain has a **policy**, the action used when no rule matches.

## A default deny sketch

Do not lock yourself out. On this lab keep SSH allowed.

```
sudo iptables -A INPUT -i lo -j ACCEPT
sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -P INPUT DROP
```

The same idea in nftables is cleaner.

```
sudo nft list ruleset
```

## Why a defender cares

Most exposure is a service that did not need to be reachable. A default deny
policy turns that from a live risk into a closed door. Firewall rules are also
readable evidence of intent, so an auditor reads them to see what a host is
meant to accept.

## Try it

List the current rules with iptables and find the policy on the INPUT chain.
Then answer the challenge with the action that a default deny firewall uses when
no rule matches.
