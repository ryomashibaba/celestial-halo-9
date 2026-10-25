"""Second macro edit after observing the repeated precinct stacks in revision 1.
Not a success declaration. Final research evidence retains both earlier models.
"""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));import atelier as a
bpy.ops.wm.open_mainfile(filepath=str(R/'revision_1/R19_REVISION_1.blend'));a.bind()
deleted=[]
def erase(prefix):
 for o in list(a.A.objects):
  if o.name.startswith(prefix):deleted.append(o.name);bpy.data.objects.remove(o,do_unlink=True)

# Urban sections share folded ground rather than float as a row of individual stacks.
# Shape each upper precinct, not only its material: broad taper, sheared crown,
# nonuniform vertical interval. Preserve every real court and transverse opening.
section_data={
 'W01':(-2420,-710,390,1050,-110,80), 'W02':(-1710,-520,540,1110,150,30),
 'W03':(-2730,80,850,1210,70,90),'W04':(-2020,140,1180,1270,-50,150),
 'W05':(-1310,220,1120,920,180,30),'W06':(-2520,810,1640,1410,150,150),
 'W07':(-1770,880,1870,1350,120,100),'W08':(-1120,1000,2040,1000,170,-40),
 'W09':(-2240,1560,2540,1510,180,190),'W10':(-1500,1680,2940,1280,160,120),
 'W11':(-710,1920,3140,890,170,80),'W12':(-1250,2400,2970,670,120,50),
 'M01':(-550,550,1790,1120,90,80),'M02':(-120,1260,2180,1140,-80,90),
 'M03':(570,1120,2080,920,120,80),'M04':(670,290,1790,870,-90,70),
}
for o in list(a.A.objects):
 pre=o.name.split('_')[0]
 if pre not in section_data:continue
 cx,cy,z,h,lx,ly=section_data[pre]
 for v in o.data.vertices:
  t=max(0,min(1,(v.co.z-z)/h));dx=v.co.x-cx;dy=v.co.y-cy
  v.co.x=cx+dx*(1-.24*t)+lx*t*t
  v.co.y=cy+dy*(1-.12*t)+ly*t
  # Continuous stepped urban ridge has a sloping upper horizon, not flat caps.
  v.co.z+=.14*dx*t+.10*dy*t
 if '_inhabited_cliff_' in o.name:
  o.data.materials.clear();o.data.materials.append(a.G if pre.startswith('W') else a.P)

def inhabited_land(n,path,w,h):
 # Real 180–300m city depth with 60–100m public streets, continuous roof ground.
 a.band(n+'_lower_ground',path,w,28,a.D)
 l,r=a.edges(a.shift(path,28),w*.66)
 a.band(n+'_inner_urban_shore',l,w*.22,h*.70,a.G)
 a.band(n+'_outer_urban_shore',r,w*.22,h*.80,a.P)
 a.band(n+'_shared_roof_land',a.shift(path,h),w,22,a.C)
 for off in range(35,int(h*.7),30):
  a.band(n+'_occupied_shore_floor',a.shift(l,off),w*.23,3,a.P)
  a.band(n+'_outer_urban_floor',a.shift(r,off),w*.23,3,a.D)
 # Upper garden is part of continuous ground, not a replacement for city mass.
 a.band(n+'_public_garden',a.shift(path,h+22),w*.20,5,a.V)
 a.route(n+'_middle_public_street',a.shift(path,32),w*.30,10)

lands=[
 ('L_WEST_LOW',[(-2700,-420,850),(-2200,-310,970),(-1560,-340,1120)],540,220),
 ('L_WEST_MIDDLE',[(-2670,360,1620),(-2180,420,1780),(-1610,540,1880),(-1110,770,2080)],560,260),
 ('L_UPPER_REVERSE',[(-2350,1220,2480),(-1870,1370,2600),(-1190,1580,2810),(-600,1800,3050)],640,290),
 ('L_HIGHEST_SHARED',[(-2050,1810,3420),(-1540,1990,3470),(-1000,2180,3490),(-580,2260,3420)],520,220),
 ('L_CENTRAL_SADDLE',[(-1480,780,2090),(-900,1000,2280),(-400,1330,2530),(180,1470,2700),(690,1190,2670)],480,250),
]
for args in lands:inhabited_land(*args)

# Eastern high city: replace the single repetitive U-building with a split skyline
# around a long diagonal civic canyon and a deep three-level reverse street.
erase('D_EAST_SKY_CITY');erase('D_SKY_WATER')
newbanks=[
 ('H_EASTERN_RIDGE',[(2050,-550,2516),(2280,-250,2620),(2110,260,2780),(1740,690,2910)],300,760,1),
 ('H_INNER_BASIN',[(1130,-220,2516),(1390,-470,2516),(1770,-430,2516)],255,360,2),
 ('H_HIGH_HORIZON',[(1350,770,2516),(1500,1050,2516),(1920,880,2516),(2100,600,2516)],265,510,0),
]
for n,p,w,h,s in newbanks:a.citybank(n,p,w,h,s)
# Correct rib pivots for these newly built bank meshes as well.
for o in a.A.objects:
 if o.name.startswith('H_') and '_city_rib_' in o.name:
  ctr=sum((v.co for v in o.data.vertices),Vector())/len(o.data.vertices);rot=Matrix.Rotation(o.rotation_euler.z,3,'Z')
  for v in o.data.vertices:v.co=ctr+rot@(v.co-ctr)
  o.rotation_euler.z=0
