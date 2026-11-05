# CELESTIAL HALO-9 R4-E12 — ART-FIRST negative-space sculpt study
# This is NOT a finished city or an accepted design.
# Opens the exact E11 BLEND COPY, removes its REJECTED repeated tower-floor structures,
# authors an asymmetrical OPEN civic-rift spatial master, renders same three cameras.
# No user machine, Work, GUI, Minecraft, canonical coordinate writes or source BLEND edits.
import bpy,math,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
a=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
out=Path(a[a.index("--output")+1] if "--output" in a else "/tmp/halo9_e12")
out.mkdir(parents=True,exist_ok=True);(out/"renders").mkdir(exist_ok=True)
scene=bpy.context.scene
assert scene["FORMAL_ART_ACCEPTED"]==0 and scene["COMPLETED_TARGETS"]==0
assert scene["CONSTRUCTION"]=="HOLD"
original=Path(bpy.data.filepath)
assert original.exists() and original.name=="E11_INHABITED_SECTION_WORKING.blend"
source_sha=hashlib.sha256(original.read_bytes()).hexdigest()
assert source_sha=="098c46fec0e61b474aba6aab4d2f51a299391937b8c29c6820278565f22a044f"
preserved_cam={n:[list(r) for r in bpy.data.objects[n].matrix_world] for n in
               ("E11_NAVE_HUMAN","E11_H1_HUMAN","E11_URBAN_AERIAL")}
# Critical remove: previous tower repetitious strips and uniform band facades.
# Do NOT erase useful public interior work, H1 portal, waterfront, human markers.
old_roots=("M247_WEST_ASCENDING_CITY","M247_EAST_TIDAL_BUTTRESS_CITY",
           "M247_DISPLACED_NORTH_CROWN")
h1_roots=("H1_WEST_LIBRARY_WING","H1_EAST_RESIDENTIAL_RISE",
          "H1_NORTH_SCHOOL_CRESCENT")
removed=[]
for obj in tuple(scene.objects):
    if obj.type not in {"MESH","CURVE"}:continue
    if any(obj.name.startswith(root) for root in old_roots+h1_roots):
        removed.append(obj.name);bpy.data.objects.remove(obj,do_unlink=True)
assert len(removed)>=130, ("did not remove existing repetitious mass",len(removed))
sculpt_collection=bpy.data.collections.new("E12_SUBTRACTIVE_CIVIC_MASTER_UNAPPROVED")
scene.collection.children.link(sculpt_collection)
mats=bpy.data.materials
def material(name, rgb, metallic=0.1, rough=0.55):
    m=mats.get(name)
    if m:return m
    m=mats.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True
    node=m.node_tree.nodes.get("Principled BSDF")
    node.inputs["Base Color"].default_value=(*rgb,1)
    node.inputs["Metallic"].default_value=metallic
    node.inputs["Roughness"].default_value=rough
    return m
P={"bone":material("E12_BONE_CERAMIC",(.76,.71,.61),.15),
   "cinder":material("E12_DARK_STRUCTURAL_STONE",(.16,.21,.25),.26),
   "bronze":material("E12_TARNISHED_BRONZE",(.51,.38,.21),.66,.38),
   "skyglass":material("E12_SKY_GLAZING",(.12,.42,.49),.49,.27),
   "garden":material("E12_INHABITED_GARDEN",(.20,.40,.27),0,.89),
   "floor":material("E12_PUBLIC_ROOM_PAVING",(.63,.61,.53),0,.72)}
def mesho(name, verts, faces, key):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
    o=bpy.data.objects.new(name,me);sculpt_collection.objects.link(o)
    o.data.materials.append(P[key]);return o
def loft(name, rings,key):
    count=len(rings[0])
    assert all(len(r)==count for r in rings)
    verts=[xyz for ring in rings for xyz in ring]
    faces=[tuple(reversed(range(count))),tuple(range((len(rings)-1)*count,len(rings)*count))]
    for i in range(len(rings)-1):
        for j in range(count):
            a=i*count+j;b=i*count+(j+1)%count
            faces.append((a,b,b+count,a+count))
    return mesho(name,verts,faces,key)
