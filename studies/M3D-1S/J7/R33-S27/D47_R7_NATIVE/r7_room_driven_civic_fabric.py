"""D47-R7 spatial-room-first fabric test, genuine editable Blender 4.5.

Question: can *built and occupiable* different polygonal civic rooms determine
the macro external form of a city, instead of a pre-shaped boulder/box/ribbon?
This is NOT a proposed final M247-C geometry, nor a 10 km city master.
3D evidence is partial and technical: independent interiors, openings and public
thresholds; no certification of all pedestrian routes or vertical transport.
A research REVERSIBLE proof with ART G0 requiring visual review, NOT automatic pass.
"""
import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector
out=Path(sys.argv[-1]).resolve();out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)

def coll(name):
    c=bpy.data.collections.get(name)
    if c is None:
        c=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(c)
    return c

def material(n,c):
    m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);return m
bone=material('01 city-fabric limestone',(.77,.77,.69))
shade=material('02 canyon shadow wall',(.24,.33,.36))
ochre=material('03 archive public copper',(.67,.46,.33))
blue=material('04 station public teal',(.28,.48,.53))
grey=material('05 street stone',(.49,.52,.52))
upper=material('06 upper lived-city pale',(.77,.68,.49))
garden=material('07 public ecological garden',(.37,.50,.40))
dark=material('08 urban layered edge',(.29,.38,.41))
def mesh(n,v,f,mat,col,role):
    me=bpy.data.meshes.new(n+'_NATIVE_EDITABLE')
    me.from_pydata(v,[],f);me.update()
    o=bpy.data.objects.new(n,me);coll(col).objects.link(o);me.materials.append(mat)
    o['programmatic_geometry_role']=role
    o['design_state']='R7 TEST NOT CANONICAL'
    return o
def linebox(n,a,b,z0,z1,t,mat,col,role):
    dx=b[0]-a[0];dy=b[1]-a[1]
    d=math.hypot(dx,dy);assert d>0.01
    nx,ny=-dy/d*t/2,dx/d*t/2
    v=[(a[0]+nx,a[1]+ny,z0),(a[0]-nx,a[1]-ny,z0),
       (b[0]-nx,b[1]-ny,z0),(b[0]+nx,b[1]+ny,z0),
       (a[0]+nx,a[1]+ny,z1),(a[0]-nx,a[1]-ny,z1),
       (b[0]-nx,b[1]-ny,z1),(b[0]+nx,b[1]+ny,z1)]
    f=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),
       (2,3,7,6),(3,0,4,7)]
    return mesh(n,v,f,mat,col,role)
def polyfloor(n,poly,z,mat,col,role,th=5):
    # A watertight true 3D floor slab. Irregular polygon is explicitly author-designed.
    N=len(poly);assert N>=5
    v=[(x,y,z-th) for x,y in poly]+[(x,y,z) for x,y in poly]
    f=[tuple(range(N-1,-1,-1)),tuple(range(N,N*2))]
    for i in range(N):j=(i+1)%N;f.append((i,j,N+j,N+i))
    return mesh(n,v,f,mat,col,role)
def roof(n,poly,z,heights,mat,col,role):
    # Folded ROOF volume of the actual room, not a free canopy placed above bare slabs.
    N=len(poly)
    v=[(x,y,z) for x,y in poly]+[
        (x,y,z+heights[i]) for i,(x,y) in enumerate(poly)]
    f=[tuple(range(N-1,-1,-1)),tuple(range(N,N*2))]
    for i in range(N):j=(i+1)%N;f.append((i,j,N+j,N+i))
    return mesh(n,v,f,mat,col,role)
def lerp(a,b,u):
    return (a[0]+(b[0]-a[0])*u,a[1]+(b[1]-a[1])*u)
shape_forms=[
 [(0.92,0.05),(0.59,0.83),(-0.23,1.00),(-0.90,0.58),(-1.00,-0.32),(-0.36,-0.88),(0.52,-0.96)],
 [(1.00,-0.06),(0.57,0.74),(-0.08,0.92),(-0.74,0.72),(-1.00,-0.21),(-0.65,-0.95),(0.34,-0.86)],
 [(0.92,0.26),(0.24,1.00),(-0.78,0.84),(-0.96,0.00),(-0.43,-0.94),(0.33,-0.82)],
 [(0.96,-0.20),(0.71,0.71),(-0.29,0.93),(-1.00,0.34),(-0.60,-0.81),(0.18,-1.00)]
]
def rotate(x,y,theta):
    c,s=math.cos(theta),math.sin(theta);return x*c-y*s,x*s+y*c
def footprint(cx,cy,rx,ry,theta,index):
    points=[]
    for xx,yy in shape_forms[index%len(shape_forms)]:
        a,b=rotate(xx*rx,yy*ry,theta)
        points.append((cx+a,cy+b))
    return points
