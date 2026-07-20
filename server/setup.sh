#!/usr/bin/env bash
# Comet Croft — one-shot dedicated server setup.
#
# Usage:
#   ./setup.sh --accept-eula [PACK_URL]
#
# PACK_URL defaults to the local repo checkout (file://…/pack.toml) so you
# can test on this machine; for a remote server pass the raw pack.toml URL,
# e.g. https://raw.githubusercontent.com/AccursedGalaxy/comet-croft/master/pack.toml
#
# Requires: Java 21+ on PATH (Temurin recommended), curl.
set -euo pipefail

MC_VERSION="26.1.2"
FABRIC_LOADER="0.19.3"
DEFAULT_PACK_URL="file://$(cd "$(dirname "$0")/.." && pwd)/pack.toml"

ACCEPT_EULA=0
PACK_URL="$DEFAULT_PACK_URL"
for arg in "$@"; do
  case "$arg" in
    --accept-eula) ACCEPT_EULA=1 ;;
    *) PACK_URL="$arg" ;;
  esac
done

if [ "$ACCEPT_EULA" -ne 1 ]; then
  echo "You must accept the Minecraft EULA (https://aka.ms/MinecraftEULA)."
  echo "Re-run with: ./setup.sh --accept-eula [PACK_URL]"
  exit 1
fi

JAVA_MAJOR=$(java -version 2>&1 | head -1 | grep -oE '"[0-9]+' | tr -d '"')
if [ "${JAVA_MAJOR:-0}" -lt 21 ]; then
  echo "Java 21+ required (found ${JAVA_MAJOR:-none}). Install Temurin 21+ and retry."
  exit 1
fi

cd "$(dirname "$0")"

INSTALLER=$(curl -s https://meta.fabricmc.net/v2/versions/installer | grep -o '"version": *"[^"]*"' | head -1 | cut -d'"' -f4)
echo "Fetching Fabric server launcher (MC $MC_VERSION, loader $FABRIC_LOADER, installer $INSTALLER)…"
curl -sL -o fabric-server.jar \
  "https://meta.fabricmc.net/v2/versions/loader/$MC_VERSION/$FABRIC_LOADER/$INSTALLER/server/jar"
curl -sL -o packwiz-installer-bootstrap.jar \
  https://github.com/packwiz/packwiz-installer-bootstrap/releases/latest/download/packwiz-installer-bootstrap.jar

echo "Installing pack (server side) from: $PACK_URL"
java -jar packwiz-installer-bootstrap.jar -g -s server "$PACK_URL"

echo "eula=true" > eula.txt

if [ ! -f server.properties ]; then
  cat > server.properties <<'EOF'
motd=Comet Croft — a homestead under a strange sky
view-distance=8
simulation-distance=8
sync-chunk-writes=false
spawn-protection=0
difficulty=normal
white-list=true
enforce-whitelist=true
EOF
  echo "Wrote default server.properties (whitelist ON — add players before they can join)."
fi

if [ ! -f start.sh ]; then
  cat > start.sh <<'EOF'
#!/usr/bin/env bash
# Heap: 4G is right for a small friend-server (4-8 players). Raise to 6G for more.
cd "$(dirname "$0")"
# Re-sync the pack on every start so the server tracks pack updates.
java -jar packwiz-installer-bootstrap.jar -g -s server "${PACK_URL:-PACK_URL_PLACEHOLDER}"
exec java -Xms4G -Xmx4G \
  -XX:+UseG1GC -XX:MaxGCPauseMillis=37 -XX:+PerfDisableSharedMem \
  -XX:G1HeapRegionSize=16M -XX:G1NewSizePercent=23 -XX:G1ReservePercent=20 \
  -XX:SurvivorRatio=32 -XX:G1MixedGCCountTarget=3 -XX:G1HeapWastePercent=20 \
  -XX:InitiatingHeapOccupancyPercent=10 -XX:G1RSetUpdatingPauseTimePercent=0 \
  -XX:MaxTenuringThreshold=1 -XX:+ParallelRefProcEnabled \
  -jar fabric-server.jar nogui
EOF
  sed -i "s|PACK_URL_PLACEHOLDER|$PACK_URL|" start.sh
  chmod +x start.sh
fi

echo
echo "Done. Next steps:"
echo "  1. ./start.sh                       — first boot (world gen takes a minute)"
echo "  2. whitelist add <player>           — from the server console"
echo "  3. chunky radius 3000 && chunky start   — pre-generate spawn region (recommended)"
echo "  4. See docs/SERVER.md for LuckPerms permission setup."
