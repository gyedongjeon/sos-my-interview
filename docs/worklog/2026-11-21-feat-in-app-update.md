---
title: "feat: update the app from inside the app"
date: 2026-11-21
branch: feat/in-app-update
request-source: chat session, 2026-11-21
---

## Request

Let users update without downloading and installing each new version by hand, at no cost. The
standard Electron updater needs an app signed with an Apple Developer ID (a paid yearly
membership), which was decided against for now, so the app updates itself in its own way.

## Changes

- **Check**: at startup the packaged app asks GitHub for the latest release, and the app menu
  has "Check for Updates…". A newer release is offered in a dialog with "Update and Restart",
  "See What's New", and "Later"; nothing is installed without that click.
- **Install**: the app downloads the release's `.zip` into its data folder, checks it, unpacks
  it, and starts a small shell script that waits for the app to quit, moves the old bundle
  aside, moves the new one in, and opens it. If the new bundle cannot be moved in, the old one
  is put back. Files the app downloads itself are not quarantined, so the `xattr -cr` step is
  needed only for the first install.
- **What an update must pass**: the release must be a plain newer `x.y.z` version that is not a
  draft or pre-release; the file must come from this repository's release downloads and match
  the SHA-256 GitHub reports for it; and the unpacked bundle must have this app's identifier,
  the expected version, and an intact code signature. This protects against a damaged or
  swapped download, but not against a compromised GitHub account, which an Apple signature
  would not fully cover either; that is why installing always needs a click.
- **When the app cannot replace itself** (run from a checkout, not moved to Applications and so
  running from a read-only place, no permission, or a release without a usable archive), the
  dialog offers the download page instead.
- **Release**: the build now also makes the `.zip`, and the release workflow uploads it next to
  the dmg. The release notes and both READMEs describe updating.
- **Code**: the logic is in `desktop/src/update.ts`, free of Electron so that it is tested with
  Vitest (18 new tests, including the real swap script run on stand-in folders); `main.ts`
  holds the dialog, progress, and menu.

Known limits: only releases from this one onward can update themselves, so users of 0.2.x
install the next version by hand once. Because the app is ad-hoc signed, macOS may ask for
camera and microphone access again after an update. The check tells GitHub the app's version
and the user's IP address, like any download.

## Verification

- The tests were written before the code and failed first; all 24 desktop tests pass, and `tsc`
  passes.
- GitHub's reply for this repository's latest release was checked to contain the `digest`
  (SHA-256) field the updater relies on.
- End to end on this machine, twice, with a build of 0.2.1 as the installed app and a build of
  0.2.2 as the new version served from a local web server: the app downloaded the archive,
  verified and unpacked it, quit, was replaced, and reopened as 0.2.2 with its backend
  answering and a valid code signature, about 12 seconds after launch. This used a temporary
  hook, not committed, that starts the install without the dialog and from a local address.
  A first attempt did not start a download within two minutes; the cause was not found, and
  the two attempts after it succeeded.
- After that run, one test turned out to be flaky: a failed download could leave an empty file
  behind, because the file was removed while it was still being opened. The download now opens
  the file only once the reply is good and waits for it to close before removing it. The tests
  then passed six times in a row, and the revised function downloaded and verified a 150 MB
  file from a local server and rejected a wrong checksum without leaving a file. The full
  end-to-end run was not repeated after this fix.
- Not verified: the dialog and menu item themselves, the check against the real GitHub API
  from inside the app, and an update between two published releases. The first real update
  will be from the release containing this change to the one after it.
