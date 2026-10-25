"""Observed macro revisions, executed in live Blender after image review."""
import bpy,sys,json,math
sys.dont_write_bytecode=True
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).parent
sys.path.insert(0,str(ROOT))
import build_r13 as H
import sculpt_c as C

def profile_cut(name,poly,depth,axis='Y',center=0):
    n=len(poly);v=[]
    for d in (center-depth/2,center+depth/2):
        for a,z in poly:v.append((a,d,z) if axis=='Y' else (d,a,z))
    f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    if axis=='Y':f=[tuple(reversed(p)) for p in f]
    return H.mesh(name,v,f,None)

def cut_all(poly,depth,axis='Y',center=0,targets=None):
    for ob in list(H.ARCH.objects):
        if targets and not any(ob.name.startswith(s) for s in targets):continue
        if ob.type!='MESH':continue
        C.carve(ob,profile_cut('temporary_city_carving',poly,depth,axis,center))

def precinct(name,center,w,d,h,orientation=0,kind='COMMON'):
    x,y,z=center
    ob=C.land(name,center,(w/2,d/2),[(0,1,1,0,0),(h*.55,1,.9,0,0),(h,.82,.8,w*.04,d*.04)],
              [(0,0,50,w*.25,d,h*.60,'Y',.1)])
    if orientation:
        for v in ob.data.vertices:
            vx,vy=v.co.x-x,v.co.y-y
            v.co.x=x+math.cos(orientation)*vx-math.sin(orientation)*vy
            v.co.y=y+math.sin(orientation)*vx+math.cos(orientation)*vy
    poly=[(x-w*.35,y-d*.22),(x+w*.3,y-d*.25),(x+w*.3,y+d*.22),(x-w*.3,y+d*.25)]
    H.prism(name+'__living_common_ground',poly,z+48,z+62,H.GREEN if kind=='GROVE' else H.BRONZE,3)

def revision1():
    H.attach_existing()
    before={o.name:len(o.data.vertices) for o in H.ARCH.objects if o.type=='MESH'}
    cut_all([(-2220,980),(-960,980),(-720,1590),(-970,2300),(-1050,3280),(-1500,3660),(-1980,3100),(-2100,2200)],4300,
            targets=['C01_'])
    cut_all([(830,720),(2190,720),(2240,1460),(1790,2460),(1230,3030),(760,2680),(860,1780)],4300,
            targets=['C02_'])
    cut_all([(-200,1170),(1350,1170),(1670,1620),(1510,2080),(420,2290),(-140,1910)],6500,axis='X',
            targets=['C01_','C02_','C03_'])
    for o in list(H.ARCH.objects):
        if o.name.startswith(('C05_','C06_')):bpy.data.objects.remove(o,do_unlink=True)
    for row in [
        ('R1_W01',(-2180,-180,970),700,900,540,.05,'GROVE'),
        ('R1_W02',(-1840,680,1520),800,680,470,-.14,'COMMON'),
        ('R1_W03',(-1440,520,2340),670,800,520,.12,'GROVE'),
        ('R1_W04',(-1650,700,3010),560,700,490,-.2,'COMMON'),
        ('R1_E01',(1980,180,730),780,950,540,-.2,'COMMON'),
        ('R1_E02',(1520,900,1420),850,900,600,.18,'GROVE'),
        ('R1_E03',(1150,580,2230),700,830,540,-.12,'COMMON'),
        ('R1_N01',(-400,1720,1240),940,700,580,.1,'COMMON'),
        ('R1_S01',(-1450,-1070,80),1000,920,710,.2,'GROVE'),
        ('R1_S02',(1540,-940,90),1000,900,600,-.3,'COMMON')]:precinct(*row)
    C.land('R1_INNER_COAST',(-380,-520,100),(800,750),
         [(0,1,.8,0,0),(270,.9,.8,0,0),(630,.45,.7,-170,100)],
         [(0,0,60,300,1200,320,'Y',0)])
    data=dict(revision=1,reason='A/B rejected. C had thick land but isolated chambers and blank sides.',
              main_edits=['merged western cavities into 2680m tall open canyon',
                          'merged eastern courts into a separate inclined 2300m world',
                          'cut transverse public connection through three principal lands',
                          'replaced blank foreground lands by inhabited 300-1000m precincts'],
              before_vertices=before,after_meshes=len(H.ARCH.objects))
    (ROOT/'qa').mkdir(exist_ok=True);(ROOT/'qa'/'revision_1.json').write_text(json.dumps(data,indent=2),encoding='utf8')
    H.save(ROOT/'revision_1','R13_C_R1')

