"""Independent Blender readback, real BMesh cuts, geometric equivalence.
Offline; no actual saves or canonical city geometry are read.
"""
import bpy,bmesh,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector,kdtree
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;Q=R/'qa';Q.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def objects():return [o for o in bpy.data.collections['R17_URBAN_CONTINENTS'].objects if o.type=='MESH']
def metrics(obs):
 lo=[math.inf]*3;hi=[-math.inf]*3;tris=bad=nonmanifold=0;points=[];centroids=[]
 for o in obs:
  me=o.data;me.calc_loop_triangles();tris+=len(me.loop_triangles)
  for v in me.vertices:
   p=o.matrix_world@v.co;points.append(tuple(p));bad+=not all(math.isfinite(c) for c in p)
   for k in range(3):lo[k]=min(lo[k],p[k]);hi[k]=max(hi[k],p[k])
  for t in me.loop_triangles:centroids.append(tuple(sum((o.matrix_world@me.vertices[i].co for i in t.vertices),Vector())/3))
  bm=bmesh.new();bm.from_mesh(me);nonmanifold+=sum(not e.is_manifold for e in bm.edges);bm.free()
 return dict(min_m=lo,max_m=hi,span_xyz_m=[hi[k]-lo[k] for k in range(3)],triangles=tris,mesh_objects=len(obs),vertices=len(points),nonfinite_vertices=bad,separate_mesh_nonmanifold_edges=nonmanifold),points,centroids
def hausdorff(a,b):
 kd=kdtree.KDTree(len(b))
 for i,p in enumerate(b):kd.insert(p,i)
 kd.balance();return max((kd.find(p)[2] for p in a),default=0)
final=R/'revision_2/R17_REVISION_2.blend'
cases=[('exploration_A','R17_A'),('exploration_B','R17_B'),('exploration_C','R17_C'),('revision_1','R17_REVISION_1'),('revision_2','R17_REVISION_2')]
sections={}
for axis,name,coordinate in [(1,'SECTION_XZ_Y500',500),(0,'SECTION_YZ_X0',0)]:
 bpy.ops.wm.open_mainfile(filepath=str(final));S=bpy.context.scene
 mat=bpy.data.materials.new('Actual section cap ochre');mat.use_nodes=True
 p=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(.65,.29,.08,1)
 normal=Vector((0,1,0) if axis==1 else (1,0,0));plane=Vector();plane[axis]=coordinate;changed=removed=0
 for o in list(objects()):
  bm=bmesh.new();bm.from_mesh(o.data);inv=o.matrix_world.inverted()
  bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.0001,plane_co=inv@plane,plane_no=o.matrix_world.to_3x3().transposed()@normal,clear_inner=True,clear_outer=False)
  if not bm.faces:bm.free();bpy.data.objects.remove(o,do_unlink=True);removed+=1;continue
  edges=[e for e in bm.edges if e.is_boundary and all(abs((o.matrix_world@v.co)[axis]-coordinate)<.003 for v in e.verts)]
  if edges:
   o.data.materials.append(mat);idx=len(o.data.materials)-1
   for face in bmesh.ops.holes_fill(bm,edges=edges,sides=0).get('faces',[]):face.material_index=idx
   changed+=1
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
 folder=R/'sections'/name;folder.mkdir(parents=True,exist_ok=True)
 c=bpy.data.objects['01_FRONT' if axis==1 else '03_SIDE'];c.location=(0,-13000,2350) if axis==1 else (-14000,500,2350)
 target=Vector((0,500,2100));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=8000;S.camera=c
 bpy.ops.wm.save_as_mainfile(filepath=str(folder/(name+'.blend')),compress=True)
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects():o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(folder/(name+'.glb')),export_format='GLB',use_selection=True)
 S.render.filepath=str(folder/(name+'.png'));bpy.ops.render.render(write_still=True)
 sections[name]=dict(source_sha256=sha(final),plane_axis=axis,coordinate_m=coordinate,kept_positive=True,cut_meshes=changed,removed_meshes=removed)
 cases.append(('sections/'+name,name));print('SECTION',name,flush=True)
