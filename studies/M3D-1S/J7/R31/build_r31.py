"""R31 Ascendant Confluence: R30-B research copy, explicitly authored sectional city.
No canonical/world data. No Boolean excavation of a single parent object.
Run background Blender: --python build_r31.py -- 1|2. Output limited to R31.
"""
import sys, math, json, hashlib
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy, bmesh
from mathutils import Vector
import meshkit as g
from meshkit import box, beam, path, surface, deck, ribbon, catmull, people, tree
R = Path(__file__).resolve().parent
REV = int(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else 1
SOURCE = R.parent/'R30/model/R30_B.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
g.materials()

# Keep only the research basin/shore experience and shared provisional context.
# The sculptural parent masses, inserted sky houses and shelf floors are replaced.
keep_prefix = ('B shore', 'B foreground', 'B forecourt', 'B tidal',
               'B_REAL_LOW', 'B_HUMAN_THRESHOLD', 'B inhabited shore',
               'B east tidal', 'B basin diagonal')
removed = []
for ob in list(bpy.context.scene.objects):
    if ob.type == 'MESH' and str(ob.get('study_group','')).startswith('B_'):
        if not ob.name.startswith(keep_prefix):
            removed.append(ob.name); g.remove(ob)

def group(label): g.GROUP = 'R31_'+label

def profile(name, outline, y, depth, material='ivory'):
    """Closed, individually drawn architectural XZ section, extruded in Y."""
    n=len(outline)
    vs=[(x,y+d,z) for d in (-depth/2,depth/2) for x,z in outline]
    fs=[tuple(reversed(range(n))),tuple(n+i for i in range(n))]
    fs += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    g.add(name,vs,fs,material)

def conduit(name, keys, depth=180, height=130, material='ivory'):
    """A bent inhabitable conduit; explicit open gaps exist between separate conduits."""
    if REV>=3 and name in ('R31 south ascending city keel','R31 north returning city keel'):
        depth*=1.65;height*=1.4
        # The upper inhabited landscape spreads into a broad confluence crown,
        # replacing the prototype's long, skinny, upturned rail tips.
        keys=[(x,y,min(z,4000)) for x,y,z in keys]
        keys[-1]=(keys[-1][0]+160,keys[-1][1],3920 if 'south' in name else 4020)
    pts=catmull(keys,9)
    rows=[]
    for i,p in enumerate(pts):
        t=i/(len(pts)-1); x,y,z=p
        d=depth*(.68+.32*math.sin(math.pi*t))
        h=height*(.68+.32*math.sin(math.pi*t))
        rows.append([(x,y-d*.5,z-h*.38),(x,y-d*.58,z+h*.18),
                     (x,y-d*.30,z+h*.58),(x,y+d*.34,z+h*.52),
                     (x,y+d*.55,z+h*.08),(x,y+d*.40,z-h*.44)])
    if REV==1:
        g.solid(name,rows,material)
    else:
        # Revision 2: the conduit is an occupied, daylit cross-section instead of a
        # smooth solid rail. Paired deep banks enclose a transport/public canyon.
        depth*=2.0; height*=1.65
        for side in (-1,1):
            cheek=[]
            for i,(x,y,z) in enumerate(pts):
                t=i/(len(pts)-1);d=depth*(.72+.28*math.sin(math.pi*t));h=height*(.75+.25*math.sin(math.pi*t))
                a=y+side*d*.24;b=y+side*d*.52
                cheek.append([(x,a,z-h*.40),(x,b,z-h*.31),(x,b,z+h*.35),(x,a,z+h*.53)])
            g.solid(name+' inhabited bank '+str(side),cheek,'recess')
            # Pale angled external blades reveal depth and create non-uniform facets.
            for j in range(0,len(pts)-7,7):
                p=Vector(pts[j]);q=Vector(pts[min(j+7,len(pts)-1)])
                beam(name+' inhabited side buttress',p+Vector((0,side*depth*.5,-height*.3)),q+Vector((0,side*depth*.45,height*.4)),12,24,material)
        for side in (-1,1):
            for zoff in (-.32,.10,.45):
                rows=[[(x,y+side*depth*.17,z+height*zoff),(x,y+side*depth*.57,z+height*zoff)] for x,y,z in pts]
                surface(name+' occupied canyon gallery',rows,12,material)
        # Cross room/station links are broad and infrequent, so daylight reaches below.
        for j in range(4,len(pts)-4,13):
            x,y,z=pts[j]
            box(name+' structural cross room',(x,y,z-height*.25),(110,depth*.95,25),material)
            box(name+' climate crown',(x+40,y,z+height*.48),(170,depth*1.05,24),material)
    return pts

def inhabited_pier(name, x,y,z0,z1,w,d,lean=0,kind=0):
    """Distinct double cheeks leave an open public vertical room, not a solid icon."""
    h=z1-z0
    if REV>=2 and not name.startswith('R31 north bank'):
        # Individually articulated deep precinct: an asymmetric C section through a
        # public urban room, with a vertical open throat to the transport canyon.
        sign=-1 if kind==1 else 1
        outer=[(x-w*.56,z0+h*.17),(x-w*.50,z0+h*.72),(x-w*.18+lean,z1),
               (x+w*.36+lean,z1-h*.07),(x+w*.61,z0+h*.51),(x+w*.40,z0+h*.10),
               (x-w*.04,z0-h*.05),(x-w*.56,z0+h*.17)]
        inner=[(x-w*.20,z0+h*.30),(x-w*.22,z0+h*.62),(x-w*.04+lean*.6,z0+h*.80),
               (x+w*.17+lean*.5,z0+h*.79),(x+w*.28,z0+h*.50),(x+w*.15,z0+h*.27),
               (x-w*.02,z0+h*.20),(x-w*.20,z0+h*.30)]
        # Each wall is deeper than a tower facade; open front/back rooms show city section.
        dd=d*(1.65 if kind==2 else 1.4)
        for j in range(7):
            if (kind==0 and j==4) or (kind==1 and j==1) or (kind==2 and j==5):continue
            quad=[outer[j],outer[j+1],inner[j+1],inner[j]]
            if REV>=4 and j in (0,3,5):
                # True transverse public rooms replace formerly blind deep prism faces.
                # Four independently closed perimeter members leave a through-aperture.
                centre=Vector((sum(p[0] for p in quad)/4,sum(p[1] for p in quad)/4))
                inside=[tuple(centre+(Vector(p)-centre)*.56) for p in quad]
                for k in range(4):
                    profile(name+' pierced deep city room '+str(j)+' frame '+str(k),[quad[k],quad[(k+1)%4],inside[(k+1)%4],inside[k]],y,dd,'ivory' if j%3 else 'porcelain')
                for side in (-1,1):
                    for k in range(3):
                        t=(k+1)/4
                        a=Vector(inside[0]).lerp(Vector(inside[1]),t)
                        b=Vector(inside[3]).lerp(Vector(inside[2]),t)
                        beam(name+' deep-room climate blades',(a.x,y+side*dd*.5,a.y),(b.x,y+side*dd*.5,b.y),4,8,'bronze')
            else:
                profile(name+' thick urban fold '+str(j),quad,y,dd,'ivory' if j%3 else 'porcelain')
        # Habitable recesses and independent galleries exist in the mass depth, and
        # extend to both faces instead of decorating only the primary camera side.
        for side in (-1,1):
            for j in range(6):
                t=(j+.8)/7;zz=z0+h*t;xx=x+lean*t
                ww=w*(.56+.12*math.sin(t*math.pi))
                yy=y+side*(dd*.48+22)
                box(name+' deep facade city rooms',(xx+sign*w*.16,yy,zz+23),(ww,80,46),'recess')
                box(name+' inhabited threshold',(xx+sign*w*.16,yy,zz),(ww+18,105,8),'porcelain')
                for k in range(4):
                    bx=xx-ww*.5+k*ww/3+sign*w*.16
                    beam(name+' climate brise',(bx,yy+side*45,zz),(bx+sign*18,yy+side*45,zz+55),4,7,'ivory')
        # Interior communal bridges stay within actual chamber boundaries.
        for t in (.31,.57):
            zz=z0+h*t
            box(name+' interior public room floor',(x+lean*t,y,zz),(w*.56,dd*.78,15),'porcelain')
        return
    for side in (-1,1):
        sx=x+side*w*.34
        outline=[(sx-w*.15,z0),(sx+w*.15,z0+15),
                 (sx+lean+w*.11,z1-h*.12),(sx+lean+w*.07,z1),
                 (sx+lean-w*.14,z1-h*.04),(sx-w*.17,z0+h*.24)]
        profile(name+' occupied cheek '+str(side),outline,y,d,'recess')
        # Finite strips express the height of an inhabited wall, not full-city floor bands.
        for j,t in enumerate((.06,.17,.31,.49,.68,.83,.94)):
            z=z0+h*t;xx=sx+lean*t
            ww=w*(.33 if j in (2,4) else .27)
            box(name+' local inhabited ledges',(xx,y,z),(ww,d+22,4 if j%2 else 7),'porcelain')
        for yy in (y-d*.5-4,y+d*.5+4):
            for k in range(6):
                t=(k+.5)/6
                beam(name+' vertical facade blade',(sx-w*.13+k*w*.052,yy,z0+35),
                     (sx+lean-w*.11+k*w*.045,yy,z1-35),2.4,5,'ivory')
    # Only 3 major public connections; a huge central atrium remains genuinely empty.
    for j,t in enumerate((.05,.45,.88)):
        z=z0+h*t;xx=x+lean*t
        box(name+' public cross-room floor',(xx,y,z),(w*.85,d*.70,12),'porcelain')
        if j==1:
            for side in (-1,1):
                beam(name+' cross-room diagonal',(xx+side*w*.38,y-d*.34,z),
                     (xx+side*w*.12,y-d*.34,z+h*.18),8,12,'ivory')

group('ASCENDING_INHABITED_STRUCTURE')
# Two unequal banks of the ascension canyon. These occupied structural reaches replace
# R30's blank contiguous continent. Their public void reaches from ground to crown.
conduit('R31 south ascending city keel',[(-2630,560,150),(-2240,380,690),(-1710,340,1750),(-810,500,2650),(370,1020,3030),(1390,1550,3480),(1990,1980,4300)],240,240)
conduit('R31 north returning city keel',[(-2440,1320,150),(-1800,1620,1080),(-780,1830,2120),(300,2200,2700),(1470,2590,3320),(2080,2510,4150)],260,270,'porcelain')
conduit('R31 eastern descent occupied buttress',[(2050,2340,4230),(1910,2170,3450),(1580,1830,2740),(1250,1660,2110),(1050,1500,1370),(710,1460,450)],230,230)
conduit('R31 western fork occupied buttress',[(-1880,400,1750),(-1370,180,1360),(-820,100,780),(-580,260,180)],210,210,'porcelain')
conduit('R31 transverse inhabited lintel',[(-1410,450,1800),(-1070,920,2010),(-600,1490,2200),(60,2040,2460)],210,175)
# The only long horizontal public worlds are separated, tapered bridge districts.
conduit('R31 horizon north inhabited bank',[(-860,1190,2470),(-360,1380,2520),(380,1630,2530),(1120,1680,2670),(1600,1840,2960)],220,250,'porcelain')
conduit('R31 low north city bank',[(-2100,1150,1180),(-1250,1460,1370),(-500,1800,1580),(360,2140,1940),(1000,2340,2290)],230,230)

group('PUBLIC_SECTION_CITY_PIERS')
inhabited_pier('R31 western harbour city',-1710,790,520,1910,610,290,170,0)
inhabited_pier('R31 central exchange city',-170,1740,880,2550,680,300,170,1)
inhabited_pier('R31 eastern hanging city',1420,1780,1320,3120,580,300,250,2)
inhabited_pier('R31 north civic shoulder',680,2450,1620,2990,510,350,160,1)
inhabited_pier('R31 crown climate archive',1940,2300,3330,4200,470,290,50,2)

group('CIVIC_VOIDS_REAL_GROUNDS')
# A new 2190m canyon street occupies the same camera station as R30-B, while its
# surroundings are made by city sections. Broad old polygon shelves are removed.
ribbon('R31_2190_REAL_STREET',catmull([(-940,840,2190),(-650,840,2190),(-100,840,2190),(650,980,2190),(1170,1230,2190),(1430,1560,2190)],12),100,18,'porcelain',True)
ribbon('R31_1000_REAL_STREET',catmull([(-2220,320,1000),(-1900,390,1000),(-1510,650,1000),(-1120,930,1000),(-650,1220,1000),(-170,1550,1000)],12),110,18,'porcelain',True)
# Irregular side courts have different section depths and uses; no single city shelf.
for name,outline,z in [
    ('R31 western public ferry court',[(-2110,400),(-1730,380),(-1520,640),(-1700,860),(-2130,650)],1000),
    ('R31 east interchange courtyard',[(1100,1230),(1550,1370),(1650,1710),(1340,1830),(1120,1640)],2190),
    ('R31 north rain garden',[(210,1640),(650,1820),(500,2130),(120,2050),(-20,1820)],1680),
    ('R31 high arrival court',[(1450,1840),(1910,1930),(2040,2240),(1640,2370),(1430,2130)],3020)]:
    deck(name,outline,z,22,'ground')
# A west garden ramp and a public north link enter real courts, not isolated floating rooms.
ribbon('R31 2190 north garden bridge',catmull([(200,870,2190),(250,1260,2190),(200,1620,2190)],10),60,12,'porcelain',True)
ribbon('R31 east high arrival street',catmull([(1430,1560,2190),(1610,1900,2190),(1760,2140,2190)],8),80,16,'porcelain',True)

group('TRANSPORT_AS_ARCHITECTURE')
LIFTS=[('West',(-2050,420,105),(-1550,750,1000)),
       ('Confluence',(-180,1550,1000),(240,1710,2190)),
       ('East',(1430,1560,2190),(1740,2110,3020)),
       ('Crown',(1740,2110,3020),(2000,2310,3970))]
for label,a,b in LIFTS:
    a,b=Vector(a),Vector(b); delta=b-a
    # Transport is an inhabited 3D truss shaft with a large station at each end.
    for side in (-1,1):
        aa=a+Vector((side*38,0,0));bb=b+Vector((side*38,0,0))
        path('R31 '+label+' double transit rail',[aa,bb],9,14,'bronze')
    for j in range(8):
        p=a+delta*j/8;q=a+delta*(j+1)/8
        beam('R31 '+label+' transit chevron',p+Vector((-38,0,0)),q+Vector((38,0,0)),5,9,'ivory')
    for t in (0,1):
        x,y,z=a+delta*t
        box('R31 '+label+' station real floor',(x,y,z-6),(150,150,12),'porcelain')
        for side in (-1,1):
            box('R31 '+label+' station occupied flank',(x+side*60,y,z+38),(27,130,76),'recess')
        surface('R31 '+label+' station folded canopy',[
            [(x-90,y-95,z+105),(x,y-95,z+140),(x+90,y-95,z+105)],
            [(x-75,y+95,z+85),(x,y+95,z+125),(x+75,y+95,z+85)]],6,'ivory')
        if REV>=3:
            # Station architecture is the transfer between a city ground and a
            # rising shaft, with open nave and visibly inhabited side districts.
            for side in (-1,1):
                profile('R31 '+label+' transfer station occupied bank '+str(t)+str(side),
                        [(x-120,z),(x+130,z),(x+160,z+120),(x+90,z+215),(x-95,z+180)],y+side*122,110,'recess')
                for k in (0,1,3):
                    box('R31 '+label+' transfer galleries',(x,y+side*122,z+15+k*40),(270,140,10),'porcelain')
            for yy in (y-175,y+175):
                beam('R31 '+label+' public station arch',(x-170,yy,z+12),(x-35,yy,z+260),16,24,'ivory')
                beam('R31 '+label+' public station arch',(x-35,yy,z+260),(x+175,yy,z+110),16,24,'ivory')
            box('R31 '+label+' station urban floor',(x,y,z-10),(330,380,20),'porcelain')
    for t in (.28,.69):
        p=a+delta*t
        box('R31 '+label+' visible transit cabin',p,(54,54,34),'recess')
        for side in (-1,1):box('R31 '+label+' cabin porcelain cheek',p+Vector((side*30,0,0)),(5,60,38),'porcelain')

# Three regional connections terminate at the unchanged provisional surroundings.
for label,pts in [
 ('west garden',[(-2220,320,1000),(-2490,470,850),(-2700,700,674.5)]),
 ('east harbour',[(1430,1560,2190),(2140,920,1540),(2350,150,1120),(2160,-580,804.5)]),
 ('north observatory',[(500,1920,1680),(600,2340,1800),(610,2850,1894.5)])]:
    ribbon('R31 regional '+label,catmull(pts,14),46,14,'ivory',True)

group('INHABITED_CANYON_BANKS')
# Four purpose-specific architectural ensembles, at intermediate scales. Their open
# public floors and wall thicknesses are built directly; ordinary private interiors are not.
# South 2190 public gallery: interrupted hall along the street rather than copied roofs.
for i,(x,y,w,d,h) in enumerate([(-770,640,260,165,160),(-260,670,340,180,270),(440,780,300,210,350),(1010,1030,270,220,240)]):
    # Asymmetric inhabited section with a public arcade toward the canyon street.
    profile('R31 south bank occupied house '+str(i),[(x-w/2,2190),(x+w/2,2190),(x+w*.43,2190+h*.82),(x+w*.12,2190+h),(x-w*.38,2190+h*.80)],y-d*.22,d*.58,'recess')
    for k,t in enumerate((.08,.28,.56,.82)):
        box('R31 south house accessible terrace',(x,y,2190+h*t),(w*(1-.18*t),d,6),'porcelain')
    for j in range(6):
        xx=x-w*.45+j*w*.18
        beam('R31 south bank daylight ribs',(xx,y+d*.52,2190),(xx+w*.07,y+d*.30,2190+h*.84),3.2,5,'ivory')
    # Actual ground porch has 6m of clear height and continuous floors to main street.
    box('R31 south bank open porch',(x,y+d*.46,2190-4),(w,d*.58,8),'porcelain')

# North wall: an inhabited wall section with tall urban rooms split by sky light slots.
for i,(x,y,z,w,h) in enumerate([(-780,1380,2190,300,490),(-220,1610,2190,370,620),(500,1790,2190,440,750)]):
    inhabited_pier('R31 north bank library quarter '+str(i),x,y,z,z+h,w,190,55,i)

# Harbor civic fan: distinct long occupied steps at 1000m; few deep rooms, no copies
# of the upper city's hall type. Steps include 30m-deep public promenades.
for k in range(5):
    zz=1000+k*38;yy=820+k*55
    deck('R31 western stepped inhabited harbour',[(-2040,yy),(-1380+k*32,yy+50),(-1260+k*20,yy+110),(-2080,yy+70)],zz,28,'porcelain')
    for j in range(3):
        xx=-1940+j*210+k*20
        box('R31 west harbour deep occupied chambers',(xx,yy+45,zz+20),(135,58,40),'recess')
# East station / great public void: 420m side cheeks, roof only on northern half.
for side in (-1,1):
    profile('R31 east transfer civic wall '+str(side),[(1370+side*180,2190),(1460+side*180,2190),(1600+side*180,2520),(1530+side*180,2690),(1460+side*180,2640)],1660,210,'ivory')
surface('R31 eastern environmental sail',[
    [(1260,1740,2650),(1510,1740,2790),(1800,1740,2670)],
    [(1370,1920,2710),(1630,1920,2790),(1880,1920,2590)]],18,'porcelain')

group('UNDERSIDE_REAR_URBAN_SECTION')
# The reverse face and undersides are not skins added after the front: cross-sectional
# public courts and deep occupied returns are integral to all three hanging districts.
for i,(x,y,z,w,d) in enumerate([(-1590,920,700,550,310),(-50,1840,1260,560,400),(1590,1910,1710,500,350)]):
    # Two deep lower side wings make a real 150-300m public opening through the underside.
    for side in (-1,1):
        profile('R31 hanging lower inhabited return '+str(i)+str(side),[(x-w*.43,z+200),(x-w*.15,z-80),(x+w*.28,z-20),(x+w*.47,z+230),(x+w*.28,z+300),(x-w*.22,z+300)],y+side*d*.36,d*.25,'porcelain')
        for k in range(4):
            box('R31 underside recessed city galleries',(x+35,y+side*d*.38,z+k*47),(w*.58,d*.32,5),'recess' if k%2 else 'ivory')
    beam('R31 underside great diagonal',(x-w*.32,y-d*.38,z+260),(x+w*.30,y+d*.38,z),24,34,'ivory')
    ribbon('R31 underside public suspended walk '+str(i),catmull([(x-w*.44,y,z+170),(x,y,z+135),(x+w*.48,y,z+220)],8),52,10,'porcelain',True)

group('REPRESENTATIVE_LIVED_THRESHOLDS')
if REV>=3:
    group('EAST_CONFLUENCE_ENVIRONMENT')
    # A folded, occupied climatic nave makes the east interchange a unique
    # skyline/underside figure. Its 650m public rift continues down through the city.
    for side in (-1,1):
        yy=1580+side*340
        profile('R31 east climate nave inhabited fold '+str(side),
                [(750,2440),(980,2430),(1370,2840),(1730,2940),(1870,3190),
                 (1490,3370),(1150,3200),(940,2790)],yy,180,'porcelain')
        for j in range(6):
            x=1000+j*120;z=2580+j*88
            box('R31 east climate nave occupied recesses',(x,yy-side*65,z),(100,110,55),'recess')
            box('R31 east climate nave public balconies',(x,yy-side*80,z-30),(135,140,10),'ivory')
    # Unequal roof segments bridge part of the nave; 200m-wide daylight fissures remain.
    for j,(x,z,w) in enumerate([(1050,2960,160),(1390,3250,210),(1740,3230,180)]):
        surface('R31 east climate nave diagonal crown '+str(j),[
            [(x-w*.5,1190,z-80),(x+w*.5,1190,z)],
            [(x-w*.35,1970,z+40),(x+w*.6,1970,z-40)]],28,'ivory')
    # The low city meets two inhabited footings rather than remaining an empty basin.
    group('GROUND_TRANSFER_PUBLIC_QUARTER')
    for side in (-1,1):
        x=-2050+side*240
        profile('R31 ground station civic bank '+str(side),[(x-90,105),(x+130,105),(x+180,260),(x+70,440),(x-90,370)],430,270,'recess')
        for k in range(4):
            box('R31 ground station public terraces',(x+25,400,105+k*70),(270,330,12),'porcelain')
    ribbon('R31 ground-to-west terminal real street',catmull([(-1350,-800,105),(-1600,-100,105),(-1900,300,105),(-2050,420,105)],10),75,10,'porcelain',True)
    group('REPRESENTATIVE_HUMAN_PORCH')
    # A short, deliberately designed human threshold tests the scale hierarchy.
    # It occupies 95m of the high street; not a whole detailed Gate-B district.
    box('R31_HIGH_PORCH_REAL_FLOOR',(-540,800,2189.5),(190,60,1),'porcelain')
    box('R31 high porch 6m public canopy',(-540,788,2196.5),(190,45,1),'ivory')
    for i in range(9):
        x=-625+i*21
        beam('R31 human porch columns',(x,808,2190),(x+2,808,2196),.4,.6,'bronze')
        box('R31 human public entrance',(x,770,2193),(8,1,6),'recess')
    for x in (-610,-560,-510,-470):
        box('R31 human porch seats',(x,815,2190.45),(3,.8,.9),'bronze')
    people([(-620+i*9,817,2190) for i in range(12)])
    group('REPRESENTATIVE_LIVED_THRESHOLDS')
# New people have 1.8m total height; no colossal scale witnesses.
people([(-630+i*20,840+(i%3-1)*8,2190) for i in range(18)])
people([(90+i*5,-1610+i*12,105) for i in range(14)])
for x,y,z in [(-800,860,2190),(-450,880,2190),(170,930,2190),(780,1100,2190),(-1800,500,1000),(1360,1560,2190)]:
    tree(x,y,z,17)
for i in range(12):
    x=-620+i*22
    box('R31 sky street seat',(x,879,2190.45),(5,1,.9),'bronze')

g.flush()
for o in bpy.context.scene.objects:
    if o.type=='MESH' and str(o.get('study_group','')).startswith('R31_'):
        o['provenance']='R31 authored relative metre research; not formal / not construction'
        bm=bmesh.new();bm.from_mesh(o.data)
        bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
        bm.to_mesh(o.data);bm.free();o.data.update()

sc=bpy.context.scene
if REV>=3:
    g.camera('08_FRONT',(200,-9500,2700),(0,1100,2100),37)
    # Revision-3 free camera looked at a near wall. This is a separate new-room shot,
    # explicitly excluded from fixed-camera geometry improvement claims.
    g.camera('09_EAST_PUBLIC',(1430,1550,2191.7),(1800,2050,2500),23,'R31 east interchange courtyard')
sc['study']='R31-A ASCENDANT CONFLUENCE / 昇界織都'
sc['revision']=REV
sc['source_R30_B_sha256']=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
sc['spatial_principle']='Transport architecture forms occupied city banks and open civic canyons from 105m to 4200m'
sc['formal_art']='UNADOPTED; accepted central art count 0; CITY MASTER incomplete; Minecraft HOLD'
sc['coordinates']='Relative research metres only; no certified canonical anchors'
# Exterior and both human cameras remain byte-for-byte in the same matrices.
bpy.data.objects['04_HUMAN']['support_floor']='B_HUMAN_THRESHOLD_FLOOR'
bpy.data.objects['03_PUBLIC']['support_floor']='R31_1000_REAL_STREET'
bpy.data.objects['07_SKY_STREET']['support_floor']='R31_2190_REAL_STREET'
bpy.context.preferences.filepaths.save_version=0
sc.camera=bpy.data.objects['02_CENTRAL']
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'model/R31_A.blend'),compress=True)
(R/'qa/BUILD.json').write_text(json.dumps({'revision':REV,'removed_R30_objects':removed,'source_R30_B_sha256':sc['source_R30_B_sha256'],'blender':bpy.app.version_string,'boolean_operations':0},ensure_ascii=False,indent=2),encoding='utf8')
print('R31_BUILD_COMPLETE',REV,flush=True)
