"""Third sculptural/spatial pass, informed by saved v2 render inspection.
Distinct room design replaces the generic inserted districts in the preferred B.
"""
import bpy,sys,math
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
from geometry import box,beam,path,solid,surface,deck,ribbon,tree,people,catmull
V=sys.argv[sys.argv.index('--')+1]
bpy.ops.wm.open_mainfile(filepath=str(g.R/f'model/R30_{V}.blend'));g.materials()

def erase_prefixes(prefixes):
    for o in list(bpy.context.scene.objects):
        if o.type=='MESH' and any(o.name.startswith(n) for n in prefixes):
            g.CHANGES.append({'removed':o.name,'vertices':len(o.data.vertices)});g.remove(o)

def repose(name,pos,target,lens=None,floor=None):
    o=bpy.data.objects[name];o.location=pos;o.rotation_euler=(Vector(target)-Vector(pos)).to_track_quat('-Z','Y').to_euler();o['target_m']=list(target)
    if lens:o.data.lens=lens
    if floor:o['support_floor']=floor

if V=='A':
    g.GROUP='A_REV3_OPEN_NORTH_CIVIL_PASSAGE'
    g.cut_portal('A actual north ground-to-sky civil gate',[(-520,104),(520,104),(650,740),(340,1690),(-100,1820),(-510,1180)],'Y',-1700,3500,['A north spine','A split crown counterleaf'])
    ribbon('A north-facing ground street',catmull([(-200,-750,105),(-130,50,105),(60,950,105),(80,1940,105),(170,2740,105)],10),92,8,'porcelain',True)
    # Genuine side rooms along the otherwise blank lower central cliff.
    deck('A north public chamber floor',[(-450,960),(500,960),(560,2340),(-420,2340)],105,12,'ground')
    for j in range(5):
        yy=1050+j*250
        for side in (-1,1):
            xx=side*(320+j*9)
            beam('A north public chamber colossal piers',(xx,yy,105),(xx*.8,yy+80,650+j*70),14,24,'ivory')
            box('A north chamber occupied side rooms',(xx+side*90,yy+80,195+j*30),(120,190,180+j*60),'recess')
            box('A north public portico roof',(xx,yy+60,240+j*34),(180,210,7),'porcelain')
    people([(-100,1000+i*80,105) for i in range(15)])
    repose('03_PUBLIC',(-200,-710,106.7),(80,2100,650),25,'A_REAL_LOW_FLOOR')
    g.CHANGES.append({'visual_reason':'Common human view hit a blind north wall; cut a true 1.6km-high central civic passage and extend real ground street through it. Camera03 retargeted separately; 04 held fixed.'})
