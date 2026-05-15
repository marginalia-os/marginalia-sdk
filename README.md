# Marginalia SDK

Developer SDK for Marginalia packages.

This repo defines the shared contract between package authors, the firmware, and the registry/hub:

- manifest schema
- package kinds and execution classes
- permissions vocabulary
- compatibility rules
- reference package structure

## Current scope

This is the v1 contract for the Xteink X3/X4 firmware line.

## Package model

Marginalia packages are either:

- `module`: loaded into the firmware host for themes, sleep screens, reader hooks, widgets, and integrations
- `app`: a standalone experience with its own navigation lifecycle

Package kinds:

- `theme`
- `sleep_screen`
- `reader_module`
- `integration`
- `app`

## Start here

- [`schema/manifest.v1.schema.json`](./schema/manifest.v1.schema.json)
- [`schema/theme.v1.schema.json`](./schema/theme.v1.schema.json)
- [`docs/package-contract.md`](./docs/package-contract.md)
- [`docs/community-sdk.md`](./docs/community-sdk.md)

## Validate a manifest

```sh
python3 tools/validate_manifest.py path/to/manifest.json
```

The default `local` profile matches what current firmware accepts for SD/Wi-Fi side loading. Use the stricter publish
profile for packages that are ready for a registry or hub:

```sh
python3 tools/validate_manifest.py --profile publish path/to/manifest.json
```

## Create a package

```sh
python3 tools/create_package.py org.example.hangman "Hangman" --kind app --output ./packages
```

The command writes a side-loadable package folder with:

- `manifest.json`
- `README.md`
- `src/entrypoints.json`

Use `--profile local` for the smallest manifest accepted by current firmware. Use the default `publish` profile when the
package is meant to become a registry or hub entry.

## Build an archive

```sh
python3 tools/build_package.py ./packages/hangman --output ./dist --json
```

The builder validates the manifest, rejects paths the firmware side-loader would reject, creates a deterministic package
archive name, and prints the SHA-256 checksum that registry and hub entries should publish.

Firmware-safe archives are capped at 96 files, 512 KiB total uncompressed data, 128 KiB per file, and 180 bytes per
relative archive path.

## Build a registry entry

```sh
python3 tools/build_catalog_entry.py ./packages/hangman \
  --archive-output ./dist \
  --entry-output ./entries/org.example.hangman.json \
  --artifact-url https://example.org/org.example.hangman-0.1.0.mpkg.zip \
  --source-url https://github.com/example/marginalia-packages.git \
  --source-ref v0.1.0 \
  --source-path hangman
```

The command builds the `.mpkg.zip`, computes its checksum and size, and writes a catalog entry shaped for
`marginalia-registry`. The source fields make registry entries reviewable in the same spirit as RT-Thread package
metadata: the artifact is what firmware installs, while the source repository and ref are what humans inspect.
