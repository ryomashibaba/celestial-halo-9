"""Run only after the macro art review. Background Blender verification/sections.
No Minecraft paths or upstream writes. All reported samples are limited samples.
"""
import bpy,bmesh,sys,json,hashlib,struct,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent
MODE=sys.argv[sys.argv.index('--')+1]
def write(name,v):(R/'qa'/name).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
def meshes():return [o for o in bpy.context.scene.objects if o.type=='MESH']
def stats():
    lo=[math.inf]*3;hi=[-math.inf]*3;verts=tris=0;digest=hashlib.sha256();top=[]
    for o in sorted(meshes(),key=lambda o:o.name):
        o.data.calc_loop_triangles();verts+=len(o.data.vertices);tris+=len(o.data.loop_triangles)
        digest.update(o.name.encode())
        for v in o.data.vertices:
            p=o.matrix_world@v.co;assert all(math.isfinite(t) for t in p)
            digest.update(struct.pack('<3f',*p))
            for k in range(3):lo[k]=min(lo[k],p[k]);hi[k]=max(hi[k],p[k])
        bm=bmesh.new();bm.from_mesh(o.data)
        top.append(dict(name=o.name,role=o.get('role'),vertices=len(bm.verts),faces=len(bm.faces),boundary_edges=sum(e.is_boundary for e in bm.edges),nonmanifold_edges=sum(not e.is_manifold for e in bm.edges),zero_area_faces=sum(f.calc_area()<1e-8 for f in bm.faces)))
        bm.free()
    return dict(meshes=len(meshes()),vertices=verts,triangles=tris,min_m=lo,max_m=hi,dimensions_m=[hi[k]-lo[k] for k in range(3)],fingerprint=digest.hexdigest(),objects=top)
def floors():
    s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();out=[]
    # Ray samples for floor support, not continuous walk certification.
    for n in ['ground_1p7','mid_1p7','high_1p7']:
        c=bpy.data.objects[n];p=c.location.copy();hit,loc,norm,face,obj,mat=s.ray_cast(dg,p,Vector((0,0,-1)),distance=10)
        near=[]
        for dx,dy in [(-.5,-.5),(-.5,.5),(.5,-.5),(.5,.5)]:
            r=s.ray_cast(dg,p+Vector((dx,dy,0)),Vector((0,0,-1)),distance=10);near.append(dict(offset=[dx,dy],hit=r[0],distance=(p+Vector((dx,dy,0))-r[1]).length if r[0] else None))
        # Six axial clear rays at eye and waist. These do not prove solid occupancy.
        clearance=[]
        for dz in [0,-.8]:
            for d in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1)]:
                r=s.ray_cast(dg,p+Vector((0,0,dz)),Vector(d),distance=.6)
                clearance.append(dict(offset_z=dz,direction=d,hit_within_0p6m=r[0],object=r[4].name if r[0] else None))
        forward=-(c.rotation_euler.to_matrix().col[2]);viewhit=s.ray_cast(dg,p,forward,distance=15000)
        downsurface=None
        if hit:
            origin=obj.matrix_world.inverted()@(loc-Vector((0,0,.01)))
            direction=(obj.matrix_world.inverted().to_3x3()@Vector((0,0,-1))).normalized()
            exit=obj.ray_cast(origin,direction,distance=10000)
            if exit[0]:downsurface=(loc-(obj.matrix_world@exit[1])).length
        out.append(dict(camera=n,eye_m=list(p),floor_hit=hit,floor_object=obj.name if hit else None,floor_point=list(loc) if hit else None,eye_above_floor_m=(p-loc).length if hit else None,floor_normal=list(norm) if hit else None,next_surface_below_same_support_m=downsurface,surrounding_1m_support=near,local_clearance=clearance,first_forward_surface_m=(p-viewhit[1]).length if viewhit[0] else None,first_forward_object=viewhit[4].name if viewhit[0] else None))
    return out
