"""Independent actual GLB image: empty scene, GLB import, native studio only."""
import bpy,sys,json
from pathlib import Path
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;F=R/'revision_2'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(F/'R15_FINAL.glb'))
mesh_count=sum(o.type=='MESH' for o in bpy.context.scene.objects)
with bpy.data.libraries.load(str(F/'R15_FINAL.blend'),link=False) as (src,dst):
 dst.collections=['STUDIO_NOT_ARCHITECTURE'];dst.worlds=['Pale blue atmosphere']
s=bpy.context.scene;s.collection.children.link(dst.collections[0]);s.world=dst.worlds[0]
s.camera=next(o for o in dst.collections[0].objects if o.name=='02_OBLIQUE')
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
s.render.resolution_x=1200;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
s.render.image_settings.file_format='PNG';s.render.filepath=str(R/'qa/GLB_REIMPORT_OBLIQUE.png');bpy.ops.render.render(write_still=True)
(R/'qa/GLB_RENDER_REACQUISITION.json').write_text(json.dumps(dict(actual_empty_scene_import=True,import_meshes_before_studio=mesh_count,studio_only_linked_from_native=True,architecture_source='GLB bytes only',image='qa/GLB_REIMPORT_OBLIQUE.png'),indent=2),encoding='utf8')
