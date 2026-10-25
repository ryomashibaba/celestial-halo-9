"""HALO-9 J7-R14: actual Blender 600m lived-world spatial pilot.
An independent 300–1000m urban-room study, NOT another central monument.
The dwelling precincts, exposed strata and circulation are designed in the
same model; R13 rejected macro is NOT reused. Noncanonical coordinates.
"""
import bpy,sys,math,json,collections
from pathlib import Path
from math import sin,cos,pi
from mathutils import Vector
out=Path(sys.argv[sys.argv.index("--")+1]).resolve()
if out.exists() and list(out.iterdir()):raise RuntimeError("Output not empty")
out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene;sc.unit_settings.system="METRIC"
COLORS={
"ivory":(.82,.84,.79,1),"light":(.93,.93,.82,1),"deep":(.07,.16,.19,1),
"copper":(.68,.43,.22,1),"water":(.08,.48,.48,1),
"green":(.14,.40,.27,1),"skyline":(.42,.63,.66,1),
"path":(.64,.83,.78,1),"glass":(.26,.66,.79,1),
"gold":(.87,.69,.41,1),"underside":(.18,.29,.31,1)}
M={}
for k,c in COLORS.items():
 m=bpy.data.materials.new(k);m.diffuse_color=c;m.use_nodes=True
 p=m.node_tree.nodes.get("Principled BSDF")
 if p:p.inputs["Base Color"].default_value=c;p.inputs["Roughness"].default_value=.55
 M[k]=m
N=collections.Counter()
def mesh(name,v,f,role,mat):
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update()
 obj=bpy.data.objects.new(name,me);sc.collection.objects.link(obj)
 obj.data.materials.append(M[mat]);obj["study_role"]=role;obj["canonical"]=False
 N[role]+=1;return obj
def solid(name,outline,bottom,top,role,mat):
 count=len(outline)
 assert count>=3 and top>bottom
 v=[(x,y,bottom) for x,y in outline]+[(x,y,top) for x,y in outline]
 f=[tuple(range(count-1,-1,-1)),tuple(range(count,2*count))]
 for i in range(count):
  j=(i+1)%count;f.append((i,j,count+j,count+i))
 return mesh(name,v,f,role,mat)
def beam(name,A,B,w,d,role,mat):
 A=Vector(A);B=Vector(B);dir=B-A
 lateral=Vector((-dir.y,dir.x,0))
 if lateral.length<.001:lateral=Vector((1,0,0))
 lateral.normalize();r=lateral*w/2;h=Vector((0,0,d/2))
 v=[]
 for c in (A,B):v.extend([tuple(c-r-h),tuple(c+r-h),tuple(c+r+h),tuple(c-r+h)])
 f=[(3,2,1,0),(4,5,6,7)]+[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)]
 return mesh(name,v,f,role,mat)
def ribbon(name,pts,widths,thickness,role,mat):
 """One continuous actual Blender Mesh with shared station vertices."""
 assert len(pts)==len(widths)
 v=[]
 for i,p in enumerate(pts):
  delta=Vector(pts[min(len(pts)-1,i+1)])-Vector(pts[max(0,i-1)])
  lat=Vector((-delta.y,delta.x,0))
  if lat.length<.001:lat=Vector((1,0,0))
  lat.normalize();side=lat*widths[i]*.5
  q=Vector(p);down=Vector((0,0,thickness))
  v.extend([tuple(q-side-down),tuple(q+side-down),tuple(q+side),tuple(q-side)])
 f=[(0,1,2,3),(len(v)-4,len(v)-3,len(v)-2,len(v)-1)]
 for i in range(len(pts)-1):
  for j in range(4):
   k=(j+1)%4;f.append((4*i+j,4*i+k,4*(i+1)+k,4*(i+1)+j))
 obj=mesh(name,v,f,role,mat);obj["shared_top_spine_quads"]=len(pts)-1
 assert len(obj.data.vertices)==len(pts)*4
 for i in range(len(pts)-1):
  expected={4*i+2,4*i+3,4*i+6,4*i+7}
  assert any(set(p.vertices)==expected for p in obj.data.polygons)
 return obj
def orbitpoly(cx,cy,rx,ry,n=9,t=0):
 return [(cx+rx*(1+.12*sin(i*1.7+t))*cos(2*pi*i/n+t),
          cy+ry*(1+.10*cos(i*2.4+t))*sin(2*pi*i/n+t)) for i in range(n)]
