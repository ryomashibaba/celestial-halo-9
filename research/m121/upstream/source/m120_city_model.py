#!/usr/bin/env python3
"""M120 giant urban architecture study; inherits immutable M119/real M117 evidence.

No Minecraft world API, no level.dat access, no edits. Deliberate *replacement*
concept volumes; existing protected voxels and exterior site boundaries unverified.
This is a visual research scaffold, not an actual traversable city or build plan.
"""
from __future__ import annotations
import sys, json, math, copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from m119_city_model import produce,SITES,HERO,CIVIC,ATLAS,box,section,sail,beam,mesh
ROOT=Path(__file__).resolve().parents[1]

# EXTRA material colors are shared by graphical renderer; original M119 untouched.
M120_MATERIALS={'obsidian':'#192a35','ivory':'#f3e8ce','opal':'#bad8d5','copper':'#b7865d',
                'lagoon':'#57a2a5','forest':'#527967','shadow':'#223b48'}

def tapered_buttress(name,a,b,width0,width1,material,site):
    # A substantial sloping rib, not a repetitive slim pole.
    (ax,az,ay),(bx,bz,by)=a,b
    vx=bz-az;vz=-(bx-ax);L=math.hypot(vx,vz)
    if L<.1: vx,vz,L=1,0,1
    dx,dz=vx/L,vz/L
    v=[]
    for (x,z,y,w) in ((ax,az,ay,width0),(bx,bz,by,width1)):
        for zsign,ysign in ((1,-1),(-1,-1),(-1,1),(1,1)):
            v.append([x+dx*zsign*w/2,z+dz*zsign*w/2,y+ysign*w*.30])
    f=[[0,1,2,3],[4,7,6,5],[0,4,5,1],[1,5,6,2],[2,6,7,3],[3,7,4,0]]
    return mesh(name,v,f,material,site,'sculptural_support_UNCERTIFIED')

def curved_arc(name,cx,cz,cy,rx,rz,yrise,angle_start,angle_end,n,width,mat,site):
    result=[]
    def p(t):
        return (cx+rx*math.cos(t),cz+rz*math.sin(t),cy+yrise*math.sin(math.pi*(t-angle_start)/(angle_end-angle_start)))
    for i in range(n):
        a=angle_start+(angle_end-angle_start)*i/n
        b=angle_start+(angle_end-angle_start)*(i+1)/n
        result.append(beam(f'{name}_{i:02d}',p(a),p(b),width,width*.42,mat,site,'monumental_arc_UNCERTIFIED'))
    return result

def segment_distance(a,b,pt):
    x,z=a[0],a[1]; dx=b[0]-x;dz=b[1]-z;ll=dx*dx+dz*dz
    t=max(0,min(1,((pt[0]-x)*dx+(pt[1]-z)*dz)/ll)) if ll else 0
    return math.hypot(pt[0]-(x+t*dx),pt[1]-(z+t*dz))

