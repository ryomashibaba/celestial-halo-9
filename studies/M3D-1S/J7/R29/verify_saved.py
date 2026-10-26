"""Independent saved-file and finite architectural QA. Never art certification."""
import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector,kdtree
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;SRC=R.parent/'R28/model/R28_CELESTIAL_ESTUARY.blend'
def record(p,v):(R/p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
def sig(o):
    import struct
    h=hashlib.sha256()
    for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
    for p in o.data.polygons:h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
    return h.hexdigest()
def bounds(vs):
    lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)]
    return {'min_m':lo,'max_m':hi,'dimensions_m':[hi[i]-lo[i] for i in range(3)]}
def capture():
    vs=[];cs=[];groups={};count=0
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        count+=1;o.data.calc_loop_triangles();ov=[o.matrix_world@v.co for v in o.data.vertices]
        assert all(math.isfinite(x) for p in ov for x in p),o.name
        vs.extend(ov);cs.extend((ov[t.vertices[0]]+ov[t.vertices[1]]+ov[t.vertices[2]])/3 for t in o.data.loop_triangles)
        groups.setdefault(o.get('study_group','imported'),[]).extend(ov)
    return vs,cs,{'meshes':count,'vertices':len(vs),'triangles':len(cs),**bounds(vs),'groups':{k:bounds(v) for k,v in groups.items()}}
def near(a,b):
    kd=kdtree.KDTree(len(b))
    for i,p in enumerate(b):kd.insert(p,i)
    kd.balance();return max(kd.find(p)[2] for p in a)
def lighting():
    sc=bpy.context.scene
    return {'world':[(n.type,[list(s.default_value) if hasattr(s.default_value,'__len__') else s.default_value for s in n.inputs if hasattr(s,'default_value')]) for n in sc.world.node_tree.nodes],
        'lights':{o.name:{'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'location':list(o.location),'rotation':list(o.rotation_euler)} for o in sc.objects if o.type=='LIGHT'},
        'exposure':sc.view_settings.exposure,'transform':sc.view_settings.view_transform,'resolution':[sc.render.resolution_x,sc.render.resolution_y],'samples':sc.cycles.samples}
bpy.ops.wm.open_mainfile(filepath=str(SRC));source={o.name:sig(o) for o in bpy.context.scene.objects if o.type=='MESH'}
source_lighting=lighting()
source_cams={o.name:{'matrix':[list(row) for row in o.matrix_world],'lens':o.data.lens} for o in bpy.context.scene.objects if o.type=='CAMERA'}
bpy.ops.wm.open_mainfile(filepath=str(R/'model/R29_TIDAL_COMMONS.blend'))
sc=bpy.context.scene;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
current={o.name:sig(o) for o in sc.objects if o.type=='MESH'}
delta={'removed':sorted(set(source)-set(current)),'modified':sorted(k for k in source.keys()&current.keys() if source[k]!=current[k]),'unchanged_count':sum(source[k]==current[k] for k in source.keys()&current.keys()),'new':sorted(set(current)-set(source))}
same_cams={o.name:source_cams[o.name]=={'matrix':[list(row) for row in o.matrix_world],'lens':o.data.lens} for o in sc.objects if o.type=='CAMERA' and o.name in source_cams}
record('qa/ACTUAL_MESH_DELTA.json',{'mesh_delta':delta,'R28_camera_transforms_and_lenses_unchanged':same_cams,'R28_lighting_exposure_and_quality_unchanged':source_lighting==lighting(),'comparison_settings':lighting()})
assert all(same_cams.values())
assert source_lighting==lighting()
av,ac,aa=capture();camera_rows=[]
for cam in [o for o in sc.objects if o.type=='CAMERA']:
    p=cam.location;floor=cam.get('floor_expected');row={'camera':cam.name,'eye_m':list(p),'target_m':list(cam.get('target_m',[])),'lens_mm':cam.data.lens,'intended_support':floor}
    if floor:
        h,l,n,f,o,m=sc.ray_cast(dg,p,Vector((0,0,-1)),distance=5)
        row.update({'actual_support':o.name if h else None,'eye_height_m':p.z-l.z if h else None,'floor_height_pass':bool(h and abs(p.z-l.z-1.7)<.01)})
        row['five_foot_samples']=[]
        for dx,dy in [(0,0),(.4,0),(-.4,0),(0,.4),(0,-.4)]:
            q=p+Vector((dx,dy,-1.5));hit,loc,*_=sc.ray_cast(dg,q,Vector((0,0,-1)),distance=.5);row['five_foot_samples'].append(bool(hit and abs(loc.z-(p.z-1.7))<.01))
        row['head_22cm_hits']=[]
        for d in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1)]:
            hit,loc,no,fi,ob,ma=sc.ray_cast(dg,p,Vector(d),distance=.22)
            if hit:row['head_22cm_hits'].append(ob.name)
    camera_rows.append(row)
