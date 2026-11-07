"""Image-led topology and section reauthoring of the saved A0 main meshes."""
import bpy, os, json, bmesh

ROOT=r"C:\Users\ryoma\Projects\CELESTIAL_HALO9\repo_gateb_section_work\studies\M3D-1S\J7\R33-S28\GATE_B_SECTION_FIRST"
SRC=os.path.join(ROOT,"SPATIAL_A0.blend")
OUT=os.path.join(ROOT,"SPATIAL_A1.blend")
IMG=os.path.join(ROOT,"A1")
os.makedirs(IMG,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=SRC)
scene=bpy.context.scene

def face_key(poly): return frozenset(int(i) for i in poly.vertices)

# A0 showed the nave's empty axial ceiling as a roof. Open the saved vaulted
# mesh along its crown, making the 660 m central cleft part of the room itself.
nave=bpy.data.objects["NAVE_ALPHA_WEST_OCCUPIED_VAULT"]
me=nave.data; n=10; ring=2*n; station_count=len(me.vertices)//ring
remove=set()
for s in range(station_count-1):
    a=s*ring; b=(s+1)*ring
    for i in (3,4,5):
        remove.add(frozenset((a+i,a+(i+1)%n,b+(i+1)%n,b+i)))
        remove.add(frozenset((a+n+(i+1)%n,a+n+i,b+n+i,b+n+(i+1)%n)))
for s in (0,station_count-1):
    off=s*ring
    for i in (3,4,5):
        remove.add(frozenset((off+i,off+n+i,off+n+(i+1)%n,off+(i+1)%n)))
before_faces=len(me.polygons)
keep=[tuple(p.vertices) for p in me.polygons if face_key(p) not in remove]
verts=[tuple(v.co) for v in me.vertices]
new=bpy.data.meshes.new("NAVE | reauthored open inhabited crown")
new.from_pydata(verts,[],keep)
for m in me.materials: new.materials.append(m)
bm=bmesh.new(); bm.from_mesh(new); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(new); bm.free(); new.update()
nave.data=new
if me.users==0: bpy.data.meshes.remove(me)
nave_open={"object":nave.name,"faces_before":before_faces,"faces_after":len(new.polygons),
           "crown_faces_removed":before_faces-len(new.polygons),
           "open_width_m":660,"vertices_retained":len(new.vertices)}

# The two A0 horizontal room-crossings read as bands from the fixed NAVE camera.
# Edit their saved mesh coordinates into deeper, partial inhabited galleries.
bridge_edits=[]
for name,xscale,dy,dz in [
    ("NAVE_LEVEL_1_CROSSING",0.54,165,22),
    ("NAVE_LEVEL_2_CROSSING",0.38,315,64),
]:
    obj=bpy.data.objects[name]; old=[v.co.copy() for v in obj.data.vertices]
    for v in obj.data.vertices:
        v.co.x*=xscale; v.co.y+=dy; v.co.z+=dz
    obj.data.update()
    bridge_edits.append({"mesh":name,"vertices":len(old),"x_scale":xscale,
                         "depth_shift_m":dy,"height_shift_m":dz,
                         "vertices_moved_over_1m":sum((old[i]-obj.data.vertices[i].co).length>1 for i in range(len(old)))})

# Move the W0 procession into the west public bay so it reads as an entry route,
# not a foreground platform across the nave camera.
entry=bpy.data.objects["NAVE_W0_PROCESSIONAL_ASCENT"]
entry_before=[v.co.copy() for v in entry.data.vertices]
for v in entry.data.vertices:
    v.co.x-=235; v.co.y+=42
entry.data.update()
entry_edit={"mesh":entry.name,"vertices":len(entry_before),"west_offset_m":-235,"depth_offset_m":42,
            "vertices_moved":sum((entry_before[i]-entry.data.vertices[i].co).length>1 for i in range(len(entry_before)))}

