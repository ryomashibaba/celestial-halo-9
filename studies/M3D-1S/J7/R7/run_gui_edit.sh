#!/usr/bin/env bash
set -euo pipefail
ROOT="studies/M3D-1S/J7/R7"
SRC="studies/M3D-1S/J7/R6/outputs/J7R6_TENKAKU_SECTION_NONCANONICAL.blend"
OUT="$ROOT/outputs"
test -s "$SRC"
mkdir -p "$OUT"
# This is a disposable GH runner: no user's local workstation or Work/Computer Use.
blender --background --factory-startup --python-exit-code 23 --python "$ROOT/prepare_gui_scene.py" -- "$SRC" "$OUT/prepared_scene.blend"
test -s "$OUT/prepared_scene.blend"
cp "$OUT/prepared_scene.blend" "$OUT/J7R7_BEFORE_REAL_GUI_EDIT.blend"
previous_stamp="$(stat -c %Y "$OUT/prepared_scene.blend")"
# IMPORTANT: Run the REAL desktop GUI, not --background. Virtual X framebuffer is active.
LIBGL_ALWAYS_SOFTWARE=1 blender "$OUT/prepared_scene.blend" --window-geometry 0 0 1350 860 > "$OUT/blender_gui_stdout.log" 2>&1 &
pid=$!
cleanup(){ kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true; }
trap cleanup EXIT
found=""
for n in $(seq 1 40); do
  if ! kill -0 "$pid" 2>/dev/null; then
    echo "Blender GUI process ended unexpectedly"; tail -50 "$OUT/blender_gui_stdout.log"; exit 1
  fi
  found="$(xdotool search --onlyvisible --name 'Blender' 2>/dev/null | tail -1 || true)"
  if [ -n "$found" ]; then break; fi
  sleep 1
done
test -n "$found" || { echo "Real Blender GUI window was never shown"; exit 1; }
echo "J7R7_GUI_WINDOW" "$(xdotool getwindowname "$found")" ID="$found"
# xvfb-run has no EWMH window manager; use native XSetInputFocus instead.
xdotool windowfocus --sync "$found"
echo "J7R7_FOCUSED_WINDOW" "$(xdotool getwindowfocus)"
xdotool mousemove --window "$found" 680 400
sleep 11
# The prepared scene has the real public-hall mesh active and in Edit Mode.
# Screenshot is obtained from actual X display, NOT Blender offscreen render.
scrot -z "$OUT/01_REAL_GUI_BEFORE.png"
sleep 2
# Transform with actual editor keyboard shortcuts in Blender viewport.
# A selects all vertices of the existing public hall mesh, S X 1.35 enlarges it.
xdotool key --clearmodifiers a
sleep 0.7
xdotool key --clearmodifiers s
sleep .4
xdotool key --clearmodifiers x
sleep .4
xdotool key --clearmodifiers 1 period 3 5
sleep 1
xdotool key --clearmodifiers Return
sleep 2
scrot -z "$OUT/02_GUI_AFTER_SCALE.png"
sleep 1
# Translate selected existing vertices 65 metres along the model Y axis.
xdotool key --clearmodifiers g
sleep .4
xdotool key --clearmodifiers y
sleep .4
xdotool key --clearmodifiers minus 6 5
sleep 1
xdotool key --clearmodifiers Return
sleep 2
scrot -z "$OUT/02_REAL_GUI_AFTER.png"
# UI save into the previously prepared and disposable scene, NOT source R6.
sleep 2
xdotool key --clearmodifiers ctrl+s
sleep 4
new_stamp="$(stat -c %Y "$OUT/prepared_scene.blend")"
if [ "$new_stamp" -le "$previous_stamp" ]; then
  echo "GUI Ctrl+S did not update the prepared scene"; exit 1
fi
cp "$OUT/prepared_scene.blend" "$OUT/J7R7_AFTER_REAL_GUI_EDIT.blend"
# Blender GUI is closed after saving, then a separate Blender process checks actual
# geometry and GLB export. Fail on ANY GUI/geometry/renderer false-positive.
cleanup
trap - EXIT
blender --background --factory-startup --python-exit-code 23 --python "$ROOT/verify_gui_mesh_change.py" -- \
 "$OUT/J7R7_BEFORE_REAL_GUI_EDIT.blend" "$OUT/J7R7_AFTER_REAL_GUI_EDIT.blend" "$OUT"
test -s "$OUT/J7R7_REAL_GUI_EXECUTION_PROOF.json"
echo 'J7R7_ACTUAL_GUI_VIEWPORT_EDIT_SUCCESS'
