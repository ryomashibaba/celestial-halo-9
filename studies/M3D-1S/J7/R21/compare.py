"""R21 background Blender comparison; original inputs are read only.
blender -b -t 5 --python compare.py -- import|early|exterior|floors|sections MODEL
All comparison cameras are perspective, 50 degrees horizontal, 1600x900.
"""
import bpy, bmesh, sys, math, json, hashlib
from pathlib import Path
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
sys.dont_write_bytecode = True
R = Path(__file__).resolve().parent
MODE, MODEL = sys.argv[sys.argv.index('--')+1:][:2]
Q = R/'qa'; Q.mkdir(exist_ok=True)
def write(name, value):
    (Q/name).write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding='utf8')
def meshes(): return [o for o in bpy.context.scene.objects if o.type == 'MESH']
def group(o): return o.get('collection', '')
def context(o): return group(o)=='TERRAIN_CONTEXT'
def decals(o): return group(o)=='LIGHT_DECALS'
def effects(o): return o.get('material','')=='beam' or o.name.startswith('sunshaft_') or o.name=='sacred_light_cone'
def stats(objs):
    lo=[float('inf')]*3; hi=[-float('inf')]*3; triangles=vertices=0
    digest=hashlib.sha256()
    import struct
    for o in sorted(objs, key=lambda x:x.name):
        o.data.calc_loop_triangles(); triangles+=len(o.data.loop_triangles); vertices+=len(o.data.vertices)
        digest.update(o.name.encode());digest.update(str(o.parent.name if o.parent else None).encode())
        for v in o.data.vertices:
            p=o.matrix_world@v.co
            assert all(math.isfinite(t) for t in p)
            digest.update(struct.pack('<3f', *p))
            for i in range(3): lo[i]=min(lo[i], p[i]);hi[i]=max(hi[i],p[i])
    return dict(meshes=len(objs),vertices=vertices,triangles=triangles,min_m=lo,max_m=hi,
                dimensions_m=[hi[i]-lo[i] for i in range(3)],world_vertex_fingerprint=digest.hexdigest())
def load_native():
    if MODEL=='C55A': bpy.ops.wm.open_mainfile(filepath=str(R/'models/C55A_IMPORTED.blend'))
    else: bpy.ops.wm.open_mainfile(filepath=str(R.parent/'R19/final/R19_LIVING_HORIZON.blend'))
    return bpy.context.scene
def setup():
    s=load_native()
    for o in list(s.objects):
        if o.type in {'LIGHT','CAMERA'} or o.name.startswith('STUDIO '): bpy.data.objects.remove(o,do_unlink=True)
    original=stats([o for o in meshes() if not context(o)])
    lo=original['min_m']; hi=original['max_m']
    center=Vector(((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,0))
    rot=Matrix.Rotation(-math.pi/2 if MODEL=='C55A' else 0,4,'Z')
    T=rot@Matrix.Translation(-center)
    for o in list(s.objects):
        if o.parent is None:o.matrix_world=T@o.matrix_world
    bpy.context.view_layer.update()
    for o in meshes():o.hide_render=context(o) or effects(o)
    s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
    s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=16;s.cycles.use_denoising=True
    s.render.threads_mode='FIXED';s.render.threads=3 if MODE in {'floors','repair_floor','sections','supplemental'} else 5
    s.render.resolution_x=1600;s.render.resolution_y=900;s.render.resolution_percentage=100
    s.render.image_settings.file_format='PNG';s.render.film_transparent=False
    s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
    s.view_settings.exposure=0;s.view_settings.gamma=1
    s.world=bpy.data.worlds.new('R21_COMMON_WORLD');s.world.use_nodes=True
    bg=s.world.node_tree.nodes.get('Background');bg.inputs[0].default_value=(.3,.34,.38,1);bg.inputs[1].default_value=.6
    sun=bpy.data.lights.new('R21_COMMON_SUN','SUN');sun.energy=2.5;sun.angle=math.radians(10)
    light=bpy.data.objects.new(sun.name,sun);s.collection.objects.link(light)
    light.rotation_euler=Vector((-.45,.6,-.75)).to_track_quat('-Z','Y').to_euler()
    clay=bpy.data.materials.new('R21_IDENTICAL_NEUTRAL_CLAY');clay.use_nodes=True
    p=clay.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.46,.46,.46,1)
    p.inputs['Roughness'].default_value=.76;p.inputs['Metallic'].default_value=0
    for m in bpy.data.materials:
        if m.use_nodes:
            for n in m.node_tree.nodes:
                if n.type=='BSDF_PRINCIPLED' and 'Emission Strength' in n.inputs:n.inputs['Emission Strength'].default_value=0
                if n.type=='EMISSION':n.inputs['Strength'].default_value=0
    s.view_layers[0].material_override=clay
    d=bpy.data.cameras.new('R21_CAMERA');cam=bpy.data.objects.new(d.name,d);s.collection.objects.link(cam);s.camera=cam
    d.type='PERSP';d.sensor_fit='HORIZONTAL';d.sensor_width=36;d.lens=18/math.tan(math.radians(25));d.clip_start=.1;d.clip_end=100000
    return s,T,clay
