"""New authored section, not a transformation of rejected meshes.
Python-assisted polygon authoring; not GUI brush sculpting. Research metres.
Run once; subsequent edits must open the saved source instead of rebuilding it.
"""
import bpy, math, json, pathlib, hashlib, struct
from mathutils import Vector
ROOT=pathlib.Path(__file__).parent
SOURCE=ROOT/'reference/HALO9_INT21_M247C_OPEN_CIVIC_CANYON_RESEARCH.blend'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='9b950f0b9d5315605d5dc0bec252950e0c150739c94249a201667c9e2d675a27'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
S=bpy.context.scene
def signature(o):
    result={'matrix':list(sum((list(r) for r in o.matrix_world),[]))}
    if o.type=='MESH':
        h=hashlib.sha256()
        for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
        for p in o.data.polygons:h.update(struct.pack('<%di'%len(p.vertices),*p.vertices))
        result['mesh']=h.hexdigest()
    if o.type=='CAMERA':result.update(lens=o.data.lens,sensor_width=o.data.sensor_width,clip_end=o.data.clip_end)
    return result
protected={o.name:signature(o) for o in S.objects if o.name.startswith('W0_') or o.name.startswith('E11_') and o.type=='CAMERA'}
(ROOT/'protected_before.json').write_text(json.dumps(protected,indent=2))
# Only source W0/cameras retained in the isolated copy. No old architecture is used.
removed=[]
for o in list(bpy.data.objects):
    if o.name not in protected:
        removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
S.name='GATE_B_TIDAL_CIVIC_SECTION_RESEARCH'
C=bpy.data.collections.new('GATE_B_NEW_ARCHITECTURE');S.collection.children.link(C)
def material(name,rgb,metal=0,rough=.5,emit=0):
    m=bpy.data.materials.new('GB_'+name);m.diffuse_color=(*rgb,1);m.use_nodes=True
    n=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    n.inputs['Base Color'].default_value=(*rgb,1);n.inputs['Metallic'].default_value=metal;n.inputs['Roughness'].default_value=rough
    n.inputs['Emission Color'].default_value=(*rgb,1);n.inputs['Emission Strength'].default_value=emit
    return m
pearl=material('ivory_titanium',(.63,.68,.66),.28,.32)
dark=material('structural_graphite',(.035,.065,.075),.35,.43)
glass=material('recessed_blue_glass',(.055,.16,.19),.62,.24)
bronze=material('anodized_champagne',(.42,.27,.12),.55,.35)
paving=material('pale_public_stone',(.5,.46,.36),.05,.65)
green=material('living_garden',(.09,.2,.11),0,.85)
light=material('warm_rooms',(.65,.36,.13),.1,.5,.2)
def mesh(name,vs,fs,ma,bevel=0):
    me=bpy.data.meshes.new('GB_'+name);me.from_pydata(vs,[],fs);me.update()
    ob=bpy.data.objects.new('GB_'+name,me);C.objects.link(ob);me.materials.append(ma)
    if bevel:
        mod=ob.modifiers.new('edge_radii','BEVEL');mod.width=bevel;mod.segments=2
    return ob
def extrude(name,poly,z,h,ma=pearl):
    n=len(poly);v=[(x,y,z) for x,y in poly]+[(x,y,z+h) for x,y in poly]
    return mesh(name,v,[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],ma,min(1.2,abs(h)/8))
def section(name,poly,y,depth,ma=pearl):
    # Explicit X/Z contour makes both inhabitable depth and a shaped soffit.
    n=len(poly);v=[(x,y,z) for x,z in poly]+[(x,y+depth,z) for x,z in poly]
    return mesh(name,v,[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],ma,1.5)
def beam(name,a,b,w,d,ma=pearl):
    a,b=Vector(a),Vector(b);q=(b-a).to_track_quat('Z','Y');l=(b-a).length
    vs=[tuple(a+q@Vector((x*w/2,y*d/2,z*l))) for z in (0,1) for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    return mesh(name,vs,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],ma,min(w/12,1))