def revision2():
    H.attach_existing()
    repairs=[]
    for o in H.ARCH.objects:
        if o.type=='MESH' and o.data.validate(verbose=False):repairs.append(o.name)
    cut_all([(-920,3290),(580,3290),(730,4050),(350,5100),(-650,5100),(-1080,4100)],1900,
            center=720,targets=['C04_','C03_'])
    cut_all([(-1120,600),(920,600),(1100,1550),(690,2810),(-60,3620),(-920,3170),(-1280,1900)],2500,
            center=2050,targets=['C03_'])
    cut_all([(-230,1220),(1690,1220),(1870,1820),(1440,2880),(690,3370),(-40,2780)],1400,axis='X',
            center=2050,targets=['C02_'])
    for row in [
        ('R2_N_LOWER',(-900,2140,620),800,850,620,-.1,'GROVE'),
        ('R2_N_EAST',(600,2190,1170),920,800,650,.18,'COMMON'),
        ('R2_N_HIGH',(-500,2050,2360),830,820,630,-.24,'GROVE'),
        ('R2_ZENITH',(-520,1020,3800),850,760,530,.22,'COMMON'),
        ('R2_SIDE_INNER',(1740,1160,1830),820,940,650,-.4,'GROVE')]:precinct(*row)
    C.land('R2_INTERWORLD_COMMON',(50,650,2500),(900,800),
        [(0,.75,1,0,0),(350,1,1,0,0),(800,.7,.8,-90,40)],
        [(0,0,110,480,1300,450,'Y',-.1),(0,0,220,330,1400,380,'X',0)])
    # District-scale incisions open the thick residual side lands to light.
    for name,center,rx,depth,h,axis in [
        ('west outer hanging court',(-2370,100,1810),220,950,650,'X'),
        ('west high light court',(-1430,450,3700),300,1300,580,'Y'),
        ('east open underside',(2140,450,370),270,1100,530,'X'),
        ('east high civic fold',(1060,720,2910),240,1300,500,'Y'),
        ('rear reverse court',(-520,1910,3200),290,1400,620,'Y')]:
        target='C01_' if name.startswith('west') else ('C02_' if name.startswith('east') else 'C03_')
        ob=next(o for o in H.ARCH.objects if o.name.startswith(target))
        C.carve(ob,C.portal('temporary_deep_court',center,rx,depth,h,axis,0))
    # The zenith has an actual open light well within its habitable depth.
    for prefix,loc,size in [('R2_ZENITH',(-520,1040,4280),(300,280,900)),
                            ('R1_E02',(1520,900,1940),(300,260,900)),
                            ('R1_W03',(-1440,520,2810),(240,300,900))]:
        ob=next(o for o in H.ARCH.objects if o.name.startswith(prefix+'__inhabited'))
        C.carve(ob,H.box('temporary_actual_lightwell',loc,size,None))
    internal_grounds()
    H.beam('West deep inclined transfer',(-1800,650,1600),(-1320,500,2360),65,75,H.STONE)
    H.beam('East deep inclined transfer',(1740,950,1460),(1150,580,2300),65,75,H.STONE)
    H.beam('Interworld transfer',(-1050,760,2810),(-570,700,2780),105,65,H.BRONZE)
    human_place()
    data=dict(revision=2,reason='R1 had a blank roof/rear and a weak side. These masses are re-excavated.',
              main_edits=['vertical 1.5km zenith incision changes silhouette and sky connection',
                          'rear 3km cavern replaces closed outer land',
                          'east 2km side mouth exposes district-depth interior',
                          'central 800m thick hollow common divides upper and lower civic skies'],
              mesh_validation_repairs=repairs,
              human_view='1.7m above saved internal floor; not proof of route completeness')
    (ROOT/'qa'/'revision_2.json').write_text(json.dumps(data,indent=2),encoding='utf8')
    H.save(ROOT/'revision_2','R13_C_R2')

