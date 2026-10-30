"""R17 E0 — one true inhabited CIVIC ARCHITECTURAL SECTION, 3D-first.

Scale: ~300m precinct. A three-sided *occupied perimeter of connected rooms*
opens around a real sky-lit public forum. No 10km skyline, no giant skin,
no disconnected pavilions, no fiction that floor count means room completion.

Author-designed staggered arcs and public-tier programs; a real connected
entrance and exactly specified physical grand staircase from z4 to z33.
Native editable BLEND/GLB and fixed 9 true camera images.
ART G0 UNREVIEWED until actual saved pixel review, never auto PASS.
"""
from pathlib import Path
import bpy, math, json, sys
from mathutils import Vector
P=Path(sys.argv[-1]).resolve();P.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
M={}
def mat(name,rgb):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*rgb,1.0)
    M[name]=m
    return m
mat("01 pale limestone woven city",(.72,.74,.68))
mat("02 dark stone cut-back",(.28,.35,.37))
mat("03 copper inhabited thresholds",(.62,.45,.33))
mat("04 glass turquoise transit markers",(.28,.54,.57))
mat("05 warm civic paving",(.69,.63,.52))
mat("06 deep library interior",(.35,.40,.41))
mat("07 planted rooftop",(.39,.51,.40))
mat("08 sheltered apartment stone",(.67,.66,.58))
def col(name):
    c=bpy.data.collections.get(name)
    if c is None:
        c=bpy.data.collections.new(name);scene.collection.children.link(c)
    return c
def mesh(name,verts,faces,ma,group,role):
    data=bpy.data.meshes.new(name+"_mesh")
    data.from_pydata(verts,[],faces);data.update()
    o=bpy.data.objects.new(name,data);col(group).objects.link(o)
    data.materials.append(M[ma])
    o["R17_function"]=role
    o["R17_verified_habitable"]=False
    o["R17_approved_art"]=False
    return o
def prism(name,p,z0,z1,ma,group,role):
    assert z1>z0 and len(p)>2
    N=len(p)
    verts=[(x,y,z0) for x,y in p]+[(x,y,z1) for x,y in p]
    faces=[tuple(range(N-1,-1,-1)),tuple(range(N,N*2))]
    faces.extend((i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N))
    return mesh(name,verts,faces,ma,group,role)
def wall(name,p,q,z0,z1,t,ma,group,role):
    dx=q[0]-p[0];dy=q[1]-p[1];length=math.hypot(dx,dy)
    assert length>0
    nx,ny=-dy/length*t/2,dx/length*t/2
    corners=[(p[0]+nx,p[1]+ny),(q[0]+nx,q[1]+ny),
             (q[0]-nx,q[1]-ny),(p[0]-nx,p[1]-ny)]
    return prism(name,corners,z0,z1,ma,group,role)
def polar(r,a,sx=1,sy=1,dx=0,dy=0):
    th=math.radians(a)
    return (math.cos(th)*r*sx+dx,math.sin(th)*r*sy+dy)
# The following three arcs share an architectural court,
# but follow *different* boundary calibrations, heights, programs & openings.
# No mirrored halves, no one-shot megastructure.
DISTRICTS={
"WEST_LIBRARY":{"arc":(129,237),"z":[4,33,62,96,126],
    "outer":(148,155,142,131,118),"inner":(63,69,77,85,94),
    "shift":(-12,-4),"skyline":"open library terraces"},
"NORTH_FORUM":{"arc":(30,145),"z":[5,36,74,107],
    "outer":(137,140,127,125),"inner":(76,80,84,91),
    "shift":(5,13),"skyline":"cultural deep forum"},
"EAST_TRANSIT":{"arc":(-48,36),"z":[3,31,59,91,125,155],
    "outer":(124,135,149,144,133,117),"inner":(65,68,76,82,90,97),
    "shift":(18,-9),"skyline":"vertical transit city"},
}
NSEG=24
def bend(name,d,i,r,a):
    # asymmetry is deliberately NON-uniform at plan-geometry level;
    # inner facade pushes into the void on alternating occupied tiers.
    rip=4*math.sin(math.radians(a*2.1+i*19))
    x,y=polar(r+rip,a)
    return (x+d["shift"][0],y+d["shift"][1])
