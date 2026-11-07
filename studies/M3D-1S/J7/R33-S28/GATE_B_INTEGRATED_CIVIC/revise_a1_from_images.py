"""Image-led large-scale vertex revision of the saved A0 meshes."""
import bpy, math, os, json
from mathutils import Vector

ROOT = r"C:\Users\ryoma\Projects\CELESTIAL_HALO9\repo\studies\M3D-1S\J7\R33-S28\GATE_B_INTEGRATED_CIVIC"
SRC = os.path.join(ROOT, "AUTHORING_A0.blend")
OUT = os.path.join(ROOT, "AUTHORING_A1.blend")
IMG = os.path.join(ROOT, "A1")
os.makedirs(IMG, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=SRC)
scene = bpy.context.scene

PROFILE = [(-0.78, -0.18), (-0.55, -0.67), (0.18, -0.79),
           (0.83, -0.32), (1.0, 0.08), (0.49, 0.31),
           (0.10, 0.88), (-0.64, 0.54)]

def reshape(name, stations, phase=0.0):
    """Reposition every saved control ring vertex in-place; preserve topology."""
    obj = bpy.data.objects[name]
    mesh = obj.data
    count = len(PROFILE)
    assert len(mesh.vertices) == len(stations)*count, (name, len(mesh.vertices))
    before = [v.co.copy() for v in mesh.vertices]
    for i, (x,y,z,width,height,twist) in enumerate(stations):
        a = math.radians(twist + phase)
        ca, sa = math.cos(a), math.sin(a)
        if i == 0:
            dx,dy=stations[1][0]-x,stations[1][1]-y
        elif i == len(stations)-1:
            dx,dy=x-stations[i-1][0],y-stations[i-1][1]
        else:
            dx,dy=stations[i+1][0]-stations[i-1][0],stations[i+1][1]-stations[i-1][1]
        ln=max(1e-6,math.hypot(dx,dy)); nx,ny=-dy/ln,dx/ln
        for k,(u,v) in enumerate(PROFILE):
            ur,vr=u*ca-v*sa,u*sa+v*ca
            mesh.vertices[i*count+k].co=(x+nx*ur*width,y+ny*ur*width,z+vr*height)
    mesh.update()
    changed=sum((before[i]-mesh.vertices[i].co).length>1.0 for i in range(len(before)))
    return {"mesh":name,"vertices":len(before),"vertices_moved_over_1m":changed,
            "bbox_dimensions":[round(v,1) for v in obj.dimensions]}

# Fold the west alpha mass upward off the escarpment so its end no longer
# sweeps into the human view as a low canopy edge.
changes=[]
changes.append(reshape("M247C_ALPHA_WEST_ANCHORED_MASS", [
    (-1630,1020,180,420,235,-14),
    (-1430,890,380,455,300,9),
    (-1170,750,610,430,360,20),
    (-980,600,810,355,330,-6),
    (-850,460,555,270,255,-25),
]))

# Move the second alpha mass to the far eastern edge and turn it into a steep
# lifted flank. This reopens the fixed H1 sight cone around (760,270,439).
changes.append(reshape("M247C_ALPHA_EAST_SEVERED_MASS", [
    (2260,1260,300,410,250,15),
    (2130,1050,510,435,320,1),
    (1980,835,850,390,340,16),
    (1780,620,1250,350,320,34),
    (1480,410,1650,300,280,49),
], 4.0))

# The image showed a lid. Replace that horizontal traverse in place with the
# steep beta sky spine behind the civic room, rising out of the western mass to
# meet the elevated east fragment. It remains a thick, inhabited body.
changes.append(reshape("M247C_BETA_OBLIQUE_INHABITED_RIDGE", [
    (-1120,1210,610,275,225,-28),
    (-900,1210,850,310,245,-17),
    (-640,1190,1150,350,270,-2),
    (-360,1150,1510,390,300,15),
    (-80,1100,1920,420,325,29),
    (280,1030,2310,370,300,43),
], -8.0))

# Rebuild the saved lower route as an ascending inhabited shoulder inside H1.
# The camera-side crossing plank was the foreground obstruction in E11 NAVE.
changes.append(reshape("H1_NAVE_PUBLIC_SHOULDER", [
    (620,490,28,125,42,-22),
    (565,610,66,145,46,-10),
    (560,760,126,155,48,10),
    (625,900,195,142,52,27),
]))

# Lift and rotate the upper connection into a steep public stair/street spine;
# keep it on the H1 side of the court rather than crossing the NAVE.
changes.append(reshape("H1_UPPER_COURT_CONNECTION", [
    (1120,1080,690,145,72,18),
    (1080,1030,585,155,68,27),
    (1010,960,475,160,64,35),
    (920,880,375,150,58,43),
    (850,820,305,130,50,52),
], 8.0))

# Return to the same fixed E11 frame and source lighting. No new object,
# camera, light, material, or scene setting is introduced in this revision.
for cam in ("E11_NAVE_HUMAN","E11_H1_HUMAN","E11_URBAN_AERIAL"):
    assert bpy.data.objects[cam].type == "CAMERA"
scene.camera=bpy.data.objects["E11_URBAN_AERIAL"]
bpy.ops.wm.save_as_mainfile(filepath=OUT)
render={"engine":scene.render.engine,"resolution":[scene.render.resolution_x,scene.render.resolution_y],
        "samples":scene.cycles.samples if scene.render.engine=="CYCLES" else None,
        "exposure":scene.view_settings.exposure,"cutaway":False,"lighting_unchanged":True,
        "fixed_E11_cameras":True,"changes":changes}
for name in ("E11_NAVE_HUMAN","E11_H1_HUMAN","E11_URBAN_AERIAL"):
    scene.camera=bpy.data.objects[name]
    scene.render.filepath=os.path.join(IMG,name+".png")
    bpy.ops.render.render(write_still=True)
with open(os.path.join(IMG,"render.json"),"w",encoding="utf-8") as f:
    json.dump(render,f,ensure_ascii=False,indent=2)
print(json.dumps({"saved":OUT,"mesh_revisions":changes,"render":render},ensure_ascii=False))
