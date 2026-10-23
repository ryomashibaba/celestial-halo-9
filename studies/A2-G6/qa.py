"""Independent GLB read with trimesh; scoped mesh/support checks, not art acceptance."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh
R=Path(__file__).resolve().parent
record=json.loads((R/'geometry-record.json').read_text(encoding='utf-8'))
s=trimesh.load(R/'selected.glb',force='scene')
objects={}
# glTF right-handed Y-up -> the study's Blender X-east, Y-north, Z-up frame.
C=np.array([[1,0,0,0],[0,0,-1,0],[0,1,0,0],[0,0,0,1]],float)
for node in s.graph.nodes_geometry:
    T,key=s.graph[node];g=s.geometry[key].copy();g.apply_transform(C@T);objects[node]=g
bb=np.array([g.bounds for g in objects.values()]);bounds=np.array([bb[:,0].min(axis=0),bb[:,1].max(axis=0)])
delta=float(np.max(np.abs(bounds-np.array(record['bounds_m']))))
assert delta<.02,(bounds,record['bounds_m'])
info=[]
for name,g in objects.items():
    assert np.isfinite(g.vertices).all()
    finite=bool(np.isfinite(g.vertices).all());g.merge_vertices(merge_tex=True,merge_norm=True)
    info.append({'object':name,'vertices':len(g.vertices),'triangles':len(g.faces),'finite':finite,
       'watertight_after_merge':bool(g.is_watertight),'winding_consistent':bool(g.is_winding_consistent),
       'note':'Glazing planes intentionally open; intersecting room/solid batches are not a single boolean-unioned building'})

def named(part):
    hits=[g for n,g in objects.items() if part in n]
    assert len(hits)==1,(part,len(hits))
    return hits[0]

def vertical_support_z(g,x,y,z):
    # Direct triangle intersection: no optional rtree dependency; only target ground mesh.
    triangles=g.triangles;values=[]
    for tri in triangles:
        A,B,D=tri
        mat=np.column_stack((B[:2]-A[:2],D[:2]-A[:2]))
        det=np.linalg.det(mat)
        if abs(det)<1e-7:continue
        u,v=np.linalg.solve(mat,np.array([x,y])-A[:2])
        if u>=-1e-6 and v>=-1e-6 and u+v<=1+1e-6:
            zz=A[2]+u*(B[2]-A[2])+v*(D[2]-A[2])
            if zz<=z+.05:values.append(float(zz))
    return max(values) if values else None

roof=named('SHARED_ROOF_EQUALS_UPPER_CITY_GROUND');lower=named('LOWER_DISTRICT_GROUND')
probes=[]
for a in record['focus_pair']['house_floor_probes']:
    x,y,z=a['xyz'];g=roof if a['id'].startswith('U') else lower
    w,d=(70,90) if a['id'].startswith('U') else (70,110)
    # Wing midpoints and external footprint corners; courtyard centre is NOT sufficient.
    for dx,dy in [(-w/2,-d/2),(w/2,-d/2),(-w/2,d/2),(w/2,d/2),(0,d/2),(-w/2,0),(w/2,0)]:
        hit=vertical_support_z(g,x+dx,y+dy,z)
        probes.append({'block':a['id'],'xy':[x+dx,y+dy],'floor_z_m':z,'support_z_m':hit,
          'gap_m':None if hit is None else float(z-hit),'pass_5cm':hit is not None and abs(z-hit)<.05})
assert all(p['pass_5cm'] for p in probes)
assert abs(roof.bounds[1,2]-record['focus_pair']['upper_street_z_m'])<.01
assert abs(roof.bounds[0,2]-2194)<.01
stairs=named('PUBLIC_STAIRS_640_TREADS_AND_LANDINGS')
stair_checks={'actual_mesh_bounds_m':stairs.bounds.tolist(),'arithmetic_total_rise_m':16*40*.15,
 'lower_street_m':2110,'upper_street_m':2206,'max_riser_design_m':.15,
 'treads':640,'landings':16,'lower_connector_gap_fixed_before_final_export':True,
 'limits':'Riser arithmetic and actual mesh bounds only. No global floor collision, headroom or universal-access validation.'}

qa={'loader':'trimesh independent of Blender','file':'selected.glb','sha256':hashlib.sha256((R/'selected.glb').read_bytes()).hexdigest(),
 'units':'m','gltf_to_study_axis_transform':C.tolist(),'bounds_m':bounds.tolist(),
 'dimensions_m':dict(zip(['width','depth','height'],(bounds[1]-bounds[0]).tolist())),
 'vs_blender_bounds_max_delta_m':delta,'all_vertices_finite':True,'geometry_objects':len(objects),'triangles':sum(len(g.faces) for g in objects.values()),
 'mesh_topology':info,'focus_housing_support_probes':probes,'focus_housing_support_summary':{'passes':len(probes),'samples':len(probes),'scope':'7 samples per block for 24 lower + 8 upper courts; school/supports/services outside this count'},
 'shared_roof':{'actual_bounds_m':roof.bounds.tolist(),'upper_street_equals_roof_top':True,
   'upper_housing_depends_on_same_mesh':True,'lower_civic_hall_has_same_roof':True,
   'roof_removal':'Would remove the sole ground used by all sampled upper housing footprints; this is geometry dependency, not structural engineering'},
 'stairs':stair_checks,'art_status':'HOLD','global_walkability':'NOT_TESTED','protected_collisions':'NOT_TESTED',
 'physics_and_environment':'NOT_ENGINEERED','formal_M247C_modified':False,'coordinate_fusion':False,
 'limits':['The main mass remains a repeated shelf/rack composition; geometry QA cannot resolve this art failure','Core world background is conceptual, not W0','Scale people are 1.7m reference solids, not inhabitants or a population simulation','Courtyard wings have entrances/windows but no full dwelling fit-out','Some batches have overlapping solids; watertight individual solids do not certify the assembled building']}
qa['comparison_models']={}
for key in ['A','B']:
    other=trimesh.load(R/'comparison'/(key+'_massing.glb'),force='scene')
    v=[]
    for node in other.graph.nodes_geometry:
        T,k=other.graph[node];g=other.geometry[k].copy();g.apply_transform(C@T);v.append(g.vertices)
    v=np.vstack(v);assert np.isfinite(v).all()
    qa['comparison_models'][key]={'independent_load':'SUCCESS','finite_vertices':True,'dimensions_m':dict(zip(['width','depth','height'],(v.max(axis=0)-v.min(axis=0)).tolist())),'scope':'massing geometry only, no inhabited-city or art validation'}
(R/'mesh-qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:qa[k] for k in ['dimensions_m','vs_blender_bounds_max_delta_m','geometry_objects','triangles','focus_housing_support_summary','art_status']}))
