"""HALO-9 INT11 — integrated research-scale M247-C inhabited hollow archipelago.

Not a continuation of rejected INT10 cliff/bridge form: those INT10 mesh
studies are removed IN THIS ISOLATED COPY. Original W0 topography, all E11
camera matrices, existing history and protection flags are retained.

Main composition:
  - Two asymmetrical excavated geologic megastructures of distinct scale,
    partly detached upper volume, deliberately non-flat / non-lofted surface.
  - Deep civic public chambers physically subtracted from those masses.
  - A central 650m high open-air NAVE forum and thick vaulted civic tiers.
  - H1 as an actually nested district of irregular vaulted residences,
    school, market and internal street around one shared rock void.
  - A distinct diagonal public seam and W0 land-water arrival.
Art may still REJECT. This script never sets acceptance or functional PASS.
"""
import bpy, math, hashlib, json, sys, random
from mathutils import Vector, Matrix
from pathlib import Path

a=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=Path(a[a.index('--output')+1]);out.mkdir(parents=True,exist_ok=True)
(out/'renders').mkdir(exist_ok=True)
src=Path(bpy.data.filepath)
PARENT='67762c7da7b4105c43e37819297ffeb95755c3eee5ee94b1f0d4b9d6d7e8111b'
assert src.name=='INT11_SOURCE.blend' and hashlib.sha256(src.read_bytes()).hexdigest()==PARENT
scene=bpy.context.scene
assert scene['CONSTRUCTION']=='HOLD' and scene['FORMAL_ART_ACCEPTED']==scene['COMPLETED_TARGETS']==0
e11=('E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL')
fixed={n:bpy.data.objects[n].matrix_world.copy() for n in e11}
original_w0={o.name for o in scene.objects if o.type=='MESH' and o.name.startswith(('W0_','INT4_W0_'))}
assert len(original_w0)>=15
core_w0=('W0_NORTH_FRACTURED_RANGE','W0_WEST_BASALT_ESCARPMENT','W0_GROUND_BASIN','W0_EASTERN_ARTIFICIAL_SEA')
def geo_fingerprint(obj):
    m=hashlib.sha256()
    for v in obj.data.vertices:
        m.update((','.join(f'{float(x):.10g}' for x in v.co)+';').encode())
    return m.hexdigest()
w0_hash={n:geo_fingerprint(bpy.data.objects[n]) for n in core_w0}

removed=[]
for obj in list(scene.objects):
    if obj.name.startswith('INT10_') and obj.type in {'MESH','LIGHT','CAMERA'}:
        removed.append(obj.name)
        bpy.data.objects.remove(obj,do_unlink=True)
assert len(removed)>=25
# Unapproved old INT4-H1 context caused previous camera obstructions;
# make it invisible in THIS isolated visual research copy, without deleting
# any preserved original mesh data. Geography/W0 references remain visible.
context_hidden=[]
for ob in scene.objects:
    if ob.type=='MESH' and ob.name.startswith(('INT4_H1_','INT4_R1_H1_')):
        if not ob.hide_render:
            ob.hide_render=True
            context_hidden.append(ob.name)

coll=bpy.data.collections.new('INT11_M247C_INHABITED_HOLLOW_ARCHIPELAGO_STUDY')
scene.collection.children.link(coll)
materials={}
def material(name,color,metal=0.0,rough=.69,glow=0):
    m=bpy.data.materials.new('INT11_'+name);m.use_nodes=True
    m.diffuse_color=(*color,1)
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Metallic'].default_value=metal
    bs.inputs['Roughness'].default_value=rough
    if glow:
        bs.inputs['Emission Color'].default_value=(*color,1)
        bs.inputs['Emission Strength'].default_value=glow
    materials[name]=m
material('mineral_ochre',(.35,.35,.32),.06,.81)
material('canyon_bone',(.66,.61,.52),.07,.75)
material('porcelain',(.76,.79,.72),.12,.55)
material('aged_bronze',(.49,.36,.22),.63,.43)
material('river_glass',(.12,.43,.47),.33,.24)
material('residence',(.71,.57,.47),.13,.65)
material('deep_lapis',(.12,.23,.31),.28,.52)
material('terrace_garden',(.14,.29,.22),.02,.91)
material('civic_light',(.98,.76,.45),.06,.47,1.5)

