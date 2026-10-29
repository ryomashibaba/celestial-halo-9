#!/usr/bin/env python3
"""D38 isolated negative controls, no claim of Blender native success."""
import json, sys, shutil, tempfile, subprocess
from pathlib import Path
import numpy as np
import trimesh
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
D37=next((ROOT/x for x in ('D37_CHAT','HALO9_D37_CHAT') if (ROOT/x/'d37_kernel.py').exists()),None)
if not D37:raise RuntimeError('D37 not available')
sys.path.insert(0,str(HERE))
import d38_native_gate as gate
from d38_native_gate import NativeEvidenceError
from d37_prepare import create as create_fixture
from d37_offline_reference import run as make_reference

def check(label,fn):
    try:fn()
    except (NativeEvidenceError,ValueError,FileNotFoundError,RuntimeError) as ex:
        return {'label':label,'rejected':True,'reason':str(ex)[:190]}
    else:raise AssertionError('FAIL OPEN: '+label)

def run():
    fail=[]
    with tempfile.TemporaryDirectory(prefix='halo9-d38-failure-probes-') as td:
        t=Path(td)
        fixture=t/'fixture'
        create_fixture(fixture)
        src=fixture/'D37_NEUTRAL_FIXTURE.glb';ref=fixture/'D37_REFERENCE_EDIT.glb';plan=fixture/'D37_EDIT_PLAN.json'
        make_reference(plan,ref)
        positive=gate.compare_geometry(gate.scene_world(ref),gate.scene_world(ref))
        actual=gate.scene_world(ref)
        evidence=t/'fake_output';evidence.mkdir()
        shutil.copy2(ref,evidence/'FAKE_BLENDER_EXPORT.glb')
        (evidence/'D37_NATIVE_REOPEN.json').write_text('{}')
        (evidence/'D37_BLENDER_RUN.json').write_text(json.dumps({'baked_glb_filename':'FAKE_BLENDER_EXPORT.glb',
                 'native_blend_filename':'DOES_NOT_EXIST.blend','source_sha256':'fake'}))
        original=subprocess.run([sys.executable,str(D37/'d37_glb_crosscheck.py'),str(plan),str(evidence),str(ref)],capture_output=True,text=True)
        if original.returncode!=0:raise AssertionError('D37 false-positive demonstration was not reproduced')
        fail.append(check('d37_forged_metadata_without_blend',lambda:gate.confirm_native(plan,evidence,ref)))
        report={'bpy_module':True,'blender_version':'4.5.15','source_sha256':json.loads(plan.read_text())['source_sha256'],
                'sculpt_shape_key':'D37_SCULPT_EDIT','protected_names':['D37_PROTECTED_FLOOR','D37_PROTECTED_MARKER'],
                'baked_glb_filename':'FAKE_BLENDER_EXPORT.glb','baked_glb_sha256':gate.sha((evidence/'FAKE_BLENDER_EXPORT.glb').read_bytes()),
                'native_blend_filename':'DOES_NOT_EXIST.blend'}
        rr={'native_reopened_in_independent_process':True,'shape_key_verified':True,
            'protected_names_verified':True,'source_hash_unchanged':True,'bpy_version':'4.5.15'}
        (evidence/'D37_BLENDER_RUN.json').write_text(json.dumps(report))
        (evidence/'D37_NATIVE_REOPEN.json').write_text(json.dumps(rr))
        fail.append(check('all_json_true_but_no_blend',lambda:gate.confirm_native(plan,evidence,ref)))
        (evidence/'DOES_NOT_EXIST.blend').write_bytes(b'NOT_BLENDER'+b'0'*1500)
        report['native_blend_sha256']=gate.sha((evidence/'DOES_NOT_EXIST.blend').read_bytes())
        (evidence/'D37_BLENDER_RUN.json').write_text(json.dumps(report))
        fail.append(check('fake_blend_header',lambda:gate.confirm_native(plan,evidence,ref)))
        (evidence/'DOES_NOT_EXIST.blend').write_bytes(b'BLENDER'+b'0'*1500)
        report['native_blend_sha256']=gate.sha((evidence/'DOES_NOT_EXIST.blend').read_bytes())
        (evidence/'D37_BLENDER_RUN.json').write_text(json.dumps(report))
        fail.append(check('fake_blender_header_but_bpy_not_installed',lambda:gate.confirm_native(plan,evidence,ref)))
        report['baked_glb_sha256']='0'*64
        (evidence/'D37_BLENDER_RUN.json').write_text(json.dumps(report))
        fail.append(check('baked_glb_digest_mismatch',lambda:gate.confirm_native(plan,evidence,ref)))
    changed={n:(v.copy(),m.copy()) for n,(v,m) in actual.items()}
    name='D37_SCULPT_TARGET'
    x,m=changed[name]; m.faces=m.faces[:-1].copy();changed[name]=(x,m)
    fail.append(check('missing_triangle_topology',lambda:gate.compare_geometry(actual,changed)))
    # Vertex set unchanged, but reverse all faces (original D37 clouds check would miss).
    changed={n:(v.copy(),m.copy()) for n,(v,m) in actual.items()}
    x,m=changed[name]; m.invert();changed[name]=(x,m)
    fail.append(check('reversed_all_face_orientations',lambda:gate.compare_geometry(actual,changed)))
    changed={n:(v.copy(),m.copy()) for n,(v,m) in actual.items()}
    x,m=changed[name];m.vertices=np.asarray(m.vertices)+[2,0,0];changed[name]=(np.asarray(m.vertices),m)
    fail.append(check('edited_target_2m_drift',lambda:gate.compare_geometry(actual,changed)))
    result={'study':'D38','prior_D37_forged_native_PASS_reproduced':True,'new_gate_negative_tests':fail,
        'negative_tests_all_rejected':all(x['rejected'] for x in fail),
        'positive_geometry_self_comparison':list(positive),
        'actual_blender_executed':False,'actual_native_pass':False,
        'repo_main_edited':False,'formal_adoptions':0,'minecraft':'HOLD'}
    (HERE/'D38_AUDIT.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2,ensure_ascii=False))
    return result
if __name__=='__main__':run()
