"""R29 TIDAL COMMONS. Open immutable R28, edit a research copy, save ONLY R29.
Background Blender 5.2: --python build_commons.py -- build|render [camera...] [--preview]
Metres, research relative coordinates. No canonical assets or world access.
"""
import bpy, bmesh, math, sys, json, random
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent
SOURCE=R.parent/'R28/model/R28_CELESTIAL_ESTUARY.blend'
ARGS=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['build']
BATCH={};GROUP='R29_EAST_INHABITED_ESCARPMENT';CHANGES=[]
rng=random.Random(291026)

def record(p,v): (R/p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
def add(name,vs,fs,mat):
    v,f=BATCH.setdefault((GROUP,name,mat),([],[]));off=len(v)
    v.extend(vs);f.extend(tuple(off+i for i in a) for a in fs)
def box(name,c,d,mat='pearl',angle=0):
    x,y,z=c;a,b,h=[v/2 for v in d];co,si=math.cos(angle),math.sin(angle)
    vs=[(x+u*co-v*si,y+u*si+v*co,z+w) for w in [-h,h] for u,v in [(-a,-b),(a,-b),(a,b),(-a,b)]]
    add(name,vs,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat)
def beam(name,a,b,w,d,mat='pearl'):
    a,b=Vector(a),Vector(b);t=(b-a).normalized();u=t.cross(Vector((0,0,1)))
    if u.length<.01:u=Vector((1,0,0))
    u.normalize();v=t.cross(u)*d/2;u*=w/2
    vs=[tuple(p+s*u+q*v) for p in [a,b] for s,q in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    add(name,vs,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat)
def path(name,pts,w,d,mat='pearl'):
    for a,b in zip(pts,pts[1:]):beam(name,a,b,w,d,mat)
def shell(name,rows,thick,mat='pearl'):
    n,m=len(rows),len(rows[0]);v=[tuple(p) for row in rows for p in row];off=len(v)
    v += [(x,y,z-thick) for x,y,z in v];f=[]
    for i in range(n-1):
        for j in range(m-1):
            a=i*m+j;b=a+m;f.extend([(a,a+1,b+1,b),(a+off,b+off,b+1+off,a+1+off)])
        for j in [0,m-1]:
            a=i*m+j;b=a+m;f.append((a,b,b+off,a+off))
    for i in [0,n-1]:
        for j in range(m-1):
            a=i*m+j;f.append((a,a+off,a+1+off,a+1))
    add(name,v,f,mat)
def floor(name,x0,x1,y0,y1,z,thick=3,mat='pearl'):
    box(name,((x0+x1)/2,(y0+y1)/2,z-thick/2),(x1-x0,y1-y0,thick),mat)
def rail(name,a,b):
    a,b=Vector(a),Vector(b);beam(name, a+Vector((0,0,1.1)),b+Vector((0,0,1.1)),.15,.16,'bronze')
    for i in range(int((b-a).length/5)+1):
        p=a.lerp(b,i/max(1,int((b-a).length/5)));box(name+' posts',p+Vector((0,0,.55)),(.12,.12,1.1),'bronze')
def ramp(name,a,b,width=12):
    # Deck TOP is the interpolation of given endpoints, unlike an angled beam.
    a,b=Vector(a),Vector(b);d=b-a;u=Vector((-d.y,d.x,0)).normalized()*width/2
    shell(name,[[tuple(a-u),tuple(a+u)],[tuple(b-u),tuple(b+u)]],1.2)
    rail(name+' rail L',a-u,b-u);rail(name+' rail R',a+u,b+u)
def tree(x,y,z,s=12):
    beam('R29 tree trunks',(x,y,z),(x,y,z+s*.65),s*.05,s*.05,'bronze')
    for k in range(3):
        zz=z+s*(.55+k*.18);rad=s*(.4-.08*k);n=16
        vs=[(x+rad*math.cos(i*math.tau/n),y+rad*math.sin(i*math.tau/n),zz) for i in range(n)]+[(x,y,zz+s*.25),(x,y,zz-s*.1)]
        add('R29 fine foliage',vs,[(i,(i+1)%n,n) for i in range(n)]+[(i,n+1,(i+1)%n) for i in range(n)],'green')
def person(x,y,z):
    box('R29 people',(x,y,z+1),(.38,.22,1.25),'human');box('R29 heads',(x,y,z+1.64),(.25,.24,.27),'human')
    for dx in [-.12,.12]:box('R29 legs',(x+dx,y,z+.3),(.12,.14,.6),'human')
def furniture(x,y,z):
    box('commons reading tables',(x,y,z+.76),(3,1.2,.12),'bronze')
    for dx in [-1.2,1.2]:box('table supports',(x+dx,y,z+.36),(.12,.8,.72),'bronze')
    for dy in [-1.1,1.1]:
        box('commons seats',(x,y+dy,z+.44),(2.8,.45,.15),'pearl')
        box('commons seat backs',(x,y+dy*1.15,z+.8),(2.8,.12,.8),'pearl')
def hall(name,cx,cy,z,w,length,h,levels=2):
    # A real open-ended room: raised side galleries, separate walls, clear centre.
    floor(name+' ground',cx-w/2,cx+w/2,cy-length/2,cy+length/2,z,2,'warmstone')
    rows=[]
    for j in range(13):
        y=cy-length/2+length*j/12
        rows.append([(cx+w/2*math.cos(math.pi*i/32),y,z+9+h*math.sin(math.pi*i/32)) for i in range(33)])
    # Split roof leaves a broad continuous zenith slot.
    shell(name+' west roof',[r[:13] for r in rows],1.2)
    shell(name+' east roof',[r[20:] for r in rows],1.2)
    for j in range(9):
        y=cy-length/2+length*j/8
        path(name+' ribs',[(cx+w/2*math.cos(math.pi*i/24),y,z+9+h*math.sin(math.pi*i/24)) for i in range(25)],.8,1.2,'bronze')
    for side in [-1,1]:
        for k in range(levels):
            zz=z+6*(k+1);xx=cx+side*w*.38
            floor(name+' side gallery',xx-w*.11,xx+w*.11,cy-length/2,cy+length/2,zz,.7)
            rail(name+' gallery rail',(xx-side*w*.11,cy-length/2,zz),(xx-side*w*.11,cy+length/2,zz))
            for yy in range(int(cy-length/2+8),int(cy+length/2-5),12):
                box(name+' books and exhibits',(xx+side*w*.07,yy,zz+1.4),(1.5,5,2.8),'dark')
                for dz in [.4,1.2,2]:box(name+' shelf lips',(xx+side*w*.07,yy,zz+dz),(1.7,5,.15),'bronze')
        for yy in range(int(cy-length/2),int(cy+length/2+1),12):
            box(name+' open colonnade',(cx+side*w*.48,yy,z+9),(1,1,18),'pearl')
        # Explicit stairs at open hall ends, rather than unreachable balconies.
        for k in range(levels*30):box(name+' stairs',(cx+side*w*.35,cy-length/2+1+k*.32,z+(k+1)*.1),(5,.34,(k+1)*.2),'warmstone')
    for yy in range(int(cy-length/2+18),int(cy+length/2-10),20):furniture(cx,yy,z)

def flush():
    for (group,name,mat),(vs,fs) in BATCH.items():
        me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update()
        bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
        ob=bpy.data.objects.new(name,me);co=bpy.data.collections.get(group)
        if co is None:co=bpy.data.collections.new(group);bpy.context.scene.collection.children.link(co)
        co.objects.link(ob);me.materials.append(bpy.data.materials[mat]);ob['study_group']=group;ob['provenance']='R29 authored research geometry, relative metres'
    BATCH.clear()
def erase(name):
    ob=bpy.data.objects.get(name)
    if ob:CHANGES.append({'removed':name,'vertices':len(ob.data.vertices)});bpy.data.objects.remove(ob,do_unlink=True)
def cut(ob,c,d,label):
    if ob.type!='MESH':return
    bpy.ops.mesh.primitive_cube_add(size=1,location=c);tool=bpy.context.object;tool.name='TEMP_R29_BOOLEAN';tool.dimensions=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new(label,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=tool
    before=len(ob.data.vertices);bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(tool,do_unlink=True)
    CHANGES.append({'cut':ob.name,'label':label,'box_center_m':c,'box_dimensions_m':d,'vertices_before':before,'vertices_after':len(ob.data.vertices)})
def union_floor(target,names):
    ob=bpy.data.objects[target]
    for name in names:
        tool=bpy.data.objects.get(name)
        if tool is None:continue
        bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('R29 continuous public floor','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=tool
        bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(tool,do_unlink=True)
        CHANGES.append({'floor_union':target,'absorbed':name})
def xc(u,z):return 1030-480*u+100*math.sin(math.pi*u)-.20*z
def top(u):return 180+1230*math.sin(math.pi*u)**.8
def public_cut(u,z):
    return ((u-.43)/.30)**2+((z-(530+170*u))/265)**2<1 or ((u-.68)/.24)**2+((z-1040)/175)**2<1

def rotate_batch(prefix,cx,cy,angle):
    co,si=math.cos(angle),math.sin(angle)
    for (group,name,mat),(vs,fs) in BATCH.items():
        if name.startswith(prefix):
            vs[:]=[(cx+(x-cx)*co-(y-cy)*si,cy+(x-cx)*si+(y-cy)*co,z) for x,y,z in vs]

def east_wing():
    global GROUP
    GROUP='R29_EAST_INHABITED_ESCARPMENT'
    # Unequal neighbourhood sections shape a rising, forked city cliff.
    for i in range(42):
        u=(i+.5)/42;y=-520+1850*u;step=1850/42;maximum=top(u)
        pitch=[10,12,9][min(2,int(u*3))]
        for k in range(int((maximum-105)/pitch)):
            z=105+k*pitch
            if public_cut(u,z):continue
            x=xc(u,z);w=290-80*u+35*math.sin(u*9+z*.003)
            box('inhabited floor cells',(x,y,z-1),(w,step+1,2),'silver')
            # Separate deep room bars, actual front/rear circulation strips.
            for side in [-1,1]:box('recessed private room bars',(x+side*w*.18,y,z+pitch*.42),(w*.32,step-7,pitch*.7),'dark')
        # Screen lengths follow the elliptical public cuts, rather than masking them.
        spans=[];start=None
        for iz in range(105,int(maximum)+1,3):
            occupied=not public_cut(u,iz)
            if occupied and start is None:start=iz
            if start is not None and (not occupied or iz>=int(maximum)-3):
                spans.append((start,iz));start=None
        for za,zb in spans:
            if zb-za<20:continue
            for side in [-1,1]:
                a=(xc(u,za)+side*(145-40*u),y,za);b=(xc(u,zb)+side*(145-40*u),y,zb)
                beam('raked inhabited facade pilasters',a,b,8,13,'pearl')
                beam('pilaster bronze reveals',(a[0]+side*5,a[1],a[2]),(b[0]+side*5,b[1],b[2]),1.2,4,'bronze')
    # Slender primary branches follow the city section; no filled curtain across rifts.
    for u in [.05,.17,.72,.94]:
        ztop=top(u);y=-520+1850*u
        path('branching civic buttresses',[(xc(u,105)+170,y,105),(xc(u,650)+145,y+20,650),(xc(u,ztop)+110,y,ztop)],20,28)
    # Tapered public landscapes, not a uniform storey extrusion.
    for label,z,ua,ub,w in [('water commons',105,0,1,440),('learning ground',345,.10,.68,390),('sky garden',650,.16,.84,510),('aerial station ground',805,.26,.91,410),('cloud archives',1025,.35,.82,270)]:
        rows=[]
        for i in range(31):
            u=ua+(ub-ua)*i/30;x=xc(u,z);y=-520+1850*u;ww=w*(.72+.28*math.sin(math.pi*i/30))
            rows.append([(x-ww/2,y,z),(x+ww/2,y,z)])
        shell(label+' civic landscape',rows,8,'warmstone')
        for side in [-1,1]:path(label+' sculpted rim',[(row[0 if side<0 else 1][0],row[0][1],z-6) for row in rows],5,14,'pearl')
        for i in range(3,28,3):
            x,y,_=rows[i][0];tree(x+20,y,z,15 if z<650 else 11)
    # Large public room changes BOTH the outer roof and internal section.
    GROUP='R29_LEARNING_AND_RESIDENTIAL_COMMONS'
    hall('learning conservatory',870,-25,345,145,255,105,3)
    hall('sky archive cloister',785,600,1025,105,180,80,2)
    # Occupied courts beside the rifts, discrete through-arcades and roof gardens.
    for name,x,y,z,w,d,h in [('estuary exchange',1120,-380,105,170,135,56),('craft court',950,260,105,210,150,85),('shared learning rooms',930,320,345,160,200,75),('north dwelling court',650,1030,650,180,160,95)]:
        for zz in range(int(z)+6,int(z+h),6):
            floor(name+' floor',x-w/2,x+w/2,y-d/2,y+d/2,zz,1)
            if zz>z+10:
                for side in [-1,1]:box(name+' private bars',(x+side*w*.33,y,zz+2.5),(w*.22,d-14,4),'dark')
        for side in [-1,1]:
            for yy in [y-d/2,y,y+d/2]:box(name+' vertical frame',(x+side*w*.47,yy,z+h/2),(3,4,h),'pearl')
        # Longitudinal ground arcade stays empty between the two room bars.
        for yy in range(int(y-d/2+12),int(y+d/2),20):tree(x,yy,z+h,10)

def forum_and_waterfront():
    global GROUP
    GROUP='R29_FORUM_CITY_SEQUENCE'
    # A 34m high public intermediate street with an explicit gentle approach.
    floor('forum east raised street',155,390,-760,210,139,6,'warmstone')
    ramp('forum garden ascent',(195,-1440,105),(195,-760,139),18)
    for y in [-650,-240,120]:
        floor('forum terraced court',55,385,y-75,y+75,105,1,'warmstone')
        hall('forum exchange '+str(y),295,y,139,95,130,34,2)
        for xx in [90,130]:
            tree(xx,y-40,105,16);tree(xx,y+40,105,13)
        ramp('court return '+str(y),(75,y+40,105),(75,y+210,139),8)
        floor('court upper landing',70,195,y+204,y+220,139,2)
    # Garden bands and a quiet clear ceremonial route remain, with real destinations.
    for y in range(-1260,240,90):
        box('garden beds',(330,y,105.6),(35,48,1.2),'green')
        for x in [320,340]:tree(x,y,106.2,11)
    # Three real transverse portals to the eastern mixed-use street.
    for y in [-1100,-600,-120]:
        floor('FORUM_EAST_PORTAL_'+str(y),355,1130,y-22,y+22,105,3,'warmstone')
        for side in [-1,1]:
            for x in range(640,1100,30):box('sea street columns',(x,y+side*25,114),(1.2,1.2,18),'bronze')
            box('sea street canopy',(875,y+side*32,124),(470,18,1.5),'pearl')
        for x in [700,780,1030]:tree(x,y-48,105,12)
    # Survey found the original reading gallery fourteen metres above the terrace.
    ramp('reading gallery accessible research ramp',(680,-1280,105),(680,-1000,119),10)
    floor('reading ramp top landing',675,710,-1005,-990,119,1.2)
    # Broad low public roof on the sea side: activity and landform at the central base.
    hall('waterfront exchange hall',1310,-1080,105,170,280,55,2)
    for y in range(-1320,-550,55):
        tree(1535,y,105,14);box('sea promenade seats',(1515,y,105.45),(9,1.4,.9),'bronze')

def transit_and_sky():
    global GROUP
    GROUP='R29_AERIAL_GATE_AND_LIFTS'
    # Two open public floors; landing datum shared with measured R28 promenade.
    floor('R29_SKY_GARDEN_FLOOR',720,1370,-520,180,650,10,'warmstone')
    floor('R29_CENTRAL_ARRIVAL_FLOOR',1000,1450,-540,-235,805,7,'warmstone')
    floor('R29_PROMENADE_JOIN',820,1080,160,260,650,6)
    # Large clerestory canopy, arch is spatially open on BOTH ends.
    hall('aerial civic terminal',1245,-390,805,330,280,82,2)
    # Public room with near furniture, middle street and distant sky neighbourhood.
    hall('outlook reading room',1120,-160,650,125,160,42,2)
    rotate_batch('outlook reading room',1120,-160,-1.993)
    for y in [-455,-250,40]:
        for x in [760,835,1285,1340]:tree(x,y,650,14)
    for z in [105,345,650,805]:
        floor('lift landing '+str(z),1090,1170,-310,-250,z,3)
        # Clear doorway between jambs, floor and lintel; no opaque lift shaft box.
        for x in [1110,1150]:
            box('lift door jamb',(x,-264,z+3),(1,1,6),'bronze')
        box('lift door lintel',(1130,-264,z+6),(42,1,1),'pearl')
    for x in [1104,1156]:
        for y in [-304,-278]:box('lift guide cage',(x,y,455),(2,2,710),'silver')
    for z in [105,650,805]:
        floor('visible research lift car',1107,1153,-302,-280,z+0.05,1)
        for x in [1108,1152]:box('lift car side glazing',(x,-291,z+2.5),(.3,22,5),'glazing')
        floor('lift car roof',1107,1153,-302,-280,z+5.3,.6)
    # A quiet horizontal sky route replaces the old enormous sloping diagonal.
    pts=[(1370,-480,805),(1600,-769,805),(1900,-769,804.5)]
    # Public footway beside a distinct two-guideway vehicle channel.
    for a,b in zip(pts,pts[1:]):
        ramp('R29_SKY_WALK',a,b,16)
        av,bv=Vector(a),Vector(b);u=Vector((-(bv-av).y,(bv-av).x,0)).normalized()
        aa=av-u*28;bb=bv-u*28
        ramp('sky transit service deck',aa,bb,22)
        for side in [-1,1]:path('twin vehicle guideways',[aa+u*side*6+Vector((0,0,.45)),bb+u*side*6+Vector((0,0,.45))],.5,.5,'bronze')
        n=12
        for side in [-1,1]:
            railpts=[]
            for i in range(n+1):
                p=av.lerp(bv,i/n)+u*side*10;p.z-=8+48*math.sin(math.pi*i/n);railpts.append(p)
                if i%2==0:beam('sky bridge web',p,av.lerp(bv,i/n)+u*side*7-Vector((0,0,1.5)),1.2,1.8,'silver')
            path('sky bridge suspended bow',railpts,3,4,'silver')
    # The offset vehicle channels need their OWN corner closure; a continuous
    # pedestrian centreline alone did not close the first 24.4m service-deck gap.
    turn_a=Vector((1600,-769,805))-Vector((289,230,0)).normalized()*28
    turn_b=Vector((1600,-797,805))
    ramp('vehicle turn connecting deck',turn_a,turn_b,22)
    for side in [-1,1]:
        aa=turn_a+Vector((289,230,0)).normalized()*side*6+Vector((0,0,.45))
        bb=turn_b+Vector((0,side*6,.45))
        path('vehicle corner guideway links',[aa,bb],.5,.5,'bronze')
    # Two illustrative vehicles only; operation, capacity and timetabling unverified.
    for x,y,angle in [(1463.1,-641.9,-.8986),(1750,-797,0)]:
        box('transit vehicle body',(x,y,809),(42,8,7),'pearl',angle)
        box('transit vehicle glazing',(x+4.1*math.sin(angle),y-4.1*math.cos(angle),810),(34,.2,3),'glazing',angle)
    GROUP='R29_B_HARBOR_ARRIVAL_QUARTER'
    floor('R29_B_ARRIVAL_FLOOR',1570,2100,-830,-710,804.5,5,'warmstone')
    hall('B harbor station',1755,-769,804.5,115,270,43,2)
    # B has a real street arrival and a distinctive tall split sail beyond it.
    for i in range(3):
        x=2020+i*210;y=-465+i*40;z=804.5
        hall('harbor civic court '+str(i),x,y,z,130,190,65+i*20,2)
        for k in range(12+i*4):
            floor('harbor inhabited comb '+str(i),x-75+k*2,x+75+k*2,y+90,y+160,z+6*k,1.2)
            box('harbor private rooms',(x+k*2,y+125,z+6*k+3),(125,48,4.5),'dark')
    for j in range(5):
        y=-390+j*24
        rows=[]
        for i in range(33):
            t=i/32;x=2040+560*t;zz=910+270*math.sin(math.pi*t)**.7
            rows.append([(x,y,zz),(x,y+15,zz+6)])
        shell('B harbor asymmetric sail roof',rows,3,'pearl')
    for x in range(1850,2640,65):tree(x,-740,804.5,10)
    # A second civic address faces the central reading room at the SAME horizon.
    # It inhabits the previously empty basket underside, rather than pretending
    # that a view of the original rim is a view of a living neighbourhood.
    GROUP='R29_B_LOWER_INHABITED_PORT'
    floor('R29_B_LOWER_PORT_FLOOR',1700,2260,-620,-330,650,8,'warmstone')
    hall('B lower public workshop',1875,-475,650,155,230,56,2)
    rotate_batch('B lower public workshop',1875,-475,-1.993)
    for x,y,w,d,h in [(2170,-465,140,150,120),(1735,-415,80,120,95),(2040,-365,130,70,110)]:
        for k in range(int(h/6)):
            zz=660+6*k;floor('B lower inhabited floors',x-w/2,x+w/2,y-d/2,y+d/2,zz,1)
            box('B lower private room bars',(x,y+10,zz+2.5),(w-18,d*.6,4.5),'dark')
        for side in [-1,1]:
            for yy in [y-d/2,y+d/2]:box('B lower inhabited vertical frames',(x+side*w*.47,yy,650+h/2),(3,4,h),'pearl')
    for x in [1760,1930,2070,2210]:tree(x,-590,650,12)
    for x in [2115,2135]:
        for y in [-605,-585]:box('B lower lift guides',(x,y,727),(1.2,1.2,154),'bronze')
    for z in [650,804.5]:
        floor('B lower lift landing',2105,2145,-614,-576,z,1.5)
        box('B lower lift cabin',(2125,-595,z+2.5),(16,14,5),'glazing')
    # Readable public life at the two arrival thresholds, without camera lights.
    for x,y in [(1210,-480),(1300,-450),(1340,-390),(1810,-780),(1950,-750),(1140,-180),(1090,-170)]:
        person(x,y,805 if x>1200 and y<-300 else 650)
    for x,y in [(1205,-430),(1310,-420),(1290,-300)]:
        box('arrival timber benches',(x,y,805.45),(12,1.2,.9),'bronze');tree(x-12,y,805,9)

NEW_CAMERAS=[
 ('10_EAST_CITY_SECTION',(3200,-2800,1450),(950,340,650),40,None),
 ('11_SKY_READING_HUMAN',(1074.4,-139.5,651.7),(1880,-500,682),28,'R29_SKY_GARDEN_FLOOR'),
 ('12_CENTRAL_ARRIVAL_HUMAN',(1350,-480,806.7),(1875,-769,840),30,'R29_CENTRAL_ARRIVAL_FLOOR'),
 ('13_B_ARRIVAL_HUMAN',(1910,-769,806.2),(950,300,1500),25,'R29_B_ARRIVAL_FLOOR'),
 ('14_LEARNING_HUMAN',(870,-110,346.7),(900,500,470),24,'learning conservatory ground'),
 ('15_FORUM_EAST_STREET',(695,-615,106.7),(1050,-230,220),28,'SEA_TERRACE_REAL_FLOOR'),
 ('16_B_LOWER_PUBLIC_CITY',(1910,-491,651.7),(780,300,880),25,'R29_B_LOWER_PORT_FLOOR'),
]
def build():
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE));bpy.context.preferences.filepaths.save_version=0
    for name,rgb,metal,rough in [('warmstone',(.58,.57,.49),.12,.62),('glazing',(.045,.18,.21),.45,.22)]:
        m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True
        p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    for name in ['EAST LANTERN storeys','EAST LANTERN room bands','EAST LANTERN vertical facade blades','EAST LANTERN continuous buttress','transit viaduct 1','transit rails 1','forum civic island']:
        erase(name)
    # Cut only necessary existing R28 components; originals on disk remain immutable.
    for y in [-1100,-600,-120]:
        for name in ['forum silver roof petals','forum branching vault ribs','forum splayed root','forum gallery floors','forum gallery piers','gallery safety rail','gallery rail posts','forum market private core','forum market floor','forum market shopfront','forum market shelter','forum market entry lintel','forum market arcade supports','forum market facade fins']:
            o=bpy.data.objects.get(name)
            if o:cut(o,(550,y,143),(420,58,88),'R29 transverse public portal')
    for name in ['B_HARBOR occupied decks','B_HARBOR recessed bands']:
        cut(bpy.data.objects[name],(1570,-715,835),(390,260,80),'R29 B street arrival opening')
    # Replace overlapping original boulevard surface under the new arrival apron.
    cut(bpy.data.objects['B_HARBOR interior boulevard'],(1835,-770,803),(530,130,12),'R29 replace B arrival floor')
    east_wing();forum_and_waterfront();transit_and_sky();flush()
    # Clear the conservatory's full actual room and three ground street mouths
    # from the new inhabited mass, preserving its separately designed floor.
    for name in ['inhabited floor cells','recessed private room bars','raked inhabited facade pilasters','pilaster bronze reveals']:
        cut(bpy.data.objects[name],(870,-25,419),(172,278,147),'R29 learning room full clearance')
        for y in [-1100,-600,-120]:cut(bpy.data.objects[name],(950,y,143),(430,58,88),'R29 new wing ground public mouth')
    # Public room floors share the larger existing datum; coincident faces caused
    # black self-intersections in the first render. Keep one real supporting floor.
    for name in ['learning conservatory ground','outlook reading room ground','aerial civic terminal ground','waterfront exchange hall ground','B harbor station ground','B lower public workshop ground']+['forum exchange '+str(y)+' ground' for y in [-650,-240,120]]:
        erase(name)
    for y in [-1100,-600,-120]:erase('FORUM_EAST_PORTAL_'+str(y))
    union_floor('R29_SKY_GARDEN_FLOOR',['sky garden civic landscape'])
    union_floor('SEA_TERRACE_REAL_FLOOR',['water commons civic landscape'])
    # The new lower B landing replaces a local part of its original open basket.
    cut(bpy.data.objects['B_HARBOR underside basket arches'],(1875,-475,694),(390,290,99),'R29 lower port public room opening')
    sc=bpy.context.scene
    for name,pos,target,lens,floorname in NEW_CAMERAS:
        o=bpy.data.objects.new(name,bpy.data.cameras.new(name));sc.collection.objects.link(o);o.location=pos
        o.rotation_euler=(Vector(target)-Vector(pos)).to_track_quat('-Z','Y').to_euler();o.data.lens=lens;o.data.clip_start=.1;o.data.clip_end=90000
        o['floor_expected']=floorname or '';o['target_m']=list(target)
    sc['status']='R29 TIDAL COMMONS independent research, NOT adopted or completed master; relative metres; Minecraft HOLD'
    sc['revision']=3;sc.camera=bpy.data.objects['02_CENTRAL_CHOIR']
    bpy.context.view_layer.update()
    record('qa/BUILD_CHANGES.json',{'base':'da2a2e630b95c939881db7428ac21ac85342346e','revision':3,'blender':bpy.app.version_string,'changes':CHANGES,'new_groups':sorted({o['study_group'] for o in sc.objects if o.get('study_group','').startswith('R29_')}),'method':'Open saved R28 BLEND, replace east wing, cut actual public portals, new authored sections and rooms; background Blender. Not live MCP.','official_coordinates':None,'transit':'Illustrative architecture, not operation or capacity certification'})
    bpy.ops.wm.save_as_mainfile(filepath=str(R/'model/R29_TIDAL_COMMONS.blend'),compress=True)
    bpy.ops.object.select_all(action='DESELECT')
    for o in sc.objects:
        if o.type=='MESH':o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(R/'model/R29_TIDAL_COMMONS.glb'),export_format='GLB',use_selection=True,export_apply=True)
    print('R29_BUILD_FINISHED',flush=True)
def render():
    before='--before' in ARGS;preview='--preview' in ARGS
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE if before else R/'model/R29_TIDAL_COMMONS.blend'))
    sc=bpy.context.scene
    names=[n for n in ARGS[1:] if not n.startswith('--')] or ['02_CENTRAL_CHOIR','03_FORUM_HUMAN','08_WHOLE_CITY','10_EAST_CITY_SECTION','11_SKY_READING_HUMAN','12_CENTRAL_ARRIVAL_HUMAN']
    if before:
        for name,pos,target,lens,floorname in NEW_CAMERAS:
            o=bpy.data.objects.new(name,bpy.data.cameras.new(name));sc.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-Vector(pos)).to_track_quat('-Z','Y').to_euler();o.data.lens=lens;o.data.clip_start=.1;o.data.clip_end=90000
    sc.render.resolution_percentage=65 if preview else 100;sc.cycles.samples=12 if preview else 32
    for name in names:
        sc.camera=bpy.data.objects[name];sc.render.filepath=str(R/('process' if preview else 'comparison' if before else 'renders')/(('R28_' if before else '')+name+'.png'))
        print('RENDER_START',name,flush=True);bpy.ops.render.render(write_still=True);print('RENDER_DONE',name,flush=True)
if __name__=='__main__':
    if ARGS[0]=='build':build()
    elif ARGS[0]=='render':render()
    else:raise ValueError(ARGS)