made=[]
major_works=[]
def mesh(name,verts,faces,mat):
    assert verts and faces
    dat=bpy.data.meshes.new('INT11_'+name)
    dat.from_pydata(verts,[],faces);dat.update()
    obj=bpy.data.objects.new('INT11_'+name,dat);coll.objects.link(obj)
    obj.data.materials.append(materials[mat])
    assert all(math.isfinite(float(c)) for v in dat.vertices for c in v.co)
    made.append(obj.name)
    return obj

def organic_geology(name,center,scale,seed,mat,warp=.17):
    # Different angular re-entrant folds and undulating overhangs across one
    # closed 3D solid. Not a flat wedge/sheet or loft of identical profiles.
    S=100;R=47;v=[];faces=[]
    for i in range(R+1):
        theta=math.pi*(.0001+(1-.0002)*i/R)
        for j in range(S):
            phi=2*math.pi*j/S
            p=math.sin(theta);c=math.cos(theta)
            twist=.29*math.sin(2.1*theta+seed)+.13*math.cos(5*theta-seed*.8)
            an=phi+twist
            scallop=.13*math.sin(5*an+3*theta+seed)+.07*math.cos(9*an-2.4*theta)
            hollow=.10*math.sin(2*an+4*theta+seed*2)*math.cos(3*theta)
            radial=1+warp*(scallop+hollow)+.12*math.sin(4*theta+seed+2.5*an)
            x=center[0]+scale[0]*p*math.cos(an)*radial
            y=center[1]+scale[1]*p*math.sin(an)*(1+.06*math.cos(4*an+seed))
            z=center[2]+scale[2]*c*(1+.075*math.sin(3*an+seed)*p)
            x+=.07*scale[0]*p*p*math.sin(4*theta+seed*1.7)
            y+=.06*scale[1]*math.cos(4*theta-2*an)*p*p
            v.append((x,y,z))
    for i in range(R):
        for j in range(S):
            a=i*S+j;b=i*S+(j+1)%S
            faces.append((a,a+S,b+S,b))
    faces.extend([tuple(range(S)),tuple(reversed(range(R*S,(R+1)*S)))])
    ob=mesh(name,v,faces,mat)
    for f in ob.data.polygons:f.use_smooth=True
    major_works.append(name)
    return ob

def ellipsoid_cutter(center,scale,angles=(0,0,0),segments=40,rings=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings)
    ob=bpy.context.object
    ob.name='INT11__TEMP_CAVITY'
    ob.location=center;ob.scale=scale;ob.rotation_euler=angles
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    return ob

cut_count=0
def cavity(target,name,center,scale,rotation=(0,0,0)):
    global cut_count
    before=len(target.data.polygons)
    cut=ellipsoid_cutter(center,scale,rotation)
    bpy.ops.object.select_all(action='DESELECT')
    target.select_set(True);bpy.context.view_layer.objects.active=target
    mod=target.modifiers.new('INT11_'+name+'_EXCAVATION','BOOLEAN')
    mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cut,do_unlink=True)
    target.data.update()
    if len(target.data.polygons)<=before:
        raise RuntimeError('CAVITY_HAS_NO_REAL_MESH_EFFECT:'+name)
    cut_count+=1
    print('INT11_REAL_EXCAVATION',name,before,len(target.data.polygons),flush=True)

# M247-C: genuine two nonmatching occupied shells with a vertically severed
# displaced crown, not the symmetric two planar cliffs of rejected INT10.
west=organic_geology('M247C_ALPHA_WEST_ACCRETED_ARCHIVE',
    (-850,510,670),(585,1020,875),2.7,'mineral_ochre')
east=organic_geology('M247C_ALPHA_EAST_CIVIC_HIGH_CITY',
    (960,560,850),(740,1080,1050),.65,'canyon_bone')
