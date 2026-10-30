"""R12 Blender 4+ portable native multi-view artist toolkit. Run Text Editor.
The controls never automatically score art; art adoption requires independent review.
"""
import bpy,hashlib,json
from pathlib import Path

CAMS=("01_LONG_APPROACH","02_FRONT","03_OBLIQUE","04_SIDE","05_REAR",
      "06_AERIAL","07_GROUND_ARRIVAL","08_CIVIC_VOID","09_SKY_CITY_DISTRICT")

class R12_OT_ReviewCamera(bpy.types.Operator):
    bl_idname="r12.review_camera"
    bl_label="Switch architectural viewpoint"
    bl_options={'REGISTER','UNDO'}
    camera_name:bpy.props.StringProperty()
    def execute(self,ctx):
        ob=bpy.data.objects.get(self.camera_name)
        if self.camera_name not in CAMS or ob is None or ob.type!="CAMERA":
            return {'CANCELLED'}
        ctx.scene.camera=ob
        for sc in bpy.data.screens:
            for area in sc.areas:
                if area.type=="VIEW_3D":
                    area.spaces.active.region_3d.view_perspective='CAMERA'
        return {'FINISHED'}

class R12_OT_SaveReview(bpy.types.Operator):
    bl_idname="r12.freeze_art_review"
    bl_label="Freeze 9-view reversible art checkpoint"
    bl_description="Write isolated new BLEND+GLB+9 images and SHA256 without changing originals"
    def execute(self,ctx):
        src=Path(bpy.data.filepath)
        if not src.is_file():self.report({'ERROR'},"Save BLEND first");return {'CANCELLED'}
        if ctx.scene.get("R12_ART_ADOPTED") is not False:
            self.report({'ERROR'},"Formal art status must remain false")
            return {'CANCELLED'}
        target=src.parent/"R12_ARTIST_CHECKPOINTS"
        target.mkdir(exist_ok=True)
        rev=1
        while (target/f"EDIT_{rev:03d}").exists():rev+=1
        d=target/f"EDIT_{rev:03d}";d.mkdir()
        previous=ctx.scene.camera;path=ctx.scene.render.filepath
        m=ctx.object.mode if ctx.object else 'OBJECT'
        try:
            if bpy.context.object and bpy.context.object.mode!="OBJECT":
                bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.wm.save_as_mainfile(filepath=str(d/f"R12_EDIT_{rev:03d}.blend"),copy=True)
            bpy.ops.export_scene.gltf(filepath=str(d/f"R12_EDIT_{rev:03d}.glb"),
                 export_format="GLB",export_cameras=False,export_lights=False)
            render=[]
            for n in CAMS:
                camera=bpy.data.objects.get(n)
                assert camera and camera.type=="CAMERA",n
                ctx.scene.camera=camera
                out=d/(n+".png")
                ctx.scene.render.filepath=str(out)
                bpy.ops.render.render(write_still=True)
                render.append(out.name)
            data={
              'revision':rev,'source':str(src),'new_blend':f"R12_EDIT_{rev:03d}.blend",
              'new_glb':f"R12_EDIT_{rev:03d}.glb",
              'actual_fixed_camera_views':render,
              'art_adopted':False,'city_10km_master':False,'minecraft_write':False,
              'checksums':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in d.iterdir() if p.is_file()}
            }
            (d/"R12_REVIEW_HASHES.json").write_text(
              json.dumps(data,ensure_ascii=False,indent=2),encoding="utf8")
        except Exception as exc:
            self.report({'ERROR'},"Checkpoint failed: "+str(exc)[:170])
            return {'CANCELLED'}
        finally:
            ctx.scene.camera=previous
            ctx.scene.render.filepath=path
            if m!='OBJECT':
                try:bpy.ops.object.mode_set(mode=m)
                except Exception:pass
        self.report({'INFO'},"Saved 9-view checkpoint EDIT_"+str(rev))
        return {'FINISHED'}

class R12_PT_ArtistView(bpy.types.Panel):
    bl_idname="R12_PT_artist_view"
    bl_label="HALO-9 R12 - 9 REAL 3D views"
    bl_space_type='VIEW_3D'
    bl_region_type='UI'
    bl_category="HALO9 Art"
    def draw(self,ctx):
        col=self.layout.column(align=True)
        col.label(text="R12 experimental geometry only")
        col.label(text="NOT formal M247-C or 10km city")
        for cam in CAMS:
            a=col.operator(R12_OT_ReviewCamera.bl_idname,
                          text=cam.replace("_"," ").title(),icon="VIEW_CAMERA")
            a.camera_name=cam
        col.separator()
        col.operator(R12_OT_SaveReview.bl_idname,icon="FILE_TICK")
        col.label(text="Editable: shape-key gallery skins")
        col.label(text="No automatic ART pass")

CLASSES=(R12_OT_ReviewCamera,R12_OT_SaveReview,R12_PT_ArtistView)
def register():
    for cls in CLASSES:
        if hasattr(bpy.types,cls.__name__):
            try:bpy.utils.unregister_class(cls)
            except RuntimeError:pass
        bpy.utils.register_class(cls)
def unregister():
    for cls in CLASSES[::-1]:
        try:bpy.utils.unregister_class(cls)
        except RuntimeError:pass
if __name__=="__main__":register()