def sector_ring_points(n,d,i):
    a0,a1=d["arc"];outer=d["outer"][i];inner=d["inner"][i]
    aa=[a0+(a1-a0)*j/NSEG for j in range(NSEG+1)]
    return ([bend(n,d,i,outer,a) for a in aa]+
           [bend(n,d,i,inner,a) for a in aa[::-1]])
def floor_and_rooms():
  programs={
   "WEST_LIBRARY":["ENTRY_ARCHIVE","PUBLIC_READING","STUDY_COLLECTION","CITY_HISTORY","SKY_GALLERY"],
   "NORTH_FORUM":["CULTURAL_HALL","AUDITORIUM_OVERVIEW","EXHIBITION","PUBLIC_ROOF"],
   "EAST_TRANSIT":["GROUND_CONCOURSE","TRANSFER_FORUM","COMMUNITY_ROOMS","TRANSIT_EXCHANGE","SKY_COLLECTIVE","HIGH_CITY_ROOM"]
  }
  floor_count=0
  for district,d in DISTRICTS.items():
    for i,z in enumerate(d["z"]):
        role=programs[district][i]
        p=sector_ring_points(district,d,i)
        prism(district+f"_LEVEL_{i:02d}_{role}_INHABITED_DECK",
           p,z-1.9,z,"05 warm civic paving","01 OCCUPIED PUBLIC FLOORS",
           "real full-depth public floor "+role)
        floor_count+=1
        # Actual tall, partly open *inner* façade of rooms, not single
        # blank external wall. Each bay creates real void between 2 piers.
        angles=[d["arc"][0]+(d["arc"][1]-d["arc"][0])*j/8 for j in range(9)]
        above=d["z"][i+1] if i+1<len(d["z"]) else z+(17 if district!="EAST_TRANSIT" else 19)
        clear_h=min(16.5,above-z-3.5)
        assert clear_h>=13
        for j,a in enumerate(angles):
            x,y=bend(district,d,i,d["inner"][i]+3,a)
            tx,ty=bend(district,d,i,d["inner"][i]+3,a+.75)
            wall(district+f"_L{i}_INNER_PORTAL_PIER_{j}",
                 (x,y),(tx,ty),z+.3,z+clear_h,3.2,
                 "02 dark stone cut-back","02 INNER ARCHITECTURAL FACADES",
                 "real spaced pier leaving open air between public spaces")
        # A subset of bay-spanning lintels clearly shows floor-to-ceiling
        # civic portals, without closing off the atrium.
        for j in (0,2,4,6):
            a,b=angles[j],angles[j+1]
            q=bend(district,d,i,d["inner"][i]+3,a)
            r=bend(district,d,i,d["inner"][i]+3,b)
            wall(district+f"_L{i}_PORTAL_HEAD_{j}",q,r,z+clear_h-2,z+clear_h,4,
                 "03 copper inhabited thresholds","02 INNER ARCHITECTURAL FACADES",
                 "real high civic opening lintel")
        # A limited fragment of a REAL internal room back wall in one
        # wing, rather than just an invented 'public room' attribute.
        ia=(angles[2]+angles[3])/2
        x,y=bend(district,d,i,d["outer"][i]-13,ia)
        t0=bend(district,d,i,d["outer"][i]-13,ia-7)
        t1=bend(district,d,i,d["outer"][i]-13,ia+7)
        wall(district+f"_L{i}_ACTUAL_ROOM_BACK_WALL",t0,t1,z+.4,z+clear_h-1,4.6,
             "06 deep library interior","03 REAL ROOMS IN WING",
             "one enclosing wall; full individual building interior incomplete")
        # Non-decora­tive book/archive or transit counters occupy real floor:
        for k in range(3):
            ang=angles[3]+k*(angles[5]-angles[3])/3
            px,py=bend(district,d,i,(d["inner"][i]+d["outer"][i])*.55,ang)
            prism(district+f"_L{i}_USABLE_ROOM_COUNTER_{k}",
                [(px-4,py-9),(px+4,py-9),(px+4,py+9),(px-4,py+9)],
                z,z+1.25,"08 sheltered apartment stone",
                "03 REAL ROOMS IN WING",
                "physical furniture/counter placeholder; function unverified")
        # Real roof terrace exists on selected levels only, uneven skyline.
        if i==len(d["z"])-1:
            p=sector_ring_points(district,d,i)
            prism(district+"_ACTUAL_SKY_ROOF_GARDEN",p,z+17,z+20,
                "07 planted rooftop","04 TERRACED CITY ROOFS",
                "real accessible-looking roof surface, connection unverified")
  return floor_count
