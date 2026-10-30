"""D47-R8 - three-shot visual experience FIRST; true 3D sightline and urban silhouette probe.
Original camera composition is defined BEFORE building the objects. This model is a deliberately
limited visual/spatial concept in a noncanonical ~2km fragment, NOT 10km city master.
Does not resurrect R1-R7 rejected shapes and makes no aesthetic PASS claim.
No Minecraft, Work, protected M247-C, official W0, H1-H6 or SB assets touched.
"""
import bpy, math, json, sys
from pathlib import Path
from mathutils import Vector
P=Path(sys.argv[-1]).resolve();P.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def layer(n):
    c=bpy.data.collections.get(n)
    if c is None:
        c=bpy.data.collections.new(n);bpy.context.scene.collection.children.link(c)
    return c
def material(n,col):
    m=bpy.data.materials.new(n);m.diffuse_color=(*col,1);return m
stone=material('01 public stone',(.65,.66,.60))
deep=material('02 cut civic facade',(.18,.28,.32))
copper=material('03 culture inhabitation',(.65,.47,.31))
white=material('04 ceremonial lighter terraces',(.87,.84,.69))
cyan=material('05 transit',(.35,.57,.59))
green=material('06 roof garden',(.39,.52,.45))
dark=material('07 urban underside',(.25,.36,.40))
def mesh(n,verts,faces,ma,group,role):
    me=bpy.data.meshes.new(n+'_NATIVE')
    me.from_pydata(verts,[],faces);me.update()
    o=bpy.data.objects.new(n,me);layer(group).objects.link(o);me.materials.append(ma)
    o['architectural_role']=role;o['not_formal_master']=True
    return o
def poly(n,outline,z,thick,ma,group,role):
    N=len(outline); assert N>=3
    v=[(x,y,z-thick) for x,y in outline]+[(x,y,z) for x,y in outline]
    f=[tuple(range(N-1,-1,-1)),tuple(range(N,N*2))]
    f +=[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
    return mesh(n,v,f,ma,group,role)
def box(n,x0,x1,y0,y1,z0,z1,ma,group,role):
    assert x1>x0 and y1>y0 and z1>z0
    return poly(n,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z1,z1-z0,ma,group,role)
def tube(n,path,radii,ma,group,role):
    # authored irregular 3D tapered structural keel; not a skyscraper block
    rings=[]
    for k,p in enumerate(path):
        w,d=radii[k];x,y,z=p
        rings.append([(x-w/2,y-d/2,z),(x+w/2,y-d/2,z),
                      (x+w/2,y+d/2,z),(x-w/2,y+d/2,z)])
    v=[p for ring in rings for p in ring]
    f=[(3,2,1,0),tuple(range((len(rings)-1)*4,len(rings)*4))]
    for k in range(len(rings)-1):
        for j in range(4):
            a=k*4+j;b=k*4+(j+1)%4
            f.append((a,b,b+4,a+4))
    return mesh(n,v,f,ma,group,role)
def strip(n,points,halfwidths,ma,group,role):
    v=[]
    for i,(x,y,z) in enumerate(points):
        a=points[max(0,i-1)];b=points[min(len(points)-1,i+1)]
        dx=b[0]-a[0];dy=b[1]-a[1]
        t=math.hypot(dx,dy)
        assert t>0
        nx,ny=-dy/t,dx/t
        v.extend([(x-nx*halfwidths[i],y-ny*halfwidths[i],z),
                  (x+nx*halfwidths[i],y+ny*halfwidths[i],z)])
    f=[(2*k,2*k+1,2*k+3,2*k+2) for k in range(len(points)-1)]
    return mesh(n,v,f,ma,group,role)

# 0. CAMERA STORYBOARD IS CREATED *BEFORE* ANY GEOMETRY.
# The intended psychological progression is intentionally testable. Eye-height
# varies in elevation because this is science-fiction scale study, NOT certified
# accessible human route.
shots=[
  ('01_APPROACH_GATE',(-65,-1220,22),(-30,380,490),23),
  ('02_RIFT_THRESHOLD',(-45,-620,24),(0,650,670),23),
  ('03_OVERHEAD_REVELATION',(45,-125,25),(5,440,1030),22),
  ('04_UPPER_CITY_INHABITED',(300,420,540),(-310,460,700),25),
  ('05_ARCHIVE_PUBLIC_INTERIOR',(-425,160,368),(-500,435,405),24)
]
review=[
  ('06_MACRO_FRONT',(0,-3650,1090),(0,280,590),1600),
  ('07_MACRO_SIDE',(3250,100,1060),(0,250,590),1700),
  ('08_MACRO_REAR',(0,3400,1100),(0,250,560),1650),
  ('09_MACRO_AERIAL',(2050,-2350,2950),(0,180,560),2100)
]
def make_camera(name,pos,target,lens,ortho=False):
    d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d)
    layer('00 VIEW STORYBOARD LOCKED BEFORE MODELING').objects.link(o)
    o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    d.clip_end=20000
    if ortho:d.type='ORTHO';d.ortho_scale=lens
    else:d.type='PERSP';d.lens=lens
    return o
