"""HALO9 E5 conditional R1 direct-edit of REAL R0B .blend (NOT RUN / NOT ART PASS).
Requires genuine R0B human-view review before production use.
This repositions obstructing NAVE civic forum inside the west urban bank.
Research coordinates only. Does not touch E2/E3/main/Minecraft.
"""

# R1_RELOCATION_SAFETY_HOLD: source-derived geometry predicts severe collisions after x=-214m.
# The original proposed edit is preserved in repository history, but execution is prohibited
# until a genuinely reviewed Blender image and a collision-free spatial redesign exist.
raise RuntimeError('R1_RELOCATION_SAFETY_HOLD: forum shift -214m overlaps existing NAVE west substructure and public galleries; do not execute original proposal.')

import bpy, sys, json, hashlib
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
def param(k):
    if k not in args or args.index(k)+1>=len(args): raise RuntimeError(k+' required')
    return args[args.index(k)+1]
if '--native-images-reviewed' not in args:
    raise RuntimeError('Inspect genuine R0B human-view PNGs first; proxy previews are NOT a substitute')
src=Path(param('--source')).resolve(strict=True)
dest=Path(param('--output')).resolve()
assert src.name=='E4_R0B_WORKING.blend', 'Unexpected input native source'
assert dest!=src.parent
assert not dest.exists() or not any(dest.iterdir()), 'Output must be empty'
h0=hashlib.sha256(src.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(src))
sc=bpy.context.scene
assert sc.get('stage')=='R4_E4_R0B_SECTION_REWORK_UNREVIEWED'
assert sc.get('minecraft_write')=='FORBIDDEN'
assert sc.get('formal_adoption') is False
assert sc.get('official_coordinates_verified') is False
names=('human_sky_district','human_public_interior')
cams={n:tuple(tuple(float(v) for v in r) for r in bpy.data.objects[n].matrix_world) for n in names}
col=bpy.data.collections['NAVE_INHABITED_PUBLIC_ROOM']
changed=[]
for ob in col.objects:
    if ob.type=='MESH' and ob.name.startswith('NAVE_NORTH_CIVIC_FORUM_'):
        before=tuple(float(x) for x in ob.location)
        ob.location.x -= 214.0
        changed.append({'name':ob.name,'before':before,'after':tuple(float(x) for x in ob.location)})
assert len(changed)>=5, 'Unexpected forum geometry, refusing edit'
bpy.context.view_layer.update()
assert cams=={n:tuple(tuple(float(v) for v in r) for r in bpy.data.objects[n].matrix_world) for n in names}
dest.mkdir(parents=True,exist_ok=True)
(dest/'renders').mkdir(exist_ok=False)
sc['stage']='R4_E5_R1_DIRECT_EDIT_ART_UNREVIEWED'
sc['art']='NOT_REVIEWED'
sc['r1_change']='NAVE_CIVIC_FORUM_WEST_BANK_RELOCATION'
outblend=dest/'E5_R1_DIRECT_EDIT.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(outblend),compress=True)
for name in names:
    sc.camera=bpy.data.objects[name]
    sc.render.filepath=str(dest/'renders'/(name+'.png'))
    bpy.ops.render.render(write_still=True)
h1=hashlib.sha256(src.read_bytes()).hexdigest()
assert h0==h1, 'Original native scene modified unexpectedly'
render_names=[p.name for p in sorted((dest/'renders').glob('*.png'))]
assert len(render_names)==2
report={'schema':'halo9-e5-r1-direct-edit-v1','input_blend':src.name,
        'input_sha256_before_after':[h0,h1],
        'output_blend':outblend.name,'out_blend_sha256':hashlib.sha256(outblend.read_bytes()).hexdigest(),
        'existing_meshes_repositioned':changed,'fixed_camera_matrices_preserved':True,
        'render_files':render_names,'render_engine':sc.render.engine,
        'visual_jury':'PENDING_NATIVE_IMAGES','art_pass':False,'formal_adoption':False,
        'minecraft':'HOLD','city_master_complete':False,'official_coordinates_verified':False}
(dest/'R1_EDIT_REPORT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('HALO9_R1_NATIVE_DIRECT_EDIT_COMPLETED_BUT_ART_PENDING')