# Central intentionally OPEN city canyon: no enclosing "arena" roof or opaque rim.
# DISTRICTS: six DIFFERENT volumetric neighborhoods at four altitudes.
# Each has an entry port, habitable 3D terraced floor(s), exposed public worlds,
# and linked interior 'transfer' with non-ordinary public program.
DISTRICTS=[
 ("D01_ORIGIN_CAVERN",(-340,-340),60,240,160,3,0.3),
 ("D02_TIDE_GARDEN",(345,-270),90,210,165,4,1.05),
 ("D03_OVERHANG_COMMUNE",(-305,85),245,240,215,4,2.24),
 ("D04_SKYWEAVE",(310,205),365,215,185,4,.48),
 ("D05_HANGING_FOREST",(-170,425),440,155,185,3,1.57),
 ("D06_VERTICAL_HARBOR",(90,490),515,225,140,3,2.72)]
# This study measures a connected URBAN-ACCESS proxy, not complete all-body
# walkability: horizontal surface endpoints and explicit multi-level lift links.
nodes=[]
for idx,(name,(X,Y),Z,rx,ry,levels,phase) in enumerate(DISTRICTS):
 # Occupied district is not a single solid monolith. Deep terrace bands stand
 # around a deliberately OPEN interior social void (210m class).
 angles=[phase+i*2*pi/9 for i in range(10)]
 for lev in range(levels):
  zz=Z+lev*41
  for j in range(7):
   angle=angles[j]
   a0=angle;a1=angles[j+1]
   # true thickness and exposed floor section, not painted tiny window rows
   outline=[
    (X+rx*.38*cos(a0),Y+ry*.32*sin(a0)),
    (X+rx*cos(a0),Y+ry*sin(a0)),
    (X+rx*cos(a1),Y+ry*sin(a1)),
    (X+rx*.38*cos(a1),Y+ry*.32*sin(a1))]
   solid(name+"_INHABITED_DISTRICT_SECTOR_"+str(lev)+"_"+str(j),outline,
     zz-20,zz+12,"multi_level_inhabited_open_precinct_floor",
     "ivory" if (lev+j+idx)%3 else "skyline")
 # Inside the same real district a large open civic world rather than a bookcase
 # or an auditorium; open center, hanging gardens, bridges, water reflections.
 solid(name+"_INTERIOR_PUBLIC_COURT",
  orbitpoly(X,Y,rx*.34,ry*.31,11,phase),Z+6,Z+14,
  "distinct_open_public_world",["water","green","path"][idx%3])
 for j in range(4):
  theta=phase+j*pi/2
  beam(name+"_INTERIOR_CROSS_WALK_"+str(j),
    (X+rx*.29*cos(theta),Y+ry*.28*sin(theta),Z+25),
    (X+rx*.79*cos(theta),Y+ry*.72*sin(theta),Z+28),
    14,10,"internal_promenade_with_measured_endpoints","path")
  x=X+rx*.89*cos(theta);y=Y+ry*.80*sin(theta)
  beam(name+"_LOCAL_VERTICAL_HABITATION_"+str(j),
   (x,y,Z-25),(x,y,Z+levels*41+60),23,38,
   "vertical_district_spatial_landmark","deep")
  for level in range(levels):
   h=Z+level*41+14
   beam(name+"_CROSS_SECTION_CITY_LEDGE_"+str(j)+"_"+str(level),
    (x-23,y-22,h),(x+24,y+23,h),26,11,
    "exposed_inhabited_multilevel_urban_section","copper")
 # Split nonparallel shell caps deliberately DO NOT close the central civic void
 ribbon(name+"_INHABITED_SKY_CREST",
    [(X-190,Y+ry*.8,Z+levels*41+65),
     (X-75,Y+ry*.95,Z+levels*41+110),
     (X+110,Y+ry*.83,Z+levels*41+78)],
    [50,90,60],18,"occupied_fractured_crown_not_an_opaque_roof","light")
 nodes.append({"name":name,"center":[X,Y,Z+19],"entry":[X+rx*.83,Y,Z+28],
               "height_m":Z,"levels":levels,"rx":rx,"ry":ry})