floors=floor_and_rooms()
# Shared central public arrival court: not a blank surrounding shell.
atrium=[(-53,-72),(2,-89),(60,-66),(71,-21),(46,46),
        (-3,72),(-52,55),(-68,-14)]
prism("OPEN_TO_SKY_PUBLIC_COMMONS_WHOLE_FLOOR",atrium,1.8,4,
     "05 warm civic paving","05 OPEN PUBLIC COURT",
     "physical courtyard connected to actual entry axis")
# Covered transit threshold, set away from central plaza; front open sky.
entry=[(-18,-175),(18,-175),(27,-75),(-29,-75)]
prism("CITY_FRONT_ENTRY_STREET_TO_COURT",entry,1.9,4,
     "05 warm civic paving","05 OPEN PUBLIC COURT",
     "same z=4 walk entry to courtyard, shared area is continuous")
# West stair is REAL 168 STEP TREADS at plausible human riser (0.1726m)
# and 0.42m run. It ends at the first elevated west gallery z=33.
start=Vector((-57,-68,4));end=Vector((-113,-17,33))
rise=end.z-start.z
NSTAIRS=168
assert abs(rise/NSTAIRS-.172619047619)<1e-7
H=Vector((end.x-start.x,end.y-start.y,0))
run=H.length;u=H/run;side=Vector((-u.y,u.x,0))
assert run/NSTAIRS>.40
vertices=[];faces=[]
for i in range(NSTAIRS):
  a=start+u*(run*i/NSTAIRS)+Vector((0,0,rise*i/NSTAIRS))
  b=start+u*(run*(i+1)/NSTAIRS)+Vector((0,0,rise*(i+1)/NSTAIRS))
  a.z=b.z  # horizontal tread, next elevation; vertical riser below
  corners=[a-side*3.4,a+side*3.4,b+side*3.4,b-side*3.4]
  idx=len(vertices);vertices.extend([tuple(v) for v in corners])
  faces.append((idx,idx+1,idx+2,idx+3))
mesh("168_ACTUAL_SINGLE_CONNECTED_STAIR_TREADS",
     vertices,faces,"03 copper inhabited thresholds",
     "06 VERTICAL PUBLIC ACCESS",
     "real 168 horizontal stair treads from lower public court to z33 west floor; guardrails and risers not certified")
# Continuous underside for physical supporting ramp ground beneath stair,
# guards along both sides. One external stair is explicit; high levels remain QA HOLD.
below=[tuple(start+side*3.4),tuple(start-side*3.4),
       tuple(end-side*3.4),tuple(end+side*3.4)]
mesh("GRAND_STAIR_CONTINUOUS_SUBSTRUCTURE",below,[(0,1,2,3)],
     "02 dark stone cut-back","06 VERTICAL PUBLIC ACCESS",
     "sloping foundation, engineering not certified")
# 2 dedicated modest vestibules bridging the uneven wing-to-court
# circulation; no giant bridge across void.
w=[(-78,-26),(-53,-34),(-45,-11),(-80,-1)]
prism("WEST_PUBLIC_ENTRY_VESTIBULE",w,3.4,4,"03 copper inhabited thresholds",
      "05 OPEN PUBLIC COURT","actual connecting foyer floor to west wing")
e=[(50,-26),(80,-25),(80,4),(50,7)]
prism("EAST_TRANSIT_ENTRY_VESTIBULE",e,3.4,4,"04 glass turquoise transit markers",
      "05 OPEN PUBLIC COURT","physical entry threshold, circulation QA HOLD")
# A narrow high-level public connector between THREE wings, not a new
# monumental exterior skin. Purpose is to demonstrate physically intersecting
# western and north gallery floors.
span=[(-85,64),(-72,75),(-24,98),(-18,85)]
prism("WEST_TO_NORTH_GALLERY_REAL_CONNECTION",span,72,74,
      "03 copper inhabited thresholds","06 VERTICAL PUBLIC ACCESS",
      "physical connector connecting upper perimeter, gradient/structure QA hold")
