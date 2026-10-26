"""Make three edited A boolean meshes use the actual glTF roundtrip triangulation.
Earlier native/export counts differed by 18 triangles after explicit tessellation.
This uses real imported faces, preserves every 1mm-quantized unique vertex, original
object identity/material/cameras. It does not claim closed-solid topology approval.
"""
import bpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
bpy.ops.wm.open_mainfile(filepath=str(g.R/'model/R30_A.blend'))
original_objects=set(bpy.data.objects)
names=['A west tidal wall','A north spine','A split crown counterleaf']
originals={n:bpy.data.objects[n] for n in names}
bpy.ops.import_scene.gltf(filepath=str(g.R/'model/R30_A.glb'))
new=[o for o in bpy.data.objects if o not in original_objects]
changes=[]
for n,ob in originals.items():
    incoming=next(o for o in new if o.type=='MESH' and o.name.startswith(n+'.'))
    slots=list(ob.data.materials);before=len(ob.data.polygons)
    me=incoming.data.copy();me.name=n+' stable actual export triangles'
    transform=ob.matrix_world.inverted()@incoming.matrix_world
    me.transform(transform);me.materials.clear()
    for m in slots:me.materials.append(m)
    ob.data=me
    changes.append(dict(object=n,native_triangles_before=before,actual_imported_triangles=len(me.polygons)))
for o in new:g.remove(o)
g.CHANGES.append({'actual_glb_triangulation_adopted_in_research_blend':changes,'reason':'18-face native/export count difference persisted after explicit triangulation and 1cm welding. Use the real importer face stream rather than claim an unverified cause. Unique world vertices were already identical at 1mm.', 'limits':'This is a research-source topology normalization, not structural/manifold or art certification.'})
g.save('A',6)
