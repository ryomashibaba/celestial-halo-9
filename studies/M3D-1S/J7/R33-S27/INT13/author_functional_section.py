"""CELESTIAL HALO-9 INT13: a hand-authored, purpose-first civic section.

A genuinely editable 3D spatial study in the existing INT12 master scene:
arrival -> NAVE interchange -> library/ceremony -> H1 school/market/housing.
Unlike prior iterations, the first authored data is a destination/connection
graph and explicit architectural floor elevations, rather than a giant loft,
ellipsoid or cylinder that is given a function afterwards.

Render both the WHOLE unchanged surroundings + ADDITIVE research section
and an explicitly labeled CUTAWAY with rejected old obstructing mass hidden.
Never confuse cutaway visibility with an actual adopted integrated master.
This is headless Blender mesh authoring, NOT GUI hand sculpt, not ART approval.
"""
import bpy,math,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
from math import sin,cos,pi
arg=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
OUT=Path(arg[arg.index('--output')+1]);OUT.mkdir(parents=True,exist_ok=True)
(OUT/'renders').mkdir(exist_ok=True)
SOURCE='563773c54328f249978c0ed6d989edfc437d467a9d543a0b21511f99d6a508a1'
src=Path(bpy.data.filepath)
assert src.name=='INT13_SOURCE.blend'
assert hashlib.sha256(src.read_bytes()).hexdigest()==SOURCE
sc=bpy.context.scene
assert sc['CONSTRUCTION']=='HOLD' and sc['FORMAL_ART_ACCEPTED']==sc['COMPLETED_TARGETS']==0
FIXED=('E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL')
original_cameras={n:bpy.data.objects[n].matrix_world.copy() for n in FIXED}
core_w0=('W0_NORTH_FRACTURED_RANGE','W0_WEST_BASALT_ESCARPMENT','W0_GROUND_BASIN','W0_EASTERN_ARTIFICIAL_SEA')
def vert_hash(ob):
    h=hashlib.sha256()
    for v in ob.data.vertices:h.update((','.join(f'{float(x):.10g}' for x in v.co)+';').encode())
    return h.hexdigest()
w0={n:vert_hash(bpy.data.objects[n]) for n in core_w0}
col=bpy.data.collections.new('INT13_PURPOSE_FIRST_CIVIC_ROOM_H1_STUDY')
sc.collection.children.link(col)
mat={}
def m(name,rgb,metal=0,rough=.66,emission=0):
    v=bpy.data.materials.new('INT13_'+name);v.use_nodes=True
    bs=v.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*rgb,1)
    bs.inputs['Metallic'].default_value=metal
    bs.inputs['Roughness'].default_value=rough
    if emission:
        bs.inputs['Emission Color'].default_value=(*rgb,1)
        bs.inputs['Emission Strength'].default_value=emission
    v.diffuse_color=(*rgb,1)
    mat[name]=v
m('limestone',(.66,.62,.51),.1,.77)
m('dark_sediment',(.15,.23,.25),.17,.8)
m('porcelain',(.8,.77,.66),.12,.48)
m('bronze',(.52,.32,.15),.66,.33)
m('gardens',(.14,.35,.23),0,.83)
m('glass',(.15,.44,.49),.26,.22)
m('mosaic',(.34,.36,.35),.19,.66)
m('light',(.98,.7,.41),.08,.4,1.6)
created=[]
def mesh(name,v,f,material):
    assert len(v)>=4 and len(f)>=4
    data=bpy.data.meshes.new('INT13_'+name)
    data.from_pydata(v,[],f);data.update()
    obj=bpy.data.objects.new('INT13_'+name,data)
    col.objects.link(obj);data.materials.append(mat[material])
    created.append(obj.name)
    return obj
def boundary_solid(name,outline,low,height,material,upper_shift=(0,0)):
    """Designer-authored 5-10 sided building, not a rectangular box."""
    n=len(outline)
    v=[(x,y,low) for x,y in outline]
    v.extend((x+upper_shift[0],y+upper_shift[1],low+height+
              8*sin(2*pi*i/n)) for i,(x,y) in enumerate(outline))
    f=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    for i in range(n):f.append((i,(i+1)%n,(i+1)%n+n,i+n))
    return mesh(name,v,f,material)
