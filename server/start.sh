#!/usr/bin/env bash
# Heap: 4G is right for a small friend-server (4-8 players). Raise to 6G for more.
cd "$(dirname "$0")"
# Re-sync the pack on every start so the server tracks pack updates.
java -jar packwiz-installer-bootstrap.jar -g -s server "${PACK_URL:-file:///home/aki/dev/comet-croft/pack.toml}"
exec java -Xms4G -Xmx4G \
  -XX:+UseG1GC -XX:MaxGCPauseMillis=37 -XX:+PerfDisableSharedMem \
  -XX:G1HeapRegionSize=16M -XX:G1NewSizePercent=23 -XX:G1ReservePercent=20 \
  -XX:SurvivorRatio=32 -XX:G1MixedGCCountTarget=3 -XX:G1HeapWastePercent=20 \
  -XX:InitiatingHeapOccupancyPercent=10 -XX:G1RSetUpdatingPauseTimePercent=0 \
  -XX:MaxTenuringThreshold=1 -XX:+ParallelRefProcEnabled \
  -jar fabric-server.jar nogui
