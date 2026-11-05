"""LCS2 R3 -- one source-pinned intervention on the real R2 BLEND.
Public uses generate monumental section; not an approved city nor Minecraft source.
"""
import bpy,math,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=Path(args[args.index('--output')+1]);out.mkdir(parents=True,exist_ok=True)
(out/'renders').mkdir(exist_ok=True)
source=Path(bpy.data.filepath)
SOURCE_SHA='3ef9ea7e97d3b7008372db3bc39656c1c207dc0ea5804c5a1df20c7e4260d243'
assert source.name=='LCS2_R3_SOURCE.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()==SOURCE_SHA
S=bpy.context.scene
assert S['FORMAL_ART_ACCEPTED']==0 and S['COMPLETED_TARGETS']==0 and S['CONSTRUCTION']=='HOLD'
views=['E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL']
cameras={n:bpy.data.objects[n].matrix_world.copy() for n in views}
removed=[]
for o in tuple(S.objects):
 if o.type not in {'MESH','CURVE'}:continue
 if o.name.startswith(('LCS2_west_fault_deep_inhabited_support_',
     'LCS2_east_sky_room_weightbearing_',
     'LCS2_diagonal_fault_civic_public_hall_floor_',
     'LCS2_civic_open_vault_west_root_',
     'LCS2_civic_open_vault_east_root_',
     'LCS2_skylight_vault_fork_west_',
     'LCS2_skylight_vault_fork_east_')) or o.name in {
         'R2_WEST_FAULT_INHABITED_CITY_ROOF_1',
         'R2_WEST_FAULT_INHABITED_CITY_ROOF_3',
         'R2_EAST_FAULT_CIVIC_ROOM_ROOF_0',
         'R2_EAST_FAULT_CIVIC_ROOM_ROOF_2'}:
  removed.append(o.name)
  bpy.data.objects.remove(o,do_unlink=True)
assert len(removed)>=28,len(removed)
C=bpy.data.collections.new('LCS2_R3_INHABITED_FAULT_CITY_UNAPPROVED')
S.collection.children.link(C)
roles={
 'white':('LCS2_por​ous_limestone',(.62,.70,.69)),
 'ivory':('LCS2_ceramic_public_rooms',(.82,.79,.65)),
 'dark':('LCS2_deep_rift_stone',(.075,.125,.16)),
 'bronze':('LCS2_bronze_tracer',(.55,.32,.17)),
 'glass':('LCS2_civic_glass',(.055,.28,.34)),
 'roof':('LCS2_matte_titanium',(.27,.36,.4)),
 'garden':('LCS2_roof_gardens',(.18,.36,.24)),
 'street':('LCS2_pedestrian_paving',(.40,.48,.46)),
 'warm':('LCS2_inhabited_luminance',(.88,.53,.26))}
M={}
for k,(name,rgb) in roles.items():
 name=name.replace('\u200b','')
 mat=bpy.data.materials.get(name)
 if mat is None:
  mat=bpy.data.materials.new('LCS2_R3_'+k)
  mat.use_nodes=True
  mat.diffuse_color=(*rgb,1)
  n=mat.node_tree.nodes.get('Principled BSDF')
  n.inputs['Base Color'].default_value=(*rgb,1)
  n.inputs['Roughness'].default_value=.51
 M[k]=mat
def mesh(name,v,f,m):
 me=bpy.data.meshes.new(name)
 me.from_pydata(v,[],f);me.update()
 ob=bpy.data.objects.new('R3_'+name,me);C.objects.link(ob);me.materials.append(M[m]);return ob
def slab(name,p,z,d,m):
 n=len(p);v=[(x,y,z-d) for x,y in p]+[(x,y,z) for x,y in p]
 f=[tuple(reversed(range(n))),tuple(range(n,n*2))]
 f += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,v,f,m)
def beam(name,a,b,w,d,m):
 a,b=Vector(a),Vector(b);delta=b-a
 q=delta.to_track_quat('Z','Y')
 v=[tuple(a+q@Vector((x*w/2,y*d/2,t*delta.length)))
    for t in (0,1) for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]]
 f=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
 return mesh(name,v,f,m)
