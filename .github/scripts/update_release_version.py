"""Update Lost Apple Integration version metadata for a release."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import json
from pathlib import Path
import re

VERSION_PATTERN = re.compile(r'^VERSION: Final = "[^"]*"$', re.MULTILINE)


def update_const_version(const_path: Path, version: str) -> None:
    """Update the integration version constant.

    Args:
        const_path: Path to the integration ``const.py`` file.
        version: Release version to write.

    Raises:
        RuntimeError: If the expected typed version constant is not found.
    """
    const_text = const_path.read_text()
    updated_text, replacement_count = VERSION_PATTERN.subn(
        f'VERSION: Final = "{version}"',
        const_text,
        count=1,
    )
    if replacement_count != 1:
        msg = f"Unable to update VERSION in {const_path}"
        raise RuntimeError(msg)
    const_path.write_text(updated_text)


def update_manifest_version(manifest_path: Path, version: str) -> None:
    """Update the Home Assistant manifest version.

    Args:
        manifest_path: Path to the integration ``manifest.json`` file.
        version: Release version to write.
    """
    manifest = json.loads(manifest_path.read_text())
    manifest["version"] = version
    manifest_path.write_text(f"{json.dumps(manifest, indent=2)}\n")


def update_version_files(project_root: Path, version: str) -> None:
    """Update all release version metadata files.

    Args:
        project_root: Repository root containing the integration files.
        version: Release version to write.
    """
    integration_path = project_root / "custom_components" / "lost_apple"
    update_manifest_version(integration_path / "manifest.json", version)
    update_const_version(integration_path / "const.py", version)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        argv: Optional argument sequence. Uses ``sys.argv`` when omitted.

    Returns:
        Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="Release version to write")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root to update",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    """Run the release version updater.

    Args:
        argv: Optional argument sequence. Uses ``sys.argv`` when omitted.
    """
    args = parse_args(argv)
    update_version_files(args.project_root, args.version)


if __name__ == "__main__":
    main()