def carve_prism(target,name,foot,zmin,zmax):
    n=len(foot);v=[(x,y,zmin) for x,y in foot]
    v +=[(x,y,zmax) for x,y in foot]
    f=[tuple(range(n)),tuple(reversed(range(n,2*n)))]
    for i in range(n):f.append((i,i+n,(i+1)%n+n,(i+1)%n))
    cutter=mesh('TEMP_'+name+'_CAVITY',v,f,'mosaic')
    bpy.ops.object.select_all(action='DESELECT')
    target.select_set(True)
    bpy.context.view_layer.objects.active=target
    original=len(target.data.polygons)
    b=target.modifiers.new('INT13_REAL_VOID_'+name,'BOOLEAN')
    b.operation='DIFFERENCE';b.solver='EXACT';b.object=cutter
    bpy.ops.object.modifier_apply(modifier=b.name)
    bpy.data.objects.remove(cutter,do_unlink=True)
    created.remove(cutter.name)
    target.data.update()
    assert len(target.data.polygons)>original,(name,original,len(target.data.polygons))
    return {'target':target.name,'cavity':name,'polys_before':original,
            'polys_after':len(target.data.polygons)}

# Spatial program is FIRST, before surfaces. Public destinations are not
# just labels added after solid forms: they determine the floor section.
sites={
 'W0_ARRIVAL':(-235,-870,48),
 'NAVE_STATION':(-110,-300,90),
 'NAVE_FORUM':(-68,-40,124),
 'NAVE_LIBRARY':(-240,150,230),
 'NAVE_CEREMONY':(35,325,326),
 'NAVE_ASCENT':(260,390,355),
 'H1_MARKET':(615,410,435),
 'H1_SCHOOL':(840,520,530),
 'H1_COMMONS':(1045,680,630),
 'H1_RESIDENCES':(1200,900,810),
}
edges=[
 ('W0_ARRIVAL','NAVE_STATION','walk'),
 ('NAVE_STATION','NAVE_FORUM','walk'),
 ('NAVE_FORUM','NAVE_LIBRARY','walk'),
 ('NAVE_LIBRARY','NAVE_CEREMONY','walk'),
 ('NAVE_CEREMONY','NAVE_ASCENT','walk'),
 ('NAVE_ASCENT','H1_MARKET','walk'),
 ('H1_MARKET','H1_SCHOOL','walk'),
 ('H1_SCHOOL','H1_COMMONS','walk'),
 ('H1_COMMONS','H1_RESIDENCES','walk'),
]
# Explicit independent 3D connections: center and both edges must share
# same xyz at adjacent endpoints, no decorative disconnected floating pads.
def street(a,b,idx):
    p=Vector(sites[a]);q=Vector(sites[b])
    tangent=q-p
    horizontal=Vector((tangent.x,tangent.y,0))
    assert horizontal.length>30
    normal=Vector((-horizontal.y,horizontal.x,0)).normalized()
    n=8
    v=[]
    # A broad inhabitable rising rock bed, thick in the middle; full side
    # mass is built into the SAME mesh instead of detached shelf planks.
    for j in range(n+1):
        t=j/n
        point=p.lerp(q,t)
        lateral=20*sin(pi*t)*(1 if idx%2 else -1)
        center=point+normal*lateral
        width=64+11*sin(pi*t)+8*sin(2*pi*t+idx)
        for height,dwidth in [(0,1),(-23,1.05),(-60,.34)]:
            for side in (-1,1):
                v.append(tuple(center+normal*side*width*.5*dwidth+
                               Vector((0,0,height))))
    faces=[(0,1,3,2),(6*n,6*n+1,6*n+3,6*n+2)]
    for j in range(n):
        h=6*j;k=6*(j+1)
        for side in range(5):
            faces.append((h+side,k+side,k+side+1,h+side+1))
        faces.append((h+5,k+5,k,k and h or h))
    # remove any degenerate face; actual valid ground is upper band.
    faces=[f for f in faces if len(set(f))>=3]
    obj=mesh('PUBLIC_SPATIAL_ROUTE_%02d_%s_TO_%s'%(idx,a,b),v,faces,
             'limestone' if idx%3 else 'dark_sediment')
    return {'from':a,'to':b,'length_m':round(tangent.length,2),
            'rise_m':round(tangent.z,2),'object':obj.name,
            'start_xyz':list(p),'end_xyz':list(q)}
routes=[street(a,b,i) for i,(a,b,mode) in enumerate(edges)]
# The SECTION, not a decorative canopy. Three distinct civic institutions
# share one continuous public floor but have individually excavated interiors.
nave=boundary_solid('NAVE_THE_SHARED_READING_MOUNTAIN',
 [(-426,-410),(-278,-445),(-182,-395),(-102,-272),
  (-134,80),(-224,218),(-388,158),(-468,-60)],
  36,370,'dark_sediment',(68,38))
nave_cuts=[]
nave_cuts.append(carve_prism(nave,'NAVE_RAIL_ARRIVAL_ATRIUM',
 [(-365,-350),(-212,-365),(-147,-251),(-213,-112),(-350,-121)],
 68,370))