for name,pos,target,lens in shots:make_camera(name,pos,target,lens)
for name,pos,target,scale in review:make_camera(name,pos,target,scale,True)
cam_signatures={name:{'eye':list(pos),'look_at':list(tgt),'lens_or_ortho':l}
  for name,pos,tgt,l in shots+review}

# 1. An actually continuous *one-mesh* public route from arrival to revelation.
# This is a study floor and not an engineering/accessible route certification.
route=[(-65,-1310,-5),(-68,-1135,-4),(-75,-930,-3),
       (-64,-730,-2),(-40,-530,0),(-12,-335,1),(25,-145,1),
       (10,10,2),(-2,178,2),(45,355,3),(13,570,4)]
strip('ONE_CONTINUOUS_PUBLIC_CITY_APPROACH',route,
      [33,30,29,33,45,53,55,58,59,49,33],stone,
      '01 UNINTERRUPTED CEREMONIAL CITY FLOOR',
      'one physically connected route surface; actual navigation needs collision clearance')
# Stage 1: approach is an OPEN-AIR elongated gap, not a giant vault or gothic arch.
# Underneath actual OPEN solid-volume human public rooms carved by separate wall segments.
# Three gateway pavilions are *purposeful* city program and open to the approach.
def court(n,coords,base,height,ma,orientation):
    poly(n+'_REAL_FLOOR',coords,base,7,ma,
       '02 PUBLIC ENCLOSED ACTUAL ROOMS',n+' inside pedestrian floor')
    poly(n+'_ACTUAL_ROOF',coords,base+height,12,stone,
       '02 PUBLIC ENCLOSED ACTUAL ROOMS',n+' room weather roof')
    for k in range(len(coords)):
        a=coords[k];b=coords[(k+1)%len(coords)]
        if k==orientation:
            for t0,t1 in [(0,.33),(.67,1)]:
                if t1>t0:
                    q0=(a[0]+(b[0]-a[0])*t0,a[1]+(b[1]-a[1])*t0)
                    q1=(a[0]+(b[0]-a[0])*t1,a[1]+(b[1]-a[1])*t1)
                    tube(n+'_REAL_DOOR_POST_'+str(int(t0*100)),[(q0[0],q0[1],base+height/2),(q1[0],q1[1],base+height/2)],[(6,height),(6,height)],deep,
                         '02 PUBLIC ENCLOSED ACTUAL ROOMS','solid piers beside actual opening; diagonal beam approximation')
        else:
            # continuous true vertical wall with side opening at top on other edges
            tube(n+'_REAL_WALL_'+str(k),[(a[0],a[1],base+height/2),
                 (b[0],b[1],base+height/2)],[(5,height),(5,height)],ma,
                 '02 PUBLIC ENCLOSED ACTUAL ROOMS','physical enclosing public room wall')
court('WEST_CULTURAL_ENTRY',
      [(-380,-890),(-215,-965),(-155,-740),(-315,-655),(-417,-740)],
      0,70,copper,2)
court('EAST_TRANSIT_ENTRY',
      [(175,-915),(385,-855),(430,-690),(274,-610),(156,-745)],
      0,85,cyan,4)

