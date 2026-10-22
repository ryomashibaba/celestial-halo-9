"""MASSING REINVENTION: actual hollow city envelopes, metres, Z up.
Run with ordinary Python 3 + Shapely 2.1. Does not import or modify legacy assets.
"""
from pathlib import Path
import math,json,hashlib
from shapely import Polygon,LineString,Point,box,constrained_delaunay_triangles,make_valid
from shapely.geometry.polygon import orient
from shapely.affinity import rotate,translate

ROOT=Path(__file__).resolve().parent
OBJECTS=[]

def polys(g):
    if g.is_empty:return []
    if g.geom_type=='Polygon':return [g]
    return [p for v in getattr(g,'geoms',[]) for p in polys(v)]

def clean(p,r=0):
    p=make_valid(p)
    if r:p=p.buffer(-r,quad_segs=3).buffer(r,quad_segs=3)
    return p

def extrude(name,poly,mapper,lo,hi,body,role='PRIMARY'):
    """2D polygon + position-dependent extrusion; triangulated faces, explicit voids."""
    vs=[];fs=[];cache={}
    def index(v):
        k=tuple(round(float(a),4) for a in v)
        if k not in cache:cache[k]=len(vs);vs.append(k)
        return cache[k]
    def face(coords):fs.append([index(c) for c in coords])
    for p in polys(clean(poly)):
        if p.area<1:continue
        p=orient(p,sign=1)
        for tri in constrained_delaunay_triangles(p).geoms:
            c=list(tri.exterior.coords)[:3]
            if (c[1][0]-c[0][0])*(c[2][1]-c[0][1])-(c[1][1]-c[0][1])*(c[2][0]-c[0][0])<0:c.reverse()
            face([mapper(a,b,hi(a,b)) for a,b in c]);face([mapper(a,b,lo(a,b)) for a,b in reversed(c)])
        for ring in [p.exterior]+list(p.interiors):
            c=list(ring.coords)
            for a,b in zip(c,c[1:]):face([mapper(*a,lo(*a)),mapper(*b,lo(*b)),mapper(*b,hi(*b)),mapper(*a,hi(*a))])
    OBJECTS.append({'name':name,'vertices':vs,'faces':fs,'body':body,'role':role})

def planar(u,v,z):return (u,v,z)
def frame(angle,origin):
    co,si=math.cos(angle),math.sin(angle)
    def point(u,z,v):return (origin[0]+co*u-si*v,origin[1]+si*u+co*v,z)
    return point

def block(name,center,size,body,role='FACILITY',angle=0):
    x,y,z=center;w,d,h=size;co,si=math.cos(angle),math.sin(angle)
    def mapper(u,v,zz):return (x+co*u-si*v,y+si*u+co*v,zz)
    extrude(name,box(-w/2,-d/2,w/2,d/2),mapper,lambda a,b:z-h/2,lambda a,b:z+h/2,body,role)

def shell_boundary(name,outer,inner,mapper,depth,body):
    """Deep outer roof, inner civic ledges leave most of the inhabited section open."""
    # Follow the actual DIFFERENCE boundary: raw outer edges may pass across a carved gate.
    profile=clean(Polygon(outer).difference(Polygon(inner)))
    reference=LineString(inner+[inner[0]])
    groups={'outer':[],'inner':[]}
    for p in polys(profile):
        for ring in [p.exterior]+list(p.interiors):
            line=list(ring.coords)
            for a,b in zip(line,line[1:]):
                mid=Point((a[0]+b[0])/2,(a[1]+b[1])/2)
                groups['inner' if reference.distance(mid)<.1 else 'outer'].append((a,b))
    for key,segments in groups.items():
        inner_edge=key=='inner'
        vs=[];fs=[]
        for a,b in segments:
            for side in ([-1,1] if inner_edge else [0]):
                if side<0:va,vb=lambda u,z:-depth(u,z)/2,lambda u,z:-depth(u,z)/2+100
                elif side>0:va,vb=lambda u,z:depth(u,z)/2-100,lambda u,z:depth(u,z)/2
                else:va,vb=lambda u,z:-depth(u,z)/2,lambda u,z:depth(u,z)/2
                off=len(vs)
                vs.extend([mapper(*a,va(*a)),mapper(*b,va(*b)),mapper(*b,vb(*b)),mapper(*a,vb(*a))])
                fs.append([off+i for i in range(4)])
        OBJECTS.append({'name':name+'_'+key,'vertices':vs,'faces':fs,'body':body,'role':'PRIMARY'})