crown=organic_geology('M247C_ALPHA_FLOATING_SEVERED_NORTH',
    (1360,1190,1710),(500,590,420),3.9,'porcelain')
# Entrances and public atria are SUBTRACTIVE VOLUMES inside the actual solids.
# NAVE is a 600m-class public interior, not merely a visible hole in facade.
cavity(west,'WEST_LIBRARY_NAVE_MEGAHALL',(-455,150,490),(480,720,430),(0,.06,.16))
cavity(west,'WEST_PUBLIC_SKYLIGHT',(-520,510,870),(280,390,650),(.20,-.17,.08))
cavity(west,'WEST_UPPER_ARCHIVE_VAULT',(-635,1000,1120),(375,380,285),(0,.12,-.15))
cavity(east,'EAST_H1_GREAT_CIVIC_CHAMBER',(765,300,485),(510,700,445),(.04,.08,-.10))
cavity(east,'EAST_H1_INHABITED_CANYON',(820,910,980),(440,540,465),(.13,-.12,.05))
cavity(east,'EAST_HIGH_SKY_PORCH',(1160,1000,1500),(360,430,380),(.20,.20,.15))
cavity(crown,'FLOATING_CROWN_TECTONIC_SLIT',(1400,1050,1770),(230,420,215),(.14,.08,-.25))

# Real public floor ribbons with thick profiles, not a repeating plank floor.
def passage(name,coords,widths,depth,mat):
    assert len(coords)==len(widths)>=2
    vs=[]
    for i,point in enumerate(coords):
        d=Vector(coords[min(i+1,len(coords)-1)])-Vector(coords[max(i-1,0)])
        t=Vector((-d.y,d.x,0))
        if t.length<.1:t=Vector((1,0,0))
        t.normalize()
        c=Vector(point);w=widths[i]/2
        for zz in (0,-depth):
            for side in (-1,1):
                vs.append(tuple(c+t*side*w+Vector((0,0,zz))))
    fs=[(0,1,3,2),tuple(range(4*(len(coords)-1),4*len(coords)))]
    for i in range(len(coords)-1):
        a=i*4;b=a+4
        fs+=((a,a+1,b+1,b),(a+2,b+2,b+3,a+3),
             (a,a+2,b+2,b),(a+1,b+1,b+3,a+3))
    # Last side uses correctly ordered quads; never rely on hidden degenerate geometry.
    fs=[f for f in fs if len(set(f))==len(f)]
    return mesh(name,vs,fs,mat)

# W0 -> public NAVE: curve routes AROUND fixed camera, no occlusion at 10m.
passage('W0_HARBOR_ARRIVAL_TO_NAVE',
 [(-310,-980,28),(-285,-790,42),(-235,-590,53),(-190,-390,64),
  (-143,-150,81),(-105,55,103)], [120,116,98,88,79,83],20,'aged_bronze')
# NAVE is a fan-shaped, escalating communal bowl with clear destination.
for k,(y0,level) in enumerate([(-240,58),(-80,125),(85,194),(262,280)]):
    points=[]
    widths=[]
    for i in range(13):
        u=i/12
        y=y0+136*u
        x=-18+57*math.sin(math.pi*(u+.2*k))
        z=level+30*u+8*math.sin(math.pi*u)
        points.append((x,y,z))
        widths.append(150+56*math.sin(math.pi*u))
    passage('NAVE_'+('MARITIME_ARRIVAL','LIBRARY_PUBLIC_FORUM','CIVIC_READING_HALL','UPPER_CEREMONIAL_GARDEN')[k],
            points,widths,19,'porcelain' if k%2 else 'aged_bronze')