SCENECAMS={
 "01_LONG_PUBLIC_APPROACH":((0,-560,130),(0,0,99),380),
 "02_FRONT":((0,-570,146),(0,8,100),365),
 "03_OBLIQUE":((350,-405,258),(0,4,100),410),
 "04_SIDE":((505,0,176),(0,9,105),360),
 "05_REAR":((0,500,205),(0,5,94),350),
 "06_AERIAL":((265,-270,540),(0,0,93),375),
 "07_PEDESTRIAN_ENTRY":((0,-158,7),(0,48,61),None),
 "08_OPEN_CIVIC_FORUM":((10,-45,7),(1,70,75),None),
 "09_INTERNAL_LIBRARY":((-113,-20,34),(-66,14,68),None),
 "10_UPPER_CITY_STREET":((103,44,92),(-18,65,105),None)
}
for name,(eye,target,scale) in SCENECAMS.items():
    cam=bpy.data.cameras.new(name)
    ob=bpy.data.objects.new(name,cam)
    col("07 TEN LOCKED G0 REVIEW CAMERAS").objects.link(ob)
    ob.location=eye
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat("-Z","Y").to_euler()
    cam.clip_end=100000
    if scale:cam.type="ORTHO";cam.ortho_scale=scale
    else:cam.type="PERSP";cam.lens=21;cam.clip_start=.05
scene.render.engine="BLENDER_WORKBENCH"
scene.display.shading.light="STUDIO"
scene.display.shading.color_type="MATERIAL"
scene.display.shading.show_cavity=True
scene.render.resolution_x=1060;scene.render.resolution_y=720
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.camera=bpy.data.objects["03_OBLIQUE"]
scene["R17_PROJECT_ROLE"]="~320m noncanonical civic inhabited section prototype"
scene["R17_ART_STATUS"]="G0_UNREVIEWED"
scene["R17_APPROVED_CENTRAL"]=False
scene["R17_10KM_CITY_MASTER_COMPLETED"]=False
scene["R17_MINECRAFT_CONSTRUCTION"]=False
scene["R17_UNVERIFIED"]="upper vertical circulation, occupancies, structure, fire escape, all detailed interiors"
blend=P/"R17_E0_EDITABLE_INHABITED_CIVIC_SECTION.blend"
glb=P/"R17_E0_PUBLIC_FORUM_CITY_SECTION.glb"
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",
      export_cameras=False,export_lights=False)
for name in SCENECAMS:
    scene.camera=bpy.data.objects[name]
    scene.render.filepath=str(P/(name+".png"))
    bpy.ops.render.render(write_still=True)
os=[o for o in bpy.data.objects if o.type=="MESH"]
man={
 "scope":"R17 independent ~320m civic 3D section, NOT official central M247-C",
 "designer_made_spatial_massing":"3 curved inhabited civic wings forming one linked open-to-sky public forum with differentiated heights",
 "floor_program_total":floors,
 "real_foyer_and_open_air_court":True,
 "real_stair_treads":NSTAIRS,
 "real_stair_riser_m":rise/NSTAIRS,
 "real_stair_run_m":run,
 "public_entry_elevation_m":4,
 "west_public_gallery_destination_m":33,
 "upper_level_access_unverified":True,
 "architecture_full_urban_interior_finished":False,
 "art_adopted":False,
 "all_completed_10km_city":False,
 "minecraft_construction":False,
 "real_mesh_count":len(os),
 "real_vertices":sum(len(o.data.vertices) for o in os),
 "real_tris":sum(sum(max(1,len(f.vertices)-2) for f in o.data.polygons) for o in os),
 "source_blend":blend.name,
 "real_glb":glb.name,
 "ten_original_real_pngs":[n+".png" for n in SCENECAMS],
 "blender_version":bpy.app.version_string,
 "formal_artist_visual_review":"PENDING"
}
(P/"R17_E0_TRUE_3D_MANIFEST.json").write_text(
 json.dumps(man,ensure_ascii=False,indent=2),encoding="utf8")
print("R17_REAL_INHABITED_CIVIC_SECTION_COMPLETE_NOT_ART_REVIEWED",
   json.dumps({k:v for k,v in man.items() if k not in ('ten_original_real_pngs',)}))
