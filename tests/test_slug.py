"""Unit tests for slugify-lite."""

from __future__ import annotations

import unittest

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


if __name__ == "__main__":
    unittest.main()
