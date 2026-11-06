"""HALO-9 INT7: integrated great-NAVE civic section, one real Blender scene.

This is NOT a new concept, formal adoption, Minecraft build or 2D illustration.
Edit an isolated copy of the ART-rejected but TECH-valid INT4-R1 native BLEND.
The previous small box/shelf NAVE and sky-deck studies are removed in THIS COPY,
replaced with two non-identical occupied tectonic banks and a connected
library / station / ceremony public interior. W0 remains the same reference,
H1 remains a non-accepted context study. Original E11 cameras stay fixed.

Research units are NOT officially registered Minecraft coordinates.
"""
import bpy, math, json, sys, hashlib
from pathlib import Path
from mathutils import Vector

a=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=Path(a[a.index('--output')+1]);out.mkdir(parents=True,exist_ok=True)
(out/'renders').mkdir(exist_ok=True)
src=Path(bpy.data.filepath)
SOURCE='7cf765923b91f06cce7951fc3558f042e488bf9f1157791b59b14d11954dc2bb'
assert src.name=='INT7_SOURCE.blend'
assert hashlib.sha256(src.read_bytes()).hexdigest()==SOURCE
scene=bpy.context.scene
assert scene['CONSTRUCTION']=='HOLD'
assert scene['FORMAL_ART_ACCEPTED']==0 and scene['COMPLETED_TARGETS']==0
original_cameras=['E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL']
camera_matrices={n:bpy.data.objects[n].matrix_world.copy() for n in original_cameras}
deleted=[]
for ob in list(scene.objects):
    # Existing reject NAVE and M247 thin-floors only. Preserve W0, H1,
    # approved historic study data outside this COPY and original cameras.
    if ob.type=='MESH' and (ob.name.startswith('INT4_NAVE_') or
        ob.name.startswith('INT4_M247_') or
        ob.name.startswith('INT4_R1_NAVE_')):
        deleted.append(ob.name)
        bpy.data.objects.remove(ob,do_unlink=True)
assert len(deleted)>=80,('unexpected research source/object scope',len(deleted))
coll=bpy.data.collections.new('INT7_SINGLE_OCCUPIED_CIVIC_RIFT_MACRO_STUDY')
scene.collection.children.link(coll)
M={}
for k,rgb,metal,rough in (
 ('pearl_cliff',(.70,.73,.67),.24,.63),
 ('basalt_shade',(.12,.20,.24),.18,.74),
 ('pale_masonry',(.83,.80,.72),.12,.72),
 ('warm_ore',(.55,.43,.30),.51,.52),
 ('copper',(.40,.29,.23),.66,.44),
 ('light_ceramic',(.68,.75,.69),.28,.44),
 ('public_glass',(.08,.34,.39),.33,.25),
 ('civic_garden',(.18,.33,.25),.03,.85),
 ('cream_light',(.96,.79,.53),.07,.48)):
    m=bpy.data.materials.new('INT7_'+k);m.diffuse_color=(*rgb,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Metallic'].default_value=metal
    p.inputs['Roughness'].default_value=rough
    if k=='cream_light':
        p.inputs['Emission Color'].default_value=(*rgb,1)
        p.inputs['Emission Strength'].default_value=.75
    M[k]=m
counts={}
def geom(name,verts,faces,mat):
    assert verts and faces
    md=bpy.data.meshes.new('INT7_'+name)
    md.from_pydata(verts,[],faces);md.update()
    ob=bpy.data.objects.new('INT7_'+name,md)
    coll.objects.link(ob);ob.data.materials.append(M[mat])
    head=name.split('_')[0];counts[head]=counts.get(head,0)+1
    assert len(md.polygons)>0,name
    return ob

def polygon(name,points,lower,upper,mat):
    assert upper>lower and len(points)>=3
    n=len(points)
    vs=[(x,y,lower) for x,y in points]+[(x,y,upper) for x,y in points]
    fs=[tuple(reversed(range(n))),tuple(range(n,n*2))]
    fs.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
    return geom(name,vs,fs,mat)

def path(name,points,width,depth,mat):
    assert len(points)>=2 and width>0 and depth>0
    vs=[]
    for i,p in enumerate(points):
        d=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)])
        L=math.hypot(d.x,d.y)
        nx,ny=((-d.y/L,d.x/L) if L>1e-5 else (1,0))
        x,y,z=p
        vs.extend(((x+nx*width/2,y+ny*width/2,z-depth),
                   (x-nx*width/2,y-ny*width/2,z-depth),
                   (x+nx*width/2,y+ny*width/2,z),
                   (x-nx*width/2,y-ny*width/2,z)))
    fs=[(0,2,3,1),tuple(range(len(vs)-4,len(vs)))]
    for i in range(len(points)-1):
        aa=4*i;bb=aa+4
        fs.extend(((aa,aa+1,bb+1,bb),(aa+2,bb+2,bb+3,aa+3),
                   (aa,aa+2,bb+2,bb),(aa+1,bb+1,bb+3,aa+3)))
    return geom(name,vs,fs,mat)

