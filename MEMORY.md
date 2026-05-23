# Project Memory

Last updated: 2026-05-23

## Purpose

Read this file at the start of future work in this workspace and update it whenever investigation findings, deployed behavior, open issues, or operating notes change.

## Current Work

- Project: `hass-lost-apple`, a Home Assistant App plus HACS-managed custom integration for Apple Find My devices via FindMy.py local anisette.
- Implementation plan: `docs/superpowers/plans/2026-05-23-hass-lost-apple.md`.
- Workspace started empty and was not a git repository on 2026-05-23.

## Repository

- GitHub repo: https://github.com/Snuffy2/hass-lost-apple
- Visibility: public
- Default branch: main
- First implementation plan: `docs/superpowers/plans/2026-05-23-hass-lost-apple.md`
- Development branch: `initial-development` was pushed to GitHub on 2026-05-23.
- Remote `main` includes `af63808 Create dependabot.yml`; this was merged into `initial-development` before final validation.
- `gh run list --limit 5` showed a visible main-branch workflow run for `Dependabot Updates` at https://github.com/Snuffy2/hass-lost-apple/actions/runs/26345846364 with conclusion `failure`.
- The project `CI` workflow was updated to run on branch pushes so `initial-development` can be verified on GitHub before any merge to `main`.
- Initial `initial-development` CI run `26346759985` failed during `pip install -e ".[test]"` because setuptools auto-discovered multiple flat-layout top-level packages (`app`, `custom_components`). Fixed by constraining package discovery to `app/src` in `pyproject.toml`.
- Follow-up `initial-development` CI run `26346786824` passed on GitHub after the package discovery fix.

## Task 10 Documentation Milestone (2026-05-23)

Updated the user-facing docs to match the current implementation boundary:

- `README.md` now describes install, privacy, and supported-device scope without claiming a finished Apple login/2FA flow.
- `app/lost_apple/DOCS.md` now explains setup, the `pairing_token` path through Home Assistant App options, and the current `fetch_location()`-based source model.
- `docs/security.md` records logging and redaction guidance for Apple credentials, session material, and pairing tokens.
- `docs/development.md` records the repo-local venv and check commands.

Verification has not been rerun yet after the doc-only edit set.

## Task 10 Verification Outcome (2026-05-23)

Ran the required checks from the repository root with `./.venv/bin` tooling:

- `./.venv/bin/ruff check .`
  - PASS
- `./.venv/bin/ruff format --check .`
  - FAIL
  - Reported files needing reformatting: `app/src/lost_apple_app/config.py`, `app/src/lost_apple_app/findmy_client.py`, `app/src/lost_apple_app/storage.py`, `app/src/lost_apple_app/web.py`, `tests/app/test_api.py`, `tests/app/test_auth_state.py`, `tests/app/test_config.py`, `tests/app/test_web.py`, `tests/integration/test_config_flow.py`, `tests/integration/test_diagnostics.py`, `tests/integration/test_entities.py`
- `./.venv/bin/mypy app/src custom_components tests`
  - FAIL
  - Duplicate-module error during package discovery:
    - `custom_components/lost_apple/coordinator.py: error: Source file found twice under different module names: "lost_apple.coordinator" and "custom_components.lost_apple.coordinator"`
- `./.venv/bin/pytest`
  - PASS
  - 43 tests passed

The remaining failures are repository-level formatting/type-check path issues outside the doc-only Task 10 scope.

## Task 1 Baseline Check Output (2026-05-23)

Re-ran on branch `initial-development` in `/Users/snuffy2/GitHub/hass-lost-apple` after `prek.toml` review fixes:

Ran on branch `initial-development` in `/Users/snuffy2/GitHub/hass-lost-apple`:

`python3 -m venv .venv && ./.venv/bin/python -m pip install --upgrade pip && ./.venv/bin/python -m pip install -e ".[test]"`

