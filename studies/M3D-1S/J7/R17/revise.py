"""Explicit native main-mass revisions AFTER observing saved predecessor images."""
import bpy,bmesh,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import atelier as a
args=sys.argv[sys.argv.index('--')+1:];rev=int(args[0]);R=a.ROOT
source=R/('exploration_C/R17_C.blend' if rev==1 else 'revision_1/R17_REVISION_1.blend')
bpy.ops.wm.open_mainfile(filepath=str(source));a.S=bpy.context.scene;a.ARCH=bpy.data.collections['R17_URBAN_CONTINENTS'];a.ENV=bpy.data.collections['STUDIO_NONCANONICAL']
for attr,name in [('P','Porcelain titanium'),('D','Midnight occupied substructure'),('G','Deep blue glazed inhabited faces'),('B','Pale champagne edges'),('F','Warm civic mineral'),('W','Quiet jade water'),('L','Warm interior light'),('V','Garden canopy')]:setattr(a,attr,bpy.data.materials.get(name) or bpy.data.materials['Porcelain titanium'])
removed=[];edits=[]
def remove(name):
 ob=bpy.data.objects.get(name)
 if ob:removed.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
def inhabited_ridge(n,stations,openings):
 ob=a.loft(n,stations,a.P,24)
 # public chambers are fully subtracted through depth, each different in size.
 for c,d in openings:a.cut(ob,n+'_open_metropolitan_chamber',c,d)
 return ob
if rev==1:
 # OBSERVED C: a blank curved boulder dominates. Replace its primary mass,
 # keep actual district cores. These are district-scale occupied buttresses,
 # grouped asymmetrically in depth, not an outer decorative cage.
 remove('C_WEST_RISING_CONTINENT');remove('C_REAR_HANGING_CIVILIZATION')
 specs=[
 ('R1_WEST_OCEAN_RIDGE',[(-2450,-150,0,340,920),(-2430,-100,900,330,890),(-2050,100,1900,300,800),(-1700,450,2900,290,700),(-1100,700,3850,290,540),(-820,760,4440,180,310)],
 [((-2300,-100,620),(670,2000,330)),((-1960,100,1570),(640,1800,380)),((-1610,420,2450),(570,1500,400)),((-1130,700,3420),(560,1200,310))]),
 ('R1_WEST_INNER_RIDGE',[(-1000,220,100,270,880),(-1120,180,820,240,850),(-1040,280,1750,230,750),(-800,500,2700,240,650),(-350,700,3680,230,460),(-130,760,4130,150,310)],
 [((-1070,180,620),(490,1900,310)),((-1040,280,1480),(470,1600,400)),((-820,500,2350),(480,1400,420)),((-360,700,3220),(450,1100,310))]),
 ('R1_REAR_WEST_RIDGE',[(-680,2140,600,350,380),(-900,2140,1450,330,370),(-850,2030,2300,350,380),(-600,1620,3100,370,440),(-240,1130,3730,320,400)],
 [((-870,2140,1350),(740,800,400)),((-820,2030,2140),(760,800,400)),((-510,1600,2950),(800,900,330))]),
 ('R1_REAR_EAST_RIDGE',[(950,2000,500,470,430),(1140,2100,1350,490,470),(1280,1950,2150,420,480),(1000,1600,2820,400,510),(500,1230,3300,330,430)],
 [((1100,2050,1200),(1000,1000,400)),((1240,1900,1970),(900,1050,420)),((1000,1600,2650),(850,1100,330))])]
 for n,st,op in specs:inhabited_ridge(n,st,op)
 # Broad city-ground extensions stitch the newly opened sides into districts.
 for n,x,y,z,w,d in [('ESTUARY',-1700,-200,400,1900,1280),('RISING',-1450,180,1245,1450,1130),('UPPER',-1070,430,2140,1250,1150),('ZENITH',-400,700,3015,1200,920),('REAR_LOWER',120,1750,1120,1830,1150),('REAR_MID',120,1720,1930,2000,1150),('REAR_HIGH',180,1450,2770,1750,1050)]:
  poly=[(x-w*.5,y-d*.4),(x+w*.44,y-d*.48),(x+w*.5,y+d*.1),(x+w*.35,y+d*.48),(x-w*.45,y+d*.45)]
  a.prism('R1_'+n+'_thick_inhabited_ground',poly,z-95,z-25,a.D)
 # A formerly smooth rear wall becomes actual multi-height deep urban squares.
 for x,y,z,rx,ry in [(-100,1860,1450,780,470),(140,1900,2240,900,480),(50,1500,3080,850,430)]:
  ob=a.loft('R1_REAR_CIVIC_OVERWORLD',[(x,y,z,rx,ry),(x+100,y,z+180,rx*.9,ry*.9)],a.P,20)
  a.cut(ob,'R1_REAR_OPEN_SKY_SQUARE',(x,y,z+120),(rx*.95,ry*2.2,200))
 edits=['Removed original broad west and rear monoliths; rebuilt four staggered inhabited ridges with actual city chambers.', 'Extended seven district grounds to inhabit the opened side/rear, moved highest occupied skyline to an asymmetric 4440m ridge.']
