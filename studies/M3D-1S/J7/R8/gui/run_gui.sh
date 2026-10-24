#!/usr/bin/env bash
# Proven J7-R7 graphical X11 Blender workflow, adapted for R8's sculptural roof crest.
set -euo pipefail
ROOT="studies/M3D-1S/J7/R8/gui"
SRC="studies/M3D-1S/J7/R8/outputs/J7R8_CIVIC_LENS_ART_STUDY.blend"
OUT="$ROOT/outputs"
test -s "$SRC"
mkdir -p "$OUT"
blender --background --factory-startup --python-exit-code 23 --python "$ROOT/prepare_gui.py" -- "$SRC" "$OUT/prepared.blend"
test -s "$OUT/prepared.blend"
cp "$OUT/prepared.blend" "$OUT/J7R8_GUI_BEFORE.blend"
STAMP="$(stat -c %Y "$OUT/prepared.blend")"
LIBGL_ALWAYS_SOFTWARE=1 blender "$OUT/prepared.blend" --window-geometry 0 0 1350 860 > "$OUT/blender_desktop.log" 2>&1 &
PID=$!
cleanup(){ kill "$PID" 2>/dev/null || true; wait "$PID" 2>/dev/null || true; }
trap cleanup EXIT
found=""
for n in $(seq 1 40); do
  kill -0 "$PID" 2>/dev/null || { echo 'GUI Blender process failed'; tail -40 "$OUT/blender_desktop.log"; exit 1; }
  found="$(xdotool search --onlyvisible --name Blender 2>/dev/null | tail -1 || true)"
  if [[ -n "$found" ]]; then break; fi
  sleep 1
done
test -n "$found" || { echo "no actual Blender GUI window found"; exit 1; }
xdotool windowfocus --sync "$found"
echo "R8_REAL_X11_GUI" "$(xdotool getwindowname "$found")"
# This runner launches on a NEW disposable machine. First startup has Quick Setup.
sleep 4
xdotool mousemove --window "$found" 674 686
xdotool click 1
sleep 3
xdotool key --clearmodifiers Escape
sleep 1
xdotool mousemove --window "$found" 680 400
sleep 4
scrot -z "$OUT/01_ACTUAL_GUI_BEFORE.png"
# Edit the selected roof crest vertices in REAL Blender Edit Mode:
# G > Z > 1 2 0 > Return => lift +120m, while anchored base vertices stay fixed.
xdotool key --clearmodifiers g
sleep .4
xdotool key --clearmodifiers z
sleep .4
xdotool key --clearmodifiers 1 2 0
sleep 1
xdotool key --clearmodifiers Return
sleep 2
scrot -z "$OUT/02_ACTUAL_GUI_AFTER.png"
sleep 1
xdotool key --clearmodifiers ctrl+s
sleep 4
NEWSTAMP="$(stat -c %Y "$OUT/prepared.blend")"
if [[ "$NEWSTAMP" -le "$STAMP" ]]; then echo 'GUI did not save'; exit 1; fi
cp "$OUT/prepared.blend" "$OUT/J7R8_GUI_AFTER.blend"
cleanup
trap - EXIT
blender --background --factory-startup --python-exit-code 23 --python "$ROOT/verify_gui.py" -- \
 "$OUT/J7R8_GUI_BEFORE.blend" "$OUT/J7R8_GUI_AFTER.blend" "$OUT"
test -s "$OUT/J7R8_REAL_GUI_EDIT_EVIDENCE.json"
echo "J7R8_GUI_EDIT_AND_NINE_VIEW_PASS"
