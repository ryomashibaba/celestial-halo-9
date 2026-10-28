"""Load the SAVED base; edit existing mesh vertices after visual review.
No regeneration, object replacement, primitive operators or protected asset access.
"""
import bpy,json,sys,hashlib,re
from pathlib import Path

OUT=Path(sys.argv[sys.argv.index('--')+1]).resolve()
assert Path(bpy.data.filepath).name=='D10_BASE.blend'
assert not (OUT/'D10_EDIT.blend').exists(), 'Use a fresh output copy; do not overwrite edited baseline.'
scene=bpy.context.scene
def snapshot():
    result={'blender':bpy.app.version_string,'objects':{},'cameras':{}}
    for ob in scene.objects:
        if ob.type=='CAMERA':result['cameras'][ob.name]={'matrix':[list(row) for row in ob.matrix_world],'lens':ob.data.lens,'type':ob.data.type,'ortho_scale':ob.data.ortho_scale}
        if ob.type!='MESH':continue
        result['objects'][ob.name]={'vertices':[list(ob.matrix_world@v.co) for v in ob.data.vertices],
            'faces':[list(p.vertices) for p in ob.data.polygons],
            'bindings':[v.index for v in ob.data.vertices if any(g.group==ob.vertex_groups.get('CIVIC_EAST_EDGE').index and g.weight>0 for g in v.groups)] if ob.vertex_groups.get('CIVIC_EAST_EDGE') else []}
    return result
def export(stage):
    options=bpy.ops.export_scene.gltf.get_rna_type().properties['export_format'].enum_items
    # This Blender exporter uses dynamic enum items; RNA reports an empty set.
    # Its live operator signature supplies the actual default identifier.
    fmt=next((x.identifier for x in options if x.identifier=='GLB'),None)
    if fmt is None:fmt=re.search(r"export_format='([^']+)'",bpy.ops.export_scene.gltf.__doc__).group(1)
    bpy.ops.export_scene.gltf(filepath=str(OUT/('D10_'+stage+'.glb')),export_format=fmt,export_cameras=False,export_lights=False)
before=snapshot()
(OUT/'BASE_snapshot.json').write_text(json.dumps(before,indent=2),encoding='utf-8')
export('BASE')
log=[]
for ob in scene.objects:
    if ob.type!='MESH':continue
    group=ob.vertex_groups.get('CIVIC_EAST_EDGE')
    if not group:continue
    for v in ob.data.vertices:
        if any(g.group==group.index and g.weight>0 for g in v.groups):
            old=list(v.co);v.co.x+=28
            log.append({'object':ob.name,'vertex':v.index,'before':old,'after':list(v.co),'reason':'public-floor/exterior boundary coupled edit +28m X'})
    ob.data.update()

# One art-diagnostic contour edit motivated by the observed blank rear wall.
# It does NOT establish art improvement or public accessibility.
rear=bpy.data.objects['REAR_OBLIQUE_HABITAT']
for index,rise in [(4,35),(5,45),(6,35)]:
    v=rear.data.vertices[index];old=list(v.co);v.co.z+=rise
    log.append({'object':rear.name,'vertex':index,'before':old,'after':list(v.co),'reason':'one diagnostic rear underside contour edit after baseline image review'})
rear.data.update()
scene['art_status']='ART REJECT - diagnostic edit only, not a finished architectural candidate'
scene['direct_edit']='Existing vertex coordinates changed; face topology and object IDs preserved.'
after=snapshot()
assert before['cameras']==after['cameras']
assert set(before['objects'])==set(after['objects'])
for name in before['objects']:assert before['objects'][name]['faces']==after['objects'][name]['faces']
(OUT/'EDIT_expected_snapshot.json').write_text(json.dumps(after,indent=2),encoding='utf-8')
(OUT/'DIRECT_EDIT_LOG.json').write_text(json.dumps(log,indent=2),encoding='utf-8')
prefs=bpy.context.preferences.filepaths
if hasattr(prefs,'use_save_preview'):prefs.use_save_preview=False
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'D10_EDIT.blend'),compress=True)
export('EDIT')
print('D10_EDIT_DONE',json.dumps({'changed_vertices':len(log),'changed_objects':sorted(set(x['object'] for x in log))}))