def cut(target,name, center, dims, bevel=0):
    prior=len(target.data.polygons)
    bpy.ops.mesh.primitive_cube_add(size=1,location=center)
    cutter=bpy.context.object;cutter.name="_E12_TEMP_BOOLEAN_"+name
    cutter.scale=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=cutter.modifiers.new("Open public vault geometry","BEVEL")
        mod.width=bevel;mod.segments=6
        bpy.context.view_layer.objects.active=cutter
        bpy.ops.object.modifier_apply(modifier=mod.name)
    mod=target.modifiers.new("PUBLIC_VOID_"+name,"BOOLEAN")
    mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    bpy.context.view_layer.objects.active=target
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True)
    return dict(name=name,target=target.name,faces_before=prior,faces_after=len(target.data.polygons))
def thick_curve(name, path,width,depth,key):
    n=len(path);v=[]
    for i,(x,y,z) in enumerate(path):
        a=Vector(path[max(0,i-1)]);b=Vector(path[min(n-1,i+1)])
        d=b-a;xy=math.hypot(d.x,d.y);ux,uy=((-d.y/xy,d.x/xy) if xy>1e-6 else (1.0,0.0))
        for zz in (z,z-depth):
            v.extend(((x-ux*width/2,y-uy*width/2,zz),(x+ux*width/2,y+uy*width/2,zz)))
    fs=[]
    for i in range(n-1):
        a=4*i;b=4*(i+1)
        fs.extend(((a,a+1,b+1,b),(a+2,b+2,b+3,a+3),
                   (a,b,b+2,a+2),(a+1,a+3,b+3,b+1)))
    fs.extend(((0,2,3,1),(4*(n-1),4*(n-1)+1,4*(n-1)+3,4*(n-1)+2)))
    return mesho(name,v,fs,key)
# Spatial design: a low, horizontally cantilevered southern INHABITED buttress,
# a displaced west horizon, and a much smaller east elevated community,
# NOT three striped vertical towers / repeated floor stacks.
west=loft("E12_WEST_TIDAL_INHABITED_RIFT",[
    [(-650,-410,52),(-395,-455,52),(-240,-280,52),(-280,-80,52),(-415,70,52),(-240,230,52),(-560,400,52),(-755,185,52)],
    [(-685,-360,190),(-390,-400,190),(-205,-245,190),(-265,-60,190),(-395,90,190),(-185,285,190),(-580,460,190),(-830,175,190)],
    [(-690,-315,380),(-360,-340,380),(-180,-200,380),(-235,25,380),(-350,145,380),(-130,335,380),(-610,510,380),(-860,230,380)],
    [(-760,-240,630),(-370,-245,630),(-110,-135,630),(-185,60,630),(-325,165,630),(-60,430,630),(-640,570,630),(-950,275,630)],
    [(-840,-185,820),(-420,-220,820),(-170,-80,820),(-210,110,820),(-360,190,820),(-50,490,820),(-680,620,820),(-1090,300,820)],
    [(-960,-135,930),(-470,-170,930),(-185,-30,930),(-225,165,930),(-405,255,930),(-100,520,930),(-730,650,930),(-1180,360,930)]
], "bone")
east=loft("E12_EAST_ELEVATED_PUBLIC_CREST",[
    [(185,-280,55),(430,-340,55),(640,-220,55),(655,45,55),(570,250,55),(360,330,55),(170,145,55),(140,-90,55)],
    [(220,-290,185),(470,-375,185),(735,-215,185),(690,65,185),(625,300,185),(395,400,185),(180,165,185),(140,-100,185)],
    [(255,-240,365),(575,-350,365),(900,-140,365),(795,110,365),(715,380,365),(410,470,365),(210,195,365),(200,-85,365)],
    [(280,-180,550),(660,-280,550),(1030,-60,550),(950,160,550),(840,430,550),(455,530,550),(260,255,550),(240,-20,550)],
    [(325,-110,720),(730,-245,720),(1160,55,720),(1040,220,720),(925,475,720),(510,590,720),(310,335,720),(300,35,720)]
],"cinder")
cuts=[
cut(west,"WEST_LOW_CIVIC_HOLLOW",(-495,-180,260),(900,390,330),65),
cut(west,"WEST_SKY_PUBLIC_BREAK",(-580,320,650),(1000,320,280),53),
cut(east,"EAST_WATER_ARCHIVE_VOID",(575,-100,250),(820,365,300),80),
cut(east,"EAST_H1_CITY_GATE",(700,280,520),(920,390,280),65)]
# One suspended inhabited diagonal over the NORTH end of the public NAVE void.
thick_curve("E12_DIAGONAL_CITY_PROMENADE",[
 (-620,330,525),(-470,360,570),(-270,390,630),(-60,420,690),
 (165,475,748),(380,500,765),(660,560,750)],56,18,"bronze")
