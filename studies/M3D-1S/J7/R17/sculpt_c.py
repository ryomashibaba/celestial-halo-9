"""Third direction: an authored polycentric civic massif, not repeated A/B modules.
Run background Blender --python sculpt_c.py -- [views].
"""
import sys, math, json
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import atelier as a
import bpy
from mathutils import Vector
a.setup();a.cameras()
R=a.ROOT/'exploration_C';R.mkdir(exist_ok=True)
districts=[]
def body(n,stations,voids):
 o=a.loft(n,stations,a.P,32)
 for j,(c,d) in enumerate(voids):a.cut(o,n+'_real_civic_valley_'+str(j),c,d)
 return o
# These are inhabited city bodies: massive upper/lower public grounds and deep
# courtyard volumes are modelled with the body, before any exterior finishing.
# Three non-bilateral rising masses meet across a twisting interior shared sky.
body('C_WEST_RISING_CONTINENT',[
 (-1750,0,0,1050,1220),(-1850,50,550,1040,1200),(-1750,140,1350,850,1080),
 (-1400,350,2250,710,940),(-1000,600,3050,680,830),(-200,760,3750,720,630),
 (100,780,4150,440,460)], [
 ((-1550,-160,610),(1750,1850,420)),
 ((-1360,150,1480),(1470,1600,470)),
 ((-1000,360,2350),(1400,1400,420)),
 ((-500,650,3220),(1450,1150,410)),
 ((150,780,3950),(710,570,190)),
 # long vertical light fissures expose district edges rather than window decals.
 ((-2050,0,1500),(180,2700,550)),
 ((-1480,700,2850),(190,2400,480))])
body('C_EAST_INLAND',[
 (1450,300,0,1340,1250),(1620,300,460,1330,1230),(1580,500,1050,1150,1100),
 (1180,850,1750,850,1060),(1000,1050,2350,610,900),(740,1200,2900,420,690)], [
 ((1400,-50,490),(1900,1900,390)),
 ((1280,250,1200),(1800,1800,450)),
 ((1000,650,1950),(1300,1850,400)),
 ((700,1100,2600),(1100,1000,320)),
 ((2100,750,1200),(160,2500,500))])
body('C_REAR_HANGING_CIVILIZATION',[
 (200,1500,650,900,620),(50,1710,1250,1050,710),(200,1810,2000,1170,760),
 (300,1630,2750,1300,780),(100,1270,3300,1170,710),(-100,1000,3700,870,500)], [
 ((100,1500,1350),(1600,1500,460)),
 ((100,1550,2150),(1900,1500,440)),
 ((150,1300,2950),(1800,1300,360)),
 ((-300,2100,2450),(310,1800,600))])
