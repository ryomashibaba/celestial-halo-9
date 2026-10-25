"""Minimal saved-geometry check after ART REJECT. Background Blender, no source writes."""
import bpy, sys, json, math
from pathlib import Path
from mathutils import Vector, kdtree
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent

def capture():
    verts=[];centers=[];count=0;groups={}
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        count+=1;m=o.data;m.calc_loop_triangles()
        vs=[o.matrix_world@v.co for v in m.vertices]
        assert all(math.isfinite(v) for p in vs for v in p)
        verts.extend(vs)
        centers.extend((vs[t.vertices[0]]+vs[t.vertices[1]]+vs[t.vertices[2]])/3 for t in m.loop_triangles)
        group=o.get('study_group','glTF imported')
        groups.setdefault(group,[]).extend(vs)
    def bounds(vs):
        lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)]
        return {'min_m':lo,'max_m':hi,'dimensions_m':[hi[i]-lo[i] for i in range(3)]}
    return verts,centers,{'meshes':count,'vertices':len(verts),'triangles':len(centers),**bounds(verts),
                         'group_bounds':{k:bounds(v) for k,v in groups.items()}}

def max_nearest(a,b):
    kd=kdtree.KDTree(len(b))
    for i,p in enumerate(b):kd.insert(p,i)
    kd.balance()
    return max(kd.find(p)[2] for p in a)

bpy.ops.wm.open_mainfile(filepath=str(R/'model/R27B_LIVING_HORIZONS.blend'))
bpy.context.view_layer.update()
av,ac,a=capture();floor=[]
for row in json.loads((R/'qa/CAMERAS.json').read_text(encoding='utf8')):
    if not row['floor_claim']:continue
    p=bpy.data.objects[row['name']].location
    hit,loc,n,f,o,m=bpy.context.scene.ray_cast(bpy.context.evaluated_depsgraph_get(),p,Vector((0,0,-1)),distance=5)
    assert hit and o.name==row['hit_object'] and abs(p.z-loc.z-1.7)<.01
    floor.append({'camera':row['name'],'support':o.name,'eye_above_floor_m':p.z-loc.z})
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(R/'model/R27B_LIVING_HORIZONS.glb'))
bpy.context.view_layer.update();bv,bc,b=capture()
errors={'blend_to_glb_vertices_m':max_nearest(av,bv),'glb_to_blend_vertices_m':max_nearest(bv,av),
        'blend_to_glb_triangle_centers_m':max_nearest(ac,bc),'glb_to_blend_triangle_centers_m':max_nearest(bc,ac)}
box_error=max(abs(a[k][i]-b[k][i]) for k in ['min_m','max_m'] for i in range(3))
ok=a['meshes']==b['meshes'] and a['triangles']==b['triangles'] and max(errors.values())<.01 and box_error<.01
out={'geometry_readback_pass':ok,'saved_blend':a,'reimported_glb':b,'max_boundary_error_m':box_error,
     'nearest_geometry_errors':errors,'tolerance_m':.01,'saved_floor_recheck':floor,
     'scope':'Both saved files independently loaded. All vertices and triangle centers checked bidirectionally. Not exact topology identity or collision QA.',
     'not_verified':['global intersections','structural integrity','enclosed public volumes','continuous pedestrian routes','rail slopes and vehicle operation','official W0/H/SB/axis/V registration','Minecraft conversion'],
     'art_judgment':'REJECT regardless of this technical result','heavy_QA_or_stage_D':False}
(R/'qa/SAVED_GEOMETRY_CHECK.json').write_text(json.dumps(out,indent=2),encoding='utf8')
assert ok,out
print('SAVED_GEOMETRY_CHECK_PASS',a['dimensions_m'],errors,flush=True)
