"""R11 native Blender visual art toolbar; run from packed Text Editor or --python.

This is a NON-AUTOMATIC, USER-OPERATED artist workstation. Clicking a
camera button changes the view; "Freeze evidence" makes a new checkpoint
with a self-contained BLEND, GLB, 6 real review PNG, and a hashes manifest.
Original architecture source is NEVER opened or written by this toolbar.
"""
import bpy, json, hashlib
from pathlib import Path

CAM_NAMES=(
  "01_FRONTAL_EYE","02_SIDE_CROSS_SECTION","03_OBLIQUE_MASS",
  "04_REAR_OTHER_SIDE","05_LOW_PUBLIC_VIEW","06_ABOVE_OTHER_WORLD")
ART_KEY="R11_EDIT_ONLY_UNAPPROVED_STUDY_SURFACE"

class R11_OT_ReviewView(bpy.types.Operator):
    bl_idname="r11.select_review_view"
    bl_label="R11: change fixed review camera"
    bl_description="Switch actual 3D viewport camera, without altering geometry"
    bl_options={'REGISTER','UNDO'}
    camera_name:bpy.props.StringProperty()
    def execute(self,context):
        cam=bpy.data.objects.get(self.camera_name)
        if self.camera_name not in CAM_NAMES or not cam or cam.type!="CAMERA":
            self.report({'ERROR'},"Missing named review camera")
            return {'CANCELLED'}
        context.scene.camera=cam
        for screen in bpy.data.screens:
            for area in screen.areas:
                if area.type=="VIEW_3D":
                    area.spaces.active.region_3d.view_perspective='CAMERA'
        self.report({'INFO'},f"R11 view: {self.camera_name}")
        return {'FINISHED'}

class R11_OT_FreezeEvidence(bpy.types.Operator):
    bl_idname="r11.freeze_artist_evidence"
    bl_label="Freeze revision: BLEND + GLB + 6 views"
    bl_description="Save a NEW isolated numbered checkpoint, not overwrite the existing .blend"
    bl_options={'REGISTER'}
    def execute(self,context):
        source=Path(bpy.data.filepath)
        ob=bpy.data.objects.get(ART_KEY)
        if not source.is_file() or not ob or ob.type!='MESH':
            self.report({'ERROR'},"Save the R11 .blend and keep the neutral target object")
            return {'CANCELLED'}
        scene=context.scene
        base=source.parent/"R11_ARTIST_REVISIONS"
        base.mkdir(exist_ok=True)
        index=1
        while (base/f"R11_REV_{index:03d}").exists():index+=1
        revdir=base/f"R11_REV_{index:03d}"
        revdir.mkdir()
        previous_scene_camera=scene.camera
        orig_filepath=scene.render.filepath
        mode_before=ob.mode
        try:
            if bpy.context.object and bpy.context.object.mode=='EDIT':
                bpy.ops.object.mode_set(mode='OBJECT')
            scene["R11_GUI_ARTIST_REVISION"]=index
            # save copy: original remains intact and currently active filepath unchanged
            blend=revdir/f"R11_REV_{index:03d}_EDITABLE.blend"
            bpy.ops.wm.save_as_mainfile(filepath=str(blend),copy=True)
            # exported candidate remains neutral and UNAPPROVED: actual mesh surface
            glb=revdir/f"R11_REV_{index:03d}_SURFACE.glb"
            bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',
                export_cameras=False,export_lights=False)
            camera_records={}
            for name in CAM_NAMES:
                cam=bpy.data.objects[name];scene.camera=cam
                image=revdir/(name+".png")
                scene.render.filepath=str(image)
                bpy.ops.render.render(write_still=True)
                camera_records[name]=str(image.name)
            result={
              "revision":index,
              "source_blend_not_overwritten":str(source),
              "new_native_blend":blend.name,
              "new_glb":glb.name,
              "real_rendered_camera_images":camera_records,
              "blender":bpy.app.version_string,
              "test_fixture_not_art_proposal":True,
              "formal_art_approved":False,
              "minecraft_construction":False,
              "source_file_hash_stable":None,
              "files_sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in sorted(revdir.iterdir()) if p.is_file()}
            }
            (revdir/"R11_REVISION_AUDIT.json").write_text(
                json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
        except Exception as exc:
            self.report({'ERROR'},"Checkpoint failed: "+str(exc)[:180])
            return {'CANCELLED'}
        finally:
            scene.camera=previous_scene_camera
            scene.render.filepath=orig_filepath
            if mode_before=='EDIT':
                try:bpy.ops.object.mode_set(mode="EDIT")
                except Exception:pass
        self.report({'INFO'},f"Evidence saved: {revdir.name}")
        return {'FINISHED'}

class R11_PT_ArtWorkstation(bpy.types.Panel):
    bl_label="HALO-9 R11 - ART FIRST"
    bl_idname="R11_PT_native_visual_workspace"
    bl_space_type='VIEW_3D'
    bl_region_type='UI'
    bl_category="HALO9 Art"
    def draw(self,context):
        col=self.layout.column(align=True)
        col.label(text="Neutral editing fixture",icon="MESH_GRID")
        col.label(text="NOT a city or M247-C proposal")
        col.separator()
        for name in CAM_NAMES:
            op=col.operator(R11_OT_ReviewView.bl_idname,
                            text=name.replace("_"," ").title(),icon="VIEW_CAMERA")
            op.camera_name=name
        col.separator()
        col.operator(R11_OT_FreezeEvidence.bl_idname,icon="FILE_TICK")
        col.label(text="Editable: one neutral mesh")
        col.label(text="6 locked cameras; no art acceptance")

CLASSES=[R11_OT_ReviewView,R11_OT_FreezeEvidence,R11_PT_ArtWorkstation]
def register():
    for cls in CLASSES:
        try:bpy.utils.unregister_class(cls)
        except RuntimeError:pass
        bpy.utils.register_class(cls)
def unregister():
    for cls in reversed(CLASSES):
        try:bpy.utils.unregister_class(cls)
        except RuntimeError:pass
if __name__=="__main__":register()
