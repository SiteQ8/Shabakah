---
id: 14
title: Find the attack in the logs
objective: Read an authentication log and pick out a brute force attempt and its source.
est_min: 12
challenge_type: static
challenge_answer: (203\.0\.113\.77)
challenge_match: regex
challenge_prompt: Read the log at /opt/shabakah/data/logs/auth.log and find the address responsible for the brute force against SSH. Which IP has by far the most failed logins?
challenge_hint: Count the failed password lines per source address. One host tries many usernames and fails again and again, then eventually gets in. Group by the address after the word from.
---

# Find the attack in the logs

When a capture is not available, logs are the next best record. An
authentication log writes down every login attempt, and a brute force attack
leaves an obvious trail in it once you know how to read it. This lesson gives you
a real log with a real attack buried in ordinary activity.

## Read the log

The file is saved in the box.

```
less /opt/shabakah/data/logs/auth.log
```

Read it top to bottom once. You will see normal activity, a key based login, a
sudo command, and then a run of failures.

## Count the failures by source

A single failed login means nothing. A hundred from one address means someone is
guessing. The skill is to aggregate, not to read line by line. Pull the failed
attempts, keep the source address, and count.

```
grep "Failed password" /opt/shabakah/data/logs/auth.log
grep "Failed password" /opt/shabakah/data/logs/auth.log | awk '{for(i=1;i<=NF;i++) if($i=="from") print $(i+1)}' | sort | uniq -c | sort -rn
```

One address will stand far above the rest. That is your brute forcer.

## Read the whole story, not just the count

Now look at what that address did after all those failures.

```
grep "203.0.113.77" /opt/shabakah/data/logs/auth.log
```

The failures end in an accepted password and a session, and then a command that
pulls a script from another host. That is a brute force that succeeded and became
a foothold. Counting told you who, but reading the sequence told you what it
cost.

## Why a defender cares

This is how real detection begins: not with an alert that says attack, but with a
pattern in a log that a person or a rule notices. Repeated failures from one
source, especially followed by a success, are one of the clearest signals there
is. Rate limits, account lockouts, key only authentication, and blocking after
repeated failures all exist to break exactly this pattern.

## Try it

Read the log and find the address behind the brute force. Submit the IP with the
most failed logins.
