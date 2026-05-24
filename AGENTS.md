# AGENTS

## Project Scope

This repository contains two deliverables:

- Lost Apple App: the Home Assistant App package and FastAPI service under `app/`.
- Lost Apple Integration: the Home Assistant custom integration under `custom_components/lost_apple/`.

Use these names consistently in documentation and release notes.

## Repository Files

Keep `AGENTS.md` and `MEMORY.md` in the project root. `MEMORY.md` is local agent memory and must stay untracked by Git.

## Git Behavior

- Use `main` as the primary branch name.
- Create PRs only when explicitly requested.
- Do not push to GitHub without permission.
- Do not commit local memory, cache, venv, coverage, or build artifacts.

## Python Tooling

- Use Python 3.14 for local development, CI, and typing configuration.
- Use the repo-local virtual environment at `./.venv`.
- Run project tools through `./.venv/bin/...` locally.
- Use `prek.toml` for hooks and prefer upstream hooks over local hooks when possible.
- Put tests under `tests/`.

## Code Standards

- Prefer root-cause fixes over surface patches.
- Add or update tests for changed behavior.
- Keep code modular and type annotated.
- Preserve existing comments and keep imports at the top of files.
- For the Lost Apple Integration, prefer Home Assistant entity `_attr_*` fields over property methods when values can be updated from coordinator data.
- Do not write to Home Assistant `.storage` files.

## Validation

For code changes, run the relevant checks from the repo-local virtual environment:

```bash
./.venv/bin/prek run --all-files
./.venv/bin/pytest
```

If a targeted check is used instead of the full suite, explain why.