def ribbon(name,rings,m):
 # Each cross section follows a different inhabited fault terrace, not a box.
 count=6;v=[]
 for x,y,z,w,d,skew in rings:
  v.extend([(x-w*.52,y-d*.45,z-10),(x+w*.49,y-d*.54,z-8),
            (x+w*.67,y+d*.12,z+skew),(x+w*.22,y+d*.57,z+5),
            (x-w*.48,y+d*.38,z-9),(x-w*.76,y-d*.08,z+skew*.7)])
 f=[tuple(reversed(range(count))),
    tuple(range((len(rings)-1)*count,len(rings)*count))]
 for j in range(len(rings)-1):
  for i in range(count):
   a=j*count+i;b=j*count+(i+1)%count
   f.append((a,b,b+count,a+count))
 return mesh(name,v,f,m)
def pathdeck(name,pts,w,d,m):
 v=[]
 for i,(x,y,z) in enumerate(pts):
  dv=Vector(pts[min(i+1,len(pts)-1)])-Vector(pts[max(0,i-1)])
  ln=math.hypot(dv.x,dv.y);px,py=(-dv.y/ln,dv.x/ln) if ln>1e-6 else (1,0)
  for zz in (z-d,z):
   v.extend(((x-px*w/2,y-py*w/2,zz),(x+px*w/2,y+py*w/2,zz)))
 f=[]
 for i in range(len(pts)-1):
  a=i*4;b=(i+1)*4
  f.extend(((a,a+1,b+1,b),(a+2,b+2,b+3,a+3),
            (a,a+2,b+2,b),(a+1,b+1,b+3,a+3)))
 f.extend(((0,2,3,1),(len(v)-4,len(v)-2,len(v)-1,len(v)-3)))
 return mesh(name,v,f,m)
