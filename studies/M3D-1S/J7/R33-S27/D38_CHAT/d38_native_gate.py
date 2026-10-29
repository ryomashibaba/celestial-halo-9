#!/usr/bin/env python3
"""D38 fail-closed Blender-native evidence gate (run ONLY with genuine bpy).

Requires a real .blend reopen in this independent process; report-file existence,
synthetic JSON or copied GLB alone CANNOT establish Blender success.
Not an architectural/art/structural certification.
"""
import json,sys,hashlib
from pathlib import Path
import numpy as np, trimesh
from scipy.spatial import cKDTree

BASE_DIR=Path(__file__).resolve().parent.parent
D37=next((BASE_DIR/name for name in ('D37_CHAT','HALO9_D37_CHAT') if (BASE_DIR/name/'d37_kernel.py').is_file()),None)
if D37 is None: raise RuntimeError('D37 source dependency missing')
sys.path.insert(0,str(D37))
from d37_kernel import validate,apply,sha

class NativeEvidenceError(ValueError): pass

def jload(p):
    with Path(p).open(encoding='utf-8') as f:return json.load(f)

def bounded_names(p):
    return {p['target_geometry'], *p['protected_geometries']}

def verified_file(out,name,digest_key,report,min_bytes=100):
    if Path(name).name!=name or '/' in name or '\\' in name:raise NativeEvidenceError('nonlocal output path')
    path=out/name
    if not path.is_file() or path.stat().st_size<min_bytes:raise NativeEvidenceError('missing or trivial output: '+name)
    if report.get(digest_key)!=sha(path.read_bytes()):raise NativeEvidenceError('output sha mismatch: '+name)
    return path

def check_artifacts(planpath,outdir):
    planpath=Path(planpath).resolve();out=Path(outdir).resolve()
    p=jload(planpath); source=planpath.parent/p['source_filename']
    if source.parent.resolve()!=planpath.parent:raise NativeEvidenceError('input path escaped')
    if not source.is_file():raise NativeEvidenceError('source GLB not found')
    validate(p,source,bounded_names(p))
    report_file=out/'D37_BLENDER_RUN.json'; re_file=out/'D37_NATIVE_REOPEN.json'
    if not report_file.is_file() or not re_file.is_file():raise NativeEvidenceError('missing Blender execution/reopen report')
    report=jload(report_file);re=jload(re_file)
    if report.get('bpy_module') is not True or not str(report.get('blender_version','')).startswith('4.5.'):
        raise NativeEvidenceError('not genuine approved Blender 4.5 run metadata')
    if report.get('source_sha256')!=p['source_sha256'] or report.get('sculpt_shape_key')!='D37_SCULPT_EDIT':
        raise NativeEvidenceError('Blender report source / key mismatch')
    for k in ('native_reopened_in_independent_process','shape_key_verified','protected_names_verified','source_hash_unchanged'):
        if re.get(k) is not True:raise NativeEvidenceError('Native reopen attestation missing: '+k)
    if re.get('bpy_version')!=report.get('blender_version'):
        raise NativeEvidenceError('native blender version mismatch')
    if set(report.get('protected_names',[]))!=set(p['protected_geometries']):
        raise NativeEvidenceError('protected names mismatch')
    blend=verified_file(out,report.get('native_blend_filename',''), 'native_blend_sha256',report, min_bytes=1000)
    if blend.suffix!='.blend' or not blend.read_bytes().startswith(b'BLENDER'):
        raise NativeEvidenceError('Invalid Blender native header')
    glb=verified_file(out,report.get('baked_glb_filename',''),'baked_glb_sha256',report,min_bytes=300)
    return p,source,out,blend,glb,report,re

def scene_world(path):
    s=trimesh.load(str(path),force='scene',process=False)
    meshes={}
    for node in s.graph.nodes_geometry:
        t,name=s.graph.get(node); m=s.geometry[name]
        if name in meshes:raise NativeEvidenceError('multi-instancing ambiguous: '+name)
        verts=trimesh.transform_points(np.asarray(m.vertices),t)
        transformed=m.copy();transformed.apply_transform(t)
        meshes[name]=(verts,transformed)
    return meshes

def set_dist(a,b):
    if not len(a) or not len(b):raise NativeEvidenceError('empty geometry')
    return float(max(cKDTree(a).query(b)[0].max(),cKDTree(b).query(a)[0].max()))