def rail(name,pts,r,ma=bronze):
    cu=bpy.data.curves.new('GB_'+name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=1
    sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
    for p,co in zip(sp.points,pts):p.co=(*co,1)
    o=bpy.data.objects.new('GB_'+name,cu);C.objects.link(o);cu.materials.append(ma);return o
def stairs(name,x,y,z,width,run,rise,n):
    for i in range(n):extrude(name+str(i),[(x,y+i*run/n),(x+width,y+i*run/n),(x+width,y+(i+1)*run/n),(x,y+(i+1)*run/n)],z+i*rise/n,rise/n,paving)
def facade(name,a,b,z,stories,step=7):
    a,b=Vector((*a,0)),Vector((*b,0));length=(b-a).length;direction=(b-a).normalized();count=max(1,round(length/step))
    for floor in range(stories):
        zz=z+floor*5.5
        beam(name+'_sill'+str(floor),a+Vector((0,0,zz)),b+Vector((0,0,zz)),.7,1.0,pearl)
        for j in range(count):
            p=a+(b-a)*(j+.5)/count
            beam(name+'_mullion',p+Vector((0,0,zz)),p+Vector((0,0,zz+5.4)),.4,.7,bronze)
        # Glazing spans are recessed behind solid columns, not a flat solid building.
        beam(name+'_glazing',a+Vector((0,0,zz+2.6)),b+Vector((0,0,zz+2.6)),4.5,.22,glass)
def court(name,poly,z,stories):
    # Occupied perimeter is built as open galleries around a real courtyard.
    cx=sum(p[0] for p in poly)/len(poly);cy=sum(p[1] for p in poly)/len(poly)
    inner=[(cx+(x-cx)*.59,cy+(y-cy)*.59) for x,y in poly]
    for f in range(stories+1):
        for i,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):
            j=(i+1)%len(poly)
            extrude(name+'_gallery', [a,b,inner[j],inner[i]],z+f*5.5,1.1,pearl)
    for a,b in zip(poly,poly[1:]+poly[:1]):facade(name,a,b,z,stories)
    extrude(name+'_court_garden',inner,z+.1,.5,green)
    return inner
# Coastal landing enters a real 320m long public nave. Sea/W0 remain unchanged.
extrude('tidal_foundation',[(-750,-780),(-190,-900),(180,-720),(420,-200),(170,680),(-600,750),(-850,130)],-3,65,dark)
extrude('public_concourse',[(-280,-650),(135,-650),(280,-220),(230,610),(-260,650),(-390,-80)],62,10,paving)
extrude('arrival_quay',[(-520,-1000),(-330,-1030),(-200,-650),(-340,-610)],-3,12,paving)
stairs('harbor_ascent',-330,-820,9,60,170,63,42)
# Western urban buttress: contour is a thick inhabited stepped building, not an egg.
west=[(-700,55),(-700,650),(-590,650),(-590,900),(-440,1120),(-250,1240),(-125,1190),(-180,990),(-260,870),(-280,650),(-390,650),(-390,410),(-470,410),(-470,240),(-550,240),(-550,55)]
section('WEST_INHABITED_FRACTURE',west,60,580,dark)
# Exposed carved terraces face the nave; use separate wings with actual light courts.
court('library_lower',[(-550,30),(-340,30),(-310,300),(-510,340)],155,5)
court('archive_upper',[(-510,160),(-330,180),(-260,480),(-440,520)],420,7)
court('west_high_residence',[(-400,380),(-225,380),(-160,620),(-340,680)],740,8)
# The eastern inhabited ledge is the nave roof and H1 ground simultaneously.
east=[(300,60),(500,60),(565,245),(700,330),(1040,350),(1190,510),(1170,630),(940,710),(760,690),(645,560),(450,520),(340,350)]
section('EAST_OCCUPIED_URBAN_GROUND',east,390,500,dark)
extrude('H1_MARKET_GROUND',[(420,220),(960,220),(1140,420),(1080,760),(650,820),(390,540)],420,17,paving)
# Four giant ribs emerge from the inhabited west and terminate at the high city.
# The split is open in full 3D; no Boolean facade or cutaway camera is used.
for i,(y,shift) in enumerate([(-250,-35),(-50,0),(180,30),(420,90)]):
    left=[(-270+shift,72),(-235+shift,240),(-180+shift,350),(-90+shift,425),(60+shift,520),(150+shift,525),(20+shift,405),(-90+shift,310),(-170+shift,72)]
    right=[(340+shift,72),(280+shift,240),(220+shift,360),(240+shift,435),(350+shift,495),(510+shift,550),(525+shift,610),(330+shift,560),(170+shift,465),(140+shift,375),(190+shift,225),(240+shift,72)]
    section('NAVE_WEST_BRANCH_'+str(i),left,y,32,pearl)
    section('NAVE_EAST_BRANCH_'+str(i),right,y,32,pearl)
    beam('roof_purlin_W',(-90+shift,y,425),(-50+shift,y+190,450),13,18,pearl)
    beam('roof_purlin_E',(300+shift,y,510),(350+shift,y+190,550),13,18,pearl)
    # Occupied rooflets sit outside the split, retaining open daylight into the nave.
    section('roof_W_'+str(i),[(-420,450),(-180+shift,465),(20+shift,550),(40+shift,570),(-190+shift,495),(-420,485)],y,175,pearl)
    section('roof_E_'+str(i),[(330+shift,530),(650,610),(690,645),(330+shift,570)],y,175,pearl)
