# Changelog

All notable changes to Shabakah are recorded here.

## 1.2.1

Fixed

- The guide and the container image now report the correct version.
- The website hero terminal now shows the current lesson count and score, and
  the guide screenshot was regenerated to match.

## 1.2.0

Added

- Three new lessons, bringing the total to fifteen: read a capture like an
  investigator (13), find the attack in the logs (14), and harden the door you
  came in through (15).
- A sample packet capture and a sample authentication log shipped in the image
  under /opt/shabakah/data, so the forensics and log lessons have real material
  to work on. The capture is generated deterministically with correct checksums.
- A SHABAKAH_DATA path and a Dockerfile copy for the sample data.

Changed

- The website and README now list fifteen lessons, in English and Arabic.
- The smoke test checks lesson parity at fifteen, runs the three new lesson
  checks, and confirms the sample data files are present and well formed.

## 1.1.1

Added

- A sixth capture the flag flag, hidden in the TLS certificate metadata on the
  HTTPS target. The certificate subject carries a field it never should, found
  with the same openssl skill lesson seven teaches. The board is now six flags
  worth a hundred and ten points.

Fixed

- The guide no longer prints a traceback when its output is piped into a reader
  that closes early, such as head or grep.

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