def compare_geometry(a,b,threshold=0.05):
    if set(a)!=set(b):raise NativeEvidenceError(f'mesh names differ {set(a)^set(b)}')
    results={}
    for name in a:
        av,am=a[name];bv,bm=b[name]
        d=set_dist(av,bv)
        if d>threshold:raise NativeEvidenceError(f'vertex positions drift {name}: {d:.4f} m')
        if len(am.faces)!=len(bm.faces):raise NativeEvidenceError(f'face count differs {name}')
        denom=max(abs(am.area),1)
        area_error=abs(am.area-bm.area)/denom
        if area_error>0.005:raise NativeEvidenceError(f'area drift {name}: {area_error:.3%}')
        denom_v=max(abs(am.volume),1)
        vol_error=abs(am.volume-bm.volume)/denom_v
        if vol_error>0.005:raise NativeEvidenceError(f'volume drift {name}: {vol_error:.3%}')
        if am.volume*bm.volume<=0:raise NativeEvidenceError(f'face orientation / volume invalid {name}')
        results[name]={'vertex_set_max_m':d,'faces':len(am.faces),'relative_area_error':float(area_error),'relative_volume_error':float(vol_error)}
    return results

def confirm_native(planpath,outdir,reference_glb):
    p,source,out,blend,glb,report,re=check_artifacts(planpath,outdir)
    try:import bpy
    except ImportError as exc:raise NativeEvidenceError('GENUINE_BPY_REQUIRED: never certify from JSON and copied GLB') from exc
    if not bpy.app.version_string.startswith('4.5.'):
        raise NativeEvidenceError('Wrong Blender version')
    # Reopen the actual .blend in THIS fresh third CI process, not from report claims.
    if bpy.ops.wm.open_mainfile(filepath=str(blend)) not in ({'FINISHED'},):
        raise NativeEvidenceError('Blender could not reopen native file')
    target=bpy.data.objects.get(p['target_geometry'])
    if target is None or target.type!='MESH' or not target.data.shape_keys:
        raise NativeEvidenceError('Actual .blend missing target shape key object')
    keys=target.data.shape_keys.key_blocks
    if 'Basis' not in keys or 'D37_SCULPT_EDIT' not in keys or abs(keys['D37_SCULPT_EDIT'].value-1)>1e-5:
        raise NativeEvidenceError('Actual native key missing or inactive')
    for name in p['protected_geometries']:
        ob=bpy.data.objects.get(name)
        if ob is None or ob.type!='MESH' or ob.data.shape_keys:
            raise NativeEvidenceError('Native protected object missing or edited: '+name)
    rworld=np.array([tuple(target.matrix_world @ v.co) for v in keys['D37_SCULPT_EDIT'].data])
    orig=scene_world(source)
    expected=apply(orig[p['target_geometry']][0],p['strokes'])
    shape_dist=set_dist(rworld,expected)
    if shape_dist>0.05:raise NativeEvidenceError(f'native shape key differs from independent formula {shape_dist:.4f}m')
    for name in p['protected_geometries']:
        obj=bpy.data.objects[name]
        world=np.array([tuple(obj.matrix_world@v.co) for v in obj.data.vertices])
        if set_dist(world,orig[name][0])>0.05:
            raise NativeEvidenceError('native protected object coordinates drift: '+name)
    reference=scene_world(reference_glb); baked=scene_world(glb)
    result=compare_geometry(reference,baked)
    for name in p['protected_geometries']:
        if set_dist(baked[name][0],orig[name][0])>0.05:raise NativeEvidenceError('protected GLB changed: '+name)
    if set_dist(baked[p['target_geometry']][0],orig[p['target_geometry']][0])<2:
        raise NativeEvidenceError('No genuine target deformation in export')
    result_dict={'status':'NATIVE_TECH_ONLY_PASS','bpy':bpy.app.version_string,
        'actual_blend_reopened_in_gate_process':True,'shape_key_max_deviation_m':shape_dist,
        'real_blender_glb_geometry':result,'native_blend_sha256':sha(blend.read_bytes()),
        'real_blender_glb_sha256':sha(glb.read_bytes()),'city_master_complete':False,
        'art':'NOT_SUBMITTED','formal_adoptions':0,'minecraft':'HOLD'}
    dest=out/'D38_NATIVE_ATTESTED.json';dest.write_text(json.dumps(result_dict,indent=2)+'\n',encoding='utf-8')
    return result_dict

if __name__=='__main__':
    if len(sys.argv)!=4:raise SystemExit('usage: python d38_native_gate.py PLAN.json BLENDER_OUTPUT_DIR REFERENCE.glb')
    print(json.dumps(confirm_native(*sys.argv[1:]),indent=2))