def make_route():
    """One mathematically continuous centerline, NOT physical accessibility."""
    north_t=math.acos((3574-3703.5)/575)
    north_x=3703.5+575*math.cos(north_t)
    north_z=-2184.5+319*math.sin(north_t)
    north_y=-1650+21*math.sin(2.5*north_t)+7
    pts=[
      ('SB13_PROXY_APPROACH',(4068.,-2348.,-1787.),'proposed_portal_not_true_3x4_anchor'),
      ('SB13_EXTERIOR_LIFT_BASE',(4056.,-2348.,-1787.),'low_approach_unverified'),
      ('SB13_EXTERIOR_LIFT_TOP',(4056.,-2348.,-1695.),'elevator_UNBUILT'),
      ('SB09_OUTER_GATE',(3830.,-2348.,-1695.),'skybridge_UNBUILT'),
      ('SB10_TRANSIT_MEZZANINE',(3830.,-2246.,-1695.),'mezzanine_UNBUILT'),
      ('CENTRAL_SKY_COURT',(3703.5,-2184.5,-1695.),'civic_gallery_UNBUILT'),
      ('SB07_PUBLIC_FORUM',(3574.,-2124.,-1695.),'forum_UNBUILT'),
      ('SB07_SECOND_LIFT_TOP',(3574.,-2124.,north_y),'elevator_UNBUILT'),
      ('SB08_TWIN_VAULTS',(3574.,-2022.,north_y),'hero_gallery_UNBUILT'),
      ('INNER_ORBITAL_TERRACE',(north_x,north_z,north_y),'ring_sample_docking_NOT_CERTIFIED'),
    ]
    segments=[]
    for i in range(len(pts)-1):
        a=pts[i][1];b=pts[i+1][1]
        length=math.dist(a,b)
        lift=abs(a[0]-b[0])<.001 and abs(a[1]-b[1])<.001
        segments.append({'id':f'S{i:02}', 'from':pts[i][0],'to':pts[i+1][0],
                         'start':a,'end':b,'type':'VERTICAL_LIFT_UNBUILT' if lift else 'SKYWAY_UNBUILT',
                         'length_m':round(length,2),'centerline_continuous':True,
                         'headroom_tested':False,'stairs_or_elevator_operational':False,
                         'collision_cleared':False,'connected_to_real_existing_portal':False})
    return {'research_path_name':'SB13_to_Civic_to_SB08_to_Orbital',
            'status':'CONTINUOUS_MATH_CENTERLINE_ONLY_NOT_TRAVERSABLE',
            'notes':['Actual SB13 protected 3x4 entry location not registered','No authenticated in-world ground/door connection',
                     'All bridges/shaft construction proposals only','Upper orbital joint based on M119 sampled ring param, not exact mesh snap',
                     'Road/park, protected void and Freeze408 voxel clearance NOT verified'],
            'stations':[{'name':n,'xyz':list(p),'claim':kind} for n,p,kind in pts],
            'segments':segments,'world_writes':0,'publicly_traversable':False}

def tile_broadphase(path):
    """Conservative site-tile AABB risk, never exact block or preservation scan."""
    old_tiles=[(s['site'],t) for s in ATLAS['sites'] for t in s['tiles']]
    for sg in path['segments']:
        a=sg['start'];b=sg['end'];yl=min(a[2],b[2])-7;yh=max(a[2],b[2])+7
        hits=set()
        for site,t in old_tiles:
            # Exclude tile if definitely separated in Y (8x8 bin extents only)
            if t['max_y']<yl or t['min_y']>yh: continue
            if segment_distance(a,b,(t['x']+4,t['z']+4))<=13.7:
                hits.add((site,t['x'],t['z']))
        sg['observed_material_tile_AABB_risks']=len(hits)
        sg['observed_material_tile_AABB_sample']=[{'site':sid,'x':x,'z':z} for sid,x,z in sorted(hits)[:12]]
        # 0 != verified: atlas excludes some materials and all invisible protected air volumes.
        sg['zero_tile_risk_is_not_collision_clearance']=True
    return path