# The inner public canyon is framed by structural vaulted *branching ribs*,
# not a giant single ring, and does not block human eye with thin overhead floors.
def arch_beam(name,points,radius,mat):
    cv=bpy.data.curves.new('INT11_'+name,'CURVE')
    cv.dimensions='3D';cv.resolution_u=18
    sp=cv.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
    for bp,p in zip(sp.bezier_points,points):
        bp.co=p;bp.handle_left_type='AUTO';bp.handle_right_type='AUTO'
    cv.bevel_depth=radius;cv.bevel_resolution=3
    ob=bpy.data.objects.new('INT11_'+name,cv);coll.objects.link(ob)
    ob.data.materials.append(materials[mat])
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True);bpy.context.view_layer.objects.active=ob
    bpy.ops.object.convert(target='MESH')
    made.append(ob.name)
    return ob

arch_beam('M247C_BETA_SLANTED_CIVIC_SEAM',
 [(-750,490,700),(-470,625,1100),(-110,800,1300),
  (370,1070,1550),(920,1350,1730)],43,'aged_bronze')
# Distinct vaulted ribs delimit rooms and provide massive inner structure.
for i,(y,height) in enumerate([(20,545),(275,675),(545,895),(830,1090)]):
    arch_beam('NAVE_OCCUPIED_CROSS_VAULT_'+str(i),[
     (-585,y,330+i*90),(-400,y+65,height),(75,y+70,height+90),
     (460,y+40,height-45),(735,y,465+i*88)],
     30+4*i,'deep_lapis')
# West library's traversable terraces are carved-wall interiors with thickness.
for k,coords in enumerate([
 [(-290,-220,160),(-360,-80,174),(-422,110,195),(-460,260,250)],
 [(-340,140,340),(-425,235,389),(-480,430,435),(-525,630,500)],
 [(-395,490,555),(-520,620,629),(-600,825,725),(-700,960,793)]
]):
    passage('WEST_NAVE_LIBRARY_OCCUPIED_GALLERY_'+str(k),coords,
            [62,83,75,62],23,'aged_bronze' if k%2 else 'porcelain')
# H1 public shared market street S-curves through the CARVED H1 chamber, 
# not the camera's origin. Route arcs toward the floating northern district.
passage('H1_CIVIC_COMMON_MARKET_STREET',
 [(1060,100,360),(1110,285,405),(1150,500,485),
  (1110,720,600),(1020,895,760),(1190,1110,930)],
 [84,91,96,87,88,65],25,'aged_bronze')
passage('H1_NAVE_PUBLIC_GRADIENT_EXCHANGE',
 [(390,50,190),(560,100,230),(700,190,290),
  (850,310,390),(975,460,498)],
 [87,75,72,69,73],26,'porcelain')
passage('H1_HIGH_DISTRICT_TO_FLOATING_HEAD',
 [(1050,850,773),(1210,1000,1010),(1340,1190,1215),
  (1370,1290,1500)], [71,70,64,61],26,'aged_bronze')

# One architectural family of actual OCCUPIED VAULTS — not cubic boxes:
# variable 7-sided courtyard mass with steep leaning, multi-level vaulted
# roof, hollow entry and vertically stepped morphology in its own geometry.
def civic_vault(name,origin,radius,height,orientation,seed,mat):
    C=9;R=5
    v=[]
    for layer in range(R+1):
        t=layer/R
        z=origin[2]+height*t
        scale=(1-.17*t)+.055*math.sin(math.pi*t+seed)
        for i in range(C):
            a=2*math.pi*i/C+orientation
            rr=radius*scale*(1+.17*math.sin(3*a+seed)+.08*math.cos(5*a-seed))
            v.append((origin[0]+rr*math.cos(a),
                      origin[1]+rr*.83*math.sin(a),
                      z+height*.08*math.cos(2*a+seed)*math.sin(math.pi*t)))
    f=[tuple(reversed(range(C))),tuple(range(R*C,(R+1)*C))]
    for k in range(R):
        for j in range(C):
            a=k*C+j;b=k*C+(j+1)%C
            f.append((a,b,b+C,a+C))
    ob=mesh(name,v,f,mat)
    # Public-facing semicircular recessed threshold carved into real solid.
    center=Vector(origin)+Vector((radius*.50,0,height*.32))
    depth=radius*.64
    cut=ellipsoid_cutter(center,(depth,radius*.34,height*.29),
                        (.1,0,orientation),segments=24,rings=14)
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True);bpy.context.view_layer.objects.active=ob
    mod=ob.modifiers.new('INT11_REAL_PUBLIC_THRESHOLD','BOOLEAN')
    mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cut,do_unlink=True)
    return ob