else:
 # OBSERVED R1: tall forked ribs still dominate; east is a closed round flank.
 # Rebuild east as an oblique integrated inland city with two huge diagonal
 # ravines, connect deep city into front void; change low silhouette and crown.
 remove('C_EAST_INLAND')
 ob=inhabited_ridge('R2_EAST_INLAND_CIVILIZATION',[
  (1770,250,0,1090,1110),(1800,330,550,1050,1110),(1500,600,1250,890,1100),(1060,1050,1950,750,950),(670,1460,2670,600,700),(470,1570,3150,380,480)],
  [((1750,200,510),(1850,2100,380)),((1360,550,1230),(1700,2000,410)),((900,1100,1980),(1470,1900,390)),((500,1470,2760),(1050,1500,350))])
 # vertical ravines open the outside towards specific inner worlds.
 a.cut(ob,'R2_EAST_SOUTH_RAVINE',(2200,-350,1560),(360,1400,1240))
 a.cut(ob,'R2_EAST_REAR_RAVINE',(1650,1450,2180),(420,1500,1000))
 # New central inhabited peninsula changes silhouette AND the shape/depth
 # of the main void: foreground low sky / deep upper chamber are no longer one hole.
 new=a.loft('R2_INNER_METROPOLITAN_PENINSULA',[
  (-80,-870,110,510,690),(80,-650,580,510,680),(100,-220,1150,450,620),(-80,150,1660,360,530),(-360,550,2080,320,450)],a.D,22)
 a.cut(new,'R2_LOWER_SHARED_CITY_CUT',(0,-450,460),(950,1600,360))
 a.cut(new,'R2_MID_SHARED_CITY_CUT',(0,20,1320),(850,1450,390))
 for side in (-1,1):
  a.loft('R2_PENINSULA_INHABITED_CHEEK',[(side*470,-700,180,65,520),(100+side*400,-250,1150,65,480),(-150+side*285,300,1780,50,330)],a.P,12)
 for z,x,y,w,d in [(280,10,-650,860,890),(1125,20,-100,790,800),(1620,-120,200,640,680)]:
  a.prism('R2_PENINSULA_PUBLIC_WORLD',[(x-w/2,y-d/2),(x+w/2,y-d*.4),(x+w*.42,y+d*.4),(x-w*.4,y+d/2)],z-28,z,a.F)
  for side in (-1,1):
   a.loft('R2_VERTICAL_PUBLIC_QUARTER',[(x+side*w*.32,y,z,w*.12,d*.29),(x+side*w*.28,y,z+140,w*.12,d*.26)],a.P,12)
  a.ribbon('R2_PENINSULA_GARDEN',[(x,y-d*.35,z+2),(x+w*.03,y+d*.32,z+2)],50,3,a.W)
 # Recompose the highest city as actual split, thick high-altitude grounds.
 for name in ['R1_WEST_OCEAN_RIDGE','R1_WEST_INNER_RIDGE']:
  o=bpy.data.objects[name]
  # The observed long, uninhabited tips are removed, not ornamented.
  a.cut(o,'R2_REMOVE_BLANK_UPPER_TIPS',(-550,800,4300),(3000,4000,1400))
 a.prism('R2_ZENITH_METROPOLITAN_GROUND',[(-1450,180),(-400,100),(100,450),(-40,1320),(-1250,1460),(-1590,750)],3540,3690,a.D)
 top=a.loft('R2_ZENITH_WEST_LIVED_CITY',[(-1330,770,3690,170,550),(-1260,790,4120,170,500),(-1050,830,4440,135,360)],a.P,20)
 a.cut(top,'R2_ZENITH_WEST_PUBLIC_ROOM',(-1250,760,3940),(450,850,250))
 top=a.loft('R2_ZENITH_EAST_LIVED_CITY',[(-140,650,3690,200,470),(-220,780,4000,190,430),(-380,870,4250,150,340)],a.P,20)
 a.cut(top,'R2_ZENITH_EAST_PUBLIC_ROOM',(-180,720,3900),(470,740,220))
 top=a.loft('R2_ZENITH_REAR_CIVILIZATION',[(-710,1260,3690,490,190),(-660,1210,4040,460,200),(-630,1130,4300,380,170)],a.P,20)
 a.cut(top,'R2_ZENITH_REAR_PUBLIC_ROOM',(-730,1230,3930),(580,550,260))
 a.prism('R2_ZENITH_PUBLIC_VALLEY',[(-1130,270),(-430,270),(-380,1100),(-1020,1220)],3690,3696,a.F)
 a.ribbon('R2_ZENITH_WATER_SKY',[(-930,360,3698),(-780,700,3698),(-650,1040,3698)],90,2,a.W)
 a.ribbon('R2_ZENITH_ARRIVAL_CONTINENT',[(-1200,650,3860),(-850,730,3880),(-350,850,3920),(50,1050,3910)],300,110,a.D)
 for i,(x,y,z) in enumerate([(-1100,650,3860),(-700,740,3890),(-290,890,3920)]):
  a.loft('R2_ZENITH_LIVING_WORLD',[(x,y,z,130,245),(x+40,y,z+190,120,220)],a.P,16)
  a.ribbon('R2_ZENITH_OPEN_COURT',[(x-100,y-140,z+70),(x+100,y-140,z+70)],100,12,a.F)
 # Wider diagonal city link becomes a populated place rather than a transit stick.
 a.ribbon('R2_INTERIOR_CIVIC_CONTINENT',[(-1250,650,2140),(-450,950,2060),(250,1470,1930),(1000,1200,1750)],320,115,a.D)
 a.ribbon('R2_INTERIOR_CIVIC_GROUND',[(-1250,650,2142),(-450,950,2062),(250,1470,1932),(1000,1200,1752)],290,4,a.F)
 # The eastern void is a stepped interior world, with actual thick sectional rooms.
 for x,y,z in [(1780,500,660),(1470,850,1400),(1000,1350,2150)]:
  for j in range(3):
   a.loft('R2_EAST_SECTIONAL_QUARTER',[(x-200+j*180,y,z,65,280),(x-200+j*180+30,y,z+230+j*30,58,240)],a.P,12)
 edits=['Replaced closed eastern mass with deep open inland city and two vertical ravines.', 'Inserted a thick inhabited central peninsula, splitting the former frontal hole into successive low and high civic spaces.', 'Split crown into high-altitude urban grounds and widened the interior diagonal into a 320m city continent.']
a.S.camera=bpy.data.objects['02_OBLIQUE'];folder=R/('revision_'+str(rev));folder.mkdir(exist_ok=True)
a.export(folder,'R17_REVISION_'+str(rev))
(folder/'REVISION_RECORD.json').write_text(json.dumps(dict(source=str(source.relative_to(R)),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),observed_predecessor_images=['01_FRONT.png','02_OBLIQUE.png'],removed_primary_meshes=removed,main_form_edits=edits,not_formal_adoption=True),indent=2),encoding='utf8')
a.render(folder,args[1:] or ['01_FRONT','02_OBLIQUE','03_SIDE','04_REAR','05_AERIAL','06_UNDERSIDE','07_GROUND_UP'])
