---
id: 10
title: Detection and hardening
objective: Tie the lessons together into a defender mindset and a repeatable routine.
est_min: 10
challenge_type: static
challenge_answer: (least\s*privilege|default[\s-]*deny|deny\s*by\s*default|أقل\s*الامتيازات|المنع\s*الافتراضي|أقل\s*امتياز)
challenge_match: regex
challenge_prompt: What is the security principle of granting only the access that is needed and refusing everything else called? Any common name for it is accepted.
challenge_hint: It has two common names. One talks about the smallest set of rights, the other talks about a firewall style base posture. Either is accepted.
---

# Detection and hardening

You have scanned, captured, enumerated and inspected. This last lesson turns
those skills into a way of working, because security is a routine, not a one time
event.

## A repeatable routine for any host

1. **Inventory.** List what is listening with ss and confirm with a scan.
2. **Justify.** For each open port, ask whether it needs to be reachable, and
   from where.
3. **Reduce.** Turn off what is not needed, then apply a default deny firewall
   for the rest.
4. **Protect.** Put TLS in front of anything sensitive and check the certificate.
5. **Watch.** Capture and log enough that you could recognise a scan or a leak.
6. **Repeat.** Re scan after changes, because drift is the normal state of
   systems.

## The principle underneath it

The idea that ties this together is simple. Grant only what is needed, and
refuse the rest. At the level of accounts and services this is called least
privilege. At the level of the network it shows up as default deny. Both say the
same thing in different words.

## Hardening moves you have already met

- Close ports you do not need, which shrinks the attack surface from lesson 1.
- Mask or trim banners so enumeration from lesson 4 gives less away.
- Replace cleartext with TLS, which answers the exposure from lesson 5.
- Keep certificates valid and matched, following lesson 7.
- Set a default deny firewall, following lesson 8.
- Keep captures and logs so the patterns from lesson 9 can be seen.

## Why this matters

Attackers only need one forgotten thing. Defenders have to be consistent across
all of it, which is why a routine beats heroics. The tools in this lab are the
same ones you will use on real systems, so the habit you build here carries over.

## Try it

Name the principle of granting only what is needed and refusing the rest. Either
common name for it is accepted. Then run `netsec progress` to see how far you
have come.