def bank(name,side,sections,mat):
    """One inhabited 3D *concave* civic section, not a giant solid wall.
    Each authored cross section is (y, outerX, innerX, footZ, terraceZ, crownZ).
    Its inner roof/civic ledge forms a legible habitable hollow facing the NAVE.
    """
    rings=[]
    for idx,(y,outer,inner,foot,level,crown) in enumerate(sections):
        span=abs(outer-inner)
        assert span>200 and crown>level>foot
        # Outer rock rises in an asymmetric fold, returns as an open inner lip.
        # Deep central inset is a spatial void, not a painted dark rectangle.
        pts=[
          (outer-side*28,y,foot-15),
          (outer-side*56,y,level*.51+foot*.49),
          (outer+side*31,y,crown*.87),
          (outer+side*(span*.45),y,crown+34*math.sin(idx*.7)),
          (inner-side*36,y,crown*.86),
          (inner-side*102,y,level+67),
          (inner+side*18,y,level-30),
          (inner+side*32,y,foot+76),
          (inner-side*113,y,foot-26)
        ]
        rings.append(pts)
    n=len(rings[0]);v=[p for ring in rings for p in ring]
    f=[tuple(reversed(range(n))),tuple(range((len(rings)-1)*n,len(rings)*n))]
    for i in range(len(rings)-1):
        for j in range(n):
            aa=i*n+j;bb=i*n+(j+1)%n
            f.append((aa,bb,bb+n,aa+n))
    return geom(name,v,f,mat)

def folded_spine(name,points,sections,mat):
    """A tapered six-sided thick flying stratum in actual 3D, with distinct
    cross sections, *not* a thin plane or generic round pipe."""
    assert len(points)==len(sections)
    rings=[]
    for i,(p,measure) in enumerate(zip(points,sections)):
        a=Vector(points[max(i-1,0)])
        b=Vector(points[min(i+1,len(points)-1)])
        d=(b-a).normalized()
        transverse=Vector((-d.y,d.x,0))
        if transverse.length<.01:transverse=Vector((1,0,0))
        transverse.normalize()
        vertical=d.cross(transverse).normalized()
        w,h=measure;center=Vector(p)
        layout=[
          (-.88,-.42),(-.61,.50),(.12,.85),
          (.93,.25),(.79,-.63),(-.23,-.90)]
        ring=[tuple(center+transverse*(u*w)+vertical*(v*h)) for u,v in layout]
        rings.append(ring)
    n=len(rings[0]);vs=[p for r in rings for p in r]
    fs=[tuple(reversed(range(n))),tuple(range((len(rings)-1)*n,len(rings)*n))]
    for i in range(len(rings)-1):
        for j in range(n):
            x=i*n+j;y=i*n+(j+1)%n
            fs.append((x,y,y+n,x+n))
    return geom(name,vs,fs,mat)

# STEP A: a genuine 750m-high civic rift whose sides belong to the same
# artificial terrain. The original NAVE eye at (15,-360,73.7) is NOT buried.
west=bank('M247_ALPHA_WEST_LIVED_FAULT_SHEAR',-1,[
 (-390,-570,-220,10,150,260),
 (-186,-655,-240,25,242,448),
 (45,-730,-290,35,325,627),
 (271,-798,-332,67,485,833),
 (530,-879,-389,120,666,1046),
 (809,-940,-451,233,806,1288),
 (1100,-986,-508,328,926,1481),
], 'pearl_cliff')
east=bank('M247_ALPHA_EAST_ASCENDING_CIVIC_SHEAR',1,[
 (-379,599,260,9,175,314),
 (-129,673,301,27,307,511),
 (94,785,340,57,411,719),
 (326,894,397,101,549,943),
 (588,960,467,192,726,1164),
 (855,1089,541,270,914,1417),
 (1176,1181,634,422,1104,1632),
], 'basalt_shade')

