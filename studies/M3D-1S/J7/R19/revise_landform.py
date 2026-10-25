"""Observed initial six views -> replace shelf grammar with individually fitted city sections.
Preserves initial BLEND/GLB and images. Fixes the initial rib pivot error explicitly.
"""
import bpy,bmesh,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));import atelier as a
bpy.ops.wm.open_mainfile(filepath=str(R/'initial/R19_INITIAL.blend'));a.bind()
removed=[]
def erase(prefix):
 for o in list(a.A.objects):
  if o.name.startswith(prefix):removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)

# Correct every surviving initial rib in mesh space around its actual centre.
for o in list(a.A.objects):
 if '_city_rib_' in o.name:
  angle=o.rotation_euler.z;ctr=sum((v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
  rot=Matrix.Rotation(angle,3,'Z')
  for v in o.data.vertices:v.co=ctr+rot@(v.co-ctr)
  o.rotation_euler.z=0

# Remove the ENTIRE western/top bank-and-floor assembly, not ornament it.
for prefix in ['B1_','B2_','B3_','B4_','E_HIGH_','E_PUBLIC_','D_WEST_','D_HIGH_WEST']:
 erase(prefix)

def cut(o,n,poly,z,h):
 cutter=a.prism('TEMP_'+n,poly,z,h,a.D);bpy.context.view_layer.objects.active=o
 mod=o.modifiers.new('Actual public urban void','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
 bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)

def rect(cx,cy,w,d):return [(cx-w/2,cy-d/2),(cx+w/2,cy-d/2),(cx+w/2,cy+d/2),(cx-w/2,cy+d/2)]

def ring(n,outer,inner,z,h,mat,omit=()):
 # Direct authored annular solid; absent opposite segments are actual streets.
 N=len(outer);verts=[(x,y,zz) for zz in (z,z+h) for path in (outer,inner) for x,y in path];faces=[]
 included=set(range(N))-set(omit)
 for i in sorted(included):
  j=(i+1)%N
  faces.extend([(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)])
  if (i-1)%N not in included:faces.append((i,N+i,3*N+i,2*N+i))
  if j not in included:faces.append((j,2*N+j,3*N+j,N+j))
 return a.mesh(n,verts,faces,mat)

def urban_section(n,c,w,d,h,turn=0,lean=(0,0),levels=4):
 """A non-uniform stepped precinct, with through public streets inside real mass.
 Each 300-900m inhabited cliff contains a deep civic canyon and several linked
 roof streets. A 140m court is a real void through the building.
 """
 old=set(a.A.objects);cx,cy,z=c
 poly=[(-w*.46,-d*.50),(w*.28,-d*.50),(w*.5,-d*.24),(w*.46,d*.29),(w*.05,d*.5),(-w*.5,d*.32)]
 for k in range(levels):
  t=k/levels;sc=1-.22*t;dx=lean[0]*t;dy=lean[1]*t
  p=[(cx+x*sc+dx,cy+y*sc+dy) for x,y in poly];zz=z+h*t;hh=h/levels
  court=[(cx+x*.35*sc+dx,cy+y*.4*sc+dy) for x,y in poly]
  bodymat=a.G if k%3 else a.P
  if k%2==0:
   ring(n+f'_inhabited_cliff_lower_{k}',p,court,zz,24,bodymat)
   ring(n+f'_inhabited_cliff_portal_{k}',p,court,zz+24,hh*.45,bodymat,omit=(0,3))
   ring(n+f'_inhabited_cliff_upper_{k}',p,court,zz+24+hh*.45,hh-26-24-hh*.45,bodymat)
  else:ring(n+f'_inhabited_cliff_{k}',p,court,zz,hh-26,bodymat)
  # Roof contours follow the carved urban depth, not a full slab.
  ring(n+f'_roof_ground_{k}',p,court,zz+hh-26,13,a.P)
  for off in range(23,int(hh-28),27):
   omit=(0,3) if k%2==0 and off<24+hh*.45 and off>24 else ()
   ring(n+f'_occupied_floor_{k}_{off}',p,court,zz+off,2.8,a.P if k%3 else a.T,omit=omit)
  # The courtyard inner side is a distinct public face, not an exterior decal.
  a.route(n+f'_court_balcony_{k}',[(cx+dx-w*.20,cy+dy-d*.22,zz+hh-12),(cx+dx-w*.20,cy+dy+d*.22,zz+hh-12),(cx+dx+w*.20,cy+dy+d*.22,zz+hh-12)],24,8)
 # Rotate complete section in WORLD mesh space about its intended centre.
 rot=Matrix.Rotation(turn,3,'Z');center=Vector((cx,cy,z))
 for o in set(a.A.objects)-old:
  for v in o.data.vertices:v.co=center+rot@(v.co-center)
 print('REBUILT SECTION',n,flush=True)
 return [o for o in a.A.objects if o.name.startswith(n)]

# Western 3D city topography: individually fitted 300–900m precincts overlap
# vertically and laterally to make the urban mountain; no giant outer shell.
sections=[
 ('W01',(-2420,-710,390),720,670,1050,-.18,(90,70),4),
 ('W02',(-1710,-520,540),620,750,1110,.17,(-80,20),4),
 ('W03',(-2730,80,850),640,620,1210,-.23,(140,20),4),
 ('W04',(-2020,140,1180),730,650,1270,.12,(90,120),5),
 ('W05',(-1310,220,1120),530,650,920,.26,(-130,60),3),
 ('W06',(-2520,810,1640),650,720,1410,-.26,(140,150),5),
 ('W07',(-1770,880,1870),690,720,1350,.14,(110,40),5),
 ('W08',(-1120,1000,2040),560,620,1000,.30,(-40,150),4),
 ('W09',(-2240,1560,2540),680,700,1510,-.18,(80,160),5),
 ('W10',(-1500,1680,2940),720,700,1280,.18,(160,40),4),
 ('W11',(-710,1920,3140),650,710,890,.40,(-40,10),3),
 ('W12',(-1250,2400,2970),690,510,670,-.2,(110,0),3),
]
for args in sections:urban_section(*args)

# Middle hinge is a broad occupied land bridge formed from four dissimilar
# cliff precincts around a 600m opening, replacing the former isolated U shelf.
for args in [
 ('M01',(-550,550,1790),600,700,1120,-.30,(100,80),4),
 ('M02',(-120,1260,2180),710,630,1140,.12,(160,-30),4),
 ('M03',(570,1120,2080),530,670,920,-.3,(-70,90),3),
 ('M04',(670,290,1790),550,600,870,.10,(80,20),3),
]:urban_section(*args)
a.route('M_SHARED_SKY_GROUND',[(-1070,1240,2790),(-430,1530,2790),(160,1620,2810),(750,1330,2750),(1110,840,2530)],190,65)

# High eastern continent: the surface remains a basin but its formerly blank
# 300m ground is excavated into an inhabited underside city.
for prefix in ['D_HIGH_EAST_','D_UNDERSIDE_']:erase(prefix)
poly=[(800,-700),(1830,-950),(2540,-280),(2380,650),(1570,1150),(870,740)]
for k in range(3):
 ground=a.prism(f'D_EAST_REAL_INHABITED_TERRAIN_{k}',poly,2090+k*140,100,a.G if k!=1 else a.D)
 for xx,yy,ww,dd in [(1270,0,190,1900),(1960,100,150,1900),(1600,520,2200,180)]:
  cut(ground,'EAST_THROUGH_URBAN_GALLERIES',rect(xx,yy,ww,dd),2090+k*140+22,85)
 a.prism(f'D_EAST_SHARED_PUBLIC_GROUND_{k}',poly,2190+k*140,15,a.P)
for args in [
 ('U01',(1100,-300,1330),470,550,800,-.3,(0,0),3),
 ('U02',(1820,-350,1340),540,620,800,.25,(-40,0),3),
 ('U03',(2190,350,1340),430,600,820,-.2,(-30,0),3),
]:urban_section(*args)
a.route('U_SHARED_HANGING_CITY',[(840,-400,1530),(1260,-740,1530),(1840,-740,1530),(2290,-300,1530),(2260,480,1530)],145,48)

# Base is no longer a blank pedestal: actual 90m streets pass into thick land.
for o in list(a.A.objects):
 if o.name.endswith('_deep_public_land') and o.name.startswith('A_'):
  coords=[v.co for v in o.data.vertices];zmin=min(p.z for p in coords);zmax=max(p.z for p in coords)
  xm=(min(p.x for p in coords)+max(p.x for p in coords))/2;ym=(min(p.y for p in coords)+max(p.y for p in coords))/2
  for xx in (xm-260,xm+240):cut(o,'GROUND_CIVIC_PASSAGE',rect(xx,ym,135,5000),zmin+45,max(60,zmax-zmin-95))

# Repair transport arrivals to match the revised inhabited terrain.
a.route('R1_HIGH_CITY_ARRIVAL',[(-2050,1500,3260),(-1520,1900,3290),(-850,2040,3290),(-260,1700,2820)],95,35)
record={
 'source':'initial/R19_INITIAL.blend',
 'source_sha256':hashlib.sha256((R/'initial/R19_INITIAL.blend').read_bytes()).hexdigest(),
 'observed_images':['qa/INITIAL_SIX.jpg','initial/01_FRONT.png'],
 'initial_art_decision':'ART_REJECT: disconnected repetitive shopping-centre bands on blank slab grounds; floating rib pivot bug',
 'removed_mesh_count':len(removed),
 'removed_prefixes':['B1','B2','B3','B4','E_HIGH','D_WEST','D_HIGH_WEST','D_HIGH_EAST','D_UNDERSIDE'],
 'new_macro_geometry':'12 individually fitted pierced western precincts, four central hinge precincts, three reverse underside precincts; real galleries carved into east terrain and base',
 'initial_rib_bug_fixed':True,
 'success_not_presumed':True,
 'canonical_adoption':False,
}
(R/'revision_1').mkdir(exist_ok=True);(R/'revision_1/REVISION_RECORD.json').write_text(json.dumps(record,indent=2),encoding='utf8')
a.save(R/'revision_1','R19_REVISION_1');a.render(R/'revision_1',['01_FRONT','02_OBLIQUE','04_REAR','06_UNDERSIDE'])
