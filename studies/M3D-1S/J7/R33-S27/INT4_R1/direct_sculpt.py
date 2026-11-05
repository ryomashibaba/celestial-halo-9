"""HALO9 INT4 R1 — evidence-led direct native mesh surgery on the SAME INT4 scene.
Addresses actual source-image visual failures, not retouched camera images:
NAVE original camera was obstructed by two public paths, H1 by a W0→H1
transit route and the crossing. Geometry is reshaped, not hidden in render.
The original 3 camera matrices, scene, lighting and context are untouched.
"""
import bpy,sys,hashlib,json,math
from mathutils import Vector
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=Path(args[args.index('--output')+1]);out.mkdir(parents=True,exist_ok=True)
(out/'renders').mkdir(exist_ok=True)
source=Path(bpy.data.filepath)
EXPECTED='c71dbe46f7fda20aee6d1355720fc76b5c64d6c0a4ccf0b8bbaa0e210d2fff41'
assert source.name=='INT4_R1_SOURCE.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()==EXPECTED
scene=bpy.context.scene
assert scene['CONSTRUCTION']=='HOLD' and scene['COMPLETED_TARGETS']==0 and scene['FORMAL_ART_ACCEPTED']==0
cameras=('E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL')
fixed={name:bpy.data.objects[name].matrix_world.copy() for name in cameras}
deps=bpy.context.evaluated_depsgraph_get()

def view_hit(name):
    c=bpy.data.objects[name]
    pos=c.matrix_world.translation
    direction=c.matrix_world.to_quaternion()@Vector((0,0,-1))
    hit,point,normal,idx,target,mx=scene.ray_cast(deps,pos,direction,distance=5000)
    return {'object':target.name if hit else 'SKY',
            'distance':round((point-pos).length,3) if hit else None,
            'location':[round(v,3) for v in point] if hit else None}

before={name:view_hit(name) for name in cameras}
assert before['E11_NAVE_HUMAN']['object']=='INT4_W0_PORT_NAVE_WALK',before
assert before['E11_H1_HUMAN']['object']=='INT4_W0_NAVE_H1_LIVING_TRANSIT',before
assert before['E11_NAVE_HUMAN']['distance']<10 and before['E11_H1_HUMAN']['distance']<15
print('INT4_R1_REAL_BEFORE_RAYCAST',before,flush=True)

def reshape_road(name,drop_by_node):
    o=bpy.data.objects['INT4_'+name]
    assert o.type=='MESH'
    assert len(o.data.vertices)%4==0
    n=len(o.data.vertices)//4
    assert max(drop_by_node)<n,(name,n)
    for idx,delta in drop_by_node.items():
        for v in o.data.vertices[idx*4:(idx+1)*4]:
            v.co.z-=delta
    o.data.update()
    return {'object':o.name,'nodes':n,'depressed_nodes_m':drop_by_node}

changes=[]
# W0 walkway must approach the NAVE under (not through) the fixed human eye.
# Keep both meaningful public entry and its W0 source; only the near-end crest
# is resculpted to follow the public plaza floor.
changes.append(reshape_road('W0_PORT_NAVE_WALK',{2:17.0,3:20.0}))
# This second NAVE public spine is brought below the original head height,
# not hidden in render and not moved to an arbitrary invisible layer.
changes.append(reshape_road('NAVE_PUBLIC_CIVIC_CROSS',{0:9.0,1:7.0}))
# The W0 -> H1 transit was modeled over the H1 camera at +6m elevation:
# its real terminal geometry is lowered to the adjacent landscape level.
changes.append(reshape_road('W0_NAVE_H1_LIVING_TRANSIT',{4:16.0}))
# A true H1 public street now begins at street elevation below the eye,
# continuing uphill as a distinct multi-altitude exterior promenade.
changes.append(reshape_road('H1_PUBLIC_BOULEVARD',{0:13.0,1:7.0}))
# Lower the underlying massive pedestrian crossing slab as a substructure.
# It was an opaque roof ABOVE the protected human eye, not a useful street.
cross=bpy.data.objects['INT4_H1_URBAN_MAIN_PEDESTRIAN_CROSSING']
assert cross.type=='MESH' and len(cross.data.vertices)==12
for vert in cross.data.vertices:vert.co.z-=18.0
cross.data.update()
changes.append({'object':cross.name,'actual_mesh_vertex_count':12,
                'vertical_recess_m':18.0})