# STEP B: NAVE's programme is one huge continuous open interior.
# Forum is intentionally beneath high tectonic roofs and opens to the sea.
polygon('NAVE_GREAT_CIVIC_ASSEMBLY_FLOOR',[
 (-145,-307),(142,-324),(213,-160),(233,65),
 (177,321),(41,381),(-198,242),(-213,-32)
],65,88,'pale_masonry')
polygon('NAVE_LIBRARY_OCCUPIED_WEST_PUBLIC_FLOOR',[
 (-462,-231),(-339,-302),(-223,-183),(-226,68),
 (-394,122),(-498,-20)
],130,145,'pale_masonry')
polygon('NAVE_LIBRARY_DEEP_READING_GALLERY',[
 (-536,0),(-411,-96),(-304,-17),(-324,151),
 (-439,229),(-584,96)
],297,314,'warm_ore')
polygon('NAVE_STATION_OCCUPIED_EAST_PLATFORM',[
 (224,-279),(343,-303),(509,-197),(495,123),
 (338,201),(245,62)
],127,144,'light_ceramic')
polygon('NAVE_STATION_PUBLIC_MEZZANINE',[
 (372,-48),(488,-68),(597,72),(555,251),
 (414,273),(324,101)
],299,314,'pale_masonry')
polygon('NAVE_NORTH_RITUAL_CIVIC_ATRIUM',[
 (-178,231),(-1,203),(224,275),(308,472),
 (178,615),(-95,541),(-253,392)
],346,363,'warm_ore')
# A singular interior void, not an empty roof-shell: sweeping public ramps
# connect library, station, ceremony and W0 to the same shared forum.
path('NAVE_CONTINUOUS_PUBLIC_CENTRAL_BOULEVARD',[
 (24,-279,90),(30,-125,91),(55,33,114),
 (59,184,226),(83,355,355)],35,11,'pale_masonry')
path('NAVE_WEST_READING_RAMP',[
 (-4,-151,92),(-159,-116,112),(-281,-57,141),
 (-403,32,311)],27,9,'cream_light')
path('NAVE_STATION_ACCESS',[
 (79,-191,92),(202,-173,112),(329,-127,140)],29,10,'cream_light')
path('NAVE_STATION_UPPER_WALK',[
 (321,-105,146),(374,-19,209),(452,97,309)],22,10,'light_ceramic')
path('NAVE_CEREMONY_PUBLIC_ASCENT',[
 (62,184,225),(-15,279,289),(46,401,362)],30,12,'pale_masonry')
# Public rail evidence in actual station hall, not residential facade decals.
for i,(xoff,zoff) in enumerate(((0,0),(41,2))):
    path('NAVE_STATION_INTEGRATED_RAIL_'+str(i),[
      (311+xoff,-321,118+zoff),(336+xoff,-161,126+zoff),
      (397+xoff,41,143+zoff)],5,3,'copper')
# Huge accessible radial library reading banks, distinct levels and open air.
for i,pts in enumerate([
 [(-485,-162),(-422,-197),(-355,-132),(-392,-59),(-467,-71)],
 [(-447,-34),(-369,-70),(-312,26),(-384,99),(-457,44)],
 [(-506,68),(-434,32),(-378,123),(-437,185),(-509,143)]
]):
    polygon('NAVE_LIBRARY_RADIAL_READING_ISLAND_'+str(i),pts,162+i*46,174+i*46,
           'warm_ore' if i%2 else 'light_ceramic')
# Ceremonial public seating flows in a fanned arrangement, not thin floors.
for i,poly in enumerate([
 [(-147,325),(-51,300),(132,346),(189,389),(93,412),(-107,380)],
 [(-137,395),(-31,359),(147,406),(196,450),(88,482),(-90,444)],
 [(-124,464),(-3,428),(145,475),(170,521),(70,545),(-98,513)]
]):
    polygon('NAVE_RITUAL_INHABITED_AUDIENCE_'+str(i),poly,363+i*28,378+i*28,
            'light_ceramic')

