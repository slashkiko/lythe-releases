#!/bin/sh
# Installs the latest Lythe into /Applications.
#
#   curl -fsSL https://slashkiko.github.io/lythe-releases/install.sh | sh
#
# Lythe is not signed by Apple. A file downloaded with curl carries no quarantine
# flag, so the app installed this way opens without the `xattr` step that a
# browser-downloaded .dmg needs.
set -eu

REPO="slashkiko/lythe-releases"
LATEST_JSON="${LYTHE_LATEST_JSON:-https://github.com/$REPO/releases/latest/download/latest.json}"
APP_DIR="${LYTHE_APP_DIR:-/Applications}"

fail() { printf 'lythe: %s\n' "$1" >&2; exit 1; }

[ "$(uname -s)" = "Darwin" ] || fail "Lythe runs on macOS only."
[ "$(uname -m)" = "arm64" ] || fail "Lythe needs an Apple Silicon Mac (this one is $(uname -m))."

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

printf 'Finding the latest release...\n'
# latest.json is the Tauri updater manifest; the app archive for this Mac is under
# platforms."darwin-aarch64".url. Read it with sed so the script needs nothing beyond macOS.
curl -fsSL -o "$tmp/latest.json" "$LATEST_JSON" || fail "Could not download $LATEST_JSON"
manifest="$(tr -d '\n' < "$tmp/latest.json")"
version="$(printf '%s' "$manifest" | sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
url="$(printf '%s' "$manifest" | sed -n 's/.*"darwin-aarch64"[[:space:]]*:[[:space:]]*{[^}]*"url"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
[ -n "$url" ] || fail "The release has no Apple Silicon build."

printf 'Downloading Lythe %s...\n' "${version:-?}"
curl -fL --progress-bar -o "$tmp/Lythe.app.tar.gz" "$url" || fail "Could not download $url"
tar -xzf "$tmp/Lythe.app.tar.gz" -C "$tmp" || fail "The download is not a valid archive."
[ -d "$tmp/Lythe.app" ] || fail "The archive does not contain Lythe.app."

if pgrep -x lythe >/dev/null 2>&1; then
  fail "Lythe is running. Quit it and run this command again."
fi

mkdir -p "$APP_DIR"
if [ -e "$APP_DIR/Lythe.app" ]; then
  rm -rf "$APP_DIR/Lythe.app" || fail "Could not replace $APP_DIR/Lythe.app. Remove it and run this command again."
fi
mv "$tmp/Lythe.app" "$APP_DIR/Lythe.app" || fail "Could not write to $APP_DIR."

printf 'Installed Lythe %s in %s.\n' "${version:-?}" "$APP_DIR"
printf 'Next: sign in to GitHub CLI with `gh auth login` if you have not, then open Lythe.\n'
