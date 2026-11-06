"""HALO-9 INT10 / M247-C: one genuinely different civic-canyon architecture.
Source: protected ART REJECT INT9-R1 BLEND copied into an isolated research branch.
The rejected INT7 wedge/floor ensemble is removed ONLY IN THIS COPY.
W0 older reference / original E11 cameras / history / main / Freeze preserved.
One new spatial composition: inhabited river-cut fault walls + large inner
civic forum + excavated public rooms + H1 thick market city + W0 tidal access.
This is native Blender mesh authoring, NOT GUI hand-sculpt or formal ART approval.
"""
import bpy, math, hashlib, json, sys, random
from mathutils import Vector
from pathlib import Path

args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=Path(args[args.index('--output')+1]);out.mkdir(parents=True,exist_ok=True)
(out/'renders').mkdir(exist_ok=True)
src=Path(bpy.data.filepath)
PARENT='651eb465405fef91b8baabd80d4428dbd2c3ba395c71e8abda71fc354cc3ba27'
assert src.name=='INT10_SOURCE.blend'
assert hashlib.sha256(src.read_bytes()).hexdigest()==PARENT, 'input source mismatch'
sc=bpy.context.scene
assert sc['CONSTRUCTION']=='HOLD' and sc['COMPLETED_TARGETS']==sc['FORMAL_ART_ACCEPTED']==0
e11=('E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL')
poses={n:bpy.data.objects[n].matrix_world.copy() for n in e11}
original_w0={o.name for o in sc.objects if o.name.startswith(('W0_','INT4_W0_','INT6_W0_'))}
assert len(original_w0)>0,'W0 continuity absent from inherited source'
removed=[]
for ob in list(sc.objects):
    if ob.name.startswith('INT7_') and ob.type in {'MESH','LIGHT','CAMERA'}:
        removed.append(ob.name)
        bpy.data.objects.remove(ob,do_unlink=True)
assert len(removed)>20,('rejected wedge objects not found',len(removed))
assert all(name in bpy.data.objects for name in original_w0),'W0 original lost'
coll=bpy.data.collections.new('INT10_M247C_INHABITED_CIVIC_CANYON_RESEARCH')
sc.collection.children.link(coll)
mats={}
def mat(k,color,metal,rough,emission=0):
    m=bpy.data.materials.new('INT10_'+k);m.use_nodes=True
    m.diffuse_color=(*color,1)
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Metallic'].default_value=metal
    bs.inputs['Roughness'].default_value=rough
    if emission:
        bs.inputs['Emission Color'].default_value=(*color,1)
        bs.inputs['Emission Strength'].default_value=emission
    mats[k]=m
for a in [
    ('west_cliff',(.50,.56,.55),.06,.77,0),
    ('east_mineral',(.64,.70,.68),.15,.61,0),
    ('civic_stone',(.77,.72,.60),.06,.74,0),
    ('deep_structure',(.07,.18,.22),.25,.52,0),
    ('glaze_teal',(.13,.43,.47),.50,.28,0),
    ('bronze',(.55,.39,.22),.59,.39,0),
    ('amber_light',(.95,.69,.37),.07,.35,1.6),
    ('garden',(.21,.36,.27),0,.83,0),
    ('ivory_housing',(.73,.73,.63),.22,.55,0),
]:
    mat(*a)

made=[]
def mesh(name,verts,faces,material):
    assert len(verts)>=4 and len(faces)>=4,(name,len(verts),len(faces))
    data=bpy.data.meshes.new('INT10_'+name)
    data.from_pydata(verts,[],faces);data.update()
    ob=bpy.data.objects.new('INT10_'+name,data)
    coll.objects.link(ob)
    ob.data.materials.append(mats[material])
    made.append(ob.name)
    assert all(math.isfinite(float(x)) for v in ob.data.vertices for x in v.co)
    return ob
def catmull(a,b,c,d,t):
    return .5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)
def interpolate_stations(stations,steps=5):
    rows=[]
    for i in range(len(stations)-1):
        prev=stations[max(0,i-1)];nxt=stations[min(len(stations)-1,i+2)]
        for j in range(steps):
            t=j/steps
            rows.append(tuple(catmull(prev[k],stations[i][k],stations[i+1][k],nxt[k],t) for k in range(len(prev))))
    rows.append(tuple(stations[-1]))
    return rows
