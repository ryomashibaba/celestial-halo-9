"""One bounded architectural edit, after observation of the native source copy.
Triangle clipping subtracts only the three stated convex volumes; no source generator.
"""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'models/C55A_BEFORE.blend'))
s=bpy.context.scene
volumes=[([-498,600,647.5],[-402,700,770]),([-498,700,647.5],[-338,880,815]),([-450,880,647.5],[-370,985,720])]
def split(poly,axis,value,sgn):
 inside=[];outside=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  da=sgn*(a[axis]-value);db=sgn*(b[axis]-value)
  (inside if da>=-1e-7 else outside).append(a)
  if (da>1e-7 and db<-1e-7) or (da<-1e-7 and db>1e-7):
   p=a+(b-a)*(da/(da-db));inside.append(p);outside.append(p)
 return inside,outside
def subtract(poly,lo,hi):
 # Sequentially peel off pieces outside each clipping plane.
 current=poly;pieces=[]
 for axis,value,sgn in [(0,lo[0],1),(0,hi[0],-1),(1,lo[1],1),(1,hi[1],-1),(2,lo[2],1),(2,hi[2],-1)]:
  if len(current)<3:break
  current,out=split(current,axis,value,sgn)
  if len(out)>=3:pieces.append(out)
 return pieces
changed=[]
for o in list(s.objects):
 if o.type!='MESH':continue
 pts=[o.matrix_world@Vector(v) for v in o.bound_box]
 if not any(all(max(p[i] for p in pts)>lo[i] and min(p[i] for p in pts)<hi[i] for i in range(3)) for lo,hi in volumes):continue
 old=o.data;old.calc_loop_triangles();verts=[];faces=[];mats=[];affected=0
 inv=o.matrix_world.inverted()
 for t in old.loop_triangles:
  poly=[o.matrix_world@old.vertices[i].co for i in t.vertices];polys=[poly]
  for lo,hi in volumes:
   nextp=[]
   for p in polys:
    if any(max(v[i] for v in p)<=lo[i] or min(v[i] for v in p)>=hi[i] for i in range(3)):nextp.append(p)
    else:nextp.extend(subtract(p,lo,hi));affected+=1
   polys=nextp
  for p in polys:
   off=len(verts);verts.extend(inv@v for v in p)
   for j in range(1,len(p)-1):faces.append((off,off+j,off+j+1));mats.append(t.material_index)
 if not affected:continue
 mesh=bpy.data.meshes.new(o.name+'_R25_LOCAL_CUT');mesh.from_pydata(verts,[],faces);mesh.update()
 for m in old.materials:mesh.materials.append(m)
 for p,mi in zip(mesh.polygons,mats):p.material_index=mi
 o.data=mesh;changed.append(dict(name=o.name,old_triangles=len(old.loop_triangles),new_triangles=len(faces),clip_events=affected))
coll=bpy.data.collections.new('R25_LOCAL_PUBLIC_PASSAGE');s.collection.children.link(coll)
def mesh(name,verts,faces):
 m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update();o=bpy.data.objects.new(name,m);coll.objects.link(o);o['R25_new']=True;return o
def box(name,lo,hi):
 x,y,z=lo;X,Y,Z=hi
 return mesh(name,[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
# The route rises 20.221 m to the pre-existing upper hall gallery.
sections=[(582,647.779,-498,-402),(700,653.5,-498,-402),(725,654.7,-498,-338),(855,661,-498,-338),(880,662.2,-450,-370),(955,668,-450,-370),(975,668,-450,-370)]
v=[]
for y,z,x,X in sections:v.extend([(x,y,z),(X,y,z),(x,y,z-4),(X,y,z-4)])
f=[]
for k in range(len(sections)-1):
 a=4*k;b=a+4;f.extend([(a,a+1,b+1,b),(a+2,b+2,b+3,a+3),(a,b,b+2,a+2),(a+1,a+3,b+3,b+1)])
f.extend([(0,2,3,1),(len(v)-4,len(v)-3,len(v)-1,len(v)-2)])
mesh('R25_PUBLIC_RAMP_AND_ARRIVAL',v,f)
# Thick jambs, reveals and a chamber with a higher ceiling: boundaries, not floating decoration.
for i,(lo,hi) in enumerate(volumes):
 x,y,z=lo;X,Y,Z=hi
 box(f'R25_REVEAL_W_{i}',(x-8,y,647),(x,Y,Z+8))
 box(f'R25_REVEAL_E_{i}',(X,y,647),(X+8,Y,Z+8))
 box(f'R25_SOFFIT_{i}',(x,y,Z),(X,Y,Z+8))
# Close step faces between the compressed thresholds and the taller offset public chamber.
box('R25_ENTRY_CHAMBER_RETURN',( -498,696,770),(-402,704,815))
box('R25_EXIT_CHAMBER_RETURN',(-450,876,720),(-370,884,815))
box('R25_CHAMBER_END_W',(-498,876,647),(-450,884,815))
box('R25_CHAMBER_END_E',(-370,876,647),(-338,884,815))
# One overlook parapet with a lateral gap continuing onto the existing gallery.
box('R25_OVERLOOK_PARAPET',(-450,974,668),(-398,976,669.2))
(R/'qa/EDIT_MANIFEST.json').write_text(json.dumps(dict(scope_native_m=volumes,changed_source_meshes=changed,sections=sections,method='triangle clipping of actual existing surfaces plus bounded floor/reveal/soffit meshes; source generator not executed',new_objects=[o.name for o in coll.objects],source_overwritten=False),indent=2),encoding='utf8')
s.camera=bpy.data.objects['01_local']
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/C55A_R25_LOCAL_EDIT.blend'),compress=True)
for name in json.loads((R/'qa/CAMERAS.json').read_text()):
 s.camera=bpy.data.objects[name];s.render.filepath=str(R/'renders'/('after_'+name+'.png'));bpy.ops.render.render(write_still=True);print('DONE',name,flush=True)
