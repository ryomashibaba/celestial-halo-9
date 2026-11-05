"""LCS2/R2: architecture-first NAVE + inhabited fault + H1 + W0.
Actual 3D intervention on a SHA-pinned research BLEND copy, not canonical.
No world coordinates, no Minecraft writes, no art acceptance.
"""
import bpy, math, sys, json, hashlib
from pathlib import Path
from mathutils import Vector

args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=Path(args[args.index('--output')+1]);out.mkdir(parents=True,exist_ok=True)
(out/'renders').mkdir(exist_ok=True)
src=Path(bpy.data.filepath)
assert src.name=='LCS2_R2_SOURCE.blend',src
SOURCE_SHA='da98dfb810502228f9bcd48804d09f0e580308653cafc141ee0cfbb563859b54'
assert hashlib.sha256(src.read_bytes()).hexdigest()==SOURCE_SHA
s=bpy.context.scene
assert s['CONSTRUCTION']=='HOLD' and s['FORMAL_ART_ACCEPTED']==0 and s['COMPLETED_TARGETS']==0
names=['E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL']
fixed={name:bpy.data.objects[name].matrix_world.copy() for name in names}
removed=[]
def remove(prefix):
 for o in tuple(s.objects):
  if o.name.startswith(prefix) and o.type in {'MESH','CURVE'}:
   removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
# Do not extend the former roof and scaffold system. Keep public-use floors and terrain.
for n in ('LCS2_NAVE_PUBLIC_CONCOURSE','LCS2_west_fault_public_inhabited_level_',
          'LCS2_west_fault_recessed_library_gallery_',
          'LCS2_east_displaced_occupied_city_floor_',
          'LCS2_east_displaced_occupied_roof_',
          'LCS2_east_displaced_civic_glazed_gallery_',
          'LCS2_diagonal_fault_departed_civic_roof_',
          'LCS2_central_upper_occupied_crossing',
          'LCS2_deep_fault_branch_'):
 remove(n)
assert 'LCS2_NAVE_PUBLIC_CONCOURSE' in removed, removed
C=bpy.data.collections.new('LCS2_R2_CIVIC_TECTONIC_SECTION_UNAPPROVED')
s.collection.children.link(C)
mats={k:bpy.data.materials.get('LCS2_'+v) for k,v in {
 'ivory':'porous_limestone','pale':'ceramic_public_rooms',
 'night':'deep_rift_stone','bronze':'bronze_tracer','glass':'civic_glass',
 'moss':'roof_gardens','walk':'pedestrian_paving',
 'warm':'inhabited_luminance','way':'public_wayfinding',
 'roof':'matte_titanium'}.items()}
# Blender drops unused material datablocks on save. Reuse available sources,
# reconstruct only absent role materials in their original established palette.
palette={'ivory':(.62,.70,.69),'pale':(.82,.79,.65),'night':(.075,.125,.16),
 'bronze':(.55,.32,.17),'glass':(.055,.28,.34),'moss':(.18,.36,.24),
 'walk':(.40,.48,.46),'warm':(.88,.53,.26),'way':(.34,.75,.79),
 'roof':(.27,.36,.40)}
for role,existing in list(mats.items()):
 if existing:continue
 mat=bpy.data.materials.new('LCS2_R2_restored_'+role)
 mat.diffuse_color=(*palette[role],1);mat.use_nodes=True
 bs=mat.node_tree.nodes.get('Principled BSDF')
 bs.inputs['Base Color'].default_value=(*palette[role],1)
 bs.inputs['Roughness'].default_value=.58
 mats[role]=mat
 print('R2_RESTORED_UNUSED_MATERIAL',role,flush=True)
assert all(mats.values())
def mesh(name,verts,faces,mat):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
 ob=bpy.data.objects.new('R2_'+name,me);C.objects.link(ob);me.materials.append(mats[mat]);return ob
def slab(name,poly,z,depth,mat):
 n=len(poly);assert n>=3
 verts=[(x,y,z-depth) for x,y in poly]+[(x,y,z) for x,y in poly]
 faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
 faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,verts,faces,mat)
