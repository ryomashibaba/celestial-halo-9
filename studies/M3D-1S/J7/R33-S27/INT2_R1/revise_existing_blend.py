"""INT2-R1: direct substantive revision of the existing INT2 native BLEND.
No camera pose change. Remove camera-burying architectural volumes by carving
usable, multi-program urban caverns; expose inhabited mass to the aerial view.
One authoring revision, not formal art adoption and not a new proposal.
"""
import bpy, sys, math, json, hashlib
from mathutils import Vector
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=Path(args[args.index('--output')+1]);out.mkdir(parents=True,exist_ok=True)
(out/'renders').mkdir(exist_ok=True)
src=Path(bpy.data.filepath)
SOURCE_SHA='51615c6cda162a14bf141ce4c90e98d2a0c14a4aafcb6d52fcacf57fb4cbd954'
assert src.name=='INT2_R1_SOURCE.blend'
assert hashlib.sha256(src.read_bytes()).hexdigest()==SOURCE_SHA
s=bpy.context.scene
assert s['CONSTRUCTION']=='HOLD' and s['COMPLETED_TARGETS']==0 and s['FORMAL_ART_ACCEPTED']==0
names=('E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL')
cameras={n:bpy.data.objects[n].matrix_world.copy() for n in names}
west=bpy.data.objects['INT2_M247_ALPHA_WEST_LIVED_FAULT_CORE']
east=bpy.data.objects['INT2_M247_ALPHA_EAST_DISPLACED_FAULT_CORE']
assert west.type==east.type=='MESH'
coll=bpy.data.collections.new('INT2_R1_ACTUAL_SCULPTED_PUBLIC_CAVITY_RESEARCH')
s.collection.children.link(coll)
materials={}
for n,rgb,metal in (
    ('sunk_limestone',(.63,.58,.49),.12),
    ('inset_ochre',(.51,.42,.32),.40),
    ('interior_ivory',(.83,.77,.65),.08),
    ('civic_azure',(.10,.40,.47),.42),
    ('civic_dark',(.13,.19,.19),.30),
    ('vegetation',(.18,.35,.25),.03)):
    m=bpy.data.materials.new('INT2_R1_'+n);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Metallic'].default_value=metal
    p.inputs['Roughness'].default_value=.63
    materials[n]=m
count=0
def geom(name,vertices,faces,mat):
    global count
    md=bpy.data.meshes.new('INT2_R1_'+name)
    md.from_pydata(vertices,[],faces);md.update()
    ob=bpy.data.objects.new('INT2_R1_'+name,md);coll.objects.link(ob)
    md.materials.append(materials[mat]);count+=1
    return ob

def polygon(name,pts,z,thickness,mat):
    n=len(pts);assert n>=3
    vs=[(x,y,z-thickness) for x,y in pts]+[(x,y,z) for x,y in pts]
    fs=[tuple(reversed(range(n))),tuple(range(n,n*2))]
    fs.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
    return geom(name,vs,fs,mat)

def ramp(name,pts,width,depth,mat):
    verts=[]
    for i,p in enumerate(pts):
        a=Vector(pts[max(0,i-1)]);b=Vector(pts[min(len(pts)-1,i+1)])
        d=b-a;ln=math.hypot(d.x,d.y)
        nx,ny=((-d.y/ln,d.x/ln) if ln>1e-5 else (1,0))
        x,y,z=p
        verts.extend(((x+nx*width/2,y+ny*width/2,z-depth),
          (x-nx*width/2,y-ny*width/2,z-depth),
          (x+nx*width/2,y+ny*width/2,z),
          (x-nx*width/2,y-ny*width/2,z)))
    faces=[(0,2,3,1),tuple(range(len(verts)-4,len(verts)))]
    for i in range(len(pts)-1):
        a=4*i;b=a+4
        faces.extend(((a,a+1,b+1,b),(a+2,b+2,b+3,a+3),
          (a,a+2,b+2,b),(a+1,b+1,b+3,a+3)))
    return geom(name,verts,faces,mat)

def cut(target,label,location,radii):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=14,location=location)
    obj=bpy.context.object;obj.name='INT2_R1_TEMP_'+label;obj.scale=radii
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bpy.ops.object.select_all(action='DESELECT')
    target.select_set(True);bpy.context.view_layer.objects.active=target
    m=target.modifiers.new('INT2_R1_'+label,'BOOLEAN')
    m.operation='DIFFERENCE';m.solver='EXACT';m.object=obj
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(obj,do_unlink=True)
    return len(target.data.polygons)