else:
    g.GROUP='B_REV3_DISTINCT_PUBLIC_WORLDS'
    erase_prefixes(['B western metropolitan gorge','B western sky address','B horizon inner city','B horizon convergence house','B horizon public neighbourhood','B landward civil confluence'])
    # WEST 1000: an inhabited amphitheatre cut into a high harbour, not a boxed hall.
    # The central walking route is kept open toward the remote hanging city.
    ribbon('B_WEST_AXIS_REAL_FLOOR',catmull([(-2200,310,1000),(-1900,380,1000),(-1530,470,1000),(-1150,600,1000),(-900,670,980)],12),110,12,'porcelain',True)
    for k in range(7):
        yy=730+k*38;zz=1000+k*20
        deck('B western amphitheatre inhabited ground',[(-2120,yy),(-1350,yy),(-1250,yy+32),(-2180,yy+32)],zz,10,'porcelain')
        # Discrete room backs leave open lateral public circulation.
        for i in range(4):
            xx=-2030+i*180+k*12
            box('B western amphitheatre chamber backs',(xx,yy+22,zz+22),(110,16,44),'recess')
            box('B western amphitheatre chamber roofs',(xx,yy+5,zz+45),(130,70,4),'ivory')
    # High curved canopy shares the geometry of the upper shore of the cave.
    rows=[]
    for i in range(33):
        t=i/32;x=-2220+1100*t
        rows.append([(x,60,1160+230*math.sin(math.pi*t)),(x,250,1280+230*math.sin(math.pi*t)),(x,430,1320+230*math.sin(math.pi*t))])
    surface('B winter harbour curved upper street',rows,18,'ivory')
    for j in range(7):
        x=-2160+j*150
        path('B winter harbour branching supports',[(x,30,1000),(x+25,50,1120),(x+70,190,1320+160*math.sin(j*math.pi/6))],9,15,'bronze')
    # 2190: an axial city room with two unequal occupied banks, open public frontages,
    # a diagonal roof, and a distinct rising destination 1.7km away.
    deck('B_HORIZON_AXIS_REAL_FLOOR',[(-760,620),(1050,620),(1050,1040),(-760,1040)],2190,14,'porcelain')
    for i,(x,yy,h,depth) in enumerate([(-590,1210,170,200),(-260,1350,280,280),(140,1440,360,300),(560,1410,250,250),(930,1300,340,200)]):
        # A full three-sided public room opening onto a city street; no front wall.
        box('B northern city-room rear walls',(x,yy+depth/2,2190+h/2),(230,9,h),'recess')
        for side in (-1,1):
            box('B northern city-room party walls',(x+side*115,yy,2190+h/2),(9,depth,h),'recess')
            for z in (2235,2290,2360):
                if z+20<2190+h:box('B northern city-room side gallery',(x+side*90,yy,z),(48,depth,3),'porcelain')
        # Roofs are distinct folds, anchored to variable public-room heights.
        surface('B unequal north civic roofs',[[(x-135,yy-depth*.6,2190+h),(x,yy-depth*.6,2190+h+60),(x+135,yy-depth*.6,2190+h-25)],[(x-135,yy+depth*.6,2190+h-30),(x,yy+depth*.6,2190+h+20),(x+135,yy+depth*.6,2190+h-45)]],8,'ivory')
        for xx in (x-104,x+104):beam('B civic front porch supports',(xx,yy-depth*.6,2190),(xx+20,yy-depth*.6,2190+h),5,9,'bronze')
        deck('B north public chamber real floors',[(x-115,yy-depth/2),(x+115,yy-depth/2),(x+115,yy+depth/2),(x-115,yy+depth/2)],2190,5,'ground')
    # South bank is one stepped, occupied landscape rather than the same rooms.
    for i in range(6):
        x=-620+i*260;h=[115,170,220,300,240,130][i]
        # Off-axis split volumes open a sequence of 80m-deep public courts.
        for s in (-1,1):
            solid('B southern inhabited buttress court '+str(i)+' '+str(s),[
                [(x-100,200+s*65,2190),(x+105,200+s*65,2190),(x+105,200+s*65+s*120,2190),(x-100,200+s*65+s*120,2190)],
                [(x-60,230+s*50,2190+h),(x+80,230+s*50,2190+h),(x+80,230+s*50+s*90,2190+h),(x-60,230+s*50+s*90,2190+h)]],'recess')
        for k in range(3):
            zz=2190+(k+1)*h/3
            deck('B southern hanging garden terrace',[(x-110,35),(x+120,35),(x+120,400),(x-110,400)],zz,5,'porcelain')
        tree(x,360,2190+h,25)
    # 500m-wide inhabited public canopy; two differently lit slits, with no repeating nave.
    rows=[]
    for i in range(29):
        x=-580+1400*i/28
        rows.append([(x,440,2490+110*math.sin(i*math.pi/28)),(x,660,2580+170*math.sin(i*math.pi/28)),(x,750,2600+180*math.sin(i*math.pi/28))])
    surface('B upper city diagonal public vault',rows,16,'ivory')
    for i in (1,6,12,19,26):
        x=-580+1400*i/28
        path('B upper city colossal branching portal',[(x,450,2190),(x+50,470,2430),(x+80,660,2580+170*math.sin(i*math.pi/28))],10,18,'bronze')
    # Genuine path to the framed eastern city; the distant upper terminus remains
    # unfinished but exists in the same scene and is not a background composite.
    ribbon('B horizon-to-highland public transit',catmull([(920,840,2190),(1180,1060,2370),(1360,1290,2680),(1480,1560,3020)],14),70,14,'ivory',True)
    # Low harbour: a unique double-curved departure roof, framed directly from the floor.
    rows=[]
    for i in range(25):
        t=i/24;x=-1450+650*t
        rows.append([(x,-250,150+160*math.sin(math.pi*t)),(x,0,250+260*math.sin(math.pi*t)),(x,220,160+200*math.sin(math.pi*t))])
    surface('B ground tidal departure shell',rows,20,'porcelain')
    for j in (1,4,8,12,16,20,23):
        x=-1450+650*j/24
        path('B ground departure frames',[(x,-250,105),(x,-220,220+100*math.sin(j*math.pi/24)),(x,0,250+260*math.sin(j*math.pi/24)),(x,200,190),(x,220,105)],10,16,'bronze')
    deck('B_DEPARTURE_REAL_FLOOR',[(-1490,-290),(-760,-290),(-760,260),(-1490,260)],105,14,'ground')
    people([(-2110+i*40,350+i*8,1000) for i in range(16)]+[(-620+i*50,850,2190) for i in range(22)])
    for x,y,z in [(-2120,570,1000),(-1700,680,1000),(-500,1060,2190),(120,1090,2190),(700,1080,2190)]:tree(x,y,z,25)
    repose('03_PUBLIC',(-2120,320,1001.7),(100,1100,1300),26,'B_WEST_AXIS_REAL_FLOOR')
    repose('07_SKY_STREET',(-650,840,2191.7),(1000,900,2460),26,'B_HORIZON_AXIS_REAL_FLOOR')
    bpy.data.objects['04_HUMAN']['support_floor']='B_HUMAN_THRESHOLD_FLOOR'
    g.CHANGES.append({'visual_reason':'Replaced repeated inserted buildings in west1000 and horizon2190 by different amphitheatre and axial city-room architectures. New actual room fronts, galleries, sky-vault and rising destination. Matched low human04 and exterior02 unchanged.'})
g.flush()
# Shared rear lens correction reveals the entire mass. Not credited as a shape change.
bpy.data.objects['05_REAR'].data.lens=32
g.CHANGES.append({'camera_only':'03 framing and B07 corrected after obstruction; 05 lens40->32 for both to reveal full silhouette. 01/02/04/06 remain identical across A/B.'})
g.save(V,3)
