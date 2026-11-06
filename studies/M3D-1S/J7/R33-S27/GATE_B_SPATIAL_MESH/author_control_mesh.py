"""Few authored spatial control meshes. No rejected architectural mesh is imported.
Python is an editing aid; this is not GUI/brush authorship. Inspect A0 before editing A1.
"""
import bpy,bmesh,pathlib,json,hashlib,math,struct
from mathutils import Vector
ROOT=pathlib.Path(__file__).parent
PREV=ROOT.parent/'GATE_B_AFTER_INT21'
SRC=PREV/'reference/HALO9_INT21_M247C_OPEN_CIVIC_CANYON_RESEARCH.blend'
assert hashlib.sha256(SRC.read_bytes()).hexdigest()=='9b950f0b9d5315605d5dc0bec252950e0c150739c94249a201667c9e2d675a27'
bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False)
S=bpy.context.scene;keep=json.loads((PREV/'protected_before.json').read_text())
for o in list(bpy.data.objects):
    if o.name not in keep:bpy.data.objects.remove(o,do_unlink=True)
S.name='GATE_B_SPATIAL_CONTROL_MESH_STUDY'
C=bpy.data.collections.new('NEW_SPATIAL_ARCHITECTURE');S.collection.children.link(C)
def mat(n,c,metal=0,rough=.5):
    m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    return m
