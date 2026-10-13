#!/usr/bin/env python3
"""Validate Android native-library readiness for 16 KiB page-size devices.

The Google Play check is not satisfied by looking only at ZIP local-header
offsets in an Android App Bundle. Native libraries must also be built with ELF
PT_LOAD segment alignment that supports 16 KiB pages, and the APKs generated
from the bundle must store native libraries on 16 KiB data boundaries.
"""

from __future__ import annotations

import argparse
import io
import struct
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Iterable, Sequence


PAGE_SIZE_BYTES = 16 * 1024
STORED = zipfile.ZIP_STORED
SUPPORTED_64_BIT_ABIS = {"arm64-v8a", "x86_64"}


@dataclass(frozen=True)
class NativeLibraryReport:
    archive: str
    member: str
    abi: str | None
    compression: str
    header_offset: int
    data_offset: int
    load_alignments: tuple[int, ...]

    @property
    def data_offset_mod_16k(self) -> int:
        return self.data_offset % PAGE_SIZE_BYTES

    @property
    def requires_elf_16kb(self) -> bool:
        return self.abi in SUPPORTED_64_BIT_ABIS


def _compression_name(compress_type: int) -> str:
    if compress_type == zipfile.ZIP_STORED:
        return "stored"
    if compress_type == zipfile.ZIP_DEFLATED:
        return "deflated"
    return f"type-{compress_type}"


def _local_data_offset(zip_file: zipfile.ZipFile, info: zipfile.ZipInfo) -> int:
    handle: BinaryIO = zip_file.fp  # type: ignore[assignment]
    handle.seek(info.header_offset)
    header = handle.read(30)
    if len(header) != 30:
        raise ValueError(f"{info.filename}: truncated ZIP local header")

    signature, _, _, _, _, _, _, _, _, name_len, extra_len = struct.unpack(
        "<IHHHHHIIIHH", header
    )
    if signature != 0x04034B50:
        raise ValueError(f"{info.filename}: invalid ZIP local header signature")

    return info.header_offset + 30 + name_len + extra_len


def _read_pt_load_alignments(data: bytes, member: str) -> tuple[int, ...]:
    if len(data) < 16 or data[:4] != b"\x7fELF":
        raise ValueError(f"{member}: native library is not an ELF file")

    elf_class = data[4]
    endian = "<" if data[5] == 1 else ">"

    if elf_class == 1:
        if len(data) < 52:
            raise ValueError(f"{member}: truncated ELF32 header")
        phoff = struct.unpack_from(endian + "I", data, 28)[0]
        phentsize = struct.unpack_from(endian + "H", data, 42)[0]
        phnum = struct.unpack_from(endian + "H", data, 44)[0]
        align_offset = 28
        type_offset = 0
        align_format = endian + "I"
    elif elf_class == 2:
        if len(data) < 64:
            raise ValueError(f"{member}: truncated ELF64 header")
        phoff = struct.unpack_from(endian + "Q", data, 32)[0]
        phentsize = struct.unpack_from(endian + "H", data, 54)[0]
        phnum = struct.unpack_from(endian + "H", data, 56)[0]
        align_offset = 48
        type_offset = 0
        align_format = endian + "Q"
    else:
        raise ValueError(f"{member}: unsupported ELF class {elf_class}")

    alignments: list[int] = []
    for index in range(phnum):
        offset = phoff + index * phentsize
        if offset + phentsize > len(data):
            raise ValueError(f"{member}: truncated ELF program header {index}")
        program_type = struct.unpack_from(endian + "I", data, offset + type_offset)[0]
        if program_type == 1:
            alignments.append(struct.unpack_from(align_format, data, offset + align_offset)[0])

    if not alignments:
        raise ValueError(f"{member}: no PT_LOAD program headers found")

    return tuple(alignments)


def _detect_abi(member: str) -> str | None:
    parts = member.split("/")
    for index, part in enumerate(parts[:-1]):
        if part in {"lib", "jni"} and index + 1 < len(parts):
            return parts[index + 1]
    return None