def internal_grounds():
    # Nonuniform 100-500m public urban landforms in the *depth* of the districts.
    for name,x,y,z,w,d,angle in [
        ('W living inlet',-1850,450,1595,420,380,.18),
        ('W upper common',-1450,350,2390,370,460,-.2),
        ('E cultivation exchange',1530,650,1470,450,500,.22),
        ('N reverse cultivation',-500,2080,2410,430,400,-.15),
        ('Zenith common',-520,1020,3850,440,390,.3)]:
        # Two unequal thick traversable contours enclose a sunken internal civic space.
        for i,(offx,offy,sx,sy,h) in enumerate([(-.26,-.12,.38,.75,85),(.2,.23,.60,.35,135)]):
            poly=[(x+(offx+a*sx)*w,y+(offy+b*sy)*d) for a,b in C.PLAN]
            H.prism(name+f' precinct contour {i}',poly,z,z+h,H.STONE if i==0 else H.PEARL,3)
        H.prism(name+' lower interior ground',[(x-w*.4,y-d*.3),(x+w*.4,y-d*.3),(x+w*.35,y+d*.4),(x-w*.4,y+d*.3)],z-15,z,H.BRONZE,3)
        # Two deep recesses and a 100m urban passage, each real hollow volume.
        for j,dx in enumerate((-.31,.23)):
            H.box(name+' enclosing common wall '+str(j),(x+dx*w,y+d*.28,z+55),(w*.18,d*.48,110),H.PEARL,3)
        H.box(name+' passage lintel',(x,y+d*.28,z+120),(w*.55,d*.48,35),H.PEARL,3)

def human_place():
    H.prism('Human common floor',[(-2020,-250),(-1770,-250),(-1740,110),(-1990,140)],1590,1600,H.BRONZE,1)
    for i,(x,y) in enumerate([(-2012,-120),(-2000,-65),(-1990,0)]):
        H.box('Human inhabited threshold pier '+str(i),(x,y,1603),(3,3,6),H.PEARL,.2)
        H.box('Human inhabited threshold head '+str(i),(x+8,y,1605.7),(19,3,1.0),H.PEARL,.2)
        H.box('Human recessed common room '+str(i),(x+15,y+9,1602.7),(8,12,5.4),H.STONE,.3)
    for y in range(-140,81,20):
        H.box('Human edge post',(-1756,y,1600.55),(.14,.14,1.1),H.STONE)
    H.box('Human continuous edge rail',(-1756,-30,1601.1),(.15,220,.13),H.STONE)
    for x,y in [(-1975,-95),(-1950,10),(-1820,70)]:
        H.box('Common growing bed',(x,y,1600.35),(12,4,.7),H.GREEN,.15)
    for i in range(2):
        x,y=-1946+i*6,-70+i*30
        H.box('1.75m figure torso '+str(i),(x,y,1601.15),(.44,.24,.7),H.BRONZE,.08)
        H.box('1.75m figure head '+str(i),(x,y,1601.625),(.23,.23,.25),H.PEARL,.08)
        for dx in (-.12,.12):H.box('Figure leg',(x+dx,y,1600.4),(.13,.14,.8),H.STONE,.03)
    H.box('Actual public threshold light',(-1990,-64,1604.9),(16,.3,.2),H.LIGHT)

if __name__=='__main__':
    stage=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else globals().get('STAGE','1')
    (revision1 if stage=='1' else revision2)()