rooms=[]
def make_room(spec,index):
    name,cx,cy,rx,ry,rotation_deg,z,depth,kind,portal_edge,roof_style=spec
    poly=footprint(cx,cy,rx,ry,math.radians(rotation_deg),index)
    group='02 ACTUAL HOLLOW PROGRAMMATIC ARCHITECTURE'
    floor=polyfloor(name+'_REAL_USABLE_FLOOR',poly,z,bone,group,
       kind+' enclosed public interior floor')
    # Authored roof is sloped at every footprint vertex, not an uninhabited "hero plate".
    hs=[8+7*math.sin((i+index)/len(poly)*math.pi*2) for i in range(len(poly))]
    roof(name+'_FOLDED_WATERPROOF_ROOF',poly,z+depth,hs,upper if z>0 else bone,group,
         kind+' physically enclosing room roof')
    door_probe=None;wall_probes=[]
    for i in range(len(poly)):
        a,b=poly[i],poly[(i+1)%len(poly)]
        sec_len=math.dist(a,b)
        if sec_len<20:continue
        isdoor=(i==portal_edge%len(poly))
        iswindow=(i!=portal_edge%len(poly) and (i+index)%3!=0)
        wallmat=shade if (i+index)%2 else bone
        if isdoor:
            gap=min(.33,22/sec_len)
            for j,(t0,t1) in enumerate([(0,.5-gap/2),(.5+gap/2,1)]):
                if t1>t0:linebox(name+f'_PORTAL_PIER_{i}_{j}',lerp(a,b,t0),
                      lerp(a,b,t1),z,z+depth,4.0,wallmat,group,
                      'REAL SOLID SIDE PIER of entrance portal')
            linebox(name+f'_REAL_PORTAL_LINTEL_{i}',lerp(a,b,.5-gap/2),
              lerp(a,b,.5+gap/2),z+22,z+depth,4.0,wallmat,group,
              'real roof lintel; open pedestrian entrance beneath')
            x,y=lerp(a,b,.5);door_probe=(x,y,z+11)
        elif iswindow:
            # Outer wall is genuinely absent inside a 12m-high aperture.
            pieces=[(z,z+11,'LOWER'),(z+23,z+depth,'UPPER')]
            for lo,hi,kindlabel in pieces:
                if hi>lo:
                    linebox(name+f'_REAL_WINDOW_{i}_{kindlabel}',a,b,
                      lo,hi,4,wallmat,group,
                      'solid wall below/above TRUE absent opening')
            x,y=lerp(a,b,.5);wall_probes.append((x,y,z+17))
        else:
            linebox(name+f'_SOLID_WALL_{i}',a,b,z,z+depth,4,wallmat,group,
               'closed wall of actually roofed public room')
    assert door_probe is not None
    room={
      'id':name,'role':kind,'floor_z_m':z,'room_height_m':depth,
      'real_portal_probe':door_probe,'portal_wall_edge':int(portal_edge),
      'real_window_probe_samples':wall_probes,
      'center':[cx,cy],'footprint':poly,
      'physical_room':True,'full_occupancy_qualified':False}
    rooms.append(room)
    # Differentiation of each room through actual inhabited detail, not labeling alone.
    if 'archive' in kind:
        for j in range(4):
            yy=cy-ry*.52+j*ry*.32
            linebox(name+f'_READING_DESK_{j}',(cx-rx*.42,yy),
                (cx+rx*.22,yy+8),z+1,z+7,3,ochre,
                '03 DIFFERENTIATED PUBLIC INTERIOR',
                'actual low reading islands, not a closed urban mass')
    elif 'station' in kind:
        for j in range(2):
            yy=cy-ry*.42+j*ry*.66
            linebox(name+f'_PLATFORM_{j}',(cx-rx*.63,yy),
                (cx+rx*.61,yy+8),z,z+3,9,blue,
                '03 DIFFERENTIATED PUBLIC INTERIOR',
                'actual platform equipment, not rail operation certified')
    elif 'forum' in kind:
        for j in range(4):
            yy=cy+ry*.1+j*ry*.16
            linebox(name+f'_AUDITORIUM_TIER_{j}',(cx-rx*(.57-j*.07),yy),
                (cx+rx*(.57-j*.07),yy+4),z+j*3,z+j*3+3,
                3,ochre,'03 DIFFERENTIATED PUBLIC INTERIOR',
                'actual occupied forum terraces')
    return room
