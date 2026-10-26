"""R32-A: three inhabited canyon cities jointly form one porous urban massif.
Background Blender only. Rebuild R32 outputs, never write source studies.
-- 1 = primary mass prototype; -- 2 = macro revision after real image review.
"""
import sys, math, json, hashlib
from pathlib import Path
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R))
import bpy,bmesh
from mathutils import Vector
import meshkit as g
from meshkit import box,beam,deck,surface,ribbon,path,people,tree
REV=int(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else 1
SOURCE=R.parent/'R31/model/R31_A.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));g.materials()
removed=[]
for o in list(bpy.context.scene.objects):
    if o.type=='MESH' and str(o.get('study_group','')).startswith('R31_'):
        removed.append(o.name);g.remove(o)
for o in list(bpy.data.objects):
    if o.type=='CAMERA' and o.name=='09_EAST_PUBLIC':g.remove(o)

def group(n):g.GROUP='R32_'+n
def annular(name,c,r0,r1,a0,a1,z,thick,mat='ivory',slope=0):
    rows=[]
    for i in range(max(2,int(abs(a1-a0)/4))+1):
        a=math.radians(a0+(a1-a0)*i/max(2,int(abs(a1-a0)/4)))
        rows.append([(c[0]+r*math.cos(a),c[1]+r*math.sin(a),z+(r-r0)*slope) for r in (r0,r1)])
    surface(name,rows,thick,mat)
def pos(c,r,a,z):
    a=math.radians(a);return (c[0]+r*math.cos(a),c[1]+r*math.sin(a),z)
def local(c,angle,x,y,z):
    co,si=math.cos(angle),math.sin(angle)
    return (c[0]+x*co-y*si,c[1]+x*si+y*co,z)
def precinct(name,c,ang,w,d,z,h,kind):
    """Occupied 120–300m deep section: actual open courtyard, loggias, cross hall.
    These are macro precinct studies; not finished ordinary building exteriors.
    Local x is along the street, local y points outward from the canyon.
    """
    def b(n,x,y,zz,ww,dd,hh,m='ivory'):
        box(name+' '+n,local(c,ang,x,y,zz),(ww,dd,hh),m,ang)
    # Two inhabited flanks leave a 55–100m through court. No solid mother shell.
    for side in (-1,1):
        b('inhabited flank',side*w*.37,0,z+h*.43,w*.24,d,h*.86,'recess')
        # 18–28m communal floor spacing; they are real overhangs, not texture stripes.
        count=max(3,int(h/27))
        for k in range(count):
            zz=z+12+k*(h-20)/count
            inset=(k%3)*w*.012
            b('deep open loggia',side*(w*.34-inset),-d*.03,zz,w*.34,d*1.07,3,'porcelain')
        for j in range(4):
            p=local(c,ang,side*w*.50,-d*.44+j*d*.29,z)
            q=local(c,ang,side*w*.46,-d*.44+j*d*.29,z+h*.91)
            beam(name+' inhabited exterior blade',p,q,4.5,7,'ivory')
    b('public court real floor',0,0,z-6,w,d,12,'ground')
    # A service/arrival room at the rear has a 35m central doorway, never a blind wall.
    for side in (-1,1):b('rear arrival bank',side*w*.32,d*.39,z+h*.3,w*.27,d*.20,h*.6,'ivory')
    b('rear public lintel',0,d*.40,z+h*.63,w*.89,d*.23,15,'porcelain')
    if kind==0:
        # Offset roof gardens; sky remains visible through the middle.
        for side in (-1,1):b('roof garden',side*w*.35,0,z+h*.90,w*.33,d*.80,5,'garden')
    elif kind==1:
        rows=[[local(c,ang,x,yy,z+h*(.88+(.16 if x>0 else 0))) for x in (-w*.53,0,w*.50)] for yy in (-d*.18,d*.52)]
        surface(name+' oblique civic canopy',rows,10,'ivory')
    else:
        b('upper public cross gallery',0,d*.12,z+h*.73,w*.95,48,10,'porcelain')
        b('upper open reading room',w*.12,d*.12,z+h*.88,w*.36,55,13,'ivory')

def scarp(name,c,angle,w,d,base,top,kind):
    """Deep occupied section: four inhabited banks enclose a radial cavern.
    The large through-aperture, galleries and top court are actual geometry.
    """
    height=top-base
    def b(n,x,y,z,ww,dd,hh,m='ivory'):
        box(name+' '+n,local(c,angle,x,y,z),(ww,dd,hh),m,angle)
    for side in (-1,1):
        b('deep occupied civic bank',side*w*.35,0,base+height*.5,w*.28,d,height,'recess')
        for k,t in enumerate((.12,.28,.49,.72,.91)):
            b('inhabited bank ledge',side*w*.34,-d*.02,base+height*t,w*.35,d*1.09,9,'porcelain')
    b('cavern lower city floor',0,0,base+38,w,d,76,'ivory')
    b('cavern upper inhabited ceiling',0,0,top-48,w,d,96,'ivory')
    for t in (.33,.68):b('cavern transverse public gallery',0,d*(.12 if t<.5 else -.24),base+height*t,w*.92,40,12,'porcelain')
    if kind==1:
        rows=[[local(c,angle,-w*.48,yy,top+20),local(c,angle,0,yy,top+90),local(c,angle,w*.48,yy,top+5)] for yy in (-d*.48,d*.50)]
        surface(name+' tectonic roof garden fold',rows,15,'porcelain')

# Three independent city basins, sharing inhabited vertical districts.
# Radius/height/rotation are not derived from the old rising transport spline.
WORLDS=[
    ('LOWER_ESTUARY',(-1100,450),1000,570,1230,-18,209,5,112),
    ('UPPER_CONCORD',(600,1250),2190,640,1510,-25,211,6,112),
    ('CROWN_GARDEN',(-440,1950),3310,450,1090,-1,226,5,123),
]
for wi,(name,c,z,ri,ro,a0,a1,tiers,rise) in enumerate(WORLDS):
    group(name)
    N=[11,13,10][wi]
    # Individual wedge neighbourhoods form the cliff. Variable crowns interrupt
    # the global contour, and 20m slots make real light wells between precincts.
    for j in range(N):
        a=a0+(a1-a0)*(j+.5)/N
        da=(a1-a0)/N
        shift=28*math.sin(j*1.7+wi)
        for k in range(tiers):
            r=ri+(ro-ri)*(k+.5)/tiers
            zz=z+k*rise+shift
            w=r*math.radians(da)*.87
            d=(ro-ri)/tiers+18
            # Bases step downward by different depths; no single flat underside.
            hh=rise*(1.4+(.25 if (j+k)%3==0 else 0))
            cc=pos(c,r,a,0)
            if REV>=2:
                # Macro revision: a connected deep city landform replaces the
                # sparse floating precincts. Each district retains a real void.
                bot=z-410+55*math.sin(j*.9+wi)
                scarp(name+' cavern district '+str(j)+' step '+str(k),cc,math.radians(a-90),w*1.08,d*1.24,bot,zz,(j+k)%3)
            precinct(name+' quarter '+str(j)+' tier '+str(k),cc,math.radians(a-90),w,d,zz,hh,(j+2*k+wi)%3)
        # A lower inhabited rib reaches toward the next world/ground.
        if j%2==0 and REV==1:
            r=ri+(ro-ri)*.64
            bot=z-[570,640,420][wi]-(j%3)*65
            p=pos(c,r*.96,a,bot);q=pos(c,r,a,z+rise)
            # Twin occupied buttresses enclose a real vertical public throat.
            tang=Vector((-math.sin(math.radians(a)),math.cos(math.radians(a)),0))
            for side in (-1,1):
                off=tang*side*65
                beam(name+' inhabited hanging buttress',Vector(p)+off,Vector(q)+off,72,145,'recess')
            for ll in range(4):
                zz=bot+(z+rise-bot)*(ll+.1)/4
                qq=pos(c,r,a,zz)
                box(name+' lower interworld public gallery',qq,(240,170,11),'porcelain',math.radians(a-90))
    # Several broad city streets follow the actual topography, not a single rail.
    for k in (0,2,4):
        rr=ri+(ro-ri)*k/tiers
        annular(name+' contour public avenue',c,rr-30,rr+35,a0,a1,z+k*rise+2,12,'porcelain')
    # Three enormous sky windows remain between the unequal city walls.
    for j in (2,6,9):
        a=a0+(a1-a0)*(j+.5)/N
        pts=[pos(c,r,a,z+2*rise+8) for r in (ri-130,ri+260)]
        ribbon(name+' canyon cross street',pts,58,15,'porcelain')

# Broad, independently drawn occupied urban piers integrate the worlds. Their
# paired walls and transverse galleries expose 150–350m public rooms front/back.
group('INTERWORLD_URBAN_ESCARPMENTS')
PIERS=[(-1780,1250,105,2100,460,650,-60),(-720,2240,450,3660,560,690,160),
       (1250,2120,810,3270,570,620,-180),(210,2750,1450,4210,510,580,-250)]
if REV>=2:
    PIERS=[(-1680,1510,105,2230,650,780,170),(670,2460,640,4180,840,840,-400)]
for j,(x,y,z0,z1,w,d,lean) in enumerate(PIERS):
    if REV>=2:
        # Unequal urban ravines replace the regularly repeated tower sections.
        levels=[z0,z0+(z1-z0)*.21,z0+(z1-z0)*.49,z0+(z1-z0)*.75,z1]
        for k,(lo,hi) in enumerate(zip(levels,levels[1:])):
            t=k/3;cc=(x+lean*t,y+90*math.sin(t*math.pi))
            scarp('interworld urban ravine '+str(j)+' '+str(k),cc,math.radians((-11,23)[j]),w*(1-t*.25),d,lo,hi+60,k%3)
            precinct('ravine hanging neighbourhood '+str(j)+' '+str(k),(cc[0],cc[1]-d*.39),.1,w*.80,210,hi-100,150,k%3)
        continue
    for k in range(int((z1-z0)/190)):
        t=k/max(1,int((z1-z0)/190)-1);z=z0+k*190
        # Alternating court orientation and setbacks make occupied discontinuous
        # cliffs; these are not long conduits wrapped in a reinstated R30 shell.
        precinct('interworld urban pier '+str(j)+' level '+str(k),(x+lean*t,y+70*math.sin(t*math.pi)),
                 math.radians((-8,16,-20,31)[j]),w*(1-.24*t),d*(1-.15*t),z,210,(k+j)%3)

group('PUBLIC_WORLD_CONNECTIONS')
# Grounded low city and high city share physically modelled arrival streets.
ribbon('R32_1000_REAL_STREET',[(-2260,320,1000),(-1720,320,1000),(-1160,480,1000)],100,18,'porcelain')
ribbon('R32_2190_REAL_STREET',[(-830,840,2190),(-100,840,2190),(650,980,2190),(1190,1250,2190)],110,20,'porcelain')
# Deep public cross-city causeway: paired inhabited banks with a broad open nave.
for side in (-1,1):
    for j in range(5):
        precinct('concordance bridge bank '+str(side)+' '+str(j),(-700+j*360,1120+side*190),0,310,155,2190,140+30*(j%2),j%3)
deck('R32_CONCORD_FORUM_FLOOR',[(-890,880),(1060,880),(1170,1350),(-890,1350)],2190,24,'porcelain')
# Only 3 disconnected roof fingers, leaving large open sky slots over the nave.
for j in range(3):
    x=-590+j*550
    surface('concordance civic crossing roof', [[(x-100,920,2440),(x+100,920,2460)],[(x-70,1320,2480),(x+120,1320,2440)]],14,'ivory')
# Discrete vertical transit shafts/stations; not silhouette-defining long rails.
group('TRANSIT_CONFLUENCES')
for x,y,z0,z1 in [(-1660,1240,105,2190),(1150,2070,1000,3310),(-700,2210,1000,3820)]:
    for dx in (-32,32):beam('paired transit shafts',(x+dx,y,z0),(x+dx,y,z1),18,30,'bronze')
    for z in (1000,2190,3310):
        if z0<=z<=z1:
            box('transit platform',(x,y,z-7),(180,140,14),'porcelain')
            for s in (-1,1):box('transit arrival hall flank',(x+s*65,y,z+20),(34,120,40),'recess')

group('INHABITED_GROUND_ARRIVALS')
for x,y,hh in [(-1730,1080,420),(-1270,1280,560),(1270,2070,700)]:
    precinct('ground urban footing',(x,y),.1,380,460,105,hh,1)
ribbon('ground arrival public boulevard',[(-1100,-850,105),(-1450,-80,105),(-1730,850,105)],100,12,'porcelain')
people([(90+i*5,-1610+i*12,105) for i in range(14)])
people([(-620+i*20,840,2190) for i in range(22)])

g.flush()
for o in bpy.context.scene.objects:
    if o.type=='MESH' and str(o.get('study_group','')).startswith('R32_'):
        o['provenance']='R32 independent relative-metre architectural study; NOT formal city allocation'
        bm=bmesh.new();bm.from_mesh(o.data)
        bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
        o.data.update()
sc=bpy.context.scene
g.camera('09_EXPLORATORY_FORUM',(100,1100,2191.7),(1000,1360,2380),26,'R32_CONCORD_FORUM_FLOOR')
sc['study']='R32-A INHABITED CONCORDANCE / 天層共都'
sc['revision']=REV
sc['formal_art']='UNADOPTED / 0 accepted central artworks / Minecraft HOLD / CITY MASTER incomplete'
sc['coordinates']='Relative research metres; certified formal anchors 0'
sc['source_R31_sha256']=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
for n,f in [('03_PUBLIC','R32_1000_REAL_STREET'),('07_SKY_STREET','R32_2190_REAL_STREET'),('04_HUMAN','B_HUMAN_THRESHOLD_FLOOR')]:bpy.data.objects[n]['support_floor']=f
sc.camera=bpy.data.objects['02_CENTRAL'];sc.view_layers[0].material_override=None
bpy.context.preferences.filepaths.save_version=0
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'model/R32_A.blend'),compress=True)
g.record('qa/BUILD.json',{'revision':REV,'source_R31_sha256':sc['source_R31_sha256'],'removed_R31_meshes':removed,'worlds':WORLDS,'piers':PIERS,'boolean_operations':0,'blender':bpy.app.version_string})
print('R32_BUILD_COMPLETE',REV,flush=True)