# A broad connected low continent, asymmetric broken shoreline instead of a plinth.
a.prism('C_LOWEST_URBAN_DELTA',[(-2850,-1150),(-1800,-1700),(-750,-1500),(300,-1100),(1600,-1450),(2860,-600),(2350,700),(1100,1000),(300,500),(-1000,800),(-2600,400)],-30,120,a.D)
a.prism('C_SHARED_INNER_SEA',[(-1100,-900),(-300,-1100),(600,-600),(750,400),(200,1100),(-500,750)],122,126,a.W)
# Individual large interior districts occupy the real cut volumes; different plans,
# open-ended streets and sectional buildings, not uniform little house scatter.
def district(n,c,w,d,z,kind):
 x,y=c;districts.append(dict(name=n,center_m=[x,y,z],span_plan_m=[w,d],type=kind))
 # two broad articulated grounds; overlap into the continental cut-floor.
 poly=[(x-w*.5,y-d*.40),(x+w*.35,y-d*.5),(x+w*.5,y-d*.20),(x+w*.40,y+d*.45),(x-w*.42,y+d*.5)]
 a.prism(n+'_public_ground',poly,z-24,z,a.F)
 if kind=='canal':
  a.ribbon(n+'_inland_water',[(x-w*.34,y-d*.30,z+1),(x,y,z+1),(x+w*.29,y+d*.30,z+1)],95,2,a.W)
  offsets=[(-.29,-.21,.20,.38,155),(.28,.18,.20,.38,195),(-.27,.28,.22,.28,120)]
 elif kind=='terraced':
  offsets=[(-.30,-.26,.24,.34,170),(-.28,.19,.22,.31,240),(.23,-.22,.29,.37,140),(.30,.25,.25,.31,200)]
 else:
  offsets=[(-.29,-.28,.23,.30,130),(.27,-.27,.25,.32,195),(-.29,.25,.22,.35,210),(.26,.25,.26,.34,140)]
 for i,(u,v,ww,dd,h) in enumerate(offsets):
  xx=x+u*w;yy=y+v*d;rw=ww*w;rd=dd*d
  ob=a.loft(n+f'_urban_chamber_{i}',[(xx,yy,z,rw*.5,rd*.5),(xx+rw*.07,yy,z+h*.7,rw*.49,rd*.46),(xx+rw*.10,yy,z+h,rw*.40,rd*.4)],a.D,12)
  a.cut(ob,n+'_public_crossing',(xx,yy,z+h*.40),(rw+40,rd*.31,h*.42))
  # structural ceramic cheeks and folded crowns are the buildings themselves.
  for side in (-1,1):
   a.loft(n+'_inhabited_vertical_cheek',[(xx+side*rw*.46,yy,z,16,rd*.48),(xx+side*rw*.43,yy,z+h*.72,18,rd*.45),(xx+side*rw*.35,yy,z+h,12,rd*.39)],a.P,8)
  a.box(n+'_roof_garden',(xx+rw*.1,yy,z+h+2),(rw*.75,rd*.70,4),a.F)
  for k in range(1,int(h/17)):
   a.box(n+'_floor_street',(xx+rw*.03,yy-rd*.48,z+k*17),(rw*.86,10,2),a.P)
  a.box(n+'_interior_warm_lantern',(xx,yy-rd*.33,z+20),(rw*.66,2,7),a.L)
 # landing platforms and public viewing edge
 a.ribbon(n+'_city_axis',[(x-w*.38,y-d*.4,z+3),(x,y,z+3),(x+w*.35,y+d*.38,z+3)],48,6,a.P)
for args in [
 ('C_W0_ESTUARY',(-1720,-310),1500,1220,400,'canal'),
 ('C_W1_RISING_GARDENS',(-1410,50),1200,1130,1245,'terraced'),
 ('C_W2_UPPER_CONCOURSE',(-1080,350),1060,1060,2140,'forum'),
 ('C_W3_ZENITH_QUARTER',(-360,650),1100,900,3015,'terraced'),
 ('C_E0_TIDAL_WORLD',(1490,-10),1460,1220,295,'canal'),
 ('C_E1_SPLIT_CITY',(1330,300),1300,1250,975,'forum'),
 ('C_E2_HANGING_GARDEN',(1030,750),1050,1150,1750,'terraced'),
 ('C_R0_INNER_ORCHARD',(0,1580),1350,1050,1120,'terraced'),
 ('C_R1_DEEP_METROPOLIS',(50,1750),1590,1080,1930,'canal'),
 ('C_R2_SHARED_SKY',(140,1450),1480,900,2770,'forum')]:district(*args)
# A few immense public grounds intersect the civic sky in depth, not a lintel.
for n,pts,w in [
 ('C_LOW_CONFLUENCE',[(-1900,-580,400),(-700,-450,380),(150,-50,295),(1450,100,295)],190),
 ('C_MID_TRANSIT',[(-1450,450,1245),(-600,700,1250),(0,1500,1120),(1100,1700,1000)],155),
 ('C_HIGH_PROMENADE',[(-1040,500,2140),(-400,1000,2130),(200,1780,1930),(1100,1150,1750)],180)]:
 a.ribbon(n,pts,w,45,a.D);a.ribbon(n+'_public_surface',[(x,y,z+3) for x,y,z in pts],w-16,3,a.F)
a.tube('C_PRIMARY_ASCENSION',[(-2100,-850,120),(-1780,-720,500),(-1350,-500,1250),(-1050,-150,2140),(-350,350,3030),(200,850,3950)],22,a.B)
a.tube('C_SECONDARY_ASCENSION',[(2200,-700,120),(1850,-400,400),(1550,0,980),(1200,550,1750),(650,1150,2600),(200,1500,3000)],20,a.B)
a.export(R,'R17_C')
(R/'DISTRICTS.json').write_text(json.dumps(districts,indent=2),encoding='utf8')
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
a.render(R,args or ['01_FRONT','02_OBLIQUE','03_SIDE','04_REAR','05_AERIAL','06_UNDERSIDE','07_GROUND_UP'])