def load():bpy.ops.wm.open_mainfile(filepath=str(R/'final/R23_CROSSING_HORIZONS.blend'))
if MODE=='verify':
    load();before=stats();samples=floors()
    bpy.ops.wm.save_as_mainfile(filepath=str(R/'final/R23_CROSSING_HORIZONS.blend'),compress=True)
    load();after=stats()
    assert before['fingerprint']==after['fingerprint'] and before['triangles']==after['triangles']
    bpy.ops.object.select_all(action='DESELECT')
    for o in meshes():o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(R/'final/R23_CROSSING_HORIZONS.glb'),export_format='GLB',use_selection=True,export_extras=True,export_cameras=False,export_lights=False)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'final/R23_CROSSING_HORIZONS.glb'))
    imported=stats();errors=[abs(a-b) for a,b in zip(after['min_m']+after['max_m'],imported['min_m']+imported['max_m'])]
    out=dict(blender_version=bpy.app.version_string,unit_scale=1,blend_exact_geometry_reload=before['fingerprint']==after['fingerprint'],blend=after,glb=imported,glb_aabb_max_error_m=max(errors),glb_triangle_count_matches=after['triangles']==imported['triangles'],floor_samples=samples,not_verified=['global self-intersections and inter-object unions','connected enclosed air volume','continuous walkability or ground-to-sky route','inhabited room capacity or utility service','transport operation or structural safety','Minecraft voxel conversion or official coordinates'],stage_two_started=False)
    write('FINAL_VERIFICATION.json',out)
    print(json.dumps({k:v for k,v in out.items() if k not in ['blend','glb','floor_samples']}))
    assert max(errors)<.01 and out['glb_triangle_count_matches']
elif MODE=='sections':
    records=[]
    for tag,axis,value,clear_outer,pos,target in [
      ('LONG_Xminus800',0,-800,True,(15000,0,2400),(-800,0,2400)),
      ('CROSS_Y500',1,500,False,(0,-15000,2400),(0,500,2400))]:
        load();s=bpy.context.scene;segs=[];cutobjs=[];normal=Vector((1 if axis==0 else 0,1 if axis==1 else 0,0));co=normal*value
        for o in list(meshes()):
            bm=bmesh.new();bm.from_mesh(o.data);bm.transform(o.matrix_world)
            result=bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.0001,plane_co=co,plane_no=normal,clear_outer=clear_outer,clear_inner=not clear_outer)
            edges=[e for e in bm.edges if e.is_boundary and all(abs(v.co[axis]-value)<.01 for v in e.verts)]
            if edges:cutobjs.append(o.name)
            for e in edges:segs.append([list(v.co) for v in e.verts])
            bm.to_mesh(o.data);bm.free();o.matrix_world.identity()
        # Actual cut contour, not a fill or a new wall. No cut caps are fabricated.
        mat=bpy.data.materials.new('ORANGE ACTUAL SECTION EDGE');mat.diffuse_color=(.9,.22,.025,1);mat.use_nodes=True
        mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.9,.22,.025,1)
        cu=bpy.data.curves.new('Actual cut line','CURVE');cu.dimensions='3D';cu.bevel_depth=5;cu.bevel_resolution=0
        for a,b in segs:
            sp=cu.splines.new('POLY');sp.points.add(1);sp.points[0].co=(*a,1);sp.points[1].co=(*b,1)
        line=bpy.data.objects.new('ACTUAL CUT CONTOUR / no caps',cu);s.collection.objects.link(line);cu.materials.append(mat)
        c=s.camera=bpy.data.objects['front'];c.data.type='ORTHO';c.data.ortho_scale=8300;c.location=pos;c.rotation_euler=(Vector(target)-Vector(pos)).to_track_quat('-Z','Y').to_euler()
        s.render.resolution_x=1600;s.render.resolution_y=1100;s.cycles.samples=24
        s.render.filepath=str(R/'sections'/(tag+'.png'))
        bpy.ops.wm.save_as_mainfile(filepath=str(R/'sections'/(tag+'.blend')),compress=True)
        bpy.ops.wm.open_mainfile(filepath=str(R/'sections'/(tag+'.blend')));s=bpy.context.scene
        bpy.ops.render.render(write_still=True)
        records.append(dict(section=tag,plane_axis='XY'[axis],plane_coordinate_m=value,cut_objects=cutobjs,cut_segments=len(segs),caps_added=False,orange_line='actual open boundary on the section plane; 5m diagrammatic radius',topology='This inspection copy is intentionally open at the cuts.'))
    write('REAL_SECTIONS.json',records)