def cut(ob,name,center,dims,rotate):
 bpy.ops.mesh.primitive_cube_add(size=1,location=center)
 c=bpy.context.object;c.name='_R3_TEMP_'+name
 c.scale=dims;c.rotation_euler=(rotate*.21,rotate*.13,rotate)
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 mod=ob.modifiers.new(name,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=c
 bpy.context.view_layer.objects.active=ob
 bpy.ops.object.modifier_apply(modifier=mod.name)
 bpy.data.objects.remove(c,do_unlink=True)
 return len(ob.data.polygons)
# WEST: a single unmistakable diagonal inhabited urban fault spine.
# Unlike R1/R2, these are substantial load-bearing carved bodies around the
# true NAVE public interior; the huge central chasm stays empty.
west=ribbon('WEST_FRACTURED_INHABITED_SPINE',[
 (-825,-250,87,167,181,12),(-766,-145,291,187,164,-22),
 (-649,20,534,187,203,35),(-510,167,809,168,214,-48),
 (-340,319,1115,171,183,37),(-238,433,1378,139,151,28)],'white')
cut_report=[]
cut_report.append(('WEST_LIBRARY_PUBLIC_HALL',
  cut(west,'WEST_LIBRARY_PUBLIC_HALL',(-759,-146,284),(162,185,144),.13)))
cut_report.append(('WEST_FAULT_CIVIC_WINDOW',
  cut(west,'WEST_FAULT_CIVIC_WINDOW',(-650,22,556),(146,166,165),-.17)))
cut_report.append(('WEST_RIFT_SKY_FORUM',
  cut(west,'WEST_RIFT_SKY_FORUM',(-496,165,825),(150,160,165),.31)))
# WEST second prong leans away from the void, separated by daylight.
west2=ribbon('WEST_SHORE_CIVIC_BUTTRESS',[
 (-1090,-265,98,161,218,-5),(-1022,-171,306,147,194,21),
 (-891,-65,586,152,183,-25),(-728,103,903,132,162,30)],'dark')
cut_report.append(('WEST_SHORE_TRANSIT_ATRIUM',
 cut(west2,'WEST_SHORE_TRANSIT_ATRIUM',(-1014,-168,337),(102,141,138),-.24)))
# EAST is displaced in both position and height, becoming an actual city ramp
# and an inhabited vertical shoreline, not a twin skyscraper.
east=ribbon('EAST_DISLOCATED_CIVIC_CLIFF',[
 (345,-75,67,180,178,25),(433,33,268,215,209,-35),
 (525,190,469,243,216,51),(671,298,721,226,221,-19),
 (819,437,982,157,159,44)],'ivory')
cut_report.append(('EAST_SEA_STATION_CONCOURSE',
 cut(east,'EAST_SEA_STATION_CONCOURSE',(425,31,276),(165,168,148),.13)))
cut_report.append(('EAST_HIGH_CIVIC_SCHOOL',
 cut(east,'EAST_HIGH_CIVIC_SCHOOL',(648,288,726),(179,176,165),-.20)))
# Exposed public routes meet the openings rather than being pinned outside.
for i,pts in enumerate([
 [(-809,-156,287),(-739,-111,291),(-680,-46,343),(-583,27,442)],
 [(-663,27,546),(-560,101,607),(-488,189,725)],
 [(-507,175,832),(-436,253,919),(-310,333,1084)],
 [(384,-64,267),(445,12,284),(501,99,348),(562,181,446)],
 [(595,247,722),(680,285,729),(749,353,821)]]):
 pathdeck('FAULT_INNER_INHABITED_PUBLIC_STREET_'+str(i),pts,21+i%2*6,8,
          'ivory' if i%2 else 'street')
# Diagonal high linkage spans an ACTUAL city-wide void, leaving its air volume.
pathdeck('DIAGONAL_UPPER_CIVIC_SPINE',
 [(-322,345,1080),(-127,385,1037),(103,425,984),(342,435,926),
  (631,415,887)],52,22,'bronze')
# Internally supported elevated platforms attach to spines in their carved
# public windows: one level per civic purpose, not repetitious horizontal stripes.
for j,(x,y,z,w,d) in enumerate([
 (-742,-132,272,126,100),(-612,29,540,147,130),
 (-469,163,808,123,114),(446,42,267,156,118),(639,285,722,145,120)]):
 p=[(x-w*.54,y-d*.52),(x+w*.46,y-d*.65),
    (x+w*.62,y+d*.25),(x-w*.37,y+d*.57)]
 slab('TECTONIC_INSIDE_ROOM_FLOOR_'+str(j),p,z,12,'ivory')
 for k in (0,2):
  xx,yy=p[k]
  beam('TECTONIC_INHABITED_PIER_%d_%d'%(j,k),
       (xx,yy,z),(xx+9,yy+12,z+62+j%3*12),8,14,'dark')
# H1: deepen existing schools into independent inhabited wings with public
# courtyard, parallel housing routes and real accessible vertical layers.
for j,(x,y,z,w,d,h) in enumerate([
 (545,527,446,132,144,145),(907,513,450,132,149,152),
 (561,697,456,154,135,142),(916,698,459,145,123,168)]):
 poly=[(x-w*.58,y-d*.48),(x+w*.44,y-d*.56),
       (x+w*.66,y+d*.32),(x+w*.15,y+d*.62),(x-w*.48,y+d*.24)]
 slab('H1_THICK_URBAN_CLASSROOM_LOW_'+str(j),poly,z,19,'ivory')
 slab('H1_PUBLIC_INTERIOR_HIGH_'+str(j),
      [(xx+8,yy+11) for xx,yy in poly],z+h*.45,13,'street')
 # Three solid external wall planes are interrupted by a double-height atrium.
 for k in (0,2,4):
  a=poly[k];b=poly[(k+1)%5]
  beam('H1_URBAN_DIVIDING_PIER_%d_%d'%(j,k),
       (a[0],a[1],z-7),(a[0]+7,a[1]+10,z+h),8,12,'dark')
 slab('H1_DOUBLE_HEIGHT_FOLDED_ROOF_'+str(j),
      [(xx+8+12*((k+j)%2),yy+17) for k,(xx,yy) in enumerate(poly)],
      z+h+5,17,'roof')
# H1’s central human view retains a broad, genuine street and daylight.
for j,pts in enumerate([
 [(677,516,445),(711,570,454),(734,666,461),(752,767,468)],
 [(853,515,448),(839,568,455),(825,655,462),(805,763,465)]]):
 pathdeck('H1_INHABITED_SIDE_PEDESTRIAN_STREET_'+str(j),pts,15,7,'street')
# W0 grounding: ferry, sheltered arcades and tiered cliff-linked waterfront.
for j,(z,p) in enumerate([
 (58,[(180,-636),(347,-562),(520,-429),(598,-325),
      (509,-278),(329,-431),(174,-530)]),
 (112,[(230,-578),(389,-458),(556,-298),(599,-139),
       (471,-182),(344,-370),(239,-479)])]):
 slab('W0_WATERFRONT_HABITABLE_CITY_LEVEL_'+str(j),p,z,29,'ivory')
 for k in (0,2,4):
  x,y=p[k]
  beam('W0_PORT_STONE_ARCADE_%d_%d'%(j,k),(x,y,z-26),
       (x+12,y+12,z+93),11,21,'dark')
for j,pts in enumerate([
 [(245,-631,61),(351,-553,62),(475,-449,66),(568,-346,112)],
 [(575,-311,116),(616,-202,175),(681,-32,241),(758,209,437)]]):
 pathdeck('W0_HARBOR_UPLAND_INHABITED_ROUTE_'+str(j),pts,25,9,'street')
# Safety & independent provenance. Camera matrix never changes.
bpy.context.view_layer.update()
for n in views:
 actual=bpy.data.objects[n].matrix_world
 assert max(abs(actual[i][j]-cameras[n][i][j]) for i in range(4) for j in range(4))<1e-6
S['R3_PROGRAM']='NAVE_STATION_LIBRARY_PUBLIC_CIVIC_FAULT_H1_HOUSING_SCHOOL_W0_PORT'
S['R3_SOURCE_SHA256']=SOURCE_SHA
S['R3_RESEARCH_METRES_NOT_WORLD_REGISTERED']=True
S['R3_CARVED_INTERIOR_ROOMS']=len(cut_report)
S['CONSTRUCTION']='HOLD';S['FORMAL_ART_ACCEPTED']=0;S['COMPLETED_TARGETS']=0
S.render.engine='CYCLES';S.cycles.device='CPU';S.cycles.samples=12;S.cycles.use_denoising=True
S.render.threads_mode='FIXED';S.render.threads=2
S.render.resolution_x=1100;S.render.resolution_y=825;S.render.resolution_percentage=100
S.render.image_settings.file_format='PNG';S.render.film_transparent=False
dest=out/'LCS2_R3_INHABITED_FAULT_CITY_WORKING.blend'
S.camera=bpy.data.objects[views[-1]]
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
shots={}
for n in views:
 S.camera=bpy.data.objects[n]
 png=out/'renders'/(n+'.png');S.render.filepath=str(png)
 bpy.ops.render.render(write_still=True)
 assert png.exists() and png.stat().st_size>5000
 shots[n]=hashlib.sha256(png.read_bytes()).hexdigest()
 print('R3_TRUE_BLENDER_RENDER',n,flush=True)
S.camera=bpy.data.objects[views[-1]]
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
info={'schema':'halo9-lcs2-r3-v1','source_sha256':SOURCE_SHA,
 'output_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
 'removed_rejected':len(removed),'authored_meshes':len(C.objects),
 'carved_public_voids':cut_report,'image_sha256':shots,
 'cameras_unchanged':True,'art':'UNREVIEWED_NOT_ADOPTED',
 'formal_art':0,'targets_complete':0,'minecraft':'HOLD'}
(out/'R3_AUTHOR_REPORT.json').write_text(json.dumps(info,indent=2))
print('R3_NATIVE_REAL_COMPLETE',info['output_sha256'],flush=True)