def pose(s,pos,target):
    s.camera.location=pos;s.camera.rotation_euler=(Vector(target)-Vector(pos)).to_track_quat('-Z','Y').to_euler()
    bpy.context.view_layer.update()
def shoot(s,tag,pos,target,clay=True,show_decals=False,extra=None):
    for o in meshes():o.hide_render=context(o) or effects(o) or (decals(o) and not show_decals)
    s.view_layers[0].material_override=bpy.data.materials['R21_IDENTICAL_NEUTRAL_CLAY'] if clay else None
    pose(s,pos,target)
    folder=R/'renders'/MODEL;folder.mkdir(parents=True,exist_ok=True)
    s.render.filepath=str(folder/(tag+'.png'))
    out=dict(file=str(Path('renders')/MODEL/(tag+'.png')),position_m=list(pos),target_m=list(target),
             hfov_degrees=50,resolution=[1600,900],engine='CYCLES',samples=16,clay=clay,
             light_decals_visible=show_decals,emission=False,terrain_context=False,
             effect_meshes_hidden=[o.name for o in meshes() if effects(o)])
    if extra:out.update(extra)
    print('R21_RENDER_START',MODEL,tag,flush=True)
    bpy.ops.render.render(write_still=True)
    write(MODEL+'_'+tag+'.json',out)
    print('R21_RENDER_DONE',MODEL,tag,flush=True)
    return out
def fit_distance(s,direction,target):
    # Project all bounding-box corners, choose distance with 9% frame margin.
    points=[o.matrix_world@Vector(v) for o in meshes() if not context(o) and not decals(o) and not effects(o) for v in o.bound_box]
    direction=Vector(direction).normalized();rot=(-direction).to_track_quat('-Z','Y').to_matrix()
    inv=rot.transposed();t=Vector(target);tanx=math.tan(math.radians(25));tany=tanx*900/1600
    need=0
    for p in points:
        q=inv@(p-t)
        need=max(need,q.z+abs(q.x)/(.91*tanx),q.z+abs(q.y)/(.91*tany))
    return need
VIEWS={'front':(0,-1,.06),'oblique':(.8,-1,.48),'side':(1,0,.06),
       'rear':(0,1,.06),'aerial':(.3,-.5,1),'underside':(.4,-.5,-1)}
def exteriors(early=False):
    s,T,clay=setup();st=stats([o for o in meshes() if not context(o)])
    target=Vector((0,0,(st['min_m'][2]+st['max_m'][2])/2))
    tags=['oblique'] if early else list(VIEWS)
    for view in tags:
        d=Vector(VIEWS[view]).normalized()
        for regime in (['fixed10km'] if early else ['fixed16km','fit']):
            tag=regime+'_'+view
            if (R/'renders'/MODEL/(tag+'.png')).exists() and MODE!='rerender':continue
            dist=(10000 if regime=='fixed10km' else 16000) if regime!='fit' else fit_distance(s,d,target)
            shoot(s,tag,target+d*dist,target,extra=dict(center_distance_m=dist,regime=regime))
    if not early:
        for view in ['oblique','rear','underside']:
            d=Vector(VIEWS[view]).normalized();dist=fit_distance(s,d,target)
            shoot(s,'material_'+view,target+d*dist,target,False,True,dict(center_distance_m=dist))
        if MODEL=='C55A':
            d=Vector(VIEWS['oblique']).normalized()
            shoot(s,'clay_decals_on_oblique',target+d*fit_distance(s,d,target),target,True,True)
        pose(s,target+Vector(VIEWS['oblique']).normalized()*10000,target)
        s.view_layers[0].material_override=clay
        for o in meshes():o.hide_render=context(o) or effects(o) or decals(o)
        dest=R/'models';dest.mkdir(exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(dest/(MODEL+'_COMPARISON.blend')),compress=True)
        write(MODEL+'_transform.json',dict(matrix=[list(v) for v in T],native_stats=original_stats(MODEL),comparison_stats=st,
              rotation_z_degrees=-90 if MODEL=='C55A' else 0,scaling_applied=False,canonical_coordinates=False))
