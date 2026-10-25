"""Independent BLEND/GLB reload, geometry identity and representative space samples.
Limited technical evidence, never art approval or all-city circulation certification.
"""
import bpy, sys, math, json
from pathlib import Path
from mathutils import Vector, kdtree
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent

def capture():
    verts=[];centers=[];groups={};count=0
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        count+=1;m=o.data;m.calc_loop_triangles()
        vs=[o.matrix_world@v.co for v in m.vertices]
        assert all(math.isfinite(v) for p in vs for v in p),o.name
        verts.extend(vs)
        centers.extend((vs[t.vertices[0]]+vs[t.vertices[1]]+vs[t.vertices[2]])/3 for t in m.loop_triangles)
        groups.setdefault(o.get('study_group','glTF imported'),[]).extend(vs)
    def bounds(vs):
        lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)]
        return {'min_m':lo,'max_m':hi,'dimensions_m':[hi[i]-lo[i] for i in range(3)]}
    return verts,centers,{'meshes':count,'vertices':len(verts),'triangles':len(centers),**bounds(verts),
        'group_bounds':{k:bounds(v) for k,v in groups.items()}}

def nearest(a,b):
    kd=kdtree.KDTree(len(b))
    for i,p in enumerate(b):kd.insert(p,i)
    kd.balance();return max(kd.find(p)[2] for p in a)

bpy.ops.wm.open_mainfile(filepath=str(R/'model/R28_CELESTIAL_ESTUARY.blend'))
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();sc=bpy.context.scene
av,ac,a=capture();cameras=[]
for cam in [o for o in sc.objects if o.type=='CAMERA']:
    p=cam.location;floor=cam.get('floor_expected')
    row={'camera':cam.name,'position_m':list(p),'target_m':list(cam['target_m']),'lens_mm':cam.data.lens,
         'kind':'AERIAL_OR_FLOATING','floor_expected':floor or None}
    if floor:
        hit,loc,normal,face,ob,mat=sc.ray_cast(dg,p,Vector((0,0,-1)),distance=5)
        row.update({'hit':bool(hit),'actual_support':ob.name if hit else None,'eye_height_m':p.z-loc.z if hit else None})
        row['floor_pass']=hit and ob.name==floor and abs(p.z-loc.z-1.7)<.01
        row['kind']='REAL_STUDY_FLOOR_HUMAN_VIEW'
        assert row['floor_pass'],row
        # Small cross around feet, not a full route test. Keep support edges explicit.
        samples=[]
        for dx,dy in [(0,0),(.45,0),(-.45,0),(0,.45),(0,-.45)]:
            q=p+Vector((dx,dy,-1.5));h,l,n,f,o,m=sc.ray_cast(dg,q,Vector((0,0,-1)),distance=.5)
            samples.append(bool(h and o.name==floor))
        row['five_foot_support_samples']=samples;assert all(samples),row
        blocked=[]
        for v in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1)]:
            h,l,n,f,o,m=sc.ray_cast(dg,p,Vector(v),distance=.22)
            if h:blocked.append(o.name)
        row['head_clearance_22cm_cardinal_hits']=blocked;assert not blocked,row
    cameras.append(row)
record={'cameras':cameras,'limits':'Floor support and tiny local head samples only, not continuous pedestrian/structural certification.'}
(R/'qa/CAMERAS.json').write_text(json.dumps(record,indent=2),encoding='utf8')
# Independent aperture probes, from the actual saved model. Not labels alone.
spaces=[]
for name,start,end in [
    ('roofed forum longitudinal lower void',(0,-1500,112),(0,300,112)),
    ('east reading gallery open front',(1035,-917,120.7),(2250,-650,850)),
    ('north choir portal transverse sample',(-80,1300,400),(-80,1950,400)),
]:
    p,q=Vector(start),Vector(end);h,l,n,f,o,m=sc.ray_cast(dg,p,(q-p).normalized(),distance=(q-p).length-.1)
    spaces.append({'name':name,'start_m':start,'end_m':end,'length_m':(q-p).length,
                   'first_hit':o.name if h else None,'distance_to_hit_m':(l-p).length if h else None,
                   'unobstructed_sample':not h})
(R/'qa/SPACE_SAMPLES.json').write_text(json.dumps({'samples':spaces,
    'limits':'Honest finite straight rays. A blocked ray is recorded, never silently removed. No enclosed-volume or building-wide access claim.'},indent=2),encoding='utf8')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(R/'model/R28_CELESTIAL_ESTUARY.glb'))
bpy.context.view_layer.update();bv,bc,b=capture()
errors={'blend_to_glb_vertex_m':nearest(av,bv),'glb_to_blend_vertex_m':nearest(bv,av),
        'blend_to_glb_triangle_center_m':nearest(ac,bc),'glb_to_blend_triangle_center_m':nearest(bc,ac)}
box_error=max(abs(a[k][i]-b[k][i]) for k in ['min_m','max_m'] for i in range(3))
ok=a['meshes']==b['meshes'] and a['triangles']==b['triangles'] and box_error<.01 and max(errors.values())<.01
out={'geometry_readback_pass':ok,'saved_blend':a,'reimported_glb':b,'max_boundary_error_m':box_error,
     'nearest_geometry_errors':errors,'tolerance_m':.01,
     'scope':'Both actual saved files independently opened. All vertices/triangle centers tested bidirectionally; not exact topology identity.',
     'not_verified':['all interpenetrations','structural integrity','all public volumes','continuous pedestrian routes','transit operational design','canonical coordinates and asset integration','Minecraft conversion'],
     'art_judgment':'Separate image-based producer review; no formal adoption'}
(R/'qa/SAVED_GEOMETRY_CHECK.json').write_text(json.dumps(out,indent=2),encoding='utf8')
assert ok,out
print('SAVED_GEOMETRY_CHECK_PASS',a['meshes'],a['triangles'],errors,flush=True)