```text
Requirement already satisfied: pip in ./.venv/lib/python3.14/site-packages (26.1.1)
Obtaining file:///Users/snuffy2/GitHub/hass-lost-apple
  Obtaining file:///Users/snuffy2/GitHub/hass-lost-apple
  Installing build dependencies: started
  Installing build dependencies: finished with status 'done'
  Checking if build backend supports build_editable: started
  Checking if build backend supports build_editable: finished with status 'done'
  Getting requirements to build editable: started
  Getting requirements to build editable: finished with status 'done'
  Preparing editable metadata (pyproject.toml): started
  Preparing editable metadata (pyproject.toml): finished with status 'done'
  Successfully installed Jinja2-3.1.6 MarkupSafe-3.0.3 Pillow-12.2.0 PyJWT-2.12.1 PyNaCl-1.6.2 PyRIC-0.1.6.3 PyYAML-6.0.3 SQLAlchemy-2.0.49 acme-5.4.0 aiodns-4.0.4 aiogithubapi-26.0.0 aiohappyeyeballs-2.6.2 aiohttp-3.13.5 aiohttp-asyncmdnsresolver-0.1.1 aiohttp-fast-zlib-0.3.0 aiohttp_cors-0.8.1 aiooui-0.1.9 aioresponses-0.7.8 aiosignal-1.4.0 aiosqlite-0.22.1 aiozoneinfo-0.2.3 anisette-1.2.4 annotated-doc-0.0.4 annotated-types-0.7.0 annotatedyaml-1.0.2 anyio-4.13.0 appdirs-1.4.4 ast-serialize-0.5.0 astral-2.2 async-interrupt-1.2.2 atomicwrites-homeassistant-1.4.1 attrs-26.1.0 audioop-lts-0.2.2 awesomeversion-25.8.0 backoff-2.2.1 bcrypt-5.0.0 beautifulsoup4-4.14.3 bleak-2.1.1 bleak-retry-connector-4.6.1 bluetooth-adapters-2.1.1 bluetooth-auto-recovery-1.5.3 bluetooth-data-tools-1.29.18 boto3-1.43.14 botocore-1.43.14 btsocket-0.3.0 certifi-2026.5.20 cffi-2.0.0 charset_normalizer-3.4.7 ciso8601-2.3.3 click-8.4.1 cronsim-2.7 cryptography-47.0.0 envs-1.4 fastapi-0.136.3 findmy-0.10.0 fnv-hash-fast-2.0.2 fnvhash-0.2.1 frozenlist-1.8.0 fs-2.4.16 grpcio-1.80.0 h11-0.16.0 habluetooth-6.5.0 hass-lost-apple-0.1.0 hass-nabucasa-2.2.0 home-assistant-bluetooth-2.0.0 homeassistant-2026.5.4 httpcore-1.0.9 httptools-0.7.1 httpx-0.28.1 icmplib-3.0.4 idna-3.16 ifaddr-0.2.0 iniconfig-2.3.0 jmespath-1.1.0 josepy-2.2.0 librt-0.11.0 lru-dict-1.4.1 mashumaro-3.21 multidict-6.7.1 mypy-2.1.0 mypy_extensions-1.1.0 orjson-3.11.8 packaging-26.2 pathspec-1.1.1 pluggy-1.6.0 propcache-0.4.1 psutil-7.2.2 psutil-home-assistant-0.0.1 pyOpenSSL-26.1.0 pycares-5.0.1 pycognito-2024.5.1 pycparser-3.0 pydantic-2.13.4 pydantic-core-2.46.4 pyelftools-0.32 pygments-2.20.0 pyobjc-core-12.1 pyobjc-framework-Cocoa-12.1 pyobjc-framework-CoreBluetooth-12.1 pyobjc-framework-libdispatch-12.1 pyrfc3339-2.1.0 pytest-9.0.3 pytest-asyncio-1.3.0 python-dateutil-2.9.0.post0 python-dotenv-1.2.2 python-slugify-8.0.4 pytz-2026.2 regex-2026.5.9 requests-2.33.1 ruff-0.15.14 s3transfer-0.17.0 securetar-2026.4.1 sentence-stream-1.3.0 setuptools-82.0.1 six-1.17.0 snitun-0.45.1 soupsieve-2.8.3 srp-1.0.22 standard-aifc-3.13.0 standard-chunk-3.13.0 standard-telnetlib-3.13.0 starlette-1.1.0 text-unidecode-1.3 typing-extensions-4.15.0 typing-inspection-0.4.2 tzdata-2026.2 uart-devices-0.1.1 ulid-transform-2.2.0 unicorn-2.1.4 urllib3-2.7.0 usb-devices-0.4.5 uv-0.11.8 uvicorn-0.47.0 uvloop-0.22.1 voluptuous-0.15.2 voluptuous-openapi-0.3.0 voluptuous-serialize-2.7.0 watchfiles-1.2.0 webrtc-models-0.3.0 websockets-16.0 yarl-1.23.0 zeroconf-0.148.0
```