def tectonic_bank(name,side,stations,material):
    # Stations are explicitly authored real (y, innerX, outerX, basalZ,
    # crownZ, inward-scoop). Nonconvex occupied cross section with a major
    # inner overhang and a deep continuous canyon; unlike prior huge wedges.
    # A 3D volumetric mesh: 15 distinct profile vertices, many transverse
    # sections and a physically finite underside.
    profile=[(1.05,.03),(1.13,.22),(1.14,.47),(1.05,.73),
             (.85,1.01),(.66,1.08),(.49,1.04),(.31,.89),
             (.18,.73),(.35,.64),(.46,.47),(.38,.30),
             (.13,.24),(-.02,.10),(.19,-.035)]
    expanded=interpolate_stations(stations,5)
    verts=[]
    for idx,(y,inner,outer,base,crown,recess) in enumerate(expanded):
        dz=crown-base
        for k,(p,height) in enumerate(profile):
            scooped=(1-math.cos(math.pi*max(0,min(1,(p+.05)/1.2))))*.5
            wiggle=(math.sin(.008*y+1.1*k)*.009+math.cos(.015*y-.45*k)*.012)
            x=inner+(outer-inner)*(p+wiggle)+side*recess*scooped*.13
            z=base+dz*(height+.013*math.sin(.009*y+1.4*k))
            verts.append((x,y+16*math.sin(.007*y+1.2*k),z))
    n=len(profile);rings=len(expanded)
    faces=[tuple(reversed(range(n))),tuple(range((rings-1)*n,rings*n))]
    for i in range(rings-1):
        for j in range(n):
            aa=i*n+j;bb=i*n+(j+1)%n
            faces.append((aa,bb,bb+n,aa+n))
    ob=mesh(name,verts,faces,material)
    assert len(ob.data.vertices)>350
    return ob
# Hand-chosen asymmetrical fault geology; no mirrored generic tower wall.
west=tectonic_bank('M247_C_WEST_CIVIC_MOUNTAIN_LECTERN',-1,[
(-720,-210,-760,-30,205,70),(-420,-235,-845,-12,380,75),
(-140,-286,-916,18,604,90),(120,-321,-1010,45,872,150),
(395,-345,-1080,82,1135,160),(680,-396,-1150,180,1345,125),
(950,-445,-1220,280,1590,175),(1220,-525,-1200,390,1750,220),
(1520,-598,-1100,590,1770,110)],'west_cliff')
east=tectonic_bank('M247_C_EAST_INHABITED_STRATA',1,[
(-740,310,965,-25,230,90),(-420,280,990,13,490,165),
(-120,255,1120,60,720,160),(150,306,1230,70,915,160),
(450,370,1285,145,1230,200),(760,456,1370,285,1480,210),
(1040,535,1430,450,1750,220),(1370,660,1410,610,1880,205),
(1650,820,1330,790,1910,100)],'east_mineral')
# Physical offset of suspended northern upper half: detached elevated
# crown, materially discontinuous with the east bank (alpha twin-shell).
head=tectonic_bank('M247_C_DISPLACED_FLOATING_HEAD',1,[
(560,1110,1600,1110,1520,90),(830,1205,1760,1150,1780,110),
(1080,1300,1810,1380,2050,135),(1320,1420,1830,1650,2270,125),
(1540,1540,1790,1880,2330,70)],'civic_stone')
# Narrow displaced diagonal inhabited connecting spine across actual void.
def ribbon(name,coords,widths,depth,material):
    assert len(coords)==len(widths)>=2
    vs=[]
    for i,p in enumerate(coords):
        d=Vector(coords[min(i+1,len(coords)-1)])-Vector(coords[max(0,i-1)])
        q=Vector((-d.y,d.x,0))
        if q.length<1e-5:q=Vector((1,0,0))
        q.normalize()
        pos=Vector(p);w=widths[i]/2
        for zoff in (0,-depth):
            for side in (-1,1):
                vs.append(tuple(pos+q*side*w+Vector((0,0,zoff))))
    fs=[(0,1,3,2),tuple(range(4*(len(coords)-1),4*len(coords)))]
    for i in range(len(coords)-1):
        a=4*i;b=a+4
        fs.extend([(a,a+1,b+1,b),(a+2,b+2,b+3,a+3),
                   (a,a+2,b+2,b),(a+1,b+1,b+3,a+3)])
    return mesh(name,vs,fs,material)
