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
./.venv/bin/mypy custom_components tests
./.venv/bin/pytest
```

## Release workflow notes

GitHub releases for this repository publish the HACS zip for the Lost Apple Integration.

The publish workflow is `.github/workflows/release.yml`.

- It runs:
  - on published or edited GitHub releases
  - on `workflow_dispatch` with an integration version input
- It updates `custom_components/lost_apple/const.py` and `custom_components/lost_apple/manifest.json` with the release version, then commits those metadata updates back to the release target branch for GitHub release events.
- It packages `custom_components/lost_apple` as `lost_apple.zip`.
- It uploads the zip to the GitHub release, or as a workflow artifact for manual runs.