`./.venv/bin/ruff check .`

```text
All checks passed!
```

`./.venv/bin/mypy app/src custom_components tests`

```text
custom_components: error: Duplicate module named "__main__" (also at "app/src")
custom_components: note: See https://mypy.readthedocs.io/en/stable/running_mypy.html#mapping-file-paths-to-modules for more info
custom_components: note: Common resolutions include:
custom_components: note:     a) using `--exclude` to avoid checking one of them,
custom_components: note:     b) adding `__init__.py` somewhere,
custom_components: note:     c) using `--explicit-package-bases` or adjusting `MYPYPATH`
Found 1 error in 1 file (errors prevented further checking)
```

`./.venv/bin/pytest`

```text
============================= test session starts ==============================
platform darwin -- Python 3.14.5, pytest-9.0.3, pluggy-1.6.0
rootdir: /Users/snuffy2/GitHub/hass-lost-apple
configfile: pyproject.toml
plugins: asyncio-1.3.0, anyio-4.13.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 0 items

=============================== warnings summary ===============================
.venv/lib/python3.14/site-packages/_pytest/config/__init__.py:1581
  /Users/snuffy2/GitHub/hass-lost-apple/.venv/lib/python3.14/site-packages/_pytest/config/__init__.py:1581: PytestConfigWarning: No files were found in testpaths; consider removing or adjusting your testpaths configuration. Searching recursively from the current directory instead.
    self.args, self.args_source = self._decide_args(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
============================== 1 warning in 0.00s ==============================
```

## Task 1 Baseline Tooling Validation Follow-up

Re-ran after baseline quality fixes:

`./.venv/bin/ruff check .`

```text
All checks passed!
```

`./.venv/bin/mypy app/src custom_components tests`

```text
custom_components: error: Duplicate module named "__main__" (also at "app/src")
custom_components: note: See https://mypy.readthedocs.io/en/stable/running_mypy.html#mapping-file-paths-to-modules for more info
custom_components: note: Common resolutions include:
custom_components: note:     a) using `--exclude` to avoid checking one of them,
custom_components: note:     b) adding `__init__.py` somewhere,
custom_components: note:     c) using `--explicit-package-bases` or adjusting `MYPYPATH`
Found 1 error in 1 file (errors prevented further checking)
```

`./.venv/bin/pytest`

```text
============================= test session starts ==============================
platform darwin -- Python 3.14.5, pytest-9.0.3, pluggy-1.6.0
rootdir: /Users/snuffy2/GitHub/hass-lost-apple
configfile: pyproject.toml
plugins: asyncio-1.3.0, anyio:4.13.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 0 items

=============================== warnings summary ===============================
.venv/lib/python3.14/site-packages/_pytest/config/__init__.py:1581
  /Users/snuffy2/GitHub/hass-lost-apple/.venv/lib/python3.14/site-packages/_pytest/config/__init__.py:1581: PytestConfigWarning: No files were found in testpaths; consider removing or adjusting your testpaths configuration. Searching recursively from the current directory instead.
    self.args, self.args_source = self._decide_args(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
============================== 1 warning in 0.00s ==============================
```

