"""Tests for Lost Apple Integration version metadata."""

from __future__ import annotations

import json
from pathlib import Path
import tomllib

from custom_components.lost_apple.const import VERSION


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_version_uses_integration_version_constant() -> None:
    """Verify package metadata reads the version from the integration constant."""
    pyproject = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text())

    assert pyproject["project"]["dynamic"] == ["version"]
    assert "version" not in pyproject["project"]
    assert pyproject["tool"]["setuptools"]["dynamic"]["version"] == {
        "attr": "custom_components.lost_apple.const.VERSION",
    }


def test_manifest_version_matches_integration_version_constant() -> None:
    """Verify the checked-in Home Assistant manifest version matches the constant."""
    manifest = json.loads(
        (PROJECT_ROOT / "custom_components/lost_apple/manifest.json").read_text(),
    )

    assert manifest["version"] == VERSION
