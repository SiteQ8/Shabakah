# Security policy

## What Shabakah is

Shabakah is a deliberately vulnerable teaching lab. Several of its services
model bad habits on purpose: a cleartext credential, a chatty banner, an
undocumented command, a reused password. These are the findings the lessons
teach you to spot. They are not bugs, and they only exist inside the container.

Every service binds locally inside the container and nothing reaches the outside
world. Run Shabakah only on a host you control, and only ever point the tools at
the lab targets or systems you own.

## Reporting a real issue

If you find a genuine security problem, for example something that lets the
container affect the host, an unintended way out of the lab, or a supply chain
issue in how the image is built, please report it privately.

Open a GitHub security advisory on the repository, or open a normal issue that
says only that you have found a security problem and asks for a private channel,
without the details. Do not post a working exploit in a public issue.

Please include the version or image digest, the host and Docker version, and the
steps to reproduce. You can expect an acknowledgement and, where a fix is
warranted, a patched image and a note in the changelog.

## Using it safely

- Change the default learner password with `LEARNER_PASSWORD` before using
  Shabakah anywhere shared.
- Do not expose the container's SSH port to an untrusted network.
- Treat the flags and credentials inside as teaching material, not secrets.
