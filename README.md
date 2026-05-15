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
- [`docs/package-contract.md`](./docs/package-contract.md)
- [`docs/community-sdk.md`](./docs/community-sdk.md)

## Validate a manifest

```sh
python3 tools/validate_manifest.py path/to/manifest.json
```
