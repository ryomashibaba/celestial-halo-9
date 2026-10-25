"""R28 CELESTIAL ESTUARY: authored background-Blender architectural study.
New geometry only; metres, east X / north Y / up Z. No world/save access.
blender --factory-startup -b -t 4 --python-exit-code 1 --python THIS -- build|render [camera...]
"""
import bpy, bmesh, math, random, sys, json
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode = True
R = Path(__file__).resolve().parent
for p in ['model', 'renders', 'qa', 'process']: (R/p).mkdir(exist_ok=True)
ARGS = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['build']
REVISION = 2
rng = random.Random(281026)
GROUP = 'CENTRAL'
BATCH = {}
MATS = {}

def record(path, data):
    (R/path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf8')

def material(name, rgb, metallic=0, rough=.55, emission=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Metallic'].default_value=metallic;p.inputs['Roughness'].default_value=rough
    if emission:
        p.inputs['Emission Color'].default_value=(*rgb,1);p.inputs['Emission Strength'].default_value=emission
    MATS[name]=m;return name

def add(name, vs, fs, mat):
    key=(GROUP,name,mat)
    v,f=BATCH.setdefault(key,([],[]));off=len(v)
    v.extend(vs);f.extend(tuple(off+i for i in face) for face in fs)

def box(name, c, d, mat, angle=0):
    x,y,z=c;a,b,h=[v/2 for v in d];co,si=math.cos(angle),math.sin(angle)
    vs=[(x+u*co-v*si,y+u*si+v*co,z+w) for w in [-h,h] for u,v in [(-a,-b),(a,-b),(a,b),(-a,b)]]
    add(name,vs,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat)

def beam(name, a, b, w, depth, mat):
    a,b=Vector(a),Vector(b);d=(b-a).normalized();u=d.cross(Vector((0,0,1)))
    if u.length<.01:u=Vector((1,0,0))
    u.normalize();u*=w/2;v=d.cross(u.normalized())*depth/2
    vs=[tuple(c+sx*u+sy*v) for c in [a,b] for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    add(name,vs,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat)

def ribbon(name, pts, width, thick, mat):
    for a,b in zip(pts,pts[1:]):beam(name,a,b,width,thick,mat)

def annulus(name, cx,cy, rx,ry, width,z,h,a0,a1,mat,steps=64):
    vs=[]
    for zz in [z-h,z]:
        for dr in [0,-width]:
            vs.extend((cx+(rx+dr)*math.cos(a0+(a1-a0)*i/steps),cy+(ry+dr)*math.sin(a0+(a1-a0)*i/steps),zz) for i in range(steps+1))
    n=steps+1;fs=[]
    for i in range(steps):
        fs.extend([(i,i+1,n+i+1,n+i),(2*n+i,3*n+i,3*n+i+1,2*n+i+1),
                   (i,2*n+i,2*n+i+1,i+1),(n+i,n+i+1,3*n+i+1,3*n+i)])
    fs.extend([(0,n,3*n,2*n),(n-1,2*n-1,4*n-1,3*n-1)])
    add(name,vs,fs,mat)

def shell(name, sections, mat, thick=8):
    # Each section is a transverse row; solid, open-ended shell rather than filled aperture.
    n=len(sections);m=len(sections[0]);vs=[tuple(p) for row in sections for p in row]
    vs += [(x,y,z-thick) for x,y,z in vs];off=n*m;fs=[]
    for i in range(n-1):
        for j in range(m-1):
            a=i*m+j;b=a+m
            fs.extend([(a,a+1,b+1,b),(a+off,b+off,b+1+off,a+1+off)])
        for j in [0,m-1]:
            a=i*m+j;b=a+m;fs.append((a,b,b+off,a+off))
    for i in [0,n-1]:
        for j in range(m-1):
            a=i*m+j;fs.append((a,a+off,a+1+off,a+1))
    add(name,vs,fs,mat)

def tree(x,y,z,size=10):
    beam('garden trunks',(x,y,z),(x,y,z+size*.62),size*.09,size*.09,'bronze')
    n=14;vs=[]
    for zz,rad in [(size*.4,size*.38),(size*.8,size*.5),(size*1.12,size*.24)]:
        vs.extend((x+rad*math.cos(i*2*math.pi/n),y+rad*math.sin(i*2*math.pi/n),z+zz) for i in range(n))
    fs=[tuple(reversed(range(n))),tuple(range(2*n,3*n))]+[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(2) for i in range(n)]
    add('garden crowns',vs,fs,'green')
    # Branching irregular subcrowns break the coarse single-polyhedron silhouette.
    for j in range(5):
        a=j*2.399;r=size*.27;xx=x+r*math.cos(a);yy=y+r*math.sin(a)
        zz=z+size*(.68+.14*math.sin(j*1.7))
        beam('garden branches',(x,y,z+size*.46),(xx,yy,zz),size*.045,size*.045,'bronze')
        vv=[(xx+size*.3*math.cos(k*2*math.pi/12),yy+size*.3*math.sin(k*2*math.pi/12),zz) for k in range(12)]
        vv += [(xx,yy,zz+size*.32),(xx,yy,zz-size*.18)]
        add('garden layered foliage',vv,[(k,(k+1)%12,12) for k in range(12)]+[(k,13,(k+1)%12) for k in range(12)],'green')

def person(x,y,z):
    beam('people 1.75m',(x,y,z+.48),(x,y,z+1.4),.42,.25,'human')
    box('people heads',(x,y,z+1.6),(.26,.26,.3),'human')
    for d in [-.13,.13]:beam('people legs',(x+d,y,z),(x+d*.6,y,z+.65),.12,.14,'human')
    for d in [-1,1]:beam('people arms',(x+d*.27,y,z+.65),(x+d*.25,y,z+1.3),.11,.12,'human')

def street_block(name,x,y,z,w,d,floors,angle=0):
    # Ground arcade, real apertures; upper private rooms deliberately simplified.
    co,si=math.cos(angle),math.sin(angle)
    def pos(a,b,h):return(x+a*co-b*si,y+a*si+b*co,z+h)
    for k in range(floors+1):
        zz=8+k*5
        box(name+' floor',pos(0,0,zz),(w,d,.7),'pearl',angle)
        if k<floors:
            box(name+' private core',pos(0,0,zz+2.4),(w*.74,d*.66,4.1),'dark',angle)
            for a in range(max(2,int(w/9))):
                xx=-w/2+4+a*(w-8)/max(1,int(w/9)-1)
                for side in [-1,1]:box(name+' facade fins',pos(xx,side*d*.49,zz+2.5),(.55,1,4.4),'pearl',angle)
    for a in [-w*.43,0,w*.43]:
        for b in [-d*.40,d*.4]:box(name+' arcade supports',pos(a,b,4),(.8,.8,8),'bronze',angle)
    box(name+' shelter',pos(0,0,7.9),(w+7,d+7,.6),'pearl',angle)
    # Ground storefronts split around open doorways; no opaque face across the passage.
    for side in [-1,1]:
        for a in [-w*.3,w*.3]:
            box(name+' shopfront',pos(a,side*d*.30,3),(w*.3,.4,5.5),'dark',angle)
            box(name+' shop transom',pos(a,side*(d*.30+.3),5.8),(w*.3,.6,.3),'bronze',angle)
        box(name+' entry lintel',pos(0,side*d*.30,6.7),(w,.8,.8),'pearl',angle)

def terrain_z(x,y):
    north=max(0,min(1.6,(y-2200)/2500))
    ridge=(1-abs(math.sin(x*.00079+y*.00043)))*.58+(1-abs(math.sin(x*.0021-y*.0012)))*.27+(1-abs(math.sin(x*.0056+y*.0031)))*.15
    mountain=north**1.1*(400+1550*ridge)
    west=650/(1+math.exp(max(-50,min(50,(x+3650+90*math.sin(y*.002))/65))))
    noise=22*math.sin(x*.0012)*math.cos(y*.0018)+12*math.sin(x*.003+y*.002)
    basin=38+noise
    coast=1850+320*math.sin(y*.0011)+140*math.sin(y*.0032)
    sea=max(0,min(1,(x-coast+120)/280));sea=sea*sea*(3-2*sea)
    basin=basin*(1-sea)+(-85+noise*.35)*sea
    return basin+mountain+west

def terrain():
    global GROUP
    GROUP='CONTEXT_TERRAIN_PROVISIONAL'
    n=121;vs=[]
    for j in range(n):
        y=-6500+j*120
        for i in range(n):
            x=-7000+i*120;vs.append((x,y,terrain_z(x,y)))
    fs=[]
    for j in range(n-1):
        for i in range(n-1):
            a=j*n+i;fs.extend([(a,a+1,a+n+1),(a,a+n+1,a+n)])
    add('landform research',vs,fs,'terrain')
    box('eastern inland sea',(7200,600,-10),(10800,18000,12),'water')
    # Deliberately distant terrain boundary, not a floating rectangular display plinth.
    box('far ground',(0,0,-170),(300000,300000,60),'terrain')

def central():
    global GROUP
    GROUP='CENTRAL_OCCUPIED_CRESCENTS'
    # Three arc-shaped inhabited wings share a public basin but have distinct rise profiles.
    wings=[('WEST CHOIR',-250,450,1250,1670,.58*math.pi,1.48*math.pi,1760,340),
           ('NORTH CHOIR',-80,620,1150,1220,-.03*math.pi,.96*math.pi,2320,300),
           ('EAST LANTERN',260,450,720,940,-.34*math.pi,.39*math.pi,1240,240)]
    for name,cx,cy,rx,ry,a0,a1,height,width in wings:
        levels=int(height/20)
        for k in range(levels):
            t=k/levels;z=105+k*20
            shrink=1-.49*t**1.35
            # roof descends towards both open tips, producing a stepped ascending silhouette.
            steps=52
            for i in range(steps):
                u=(i+.5)/steps
                profile=.22+.78*math.sin(math.pi*u)**.68
                if t>profile:continue
                aa=a0+(a1-a0)*i/steps;bb=a0+(a1-a0)*(i+1)/steps
                # Major public cuts: a 520m-high passage through the north choir,
                # and an east belvedere joining the forum to the sea panorama.
                mid=(aa+bb)/2
                portal=(name=='NORTH CHOIR' and .39*math.pi<mid<.57*math.pi and 80<z<650)
                belvedere=(name=='EAST LANTERN' and -.30*math.pi<mid<-.07*math.pi and 120<z<410)
                if portal or belvedere:continue
                annulus(name+' storeys',cx,cy,rx*shrink,ry*shrink,width*(.65+.35*(1-t)),z,2.8,aa,bb,'pearl',1)
                # Set-back occupied spine: actual front/back gallery voids around it.
                if k%12 not in [9,10,11]:
                    annulus(name+' room bands',cx,cy,rx*shrink-26,ry*shrink-26,width*(.65+.35*(1-t))-60,z+15,12,aa,bb,'dark',1)
                if k%2==0:
                    a=(aa+bb)/2
                    for inset in [4,width*(.65+.35*(1-t))-4]:
                        x=cx+(rx*shrink-inset)*math.cos(a);y=cy+(ry*shrink-inset)*math.sin(a)
                        box(name+' vertical facade blades',(x,y,z+9),(3,4,18),'silver',a)
                if k%9==0 and i%4==0:
                    a=(aa+bb)/2;tree(cx+(rx*shrink-13)*math.cos(a),cy+(ry*shrink-13)*math.sin(a),z,13)
        # Great structural ribs follow the actual stacked-floor recession.
        for i in range(13):
            u=(i+.5)/13;a=a0+(a1-a0)*u;profile=.22+.78*math.sin(math.pi*u)**.68
            pts=[]
            for j in range(19):
                t=profile*j/18;s=1-.49*t**1.35
                pts.append((cx+(rx*s+10)*math.cos(a),cy+(ry*s+10)*math.sin(a),105+height*t))
            ribbon(name+' continuous buttress',pts,12,14,'pearl')
    GROUP='CENTRAL_SPINE'
    # Slender hollow trilobed spine; stacked ring floors instead of a solid crystal.
    for k in range(155):
        t=k/155;z=135+k*20;rad=310*(1-.84*t**1.4)
        annulus('spine occupied ring',-180,1050,rad,rad*.76,52*(1-.5*t),z,2.5,0,2*math.pi,'silver',32)
        if k<148:annulus('spine recessed rooms',-180,1050,rad-9,rad*.76-9,30*(1-.45*t),z+15,11,0,2*math.pi,'dark',32)
    for j in range(9):
        a=j*2*math.pi/9
        pts=[]
        for k in range(33):
            t=k/32;rad=318*(1-.84*t**1.4);ang=a+.26*t
            pts.append((-180+rad*math.cos(ang),1050+rad*.76*math.sin(ang),100+3170*t))
        ribbon('spine ascending flutes',pts,10,13,'pearl')
    # One tilted open ceremonial halo, not seven copied rings.
    pts=[]
    for i in range(129):
        a=2*math.pi*i/128
        pts.append((-180+820*math.cos(a),1020+300*math.sin(a),2010+570*math.sin(a)))
    ribbon('inclined crown halo',pts,24,36,'pearl')
    ribbon('halo bronze inner seam',[(x,y-24,z) for x,y,z in pts],5,6,'bronze')
    GROUP='CENTRAL_PUBLIC_FORUM'
    box('FORUM_REAL_FLOOR',(0,-460,96),(1220,2350,18),'paving')
    # Upper courtyard ring ties occupied wings together, opening to the sea in the SE.
    annulus('upper civic promenade',0,470,910,1150,115,650,15,-.15*math.pi,1.48*math.pi,'pearl',100)
    # 1.8km vaulted forum. The taper opens towards daylight, not a closed end wall.
    for k in range(19):
        y=-1450+k*95;span=410+65*math.sin(k*.18);rise=220+140*k/18
        pts=[(span*math.cos(math.pi*i/48),y,105+rise*math.sin(math.pi*i/48)) for i in range(49)]
        ribbon('forum branching vault ribs',pts,8,12,'pearl')
        for side in [-1,1]:
            beam('forum splayed root',(side*span,y,105),(side*(span+90),y+20,105),13,16,'bronze')
    for stripe in range(8):
        if stripe in [2,3,5,6]:continue  # widened open skylight channels
        sections=[]
        for k in range(37):
            f=k/36;y=-1450+1710*f;span=410+65*math.sin(18*f*.18);rise=220+140*f
            sections.append([(span*math.cos(math.pi*(stripe/8+j/64)),y,111+rise*math.sin(math.pi*(stripe/8+j/64))) for j in range(9)])
        shell('forum silver roof petals',sections,'silver',5)
    # Public galleries have floors, open colonnades, stairs and unfilled portals.
    for side in [-1,1]:
        for level in range(4):
            z=105+level*20;xx=side*(460+level*14)
            box('forum gallery floors',(xx,-590,z-1.4),(86,1830,2.8),'pearl')
            if level:
                beam('gallery safety rail',(xx-side*41,-1505,z+1.1),(xx-side*41,325,z+1.1),.35,.45,'bronze')
                for yy in range(-1505,326,12):box('gallery rail posts',(xx-side*41,yy,z+.55),(.16,.16,1.1),'bronze')
            for j in range(51):
                y=-1485+j*36
                box('forum gallery piers',(xx+side*31,y,z+8),(2,2,16),'bronze')
            if level<3:
                for yy in [-1300,-500,160]:
                    # real 20m-rise stairs; detailed pedestrian certification remains outside this prototype
                    for k in range(100):
                        box('gallery stair flights',(xx,yy+k*.32,z+.1+k*.2),(5,.34,.2),'pearl')
            for yy in [-1380,-760,-100,190]:
                box('gallery lift shaft',(side*552,yy,145),(9,10,80),'dark')
        # Lower market arcade has discrete destinations, varied heights and open passage mouths.
        for j in range(11):
            street_block('forum market',side*566,-1370+j*142,105,64,90,2+(j%3))
    # Cross bridges at different distances, with guarded edges.
    for y,z in [(-980,185),(-120,245),(420,650)]:
        width=15 if z<300 else 36
        box('forum cross bridge',(0,y,z-2),(1080,width,4),'pearl')
        for side in [-1,1]:beam('bridge parapet',(-540,y+side*width/2,z+1.1),(540,y+side*width/2,z+1.1),.6,1.1,'bronze')
    # Human-scale forecourt within the roofed volume, with gardens, seats and inset channels.
    for x in [-300,300]:
        box('forum reflecting channel',(x,-550,105.1),(22,1640,.25),'water')
        for y in range(-1420,260,65):
            box('forum tree planters',(x+(-25 if x<0 else 25),y,105.6),(9,14,1.2),'paving')
            tree(x+(-25 if x<0 else 25),y,106.2,13)
            box('forum benches',(x+(-38 if x<0 else 38),y,105.45),(1,5,.9),'bronze')
    for i in range(130):person(rng.uniform(-260,260),rng.uniform(-1460,380),105)
    # City within the room: smaller destination courts interrupt the empty ceremonial apron.
    for x,y in [(-80,-940),(170,-640),(-170,-350),(140,60),(80,-1260)]:
        box('forum civic island',(x,y,105.3),(85,120,.6),'pearl')
        for dx in [-24,24]:
            tree(x+dx,y+27,105.6,11)
            box('civic court bench',(x+dx,y+9,106.05),(6,1,.9),'bronze')
        street_block('public reading pavilion',x,y-20,105.6,43,32,1)
    # Detailed near-camera city street at the west edge, offset from the broad ceremonial nave.
    for y in [-1350,-1240,-1130]:
        street_block('library lane',-205,y,105,48,64,3)
        tree(-164,y,105,9)
    box('library awning',(-179,-1270,113.2),(12,280,1),'pearl')
    for y in range(-1390,-1120,14):box('library awning posts',(-174,y,109),(.45,.45,8),'bronze')
    # Freestanding colonnade gives a second, close spatial frame without closing the distant view.
    for yy in [-1345,-1320,-1295,-1270,-1245,-1220]:
        box('lane seating',(-161,yy,105.45),(1.4,5,.9),'bronze')
        box('lane planter',(-144,yy,105.6),(4,7,1.2),'pearl')
    # An outward-looking public gallery is built into the eastern edge, with real roof and doors.
    box('EAST_GALLERY_REAL_FLOOR',(920,-960,115),(560,90,8),'pearl')
    box('east gallery roof',(920,-960,142),(560,96,4),'pearl')
    for xx in range(660,1200,30):
        for yy in [-1002,-918]:box('east gallery colonnade',(xx,yy,128.5),(1.8,1.8,23),'bronze')
    for xx in range(680,1180,75):
        tree(xx,-930,119,9)
        box('east gallery reading benches',(xx,-970,119.45),(8,1.4,.9),'bronze')
    for i in range(18):person(665+i*28,-960+5*math.sin(i),119)
    # Readable furniture and protective edge in the outward-facing public room.
    for xx in [760,840,920,1000,1080,1160]:
        box('reading tables',(xx,-948,119.78),(3.2,1.3,.12),'bronze')
        for dx in [-1.2,1.2]:box('reading table legs',(xx+dx,-948,119.38),(.12,.6,.76),'bronze')
        for yy in [-946.6,-949.4]:
            box('reading seats',(xx,yy,119.45),(2.6,.45,.15),'pearl')
            box('reading seat backs',(xx,yy,119.85),(2.6,.15,.8),'pearl')
    for xx in range(655,1200,12):box('reading gallery edge posts',(xx,-916,119.55),(.15,.15,1.1),'bronze')
    beam('reading gallery open parapet',(650,-916,120.1),(1200,-916,120.1),.18,.2,'bronze')
    for i in range(12):person(-157+rng.uniform(-4,9),-1350+i*17,105)
    # Outdoor sea terrace shares the same forum datum, actual open edge.
    box('SEA_TERRACE_REAL_FLOOR',(1110,-800,96),(1100,1400,18),'paving')
    for j in range(8):street_block('harbor terraces',1000+j*62,-320+45*math.sin(j),105,48,75,3+j%4)
    for x in range(680,1640,70):tree(x,-1390,105,12)
    for y in [-1350,-1000,-650]:
        box('water stairs landing',(1650,y,100),(180,120,10),'pearl')

def sky_cities():
    global GROUP
    GROUP='SIX_UNASSIGNED_SKY_STUDIES'
    specs=[('A_GARDEN',-2700,700,650,660,410,.15),('B_HARBOR',2250,-650,780,760,360,-.25),
           ('C_CULTURE',2050,1900,1240,620,550,.38),('D_RIDGE',-2100,2700,1450,590,410,-.3),
           ('E_OBSERVATORY',580,3100,1870,590,350,.5),('F_CASCADE',-2700,-1250,460,570,370,-.4)]
    for idx,(name,x,y,z,rx,ry,turn) in enumerate(specs):
        # A thick occupied perimeter with a real open central city court, stepped floors and exposed underside arches.
        for k in range(12+idx%3*3):
            t=k/16;s=1-.21*t
            # Different section logic for each place: harbor horseshoe, offset cascade,
            # long garden crescent, compact cultural court, tall observatory, split ridge.
            a0=[.05,-.05,.12,.05,-.25,.08][idx]*math.pi
            a1=[1.30,1.62,1.9,1.38,1.15,1.72][idx]*math.pi
            ox=[0,k*5,0,-k*6,k*3,k*8][idx];oy=[k*4,0,0,k*2,0,-k*5][idx]
            sx=s*(1.12 if idx==0 else 1);sy=s*(.7 if idx==0 else 1)
            if idx==4:sy=1-k*.028;sx=1-k*.036
            annulus(name+' occupied decks',x+ox,y+oy,rx*sx,ry*sy,100+idx*6,z+k*10,2.3,a0,a1,'pearl',72)
            if k%3!=0:annulus(name+' recessed bands',x+ox,y+oy,rx*sx-9,ry*sy-9,73,z+k*10+7,4.5,a0,a1,'dark',72)
        # Street crosses the interior as inhabited bridges; no monolithic slab filling the city bowl.
        for side in [-1,1]:
            box(name+' interior boulevard',(x,y+side*ry*.33,z+22),(rx*1.55,32,5),'paving')
            for j in range(7):
                xx=x-rx*.65+j*rx*.21;yy=y+side*ry*.4
                street_block(name+' mixed use',xx,yy,z+24.5,58+idx*2,60,4+j%4)
                tree(xx,yy-side*42,z+24.5,10)
        for j in range(9):
            a=j*2*math.pi/9
            pts=[]
            for k in range(21):
                t=k/20
                pts.append((x+rx*.89*math.cos(a)*math.cos(t*math.pi/2),y+ry*.89*math.sin(a)*math.cos(t*math.pi/2),z-20-160*math.sin(t*math.pi/2)))
            ribbon(name+' underside basket arches',pts,13,15,'silver')
        # Distinct civic canopy / garden / spire silhouette at each court's rear.
        if idx%2==0:
            for j in range(6):
                yy=y+70+j*24
                pts=[(x+210*math.cos(math.pi*k/32),yy,z+65+170*math.sin(math.pi*k/32)) for k in range(33)]
                ribbon(name+' civic canopy',pts,6,10,'bronze')
        else:
            for j in range(3):
                xx=x-150+j*150
                street_block(name+' stepped civic library',xx,y+ry*.45,z+130,110,80,10-j*2)
    record('qa/SCOPE.json',{'sky_prototypes':[{'id':s[0],'origin_m':s[1:4],'formal_H_assignment':None} for s in specs],
         'status':'Independent provisional composition; NOT canonical H1-H6, SB, W0 or city master',
         'unfinished':['All sky-district full public interiors','SB01-SB16 complete models','Official anchors and transforms','Full pedestrian/rail operations','General-building full exterior design across 10km']})

def context_city():
    global GROUP
    GROUP='SECONDARY_CITY_RESEARCH'
    # District-specific clusters, not an even city carpet. SW void kept empty.
    for idx,(cx,cy,nx,ny) in enumerate([(-2050,650,7,10),(2000,700,7,9),(200,2350,9,5),(2600,-1300,8,3)]):
        for i in range(nx):
            for j in range(ny):
                x=cx+(i-nx/2)*92;y=cy+(j-ny/2)*115
                z=terrain_z(x,y)+10
                if z<0:continue
                street_block('city fabric '+str(idx),x,y,z,54+18*rng.random(),70,4+rng.randrange(12),.05*math.sin(i))
    # Four major secondary public buildings, deliberately unassigned to protected facility IDs.
    GROUP='FOUR_UNASSIGNED_LANDMARKS'
    for j in range(2):
        x=2650+j*480;y=-2400+j*180;z=100
        box('twin conservatory floor',(x,y,z),(400,650,10),'paving')
        for k in range(12):
            yy=y-300+k*55
            pts=[(x+200*math.cos(math.pi*i/32),yy,z+270*math.sin(math.pi*i/32)) for i in range(33)]
            ribbon('conservatory vaults',pts,8,10,'pearl')
    for k in range(22):
        z=130+k*25
        annulus('sea sail floors',3600,650,440*(1-k*.019),210,85,z,3,0,1.4*math.pi,'silver',48)
    for j in range(3):
        x=1500+j*360;y=3600;z=terrain_z(x,y)+20
        for k in range(12):annulus('mountain sanctuary galleries',x,y,180-k*5,160-k*4,55,z+k*15,3,0,1.8*math.pi,'pearl',40)
    for side in [-1,1]:
        for k in range(22):annulus('south gateway inhabited pier',side*350,-2650,170-k*3,140,65,100+k*22,3,0,2*math.pi,'pearl',28)
    ribbon('gateway rising lintel',[(-350,-2650,540),(0,-2650,620),(350,-2650,540)],55,60,'silver')
    GROUP='TRANSIT_RESEARCH'
    # Shared endpoints are geometrically joined; vehicle/grade/station operation NOT certified.
    routes=[[(0,-2400,105),(0,-1700,105)],[(570,-760,180),(1500,-900,400),(2250,-650,805)],
            [(-1250,100,480),(-2150,250,610),(-2700,700,675)],[(50,1500,1250),(1450,2000,1265),(2050,1900,1265)],
            [(-900,1450,1000),(-1900,2300,1300),(-2100,2700,1475)],[(0,1700,1740),(580,3100,1895)]]
    for i,pts in enumerate(routes):
        ribbon('transit viaduct '+str(i),pts,28,12,'dark')
        for side in [-1,1]:ribbon('transit rails '+str(i),[(x+side*7,y,z+8) for x,y,z in pts],1,1.2,'bronze')
        for x,y,z in pts[1:-1]:beam('transit piers',(x,y,terrain_z(x,y)),(x,y,z-8),18,22,'pearl')
    record('qa/TRANSIT.json',{'research_paths':routes,'official_axis_or_V_assignment':None,'certification':'GEOMETRY ONLY. Grade, complete stations, circulation and operations unfinished.'})

def flush():
    for (group,name,mat),(vs,fs) in BATCH.items():
        me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update()
        bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
        ob=bpy.data.objects.new(name,me);co=bpy.data.collections.get(group)
        if not co:co=bpy.data.collections.new(group);bpy.context.scene.collection.children.link(co)
        co.objects.link(ob);me.materials.append(MATS[mat]);ob['study_group']=group
        ob['provenance']='R28 newly authored, provisional relative art coordinates only'
        if mat in ['water','terrain']:
            for p in me.polygons:p.use_smooth=True
    BATCH.clear()

CAMERAS=[
 ('01_ESTUARY_CITY', (8400,-10600,4200),(-250,550,1050),43,None),
 ('02_CENTRAL_CHOIR', (3900,-4900,2100),(-300,620,1370),32,None),
 ('03_FORUM_HUMAN', (105,-1390,106.7),(-90,580,310),23,'FORUM_REAL_FLOOR'),
 ('04_LIBRARY_LANE', (-168,-1350,106.7),(-154,-700,145),26,'FORUM_REAL_FLOOR'),
 ('05_SEA_TERRACE', (1460,-1430,106.7),(-200,800,1700),24,'SEA_TERRACE_REAL_FLOOR'),
 ('06_REAR_NORTH', (1000,5400,4300),(0,800,1300),38,None),
 ('07_SKY_COURT', (2280,-769,806.2),(-200,800,1600),25,'B_HARBOR interior boulevard'),
 ('08_WHOLE_CITY', (8500,-11000,11000),(0,600,500),43,None),
 ('09_UPPER_CIVIC_PROMENADE', (860,230,651.7),(2250,-650,850),30,'upper civic promenade'),
]

def setup():
    sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
    sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=32;sc.cycles.use_denoising=True
    sc.render.threads_mode='FIXED';sc.render.threads=4
    sc.render.resolution_x=1600;sc.render.resolution_y=1000;sc.render.resolution_percentage=100
    sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGB'
    sc.world=bpy.data.worlds.new('pearl marine daylight');sc.world.use_nodes=True
    bg=sc.world.node_tree.nodes.get('Background');bg.inputs[0].default_value=(.38,.55,.70,1);bg.inputs[1].default_value=.5
    ld=bpy.data.lights.new('sun','SUN');ld.energy=3;ld.angle=.12
    ob=bpy.data.objects.new('sun',ld);sc.collection.objects.link(ob);ob.rotation_euler=(.5,-.36,-.55)
    sc.view_settings.view_transform='AgX';sc.view_settings.exposure=.35
    # Architectural soffit lighting is fixed to gallery roofs, never attached to cameras.
    for side in [-1,1]:
        for yy in [-1200,-600,0]:
            ld=bpy.data.lights.new('forum gallery architectural light','AREA');ld.energy=350000;ld.shape='RECTANGLE';ld.size=55;ld.size_y=130;ld.color=(1,.79,.54)
            o=bpy.data.objects.new(ld.name,ld);sc.collection.objects.link(o);o.location=(side*470,yy,182)
    for name,pos,target,lens,floor in CAMERAS:
        ca=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,ca);sc.collection.objects.link(o)
        o.location=pos;o.rotation_euler=(Vector(target)-Vector(pos)).to_track_quat('-Z','Y').to_euler()
        ca.lens=lens;ca.clip_start=.1;ca.clip_end=90000
        o['floor_expected']=floor or '';o['target_m']=list(target)
    sc.camera=bpy.data.objects['01_ESTUARY_CITY']
    sc['status']='INDEPENDENT ART RESEARCH. Not adopted; not finished city master. No world writes.'
    sc['revision']=REVISION

def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version=0
    material('pearl',(.77,.82,.81),.26,.37)
    material('silver',(.42,.55,.60),.65,.32)
    material('dark',(.045,.095,.115),.35,.46)
    material('bronze',(.38,.23,.095),.65,.4)
    material('paving',(.46,.50,.47),.1,.65)
    material('green',(.055,.16,.10),0,.88)
    material('water',(.025,.13,.17),.5,.22)
    material('terrain',(.16,.21,.21),0,.92)
    material('human',(.055,.045,.035),0,.9)
    terrain();central();sky_cities();context_city();flush();setup()
    bpy.context.view_layer.update()
    record('qa/BUILD.json',{'revision':REVISION,'blender':bpy.app.version_string,'seed':281026,
        'meshes':sum(o.type=='MESH' for o in bpy.context.scene.objects),'units':'metres',
        'base':'60bff854b8cec7265a50de34190d740a626d4c13','canonical_transform':None,
        'method':'Designed floor plates, occupied arc sectors, solid roof sweeps, articulated ribs, actual galleries; background Blender Python',
        'formal_art_adoptions':0,'minecraft':'HOLD'})
    bpy.ops.wm.save_as_mainfile(filepath=str(R/'model/R28_CELESTIAL_ESTUARY.blend'),compress=True)
    bpy.ops.object.select_all(action='DESELECT')
    for ob in bpy.context.scene.objects:
        if ob.type=='MESH':ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(R/'model/R28_CELESTIAL_ESTUARY.glb'),export_format='GLB',use_selection=True,export_apply=True)
    print('R28_BUILD_FINISHED',flush=True)

def render():
    bpy.ops.wm.open_mainfile(filepath=str(R/'model/R28_CELESTIAL_ESTUARY.blend'))
    sc=bpy.context.scene
    names=ARGS[1:] or [c[0] for c in CAMERAS]
    preview='--preview' in names
    names=[n for n in names if n!='--preview']
    if preview:sc.render.resolution_percentage=65;sc.cycles.samples=12
    for name in names:
        sc.camera=bpy.data.objects[name];sc.render.filepath=str(R/('process' if preview else 'renders')/(name+'.png'))
        print('RENDER_START',name,flush=True);bpy.ops.render.render(write_still=True);print('RENDER_DONE',name,flush=True)

if __name__=='__main__':
    if ARGS[0]=='build':build()
    elif ARGS[0]=='render':render()
    else:raise ValueError(ARGS)