`./.venv/bin/prek run --all-files`

```text
ruff.................................................(no files to check)Skipped
ruff-format..........................................(no files to check)Skipped
mypy.....................................................................Failed
- hook id: mypy
- exit code: 2

  custom_components: error: Duplicate module named "__main__" (also at "app/src")
  custom_components: note: See https://mypy.readthedocs.io/en/stable/running_mypy.html#mapping-file-paths-to-modules for more info
  custom_components: note: Common resolutions include:
  custom_components: note:     a) using `--exclude` to avoid checking one of them,
  custom_components: note:     b) adding `__init__.py` somewhere,
  custom_components: note:     c) using `--explicit-package-bases` or adjusting `MYPYPATH`
  Found 1 error in 1 file (errors prevented further checking)

pytest...................................................................Failed
- hook id: pytest
- exit code: 5

  ============================= test session starts ==============================
  platform darwin -- Python 3.14.5, pytest-9.0.3, pluggy-1.6.0
  rootdir: /Users/snuffy2/GitHub/hass-lost-apple
  configfile: pyproject.toml
  plugins: asyncio-1.3.0, anyio-4.13.0
  asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
  collected 0 items

  =============================== warnings summary ===============================
  .venv/lib/python3.14/site-packages/_pytest/config/__init__.py:1581
    /Users/snuffy2/GitHub/hass-lost-apple/.venv/lib/python3.14/site-packages/_pytest/config/__init__.py:1581: PytestConfigWarning: No files were found in testpaths; consider removing or adjusting your testpaths configuration. Searching recursively from the current directory instead.
      self.args, self.args_source = self._decide_args(

  -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
  ============================== 1 warning in 0.00s ==============================
```

## Task 10 Verification Follow-up (2026-05-23)

Ran the required full verification commands after resolving Task 10 follow-ups:

- `./.venv/bin/ruff check .`
  - PASS
- `./.venv/bin/ruff format --check .`
  - PASS
- `./.venv/bin/mypy app/src custom_components tests`
  - PASS (after adding repository-root `mypy.ini` with `explicit_package_bases = true`, `python_version = 3.14`, and `mypy_path = app/src`)
- `./.venv/bin/pytest`
  - PASS
  - 43 passed

Additional follow-up edits made:
- Added `mypy.ini` to normalize mypy module-path behavior and avoid duplicate-module discovery.
- Adjusted typing annotations in `custom_components/lost_apple/diagnostics.py`, `custom_components/lost_apple/device_tracker.py`, and `tests/integration/test_config_flow.py` to satisfy strict checks under the current dependency typing surface.
- Removed obsolete `[tool.mypy]` section from `pyproject.toml` after moving mypy settings to `mypy.ini`.

## Task 10 Python Runtime Alignment Follow-up (2026-05-23)

Aligned the project runtime/tooling contract to Python 3.14 after review found `mypy.ini` was using Python 3.14 while package metadata, Ruff, CI, and the App Dockerfile still advertised Python 3.13. Keeping mypy at Python 3.13 was not viable with the installed `homeassistant` 2026.5 dependency, because that package includes Python 3.14-only syntax in its installed code.

Updated:
- `pyproject.toml` now requires Python `>=3.14`.
- `pyproject.toml` Ruff target is `py314`.
- `mypy.ini` uses `python_version = 3.14`.
- `.github/workflows/ci.yml` uses Python `3.14`.
- `app/lost_apple/Dockerfile` uses `python:3.14-slim`.
- `docs/development.md` documents the local Python 3.14 environment.

Re-ran the required full verification commands:
- `./.venv/bin/ruff check .`
  - PASS
- `./.venv/bin/ruff format --check .`
  - PASS
  - 33 files already formatted
- `./.venv/bin/mypy app/src custom_components tests`
  - PASS
  - Success: no issues found in 33 source files
- `./.venv/bin/pytest`
  - PASS
  - 43 passed, 13 warnings
