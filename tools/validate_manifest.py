#!/usr/bin/env python3
"""Validate Marginalia package manifests."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "manifest.v1.schema.json"
PACKAGE_API_LEVEL = 1
SUPPORTED_DEVICES = {"xteink-x3", "xteink-x4"}
SUPPORTED_CHIP_FAMILIES = {"esp32-c3"}
PUBLISH_REQUIRED_FIELDS = ("target", "permissions", "entrypoints", "integrity")


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def parse_version(value: str) -> tuple[int, int, int] | None:
    parts = value.split(".", 2)
    if len(parts) != 3:
        return None

    parsed: list[int] = []
    for index, part in enumerate(parts):
        if index == 2:
            part = part.split("-", 1)[0].split("+", 1)[0]
        if not part.isdigit():
            return None
        parsed.append(int(part))
    return parsed[0], parsed[1], parsed[2]


def compatible_with_firmware(manifest: dict[str, object], firmware_version: str) -> list[str]:
    target = manifest.get("target")
    if not isinstance(target, dict):
        return []

    errors: list[str] = []
    devices = target.get("devices")
    if isinstance(devices, list) and not any(device in SUPPORTED_DEVICES for device in devices):
        errors.append("target.devices does not include xteink-x3 or xteink-x4")

    chip_families = target.get("chipFamilies")
    if isinstance(chip_families, list) and not any(chip in SUPPORTED_CHIP_FAMILIES for chip in chip_families):
        errors.append("target.chipFamilies does not include esp32-c3")

    api_level = target.get("apiLevel", 1)
    if isinstance(api_level, int) and api_level > PACKAGE_API_LEVEL:
        errors.append(f"target.apiLevel {api_level} is newer than supported API {PACKAGE_API_LEVEL}")

    if target.get("requiresPSRAM") is True:
        errors.append("target.requiresPSRAM must be false for Xteink X3/X4")

    min_firmware = target.get("minFirmware")
    if isinstance(min_firmware, str):
        current = parse_version(firmware_version)
        required = parse_version(min_firmware)
        if current is None:
            errors.append(f"firmware version is not semver-like: {firmware_version}")
        elif required is None:
            errors.append(f"target.minFirmware is not semver-like: {min_firmware}")
        elif current < required:
            errors.append(f"target.minFirmware {min_firmware} is newer than {firmware_version}")

    return errors


def validate_publish_profile(manifest: dict[str, object]) -> list[str]:
    errors = [f"<root>: '{field}' is required for publish profile" for field in PUBLISH_REQUIRED_FIELDS if field not in manifest]

    entrypoints = manifest.get("entrypoints")
    if isinstance(entrypoints, dict) and len(entrypoints) == 0:
        errors.append("entrypoints: publish profile requires at least one entrypoint")

    return errors


def validate_manifest(path: Path, validator: Draft202012Validator, profile: str, firmware_version: str) -> bool:
    try:
        manifest = load_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"{path}: invalid JSON: {exc}", file=sys.stderr)
        return False

    if not isinstance(manifest, dict):
        print(f"{path}: invalid", file=sys.stderr)
        print("  <root>: manifest must be a JSON object", file=sys.stderr)
        return False

    errors = sorted(validator.iter_errors(manifest), key=lambda error: list(error.path))
    profile_errors = compatible_with_firmware(manifest, firmware_version)
    if profile == "publish":
        profile_errors.extend(validate_publish_profile(manifest))

    if not errors and not profile_errors:
        print(f"{path}: ok")
        return True

    print(f"{path}: invalid", file=sys.stderr)
    for error in errors:
        location = ".".join(str(part) for part in error.path) or "<root>"
        print(f"  {location}: {error.message}", file=sys.stderr)
    for error in profile_errors:
        print(f"  {error}", file=sys.stderr)
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Marginalia package manifests.")
    parser.add_argument("--profile", choices=("local", "publish"), default="local", help="validation profile")
    parser.add_argument(
        "--firmware-version",
        default="1.2.0",
        help="firmware version used for target.minFirmware checks",
    )
    parser.add_argument("manifests", nargs="+", type=Path, help="manifest.json files to validate")
    args = parser.parse_args()

    schema = load_json(SCHEMA_PATH)
    validator = Draft202012Validator(schema)

    ok = True
    for manifest_path in args.manifests:
        ok = validate_manifest(manifest_path, validator, args.profile, args.firmware_version) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