# Reauthor the saved east-alpha body as two lifted inhabited limbs and a rear
# oblique transfer mass. This opens the H1 camera's south-to-north street line;
# the market, school and two court-housing meshes remain the occupied interior.
obj=bpy.data.objects["ALPHA_EAST_LIFTED_H1_LIVING_MASS"]
old_count=len(obj.data.vertices); old_mesh=obj.data
parts=[
    # west raised habitation, varied footprint and sloped top
    ([(1460,400),(1715,455),(1810,690),(1730,970),(1515,1080),(1395,785)],
     [(1530,485),(1690,530),(1760,700),(1700,900),(1550,980),(1480,770)],170,690),
    # east floating habitation, separated by the public rift
    ([(1850,785),(2070,700),(2250,900),(2190,1205),(1970,1340),(1800,1100)],
     [(1905,850),(2050,790),(2160,940),(2100,1150),(1955,1240),(1850,1060)],430,1050),
    # high rear transfer mass; diagonal in section, never a NAVE canopy
    ([(1620,1010),(1840,930),(2025,1065),(1950,1395),(1730,1460),(1580,1245)],
     [(1670,1050),(1855,990),(1980,1105),(1910,1320),(1755,1380),(1635,1225)],650,1280),
]
verts=[]; faces=[]
for base,top,z0,z1 in parts:
    assert len(base)==len(top)
    n=len(base); off=len(verts)
    verts.extend((x,y,z0) for x,y in base)
    verts.extend((x,y,z1) for x,y in top)
    faces.append(tuple(off+i for i in reversed(range(n))))
    faces.append(tuple(off+n+i for i in range(n)))
    for i in range(n):
        j=(i+1)%n
        faces.append((off+i,off+j,off+n+j,off+n+i))
new=bpy.data.meshes.new("ALPHA east | open inhabited section A1")
new.from_pydata(verts,[],faces)
for m in old_mesh.materials: new.materials.append(m)
bm=bmesh.new(); bm.from_mesh(new); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(new); bm.free(); new.update()
obj.data=new
if old_mesh.users==0: bpy.data.meshes.remove(old_mesh)
alpha_edit={"mesh":obj.name,"old_vertices":old_count,"new_vertices":len(new.vertices),
            "topology":"three connected-by-program lifted limbs with a 560 m H1 view slot",
            "clear_H1_centerline_x_m":[620,1180]}

# No camera, W0, light, material, world, exposure, engine or render setting changes.
for n in ("E11_NAVE_HUMAN","E11_H1_HUMAN","E11_URBAN_AERIAL"):
    assert bpy.data.objects[n].type=="CAMERA"
scene.camera=bpy.data.objects["E11_URBAN_AERIAL"]
bpy.ops.wm.save_as_mainfile(filepath=OUT)
render={"engine":scene.render.engine,"resolution":[scene.render.resolution_x,scene.render.resolution_y],
        "samples":scene.cycles.samples if scene.render.engine=="CYCLES" else None,
        "exposure":scene.view_settings.exposure,"view_transform":scene.view_settings.view_transform,
        "look":scene.view_settings.look,"fixed_E11":True,"protected_W0":True,
        "lights_unchanged":True,"cutaway":False,
        "mesh_edits":{"nave_open_crown":nave_open,"crossings":bridge_edits,
                       "entry_route":entry_edit,"alpha_east":alpha_edit}}
for name in ("E11_NAVE_HUMAN","E11_H1_HUMAN","E11_URBAN_AERIAL"):
    scene.camera=bpy.data.objects[name]
    scene.render.filepath=os.path.join(IMG,name+".png")
    bpy.ops.render.render(write_still=True)
with open(os.path.join(IMG,"render.json"),"w",encoding="utf-8") as f:
    json.dump(render,f,ensure_ascii=False,indent=2)
print(json.dumps({"saved":OUT,"mesh_edits":render["mesh_edits"],"render":{k:v for k,v in render.items() if k!="mesh_edits"}},ensure_ascii=False))
