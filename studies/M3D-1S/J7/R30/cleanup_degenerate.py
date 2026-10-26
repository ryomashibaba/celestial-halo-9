"""Explicit R30-A tessellation for consistent BLEND/GLB export.
The original A export had 60 fewer triangles despite identical unique vertices.
The first zero-area hypothesis was false (zero such faces); keep that fact in the log.
No vertex repositioning or camera changes.
"""
import bpy,bmesh,sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
bpy.ops.wm.open_mainfile(filepath=str(g.R/'model/R30_A.blend'))
rows=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH':continue
    o.data.calc_loop_triangles()
    bad=sum(t.area<1e-10 for t in o.data.loop_triangles)
    if not o.get('study_group','').startswith('A_'):continue
    before=len(o.data.loop_triangles)
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces))
    if o.name in ['A west tidal wall','A north spine','A split crown counterleaf']:
        # Try a 1cm weld at Boolean junctions (the study spans 5km). This alone
        # did not resolve the remaining 18-face difference; see stabilize_a_export.py.
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.01)
        bmesh.ops.dissolve_degenerate(bm,dist=.001,edges=list(bm.edges))
        bmesh.ops.triangulate(bm,faces=list(bm.faces))
    remove=[f for f in bm.faces if f.calc_area()<1e-10]
    bmesh.ops.delete(bm,geom=remove,context='FACES_ONLY')
    bmesh.ops.delete(bm,geom=[e for e in bm.edges if not e.link_faces],context='EDGES')
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_edges],context='VERTS')
    bm.to_mesh(o.data);bm.free();o.data.update();o.data.calc_loop_triangles()
    rows.append(dict(object=o.name,triangles_before=before,triangles_after=len(o.data.loop_triangles),zero_area_triangles_removed=bad))
g.CHANGES.append({'export_tessellation':rows,'earlier_hypothesis':'No zero-area triangles were present; the original 60-triangle difference was not confirmed as degeneracy.'})
g.save('A',5)