def _iter_native_libraries_from_zip(
    zip_file: zipfile.ZipFile, archive_label: str
) -> Iterable[NativeLibraryReport]:
    for info in zip_file.infolist():
        if not info.filename.endswith(".so"):
            continue
        data = zip_file.read(info)
        yield NativeLibraryReport(
            archive=archive_label,
            member=info.filename,
            abi=_detect_abi(info.filename),
            compression=_compression_name(info.compress_type),
            header_offset=info.header_offset,
            data_offset=_local_data_offset(zip_file, info),
            load_alignments=_read_pt_load_alignments(data, info.filename),
        )


def _iter_reports(path: Path) -> Iterable[NativeLibraryReport]:
    lower_name = path.name.lower()
    with zipfile.ZipFile(path) as outer_zip:
        if lower_name.endswith(".apks"):
            for info in outer_zip.infolist():
                if not info.filename.endswith(".apk"):
                    continue
                apk_bytes = outer_zip.read(info)
                with zipfile.ZipFile(io.BytesIO(apk_bytes)) as apk_zip:
                    yield from _iter_native_libraries_from_zip(
                        apk_zip, f"{path}!{info.filename}"
                    )
        else:
            yield from _iter_native_libraries_from_zip(outer_zip, str(path))


def validate_archive(
    path: Path, *, strict_zip: bool = False, check_all_abis_elf: bool = False
) -> list[str]:
    errors: list[str] = []
    reports = list(_iter_reports(path))

    if not reports:
        return [f"{path}: no native libraries (*.so) found to validate"]

    for report in reports:
        print(
            f"{report.archive}: {report.member} "
            f"abi={report.abi or 'unknown'} compression={report.compression} "
            f"header_offset_mod_16k={report.header_offset % PAGE_SIZE_BYTES} "
            f"data_offset_mod_16k={report.data_offset_mod_16k} "
            f"pt_load_alignments={','.join(str(value) for value in report.load_alignments)}"
        )

        should_check_elf = check_all_abis_elf or report.requires_elf_16kb
        if should_check_elf and any(value < PAGE_SIZE_BYTES for value in report.load_alignments):
            errors.append(
                f"{report.archive}: {report.member} has PT_LOAD alignment "
                f"{report.load_alignments}; 64-bit native libraries must be built "
                "with 16 KiB ELF load-segment alignment."
            )

        if strict_zip:
            if report.compression != "stored":
                errors.append(
                    f"{report.archive}: {report.member} is {report.compression}; "
                    "generated APK native libraries must be stored, not compressed."
                )
            if report.data_offset_mod_16k != 0:
                errors.append(
                    f"{report.archive}: {report.member} data offset is not 16 KiB "
                    f"aligned (mod={report.data_offset_mod_16k}). Use bundletool plus "
                    "zipalign -c -P 16 -v 4 to verify Play-bound APK splits."
                )

    return errors


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archives", nargs="+", type=Path, help="AAB, APK, APKS, or AAR paths")
    parser.add_argument(
        "--strict-zip",
        action="store_true",
        help="Require native libraries to be stored and data-aligned to 16 KiB.",
    )
    parser.add_argument(
        "--check-all-abis-elf",
        action="store_true",
        help="Apply the 16 KiB ELF PT_LOAD alignment check to 32-bit ABIs too.",
    )
    args = parser.parse_args(argv)

    all_errors: list[str] = []
    for archive in args.archives:
        if not archive.is_file():
            all_errors.append(f"{archive}: file does not exist")
            continue
        try:
            all_errors.extend(
                validate_archive(
                    archive,
                    strict_zip=args.strict_zip,
                    check_all_abis_elf=args.check_all_abis_elf,
                )
            )
        except (OSError, ValueError, zipfile.BadZipFile) as exc:
            all_errors.append(f"{archive}: {exc}")

    if all_errors:
        print("16 KiB native-library validation failed:", file=sys.stderr)
        for error in all_errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("All checked Android native libraries support 16 KiB page-size requirements.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
