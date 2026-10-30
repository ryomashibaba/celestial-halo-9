#!/usr/bin/env bash
set -euo pipefail
OUT="$1"
PRE="$OUT/R14_E0_NATIVE_PRESELECTED.blend"
EDIT="$OUT/R14_E1_ACTUAL_LOCAL_SCULPT.blend"
test -s "$PRE"
cp "$PRE" "$EDIT"
sha="$(sha256sum "$PRE"|awk '{print $1}')"
LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe blender \
  --factory-startup "$EDIT" --window-geometry 0 0 1400 900 \
  >"$OUT/R14_REAL_GUI_STDOUT.txt" 2>&1 &
pid=$!
cleanup(){ kill "$pid" 2>/dev/null || :; wait "$pid" 2>/dev/null || :; }
trap cleanup EXIT
win=""
for attempt in $(seq 1 55); do
  kill -0 "$pid" 2>/dev/null || { cat "$OUT/R14_REAL_GUI_STDOUT.txt";exit 1; }
  win="$(xdotool search --onlyvisible --name Blender 2>/dev/null | tail -1 || true)"
  test -n "$win" && break
  sleep 1
done
test -n "$win" || { echo "No visible Blender desktop"; exit 1; }
xdotool windowfocus --sync "$win"
sleep 3
# Handle disposable Blender first-run.
xdotool mousemove --window "$win" 674 686;xdotool click 1
sleep 2
xdotool key --clearmodifiers Escape
xdotool mousemove --window "$win" 410 370
sleep 2
scrot -z "$OUT/R14_E0_REAL_GUI_BEFORE.png"
# Critically: EDIT-mode preselection is a restricted local mesh patch,
# not the global A + G move used in J7-R7/R11.
xdotool key --clearmodifiers g
sleep .5
xdotool key --clearmodifiers y
sleep .5
xdotool key --clearmodifiers 1 2 0
sleep .5
xdotool key --clearmodifiers Return
sleep 2
scrot -z "$OUT/R14_E1_REAL_GUI_LOCAL_AFTER.png"
xdotool key --clearmodifiers ctrl+s
sleep 3
test "$sha" = "$(sha256sum "$PRE"|awk '{print $1}')"
test "$sha" != "$(sha256sum "$EDIT"|awk '{print $1}')"
cleanup;trap - EXIT
echo "R14_NATIVE_GUI_LOCAL_SELECTION_MODIFICATION_COMPLETED"
