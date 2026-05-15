# CrossPoint Community SDK Relationship

[`crosspoint-reader/community-sdk`](https://github.com/crosspoint-reader/community-sdk) is an Xteink X4 hardware and
PlatformIO component SDK. It currently focuses on reusable display, input, SD-card, and battery libraries that firmware
projects can include as submodules.

Marginalia SDK is a different layer:

- `community-sdk` helps firmware talk to the board.
- `marginalia-sdk` defines the package manifest, compatibility model, permissions, and package author contract.
- `marginalia-firmware` may continue to depend on low-level board libraries from the X4 community SDK when that reduces
  hardware maintenance.
- Marginalia packages should not depend directly on the X4 community SDK contract unless a future native app ABI
  explicitly exposes a board-support layer.

The practical decision is to keep Marginalia SDK independent and reference the community SDK as a low-level hardware
source, not as the package ecosystem base.