# Both programmes must have a readable spatial target beyond the immediate
# pedestrian approach. Add only one NAVE library balcony (actual new geometry)
# and one H1 market landfall (actual enclosed solid), not thousands of windows.
palette={}
for key,color in (
 ('warm_stone',(.66,.55,.43)),('deep_glass',(.10,.31,.35))):
    mat=bpy.data.materials.new('INT4_R1_'+key);mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Roughness'].default_value=.7
    palette[key]=mat
coll=bpy.data.collections.new('INT4_R1_DIRECT_PUBLIC_ACCESS_AND_ROOM')
scene.collection.children.link(coll)
def solid(name,poly,bot,top,mat):
    n=len(poly)
    v=[(x,y,bot) for x,y in poly]+[(x,y,top) for x,y in poly]
    f=[tuple(reversed(range(n))),tuple(range(n,n*2))]
    f.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
    me=bpy.data.meshes.new('INT4_R1_'+name);me.from_pydata(v,[],f);me.update()
    ob=bpy.data.objects.new('INT4_R1_'+name,me)
    coll.objects.link(ob);me.materials.append(palette[mat])
    return ob
# Use exposed civic walls as an alternative to a giant featureless roof.
solid('NAVE_PUBLIC_LIBRARY_SECOND_LEVEL',[
 (-373,-209),(-290,-269),(-219,-213),(-199,-155),(-277,-98),(-355,-128)
],183,195,'warm_stone')
solid('H1_MARKET_MEZZANINE_LANDING',[
 (511,378),(586,344),(677,386),(694,467),
 (590,485),(497,449)],549,559,'warm_stone')
# One protected open-to-sky crossing over the diagonal scar. Does not occlude
# camera entrance: all new faces sit >175m away horizontally.
solid('NAVE_SECOND_LEVEL_PUBLIC_READING_VOID_EDGE',[
 (-251,25),(-186,58),(-193,124),(-264,99)
],264,273,'deep_glass')

bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
after={name:view_hit(name) for name in cameras}
print('INT4_R1_REAL_AFTER_RAYCAST',after,flush=True)
assert after['E11_NAVE_HUMAN']['distance'] is None or after['E11_NAVE_HUMAN']['distance']>22,after
assert after['E11_H1_HUMAN']['distance'] is None or after['E11_H1_HUMAN']['distance']>22,after
for name,m in fixed.items():
    now=bpy.data.objects[name].matrix_world
    assert max(abs(now[i][j]-m[i][j]) for i in range(4) for j in range(4))<1e-6
scene['INT4_R1_PARENT_SHA256']=EXPECTED
scene['INT4_R1_CARVED']='PHYSICAL_MAIN_WALKWAY_AND_LANDSCAPE_ACCESS_GEOMETRY_NOT_CAMERA_TRICK'
scene['CONSTRUCTION']='HOLD';scene['FORMAL_ART_ACCEPTED']=0;scene['COMPLETED_TARGETS']=0
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=20
scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED';scene.render.threads=2
scene.render.resolution_x=1100;scene.render.resolution_y=825
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
dst=out/'HALO9_INT4_R1_SCULPTED_VIEW_AND_PUBLIC_ACCESS.blend'
scene.camera=bpy.data.objects[cameras[-1]]
bpy.ops.wm.save_as_mainfile(filepath=str(dst),compress=True)
render_hashes={}
for name in cameras:
    scene.camera=bpy.data.objects[name]
    path=out/'renders'/(name+'.png')
    scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
    assert path.exists() and path.stat().st_size>5000
    render_hashes[name]=hashlib.sha256(path.read_bytes()).hexdigest()
    print('INT4_R1_TRUE_IMAGE',name,path.stat().st_size,flush=True)
scene.camera=bpy.data.objects[cameras[-1]]
bpy.ops.wm.save_as_mainfile(filepath=str(dst),compress=True)
report={'schema':'halo9-int4-r1-protected-human-view-sculpt-v1',
 'source_sha256':EXPECTED,'blend_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),
 'surgical_geometry_changes':changes,
 'original_camera_raycast':before,'revised_camera_raycast':after,
 'native_render_sha256':render_hashes,'cameras_unchanged':True,
 'function':'UNKNOWN_NOT_INDEPENDENTLY_PROVEN',
 'art':'UNREVIEWED_NOT_ADOPTED',
 'formal_art_adopted':0,'completed_targets':0,
 'minecraft_construction':'HOLD','coordinates':'UNREGISTERED_RESEARCH_METRES'}
(out/'INT4_R1_NATIVE_REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('INT4_R1_SAME_NATIVE_SCENE_REVISED',report['blend_sha256'],flush=True)
