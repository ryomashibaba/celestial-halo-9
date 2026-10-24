"""Read back saved BLEND and reimport each GLB into an empty scene; do not modify sources."""
import bpy,math,json,sys,bmesh
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent

def measurements(objects):
    dg=bpy.context.evaluated_depsgraph_get()
    lo=[math.inf]*3;hi=[-math.inf]*3
    verts=tris=0;bad=[];boundary=nonmanifold=0
    for ob in objects:
        if ob.type not in {'MESH','CURVE'}:continue
        ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles()
        verts+=len(me.vertices);tris+=len(me.loop_triangles)
        for v in me.vertices:
            p=ev.matrix_world@v.co
            if not all(math.isfinite(t) for t in p):bad.append(ob.name)
            for i in range(3):lo[i]=min(lo[i],p[i]);hi[i]=max(hi[i],p[i])
        bm=bmesh.new();bm.from_mesh(me)
        boundary+=sum(e.is_boundary for e in bm.edges)
        nonmanifold+=sum(not e.is_manifold for e in bm.edges)
        bm.free();ev.to_mesh_clear()
    return {'min_m':lo,'max_m':hi,'span_m':[hi[i]-lo[i] for i in range(3)],
            'objects':len(objects),'vertices':verts,'triangles':tris,
            'nonfinite_objects':bad,'boundary_edges':boundary,'nonmanifold_edges':nonmanifold}

def rays(label):
    origins={'A':(-1000,0,1100),'B':(-1000,0,1000),'B_REFINED':(-700,0,1500)}
    origin=Vector(origins[label]);dg=bpy.context.evaluated_depsgraph_get()
    out={}
    for name,d in [('down',(0,0,-1)),('up',(0,0,1)),('left',(-1,0,0)),
                   ('right',(1,0,0)),('front',(0,-1,0)),('rear',(0,1,0))]:
        hit,co,no,idx,obj,m=bpy.context.scene.ray_cast(dg,origin,Vector(d),distance=10000)
        out[name]={'hit':hit,'distance_m':(co-origin).length if hit else None,
                   'object':obj.name if hit else None,'position_m':list(co) if hit else None}
    return {'origin_m':list(origin),'surface_probes':out,
            'scope':'six rays only; NOT a volume, walkability or clearance certification'}

out={}
for folder,label in [('concept_A','A'),('concept_B','B'),('refined','B_REFINED')]:
    f=ROOT/folder
    bpy.ops.wm.open_mainfile(filepath=str(f/('R11_'+label+'.blend')))
    native_obs=list(bpy.data.collections['01_EDITABLE_ARCHITECTURE'].objects)
    native=measurements(native_obs)
    probes=rays(label)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(f/('R11_'+label+'.glb')))
    imported=measurements([o for o in bpy.context.scene.objects if o.type=='MESH'])
    err=max(abs(native[key][i]-imported[key][i]) for key in ['min_m','max_m'] for i in range(3))
    checks={'reimport_bounds_error_m':err,'bounds_match_within_2cm':err<.02,
            'object_count_equal':native['objects']==imported['objects'],
            'triangle_count_equal':native['triangles']==imported['triangles'],
            'all_vertices_finite':not(native['nonfinite_objects'] or imported['nonfinite_objects'])}
    assert all(checks[k] for k in checks if isinstance(checks[k],bool)),checks
    out[label]={'native_blend_readback':native,'actual_glb_reimport':imported,
                'basic_persistence_checks':checks,'actual_scene_rays':probes,
                'model_below_neutral_datum':native['min_m'][2]<0,
                'topology_note':'Open curve end caps, boolean surfaces and separate intersecting solids are retained. Not watertight construction geometry.',
                'art_decision':'REJECT','construction':'HOLD'}
(ROOT/'qa'/'BLEND_GLB_READBACK.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print('R11_BLENDER_READBACK',json.dumps({k:v['basic_persistence_checks'] for k,v in out.items()}),flush=True)
