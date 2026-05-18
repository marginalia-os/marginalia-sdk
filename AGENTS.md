# AGENTS.md

Guidance for agents working in `marginalia-sdk`.

## Project Role

This repo defines the package authoring contract for Marginalia:

- manifest schemas
- package kinds and execution classes
- permissions vocabulary
- compatibility rules
- package creation, validation, archive, and catalog-entry tooling

Firmware, registry, hub, and examples should follow this contract rather than each defining their own schema.

## Common Commands

Validate a manifest:

```sh
python3 tools/validate_manifest.py path/to/manifest.json
python3 tools/validate_manifest.py --profile publish path/to/manifest.json
```

Create a package:

```sh
python3 tools/create_package.py org.example.hangman "Hangman" --kind app --output ./packages
```

Build an archive:

```sh
python3 tools/build_package.py ./packages/hangman --output ./dist --json
```

Build a registry entry:

```sh
python3 tools/build_catalog_entry.py ./packages/hangman \
  --archive-output ./dist \
  --entry-output ./entries/org.example.hangman.json \
  --artifact-url https://example.org/org.example.hangman-0.1.0.mpkg.zip \
  --source-url https://github.com/example/marginalia-packages.git \
  --source-ref v0.1.0 \
  --source-path hangman
```

## Contract Guidelines

- Keep schema changes backward compatible unless deliberately bumping schema version.
- Current firmware target is Xteink X3/X4, ESP32-C3, package API level 1, no PSRAM.
- Use the narrowest permission vocabulary that works.
- Package ids must remain firmware-safe and path-safe.
- Package settings live outside archives in `/.marginalia/package-state/<package-id>.json`.
- SDK tooling should reject files and paths that firmware side-loading would reject.
- Archive output must stay deterministic enough for stable checksums.

When changing package schema, update examples, registry validation expectations, hub catalog assumptions, and firmware
compatibility checks as needed.

