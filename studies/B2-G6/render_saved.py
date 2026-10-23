"""Render additional cameras from the saved selected BLEND, never rebuild geometry."""
import bpy,bmesh,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;O=R/'selected'
bpy.ops.wm.open_mainfile(filepath=str(O/'study.blend'))
S=bpy.context.scene
m=json.loads((O/'manifest.json').read_text(encoding='utf-8'))
arch=[o for o in S.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
def signature(obs):
    h=hashlib.sha256()
    for ob in sorted(obs,key=lambda q:q.name):
        h.update(ob.name.encode());h.update(str([list(r) for r in ob.matrix_world]).encode());h.update(str([tuple(v.co) for v in ob.data.vertices]).encode());h.update(str([tuple(p.vertices) for p in ob.data.polygons]).encode())
    return h.hexdigest()
bpy.context.view_layer.update();assert signature(arch)==m['geometry_sha256']
views=sys.argv[sys.argv.index('--')+1].split(',')
for n in views:
    backup={}
    if n=='09_SECTION':
        for ob in arch:
            backup[ob]=ob.data;ob.data=ob.data.copy();bm=bmesh.new();bm.from_mesh(ob.data)
            inv=ob.matrix_world.inverted();pp=inv@Vector((0,0,0));normal=ob.matrix_world.to_3x3().transposed()@Vector((1,0,0))
            bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.001,plane_co=pp,plane_no=normal,clear_outer=True,clear_inner=False)
            bm.to_mesh(ob.data);bm.free()
    S.camera=bpy.data.objects[n];S.render.filepath=str(O/(n+'.png'));bpy.ops.render.render(write_still=True)
    for ob,me in backup.items():tmp=ob.data;ob.data=me;bpy.data.meshes.remove(tmp)
    bpy.context.view_layer.update();assert signature(arch)==m['geometry_sha256']
    m['renders']=[v for v in m['renders'] if v['camera']!=n]
    m['renders'].append({'camera':n,'path':n+'.png','source_geometry_sha256':m['geometry_sha256'],'section_derived':n=='09_SECTION'})
    (O/'manifest.json').write_text(json.dumps(m,indent=2),encoding='utf-8')
print('SAVED MODEL RENDERS COMPLETE',views)
