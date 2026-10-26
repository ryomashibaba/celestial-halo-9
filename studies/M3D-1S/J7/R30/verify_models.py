"""Limited saved Blender/GLB and metre-scale evidence. Not structural or ART QA.
Background Blender. Each GLB is imported into an independently empty scene.
"""
import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent

def geometry():
    pts=[];triangles=0;meshes=0;central=[];counts={}
    for o in bpy.context.scene.objects:
        if o.type!='MESH' or o.name=='far ground':continue
        meshes+=1;me=o.data;me.calc_loop_triangles();triangles+=len(me.loop_triangles)
        counts[o.name]=len(me.loop_triangles)
        a=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',a);a=a.reshape(-1,3)
        mw=np.array(o.matrix_world);a=a@mw[:3,:3].T+mw[:3,3]
        pts.append(a)
        if o.get('study_group','').startswith(('A_','B_')):central.append(a)
    allpts=np.concatenate(pts)
    # Tolerance-quantized unique coordinates ignore intentional GLB normal/UV vertex splits.
    q=np.unique(np.rint(allpts*1000).astype(np.int64),axis=0)
    result=dict(meshes=meshes,triangles=triangles,raw_vertices=len(allpts),finite=bool(np.isfinite(allpts).all()),unique_vertices_mm=len(q),unique_vertex_hash_mm=hashlib.sha256(q.tobytes()).hexdigest(),bounds_m=[allpts.min(axis=0).tolist(),allpts.max(axis=0).tolist()])
    if central:
        c=np.concatenate(central);result['authored_bounds_m']=[c.min(axis=0).tolist(),c.max(axis=0).tolist()];result['authored_size_m']=(c.max(axis=0)-c.min(axis=0)).tolist()
    result['triangle_counts']=counts
    return result

def cameras():
    sc=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();out=[]
    for o in sc.objects:
        if o.type!='CAMERA' or not o.get('support_floor'):continue
        eye=o.location.copy();hit,p,n,f,ob,m=sc.ray_cast(dg,eye,Vector((0,0,-1)),distance=10)
        floor=dict(hit=ob.name if hit else None,eye_above_floor_m=eye.z-p.z if hit else None,surface_m=list(p) if hit else None)
        samples=[]
        for dx,dy in [(0,0),(.45,0),(-.45,0),(0,.45),(0,-.45)]:
            e=eye+Vector((dx,dy,0));hh,pp,nn,ff,oo,mm=sc.ray_cast(dg,e,Vector((0,0,-1)),distance=3)
            samples.append(dict(hit=oo.name if hh else None,height_m=e.z-pp.z if hh else None))
        near=[]
        for j in range(16):
            d=Vector((math.cos(j*math.tau/16),math.sin(j*math.tau/16),0))
            hh,pp,nn,ff,oo,mm=sc.ray_cast(dg,eye,d,distance=.23)
            if hh:near.append(oo.name)
        target=Vector(o['target_m']);direction=(target-eye).normalized();hh,pp,nn,ff,oo,mm=sc.ray_cast(dg,eye,direction,distance=(target-eye).length)
        out.append(dict(camera=o.name,eye_m=list(eye),target_m=list(target),lens_mm=o.data.lens,expected_support=o['support_floor'],actual_floor=floor,footprint_5=samples,head_near_23cm=near,view_first_hit=oo.name if hh else None,view_first_distance_m=(pp-eye).length if hh else None,
                        limited_floor_pass=hit and abs(eye.z-p.z-1.7)<.025 and all(s['height_m'] is not None and abs(s['height_m']-1.7)<.05 for s in samples) and not near))
    return out

reports=[];camera_compare=[]
for v in ('A','B'):
    bpy.ops.wm.open_mainfile(filepath=str(R/f'model/R30_{v}.blend'));bpy.context.view_layer.update()
    sc=bpy.context.scene;original=geometry();cams=cameras()
    camset={o.name:dict(matrix=[list(r) for r in o.matrix_world],lens=o.data.lens,clip_start=o.data.clip_start,clip_end=o.data.clip_end) for o in sc.objects if o.type=='CAMERA'}
    camera_compare.append(camset)
    info=dict(variant=v,revision=sc['revision'],blend=original,human_cameras=cams,external_image_dependencies=[dict(name=i.name,path=i.filepath) for i in bpy.data.images if i.source=='FILE' and not i.packed_file],settings=dict(engine=sc.render.engine,resolution=[sc.render.resolution_x,sc.render.resolution_y],samples=sc.cycles.samples,world=sc.world.name,exposure=sc.view_settings.exposure),glb_excludes='Only far ground 300km background plane; every architectural/context mesh included')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(R/f'model/R30_{v}.glb'));bpy.context.view_layer.update()
    imported=geometry();info['glb_independent_reload']=imported
    info['same_mesh_count']=original['meshes']==imported['meshes'];info['same_triangle_count']=original['triangles']==imported['triangles'];info['same_unique_vertices_1mm']=original['unique_vertex_hash_mm']==imported['unique_vertex_hash_mm']
    reports.append(info)
matched={n:camera_compare[0][n]==camera_compare[1][n] for n in ['01_CITY','02_CENTRAL','04_HUMAN','05_REAR','06_UNDERSIDE']}
out=dict(blender=bpy.app.version_string,units='1 unit=1m; relative study only',models=reports,matched_cameras=matched,public_03_and_high_07='Purpose-matched rooms, distinct locations/heights and framing. Not same-camera shape comparison.',verification_scope='Saved source reload, independent GLB import, mesh/triangle counts, unique world-space coordinates at 1mm quantization, authored bounds, three eye/footprint/head samples per variant. No topology/manifold/whole-route/structure/vehicle/evacuation/formal-world certification.')
(R/'qa/SAVED_MODELS.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(out,ensure_ascii=False,indent=2),flush=True)
assert all(m['same_mesh_count'] and m['same_triangle_count'] and m['same_unique_vertices_1mm'] for m in reports)
assert all(matched.values())
assert all(c['limited_floor_pass'] for m in reports for c in m['human_cameras'])