record('qa/CAMERAS.json',camera_rows)
assert all(r['floor_height_pass'] and all(r['five_foot_samples']) and not r['head_22cm_hits'] for r in camera_rows if r.get('intended_support'))
probes=[]
for label,a,b in [
 ('forum east portal -1100',(350,-1100,106.7),(1100,-1100,106.7)),
 ('forum east portal -600',(350,-600,106.7),(1080,-600,106.7)),
 ('forum east portal -120',(350,-120,106.7),(1080,-120,106.7)),
 ('east great civic rift',(500,150,530),(1350,150,530)),
 ('east upper arrival rift',(400,700,1040),(1250,700,1040)),
 ('sky walk first span',(1370,-480,806.7),(1600,-769,806.5)),
 ('B arrival actual opening',(1510,-769,806.5),(1900,-769,806.2)),
 ('reading room outlook toward lower B',(1074.4,-139.5,651.7),(1800,-465,668)),
]:
    p,q=Vector(a),Vector(b);h,l,n,f,o,m=sc.ray_cast(dg,p,(q-p).normalized(),distance=(q-p).length-.05)
    probes.append({'name':label,'start_m':a,'end_m':b,'clear':not h,'first_hit':o.name if h else None,'hit_m':list(l) if h else None})
# Finite floor-height samples along intended joins; records all failures.
joins=[]
paths=[('reading ramp',(680,-1280,105),(680,-1000,119)),('forum ramp',(195,-1440,105),(195,-760,139)),('sky first',(1370,-480,805),(1600,-769,805)),('sky second',(1600,-769,805),(1900,-769,804.5)),('vehicle deck corner',(1578.079,-786.445,805),(1600,-797,805))]
for label,a,b in paths:
    samples=[]
    for i in range(21):
        p=Vector(a).lerp(Vector(b),i/20);h,l,n,f,o,m=sc.ray_cast(dg,p+Vector((0,0,1.7)),Vector((0,0,-1)),distance=3)
        samples.append({'t':i/20,'support':o.name if h else None,'surface_error_m':abs(l.z-p.z) if h else None,'pass':bool(h and abs(l.z-p.z)<.02)})
    joins.append({'name':label,'start_m':a,'end_m':b,'samples':samples,'all_floor_samples_pass':all(x['pass'] for x in samples)})
record('qa/SPACE_AND_CONNECTIONS.json',{'rays':probes,'sampled_floor_joins':joins,'limits':'Finite straight sight/head rays and 21 floor samples per named segment only. Not swept body, complete path graph, egress, vehicle operation, enclosure volume or structure certification.'})
assert all(r['clear'] for r in probes[:7])
assert all(j['all_floor_samples_pass'] for j in joins)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'model/R29_TIDAL_COMMONS.glb'));bpy.context.view_layer.update()
bv,bc,bb=capture();err={'blend_to_glb_vertex_m':near(av,bv),'glb_to_blend_vertex_m':near(bv,av),'blend_to_glb_triangle_center_m':near(ac,bc),'glb_to_blend_triangle_center_m':near(bc,ac)}
be=max(abs(aa[k][i]-bb[k][i]) for k in ['min_m','max_m'] for i in range(3))
ok=aa['meshes']==bb['meshes'] and aa['triangles']==bb['triangles'] and be<.01 and max(err.values())<.01
record('qa/SAVED_GEOMETRY_CHECK.json',{'geometry_readback_pass':ok,'saved_blend':aa,'reimported_glb':bb,'bidirectional_nearest_errors':err,'boundary_error_m':be,'tolerance_m':.01,'scope':'Every vertex and triangle centroid both directions, count and bounds. Not exact topology identity or art approval.'})
print(json.dumps({'readback_pass':ok,'meshes':aa['meshes'],'triangles':aa['triangles'],'errors':err,'camera_floor_failures':[r for r in camera_rows if r.get('intended_support') and not r.get('floor_height_pass')],'blocked_rays':[r for r in probes if not r['clear']],'join_failures':[j['name'] for j in joins if not j['all_floor_samples_pass']]},indent=2),flush=True)
assert ok