nave_cuts.append(carve_prism(nave,'NAVE_OPEN_LIBRARY_COURT',
 [(-390,-50),(-246,-70),(-170,44),(-213,159),(-365,120)],
 152,474))
# Unlike a stage slab, a public void and civic street cut through the block.
# A second major public institution stands at a completely different
# height and orientation, with its own visible entrance/roof cut.
ceremony=boundary_solid('NAVE_CEREMONIAL_STATION_CONFLUENCE',
 [(-116,150),(20,116),(182,184),(275,364),
  (201,497),(39,489),(-119,357)],
 182,265,'porcelain',(-43,24))
nave_cuts.append(carve_prism(ceremony,'NAVE_CONFLUENCE_PUBLIC_HALL',
 [(-70,219),(56,159),(191,284),(132,427),(-49,392)],
 264,535))
# H1's thick inhabited public-city section: genuine internal public
# courtyards in a rock building, with school/market/commons differentiated
# by mass and vertical program rather than repeating uniform towers.
h1=boundary_solid('H1_OCCUPIED_SCHOOL_MARKET_COMMONS_MASS',
 [(460,195),(666,163),(1032,312),(1238,552),
  (1208,1002),(987,1122),(711,925),(462,587)],
 350,670,'dark_sediment',(-56,-24))
h1_cuts=[
 carve_prism(h1,'H1_MARKET_INTERNAL_STREET',
 [(537,273),(699,254),(875,360),(949,504),
  (782,543),(596,445)],382,780),
 carve_prism(h1,'H1_SCHOOL_PUBLIC_ATRIUM',
 [(793,477),(952,434),(1071,559),(1073,743),
  (893,789),(777,668)],478,1150),
 carve_prism(h1,'H1_COMMONS_SKY_COURT',
 [(949,737),(1160,729),(1181,955),
  (1048,1025),(912,915)],608,1210)
]
# Physical slabs are inserted *inside carved rooms*, never as exterior
# floating shelves. Their dimensions/height are tied to destinations.
def finish_floor(name,center,dx,dy,z,material):
    x,y=center
    poly=[(x-dx*.52,y-dy*.29),(x-dx*.36,y-dy*.54),
          (x+dx*.43,y-dy*.49),(x+dx*.57,y+dy*.25),
          (x+dx*.29,y+dy*.48),(x-dx*.50,y+dy*.42)]
    return boundary_solid(name,poly,z-26,26,material,(0,0))
inside=[
 finish_floor('H1_MARKET_INTERIOR_FLOOR',(699,378),195,155,440,'bronze'),
 finish_floor('H1_SCHOOL_INNER_PUBLIC_PLATEAU',(914,619),220,178,574,'limestone'),
 finish_floor('H1_COMMONS_INTERIOR_GREEN',(1052,846),198,194,710,'gardens'),
 finish_floor('NAVE_PUBLIC_LIBRARY_READING_FLOOR',(-288,35),174,110,214,'bronze'),
]
# Specific urban silhouette and material contact, no batches of ordinary
# rectangular high rises: one working garden and one light-guiding fin.
fin=boundary_solid('M247C_BETA_SLANTED_PUBLIC_LIGHT_FIN',
 [(100,314),(143,290),(245,359),(351,484),(315,540),(209,465)],
 252,425,'bronze',(-75,130))
# This fin is an inhabited light catcher with a street below and a sloped
# top crossing the NAVE-to-H1 civic transition. Main beta concept preserved.
# Integration with preserved W0 is spatial proposal only, NOT a certified
# official world-coordinate registration.
def review_camera(name,eye,target,lens):
    dat=bpy.data.cameras.new('INT13_'+name)
    dat.lens=lens;dat.clip_end=20000
    ob=bpy.data.objects.new(dat.name,dat)
    col.objects.link(ob);ob.location=eye
    ob.rotation_euler=(Vector(target)-Vector(eye)).to_track_quat('-Z','Y').to_euler()
    return ob
review_camera('W0_TO_NAVE_GROUND_APPROACH',(-330,-890,120),(-120,10,190),30)
review_camera('NAVE_CIVIC_PUBLIC_ROOM',(-44,-150,214),(-170,225,337),23)
review_camera('H1_MARKET_SCHOOL_INTERIOR',(643,305,496),(957,722,730),25)
review_camera('M247C_W0_RESEARCH_CITY_AERIAL',(1740,-1150,1390),(190,330,535),36)
# Make the additional 4 SECTION images by hiding only ART-rejected old
# masses. All source mesh object data remains physically present and all
# visibility flags are restored before saving the final native BLEND.
rejected_mask=('INT11_M247C_ALPHA_WEST_ACCRETED_ARCHIVE',
               'INT11_M247C_ALPHA_EAST_CIVIC_HIGH_CITY',
               'INT11_M247C_ALPHA_FLOATING_SEVERED_NORTH')