def original_stats(model):
    if model=='C55A':return json.loads((Q/'C55A_IMPORT.json').read_text())['central']
    return json.loads((Q/'R19_INVENTORY.json').read_text())['central']
def import_model():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(R/'source/model/C55A_SevenfoldHaloRift.glb'))
    s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
    before=dict(all=stats(meshes()),central=stats([o for o in meshes() if not context(o)]),materials=len(bpy.data.materials),
                inventory=[dict(name=o.name,group=group(o),parent=o.parent.name if o.parent else None,
                   min_m=[min((o.matrix_world@Vector(v))[i] for v in o.bound_box) for i in range(3)],
                   max_m=[max((o.matrix_world@Vector(v))[i] for v in o.bound_box) for i in range(3)]) for o in meshes()])
    dest=R/'models';dest.mkdir(exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(dest/'C55A_IMPORTED.blend'),compress=True)
    bpy.ops.wm.open_mainfile(filepath=str(dest/'C55A_IMPORTED.blend'))
    after=stats(meshes());assert before['all']==after
    assert before['all']['triangles']==668623
    before.update(readback=after,readback_exact=True,gltf_y_up_to_blender_z_up='Blender native importer; no added X rotation',units_m=1)
    write('C55A_IMPORT.json',before)
    global MODEL
    MODEL='R19';load_native()
    write('R19_INVENTORY.json',dict(central=stats([o for o in meshes() if not o.name.startswith('STUDIO ')])))
    print('R21_IMPORT_PASS',json.dumps({k:v for k,v in before.items() if k not in ['inventory']}),flush=True)
def make_bvh(objects):
    vs=[];fs=[];owners=[]
    for o in objects:
        off=len(vs);vs.extend([o.matrix_world@v.co for v in o.data.vertices]);o.data.calc_loop_triangles()
        for t in o.data.loop_triangles:fs.append(tuple(off+i for i in t.vertices));owners.append(o.name)
    return BVHTree.FromPolygons(vs,fs,all_triangles=True,epsilon=.00001),owners
