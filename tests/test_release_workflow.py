"""Tests for the Lost Apple Integration release workflow."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_release_workflow_guards_version_tag_normalization() -> None:
    """Verify the release workflow does not blindly strip leading v characters."""
    release_workflow = (PROJECT_ROOT / ".github/workflows/release.yml").read_text()

    assert "${RELEASE_TAG#v}" not in release_workflow
    assert r"^v?([0-9]+)\.([0-9]+)\.([0-9]+)" in release_workflow
    assert '[[ "${release_version}" =~ ^v[0-9] ]]' in release_workflow