def beam(name,a,b,w,d,mat):
 a,b=Vector(a),Vector(b);v=b-a
 assert v.length>2
 q=v.to_track_quat('Z','Y')
 vertices=[tuple(a+q@Vector((x*w/2,y*d/2,t*v.length)))
           for t in (0,1) for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]]
 faces=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
 return mesh(name,vertices,faces,mat)
def linewalk(name,pts,width,depth,mat):
 verts=[]
 for i,p in enumerate(pts):
  x,y,z=p;delta=Vector(pts[min(i+1,len(pts)-1)])-Vector(pts[max(0,i-1)])
  d=math.hypot(delta.x,delta.y);px,py=(-delta.y/d,delta.x/d) if d>0.01 else (1,0)
  for zz in (z-depth,z):
   verts.extend([(x-px*width/2,y-py*width/2,zz),(x+px*width/2,y+py*width/2,zz)])
 faces=[]
 for i in range(len(pts)-1):
  a=4*i;b=4*(i+1)
  faces += [(a,a+1,b+1,b),(a+2,b+2,b+3,a+3),
            (a,a+2,b+2,b),(a+1,b+1,b+3,a+3)]
 faces += [(0,2,3,1),tuple(range(len(verts)-4,len(verts)))]
 return mesh(name,verts,faces,mat)
def tree(name,x,y,z):
 beam(name+'_trunk',(x,y,z),(x+2,y,z+21),2,2,'night')
 slab(name+'_crown',[(x-10,y-7),(x+8,y-9),(x+13,y+4),
                     (x+2,y+11),(x-11,y+4)],z+24,7,'moss')
# NAVE: keep one open clear-air civic atrium at camera location, introduce
# physically separated destinations along its left and right excavated walls.
slab('NAVE_WEST_THICK_LIBRARY_GALLERY',[(-271,-392),(-156,-379),(-150,-260),
 (-195,-105),(-291,-96),(-331,-248)],121,20,'ivory')
slab('NAVE_EAST_SPLIT_STATION_GALLERY',[(164,-405),(318,-375),(341,-240),
 (274,-105),(170,-149),(151,-282)],133,18,'pale')
for side,points in [('W',[(-260,-350,81),(-239,-230,122),(-276,-118,204),
                       (-267,4,290)]),
                    ('E',[(258,-372,80),(271,-238,132),(253,-93,220),
                         (224,71,315)])]:
 for i,(a,b) in enumerate(zip(points,points[1:])):
  beam('NAVE_'+side+'_INHABITED_RAMP_SPAR_'+str(i),a,b,12,10,'ivory')
  linewalk('NAVE_'+side+'_PUBLIC_RAMP_'+str(i),[a,b],17,6,'pale')
# The roof was the obstruction; replace with sparse piers on the SIDES,
# not an overhead slab or giant shell. Clear width remains about 170m.
for i,y in enumerate((-352,-170,40,211)):
 for side,x,sign in (('W',-295,1),('E',294,-1)):
  a=(x,y,95);b=(x+sign*58,y+27,280+27*i)
  beam('NAVE_SKY_CIVIC_FORK_'+side+str(i),a,b,18,27,'night')
# A legible inhabited library building with transparent opening to the forum.
for j,z in enumerate((145,202,267)):
 slab('NAVE_LIBRARY_REAL_OCCUPIED_ROOM_'+str(j),
      [(-409,-330),(-323,-326),(-289,-186),(-363,-132),(-437,-205)],
      z,12,'ivory' if j%2 else 'pale')
for x,y in ((-395,-318),(-310,-298),(-358,-144)):
 beam('NAVE_LIBRARY_ROOM_PIER_'+str(x),(x,y,141),(x+13,y+17,311),9,16,'night')
slab('NAVE_LIBRARY_DUAL_HEIGHT_NORTH_ROOF',
     [(-440,-319),(-358,-354),(-290,-188),(-374,-122),(-460,-198)],
     327,11,'roof')
# East station with distinct platforms and mezzanine instead of repeating piers.
slab('NAVE_STATION_OPEN_TRAIN_HALL',[(211,-343),(363,-351),(397,-217),
  (329,-82),(212,-103)],273,16,'ivory')
for k,(x,y) in enumerate(((215,-352),(364,-325),(358,-134))):
 beam('NAVE_STATION_TRI_BRANCH_'+str(k),(x,y,134),
      (x-22,y+17,278),12,22,'night')
