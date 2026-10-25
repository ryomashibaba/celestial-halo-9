import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
def settings():
 s=bpy.context.scene
 return dict(cameras={o.name:dict(matrix=[list(v) for v in o.matrix_world],lens=o.data.lens,sensor_width=o.data.sensor_width) for o in s.objects if o.type=='CAMERA'},
 lights={o.name:dict(matrix=[list(v) for v in o.matrix_world],energy=o.data.energy) for o in s.objects if o.type=='LIGHT'},
 resolution=[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage],engine=s.render.engine,exposure=s.view_settings.exposure,
 world=[list(n.inputs[0].default_value)+[n.inputs[1].default_value] for n in s.world.node_tree.nodes if n.type=='BACKGROUND'])
def stats(objs):
 lo=[math.inf]*3;hi=[-math.inf]*3;tri=0
 for o in objs:
  o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
  for v in o.data.vertices:
   p=o.matrix_world@v.co
   for i in range(3):lo[i]=min(lo[i],p[i]);hi[i]=max(hi[i],p[i])
 return dict(meshes=len(objs),triangles=tri,min=lo,max=hi)
bpy.ops.wm.open_mainfile(filepath=str(R/'models/C55A_BEFORE.blend'));b=settings()
bpy.ops.wm.open_mainfile(filepath=str(R/'models/C55A_R25_LOCAL_EDIT.blend'));a=settings();expected=stats([o for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_render])
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(R/'models/C55A_R25_LOCAL_EDIT.glb'))
actual=stats([o for o in bpy.context.scene.objects if o.type=='MESH'])
bounderr=max(abs(expected[k][i]-actual[k][i]) for k in ['min','max'] for i in range(3))
out=dict(camera_light_render_conditions_exact=b==a,exported_visible_geometry=expected,imported_glb=actual,triangle_match=expected['triangles']==actual['triangles'],max_bounds_error_m=bounderr,pass_basic= b==a and expected['triangles']==actual['triangles'] and bounderr<.01,scope='Basic file and geometry readback only; no art or endpoint success implied.')
(R/'qa/FILE_READBACK.json').write_text(json.dumps(out,indent=2),encoding='utf8')
assert out['pass_basic'],out
print('BASIC_FILE_READBACK_PASS',flush=True)
