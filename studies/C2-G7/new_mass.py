"""One new low-detail mass only. Load G6 background read-only; replace central in memory.
No housing multiplication, no interior campaign, exactly three 960x720 JPEGs.
"""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;S=R.parent/'C2-G6'
bpy.ops.wm.open_mainfile(filepath=str(S/'A.blend'))
sc=bpy.context.scene
for o in list(sc.objects):
 if o.type=='MESH' and o.get('role')!='context':bpy.data.objects.remove(o,do_unlink=True)
for o in list(sc.objects):
 if o.type=='LIGHT' and o.data.type!='SUN':bpy.data.objects.remove(o,do_unlink=True)
def mat(name,c):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*c,1);m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.78;return m
M={n:mat(n,c) for n,c in {'body':(.67,.71,.69),'floor':(.53,.41,.25),'life':(.37,.48,.47),'garden':(.25,.37,.28)}.items()}
objects=[]
def mesh(name,v,f,material='body'):
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update();bm=bmesh.new();bm.from_mesh(me)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 o=bpy.data.objects.new(name,me);sc.collection.objects.link(o);o.data.materials.append(M[material]);o['role']='G7_NEW_CENTRAL';objects.append(o);return o
def profile(name,points,y0,y1,shear=.0,material='body'):
 v=[(x+shear*y,y,z) for y in [y0,y1] for x,z in points];n=len(points)
 faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,v,faces,material)
def box(name,x0,x1,y0,y1,z0,z1,material='floor'):
 return profile(name,[(x0,z0),(x1,z0),(x1,z1),(x0,z1)],y0,y1,material=material)
def boolean(body,cutter,op):
 bpy.context.view_layer.update();bpy.context.view_layer.objects.active=body
 m=body.modifiers.new(op,'BOOLEAN');m.operation=op;m.solver='MANIFOLD';m.object=cutter;bpy.ops.object.modifier_apply(modifier=m.name)
 objects.remove(cutter);bpy.data.objects.remove(cutter,do_unlink=True)
# Three room-bearing bodies join along inhabited thickness, not three radial roofs.
lower=profile('LOWER_COLLECTIVE_CITY',[(-1800,-50),(1350,-50),(1750,420),(750,930),(-900,850),(-1850,260)],-1000,600,shear=.16)
middle=profile('DUAL_PUBLIC_CITY',[(-1050,520),(1050,550),(1450,1530),(300,2110),(-1420,1580)],-500,950,shear=-.30)
# Upper independent city is broad and deep, with real open courts, not roof ornaments.
upper=profile('HIGH_COURTYARD_CITY',[(-1350,1480),(550,1570),(1250,2100),(700,2510),(-950,2460),(-1570,1900)],400,1750,shear=.33)
boolean(lower,middle,'UNION');boolean(lower,upper,'UNION');body=lower;body.name='N1_INTERLOCKED_PUBLIC_CITY_MASS'
# Ground arrival: long horizontal space, open through two city edges.
c=profile('COLLECTIVE_ROOM',[(-1050,-100),(450,-100),(820,420),(-700,580)],-1500,1800,shear=.12);boolean(body,c,'DIFFERENCE')
# Twin public rooms differ in section and direction. They generate two unequal facades.
c=profile('TALL_EXCHANGE_ROOM',[(-850,920),(-170,800),(120,1390),(-530,1690)],-1400,1850,shear=-.30);boolean(body,c,'DIFFERENCE')
c=profile('BROAD_CULTURAL_ROOM',[(430,970),(1160,1080),(1260,1470),(580,1690)],-1400,1850,shear=.20);boolean(body,c,'DIFFERENCE')
# Open-ended diagonal terrace cuts the high city toward the skyline.
c=box('HIGH_CITY_OPEN_LOGGIA',-1750,1600,1250,2200,1850,2070);boolean(body,c,'DIFFERENCE')
# Three genuine courtyards through the upper occupied body, different depths.
for i,(x0,x1,y0,y1) in enumerate([(-850,-350,660,1140),(40,510,730,1210),(-400,70,1320,1650)]):
 c=box('COURTYARD_'+str(i),x0,x1,y0,y1,2080,2900);boolean(body,c,'DIFFERENCE')
for p in body.data.polygons:p.use_smooth=False
# Public floors correspond to room thresholds; only a few diagram-scale decks.
box('GROUND_ARRIVAL_PUBLIC_SPACE',-1050,450,-1900,400,-12,0)
profile('LOWER_ROOM_PUBLIC_FLOOR',[(-1010,0),(430,0),(430,12),(-1010,12)],-800,700,shear=.12,material='floor')
profile('TALL_ROOM_THRESHOLD',[(-745,950),(-205,850),(-205,862),(-745,962)],-520,1000,shear=-.30,material='floor')
profile('CULTURE_ROOM_THRESHOLD',[(480,1010),(1140,1110),(1140,1122),(480,1022)],-510,1100,shear=.20,material='floor')
box('HIGH_CITY_PUBLIC_STREET',-1200,950,1260,1450,1851,1863,'life')
# Occupied-band/frontage markers, not individual homes or populations.
box('HIGH_CULTURE_BAND',-1000,650,420,570,2150,2310,'life')
box('HIGH_PUBLIC_GARDEN',-700,-420,750,1020,2081,2087,'garden')
box('UPPER_COURT_PUBLIC_FLOOR',80,470,770,1160,2081,2087,'floor')
box('SHARED_ARRIVAL_STREET',-240,120,-2100,-800,2,12,'floor')
body['design_role']='Room-shaped mass: collective / tall exchange / broad culture / upper inhabited courts'
bpy.context.view_layer.update()
pts=[o.matrix_world@Vector(p) for o in objects for p in o.bound_box]
mn=[min(p[i] for p in pts) for i in range(3)];mx=[max(p[i] for p in pts) for i in range(3)]
specs=json.loads((S/'A_metrics.json').read_text())['cameras']
sc.render.resolution_x=960;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.cycles.samples=14
sc.render.image_settings.file_format='JPEG';sc.render.image_settings.quality=86
# No resave/export of the G6 model; only the newly created central objects leave this scene.
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(R/'N1_CENTRAL.glb'),export_format='GLB',use_selection=True,export_extras=True)
for label,key in [('oblique','05_oblique'),('side','07_side'),('back','08_back')]:
 s=specs[key];cam=sc.camera;cam.location=s['eye'];cam.rotation_euler=(Vector(s['target'])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=s['ortho']
 sc.render.filepath=str(R/('new_'+label+'.jpg'));bpy.ops.render.render(write_still=True);print('NEW_DONE',label,flush=True)
(R/'new_metrics.json').write_text(json.dumps({'study_id':'C2-G7','scheme':'N1 交室都宮','stage':'BLOCKOUT_3D','dimensions_m':[mx[i]-mn[i] for i in range(3)],'bbox_min_m':mn,'bbox_max_m':mx,'new_objects':len(objects),'mass_polygons':len(body.data.polygons),'context_from':'studies/C2-G6/A.blend','context_formal_positions':False,'views':{k:specs[k] for k in ['05_oblique','07_side','08_back']},'render':{'pixels':[960,720],'samples':14,'format':'JPEG'},'interior_rendered':False,'housing_multiplied':False,'structural_and_circulation_certified':False},indent=2),encoding='utf-8')
print('NEW_ONE_SCHEME_COMPLETE',flush=True)
