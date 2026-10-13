#!/usr/bin/env python3
"""M121 cathedral + city public realm as UNAPPROVED independent voxel-world-free research.

Only inherited immutable M117 evidence and M120 procedural source are read.
Does NOT attempt to alter Minecraft saves, protected voxels or baseline design.
Minecraft X/Z/Y is used as a visual world coordinate frame, not validated
relative-H conversion. Old built blocks remain untouched.
"""
from __future__ import annotations
import sys,math,json,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from m119_city_model import mesh,beam,box,section,ATLAS,SITES
from m120_city_model import produce_m120,tapered_buttress
ROOT=Path(__file__).resolve().parents[1]

# Human-scale one-site study: the inherited M120 model is NOT changed in place.
FLOOR=-1723.0
CATH_X,CATH_Z=3572.,-2024.
CIVIC_X,CIVIC_Z=3703.5,-2184.5


def arc_segments(prefix,xcenter,zcenter,base_y,rx,rise,steps,thickness,material,site):
    """Full semi-circular megavolt arch in an X/Y plane; open nave below."""
    out=[]
    for i in range(steps):
        a=math.pi*i/steps;b=math.pi*(i+1)/steps
        p0=(xcenter-rx*math.cos(a),zcenter,base_y+rise*math.sin(a))
        p1=(xcenter-rx*math.cos(b),zcenter,base_y+rise*math.sin(b))
        if math.dist(p0,p1)>.01:out.append(beam(f'{prefix}_{i:02}',p0,p1,thickness,thickness*.77,material,site,'UNAPPROVED_HIGH_VAULT_RIB'))
    return out

def gable_panel(name,p0,p1,p2,p3,mat,site,role):
    # Architectural membrane QUAD, no collision / closed-volume qualification.
    return mesh(name,[p0,p1,p2,p3],[[0,1,2],[0,2,3]],mat,site,role)

def column(name,x,z,y0,y1,w,mat,site):
    return box(name,x-w/2,z-w/2,y0,x+w/2,z+w/2,y1,mat,site,'UNAPPROVED_COLUMN')