def floors_in_profile(prefix,profile,mapper,depth,levels,body):
    for z in levels:
        cut=profile.intersection(box(-10000,z-.2,10000,z+.2))
        for i,p in enumerate(polys(cut)):
            a,_,b,_=p.bounds
            if b-a<80:continue
            w=min(depth(a,z),depth(b,z))*.5-125
            extrude(prefix+'_'+str(z)+'_'+str(i),box(a+8,-w,b-8,w),
                lambda u,v,zz:mapper(u,zz,v),lambda u,v:z-45,lambda u,v:z,body,'CITY_GROUND')

def corridor(name,points,width,height,body='TRANSIT'):
    # Actual human-scale transport envelope, deliberately subordinate to city mass.
    for i,(a,b) in enumerate(zip(points,points[1:])):
        dx,dy=b[0]-a[0],b[1]-a[1];ll=math.hypot(dx,dy)
        if ll<.1:continue
        nx,ny=-dy/ll,dx/ll
        vs=[]
        for p in [a,b]:
            for u,z in [(-width/2,-height/2),(width/2,-height/2),(width/2,height/2),(-width/2,height/2)]:
                vs.append((p[0]+nx*u,p[1]+ny*u,p[2]+z))
        OBJECTS.append({'name':name+'_'+str(i),'vertices':vs,'faces':[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'body':body,'role':'TRANSIT'})

def civic_room(name,xy,z,w,d,h,body,angle=0):
    # A few hundred-metre open civic facilities: wall/core, galleries, roof; real interior.
    co,si=math.cos(angle),math.sin(angle)
    def place(label,u,v,zz,size,role='FACILITY'):
        block(name+'_'+label,(xy[0]+co*u-si*v,xy[1]+si*u+co*v,zz),size,body,role,angle)
    place('public_floor',0,0,z-25,(w,d,50),'CITY_GROUND')
    place('roof',0,0,z+h-45,(w,d,90))
    place('inhabited_core',-w/2+55,0,z+h/2,(110,d,h))
    place('library_wall',w/2-45,0,z+h/2,(90,d,h))
    place('rear_galleries',0,d/2-45,z+h*.45,(w-180,90,70))

# A: a deep inhabited portal. Apertures are city rooms in a wall, not window decoration.
Aouter=[(-1800,0),(-2070,700),(-1950,2050),(-1370,3200),(-600,3800),(160,3620),(1040,2800),(1450,1350),(1350,0)]
Ainner=[(-1100,0),(-1220,650),(-1000,1720),(-480,2590),(0,2780),(450,2310),(650,1450),(650,0)]
Aprofile=clean(Polygon(Aouter+list(reversed(Ainner))))
Amap=frame(-.12,(0,650))
def Ad(u,z):return 970-270*min(1,z/3800)+100*math.sin((u+1800)/3200*math.pi)
frontcuts=[Polygon([(-1910,650),(-1370,850),(-1190,1550),(-1740,1530)]),
           Polygon([(-1030,2990),(110,2990),(300,3360),(-680,3520)]),
           Polygon([(690,1190),(1250,1100),(1190,1820),(620,1800)])]
backcuts=[Polygon([(-1790,1450),(-1210,1670),(-890,2270),(-1420,2350)]),
          Polygon([(-930,3020),(190,3020),(240,3400),(-640,3540)]),
          Polygon([(650,450),(1270,510),(1230,1120),(700,1050)])]
for side,cuts in [(-1,frontcuts),(1,backcuts)]:
    p=Aprofile
    for c in cuts:p=p.difference(c)
    extrude('TENRYO_'+('south_city_wall' if side<0 else 'north_city_wall'),p,Amap,
       (lambda u,z:-Ad(u,z)/2) if side<0 else (lambda u,z:Ad(u,z)/2-165),
       (lambda u,z:-Ad(u,z)/2+165) if side<0 else (lambda u,z:Ad(u,z)/2),'TENRYO')
shell_boundary('TENRYO_deep_envelope',Aouter,Ainner,Amap,Ad,'TENRYO')
floors_in_profile('TENRYO_district',Aprofile,Amap,Ad,[600,1550,3000],'TENRYO')
extrude('TENRYO_crown_urban_threshold',box(-800,-560,200,-240),lambda u,v,z:Amap(u,z,v),lambda u,v:2960,lambda u,v:3000,'TENRYO','CITY_GROUND')
for label,u,z,w,h in [('west_civic_core',-1680,850,190,1600),('east_civic_core',1020,750,170,1400)]:
    p=Amap(u,z,0);block('TENRYO_'+label,p,(w,450,h),'TENRYO')

# B: an asymmetric inhabited basin. One landmass with a large civic courtyard and crypt.
Bouter=orient(clean(Polygon([(-1900,480),(-900,1050),(700,1080),(2240,520),(2500,-380),(1850,-1210),(300,-1560),(-1200,-1050),(-1740,-400)]),80),sign=1)
Bcourt=clean(Polygon([(-720,0),(-380,-720),(620,-800),(1260,-340),(1080,250),(170,480)]),70)
Bpoly=Bouter.difference(Bcourt)
def Bt(x,y):return 1750+.16*(x+600)+.055*(y+300)
def Bb(x,y):return 1080+.05*abs(x-400)
extrude('CHOTEI_carved_keel',Bpoly,planar,Bb,lambda x,y:Bb(x,y)+140,'CHOTEI')
eastangle=-math.pi/2+.1
eastfoot=translate(rotate(box(-280,-350,280,350),eastangle,origin=(0,0),use_radians=True),1510,-420)
northfoot=translate(rotate(box(-250,-175,250,175),.04,origin=(0,0),use_radians=True),350,780)
j1foot=translate(rotate(box(-230,-340,230,340),-.12,origin=(0,0),use_radians=True),690,650)
j2foot=translate(rotate(box(-260,-210,260,210),math.pi/2,origin=(0,0),use_radians=True),-700,-520)
civicstreet=box(-950,-730,-250,-300)
facilities=eastfoot.union(northfoot).union(j1foot).union(j2foot).union(civicstreet)
extrude('CHOTEI_sky_landform',Bpoly.difference(facilities),planar,lambda x,y:Bt(x,y)-135,Bt,'CHOTEI')
# A thick inhabited hull replaces the former open perimeter/deck reading.
outerwall=Bouter.difference(Bouter.buffer(-180,quad_segs=3))
gates=box(-200,-1700,650,-1100).union(box(2100,-420,2700,250))
extrude('CHOTEI_outer_city_shell',outerwall.difference(gates),planar,lambda x,y:Bb(x,y)+130,lambda x,y:Bt(x,y)-125,'CHOTEI')
extrude('CHOTEI_gate_foundations',outerwall.intersection(gates),planar,lambda x,y:Bb(x,y)+130,lambda x,y:Bb(x,y)+250,'CHOTEI')
extrude('CHOTEI_gate_roofs',outerwall.intersection(gates),planar,lambda x,y:Bt(x,y)-265,lambda x,y:Bt(x,y)-125,'CHOTEI')
innerbank=Bcourt.buffer(135,quad_segs=3).difference(Bcourt).intersection(Bpoly)
innergates=box(-1100,-240,-300,200).union(box(900,-580,1600,30)).union(box(-100,0,500,1000))
innerbank=innerbank.difference(innergates.union(j1foot).union(j2foot).union(civicstreet))
extrude('CHOTEI_inhabited_court_bank',innerbank,planar,lambda x,y:1360,lambda x,y:Bt(x,y)-120,'CHOTEI')
extrude('CHOTEI_central_public_ground',Bcourt,planar,lambda x,y:1450,lambda x,y:1500,'CHOTEI','CITY_GROUND')
# Public gateways through the courtyard's bank: open the west and southeast connection.
# Main gate is furnished by a broad passage above the lower crypt rather than extra decks.
westgate=box(-1000,-180,-400,120).intersection(Bouter)
extrude('CHOTEI_west_public_passage',westgate,planar,lambda x,y:1450,lambda x,y:1500,'CHOTEI','CITY_GROUND')
extrude('CHOTEI_east_public_ramp',box(900,-560,1800,-160),planar,lambda x,y:1455+min(40,max(0,(x-900)*40/260)),lambda x,y:1500+min(40,max(0,(x-900)*40/260)),'CHOTEI','CITY_GROUND')
extrude('CHOTEI_cavern_public_ramp',box(-490,-730,-250,-300),planar,lambda x,y:1505-(x+490)*50/240,lambda x,y:1550-(x+490)*50/240,'CHOTEI','CITY_GROUND')
civic_room('CHOTEI_east_forum',(1510,-420),1540,560,700,510,'CHOTEI',eastangle)
civic_room('CHOTEI_north_institute',(350,780),1680,500,350,300,'CHOTEI',.04)

# A hollow inhabited support below the eastern basin; not a generic slender column.
Rout=[(-700,0),(430,0),(350,470),(-50,1500),(-720,1510),(-920,900)]
Rhole=Polygon([(-530,180),(110,180),(-190,1030),(-530,1000)])
Rprofile=clean(Polygon(Rout).difference(Rhole),35)
Rmap=frame(-.22,(1840,-590))
extrude('CHOTEI_ground_city_root',Rprofile,Rmap,lambda u,z:-260,lambda u,z:260,'CHOTEI')
floors_in_profile('CHOTEI_root_district',Rprofile,Rmap,lambda u,z:520,[300,1050],'CHOTEI')

# C: a diagonal hollow urban wedge with a continuous cavern, not another ring or band.
Couter=[(0,0),(700,0),(1690,1100),(3100,1690),(4300,1610),(4170,2210),(2870,2810),(1630,2310),(470,1110)]
Cinner=[(840,350),(1690,1100),(2850,1510),(3550,1510),(2970,2310),(1730,1840)]
Cprofile=clean(Polygon(Couter).difference(Polygon(Cinner)))
Cmap=frame(math.radians(45),(-2200,-1900))
def Cd(u,z):return 700+220*math.sin(min(1,u/4300)*math.pi)
for side in [-1,1]:
    p=Cprofile
    if side<0:p=p.difference(Polygon([(1380,1410),(1750,1640),(2650,2120),(2510,2300),(1630,1910)]))
    else:p=p.difference(Polygon([(2180,1370),(3100,1790),(3580,1690),(3500,2010),(2780,2240),(2200,1840)]))
    extrude('SHATO_'+('west_canyon_wall' if side<0 else 'east_canyon_wall'),p,Cmap,
      (lambda u,z:-Cd(u,z)/2) if side<0 else (lambda u,z:Cd(u,z)/2-150),
      (lambda u,z:-Cd(u,z)/2+150) if side<0 else (lambda u,z:Cd(u,z)/2),'SHATO')
shell_boundary('SHATO_cavern_envelope',Couter,Cinner+[Cinner[0]],Cmap,Cd,'SHATO')
floors_in_profile('SHATO_cavern_district',Cprofile,Cmap,Cd,[450,1550,2370],'SHATO')

# Three civic junctions, spatially different: a public gate, an ascending forum, a sky hall.
civic_room('J1_public_gate',(690,650),1550,460,680,430,'JUNCTION',-.12)
civic_room('J2_ascending_forum',(-700,-520),1550,520,420,440,'JUNCTION',math.pi/2)
civic_room('J3_crown_exchange',(80,650),2370,420,500,350,'JUNCTION',.1)

# Legible transport hierarchy, no light strips or surface decoration.
corridor('ground_to_basin',[(-1500,-1450,60),(-1100,-950,450),(-710,-500,1550),(690,650,1550)],42,45)
corridor('basin_to_sky',[(-710,-500,1550),(-420,40,2060),(80,650,2370),(-380,700,3000)],40,42)
corridor('civic_basin_route',[(-650,-50,1535),(100,-480,1535),(1000,-430,1535),(1510,-420,1580)],55,35)

# Ground forum is part of the architectural itinerary; context remains separate.
block('GROUND_public_forum',(-300,-900,-35),(1600,1400,70),'PUBLIC_GROUND','CITY_GROUND')
block('GROUND_portal_public_ground',(0,400,-25),(1800,1200,50),'PUBLIC_GROUND','CITY_GROUND')

data={'units':'metres','up_axis':'Z','design':'ASTERION / INTERWOVEN VOIDS / R3','objects':OBJECTS,
 'opening_profiles':{'TENRYO_portal_local_uz':Ainner,'SHATO_cavern_local_uz':Cinner,
  'CHOTEI_courtyard_xy':list(Bcourt.exterior.coords)},
 'nominal_public_spaces':{'crown_district_floor_m':3000,'basin_floor_m':1500,'diagonal_exchange_floor_m':2370},
 'aperture_geometry':{
   'TENRYO_profile_removed_uz_bounds_m':Polygon(Aouter).intersection(Polygon(Ainner)).bounds,
   'SHATO_profile_removed_uz_bounds_m':Polygon(Couter).intersection(Polygon(Cinner)).bounds,
   'CHOTEI_court_xy_bounds_m':Bcourt.bounds,
   'note':'Bounds of actual removed profile/plan polygons, before occupation by other city bodies. Not empty bounding boxes in the assembled model.'}}
(ROOT/'geometry.json').write_text(json.dumps(data,separators=(',',':')),encoding='utf-8')
legacy=ROOT.parent/'research_asterion_primary_gate'
protected={str(p.relative_to(legacy)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(legacy.rglob('*')) if p.is_file()}
if not (ROOT/'protected_legacy_hashes.json').exists():(ROOT/'protected_legacy_hashes.json').write_text(json.dumps(protected,indent=2),encoding='utf-8')
print('Prepared',len(OBJECTS),'architectural meshes; legacy files only read.')