assert all(n in bpy.data.objects for n in rejected_mask)
old_hidden={n:bool(bpy.data.objects[n].hide_render) for n in rejected_mask}
# Original cameras and W0 unchanged:
assert all(vert_hash(bpy.data.objects[n])==h for n,h in w0.items())
for name,old in original_cameras.items():
    cur=bpy.data.objects[name].matrix_world
    assert max(abs(cur[i][j]-old[i][j]) for i in range(4) for j in range(4))<1e-6
assert len(routes)==9 and len(nave_cuts)+len(h1_cuts)==6
assert sc['CONSTRUCTION']=='HOLD' and sc['FORMAL_ART_ACCEPTED']==sc['COMPLETED_TARGETS']==0
sc['INT13_SOURCE_SHA256']=SOURCE
sc['INT13_NOT_A_FORMAL_ART_ADOPTION']=True
sc['INT13_SPATIAL_SECTION_RESEARCH_UNREGISTERED']=True
sc['INT13_PROGRAM']='W0_NAVE_STATION_LIBRARY_CEREMONY_H1_MARKET_SCHOOL_COMMONS_RESIDENCES'
sc.camera=bpy.data.objects['E11_URBAN_AERIAL']
native=OUT/'HALO9_INT13_PURPOSE_FIRST_INHABITED_SECTION.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
sc.render.engine='CYCLES'
sc.cycles.device='CPU'
sc.cycles.samples=9
sc.cycles.use_denoising=True
sc.render.threads_mode='FIXED';sc.render.threads=2
sc.render.resolution_x=960;sc.render.resolution_y=720
sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'
images={}
full=('E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL')
cut=('INT13_W0_TO_NAVE_GROUND_APPROACH','INT13_NAVE_CIVIC_PUBLIC_ROOM',
     'INT13_H1_MARKET_SCHOOL_INTERIOR','INT13_M247C_W0_RESEARCH_CITY_AERIAL')
for name in full+cut:
    if name==cut[0]:
        for n in rejected_mask:bpy.data.objects[n].hide_render=True
    sc.camera=bpy.data.objects[name]
    filepath=OUT/'renders'/(name+'.png')
    sc.render.filepath=str(filepath)
    bpy.ops.render.render(write_still=True)
    assert filepath.stat().st_size>5000,name
    images[name]=hashlib.sha256(filepath.read_bytes()).hexdigest()
    print('INT13_ACTUAL_BLENDER_RENDER',name,filepath.stat().st_size,flush=True)
for n,v in old_hidden.items():bpy.data.objects[n].hide_render=v
sc.camera=bpy.data.objects['E11_URBAN_AERIAL']
bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
assert all(bpy.data.objects[n].hide_render==v for n,v in old_hidden.items())
report={
 'schema':'halo9-int13-purpose-first-civic-section-v1',
 'parent_sha256':SOURCE,
 'saved_native_blend_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),
 'public_program_nodes':sites,'physical_route_edges':routes,
 'physical_voids':nave_cuts+h1_cuts,
 'new_native_mesh_count':len(created),'new_native_meshes':created,
 'fixed_original_E11_camera_matrices':{n:[[float(x) for x in row] for row in original_cameras[n]] for n in FIXED},
 'protected_W0_geometry_hash':w0,
 'rejected_shells_masked_in_section_only':list(rejected_mask),
 'rejected_shell_visibility_restored_for_native_blend':True,
 'source_view_full_original_E11':list(full),
 'source_view_cutaway_art_rejected_shells_hidden':list(cut),
 'all_native_render_png_sha256':images,
 'topological_path_endpoints':'PASS_FROM_EXPLICIT_GRAPH_ONLY',
 'actual_walkability':'UNVERIFIED',
 'rejected_shell_boolean_integration':'NOT_PERFORMED',
 'main_city_master_completion':'ZERO_OF_30',
 'formal_art_accepted':0,'completed_targets':0,
 'minecraft':'HOLD','art':'UNREVIEWED_NOT_ADOPTED'
}
(OUT/'INT13_NATIVE_RESEARCH_NOT_ART.json').write_text(json.dumps(report,indent=2))
print('INT13_TRUE_PURPOSE_FIRST_ARCHITECTURAL_SECTION_SAVED',report['saved_native_blend_sha256'],flush=True)
