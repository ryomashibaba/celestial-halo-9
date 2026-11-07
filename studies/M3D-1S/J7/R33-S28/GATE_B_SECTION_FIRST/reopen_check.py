import bpy, json, hashlib, os
p=r"C:\Users\ryoma\Projects\CELESTIAL_HALO9\repo_gateb_section_work\studies\M3D-1S\J7\R33-S28\GATE_B_SECTION_FIRST\SPATIAL_A1.blend"
bpy.ops.wm.open_mainfile(filepath=p)
sc=bpy.context.scene
names=["E11_NAVE_HUMAN","E11_H1_HUMAN","E11_URBAN_AERIAL","W0_NORTH_FRACTURED_RANGE","W0_WEST_BASALT_ESCARPMENT","W0_GROUND_BASIN","W0_EASTERN_ARTIFICIAL_SEA"]
objs={n:bpy.data.objects.get(n) for n in names}
record={"blend":p,"reopened":True,"objects":{n:bool(o) for n,o in objs.items()},
 "cameras":[o.name for o in bpy.data.objects if o.type=="CAMERA" and o.name.startswith("E11_")],
 "lights":sum(o.type=="LIGHT" for o in bpy.data.objects),"meshes":sum(o.type=="MESH" for o in bpy.data.objects),
 "render":{"engine":sc.render.engine,"resolution":[sc.render.resolution_x,sc.render.resolution_y],"samples":sc.cycles.samples,"exposure":sc.view_settings.exposure,"view_transform":sc.view_settings.view_transform,"look":sc.view_settings.look},
 "revised_meshes":{n:len(bpy.data.objects[n].data.vertices) for n in ["NAVE_ALPHA_WEST_OCCUPIED_VAULT","ALPHA_EAST_LIFTED_H1_LIVING_MASS"]}}
out=os.path.join(os.path.dirname(p),"INDEPENDENT_REOPEN.json")
open(out,"w",encoding="utf-8").write(json.dumps(record,ensure_ascii=False,indent=2))
print(json.dumps(record,ensure_ascii=False))