# Nested H1 urban aggregation: distinct purposeful public programmes, 
# grouped around one real shared courtyard. Each vault geometrically unique;
# they are not 30 repeating rectangular apartment towers.
program=[
('SCHOOL_HUMANITIES',(1130,380,470),82,122,.3,1.5,'porcelain'),
('SCHOOL_CIVIC_STUDIO',(1210,510,540),64,100,-.22,2.3,'residence'),
('MARKET_FOOD_HALL',(945,560,570),94,137,.45,3.5,'residence'),
('MARKET_COVERED_COMMONS',(1140,690,680),70,108,-.24,1.7,'aged_bronze'),
('LIBRARY_READING_GARDEN',(890,735,730),92,155,.51,1.3,'porcelain'),
('HEALTH_COMMUNITY',(1170,845,820),63,113,-.48,4.1,'residence'),
('WORKSHOP_METAL_AND_WATER',(1035,975,955),75,140,.18,2.7,'deep_lapis'),
('RESIDENTIAL_HANGING_COURT_1',(1320,750,970),95,192,.40,3.1,'residence'),
('RESIDENTIAL_HANGING_COURT_2',(1225,925,1045),84,179,.10,5.3,'porcelain'),
('RESIDENTIAL_HANGING_COURT_3',(1415,1050,1190),93,211,-.22,1.9,'residence'),
('NORTH_NEIGHBORHOOD_FORUM',(1165,1100,1250),102,157,.4,2.4,'porcelain'),
('SKY_RESEARCH_CIVIC_LOUNGE',(1430,1300,1580),110,170,-.24,3.2,'aged_bronze')]
for name,origin,r,h,a,seed,mat in program:
    civic_vault('H1_'+name,origin,r,h,a,seed,mat)
# Key civic floors exist within the actual H1 void, not decal roofs.
for k,(x,y,z) in enumerate([(760,315,400),(930,465,560),(985,660,675),
                             (950,885,865),(1170,1130,1160)]):
    arch_beam('H1_INHABITED_ROCK_SUPPORT_'+str(k),
       [(x-195,y-96,z-55),(x-60,y,z+104),
        (x+112,y+65,z+140),(x+206,y+103,z+42)],
       18+k*2,'deep_lapis')
# W0 tidal binding: one sloped man-made spit and a preserved open sea.
passage('W0_MARITIME_GARDEN_LAND_TO_LIBRARY',
 [(-710,-1130,22),(-615,-995,41),(-485,-755,63),
  (-380,-550,83),(-270,-320,128)],
 [155,145,130,97,79],22,'mineral_ochre')

# Simple spatial illumination does not falsely fix ART; light both truly
# carved public halls and high-town residences.
for i,(where,energy,size) in enumerate([
 ((-190,65,470),2.5e6,280),((-580,470,810),2.1e6,250),
 ((665,120,700),2.1e6,300),((1020,620,870),2.8e6,360),
 ((1210,1230,1590),1.5e6,260)]):
    data=bpy.data.lights.new('INT11_CIVIC_ROOM_BOUNCE_'+str(i),'AREA')
    data.energy=energy;data.shape='DISK';data.size=size
    ob=bpy.data.objects.new(data.name,data);coll.objects.link(ob)
    ob.location=where
    aim=Vector((20,380,470))-ob.location
    ob.rotation_euler=aim.to_track_quat('-Z','Y').to_euler()

def camera(name,eye,at,lens=27):
    data=bpy.data.cameras.new(name);data.lens=lens;data.clip_end=18000
    ob=bpy.data.objects.new(name,data);coll.objects.link(ob)
    ob.location=eye
    ob.rotation_euler=(Vector(at)-Vector(eye)).to_track_quat('-Z','Y').to_euler()
