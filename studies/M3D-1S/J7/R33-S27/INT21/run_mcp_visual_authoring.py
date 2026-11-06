"""INT21: live visual MCP loop, TWO true views around ONE authored 3D revision.

This is a single image-grounded edit to existing geometry, not a scripted
automatic art-approval or a random candidate generator.
"""
import hashlib, json, socket
from pathlib import Path
from PIL import Image, ImageChops, ImageStat

SRC=Path("/tmp/INT21_SOURCE.blend")
OUT=Path("/tmp/halo9-int21")
ROOT=Path("studies/M3D-1S/J7/R33-S27/INT21")
OUT.mkdir(parents=True,exist_ok=True)
SHA="e996fab613904dc557638612d4380ba67ef5c6bbd4aa9fb219d9aeaa8f511fb9"
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==SHA

def call(cmd,params=None):
    payload=json.dumps({"type":cmd,"params":params or {}},ensure_ascii=False).encode()
    with socket.create_connection(("127.0.0.1",9876),timeout=20) as sock:
        sock.settimeout(120)
        sock.sendall(payload)
        buf=b""
        while True:
            part=sock.recv(1024*1024)
            if not part:break
            buf+=part
            assert len(buf)<6*1024*1024, "UNSAFE_MCP_RESPONSE"
            try:
                ans=json.loads(buf.decode("utf-8"))
                break
            except (json.JSONDecodeError,UnicodeDecodeError):
                continue
    ans=json.loads(buf.decode("utf-8"))
    if ans.get("status")!="success":raise RuntimeError((cmd,ans))
    r=ans.get("result")
    if isinstance(r,dict) and r.get("error"):raise RuntimeError((cmd,r))
    return r

init="""import bpy
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath='/tmp/INT21_SOURCE.blend',load_ui=False)
sc=bpy.context.scene
assert sc['CONSTRUCTION']=='HOLD' and sc['FORMAL_ART_ACCEPTED']==sc['COMPLETED_TARGETS']==0
w=bpy.context.window_manager.windows[0]
area=next((a for a in w.screen.areas if a.type=='VIEW_3D'),None)
assert area is not None
sc.camera=bpy.data.objects['E11_URBAN_AERIAL']
area.spaces.active.region_3d.view_perspective='CAMERA'
area.spaces.active.shading.type='SOLID'
area.spaces.active.overlay.show_overlays=False
area.tag_redraw()
print('INT21_ACTUAL_CITY_OPENED_FOR_VISUAL_AUTHORING',len(sc.objects),flush=True)
"""
start=call("execute_code",{"code":init})
assert "INT21_ACTUAL_CITY_OPENED_FOR_VISUAL_AUTHORING" in start["result"]

def screenshot(filename):
    p=OUT/filename
    r=call("get_viewport_screenshot",{
        "filepath":str(p),"max_size":1100,"format":"png"})
    assert r.get("success") and p.stat().st_size>10000,(filename,r)
    im=Image.open(p).convert("RGB")
    std=ImageStat.Stat(im.convert("L")).stddev[0]
    assert im.width>700 and im.height>300 and std>10,(filename,std)
    return im

before=screenshot("INT21_MCP_BEFORE_OPEN_CANYON.png")
# Execute ONLY the reviewed, version-controlled geometry-matrix script.
# No new geometry and no direct unreviewed network code in this command.
filepath=ROOT/"author_existing_civic_masses_visual_revision.py"
command="exec(compile(open("+repr(str(filepath))+",encoding='utf8').read(),"+repr(str(filepath))+",'exec'))"
after_status=call("execute_code",{"code":command})
assert "INT21_TRUE_LIVE_MCP_EXISTING_CITY_MACRO_RECOMPOSED_ART_UNREVIEWED" in after_status["result"],after_status
after=screenshot("INT21_MCP_AFTER_OPEN_CANYON.png")
a=before.resize(after.size)
diff=ImageChops.difference(a,after)
bbox=diff.getbbox()
assert bbox is not None and len(diff.getcolors(maxcolors=16000000) or [])>20,"UNCHANGED_IMAGE"
metadata=json.loads((OUT/"INT21_LIVE_MCP_GEOMETRY_EVIDENCE.json").read_text())
metadata.update({
    "mcp_real_blender_visual_before_sha256":hashlib.sha256((OUT/"INT21_MCP_BEFORE_OPEN_CANYON.png").read_bytes()).hexdigest(),
    "mcp_real_blender_visual_after_sha256":hashlib.sha256((OUT/"INT21_MCP_AFTER_OPEN_CANYON.png").read_bytes()).hexdigest(),
    "mcp_before_after_pixel_diff_bbox":bbox,
    "mcp_source":"pinned_digitable_lol_blender_mcp_ae010efa",
    "mcp_gui_images_both_nonblack":True,
    "visual_art_review":"REQUIRED_HUMAN_IMAGE_JUDGMENT",
    "art":"UNREVIEWED_NOT_ADOPTED",
})
(OUT/"INT21_LIVE_MCP_GEOMETRY_EVIDENCE.json").write_text(json.dumps(metadata,indent=2))
print("INT21_LIVE_VISUAL_MCP_BEFORE_AFTER_AND_TRUE_EDIT_COMPLETE_NOT_ART",len(metadata["authored_macro_movements"]),flush=True)