# The urban canyon between physical precinct masses must remain open: all
# transfer beams DEFINED by real endpoints through free civic space.
# Levels do not falsely pretend to be physically walkable via inclined strips.
links=[
 (0,1,"TIDE_BOULEVARD"),
 (0,2,"OVERHANG_RISE"),
 (1,3,"GLASS_CROSSING"),
 (2,3,"CIVIC_AIR_SUSPENSION"),
 (2,4,"NORTHERN_SKY_GROVE"),
 (3,5,"NORTHERN_UMBRA_SPAN"),
 (4,5,"CROWN_CORRIDOR")]
link_records=[]
for i,j,name in links:
 a=nodes[i]["entry"];b=nodes[j]["entry"]
 rise=abs(a[2]-b[2]);length=math.hypot(b[0]-a[0],b[1]-a[1])
 # Both an actual transfer bridge surface and visible level-change mechanism.
 # A lift domain is a vertical transit element, not a fantasy walkable slope.
 if rise<42:
  ribbon("WORLD_LINK_"+name,[a,b],[36,38],12,
    "shared_floor_connected_city_route_proxy","path")
  method="level_route_rough"
 else:
  ax,ay,az=a;bx,by,bz=b;h=max(az,bz)+25
  beam("WORLD_LINK_"+name+"_UPPER_ACCESS",(ax,ay,az),(ax,ay,h),
        36,32,"vertical_access_lift_shaft_geometry_not_certified","deep")
  beam("WORLD_LINK_"+name+"_UPPER_TRAVERSE",(ax,ay,h),(bx,by,h),
        32,18,"high_city_route_physical_bridge","path")
  beam("WORLD_LINK_"+name+"_LOWER_LIFT",(bx,by,bz),(bx,by,h),
        36,32,"vertical_access_lift_shaft_geometry_not_certified","deep")
  method="two_lift_terminals_plus_high_crossing_unverified"
 link_records.append({"from":nodes[i]["name"],"to":nodes[j]["name"],
   "horizontal_separation_m":round(length,2),"level_difference_m":round(rise,2),
   "type":method,"spatial_geometry_created":True,"human_walkability":"NOT_CERTIFIED"})
# A spatial field that stands as a true district-linked giant public void:
# multiple separate worlds visibly face a single breathing urban hollow.
# Avoid adding a heavy roof, bland rock walls or a hollow tube shell.
for k,(a,b) in enumerate([(0,2),(1,3),(2,4),(3,5)]):
 A=nodes[a]["center"];B=nodes[b]["center"]
 t=(k+.25)/4
 beam("CITY_VOID_LONGITUDINAL_HABITABLE_STRUT_"+str(k),
  (A[0]*.7,A[1]+160,A[2]+30),(B[0]*.82,B[1]+170,B[2]+85),
  36,48,"distinct_urban_canyon_transfer_structure","underside")
# public anchors to independent exterior context. No official W0 coordinates.
ribbon("SOUTH_EXTERNAL_STREET",
 [(-400,-620,74),(-320,-545,76),(-155,-450,78)], [78,95,83],18,
 "unverified_city_public_arrival","ivory")
ribbon("NORTH_EXIT_STREET",
 [(60,555,544),(160,690,545),(290,810,550)],[62,78,100],20,
 "unverified_north_city_release","ivory")
# geometric and evidence
scene_meshes=[o for o in bpy.data.objects if o.type=="MESH"]
def model_bounds():
 pp=[o.matrix_world@v.co for o in scene_meshes for v in o.data.vertices]
 return [[round(min(p[i] for p in pp),3) for i in range(3)],
         [round(max(p[i] for p in pp),3) for i in range(3)]]
bounds=model_bounds()
# 5 wide real image views + 3 localized civic-world experiences
sc.render.engine="BLENDER_WORKBENCH";sc.render.resolution_x=1250;sc.render.resolution_y=860
sc.render.resolution_percentage=100;sc.render.image_settings.file_format="PNG"
sc.display.shading.light="STUDIO";sc.display.shading.color_type="MATERIAL"
sc.display.shading.show_shadows=True;sc.display.shading.show_cavity=True
sc.display.shading.cavity_type="BOTH"
def cam_render(name,eye,look,scale,typ="ORTHO"):
 ca=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,ca);sc.collection.objects.link(ob)
 ob.location=Vector(eye);ob.rotation_euler=(Vector(look)-ob.location).to_track_quat("-Z","Y").to_euler()
 ca.type=typ;ca.clip_end=30000
 if typ=="ORTHO":ca.ortho_scale=scale
 else:ca.lens=scale
 sc.camera=ob;outname=out/(name+".png");sc.render.filepath=str(outname)
 bpy.ops.render.render(write_still=True)
 assert outname.exists() and outname.stat().st_size>10000,name
 return {"name":name,"camera":typ,"scale":scale,"bytes":outname.stat().st_size}
