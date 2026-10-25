"""Offline saved-BLEND / empty-scene GLB readback and two real mesh cuts.
Not a certificate of connected enclosed void volume, occupancy or operation.
"""
import bpy,bmesh,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector,kdtree
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;Q=R/'qa';Q.mkdir(exist_ok=True)
sys.path.insert(0,str(R));import atelier as a
final=R/'final/R19_LIVING_HORIZON.blend'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def obs():return [o for o in bpy.data.collections['R19_LIVING_HORIZON'].objects if o.type=='MESH']
def metrics(objects):
 lo=[math.inf]*3;hi=[-math.inf]*3;tri=bad=nm=0;points=[];cent=[]
 for o in objects:
  me=o.data;me.calc_loop_triangles();tri+=len(me.loop_triangles)
  for v in me.vertices:
   p=o.matrix_world@v.co;points.append(tuple(p));bad+=not all(math.isfinite(c) for c in p)
   for k in range(3):lo[k]=min(lo[k],p[k]);hi[k]=max(hi[k],p[k])
  for t in me.loop_triangles:cent.append(tuple(sum((o.matrix_world@me.vertices[i].co for i in t.vertices),Vector())/3))
  bm=bmesh.new();bm.from_mesh(me);nm+=sum(not e.is_manifold for e in bm.edges);bm.free()
 return dict(min_m=lo,max_m=hi,span_xyz_m=[hi[k]-lo[k] for k in range(3)],mesh_objects=len(objects),triangles=tri,vertices=len(points),nonfinite_vertices=bad,separate_mesh_nonmanifold_edges=nm),points,cent
def distance(p,q):
 kd=kdtree.KDTree(len(q))
 for i,v in enumerate(q):kd.insert(v,i)
 kd.balance();return max((kd.find(v)[2] for v in p),default=0)
FINAL_ONLY='--final-only' in sys.argv
cases=[('final','R19_LIVING_HORIZON')] if FINAL_ONLY else [('initial','R19_INITIAL'),('revision_1','R19_REVISION_1'),('revision_2','R19_LIVING_HORIZON'),('final','R19_LIVING_HORIZON')]
sections={}
for axis,name,coordinate in ([] if FINAL_ONLY else [(1,'XZ_Y200',200),(0,'YZ_X0',0)]):
 bpy.ops.wm.open_mainfile(filepath=str(final));a.bind();s=bpy.context.scene
 mat=a.mat('Cut surface amber',(.75,.31,.055),.2,.6)
 plane=Vector();plane[axis]=coordinate;normal=Vector();normal[axis]=1;changed=removed=0
 for o in list(obs()):
  bm=bmesh.new();bm.from_mesh(o.data);inv=o.matrix_world.inverted()
  bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.0001,plane_co=inv@plane,plane_no=o.matrix_world.to_3x3().transposed()@normal,clear_inner=True,clear_outer=False)
  if not bm.faces:bm.free();bpy.data.objects.remove(o,do_unlink=True);removed+=1;continue
  edges=[e for e in bm.edges if e.is_boundary and all(abs((o.matrix_world@v.co)[axis]-coordinate)<.005 for v in e.verts)]
  if edges:
   o.data.materials.append(mat);idx=len(o.data.materials)-1
   for f in bmesh.ops.holes_fill(bm,edges=edges,sides=0).get('faces',[]):f.material_index=idx
   changed+=1
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
 c=bpy.data.objects['01_FRONT' if axis==1 else '03_SIDE'];c.location=(0,-15000,2700) if axis==1 else (-15000,700,2700)
 target=Vector((0,500,2000));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=8600
 s.render.threads=3
 a.save(R/'sections'/name,name,camera=c.name)
 s.render.filepath=str(R/'sections'/name/(name+'.png'));bpy.ops.render.render(write_still=True)
 sections[name]=dict(source_sha256=sha(final),plane_axis=axis,coordinate_m=coordinate,kept_positive_half=True,cut_meshes=changed,removed_meshes=removed)
 cases.append(('sections/'+name,name));print('SECTION',name,flush=True)
if not FINAL_ONLY:(Q/'ACTUAL_SECTIONS.json').write_text(json.dumps(sections,indent=2),encoding='utf8')
out=json.loads((Q/'BLEND_GLB_READBACK.json').read_text(encoding='utf8')) if FINAL_ONLY else {'scope':'Saved file reopens, finite world vertices, triangle counts, bounds, bidirectional nearest vertices and triangle centroids within 2cm. Not full topology/collision/volume/operation/art certification.','models':{}}
for folder,stem in cases:
 bl=R/folder/(stem+'.blend');gl=R/folder/(stem+'.glb')
 bpy.ops.wm.open_mainfile(filepath=str(bl));native,p,c=metrics(obs())
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(gl))
 imported,ip,ic=metrics([o for o in bpy.context.scene.objects if o.type=='MESH'])
 err=max(abs(native[k][i]-imported[k][i]) for k in ['min_m','max_m'] for i in range(3));ve=max(distance(p,ip),distance(ip,p));ce=max(distance(c,ic),distance(ic,c))
 checks=dict(saved_blend_open=True,empty_scene_glb_import=True,bounds_max_error_m=err,vertex_bidirectional_max_error_m=ve,triangle_centroid_bidirectional_max_error_m=ce,geometry_under_2cm=max(err,ve,ce)<.02,triangles_equal=native['triangles']==imported['triangles'],finite=native['nonfinite_vertices']==imported['nonfinite_vertices']==0)
 out['models'][folder+'/'+stem]=dict(native=native,glb=imported,checks=checks,blend_sha256=sha(bl),glb_sha256=sha(gl))
 print('READBACK',stem,checks,flush=True)
 if folder=='final' and '--geometry-only' not in sys.argv:
  with bpy.data.libraries.load(str(bl),link=False) as (src,dst):dst.collections=['REVIEW_STUDIO'];dst.worlds=src.worlds
  for coll in dst.collections:
   if coll:bpy.context.scene.collection.children.link(coll)
  s=bpy.context.scene;s.world=dst.worlds[0];s.camera=bpy.data.objects['02_OBLIQUE'];s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=3;s.view_settings.view_transform='AgX'
  s.render.resolution_x=1280;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
  s.render.filepath=str(Q/'GLB_REIMPORTED.png');bpy.ops.render.render(write_still=True)
out['basic_persistence_pass']=all(all(v['checks'][k] for k in ['saved_blend_open','empty_scene_glb_import','geometry_under_2cm','triangles_equal','finite']) for v in out['models'].values())
(Q/'BLEND_GLB_READBACK.json').write_text(json.dumps(out,indent=2),encoding='utf8');print('PERSISTENCE_PASS',out['basic_persistence_pass'],flush=True)