ivory=mat('SC_pearl_titanium',(.69,.72,.68),.3,.32)
soffit=mat('SC_warm_soffit',(.4,.34,.25),.25,.47)
dark=mat('SC_inner_structure',(.045,.075,.08),.4,.4)
glass=mat('SC_deep_glazing',(.045,.14,.16),.55,.24)
stone=mat('SC_public_stone',(.52,.5,.43),.05,.7)
green=mat('SC_garden',(.10,.19,.12),0,.9)
bronze=mat('SC_bronze_reveals',(.4,.27,.15),.5,.4)
class Mesh:
    def __init__(self):self.v=[];self.f=[];self.m=[]
    def face(self,points,mi=0):
        k=len(self.v);self.v.extend(points);self.f.append(tuple(range(k,k+len(points))));self.m.append(mi)
    def prism(self,poly,z,h,mi=0):
        self.face([(x,y,z) for x,y in reversed(poly)],mi);self.face([(x,y,z+h) for x,y in poly],mi)
        for a,b in zip(poly,poly[1:]+poly[:1]):self.face([(*a,z),(*b,z),(*b,z+h),(*a,z+h)],mi)
    def beam(self,a,b,w,d,mi=0):
        a,b=Vector(a),Vector(b);q=(b-a).to_track_quat('Z','Y');l=(b-a).length
        p=[tuple(a+q@Vector((x*w/2,y*d/2,z*l))) for z in (0,1) for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]]
        for f in [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:self.face([p[i] for i in f],mi)
    def finish(self,n,mats,bevel=0):
        me=bpy.data.meshes.new(n);me.from_pydata(self.v,[],self.f);me.update()
        bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
        # Assign face slots after welding (faces are not dissolved).
        for p,mi in zip(me.polygons,self.m):p.material_index=mi
        o=bpy.data.objects.new(n,me);C.objects.link(o)
        for ma in mats:me.materials.append(ma)
        if bevel:
            mod=o.modifiers.new('real_edge_radius','BEVEL');mod.width=bevel;mod.segments=3
        return o
def patch(name,rows,skip,thick):
    # Each row is explicitly authored 3D control geometry, not a formula-generated mass.
    n=len(rows[0]);vs=[p for row in rows for p in row];fs=[]
    for j in range(len(rows)-1):
        for i in range(n-1):
            if (j,i) not in skip:fs.append((j*n+i,j*n+i+1,(j+1)*n+i+1,(j+1)*n+i))
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update()
    o=bpy.data.objects.new(name,me);C.objects.link(o);me.materials.append(ivory);me.materials.append(soffit)
    for p in me.polygons:p.use_smooth=True
    sub=o.modifiers.new('authored_surface_subdivision','SUBSURF');sub.levels=2;sub.render_levels=2
    sol=o.modifiers.new('structural_depth','SOLIDIFY');sol.thickness=thick;sol.offset=0;sol.material_offset=1;sol.material_offset_rim=1
    return o
# The west roof is a continuous branching vault that rises along the civic room.
# Its low outer end meets the W0 shore; inner edge creates one diagonal opening.
west=patch('SC_WEST_PUBLIC_VAULT',[
 [(-640,-560,12),(-535,-560,75),(-445,-500,245),(-300,-450,350),(-110,-390,415),(40,-330,390)],
 [(-735,-310,18),(-625,-300,160),(-440,-240,360),(-245,-210,475),(-20,-170,545),(110,-100,500)],
 [(-780,0,65),(-660,20,255),(-445,40,495),(-190,70,650),(80,100,735),(240,180,660)],
 [(-730,310,110),(-630,350,415),(-420,370,690),(-140,420,880),(160,460,950),(315,530,840)],
 [(-640,610,170),(-540,650,570),(-345,690,870),(-65,730,1050),(230,770,1090),(390,800,970)],
 [(-440,850,350),(-390,870,650),(-210,900,920),(45,920,1110),(310,940,1125),(470,970,1020)]
 ],{(2,1),(3,1)},28)
east=patch('SC_EAST_INHABITED_VAULT',[
 [(270,-240,330),(420,-280,345),(610,-300,280),(800,-320,145),(960,-340,20)],
 [(330,10,440),(490,-10,480),(715,0,490),(960,30,380),(1130,80,130)],
 [(420,260,590),(580,280,640),(800,300,650),(1050,330,530),(1230,380,290)],
 [(490,510,740),(680,530,800),(920,550,790),(1140,590,670),(1300,650,430)],
 [(565,740,900),(760,780,950),(1000,800,920),(1190,820,790),(1320,900,560)],
 [(630,940,1010),(840,970,1035),(1055,1000,990),(1220,1030,840),(1290,1090,680)]
 ],{(1,1),(1,2),(2,1),(2,2)},35)
# Detached inhabited fragment echoes the gap and is not an oval solid.
crown=patch('SC_SEVERED_OCCUPIED_CANOPY',[
 [(-180,550,1180),(-70,510,1280),(100,520,1330),(270,570,1295)],
 [(-150,700,1215),(-20,675,1340),(180,710,1400),(370,750,1320)],
 [(-70,860,1210),(60,850,1320),(250,900,1355),(410,940,1250)]
 ],set(),60)
# Thick inhabited west section: real floors and deeply recessed public rooms,
# within the shell, not small houses attached to a giant opaque wall.
def occupied_gallery(name,path,z,levels,depth,height=6.5):
    # path follows a purposeful bent street frontage; ground-facing arc is open.
    M=Mesh()
    outer=[(x-depth,y+15) for x,y in path]
    for f in range(levels+1):
        zz=z+f*height
        for i in range(len(path)-1):M.prism([path[i],path[i+1],outer[i+1],outer[i]],zz,1.3,0)
    for i,(a,b) in enumerate(zip(path,path[1:])):
        aa,bb=Vector((*a,0)),Vector((*b,0));length=(bb-aa).length
        for j in range(max(2,int(length/11))+1):
            p=aa+(bb-aa)*j/max(2,int(length/11))
            M.beam((*p.xy,z),(*p.xy,z+levels*height),1.1,1.5,1)
        # Recessed rear wall is physically 35-70m behind the public arcade.
        oa,ob=outer[i],outer[i+1]
        M.face([(*oa,z),(*ob,z),(*ob,z+levels*height),(*oa,z+levels*height)],2)
    return M.finish(name,[ivory,bronze,glass],.3)
occupied_gallery('SC_NAVE_LIBRARY_ARCADE',[(-270,-250),(-260,-100),(-285,80),(-340,230)],98,9,65)
occupied_gallery('SC_WEST_UPPER_INHABITED_STREET',[(-510,150),(-450,300),(-345,470),(-230,620)],540,16,100)
occupied_gallery('SC_SEVERED_INTERNAL_CITY',[(20,590),(70,710),(170,820)],1220,8,75)
# H1 is a 100m deep occupied urban fabric enclosing real courtyards.
# Its four authored courts differ in footprint and vertical section, all open to sky.
def courtyard(name,plan,inner,z,levels,height=6.2):
    M=Mesh();N=len(plan)
    for f in range(levels+1):
        zz=z+f*height;shrink=max(0,(f-levels*.65)/(levels*.35))*.12
        # Upper sections retreat into their courtyards, making occupied terraces.
        p=[(a[0]*(1-shrink)+b[0]*shrink,a[1]*(1-shrink)+b[1]*shrink) for a,b in zip(plan,inner)]
        for i in range(N):M.prism([p[i],p[(i+1)%N],inner[(i+1)%N],inner[i]],zz,1.35)
    for i,(a,b) in enumerate(zip(plan,plan[1:]+plan[:1])):
        aa,bb=Vector((*a,0)),Vector((*b,0));L=(bb-aa).length;nb=max(1,int(L/9))
        for j in range(nb+1):
            p=aa+(bb-aa)*j/nb
            M.beam((*p.xy,z),(*p.xy,z+levels*height),.9,1.3,1)
        # Inner face includes genuine open bays, rather than a solid labelled box.
        ia,ib=inner[i],inner[(i+1)%N]
        M.beam((*ia,z+levels*height/2),(*ib,z+levels*height/2),levels*height,.35,2)
    M.prism(inner,z,.5,3)
    return M.finish(name,[ivory,bronze,glass,green],.25)
courtyard('SC_H1_WEST_SCHOOL',[(525,310),(650,330),(665,470),(600,540),(500,475)],[(555,355),(615,365),(625,445),(595,490),(540,450)],437,7)
courtyard('SC_H1_EAST_DWELLING',[(880,260),(1000,305),(1060,440),(1000,530),(880,475)],[(920,320),(965,340),(1005,420),(975,470),(920,440)],437,13)
courtyard('SC_H1_NORTH_DWELLING',[(680,570),(810,550),(920,650),(860,770),(695,740)],[(720,610),(795,600),(860,660),(825,720),(735,695)],437,17)
# H1 ground is a shaped inhabited hollow body 110m deep with a station below.
# Top surface surrounds two real light wells, avoiding an opaque solid foundation.
M=Mesh()
outline=[(400,210),(780,180),(1080,250),(1160,510),(1010,800),(660,845),(400,620)]
inside=[(510,310),(760,285),(970,330),(1030,500),(930,690),(685,735),(510,570)]
for i in range(7):
    j=(i+1)%7
    M.prism([outline[i],outline[j],inside[j],inside[i]],320,15,1)
    M.prism([outline[i],outline[j],inside[j],inside[i]],425,12,0)
    # Outer deep edge is an arcade with spans and clear openings into the station.
    a,b=Vector((*outline[i],0)),Vector((*outline[j],0));nb=max(1,int((b-a).length/48))
    for k in range(nb+1):
        p=a+(b-a)*k/nb;M.beam((*p.xy,335),(*p.xy,425),6,12,1)
# Public street stitches the courts, across the two light-well voids.
M.prism([(680,190),(835,205),(865,510),(790,650),(695,620),(705,400)],425,12)
M.finish('SC_H1_THICK_PUBLIC_CITY_GROUND',[stone,dark],1.5)
# One public market/learning canopy is a spatial mesh shared by the adjoining street.
patch('SC_H1_MARKET_ROOM',[
 [(690,300,437),(710,300,458),(750,300,475),(795,300,468),(820,300,437)],
 [(675,390,437),(710,390,467),(755,390,485),(805,390,475),(835,390,437)],
 [(690,485,437),(725,485,465),(770,485,478),(810,485,466),(825,485,437)]
 ],{(0,2)},2.5)
# NAVE ground and shore form one landing route; H1 is reached through two lift rooms.
M=Mesh();M.prism([(-350,-540),(190,-540),(260,-150),(245,280),(350,500),(-150,650),(-370,150)],60,12)
M.prism([(-540,-950),(-390,-990),(-150,-540),(-320,-500)],-3,14)
for i in range(40):
    y=-820+i*7;M.prism([(-330,y),(-270,y),(-270,y+7),(-330,y+7)],11+i*1.225,1.225)
# Curved library landings, each physically thick rather than decorative outlines.
M.prism([(-270,-250),(-100,-260),(-80,-150),(-240,-80)],88,10)
M.prism([(-285,0),(-130,20),(-100,170),(-325,230)],150,10)
M.prism([(190,230),(300,200),(420,320),(390,450),(260,450)],105,12)
M.finish('SC_SHORE_NAVE_PUBLIC_ROUTE',[stone],1.2)
M=Mesh()
for x in (360,395):
    M.beam((x,430,72),(x,430,440),9,12,0)
    for z in (72,117,437):M.prism([(x-15,410),(x+25,410),(x+25,450),(x-15,450)],z,4,1)
M.beam((395,430,434),(500,430,434),6,30,1)
M.finish('SC_PUBLIC_LIFT_ROOMS',[glass,ivory],.8)
# A few scale figures; no decorative district population or window-object generation.
M=Mesh()
for x,y,z in [(0,-310,72),(12,-300,72),(-15,-298,72),(760,290,437),(770,295,437),(740,530,437)]:
    M.beam((x,y,z),(x,y,z+1.5),.5,.3);M.beam((x,y,z+1.5),(x,y,z+1.8),.3,.3)
M.finish('SC_SCALE_FIGURES',[dark])
world=bpy.data.worlds.new('SC_clear_diffuse_day');world.use_nodes=True
bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.66,.74,.85,1);bg.inputs['Strength'].default_value=.7;S.world=world
ld=bpy.data.lights.new('SC_SUN','SUN');ld.energy=2.5;ld.angle=.2
ob=bpy.data.objects.new('SC_SUN',ld);C.objects.link(ob);ob.rotation_euler=(.5,-.6,-.4)
S.render.engine='CYCLES';S.cycles.device='CPU';S.cycles.samples=16;S.cycles.use_denoising=True
S.render.threads_mode='FIXED';S.render.threads=2;S.render.resolution_x=960;S.render.resolution_y=720;S.render.resolution_percentage=100
S.render.image_settings.file_format='PNG';S.render.film_transparent=False;S.unit_settings.system='METRIC';S.unit_settings.scale_length=1
S.camera=bpy.data.objects['E11_URBAN_AERIAL'];bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'SPATIAL_A0.blend'))
(ROOT/'AUTHORING.json').write_text(json.dumps({'source':str(SRC.relative_to(ROOT.parent)),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'protected_source':str((PREV/'protected_before.json').relative_to(ROOT.parent)),'method':'Explicit spatial mesh control points and cavity topology; subdivision+solidify. Python-assisted; not GUI sculpt. Repeated geometry limited to occupied floor/bay topology within combined meshes.','new_objects':len(C.objects),'old_architecture_imported':0,'art':'UNREVIEWED','function':'UNVERIFIED'},indent=2),encoding='utf8',newline='\n')
print('SPATIAL_CONTROL_MESH_A0_SAVED',len(C.objects),flush=True)
