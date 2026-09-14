# Changelog

All notable changes to Shabakah are recorded here.

## 1.1.0

Added

- Capture the flag: five flags hidden across the targets, worth ninety points,
  with a board, per flag hints, and live submission through `netsec submit`.
- Achievements: seven badges that unlock as you clear lessons and capture flags.
- Two new lessons, bringing the total to twelve: UDP services and why they hide
  (11), and chaining findings into access (12).
- Two new practice targets: a cleartext admin console on tcp 2323 that reuses a
  password, and a UDP banner service on udp 9001.
- New commands: `netsec ctf`, `netsec ctf hint <id>`, `netsec submit`, and
  `netsec achievements`.
- Real terminal screenshots in the repository and on the website.
- A much richer bilingual website, now served at shabakah.3li.info.

Changed

- The web target now exposes hidden paths behind robots.txt, an admin notes
  page, and a config backup, so recon and enumeration have real findings.
- The enumeration service now answers an undocumented `DEBUG` command and
  processes piped input line by line.
- The guide banner now shows your lesson count and score when you have progress.
- The Dockerfile exposes the new target ports.
- The smoke test now checks lesson parity at twelve, verifies every dynamic
  check resolves, runs the full capture the flag flow, and confirms flags are
  reachable on the wire.

## 1.0.0

- First release. A single Docker container you SSH into, with a bilingual guide,
  ten hands on lessons, four practice targets, live challenge checking, saved
  progress, and a published image on the GitHub Container Registry.