def produce_m120():
    base=produce('B_FRACTURED_SKY_TERRACES')
    model=copy.deepcopy(base)
    model['phase']='M120'
    model['variant']='B_ARCHITECTURAL_SPINE_REVISION'
    model['original_M119_mesh_count']=len(base['meshes'])
    model['model_reference']='M119 B FRACTURED SKY TERRACES, UNMODIFIED inherited proposal'
    model['all_new_geometry_requires_exterior_protected_classification']=True
    model['new_meshes_start_index']=len(base['meshes'])
    m=[]
    # Extra monumental architecture, each HERO has its own movement vocabulary.
    for sid in ('SB05','SB08','SB09','SB12'):
        s=SITES[sid];cx,cz=s['center'];lo=s['observed_y_min']+5;top=s['observed_y_max']
        x0,z0,x1,z1=s['tile_box']
        # twin wraparound podiums, dark at old-building-root and pale stepped upper deck
        m.append(section(f'M120_{sid}_DARK_PODIUM_CRADLE',cx,cz,lo+4,(x1-x0)*.86,(z1-z0)*.89,27,'obsidian',sid,.94))
        m.append(section(f'M120_{sid}_IVORY_APRON',cx,cz,lo+34,(x1-x0)*.78,(z1-z0)*.77,11,'ivory',sid,.84))
        # Floating pavilion in interior offset, no 'entry' claim
        m.append(section(f'M120_{sid}_OBSERVATION_EYRIE',cx,cz,top+19,48,42,37,'opal',sid,.60))
        for sign in (-1,1):
            z_start=cz+sign*(z1-z0)*.36
            m.append(tapered_buttress(f'M120_{sid}_FOUNDATION_WING_{sign}',
              (cx+sign*58,z_start,lo-4),(cx+sign*33,cz+sign*24,top+64),27,8,'shadow',sid))
    # De-box HERO4 signature canopies, dramatically different each.
    sx,sz=SITES['SB05']['center'];yy=SITES['SB05']['observed_y_max']
    for i,(theta,height) in enumerate([(-.7,58),(-.36,96),(0,128),(.31,101),(.66,77)]):
        m.append(sail(f'M120_SB05_SWEPT_ASYMMETRIC_CANOPY_{i}',
          [(sx-74+29*i,sz-38,yy+8),(sx-52+29*i,sz+50,yy+31),(sx+math.sin(theta)*78,sz+15,yy+height)],5,
          'ivory' if i%2==0 else 'opal','SB05'))
    cx,cz=SITES['SB08']['center'];y=SITES['SB08']['observed_y_min']+23
    # 2 tapered giant contrasting longitudinal arches over an open cathedral void.
    for q,xc in enumerate((cx-63,cx+61)):
        m+=curved_arc(f'M120_SB08_LONGITUDINAL_VAULT_{q}',xc,cz,y,52,61,150,math.pi,2*math.pi,16,14,
                       'ivory' if q==0 else 'opal','SB08')
    cx,cz=SITES['SB09']['center'];top=SITES['SB09']['observed_y_max']
    # Layered gate necks flank protected void, without claiming actual clearance
    for q,sx in enumerate((-1,1)):
        m.append(tapered_buttress(f'M120_SB09_GATE_SPLAY_{q}',
          (cx+sx*104,cz+55,top-76),(cx+sx*66,cz-13,top+108),34,9,'ivory','SB09'))
        m.append(sail(f'M120_SB09_AERIAL_GATE_FLAG_{q}',[(cx+sx*76,cz-44,top+108),
           (cx+sx*104,cz+36,top+66),(cx+sx*41,cz-8,top+160)],4,'opal','SB09'))
    cx,cz=SITES['SB12']['center'];top=SITES['SB12']['observed_y_max']
    for q in range(6):
        rad=math.pi*q/5
        m.append(sail(f'M120_SB12_MOUNTAIN_FAN_{q}',
          [(cx-68+q*22,cz-28,top+8),(cx-61+q*22,cz+42,top+16),
           (cx+(q-2.5)*17,cz-16,top+64+41*math.sin(rad))],4,
          'forest' if q in (1,4) else 'ivory','SB12'))
    # Civic neighborhood eight monumental anchored arch ribs with genuinely different span.
    ccx,ccz=3703.5,-2184.5
    for j,(angle,rad,height) in enumerate([(math.pi*.10,181,96),(.45*math.pi,205,121),(.87*math.pi,161,71),
            (1.23*math.pi,210,119),(1.62*math.pi,225,103),(1.93*math.pi,177,77)]):
        xx=ccx+rad*math.cos(angle);zz=ccz+rad*.64*math.sin(angle)
        foot=(xx,zz,-1824)
        tip=(ccx+rad*.65*math.cos(angle),ccz+rad*.45*math.sin(angle),-1650+height*.28)
        m.append(tapered_buttress(f'M120_CIVIC_DEEP_DIAGONAL_BUTTRESS_{j}',foot,tip,29,8,'obsidian','CIVIC_CORE'))
        m.append(tapered_buttress(f'M120_CIVIC_LIGHT_RIB_{j}',(xx+9,zz,-1784),
                     (tip[0]+4,tip[1],tip[2]+18),9,3,'copper','CIVIC_CORE'))
    # Add expansive monumental flight of civic terraces with different geometry, ample void between halves.
    for i,(dx,dz,w,l,h) in enumerate([(-85,-65,112,55,-1722),(95,54,138,67,-1708),(-30,124,175,42,-1648)]):
        cx=ccx+dx;cz=ccz+dz
        m.append(section(f'M120_CIVIC_HEAVY_SPINE_TERRACE_{i}',cx,cz,h-13,w,l,17,'obsidian','CIVIC_CORE',.80))
        m.append(section(f'M120_CIVIC_BRIGHT_HANGING_COURT_{i}',cx,cz,h+5,w*.91,l*.84,9,'ivory','CIVIC_CORE',.93))
        m.append(box(f'M120_CIVIC_SKYGARDEN_{i}',cx-w*.38,cz-l*.29,h+14,cx+w*.38,cz+l*.29,h+19,'forest','CIVIC_CORE','SKY_GARDEN_UNAPPROVED'))
    # Strategic 8 architecturally distinct outer dark anchors, not 20 repeated slim pylons.
    for i,(deg,basewidth) in enumerate([(6,72),(40,63),(81,88),(135,55),(180,77),(235,68),(285,57),(333,91)]):
        ang=math.radians(deg);x=3703.5+650*math.cos(ang);z=-2184.5+369*math.sin(ang)
        h=-1612+23*math.sin(ang*2)
        m.append(tapered_buttress(f'M120_MEGAFRAME_RADIAL_CRADLE_{i}',
           (x-22,z-25,-1854),(x,z,h+26),basewidth,14,'obsidian','MACRO'))
        m.append(tapered_buttress(f'M120_MEGAFRAME_REAR_SWEEP_{i}',
           (x+25,z+31,-1816),(x,z,h+25),basewidth*.48,8,'opal','MACRO'))
        m.append(section(f'M120_MEGAFRAME_BEACON_{i}',x,z,h+13,24,29,22,'copper','MACRO',.28))
    # Coherent centerline route. Separately show prospective deck slabs so it reads in perspective.
    route=tile_broadphase(make_route())
    for segment in route['segments']:
        a=segment['start'];b=segment['end']
        if segment['type']=='VERTICAL_LIFT_UNBUILT':
            x,z=a[0],a[1]
            m.append(box(f'M120_{segment["id"]}_DARK_LIFT_SHAFT',x-8,z-8,min(a[2],b[2]),x+8,z+8,max(a[2],b[2]),'obsidian','PUBLIC_ROUTE','ELEVATOR_NONFUNCTIONAL'))
            m.append(box(f'M120_{segment["id"]}_LIGHT_LIFT_FASCIA',x-2,z-9,min(a[2],b[2]),x+2,z-7,max(a[2],b[2]),'opal','PUBLIC_ROUTE','LIFT_FASCIA'))
        else:
            m.append(beam(f'M120_{segment["id"]}_SKY_PROMENADE_UNBUILT',a,b,15,5,'ivory','PUBLIC_ROUTE','NOT_CERTIFIED_PUBLIC_ROUTE'))
            m.append(beam(f'M120_{segment["id"]}_DARK_UNDERTRUSS',
                          (a[0],a[1],a[2]-6),(b[0],b[1],b[2]-6),18,5,'obsidian','PUBLIC_ROUTE','UNSUPPORTED_TRUSS'))
    model['meshes'].extend(m)
    model['m120_added_meshes']=len(m)
    model['public_route_concept']=route
    model['governance']={'old_city_world_modified':False,'construction_approved':False,'comparison_baseline_promoted':False,
      'formal_protection_clearance':False,'review_copy_only':True,'world_writes':0}
    model['collision_certified']=False
    model['accessible_continuous_public_route']=False
    model['model_H_to_world_Y']='UNVERIFIED'
    model['unverified_site_programs_count']=16
    return model

if __name__=='__main__':
    p=produce_m120();dest=ROOT/'data/M120_B_ARCHITECTURAL_SPINE_REVISION.json'
    dest.write_text(json.dumps(p,separators=(',',':')),encoding='utf8')
    print('M120 model',len(p['meshes']),'M120 adds',p['m120_added_meshes'],'route segments',len(p['public_route_concept']['segments']))
    print('tile risks',[(s['id'],s['observed_material_tile_AABB_risks']) for s in p['public_route_concept']['segments']])