# Four DIFFERENT public city-room levels. Avoid 10m stacked strip repetition.
thick_curve("E12_NAVE_WEST_INSIDE_PUBLIC_BALCONY",[
 (-420,-210,186),(-350,-80,213),(-275,70,260),(-240,190,318),
 (-175,340,392)],38,10,"floor")
thick_curve("E12_NAVE_EAST_WATER_ARCHIVE_GALLERY",[
 (270,-280,201),(345,-160,238),(380,-10,290),
 (355,140,355),(300,290,431)],44,13,"bronze")
# Truly spatial H1 places, four non-identical occupied bodies around surviving R2 portal.
h1=loft("E12_H1_LIBRARY_AND_SCHOOL_CIVIC_QUARTER",[
 [(515,340,436),(620,320,436),(680,370,436),(685,505,436),(600,575,436),(510,525,436)],
 [(510,335,490),(630,330,490),(710,395,490),(700,515,490),(610,600,490),(515,540,490)],
 [(520,370,565),(620,360,565),(720,430,565),(695,570,565),(625,650,565),(525,560,565)],
 [(550,410,635),(635,395,635),(710,460,635),(665,580,635),(610,650,635),(540,555,635)]
],"bone")
cuts.append(cut(h1,"H1_PUBLIC_CLASSROOM_ATRIUM",(610,480,505),(210,210,120),19))
for n,path,w,d,m in [
 ("E12_H1_CROSS_COURTYARD",[(720,290,441),(755,370,443),(780,475,455),(840,550,475)],25,8,"floor"),
 ("E12_H1_NORTH_RESIDENTIAL_RAMP",[(805,535,445),(900,570,475),(970,615,510)],24,8,"bronze"),
 ("E12_NAVE_W0_EAST_SEA_GATE",[(125,-490,69),(220,-535,68),(300,-555,63),(400,-625,50)],36,8,"floor")]:
    thick_curve(n,path,w,d,m)
# research quality; not fake detailed city
assert scene.camera is not None
scene["E12_ART_STATUS"]="UNREVIEWED_NOT_ADOPTED"
scene["E12_METHOD"]="TRUE_EDITABLE_BLENDER_STUDY_REJECTED_E11_TOWER_BANDS_REMOVED"
scene["E12_E11_SOURCE_SHA256"]=source_sha
scene["E12_REMOVED_REJECTED_MESHES"]=len(removed)
scene["E12_REAL_CARVINGS"]=len(cuts)
scene["FORMAL_ART_ACCEPTED"]=0
scene["COMPLETED_TARGETS"]=0
scene["CONSTRUCTION"]="HOLD"
for name,transform in preserved_cam.items():
    bpy.context.view_layer.update()
    assert all(abs(bpy.data.objects[name].matrix_world[r][c]-transform[r][c])<1e-6 for r in range(4) for c in range(4))
scene.render.engine='CYCLES'
scene.cycles.samples=14
scene.render.threads_mode='FIXED';scene.render.threads=2
scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
dest=out/"E12_SUBTRACTIVE_CIVIC_RIFT_WORKING.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
views=["E11_NAVE_HUMAN","E11_H1_HUMAN","E11_URBAN_AERIAL"]
for name in views:
    scene.camera=bpy.data.objects[name]
    scene.render.filepath=str(out/"renders"/(name+".png"))
    bpy.ops.render.render(write_still=True)
    print("E12_REAL_RENDER",name,flush=True)
scene.camera=bpy.data.objects["E11_URBAN_AERIAL"]
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
info={"schema":"halo9-e12-art-first-subtractive-v1",
  "research_source":source_sha,"new_blend_sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),
  "removed_rejected_meshes":len(removed),"carved_public_voids":cuts,
  "mesh_count":sum(o.type=="MESH" for o in scene.objects),
  "same_cameras":views,"formal_art_adoptions":0,"completed_targets":0,
  "minecraft":"HOLD","art":"UNREVIEWED_NO_PASS",
  "png_sha256":{n:hashlib.sha256((out/"renders"/(n+".png")).read_bytes()).hexdigest() for n in views}}
(out/"E12_AUTHOR_REPORT.json").write_text(json.dumps(info,indent=2))
print("E12_REAL_NATIVE_COMPLETE",json.dumps(info),flush=True)
