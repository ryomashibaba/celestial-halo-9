"""Verify R21 evidence completeness, summarize finite visibility and package it."""
import json, hashlib, subprocess, struct
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parent;Q=R/'qa'
load=lambda p:json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
views=['front','oblique','side','rear','aerial','underside']
required={m:[f'{regime}_{v}' for regime in ['fixed16km','fit'] for v in views]+
          ['material_'+v for v in ['oblique','rear','underside','open_oblique','floor_axis_middle','floor_high']]+
          ['floor_'+v for v in ['low','mid','high','axis_entry','axis_middle','axis_arrival','low_axis15']]+['fit_open_oblique'] for m in ['R19','C55A']}
required['C55A']+=['clay_decals_on_oblique','floor_hall','section_longitudinal_X860','section_cross_Yminus600']
checks=[]
for model,tags in required.items():
    for tag in tags:
        image=R/'renders'/model/(tag+'.png');j=load(Q/(model+'_'+tag+'.json'))
        assert image.exists() and Image.open(image).size==(1600,900),(model,tag)
        assert j['hfov_degrees']==50 and j['emission'] is False
        if model=='C55A':assert len(j['effect_meshes_hidden'])==6,(model,tag)
        if tag.startswith('fixed16km'):assert abs(j['center_distance_m']-16000)<.01
        checks.append(dict(model=model,tag=tag,file=str(image.relative_to(R)),sha256=sha(image)))
visibility={}
for model in ['R19','C55A']:
    floors=load(Q/(model+'_FLOORS.json'));visibility[model]={}
    for tag,info in floors.items():
        assert abs(info['eye_above_floor_m']-1.7)<.002
        assert info['floor']['normal'][2]>.985
        hits=info['frustum_first_hits'];distances=[v['distance_m'] for v in hits]
        far=sorted([v for v in hits if v['distance_m']>2000],key=lambda x:-x['distance_m'])
        visibility[model][tag]=dict(floor_native_m=info['native_floor_m'],floor_object=info['floor']['object'],
             max_sampled_first_hit_distance_m=max(distances,default=None),far_first_hit_examples=far[:4],
             distinct_hit_objects=sorted(set(v['object'] for v in hits)),
             note='77 finite frustum directions; far hits may be walls/rings, not habitable districts. No continuous route proof.')
(Q/'VISIBILITY_SUMMARY.json').write_text(json.dumps(visibility,indent=2,ensure_ascii=False),encoding='utf8')
# Independently account for the importer's discarded unreferenced GLB vertices.
b=(R/'source/model/C55A_SevenfoldHaloRift.glb').read_bytes();jl=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+jl]);base=28+jl
total=used=0
for m in g['meshes']:
    p=m['primitives'][0];a=g['accessors'][p['indices']];v=g['bufferViews'][a['bufferView']]
    indices=struct.unpack_from('<'+str(a['count'])+'I',b,base+v.get('byteOffset',0)+a.get('byteOffset',0))
    total+=g['accessors'][p['attributes']['POSITION']]['count'];used+=len(set(indices))
assert total-used==502 and load(Q/'C55A_IMPORT.json')['all']['vertices']==used
readback=load(Q/'SAVED_READBACK.json');assert readback['R19']['geometry_readback_exact'] and readback['C55A']['geometry_readback_exact']
source=load(R/'SOURCE_VERIFICATION.json')
assert sha(R.parent/'R19/final/R19_LIVING_HORIZON.blend')==source['r19_original_sha256']
assert sha(R/'source/model/C55A_SevenfoldHaloRift.glb')==source['glb_sha256']
assert sha(Path(source['zip_original_path']))==source['zip_sha256']
branch=subprocess.check_output(['git','branch','--show-current'],text=True).strip()
assert branch=='research/m3d1s-j7-r21-c55a-r19-blender-comparison-20261025'
changed=subprocess.check_output(['git','diff','--name-only','8ed17bcb0078e5fcd276e5db72954791d2ae1338'],text=True).splitlines()
assert all(p.startswith('studies/M3D-1S/J7/R21/') for p in changed)
result=dict(required_images=len(checks),all_images_and_camera_records_present=True,images=checks,
            glb_accessor_vertices=total,referenced_vertices=used,unreferenced_vertices_discarded_by_importer=total-used,
            original_sources_unchanged=True,only_r21_tracked_changes=True,scope='Focused source/readback/camera/completeness checks, not building or occupancy certification.')
(Q/'FINAL_VERIFICATION.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k!='images'},indent=2))
