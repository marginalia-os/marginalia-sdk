#!/usr/bin/env python3
"""Build a Marginalia package archive and checksum."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import sys
import zipfile
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "manifest.v1.schema.json"
SAFE_PART = re.compile(r"^[A-Za-z0-9._-]+$")
MAX_ARCHIVE_ENTRIES = 96
MAX_ARCHIVE_UNCOMPRESSED_BYTES = 512 * 1024
MAX_ARCHIVE_ENTRY_BYTES = 128 * 1024
MAX_ARCHIVE_RELATIVE_PATH_BYTES = 180
ZIP_EPOCH = (1980, 1, 1, 0, 0, 0)


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def safe_relative_path(path: Path) -> bool:
    return all(part and not part.startswith(".") and SAFE_PART.match(part) for part in path.parts)


def package_files(package_dir: Path) -> list[Path]:
    files: list[Path] = []
    total_size = 0
    for path in sorted(package_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(package_dir)
        if not safe_relative_path(rel):
            raise ValueError(f"unsafe package path: {rel}")
        rel_name = rel.as_posix()
        if len(rel_name.encode("utf-8")) > MAX_ARCHIVE_RELATIVE_PATH_BYTES:
            raise ValueError(
                f"package archive path is too long: {rel_name} "
                f"({len(rel_name.encode('utf-8'))} > {MAX_ARCHIVE_RELATIVE_PATH_BYTES})"
            )
        size = path.stat().st_size
        if size > MAX_ARCHIVE_ENTRY_BYTES:
            raise ValueError(f"package file is too large: {rel_name} ({size} > {MAX_ARCHIVE_ENTRY_BYTES})")
        total_size += size
        if total_size > MAX_ARCHIVE_UNCOMPRESSED_BYTES:
            raise ValueError(f"package is too large: {total_size} > {MAX_ARCHIVE_UNCOMPRESSED_BYTES}")
        files.append(path)
        if len(files) > MAX_ARCHIVE_ENTRIES:
            raise ValueError(f"package has too many archive entries: {len(files)} > {MAX_ARCHIVE_ENTRIES}")
    return files


def validate_manifest(package_dir: Path, profile: str) -> dict[str, object]:
    manifest_path = package_dir / "manifest.json"
    if not manifest_path.is_file():
        raise ValueError("manifest.json missing")

    manifest = load_json(manifest_path)
    if not isinstance(manifest, dict):
        raise ValueError("manifest must be a JSON object")

    schema = load_json(SCHEMA_PATH)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(manifest), key=lambda error: list(error.path))
    if errors:
        details = []
        for error in errors:
            location = ".".join(str(part) for part in error.path) or "<root>"
            details.append(f"{location}: {error.message}")
        raise ValueError("manifest invalid: " + "; ".join(details))

    if profile == "publish":
        for field in ("target", "permissions", "entrypoints", "integrity"):
            if field not in manifest:
                raise ValueError(f"manifest missing publish field: {field}")

    return manifest


def archive_name(manifest: dict[str, object]) -> str:
    package_id = str(manifest["id"])
    version = str(manifest["version"])
    return f"{package_id}-{version}.mpkg.zip"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_archive(package_dir: Path, output_dir: Path, profile: str) -> dict[str, object]:
    package_dir = package_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = validate_manifest(package_dir, profile)
    files = package_files(package_dir)
    if not files:
        raise ValueError("package folder contains no files")

    archive_path = output_dir / archive_name(manifest)
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            rel = path.relative_to(package_dir).as_posix()
            info = zipfile.ZipInfo(rel, date_time=ZIP_EPOCH)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IMODE(path.stat().st_mode) & 0o777) << 16
            archive.writestr(info, path.read_bytes())

    return {
        "id": manifest["id"],
        "version": manifest["version"],
        "archive": str(archive_path),
        "format": "mpkg.zip",
        "size": archive_path.stat().st_size,
        "sha256": sha256_file(archive_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a Marginalia package archive.")
    parser.add_argument("package_dir", type=Path, help="package folder containing manifest.json")
    parser.add_argument("--output", type=Path, default=Path("dist"), help="archive output directory")
    parser.add_argument("--profile", choices=("local", "publish"), default="publish")
    parser.add_argument("--json", action="store_true", help="print machine-readable build metadata")
    args = parser.parse_args()

    try:
        metadata = build_archive(args.package_dir, args.output, args.profile)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"build failed: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(metadata, indent=2))
    else:
        print(f"{metadata['archive']}")
        print(f"sha256={metadata['sha256']}")
        print(f"size={metadata['size']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
