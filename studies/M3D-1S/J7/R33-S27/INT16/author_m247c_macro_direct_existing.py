"""INT16: visually selected direct macro-mesh reconstruction, *not* art acceptance.

Starts from verified INT15 real Blender COPY. The INT15 aerial clearly showed two
undifferentiated oval solids, so this experiment EDITS existing INT11 alpha meshes
at a handful of explicit sculpt anchors and excavates four nonrepeated, author-
specified civic escarpment volumes. No new megashell, city façade or generic tower.
The fixed E11 cameras, W0 geometry, non-approval state remain untouched.
This is Blender scripting/direct vertex manipulation, NOT GUI hand-sculpting.
"""
import bpy, hashlib, json, math, sys
from pathlib import Path
from mathutils import Vector

argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=Path(argv[argv.index('--output')+1]);out.mkdir(parents=True,exist_ok=True)
(out/'renders').mkdir(exist_ok=True)
source=Path(bpy.data.filepath)
PARENT='e996fab613904dc557638612d4380ba67ef5c6bbd4aa9fb219d9aeaa8f511fb9'
assert source.name=='INT16_SOURCE.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()==PARENT
scene=bpy.context.scene
assert scene['CONSTRUCTION']=='HOLD'
assert scene['FORMAL_ART_ACCEPTED']==0 and scene['COMPLETED_TARGETS']==0
E11=('E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL')
W0=('W0_NORTH_FRACTURED_RANGE','W0_WEST_BASALT_ESCARPMENT',
    'W0_GROUND_BASIN','W0_EASTERN_ARTIFICIAL_SEA')
def vertex_digest(obj):
    h=hashlib.sha256()
    for v in obj.data.vertices:
        h.update((','.join(f'{float(c):.10g}' for c in v.co)+';').encode())
    return h.hexdigest()
w0={k:vertex_digest(bpy.data.objects[k]) for k in W0}
camera={k:bpy.data.objects[k].matrix_world.copy() for k in E11}
WEST='INT11_M247C_ALPHA_WEST_ACCRETED_ARCHIVE'
EAST='INT11_M247C_ALPHA_EAST_CIVIC_HIGH_CITY'
CROWN='INT11_M247C_ALPHA_FLOATING_SEVERED_NORTH'
SEAM='INT11_M247C_BETA_SLANTED_CIVIC_SEAM'
assert all(k in bpy.data.objects for k in (WEST,EAST,CROWN,SEAM))
assert all(bpy.data.objects[k].type=='MESH' for k in (WEST,EAST))
# Sculpt anchors are deliberately different. These are not a repeatable
# "generate a shell" rule: each field controls an observed part of the
# REJECTED eggs, displacing vertices of the existing REAL mesh.
anchors={
 WEST:[
  ((-1060,-310,760),(390,380,480),(135,205,-30)),
  ((-680,140,1390),(320,440,430),(-195,-85,145)),
  ((-1370,610,480),(270,400,370),(-70,-115,-100)),
  ((-340,960,940),(320,400,410),(115,105,65)),
 ],
 EAST:[
  ((890,-370,780),(470,470,570),(-155,240,-75)),
  ((1470,-170,1360),(390,420,450),(200,-165,95)),
  ((530,900,1520),(380,440,430),(-135,90,80)),
  ((1560,1120,520),(390,420,420),(90,100,-110)),
 ]}
sculpt=[]
for name,fields in anchors.items():
    obj=bpy.data.objects[name]
    inverse=obj.matrix_world.inverted()
    changed=0;maximum=0.0
    for v in obj.data.vertices:
        pos=obj.matrix_world@v.co
        shift=Vector((0.0,0.0,0.0))
        for center,radius,amplitude in fields:
            d=sum(((pos[i]-center[i])/radius[i])**2 for i in range(3))
            # Explicit local falloff with an 0.8 contour, no global ellipsoid retile.
            weight=math.exp(-2*d)
            if weight<0.005:continue
            shift+=Vector(amplitude)*weight
        if shift.length>1:
            v.co=inverse@(pos+shift)
            changed+=1;maximum=max(maximum,shift.length)
    obj.data.update()
    assert changed>=35,(name,'NO_PHYSICAL_SCULPT',changed)
    sculpt.append({'mesh':name,'vertices_directly_moved':changed,
                   'maximum_displacement_m':round(maximum,2),
                   'anchors':fields,'mesh_polygon_count':len(obj.data.polygons)})
    print('INT16_DIRECT_VERTEX_MESH_SCULPT',name,changed,maximum,flush=True)
# Closed, deliberately asymmetric front-facing voids authored as spatial
# X/Z drawings with finite Y depth. Each removes a distinct CIVIC INTERIOR
# from the existing solid (not a replacement shell nor camera-only masking).
cut_specs=[
 (WEST,'WEST_PUBLIC_LIBRARY_CANYON',
  [(-1470,270),(-920,250),(-600,390),(-440,600),
   (-580,940),(-950,1100),(-1360,970)],-1000,580),
 (EAST,'EAST_H1_EXPOSED_CIVIC_TERRACE',
  [(360,320),(1000,265),(1410,410),(1560,790),
   (1420,1110),(940,1280),(550,1130),(300,850)],-1050,720),
 (WEST,'WEST_SKY_READING_COURT',
  [(-1210,1120),(-740,1100),(-420,1400),
   (-630,1890),(-1190,1860),(-1480,1600)],-850,300),
 (EAST,'EAST_HIGH_CITY_BROKEN_CROWN',
  [(960,1430),(1280,1330),(1670,1570),
   (1780,1990),(1390,2260),(830,2140),(730,1750)],-850,440),
]
def polygon_area(poly):
    return sum(poly[i][0]*poly[(i+1)%len(poly)][1]-
               poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))/2
