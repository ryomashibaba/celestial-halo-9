"""Reproduce the observed edit stages after Boolean topology repair."""
import bpy,sys
from pathlib import Path
ROOT=Path(__file__).parent;sys.path.insert(0,str(ROOT))
import build_r13 as H,revise_r13 as R
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'exploration_C/R13_C.blend'))
H.attach_existing();H.save(ROOT/'selected','R13_C_SELECTED');H.render(ROOT/'selected')
R.revision1();H.render(ROOT/'revision_1')
R.revision2();H.render(ROOT/'revision_2')
