"""Reopen final native model, add real interior cameras, floor ray and scale scene.
Architectural render pixels remain untouched. Context is explicitly noncanonical.
"""
import sys,bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import atelier as a
R=a.ROOT;folder=R/'revision_2';final=folder/'R17_REVISION_2.blend'
bpy.ops.wm.open_mainfile(filepath=str(final));a.S=bpy.context.scene;a.ARCH=bpy.data.collections['R17_URBAN_CONTINENTS'];a.ENV=bpy.data.collections['STUDIO_NONCANONICAL']
for attr,name in [('P','Porcelain titanium'),('D','Midnight occupied substructure'),('B','Pale champagne edges'),('F','Warm civic mineral'),('W','Quiet jade water')]:setattr(a,attr,bpy.data.materials[name])
def pose(name,loc,target,lens=23):
 o=bpy.data.objects.get(name)
 if o is None:
  data=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,data);a.ENV.objects.link(o)
 o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.type='PERSP';o.data.lens=lens;o.data.clip_start=.1;o.data.clip_end=100000
 return o
pose('08_INTERIOR_LOW',(-600,-850,550),(-1450,900,1550),20)
pose('09_INTERIOR_MID',(-500,1050,1480),(-1500,700,2250),22)
pose('10_INTERIOR_HIGH',(-400,-100,3200),(300,1700,3250),23)
pose('11_DISTRICT',(-2700,-1500,1050),(-1700,-200,600),30)
selection=R/'qa/SELECTED_INTERIOR_CAMERAS.json'
if selection.exists():
 for name,params in json.loads(selection.read_text('utf8')).items():pose(name,params['location'],params['target'],params['lens_mm'])
S=a.S;dg=bpy.context.evaluated_depsgraph_get()
origin=Vector((-1710,-520,420));hit,loc,normal,index,ob,matrix=S.ray_cast(dg,origin,Vector((0,0,-1)),distance=60)
floor={'hit':hit}
if hit:
 eye=loc+Vector((0,0,1.7));c=pose('13_HUMAN_ESTUARY',eye,(200,700,loc.z+350),22)
 bpy.context.view_layer.update()
 h2,l2,n2,i2,o2,m2=S.ray_cast(dg,c.location,Vector((0,0,-1)),distance=5)
 floor.update(camera_xyz_m=list(c.location),floor_xyz_m=list(l2),object=o2.name if h2 else None,normal=list(n2),distance_m=(c.location-l2).length if h2 else None,pass_1_7m_2mm=h2 and abs((c.location-l2).length-1.7)<.002 and n2.z>.9)
poses={n:{'xyz_m':list(bpy.data.objects[n].location),'rotation_euler_rad':list(bpy.data.objects[n].rotation_euler),'lens_mm':bpy.data.objects[n].data.lens} for n in ['08_INTERIOR_LOW','09_INTERIOR_MID','10_INTERIOR_HIGH','11_DISTRICT','13_HUMAN_ESTUARY'] if bpy.data.objects.get(n)}
# Six directional surface samples. These are explicitly NOT a volume or clearance certificate.
probes={}
for name in ['08_INTERIOR_LOW','09_INTERIOR_MID','10_INTERIOR_HIGH']:
 eye=bpy.data.objects[name].location;result={}
 for label,direction in [('X+',(1,0,0)),('X-',(-1,0,0)),('Y+',(0,1,0)),('Y-',(0,-1,0)),('Z+',(0,0,1)),('Z-',(0,0,-1))]:
  h,p,n,i,o,m=S.ray_cast(dg,eye,Vector(direction),distance=10000)
  result[label]={'hit':h,'distance_m':(p-eye).length if h else None,'surface':o.name if h else None}
 probes[name]=result
S.camera=bpy.data.objects['02_OBLIQUE'];bpy.ops.wm.save_as_mainfile(filepath=str(final),compress=True)
(R/'qa/SPATIAL_INSPECTION.json').write_text(json.dumps(dict(source_blend_sha256=hashlib.sha256(final.read_bytes()).hexdigest(),floor_ray=floor,cameras=poses,six_axis_surface_samples=probes,scope='Single-line surface rays only. No connected void volume, full path, collision, usable habitat or lift operation certified.'),indent=2),encoding='utf8')
a.render(folder,list(poses))
# Approximate 10km scale diagram in actual 3D. No W0/H/SB geometry is loaded.
context=bpy.data.collections.new('NONCANONICAL_10KM_SCALE_ONLY');S.collection.children.link(context)
for x in (-5000,5000):a.box('10km boundary',(x,0,-15),(16,10000,20),a.F,context)
for y in (-5000,5000):a.box('10km boundary',(0,y,-15),(10000,16,20),a.F,context)
# Neutral scale masses only, deliberately not claimed to be an actual city master.
for i,(x,y,w,d,h) in enumerate([(-4000,-3200,650,900,280),(-2200,-3900,900,650,210),(500,-3500,750,800,350),(3000,-3000,700,800,380),(3900,-900,850,650,260),(3900,2000,700,900,450),(2500,3900,1000,650,370),(-500,4100,850,600,320),(-3400,3000,850,950,500),(-4200,500,650,950,350)]):
 a.box('Neutral unregistered scale mass '+str(i),(x,y,h/2),(w,d,h),a.D,context)
context_folder=R/'context';context_folder.mkdir(exist_ok=True);S.camera=bpy.data.objects['12_CITY_10KM']
bpy.ops.wm.save_as_mainfile(filepath=str(context_folder/'R17_NONCANONICAL_10KM.blend'),compress=True)
S.render.filepath=str(context_folder/'12_CITY_10KM.png');bpy.ops.render.render(write_still=True)
(context_folder/'CONTEXT_LIMIT.json').write_text(json.dumps({'span_xy_m':10000,'canonical_alignment':'UNVERIFIED','actual_W0_H_SB_integrated':False,'context_purpose':'Central hierarchy and remaining surrounding space only. Boundary and neutral masses are not city design.'},indent=2),encoding='utf8')
print('SPATIAL REVIEW COMPLETE',floor,flush=True)