def negative_prism(name,profile,ymin,ymax):
    assert len(profile)>=5 and ymin<ymax
    if polygon_area(profile)<0:profile=list(reversed(profile))
    n=len(profile)
    v=[(x,ymin,z) for x,z in profile]+[(x,ymax,z) for x,z in profile]
    # In XZ planar coordinates CCW looks toward -Y.
    f=[tuple(range(n)),tuple(reversed(range(n,n*2)))]
    for i in range(n):
        j=(i+1)%n
        f.append((i,j,j+n,i+n))
    data=bpy.data.meshes.new('INT16_TEMP_'+name)
    data.from_pydata(v,[],f);data.update()
    obj=bpy.data.objects.new(data.name,data);scene.collection.objects.link(obj)
    return obj

cut_results=[]
for target,name,poly,ymin,ymax in cut_specs:
    ob=bpy.data.objects[target]
    prev=len(ob.data.polygons)
    cutter=negative_prism(name,poly,ymin,ymax)
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True);bpy.context.view_layer.objects.active=ob
    mod=ob.modifiers.new('INT16_'+name,'BOOLEAN')
    mod.object=cutter;mod.operation='DIFFERENCE';mod.solver='EXACT'
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True)
    current=len(ob.data.polygons)
    assert current>60 and all(math.isfinite(float(c)) for q in ob.data.vertices for c in q.co)
    cut_results.append({'name':name,'target':target,'faces_before':prev,
       'faces_after':current,'polygon':poly,'y_bounds':[ymin,ymax],
       'topology_changed':current!=prev})
    print('INT16_REAL_EXISTING_MESH_EXCAVATION',name,prev,current,flush=True)
assert sum(q['topology_changed'] for q in cut_results)>=3, 'CIVIC_VOID_EXPERIMENT_DID_NOT_CUT_SOURCE'
assert all(vertex_digest(bpy.data.objects[k])==v for k,v in w0.items()),'W0_MUTATED'
for k,pose in camera.items():
    q=bpy.data.objects[k].matrix_world
    assert max(abs(q[i][j]-pose[i][j]) for i in range(4) for j in range(4))<1e-6,'E11_CAMERA_CHANGED'
assert all(k in bpy.data.objects for k in (WEST,EAST,CROWN,SEAM))
assert scene['CONSTRUCTION']=='HOLD'
assert scene['FORMAL_ART_ACCEPTED']==scene['COMPLETED_TARGETS']==0

# New inspection view is ADDITIONAL, not a replacement for the E11 baseline.
data=bpy.data.cameras.new('INT16_ARCHITECTURAL_FRONT_EXTRA')
data.lens=35;data.clip_end=14000
extra=bpy.data.objects.new(data.name,data);scene.collection.objects.link(extra)
extra.location=(200,-3300,1350)
extra.rotation_euler=(Vector((100,550,920))-extra.location).to_track_quat('-Z','Y').to_euler()
scene['INT16_EXPERIMENT']='EXISTING_ALPHA_DIRECT_VERTEX_SCULPT_PLUS_ASYMMETRIC_CIVIC_EXCAVATION'
scene['INT16_METHOD']='SCRIPTED_NATIVE_MESH_EDIT_NOT_GUI_BRUSH'
scene['INT16_ART']='UNREVIEWED_NOT_ADOPTED'
scene['INT16_FUNCTION']='UNVERIFIED'
scene['INT16_WORLD_COORDINATES']='RESEARCH_ONLY'
scene.camera=bpy.data.objects['E11_URBAN_AERIAL']
blend=out/'HALO9_INT16_MACRO_CIVIC_SCARPS.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)

scene.render.engine='CYCLES'
scene.cycles.device='CPU';scene.cycles.samples=12
scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED';scene.render.threads=2
scene.render.resolution_x=900;scene.render.resolution_y=675
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
views=E11+('INT16_ARCHITECTURAL_FRONT_EXTRA',)
images={}
for k in views:
    scene.camera=bpy.data.objects[k]
    dst=out/'renders'/(k+'.png')
    scene.render.filepath=str(dst)
    bpy.ops.render.render(write_still=True)
    assert dst.stat().st_size>6000
    images[k]=hashlib.sha256(dst.read_bytes()).hexdigest()
    print('INT16_TRUE_UNMASKED_E11_AND_ADDITIONAL_RENDER',k,dst.stat().st_size,flush=True)
scene.camera=bpy.data.objects['E11_URBAN_AERIAL']
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
report={'status':'TECH_PROVISIONAL_NOT_ART','source':PARENT,
        'new_blend_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),
        'sculpt':sculpt,'voids':cut_results,'images':images,
        'e11_camera_original_matrices':{k:[[float(v) for v in row] for row in camera[k]] for k in E11},
        'protected_w0_sha256':w0,'no_cutaway':True,
        'formal_art_accepted':0,'completed_targets':0,
        'function':'UNVERIFIED','construction':'HOLD',
        'world_coordinates':'UNREGISTERED','visual_judgment':'REQUIRED'}
(out/'INT16_NATIVE_RESEARCH_EVIDENCE_NOT_ART.json').write_text(
    json.dumps(report,indent=2))
print('INT16_NATIVE_MACRO_DIRECT_EDIT_COMPLETE_NOT_ART',
      report['new_blend_sha256'],flush=True)