# STEP C: two highly dissimilar, 3D tectonic crown spines anchor the civic
# room in the larger M247-C dual-shell / oblique rift idea, but do NOT cap
# the entire NAVE sightline with a flat ceiling.
folded_spine('M247_WEST_ASCENDING_FAULT_CREST',[
 (-683,-344,102),(-667,-75,357),(-617,219,604),
 (-526,526,837),(-379,821,1174)
],[(124,104),(150,138),(181,171),(173,165),(100,94)],'warm_ore')
folded_spine('M247_EAST_DISPLACED_FAULT_CREST',[
 (675,-306,72),(623,-89,321),(701,242,609),
 (807,553,926),(1047,837,1294)
],[(105,99),(144,136),(179,178),(161,161),(96,109)],'pearl_cliff')
# One large diagonal transfer with actual structural thickness linking the
# west civic library strata to east suspended housing territory.
folded_spine('M247_BETA_PUBLIC_TRANSFAULT_CIVIC_SPINE',[
 (-494,316,570),(-287,441,687),(-65,528,753),
 (210,621,882),(506,786,1022)
],[(89,70),(101,79),(122,84),(104,94),(77,77)],'light_ceramic')
path('M247_BETA_INHABITED_PASSAGE',[
 (-494,320,625),(-292,445,733),(-70,534,793),
 (214,623,923),(505,785,1062)],30,10,'cream_light')
# A crucial public-to-cliff connection, neither a facade-only label nor
# a thin unlanded balcony. Thick landing closes the route at both ends.
path('M247_NAVE_WEST_CLIFF_LEARNING_ACCESS',[
 (-402,33,312),(-462,210,424),(-494,326,568)],29,13,'pale_masonry')
path('M247_NAVE_EAST_CLIFF_TRANSIT_ACCESS',[
 (452,101,314),(479,274,432),(534,449,574)],32,13,'light_ceramic')
# Integrate coast with city; do not delete W0 or invent Minecraft anchors.
path('W0_TIDAL_LANDING_TO_NAVE_GREAT_INTERIOR',[
 (270,-591,72),(171,-511,74),(76,-414,82),
 (26,-290,90)],38,14,'pale_masonry')

# Living urban program belongs inside the concave faults, not just to
# roofs or window stickers. Each occupied volume has different footprint.
for label,poly,z,h,mat in [
 ('WEST_OCCUPIED_LIBRARY',[
  (-541,190),(-479,114),(-343,135),(-290,266),
  (-391,350),(-548,296)],384,95,'basalt_shade'),
 ('EAST_INHABITED_SCHOOL',[
  (493,310),(603,236),(760,318),(784,459),
  (662,519),(496,442)],451,139,'pearl_cliff'),
 ('WEST_CIVIC_GARDEN',[
  (-718,473),(-572,413),(-465,494),(-504,631),
  (-656,685),(-759,578)],702,27,'civic_garden'),
 ('EAST_MARKET_COURT',[
  (668,548),(813,488),(920,600),(852,751),
  (713,771),(617,674)],717,98,'warm_ore')
]:
    polygon('CITY_'+label+'_PHYSICAL_PUBLIC_BODY',poly,z-68,z+h,mat)
    # Sky-exposed courtyard within the scene, separate from the main mass.
    p=[(x*.58+sum(a for a,b in poly)/len(poly)*.42,
        y*.58+sum(b for a,b in poly)/len(poly)*.42) for x,y in poly]
    polygon('CITY_'+label+'_INTERNAL_PUBLIC_COURT',p,z+h,z+h+7,
           'civic_garden' if 'GARDEN' in label else 'light_ceramic')
# Unique civic atrium lighting, not masking the forms with bloom.
for i,(pos,energy,size) in enumerate([
 ((-250,-55,320),1250000,140),((319,-23,320),1390000,125),
 ((40,231,545),1550000,185),((-480,292,637),1160000,130),
 ((555,365,735),1150000,130)
]):
    data=bpy.data.lights.new('INT7_CIVIC_HALL_AREA_'+str(i),'AREA')
    data.energy=energy;data.shape='DISK';data.size=size
    ob=bpy.data.objects.new(data.name,data);coll.objects.link(ob)
    ob.location=pos;ob.rotation_euler=(0,0,0)

