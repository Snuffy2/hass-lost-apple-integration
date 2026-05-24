# Development

Create or refresh the local Python 3.14 virtual environment:

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -e ".[test]"
```

Run the project checks from the repository root with the repo-local venv:

```bash
./.venv/bin/ruff check .
./.venv/bin/ruff format --check .
./.venv/bin/mypy app/src custom_components tests
./.venv/bin/pytest
```

## Release workflow notes

Container images for the Home Assistant App are built from:
- `app/lost_apple/Dockerfile`
- repository root as Docker build context

The publish workflow is `.github/workflows/release-app-images.yml`.

- It runs:
  - on pushes to branch `initial-development` (build validation only, no publish)
  - on pushes of `v*` tags (build and publish)
  - on `workflow_dispatch` (manual build and publish)
- It publishes two GHCR repositories matching App metadata in `app/lost_apple/config.yaml`:
  - `ghcr.io/snuffy2/hass-lost-apple-amd64`
  - `ghcr.io/snuffy2/hass-lost-apple-aarch64`