def floor_views(render=True):
    s,T,clay=setup();architecture=[o for o in meshes() if not context(o) and not decals(o) and not effects(o)]
    bvh,owners=make_bvh(architecture)
    inv=T.inverted()
    def ray(p,d,dist=10000):
        p,n,idx,t=bvh.ray_cast(Vector(p),Vector(d).normalized(),dist)
        return None if idx is None else dict(point_m=list(p),normal=list(n),object=owners[idx],distance_m=t)
    def locate(name,desired,zrange,target):
        obj=bpy.data.objects[name];candidates=[]
        local_bvh,_=make_bvh([obj]);query=T@Vector(desired);query.z=zrange[1]+2
        dp,dn,di,dt=local_bvh.ray_cast(query,Vector((0,0,-1)),zrange[1]-zrange[0]+4)
        if di is not None and dn.z>.985 and zrange[0]<=dp.z<=zrange[1]:candidates.append((-1,dp,dn))
        obj.data.calc_loop_triangles()
        for tr in obj.data.loop_triangles:
            a,b,c=[obj.matrix_world@obj.data.vertices[i].co for i in tr.vertices]
            norm=(b-a).cross(c-a);area=norm.length/2
            if norm.length<.0001:continue
            norm.normalize();p=(a+b+c)/3
            if norm.z<.985 or area<4 or not zrange[0]<=p.z<=zrange[1]:continue
            score=(inv@p-Vector(desired)).length
            candidates.append((score,p,norm))
        for score,p,n in sorted(candidates,key=lambda v:v[0]):
            eye=p+Vector((0,0,1.7));near=bvh.find_nearest(eye)
            if near[3] is not None and near[3]<.5:continue
            down=ray(eye,(0,0,-1),2)
            if not down or abs(down['distance_m']-1.7)>.002 or down['object']!=name:continue
            patches=[ray(p+Vector((dx,dy,1.7)),(0,0,-1),2) for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]]
            if not all(v and abs(v['distance_m']-1.7)<.05 for v in patches):continue
            if any(ray(eye,d,.5) for d in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1)]):continue
            forward=T@Vector(target)-eye
            forward_hit=ray(eye,forward)
            if forward_hit and forward_hit['distance_m']<50:continue
            return p,eye,down,patches
        raise RuntimeError('NO_VALID_SUPPORTED_FLOOR '+name)
    if MODEL=='C55A':
        # Source coordinates. Actual triangle centroids replace all nominal heights.
        specs=[('low','floor_N',(1779,-54,0),(0,300),(-1021,-94,760)),
               ('mid','N_wall_ledges',(-850,800,1300),(1100,1600),(700,-400,1800)),
               ('high','N_wall_ledges',(-1000,1400,2800),(2600,3100),(900,-500,2500)),
               ('axis_entry','floor_N',(2050,-120,0),(0,300),(-2300,50,450)),
               ('axis_middle','floor_N',(0,350,88),(0,300),(-2400,50,650)),
               ('axis_arrival','apse_floor',(-2350,100,250),(245,260),(-3300,50,900)),
               ('hall','hall_floor',(-850,1200,440),(439,441),(100,1200,680))]
    else:
        specs=[('low','A_INNER_public_surface',(600,-600,306),(305,307),(1500,450,2100)),
               ('mid','F_PUBLIC_ISTHMUS_middle_public_street_public_deck',(-600,-65,1218),(1217,1219),(-1700,600,2200)),
               ('high','H_CANYON_GROUND_shared_roof_land',(1570,480,2520),(2519,2521),(-650,1540,3500)),
               ('axis_entry','A_PUBLIC_CAUSEWAY_public_deck',(-2500,-2040,152),(151,153),(0,2400,1300)),
               ('axis_middle','A_INNER_public_surface',(200,-300,306),(305,307),(0,2400,1300)),
               ('axis_arrival','C_REVERSE_civic_ground_0',(0,2100,950),(0,2000),(0,-1600,1500))]
        # R19 has no equivalent authored longitudinal promenade; arrival is explicitly a spatial sample.
        if specs[-1][1] not in bpy.data.objects:
            candidates=[o for o in architecture if o.name.startswith('C_REVERSE') and ('public_deck' in o.name or 'civic_ground' in o.name)]
            if not candidates:raise RuntimeError('No R19 rear public floor')
            specs[-1]=('axis_arrival',candidates[0].name,(0,2100,950),(0,2000),(0,-1600,1500))
    out=json.loads((Q/(MODEL+'_FLOORS.json')).read_text()) if MODE=='repair_floor' else {}
    for tag,name,desired,zrange,target in specs:
        if MODE=='repair_floor' and tag not in {'low','axis_entry'}:continue
        p,eye,down,patches=locate(name,desired,zrange,target);target=T@Vector(target)
        probes={k:ray(eye,d) for k,d in dict(east=(1,0,0),west=(-1,0,0),north=(0,1,0),south=(0,-1,0),up=(0,0,1),down=(0,0,-1)).items()}
        # First-hit samples inside actual 50-degree frustum, not transparency or x-ray views.
        pose(s,eye,target);rot=s.camera.rotation_euler.to_matrix();visible=[]
        for ix in range(-5,6):
            for iy in range(-3,4):
                d=rot@Vector((ix/5*math.tan(math.radians(25)),iy/3*math.tan(math.radians(25))*900/1600,-1))
                hit=ray(eye,d,15000)
                if hit:visible.append(hit)
        record=dict(native_floor_m=list(inv@p),eye_m=list(eye),floor=down,floor_patch_1m=patches,
                    eye_above_floor_m=eye.z-p.z,nearest_surface_m=bvh.find_nearest(eye)[3],six_axis_first_hits=probes,
                    frustum_first_hits=visible,walking_route_certified=False,
                    method='Upward actual triangle, global downward ray 1.7m; four floor patch rays; 0.5m local head/body clearance; forward first hit >=50m. Not closed-solid occupancy or continuous access certification.')
        out[tag]=record;write(MODEL+'_FLOORS.json',out)
        if render:shoot(s,'floor_'+tag,eye,target,True,False,record)
    if render and MODE!='repair_floor':
        # Same camera/material rules; original PBR retained with emission disabled.
        for tag in ['axis_middle','high']:
            v=out[tag];data=json.loads((Q/(MODEL+'_floor_'+tag+'.json')).read_text())
            shoot(s,'material_floor_'+tag,v['eye_m'],data['target_m'],False,True)
    write(MODEL+'_FLOORS.json',out)
