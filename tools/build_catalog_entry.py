#!/usr/bin/env python3
"""Build a package archive and registry catalog entry."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from build_package import build_archive, load_json


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def catalog_entry(
    manifest: dict[str, object],
    archive_metadata: dict[str, object],
    artifact_url: str,
    channel: str,
    released_at: str,
) -> dict[str, object]:
    target = manifest.get("target")
    if not isinstance(target, dict):
        raise ValueError("manifest target is required for catalog entries")

    entry: dict[str, object] = {
        "$schema": "../schema/catalog-entry.v1.schema.json",
        "id": manifest["id"],
        "name": manifest["name"],
        "version": manifest["version"],
        "kind": manifest["kind"],
        "execution": manifest["execution"],
        "channel": channel,
        "target": target,
        "integrity": {
            "sha256": archive_metadata["sha256"],
        },
        "artifact": {
            "url": artifact_url,
            "format": archive_metadata["format"],
            "size": archive_metadata["size"],
        },
        "releasedAt": released_at,
        "updatedAt": released_at,
    }

    for key in ("summary", "author", "homepage"):
        value = manifest.get(key)
        if isinstance(value, str) and value:
            entry[key] = value

    return entry


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a Marginalia package archive and catalog entry.")
    parser.add_argument("package_dir", type=Path, help="package folder containing manifest.json")
    parser.add_argument("--archive-output", type=Path, default=Path("dist"), help="archive output directory")
    parser.add_argument("--entry-output", type=Path, required=True, help="catalog entry JSON output path")
    parser.add_argument("--artifact-url", required=True, help="published URL for the built archive")
    parser.add_argument("--channel", choices=("stable", "beta", "experimental"), default="experimental")
    parser.add_argument("--released-at", default=utc_now())
    parser.add_argument("--json", action="store_true", help="print combined machine-readable metadata")
    args = parser.parse_args()

    try:
        archive_metadata = build_archive(args.package_dir, args.archive_output, "publish")
        manifest = load_json(args.package_dir / "manifest.json")
        if not isinstance(manifest, dict):
            raise ValueError("manifest must be a JSON object")
        entry = catalog_entry(manifest, archive_metadata, args.artifact_url, args.channel, args.released_at)
        write_json(args.entry_output, entry)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"catalog entry build failed: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps({"archive": archive_metadata, "entry": str(args.entry_output)}, indent=2))
    else:
        print(f"archive={archive_metadata['archive']}")
        print(f"entry={args.entry_output}")
        print(f"sha256={archive_metadata['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
