# Marginalia Package Contract v1

## Goals

- Keep package metadata stable across firmware and hub releases.
- Make compatibility checks deterministic.
- Keep package capabilities explicit.

## Required manifest fields

- `schemaVersion`
- `id`
- `name`
- `version`
- `kind`
- `execution`
- `target`
- `permissions`
- `entrypoints`
- `integrity`

## Compatibility rules

- firmware must reject packages with a higher unsupported `schemaVersion`
- firmware must reject packages targeting unsupported `chipFamilies`
- firmware must reject packages targeting a different device class when no fallback is declared
- firmware must reject packages that request unavailable permissions
- firmware must prefer the newest compatible package version unless the user pins a version

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