def supplemental():
    s,T,clay=setup();st=stats([o for o in meshes() if not context(o)])
    target=Vector((0,0,(st['min_m'][2]+st['max_m'][2])/2));d=Vector((-.8,-1,.48)).normalized()
    dist=fit_distance(s,d,target)
    shoot(s,'fit_open_oblique',target+d*dist,target,True,False,dict(center_distance_m=dist,regime='fit',flank='west / C55A source south'))
    shoot(s,'material_open_oblique',target+d*dist,target,False,True,dict(center_distance_m=dist))
def matched_low():
    s,T,clay=setup();record=json.loads((Q/(MODEL+'_FLOORS.json')).read_text())['low']
    eye=Vector(record['eye_m']);target=eye+Vector((0,4000,4000*math.tan(math.radians(15))))
    bvh,owners=make_bvh([o for o in meshes() if not context(o) and not decals(o) and not effects(o)])
    pose(s,eye,target);rot=s.camera.rotation_euler.to_matrix();hits=[]
    for ix in range(-5,6):
        for iy in range(-3,4):
            d=(rot@Vector((ix/5*math.tan(math.radians(25)),iy/3*math.tan(math.radians(25))*900/1600,-1))).normalized()
            p,n,idx,dist=bvh.ray_cast(eye,d,15000)
            if idx is not None:hits.append(dict(point_m=list(p),object=owners[idx],distance_m=dist))
    shoot(s,'floor_low_axis15',eye,target,True,False,dict(eye_above_floor_m=record['eye_above_floor_m'],
          floor=record['floor'],pitch_degrees=15,horizontal_direction='comparison +Y (native main axis)',frustum_first_hits=hits,
          note='Same supported low-level eye; matched 15 degree upward pitch. No route certification.'))
def sections():
    # Physical bisect of copies. No automatic cap: shell openings remain honest.
    for axis,coord,label,view in [(0,860,'longitudinal_X860','side'),(1,-600,'cross_Yminus600','front')]:
        s,T,clay=setup();objects=[o for o in meshes() if not context(o) and not decals(o) and not effects(o)]
        native_plane=T.inverted()@Vector((coord if axis==0 else 0,coord if axis==1 else 0,0))
        plane=Vector();plane[axis]=coord;normal=Vector();normal[axis]=1
        changed=removed=0;segments=[]
        for o in objects:
            bm=bmesh.new();bm.from_mesh(o.data);inv=o.matrix_world.inverted()
            vals=[(o.matrix_world@v.co)[axis]-coord for v in bm.verts]
            crossing=min(vals)<0<max(vals) if vals else False
            result=bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.0001,
                  plane_co=inv@plane,plane_no=o.matrix_world.to_3x3().transposed()@normal,clear_inner=True,clear_outer=False)
            if not bm.faces:bm.free();bpy.data.objects.remove(o,do_unlink=True);removed+=1;continue
            if crossing:
                changed+=1
                for e in result['geom_cut']:
                    if isinstance(e,bmesh.types.BMEdge):segments.append(dict(object=o.name,points_m=[list(o.matrix_world@v.co) for v in e.verts]))
            bm.to_mesh(o.data);bm.free();o.data.update()
        # Hide rather than cut context/decals; both are excluded from this section evidence.
        st=stats([o for o in meshes() if not context(o) and not decals(o) and not effects(o)])
        target=Vector((0,0,2300));d=Vector((-1,0,.05) if axis==0 else (0,-1,.05)).normalized()
        dist=fit_distance(s,d,target)
        shoot(s,'section_'+label,target+d*dist,target,True,False,dict(plane_axis=axis,coordinate_m=coord,cap_added=False))
        folder=R/'sections';folder.mkdir(exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(folder/(MODEL+'_'+label+'.blend')),compress=True)
        write(MODEL+'_CUT_'+label+'.json',dict(plane_axis=axis,coordinate_m=coord,native_plane_point_m=list(native_plane),kept_positive_half=True,
          actual_mesh_bisect=True,cap_added=False,changed_meshes=changed,removed_meshes=removed,
          cut_segments=segments,section_stats=st,scope='Actual intersecting triangle edges; not inferred occupied or void volume.'))
if MODE=='import':import_model()
elif MODE=='early':exteriors(True)
elif MODE=='exterior':exteriors()
elif MODE=='rerender':exteriors()
elif MODE=='floors':floor_views()
elif MODE=='repair_floor':floor_views()
elif MODE=='probe_floors':floor_views(False)
elif MODE=='sections':sections()
elif MODE=='supplemental':supplemental()
elif MODE=='matched_low':matched_low()
