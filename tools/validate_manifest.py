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


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_manifest(path: Path, validator: Draft202012Validator) -> bool:
    try:
        manifest = load_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"{path}: invalid JSON: {exc}", file=sys.stderr)
        return False

    errors = sorted(validator.iter_errors(manifest), key=lambda error: list(error.path))
    if not errors:
        print(f"{path}: ok")
        return True

    print(f"{path}: invalid", file=sys.stderr)
    for error in errors:
        location = ".".join(str(part) for part in error.path) or "<root>"
        print(f"  {location}: {error.message}", file=sys.stderr)
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Marginalia package manifests.")
    parser.add_argument("manifests", nargs="+", type=Path, help="manifest.json files to validate")
    args = parser.parse_args()

    schema = load_json(SCHEMA_PATH)
    validator = Draft202012Validator(schema)

    ok = True
    for manifest_path in args.manifests:
        ok = validate_manifest(manifest_path, validator) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
