"""R4-E2 native atelier. One authored composition, not a city generator.
Only `initial` creates geometry. Later operations open the saved scene and edit
named existing mesh vertices, after the coordinator has inspected real renders.
Research metres, NOT registered Minecraft or historical shared coordinates.
"""
import bpy, math, json, hashlib, sys
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
ARGS = sys.argv[sys.argv.index('--')+1:]
MODE = ARGS[0]
SCENE = ROOT/'E2_WORKING.blend'
VIEWS = ['urban_aerial','central_front','central_rear','east_seafront',
         'human_street','human_public_interior','human_sky_district']

def mesh(name, verts, faces, mat, collection=None):
    data=bpy.data.meshes.new(name); data.from_pydata(verts,[],faces); data.update()
    ob=bpy.data.objects.new(name,data)
    (collection or bpy.context.scene.collection).objects.link(ob)
    if mat: data.materials.append(mat)
    return ob

def mat(name,color,metal=.0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=.68
    return m

def solid(name, rings, material):
    # Explicitly authored section polygons, no equation-derived city envelope.
    n=len(rings[0]); verts=[v for ring in rings for v in ring]
    faces=[tuple(reversed(range(n))),tuple(range((len(rings)-1)*n,len(rings)*n))]
    for k in range(len(rings)-1):
        for j in range(n): faces.append((k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j))
    return mesh(name,verts,faces,material)

def prism(name,poly,z,h,material,lean=(0,0)):
    return solid(name,[[(x,y,z) for x,y in poly],[(x+lean[0],y+lean[1],z+h) for x,y in poly]],material)

def box(name,p,s,material):
    x,y,z=p;w,d,h=s
    return prism(name,[(x-w/2,y-d/2),(x+w/2,y-d/2),(x+w/2,y+d/2),(x-w/2,y+d/2)],z,h,material)

def ribbon(name,points,width,depth,material):
    verts=[]
    for i,p in enumerate(points):
        a=Vector(points[max(0,i-1)]);b=Vector(points[min(len(points)-1,i+1)])
        t=(b-a).normalized();n=Vector((-t.y,t.x,0)).normalized()*width/2
        v=Vector(p)
        verts += [tuple(v+n),tuple(v-n),tuple(v-n-Vector((0,0,depth))),tuple(v+n-Vector((0,0,depth)))]
    return solid(name,[verts[i:i+4] for i in range(0,len(verts),4)],material)

def snapshot():
    out={}
    for ob in bpy.data.objects:
        if ob.type=='MESH':
            raw={'vertices':[list(v.co) for v in ob.data.vertices], 'polygons':[list(p.vertices) for p in ob.data.polygons], 'matrix':[list(r) for r in ob.matrix_world]}
            out[ob.name]=hashlib.sha256(json.dumps(raw,sort_keys=True).encode()).hexdigest()
    cams={o.name:{'matrix':[list(r) for r in o.matrix_world],'lens':o.data.lens,'clip':[o.data.clip_start,o.data.clip_end]} for o in bpy.data.objects if o.type=='CAMERA'}
    return {'meshes':out,'cameras':cams}

def save(stage):
    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(SCENE),compress=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/(stage+'.blend')),compress=True,copy=True)
    (ROOT/(stage+'_geometry.json')).write_text(json.dumps(snapshot(),indent=2))

