---
title: "ci: build and publish the dmg on version tags"
date: 2026-11-21
branch: ci/release-workflow
request-source: chat session, 2026-11-21
---

## Request

After `v0.1.0` was tagged and its installer was built and uploaded by hand, automate that: when
a version tag is pushed, build the dmg and publish it as a GitHub Release. Also correct the
branching document, which said that merging into `main` deploys, while releases are in fact cut
by tagging.

## Changes

- **Release workflow**: `.github/workflows/release.yml` runs when a `v*` tag is pushed. It runs
  the existing checks, then on an Apple Silicon macOS runner checks the tag against the version
  in the three packages, builds the dmg, and publishes a GitHub Release with the dmg attached.
  The release notes are an install section (uv, the `xattr -cr` step for the unsigned build,
  the dmg's SHA-256) followed by GitHub's generated list of changes. Re-running the workflow for
  a tag that already has a release replaces the dmg instead of failing.
- **Checks before a release**: `ci.yml` can now be called from another workflow, and the release
  workflow calls it first. The pull request trigger runs only when a pull request is opened, so
  without this a release could be built from commits that were never tested.
- **Helper scripts**: `.github/scripts/check-version.sh` (tag equals the three versions) and
  `.github/scripts/release-notes.sh` (install section) are separate files so they can be run
  locally.
- **electron-builder publishing is off**: the build passes `--publish never`, because
  electron-builder tries to publish by itself on a tagged CI build; the release is created with
  `gh` instead.
- **Docs**: `branching-strategy.md` now says `main` is always releasable and that a release is a
  tag on `main`, not a merge, and states that there are no `develop`, `release`, or `hotfix`
  branches (git-flow was considered and not adopted: one developer, one supported version).
  `versioning.md` describes what pushing a tag does. The README points to the Releases page for
  the installer.
- `.vite/` (the Vitest cache) is ignored.

Not included: signing and notarization (needs an Apple Developer account), and installers for
Intel Macs, Windows, or Linux.

## Verification

- `check-version.sh v0.1.0` passes and `check-version.sh v0.2.0` fails with one error per
  package, run locally against the current `0.1.0` versions.
- `release-notes.sh` was run locally against the `v0.1.0` dmg and prints the install section
  with the uploaded file name and checksum.
- Both workflow files parse as YAML, and `electron-builder --help` lists `never` as a value of
  `--publish`.
- Not verified: the release workflow itself has never run. It first runs when the next version
  tag is pushed; the calling of `ci.yml` from it and the build on a GitHub runner are untested
  until then.
