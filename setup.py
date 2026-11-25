"""Build script for slugify-lite."""

from __future__ import annotations

from setuptools import setup

setup(
    name="slugify-lite",
    version="0.2.1",
    description="Lightweight stdlib-only ASCII URL slug utility",
    packages=["slugify_lite"],
    python_requires=">=3.10",
)
