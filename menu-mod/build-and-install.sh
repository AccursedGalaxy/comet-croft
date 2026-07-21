#!/usr/bin/env bash
# Build the Comet Croft menu mod and install it into the packwiz pack so the
# dev instance (and `testing/e2e.py client`) picks it up on next launch.
#
#   jar  ->  mods/comet-croft-menu.jar  ->  packwiz refresh  ->  e2e sync
#
# Usage: menu-mod/build-and-install.sh
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
MODDIR="$REPO/menu-mod"
JAVA_HOME="${JAVA_HOME:-$HOME/.local/share/mise/installs/java/temurin-25.0.3+9.0.LTS}"
PACKWIZ="${PACKWIZ:-$HOME/go/bin/packwiz}"
export JAVA_HOME

echo ">> building menu mod (JAVA_HOME=$JAVA_HOME)"
cd "$MODDIR"
./gradlew build -q

JAR="$(ls -t "$MODDIR"/build/libs/comet-croft-menu-*.jar | head -1)"
echo ">> built $JAR"

DEST="$REPO/mods/comet-croft-menu.jar"
cp "$JAR" "$DEST"
echo ">> installed -> $DEST"

echo ">> packwiz refresh"
cd "$REPO"
"$PACKWIZ" refresh

echo ">> done. index entry:"
grep -A3 'comet-croft-menu.jar' "$REPO/index.toml" || echo "   (not found in index.toml — check packwiz refresh)"