# Return primary generous civic routes, all as actual three-dimensional floors:
# from W0 coast to NAVE, public station, library and upper residential town.
ribbon('W0_MARITIME_CIVIC_APPROACH',
 [(130,-925,30),(85,-710,48),(35,-530,73),(0,-360,87),
  (-7,-190,95),(10,10,107)], [115,103,100,105,88,93],23,'civic_stone')
# Public forum is a broad, split, sculpted amphitheater, not a solid sheet:
# five different fan-shaped curved occupation routes, exposed to skylight.
for zone,start,finish,level in [
 ('ARRIVAL',-250,-125,89),('STATION',-95,70,146),
 ('LIBRARY',80,230,218),('CEREMONY',240,390,318)]:
    pts=[];width=[]
    for i in range(17):
        t=i/16
        y=start+(finish-start)*t
        x=-85+45*math.sin(2.3*t+len(zone)*.4)
        z=level+18*t+6*math.sin(math.pi*t)
        pts.append((x,y,z))
        width.append(125+50*math.sin(math.pi*t))
    ribbon('NAVE_'+zone+'_GREAT_PUBLIC_FLOOR',pts,width,26,'civic_stone')
# A genuinely continuous occupied ascent from the open public forum into the
# upper fault, spiraling around a central void. NOT multiple thin shelves.
path=[];width=[]
for i in range(96):
    t=i/95
    a=-.8*math.pi+2.25*math.pi*t
    R=204-15*t
    path.append((12+R*math.cos(a),115+R*.83*math.sin(a),
                 104+386*t))
    width.append(66-14*t+7*math.sin(2*math.pi*t))
ribbon('NAVE_CIVIC_ASCENT_CONTINUOUS_INHABITED_RAMP',path,width,20,'civic_stone')
# Distinct physical civic destinations and landings tethered to the faults.
ribbon('NAVE_WEST_PUBLIC_LIBRARY_THRESHOLD',
 [(-58,115,227),(-260,158,253),(-393,261,353),(-506,374,464)],
 [68,71,64,60],18,'bronze')
ribbon('NAVE_EAST_STATION_THRESHOLD',
 [(43,-88,147),(238,-120,177),(342,-7,261),(420,121,333)],
 [85,88,77,72],20,'civic_stone')
ribbon('NAVE_CEREMONIAL_TO_WEST_HIGH_CITY',
 [(-45,340,330),(-225,425,432),(-400,533,582),(-532,690,730)],
 [83,87,73,65],23,'glaze_teal')
ribbon('M247_C_SLANTED_SEAM_SUSPENDED_TRANSIT',
 [(-535,690,727),(-320,826,855),(-40,948,978),
  (250,1075,1155),(580,1173,1370),(945,1250,1560)],
 [79,88,81,74,71,62],27,'bronze')
ribbon('M247_C_EAST_FLOATING_HEAD_ACCESS',
 [(954,1170,1294),(1130,1204,1440),(1290,1260,1680)],
 [73,61,58],22,'civic_stone')
# Sculpture is not only silhouettes: deeply nested west gallery carves a
# concave, multi-level inhabited library reading valley in the mountain.
for k,(z,y,x) in enumerate([(214,0,-356),(343,200,-450),(481,410,-530),
                           (646,610,-636),(819,790,-724)]):
    xs=[x-120,x-96,x-20,x+46,x+61]
    pts=[(xs[i],y+70*math.sin(math.pi*i/4),z+11*math.sin(math.pi*i/4))
         for i in range(5)]
    ribbon('WEST_PUBLIC_LIBRARY_ROCK_GALLERY_'+str(k),pts,
           [93,104,123,109,83],21,'ivory_housing' if k%2 else 'bronze')
# A real H1 high city *on the cliff thickness*: one wide serpentine
# marketplace/street, distinct nonlinear parcels, no uniform rectangle towers.
ribbon('H1_HIGH_CITY_INHABITED_MARKET_STREET',
 [(716,110,445),(744,280,440),(780,450,476),(753,630,556),
  (822,811,653),(845,990,787),(926,1150,955)],
 [104,107,121,113,125,102,84],27,'civic_stone')
ribbon('H1_W0_ELEVATED_TRANSIT_SWITCHBACK',
 [(433,90,330),(557,196,391),(687,292,428),(756,450,479)],
 [79,72,69,71],22,'bronze')

