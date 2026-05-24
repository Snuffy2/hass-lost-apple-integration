"""Tests for the Lost Apple Integration release workflow."""

from __future__ import annotations

from collections.abc import Callable
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import cast

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_update_version_files() -> Callable[[Path, str], None]:
    """Load the release version updater from the GitHub scripts folder."""
    script_path = PROJECT_ROOT / ".github" / "scripts" / "update_release_version.py"
    spec = importlib.util.spec_from_file_location("update_release_version", script_path)
    if spec is None or spec.loader is None:
        msg = f"Unable to load release updater script from {script_path}"
        raise RuntimeError(msg)
    module = importlib.util.module_from_spec(spec)
    cast("ModuleType", module)
    spec.loader.exec_module(module)
    update_version_files = module.update_version_files
    if not callable(update_version_files):
        msg = "Release updater script does not expose update_version_files"
        raise TypeError(msg)
    return cast("Callable[[Path, str], None]", update_version_files)


UPDATE_VERSION_FILES = load_update_version_files()


def test_release_workflow_updates_version_metadata_without_sed() -> None:
    """Verify the release workflow delegates version updates to the updater script."""
    release_workflow = (PROJECT_ROOT / ".github/workflows/release.yml").read_text()

    assert "sed -i" not in release_workflow
    assert ".github/scripts/update_release_version.py" in release_workflow
    assert "RELEASE_VERSION" in release_workflow


def test_release_workflow_persists_version_metadata_updates() -> None:
    """Verify release events commit version metadata updates back to the branch."""
    release_workflow = (PROJECT_ROOT / ".github/workflows/release.yml").read_text()

    assert "Commit & Push Version Changes" in release_workflow
    assert "types: [published]" in release_workflow
    assert "github.event.release.target_commitish" in release_workflow


def test_update_release_version_updates_manifest_and_typed_constant(
    tmp_path: Path,
) -> None:
    """Verify release metadata updates preserve JSON and the typed version constant."""
    integration_path = tmp_path / "custom_components" / "lost_apple"
    integration_path.mkdir(parents=True)
    const_path = integration_path / "const.py"
    manifest_path = integration_path / "manifest.json"
    const_path.write_text(
        '"""Constants."""\n\n'
        "from typing import Final\n\n"
        'DOMAIN: Final = "lost_apple"\n'
        'VERSION: Final = "0.1.2"\n',
    )
    manifest_path.write_text(
        json.dumps(
            {
                "domain": "lost_apple",
                "name": "Lost Apple",
                "version": "0.1.2",
            },
            indent=2,
        )
        + "\n",
    )

    UPDATE_VERSION_FILES(tmp_path, "1.2.3")

    assert 'VERSION: Final = "1.2.3"' in const_path.read_text()
    assert json.loads(manifest_path.read_text())["version"] == "1.2.3"
