"""C2-G4: real closed polygon prisms, metres/Z up; no generated imagery.
Run with Python 3 + shapely 2.1. Exported envelope geometry is NOT fitted housing.
"""
from pathlib import Path
import json, math, hashlib
from shapely import Polygon, box, constrained_delaunay_triangles
from shapely.affinity import scale, translate
from shapely.geometry.polygon import orient
ROOT=Path(__file__).resolve().parent
OBJECTS=[]
def parts(p):
    if p.is_empty:return []
    if p.geom_type=='Polygon':return [p]
    return [q for g in p.geoms for q in parts(g)]
def prism(name,p,lo,hi,role='CITY_MASS',axis='z'):
    verts=[];faces=[];ids={}
    def xyz(a,b,c):return (a,b,c) if axis=='z' else (a,c,b)
    def ind(v):
        v=tuple(round(float(x),4) for x in v)
        if v not in ids:ids[v]=len(verts);verts.append(v)
        return ids[v]
    def face(v):faces.append([ind(x) for x in v])
    for poly in parts(p):
        if poly.area<1:continue
        poly=orient(poly,sign=1)
        for t in constrained_delaunay_triangles(poly).geoms:
            c=list(t.exterior.coords)[:3]
            face([xyz(a,b,lo) for a,b in reversed(c)])
            face([xyz(a,b,hi) for a,b in c])
        for ring in [poly.exterior,*poly.interiors]:
            c=list(ring.coords)
            for (a,b),(d,e) in zip(c,c[1:]):face([xyz(a,b,lo),xyz(d,e,lo),xyz(d,e,hi),xyz(a,b,hi)])
    if verts:OBJECTS.append(dict(name=name,vertices=verts,faces=faces,role=role))
def oval(rx,ry,cx=0,cy=0,n=64):
    return Polygon([(cx+rx*math.cos(i*2*math.pi/n),cy+ry*math.sin(i*2*math.pi/n)) for i in range(n)])
def block(name,x,y,z,w,d,h,role):prism(name,box(x-w/2,y-d/2,x+w/2,y+d/2),z,z+h,role)
def save(name,spaces):
    (ROOT/(name+'.json')).write_text(json.dumps(dict(units='metres',up='Z',objects=OBJECTS,spaces=spaces),separators=(',',':')),encoding='utf-8')
    OBJECTS.clear()

# N1: widening inhabited caldera, a single thick civic vessel rather than a portal.
spaces=[]
for i,(z0,z1,rx,ry,ix,iy) in enumerate([(0,650,1770,1350,480,500),(650,1250,2090,1520,760,650),(1250,1900,2420,1690,1100,880),(1900,2450,2580,1740,1490,1140),(2450,3010,2450,1660,1780,1360),(3010,3420,2200,1510,1860,1400)]):
    outer=oval(rx,ry,-100,100)
    inner=oval(ix,iy,200,-40)
    # The public inlet reaches every band, widening upward. Upper rim is incomplete.
    mouth=Polygon([(-200,-200),(700,-200),(1100,-2600),(-400,-2600)])
    p=outer.difference(inner.union(mouth))
    if i==5:p=p.intersection(box(-3000,0,400,3000))
    if i==4:p=p.difference(box(1150,-3000,3000,100))
    prism('N1_inhabited_wall_'+str(i),p,z0,z1)
    if i in [1,3,4]:
        terrace=outer.difference(inner).difference(mouth).buffer(-45)
        prism('N1_public_terrace_'+str(i),terrace,z1,z1+8,'PUBLIC_GROUND')
        spaces.append(dict(level_m=z1,kind='inhabited caldera terrace',area_m2=round(terrace.area)))
block('N1_civic_floor',200,-40,600,1200,1000,50,'PUBLIC_GROUND')
# Facility volumes are open halls with side walls and roof, not solid cubes.
def hall(name,x,y,z,w,d,h):
    block(name+'_floor',x,y,z,w,d,10,'PUBLIC_GROUND')
    block(name+'_roof',x,y,z+h-22,w,d,22,'FACILITY')
    for s in [-1,1]:block(name+'_side_'+str(s),x+s*(w/2-18),y,z+10,36,d,h-32,'FACILITY')
