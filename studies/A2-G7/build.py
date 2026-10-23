"""A2-G7 / original public-confluence massing. Blender 5.2; metres.
Run: blender -b --factory-startup --python build.py
No imported G6 mesh. All final views use one reimported GLB.
The macro mass is a schematic civic envelope, NOT fully occupied floors.
"""
import bpy, bmesh, math, json, hashlib, sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
(R/'renders').mkdir(exist_ok=True)

def save(n,v): (R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def mat(n,c):
    m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True
    bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bs.inputs['Base Color'].default_value=(*c,1);bs.inputs['Roughness'].default_value=.78
    return m
def mesh(n,v,f,m):
    d=bpy.data.meshes.new(n);d.from_pydata(v,[],f);d.update()
    bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free()
    o=bpy.data.objects.new(n,d);bpy.context.collection.objects.link(o);d.materials.append(m);return o
def box(n,p,s,m):
    x,y,z=p;a,b,c=[q/2 for q in s]
    v=[(x+dx,y+dy,z+dz) for dz in [-c,c] for dx,dy in [(-a,-b),(a,-b),(a,b),(-a,b)]]
    return mesh(n,v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m)
def cut(o,n,p,s):
    q=box('CUT_'+n,p,s,M['dark']);bpy.context.view_layer.objects.active=o
    mod=o.modifiers.new(n,'BOOLEAN');mod.operation='DIFFERENCE';mod.object=q
    bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(q,do_unlink=True)
def bounds(obs):
    pts=[o.matrix_world@Vector(v) for o in obs for v in o.bound_box]
    return [[min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]]
def crown():
    # Street/atrium contract first: a continuous open ground passage, an asymmetric
    # high civic catchment, and an open-to-sky high street incised into that catchment.
    # A single nonrepeating envelope joins both civic banks around the protected void.
    v=[];N=100
    for i in range(N+1):
        a=math.pi*i/N;s=math.sin(a);c=math.cos(a)
        x=2350*c+170*s*s;z=4100*s+320*math.sin(2*a)
        cy=230*math.sin(2*a)+220*s
        w=480+410*s**1.4+110*math.sin(2*a)
        dep=650+470*s+120*math.sin(2*a)
        # Chamfered eight-corner section gives urban thickness in EVERY view.
        for nr,ny in [(-1,-.72),(-.72,-1),(.70,-1),(1,-.70),(1,.70),(.70,1),(-.72,1),(-1,.72)]:
            v.append((x+nr*w*c,cy+ny*dep,max(0,z+nr*w*s)))
    f=[]
    for i in range(N):
        for k in range(8):f.append((i*8+k,i*8+(k+1)%8,(i+1)*8+(k+1)%8,(i+1)*8+k))
    f += [tuple(reversed(range(8))),tuple(N*8+k for k in range(8))]
    o=mesh('CIVIC_CATCHMENT_ENVELOPE',v,f,M['ivory'])
    # These are genuine subtractions. Without this street, the crown closes across
    # the district: the incised public route changes the external silhouette.
    cut(o,'HIGH_STREET_OPEN_SKY_CLEFT',(-300,-950,4800),(1260,1700,2000))
    cut(o,'LOWER_CIVIC_HALL_AND_UPPER_TERRACE',(-2250,-1000,150),(800,1400,260))
    return o
def court(n,x,y,z,m):
    # Four low-detail wings with an entrance, horizontal floors, an open courtyard.
    w=72;d=90;t=12;h=28
    for suffix,p,s in [('N',(x,y+d/2-t/2,z+h/2),(w,t,h)),('E',(x+w/2-t/2,y,z+h/2),(t,d-t,h)),('W',(x-w/2+t/2,y,z+h/2),(t,d-t,h)),('S1',(x-21,y-d/2+t/2,z+h/2),(30,t,h)),('S2',(x+21,y-d/2+t/2,z+h/2),(30,t,h))]:
        box(n+'_'+suffix,p,s,m)
    box(n+'_COURT',(x,y,z+.3),(w-2*t,d-2*t,.6),M['garden'])
    return {'id':n,'x':x,'y':y,'floor_z_m':z,'footprint_m':[w,d]}
def pair(tag,x,y,z,w=800,d=700):
    upper=z+128
    box(tag+'_LOWER_GROUND',(x,y,z-4),(w+260,d+180,8),M['stone'])
    roof=box(tag+'_SHARED_ROOF_UPPER_GROUND',(x,y,upper-6),(w,d,12),M['street'])
    roof['role']='same object: lower civic roof and upper district ground'
    # Perimeter civic rooms keep a broad passage through the centre.
    for side in [-1,1]:
        box(tag+'_LIBRARY_CLINIC_'+str(side),(x+side*(w/2-60),y,z+44),(100,d*.60,88),M['teal'])
        for yy in [y-d*.38,y+d*.38]:box(tag+'_CIVIC_PIER',(x+side*(w/2-24),yy,z+58),(32,32,116),M['ivory'])
    probes=[]
    for side in [-1,1]:
        for yy in [y-190,y+110]:
            probes.append(court(tag+'_UPPER_'+str(side)+'_'+str(yy),x+side*250,yy,upper,M['homes']))
            probes.append(court(tag+'_LOWER_'+str(side)+'_'+str(yy),x+side*(w/2+70),yy,z,M['homes']))
    # Two geometrically connected but static lifts; no operating transport claim.
    for side in [-1,1]:
        box(tag+'_LIFT_SHAFT',(x+side*365,y-250,z+64),(18,22,128),M['dark'])
        for zz in [z,upper]:box(tag+'_LIFT_THRESHOLD',(x+side*365,y-270,zz-1),(40,42,2),M['gold'])
    # The upper public street is a 60m clear strip on this very roof.
    box(tag+'_UPPER_WALK',(x,y-35,upper+.4),(60,d-30,.8),M['gold'])
    box(tag+'_LOWER_WALK',(x,y-35,z+.4),(60,d+160,.8),M['gold'])
    return {'id':tag,'lower_z_m':z,'upper_z_m':upper,'roof':roof.name,'roof_bounds_m':bounds([roof]),'courts':probes,
      'common_hall_axis_xy':[x,y],'roof_thickness_m':12,'clear_height_m':116,
      'scope':'4 upper and 4 lower courts, schematic clinic/library and two static lifts; no full-city fitout'}
def setup():
    sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
    sc.render.engine='CYCLES';sc.cycles.samples=16;sc.cycles.use_denoising=True
    sc.render.threads_mode='FIXED';sc.render.threads=10
    sc.render.resolution_x=1200;sc.render.resolution_y=1000;sc.render.resolution_percentage=100
    sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='AgX'
    sc.world=bpy.data.worlds.new('Neutral study sky');sc.world.use_nodes=True
    bg=next(n for n in sc.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.45,.54,.65,1);bg.inputs['Strength'].default_value=.65
    bpy.ops.object.light_add(type='SUN');sun=bpy.context.object;sun.rotation_euler=(.45,-.6,-.5);sun.data.energy=2.7;sun.data.angle=.12
    return sc
def camera(n,p,t,span):
    bpy.ops.object.camera_add(location=p);o=bpy.context.object;o.name='CAM_'+n
    o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
    o.data.type='ORTHO';o.data.ortho_scale=span;o.data.clip_start=.2;o.data.clip_end=60000
    return o
CAMS={
 '01_oblique':[(10000,-15000,8500),(0,0,2400),7700],
 '02_side':[(16000,0,3300),(0,0,2400),7700],
 '03_back':[(0,16000,3900),(0,0,2400),7700],
 '04_city':[(12500,-17500,11000),(0,0,1800),14000],
 '05_shared_high':[(1800,-3900,5700),(-300,-600,3870),2300],
 '06_shared_ground':[(-500,-4200,1800),(-2250,-1050,120),2150],
 '07_front':[(0,-18000,2800),(0,0,2400),7700]
}
def context():
    old=set(bpy.context.scene.objects)
    box('CONTEXT_10KM_NOT_W0',(0,0,-52),(10000,10000,100),M['context'])
    # Deliberately unregistered abstract scale districts, not H1-H6.
    for k in range(8):
        a=k*math.tau/8;cx=3900*math.cos(a);cy=3900*math.sin(a)
        for i in range(7):
            for j in range(5):
                h=40+18*((i+j+k)%4)
                box('UNREGISTERED_SCALE_CITY',(cx+(i-3)*105,cy+(j-2)*110,h/2),(70,78,h),M['context_buildings'])
    col=bpy.data.collections.new('CONCEPT_10KM_NOT_CANONICAL');bpy.context.scene.collection.children.link(col)
    for o in set(bpy.context.scene.objects)-old:
        for c in list(o.users_collection):c.objects.unlink(o)
        col.objects.link(o)
    return col
def main():
    global M
    bpy.ops.wm.read_factory_settings(use_empty=True)
    M={k:mat(k,c) for k,c in {'ivory':(.68,.72,.68),'stone':(.31,.39,.38),'street':(.39,.53,.49),'teal':(.15,.30,.32),'homes':(.64,.54,.39),'gold':(.66,.37,.12),'dark':(.065,.12,.14),'garden':(.17,.28,.21),'context':(.10,.16,.20),'context_buildings':(.20,.28,.30)}.items()}
    crown()
    pairs=[pair('GROUND',-2250,-1030,40),pair('HIGH',-300,-500,3800,1000,800)]
    # Ground-to-high transport is a massing reservation embedded at the street mouth.
    box('TRANSIT_RESERVATION_NOT_OPERATIONAL',(-880,-480,1920),(55,70,3760),M['teal'])
    box('GROUND_ROUTE_TO_TRANSIT',(-1565,-1065,38),(1430,60,4),M['stone'])
    box('GROUND_ROUTE_TURN',(-880,-772.5,38),(60,645,4),M['stone'])
    arch=[o for o in bpy.context.scene.objects if o.type=='MESH'];before=bounds(arch)
    bpy.ops.object.select_all(action='DESELECT')
    for o in arch:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(R/'selected.glb'),export_format='GLB',use_selection=True,export_yup=True)
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(R/'selected.glb'))
    arch=[o for o in bpy.context.scene.objects if o.type=='MESH'];after=bounds(arch)
    sc=setup();ctx=context()
    for name,(eye,target,span) in CAMS.items():
        for o in ctx.objects:o.hide_render=name!='04_city'
        sc.camera=camera(name,eye,target,span);sc.render.filepath=str(R/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
    for o in ctx.objects:o.hide_render=False
    sc.camera=bpy.data.objects['CAM_01_oblique']
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(R/'selected.blend'),compress=True)
    save('geometry.json',{'study':'A2-G7','units':'m','base_head':'156ccccdf0965df64109d43bc62282ab7b818d5e','model':'I / 合流天窟',
      'bounds_m':after,'dimensions_m':dict(zip(['width','depth','height'],[after[1][i]-after[0][i] for i in range(3)])),
      'roundtrip_bounds_delta_m':max(abs(before[j][i]-after[j][i]) for j in range(2) for i in range(3)),
      'pairs':pairs,'cameras':CAMS,'render_source':'one reimported selected.glb; context only in 04_city',
      'new_envelope':True,'g6_mesh_reused':False,'macro_envelope_is_full_floor_city':False,
      'public_incisions':[{'name':'HIGH_STREET_OPEN_SKY_CLEFT','center_m':[-300,-950,4800],'size_m':[1260,1700,2000]},
       {'name':'LOWER_CIVIC_HALL_AND_UPPER_TERRACE','center_m':[-2250,-1000,150],'size_m':[800,1400,260]}],
      'formal_art_adoption':False,'minecraft':'HOLD','work_transfer':False})