# This list is the actual ARCHITECTURE OF PROGRAM, drawn first before any outer shell:
# each polygonal room is physically open at its entrance and uses the surrounding
# room walls/roof as the *visible external form*. These are unique irregular rooms,
# not a giant encompassing shell to fill later with generic rectangular houses.
SPECS=[
 ('CIVIC_GATE_SOUTH',-5,-387,84,74,-8,0,54,'forum gate',4,0),
 ('WEST_ARCHIVE_HALL_01',-250,-215,104,84,36,0,76,'archive library',0,1),
 ('EAST_STATION_HALL_01',232,-245,116,92,-32,0,72,'station transfer',3,2),
 ('WEST_ARCHIVE_HALL_02',-291,8,123,105,65,0,86,'archive public museum',0,1),
 ('EAST_STATION_HALL_02',272,-28,126,117,-21,0,83,'station interchange',3,3),
 ('NORTH_COUNCIL_FORUM',-65,135,140,111,-18,0,108,'forum civic assembly',4,0),
 ('WEST_GARDEN_GALLERY',-264,249,95,96,12,0,68,'public garden gallery',0,2),
 ('EAST_SKYPORT_HALL',269,249,127,110,58,0,82,'station public skyport',3,3),
 ('NORTH_EXHIBITION_HALL',-15,383,120,94,23,0,83,'museum forum',4,1),
 # upper civilization is spatially offset, with actual rooms, not a solid block
 ('HIGH_WEST_ARCHIVE_01',-206,-74,112,83,51,172,83,'archive sky library',2,2),
 ('HIGH_WEST_ARCHIVE_02',-273,157,95,102,14,174,67,'archive upper museum',1,1),
 ('HIGH_EAST_STATION_01',253,15,117,94,-26,171,74,'station sky concourse',4,3),
 ('HIGH_EAST_CITY_FORUM',187,263,114,94,41,175,73,'forum upper civic chamber',2,0),
 ('HIGH_NORTH_COMMONS',3,402,126,81,-18,182,87,'public garden sky commons',4,1),
 ('HIGH_OVERHEAD_PUBLIC_CITY',-35,77,120,87,18,310,77,'forum high public assembly',1,3)
]
for i,s in enumerate(SPECS):make_room(s,i)

# Actual shared ground: connected geometric path woven among rooms, not a giant
# enclosing bridge/roof. These are narrow surfaces (20-32m), interior intersections
# still require a real human collision/clearance audit before claiming access.
def walkstrip(name,centers,widths,zs,role):
    assert len(centers)==len(widths)==len(zs)
    vs=[]
    for i,(x,y) in enumerate(centers):
        a=centers[max(0,i-1)];b=centers[min(len(centers)-1,i+1)]
        dx=b[0]-a[0];dy=b[1]-a[1];mag=math.hypot(dx,dy)
        assert mag>0
        n=(-dy/mag,dx/mag)
        for sign in [-1,1]:
            vs.append((x+sign*n[0]*widths[i]/2,y+sign*n[1]*widths[i]/2,zs[i]))
    f=[(i*2,i*2+1,i*2+3,i*2+2) for i in range(len(centers)-1)]
    return mesh(name,vs,f,grey,'01 ACTUAL PUBLIC MOVEMENT FABRIC',role)
walkstrip('SOUTH_GATE_TO_NORTH_MARKET',[
    (-14,-560),(0,-415),(0,-285),(-5,-130),(-12,15),(-23,178),(-18,343),(-3,515)],
    [50,38,42,54,56,48,44,48],[0]*8,
    'one true continuous public ground centerline; collision/accessibility not certified')
walkstrip('PUBLIC_WEST_ARCHIVE_STREET',[
    (-14,-380),(-102,-303),(-174,-241),(-234,-142),(-274,-16),(-274,120),(-234,239)],
    [35,31,26,33,33,28,30],[0]*7,
    'physical civic street passing side halls; entrances require separate navigation QA')
walkstrip('EAST_STATION_STREET',[
    (3,-405),(110,-350),(202,-240),(255,-115),(275,20),(273,130),(253,263)],
    [36,35,30,36,36,32,30],[0]*7,
    'physical station public walk corridor; station operation not certified')
# High city has two differently shaped actual inhabited streets:
walkstrip('HIGH_WEST_SHADOW_GALLERY',[
    (-191,-150),(-232,-72),(-276,35),(-270,125),(-258,225),(-192,305)],
    [28,31,26,31,29,26],[172,173,174,174,175,176],
    'genuine elevated street, unsupported route span requires structural audit')
walkstrip('HIGH_EAST_PUBLIC_TERRACE',[
    (262,-115),(249,-15),(228,88),(199,207),(185,293),(95,373)],
    [30,31,29,26,29,30],[171,171,173,175,175,182],
    'genuine high public gallery; upper transit unqualified')
# Cross void bridges: physically present but not falsely called accessible certified.
walkstrip('CITY_VOID_CROSSING_LOW',[
   (-231,-74),(-129,-67),(-30,-45),(87,-21),(236,15)],
   [33,34,37,36,34],[174,174,174,173,171],
   'true 3d public floor spanning canyon; ramp/lift and barriers unproven')