hall('N1_civic_archive',-1200,300,1900,360,500,220)
hall('N1_forum',1000,400,1250,440,520,280)
save('N1',spaces)

# N2: civic escarpment. Six deep urban bands form a single continuous land-building.
# Profiles are deliberately unequal: one broad skyline, no crossing beams / forced triplet.
spaces=[]
profiles=[
 [(-2450,0),(-2300,440),(-1600,750),(-400,900),(850,730),(2350,300),(2450,0)],
 [(-2450,0),(-2330,850),(-1660,1300),(-650,1530),(550,1360),(2150,760),(2380,0)],
 [(-2320,0),(-2180,1320),(-1460,1930),(-440,2160),(620,1900),(1990,1130),(2260,0)],
 [(-2130,0),(-1980,1920),(-1250,2630),(-200,2830),(700,2390),(1700,1460),(2010,0)],
 [(-1860,0),(-1700,2380),(-1080,3150),(-180,3390),(550,3000),(1430,1840),(1720,0)],
 [(-1460,0),(-1360,2350),(-800,3060),(-140,3270),(510,2880),(1110,1880),(1450,0)]]
# South-to-north strata: 450m deep. Voids cut across these bands at the same levels.
for i,pts in enumerate(profiles):
    p=Polygon(pts)
    # Grand rooms excavated INTO the city mass, with roof/side material retained.
    if i in [1,2,3,4]:
        p=p.difference(box(-600,680,360,1030))
    if i in [3,4,5]:p=p.difference(Polygon([(-500,1650),(750,1650),(650,2060),(-400,2140)]))
    if i in [4,5]:p=p.difference(box(-850,2540,-100,2820))
    # A wide open-to-sky notch breaks the middle terraces, distinct from a roofed gate.
    if i<4:
        center=640-170*i
        p=p.difference(box(center-150,0,center+150,420+580*i))
    if i<5:
        terrace_z=[440,1100,1650,2300,2860][i]
        terrace_x0,terrace_x1=[(-1600,-450),(-1300,-300),(-1100,-350),(-900,-250),(-700,-240)][i]
        p=p.difference(box(terrace_x0,terrace_z,terrace_x1,5000))
    prism('N2_inhabited_stratum_'+str(i),p,-1420+i*450,-970+i*450,axis='y')
    # Major accessible horizontal grounds sit on solid mass; no thin stacked decks.
    if i<5:
        z=[440,1100,1650,2300,2860][i]
        x0,x1=[(-1600,-450),(-1300,-300),(-1100,-350),(-900,-250),(-700,-240)][i]
        # Trim platform to actual profile by selecting a conservative interior region.
        block('N2_ground_'+str(i),(x0+x1)/2,-1195+i*450,z,x1-x0,420,12,'PUBLIC_GROUND')
        spaces.append(dict(id='ground_'+str(i),level_m=z+12,area_m2=(x1-x0)*420,kind='terrace district envelope'))
        # Courtyard urban blocks. Each is 70-110m, not a kilometre-scale ornament.
        for k in range(max(1,int((x1-x0)/150))):
            x=x0+65+k*150
            footprint=box(x-48,-1300+i*450,x+48,-1100+i*450).difference(box(x-22,-1260+i*450,x+22,-1140+i*450))
            prism('N2_courtyard_%d_%d'%(i,k),footprint,z+12,z+70+(k%3)*14,'DISTRICT')
    # Vertical public circulation volumes embedded at rear, opened on north frontage.
    if i==5:
        for x in [-1050,870]:
            block('N2_vertical_exchange_'+str(x),x,1065,0,95,90,2450,'TRANSIT_ENVELOPE')
# Internal halls line the excavated rooms, with district scales nested within.
hall('N2_civic_assembly',-100,370,1650,560,600,270)
hall('N2_university',-475,950,2540,520,400,230)
hall('N2_ground_library',-100,-520,680,540,520,260)
block('N2_ground_forum',0,-1760,-12,1600,650,12,'PUBLIC_GROUND')
# Actual level transfer envelopes: concept lifts, not certified transit systems.
for x,y,h in [(-1050,-200,2300),(-700,680,2860)]:block('N2_lift_'+str(h),x,y,0,80,100,h,'TRANSIT_ENVELOPE')
save('N2',spaces)