center=(0,0,315)
C=[
 ("01_FRONT",(0,-2600,1320),center,1675),
 ("02_OBLIQUE",(1580,-2030,1750),center,1675),
 ("03_SIDE",(2650,0,1440),center,1675),
 ("04_REAR",(0,2600,1500),center,1675),
 ("05_AERIAL",(1600,-1200,2600),center,1675),
 ("06_CIVIC_VOID",(0,-730,470),(0,105,345),750),
 ("07_DISTRICT_INSIDE",(60,150,390),(320,245,415),590),
 ("08_HUMAN_SCALE",(-340,-340,75.7),(50,-10,275),24,"PERSP")]
# Certified ONLY as a correctly measured 1.7m camera above real floor,
# never confuse a low floating viewpoint with human-height perspective.
eye=Vector((-340,-340,75.7))
h,point,norm,face_idx,floor_obj,_=sc.ray_cast(
 bpy.context.evaluated_depsgraph_get(),eye,Vector((0,0,-1)),distance=12)
human_ray={"camera_position_m":list(eye),"hit":bool(h),
 "floor_name":floor_obj.name if floor_obj else None,
 "eye_to_floor_m":round((eye-point).length,5) if h else None}
assert h and abs((eye-point).length-1.7)<.02 and "INTERIOR_PUBLIC_COURT" in floor_obj.name,human_ray
rendered=[cam_render(*v) for v in C]
before=out/"R14_INHABITED_WORLD_PILOT.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(before),compress=True)
glb=out/"R14_INHABITED_WORLD_PILOT.glb"
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB")
triangle_count=sum(sum(max(len(f.vertices)-2,0) for f in o.data.polygons) for o in scene_meshes)
vcount=sum(len(o.data.vertices) for o in scene_meshes)
ev={"schema":"halo9.j7r14.single_real_urban_world_pilot.v1",
 "art_evaluation":"TO_BE_IMAGE_REVIEWED_RESEARCH_ONLY_NOT_ACCEPTED",
 "source":"Blender 4.0+ actual native mesh and Workbench render",
 "model_role":"local_300_to_1000m_urban_world_section_NOT_CENTRAL_ART",
 "coords":"NONCANONICAL_RESEARCH_Z_UP_METERS",
 "Blender_version":bpy.app.version_string,
 "urban_world_count":len(nodes),"actual_nodes":nodes,
 "explicit_access_links":link_records,"link_count":len(links),
 "connected_graph_topologically":True,
 "floor_and_vertical_access":"GEOMETRY_PRESENT_NOT_REAL_WALKABILITY_CERTIFICATION",
 "all_navigable":"NOT_CERTIFIED",
 "human_view_camera_verified":human_ray,
 "true_void_volume":"NOT_MEASURED",
 "main_city_master_completed":False,
 "minecraft_construction":"HOLD",
 "research_bounds":bounds,
 "mesh_count":len(scene_meshes),"vertices":vcount,"triangles":triangle_count,
 "mesh_roles":dict(N),"rendered_views":rendered,
 "native_blend_bytes":before.stat().st_size,"glb_bytes":glb.stat().st_size}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(glb))
n=len([o for o in bpy.data.objects if o.type=="MESH"])
assert n==len(scene_meshes),(n,len(scene_meshes))
ev["reimport_meshes"]=n
(out/"R14_ACTUAL_BLENDER_PILOT_QA.json").write_text(json.dumps(ev,indent=2,ensure_ascii=False),encoding="utf8")
print("J7R14_REAL_BLENDER_PILOT_PASS",json.dumps({"meshes":n,"tri":triangle_count,"views":len(rendered),"nodes":len(nodes),"links":len(links),"spans":[bounds[1][i]-bounds[0][i] for i in range(3)]}))
