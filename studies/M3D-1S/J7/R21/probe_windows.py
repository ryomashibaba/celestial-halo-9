"""Limited real-mesh window backing tests; not an exhaustive facade audit."""
import bpy, sys, json, statistics
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R))
sys.argv=['probe_windows.py','--','helpers','C55A']
import compare as c
c.MODEL='C55A';c.load_native()
bvh,owners=c.make_bvh([o for o in c.meshes() if not c.context(o) and not c.decals(o) and not c.effects(o)])
out={'scope':'12 deterministic face samples per named decal mesh. Actual architecture first hit; no global opening or occupancy certification.', 'objects':{}}
for name in ['N_win_win_warm','S_win_win_warm','N_outwin_win_warm','S_outwin_win_warm']:
    o=bpy.data.objects[name];o.data.calc_loop_triangles();ts=o.data.loop_triangles;samples=[]
    for k in range(12):
        tr=ts[int((k+.5)*len(ts)/12)];a,b,d=[o.matrix_world@o.data.vertices[i].co for i in tr.vertices]
        p=(a+b+d)/3;n=(b-a).cross(d-a).normalized();nearest=bvh.find_nearest(p)
        shots=[]
        for sign in [-1,1]:
            hit,normal,idx,dist=bvh.ray_cast(p+n*(2*sign),n*(-sign),4)
            if idx is not None:shots.append(dict(backing_object=owners[idx],distance_from_window_m=(hit-p).length,point_m=list(hit)))
        samples.append(dict(window_point_m=list(p),nearest_architecture_distance_m=nearest[3],
          nearest_architecture_object=owners[nearest[2]] if nearest[2] is not None else None,normal_rays=shots,
          backing_within_2m=any(s['distance_from_window_m']<2 for s in shots)))
    out['objects'][name]=samples
portal=bpy.data.objects.get('west_portal_glow')
if portal:
    portal.data.calc_loop_triangles()
    out['named_west_portal']=dict(mesh_name=portal.name,triangles=len(portal.data.loop_triangles),
        observation='Filled emissive ellipse mesh; name does not certify an open doorway. Emission disabled for R21 renders.')
(R/'qa/WINDOW_BACKING_SAMPLES.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print('WINDOW_BACKING', {k:sum(x['backing_within_2m'] for x in v) for k,v in out['objects'].items()},flush=True)
