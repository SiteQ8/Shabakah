# Contributing to Shabakah

Thanks for your interest in improving Shabakah. New lessons, new practice
targets, and translations are all welcome.

## How the pieces fit

- `lab/bin/netsec` is the guide. It is plain Python 3 with no dependencies. It
  loads lessons, renders them in the terminal, checks challenge answers against
  the live targets, and runs the capture the flag board and achievements.
- `lab/targets/targets.py` is the set of practice services. Each service binds
  locally inside the container and models something a lesson can find.
- `lab/lessons/en/` and `lab/lessons/ar/` hold the lessons as markdown, one file
  per lesson, numbered. Each file starts with a small front matter block.
- `tests/smoke.sh` runs the whole thing without Docker: it starts the targets,
  checks every lesson challenge, and runs the full capture the flag flow.

## Adding a lesson

1. Write two markdown files with the same id, one in `lab/lessons/en/` and one in
   `lab/lessons/ar/`. Follow the numbering and the front matter of an existing
   lesson.
2. If the lesson has an automatically checked challenge, set `challenge_type` to
   `static` or `dynamic`. A static challenge compares the answer to
   `challenge_answer`. A dynamic challenge names a `challenge_check` function
   that must exist in `netsec` under `DYNAMIC_CHECKS`.
3. Keep both language versions in step. The Arabic version follows Arabic
   sentence rules: verb first phrasing, a period only at the end of a sentence,
   and clauses joined with connectors.
4. Run `sh tests/smoke.sh` and make sure it passes.

## Adding a target

Add the service to `lab/targets/targets.py` as its own thread in `main`, expose
its port in the `Dockerfile`, and add a row to the target list in `netsec` so it
shows up in `netsec targets`.

## Style

- No dependencies beyond the Python standard library in the guide and targets.
- Plain language in both the code and the lessons.
- Do not use em dashes or en dashes in written content.

## Before you open a pull request

Run the test suite and confirm it exits cleanly:

```
sh tests/smoke.sh
```

Please describe what you changed and why, and note whether you updated both
language versions.