# N1-R1: primary-mass revision, not detail of the rejected cylindrical N1.
# A continuous swelling outer wall and a continuously varying crest replace stacked drums.
# Internal terrace widths arise from inward steps of the same inhabited mass.
def outer_radius(z):
    return 1660+850*math.sin(min(z,3400)/3400*math.pi*.72)
def point(r,t,z):return (r*math.cos(t)-100+z*.065,r*.72*math.sin(t)+100,z)
tiers=[(0,750,320),(750,1450,720),(1450,2100,1130),(2100,2700,1510),(2700,3500,1790)]
segments=72
start=math.radians(-64);end=math.radians(256)
spaces=[]
for band,(zlo,zhi,rin) in enumerate(tiers):
    vs=[];fs=[]
    def f(coords):
        j=len(vs);vs.extend(coords);fs.append(list(range(j,j+len(coords))))
    for k in range(segments):
        a=start+(end-start)*k/segments;b=start+(end-start)*(k+1)/segments
        cap=lambda t:min(zhi,2900+460*math.sin(t)+170*math.cos(2*t))
        za,zb=cap(a),cap(b)
        if min(za,zb)<=zlo:continue
        oa=point(outer_radius(zlo),a,zlo);ob=point(outer_radius(zlo),b,zlo)
        Oa=point(outer_radius(za),a,za);Ob=point(outer_radius(zb),b,zb)
        ia=point(rin,a,zlo);ib=point(rin,b,zlo);Ia=point(rin,a,za);Ib=point(rin,b,zb)
        # Closed wedge sectors allow GLB topology inspection, no implicit occupancy formula.
        for q in [(oa,ob,Ob,Oa),(ib,ia,Ia,Ib),(Oa,Ob,Ib,Ia),(ob,oa,ia,ib),(oa,Oa,Ia,ia),(ob,ib,Ib,Ob)]:f(q)
    OBJECTS.append(dict(name='N1R1_city_shell_'+str(band),vertices=vs,faces=fs,role='CITY_MASS'))
    if band<4:
        nextinner=tiers[band+1][2]
        # The annular terrace is exactly over solid material of the band below.
        for k in range(segments):
            a=start+(end-start)*k/segments;b=start+(end-start)*(k+1)/segments
            vv=[point(rin+10,a,zhi),point(nextinner-10,a,zhi),point(nextinner-10,b,zhi),point(rin+10,b,zhi)]
            j=len(OBJECTS)
            OBJECTS.append(dict(name='N1R1_terrace_%d_%d'%(band,k),vertices=vv+[tuple([*v[:2],v[2]+8]) for v in vv],faces=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],role='PUBLIC_GROUND'))
        spaces.append(dict(id='inward_terrace_'+str(band),floor_m=zhi+8,inner_radius_m=rin+10,outer_radius_m=nextinner-10,kind='continuous arc street / city district'))
        # Contiguous courtyard neighbourhoods on each inward terrace, 96 x 120m envelopes.
        r=(rin+nextinner)/2
        for k in range(12):
            t=start+.35+(end-start-.7)*k/11
            x,y,_=point(r,t,zhi)
            fp=box(x-48,y-60,x+48,y+60).difference(box(x-22,y-30,x+22,y+30))
            prism('N1R1_courtyard_%d_%d'%(band,k),fp,zhi+8,zhi+68+(k%3)*12,'DISTRICT')
# Grand civic floor with a precisely modelled open hall, nested into the lower caldera.
block('N1R1_central_forum',-50,100,700,640,460,50,'PUBLIC_GROUND')
hall('N1R1_public_conservatory',-50,230,750,400,300,210)
block('N1R1_ground_public',150,-1600,-12,1000,650,12,'PUBLIC_GROUND')
# Four circulation spines: envelopes only; transfer details deliberately not claimed.
for k,t in enumerate([.25,1.3,2.5,3.7]):
    x,y,_=point(1840,t,0)
    block('N1R1_lift_'+str(k),x,y,0,70,80,2800,'TRANSIT_ENVELOPE')
save('N1R1',spaces)
print('C2-G4 N1 / N2 geometry written')
