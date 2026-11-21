#!/usr/bin/env bash
# Prints the install section of the release notes for a built installer.
# GitHub's generated list of changes is appended after it by `gh release create`.
set -euo pipefail

tag="${1:?usage: release-notes.sh <tag> <dmg>}"
dmg="${2:?usage: release-notes.sh <tag> <dmg>}"
# GitHub replaces spaces in uploaded file names with dots.
asset="$(basename "$dmg" | tr ' ' '.')"
sha256="$(shasum -a 256 "$dmg" | cut -d ' ' -f 1)"

cat <<NOTES
## Install (macOS, Apple Silicon)
1. Download \`$asset\` below, open it, and drag the app to Applications.
2. The build is not signed with an Apple developer certificate, so macOS blocks it at first. Run this once in Terminal, then open the app:
   \`\`\`bash
   xattr -cr "/Applications/SOS My Interview.app"
   \`\`\`
3. The first launch after installing or updating downloads Python and the Python packages, so it needs an internet connection and can take a few minutes. Nothing else has to be installed.

Intel Macs, Windows, and Linux have no installer yet; the app can be run from source there (see the README).

SHA-256 of \`$asset\`: \`$sha256\`

NOTES
