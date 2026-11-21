---
title: "feat: add the app icon"
date: 2026-11-21
branch: feat/app-icon
request-source: chat session, 2026-11-21
---

## Request

The installed app and its installer window still showed Electron's default icon. Give the app
its own icon.

## Changes

- **Icon**: the life ring from the logo on a navy tile that follows the macOS icon grid (an
  824 px rounded tile in a 1024 px canvas). The source is `desktop/assets/icon.svg`, and
  `desktop/assets/icon.png` is rendered from it; electron-builder converts the PNG into the
  bundle's `icon.icns`.
- **Rendering script**: `desktop/scripts/render-icon.sh` renders the SVG to a 1024 px PNG with a
  transparent background using headless Chrome, so the PNG can be regenerated after editing the
  SVG without extra tools.
- **Development**: when the app runs from a checkout, the Dock icon is set to the same image
  instead of Electron's.

Only the macOS icon is set, since macOS is the only platform an installer is built for.

## Verification

- The rendered PNG is 1024 x 1024 with transparent corners (checked from the pixel data) and
  was looked at.
- `npm run dist` built the dmg; the app bundle contains `icon.icns` named in `Info.plist`, and
  the image extracted from it matches the design.
- `tsc` and the desktop tests pass.
- Not verified: the Dock icon in development mode, and how the icon reads at the smallest sizes
  (16 and 32 px).