# Ceramic transition platforms at sea-level keep the old NAVE public floor visible.
for i in range(12):
 yy=-460+i*22;xx=-83+i*5
 slab('NAVE_EXCAVATED_RITUAL_STAIR_'+str(i),
      [(xx-37,yy),(xx+44,yy+1),(xx+35,yy+13),(xx-44,yy+15)],
      75+i*3.8,5,'pale')
# An inhabited fault uses asymmetrical thick room strata at wildly different
# elevations; open negative space between opposing city cliffs stays unroofed.
west=[
 ((-740,-235,135),(-340,-280,135),(-210,10,135),(-500,241,135),-2),
 ((-821,-180,386),(-355,-268,386),(-164,71,386),(-485,300,386),-2),
 ((-900,-93,704),(-387,-213,704),(-108,140,704),(-496,384,704),-2),
 ((-1016,41,998),(-444,-110,998),(-41,211,998),(-590,485,998),-2)
]
# These aren't solid envelope masses: three streets and their separated roofs
# are exposed, and side buttresses follow the city room elevations.
for j,profile in enumerate(west):
 pts=[(v[0],v[1]) for v in profile[:4]]
 z=profile[0][2]
 slab('WEST_FAULT_INHABITED_CITY_ROOM_'+str(j),pts,z,32,'pale' if j%2 else 'ivory')
 slab('WEST_FAULT_INHABITED_CITY_ROOF_'+str(j),
      [(x+20+j*5,y+26) for x,y in pts],z+87+13*j,16,'roof')
 for k in (0,2):
  xx,yy=pts[k];beam('WEST_FAULT_DEEP_OCCUPIED_COLUMN_%d_%d'%(j,k),
                    (xx,yy,z),(xx+14,yy+17,z+87+13*j),20,28,'night')
for j in range(3):
 for k in (0,2):
  a=west[j][k];b=west[j+1][k]
  beam('WEST_FAULT_TECTONIC_CROSS_STRUT_%d_%d'%(j,k),a,b,53,78,'ivory')
# East counterpart is a thick stepped inhabited scar, not a second twin tower.
for j,(x,y,z,w,d) in enumerate([(331,78,255,245,214),(428,205,476,300,225),
                               (548,328,721,270,260),(684,431,942,206,205)]):
 poly=[(x-w*.6,y-d*.4),(x+w*.45,y-d*.62),
       (x+w*.67,y+d*.2),(x+w*.14,y+d*.71),(x-w*.47,y+d*.46)]
 slab('EAST_FAULT_INHABITED_QUARTER_'+str(j),poly,z,36,'ivory')
 slab('EAST_FAULT_CIVIC_ROOM_ROOF_'+str(j),
      [(a+17,b+29) for a,b in poly],z+100+j*11,15,'roof')
 for k in (0,3):
  xx,yy=poly[k];beam('EAST_FAULT_HABITABLE_PIER_%d_%d'%(j,k),
        (xx,yy,z-5),(xx+23,yy+29,z+100+j*11),18,28,'night')
 if j>0:
  beam('EAST_FAULT_FRACTURE_SPINE_'+str(j),(x-130,y-75,z-220),
       (x-95,y+42,z+113),42,59,'ivory')
# The diagonal spatial rupture stays empty in the lower NAVE and inhabited up high.
linewalk('CITY_CROSSING_WITH_OPEN_VOID',[(-270,230,724),(-125,270,771),
       (85,330,804),(266,366,789),(414,378,740)],33,15,'bronze')
# H1: actual thick living neighborhoods grow from the three-level undercity,
# with a northern courtyard and publicly open marketplace on the high street.
# Never build over the fixed human-camera origin (760,270,438.7).
for i,(z,poly) in enumerate([
 (196,[(480,320),(631,291),(719,376),(725,648),(553,699),(467,518)]),
 (303,[(476,347),(646,324),(723,401),(726,678),(554,731),(465,544)])]):
 slab('H1_HABITABLE_NORTH_CLIFF_FLOOR_'+str(i),poly,z,23,'pale')
 for k in (0,2,4):
  x,y=poly[k];beam('H1_THICK_NORTH_ARCADE_PIER_%d_%d'%(i,k),
                  (x,y,z-20),(x+12,y+18,z+94),10,17,'night')
 slab('H1_NORTH_CLIFF_INTERIOR_PUBLIC_MEZZANINE_'+str(i),
      [(x+8,y+18) for x,y in poly],z+50,8,'ivory')
