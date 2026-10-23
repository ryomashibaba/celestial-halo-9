"""A2-G6 original mesh study. Metres. Blender 5.2. No external assets.
blender -b --factory-startup --python build.py -- compare|selected|render
All final pictures render a reimport of the submitted selected.glb.
"""
import bpy, math, json, sys, os, random
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
(R/'renders').mkdir(exist_ok=True)
(R/'comparison').mkdir(exist_ok=True)
random.seed(906)

def material(name,c,metal=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True
    bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bs.inputs['Base Color'].default_value=(*c,1);bs.inputs['Roughness'].default_value=.66;bs.inputs['Metallic'].default_value=metal
    return m

def mesh(name,v,f,mat):
    d=bpy.data.meshes.new(name);d.from_pydata(v,[],f);d.update()
    o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.data.materials.append(mat)
    return o

class Batch:
    def __init__(self,name,mat):self.name=name;self.mat=mat;self.v=[];self.f=[]
    def box(self,p,s,angle=0):
        x,y,z=p;a,b,c=[q/2 for q in s];n=len(self.v);co=math.cos(angle);si=math.sin(angle)
        # Glazing is an actual planar facade surface; no invisible 0.12m box backs.
        # Low-detail window surfaces are intentionally non-watertight, unlike solid walls.
        if min(s)<.2:
            if s[0]<.2:local=[(0,-b,-c),(0,b,-c),(0,b,c),(0,-b,c)]
            elif s[1]<.2:local=[(-a,0,-c),(a,0,-c),(a,0,c),(-a,0,c)]
            else:local=[(-a,-b,0),(a,-b,0),(a,b,0),(-a,b,0)]
            for dx,dy,dz in local:self.v.append((x+dx*co-dy*si,y+dx*si+dy*co,z+dz))
            self.f.append(tuple(n+i for i in range(4)));return
        for dz in [-c,c]:
            for dx,dy in [(-a,-b),(a,-b),(a,b),(-a,b)]:self.v.append((x+dx*co-dy*si,y+dx*si+dy*co,z+dz))
        self.f += [tuple(n+i for i in f) for f in [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]]
    def finish(self):return mesh(self.name,self.v,self.f,self.mat) if self.v else None

def cube(name,p,s,mat):
    b=Batch(name,mat);b.box(p,s);return b.finish()

def annular(name,c,r,width,a0,a1,z0,z1,mat,N=72):
    # A solid open curved urban ground, not a closed torus.
    v=[]
    for z in [z0,z1]:
        for rr in [r-width/2,r+width/2]:
            for i in range(N+1):
                a=a0+(a1-a0)*i/N;v.append((c[0]+rr*math.cos(a),c[1]+rr*math.sin(a),z))
    L=N+1;f=[]
    for i in range(N):
        f += [(i,i+1,L+i+1,L+i),(2*L+i,3*L+i,3*L+i+1,2*L+i+1),
              (i,2*L+i,2*L+i+1,i+1),(L+i,L+i+1,3*L+i+1,3*L+i)]
    f += [(0,L,3*L,2*L),(N,2*L+N,3*L+N,L+N)]
    return mesh(name,v,f,mat)

def ridge(name,c,r,width,angles,height,lean,mat,fold=False):
    # Lofted inhabited back: a changing crescent section with open ends.
    v=[];N=64;L=2*(N+1)
    levels=[0,.10,.22,.35,.47,.60,.72,.83,.92,1]
    for j,t in enumerate(levels):
        shiftx=lean[0]*t;shifty=lean[1]*t
        rr=r*(1-.32*t)+80*math.sin(t*math.pi)
        w=width*(1-.24*t)
        span=(angles[1]-angles[0])*(1-.30*t)
        mid=(angles[0]+angles[1])/2 + (.50*t if fold else -.15*t)
        for side in [-1,1]:
            for i in range(N+1):
                q=i/N;a=mid-span/2+span*q
                wr=w/2*(1+.12*math.cos(q*math.pi*4+t*2))
                rad=rr+side*wr
                if fold:
                    x=(q-.5)*r*2.3; y=350*math.sin(q*math.pi*2+t*1.6)+side*w/2
                    co=math.cos(mid);si=math.sin(mid);xx=x*co-y*si;yy=x*si+y*co
                else:xx=rad*math.cos(a);yy=rad*math.sin(a)
                # Crown is broad and uneven, not a needle.
                z=height*t-230*(t**5)*(1-math.sin(math.pi*q)**.4)
                v.append((c[0]+shiftx+xx,c[1]+shifty+yy,max(0,z)))
    f=[]
    for j in range(len(levels)-1):
        off=j*L;up=(j+1)*L
        for i in range(N):
            f.extend([(off+i,off+i+1,up+i+1,up+i),
                      (off+N+1+i,up+N+1+i,up+N+2+i,off+N+2+i)])
        f += [(off,up,up+N+1,off+N+1),(off+N,off+2*N+1,up+2*N+1,up+N)]
    for j,reverse in [(0,True),(len(levels)-1,False)]:
        off=j*L
        for i in range(N):
            ff=(off+i,off+N+1+i,off+N+2+i,off+i+1)
            f.append(tuple(reversed(ff)) if reverse else ff)
    return mesh(name,v,f,mat)

def palette():
    return {k:material(k,c) for k,c in {
     'ivory':(.68,.73,.70),'edge':(.28,.42,.44),'dark':(.075,.12,.155),
     'street':(.40,.49,.47),'ochre':(.64,.39,.17),'homes':(.68,.66,.56),
     'glass':(.10,.27,.32),'garden':(.17,.32,.25),'people':(.72,.28,.13),
     'context':(.15,.20,.23)}.items()}

RIDGES={
 'A':[
  {'c':(-650,350),'r':1400,'w':650,'a':(-2.1,1.35),'h':5530,'lean':(500,-150)},
  {'c':(700,600),'r':1150,'w':740,'a':(-.35,2.5),'h':4860,'lean':(-450,100)},
  {'c':(-250,-500),'r':1050,'w':620,'a':(-2.4,.1),'h':3710,'lean':(450,400)}],
 'B':[
  {'c':(-750,300),'r':1200,'w':620,'a':(-1.5,.5),'h':5500,'lean':(750,-500)},
  {'c':(600,650),'r':1100,'w':650,'a':(.3,2.3),'h':4880,'lean':(-700,-200)},
  {'c':(200,-700),'r':1000,'w':550,'a':(-2.9,-.9),'h':3900,'lean':(-300,700)}]}

def massing(key,m,terraces=True):
    obs=[];grounds=[]
    for idx,d in enumerate(RIDGES[key]):
        obs.append(ridge('URBAN_BACK_'+str(idx),d['c'],d['r'],d['w'],d['a'],d['h'],d['lean'],m['ivory'],key=='B'))
        if not terraces:continue
        for j,z in enumerate([680,1390,2110,2920,3730,4540,5150]):
            if z>d['h']-150:continue
            t=z/d['h'];c=(d['c'][0]+d['lean'][0]*t,d['c'][1]+d['lean'][1]*t)
            r=d['r']*(1-.32*t)+80*math.sin(t*math.pi)
            mid=sum(d['a'])/2+(-.15*t if key=='A' else .5*t);span=(d['a'][1]-d['a'][0])*(1-.30*t)
            if key=='A':
                # Inner and outer shores: distinct horizontal city streets.
                for side in [-1,1]:
                    rr=r+side*d['w']*(1-.24*t)*.48
                    ob=annular('CITY_GROUND_%d_%d_%d'%(idx,j,side),c,rr,210,mid-span*.47,mid+span*.47,z-105,z,m['edge'])
                    obs.append(ob);grounds.append({'ridge':idx,'c':c,'r':rr,'a0':mid-span*.47,'a1':mid+span*.47,'z':z,'width':210})
            else:
                # Bent civic plates along a folded urban face, markedly unlike A's bays.
                for side in [-1,1]:
                    n=18;vv=[]
                    for zz in [z-100,z]:
                        for s in [-1,1]:
                            for i in range(n+1):
                                q=.06+.88*i/n;x=(q-.5)*d['r']*2.3;y=350*math.sin(q*math.pi*2+t*1.6)+side*d['w']/2+s*100
                                co=math.cos(mid);si=math.sin(mid);vv.append((c[0]+x*co-y*si,c[1]+x*si+y*co,zz))
                    L=n+1;ff=[]
                    for i in range(n):ff.extend([(i,i+1,L+i+1,L+i),(2*L+i,3*L+i,3*L+i+1,2*L+i+1),(i,2*L+i,2*L+i+1,i+1),(L+i,L+i+1,3*L+i+1,3*L+i)])
                    ff += [(0,L,3*L,2*L),(n,2*L+n,3*L+n,L+n)]
                    obs.append(mesh('FOLDED_CITY_GROUND_%d_%d_%d'%(idx,j,side),vv,ff,m['edge']))
    return obs,grounds

def setup(preview=False):
    sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
    sc.render.engine='CYCLES';sc.cycles.samples=8 if preview else 16;sc.cycles.use_denoising=True
    sc.render.threads_mode='FIXED';sc.render.threads=8
    sc.render.resolution_x=1200 if preview else 1600;sc.render.resolution_y=1000 if preview else 1350;sc.render.resolution_percentage=100
    sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='AgX'
    sc.world=bpy.data.worlds.new('study sky');sc.world.use_nodes=True
    bg=next(n for n in sc.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.38,.49,.63,1);bg.inputs['Strength'].default_value=.7
    bpy.ops.object.light_add(type='SUN');o=bpy.context.object;o.rotation_euler=(.55,-.5,-.45);o.data.energy=3.2;o.data.angle=.09
    if not preview:
        # Diagnostic soft fill inside the public hall; not a designed building lighting system.
        for x,y,z,power,size in [(0,-1460,2185,8000000,360),(0,-1100,2185,6500000,250)]:
            bpy.ops.object.light_add(type='AREA',location=(x,y,z));a=bpy.context.object;a.name='DIAGNOSTIC_HALL_FILL';a.data.energy=power;a.data.shape='DISK';a.data.size=size
    return sc

def camera(name,eye,target,span=None,lens=28):
    bpy.ops.object.camera_add(location=eye);o=bpy.context.object;o.name='CAM_'+name
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.clip_end=80000;o.data.clip_start=.15
    o.data.sensor_width=36;o.data.lens=lens
    if span:o.data.type='ORTHO';o.data.ortho_scale=span
    return o

CAMS={
 '01_city':((14500,-18000,10000),(0,0,2200),13500),
 '02_oblique':((10000,-14000,8500),(0,100,2700),8100),
 '03_front':((0,-16000,2700),(0,0,2700),7600),
 '04_side':((16000,0,2700),(0,0,2700),7600),
 '05_back':((0,16000,2700),(0,0,2700),7600),
 '06_high':((6500,-4500,11500),(0,0,3000),7500)}

def render_to(path,eye,target,span=None,lens=28):
    sc=bpy.context.scene
    sc.view_settings.exposure=-2 if path.stem in ['07_human','08_public_hall','11_living_street'] else 0
    sc.camera=camera(path.stem,eye,target,span,lens);sc.render.filepath=str(path);bpy.ops.render.render(write_still=True)

def context(m):
    col=bpy.data.collections.new('CONCEPT_CONTEXT_10KM_NOT_W0');bpy.context.scene.collection.children.link(col)
    old=set(bpy.context.scene.objects)
    cube('CONTEXT_10KM_GROUND',(0,0,-70),(10000,10000,100),m['context'])
    # Six abstract surrounding quarters, NO W0 / M204 / M207 registration.
    for k,a in enumerate([.2,1.2,2.2,3.2,4.2,5.2]):
        x,y=4000*math.cos(a),4000*math.sin(a)
        b=Batch('CONTEXT_QUARTER_%d_UNREGISTERED'%(k+1),m['street'])
        for i in range(6):
            for j in range(4):b.box((x+(i-2.5)*90,y+(j-1.5)*90,60+12*((i+j)%3)),(55,58,120+24*((i+j)%3)))
        b.finish()
    for ob in set(bpy.context.scene.objects)-old:
        for c in list(ob.users_collection):c.objects.unlink(ob)
        col.objects.link(ob)
    return col

def write_json(name,data):(R/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def compare():
    record={}
    for key in ['A','B']:
        bpy.ops.wm.read_factory_settings(use_empty=True);m=palette();obs,_=massing(key,m);setup(True);context(m)
        for view in ['02_oblique','03_front','05_back']:render_to(R/'comparison'/(key+'_'+view+'.png'),*CAMS[view])
        for o in bpy.context.scene.objects:o.select_set(o in obs)
        bpy.ops.export_scene.gltf(filepath=str(R/'comparison'/(key+'_massing.glb')),export_format='GLB',use_selection=True)
        record[key]={'name':'連湾交庭' if key=='A' else '折面交庭','role':'original massing comparison; no residential detail','same_cameras':True}
    write_json('comparison-record.json',{'models':record,'cameras':CAMS,'units':'m','art_acceptance':False})

def courtyard(batch,glass,p,s,angle=0,detail=False):
    """Four real wings around an open court; split south wing has an entrance."""
    x,y,z=p;w,d,h=s;wing=min(10,w*.21,d*.21);co=math.cos(angle);si=math.sin(angle)
    def put(b,dx,dy,dz,ww,dd,hh):b.box((x+dx*co-dy*si,y+dx*si+dy*co,z+dz),(ww,dd,hh),angle)
    put(batch,0,d/2-wing/2,h/2,w,wing,h)
    for side in [-1,1]:
        put(batch,side*(w/2-wing/2),0,h/2,wing,d-wing,h)
        # Four-metre gap is the courtyard's entrance; never a sealed colour marker.
        ww=(w-4)/2;put(batch,side*(2+ww/2),-d/2+wing/2,h/2,ww,wing,h)
    for level in (range(1,max(2,int(h/4))) if detail else [1,max(2,int(h/4)-1)]):
        zz=level*4
        put(glass,0,d/2+.06,zz,w-3,.12,1.6)
        for side in [-1,1]:put(glass,side*(w/2+.06),0,zz,.12,d-3,1.6)
        # Court-facing gallery parapet / slab: actual geometry, not a label.
        if detail:put(batch,0,d/2-wing-1,zz-.6,w-2*wing,2,.35)

def fabric(m):
    """Revision C replaces the failed solid lofts; no A/B wall is retained."""
    grounds=[];records=[]
    homes=Batch('URBAN_COURTYARD_WINGS_LOW_DETAIL',m['homes']);glazing=Batch('URBAN_WINDOW_STRIPS',m['glass'])
    supports=Batch('INHABITED_BACK_ROOMS_AND_CIVIC_PIERS',m['ivory'])
    # Each tier is urban ground + open court district, not an ornament on a wall.
    zs=[0,260,520,820,1100,1390,1710,2110,2450,2790,3130,3550,3900,4300,4700,5100,5450]
    for idx,d in enumerate(RIDGES['A']):
        prev=None
        for j,z in enumerate(zs):
            if z>d['h']-50:continue
            t=z/d['h'];cc=(d['c'][0]+d['lean'][0]*t,d['c'][1]+d['lean'][1]*t)
            rr=d['r']*(1-.32*t)+80*math.sin(math.pi*t)
            mid=sum(d['a'])/2-.15*t;span=(d['a'][1]-d['a'][0])*(1-.30*t)
            # Wider living ground, discontinuous arcs with unequal ends.
            a0=mid-span*.48;a1=mid+span*.48;ww=d['w']*(1-.20*t)+220
            if z==2110:
                # The focus ground replaces this part of the macro floor; do not leave
                # coplanar overlapping floors that produce a black self-shadow in renders.
                for seg in range(24):
                    aa=a0+(a1-a0)*seg/24;ab=a0+(a1-a0)*(seg+1)/24
                    corners=[(cc[0]+rad*math.cos(a),cc[1]+rad*math.sin(a)) for rad in [rr-ww/2,rr+ww/2] for a in [aa,(aa+ab)/2,ab]]
                    xs=[p[0] for p in corners];ys=[p[1] for p in corners]
                    overlap=not(max(xs)<-960 or min(xs)>820 or max(ys)<-1860 or min(ys)>-560)
                    if not overlap:annular('FABRIC_GROUND_%02d_%02d_SEG_%02d'%(idx,j,seg),cc,rr,ww,aa,ab,z-110,z,m['edge'],N=4)
            else:annular('FABRIC_GROUND_%02d_%02d'%(idx,j),cc,rr,ww,a0,a1,max(0,z-110),max(90,z),m['edge'])
            floor=max(90,z);grounds.append({'c':cc,'r':rr,'w':ww,'a0':a0,'a1':a1,'z':floor,'ridge':idx,'tier':j})
            # Civic rooms occupy the back 160m of each shared urban section.
            if prev is not None:
                dz=floor-prev['z'];N=12
                for n in range(N):
                    a=a0+(a1-a0)*(n+.5)/N
                    x=cc[0]+(rr+ww*.34)*math.cos(a);y=cc[1]+(rr+ww*.34)*math.sin(a)
                    # Occupied side rooms support public roof; large unbuilt bays remain between.
                    # Reserve the actual shared hall/plaza volume, not just its houses.
                    # Otherwise macro room piers occupied the public approach in the first eye view.
                    conflicts_focus=(prev['z']<2300 and floor>2110 and -1040<x<920 and -1940<y<-480)
                    if (n+j+idx)%4!=0 and not conflicts_focus:supports.box((x,y,prev['z']+dz/2),(90,125,dz),a)
            count=0
            for n in range(18):
                a=a0+(a1-a0)*(n+.5)/18
                # Large sections are kept open for public gardens and views.
                if (n+2*j+idx)%7 in [0,1]:continue
                for lane in [-1,1]:
                    rad=rr+lane*ww*.20
                    x=cc[0]+rad*math.cos(a);y=cc[1]+rad*math.sin(a)
                    # Reserved focus district has its own geometrically resolved houses.
                    if 1950<floor<2350 and -1000<x<1000 and -1950<y<-500:continue
                    courtyard(homes,glazing,(x,y,floor),(62+10*((n+j)%3),65,32+8*(n%4)),a+math.pi/2)
                    count+=1
            # Broad high-city civic buildings are usable-volume proxies, not 100m house markers.
            a=a0+(a1-a0)*.52;x=cc[0]+rr*math.cos(a);y=cc[1]+rr*math.sin(a)
            courtyard(homes,glazing,(x,y,floor),(150,180,64),a+math.pi/2)
            records.append({'ridge':idx,'floor_z_m':floor,'courtyard_blocks':count,'civic_court_block':1,'scope':'open courts, split entrances and window-strip meshes; interiors not fully fitted'})
            prev={'z':floor}
    homes.finish();glazing.finish();supports.finish()
    return grounds,records

def focus_pair(m):
    """Lower street 2110m / upper street 2206m share a civic roof mesh."""
    z=2110;upper=2206
    floor=cube('LOWER_DISTRICT_GROUND',(-70,-1210,z-45),(1700,1220,90),m['edge'])
    # A tapering inhabited civic root, not an invisible floating marker support.
    # Its upper floor is continuous with the curved mid-city ground.
    v=[(-800,-1700,1390),(650,-1700,1390),(650,-650,1390),(-800,-650,1390),
       (-920,-1820,2065),(780,-1820,2065),(780,-600,2065),(-920,-600,2065)]
    mesh('FOCUS_SHARED_INHABITED_ROOT',v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m['ivory'])
    # Actual civic building: open south foyer, side rooms, gallery and public roof.
    # Roof is literally the U district's supporting ground, a single shared mesh.
    cube('SHARED_ROOF_EQUALS_UPPER_CITY_GROUND',(0,-1110,2200),(700,480,12),m['street'])
    hall=Batch('CIVIC_HALL_PIERS_SIDE_ROOMS',m['ivory']);win=Batch('CIVIC_ROOM_WINDOWS',m['glass'])
    for x in [-300,-180,-60,60,180,300]:
        for y in [-1320,-1100,-900]:hall.box((x,y,z+42),(7,7,84))
    # Rear library / clinic room wings. Their side streets remain independent.
    for x in [-280,280]:
        hall.box((x,-1110,z+37),(92,350,74))
        for zz in [2116,2124,2132,2140,2148,2156,2164,2172]:win.box((x,-1285.1,zz),(76,.15,2.6))
    # Public middle gallery, open central court and overlook from upper city.
    for x in [-235,235]:hall.box((x,-1110,2160),(150,460,4))
    hall.box((0,-910,2160),(320,70,4));hall.finish();win.finish()
    # Upper school and 14 court housing blocks have open courtyards and entrances.
    h=Batch('FOCUS_LOWER_RESIDENTIAL_COURTS',m['homes']);w=Batch('FOCUS_RESIDENTIAL_WINDOWS',m['glass'])
    house_anchors=[]
    for side in [-1,1]:
        for i in range(4):
            for j in range(3):
                x=side*(440+i*100);y=-1510+j*210
                courtyard(h,w,(x,y,z),(70,110,24+8*(i%3)),0,True)
                house_anchors.append({'id':'L_%d_%d_%d'%(side,i,j),'xyz':[x,y,z],'ground':'LOWER_DISTRICT_GROUND'})
    h.finish()
    hu=Batch('FOCUS_UPPER_RESIDENTIAL_COURTS',m['homes'])
    for x in [-250,-135,135,250]:
        for y in [-1230,-1030]:
            courtyard(hu,w,(x,y,upper),(70,90,24),0,True)
            house_anchors.append({'id':'U_%d_%d'%(x,y),'xyz':[x,y,upper],'ground':'SHARED_ROOF_EQUALS_UPPER_CITY_GROUND'})
    hu.finish();w.finish()
    school=Batch('UPPER_SCHOOL_CLASSROOM_WINGS',m['ivory']);sg=Batch('SCHOOL_WINDOW_OPENINGS_GLAZING',m['glass'])
    courtyard(school,sg,(0,-925,upper),(170,100,20),0,True);school.finish();sg.finish()
    # Market: open booths, actual canopy roofs and counters along the lower street.
    stalls=Batch('LOWER_MARKET_STALLS_COUNTERS_CANOPIES',m['ochre'])
    for x in [-180,-135,-90,90,135,180]:
        y=-1410
        for dx in [-3,3]:stalls.box((x+dx,y,z+1.8),(.22,5,3.6))
        stalls.box((x,y,z+3.7),(7.3,5.5,.3));stalls.box((x,y-2,z+.8),(6,.8,1.6))
    # Seats, planters, sheltered daily-life street; no population estimate.
    garden=Batch('FOCUS_PLANTERS_AND_SEATS',m['garden'])
    for x in [-300,-220,-70,70,220,300]:
        garden.box((x,-1470,z+.7),(9,4,1.4));garden.box((x,-1180,upper+.7),(8,6,1.4))
    garden.finish();stalls.finish()
    # Walking stairs: 16 flights x 40 risers x .15 = 96m, .30m treads.
    st=Batch('PUBLIC_STAIRS_640_TREADS_AND_LANDINGS',m['ochre'])
    x0=370;y0=-1260;W=4.5;steps=[]
    for f in range(16):
        bay=f%2;xx=x0+bay*5.3;zz=z+f*6
        for k in range(40):
            yy=y0+(k+.5)*.30 if bay==0 else y0+12-(k+.5)*.30
            top=zz+(k+1)*.15
            st.box((xx,yy,top-.12),(W,.30,.24));steps.append([xx,yy,top])
        # Landing bridges the parallel flights; next flight begins on its top.
        end=y0+12 if bay==0 else y0
        st.box((x0+2.65,end,zz+6-.15),(10,3,.30))
    st.finish()
    # Connector pavements join both ends of staircase to actual public grounds.
    cube('UPPER_STAIR_TO_SCHOOL_WALK',(357,-1260,upper-.5),(42,8,1),m['street'])
    cube('LOWER_STAIR_APPROACH',(376,-1290,z-.5),(20,70,1),m['street'])
    # Geometric transit shafts + platform thresholds; no simulated functioning lift.
    lifts=Batch('TWIN_PUBLIC_LIFT_SHAFTS',m['dark']);lg=Batch('LIFT_CABINS_AND_LOBBIES',m['ochre'])
    for x in [330,348]:
        lifts.box((x,-1290,(upper+90)/2),(8,10,upper-90))
        for zz in [90,1390,z,upper,3130,4300,5100]:
            if zz<=upper:
                lg.box((x,-1290,zz+2),(7,8,4));lg.box((x,-1300,zz-.5),(16,12,1))
    lifts.finish();lg.finish()
    # Ground arrival pavement and the public interface to vertical transport.
    cube('GROUND_ARRIVAL_STREET',(300,-1550,89),(200,600,2),m['street'])
    people=Batch('SCALE_PEOPLE_1P7M_NO_POPULATION_CLAIM',m['people'])
    for x,y in [(-5,-1518),(9,-1510),(15,-1490),(-20,-1450),(80,-1420),(-110,-1410),(130,-1415)]:
        people.box((x,y,z+.65),(.45,.30,1.3));people.box((x,y,z+1.52),(.25,.25,.3))
    people.finish()
    return {'lower_street_z_m':z,'upper_street_z_m':upper,'shared_roof_object':'SHARED_ROOF_EQUALS_UPPER_CITY_GROUND',
      'shared_roof_top_z_m':upper,'hall_clear_height_to_gallery_m':48,'roof_thickness_m':12,
      'lower_courtyard_blocks':24,'upper_courtyard_blocks':8,'upper_school_court':1,
      'house_floor_probes':house_anchors,'stairs':{'flights':16,'risers_per_flight':40,'rise_m':.15,'tread_m':.30,'width_m':W,'total_rise_m':96,'tread_tops_m':steps},
      'limits':['Room wings are low-detail volumes with visible windows, not room-by-room dwelling plans','Lift equipment is static geometry, not operational','No code-compliance, crowd flow, services or structural certification']}

def select_build(preview=False):
    bpy.ops.wm.read_factory_settings(use_empty=True);m=palette()
    grounds,districts=fabric(m)
    # The pair is built as part of the selected model, not pasted over a render.
    pair=focus_pair(m)
    architecture=[o for o in bpy.context.scene.objects if o.type=='MESH']
    for o in architecture:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(R/'selected.glb'),export_format='GLB',use_selection=True,export_yup=True)
    before=bounds(architecture)
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(R/'selected.glb'))
    imported=[o for o in bpy.context.scene.objects if o.type=='MESH'];after=bounds(imported)
    col=bpy.data.collections.new('SELECTED_C_ARCHITECTURE');bpy.context.scene.collection.children.link(col)
    for o in imported:
        for c in list(o.users_collection):c.objects.unlink(o)
        col.objects.link(o)
    ctx=context(m);setup(preview)
    audit={'selected':'C / 多院連湾','baseline':'A2-G5 @ b74e452f664adc8ae505846509d978e324fc6e1b',
     'source_3d':'new generated mesh; G4 meshes not reused','render_source':'selected.glb reimport',
     'units':'metres','bounds_m':after,'dimensions_m':dict(zip(['width','depth','height'],[after[1][i]-after[0][i] for i in range(3)])),
     'roundtrip_max_bound_delta_m':max(abs(before[j][i]-after[j][i]) for j in range(2) for i in range(3)),
     'mesh_objects':len(imported),'districts':districts,'focus_pair':pair,'cameras':CAMS,
     'context':'separate collection, 10km conceptual ground + six unregistered scale quarters; NOT W0',
     'formal_art_acceptance':False,'stage':'BLOCKOUT_3D'}
    write_json('geometry-record.json',audit)
    # Preview is a new main-mass iteration, before deciding whether to retain it.
    if preview:
        render_to(R/'comparison'/'C_02_oblique.png',*CAMS['02_oblique'])
        render_to(R/'comparison'/'C_05_back.png',*CAMS['05_back'])
    else:
        for view,args in CAMS.items():render_to(R/'renders'/(view+'.png'),*args)
        sc=bpy.context.scene;sc.render.resolution_x=1900;sc.render.resolution_y=1400
        human={'07_human':((0,-1535,2111.65),(0,-1100,2165),None,23),
               '08_public_hall':((0,-1300,2111.65),(20,-990,2140),None,23),
               '09_pair_aerial':((1100,-2400,2900),(0,-1190,2180),1550,28),
               '11_living_street':((0,-1535,2111.65),(-440,-1340,2145),None,26)}
        for name,args in human.items():render_to(R/'renders'/(name+'.png'),*args)
        audit['human_cameras']=human
        # Destructive section on COPY geometry only; source/imported data remain unchanged.
        ctx.hide_render=True
        for o in imported:o.hide_render=True
        section_col=bpy.data.collections.new('SECTION_COPY_NOT_EXPORTED');bpy.context.scene.collection.children.link(section_col)
        import bmesh
        for source in imported:
            if not any(s in source.name for s in ['FOCUS','LOWER_DISTRICT_GROUND','CIVIC_HALL','SHARED_ROOF','SCHOOL','PUBLIC_STAIRS','LOWER_MARKET','UPPER_STAIR','LOWER_STAIR','LIFT']):continue
            du=source.copy();du.data=source.data.copy();section_col.objects.link(du);du.hide_render=False
            bm=bmesh.new();bm.from_mesh(du.data)
            # World y=-1110 section. glTF reimport objects may have non-identity transforms.
            inv=du.matrix_world.inverted();pt=inv@Vector((0,-1110,0));normal=(du.matrix_world.to_3x3().transposed()@Vector((0,-1,0))).normalized()
            bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.0001,plane_co=pt,plane_no=normal,clear_outer=True,clear_inner=False)
            bm.to_mesh(du.data);bm.free()
        render_to(R/'renders'/'10_pair_section.png',(1150,-2400,2510),(0,-1110,2165),1550)
        for o in section_col.objects:o.hide_render=True
        for o in imported:o.hide_render=False
        ctx.hide_render=False
        write_json('geometry-record.json',audit)
    bpy.ops.wm.save_as_mainfile(filepath=str(R/'selected.blend'),compress=True)

def bounds(obs):
    vv=[o.matrix_world@p.co for o in obs for p in o.data.vertices]
    return [[min(v[i] for v in vv) for i in range(3)],[max(v[i] for v in vv) for i in range(3)]]

if __name__=='__main__':
    mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'compare'
    if mode=='compare':compare()
    elif mode=='revision':select_build(True)
    elif mode=='selected':select_build(False)