def section_views():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(R/'selected.glb'))
    # A diagnostic crop of the exact model, not a separately designed section.
    for o in list(bpy.context.scene.objects):
        if o.type!='MESH':continue
        if not o.name.startswith('HIGH_'):
            bpy.data.objects.remove(o,do_unlink=True);continue
        bm=bmesh.new();bm.from_mesh(o.data)
        bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.001,
          plane_co=(0,-500,0),plane_no=(0,1,0),clear_inner=True,clear_outer=False)
        bm.to_mesh(o.data);bm.free()
    sc=setup();sc.camera=camera('08_section',(1000,-3300,4620),(-300,-330,3860),1700)
    sc.render.filepath=str(R/'renders'/'08_section.png');bpy.ops.render.render(write_still=True)
    save('section.json',{'source':'selected.glb','keep':'HIGH_ objects only, y >= -500m','plane_y_m':-500,
      'cut_faces_capped':False,'envelope_hidden':True,'diagnostic_only':True,
      'camera':{'eye':[1000,-3300,4620],'target':[-300,-330,3860],'ortho_span_m':1700},
      'limits':'Local shared section only; removed front court and macro envelope explicitly hidden. Not a full building cutaway.'})
if __name__=='__main__':
    if 'section' in sys.argv:section_views()
    else:main()
