#!/usr/bin/env bash
set -euo pipefail
OUT="$1"
ROOT="studies/M3D-1S/J7/R33-S27/D47_R11_WORKSTATION"
ORIGINAL="$OUT/R11_OPEN_IN_BLENDER_VISUAL_SCULPT_STUDIO.blend"
EDITED="$OUT/R11_GUI_ACTUAL_INPUT_EDITED_COPY.blend"
test -s "$ORIGINAL"
cp "$ORIGINAL" "$EDITED"
originalsha="$(sha256sum "$ORIGINAL"|awk '{print $1}')"
# Real X11 Blender GUI in disposable virtual display, NOT Work/user PC.
LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe \
blender --factory-startup "$EDITED" --python "$ROOT/r11_art_direction_toolbar.py" \
 --window-geometry 0 0 1420 880 > "$OUT/R11_BLENDER_REAL_GUI_LOG.txt" 2>&1 &
pid=$!
cleanup(){ kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true; }
trap cleanup EXIT
win=""
for i in $(seq 1 55); do
    if ! kill -0 "$pid" 2>/dev/null; then
        echo "R11_GUI_PROCESS_DIED";tail -80 "$OUT/R11_BLENDER_REAL_GUI_LOG.txt";exit 1
    fi
    win="$(xdotool search --onlyvisible --name 'Blender' 2>/dev/null | tail -1 || true)"
    if [ -n "$win" ]; then break; fi
    sleep 1
done
test -n "$win" || { echo 'R11 Blender GUI never became visible';exit 1; }
echo "R11_GUI_WINDOW_ID=$win"
xdotool windowfocus --sync "$win"
sleep 4
xdotool mousemove --window "$win" 674 686
xdotool click 1
sleep 2
xdotool key --clearmodifiers Escape
sleep 1
xdotool mousemove --window "$win" 550 400
xdotool key --clearmodifiers n
sleep 2
scrot -z "$OUT/R11_01_REAL_GUI_BEFORE.png"
xdotool mousemove --window "$win" 475 420
xdotool key --clearmodifiers Tab
sleep 1
xdotool key --clearmodifiers a
sleep .5
xdotool key --clearmodifiers g
sleep .4
xdotool key --clearmodifiers x
sleep .4
xdotool key --clearmodifiers 3 0
sleep .6
xdotool key --clearmodifiers Return
sleep 2
scrot -z "$OUT/R11_02_REAL_GUI_AFTER.png"
xdotool key --clearmodifiers ctrl+s
sleep 4
echo "R11_AFTER_SAVE_SHA=$(sha256sum "$EDITED"|awk '{print $1}')"
test "$originalsha" = "$(sha256sum "$ORIGINAL"|awk '{print $1}')"
test "$originalsha" != "$(sha256sum "$EDITED"|awk '{print $1}')"
cleanup;trap - EXIT
echo "R11_GUI_VIEWPORT_OPERATOR_AND_BLENDER_SAVE_TEST_COMPLETE"