def initial():
    if SCENE.exists(): raise FileExistsError('Do not overwrite an existing atelier scene')
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    pearl=mat('Pearl ceramic / principal mass',(.66,.73,.75),.18)
    cut=mat('Dark titanium / inhabited cut faces',(.12,.20,.24),.15)
    stone=mat('Pale civic stone',(.43,.50,.51))
    bronze=mat('Warm public thresholds',(.40,.27,.13),.2)
    green=mat('Garden soil and planting mass',(.10,.22,.16))
    sea=mat('Eastern inland sea',(.055,.16,.20),.3)
    terrain=mat('W0 mineral basin',(.19,.25,.28))
    glass=mat('Recessed glazing',(.055,.11,.14),.25)

    # Public experience first: street mouth -> vast inhabited nave -> daylight
    # fissure. Main public datum +130m, a gently rising 1.6km ground causeway.
    prism('CIVIC_NAVE_FOUNDATION',[(-680,-700),(400,-650),(720,120),(510,740),(-510,890),(-900,230)],100,30,stone)
    ribbon('GROUND_PROCESSIONAL_RISE',[(0,-2400,0),(0,-1600,0),(0,-950,65),(0,-600,130),(40,-150,130)],170,16,stone)
    # Wide island districts at the nave floor; not a field of repeated boxes.
    prism('NAVE_LIBRARY_COURT',[(-570,-150),(-220,-180),(-200,40),(-360,200),(-620,80)],130,18,bronze)
    prism('NAVE_CIVIC_FORUM',[(150,-60),(390,-120),(590,120),(430,360),(130,260)],130,12,stone)
    ribbon('NAVE_NORTH_PUBLIC_STREET',[(-240,-490,130),(-360,-50,130),(-280,400,130),(40,640,130),(320,450,130)],32,8,bronze)
    # Freestanding civic rooms are hollow around an actual courtyard.
    def court(name,cx,cy,z,w,d,h):
        # Four unequal occupied wings; the inside is actual empty space.
        box(name+'_WEST',(cx-w/2+9,cy,z),(18,d,h),stone)
        box(name+'_NORTH',(cx,cy+d/2-9,z),(w,18,h*1.12),pearl)
        box(name+'_EAST',(cx+w/2-9,cy+12,z),(18,d-24,h*.83),stone)
        box(name+'_SOUTH_L',(cx-w/3,cy-d/2+9,z),(w/3,18,h*.65),pearl)
        box(name+'_SOUTH_R',(cx+w/3,cy-d/2+9,z),(w/3,18,h*.65),pearl)
    court('PUBLIC_ARCHIVE',-435,-10,148,210,190,90)
    court('PUBLIC_ASSEMBLY',335,140,142,180,200,110)

    # Lower western shell: a deep inhabited C-section, tapering and shifting
    # with altitude. The south and east remain open as genuine civic fissures.
    west=[(-300,-1040),(-1030,-920),(-1510,-270),(-1390,720),(-760,1270),(50,1110),(280,680),(-300,840),(-810,680),(-960,20),(-650,-490),(-250,-650)]
    def ring(poly,z,sx,sy,dx,dy): return [(x*sx+dx,y*sy+dy,z) for x,y in poly]
    solid('ALPHA_WEST_INHABITED_SHELL',[
        ring(west,0,.88,.93,0,0),ring(west,260,1.02,1.0,-40,0),
        ring(west,760,.98,.91,15,90),ring(west,1240,.86,.80,0,190),
        ring(west,1650,.58,.59,-120,340),ring(west,1870,.27,.35,-180,500)],pearl)
    # Upper displaced eastern shell: thick inhabited volume, diagonal underside
    # opening towards the nave; it is not an attached flat platform.
    east=[(-190,-650),(590,-870),(1230,-380),(1350,340),(930,1010),(150,1170),(-190,860),(400,710),(730,350),(680,-120),(240,-390),(-180,-370)]
    solid('ALPHA_EAST_DISPLACED_SHELL',[
        ring(east,1010,.60,.65,320,200),ring(east,1270,.93,.85,200,120),
        ring(east,1660,1.02,.93,180,100),ring(east,2110,.86,.77,260,190),
        ring(east,2510,.48,.46,400,320),ring(east,2770,.13,.18,520,470)],pearl)
    # Slanted rear spine with explicitly unequal section outlines; the gap
    # between shell and spine is a deep, daylighted diagonal urban canyon.
    solid('BETA_OBLIQUE_SPINE',[
        [(-480,940,0),(-80,850,0),(280,1180,0),(-180,1530,0)],
        [(-250,920,900),(120,820,900),(460,1110,900),(70,1390,900)],
        [(80,1000,1800),(350,890,1800),(650,1130,1800),(310,1370,1800)],
        [(520,1100,2850),(650,1050,2850),(850,1220,2850),(690,1320,2850)],
        [(850,1190,3290),(875,1180,3290),(910,1220,3290),(880,1250,3290)]],cut)

    # Inhabited cut-section: real deep streets, courtyard wings and substantial
    # neighborhood volumes nested within the shell at multiple altitudes.
    prism('H1_INHABITED_TERRAIN',[(-780,-350),(-230,-480),(30,-180),(-100,500),(-520,730),(-850,340)],1040,80,cut)
    ribbon('H1_PUBLIC_PROMENADE',[(-610,-350,1120),(-500,-140,1120),(-430,130,1120),(-290,390,1120)],42,10,stone)
    court('H1_SCHOOL',-650,160,1120,150,170,65)
    court('H1_RESIDENTIAL_COURT_A',-660,-140,1120,150,145,78)
    court('H1_RESIDENTIAL_COURT_B',-290,170,1120,130,160,96)
    court('H1_PUBLIC_MARKET',-310,-190,1120,120,140,42)
    prism('H1_GARDEN',[(-570,360),(-420,330),(-350,490),(-490,580)],1120,3,green)
    # Horizontal public cuts are occupied, deep sectional precincts, with
    # irregular outlines and clear thresholds. No thin external shelf stack.
    prism('EAST_CIVIC_SECTION',[(570,-380),(1040,-200),(1080,350),(800,650),(490,470),(660,100)],1520,95,cut)
    court('EAST_CONSERVATORY',860,210,1615,210,190,110)
    court('EAST_RESEARCH_COURT',830,-130,1615,160,150,130)
    ribbon('TRANSVERSE_SKY_TRANSIT',[(-540,500,1120),(-110,580,1270),(240,620,1440),(690,420,1615)],38,20,bronze)
    ribbon('PUBLIC_ASCENT_WEST',[(-700,-400,130),(-920,70,350),(-810,460,700),(-560,500,1120)],55,30,cut)
    # Lift/station expressed as a habitable fissure edge, not an unconnected
    # transport line. Operational/walkability certification remains pending.
    prism('WEST_LIFT_AND_STATION',[(-765,330),(-690,310),(-630,390),(-710,440)],130,990,bronze,lean=(100,80))
    box('GROUND_ARRIVAL_STATION',(-165,-1500,0),(160,210,45),cut)
    ribbon('METRO_AXIS_1_STUDY',[(-4200,-3200,0),(0,-1600,0),(1900,-650,0),(4500,850,0)],65,10,stone)
    ribbon('METRO_AXIS_2_STUDY',[(-4200,700,0),(-1700,400,0),(-850,250,100)],55,12,stone)
    ribbon('METRO_AXIS_3_STUDY',[(1500,3700,0),(600,2100,0),(350,900,130)],50,10,stone)

    # W0 study terrain: north mountains, west cliff, east sea and SW void.
    prism('W0_BASIN_STUDY',[(-5200,-5000),(5200,-5000),(5200,5000),(-5200,5000)],-110,105,terrain)
    prism('W0_EAST_SEA_STUDY',[(1900,-3500),(5200,-3500),(5200,4900),(2500,3900),(1700,1600)],-4,2,sea)
    solid('W0_NORTH_MOUNTAIN_STUDY',[
        [(-5100,3000,-5),(-3100,2700,-5),(-1000,3100,-5),(1000,2900,-5),(2800,3700,-5),(5100,4600,-5),(5100,5200,-5),(-5100,5200,-5)],
        [(-4800,4200,700),(-3000,3700,1500),(-1200,4100,950),(700,3900,1800),(2400,4400,700),(4800,5100,1100),(4800,5200,900),(-4800,5200,600)]],terrain)
    prism('W0_WEST_CLIFF_STUDY',[(-5200,-1400),(-4100,-1250),(-3800,100),(-4250,2600),(-5200,3200)],-5,420,terrain)
    # All 30 research entities share this scene. Empty markers deliberately do
    # not render as fake buildings; registry states NOT MADE explicitly.
    scope=['M247-C','W0']+[f'H{i}' for i in range(1,7)]+[f'SB{i:02}' for i in range(1,17)]+[f'V{i}' for i in range(1,4)]+[f'METRO_AXIS_{i}' for i in range(1,4)]
    reg=[];col=bpy.data.collections.new('30_TARGET_REGISTRY__RESEARCH_ONLY');bpy.context.scene.collection.children.link(col)
    for i,name in enumerate(scope):
        ob=bpy.data.objects.new(name+'__STATUS_MARKER',None);col.objects.link(ob);ob.empty_display_type='PLAIN_AXES';ob.empty_display_size=120
        if name=='M247-C': p=(0,0,0);status='INITIAL_MASS_PUBLIC_AND_RESIDENTIAL_STUDY_UNFINISHED'
        elif name=='W0': p=(0,0,-5);status='ROUGH_TERRAIN_ONLY_UNFINISHED'
        elif name=='H1': p=(-500,0,1120);status='PARTIAL_COURTYARD_STUDY_UNFINISHED'
        else: p=(0,0,0);status='NOT_MADE_UNLOCATED_OFFICIAL_ANCHORS_UNVERIFIED'
        if name.startswith('METRO'):status='PARTIAL_ROUTE_STUDY_UNFINISHED'
        ob.location=p;ob['status']=status;ob['official_coordinates_verified']=False
        reg.append({'target':name,'status':status,'marker':ob.name,'research_position':p,'official_coordinates_verified':False})
    (ROOT/'30_TARGETS.json').write_text(json.dumps(reg,indent=2))
    # Lighting held fixed across all review rounds, CPU only.
    scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=12
    scene.cycles.use_denoising=True;scene.render.threads_mode='FIXED';scene.render.threads=2
    scene.cycles.max_bounces=4;scene.cycles.diffuse_bounces=2;scene.cycles.glossy_bounces=2
    scene.render.resolution_x=900;scene.render.resolution_y=600;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
    scene.world.color=(.3,.3,.3);scene.world.use_nodes=True
    bg=scene.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.58,.70,.85,1);bg.inputs['Strength'].default_value=.55
    data=bpy.data.lights.new('Fixed afternoon sun','SUN');data.energy=2.2;data.angle=.10
    sun=bpy.data.objects.new('Fixed afternoon sun',data);scene.collection.objects.link(sun);sun.rotation_euler=(math.radians(28),math.radians(-24),math.radians(-35))
    cameras=[
        ('urban_aerial',(7900,-10000,7200),(0,300,800),42),
        ('central_front',(200,-6800,2000),(0,350,1400),48),
        ('central_rear',(-1800,6300,2400),(0,300,1400),48),
        ('east_seafront',(6400,-2300,1500),(0,300,1400),44),
        ('human_street',(0,-1450,16.65),(0,-450,650),24),
        ('human_public_interior',(0,-500,131.65),(100,650,650),21),
        ('human_sky_district',(-500,-140,1121.65),(-430,300,1160),24)]
    # Ground rise is 15m at y=-1450; eye height is datum +1.65m.
    for name,p,target,lens in cameras:
        data=bpy.data.cameras.new(name);data.lens=lens;data.clip_start=.1;data.clip_end=40000
        ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob);ob.location=p
        ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
    scene['research_only']=True;scene['art_status']='UNREVIEWED';scene['minecraft']='HOLD'
    scene['basis_head']='f14e8561a5a8d169d7995c83f47020a6161d5861'
    scene['official_coordinates_verified']=False
    save('R0')