def build_experience():
    m=copy.deepcopy(produce_m120())
    inherited=len(m['meshes']);g=[]
    sid='SB08';cx,cz=CATH_X,CATH_Z;y=FLOOR
    # TWO very broad structural side aisles, an intentionally OPEN nave.
    # Do NOT fill entire interior with old-style enclosing block boxes.
    g.append(box('M121_SB08_NAVE_STONE_FLOOR',cx-70,cz-58,y-2.7,cx+70,cz+59,y,'obsidian',sid,'PROPOSED_NEW_FLOOR_REPLACEMENT'))
    g.append(box('M121_SB08_NAVE_LIT_PATH',cx-11,cz-56,y+.04,cx+11,cz+57,y+.24,'ivory',sid,'UNAPPROVED_PUBLIC_PATH'))
    for side in (-1,1):
        xx=cx+side*81
        g.append(box(f'M121_SB08_SIDE_MECHANICAL_PLINTH_{side}',xx-15,cz-60,y-13,xx+15,cz+61,y+3,'obsidian',sid,'UNAPPROVED_HEAVY_SUBSTRUCTURE'))
        # Aisle gallery slabs are offset from nave, leaving full cathedral clear.
        for level in (26,53,81):
            g.append(box(f'M121_SB08_GALLERY_{side}_{level}',cx+side*77-15,cz-52,y+level,
                         cx+side*77+15,cz+55,y+level+3.8,'ivory',sid,'UNBUILT_GALLERY_FLOOR'))
            g.append(box(f'M121_SB08_GALLERY_GOLD_LIP_{side}_{level}',cx+side*62-1.5,cz-52,y+level+4,
                         cx+side*62+1.5,cz+55,y+level+5.4,'copper',sid,'UNAPPROVED_EDGE_MOLDING'))
        for zi,zp in enumerate((cz-55,cz-37,cz-19,cz,cz+19,cz+38,cz+56)):
            g.append(column(f'M121_SB08_DEEP_AISLE_PIER_{side}_{zi}',xx,zp,y+2,y+109,11,'shadow',sid))
            g.append(column(f'M121_SB08_IVORY_AISLE_FACE_{side}_{zi}',xx-side*5,zp,y+9,y+116,2.7,'ivory',sid))
            # Very tall colored window bays: luminous narrow vertical panes.
            if zi<6:
                g.append(box(f'M121_SB08_GLASS_TRACERY_{side}_{zi}',xx-side*7,
                     zp+5,y+15,xx-side*7+1.1,zp+14,y+100,'lagoon',sid,'NONSTRUCTURAL_TRANSLUCENT_APERTURE'))
    # 7 arches in sequence, with genuine 138m clear span, ~154m rise.
    for i,zp in enumerate([cz-53+j*17.7 for j in range(7)]):
        g.extend(arc_segments(f'M121_SB08_PRIMARY_VAULT_RIB_{i}',cx,zp,y+5,74,150,18,7.2,'ivory',sid))
        g.extend(arc_segments(f'M121_SB08_COPPER_CROWN_{i}',cx,zp+1.9,y+7,68,146,18,1.25,'copper',sid))
        for side in (-1,1):
            # Dark flying buttress ribs anchor structure only as speculative silhouettes.
            g.append(tapered_buttress(f'M121_SB08_FLYING_SHOULDER_{i}_{side}',
                  (cx+side*111,zp,y+6),(cx+side*73,zp,y+91),10,4,'shadow',sid))
    # Thin roof membrane below upper arch leaves 30m wide continuous open skylight.
    for i in range(6):
        z0=cz-53+i*17.7;z1=z0+17.7
        for side in (-1,1):
            # Three sloping membrane strips at outer flanks only; central >35m is open.
            for j,(a,b) in enumerate(((35,50),(50,65))):
                x0=cx+side*a;x1=cx+side*b
                # Roof Y from arch profile, no wall across the nave.
                h0=y+5+150*math.sqrt(max(0,1-(a/74)**2))
                h1=y+5+150*math.sqrt(max(0,1-(b/74)**2))
                g.append(gable_panel(f'M121_SB08_SAIL_ROOF_{i}_{side}_{j}',[x0,z0,h0],[x1,z0,h1],
                  [x1,z1,h1],[x0,z1,h0],'opal',sid,'PROPOSED_OPEN_CATHEDRAL_CANOPY'))
    # Mid-height glass bridges only at extremities, not blocking central void.
    for zp in (cz-46,cz+49):
        g.append(beam(f'M121_SB08_SUSPENDED_CROSS_GALLERY_{int(zp)}',(cx-84,zp,y+52),(cx+84,zp,y+52),
                      5.5,2.8,'copper',sid,'UNBUILT_SUSPENDED_WALKWAY'))
    # Material & human-scale path: 1.8m figurines at y=FLOOR; placed safely in drawn open nave only.
    for i,(dx,dz) in enumerate(((-6,-43),(5,-25),(-3,0),(4,29),(12,44))):
        xx=cx+dx;zz=cz+dz
        g.append(column(f'M121_SB08_1P8M_SCALE_PERSON_{i}',xx,zz,y+.2,y+1.8,.55,'copper',sid))
    # Central light datum and ceremonial aperture; never a functional skylight at old world.
    for i in range(7):
        zp=cz-51+i*17.7
        g.append(beam(f'M121_SB08_OCULUS_GUIDE_{i}',(cx-12,zp,y+148),(cx+12,zp,y+148),1.8,1.8,'cyan',sid,'UNAPPROVED_LIGHT_TRACE'))

    # CIVIC CORE: huge open civic eye + two unequal arcades + bridges, avoid generic filled blocks.
    sid='CIVIC_CORE';cx,cz=CIVIC_X,CIVIC_Z
    y0=-1740
    # public deck level larger-than-building; all replacement proposals, not a carved existing site.
    g.append(box('M121_CIVIC_100M_ENTRY_PLATFORM',cx-63,cz-53,y0-6,cx+63,cz+56,y0-2,'obsidian',sid,'UNBUILT_CIVIC_PLATFORM'))
    g.append(box('M121_CIVIC_PUBLIC_STONE_COURT',cx-49,cz-51,y0-1.6,cx+49,cz+56,y0+.2,'ivory',sid,'UNBUILT_FLOOR'))
    # long axial pavement strips reinforce pedestrian scale in giant public cathedral.
    for i in range(9):
        zp=cz-45+i*12
        g.append(box(f'M121_CIVIC_GOLD_PROCESSIONAL_LINE_{i}',cx-1.6,zp,y0+.26,cx+1.6,zp+5,y0+.48,'copper',sid,'UNAPPROVED_FLOOR_MARKER'))
    # 4 unequal vault arches over new civic plaza at different longitudinal positions, not repetitively identical.
    for i,(zz,rx,rise) in enumerate(((cz-39,74,98),(cz-9,88,119),(cz+26,94,137),(cz+48,83,111))):
        g.extend(arc_segments(f'M121_CIVIC_MAJOR_HEAVY_VAULT_{i}',cx,zz,y0+4,rx,rise,19,10,'shadow',sid))
        g.extend(arc_segments(f'M121_CIVIC_LIGHT_EDGE_{i}',cx,zz+2,y0+7,rx-7,rise-9,19,2.4,'ivory',sid))
    for sign in (-1,1):
        xx=cx+sign*96
        g.append(box(f'M121_CIVIC_DARK_SIDE_MEGAFRAME_{sign}',xx-17,cz-56,y0-14,xx+17,cz+54,y0+4,'obsidian',sid,'UNBUILT_SPINE_PLINTH'))
        for j in range(6):
            zp=cz-42+j*18
            g.append(column(f'M121_CIVIC_SIDE_COLUMN_{sign}_{j}',xx,zp,y0+3,y0+94,10,'shadow',sid))
            g.append(box(f'M121_CIVIC_SIDE_GLASS_{sign}_{j}',xx-sign*7,zp-4,y0+10,xx-sign*7+1,zp+6,y0+85,'lagoon',sid,'TRANSPARENT_CONCEPT_PANEL'))
        for level in (23,51,78):
            g.append(box(f'M121_CIVIC_SIDE_PUBLIC_GALLERY_{sign}_{level}',xx-13,cz-52,y0+level,
                         xx+13,cz+51,y0+level+3,'ivory',sid,'UNBUILT_LEVEL'))
    # TWO genuinely suspended decks in deeper view, not connected to protected stair routes.
    for i,(zz,h,span) in enumerate(((cz-21,68,112),(cz+35,105,135))):
        g.append(beam(f'M121_CIVIC_CROSSING_SKYBRIDGE_{i}',(cx-span/2,zz,y0+h),(cx+span/2,zz,y0+h),
                      9.2,4.0,'ivory',sid,'UNCONNECTED_SUSPENDED_GALLERY'))
        g.append(beam(f'M121_CIVIC_UNDERTRUSS_{i}',(cx-span/2,zz,y0+h-6),(cx+span/2,zz,y0+h-6),
                      4.0,4.0,'obsidian',sid,'UNBUILT_BRIDGE_SUPPORT'))
    for i,(dx,dz) in enumerate(((0,-30),(-11,-18),(10,13),(5,45))):
        g.append(column(f'M121_CIVIC_1P8M_SCALE_PERSON_{i}',cx+dx,cz+dz,y0+.25,y0+2.05,.65,'copper',sid))

    # One pedestrian-experience conceptual glass-link FROM SB07 to SB08, intentionally no official claim.
    sid='PUBLIC_EXPERIENCE_SPINE'
    ya=-1671
    a=(3572,-2080,ya);b=(3572,-2073,ya)
    g.append(beam('M121_SB07_SB08_PROCESSIONAL_THRESHOLD',a,b,18,4.6,'ivory',sid,'UNBUILT_INDOOR_LINK'))
    for side in (-1,1):
        xx=3572+side*9
        g.append(beam(f'M121_PUBLIC_NECK_RAIL_{side}',(xx,-2080,ya+2),(xx,-2073,ya+2),1.8,2,'copper',sid,'UNBUILT_EDGE'))

    for new in g:
        new['m121_experience_research_only']=True
        new['approved_for_world_write']=False
        new['collision_certified']=False
        new['existing_frozen_voxel_clearance']='UNKNOWN'
    m['meshes'].extend(g)
    m['phase']='M121';m['variant']='B_PUBLIC_REALM_HUMAN_SCALE_RESEARCH'
    m['m121_new_mesh_count']=len(g)
    m['m121_meshes_start_index']=inherited
    m['experience']={
      'primary_spatial_focus':'SB08 150-block open nave / CIVIC 137-block skycourt',
      'public_eye_level_cameras':2,
      '1p8m_scale_figures':9,
      'proposed_visitor_walkway_geom_count':sum('FLOOR' in p['role'] or 'WALKWAY' in p['role'] for p in g),
      'actual_SB13_entry_anchor_verified':False,
      'continuous_physical_route_pass':False,
      'usable_real_elevator':False,
      'safe_for_construction':False,
      'next_work_mode':'SETUP_LOCAL_WORK_PROJECT_AFTER_M121',
    }
    m['world_writes']=0
    return m

if __name__=='__main__':
    m=build_experience()
    dest=ROOT/'data/M121_B_PUBLIC_REALM_RESEARCH.json'
    dest.write_text(json.dumps(m,separators=(',',':')),encoding='utf8')
    print(json.dumps({'phase':'M121','all_meshes':len(m['meshes']),
                      'new_meshes':m['m121_new_mesh_count'],'world_writes':0},indent=2))
