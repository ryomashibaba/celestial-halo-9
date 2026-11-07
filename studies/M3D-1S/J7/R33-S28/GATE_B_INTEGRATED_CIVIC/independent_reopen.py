"""Independent-process preservation check for the Gate B A1 study copy."""
import bpy, os, json, hashlib

ROOT = r"C:\Users\ryoma\Projects\CELESTIAL_HALO9\repo\studies\M3D-1S\J7\R33-S28\GATE_B_INTEGRATED_CIVIC"
BASE = os.path.join(ROOT, "BASELINE_INT21.blend")
A1 = os.path.join(ROOT, "AUTHORING_A1.blend")
ORIGINAL = r"C:\Users\ryoma\Projects\CELESTIAL_HALO9\repo\studies\M3D-1S\J7\R33-S27\GATE_B_AFTER_INT21\reference\HALO9_INT21_M247C_OPEN_CIVIC_CANYON_RESEARCH.blend"
OUT = os.path.join(ROOT, "INDEPENDENT_REOPEN.json")
W0 = ["W0_NORTH_FRACTURED_RANGE","W0_WEST_BASALT_ESCARPMENT","W0_GROUND_BASIN","W0_EASTERN_ARTIFICIAL_SEA"]
E11 = ["E11_NAVE_HUMAN","E11_H1_HUMAN","E11_URBAN_AERIAL","E11_WATER_APPROACH","E11_REVERSE"]

def digest_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""): h.update(block)
    return h.hexdigest()

def snap(path):
    bpy.ops.wm.open_mainfile(filepath=path)
    def mesh_hash(obj):
        payload={"v":[tuple(round(float(c),6) for c in v.co) for v in obj.data.vertices],
                 "p":[tuple(p.vertices) for p in obj.data.polygons],
                 "m":[[round(float(c),7) for c in row] for row in obj.matrix_world]}
        return hashlib.sha256(json.dumps(payload,separators=(",",":"),sort_keys=True).encode()).hexdigest()
    w={n:mesh_hash(bpy.data.objects[n]) for n in W0}
    cams={}
    for n in E11:
        o=bpy.data.objects[n]
        cams[n]={"matrix":[[round(float(c),7) for c in row] for row in o.matrix_world],
                 "lens":o.data.lens,"sensor_width":o.data.sensor_width,"clip_end":o.data.clip_end}
    lights={}
    for o in bpy.data.objects:
        if o.type=="LIGHT":
            lights[o.name]={"type":o.data.type,"energy":o.data.energy,
                            "color":[round(float(x),7) for x in o.data.color],
                            "shape":getattr(o.data,"shape",None),"size":getattr(o.data,"size",None),
                            "size_y":getattr(o.data,"size_y",None),"angle":getattr(o.data,"angle",None),
                            "matrix":[[round(float(c),7) for c in row] for row in o.matrix_world]}
    s=bpy.context.scene
    settings={"engine":s.render.engine,"resolution":[s.render.resolution_x,s.render.resolution_y],
              "samples":s.cycles.samples if s.render.engine=="CYCLES" else None,
              "exposure":s.view_settings.exposure,"view_transform":s.view_settings.view_transform,
              "look":s.view_settings.look}
    return {"file":bpy.data.filepath,"w0":w,"e11":cams,"lights":lights,"settings":settings,
            "objects":[o.name for o in bpy.data.objects]}

before=snap(BASE)
after=snap(A1)
report={"background_process":bool(bpy.app.background),"independent_pid":os.getpid(),
        "original_sha256":digest_file(ORIGINAL),"baseline_sha256":digest_file(BASE),
        "baseline_matches_original":digest_file(ORIGINAL)==digest_file(BASE),"a1_sha256":digest_file(A1),
        "w0_unchanged":before["w0"]==after["w0"],"e11_cameras_unchanged":before["e11"]==after["e11"],
        "lights_unchanged":before["lights"]==after["lights"],
        "render_conditions_unchanged":before["settings"]==after["settings"],
        "checks":{"w0":before["w0"],"e11":before["e11"],"lights":before["lights"],
                  "settings":after["settings"],"a1_objects":after["objects"]}}
report["all_preservation_checks_pass"] = all(report[k] for k in
    ("w0_unchanged","e11_cameras_unchanged","lights_unchanged","render_conditions_unchanged"))
with open(OUT,"w",encoding="utf-8") as f: json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps({k:report[k] for k in ("background_process","independent_pid","original_sha256","baseline_sha256",
      "baseline_matches_original","a1_sha256",
      "w0_unchanged","e11_cameras_unchanged","lights_unchanged","render_conditions_unchanged",
      "all_preservation_checks_pass")},ensure_ascii=False))
if not report["all_preservation_checks_pass"]: raise RuntimeError("Protected W0/E11 or scene settings changed")