(Q/'ACTUAL_SECTIONS.json').write_text(json.dumps(sections,indent=2),encoding='utf8')
out={'scope':'Actual saved-file reopen, empty-scene GLB import, world bounds, finite vertices, triangles and bidirectional nearest vertex/triangle-centroid positions. Not collision, occupancy, topology volume, traversal or art certification.','models':{}}
for folder,stem in cases:
 bl=R/folder/(stem+'.blend');gl=R/folder/(stem+'.glb')
 bpy.ops.wm.open_mainfile(filepath=str(bl));native,pts,cent=metrics(objects())
 # Retain original camera/studio only for final independent GLB render.
 if stem=='R17_REVISION_2':
  camera=bpy.data.objects['02_OBLIQUE'];camera_matrix=camera.matrix_world.copy();ortho=camera.data.ortho_scale
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(gl))
 imported,ip,ic=metrics([o for o in bpy.context.scene.objects if o.type=='MESH'])
 err=max(abs(native[k][i]-imported[k][i]) for k in ('min_m','max_m') for i in range(3))
 pe=max(hausdorff(pts,ip),hausdorff(ip,pts));ce=max(hausdorff(cent,ic),hausdorff(ic,cent))
 checks=dict(saved_blend_open=True,empty_scene_glb_import=True,bounds_max_error_m=err,vertices_bidirectional_max_error_m=pe,triangle_centroids_bidirectional_max_error_m=ce,geometry_under_2cm=max(err,pe,ce)<.02,triangles_equal=native['triangles']==imported['triangles'],finite=native['nonfinite_vertices']==imported['nonfinite_vertices']==0)
 out['models'][stem]=dict(native=native,glb_import=imported,checks=checks,blend_sha256=sha(bl),glb_sha256=sha(gl))
 print('READBACK',stem,checks,flush=True)
 if stem=='R17_REVISION_2':
  # Use only imported architecture; append native studio, never native geometry.
  with bpy.data.libraries.load(str(bl),link=False) as (src,dst):dst.collections=['STUDIO_NONCANONICAL']
  for collection in dst.collections:
   if collection:bpy.context.scene.collection.children.link(collection)
  S=bpy.context.scene;S.render.engine='CYCLES';S.cycles.samples=16;S.cycles.use_denoising=True;S.render.threads_mode='FIXED';S.render.threads=6
  S.render.resolution_x=1100;S.render.resolution_y=1000;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';S.view_settings.view_transform='AgX'
  with bpy.data.libraries.load(str(bl),link=False) as (src,dst):dst.worlds=src.worlds
  S.world=dst.worlds[0];S.camera=next(o for o in S.objects if o.type=='CAMERA' and o.name.startswith('02_OBLIQUE'))
  S.render.filepath=str(Q/'GLB_REIMPORT_OBLIQUE.png');bpy.ops.render.render(write_still=True)
out['basic_persistence_pass']=all(all(x['checks'][k] for k in ['saved_blend_open','empty_scene_glb_import','geometry_under_2cm','triangles_equal','finite']) for x in out['models'].values())
bpy.ops.wm.open_mainfile(filepath=str(R/'context/R17_NONCANONICAL_10KM.blend'))
context_metrics,context_points,context_centroids=metrics(objects())
out['context_native_reopened']={'architecture_matches_final_triangles':context_metrics['triangles']==out['models']['R17_REVISION_2']['native']['triangles'],'architecture_span_matches':context_metrics['span_xyz_m']==out['models']['R17_REVISION_2']['native']['span_xyz_m'],'canonical_alignment':'UNVERIFIED','W0_integrated':False}
(Q/'BLEND_GLB_READBACK.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print('INDEPENDENT QA',out['basic_persistence_pass'],flush=True)
