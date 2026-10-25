"""Actual mesh bisects, saved-file opens and empty-scene GLB imports.
Persistence checks do not certify art, occupancy, structural safety or traversal.
"""
import bpy,bmesh,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
FINAL=ROOT/'revision_2/R15_FINAL.blend'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def metrics(obs):
 lo=[math.inf]*3;hi=[-math.inf]*3;tri=nv=bad=nm=0
 for o in obs:
  me=o.data;me.calc_loop_triangles();tri+=len(me.loop_triangles);nv+=len(me.vertices)
  for v in me.vertices:
   p=o.matrix_world@v.co
   bad+=int(not all(math.isfinite(c) for c in p))
   for i in range(3):lo[i]=min(lo[i],p[i]);hi[i]=max(hi[i],p[i])
  bm=bmesh.new();bm.from_mesh(me);nm+=sum(not e.is_manifold for e in bm.edges);bm.free()
 return dict(min_m=lo,max_m=hi,span_xyz_m=[hi[i]-lo[i] for i in range(3)],meshes=len(obs),vertices=nv,triangles=tri,nonfinite_vertices=bad,separate_solid_nonmanifold_edges=nm)
def save_glb(folder,stem):
 bpy.ops.object.select_all(action='DESELECT')
 for o in bpy.data.collections['R15_SYMMETRIC_LIVED_WORLD'].objects:o.select_set(True)
 bpy.ops.wm.save_as_mainfile(filepath=str(folder/(stem+'.blend')),compress=True)
 bpy.ops.export_scene.gltf(filepath=str(folder/(stem+'.glb')),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False)
cases=[('concept','R15_CONCEPT'),('revision_1','R15_REVISION_1'),('revision_2/observed_before_refinement','R15_OPEN_CLEFT_ATTEMPT'),('revision_2','R15_FINAL')]
sections={}
for axis,name in [(1,'SECTION_XZ_Y0'),(0,'SECTION_YZ_X0')]:
 bpy.ops.wm.open_mainfile(filepath=str(FINAL));s=bpy.context.scene
 cap=bpy.data.materials.new('Actual cut faces ochre');cap.diffuse_color=(.68,.32,.08,1);cap.use_nodes=True
 p=next(n for n in cap.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(.68,.32,.08,1)
 normal=Vector((0,1,0) if axis==1 else (1,0,0));changed=deleted=0
 for o in list(bpy.data.collections['R15_SYMMETRIC_LIVED_WORLD'].objects):
  if o.type!='MESH':continue
  bm=bmesh.new();bm.from_mesh(o.data)
  # Native study meshes have identity transforms, but use inverse for explicit plane conversion.
  inv=o.matrix_world.inverted();co=inv@Vector((0,0,0));no=o.matrix_world.to_3x3().transposed()@normal
  before=len(bm.verts)
  result=bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.0001,plane_co=co,plane_no=no,clear_inner=True,clear_outer=False)
  if not bm.faces:
   bm.free();bpy.data.objects.remove(o,do_unlink=True);deleted+=1;continue
  edges=[e for e in bm.edges if e.is_boundary and all(abs((o.matrix_world@v.co)[axis])<.003 for v in e.verts)]
  if edges:
   o.data.materials.append(cap);idx=len(o.data.materials)-1
   filled=bmesh.ops.holes_fill(bm,edges=edges,sides=0)
   for f in filled.get('faces',[]):f.material_index=idx
   changed+=1
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
 folder=ROOT/'sections'/name;folder.mkdir(parents=True,exist_ok=True)
 if axis==1:
  c=bpy.data.objects['01_FRONT'];c.location=(0,-5500,1150);target=Vector((0,0,1030));c.data.ortho_scale=3400
 else:
  c=bpy.data.objects['03_SIDE'];c.location=(-5500,0,1150);target=Vector((0,0,1030));c.data.ortho_scale=3200
 c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();s.camera=c
 save_glb(folder,name)
 s.render.filepath=str(folder/(name+'.png'));bpy.ops.render.render(write_still=True)
 sections[name]=dict(source_sha256=digest(FINAL),plane_axis=axis,plane_m=0,kept_positive_half=True,meshes_capped=changed,meshes_removed=deleted)
 cases.append(('sections/'+name,name));print('SECTION DONE',name,flush=True)
(ROOT/'qa').mkdir(exist_ok=True)
(ROOT/'qa/ACTUAL_SECTIONS.json').write_text(json.dumps(sections,indent=2),encoding='utf8')
out={'scope':'Actual saved BLEND open, GLB empty-scene import, world bounds, triangles, finite vertices and independent solid edge topology only. No full occupancy, collisions, structure or art certification.','models':{}}
for directory,stem in cases:
 folder=ROOT/directory;bl=folder/(stem+'.blend');glb=folder/(stem+'.glb')
 bpy.ops.wm.open_mainfile(filepath=str(bl))
 native=metrics([o for o in bpy.data.collections['R15_SYMMETRIC_LIVED_WORLD'].objects if o.type=='MESH'])
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb))
 imported=metrics([o for o in bpy.context.scene.objects if o.type=='MESH'])
 delta=max(abs(native[k][i]-imported[k][i]) for k in ('min_m','max_m') for i in range(3))
 checks=dict(actual_saved_blend_open=True,actual_empty_scene_glb_import=True,bounds_max_error_m=delta,bounds_under_2cm=delta<.02,triangles_equal=native['triangles']==imported['triangles'],finite=native['nonfinite_vertices']==imported['nonfinite_vertices']==0)
 out['models'][stem]=dict(blend_sha256=digest(bl),glb_sha256=digest(glb),native=native,glb_import=imported,checks=checks)
 print('READBACK',stem,checks,flush=True)
out['pass_basic_persistence']=all(all(r['checks'][k] for k in ('actual_saved_blend_open','actual_empty_scene_glb_import','bounds_under_2cm','triangles_equal','finite')) for r in out['models'].values())
(ROOT/'qa/BLEND_GLB_READBACK.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print('QA COMPLETE',out['pass_basic_persistence'],flush=True)
