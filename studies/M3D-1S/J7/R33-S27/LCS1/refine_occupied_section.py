"""LCS1-R1: same verified native BLEND revised in-place on an ISOLATED copy.
Fix invalid H1 camera by moving physical street floor; build massive occupied
undercroft / section-support rooms and diagonal civic galleries without a box.
ART remains unadopted, 0/30, world HOLD.
"""
import bpy,math,json,sys,hashlib
from mathutils import Vector
from pathlib import Path
a=sys.argv[sys.argv.index('--')+1:]
out=Path(a[a.index('--output')+1]);out.mkdir(parents=True,exist_ok=True);(out/'renders').mkdir(exist_ok=True)
src=Path(bpy.data.filepath)
assert src.name=='LCS1_R1_SOURCE.blend'
assert hashlib.sha256(src.read_bytes()).hexdigest()=='db7476b9e0661966fd1fb15437ec1c3cab2452099208ef3020cc742aba9e5599'
S=bpy.context.scene
assert S['CONSTRUCTION']=='HOLD' and S['COMPLETED_TARGETS']==0 and S['FORMAL_ART_ACCEPTED']==0
cam={n:bpy.data.objects[n].matrix_world.copy() for n in ['E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL']}
# CAMERA IS INSIDE TOP FACE at z439, while lens centre z438.7. MOVE THE FLOOR, NOT THE CAMERA.
street=bpy.data.objects['LCS1_h1_public_street']
moved=0
for v in street.data.vertices:
    if abs(v.co.y-270)<.02:
        v.co.y=318; moved+=1
assert moved==4,moved
street.data.update()
C=bpy.data.collections.new('LCS1_R1_ACTUAL_OCCUPIED_RECOMPOSITION_UNAPPROVED');S.collection.children.link(C)
M={k:(bpy.data.materials.get(v) or bpy.data.materials.new(v)) for k,v in {'chalk': 'LCS1_chalk_formed_civic_concrete', 'bone': 'LCS1_warm_public_limestone', 'slate': 'LCS1_rift_shadow_basalt', 'steel': 'LCS1_aged_champagne_titanium', 'copper': 'LCS1_patinated_copper', 'glass': 'LCS1_deep_teal_reflecting_glass', 'water': 'LCS1_tidal_pools', 'light': 'LCS1_inhabited_warm_light', 'way': 'LCS1_wayfinding_glow', 'green': 'LCS1_gardens', 'street': 'LCS1_warm_paving', 'roof': 'LCS1_titanium_roof'} .items()}
def mesh(n,vs,fs,mat):
 d=bpy.data.meshes.new('R1_'+n);d.from_pydata(vs,[],fs);d.update();o=bpy.data.objects.new('R1_'+n,d);C.objects.link(o);d.materials.append(M[mat]);return o
def slab(n,poly,z,d,mat):
 m=len(poly);v=[(x,y,z-d) for x,y in poly]+[(x,y,z) for x,y in poly]
 f=[tuple(range(m-1,-1,-1)),tuple(range(m,m*2))]+[(j,(j+1)%m,(j+1)%m+m,j+m) for j in range(m)]
 return mesh(n,v,f,mat)
def beam(n,aa,bb,w,h,mat):
 a,b=Vector(aa),Vector(bb);d=b-a;q=d.to_track_quat('Z','Y');v=[]
 for t in (0,1):
  for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]:v.append(tuple(a+q@Vector((x*w/2,y*h/2,t*d.length))))
 return mesh(n,v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat)