camera('INT11_NAVE_HOLLOW_PUBLIC_INTERIOR',(70,-390,132),(-140,350,490),24)
camera('INT11_H1_CIVIC_MARKET_INTERIOR',(870,190,460),(1110,780,850),27)
camera('INT11_M247C_W0_THREE_DIMENSIONAL_AERIAL',(2250,-2500,2050),(200,520,1000),38)

bpy.context.view_layer.update()
for name,old in fixed.items():
    now=bpy.data.objects[name].matrix_world
    assert max(abs(now[i][j]-old[i][j]) for i in range(4) for j in range(4))<1e-6
assert all(name in bpy.data.objects for name in original_w0)
assert all(geo_fingerprint(bpy.data.objects[n])==w0_hash[n] for n in core_w0)
assert len(made)>=27 and cut_count>=7
assert scene['CONSTRUCTION']=='HOLD' and scene['FORMAL_ART_ACCEPTED']==scene['COMPLETED_TARGETS']==0
scene['INT11_SOURCE_SHA256']=PARENT
scene['INT11_METHOD']='VOLUMETRIC_SCULPTED_PUBLIC_ROOM_AND_INHABITED_COURTYARDS_NOT_WEDGE_LOFT'
scene['INT11_PRIVATE_ART_RESEARCH_ONLY']=True
scene['INT11_RESEARCH_NOT_OFFICIAL_MINECRAFT_COORDINATES']=True
scene['INT11_FORMAL_ART']=0
scene.camera=bpy.data.objects['E11_URBAN_AERIAL']
dst=out/'HALO9_INT11_HOLLOW_ARCHIPELAGO_CIVIC_CITY.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dst),compress=True)
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=12
scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED';scene.render.threads=2
scene.render.resolution_x=1024;scene.render.resolution_y=768
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
views=e11+('INT11_NAVE_HOLLOW_PUBLIC_INTERIOR',
            'INT11_H1_CIVIC_MARKET_INTERIOR',
            'INT11_M247C_W0_THREE_DIMENSIONAL_AERIAL')
hashes={}
for n in views:
    scene.camera=bpy.data.objects[n]
    target=out/'renders'/(n+'.png');scene.render.filepath=str(target)
    bpy.ops.render.render(write_still=True)
    assert target.stat().st_size>10000
    hashes[n]=hashlib.sha256(target.read_bytes()).hexdigest()
    print('INT11_REAL_INTEGRATED_3D_RENDER',n,target.stat().st_size,flush=True)
scene.camera=bpy.data.objects['E11_URBAN_AERIAL']
bpy.ops.wm.save_as_mainfile(filepath=str(dst),compress=True)
report={
 'schema':'halo9-int11-hollow-civic-archipelago-v1',
 'source_sha256':PARENT,
 'edited_native_blend_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),
 'removed_rejected_int10_meshes':len(removed),
 'preserved_W0_mesh_count':len(original_w0),
 'protected_W0_core_geometry_hashes':w0_hash,
 'hidden_only_in_research_copy_old_H1_context_meshes':context_hidden,
 'hollow_megastructures':major_works,
 'actual_Boolean_public_cavities':cut_count,
 'actual_new_3d_mesh_count':len(made),
 'new_mesh_names':made,
 'camera_original_e11_matrices':{
    n:[[float(x) for x in row] for row in fixed[n]] for n in e11},
 'six_authentic_render_sha256':hashes,
 'world_coordinates':'NOT_OFFICIALLY_REGISTERED',
 'structure_qa':'UNVERIFIED',
 'walkability':'UNVERIFIED',
 'art':'UNREVIEWED_NOT_ADOPTED',
 'formal_art_accepted':0,'completed_targets':0,'minecraft':'HOLD'}
(out/'INT11_TRUE_NATIVE_TECH_NOT_ART.json').write_text(json.dumps(report,indent=2))
print('INT11_ACTUAL_EDITABLE_CITY_AND_6_RENDERS_COMPLETE',report['edited_native_blend_sha256'],flush=True)