def render(stage):
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/(stage+'.blend')))
    dest=ROOT/'renders'/stage;dest.mkdir(parents=True,exist_ok=True)
    for name in VIEWS:
        bpy.context.scene.camera=bpy.data.objects[name]
        bpy.context.scene.render.filepath=str(dest/(name+'.png'))
        bpy.ops.render.render(write_still=True)
        print('VIEW_COMPLETE',stage,name,flush=True)

def difference(target, cutter):
    ob=bpy.data.objects[target];bpy.context.view_layer.objects.active=ob
    mod=ob.modifiers.new('Authored civic excavation','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True)

def edit1():
    # Decisions made AFTER direct inspection of all seven R0 camera PNGs.
    bpy.ops.wm.open_mainfile(filepath=str(SCENE))
    assert snapshot()==json.loads((ROOT/'R0_geometry.json').read_text()), 'Unexpected source geometry'
    pearl=bpy.data.materials['Pearl ceramic / principal mass']
    east=bpy.data.objects['ALPHA_EAST_DISPLACED_SHELL']
    for v in east.data.vertices:
        z=v.co.z
        # Eliminate the rounded closed crown, extend the upper inhabited
        # landmass diagonally towards the northeast, making its cut legible.
        if z>2000:
            f=(z-2000)/770;v.co.x+=330*f;v.co.y+=250*f;v.co.z-=180*f
        if z<1300:v.co.x+=100
    cutter=solid('TEMP_EAST_DIAGONAL_CIVIC_EXCAVATION',[
        [(-1000,-2000,850),(2400,-2000,850),(2400,-650,850),(-1000,-650,850)],
        [(-1000,-2000,1700),(2400,-2000,1700),(2400,80,1700),(-1000,80,1700)],
        [(-1000,-2000,3000),(2400,-2000,3000),(2400,800,3000),(-1000,800,3000)]],None)
    difference(east.name,cutter)
    west=bpy.data.objects['ALPHA_WEST_INHABITED_SHELL']
    for v in west.data.vertices:
        if v.co.z>1200:
            f=(v.co.z-1200)/670;v.co.x-=200*f;v.co.y+=200*f
        # Retreat broad southern face from the processional entry.
        if v.co.y < -400 and v.co.z<900:v.co.y+=180*(1-v.co.z/1100)
    # A tall diagonal inhabited opening through the west mass; daylight and
    # the public ascent can actually pass through the former blind shell.
    cutter=solid('TEMP_WEST_URBAN_CANYON',[
        [(-1800,-480,500),(-650,-480,500),(-650,-180,500),(-1800,-180,500)],
        [(-1800,-100,1200),(-450,-100,1200),(-450,250,1200),(-1800,250,1200)],
        [(-1800,320,1800),(-300,320,1800),(-300,640,1800),(-1800,640,1800)]],None)
    difference(west.name,cutter)
    # Existing spine: less arbitrary needle, deeper rear-facing civic mass.
    spine=bpy.data.objects['BETA_OBLIQUE_SPINE']
    for v in spine.data.vertices:
        if v.co.z>2800:v.co.z-=300;v.co.y+=150
        if 800<v.co.z<2000:v.co.y+=180
    cutter=solid('TEMP_SPINE_PUBLIC_LIGHT_WELL',[
        [(-200,900,500),(300,900,500),(300,1800,500),(-200,1800,500)],
        [(200,900,1700),(550,900,1700),(550,1800,1700),(200,1800,1700)]],None)
    difference(spine.name,cutter)
    # Correct coincident floor surfaces, identified as black patches in R0.
    for name in ['GROUND_PROCESSIONAL_RISE','H1_PUBLIC_PROMENADE','NAVE_NORTH_PUBLIC_STREET']:
        for v in bpy.data.objects[name].data.vertices:v.co.z+=.25
    bpy.context.scene['art_status']='R0_ART_REJECT__R1_AWAITING_REVIEW'
    save('R1')

def edit2():
    # Independent second decision, after viewing all seven R1 images.
    # Undoing the architectural 'shelf' reading requires occupied depth and
    # excavated public rooms, rather than surface ornaments or a new model.
    bpy.ops.wm.open_mainfile(filepath=str(SCENE))
    assert snapshot()==json.loads((ROOT/'R1_geometry.json').read_text()), 'Unexpected source geometry'
    for name,base in [('H1_INHABITED_TERRAIN',1040),('EAST_CIVIC_SECTION',1520)]:
        ob=bpy.data.objects[name]
        for v in ob.data.vertices:
            if abs(v.co.z-base)<.1:
                if name.startswith('H1'):
                    v.co.z=700+max(0,min(1,(v.co.y+350)/1080))*180
                    v.co.x=(v.co.x+400)*.72-400
                else:
                    v.co.z=1140+max(0,min(1,(v.co.y+380)/1030))*190
                    v.co.x=(v.co.x-800)*.72+800
        ob.data.update()
    # Real public gallery through the H1 inhabited rock: the R1 camera looked
    # directly into a featureless wall. This opens that wall to the north.
    c=solid('TEMP_H1_CIVIC_CANYON',[
        [(-900,360,1120),(-180,360,1120),(-180,1550,1120),(-900,1550,1120)],
        [(-790,400,1440),(-160,400,1440),(-160,1550,1440),(-790,1550,1440)]],None)
    difference('ALPHA_WEST_INHABITED_SHELL',c)
    # Recut the public nave's blank rear wall as a long civic chamber and
    # northward arrival threshold, retaining side and overhead mass.
    c=solid('TEMP_NAVE_NORTH_ROOM',[
        [(-330,510,130),(350,510,130),(350,1600,130),(-330,1600,130)],
        [(-210,550,660),(510,550,660),(510,1600,660),(-210,1600,660)]],None)
    difference('ALPHA_WEST_INHABITED_SHELL',c)
    c=solid('TEMP_SPINE_NAVE_CONTINUATION',[
        [(-330,510,130),(350,510,130),(350,1600,130),(-330,1600,130)],
        [(-210,550,660),(510,550,660),(510,1600,660),(-210,1600,660)]],None)
    difference('BETA_OBLIQUE_SPINE',c)
    # East seafront: three differently proportioned major inhabited chambers
    # and roof cuts, not a repeated facade pattern. These are real voids.
    cuts=[('LOWER_SEA_ROOM',[(850,-300),(1800,-300),(1800,200),(850,200)],1320,190),
          ('UPPER_SEA_ROOM',[(1060,180),(1800,180),(1800,700),(1060,700)],1750,250),
          ('CROWN_OPEN_COURT',[(500,380),(830,380),(830,1000),(500,1000)],2180,700)]
    for name,poly,z,h in cuts:
        difference('ALPHA_EAST_DISPLACED_SHELL',prism('TEMP_'+name,poly,z,h,None))
    # Give the west roof a directional split skyline instead of a round cap.
    west=bpy.data.objects['ALPHA_WEST_INHABITED_SHELL']
    for v in west.data.vertices:
        if v.co.z>1200:
            f=max(0,min(1,(600-v.co.y)/800));v.co.z-=250*f;v.co.x-=160*f
    # Existing occupied terrain is excavated into a section with deep public
    # rooms. The original top streets are retained, not floating thin decks.
    for name,poly,z,h in [
        ('H1_INHABITED_TERRAIN',[(-1000,-220),(-390,-220),(-390,50),(-1000,50)],850,150),
        ('EAST_CIVIC_SECTION',[(800,-500),(1300,-500),(1300,220),(800,220)],1330,180)]:
        difference(name,prism('TEMP_SECTION_PUBLIC_ROOM',poly,z,h,None))
    # Move/scale existing courtyard-wing geometry to establish proper streets
    # and a larger entrance square, not adding decorative street objects.
    for ob in list(bpy.data.objects):
        if ob.type=='MESH' and ob.name.startswith('H1_RESIDENTIAL_COURT_B'):
            for v in ob.data.vertices:
                v.co.x+=45;v.co.y+=65
                if v.co.z>1120:v.co.z=1120+(v.co.z-1120)*.72
    # Real passages cut into two pre-existing public building wings. These
    # openings are spatial changes; no window textures, greebles or lights.
    for name,cx,cy,z in [('H1_PUBLIC_MARKET_WEST',-361,-190,1120),('PUBLIC_ASSEMBLY_NORTH',335,231,142)]:
        c=box('TEMP_PUBLIC_DOOR',(cx,cy,z-.1),(40,55,16),None)
        difference(name,c)
    bpy.context.scene['art_status']='R1_ART_REJECT__R2_AWAITING_REVIEW'
    save('R2')

def floor_finish():
    # Technical completion of R2, not a third art cycle. R1 lifted streets
    # by 25cm to remove z-fighting, inadvertently reducing two eye heights.
    # Keep ALL camera matrices. Restore street datums and lower duplicate
    # supporting faces instead. No image from the draft R2 is the final proof.
    bpy.ops.wm.open_mainfile(filepath=str(SCENE))
    for name in ['GROUND_PROCESSIONAL_RISE','H1_PUBLIC_PROMENADE','NAVE_NORTH_PUBLIC_STREET']:
        for v in bpy.data.objects[name].data.vertices:v.co.z-=.25
    for name,top in [('CIVIC_NAVE_FOUNDATION',130),('H1_INHABITED_TERRAIN',1120)]:
        for v in bpy.data.objects[name].data.vertices:
            if abs(v.co.z-top)<.01:v.co.z-=.25
    bpy.context.scene['art_status']='ART_REJECT__NOT_ADOPTED__CITY_MASTER_INCOMPLETE'
    save('R2')

def inspect():
    bpy.ops.wm.open_mainfile(filepath=str(SCENE))
    deps=bpy.context.evaluated_depsgraph_get();s=bpy.context.scene
    evidence={'scene':SCENE.name,'status':'PRODUCTION_INSPECTION_NOT_E1B_RETEST_NOT_ART_PASS',
      'meshes':sum(o.type=='MESH' for o in s.objects),'cameras':{},'central_bounds':{},
      'scope_count':len(json.loads((ROOT/'30_TARGETS.json').read_text())),
      'art':'REJECT','city_master_complete':False,'minecraft':'HOLD','coordinate_system':'UNREGISTERED_RESEARCH_METRES'}
    for name in VIEWS:
        c=bpy.data.objects[name];o=c.matrix_world.translation
        forward=c.matrix_world.to_quaternion()@Vector((0,0,-1))
        hit,loc,n,i,ob,m=s.ray_cast(deps,o,Vector((0,0,-1)),distance=5000)
        fh,fl,fn,fi,fo,fm=s.ray_cast(deps,o,forward,distance=10000)
        evidence['cameras'][name]={'eye':list(o),'support':ob.name if hit else None,
          'eye_above_support_m':round(o.z-loc.z,4) if hit else None,
          'forward_hit':fo.name if fh else None,'forward_distance_m':round((fl-o).length,3) if fh else None}
    for name in ['ALPHA_WEST_INHABITED_SHELL','ALPHA_EAST_DISPLACED_SHELL','BETA_OBLIQUE_SPINE']:
        ob=bpy.data.objects[name];vs=[ob.matrix_world@v.co for v in ob.data.vertices]
        lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)]
        evidence['central_bounds'][name]={'min_m':lo,'max_m':hi,'size_m':[hi[i]-lo[i] for i in range(3)],'vertices':len(vs),'polygons':len(ob.data.polygons)}
    (ROOT/'PRODUCTION_INSPECTION.json').write_text(json.dumps(evidence,indent=2))
    print(json.dumps(evidence,indent=2))

if MODE=='initial': initial()
elif MODE=='render': render(ARGS[1])
elif MODE=='edit1': edit1()
elif MODE=='edit2': edit2()
elif MODE=='floor_finish': floor_finish()
elif MODE=='inspect': inspect()
else: raise RuntimeError('Editing operations added only after real visual review')