inhabited_land('H_CANYON_GROUND',[(1100,70,2460),(1510,220,2460),(1760,550,2460),(1510,820,2460)],470,38)
a.lake('H_RESERVOIR',[(1370,-50),(1610,-170),(1880,60),(1790,300),(1530,400),(1310,220)],2514)
# Join the 31m gap between ground and old public level explicitly.
poly=[(800,-700),(1830,-950),(2540,-280),(2380,650),(1570,1150),(870,740)]
a.prism('H_CONTINUOUS_TOP_GROUND',poly,2485,31,a.C)

# Internal confluence is no longer a hotel on a blank shelf: remove its top band
# and pierce the ground beneath with real city-scale mouths.
for pre in ['F_CIVIC_WEST','F_EAST_PUBLIC']:erase(pre)
inhabited_land('F_PUBLIC_ISTHMUS',[(-800,100,1176),(-360,-280,1176),(220,-140,1176),(650,240,1176)],440,260)
inhabited_land('F_REVERSE_ISTHMUS',[(-650,620,1176),(-150,870,1176),(370,670,1176)],420,310)

# The north face acquires a long *different* stepped urban district, not a rear decal.
inhabited_land('N_REAR_HIGH_CITY',[(-1100,2110,1940),(-580,2400,1940),(150,2500,1940),(800,2250,1940)],470,340)
a.route('N_REVERSE_TRANSIT',[(-1550,2350,1600),(-900,2590,1950),(-250,2730,2290),(700,2480,2290),(1500,2070,1600)],68,25)

# Camera positions are part of the actual saved model. They are not image edits.
def pose(n,p,t,lens=23,ortho=None):
 o=bpy.data.objects.get(n)
 if not o:
  d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d);a.E.objects.link(o)
 o.location=p;o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler();o.data.type='ORTHO' if ortho else 'PERSP';o.data.lens=lens;o.data.clip_start=.15;o.data.clip_end=200000
 if ortho:o.data.ortho_scale=ortho
 return o
pose('08_LOW',(-370,-1110,700),(0,600,2300),22)
pose('09_MID',(-100,-650,1440),(700,900,2870),22)
pose('10_HIGH',(1570,480,2580),(-650,1540,3500),22)
pose('11_REVERSE_CITY',(400,4100,2200),(0,1800,2100),26)
human=pose('13_HUMAN',(-2500,-2040,153.7),(-800,300,2200),24)

record={'source':'revision_1/R19_REVISION_1.blend','source_sha256':hashlib.sha256((R/'revision_1/R19_REVISION_1.blend').read_bytes()).hexdigest(),
 'observed_before':['revision_1/01_FRONT.png','revision_1/02_OBLIQUE.png'],
 'revision_1_art':'ART_REJECT: repeated detached stack cells, still a facility model rather than inhabited terrain',
 'mesh_edits':['Reshaped 16 western/hinge precincts into tapered sheared horizons in actual vertex positions.',
 'Added five 480–640m-wide inhabited shared urban grounds with actual interior streets, connecting separate western precincts.',
 'Removed eastern U-building and rebuilt three unlike sky ridges around a diagonal basin.',
 'Replaced inner confluence bands with two broad occupied public isthmuses; added independent north-facing high city.',
 'Closed the measured 31m eastern ground/precinct gap.'],
 'removed_meshes':len(deleted),'not_formal_art':True,'art_success_not_presumed':True}
(R/'final').mkdir(exist_ok=True);(R/'final/REVISION_RECORD.json').write_text(json.dumps(record,indent=2),encoding='utf8')
a.save(R/'final','R19_LIVING_HORIZON');a.render(R/'final',['01_FRONT','02_OBLIQUE','03_SIDE','04_REAR','05_AERIAL','06_UNDERSIDE','07_GROUND','08_LOW','09_MID','10_HIGH','11_REVERSE_CITY','13_HUMAN'])

# Independent noncanonical 10km frame. Comparators are unnamed research markers;
# none are assigned W0/H/SB anchors or pretended to be completed districts.
context=bpy.data.collections.new('NONCANONICAL_10KM_SCALE_ONLY');a.S.collection.children.link(context)
for i,(x,y,w,d,h) in enumerate([(-4100,-3000,600,900,650),(3900,-2200,700,900,980),(-4300,2400,650,700,1100),(3600,3100,700,1000,1250),(1000,4000,700,500,500),(3300,1000,450,600,720)]):
 a.box('Unassigned research comparator '+str(i),(x,y,h/2-110),(w,d,h),a.D,context)
for i,(x,y,dx,dy) in enumerate([(0,-5000,10000,8),(0,5000,10000,8),(-5000,0,8,10000),(5000,0,8,10000)]):a.box('10km reference boundary '+str(i),(x,y,-145),(dx,dy,8),a.T,context)
a.S.camera=bpy.data.objects['12_CITY_10KM'];bpy.data.objects['STUDIO ground'].hide_render=False
(R/'context').mkdir(exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(R/'context/R19_NONCANONICAL_10KM.blend'),compress=True)
a.S.render.filepath=str(R/'context/12_CITY_10KM.png');bpy.ops.render.render(write_still=True)
(R/'context/LIMITS.json').write_text(json.dumps({'width_m':10000,'depth_m':10000,'canonical_anchor':'UNVERIFIED','W0_H_SB_integrated':False,'city_master_complete':False,'comparators':'Unnamed scale masses only; not designed city facilities'},indent=2),encoding='utf8')