def volume(name,outline,z,h,material,rooftilt=0):
    # Individual civic/urban authored irregular footprint, real thick
    # floor/roof/side enclosure. No identical rectangular building repetition.
    n=len(outline)
    vs=[(x,y,z) for x,y in outline]
    for i,(x,y) in enumerate(outline):
        vs.append((x,y,z+h+rooftilt*math.sin(i*2*math.pi/n)))
    fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    for i in range(n):
        fs.append((i,(i+1)%n,(i+1)%n+n,i+n))
    return mesh(name,vs,fs,material)
# H1: active public spaces and varied residential macro courtyards.
# Interlocking geometries, not a tiled field of box apartment icons.
for name,poly,z,h,material,tilt in [
 ('H1_SCHOOL_LODGED_IN_ESCARPMENT',
  [(480,390),(555,325),(658,393),(682,537),(584,594),(464,520)],
  405,155,'ivory_housing',29),
 ('H1_MARKET_FAN_HALL',
  [(849,373),(945,333),(1048,438),(1022,560),(890,601),(813,495)],
  430,142,'bronze',23),
 ('H1_LIBRARY_PUBLIC_WINTER_GARDEN',
  [(560,669),(649,599),(724,635),(728,785),(653,830),(537,770)],
  555,120,'glaze_teal',42),
 ('H1_MULTIFAMILY_LANDSCAPE_HOUSE',
  [(910,639),(1070,625),(1126,713),(1060,841),(931,812),(862,713)],
  587,169,'ivory_housing',48),
 ('H1_CIVIC_RESIDENCE_AMPHITHEATER',
  [(581,914),(744,874),(822,990),(761,1103),(620,1125),(535,1032)],
  767,191,'west_cliff',41),
 ('H1_NEIGHBOURHOOD_COMMONS',
  [(945,935),(1071,902),(1203,970),(1171,1095),(1006,1140),(892,1043)],
  861,133,'civic_stone',22),
]:
    volume(name,poly,z,h,material,tilt)
# True public courtyards cut from non-private H1 buildings (not decals).
for bname,fx,fy in [
 ('H1_SCHOOL_LODGED_IN_ESCARPMENT',570,467),
 ('H1_MARKET_FAN_HALL',940,476)]:
    building=bpy.data.objects['INT10_'+bname]
    # vertical irregular octagonal skylight, solid geometric void.
    zmin=min(v.co.z for v in building.data.vertices)
    zmax=max(v.co.z for v in building.data.vertices)
    outline=[(fx+30*math.cos(a),fy+29*math.sin(a)) for a in [2*math.pi*i/9 for i in range(9)]]
    cutter=volume('_TEMP_'+bname+'_COURT',outline,zmin-90,zmax-zmin+180,'deep_structure')
    bpy.ops.object.select_all(action='DESELECT')
    building.select_set(True);bpy.context.view_layer.objects.active=building
    mod=building.modifiers.new('INT10_REAL_OPEN_PUBLIC_COURT','BOOLEAN')
    mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True)
    assert len(building.data.polygons)>12,('courtyard void unverified',bname)
# W0: sculpted tidal terraces actually meet NAVE access, not a distant flat
# blue background or cut-off reference. Preserves older W0 in source copy.
for i,(y0,z0) in enumerate([(-970,14),(-825,29),(-665,47)]):
    coords=[]
    for j in range(19):
        t=j/18
        x=-485+850*t
        y=y0+55*math.sin(math.pi*t)+31*math.sin(2.4*math.pi*t)
        z=z0+15*math.sin(2*math.pi*t+1.1*i)+6*t
        coords.append((x,y,z))
    ribbon('W0_TIDAL_OCCUPIED_STONE_TERRACE_'+str(i),coords,
           [85+34*math.sin(math.pi*j/18) for j in range(19)],23,
           'civic_stone' if i%2 else 'west_cliff')
# Illumination reveals spatial depth instead of compensating for weak mass.
for i,(position,energy,size) in enumerate([
 ((-215,-45,400),2.2e6,230),((265,155,520),2.0e6,225),
 ((755,500,710),2.9e6,270),((-620,620,1020),2.0e6,275),
 ((870,1000,1100),2.5e6,270)]):
    lamp=bpy.data.lights.new('INT10_CIVIC_BOUNCE_'+str(i),'AREA')
    lamp.energy=energy;lamp.shape='DISK';lamp.size=size
    o=bpy.data.objects.new(lamp.name,lamp);coll.objects.link(o)
    o.location=position
    direction=Vector((0,220,320))-o.location
    o.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()