walkstrip('CITY_VOID_CROSSING_HIGH',[
   (-268,160),(-167,178),(-64,201),(42,225),(166,263)],
   [29,29,31,29,28],[174,174,175,176,175],
   'second real non-parallel elevated civic floor linking upper distinct rooms')
# 2 lift shafts open on one side. The actual mechanism and loading are unverified.
for name,x,y in [('LIFT_WEST',-171,-178),('LIFT_EAST',172,-207)]:
    for side in [-1,1]:
        linebox(name+'_SHAFT_FRAME_'+str(side),
            (x-14,y+side*15),(x+14,y+side*15),0,200,5,dark,
            '04 VERTICAL TRANSPORT STRUCTURE INCOMPLETE',
            'actual open elevator framing, certified functionality not present')
    for z in [0,172]:
        poly=[(x-11,y-11),(x+11,y-11),(x+12,y+10),(x-11,y+10),(x-14,y)]
        polyfloor(name+'_LANDING_'+str(z),poly,z,blue,
            '04 VERTICAL TRANSPORT STRUCTURE INCOMPLETE',
            'landing slab; not mechanically proven',3)
# A real garden public commons under the upper chambers.
garden_poly=[(-168,301),(-97,271),(-13,312),(122,351),
             (112,449),(12,490),(-126,457)]
polyfloor('REAL_OPEN_PUBLIC_GARDEN',garden_poly,-3,garden,
          '05 NONCLOSED INHABITED URBAN LANDSCAPE',
          'open civic garden plot as real ground geometry',5)
scene=bpy.context.scene
scene['study']='D47-R7 spatial-room-first geometry not macro primitive generator'
scene['art_approved']=False
scene['M247_C_formal_adopted']=False
scene['original_rejected_R6_edited']=False
scene['main_modified']=False
scene['minecraft_construction']=False
scene['all_routes_human_access_certified']=False
scene['sky_lifts_operational_certified']=False
scene['city_10km_master_complete']=False
scene['only_general_private_interiors_may_be_simplified']=True
def camera(n,loc,target,orto):
    d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d)
    coll('06 FIXED 8 VIEW TRUE BLENDER CAMERAS').objects.link(o);o.location=loc
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    d.clip_end=25000
    if orto:d.type='ORTHO';d.ortho_scale=orto
    else:d.type='PERSP';d.lens=25
    return o
views=[
 ('01_APPROACH',(15,-1200,240),(0,-10,135),1260),
 ('02_FRONT',(-35,-920,420),(0,20,145),1020),
 ('03_OBLIQUE',(785,-780,510),(0,10,165),1160),
 ('04_REAR',(-60,985,410),(0,0,180),1130),
 ('05_AERIAL',(-450,-370,1420),(0,25,140),1280),
 ('06_SHARED_CIVIC',(15,-260,15),(0,185,120),None),
 ('07_ARCHIVE_ROOM',(-248,-165,12),(-265,-85,36),None),
 ('08_OVERHEAD_CITY',(35,25,30),(0,120,315),None)
]
for item in views:camera(*item)
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO'
scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_cavity=True
scene.render.resolution_x=1080
scene.render.resolution_y=740
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
bpy.ops.wm.save_as_mainfile(filepath=str(out/'R7_TRUE_ROOM_TOPOLOGY_G0_EDITABLE.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'R7_TRUE_ROOM_TOPOLOGY_G0.glb'),
    export_format='GLB',export_cameras=False,export_lights=False)
for name,*_ in views:
    scene.camera=bpy.data.objects[name]
    scene.render.filepath=str(out/(name+'.png'))
    bpy.ops.render.render(write_still=True)
manifest={
 'scope':'R7 900m-scale LOCAL architecture-room-derived fabric only; not official city',
 'rooms':rooms,
 'room_count':len(rooms),
 'all_rooms_have_true_portals_and_floors':True,
 'all_windows_physically_open_where_labeled':True,
 'public_meshes':len([o for o in bpy.data.objects if o.type=='MESH']),
 'render_names':[n+'.png' for n,*_ in views],
 'blender_version':bpy.app.version_string,
 'urban_aesthetics':'NOT_REVIEWED',
 'complete_structural_support':False,
 'rooms_full_accessibility':False,'sky_lifts_operational':False,
 'formal_city_master_complete':False,'formal_m247c_art_adopted':False,
 'official_coords':False,'minecraft_construction':False,
 'was_gui_direct_edit':False
}
(out/'R7_G0_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
print('D47_R7_G0_15_REAL_ENCLOSED_POLYGON_ROOMS_CREATED_UNREVIEWED',
      len(rooms),manifest['public_meshes'])
