#!/usr/bin/env python3
"""Static-only tests for Blender bridge plan: does not pretend to run bpy."""
import json,hashlib,copy,sys,py_compile
from pathlib import Path
HERE=Path(__file__).parent
sys.path.insert(0,str(HERE))
from d36_blender_bridge import validate
source=HERE/'D36_NEUTRAL_TECH_FIXTURE.glb'
plan=json.loads((HERE/'D36_EDIT_PLAN.json').read_text())
names=['D36_SCULPT_TARGET','D36_PROTECTED_FLOOR','D36_PROTECTED_ACCESS_MARKER']
validate(plan,source,names)
checks={'valid_plan':True}
for filename in ['d36_offline_sculpt.py','d36_blender_bridge.py','d36_blender_verify.py','d36_audit.py','d36_render_real_glb.py']:
    py_compile.compile(str(HERE/filename),doraise=True)
checks['python_scripts_syntax_ok']=True

def must_fail(label,fn):
    p=copy.deepcopy(plan);fn(p)
    try:validate(p,source,names)
    except (ValueError,KeyError) as e:checks[label]=str(e)
    else:raise AssertionError(label+' was accepted')
must_fail('bad_sha',lambda p:p.update(source_sha256='0'*64))
must_fail('bad_protected_name',lambda p:p.update(protected_geometries=['BOGUS']))
must_fail('target_protected',lambda p:p.update(protected_geometries=['D36_SCULPT_TARGET','D36_PROTECTED_FLOOR']))
must_fail('unsafe_radius',lambda p:p['strokes'][0].update(radius_m=-1))
must_fail('unsafe_delta',lambda p:p['strokes'][0].update(delta_xyz_m=[10000,0,0]))
must_fail('wrong_status',lambda p:p.update(art_status='ADOPTED'))
checks.update({'blender_executable_available':False,'bpy_runtime_available':False,'native_blend_generated':False})
(HERE/'D36_BLENDER_STATIC_TESTS.json').write_text(json.dumps(checks,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(checks,ensure_ascii=False,indent=2))