# 2. Two city banks arise from LIVED terraces across uneven depth, NOT solid walls.
# Explicit upper city heads have occupied floors/roof/facade openings and variable
# fronts; negative civic gap stays open at x near zero, never filled with a wall.
west=[
 (-345,-450,155,[-540,-183]),(-455,-180,255,[-700,-175]),
 (-510,110,390,[-760,-195]),(-480,380,535,[-790,-165]),
 (-590,665,625,[-890,-245]),(-630,920,745,[-920,-260])
]
east=[
 (300,-470,110,[170,550]),(425,-230,235,[185,645]),
 (505,95,320,[205,720]),(425,370,465,[190,680]),
 (520,655,570,[225,805]),(650,955,690,[295,950])
]
def inhabited_strata(side,st,ma):
    # Real floor stages at all city bank nodes and inhabitable public wall/roof
    # ledges: they interlock but don't form a solid continuous boulder.
    for i,(x,y,z,limits) in enumerate(st):
        left,right=limits
        yr=95 if i%2 else 118
        if i%2:
            outline=[(left,y-yr),(right-40,y-yr*1.14),(right,y+yr*.62),
                     (right-50,y+yr),(left+23,y+yr*.93)]
        else:
            outline=[(left,y-yr*.86),(right-35,y-yr),
                     (right,y+yr*.74),(left+40,y+yr)]
        poly(side+f'_L{i}_CIVIC_CITY_FLOOR',outline,z,25,
             ma,'03 ACTUAL DIFFERENT TERRACED CITY DISTRICTS',
             'physical outdoor city terrace')
        # Other half-levels are roofed civic living rooms with openings,
        # arranged by actual street-facing population scales.
        if i in (1,2,3,4):
            # The inner edge nearest the void is deliberately NOT fully
            # closed: open 3D public dwelling facades show internal floors.
            cx=right-76 if side=='WEST' else left+76
            ya=y+26 if i%2 else y-15
            w=97+i*7
            h=55+i*11
            for j in range(3):
                zlev=z+j*h
                outline2=[(cx-w,ya-55),(cx+w,ya-47),
                          (cx+w+28,ya+62),(cx-w+23,ya+72)]
                poly(side+f'_L{i}_ROOM{j}_REAL_FLOOR',outline2,zlev,9,
                     stone,'04 GENUINE PUBLIC OPEN BUILDING CELLS',
                     'observable terrace room floor with open void-side elevation')
                poly(side+f'_L{i}_ROOM{j}_WEATHER_ROOF',outline2,zlev+h-8,9,
                     white,'04 GENUINE PUBLIC OPEN BUILDING CELLS',
                     'physical covered space, open front to the civic void')
                # rear non-void city weather wall
                if side=='WEST':
                    wa=(cx-w,ya-47);wb=(cx-w+23,ya+72)
                else:
                    wa=(cx+w+15,ya-47);wb=(cx+w+28,ya+62)
                tube(side+f'_L{i}_ROOM{j}_BACK_WALL',[(wa[0],wa[1],zlev+h*.45),
                   (wb[0],wb[1],zlev+h*.45)],[(8,h),(8,h)],deep,
                   '04 GENUINE PUBLIC OPEN BUILDING CELLS',
                   'actual rear wall; outer envelope of open urban room')
                # structural fins at actual facade-side bays, NOT fake paint.
                for k in [0,1]:
                    dx=(-w+2*k*w)
                    xx=cx+dx
                    tube(side+f'_L{i}_ROOM{j}_FACETED_PIER_{k}',
                         [(xx,ya-43,zlev+h*.48),(xx+16,ya+57,zlev+h*.48)],
                         [(9,h*.96),(9,h*.96)],copper,
                         '04 GENUINE PUBLIC OPEN BUILDING CELLS',
                         'actual spaced portal supports for open civic gallery')
        # green care spaces on 2 out of 6 strata only, not decoration rescue.
        if i in (2,4):
            poly(side+f'_L{i}_OPEN_PUBLIC_GARDEN',
                 [(left+47,y-55),(left+140,y-48),
                  (left+162,y+50),(left+66,y+62)],z+2,3,green,
                 '05 PUBLIC LIFE AND ECOLOGICAL TERRACES',
                 'actual roof garden walking surface')
    # Witness physically continuous elevated public access strips along each
    # bank. This is only a pilot; stairs/lifts still require engineering.
    route_pts=[((q[3][0]+q[3][1])/2,q[1],q[2]+3) for q in st]
    strip(side+'_JOINED_DISTRICT_PUBLIC_STREET',route_pts,
          [29,30,38,33,36,28],stone,'06 ACTUAL ELEVATED PUBLIC ROADS',
          'single connected slope-to-slope public street; gradient might be unacceptable')
inhabited_strata('WEST',west,copper)
inhabited_strata('EAST',east,cyan)