# Real camera coordinates and world-facing directions determine excavation
# entrances, not changed camera placement or a render-only scene override.
camera_geom={}
for n in names:
    c=bpy.data.objects[n]
    pos=c.matrix_world.translation
    front=c.matrix_world.to_quaternion()@Vector((0,0,-1))
    camera_geom[n]={'location':[round(v,3) for v in pos],
                    'forward':[round(v,4) for v in front]}
    print('INT2_R1_ORIGINAL_CAMERA',n,camera_geom[n],flush=True)

# Repair the observed image-invalid human views with real contiguous
# architecturally large holes in both civic cores. Each interlocking
# excavation is a continuous inhabitable promenade (not a fake lens mask).
cuts={}
for prefix,n in (('NAVE','E11_NAVE_HUMAN'),('H1','E11_H1_HUMAN')):
    cam=bpy.data.objects[n];origin=cam.matrix_world.translation
    view=cam.matrix_world.to_quaternion()@Vector((0,0,-1))
    for j,(step,radii) in enumerate(((0,(165,178,162)),
                                     (160,(196,205,166)),
                                     (362,(224,233,180)),
                                     (566,(248,259,190)))):
        location=origin+view*step
        for side,ob in (('WEST',west),('EAST',east)):
            cuts[prefix+'_'+side+'_'+str(j)]=cut(
                 ob,prefix+'_'+side+'_'+str(j),location,radii)
    # Carving a corridor is useless if the camera is still buried in
    # an unrelated raised forum floor. Lower only the studied forum floor,
    # when its vertical extent actually intersects this protected viewpoint.
    if prefix=='NAVE':
        floor=bpy.data.objects['INT2_NAVE_MAIN_FORUM']
        a,b=sorted(v.co.z for v in floor.data.vertices)[::len(floor.data.vertices)-1]
        zcam=origin.z
        if a-1<=zcam<=b+2:
            correction=b-(zcam-1.75)
            for vertex in floor.data.vertices:vertex.co.z-=correction
            floor.data.update()
            print('INT2_R1_FORUM_FLOOR_RESCULPT',correction,flush=True)

# Replace two blank cliff faces with city-scale mouths facing the actual
# original aerial camera. Their different levels and shapes reveal
# inhabited urban anatomy rather than painting windows onto white rock.
aerial=bpy.data.objects['E11_URBAN_AERIAL'].matrix_world.translation
facade_areas=(
 ('WEST_LOWER',west,(-496,-132,462),294,(240,224,143)),
 ('WEST_UPPER',west,(-677,115,828),270,(229,212,151)),
 ('EAST_LOWER',east,(655,-68,531),309,(257,252,155)),
 ('EAST_UPPER',east,(836,290,957),276,(244,227,157)),
)
for tag,ob,(cx,cy,z),distance,radii in facade_areas:
    toward=Vector((aerial.x-cx,aerial.y-cy,0))
    if toward.length<.001:toward=Vector((0,-1,0))
    toward.normalize()
    mouth=Vector((cx,cy,z))+toward*distance
    cuts['FACET_'+tag]=cut(ob,'VISIBLE_CITY_'+tag,mouth,radii)
    # Public urban floor actually occupies the newly eroded volume.
    direction=Vector((-toward.y,toward.x,0))
    center=mouth-toward*34
    footprint=[]
    for angle in range(8):
        t=math.tau*angle/8
        r=105+(20 if angle%3==0 else -5)
        p=center+direction*math.cos(t)*r+toward*math.sin(t)*r
        footprint.append((p.x,p.y))
    polygon('CITY_VISIBLE_FACET_'+tag,footprint,z-34,12,'interior_ivory')
    # Divergent public circulation inside the same excavated body.
    p1=center-toward*98; p1.z=z-30
    p2=center+toward*37+direction*45; p2.z=z-12
    p3=center+toward*84+direction*102; p3.z=z+22
    ramp('CITY_FACET_ASYMMETRIC_PUBLIC_ROUTE_'+tag,
         [tuple(p1),tuple(p2),tuple(p3)],18,7,'inset_ochre')
    # Single local roof garden in the hollowed interior, not city-wide shelf.
    g=center+direction*33+toward*23
    polygon('CITY_FACET_GARDEN_'+tag,[
      (g.x-34,g.y-23),(g.x+27,g.y-31),
      (g.x+45,g.y+10),(g.x-20,g.y+33)],z-13,7,'vegetation')

