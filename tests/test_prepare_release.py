"""Tests for the guarded v0.3.0 release-preparation command."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "prepare_release.py"


def _load_module():
    """Load the release-preparation script without requiring ``scripts`` as a package."""
    spec = importlib.util.spec_from_file_location("prepare_release", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_dry_run_accepts_current_v030_source_state() -> None:
    """The guarded migration should match the exact current release state."""
    module = _load_module()
    module.prepare("0.3.0", dry_run=True)


@pytest.mark.parametrize("version", ["0.3", "v0.3.0", "0.3.0.1", "next"])
def test_prepare_rejects_invalid_semver(version: str) -> None:
    """Only an explicit MAJOR.MINOR.PATCH candidate is accepted."""
    module = _load_module()
    with pytest.raises(ValueError, match="MAJOR.MINOR.PATCH"):
        module.prepare(version, dry_run=True)


def test_prepare_rejects_other_valid_versions() -> None:
    """The migration is intentionally one-shot rather than a generic release mutator."""
    module = _load_module()
    with pytest.raises(ValueError, match="scoped to 0.3.0"):
        module.prepare("0.4.0", dry_run=True)