# 3. HIGH ALTITUDE REVELATION: not a ring, not a single pipe/beam. Distinct
# occupied, OPEN-PERFORATED double city, offset in plan at 1000m altitude.
# The roofs and rooms *are the view*, their occupation shapes the silhouette.
high=[
 ('UPPER_WEST_STUDY',(-520,250,1080),(-780,-150),190),
 ('UPPER_REVERSED_COMMONS',(-25,515,1290),(-295,330),210),
 ('UPPER_EAST_CIVIC', (505,755,1160),(275,830),175)
]
for n,(cx,cy,z),(xl,xr),h in high:
    outline=[(xl,cy-170),(xr-36,cy-185),(xr+65,cy-38),
             (xr,cy+133),(xl+51,cy+179),(xl-61,cy+32)]
    # real city floor and actual accessible-in-principle open upper world
    poly(n+'_HIGH_PUBLIC_CITY_FLOOR',outline,z,30,white,
          '07 HIGH REVERSAL PUBLIC CITY','actual high city occupied floor')
    for k in range(2):
        little=[(cx-125+k*95,cy-75),(cx-30+k*95,cy-95),
                (cx+10+k*95,cy+82),(cx-106+k*95,cy+88)]
        poly(n+f'_PUBLIC_FACILITY_LEVEL_{k}',little,z+50+k*90,14,
             copper if k==0 else cyan,'07 HIGH REVERSAL PUBLIC CITY',
             'two real upper public facility floors; not solid monolith')
    poly(n+'_UPPER_ROOF',outline,z+h,18,stone,
         '07 HIGH REVERSAL PUBLIC CITY',
         'actual separate upper city weather roof, NOT one beam')
    for j,edge in enumerate([0,2,4]):
        a,b=outline[edge],outline[(edge+1)%len(outline)]
        tube(n+f'_VOID_FACING_SUPPORT_{j}',[(a[0],a[1],z+h*.5),
             (b[0],b[1],z+h*.5)],[(9,h),(9,h)],deep,
             '07 HIGH REVERSAL PUBLIC CITY',
             'discrete support facade not a solid front wall')
# Structural routes in the air visibly AND physically integrated as narrow
# crossing land, not enclosing entire void. Actual engineering not proven.
strip('SKY_CIVIC_CONNECTOR_WEST_EAST',
      [(-560,250,1050),(-260,315,1120),(-45,475,1220),(245,590,1160),(500,745,1140)],
      [20,22,23,25,22],white,'08 CIVIC CONNECTIVITY PROVISIONAL',
      'physical cross-city promenade, route gradient and support unverified')
strip('SECOND_INDEPENDENT_SKY_STREET',
      [(-510,450,775),(-270,475,810),(-5,535,860),(215,630,890),(490,790,930)],
      [16,21,22,19,17],grey if False else stone,
      '08 CIVIC CONNECTIVITY PROVISIONAL',
      'separate real city street at different altitude; access unverified')

# Capture once from exact scene and keep all 9 cameras recorded.
scene=bpy.context.scene
scene['phase']='D47-R8 Sequence-driven visual-city pilot'
scene['shotlist_authored_before_geometry']=True
scene['formal_art_adopted']=False
scene['main_modified']=False
scene['official_city_coords']=False
scene['m247c_protected']=True
scene['master_10km_complete']=False
scene['minecraft_construction']=False
scene['all_rooms_reachable']=False
scene['all_streets_accessible']=False
scene['lift_access_verified']=False
scene['visual_los_certified']=False
scene['art_status']='UNREVIEWED'
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO'
scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_cavity=True
scene.render.resolution_x=1160
scene.render.resolution_y=750
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
bpy.ops.wm.save_as_mainfile(filepath=str(P/'R8_SEQUENCE_3D_NATIVE_EDITABLE.blend'))
bpy.ops.export_scene.gltf(filepath=str(P/'R8_SEQUENCE_3D_NATIVE_EDITABLE.glb'),
     export_format='GLB',export_cameras=False,export_lights=False)
for name,*_ in shots+review:
    scene.camera=bpy.data.objects[name]
    scene.render.filepath=str(P/(name+'.png'))
    bpy.ops.render.render(write_still=True)
manifest={
  'scope':'D47-R8 ~2km NONCANONICAL visual pilot; not completed city master',
  'phase':'nine true cameras, three narrative shots defined before geometry',
  'shots':[x[0] for x in shots],'macro_review':[x[0] for x in review],
  'cameras':cam_signatures,
  'mesh_count':len([o for o in bpy.data.objects if o.type=='MESH']),
  'camera_count':len(shots+review),
  'native_blend':'R8_SEQUENCE_3D_NATIVE_EDITABLE.blend',
  'gltf':'R8_SEQUENCE_3D_NATIVE_EDITABLE.glb',
  'stage_eye_points_m':[list(s[1]) for s in shots[:3]],
  'urban_rift_los_tested':False,
  'physical_walking_complete':False,'city_master_10km':False,
  'H1_H6_SB01_SB16_complete':False,'official_anchors_verified':False,
  'art':'G0_NEEDS_HUMAN_VISUAL_AUDIT',
  'canonical_M247_C_adopted':False,'minecraft_write':False,
  'bpy_version':bpy.app.version_string
}
(P/'R8_G0_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('R8_SEQUENCE_FIRST_G0_REAL_3D_CREATED_ART_UNREVIEWED',manifest['mesh_count'])