# Two explicitly NEW review cameras do not replace original protected E11.
def new_camera(name,eye,at,lens=34):
    data=bpy.data.cameras.new(name)
    ob=bpy.data.objects.new(name,data);coll.objects.link(ob)
    ob.location=eye
    ob.rotation_euler=(Vector(at)-Vector(eye)).to_track_quat('-Z','Y').to_euler()
    data.type='PERSP';data.lens=lens
new_camera('INT7_NAVE_CIVIC_INTERIOR_DETAIL',
           (-28,-115,171),(0,206,355),25)
new_camera('INT7_M247_W0_SCULPTURE_OBLIQUE',
           (1415,-1470,1190),(10,265,490),38)

# Preserve originals and safety; report failures instead of fake TECH.
bpy.context.view_layer.update()
for n,m in camera_matrices.items():
    now=bpy.data.objects[n].matrix_world
    assert max(abs(now[i][j]-m[i][j]) for i in range(4) for j in range(4))<1e-6
assert len(west.data.polygons)>50 and len(east.data.polygons)>50
assert all(math.isfinite(a) for ob in (west,east) for v in ob.data.vertices for a in v.co[:])
scene['INT7_PARENT_SHA256']=SOURCE
scene['INT7_RESEARCH_METHOD']='MANUALLY_AUTHORED_MULTI_PROGRAM_CONCAVE_CIVIC_SECTION'
scene['INT7_REMOVED_REJECTED_NAVE_AND_SHELVES']=len(deleted)
scene['INT7_UNITS']='RESEARCH_METRES_NOT_MINECRAFT_ANCHORS'
scene['CONSTRUCTION']='HOLD';scene['FORMAL_ART_ACCEPTED']=0
scene['COMPLETED_TARGETS']=0
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=18
scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED';scene.render.threads=2
scene.render.resolution_x=1100;scene.render.resolution_y=825
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.camera=bpy.data.objects[original_cameras[-1]]
dest=out/'HALO9_INT7_NAVE_GREAT_OCCUPIED_RIFT.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
views=original_cameras+['INT7_NAVE_CIVIC_INTERIOR_DETAIL',
                        'INT7_M247_W0_SCULPTURE_OBLIQUE']
renders={}
for n in views:
    scene.camera=bpy.data.objects[n]
    p=out/'renders'/(n+'.png')
    scene.render.filepath=str(p)
    bpy.ops.render.render(write_still=True)
    assert p.exists() and p.stat().st_size>5000
    renders[n]=hashlib.sha256(p.read_bytes()).hexdigest()
    print('INT7_NATIVE_E11_OR_NEW_VIEW_RENDER',n,p.stat().st_size,flush=True)
scene.camera=bpy.data.objects[original_cameras[-1]]
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
report={
 'schema':'halo9-int7-nave-occupied-rift-native-v1',
 'source_sha256':SOURCE,
 'native_blend_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
 'rejected_nave_and_m247_objects_removed_in_study':len(deleted),
 'new_mesh_by_role':counts,
 'camera_original_matrices_unchanged':True,
 'public_programmes':['library','rail station','ceremony','W0 access',
                      'inhabited high city','civic street'],
 'geometry_integrity':'NONZERO_MESH_ONLY_VOLUME_NOT_YET_VERIFIED',
 'functional_walkability':'UNKNOWN_NOT_EXHAUSTIVELY_SWEEP_VERIFIED',
 'original_e11_render_names':original_cameras,
 'extra_review_views':['INT7_NAVE_CIVIC_INTERIOR_DETAIL','INT7_M247_W0_SCULPTURE_OBLIQUE'],
 'render_sha256':renders,
 'formal_art_accepted':0,'completed_targets':0,
 'minecraft':'HOLD','art':'UNREVIEWED_AWAITING_DIRECT_IMAGE_ASSESSMENT'
}
(out/'INT7_NATIVE_EVIDENCE.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('INT7_NATIVE_NAVE_SCULPTURE_FINISHED',report['native_blend_sha256'],flush=True)
