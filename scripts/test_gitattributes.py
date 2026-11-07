#!/usr/bin/env python3
"""Unit tests validating .gitattributes and starter asset tracking."""

from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
GITATTRIBUTES_PATH = REPO_ROOT / ".gitattributes"
FONTS_DIR = REPO_ROOT / "game" / "assets" / "fonts"
ICONS_DIR = REPO_ROOT / "game" / "assets" / "icons"


class GitAttributesStarterAssetsTests(unittest.TestCase):
    def test_gitattributes_contains_starter_asset_exemptions(self) -> None:
        self.assertTrue(GITATTRIBUTES_PATH.is_file(), ".gitattributes must exist")
        content = GITATTRIBUTES_PATH.read_text(encoding="utf-8")
        self.assertIn(
            "game/assets/fonts/* -filter -diff -merge -text",
            content,
            ".gitattributes must exempt game/assets/fonts/* from LFS filters",
        )
        self.assertIn(
            "game/assets/icons/* -filter -diff -merge -text",
            content,
            ".gitattributes must exempt game/assets/icons/* from LFS filters",
        )

    def test_starter_fonts_are_valid_binaries_not_lfs_pointers(self) -> None:
        font_files = list(FONTS_DIR.glob("*.ttf"))
        self.assertGreaterEqual(len(font_files), 2, "Expected at least 2 starter fonts")
        for font in font_files:
            raw = font.read_bytes()
            self.assertFalse(
                raw.startswith(b"version https://git-lfs.github.com/spec/v1"),
                f"{font.name} must be a real binary font, not an LFS pointer",
            )
            self.assertGreater(
                len(raw),
                1000,
                f"{font.name} size ({len(raw)} bytes) is too small to be a binary font",
            )

    def test_starter_icons_are_valid_binaries_not_lfs_pointers(self) -> None:
        icon_files = list(ICONS_DIR.glob("*.png"))
        self.assertGreaterEqual(len(icon_files), 5, "Expected starter icon PNGs")
        for icon in icon_files:
            raw = icon.read_bytes()
            self.assertFalse(
                raw.startswith(b"version https://git-lfs.github.com/spec/v1"),
                f"{icon.name} must be a real binary PNG, not an LFS pointer",
            )
            self.assertTrue(
                raw.startswith(b"\x89PNG\r\n\x1a\n"),
                f"{icon.name} must have a valid PNG magic header",
            )


if __name__ == "__main__":
    unittest.main()
