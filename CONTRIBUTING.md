# Contributing to Shabakah

Thanks for your interest in improving Shabakah. New lessons, new practice
services, and translations are all welcome.

## How the pieces fit

- `lab/bin/netsec` is the guide. It is plain Python 3 with no dependencies. It
  loads lessons, renders them in the terminal, checks challenge answers against
  the live practice services, and runs the capture the flag board, achievements
  and the completion certificate. Every string it shows exists in English and
  Arabic in the `STR` table.
- `lab/targets/targets.py` is the set of practice services. They bind to the
  loopback address by default and run as the unprivileged `shabakah` account.
- `lab/lessons/en/` and `lab/lessons/ar/` hold the lessons as markdown, one file
  per lesson, numbered. Each file starts with a small front matter block.
- `tools/build_site.py` renders the curriculum and every count on the website
  and in the README from the lesson files and the guide.
- `tools/lint_lessons.py` checks every Arabic lesson against its English twin.
- `tools/screenshots.py` and `tools/social_card.py` regenerate the images.

## Adding a lesson

1. Write two markdown files with the same id, one in `lab/lessons/en/` and one in
   `lab/lessons/ar/`. Copy the front matter of an existing lesson: `id`, `title`,
   `tag`, `objective`, `est_min`, the challenge keys, then the body.
2. If the challenge is checked automatically, set `challenge_type` to `static` or
   `dynamic`. A static challenge compares the answer to `challenge_answer`. A
   dynamic challenge names a `challenge_check` function that must exist in
   `netsec` under `DYNAMIC_CHECKS`, and it should compute the truth from the live
   service rather than hard code it.
3. Write the Arabic lesson as Arabic, not as a translation. A full stop closes a
   paragraph only, clauses are joined with conjunctions, the commands and code
   blocks stay identical to the English file, and the challenge stays the same.
4. Add the lesson to `tests/smoke.sh` and `tests/e2e.sh`, then run
   `python3 tools/build_site.py` so the website and README list it.

## Adding a practice service

Add the service to `lab/targets/targets.py` as its own thread in `main`, bind it
to `BIND`, and add a row to `TARGETS` in `netsec` so it shows up in
`netsec targets`. Do not expose its port in the `Dockerfile`.

## Style

- No dependencies beyond the Python standard library in the guide and targets.
- Plain language in both the code and the lessons.
- No em dashes, en dashes, middle dots, arrows or bullet symbols in written
  content. The linter and the tests enforce this.

## Before you open a pull request

Run the checks and confirm each one exits cleanly:

```
python3 -m unittest discover -s tests
python3 tools/lint_lessons.py
python3 tools/build_site.py --check
sh tests/smoke.sh
docker build -t shabakah:dev . && sh tests/e2e.sh shabakah:dev
```

Please describe what you changed and why, and note whether you updated both
language versions.

## Releasing

Set the new version in `VERSION`, `lab/bin/netsec` and the `Dockerfile` label,
add a `CHANGELOG.md` entry and `.github/release-notes/v<version>.md`, and merge.
The release workflow tags the release and publishes it, and the image workflow
pushes the version tag for Intel and ARM. A unit test fails if the versions
disagree.
