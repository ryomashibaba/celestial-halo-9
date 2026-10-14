# M119–M121 offline research source

`upstream/` is a byte-for-byte copy of the 46 non-cache files from the local M121 handoff ZIP. Do not run generators or renderers there: their entry points overwrite bundled data/images, and `render_m119_sections.py` writes an image even when imported. Changes belong in a separate working copy. The M117 atlas is user-provided offline evidence; no Minecraft save is needed or authorized.

From the repository root, run:

```powershell
../.venv/Scripts/python.exe -B -X utf8 tools/m121_offline_check.py --repo-tests
```

The isolated environment uses CPython 3.12.14 and no third-party dependencies for these 15 tests. `-X utf8` is required for original sources that omit an explicit encoding; `-B` prevents new cache files. `--repo-tests` also runs the existing 37 repository tests and policy check, directing synthetic identity fixtures to `artifacts/test-temp/`. The default sandbox temporary directory refused fixture creation/cleanup with WinError 5; no real save is used by these tests.

Rendering environment is pending: matplotlib and VTK are absent; the original M121 renderer requires Pillow and a Linux-only DejaVu font path. Reference dependency lower bounds are in `upstream/requirements_m121_reference.txt`, not a verified render lock. Install/lock the rendering stack in a separate environment and adapt a working copy's font/output paths before rendering. No renderer has been executed during setup.

All geometry remains NON-CONSTRUCTION research. 38 M120 overlap candidates and 0 M121 limited material AABB hits do not establish protected clearance. Freeze408/public959, SB09, SB13, 88 voids, roads/parks, M101 and formal designs remain unchanged. Construction world is unregistered. No M122 implementation or GitHub push/merge is part of this import.