def path(n,pts,w,h,mat):
 v=[]
 for i,(x,y,z) in enumerate(pts):
  d=Vector(pts[min(i+1,len(pts)-1)])-Vector(pts[max(0,i-1)]);L=math.hypot(d.x,d.y)
  nx,ny=(-d.y/L,d.x/L) if L>.1 else (1,0)
  for delta in (0,h):
   v.extend([(x+nx*w/2,y+ny*w/2,z-delta),(x-nx*w/2,y-ny*w/2,z-delta)])
 fs=[]
 for i in range(len(pts)-1):
  a=4*i;b=4*(i+1);fs.extend([(a,a+1,b+1,b),(a+2,b+2,b+3,a+3),(a,b,b+2,a+2),(a+1,a+3,b+3,b+1)])
 fs.extend([(0,2,3,1),(len(v)-4,len(v)-3,len(v)-1,len(v)-2)])
 return mesh(n,v,fs,mat)
# Actual inhabited H1 support: valley-access arcade, civic gym, transit, shaded garden.
# Three UNIQUE public levels around a deep void; never one continuous closed cube.
levels=[
 ('tidal_transit',[(468,47),(588,35),(745,74),(822,165),(755,259),(632,251),(512,148)],116,13),
 ('undercroft_library',[(479,143),(602,121),(748,180),(828,286),(784,357),(655,342),(538,264)],223,16),
 ('garden_hall',[(515,215),(616,194),(810,274),(890,398),(813,445),(688,434),(568,341)],338,14)]
for i,(label,poly,z,thickness) in enumerate(levels):
 slab('h1_'+label+'_occupied_ground',poly,z,thickness,'street' if i==0 else 'bone')
 for j in (0,2,4,6):
  x,y=poly[j];up=levels[i+1][2] if i<2 else 436
  beam('h1_'+label+'_branched_buttress_'+str(j),(x,y,z-6),
       (x+(j-3)*9,y+(j-4)*15,up),9+i*2,12+i*2,'slate' if j%4==0 else 'steel')
 # Open side galleried wings, roof only over one side so the natural sun enters.
 slab('h1_'+label+'_civic_mezzanine',poly[:4]+[poly[-1]],z+36,6,'chalk')
 slab('h1_'+label+'_canopy',[(x+2,y-5) for x,y in poly[:3]]+
      [(poly[3][0]-20,poly[3][1]+19),(poly[0][0]-30,poly[0][1]+24)],z+78,5,'roof')
for p,q in [((522,160,120),(566,266,221)),((622,232,223),(671,315,338)),
            ((741,340,338),(779,364,438))]:
 beam('h1_visible_vertical_urban_escalator_'+str(int(p[2])),p,q,14,7,'copper')
# Main NAVE diagonal fractured *inhabited* structural ascent: terraces and the hollow between.
west_rooms=[
 ('water_library',[(-543,-214),(-411,-242),(-300,-125),(-348,33),(-500,51)],190),
 ('hewn_assembly',[(-488,2),(-349,-30),(-244,132),(-342,260),(-500,201)],368),
 ('sky_research',[(-392,236),(-216,194),(-127,385),(-276,487),(-442,427)],564)]
for i,(label,poly,z) in enumerate(west_rooms):
 slab('nave_'+label+'_deep_public_floor',poly,z,19,'bone')
 slab('nave_'+label+'_open_lobby_mezzanine',poly[:3]+[poly[-1]],z+57,6,'street')
 x0,y0=poly[0];x1,y1=poly[2]
 for j,(x,y) in enumerate([poly[0],poly[2],poly[-1]]):
  beam('nave_'+label+'_arched_city_column_'+str(j),(x,y,z-8),
   (x+(i-1)*30,y+(j-1)*20,z+136),9,13,'steel')
 slab('nave_'+label+'_slit_roof',[(x-12,y-12) for x,y in poly[:3]]+
     [(poly[2][0]-65,poly[2][1]+45),(poly[0][0]-50,poly[0][1]+55)],z+142,5,'roof')
 path('nave_'+label+'_human_facing_civic_gallery',[(x0+14,y0+14,z+19),
    ((x0+x1)/2,(y0+y1)/2,z+42),(x1-10,y1+10,z+57)],18,5,'chalk')
