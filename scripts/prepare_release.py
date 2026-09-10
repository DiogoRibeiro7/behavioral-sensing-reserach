"""Prepare a release candidate by updating all version-bearing metadata atomically.

The command deliberately separates *release preparation* from *publication*.
Preparing a candidate updates versions and evidence wording, but it does not
invent a release date or a Zenodo version DOI. Those only exist after the
release is actually published.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import yaml

ROOT: Final[Path] = Path(__file__).resolve().parents[1]
VERSION_RE: Final[re.Pattern[str]] = re.compile(r"^\d+\.\d+\.\d+$")


@dataclass(frozen=True)
class Replacement:
    """One exact text replacement required by release preparation."""

    path: Path
    old: str
    new: str
    expected_count: int = 1


def _read(path: Path) -> str:
    """Read UTF-8 text from ``path``."""
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    """Write UTF-8 text with stable LF newlines."""
    path.write_text(text, encoding="utf-8", newline="\n")


def _replace_exact(replacement: Replacement, *, dry_run: bool) -> None:
    """Apply one guarded replacement, refusing an unexpected source state."""
    text = _read(replacement.path)
    count = text.count(replacement.old)
    if count != replacement.expected_count:
        raise RuntimeError(
            f"{replacement.path}: expected {replacement.expected_count} occurrences "
            f"of {replacement.old!r}, found {count}"
        )
    if not dry_run:
        _write(replacement.path, text.replace(replacement.old, replacement.new))


def _prepare_zenodo(version: str, *, dry_run: bool) -> None:
    """Update Zenodo candidate metadata without claiming publication."""
    path = ROOT / ".zenodo.json"
    data = json.loads(_read(path))
    if data.get("version") != "0.2.0":
        raise RuntimeError(f"{path}: expected current version 0.2.0")

    data["version"] = version
    data.pop("publication_date", None)

    lineage = [
        item
        for item in data.get("related_identifiers", [])
        if item.get("relation") == "isNewVersionOf"
    ]
    if len(lineage) != 1 or lineage[0].get("identifier") != "10.5281/zenodo.17070042":
        raise RuntimeError(f"{path}: unexpected version-lineage metadata")
    lineage[0]["identifier"] = "10.5281/zenodo.22171268"

    data["notes"] = (
        "Research software. Not a medical device. Version 0.3.0 adds real-data "
        "evaluation and the frozen external test of the optional circadian prior. "
        "Across 43 primary external CASAS homes the median paired balanced-accuracy "
        "difference versus the v0.2 baseline was +0.0091 with a 95% household "
        "bootstrap interval [+0.0054, +0.0117], with 37 of 43 homes improved. "
        "The effect is small and does not establish clinical effectiveness or general "
        "smart-home performance. The current abstention mechanism remains a negative "
        "result. The project concept DOI remains 10.5281/zenodo.21337272. No 0.3.0 "
        "version DOI is recorded until Zenodo actually archives the release."
    )

    if not dry_run:
        _write(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def _validate_candidate(version: str) -> None:
    """Verify that all version-bearing metadata agrees after preparation."""
    pyproject = _read(ROOT / "pyproject.toml")
    package = _read(ROOT / "sensor_modeling/__init__.py")
    citation = yaml.safe_load(_read(ROOT / "CITATION.cff"))
    zenodo = json.loads(_read(ROOT / ".zenodo.json"))
    readme = _read(ROOT / "README.md")

    versions = {
        "pyproject": re.search(r'^version = "([^"]+)"', pyproject, re.MULTILINE).group(1),
        "package": re.search(r'__version__ = "([^"]+)"', package).group(1),
        "citation": citation["version"],
        "citation_preferred": citation["preferred-citation"]["version"],
        "zenodo": zenodo["version"],
        "readme": re.search(r"version=\{([^}]+)\}", readme).group(1),
    }
    if set(versions.values()) != {version}:
        raise RuntimeError(f"release versions disagree: {versions}")
    if "date-released" in citation:
        raise RuntimeError("CITATION.cff must not claim a release date before publication")
    if "publication_date" in zenodo:
        raise RuntimeError(".zenodo.json must not claim a publication date before publication")


def prepare(version: str, *, dry_run: bool = False) -> None:
    """Prepare ``version`` across release metadata without publishing it."""
    if VERSION_RE.fullmatch(version) is None:
        raise ValueError(f"version must be MAJOR.MINOR.PATCH, got {version!r}")
    if version != "0.3.0":
        raise ValueError("this guarded migration is intentionally scoped to 0.3.0")

    replacements = (
        Replacement(ROOT / "pyproject.toml", 'version = "0.2.0"', f'version = "{version}"'),
        Replacement(
            ROOT / "pyproject.toml",
            'current_version = "0.2.0"',
            f'current_version = "{version}"',
        ),
        Replacement(
            ROOT / "sensor_modeling/__init__.py",
            '__version__ = "0.2.0"',
            f'__version__ = "{version}"',
        ),
        Replacement(ROOT / "CITATION.cff", 'version: "0.2.0"', f'version: "{version}"', 2),
        Replacement(ROOT / "CITATION.cff", 'date-released: "2026-08-30"\n', ""),
        Replacement(
            ROOT / "README.md",
            "version-0.2.0-informational",
            f"version-{version}-informational",
        ),
        Replacement(ROOT / "README.md", "  version={0.2.0},", f"  version={{{version}}},"),
    )
    for replacement in replacements:
        _replace_exact(replacement, dry_run=dry_run)

    _prepare_zenodo(version, dry_run=dry_run)

    if not dry_run:
        _validate_candidate(version)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="candidate version, currently 0.3.0")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="verify the expected source state without writing files",
    )
    args = parser.parse_args()
    prepare(args.version, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
