"""INT20: first GUI-rendered MCP *view* of the authentic protected INT15 BLEND.

Not artwork, not GUI hand-sculpting, not an invitation to mutate originals.
Proves whether patched GPUOffScreen returns nonblack usable 3D viewport pixels,
and whether the same live Blender instance exposes actual source objects.
"""
import hashlib
import json
import os
from pathlib import Path
import socket
import sys
import time

from PIL import Image, ImageStat

SOURCE = Path("/tmp/INT20_SOURCE.blend")
OUT = Path("/tmp/halo9-int20")
OUT.mkdir(parents=True,exist_ok=True)
EXPECTED_SHA="e996fab613904dc557638612d4380ba67ef5c6bbd4aa9fb219d9aeaa8f511fb9"
assert SOURCE.is_file()
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED_SHA
PORT=9876

def call(kind,params=None):
    command=json.dumps({"type":kind,"params":params or {}},ensure_ascii=False).encode("utf8")
    with socket.create_connection(("127.0.0.1",PORT),timeout=15) as conn:
        conn.settimeout(75)
        conn.sendall(command)
        buffer=b""
        while True:
            frag=conn.recv(1024*1024)
            if not frag:break
            buffer+=frag
            assert len(buffer)<8*1024*1024,"MCP_REPLY_TOO_LARGE"
            try:
                obj=json.loads(buffer.decode("utf8"))
                break
            except (json.JSONDecodeError,UnicodeDecodeError):
                continue
        else:
            raise AssertionError("MCP_REPLY_UNAVAILABLE")
    obj=json.loads(buffer.decode("utf8"))
    if obj.get("status")!="success":
        raise RuntimeError((kind,obj.get("message",obj)))
    result=obj.get("result")
    if isinstance(result,dict) and result.get("error"):
        raise RuntimeError((kind,result))
    return result

before=call("get_scene_info")
assert before and isinstance(before,dict),"MCP_PORT_OPEN_BUT_NO_SCENE_DATA"
open_cmd=f"""
import bpy
from pathlib import Path
src=Path('/tmp/INT20_SOURCE.blend')
bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False)
sc=bpy.context.scene
assert sc['CONSTRUCTION']=='HOLD'
assert sc['FORMAL_ART_ACCEPTED']==sc['COMPLETED_TARGETS']==0
assert all(n in bpy.data.objects for n in ('E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL',
    'W0_NORTH_FRACTURED_RANGE','W0_WEST_BASALT_ESCARPMENT',
    'W0_GROUND_BASIN','W0_EASTERN_ARTIFICIAL_SEA',
    'INT11_M247C_ALPHA_WEST_ACCRETED_ARCHIVE'))
assert bpy.data.filepath == str(src)
screen=bpy.context.window_manager.windows[0].screen
area=next((a for a in screen.areas if a.type=='VIEW_3D'),None)
assert area is not None,'NO_REAL_VIEW_3D_FOR_MCP'
v=area.spaces.active
v.region_3d.view_perspective='CAMERA'
bpy.context.scene.camera=bpy.data.objects['E11_URBAN_AERIAL']
v.shading.type='SOLID'
v.overlay.show_overlays=False
area.tag_redraw()
print('INT20_LIVE_MCP_LOADED_ACTUAL_PROTECTED_CITY',len(sc.objects),flush=True)
"""
loaded=call("execute_code",{"code":open_cmd})
assert isinstance(loaded,dict) and loaded.get("executed") is True,loaded
if "INT20_LIVE_MCP_LOADED_ACTUAL_PROTECTED_CITY" not in loaded.get("result",""):
    raise RuntimeError(("SOURCE_NOT_OPENED_IN_LIVE_MCP",loaded))
# The addon runs in non-background GUI. The scene and its viewport live in
# one process, so the camera view can be inspected and subsequently edited.
scene_info=call("get_scene_info")
assert scene_info.get("object_count",0)>=50,scene_info

screenshot=OUT/"INT20_REAL_MCP_OFFSCREEN_CITY_VIEWPORT.png"
result=call("get_viewport_screenshot",{"filepath":str(screenshot),
                                      "max_size":1000,"format":"png"})
assert result.get("success") is True and screenshot.stat().st_size>5000,result
im=Image.open(screenshot).convert("RGB")
assert im.width>400 and im.height>250,im.size
stats=ImageStat.Stat(im.convert("L"))
assert stats.stddev[0]>8,"VIEWPORT_BLACK_OR_FLAT_RENDER_STOP"
assert len(im.convert("RGB").getcolors(maxcolors=10000000) or [])>50,"GUI_IMAGE_NO_SCENE_VARIATION"

evidence={
  "source_sha256":EXPECTED_SHA,
  "live_blender_gui":True,
  "real_mcp_socket_localhost_only":True,
  "scene_objects_count":scene_info["object_count"],
  "nonblack_gpu_offscreen_screenshot":True,
  "mcp_screenshot_sha256":hashlib.sha256(screenshot.read_bytes()).hexdigest(),
  "screenshot_dimensions":list(im.size),
  "screenshot_grayscale_stddev":round(stats.stddev[0],3),
  "upstream_pinned_revision":"ae010efa2a3f3d799ef1074d7cd3d9a7f36a0118",
  "upstream_license":"MIT",
  "telemetry_disabled_requested":True,
  "blender_code_execution_capability":"PROVEN_FOR_LOADING_AND_CAMERA_VIEW_ONLY",
  "original_blend_modified":False,
  "geometry_modified":False,
  "art":"NOT_REVIEWED_NOT_ADOPTED",
  "function":"UNVERIFIED",
  "formal_adoption":0,
  "city_master_completed":0,
  "minecraft":"HOLD",
  "scope":"ONE_TRUE_VISUAL_AGENT_BRIDGE_PROBE_NOT_NEW_CITY_ART"
}
(OUT/"INT20_TRUE_MCP_GUI_VISUAL_EVIDENCE.json").write_text(
    json.dumps(evidence,indent=2),encoding="utf8")
print("INT20_PATCHED_MCP_REAL_CITY_VIEWPORT_NONBLACK_TECH_PASS_NOT_ART",json.dumps(evidence),flush=True)
