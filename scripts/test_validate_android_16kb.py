#!/usr/bin/env python3
"""Targeted unit tests for Android 16 KiB native-library validation."""

from __future__ import annotations

import io
import struct
import unittest
import zipfile
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from scripts import validate_android_16kb


def _elf64_with_load_alignments(alignments: list[int]) -> bytes:
    phoff = 64
    phentsize = 56
    header = bytearray(phoff + phentsize * len(alignments))
    header[:16] = b"\x7fELF" + bytes([2, 1, 1]) + bytes(9)
    struct.pack_into("<HHIQQQIHHHHHH", header, 16, 3, 183, 1, 0, phoff, 0, 0, 64, phentsize, len(alignments), 0, 0, 0)
    for index, alignment in enumerate(alignments):
        offset = phoff + index * phentsize
        struct.pack_into("<IIQQQQQQ", header, offset, 1, 5, 0, 0, 0, 1, 1, alignment)
    return bytes(header)


def _elf32_with_load_alignments(alignments: list[int]) -> bytes:
    phoff = 52
    phentsize = 32
    header = bytearray(phoff + phentsize * len(alignments))
    header[:16] = b"\x7fELF" + bytes([1, 1, 1]) + bytes(9)
    struct.pack_into("<HHIIIIIHHHHHH", header, 16, 3, 40, 1, 0, phoff, 0, 0, 52, phentsize, len(alignments), 0, 0, 0)
    for index, alignment in enumerate(alignments):
        offset = phoff + index * phentsize
        struct.pack_into("<IIIIIIII", header, offset, 1, 0, 0, 0, 1, 1, 5, alignment)
    return bytes(header)


def _zip_bytes(member: str, payload: bytes, *, compress_type: int, align_data: bool = False) -> bytes:
    buffer = io.BytesIO()
    info = zipfile.ZipInfo(member)
    info.compress_type = compress_type
    if align_data:
        base_offset = 30 + len(member.encode("utf-8"))
        padding = (-base_offset) % validate_android_16kb.PAGE_SIZE_BYTES
        if padding < 4:
            padding += validate_android_16kb.PAGE_SIZE_BYTES
        info.extra = b"\xca\xfe" + struct.pack("<H", padding - 4) + bytes(padding - 4)
    with zipfile.ZipFile(buffer, "w") as zip_file:
        zip_file.writestr(info, payload)
    return buffer.getvalue()


class ValidateAndroid16KbTests(unittest.TestCase):
    def _validate_zip_bytes(self, data: bytes, *, strict_zip: bool = False) -> list[str]:
        with zipfile.ZipFile(io.BytesIO(data)) as zip_file:
            with patch.object(validate_android_16kb, "_iter_reports") as iter_reports:
                iter_reports.return_value = list(
                    validate_android_16kb._iter_native_libraries_from_zip(zip_file, "memory.zip")
                )
                with redirect_stdout(io.StringIO()):
                    return validate_android_16kb.validate_archive(
                        Path("memory.zip"), strict_zip=strict_zip
                    )

    def test_rejects_64_bit_elf_load_alignment_below_16kb(self) -> None:
        archive = _zip_bytes(
            "base/lib/arm64-v8a/libgodot_android.so",
            _elf64_with_load_alignments([4096, 4096]),
            compress_type=zipfile.ZIP_DEFLATED,
        )

        errors = self._validate_zip_bytes(archive)

        self.assertEqual(1, len(errors))
        self.assertIn("PT_LOAD alignment", errors[0])

    def test_allows_32_bit_elf_load_alignment_by_default(self) -> None:
        archive = _zip_bytes(
            "base/lib/armeabi-v7a/libgodot_android.so",
            _elf32_with_load_alignments([4096, 4096]),
            compress_type=zipfile.ZIP_DEFLATED,
        )

        errors = self._validate_zip_bytes(archive)

        self.assertEqual([], errors)

    def test_strict_zip_rejects_compressed_native_library(self) -> None:
        archive = _zip_bytes(
            "lib/arm64-v8a/libgodot_android.so",
            _elf64_with_load_alignments([16384, 16384]),
            compress_type=zipfile.ZIP_DEFLATED,
        )

        errors = self._validate_zip_bytes(archive, strict_zip=True)

        self.assertTrue(any("must be stored" in error for error in errors))

    def test_strict_zip_accepts_stored_16kb_aligned_native_library(self) -> None:
        archive = _zip_bytes(
            "lib/arm64-v8a/libgodot_android.so",
            _elf64_with_load_alignments([16384, 16384]),
            compress_type=zipfile.ZIP_STORED,
            align_data=True,
        )

        errors = self._validate_zip_bytes(archive, strict_zip=True)

        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