# Two non-concentric mass-bearing diagonal branches frame a real open urban fissure.
for i,(a,b,w) in enumerate([
 ((-525,-244,74),(-408,290,723),49),
 ((-338,-341,80),(-191,461,867),37),
 ((379,-95,94),(641,467,828),44),
 ((885,-134,55),(995,482,651),28)]):
 beam('rift_big_spatial_buttress_'+str(i),a,b,w,w*.74,'slate' if i%2==0 else 'chalk')
# Real lateral destinations on the diagonal, not decorative bands on giant facades.
path('ritual_rift_to_h1_civic_crossing',[(-172,406,575),(-32,439,614),
 (172,463,632),(338,491,613),(535,509,532),(696,503,457)],30,8,'bone')
slab('rite_high_hall_terrace',[(-224,410),(-22,418),(133,478),(46,554),(-186,543)],625,11,'chalk')
for j,p in enumerate([(-168,440),(98,482)]):
 beam('rite_open_crown_leaf_'+str(j),(p[0],p[1],619),(p[0]+56,p[1]+60,757),10,15,'steel')
# Water-facing undercroft has occupied spaces and a real accessible descent.
slab('w0_estuary_cliff_gallery',[(383,-382),(509,-381),(609,-300),(639,-137),
 (548,-103),(427,-246)],100,12,'bone')
path('w0_street_into_urban_undercroft',[(510,-217,60),(568,-106,105),
 (601,12,116),(631,105,116),(652,191,223)],18,5,'street')
for i,poly in enumerate([
 [(404,-382),(447,-414),(514,-357),(507,-305)],
 [(503,-301),(541,-321),(593,-250),(575,-192)],
 [(581,-221),(621,-246),(649,-171),(626,-125)]]):
 slab('w0_inhabited_port_public_room_'+str(i),poly,109+i*11,6,'copper')
# Fixed research cameras: no camera swapping, and only physical floor edit repaired image validity.
for name,m in cam.items():
 bpy.context.view_layer.update()
 assert max(abs(bpy.data.objects[name].matrix_world[r][c]-m[r][c]) for r in range(4) for c in range(4))<1e-5
S['LCS1_R1_ART_STATUS']='NOT_ACCEPTED_PENDING_DIRECT_REVIEW'
S['LCS1_R1_H1_STREET_FLOOR_PHYSICAL_VERTICES_MOVED']=moved
S['LCS1_R1_NEW_AUTHOR_MESHES']=len(C.objects)
S['CONSTRUCTION']='HOLD';S['COMPLETED_TARGETS']=0;S['FORMAL_ART_ACCEPTED']=0
S.cycles.samples=12;S.render.resolution_x=1100;S.render.resolution_y=825
S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG'
S.camera=bpy.data.objects['E11_URBAN_AERIAL']
result=out/'LCS1_R1_OCCUPIED_CITY_REVISION.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(result),compress=True)
shots={}
for name in cam:
 S.camera=bpy.data.objects[name];p=out/'renders'/(name+'.png')
 S.render.filepath=str(p);bpy.ops.render.render(write_still=True)
 assert p.stat().st_size>4000
 shots[name]=hashlib.sha256(p.read_bytes()).hexdigest()
 print('LCS1_R1_REAL_RENDER',name,flush=True)
S.camera=bpy.data.objects['E11_URBAN_AERIAL'];bpy.ops.wm.save_as_mainfile(filepath=str(result),compress=True)
report={'schema':'halo9-lcs1-r1-native-revision-v1','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
 'new_blend_sha256':hashlib.sha256(result.read_bytes()).hexdigest(),
 'floor_vertices_corrected':moved,'new_meshes':len(C.objects),'image_sha256':shots,
 'art':'UNREVIEWED_NOT_ADOPTED','adoptions':0,'targets_completed':0,'minecraft':'HOLD'}
(out/'AUTHOR_R1.json').write_text(json.dumps(report,indent=2))
print('LCS1_R1_NATIVE_COMPLETE',json.dumps(report),flush=True)