# East inhabited promenade is deliberately elevated above the three civic levels,
# with transfer routes linking it to the existing H1 surface and the seawall.
linewalk('H1_CLIFF_TO_MARKET_LIFT_LANDING',[(881,450,358),(921,490,386),
       (928,570,436)],19,8,'bronze')
for i,(x,y) in enumerate(((574,564),(628,685),(870,566),(934,732))):
 slab('H1_MARKET_OPEN_LODGIA_'+str(i),
      [(x-31,y-19),(x+41,y-27),(x+52,y+26),(x-16,y+41)],
      463+i%2*13,11,'pale')
 for j in (0,2):
  px,py=[(x-31,y-19),(x+41,y-27),(x+52,y+26),(x-16,y+41)][j]
  beam('H1_LODGIA_GROUNDED_SUPPORT_%d_%d'%(i,j),
       (px,py,437),(px+6,py+10,473+i%2*13),5,9,'night')
# Water-edge: orient civic descending terraces toward east sea and separated ferry halls.
for i,(z,poly) in enumerate([
 (72,[(135,-706),(349,-632),(508,-482),(555,-363),(369,-408),(188,-571)]),
 (33,[(187,-813),(434,-721),(606,-558),(666,-394),(499,-498),(261,-688)])]):
 slab('W0_INHABITED_TIDAL_CITY_SECTION_'+str(i),poly,z,28,'night' if i==0 else 'ivory')
for j,(a,b) in enumerate([
 ((147,-632,75),(332,-544,78)),((342,-541,74),(493,-370,51)),
 ((477,-380,51),(580,-241,44))]):
 linewalk('W0_QUAY_PUBLIC_TERRACE_'+str(j),[a,b],27,6,'pale')
# Preserve all formal/canonical boundaries.
s['CONSTRUCTION']='HOLD'
s['FORMAL_ART_ACCEPTED']=0
s['COMPLETED_TARGETS']=0
s['R2_STATUS']='REAL_SPATIAL_REVISION_AWAIT_ART_JUDGMENT'
s['R2_SOURCE_SHA256']=SOURCE_SHA
s['R2_REMOVED_REJECTED_OBJECTS']=len(removed)
s['R2_CIVIC_MESHES']=len(C.objects)
s['R2_RESEARCH_COORDINATES']='NOT_MINECRAFT_REGISTERED'
bpy.context.view_layer.update()
for n in names:
 a=bpy.data.objects[n].matrix_world
 assert max(abs(a[i][j]-fixed[n][i][j]) for i in range(4) for j in range(4))<1e-6
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=12;s.cycles.use_denoising=True
s.render.threads_mode='FIXED';s.render.threads=2
s.render.resolution_x=1100;s.render.resolution_y=825;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.film_transparent=False
dest=out/'LCS2_R2_ARCHITECTURAL_SECTION.blend'
s.camera=bpy.data.objects[names[-1]]
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
hashes={}
for n in names:
 s.camera=bpy.data.objects[n];f=out/'renders'/(n+'.png');s.render.filepath=str(f)
 bpy.ops.render.render(write_still=True)
 assert f.exists() and f.stat().st_size>5000
 hashes[n]=hashlib.sha256(f.read_bytes()).hexdigest()
 print('R2_TRUE_RENDER',n,f.stat().st_size,flush=True)
s.camera=bpy.data.objects[names[-1]]
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
info={'schema':'halo9-lcs2-r2-v1','source_sha256':SOURCE_SHA,
      'output_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
      'removed_objects':removed,'new_meshes':len(C.objects),
      'png_sha256':hashes,'cameras_unchanged':True,
      'formal_art':0,'completed_targets':0,'minecraft':'HOLD',
      'art':'AWAIT_DIRECT_IMAGE_REVIEW'}
(out/'AUTHOR_REPORT.json').write_text(json.dumps(info,indent=2))
print('R2_REAL_AUTHOR_COMPLETE',info['output_sha256'],flush=True)