# Library galleries face public room, with real stairs and interior frontages.
for z,x,y in [(105,-265,-100),(155,-310,60),(210,-350,220)]:
    extrude('reading_balcony',[(x,y),(x+120,y),(x+120,y+170),(x,y+170)],z,6,paving)
    facade('reading_rooms',(x,y+160),(x+120,y+160),z+6,3)
    rail('library_balustrade',[(x+120,y,z+7.2),(x+120,y+170,z+7.2)],.35)
stairs('library_public_stairs',-270,-125,72,30,150,33,22)
stairs('library_upper_stairs',-310,60,111,26,130,44,30)
# H1: street view starts on the same 437m market ground as the inherited camera.
court('H1_school_courtyard',[(580,400),(700,400),(715,560),(595,580)],437,4)
court('H1_housing_east',[(870,340),(1000,375),(1020,550),(875,530)],437,9)
court('H1_housing_north',[(760,630),(935,615),(1000,735),(770,780)],437,12)
court('H1_housing_west',[(440,560),(555,575),(610,745),(465,740)],437,7)
# Market halls deliberately vary in section, leaving an open north/south street.
for x,y,width,depth,height in [(695,350,52,65,18),(800,430,48,95,24),(725,570,55,55,16)]:
    for dx in (0,width):beam('market_pier',(x+dx,y,437),(x+dx,y,437+height),1.6,1.6,bronze)
    section('market_fold',[(x-5,437+height),(x+width*.45,445+height),(x+width+5,437+height),(x+width+5,440+height),(x+width*.45,449+height),(x-5,440+height)],y,depth,pearl)
    for j in range(4):extrude('market_stall',[(x+j*width/4,y+4),(x+(j+1)*width/4-2,y+4),(x+(j+1)*width/4-2,y+10),(x+j*width/4,y+10)],437,1.1,light)
# Vertical movement has actual landings, twin shafts, and public bridges (function unverified).
for x in (360,395):
    beam('lift_shaft',(x,440,72),(x,440,850),8,12,glass)
    for z in (72,155,437,740):extrude('lift_landing',[(x-10,420),(x+28,420),(x+28,455),(x-10,455)],z,4,pearl)
beam('H1_station_bridge',(390,440,434),(540,440,434),7,35,pearl)
rail('transit_guideway',[(360,-550,50),(370,-100,60),(375,440,74),(370,440,740)],1.3,dark)
# Detached crown: broken occupied section rather than an oval loose boulder.
section('SEVERED_CROWN',[(50,1380),(160,1320),(360,1325),(520,1460),(500,1580),(340,1690),(290,1600),(340,1490),(250,1440),(110,1470)],740,260,pearl)
court('crown_habitat',[(100,755),(300,755),(390,940),(140,985)],1450,7)
# Human scale in the nave and H1, modelled as neutral silhouettes.
for x,y,z in [(0,-300,72),(15,-295,72),(-20,-290,72),(760,315,437),(775,330,437),(720,470,437)]:
    beam('human_body',(x,y,z+.3),(x,y,z+1.45),.5,.3,dark)
    beam('human_head',(x,y,z+1.5),(x,y,z+1.8),.3,.3,dark)
# Natural daylight, no emissive cyan used to disguise shape.
world=bpy.data.worlds.new('GB_overcast_daylight');world.use_nodes=True
bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.62,.73,.85,1);bg.inputs['Strength'].default_value=.6;S.world=world
ld=bpy.data.lights.new('GB_sun','SUN');ld.energy=2.5;ld.angle=.18
ob=bpy.data.objects.new('GB_sun',ld);C.objects.link(ob);ob.rotation_euler=(.45,-.55,-.45)
S.render.engine='CYCLES';S.cycles.device='CPU';S.cycles.samples=12;S.cycles.use_denoising=True
S.render.threads_mode='FIXED';S.render.threads=2
S.render.resolution_x=960;S.render.resolution_y=720;S.render.resolution_percentage=100
S.render.image_settings.file_format='PNG';S.render.film_transparent=False
S.unit_settings.system='METRIC';S.unit_settings.scale_length=1
assert all(signature(bpy.data.objects[n])==sig for n,sig in protected.items())
(ROOT/'R0_authoring_record.json').write_text(json.dumps({'method':'Python-assisted explicit polygon authoring, background Blender; no GUI brush; not live MCP','source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'excluded_source_objects':removed,'protected_names':list(protected),'new_object_count':len(C.objects),'art':'UNREVIEWED','function':'UNVERIFIED','construction':'HOLD'},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'GATE_B_R0.blend'))
print('GATE_B_NEW_SECTION_SAVED',len(C.objects))
