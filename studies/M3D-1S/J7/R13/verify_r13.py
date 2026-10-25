"""Read actual BLEND then actual GLB; basic persistence, not art/inhabitation QA."""
import bpy,bmesh,math,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).parent
CASES=[('A','exploration_A','R13_A'),('B','exploration_B','R13_B'),
       ('C_SELECTED','selected','R13_C_SELECTED'),('C_R1','revision_1','R13_C_R1'),
       ('C_R2','revision_2','R13_C_R2'),
       ('SECTION_XZ','sections/SECTION_XZ_Y680','SECTION_XZ_Y680'),
       ('SECTION_YZ','sections/SECTION_YZ_X0','SECTION_YZ_X0')]

def metrics(obs):
    dg=bpy.context.evaluated_depsgraph_get()
    lo=Vector((math.inf,)*3);hi=Vector((-math.inf,)*3);tris=verts=nm=boundary=bad=0
    buckets={k:0. for k in ['under_20','20_100','100_500','500_1500','over_1500']}
    details=[];volume=0
    for ob in obs:
        ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles()
        if not me.vertices:ev.to_mesh_clear();continue
        coords=[ev.matrix_world@v.co for v in me.vertices]
        low=Vector([min(v[i] for v in coords) for i in range(3)])
        high=Vector([max(v[i] for v in coords) for i in range(3)])
        for i in range(3):lo[i]=min(lo[i],low[i]);hi[i]=max(hi[i],high[i])
        bad+=sum(not all(math.isfinite(c) for c in v) for v in coords)
        area=0.
        for tri in me.loop_triangles:
            a,b,c=[coords[i] for i in tri.vertices];area+=(b-a).cross(c-a).length/2
        span=max(high-low)
        key=next(k for a,b,k in [(0,20,'under_20'),(20,100,'20_100'),(100,500,'100_500'),(500,1500,'500_1500'),(1500,math.inf,'over_1500')] if a<=span<b)
        buckets[key]+=area
        bm=bmesh.new();bm.from_mesh(me)
        count=sum(not e.is_manifold for e in bm.edges)
        nm+=count;boundary+=sum(e.is_boundary for e in bm.edges)
        if count==0:volume+=abs(bm.calc_volume(signed=True))
        bm.free()
        details.append(dict(name=ob.name,max_dimension_m=span,summed_triangle_area_m2=area,triangles=len(me.loop_triangles),nonmanifold_edges=count))
        tris+=len(me.loop_triangles);verts+=len(me.vertices);ev.to_mesh_clear()
    total=sum(buckets.values())
    return dict(min_m=list(lo),max_m=list(hi),span_m=list(hi-lo),mesh_objects=len(obs),vertices=verts,triangles=tris,
                nonfinite_vertices=bad,nonmanifold_edges=nm,boundary_edges=boundary,
                summed_solid_volume_not_habitable_m3=volume,
                summed_triangle_area_m2=total,area_by_object_max_dimension_m2=buckets,
                area_fraction_by_object_max_dimension={k:v/total for k,v in buckets.items()},
                top_area_objects=sorted(details,key=lambda d:d['summed_triangle_area_m2'],reverse=True)[:12])

out={'scope':'Persistence, finite coordinates, dimensions, triangle counts and separate solid topology. NOT occupancy, habitation, route, load, art or construction approval. Object-size area bins depend on modelling organisation; no objects are split to improve the score.',
     'models':{}}
for label,folder,stem in CASES:
    folder=ROOT/folder;blend=folder/(stem+'.blend');glb=folder/(stem+'.glb')
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    native=metrics([o for o in bpy.data.collections['R13_EDITABLE_CITY'].objects if o.type=='MESH' and len(o.data.polygons)>0])
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(glb))
    imported=metrics([o for o in bpy.context.scene.objects if o.type=='MESH'])
    error=max(abs(native[k][i]-imported[k][i]) for k in ['min_m','max_m'] for i in range(3))
    checks=dict(actual_blend_open=True,actual_glb_import=True,bounds_error_m=error,bounds_match_2cm=error<.02,
                triangle_counts_equal=native['triangles']==imported['triangles'],
                all_vertices_finite=native['nonfinite_vertices']==imported['nonfinite_vertices']==0)
    out['models'][label]=dict(blend_sha256=hashlib.sha256(blend.read_bytes()).hexdigest(),
        glb_sha256=hashlib.sha256(glb.read_bytes()).hexdigest(),blend_bytes=blend.stat().st_size,
        glb_bytes=glb.stat().st_size,native=native,glb_reimport=imported,checks=checks)
    print('CHECK',label,checks,flush=True)
out['basic_persistence_pass']=all(all(v['checks'][k] for k in ['actual_blend_open','actual_glb_import','bounds_match_2cm','triangle_counts_equal','all_vertices_finite']) for v in out['models'].values())
(ROOT/'qa/BLEND_GLB_READBACK.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print('PERSISTENCE',out['basic_persistence_pass'],flush=True)
