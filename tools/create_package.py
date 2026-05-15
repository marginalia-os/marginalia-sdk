#!/usr/bin/env python3
"""Scaffold a Marginalia package folder."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


PACKAGE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{1,95}$")
KINDS = ("theme", "sleep_screen", "reader_module", "integration", "app")

DEFAULT_ENTRYPOINTS = {
    "theme": {"onLoad": "init", "onUnload": "shutdown"},
    "sleep_screen": {"onLoad": "init", "onSleepEnter": "renderFrame", "onSleepTick": "advance", "onUnload": "shutdown"},
    "reader_module": {
        "onLoad": "init",
        "onBookOpen": "bookOpen",
        "onBookClose": "bookClose",
        "onPageTurn": "pageTurn",
        "onUnload": "shutdown",
    },
    "integration": {"onLoad": "init", "onUnload": "shutdown"},
    "app": {"onLoad": "init", "onAppLaunch": "launch", "onAppExit": "exit", "onUnload": "shutdown"},
}

DEFAULT_PERMISSIONS = {
    "theme": ["display", "settings"],
    "sleep_screen": ["display", "sleep_state"],
    "reader_module": ["reader_state", "storage"],
    "integration": ["network", "storage"],
    "app": ["display", "input", "storage"],
}


def package_dir_name(package_id: str) -> str:
    return package_id.split(".")[-1].replace("_", "-")


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def build_manifest(args: argparse.Namespace) -> dict[str, object]:
    execution = "app" if args.kind == "app" else "module"
    manifest: dict[str, object] = {
        "schemaVersion": 1,
        "id": args.package_id,
        "name": args.name,
        "version": args.version,
        "kind": args.kind,
        "execution": execution,
        "summary": args.summary,
        "author": args.author,
        "license": args.license,
    }

    if args.profile == "publish":
        manifest.update(
            {
                "target": {
                    "devices": ["xteink-x3", "xteink-x4"],
                    "chipFamilies": ["esp32-c3"],
                    "minFirmware": args.min_firmware,
                    "apiLevel": 1,
                    "ramClass": "low",
                    "requiresPSRAM": False,
                },
                "permissions": DEFAULT_PERMISSIONS[args.kind],
                "dependencies": [],
                "entrypoints": DEFAULT_ENTRYPOINTS[args.kind],
                "integrity": {"sha256": "replace-me"},
            }
        )

    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a side-loadable Marginalia package folder.")
    parser.add_argument("package_id", help="reverse-DNS package id, for example org.example.hangman")
    parser.add_argument("name", help="display name")
    parser.add_argument("--kind", choices=KINDS, default="app")
    parser.add_argument("--summary", default="A Marginalia package")
    parser.add_argument("--author", default="Unknown")
    parser.add_argument("--license", default="MIT")
    parser.add_argument("--version", default="0.1.0")
    parser.add_argument("--min-firmware", default="0.1.0")
    parser.add_argument("--profile", choices=("local", "publish"), default="publish")
    parser.add_argument("--output", type=Path, default=Path("."))
    parser.add_argument("--force", action="store_true", help="overwrite an existing package directory")
    args = parser.parse_args()

    if not PACKAGE_ID_PATTERN.match(args.package_id):
        print(f"invalid package id: {args.package_id}", file=sys.stderr)
        return 2

    destination = args.output / package_dir_name(args.package_id)
    if destination.exists() and not args.force:
        print(f"package directory already exists: {destination}", file=sys.stderr)
        return 2

    destination.mkdir(parents=True, exist_ok=True)
    (destination / "src").mkdir(exist_ok=True)

    manifest = build_manifest(args)
    write_json(destination / "manifest.json", manifest)
    write_json(
        destination / "src" / "entrypoints.json",
        {name: {"description": f"Placeholder for {name}."} for name in DEFAULT_ENTRYPOINTS[args.kind].values()},
    )
    (destination / "README.md").write_text(
        f"# {args.name}\n\n{args.summary}\n\nThis package was scaffolded with the Marginalia SDK.\n",
        encoding="utf-8",
    )

    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
