# Marginalia Package Contract v1

## Goals

- Keep package metadata stable across firmware and hub releases.
- Make compatibility checks deterministic.
- Keep package capabilities explicit.

## Local side-load manifest fields

The firmware accepts a small local manifest for SD/Wi-Fi side loading:

- `schemaVersion`
- `id`
- `name`
- `version`
- `kind`
- `execution`

These are enough for the firmware to list, install, enable, disable, uninstall, and later route the package to a runtime
host.

Create a local package skeleton with:

```sh
python3 tools/create_package.py org.example.theme "Example Theme" --kind theme --profile local --output ./packages
```

## Publish-ready manifest fields

Packages submitted to the future hub should also include:

- `target`
- `permissions`
- `entrypoints`
- `integrity`

Create a publish-ready skeleton with:

```sh
python3 tools/create_package.py org.example.hangman "Hangman" --kind app --output ./packages
```

## Compatibility rules

- firmware must reject packages with a higher unsupported `schemaVersion`
- firmware must reject packages targeting unsupported `chipFamilies`
- firmware must reject packages targeting a different device class when no fallback is declared
- firmware must reject packages with a higher unsupported package `apiLevel`
- firmware must reject packages that require unavailable hardware such as PSRAM on Xteink X3/X4
- firmware must reject packages that require a newer firmware version
- runtime hosts must reject packages that request unavailable permissions
- firmware must prefer the newest compatible package version unless the user pins a version

Current firmware compatibility target:

- devices: `xteink-x3`, `xteink-x4`
- chip family: `esp32-c3`
- package API level: `1`
- PSRAM: unavailable

## Permissions vocabulary

Initial permissions:

- `display`
- `input`
- `storage`
- `network`
- `reader_state`
- `sleep_state`
- `settings`

Use the narrowest permission set that fits the package.

## Lifecycle entrypoints

Package entrypoints are declared by string name in the manifest and mapped by the firmware host.

Common entrypoints:

- `onLoad`
- `onUnload`
- `onBookOpen`
- `onBookClose`
- `onPageTurn`
- `onSleepEnter`
- `onSleepTick`
- `onSleepExit`
- `onAppLaunch`
- `onAppExit`

## Notes

The SDK does not decide how a package is executed. It only defines the contract that the firmware host and hub both understand.
