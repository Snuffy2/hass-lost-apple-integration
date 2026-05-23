# Development

Create or refresh the local virtual environment:

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
