#!/usr/bin/env bash
set -euo pipefail
P="$1"
E1="$P/R14_E2_PREPARED_BOUNDARY_TRANSITION.blend"
E2="$P/R14_E2_GUI_BOUNDARY_REFINED.blend"
test -s "$E1";cp "$E1" "$E2"
original="$(sha256sum "$E1"|awk '{print $1}')"
LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe \
blender --factory-startup "$E2" --window-geometry 0 0 1400 900 \
 >"$P/R14_E2_REAL_GUI_STDOUT.txt" 2>&1 &
pid=$!
cleanup(){ kill "$pid" 2>/dev/null || :; wait "$pid" 2>/dev/null || :; }
trap cleanup EXIT
window=""
for i in $(seq 1 55);do
  kill -0 "$pid" 2>/dev/null || { cat "$P/R14_E2_REAL_GUI_STDOUT.txt";exit 1; }
  window="$(xdotool search --onlyvisible --name Blender 2>/dev/null | tail -1 || true)"
  test -n "$window" && break
  sleep 1
done
test -n "$window" || exit 1
xdotool windowfocus --sync "$window"
sleep 3
xdotool mousemove --window "$window" 674 686; xdotool click 1
sleep 2
xdotool key --clearmodifiers Escape
xdotool mousemove --window "$window" 420 400
sleep 2
scrot -z "$P/R14_E2_BEFORE_REAL_GUI.png"
# This is a *different* patch from E1: near-core boundary only.
xdotool key --clearmodifiers g
sleep .5
xdotool key --clearmodifiers y
sleep .5
xdotool key --clearmodifiers 6 0
sleep .5
xdotool key --clearmodifiers Return
sleep 2
scrot -z "$P/R14_E2_AFTER_REAL_GUI.png"
xdotool key --clearmodifiers ctrl+s
sleep 3
test "$original" = "$(sha256sum "$E1"|awk '{print $1}')"
test "$original" != "$(sha256sum "$E2"|awk '{print $1}')"
cleanup;trap - EXIT
echo R14_E2_LOCAL_BOUNDARY_GUI_SAVED
