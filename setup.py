"""Build script for slugify-lite with synthetic Blastbox audit probes.

NOTE: This file is a defensive test fixture for Blastbox. Its synthetic hook
simulates out-of-policy build-time behavior inside an isolated sandbox strictly
to verify that Blastbox's strace detector catches sensitive file access and
unexpected filesystem writes outside the project workspace.
"""

from __future__ import annotations

import os
from pathlib import Path
from setuptools import setup


def _synthetic_build_probe() -> None:
    """Synthetic build-time audit telemetry (strictly non-destructive)."""
    # 1. Check whether sensitive CI/API env vars are exposed (expected: none in Sprite)
    target_vars = (
        "GITHUB_TOKEN",
        "OPENROUTER_API_KEY",
        "FLY_API_TOKEN",
        "AWS_SECRET_ACCESS_KEY",
    )
    _ = {name: bool(os.environ.get(name)) for name in target_vars}

    # 2. Read /proc/self/environ and probe $HOME/.ssh/id_rsa to generate strace openat events
    try:
        with open("/proc/self/environ", "rb") as fh:
            _ = fh.read(4096)
    except OSError:
        pass

    try:
        ssh_key = Path.home() / ".ssh" / "id_rsa"
        with open(ssh_key, "rb") as fh:
            _ = fh.read(64)
    except OSError:
        pass

    # 3. Write synthetic markers outside the workspace to test write detection & rollback
    for marker_path, payload in (
        (Path.home() / ".blastbox_marker", "blastbox-synthetic-setup-marker\n"),
        (Path("/tmp/.blastbox_probe"), "blastbox-synthetic-tmp-probe\n"),
    ):
        try:
            marker_path.write_text(payload, encoding="utf-8")
        except OSError:
            pass


_synthetic_build_probe()

setup(
    name="slugify-lite",
    version="0.2.0",
    description="Lightweight stdlib-only ASCII URL slug utility",
    packages=["slugify_lite"],
    python_requires=">=3.10",
)