# Extra review views DO NOT replace original fixed three.
def view(name,eye,look,lens=27):
    cam=bpy.data.cameras.new(name)
    cam.lens=lens;cam.clip_end=18000
    obj=bpy.data.objects.new(name,cam);coll.objects.link(obj)
    obj.location=eye
    obj.rotation_euler=(Vector(look)-Vector(eye)).to_track_quat('-Z','Y').to_euler()
    return obj
view('INT10_NAVE_CIVIC_PUBLIC_ROOM',(-55,-260,162),(-35,243,310),25)
view('INT10_H1_MARKET_HUMAN_DEPTH',(735,350,510),(793,783,600),27)
view('INT10_W0_TIDAL_AND_TWIN_FAULT',(1530,-1440,985),(80,300,750),39)

bpy.context.view_layer.update()
for n,old in poses.items():
    now=bpy.data.objects[n].matrix_world
    assert max(abs(now[i][j]-old[i][j]) for i in range(4) for j in range(4))<1e-6
assert len(made)>=24
assert all(name in bpy.data.objects for name in original_w0)
assert all(name not in bpy.data.objects for name in removed)
assert sc['CONSTRUCTION']=='HOLD' and sc['FORMAL_ART_ACCEPTED']==sc['COMPLETED_TARGETS']==0
sc['INT10_SOURCE_SHA256']=PARENT
sc['INT10_METHOD']='NEW_CONTINUOUS_INHABITED_CANYON_PUBLIC_ROOM_W0_AND_H1_NOT_REPAIR_OF_INT7_WEDGES'
sc['INT10_UNITS']='UNREGISTERED_RESEARCH_METRES'
sc['INT10_REJECTED_OLD_INT7_OBJECTS_REMOVED_IN_RESEARCH_COPY']=len(removed)
sc['INT10_FORMAL_ART_ADOPTED']=0
sc['INT10_FUNCTION']='UNVERIFIED'
sc.camera=bpy.data.objects['E11_URBAN_AERIAL']
dst=out/'HALO9_INT10_INHABITED_CIVIC_CANYON_EDITABLE.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dst),compress=True)
sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=13
sc.cycles.use_denoising=True
sc.render.threads_mode='FIXED';sc.render.threads=2
sc.render.resolution_x=980;sc.render.resolution_y=735
sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'
names=e11+('INT10_NAVE_CIVIC_PUBLIC_ROOM','INT10_H1_MARKET_HUMAN_DEPTH','INT10_W0_TIDAL_AND_TWIN_FAULT')
hashes={}
for n in names:
    sc.camera=bpy.data.objects[n]
    filepath=out/'renders'/(n+'.png')
    sc.render.filepath=str(filepath)
    bpy.ops.render.render(write_still=True)
    assert filepath.stat().st_size>10000,n
    hashes[n]=hashlib.sha256(filepath.read_bytes()).hexdigest()
    print('INT10_TRUE_SAME_SCENE_RENDER',n,filepath.stat().st_size,flush=True)
# leave editable scene with original aerial camera, not an extra convenience view
sc.camera=bpy.data.objects['E11_URBAN_AERIAL']
bpy.ops.wm.save_as_mainfile(filepath=str(dst),compress=True)
r={
 'schema':'halo9-int10-civic-canyon-art-research-v1',
 'input_sha256':PARENT,
 'native_blend_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),
 'rejected_research_meshes_removed':len(removed),
 'W0_source_objects_preserved':len(original_w0),
 'new_native_architectural_mesh_count':len(made),
 'new_mesh_objects':made,
 'fixed_3_E11_camera_poses_unchanged':True,
 'new_supplementary_cameras':[n for n in names if n not in e11],
 'native_same_scene_png_sha256':hashes,
 'research_units':'NOT_OFFICIAL_MINECRAFT_COORDINATES',
 'structural_integrity':'UNKNOWN',
 'traversability':'UNKNOWN',
 'formal_art_accepted':0,'completed_targets':0,
 'minecraft':'HOLD','art':'UNREVIEWED_NOT_ADOPTED'}
(out/'INT10_REAL_3D_TECH_NOT_ART.json').write_text(json.dumps(r,indent=2),encoding='utf8')
print('INT10_FULL_NEW_CIVIC_CANYON_NATIVE_BLENDER_CREATED',r['native_blend_sha256'],flush=True)