# Reshape the *same existing* two massive mesh objects: break their smooth
# terminal rock silhouettes into chiral, bifurcating inhabited cliff crests.
# A large-scale change to stored vertices, not an added paint/material.
for target,origin_x,strength,phase in (
    (west,-620,-1,.15),(east,1050,1,1.05)):
    for v in target.data.vertices:
        z=v.co.z
        if z<730:continue
        a=math.atan2(v.co.y-160,v.co.x-origin_x)
        ratio=min(1,max(0,(z-730)/650))
        # High-level translated civic strata and fissured crest.
        v.co.x+=strength*ratio*ratio*(70+49*math.sin(2*a+phase))
        v.co.y+=ratio*ratio*(47*math.sin(3*a+phase))
        v.co.z+=ratio*(33*math.sin(4*a+phase)+19*math.cos(7*a))
    target.data.update()

# Inhabited elevated public crossings tie the carved chambers back to the
# fissure and the W0 coast, instead of adding freestanding towers.
ramp('NAVE_VISIBLE_PUBLIC_READING_PROMENADE',[
 (-312,-201,186),(-217,-111,227),(-136,48,296),
 (-21,179,365)],24,10,'interior_ivory')
ramp('H1_VISIBLE_MARKET_TO_CROSSFAULT',[
 (751,289,445),(686,393,489),(564,474,598),
 (404,472,702)],24,11,'interior_ivory')
ramp('W0_VISIBLE_QUAY_TO_NAVE_SECTION',[
 (417,-575,52),(275,-555,64),(113,-468,76),
 (14,-338,93)],28,12,'interior_ivory')

# Actual light sources for the newly exposed interior city; old sunlight alone
# cannot illuminate a 300m-deep public volume.
for n in ('E11_NAVE_HUMAN','E11_H1_HUMAN'):
    c=bpy.data.objects[n];front=c.matrix_world.to_quaternion()@Vector((0,0,-1))
    point=c.matrix_world.translation+front*155+Vector((0,0,105))
    light=bpy.data.lights.new('INT2_R1_PUBLIC_INTERIOR_'+n,'POINT')
    light.energy=1600000;light.shadow_soft_size=100
    ob=bpy.data.objects.new(light.name,light)
    coll.objects.link(ob);ob.location=point

bpy.context.view_layer.update()
for n,m in cameras.items():
    matrix=bpy.data.objects[n].matrix_world
    assert max(abs(matrix[i][j]-m[i][j]) for i in range(4) for j in range(4))<1e-6
s['INT2_R1_SOURCE_SHA256']=SOURCE_SHA
s['INT2_R1_EDITS']='SAME_EXISTING_BLENDER_SCENE_CORES_CARVED_AND_RESCULPTED'
s['INT2_R1_NEW_MESHES']=count;s['INT2_R1_TRUE_BOOLEAN_CUTS']=len(cuts)
s['FORMAL_ART_ACCEPTED']=0;s['COMPLETED_TARGETS']=0;s['CONSTRUCTION']='HOLD'
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=16
s.cycles.use_denoising=True
s.render.threads_mode='FIXED';s.render.threads=2
s.render.resolution_x=1100;s.render.resolution_y=825
s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'
dest=out/'HALO9_INT2_R1_DIRECT_SCULPTED.blend'
s.camera=bpy.data.objects[names[-1]]
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
renders={}
for n in names:
    s.camera=bpy.data.objects[n]
    path=out/'renders'/(n+'.png')
    s.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    assert path.exists() and path.stat().st_size>5000
    renders[n]=hashlib.sha256(path.read_bytes()).hexdigest()
    print('INT2_R1_REAL_RENDER',n,path.stat().st_size,flush=True)
s.camera=bpy.data.objects[names[-1]]
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
report={
 'schema':'HALO9-INT2-R1-DIRECT-SAVED-BLEND-REVISION',
 'status':'TECH_PENDING_INDEPENDENT_REOPEN',
 'source_sha256':SOURCE_SHA,
 'render_hashes':renders,
 'camera_positions':camera_geom,
 'saved_blend_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
 'boolean_cut_mesh_polygons':cuts,
 'new_civic_objects':count,
 'unchanged_three_camera_matrices':True,
 'function':'UNKNOWN_NO_INDEPENDENT_PEDESTRIAN_SWEEP',
 'formal_art_adopted':0,'completed_targets':0,'minecraft':'HOLD',
 'art':'UNREVIEWED_AWAITING_IMAGE_DIRECT_CHECK'}
(out/'INT2_R1_NATIVE_TECH.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('INT2_R1_REVISION_FINISHED',report['saved_blend_sha256'],flush=True)
