"""INT21: separate Blender process, 3 unchanged E11 cameras × both scene states.

This is a technical oracle only; art acceptance is a subsequent DIRECT
IMAGE judgement, never inferred from vertex / matrix / screenshot metrics.
"""
import bpy, hashlib, json, sys
from pathlib import Path

argv=sys.argv[sys.argv.index("--")+1:]
phase=argv[argv.index("--phase")+1]
assert phase in ("before","after"),phase
out=Path("/tmp/halo9-int21")
p=Path(bpy.data.filepath)
report=json.loads((out/"INT21_LIVE_MCP_GEOMETRY_EVIDENCE.json").read_text())
if phase=="before":
    assert p.name=="INT21_SOURCE.blend"
    assert hashlib.sha256(p.read_bytes()).hexdigest()==report["source_sha256"]
else:
    assert p.name=="HALO9_INT21_M247C_OPEN_CIVIC_CANYON_RESEARCH.blend"
    assert hashlib.sha256(p.read_bytes()).hexdigest()==report["saved_blend_sha256"]
sc=bpy.context.scene
assert sc['CONSTRUCTION']=='HOLD'
assert sc['COMPLETED_TARGETS']==sc['FORMAL_ART_ACCEPTED']==0

for name,mat in report["E11_fixed_original"].items():
    actual=bpy.data.objects[name].matrix_world
    assert max(abs(actual[i][j]-mat[i][j]) for i in range(4) for j in range(4))<1e-6,name
for name,evidence in report["W0_before"].items():
    obj=bpy.data.objects[name]
    def fingerprint(ob):
        h=hashlib.sha256()
        for v in ob.data.vertices:
            h.update((",".join(f"{float(x):.10g}" for x in v.co)+";").encode())
        return h.hexdigest()
    assert fingerprint(obj)==evidence["vertex_sha"],name
    assert max(abs(obj.matrix_world[i][j]-evidence["world_matrix"][i][j])
        for i in range(4) for j in range(4))<1e-6,name

for evidence in report["authored_macro_movements"]:
    obj=bpy.data.objects[evidence["name"]]
    matrix=evidence["before_matrix"] if phase=="before" else evidence["after_matrix"]
    assert max(abs(obj.matrix_world[i][j]-matrix[i][j])
        for i in range(4) for j in range(4))<1e-5,evidence["name"]

if phase=="after":
    assert sc["INT21_ART"]=="UNREVIEWED_NOT_ADOPTED"
    assert sc["INT21_MINECRAFT"]=="HOLD"
    assert sc["INT21_METHOD"]=="MCP_NATIVE_MATRIX_EDIT_THREE_EXISTING_MESHES_NOT_GUI_SCULPT"
print("INT21_INDEPENDENT_BLENDER_REOPEN_AND_PROTECTED_W0_E11_PASS",phase,flush=True)

target=out/("render-"+phase)
target.mkdir(parents=True,exist_ok=True)
sc.render.engine="CYCLES"
sc.cycles.device="CPU"
sc.cycles.samples=11
sc.cycles.use_denoising=True
sc.render.threads_mode="FIXED"
sc.render.threads=2
sc.render.resolution_x=800
sc.render.resolution_y=600
sc.render.resolution_percentage=100
sc.render.image_settings.file_format="PNG"
sha={}
for key in ("E11_NAVE_HUMAN","E11_H1_HUMAN","E11_URBAN_AERIAL"):
    sc.camera=bpy.data.objects[key]
    img=target/(key+".png")
    sc.render.filepath=str(img)
    bpy.ops.render.render(write_still=True)
    assert img.stat().st_size>8000
    sha[key]=hashlib.sha256(img.read_bytes()).hexdigest()
    print("INT21_TRUE_UNMASKED_E11_IMAGE",phase,key,img.stat().st_size,flush=True)
(target/"sha256.json").write_text(json.dumps(sha,indent=2))
print("INT21_INDEPENDENT_REAL_E11_COMPLETE",phase,flush=True)
